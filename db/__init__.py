import inspect

import pandas as pd
import streamlit as st

# Cargamos primero db.client para conservar todos sus parches existentes y,
# después, afinamos únicamente la visualización de marcas/temporadas.
from . import client as _client

_SEASON_START_MONTH = 8


def _season_start(ts=None):
    ts = pd.Timestamp.today() if ts is None else pd.Timestamp(ts)
    return int(ts.year if ts.month >= _SEASON_START_MONTH else ts.year - 1)


def _season_label(start_year):
    start_year = int(start_year)
    return f"Temporada {start_year}/{start_year + 1}"


def _season_bounds(start_year):
    start_year = int(start_year)
    return (
        pd.Timestamp(year=start_year, month=_SEASON_START_MONTH, day=1),
        pd.Timestamp(year=start_year + 1, month=_SEASON_START_MONTH, day=1),
    )


def _best(df):
    if df is None or df.empty:
        return None
    valid = df.copy()
    valid["result_seconds"] = pd.to_numeric(valid["result_seconds"], errors="coerce")
    valid = valid[valid["result_seconds"] > 0]
    if valid.empty:
        return None
    return valid.loc[valid["result_seconds"].idxmin()]


def _caption_for(row):
    if row is None:
        return "Sin marca registrada"
    date_value = pd.to_datetime(row.get("competition_date"), errors="coerce")
    date_text = date_value.strftime("%d/%m/%Y") if not pd.isna(date_value) else ""
    competition = row.get("competition_name") or ""
    wind = row.get("wind")
    parts = [p for p in [date_text, competition] if p]
    if wind is not None:
        try:
            parts.append(f"viento {float(wind):+.1f} m/s")
        except Exception:
            pass
    return " · ".join(parts) if parts else "Marca registrada"


def _render_marks_season(uid, key_prefix):
    rows = _client._competition_rows(uid)
    df = pd.DataFrame(rows)
    current_start = _season_start()

    starts = []
    if not df.empty:
        df["competition_date"] = pd.to_datetime(df["competition_date"], errors="coerce")
        df["result_seconds"] = pd.to_numeric(df["result_seconds"], errors="coerce")
        starts = sorted({_season_start(d) for d in df["competition_date"].dropna()}, reverse=True)
    if current_start not in starts:
        starts.insert(0, current_start)
    if not starts:
        starts = [current_start]

    labels = [_season_label(y) for y in starts]
    st.markdown("### 🏅 Marcas")
    selected_label = st.selectbox("Temporada", labels, index=0, key=f"marks_season_{key_prefix}")
    selected_start = starts[labels.index(selected_label)]
    season_from, season_to = _season_bounds(selected_start)
    st.caption("La mejor marca personal usa todas las competiciones registradas. La mejor marca de la temporada usa la temporada seleccionada.")

    cols = st.columns(2)
    for index, event in enumerate(_client._MARK_EVENTS):
        event_df = df[df["event"] == event].copy() if not df.empty else pd.DataFrame()
        pb = _best(event_df)
        if event_df.empty:
            season_df = pd.DataFrame()
        else:
            season_df = event_df[(event_df["competition_date"] >= season_from) & (event_df["competition_date"] < season_to)].copy()
        sb = _best(season_df)

        with cols[index % 2]:
            with st.container(border=True):
                st.markdown(f"#### {event.replace('m', ' m')}")
                c1, c2 = st.columns(2)
                c1.metric("Marca personal", f"{float(pb['result_seconds']):.3f} s" if pb is not None else "—")
                c2.metric(selected_label, f"{float(sb['result_seconds']):.3f} s" if sb is not None else "—")
                st.caption(f"MP: {_caption_for(pb)}")
                st.caption(f"MT: {_caption_for(sb)}")


# Coach y Mi perfil del atleta usan ya el formato de temporada agosto-julio.
_client._render_marks = _render_marks_season


_original_selectbox = st.selectbox
_original_subheader = st.subheader
_original_metric = st.metric
_original_caption = st.caption


def _evolution_frame():
    frame = inspect.currentframe()
    while frame is not None:
        if frame.f_code.co_name == "evolution":
            return frame
        frame = frame.f_back
    return None


def _selectbox_season(label, options, *args, **kwargs):
    frame = _evolution_frame()
    if label == "Temporada" and frame is not None:
        values = list(options)
        current_start = _season_start()
        numeric = []
        for value in values:
            try:
                numeric.append(int(value))
            except Exception:
                pass
        if current_start not in numeric:
            numeric.insert(0, current_start)
        values = numeric or [current_start]
        kwargs.setdefault("format_func", lambda y: _season_label(int(y)))
        kwargs["index"] = 0
        return _original_selectbox(label, values, *args, **kwargs)
    return _original_selectbox(label, options, *args, **kwargs)


def _subheader_marks(body, *args, **kwargs):
    if body == "Mejor marca de la temporada" and _evolution_frame() is not None:
        body = "Marcas"
    return _original_subheader(body, *args, **kwargs)


def _evolution_results(frame):
    cdf = frame.f_locals.get("cdf")
    event = frame.f_locals.get("event")
    season = frame.f_locals.get("season")
    if not isinstance(cdf, pd.DataFrame) or not event:
        return None, None, None
    try:
        start_year = int(season)
    except Exception:
        start_year = _season_start()

    event_df = cdf[cdf["event"] == event].copy()
    pb = _best(event_df)
    season_from, season_to = _season_bounds(start_year)
    if event_df.empty:
        season_df = pd.DataFrame()
    else:
        season_df = event_df[(event_df["competition_date"] >= season_from) & (event_df["competition_date"] < season_to)].copy()
    sb = _best(season_df)
    return pb, sb, start_year


def _render_evolution_metrics(frame):
    pb, sb, start_year = _evolution_results(frame)
    c1, c2 = st.columns(2)
    c1.metric("Marca personal", f"{float(pb['result_seconds']):.3f} s" if pb is not None else "—")
    c2.metric(_season_label(start_year), f"{float(sb['result_seconds']):.3f} s" if sb is not None else "—")
    return pb, sb


def _metric_marks(label, value, *args, **kwargs):
    frame = _evolution_frame()
    if frame is not None and label == "Mejor marca":
        _render_evolution_metrics(frame)
        return None
    return _original_metric(label, value, *args, **kwargs)


def _caption_marks(body, *args, **kwargs):
    frame = _evolution_frame()
    if frame is not None and frame.f_locals.get("event"):
        pb, sb, _ = _evolution_results(frame)
        if body == "Sin marca registrada":
            _render_evolution_metrics(frame)
        _original_caption(f"MP: {_caption_for(pb)}")
        return _original_caption(f"MT: {_caption_for(sb)}")
    return _original_caption(body, *args, **kwargs)


st.selectbox = _selectbox_season
st.subheader = _subheader_marks
st.metric = _metric_marks
st.caption = _caption_marks
