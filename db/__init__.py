"""Compatibilidad de interfaz para Sprint Monitor."""

import builtins
import inspect

import pandas as pd
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

_BASE_MARK_EVENTS = ["60m", "100m", "200m", "400m"]
_HURDLE_EVENTS = ["60m vallas", "110m vallas"]
_ALL_MARK_EVENTS = _BASE_MARK_EVENTS + _HURDLE_EVENTS


def _extend_options(label, options):
    values = list(options)
    if label == "Prueba" and all(event in values for event in _BASE_MARK_EVENTS):
        for event in _HURDLE_EVENTS:
            if event not in values:
                insert_at = values.index("4x100") if "4x100" in values else (values.index("other") if "other" in values else len(values))
                values.insert(insert_at, event)
    elif label == "Especialidad":
        for specialty in ["60 m vallas", "110 m vallas"]:
            if specialty not in values:
                values.append(specialty)
    return values


# Durante la importación de db.client conservamos la ampliación del selectbox global.
_selectbox_before_client = st.selectbox


def _selectbox_before_import(label, options, *args, **kwargs):
    return _selectbox_before_client(label, _extend_options(label, options), *args, **kwargs)


st.selectbox = _selectbox_before_import

from . import client as _client  # noqa: E402

# db.client sustituye st.selectbox al terminar de importarse. Añadimos una
# segunda capa para el selectbox global.
_selectbox_after_client = st.selectbox


def _selectbox_with_hurdles(label, options, *args, **kwargs):
    return _selectbox_after_client(label, _extend_options(label, options), *args, **kwargs)


st.selectbox = _selectbox_with_hurdles

# IMPORTANTE: los selectores creados dentro de columnas usan
# DeltaGenerator.selectbox (por ejemplo c1.selectbox), no st.selectbox.
# Esta era la razón por la que "Añadir marca" seguía mostrando solo 4 pruebas.
_delta_selectbox_original = DeltaGenerator.selectbox


def _delta_selectbox_with_hurdles(self, label, options, *args, **kwargs):
    return _delta_selectbox_original(self, label, _extend_options(label, options), *args, **kwargs)


if not getattr(DeltaGenerator.selectbox, "_sprint_monitor_hurdles", False):
    _delta_selectbox_with_hurdles._sprint_monitor_hurdles = True
    DeltaGenerator.selectbox = _delta_selectbox_with_hurdles

# app.py conserva MARK_EVENTS con las cuatro pruebas originales. Cuando su
# renderer de marcas recorre esa lista, ampliamos únicamente ese recorrido.
_original_enumerate = builtins.enumerate


def _enumerate_with_hurdles(iterable, *args):
    try:
        caller = inspect.currentframe().f_back
        if (
            caller is not None
            and caller.f_code.co_name in {"_render_marks", "_render_marks_season"}
            and list(iterable) == _BASE_MARK_EVENTS
        ):
            iterable = _ALL_MARK_EVENTS
    except Exception:
        pass
    return _original_enumerate(iterable, *args)


builtins.enumerate = _enumerate_with_hurdles

# Las consultas de competiciones de app.py filtran por MARK_EVENTS. Extendemos
# solo el filtro event para que también entren las marcas de vallas.
_original_get_supabase = _client.get_supabase


def _get_supabase_with_hurdles():
    client = _original_get_supabase()
    try:
        query_class = type(client.table("competitions"))
        if not getattr(query_class, "_sprint_monitor_hurdles", False):
            original_in = query_class.in_

            def in_with_hurdles(self, column, values):
                updated = list(values) if isinstance(values, (list, tuple, set)) else values
                if column == "event" and isinstance(updated, list) and all(event in updated for event in _BASE_MARK_EVENTS):
                    for event in _HURDLE_EVENTS:
                        if event not in updated:
                            updated.append(event)
                return original_in(self, column, updated)

            query_class.in_ = in_with_hurdles
            query_class._sprint_monitor_hurdles = True
    except Exception:
        pass
    return client


_client.get_supabase = _get_supabase_with_hurdles


def _season_start(value):
    ts = pd.Timestamp(value)
    return int(ts.year if ts.month >= 8 else ts.year - 1)


def _season_label(start_year):
    return f"Temporada {int(start_year)}/{int(start_year) + 1}"


def _best_mark(df):
    if df.empty:
        return None
    valid = df.copy()
    valid["mark_seconds"] = pd.to_numeric(valid["mark_seconds"], errors="coerce")
    valid = valid[valid["mark_seconds"] > 0]
    if valid.empty:
        return None
    return valid.loc[valid["mark_seconds"].idxmin()]


def _mark_caption(row):
    if row is None:
        return "Sin marca registrada"
    parsed = pd.to_datetime(row.get("mark_date"), errors="coerce")
    when = parsed.strftime("%d/%m/%Y") if not pd.isna(parsed) else ""
    extras = [x for x in [when, row.get("source") or ""] if x]
    wind = row.get("wind")
    if wind is not None:
        try:
            extras.append(f"viento {float(wind):+.1f} m/s")
        except Exception:
            pass
    if row.get("notes"):
        extras.append(str(row.get("notes")))
    return " · ".join(extras) if extras else "Marca registrada"


def _profile_mark_rows(uid):
    client = _client.get_supabase()
    rows = []
    try:
        competitions = (
            client.table("competitions")
            .select("competition_date,competition_name,event,result_seconds,wind")
            .eq("athlete_id", uid)
            .in_("event", _ALL_MARK_EVENTS)
            .order("competition_date")
            .limit(500)
            .execute()
            .data
            or []
        )
        for row in competitions:
            rows.append({
                "event": row.get("event"),
                "mark_seconds": row.get("result_seconds"),
                "mark_date": row.get("competition_date"),
                "source": row.get("competition_name") or "Competición",
                "wind": row.get("wind"),
                "notes": None,
            })
    except Exception:
        pass

    try:
        manual = (
            client.table("athlete_marks")
            .select("event,mark_seconds,mark_date,notes")
            .eq("athlete_id", uid)
            .order("mark_date")
            .limit(500)
            .execute()
            .data
            or []
        )
        for row in manual:
            rows.append({
                "event": row.get("event"),
                "mark_seconds": row.get("mark_seconds"),
                "mark_date": row.get("mark_date"),
                "source": "Marca añadida en Mi evolución",
                "wind": None,
                "notes": row.get("notes"),
            })
    except Exception:
        pass
    return rows


def _render_profile_marks(uid, key_prefix):
    rows = _profile_mark_rows(uid)
    df = pd.DataFrame(rows)
    current_start = _season_start(pd.Timestamp.today())
    starts = []
    if not df.empty:
        df["mark_date"] = pd.to_datetime(df["mark_date"], errors="coerce")
        df["mark_seconds"] = pd.to_numeric(df["mark_seconds"], errors="coerce")
        starts = sorted({_season_start(d) for d in df["mark_date"].dropna()}, reverse=True)
    if current_start not in starts:
        starts.insert(0, current_start)
    if not starts:
        starts = [current_start]

    labels = [_season_label(year) for year in starts]
    st.markdown("### 🏅 Marcas")
    selected_label = st.selectbox("Temporada", labels, index=0, key=f"marks_season_{key_prefix}")
    selected_start = starts[labels.index(selected_label)]
    season_from = pd.Timestamp(year=selected_start, month=8, day=1)
    season_to = pd.Timestamp(year=selected_start + 1, month=8, day=1)
    st.caption("La marca personal usa todos los registros. La marca de la temporada usa la temporada seleccionada.")

    cols = st.columns(2)
    for index, event in _original_enumerate(_ALL_MARK_EVENTS):
        event_df = df[df["event"] == event].copy() if not df.empty else pd.DataFrame()
        pb = _best_mark(event_df)
        season_df = event_df[(event_df["mark_date"] >= season_from) & (event_df["mark_date"] < season_to)].copy() if not event_df.empty else pd.DataFrame()
        sb = _best_mark(season_df)
        with cols[index % 2]:
            with st.container(border=True):
                st.markdown(f"#### {event.replace('m', ' m')}")
                c1, c2 = st.columns(2)
                c1.metric("Marca personal", f"{float(pb['mark_seconds']):.3f} s" if pb is not None else "—")
                c2.metric(selected_label, f"{float(sb['mark_seconds']):.3f} s" if sb is not None else "—")
                st.caption(f"MP: {_mark_caption(pb)}")
                st.caption(f"MT: {_mark_caption(sb)}")

    manual_rows = [row for row in rows if row.get("source") == "Marca añadida en Mi evolución"]
    if manual_rows:
        st.markdown("### Historial de marcas registradas")
        history = pd.DataFrame(manual_rows)
        history["mark_date"] = pd.to_datetime(history["mark_date"], errors="coerce")
        history = history.sort_values("mark_date", ascending=False)
        history = history.rename(columns={
            "mark_date": "Fecha",
            "event": "Prueba",
            "mark_seconds": "Marca (s)",
            "notes": "Comentario",
        })
        st.dataframe(history[["Fecha", "Prueba", "Marca (s)", "Comentario"]], use_container_width=True, hide_index=True)


# Mi perfil del atleta conserva foto y datos básicos, pero ya no muestra marcas.
# El coach sigue pudiendo consultar las marcas desde la ficha del atleta.
_original_client_render_marks = _client._render_marks


def _render_marks_without_athlete_profile(uid, key_prefix):
    if key_prefix == "athlete_profile":
        return None
    return _render_profile_marks(uid, key_prefix)


_client._render_marks = _render_marks_without_athlete_profile
