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


if not hasattr(st, "_sprint_monitor_base_selectbox"):
    st._sprint_monitor_base_selectbox = st.selectbox


def _selectbox_before_import(label, options, *args, **kwargs):
    return st._sprint_monitor_base_selectbox(label, _extend_options(label, options), *args, **kwargs)


st.selectbox = _selectbox_before_import

from . import client as _client  # noqa: E402

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


_original_get_supabase = _client.get_supabase


class _TrainingTableProxy:
    """Delegado que modifica solo los INSERT de training_sessions."""

    def __init__(self, builder):
        self._builder = builder

    def __getattr__(self, name):
        return getattr(self._builder, name)

    def insert(self, payload, *args, **kwargs):
        if isinstance(payload, dict):
            payload = dict(payload)
            gym = st.session_state.get("training_did_gym")
            plyo = st.session_state.get("training_did_plyo")
            sled = st.session_state.get("training_did_sled")
            if gym in {"Sí", "No"}:
                payload["did_gym"] = gym == "Sí"
            if plyo in {"Sí", "No"}:
                payload["did_plyometrics"] = plyo == "Sí"
            if sled in {"Sí", "No"}:
                payload["did_sled"] = sled == "Sí"
        return self._builder.insert(payload, *args, **kwargs)


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

        if not getattr(client, "_sprint_monitor_training_table_wrapped", False):
            original_table = client.table

            def table_with_training_flags(table_name, *args, **kwargs):
                builder = original_table(table_name, *args, **kwargs)
                if table_name == "training_sessions":
                    return _TrainingTableProxy(builder)
                return builder

            client.table = table_with_training_flags
            client._sprint_monitor_training_table_wrapped = True
    except Exception:
        pass
    return client


_client.get_supabase = _get_supabase_with_hurdles


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


def _radio_with_sled(label, options, *args, **kwargs):
    result = st._main.radio(label, options, *args, **kwargs)
    if label == "¿Has hecho pliometría?":
        st._main.radio(
            "¿Has hecho series con arrastres?",
            ["Sí", "No"],
            horizontal=True,
            index=None,
            key="training_did_sled",
        )
    return result


st.radio = _radio_with_sled


def _button_require_sled(label, *args, **kwargs):
    clicked = st._main.button(label, *args, **kwargs)
    if label == "💾 Guardar entrenamiento" and clicked:
        if st.session_state.get("training_did_sled") not in {"Sí", "No"}:
            st.warning("Debes responder si has hecho series con arrastres antes de guardar.")
            return False
    return clicked


st.button = _button_require_sled


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
            display_tabs = st._main.tabs(display_values, *args, **kwargs)
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
                                [{"Fecha":r.get("session_date"),"Metros":r.get("volume_m"),"RPE":r.get("rpe"),"Comentarios":r.get("notes")} for r in sled_days],
                                use_container_width=True,
                                hide_index=True,
                            )
                        else:
                            st.info("Todavía no hay entrenamientos registrados con arrastres.")
                    except Exception as exc:
                        st.warning(f"No se pudieron cargar los arrastres: {exc}")
            return list(display_tabs[:insert_at]) + list(display_tabs[insert_at + 1:]) + [sled_tab]
    except Exception as exc:
        if "display_tabs" in locals():
            st.warning(f"No se pudo completar la pestaña de arrastres: {exc}")
            return list(display_tabs)
    return st._main.tabs(values, *args, **kwargs)


st.tabs = _tabs_with_sled
