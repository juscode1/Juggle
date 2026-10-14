
class Task:

    def __init__(self, name, subject, deadline, duration, priority):
        self._name = name
        self._subject = subject
        self._deadline = deadline
        self._duration = duration
        self._priority = priority
        self.completed = False

    @property
    def name(self):
        return self._name

    @property
    def subject(self):
        return self._subject

    @property
    def deadline(self):
        return self._deadline

    @property
    def duration(self):
        return self._duration

    @property
    def priority(self):
        return self._priority

    def get_category(self):
        return "Other"