import inspect

import pandas as pd
import streamlit as st
from supabase import create_client, Client


# Los gráficos de RPE deben usar siempre la escala fisiológica 0-10.
# Streamlit st.line_chart ajusta el eje automáticamente, así que interceptamos
# únicamente los gráficos de RPE y los dibujamos con Vega-Lite con dominio fijo.
_original_line_chart = st.line_chart


def _fixed_rpe_line_chart(data):
    df = pd.DataFrame(data).copy()
    if df.empty:
        return _original_line_chart(data)

    plot_df = df.reset_index()
    x_col = plot_df.columns[0]
    series_cols = list(plot_df.columns[1:])
    long_df = plot_df.melt(
        id_vars=[x_col],
        value_vars=series_cols,
        var_name="serie",
        value_name="RPE",
    )

    spec = {
        "mark": {"type": "line", "point": True},
        "encoding": {
            "x": {"field": x_col, "type": "temporal", "title": None},
            "y": {
                "field": "RPE",
                "type": "quantitative",
                "scale": {"domain": [0, 10], "clamp": True},
                "axis": {
                    "title": "RPE",
                    "values": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                },
            },
            "color": {"field": "serie", "type": "nominal", "title": None},
            "tooltip": [
                {"field": x_col, "type": "temporal", "title": "Periodo"},
                {"field": "serie", "type": "nominal", "title": "Atleta"},
                {"field": "RPE", "type": "quantitative", "title": "RPE"},
            ],
        },
    }
    return st.vega_lite_chart(long_df, spec, use_container_width=True)


def _line_chart_with_fixed_rpe(data=None, *args, **kwargs):
    """Mantiene st.line_chart normal salvo en las visualizaciones de RPE."""
    try:
        df = pd.DataFrame(data)
        columns = [str(c).lower() for c in df.columns]
        caller = inspect.currentframe().f_back
        caller_is_group_rpe = (
            caller is not None
            and caller.f_code.co_name == "_render_group_metric"
            and caller.f_locals.get("value_col") == "rpe"
        )
        single_rpe_series = len(columns) == 1 and columns[0] == "rpe"

        if caller_is_group_rpe or single_rpe_series:
            return _fixed_rpe_line_chart(data)
    except Exception:
        # Si no podemos identificar el gráfico, conservamos el comportamiento
        # estándar de Streamlit en lugar de romper la pantalla.
        pass

    return _original_line_chart(data, *args, **kwargs)


if not getattr(st.line_chart, "_sprint_monitor_fixed_rpe", False):
    _line_chart_with_fixed_rpe._sprint_monitor_fixed_rpe = True
    st.line_chart = _line_chart_with_fixed_rpe


def get_supabase() -> Client:
    # Un cliente por sesión de Streamlit. No usar st.cache_resource:
    # el cliente mantiene estado de autenticación.
    if "_supabase_client" not in st.session_state:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_ANON_KEY"]
        st.session_state["_supabase_client"] = create_client(url, key)
    return st.session_state["_supabase_client"]
