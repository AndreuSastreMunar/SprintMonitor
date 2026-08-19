import copy
import inspect

import pandas as pd
import streamlit as st
from supabase import create_client, Client


# Formato visual español en toda la app.
# La base de datos sigue guardando fechas en ISO (YYYY-MM-DD), que es lo correcto;
# aquí solo cambiamos cómo se muestran al usuario.
_original_date_input = st.date_input
_original_dataframe = st.dataframe
_original_vega_lite_chart = st.vega_lite_chart

_DATE_COLUMN_NAMES = {
    "fecha",
    "date",
    "session_date",
    "entry_date",
    "competition_date",
    "start_date",
    "end_date",
    "periodo",
    "día",
    "semana",
    "mes",
}


def _date_input_es(*args, **kwargs):
    """Muestra los selectores de fecha como DD/MM/AAAA."""
    kwargs.setdefault("format", "DD/MM/YYYY")
    try:
        return _original_date_input(*args, **kwargs)
    except TypeError:
        # Compatibilidad con versiones antiguas de Streamlit.
        kwargs.pop("format", None)
        return _original_date_input(*args, **kwargs)


def _format_datetime_series_es(series):
    parsed = pd.to_datetime(series, errors="coerce")
    non_null = series.notna()
    if non_null.any() and parsed[non_null].notna().all():
        has_time = (
            (parsed.dt.hour.fillna(0) != 0)
            | (parsed.dt.minute.fillna(0) != 0)
            | (parsed.dt.second.fillna(0) != 0)
        ).any()
        return parsed.dt.strftime("%d/%m/%Y %H:%M" if has_time else "%d/%m/%Y")
    return series


def _dataframe_es(data=None, *args, **kwargs):
    """Convierte las fechas de las tablas a DD/MM/AAAA y las horas a 24 h."""
    if isinstance(data, pd.DataFrame):
        data = data.copy()
        for col in data.columns:
            name = str(col).strip().lower()
            if name in _DATE_COLUMN_NAMES or pd.api.types.is_datetime64_any_dtype(data[col]):
                data[col] = _format_datetime_series_es(data[col])
    return _original_dataframe(data, *args, **kwargs)


def _apply_spanish_temporal_format(spec):
    """Fuerza DD/MM/AAAA en ejes y tooltips temporales de Vega-Lite."""
    if not isinstance(spec, dict):
        return spec
    spec = copy.deepcopy(spec)
    encoding = spec.get("encoding")
    if isinstance(encoding, dict):
        x = encoding.get("x")
        if isinstance(x, dict) and x.get("type") == "temporal":
            axis = x.setdefault("axis", {})
            if isinstance(axis, dict):
                axis.setdefault("format", "%d/%m/%Y")
            x.setdefault("format", "%d/%m/%Y")

        tooltip = encoding.get("tooltip")
        if isinstance(tooltip, list):
            for item in tooltip:
                if isinstance(item, dict) and item.get("type") == "temporal":
                    item.setdefault("format", "%d/%m/%Y")
        elif isinstance(tooltip, dict) and tooltip.get("type") == "temporal":
            tooltip.setdefault("format", "%d/%m/%Y")
    return spec


def _vega_lite_chart_es(data=None, spec=None, *args, **kwargs):
    # Streamlit admite tanto st.vega_lite_chart(spec) como
    # st.vega_lite_chart(data, spec). Cubrimos ambas formas.
    if spec is None and isinstance(data, dict) and "encoding" in data:
        data = _apply_spanish_temporal_format(data)
    else:
        spec = _apply_spanish_temporal_format(spec)
    return _original_vega_lite_chart(data, spec, *args, **kwargs)


if not getattr(st.date_input, "_sprint_monitor_es", False):
    _date_input_es._sprint_monitor_es = True
    st.date_input = _date_input_es

if not getattr(st.dataframe, "_sprint_monitor_es", False):
    _dataframe_es._sprint_monitor_es = True
    st.dataframe = _dataframe_es

if not getattr(st.vega_lite_chart, "_sprint_monitor_es", False):
    _vega_lite_chart_es._sprint_monitor_es = True
    st.vega_lite_chart = _vega_lite_chart_es


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
            "x": {
                "field": x_col,
                "type": "temporal",
                "title": None,
                "axis": {"format": "%d/%m/%Y"},
            },
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
                {"field": x_col, "type": "temporal", "title": "Periodo", "format": "%d/%m/%Y"},
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
