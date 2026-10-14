import streamlit as st

from services.workload_analyzer import WorkloadAnalyzer


def show_recommendation():
    st.title("Recommendation")

    st.write(
        "Juggle analyzes your unfinished tasks and recommends "
        "what to do first based on your priority, deadline, "
        "available time, and work style."
    )

    st.divider()

    tasks = st.session_state.get("tasks", [])
    available_time = st.session_state.get("available_time", 120)

    analyzer = WorkloadAnalyzer(tasks, available_time)
    ranked_tasks = analyzer.rank_tasks()

    selected_task = st.session_state.get("selected_task")

    # Remove the saved selection if the task is no longer available.
    if selected_task is not None:
        still_available = any(
            task is selected_task for task in ranked_tasks
        )

        if not still_available:
            st.session_state.pop("selected_task", None)
            st.session_state.pop("selected_task_name", None)
            selected_task = None

    if not tasks:
        st.info("Add tasks before requesting a recommendation.")
        return

    if not ranked_tasks:
        st.session_state.pop("selected_task", None)
        st.session_state.pop("selected_task_name", None)

        st.success("You have completed all of your tasks.")
        return

    # Display the user's work style, if the assessment is completed.
    user = st.session_state.get("user")
    profile = getattr(user, "work_style", None) if user else None

    st.subheader("Your Work Style")

    if profile is not None:
        st.write(profile.style)
    else:
        st.info(
            "Complete the Work Style Assessment "
            "to personalize your recommendations."
        )

    st.divider()

    workload = analyzer.calculate_workload()
    remaining_time = available_time - workload

    # Compare the total task duration with the available time.
    st.subheader("Workload Status")

    col1, col2 = st.columns(2)

    with col1:
        st.write("Total Workload")
        st.markdown(f"### {workload:g} min")

    with col2:
        st.write("Available Time")
        st.markdown(f"### {available_time:g} min")

    if workload > available_time:
        st.error(
            f"Your workload exceeds your available "
            f"time by {abs(remaining_time):g} minutes."
        )

        st.write(
            "Consider prioritizing urgent and high-priority "
            "tasks and moving lower-priority tasks to another time."
        )

    elif workload == available_time:
        st.warning(
            "Your workload exactly matches your available time."
        )

        st.write(
            "You can complete your current tasks, "
            "but you have no extra time available."
        )

    else:
        st.success(
            f"Your workload fits within your available time. "
            f"You have {remaining_time:g} minutes remaining."
        )

    st.divider()

    # Show the tasks in the order determined by WorkloadAnalyzer.
    st.subheader("Recommended Task Order")

    for index, task in enumerate(ranked_tasks, start=1):
        name = getattr(task, "name", "Unnamed Task")
        subject = getattr(task, "subject", "Unknown")
        priority = getattr(task, "priority", "Unknown")
        duration = analyzer.get_duration(task)
        deadline = getattr(task, "deadline", "Unknown")

        with st.container(border=True):
            st.markdown(f"### {index}. {name}")

            st.caption(
                f"{subject} | {priority} priority | "
                f"{duration:g} minutes | Due {deadline}"
            )

            if selected_task is task:
                st.success("Selected starting task")
            elif selected_task is None and index == 1:
                st.success("Recommended starting task")

            st.write("**Why this task?**")
            st.write(analyzer.get_reason(task))

    st.divider()

    # Let the user choose a different starting task.
    st.subheader("Choose Your Starting Task")

    def format_task(task):
        name = getattr(task, "name", "Unnamed Task")
        priority = getattr(task, "priority", "Unknown")
        duration = analyzer.get_duration(task)
        deadline = getattr(task, "deadline", "Unknown")

        return (
            f"{name} | {priority} priority | "
            f"{duration:g} minutes | Due {deadline}"
        )

    default_index = 0

    if selected_task is not None:
        for index, task in enumerate(ranked_tasks):
            if task is selected_task:
                default_index = index
                break

    task_signature = tuple(id(task) for task in ranked_tasks)

    widget_key = (
        "recommendation_task_"
        + "_".join(map(str, task_signature))
    )

    chosen_task = st.selectbox(
        "You can choose a different task if you prefer.",
        options=ranked_tasks,
        index=default_index,
        format_func=format_task,
        key=widget_key
    )

    st.divider()

    if st.button("Use This Task", use_container_width=True):
        if getattr(chosen_task, "completed", False):
            st.session_state.pop("selected_task", None)
            st.session_state.pop("selected_task_name", None)

            st.warning(
                "This task has already been completed. "
                "Choose another unfinished task."
            )
            st.rerun()

        st.session_state.selected_task = chosen_task
        st.session_state.selected_task_name = chosen_task.name
        st.session_state.page = "Home"

        st.rerun()
