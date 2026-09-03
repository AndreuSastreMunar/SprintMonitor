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


class _SupabaseProxy:
    def __init__(self, client):
        self._client = client

    def __getattr__(self, name):
        return getattr(self._client, name)

    def table(self, table_name, *args, **kwargs):
        builder = self._client.table(table_name, *args, **kwargs)
        if table_name == "training_sessions":
            return _TrainingTableProxy(builder)
        return builder


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
    return _SupabaseProxy(client)


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
                            sled_df = pd.DataFrame(
                                [
                                    {
                                        "session_date": r.get("session_date"),
                                        "volume_m": r.get("volume_m"),
                                        "rpe": r.get("rpe"),
                                        "notes": r.get("notes"),
                                    }
                                    for r in sled_days
                                ]
                            )
                            sled_df["session_date"] = pd.to_datetime(
                                sled_df["session_date"], errors="coerce"
                            ).dt.strftime("%d/%m/%Y")
                            st.dataframe(
                                sled_df,
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


# Referencias visuales para los sliders de Wellness.
if not hasattr(st, "_sprint_monitor_base_slider"):
    st._sprint_monitor_base_slider = st.slider

_WELLNESS_SLIDER_REFERENCES = {
    "Sueño": ("Muy bueno", "Muy malo"),
    "Fatiga": ("Muy bajo", "Muy alto"),
    "Dolor muscular": ("Muy bajo", "Muy alto"),
    "Estrés": ("Muy bajo", "Muy alto"),
    "Disposición para entrenar": ("Muy bajo", "Muy alto"),
}


def _slider_with_wellness_references(label, *args, **kwargs):
    value = st._sprint_monitor_base_slider(label, *args, **kwargs)
    references = _WELLNESS_SLIDER_REFERENCES.get(label)
    if references:
        left, right = references
        st.markdown(
            f'<div style="display:flex;justify-content:space-between;margin-top:-0.65rem;margin-bottom:0.7rem;font-size:0.82rem;opacity:0.72;"><span>{left}</span><span>{right}</span></div>',
            unsafe_allow_html=True,
        )
    return value


st.slider = _slider_with_wellness_references


# Evita que el formulario de Mi perfil use la misma clave que
# st.session_state.profile, que contiene los datos del usuario.
if not hasattr(st, "_sprint_monitor_base_form"):
    st._sprint_monitor_base_form = st.form


def _form_without_profile_key_collision(key, *args, **kwargs):
    if key == "profile":
        key = "profile_form"
    return st._sprint_monitor_base_form(key, *args, **kwargs)


st.form = _form_without_profile_key_collision


# En un st.form los cambios de un checkbox no fuerzan un rerun inmediato.
# Por eso el campo "Fin de la menstruación" podía quedar deshabilitado aunque
# se marcase "Ya ha finalizado". Lo mantenemos editable y, si no ha finalizado,
# app.py seguirá guardando end_date como None.
if not hasattr(st, "_sprint_monitor_base_date_input"):
    st._sprint_monitor_base_date_input = st.date_input


def _date_input_cycle_end_enabled(label, *args, **kwargs):
    if label == "Fin de la menstruación":
        kwargs["disabled"] = False
    return st._sprint_monitor_base_date_input(label, *args, **kwargs)


st.date_input = _date_input_cycle_end_enabled


from .cycle_redirect import install_cycle_success_redirect
install_cycle_success_redirect()
