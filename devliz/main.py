import sys

from PySide6.QtWidgets import QApplication


from devliz.dash_controller import DashboardController
from devliz.ui.splash import SplashWindow



if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = SplashWindow()
    splash.show()
    splash.close()
    dashboard = DashboardController()
    dashboard.start()
    app.exec()