import json
from pathlib import Path

import streamlit as st
from supabase import create_client


SESSION_FILE = Path(__file__).resolve().parent / ".supabase_session.json"


def create_supabase_client():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )


def get_supabase():
    if "supabase_client" not in st.session_state:
        client = create_supabase_client()

        if SESSION_FILE.exists():
            try:
                with SESSION_FILE.open("r", encoding="utf-8") as file:
                    saved_session = json.load(file)

                access_token = saved_session.get("access_token")
                refresh_token = saved_session.get("refresh_token")

                if access_token and refresh_token:
                    client.auth.set_session(
                        access_token,
                        refresh_token
                    )

            except Exception:
                # Invalid or expired saved sessions require login again.
                try:
                    SESSION_FILE.unlink(missing_ok=True)
                except OSError:
                    pass

        st.session_state.supabase_client = client

    return st.session_state.supabase_client


def save_auth_session(client):
    session = client.auth.get_session()

    if not session:
        return

    SESSION_FILE.write_text(
        json.dumps({
            "access_token": session.access_token,
            "refresh_token": session.refresh_token
        }),
        encoding="utf-8"
    )


def clear_auth_session():
    try:
        SESSION_FILE.unlink(missing_ok=True)
    except OSError:
        pass
