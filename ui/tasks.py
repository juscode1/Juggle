import streamlit as st
from datetime import datetime, date
from zoneinfo import ZoneInfo

from supabase_client import get_supabase
from models.TaskTypes import AcademicTask, PersonalTask, WorkTask
from ui.styles import priority_badge, to_date, today_manila


PRIORITY_OPTIONS = ["Low", "Medium", "High"]

TASK_CLASSES = {
    "Academic": AcademicTask,
    "Personal": PersonalTask,
    "Work": WorkTask,
}


def get_user_id():
    return st.session_state.get("user_id")


def get_db():
    return get_supabase()


# Convert a database record into your existing OOP task subclass.
def task_from_record(record):
    category = record.get("category", "Academic")
    task_class = TASK_CLASSES.get(category, AcademicTask)

    deadline = record.get("deadline")
    if deadline:
        deadline = date.fromisoformat(str(deadline)[:10])
    else:
        deadline = date.today()

    task = task_class(
        record["name"],
        record.get("subject", ""),
        deadline,
        int(record.get("duration", 60)),
        record.get("priority", "Medium"),
    )

    task.id = record["id"]
    task.completed = bool(record.get("completed", False))
    task.completed_date = record.get("completed_date")
    return task


# Load only the logged-in user's tasks.
def load_tasks():
    user_id = get_user_id()

    if not user_id:
        st.error("Your user session is missing. Please log in again.")
        return False

    try:
        response = (
            get_db()
            .table("tasks")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at")
            .execute()
        )

        st.session_state.tasks = [
            task_from_record(record) for record in response.data
        ]
        return True

    except Exception as e:
        st.error(f"Could not load tasks from Supabase: {e}")
        return False


def save_task_changes(task):
    user_id = get_user_id()

    if not user_id or not getattr(task, "id", None):
        st.error("Task ID or user ID is missing.")
        return False

    try:
        (
            get_db()
            .table("tasks")
            .update({
                "name": task.name,
                "subject": task.subject,
                "deadline": task.deadline.isoformat(),
                "duration": int(task.duration),
                "priority": task.priority,
                "category": task.get_category(),
                "completed": bool(task.completed),
                "completed_date": getattr(task, "completed_date", None),
            })
            .eq("id", task.id)
            .eq("user_id", user_id)
            .execute()
        )
        return True

    except Exception as e:
        st.error(f"Could not save task changes: {e}")
        return False


def show_task_title(task, completed=False):
    name = getattr(task, "name", "Unnamed Task")

    if completed:
        st.markdown(f"~~{name}~~")
        return

    st.markdown(
        f"**{name}** &nbsp; "
        f"{priority_badge(getattr(task, 'priority', 'Unknown'))}",
        unsafe_allow_html=True,
    )


def show_task_details(task, completed=False):
    deadline = getattr(task, "deadline", "Unknown")
    deadline_date = to_date(deadline)

    overdue = (
        not completed
        and deadline_date is not None
        and deadline_date < today_manila()
    )

    details = (
        f"{task.get_category()} | "
        f"{getattr(task, 'subject', 'Unknown')} | "
        f"{getattr(task, 'duration', 0)} minutes | "
        f"Due {deadline}"
    )

    if overdue:
        details += ' | <span style="color:#E05252; font-weight:600;">Overdue</span>'

    st.markdown(details, unsafe_allow_html=True)

def show_tasks():
    st.title("My Tasks")

    if "task_message" in st.session_state:
        st.success(st.session_state.pop("task_message"))

    if "editing_task" not in st.session_state:
        st.session_state.editing_task = None

    if "activity" not in st.session_state:
        st.session_state.activity = {}

    if not load_tasks():
        return

    tasks = st.session_state.tasks

    if tasks:
        tab1, tab2, tab3 = st.tabs(
            ["Ongoing Tasks", "Completed Tasks", "Add Task"]
        )

        with tab1:
            ongoing_tasks = [
                (i, task)
                for i, task in enumerate(tasks)
                if not task.completed
            ]

            st.subheader("Your Ongoing Tasks")
            st.write(
                f"You currently have {len(ongoing_tasks)} ongoing task(s)."
            )

            if ongoing_tasks:
                for index, task in ongoing_tasks:
                    col1, col2, col3 = st.columns([3, 1, 1])

                    with col1:
                        show_task_title(task)
                        show_task_details(task)

                    with col2:
                        if st.button(
                            "Edit",
                            key=f"edit_task_{task.id}",
                            use_container_width=True,
                        ):
                            st.session_state.editing_task = task.id
                            st.rerun()

                    with col3:
                        if st.button(
                            "Complete",
                            key=f"complete_task_{task.id}",
                            type="primary",
                            use_container_width=True,
                        ):
                            task.completed = True
                            task.completed_date = datetime.now(
                                ZoneInfo("Asia/Manila")
                            ).date().isoformat()

                            if save_task_changes(task):
                                today = task.completed_date
                                st.session_state.activity[today] = (
                                    st.session_state.activity.get(today, 0) + 1
                                )
                                st.session_state.task_message = (
                                    f"Task '{task.name}' completed."
                                )
                                st.session_state.editing_task = None
                                st.rerun()

                    if st.session_state.editing_task == task.id:
                        show_edit_task(task.id, task)

                    st.divider()
            else:
                st.info("You have no ongoing tasks.")

        with tab2:
            completed_tasks = [
                task for task in tasks if task.completed
            ]

            st.subheader("Your Completed Tasks")
            st.write(
                f"You have completed {len(completed_tasks)} task(s)."
            )

            if completed_tasks:
                completed_dates = {}

                for task in completed_tasks:
                    completed_date = getattr(
                        task, "completed_date", None
                    ) or "Unknown"
                    completed_dates.setdefault(
                        completed_date, []
                    ).append(task)

                for completed_date, date_tasks in completed_dates.items():
                    if completed_date != "Unknown":
                        try:
                            formatted_date = datetime.strptime(
                                str(completed_date), "%Y-%m-%d"
                            ).strftime("%B %d, %Y")
                        except ValueError:
                            formatted_date = str(completed_date)
                    else:
                        formatted_date = "Date Unknown"

                    st.write(f"### {formatted_date}")

                    for task in date_tasks:
                        col1, col2, col3 = st.columns([3, 1, 1])

                        with col1:
                            show_task_title(task, completed=True)
                            show_task_details(task, completed=True)

                        with col2:
                            if st.button(
                                "Edit",
                                key=f"edit_completed_task_{task.id}",
                                use_container_width=True,
                            ):
                                st.session_state.editing_task = task.id
                                st.rerun()

                        with col3:
                            st.markdown(":green[✓ Completed]")

                        if st.session_state.editing_task == task.id:
                            show_edit_task(task.id, task)

                        st.divider()
            else:
                st.info("You have no completed tasks.")

        with tab3:
            show_add_task()

    else:
        st.subheader("Create a Task")
        show_add_task()


def show_edit_task(task_id, task):
    current_deadline = getattr(task, "deadline", date.today())

    if isinstance(current_deadline, datetime):
        current_deadline = current_deadline.date()
    elif not isinstance(current_deadline, date):
        current_deadline = date.today()

    current_priority = getattr(task, "priority", "Medium")
    if current_priority not in PRIORITY_OPTIONS:
        current_priority = "Medium"

    current_name = getattr(task, "name", "")
    current_subject = getattr(task, "subject", "")
    current_duration = int(getattr(task, "duration", 60))

    with st.form(f"edit_task_form_{task_id}"):
        st.write("**Edit Task**")

        new_name = st.text_input(
            "Task Name", value=current_name, max_chars=100
        )
        new_subject = st.text_input(
            "Subject / Area", value=current_subject, max_chars=100
        )

        col1, col2 = st.columns(2)

        with col1:
            new_deadline = st.date_input(
                "Deadline", value=current_deadline
            )

        with col2:
            new_duration = st.number_input(
                "Duration (minutes)",
                min_value=1,
                max_value=1440,
                value=max(1, min(1440, current_duration)),
                step=5,
            )

        new_priority = st.selectbox(
            "Priority",
            PRIORITY_OPTIONS,
            index=PRIORITY_OPTIONS.index(current_priority),
        )

        save_col, cancel_col = st.columns(2)

        with save_col:
            saved = st.form_submit_button(
                "Save Changes", use_container_width=True
            )

        with cancel_col:
            cancelled = st.form_submit_button(
                "Cancel", use_container_width=True
            )

    if cancelled:
        st.session_state.editing_task = None
        st.rerun()

    if saved:
        new_name = new_name.strip()
        new_subject = new_subject.strip()

        if not new_name:
            st.error("Please enter a task name.")
            return

        if not new_subject:
            st.error("Please enter a subject or area.")
            return

        no_changes = (
            new_name == current_name
            and new_subject == current_subject
            and new_deadline == current_deadline
            and new_duration == current_duration
            and new_priority == current_priority
        )

        if no_changes:
            st.info("No changes were made.")
            return

        # Update the encapsulated attributes of the OOP task.
        task._name = new_name
        task._subject = new_subject
        task._deadline = new_deadline
        task._duration = int(new_duration)
        task._priority = new_priority

        if save_task_changes(task):
            st.session_state.editing_task = None
            st.session_state.task_message = (
                f"Task '{new_name}' updated successfully."
            )
            st.rerun()


def show_add_task():
    with st.form("add_task_form"):
        task_name = st.text_input("Task Name", max_chars=100)
        subject = st.text_input("Subject / Area", max_chars=100)

        col1, col2 = st.columns(2)

        with col1:
            deadline = st.date_input(
                "Deadline", min_value=date.today()
            )

        with col2:
            duration = st.number_input(
                "Duration (minutes)",
                min_value=1,
                max_value=1440,
                value=60,
                step=5,
            )

        col1, col2 = st.columns(2)

        with col1:
            priority = st.selectbox("Priority", PRIORITY_OPTIONS)

        with col2:
            category = st.selectbox(
                "Category", list(TASK_CLASSES.keys())
            )

        submitted = st.form_submit_button(
            "Add Task", use_container_width=True
        )

    if not submitted:
        return

    task_name = task_name.strip()
    subject = subject.strip()

    if not task_name:
        st.error("Please enter a task name.")
        return

    if not subject:
        st.error("Please enter a subject or area.")
        return

    user_id = get_user_id()
    if not user_id:
        st.error("Your user session is missing. Please log in again.")
        return

    try:
        # Inheritance and polymorphism select the correct task subclass.
        task_class = TASK_CLASSES[category]
        task = task_class(
            task_name, subject, deadline, int(duration), priority
        )

        response = (
            get_db()
            .table("tasks")
            .insert({
                "user_id": user_id,
                "name": task.name,
                "subject": task.subject,
                "deadline": task.deadline.isoformat(),
                "duration": int(task.duration),
                "priority": task.priority,
                "category": category,
                "completed": False,
                "completed_date": None,
            })
            .execute()
        )

        if not response.data:
            st.error("Supabase did not return the saved task.")
            return

        # Store the database ID on the OOP object.
        task.id = response.data[0]["id"]
        task.completed = False
        task.completed_date = None

        st.session_state.tasks.append(task)

        user = st.session_state.get("user")
        if user is not None:
            user.add_task(task)

        st.session_state.task_message = (
            f"Task '{task_name}' added successfully."
        )
        st.rerun()

    except Exception as e:
        st.error(f"The task could not be added: {e}")
