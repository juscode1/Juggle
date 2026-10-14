from models.Task import Task


class AcademicTask(Task):

    def get_category(self):
        return "Academic"


class PersonalTask(Task):

    def get_category(self):
        return "Personal"


class WorkTask(Task):

    def get_category(self):
        return "Work"