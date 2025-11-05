import sys

from PySide6.QtWidgets import QApplication


from devliz.controller.dashboard import DashboardController
from devliz.view.widgets.splash import SplashWindow



if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = SplashWindow()
    splash.show()
    splash.close()
    dashboard = DashboardController()
    dashboard.start()
    app.exec()