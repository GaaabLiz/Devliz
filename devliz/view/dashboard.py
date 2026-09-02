import sys


from PySide6.QtCore import Signal
from PySide6.QtGui import QShortcut, QKeySequence, QIcon
from pylizlib.qt.domain.view import UiWidgetMode
from qfluentwidgets import FluentWindow, Theme, setTheme, setThemeColor, isDarkTheme
from qframelesswindow.utils import getSystemAccentColor

from devliz.application.app import app, RESOURCE_ID_LOGO

from devliz.application.resources import resources_rc

class DashboardView(FluentWindow):
    """
    Main dashboard view for the Devliz application.
    Inherits from FluentWindow to provide a fluent design interface.
    """

    f5_pressed = Signal()

    def __init__(self):
        """
        Initialize the dashboard view, setting up the window properties and shortcuts.
        """
        super().__init__()
        self.__init_window()
        self.__init_shortcuts()

    def __init_window(self):
        """
        Set up the window's dimensions, icon, title, and theme settings based on system preferences.
        """
        self.resize(1100, 700)
        self.setWindowIcon(QIcon(RESOURCE_ID_LOGO))
        self.setWindowTitle(app.name)
        theme = Theme.LIGHT if not isDarkTheme() else Theme.DARK
        setTheme(theme, True, False)
        if sys.platform in ["win32", "darwin"]:
            setThemeColor(getSystemAccentColor(), save=True)

    def __init_shortcuts(self):
        """
        Initialize keyboard shortcuts for the dashboard, such as F5 for refreshing.
        """
        shortcut = QShortcut(QKeySequence("F5"), self)
        shortcut.activated.connect(self.f5_pressed.emit)

    def set_state(self, state: UiWidgetMode):
        """
        Update the UI state of the dashboard widgets.

        :param state: The new UI state mode to apply.
        :type state: UiWidgetMode
        """
        self.widget_catalogue.set_state(state)