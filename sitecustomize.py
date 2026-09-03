"""Pequeños ajustes de arranque para Sprint Monitor."""

import importlib.util
import inspect
from pathlib import Path

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

    # Login base.
    try:
        login_path = Path(__file__).resolve().parent / "db" / "login_branding.py"
        login_spec = importlib.util.spec_from_file_location("sprintmonitor_login_branding", login_path)
        if login_spec and login_spec.loader:
            login_branding = importlib.util.module_from_spec(login_spec)
            login_spec.loader.exec_module(login_branding)
            login_branding.install_login_branding()
    except Exception:
        pass

    # Branding general para el resto de la aplicación.
    try:
        branding_path = Path(__file__).resolve().parent / "db" / "visual_branding.py"
        spec = importlib.util.spec_from_file_location("sprintmonitor_visual_branding", branding_path)
        if spec and spec.loader:
            branding = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(branding)
            branding.install_visual_branding()
    except Exception:
        pass

    # Última capa: se instala después de todo lo anterior y sustituye la
    # cabecera antigua del login por el diseño móvil CTEIB Velocistas.
    try:
        final_login_path = Path(__file__).resolve().parent / "db" / "login_final_patch.py"
        final_login_spec = importlib.util.spec_from_file_location("sprintmonitor_login_final_patch", final_login_path)
        if final_login_spec and final_login_spec.loader:
            final_login = importlib.util.module_from_spec(final_login_spec)
            final_login_spec.loader.exec_module(final_login)
            final_login.install_login_final_patch()
    except Exception:
        pass
except Exception:
    pass
