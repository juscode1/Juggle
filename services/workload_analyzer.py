class WorkloadAnalyzer:

    def __init__(self, tasks, available_time):
        self.tasks = tasks
        self.available_time = available_time
        self.total_workload = 0

    # Return tasks that are not yet completed.
    def get_active_tasks(self):
        active_tasks = []

        for task in self.tasks:
            completed = getattr(task, "completed", False)

            if not completed:
                active_tasks.append(task)

        return active_tasks

    # Calculate the total duration of pending tasks.
    def calculate_workload(self):
        total = 0

        for task in self.get_active_tasks():
            total += self.get_duration(task)

        self.total_workload = total
        return total

    def check_overload(self):
        return self.calculate_workload() > self.available_time

    def remaining_time(self):
        return self.available_time - self.calculate_workload()

    # Get the user's work style
    def get_work_style(self):
        try:
            import streamlit as st
            user = st.session_state.get("user")
        except Exception:
            return ""

        if user is None:
            return ""

        profile = getattr(user, "work_style", None)

        if profile is None:
            return ""

        return getattr(profile, "style", "")

    def get_duration(self, task):
        try:
            duration = float(getattr(task, "duration", 0))
            return max(0, duration)
        except (TypeError, ValueError):
            return 0

    def get_priority(self, task):
        priority_order = {
            "High": 1,
            "Medium": 2,
            "Low": 3
        }

        priority = getattr(task, "priority", "Low")
        return priority_order.get(priority, 3)

    def get_deadline(self, task):
        deadline = getattr(task, "deadline", "")

        if deadline is None or deadline == "":
            return "9999-12-31"

        return str(deadline)

    # Rank pending tasks based on work style and available time.
    def rank_tasks(self):
        pending_tasks = self.get_active_tasks()

        if not pending_tasks:
            return []

        style = self.get_work_style()

        def sort_key(task):
            duration = self.get_duration(task)
            deadline = self.get_deadline(task)
            priority = self.get_priority(task)

            fits_time = duration <= self.available_time

            if style == "Focused Planner":
                return (
                    not fits_time,
                    -duration,
                    priority,
                    deadline
                )

            elif style == "Quick Starter":
                return (
                    not fits_time,
                    duration,
                    priority,
                    deadline
                )

            elif style == "Deadline Driven":
                return (
                    not fits_time,
                    deadline,
                    priority,
                    duration
                )

            return (
                not fits_time,
                priority,
                deadline,
                duration
            )

        return sorted(pending_tasks, key=sort_key)

    def recommend_task(self):
        ranked_tasks = self.rank_tasks()

        if not ranked_tasks:
            return None

        return ranked_tasks[0]

    # Explain why a task was recommended.
    def get_reason(self, task):
        priority = getattr(task, "priority", "Unknown")
        deadline = getattr(task, "deadline", "Unknown")
        duration = self.get_duration(task)
        style = self.get_work_style()
        available_time = self.available_time

        if priority == "High":
            priority_reason = "It has high priority"
        elif priority == "Medium":
            priority_reason = "It has medium priority"
        else:
            priority_reason = "It has low priority"

        reason = (
            f"{priority_reason} and is due on {deadline}. "
            f"This task takes {duration:g} minutes."
        )

        if duration <= available_time:
            reason += (
                f" It fits within your available time "
                f"of {available_time:g} minutes."
            )
        else:
            reason += (
                f" It exceeds your available time "
                f"of {available_time:g} minutes."
            )

        if style == "Focused Planner":
            reason += (
                " Your Focused Planner work style prioritizes "
                "longer tasks first."
            )

        elif style == "Quick Starter":
            reason += (
                " Your Quick Starter work style prioritizes "
                "shorter tasks first."
            )

        elif style == "Deadline Driven":
            reason += (
                " Your Deadline Driven work style prioritizes "
                "the nearest deadlines first."
            )

        else:
            reason += (
                " The recommendation considers priority, "
                "deadline, duration, and available time."
            )

        return reason