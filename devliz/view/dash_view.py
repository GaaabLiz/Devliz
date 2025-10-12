import sys


from PySide6.QtCore import Signal
from PySide6.QtGui import QShortcut, QKeySequence, QIcon
from qfluentwidgets import FluentWindow, Theme, setTheme, setThemeColor, isDarkTheme, FluentIcon, NavigationItemPosition
from qframelesswindow.utils import getSystemAccentColor

from devliz.view.widgets.setting_widget import WidgetSettingsScrollable


class DashboardView(FluentWindow):

    f5_pressed = Signal()

    def __init__(self):
        super().__init__()
        self.__init_window()
        self.__init_widgets()
        self.__init_shortcuts()

    def __init_window(self):
        self.resize(1100, 700)
        self.setWindowIcon(QIcon(':/resources/logo2.png'))
        self.setWindowTitle('Devliz')
        theme = Theme.LIGHT if not isDarkTheme() else Theme.DARK
        setTheme(theme, True, False)
        if sys.platform in ["win32", "darwin"]:
            setThemeColor(getSystemAccentColor(), save=True)

    def __init_widgets(self):
        self.widget_setting = WidgetSettingsScrollable(self)
        self.addSubInterface(self.widget_setting, FluentIcon.SETTING, self.widget_setting.window_name, NavigationItemPosition.BOTTOM)

    def __init_shortcuts(self):
        shortcut = QShortcut(QKeySequence("F5"), self)
        shortcut.activated.connect(self.f5_pressed.emit)