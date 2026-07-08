from PySide6.QtCore import QSize, QEventLoop, QTimer
from PySide6.QtGui import QIcon
from qfluentwidgets import SplashScreen
from qfluentwidgets.components.widgets.frameless_window import FramelessWindow

from devliz.application.app import app, RESOURCE_ID_LOGO

from devliz.application.resources import resources_rc

class SplashWindow(FramelessWindow):

    def __init__(self):
        super().__init__()
        self.resize(700, 600)
        self.setWindowTitle(app.name)
        self.setWindowIcon(QIcon(RESOURCE_ID_LOGO))

        # 1. Create a splash screen
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(102, 102))

    def show_splash(self):
        self.show()

    def close_splash(self):
        self.splashScreen.finish()
        self.close()