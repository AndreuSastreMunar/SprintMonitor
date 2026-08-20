"""Compatibilidad de interfaz para Sprint Monitor."""

import builtins
import inspect

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
        for specialty in ["400 m", "60 m vallas", "110 m vallas"]:
            if specialty not in values:
                values.append(specialty)
    return values


# Conservamos funciones base estables para evitar que los reruns de Streamlit
# encadenen wrappers sobre wrappers y generen widgets duplicados.
if not hasattr(st, "_sprint_monitor_base_selectbox"):
    st._sprint_monitor_base_selectbox = st.selectbox
if not hasattr(st, "_sprint_monitor_base_radio"):
    st._sprint_monitor_base_radio = st.radio
if not hasattr(st, "_sprint_monitor_base_button"):
    st._sprint_monitor_base_button = st.button
if not hasattr(st, "_sprint_monitor_base_rerun"):
    st._sprint_monitor_base_rerun = st.rerun
if not hasattr(st, "_sprint_monitor_base_tabs"):
    st._sprint_monitor_base_tabs = st.tabs


def _selectbox_before_import(label, options, *args, **kwargs):
    return st._sprint_monitor_base_selectbox(label, _extend_options(label, options), *args, **kwargs)


st.selectbox = _selectbox_before_import

from . import client as _client  # noqa: E402

# db.client puede instalar sus propios wrappers. Guardamos el selector resultante
# una sola vez y añadimos las pruebas de vallas encima.
if not hasattr(st, "_sprint_monitor_selectbox_after_client"):
    st._sprint_monitor_selectbox_after_client = st.selectbox


def _selectbox_with_hurdles(label, options, *args, **kwargs):
    return st._sprint_monitor_selectbox_after_client(label, _extend_options(label, options), *args, **kwargs)


st.selectbox = _selectbox_with_hurdles

_delta_selectbox_original = DeltaGenerator.selectbox


def _delta_selectbox_with_hurdles(self, label, options, *args, **kwargs):
    return _delta_selectbox_original(self, label, _extend_options(label, options), *args, **kwargs)


if not getattr(DeltaGenerator.selectbox, "_sprint_monitor_hurdles", False):
    _delta_selectbox_with_hurdles._sprint_monitor_hurdles = True
    DeltaGenerator.selectbox = _delta_selectbox_with_hurdles


# Amplía las tarjetas de marcas a las pruebas de vallas.
if not hasattr(builtins, "_sprint_monitor_original_enumerate"):
    builtins._sprint_monitor_original_enumerate = builtins.enumerate


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
    return builtins._sprint_monitor_original_enumerate(iterable, *args)


builtins.enumerate = _enumerate_with_hurdles


# Amplía filtros de marcas y añade did_sled al guardar training_sessions.
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

        if not getattr(query_class, "_sprint_monitor_sled", False):
            original_insert = query_class.insert

            def insert_with_sled(self, json, *args, **kwargs):
                payload = json
                if (
                    isinstance(json, dict)
                    and "athlete_id" in json
                    and "session_date" in json
                    and "rpe" in json
                    and "did_gym" in json
                    and "did_plyometrics" in json
                    and "did_sled" not in json
                ):
                    payload = dict(json)
                    answer = st.session_state.get("training_did_sled")
                    payload["did_sled"] = answer == "Sí" if answer in {"Sí", "No"} else None
                return original_insert(self, payload, *args, **kwargs)

            query_class.insert = insert_with_sled
            query_class._sprint_monitor_sled = True
    except Exception:
        pass
    return client


_client.get_supabase = _get_supabase_with_hurdles


# Mi perfil: mostramos título nativo + foto, sin la sección de marcas.
if not hasattr(st, "_sprint_monitor_title_after_client"):
    st._sprint_monitor_title_after_client = st.title


def _title_without_profile_marks(body, *args, **kwargs):
    if body == "👤 Mi perfil":
        result = _client._original_title(body, *args, **kwargs)
        try:
            user = st.session_state.get("user")
            if user:
                _client._show_avatar(user.id, editable=True)
        except Exception:
            pass
        return result
    return st._sprint_monitor_title_after_client(body, *args, **kwargs)


st.title = _title_without_profile_marks


# Trabajo complementario: tercera pregunta obligatoria. Se usa siempre la
# función base de radio para que el mismo key no se registre dos veces.
def _radio_with_sled(label, options, *args, **kwargs):
    result = st._sprint_monitor_base_radio(label, options, *args, **kwargs)
    if label == "¿Has hecho pliometría?":
        st._sprint_monitor_base_radio(
            "¿Has hecho series con arrastres?",
            ["Sí", "No"],
            horizontal=True,
            index=None,
            key="training_did_sled",
        )
    return result


st.radio = _radio_with_sled


def _button_require_sled(label, *args, **kwargs):
    clicked = st._sprint_monitor_base_button(label, *args, **kwargs)
    if label == "💾 Guardar entrenamiento" and clicked:
        if st.session_state.get("training_did_sled") not in {"Sí", "No"}:
            st.warning("Debes responder si has hecho series con arrastres antes de guardar.")
            return False
    return clicked


st.button = _button_require_sled


def _rerun_clear_sled(*args, **kwargs):
    if st.session_state.get("flash_message") == "Entrenamiento guardado correctamente.":
        st.session_state.pop("training_did_sled", None)
    return st._sprint_monitor_base_rerun(*args, **kwargs)


st.rerun = _rerun_clear_sled


# Ficha del entrenador: Arrastres se ve entre Series y Gimnasio sin alterar
# los índices lógicos que app.py usa para las demás pestañas.
def _tabs_with_sled(labels, *args, **kwargs):
    values = list(labels)
    try:
        caller = inspect.currentframe().f_back
        is_coach_detail = (
            caller is not None
            and caller.f_code.co_name == "coach_athlete_detail"
            and "Gimnasio" in values
            and "Pliometría" in values
            and "Entrenamientos" in values
        )
        if is_coach_detail and "Arrastres" not in values:
            insert_at = values.index("Gimnasio")
            display_values = values[:insert_at] + ["Arrastres"] + values[insert_at:]
            display_tabs = st._sprint_monitor_base_tabs(display_values, *args, **kwargs)
            sled_tab = display_tabs[insert_at]
            aid = caller.f_locals.get("aid")
            with sled_tab:
                st.subheader("🛷 Arrastres")
                if not aid:
                    st.info("No se pudo identificar al atleta.")
                else:
                    try:
                        rows = (
                            _client.get_supabase().table("training_sessions")
                            .select("session_date,volume_m,rpe,notes,did_sled")
                            .eq("athlete_id", aid)
                            .order("session_date", desc=True)
                            .limit(200)
                            .execute().data or []
                        )
                        sled_days = [row for row in rows if row.get("did_sled") is True]
                        st.metric("Días con arrastres", len(sled_days))
                        if sled_days:
                            st.dataframe(
                                [
                                    {
                                        "Fecha": row.get("session_date"),
                                        "Metros": row.get("volume_m"),
                                        "RPE": row.get("rpe"),
                                        "Comentarios": row.get("notes"),
                                    }
                                    for row in sled_days
                                ],
                                use_container_width=True,
                                hide_index=True,
                            )
                        else:
                            st.info("Todavía no hay entrenamientos registrados con arrastres.")
                    except Exception as exc:
                        st.warning(f"No se pudieron cargar los arrastres: {exc}")

            return display_tabs[:insert_at] + display_tabs[insert_at + 1:] + [sled_tab]
    except Exception:
        pass
    return st._sprint_monitor_base_tabs(values, *args, **kwargs)


st.tabs = _tabs_with_sled
