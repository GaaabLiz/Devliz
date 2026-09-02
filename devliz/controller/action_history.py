from devliz.model.action_history import list_actions
from devliz.view.action_history import ActionHistoryView


class ActionHistoryController:
    """
    Controller responsible for managing the action history view.

    This controller coordinates the interaction between the underlying action history
    model and the user interface representation, allowing the user to view a log of
    actions performed within the application.
    """

    def __init__(self):
        """
        Initializes the ActionHistoryController.

        This sets up the associated view component which will display the history data.
        """
        self.view = ActionHistoryView()

    def reload(self):
        """
        Reloads the action history data and updates the view.

        This method fetches the latest list of actions from the model using `list_actions()`
        and populates the view's rows with the retrieved data.
        """
        self.view.update_rows(list_actions())
