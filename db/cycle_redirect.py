"""Redirección al inicio tras guardar un registro del ciclo menstrual."""

import inspect
import streamlit as st

from .multi_coach import install_multi_coach_support
from .coach_manager import install_coach_manager
from .chart_style import install_chart_style


def install_cycle_success_redirect():
    install_multi_coach_support()
    install_coach_manager()
    install_chart_style()

    if hasattr(st, "_sprint_monitor_cycle_success_installed"):
        return

    # Los botones de navegación hacia atrás son el primer elemento de varias
    # pantallas. En Streamlit Community Cloud podían quedar parcialmente
    # ocultos bajo la cabecera superior. Añadimos espacio únicamente delante
    # de esos botones, sin desplazar el resto de botones de la aplicación.
    original_button = st.button

    def button_with_back_spacing(label, *args, **kwargs):
        if isinstance(label, str) and label.startswith("← "):
            st.markdown(
                '<div style="height:2.25rem"></div>',
                unsafe_allow_html=True,
            )
        return original_button(label, *args, **kwargs)

    st.button = button_with_back_spacing

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
