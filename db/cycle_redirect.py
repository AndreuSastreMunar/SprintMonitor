"""Redirección al inicio tras guardar un registro del ciclo menstrual."""

import inspect
import streamlit as st

from .multi_coach import install_multi_coach_support
from .coach_manager import install_coach_manager


def install_cycle_success_redirect():
    install_multi_coach_support()
    install_coach_manager()

    if hasattr(st, "_sprint_monitor_cycle_success_installed"):
        return

    original_success = st.success

    def success_with_cycle_redirect(body, *args, **kwargs):
        result = original_success(body, *args, **kwargs)
        caller = inspect.currentframe().f_back
        if body == "Registro guardado." and caller is not None and caller.f_code.co_name == "cycle":
            st.session_state.flash_message = "Ciclo menstrual guardado correctamente."
            st.session_state.view = "home"
            st.rerun()
        return result

    st.success = success_with_cycle_redirect
    st._sprint_monitor_cycle_success_installed = True
