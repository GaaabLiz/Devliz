import sys

from PySide6.QtWidgets import QApplication

from devliz.dash_controller import DashboardController

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = DashboardController()
    dashboard.start()
    app.exec()