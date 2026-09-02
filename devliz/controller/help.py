from devliz.view.help import HelpView
from devliz.model.help import HelpModel
from devliz.model.action_history import log_action, ActionCategory, ActionType


class HelpController:
    """
    Controller for the application's help/documentation section.

    This controller manages the HelpView, providing the user with
    information and assistance on how to use the application.
    """

    def __init__(self):
        """
        Initializes the HelpController.

        Sets up the HelpView component and HelpModel component.
        """
        self.model = HelpModel()
        self.view = HelpView()

        # Connect view signals to controller slots
        self.view.signal_card_clicked.connect(self._on_card_clicked)

        # Initialize the view with data from the model
        self.view.set_cards(self.model.get_cards())

    def _on_card_clicked(self, card_id: str):
        """
        Handles the event when a help card is clicked.
        
        Retrieves details from the model, logs the action, and instructs the view to show the dialog.
        """
        details_payload = self.model.get_details(card_id)
        if details_payload:
            title, subtitle, details = details_payload
            log_action(ActionCategory.HELP, ActionType.HELP_CARD_OPENED, title)
            self.view.show_details_dialog(title, subtitle, details)
