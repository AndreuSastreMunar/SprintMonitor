"""Pequeños ajustes de arranque para Sprint Monitor."""

import inspect

try:
    import streamlit as st

    _original_success = st.success

    def _success_with_cycle_redirect(body, *args, **kwargs):
        result = _original_success(body, *args, **kwargs)
        try:
            caller = inspect.currentframe().f_back
            if (
                body == "Registro guardado."
                and caller is not None
                and caller.f_code.co_name == "cycle"
            ):
                st.session_state.flash_message = "Ciclo menstrual guardado correctamente."
                st.session_state.view = "home"
                st.rerun()
        except Exception:
            pass
        return result

    st.success = _success_with_cycle_redirect
except Exception:
    pass
