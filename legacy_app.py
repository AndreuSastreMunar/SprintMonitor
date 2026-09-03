from datetime import date
import pandas as pd
import streamlit as st
from db.client import get_supabase

# Icono propio CTEIB Velocistas para pestaña/navegador y acceso desde móvil.
# Se usa un SVG embebido para no depender del icono por defecto de Streamlit.
CTEIB_APP_ICON = "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'><defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'><stop stop-color='%235612d6'/><stop offset='1' stop-color='%23ff0b68'/></linearGradient></defs><rect width='512' height='512' rx='110' fill='url(%23g)'/><g fill='white'><circle cx='330' cy='112' r='42'/><path d='M286 156c-31 4-55 19-73 46l-33 49-70 18 13 35 88-21 35-48 31 30-38 61-72 63 27 30 85-71 49-75 46 39 24-29-68-62-39-59c-11-17-28-28-45-30z'/><path d='M91 214h93v17H91zm-25 38h101v17H66zm12 38h70v17H78z'/></g><text x='256' y='456' text-anchor='middle' fill='white' font-family='Arial,sans-serif' font-size='48' font-weight='900'>CTEIB</text></svg>"

st.set_page_config(page_title="CTEIB Velocistas", page_icon=CTEIB_APP_ICON, layout="centered", initial_sidebar_state="collapsed")
st.markdown("""
<style>
.block-container{max-width:760px;padding-top:1rem;padding-bottom:3rem} section[data-testid="stSidebar"]{display:none}
.hero{margin:.2rem 0 1rem}.brand{font-size:.9rem;font-weight:800;letter-spacing:.14em;opacity:.65}.hello{font-size:2rem;font-weight:850;line-height:1.05;margin-top:.3rem}.sub{opacity:.6;margin-top:.25rem}
.menu-card{border:1px solid rgba(0,0,0,.08);border-radius:24px;padding:1.05rem;min-height:145px;box-shadow:0 8px 24px rgba(0,0,0,.08);background:linear-gradient(180deg,#fff,#f7f8fa);margin-bottom:.45rem}
.menu-icon{font-size:2rem}.menu-title{font-size:1.15rem;font-weight:800;margin-top:.35rem}.menu-sub{font-size:.9rem;opacity:.65;margin-top:.2rem}.menu-num{display:inline-flex;width:34px;height:34px;border-radius:50%;align-items:center;justify-content:center;background:#111827;color:white;font-weight:800;margin-top:.75rem}
.stButton>button{border-radius:16px;min-height:46px;font-weight:700;width:100%} div[data-testid="stForm"]{border-radius:22px;padding:1rem}
@media(max-width:640px){.block-container{padding-left:.85rem;padding-right:.85rem}.hello{font-size:1.7rem}.menu-card{min-height:132px}}
</style>""", unsafe_allow_html=True)

supabase=get_supabase()
WELLNESS_LABELS={"sleep":"Sueño","fatigue":"Fatiga","muscle_soreness":"Dolor muscular","stress":"Estrés","readiness":"Disposición para entrenar"}
HEALTH_LABELS={
    "completed_no_problem":"Completado sin problemas de salud",
    "completed_with_health_problem":"Completado con algún problema de salud",
    "adapted_due_health_problem":"Adaptado por problemas de salud",
    "not_completed_due_health_problem":"No completado por problemas de salud",
}
MARK_EVENTS=["60m","100m","200m","400m"]
SEASON_START_MONTH=8

def get_profile(uid):
    return supabase.table("profiles").select("*").eq("id",uid).single().execute().data

def sign_out():
    try: supabase.auth.sign_out()
    except Exception: pass
    for k in ["user","profile","view","blocks","selected_athlete","training_did_gym","training_did_plyo","health_completed_ok","health_reason"]:
        st.session_state.pop(k,None)
    st.rerun()

def go_home_with_message(message):
    st.session_state.flash_message=message
    st.session_state.view="home"
