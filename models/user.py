class User:
    def __init__(self, name):
        self.name = name
        self.tasks = []
        self.work_style = None

    def add_task(self, task):
        self.tasks.append(task)

    def set_work_style(self, profile):
        self.work_style = profile