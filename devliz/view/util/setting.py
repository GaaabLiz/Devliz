from PySide6.QtWidgets import QSizePolicy, QSpacerItem
from pylizlib.qtfw.domain.setting import QtFwQConfigItem
from qfluentwidgets import SettingCardGroup

from devliz.application.app import AppSettings, app_settings


class SettingGroupManager:
    """
    Manager class for handling a group of setting cards in the UI.
    """

    def __init__(self, name: str, parent, group_enabled: bool = True):
        """
        Initialize the SettingGroupManager.

        :param name: The name/title of the setting group.
        :param parent: The parent widget.
        :param group_enabled: Whether the setting group is enabled by default.
        """
        self.group_enabled = group_enabled
        self.group = SettingCardGroup(name, parent)
        self.group.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        self.debug_test_mode = app_settings.get(AppSettings.debug_test_mode)

    def add_widget(self, setting: QtFwQConfigItem | None, widget, signal):
        """
        Add a setting widget to the group, applying visibility logic based on settings and debug mode.

        :param setting: The configuration item associated with the widget, if any.
        :param widget: The widget to add to the setting group.
        :param signal: The signal to connect the widget's clicked event to.
        """
        if setting is None:
            self.__add_widget_(widget, signal)
            return
        if self.debug_test_mode:
            self.__add_widget_(widget, signal)
            return
        if not setting.enabled:
            return
        self.__add_widget_(widget, signal)

    def __add_widget_(self, widget, signal):
        """
        Internal method to configure and add a widget to the SettingCardGroup.

        :param widget: The widget to add.
        :param signal: The signal to connect the clicked event to.
        """
        widget.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        if signal is not None:
            widget.clicked.connect(signal.emit)
        self.group.addSettingCard(widget)

    def install_group_on(self, layout):
        """
        Install the setting group widget onto a given layout with appropriate spacing.

        :param layout: The layout to add the setting group to.
        """
        layout.addSpacerItem(QSpacerItem(1, 5))
        layout.addWidget(self.group)

    def install_spacer_on(self, layout):
        """
        Install a vertical spacer onto a given layout.

        :param layout: The layout to add the spacer to.
        """
        layout.addSpacerItem(QSpacerItem(1, 10))
