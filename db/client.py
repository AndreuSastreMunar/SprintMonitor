import streamlit as st
from supabase import create_client, Client

def get_supabase() -> Client:
    # Un cliente por sesión de Streamlit. No usar st.cache_resource:
    # el cliente mantiene estado de autenticación.
    if "_supabase_client" not in st.session_state:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_ANON_KEY"]
        st.session_state["_supabase_client"] = create_client(url, key)
    return st.session_state["_supabase_client"]
