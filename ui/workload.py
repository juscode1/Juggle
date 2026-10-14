import streamlit as st

from services.workload_analyzer import WorkloadAnalyzer
from ui.home import available_time_input


def show_workload():
    st.title("Workload Analysis")

    st.write(
        "See how your current tasks compare with "
        "the amount of time you have available."
    )

    st.divider()

    tasks = st.session_state.get("tasks", [])

    if not tasks:
        st.info("Add tasks before analyzing your workload.")
        return

    # Let the user set how much time they have available today.
    available_time = available_time_input("workload_available_time_input")

    analyzer = WorkloadAnalyzer(tasks, available_time)

    workload = analyzer.calculate_workload()
    remaining = analyzer.remaining_time()
    active_tasks = analyzer.get_active_tasks()

    completed_count = len(tasks) - len(active_tasks)

    st.divider()

    # Summarize workload and available time.
    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("Active Workload")
        st.markdown(f"### {int(workload)} min")

    with col2:
        st.write("Available Time")
        st.markdown(f"### {int(available_time)} min")

    with col3:
        st.write("Remaining Time")

        if remaining >= 0:
            st.markdown(f"### {int(remaining)} min")
        else:
            st.markdown(f"### {abs(int(remaining))} min over")

    st.divider()

    # Explain whether the unfinished workload fits the available time.
    if workload == 0:
        st.success("You have no unfinished tasks.")

    elif workload < available_time:
        st.success(
            f"Your workload fits within your available time. "
            f"You have {int(remaining)} minutes remaining."
        )

    elif workload == available_time:
        st.warning(
            "Your workload exactly matches your available time."
        )

    else:
        st.error(
            f"Your workload is {abs(int(remaining))} minutes over "
            "your available time."
        )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.write("Active Tasks")
        st.markdown(f"### {len(active_tasks)}")

    with col2:
        st.write("Completed Tasks")
        st.markdown(f"### {completed_count}")

    st.divider()

    # Display details for each unfinished task.
    st.subheader("Task Breakdown")

    if not active_tasks:
        st.info("All of your tasks are completed.")
        return

    for task in active_tasks:
        name = getattr(task, "name", "Unnamed Task")
        duration = getattr(task, "duration", 0)
        priority = getattr(task, "priority", "Unknown")
        deadline = getattr(task, "deadline", "Unknown")

        st.write(f"**{name}**")

        st.caption(
            f"{duration} minutes | "
            f"{priority} priority | "
            f"Due {deadline}"
        )

        st.divider()