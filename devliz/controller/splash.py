import sys
from PySide6.QtCore import QEventLoop, QTimer
from devliz.model.splash import SplashModel
from devliz.view.splash import SplashWindow

class SplashController:
    """
    Controller for managing the application's splash screen.

    This controller handles the initial loading sequence of the application,
    including displaying the splash screen and verifying critical startup conditions
    like the availability of the catalogue path.
    """

    def __init__(self):
        """
        Initializes the SplashController.

        Sets up the splash screen model and view.
        """
        self.model = SplashModel()
        self.view = SplashWindow()

    def start(self):
        """
        Starts the splash screen logic:
        1. Shows the splash window.
        2. Waits for 1 second to display the logo.
        3. Checks the existence of the catalogue path.
        4. Shows an error MessageBox if it does not exist.
        5. Closes the splash screen and allows the caller to continue.
        """
        self.view.show_splash()

        # Wait for 1 second (same logic as the original view)
        loop = QEventLoop()
        QTimer.singleShot(1000, loop.quit)
        loop.exec()

        self.view.hide_overlay()

        self.__check_catalogue()

        self.view.close_splash()

    def __check_catalogue(self):
        """
        Checks the catalogue path and prompts the user on how to proceed if it is invalid.
        """
        if not self.model.check_catalogue_path():
            catalogue_path_str = self.model.get_catalogue_path_str()

            if self.view.show_catalogue_error_dialog(catalogue_path_str):
                self.model.set_default_catalogue_path()
            else:
                sys.exit(0)
