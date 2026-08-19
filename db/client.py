import copy
import inspect
import io

import pandas as pd
import streamlit as st
from PIL import Image, ImageOps
from supabase import create_client, Client


# Formato visual español en toda la app.
_original_date_input = st.date_input
_original_dataframe = st.dataframe
_original_vega_lite_chart = st.vega_lite_chart
_original_selectbox = st.selectbox
_original_title = st.title
_original_tabs = st.tabs
_original_line_chart = st.line_chart

_DATE_COLUMN_NAMES = {
    "fecha", "date", "session_date", "entry_date", "competition_date",
    "start_date", "end_date", "periodo", "día", "semana", "mes",
}


def _date_input_es(*args, **kwargs):
    kwargs.setdefault("format", "DD/MM/YYYY")
    try:
        return _original_date_input(*args, **kwargs)
    except TypeError:
        kwargs.pop("format", None)
        return _original_date_input(*args, **kwargs)


def _format_datetime_series_es(series):
    parsed = pd.to_datetime(series, errors="coerce")
    non_null = series.notna()
    if non_null.any() and parsed[non_null].notna().all():
        has_time = ((parsed.dt.hour.fillna(0) != 0) | (parsed.dt.minute.fillna(0) != 0) | (parsed.dt.second.fillna(0) != 0)).any()
        return parsed.dt.strftime("%d/%m/%Y %H:%M" if has_time else "%d/%m/%Y")
    return series


def _dataframe_es(data=None, *args, **kwargs):
    if isinstance(data, pd.DataFrame):
        data = data.copy()
        for col in data.columns:
            name = str(col).strip().lower()
            if name in _DATE_COLUMN_NAMES or pd.api.types.is_datetime64_any_dtype(data[col]):
                data[col] = _format_datetime_series_es(data[col])
    return _original_dataframe(data, *args, **kwargs)


def _apply_spanish_temporal_format(spec):
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


# RPE siempre 0-10.
def _fixed_rpe_line_chart(data):
    df = pd.DataFrame(data).copy()
    if df.empty:
        return _original_line_chart(data)
    plot_df = df.reset_index()
    x_col = plot_df.columns[0]
    series_cols = list(plot_df.columns[1:])
    long_df = plot_df.melt(id_vars=[x_col], value_vars=series_cols, var_name="serie", value_name="RPE")
    spec = {
        "mark": {"type": "line", "point": True},
        "encoding": {
            "x": {"field": x_col, "type": "temporal", "title": None, "axis": {"format": "%d/%m/%Y"}},
            "y": {"field": "RPE", "type": "quantitative", "scale": {"domain": [0, 10], "clamp": True}, "axis": {"title": "RPE", "values": list(range(11))}},
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
    try:
        df = pd.DataFrame(data)
        columns = [str(c).lower() for c in df.columns]
        caller = inspect.currentframe().f_back
        caller_is_group_rpe = caller is not None and caller.f_code.co_name == "_render_group_metric" and caller.f_locals.get("value_col") == "rpe"
        single_rpe_series = len(columns) == 1 and columns[0] == "rpe"
        if caller_is_group_rpe or single_rpe_series:
            return _fixed_rpe_line_chart(data)
    except Exception:
        pass
    return _original_line_chart(data, *args, **kwargs)


if not getattr(st.line_chart, "_sprint_monitor_fixed_rpe", False):
    _line_chart_with_fixed_rpe._sprint_monitor_fixed_rpe = True
    st.line_chart = _line_chart_with_fixed_rpe


# Especialidad 400 m.
def _selectbox_with_400m(label, options, *args, **kwargs):
    if label == "Especialidad":
        values = list(options)
        if "400 m" not in values:
            values.append("400 m")
        profile = st.session_state.get("profile") or {}
        current = profile.get("specialty")
        if current in values:
            kwargs["index"] = values.index(current)
        options = values
    return _original_selectbox(label, options, *args, **kwargs)


# Foto de perfil ligera.
def _avatar_bytes(uploaded_file):
    image = Image.open(uploaded_file).convert("RGB")
    image = ImageOps.fit(image, (256, 256), method=Image.Resampling.LANCZOS)
    output = io.BytesIO()
    image.save(output, format="JPEG", quality=58, optimize=True, progressive=True)
    data = output.getvalue()
    if len(data) > 450_000:
        output = io.BytesIO()
        image.save(output, format="JPEG", quality=42, optimize=True)
        data = output.getvalue()
    return data


def _profile_row(uid):
    try:
        return get_supabase().table("profiles").select("id,avatar_path").eq("id", uid).single().execute().data or {}
    except Exception:
        return {}


def _show_avatar(uid, editable=False):
    client = get_supabase()
    avatar_path = _profile_row(uid).get("avatar_path")
    if avatar_path:
        try:
            signed = client.storage.from_("profile-photos").create_signed_url(avatar_path, 900)
            url = signed.get("signedURL") or signed.get("signedUrl") or signed.get("signed_url")
            if url:
                st.image(url, width=120)
        except Exception:
            pass
    if not editable:
        return
    uploaded = st.file_uploader("Foto de perfil", type=["jpg", "jpeg", "png", "webp"], key="profile_photo_upload", help="La app la reduce automáticamente a 256×256 px y baja calidad para que pese poco.")
    if uploaded is not None:
        st.caption("La foto se recortará en formato cuadrado y se comprimirá antes de subirla.")
        if st.button("Guardar foto de perfil", key="save_profile_photo"):
            try:
                data = _avatar_bytes(uploaded)
                path = f"{uid}/avatar.jpg"
                client.storage.from_("profile-photos").upload(path=path, file=data, file_options={"content-type": "image/jpeg", "upsert": "true", "cache-control": "3600"})
                client.table("profiles").update({"avatar_path": path}).eq("id", uid).execute()
                if st.session_state.get("profile"):
                    st.session_state.profile["avatar_path"] = path
                st.success(f"Foto guardada ({max(1, round(len(data) / 1024))} KB).")
                st.rerun()
            except Exception as exc:
                st.error(f"No se pudo guardar la foto: {exc}")


# Marcas personales y de temporada.
_MARK_EVENTS = ["60m", "100m", "200m", "400m"]
_SEASON_START_MONTH = 8


def _competition_rows(uid):
    try:
        return (get_supabase().table("competitions").select("competition_date,competition_name,event,result_seconds,wind").eq("athlete_id", uid).in_("event", _MARK_EVENTS).order("competition_date").limit(500).execute().data or [])
    except Exception:
        return []


def _best_result(df):
    if df.empty:
        return None
    valid = df[pd.to_numeric(df["result_seconds"], errors="coerce") > 0].copy()
    if valid.empty:
        return None
    valid["result_seconds"] = pd.to_numeric(valid["result_seconds"], errors="coerce")
    return valid.loc[valid["result_seconds"].idxmin()]


def _mark_caption(row):
    if row is None:
        return "Sin marca registrada"
    parsed = pd.to_datetime(row.get("competition_date"), errors="coerce")
    when = parsed.strftime("%d/%m/%Y") if not pd.isna(parsed) else ""
    competition = row.get("competition_name") or ""
    wind = row.get("wind")
    extras = [x for x in [when, competition] if x]
    if wind is not None:
        try:
            extras.append(f"viento {float(wind):+.1f} m/s")
        except Exception:
            pass
    return " · ".join(extras) if extras else "Marca registrada"


def _season_start_for_date(ts):
    ts = pd.Timestamp(ts)
    return int(ts.year if ts.month >= _SEASON_START_MONTH else ts.year - 1)


def _season_label(start_year):
    return f"Temporada {start_year}/{start_year + 1}"


def _render_marks(uid, key_prefix):
    rows = _competition_rows(uid)
    df = pd.DataFrame(rows)
    now = pd.Timestamp.today()
    current_start = _season_start_for_date(now)

    season_starts = []
    if not df.empty:
        df["competition_date"] = pd.to_datetime(df["competition_date"], errors="coerce")
        df["result_seconds"] = pd.to_numeric(df["result_seconds"], errors="coerce")
        season_starts = sorted({_season_start_for_date(d) for d in df["competition_date"].dropna()}, reverse=True)
    if current_start not in season_starts:
        season_starts = [current_start] + season_starts
    if not season_starts:
        season_starts = [current_start]

    labels = [_season_label(y) for y in season_starts]
    st.markdown("### 🏅 Marcas")
    selected_label = st.selectbox("Temporada", labels, index=0, key=f"marks_season_{key_prefix}")
    selected_start = season_starts[labels.index(selected_label)]
    season_from = pd.Timestamp(year=selected_start, month=_SEASON_START_MONTH, day=1)
    season_to = pd.Timestamp(year=selected_start + 1, month=_SEASON_START_MONTH, day=1)
    st.caption("La mejor marca personal usa todas las competiciones registradas. La mejor marca de la temporada usa la temporada seleccionada.")

    cols = st.columns(2)
    for index, event in enumerate(_MARK_EVENTS):
        event_df = df[df["event"] == event].copy() if not df.empty else pd.DataFrame()
        pb = _best_result(event_df)
        if not event_df.empty:
            season_df = event_df[(event_df["competition_date"] >= season_from) & (event_df["competition_date"] < season_to)].copy()
        else:
            season_df = pd.DataFrame()
        sb = _best_result(season_df)
        with cols[index % 2]:
            with st.container(border=True):
                st.markdown(f"#### {event.replace('m', ' m')}")
                c1, c2 = st.columns(2)
                c1.metric("Marca personal", f"{float(pb['result_seconds']):.3f} s" if pb is not None else "—")
                c2.metric(selected_label, f"{float(sb['result_seconds']):.3f} s" if sb is not None else "—")
                st.caption(f"MP: {_mark_caption(pb)}")
                st.caption(f"MT: {_mark_caption(sb)}")


def _title_with_profile_photo(body, *args, **kwargs):
    result = _original_title(body, *args, **kwargs)
    try:
        if body == "👤 Mi perfil":
            user = st.session_state.get("user")
            if user:
                _show_avatar(user.id, editable=True)
                _render_marks(user.id, "athlete_profile")
        elif isinstance(body, str) and body.startswith("👤 "):
            athlete = st.session_state.get("selected_athlete")
            if athlete and athlete.get("id"):
                _show_avatar(athlete["id"], editable=False)
    except Exception:
        pass
    return result


def _tabs_with_marks(labels, *args, **kwargs):
    values = list(labels)
    try:
        caller = inspect.currentframe().f_back
        caller_name = caller.f_code.co_name if caller is not None else ""

        is_coach_detail = caller_name == "coach_athlete_detail" and "Entrenamientos" in values and "Competiciones" in values and "Carga" in values
        if is_coach_detail and not any("Marcas" in str(v) for v in values):
            tabs = _original_tabs(values + ["🏅 Marcas"], *args, **kwargs)
            athlete = st.session_state.get("selected_athlete") or {}
            if athlete.get("id"):
                with tabs[-1]:
                    _render_marks(athlete["id"], "coach_athlete")
            return tabs

        is_athlete_evolution = caller_name == "evolution" and "🏅 Mejor marca" in values and "📊 Carga" in values and "❤️ Bienestar" in values
        if is_athlete_evolution and not any(v == "🏅 Marcas" for v in values):
            tabs = _original_tabs(values + ["🏅 Marcas"], *args, **kwargs)
            user = st.session_state.get("user")
            if user:
                with tabs[-1]:
                    _render_marks(user.id, "athlete_evolution")
            return tabs
    except Exception:
        pass
    return _original_tabs(values, *args, **kwargs)


if not getattr(st.selectbox, "_sprint_monitor_400m", False):
    _selectbox_with_400m._sprint_monitor_400m = True
    st.selectbox = _selectbox_with_400m
if not getattr(st.title, "_sprint_monitor_profile_photo", False):
    _title_with_profile_photo._sprint_monitor_profile_photo = True
    st.title = _title_with_profile_photo
if not getattr(st.tabs, "_sprint_monitor_marks_v2", False):
    _tabs_with_marks._sprint_monitor_marks_v2 = True
    st.tabs = _tabs_with_marks


def get_supabase() -> Client:
    if "_supabase_client" not in st.session_state:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_ANON_KEY"]
        st.session_state["_supabase_client"] = create_client(url, key)
    return st.session_state["_supabase_client"]
