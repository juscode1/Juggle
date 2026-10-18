import streamlit as st
from supabase import create_client


def create_supabase_client():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )


def get_supabase():
    if "supabase_client" not in st.session_state:
        st.session_state.supabase_client = create_supabase_client()

    return st.session_state.supabase_client


def clear_auth_session():
    client = st.session_state.get("supabase_client")

    if client is not None:
        try:
            client.auth.sign_out()
        except Exception:
            pass

    st.session_state.pop("supabase_client", None)
