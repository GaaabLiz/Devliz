from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from qfluentwidgets import SplashScreen
from qfluentwidgets.components.widgets.frameless_window import FramelessWindow

from devliz.application.app import app, RESOURCE_ID_LOGO

from devliz.application.resources import resources_rc

class SplashWindow(FramelessWindow):
    """
    Splash screen window displayed during application startup.
    Provides a frameless window with the application logo.
    """

    def __init__(self):
        """
        Initialize the splash window, configuring size, title, icon, and the splash screen widget.
        """
        super().__init__()
        self.resize(700, 600)
        self.setWindowTitle(app.name)
        self.setWindowIcon(QIcon(RESOURCE_ID_LOGO))

        # 1. Create a splash screen
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(102, 102))

    def show_splash(self):
        """
        Display the splash screen window.
        """
        self.show()

    def hide_overlay(self):
        """
        Hide the splash screen overlay, signaling that the loading phase is finished.
        """
        self.splashScreen.finish()

    def close_splash(self):
        """
        Close the splash screen window completely.
        """
        self.close()