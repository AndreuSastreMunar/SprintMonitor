"""Utilidades y compatibilidad de interfaz para Sprint Monitor."""

import builtins
import inspect

import streamlit as st

_BASE_MARK_EVENTS = ["60m", "100m", "200m", "400m"]
_HURDLE_EVENTS = ["60m vallas", "110m vallas"]

# Amplía los selectores existentes de prueba y especialidad.
_original_selectbox_hurdles = st.selectbox


def _selectbox_with_hurdles(label, options, *args, **kwargs):
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
    return _original_selectbox_hurdles(label, values, *args, **kwargs)


st.selectbox = _selectbox_with_hurdles

# db.client captura st.selectbox al importarse, así se conservan todos los
# parches previos de fechas, perfil, foto, 400 m, etc.
from . import client as _client  # noqa: E402

# Las pantallas de marcas recorren la lista histórica de cuatro pruebas con
# enumerate(). Solo en ese contexto ampliamos el recorrido con las vallas.
_original_enumerate_hurdles = builtins.enumerate


def _enumerate_with_hurdles(iterable, *args):
    try:
        caller = inspect.currentframe().f_back
        if (
            caller is not None
            and caller.f_code.co_name in {"_render_marks", "_render_marks_season"}
            and list(iterable) == _BASE_MARK_EVENTS
        ):
            iterable = _BASE_MARK_EVENTS + _HURDLE_EVENTS
    except Exception:
        pass
    return _original_enumerate_hurdles(iterable, *args)


builtins.enumerate = _enumerate_with_hurdles

# Las consultas que calculan marcas filtran por la lista histórica de cuatro
# pruebas. Ampliamos únicamente el filtro de la columna `event`.
_original_get_supabase_hurdles = _client.get_supabase


def _get_supabase_with_hurdles():
    client = _original_get_supabase_hurdles()
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
