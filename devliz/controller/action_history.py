from devliz.application.action_history import list_actions
from devliz.view.action_history import ActionHistoryView


class ActionHistoryController:

    def __init__(self):
        self.view = ActionHistoryView()

    def reload(self):
        self.view.update_rows(list_actions())
