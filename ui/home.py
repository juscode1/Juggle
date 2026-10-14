
import streamlit as st
from services.workload_analyzer import WorkloadAnalyzer
from ui.activity import show_activity_heatmap
from ui.styles import priority_badge, chip, to_date, today_manila
from supabase_client import get_supabase

PREVIEW_LIMIT = 3
OVERDUE_COLOR = "#E05252"
DUE_TODAY_COLOR = "#D99A00"


# Shows a short task preview and highlights the recommended task.
def show_task_preview(
    task_list,
    empty_message,
    button_label,
    button_key,
    completed=False,
    selected_task_name=None
):
    if not task_list:
        st.info(empty_message)
        return

    preview_tasks = list(task_list)

    # Put the selected recommendation first in the ongoing list.
    if not completed and selected_task_name is not None:
        selected_task = next(
            (
                task for task in preview_tasks
                if getattr(task, "name", "") == selected_task_name
            ),
            None
        )

        if selected_task is not None:
            preview_tasks.remove(selected_task)
            preview_tasks.insert(0, selected_task)

    preview_tasks = preview_tasks[:PREVIEW_LIMIT]
    today = today_manila()

    for index, task in enumerate(preview_tasks):
        name = getattr(task, "name", "Unnamed Task")
        subject = getattr(task, "subject", "Unknown")
        priority = getattr(task, "priority", "Unknown")
        duration = getattr(task, "duration", 0)
        deadline = to_date(getattr(task, "deadline", None))

        # Only unfinished tasks can be overdue or due today.
        is_overdue = (
            not completed
            and deadline is not None
            and deadline < today
        )

        is_due_today = (
            not completed
            and deadline is not None
            and deadline == today
        )

        is_selected = (
            not completed
            and index == 0
            and selected_task_name is not None
            and name == selected_task_name
        )

        with st.container(border=True):
            col1, col2 = st.columns([3, 2])

            with col1:
                if completed:
                    st.markdown(f"~~{name}~~")
                    st.caption(
                        f"✓ {subject} · {duration} min · Completed"
                    )
                else:
                    st.markdown(f"**{name}**")
                    st.caption(f"{subject} · {duration} min")

                    if is_overdue:
                        st.markdown(
                            f'<span style="color:{OVERDUE_COLOR};'
                            'font-weight:600;">'
                            '⚠ Overdue</span>',
                            unsafe_allow_html=True
                        )
                    elif is_due_today:
                        st.markdown(
                            f'<span style="color:{DUE_TODAY_COLOR};'
                            'font-weight:600;">'
                            'Due today</span>',
                            unsafe_allow_html=True
                        )

            with col2:
                if not completed:
                    extra = ""

                    if is_selected:
                        extra = (
                            '<div style="margin-top:6px;">'
                            '<span style="display:inline-block;'
                            'background-color:rgba(57,230,138,0.12);'
                            'color:#39e68a;'
                            'border:1px solid rgba(57,230,138,0.45);'
                            'border-radius:999px;padding:4px 12px;'
                            'font-size:13px;font-weight:600;'
                            'white-space:nowrap;">'
                            'task to finish first</span></div>'
                        )

                    st.markdown(
                        '<div style="text-align:right;">'
                        f'{priority_badge(priority)}{extra}</div>',
                        unsafe_allow_html=True
                    )

    total = len(task_list)

    if total > PREVIEW_LIMIT:
        st.caption(f"Showing {PREVIEW_LIMIT} of {total} tasks")

    if st.button(
        f"{button_label} ({total})",
        key=button_key,
        use_container_width=True
    ):
        st.session_state.page = "My Tasks"
        st.rerun()


# Saves today's available work time to the logged-in user's profile.
def save_available_time():
    available_time = int(st.session_state.available_time_input)
    user_id = st.session_state.get("user_id")

    if not user_id:
        st.session_state.available_time_error = (
            "Your session is missing. Please log in again."
        )
        return

    try:
        (
            get_supabase()
            .table("users")
            .update({"available_time": available_time})
            .eq("id", user_id)
            .execute()
        )

        st.session_state.available_time = available_time
        st.session_state.available_time_error = ""

    except Exception as e:
        st.session_state.available_time_error = (
            f"Could not save available time: {e}"
        )


# Main Home dashboard.
def show_home():
    st.title("Welcome to Juggle")
    st.write("Your personalized workload dashboard.")

    user = st.session_state.get("user")
    tasks = st.session_state.get("tasks", [])

    ongoing_tasks = [
        task for task in tasks
        if not getattr(task, "completed", False)
    ]

    completed_tasks = [
        task for task in tasks
        if getattr(task, "completed", False)
    ]

    # Count deadlines using the same date rules as the task previews.
    today = today_manila()
    due_today = 0
    overdue = 0

    for task in ongoing_tasks:
        deadline = to_date(getattr(task, "deadline", None))

        if deadline is None:
            continue

        if deadline == today:
            due_today += 1
        elif deadline < today:
            overdue += 1

    st.divider()

    profile = None

    if user is not None:
        profile = getattr(user, "work_style", None)

    style_col, overview_col = st.columns(2)

    with style_col:
        st.subheader("Your Work Style")

        if profile is not None:
            st.markdown(
                '<div style="display:flex;gap:12px;flex-wrap:wrap;">'
                f'{chip("Work Style", profile.style)}'
                f'{chip("Task Preference", profile.taskpreference)}'
                '</div>',
                unsafe_allow_html=True
            )
        else:
            st.info(
                "Complete the Work Style Assessment "
                "to discover your work style."
            )

    with overview_col:
        st.subheader("Task Overview")

        st.markdown(
            '<div style="display:flex;gap:12px;flex-wrap:wrap;">'
            f'{chip("Ongoing", len(ongoing_tasks))}'
            f'{chip("Completed", len(completed_tasks))}'
            f'{chip("Due today", due_today)}'
            f'{chip("Overdue", overdue, OVERDUE_COLOR if overdue else None)}'
            '</div>',
            unsafe_allow_html=True
        )

    st.divider()
    st.subheader("My Tasks")

    if tasks:
        selected_task_name = st.session_state.get("selected_task_name")

        ongoing_col, completed_col = st.columns(2)

        with ongoing_col:
            st.write("### Ongoing Tasks")

            show_task_preview(
                ongoing_tasks,
                "No ongoing tasks.",
                "View all ongoing",
                "view_all_ongoing",
                selected_task_name=selected_task_name
            )

        with completed_col:
            st.write("### Completed Tasks")

            show_task_preview(
                completed_tasks,
                "No completed tasks.",
                "View all completed",
                "view_all_completed",
                completed=True
            )
    else:
        st.info(
            "You don't have any tasks yet. "
            "Add a task from My Tasks."
        )

    st.divider()

    workload_col, activity_col = st.columns(2)

    with workload_col:
        st.write("### Workload Overview")

        # Keep the input tied to the saved available-time value.
        if "available_time_input" not in st.session_state:
            st.session_state.available_time_input = (
                st.session_state.get("available_time", 120)
            )

        available_time = st.number_input(
            "Available Time Today (minutes)",
            min_value=1,
            max_value=1440,
            step=15,
            key="available_time_input",
            on_change=save_available_time
        )

        st.session_state.available_time = available_time

        if st.session_state.get("available_time_error"):
            st.error(st.session_state.available_time_error)

        if tasks:
            try:
                analyzer = WorkloadAnalyzer(tasks, available_time)
                workload = analyzer.calculate_workload()
                remaining_time = available_time - workload

                workload_col1, workload_col2 = st.columns(2)

                with workload_col1:
                    st.write("Total Workload")
                    st.markdown(f"### {workload} min")

                with workload_col2:
                    st.write("Remaining Time")

                    if remaining_time >= 0:
                        st.markdown(f"### {remaining_time} min")
                    else:
                        st.markdown(f"### {abs(remaining_time)} min over")

                if workload > available_time:
                    st.error(
                        f"Your workload exceeds your "
                        f"available time by "
                        f"{abs(remaining_time)} minutes."
                    )
                elif workload == available_time:
                    st.warning(
                        "Your workload exactly matches "
                        "your available time."
                    )
                else:
                    st.success(
                        f"You have {remaining_time} "
                        f"minutes remaining."
                    )

            except Exception:
                st.error("Unable to calculate your workload.")
        else:
            st.info("Add tasks to calculate your workload.")

    with activity_col:
        st.write("### Activity")
        show_activity_heatmap()
        st.caption("Completed tasks so far")
