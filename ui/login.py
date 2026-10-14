
import re

import streamlit as st

from supabase_client import get_supabase, save_auth_session
from models.user import User


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 6


# Login interface
def show_login():
    st.markdown(
        "<h1 style='text-align:center; margin-bottom:0;'>Juggle</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='text-align:center; opacity:0.7;'>"
        "Personalized Workload Decision & Management System"
        "</p>",
        unsafe_allow_html=True
    )

    st.write("")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        with st.container(border=True):
            login_tab, signup_tab = st.tabs(["Login", "Create Account"])

            with login_tab:
                st.subheader("Welcome Back")

                with st.form("login_form"):
                    email = st.text_input(
                        "Email",
                        placeholder="you@example.com"
                    )
                    password = st.text_input(
                        "Password",
                        type="password"
                    )

                    submitted = st.form_submit_button(
                        "Login",
                        type="primary",
                        use_container_width=True
                    )

                if submitted:
                    login_user(email, password)

            with signup_tab:
                st.subheader("Create Your Account")

                with st.form("signup_form"):
                    name = st.text_input("Name")
                    email = st.text_input(
                        "Email",
                        placeholder="you@example.com"
                    )
                    password = st.text_input(
                        "Password",
                        type="password",
                        help=f"At least {MIN_PASSWORD_LENGTH} characters."
                    )
                    confirm_password = st.text_input(
                        "Confirm Password",
                        type="password"
                    )

                    submitted = st.form_submit_button(
                        "Create Account",
                        type="primary",
                        use_container_width=True
                    )

                if submitted:
                    create_account(
                        name,
                        email,
                        password,
                        confirm_password
                    )


# Set up the session after successful authentication
def start_session(user_id, email, name):
    st.session_state.user = User(name)
    st.session_state.user_id = user_id
    st.session_state.user_email = email
    st.session_state.logged_in = True

    st.session_state.tasks = []
    st.session_state.tasks_loaded_for_user = None

    st.session_state.available_time = 120
    st.session_state.available_time_input = 120
    st.session_state.available_time_error = ""


# Restore saved preferences and assessment results
def restore_profile(profile_data):
    from models.workstyle import WorkStyleProfile

    profile_data = profile_data or {}

    try:
        saved_time = int(profile_data.get("available_time") or 120)
    except (TypeError, ValueError):
        saved_time = 120

    saved_time = max(1, min(1440, saved_time))

    st.session_state.available_time = saved_time
    st.session_state.available_time_input = saved_time
    st.session_state.available_time_error = ""

    assessment_answers = profile_data.get("assessment_answers") or {}
    st.session_state.assessment_answers = assessment_answers

    style = profile_data.get("work_style")

    if style:
        work_time = profile_data.get("preferred_time") or 60
        preference = (
            profile_data.get("task_preference")
            or "Urgent tasks first"
        )

        profile = WorkStyleProfile(
            style,
            work_time,
            preference
        )

        st.session_state.user.set_work_style(profile)
        st.session_state.work_style = style
        st.session_state.assessment_completed = True
        st.session_state.page = "Home"
        st.session_state.assessment_page_selected = False

    else:
        st.session_state.assessment_completed = False
        st.session_state.page = "Assessment"
        st.session_state.assessment_page_selected = False


def get_user_metadata(auth_user):
    """Retrieve the name stored in Supabase Auth metadata."""

    metadata = getattr(auth_user, "user_metadata", None)

    if not isinstance(metadata, dict):
        return {}

    return metadata


# Load an existing database profile or create one for the user
def get_or_create_profile(supabase, auth_user, email, name):
    response = (
        supabase.table("users")
        .select("*")
        .eq("id", auth_user.id)
        .limit(1)
        .execute()
    )

    if response.data:
        profile_data = response.data[0]
        saved_name = profile_data.get("name")

        if isinstance(saved_name, str) and saved_name.strip():
            name = saved_name.strip()
        else:
            supabase.table("users").update({
                "name": name,
                "email": email
            }).eq("id", auth_user.id).execute()

            profile_data["name"] = name

        return profile_data, name

    supabase.table("users").insert({
        "id": auth_user.id,
        "email": email,
        "name": name,
        "available_time": 120
    }).execute()

    return {
        "id": auth_user.id,
        "email": email,
        "name": name,
        "available_time": 120
    }, name


# Validate credentials, authenticate, and restore the user's profile
def login_user(email, password):
    supabase = get_supabase()
    email = email.strip()

    if not email or not password:
        st.error("Please enter your email and password.")
        return

    if not EMAIL_PATTERN.match(email):
        st.error("Please enter a valid email address.")
        return

    with st.spinner("Logging in..."):
        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            auth_user = response.user

            if auth_user is None:
                st.error("Invalid email or password.")
                return

            # Keep the session available after a browser refresh.
            save_auth_session(supabase)

        except Exception as error:
            message = str(error).lower()

            if "not confirmed" in message:
                st.error(
                    "Please confirm your email first, then log in."
                )
            elif (
                "invalid" in message
                or "credentials" in message
                or "password" in message
            ):
                st.error("Invalid email or password.")
            else:
                st.error(
                    "Could not log in. Check your internet connection "
                    "and try again."
                )

            return

        metadata = get_user_metadata(auth_user)
        name = (
            metadata.get("name")
            or metadata.get("full_name")
            or email.split("@")[0]
        )

        try:
            profile_data, name = get_or_create_profile(
                supabase,
                auth_user,
                email,
                name
            )

        except Exception as error:
            st.error(
                "Your login succeeded, but your database profile could "
                "not be loaded. Check your users table and RLS policies."
            )
            st.caption(str(error))
            return

        start_session(auth_user.id, email, name)
        restore_profile(profile_data)

    st.rerun()


# Create a Supabase account and its corresponding user profile
def create_account(name, email, password, confirm_password):
    supabase = get_supabase()

    name = name.strip()
    email = email.strip()

    if not name or not email or not password or not confirm_password:
        st.error("Please complete all fields.")
        return

    if not EMAIL_PATTERN.match(email):
        st.error("Please enter a valid email address.")
        return

    if len(password) < MIN_PASSWORD_LENGTH:
        st.error(
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
        )
        return

    if password != confirm_password:
        st.error("Passwords do not match.")
        return

    with st.spinner("Creating your account..."):
        try:
            response = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "name": name,
                        "full_name": name
                    }
                }
            })

            auth_user = response.user

            if auth_user is None:
                st.error("Account could not be created.")
                return

            # Some Supabase projects require email confirmation first.
            if response.session is None:
                st.success(
                    "Account created. Check your email to confirm your "
                    "account, then log in."
                )
                return

            supabase.table("users").upsert({
                "id": auth_user.id,
                "email": email,
                "name": name,
                "available_time": 120
            }).execute()

            # Save the session if signup immediately authenticates the user.
            save_auth_session(supabase)

        except Exception as error:
            message = str(error).lower()

            if "already" in message or "registered" in message:
                st.error("An account with this email already exists.")
            else:
                st.error(
                    "Unable to create your account or save your profile."
                )
                st.caption(str(error))

            return

        start_session(auth_user.id, email, name)

        saved_profile = {
            "id": auth_user.id,
            "email": email,
            "name": name,
            "available_time": 120
        }

        restore_profile(saved_profile)

    st.rerun()
