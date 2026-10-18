from html import escape

import streamlit as st

from models.user import User
from supabase_client import get_supabase, clear_auth_session

from ui.login import show_login, restore_profile, get_or_create_profile
from ui.home import show_home
from ui.assessment import show_assessment
from ui.tasks import show_tasks, load_tasks
from ui.workload import show_workload
from ui.recommendation import show_recommendation

st.set_page_config(
    page_title="Juggle",
    page_icon="assets/juggle_logo.png",
    layout="wide"
)

supabase = get_supabase()


# Main application styling
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Playfair+Display:wght@600;700&display=swap');

    /* Fonts */
    .stApp, .stApp p, .stApp label, .stApp input,
    .stApp textarea, .stApp button, [data-testid="stCaptionContainer"] {
        font-family: 'DM Sans', sans-serif;
    }

    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: #2B2620;
        letter-spacing: -0.2px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #EBE1CC;
        border-right: 1px solid #DDD0B5;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding: 2rem 1.5rem 0;
    }

    [data-testid="stSidebar"] h1 {
        text-align: center;
        margin-bottom: 0.5rem;
        font-size: 2rem;
        color: #2B2620;
    }

    [data-testid="stSidebar"] h1::after {
        content: "";
        display: block;
        width: 36px;
        height: 3px;
        margin: 10px auto 0;
        background: #D9A93B;
        border-radius: 2px;
    }

    [data-testid="stSidebar"] hr {
        border-color: #DDD0B5;
    }

    [data-testid="stSidebar"] .stButton {
        margin-bottom: 10px;
    }

    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        min-height: 44px;
        border-radius: 9px;
        font-weight: 500;
        transition: 0.15s;
    }

    [data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"] {
        background: transparent;
        border: 1px solid #D2C4A6;
        color: #2B2620;
    }

    [data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"]:hover {
        background: #F3EBDA;
        border-color: #D9A93B;
    }

    [data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] {
        background: #D9A93B;
        border: 1px solid #D9A93B;
        color: #2B2620;
        font-weight: 700;
    }

    /* Cards and metrics */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #FFFDF8;
        border: 1px solid #E3D8C3;
        border-radius: 12px;
    }

    [data-testid="stMetric"] {
        background: #FFFDF8;
        border: 1px solid #E3D8C3;
        border-left: 4px solid #D9A93B;
        border-radius: 10px;
        padding: 12px 16px;
    }

    /* Feedback messages */
    [data-testid="stAlert"] {
        background: #FBF3DC;
        border: 1px solid #EBD9A4;
        border-radius: 10px;
    }

    [data-testid="stAlert"] * {
        color: #5C4A14 !important;
    }

    /* Main page buttons */
    [data-testid="stMain"] button[data-testid^="stBaseButton-primary"] {
        background: #2B2620;
        border: none;
        color: #F6F1E7;
        font-weight: 600;
    }

    [data-testid="stMain"] button[data-testid^="stBaseButton-primary"]:hover {
        background: #D9A93B;
        color: #2B2620;
    }

    [data-testid="stMain"] button[data-testid^="stBaseButton-secondary"] {
        background: #FFFDF8;
        border: 1px solid #D9CCB2;
        color: #2B2620;
    }

    [data-testid="stMain"] button[data-testid^="stBaseButton-secondary"]:hover {
        border-color: #D9A93B;
        color: #2B2620;
    }

    .stButton > button {
        border-radius: 8px;
        min-height: 42px;
    }

    .stTextInput input, .stNumberInput input {
        border-radius: 8px;
    }

    [data-baseweb="select"] > div {
        border-radius: 8px;
    }

    div[role="radiogroup"] {
        gap: 8px;
    }

    hr {
        margin: 1.5rem 0;
        border-color: #E3D8C3;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Set default values without overwriting existing session data.
defaults = {
    "logged_in": False,
    "user_email": "",
    "user_id": None,
    "user": User("User"),
    "tasks": [],
    "available_time": 120,
    "available_time_error": "",
    "assessment_completed": False,
    "assessment_answers": {},
    "assessment_page_selected": False,
    "tasks_loaded_for_user": None,
    "activity": {},
    "page": "Assessment",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# Restore the authenticated user and their saved profile after a refresh.
def restore_login_from_supabase():
    try:
        auth_response = supabase.auth.get_user()
        auth_user = auth_response.user

        if auth_user is None:
            return False

        email = getattr(auth_user, "email", None)

        if not email:
            return False

        metadata = getattr(auth_user, "user_metadata", None) or {}

        if not isinstance(metadata, dict):
            metadata = {}

        name = (
            metadata.get("name")
            or metadata.get("full_name")
            or email.split("@")[0]
        )

        profile_data, name = get_or_create_profile(
            supabase,
            auth_user,
            email,
            name
        )

        st.session_state.user = User(name)
        st.session_state.user_id = auth_user.id
        st.session_state.user_email = email
        st.session_state.logged_in = True
        st.session_state.tasks = []
        st.session_state.tasks_loaded_for_user = None

        restore_profile(profile_data)

        return True

    except Exception:
        # If restoration fails, the login screen will be displayed.
        return False


# Show the login screen when no authenticated session can be restored.
if not st.session_state.logged_in:
    if not restore_login_from_supabase():
        show_login()
        st.stop()


# Load the current user's tasks once per login session.
user_id = st.session_state.get("user_id")

if (
    user_id
    and st.session_state.get("tasks_loaded_for_user") != user_id
):
    if load_tasks():
        st.session_state.tasks_loaded_for_user = user_id


assessment_completed = st.session_state.assessment_completed


# Require the assessment before allowing access to other pages.
if not assessment_completed:
    if st.session_state.page != "Assessment":
        st.session_state.page = "Assessment"
        st.rerun()

# Send returning users to Home after restoring their completed assessment.
elif (
    st.session_state.page == "Assessment"
    and not st.session_state.get("assessment_page_selected", False)
):
    st.session_state.page = "Home"
    st.rerun()


# Sidebar header and authenticated user's email.
st.sidebar.title("Juggle")

st.sidebar.markdown(
    "<div style='text-align:center; font-size:14px; color:#7A705F; "
    "word-break:break-all;'>"
    f"{escape(st.session_state.user_email)}</div>",
    unsafe_allow_html=True
)

st.sidebar.divider()


# Navigation available before the assessment is completed.
if not assessment_completed:
    st.sidebar.write("Complete the assessment to unlock Juggle.")

    if st.sidebar.button(
        "Assessment",
        use_container_width=True,
        type="primary"
    ):
        st.session_state.page = "Assessment"
        st.rerun()

# Navigation available after completing the assessment.
else:
    pages = [
        "Home",
        "My Tasks",
        "Assessment",
        "Workload Analysis",
        "Recommendation"
    ]

    for page_name in pages:
        if st.sidebar.button(
            page_name,
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.page == page_name
                else "secondary"
            )
        ):
            st.session_state.page = page_name
            st.session_state.assessment_page_selected = (
                page_name == "Assessment"
            )
            st.rerun()

# Sign out and clear the local application session.
if st.sidebar.button("Logout", use_container_width=True):
    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    clear_auth_session()

    for key in list(st.session_state.keys()):
        del st.session_state[key]

    st.rerun()

# Display the page selected in the sidebar.
page = st.session_state.page

if not assessment_completed:
    show_assessment()

elif page == "Home":
    show_home()

elif page == "My Tasks":
    show_tasks()

elif page == "Assessment":
    show_assessment()

elif page == "Workload Analysis":
    show_workload()

elif page == "Recommendation":
    show_recommendation()

else:
    st.session_state.page = "Home"
    st.rerun()