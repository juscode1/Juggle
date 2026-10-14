
import streamlit as st
from models.workstyle import WorkStyleProfile
from supabase_client import get_supabase


def show_assessment():
    st.title("Work Style Assessment")

    st.write(
        "Answer the questions below to determine how "
        "you prefer to manage your workload."
    )

    st.divider()

    q1 = st.radio(
        "1. You receive several tasks at once. What do you do?",
        [
            "Plan everything before starting.",
            "Start with a quick task to build momentum.",
            "Start with the task that is due soonest."
        ],
        key="assessment_q1"
    )

    q2 = st.radio(
        "2. How do you prefer to work?",
        [
            "Long, focused sessions.",
            "Short sessions with quick progress.",
            "I work best when there is a deadline."
        ],
        key="assessment_q2"
    )

    q3 = st.radio(
        "3. When a deadline is still far away, you usually:",
        [
            "Start early and plan ahead.",
            "Do smaller parts when I have time.",
            "Focus on it when the deadline gets closer."
        ],
        key="assessment_q3"
    )

    q4 = st.radio(
        "4. Which task would you choose first?",
        [
            "A difficult task that needs planning.",
            "A short task that I can finish quickly.",
            "A task that is due tomorrow."
        ],
        key="assessment_q4"
    )

    q5 = st.radio(
        "5. What motivates you to start working?",
        [
            "Having a clear plan.",
            "Seeing quick progress.",
            "Having an approaching deadline."
        ],
        key="assessment_q5"
    )

    st.divider()

    if st.button("Finish Assessment", use_container_width=True):

        planner_answers = {
            "Plan everything before starting.",
            "Long, focused sessions.",
            "Start early and plan ahead.",
            "A difficult task that needs planning.",
            "Having a clear plan."
        }

        starter_answers = {
            "Start with a quick task to build momentum.",
            "Short sessions with quick progress.",
            "Do smaller parts when I have time.",
            "A short task that I can finish quickly.",
            "Seeing quick progress."
        }

        answers = [q1, q2, q3, q4, q5]

        planner = sum(
            answer in planner_answers
            for answer in answers
        )

        starter = sum(
            answer in starter_answers
            for answer in answers
        )

        deadline = 5 - planner - starter

        if planner >= starter and planner >= deadline:
            style = "Focused Planner"
            work_time = 90
            preference = "Most important tasks first"

        elif starter >= planner and starter >= deadline:
            style = "Quick Starter"
            work_time = 30
            preference = "Short tasks first"

        else:
            style = "Deadline Driven"
            work_time = 60
            preference = "Urgent tasks first"

        user_id = st.session_state.get("user_id")

        if not user_id:
            st.error("Your session has expired. Please log in again.")
            return

        assessment_answers = {
            "q1": q1,
            "q2": q2,
            "q3": q3,
            "q4": q4,
            "q5": q5
        }

        assessment_data = {
            "assessment_answers": assessment_answers,
            "work_style": style,
            "preferred_time": work_time,
            "task_preference": preference
        }

        try:
            supabase = get_supabase()

            supabase.table("users").update(
                assessment_data
            ).eq("id", user_id).execute()

        except Exception:
            st.error(
                "Your assessment could not be saved. "
                "Please try again."
            )
            return

        profile = WorkStyleProfile(
            style,
            work_time,
            preference
        )

        st.session_state.user.set_work_style(profile)
        st.session_state.assessment_answers = assessment_answers
        st.session_state.assessment_completed = True
        st.session_state.work_style = style
        st.session_state.page = "Home"

        st.rerun()
