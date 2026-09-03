"""Interfaz de gestión de atletas desde la pantalla principal del entrenador."""

import streamlit as st

from . import client as _client


def _coach_profile():
    profile = st.session_state.get("profile") or {}
    return profile if isinstance(profile, dict) else {}


def _render_manager():
    st.markdown("### 👥 Gestionar atletas")
    st.caption("Añade deportistas por email o elimina tu vinculación con ellos. Un mismo atleta puede estar vinculado a varios entrenadores.")

    supabase = _client.get_supabase()

    with st.container(border=True):
        st.markdown("#### Añadir atleta")
        email = st.text_input(
            "Email del atleta",
            key="coach_manage_athlete_email",
            placeholder="atleta@correo.com",
        )
        if st._main.button(
            "Añadir a Mis atletas",
            key="coach_manage_add_athlete",
            use_container_width=True,
        ):
            if not email.strip():
                st.warning("Introduce el email del atleta.")
            else:
                try:
                    supabase.rpc(
                        "coach_add_athlete_by_email",
                        {"athlete_email": email.strip()},
                    ).execute()
                    st.success("Atleta añadido correctamente.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"No se pudo añadir el atleta: {exc}")

    st.markdown("#### Atletas vinculados")
    try:
        athletes = supabase.rpc("coach_my_athletes").execute().data or []
    except Exception as exc:
        st.warning(
            "No se pudo cargar la gestión de atletas. Ejecuta primero "
            "db/013_coach_manage_athletes.sql en Supabase."
        )
        st.caption(str(exc))
        athletes = []

    if not athletes:
        st.info("Todavía no tienes atletas vinculados.")
    else:
        for athlete in athletes:
            athlete_id = athlete.get("id")
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**{athlete.get('full_name') or athlete.get('email') or 'Atleta'}**")
                    details = [athlete.get("email"), athlete.get("specialty")]
                    st.caption(" · ".join(str(x) for x in details if x))
                with c2:
                    if st._main.button(
                        "Quitar",
                        key=f"coach_manage_remove_{athlete_id}",
                        use_container_width=True,
                    ):
                        try:
                            supabase.rpc(
                                "coach_remove_athlete",
                                {"athlete_uuid": athlete_id},
                            ).execute()
                            selected = st.session_state.get("selected_athlete") or {}
                            if isinstance(selected, dict) and selected.get("id") == athlete_id:
                                st.session_state.pop("selected_athlete", None)
                            st.success("Atleta eliminado de tu grupo.")
                            st.rerun()
                        except Exception as exc:
                            st.error(f"No se pudo quitar el atleta: {exc}")

    if st._main.button(
        "Cerrar gestión de atletas",
        key="coach_manage_close",
        use_container_width=True,
    ):
        st.session_state["coach_manage_open"] = False
        st.rerun()


def install_coach_manager():
    if getattr(st, "_sprint_monitor_coach_manager_installed", False):
        return

    original_button = st.button

    def button_with_coach_manager(label, *args, **kwargs):
        # coach_home siempre termina llamando a este botón después de las tarjetas.
        # Aprovechamos ese punto para añadir una tercera acción sin alterar app.py.
        if label == "Cerrar sesión" and _coach_profile().get("role") == "coach":
            if st.session_state.get("coach_manage_open"):
                _render_manager()
            else:
                if st._main.button(
                    "👥 Gestionar atletas",
                    key="coach_manage_open_button",
                    use_container_width=True,
                ):
                    st.session_state["coach_manage_open"] = True
                    st.rerun()
        return original_button(label, *args, **kwargs)

    st.button = button_with_coach_manager
    st._sprint_monitor_coach_manager_installed = True
