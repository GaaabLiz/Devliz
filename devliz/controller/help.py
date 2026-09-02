from devliz.view.help import HelpView


class HelpController:
    """
    Controller for the application's help/documentation section.

    This controller manages the HelpView, providing the user with
    information and assistance on how to use the application.
    """

    def __init__(self):
        """
        Initializes the HelpController.

        Sets up the HelpView component.
        """
        self.view = HelpView()
