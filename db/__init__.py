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


# Antes de importar db.client ampliamos los selectores globales.
_selectbox_before_client = st.selectbox


def _selectbox_before_import(label, options, *args, **kwargs):
    return _selectbox_before_client(label, _extend_options(label, options), *args, **kwargs)


st.selectbox = _selectbox_before_import

from . import client as _client  # noqa: E402

# db.client instala sus propios wrappers, así que encadenamos los nuestros después.
_selectbox_after_client = st.selectbox


def _selectbox_with_hurdles(label, options, *args, **kwargs):
    return _selectbox_after_client(label, _extend_options(label, options), *args, **kwargs)


st.selectbox = _selectbox_with_hurdles

_delta_selectbox_original = DeltaGenerator.selectbox


def _delta_selectbox_with_hurdles(self, label, options, *args, **kwargs):
    return _delta_selectbox_original(self, label, _extend_options(label, options), *args, **kwargs)


if not getattr(DeltaGenerator.selectbox, "_sprint_monitor_hurdles", False):
    _delta_selectbox_with_hurdles._sprint_monitor_hurdles = True
    DeltaGenerator.selectbox = _delta_selectbox_with_hurdles

# app.py conserva MARK_EVENTS con las cuatro pruebas originales. Ampliamos
# únicamente los recorridos que dibujan marcas para incluir vallas.
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

# También ampliamos el filtro de competiciones para que las pruebas de vallas
# entren en los cálculos de marcas. En la misma capa añadimos did_sled a las
# inserciones de training_sessions sin tener que duplicar la lógica de app.py.
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

# Corrección definitiva de Mi perfil: usamos el título nativo y mostramos solo
# la foto. Así evitamos que el wrapper antiguo de db.client añada Marcas.
_title_after_client = st.title


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
    return _title_after_client(body, *args, **kwargs)


st.title = _title_without_profile_marks

# Trabajo complementario: añadimos la tercera pregunta justo después de
# pliometría. La respuesta es obligatoria antes de guardar el entrenamiento.
_radio_after_client = st.radio


def _radio_with_sled(label, options, *args, **kwargs):
    result = _radio_after_client(label, options, *args, **kwargs)
    if label == "¿Has hecho pliometría?":
        _radio_after_client(
            "¿Has hecho series con arrastres?",
            ["Sí", "No"],
            horizontal=True,
            index=None,
            key="training_did_sled",
        )
    return result


st.radio = _radio_with_sled

_button_after_client = st.button


def _button_require_sled(label, *args, **kwargs):
    clicked = _button_after_client(label, *args, **kwargs)
    if label == "💾 Guardar entrenamiento" and clicked:
        if st.session_state.get("training_did_sled") not in {"Sí", "No"}:
            st.warning("Debes responder si has hecho series con arrastres antes de guardar.")
            return False
    return clicked


st.button = _button_require_sled

# Al guardar correctamente un entrenamiento limpiamos también esta respuesta
# para que en la siguiente sesión vuelva a ser obligatoria.
_rerun_after_client = st.rerun


def _rerun_clear_sled(*args, **kwargs):
    if st.session_state.get("flash_message") == "Entrenamiento guardado correctamente.":
        st.session_state.pop("training_did_sled", None)
    return _rerun_after_client(*args, **kwargs)


st.rerun = _rerun_clear_sled

# Ficha del entrenador: mostramos Arrastres entre Series y Gimnasio. Para no
# romper los índices que app.py usa para el resto de pestañas, devolvemos los
# tabs en el orden lógico antiguo y dejamos Arrastres como tab adicional al final
# de la lista devuelta, aunque visualmente aparezca en la posición deseada.
_tabs_after_client = st.tabs


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
            display_tabs = _tabs_after_client(display_values, *args, **kwargs)
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

            # app.py espera que tabs[3] siga siendo Gimnasio, tabs[4]
            # Pliometría, etc. Reordenamos solo la lista devuelta, no la vista.
            logical_tabs = display_tabs[:insert_at] + display_tabs[insert_at + 1:] + [sled_tab]
            return logical_tabs
    except Exception:
        pass
    return _tabs_after_client(values, *args, **kwargs)


st.tabs = _tabs_with_sled
