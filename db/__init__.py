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
# entren en los cálculos de marcas.
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
