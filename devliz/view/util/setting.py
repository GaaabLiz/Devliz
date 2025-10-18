from PySide6.QtWidgets import QSizePolicy, QSpacerItem
from qfluentwidgets import SettingCardGroup


class SettingGroupManager:

    def __init__(self, name: str, parent):
        self.group = SettingCardGroup(name, parent)
        self.group.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)

    def add_widget(self, widget, signal):
        widget.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        if signal is not None:
            widget.clicked.connect(signal.emit)
        self.group.addSettingCard(widget)

    def install_group_on(self, layout):
        layout.addSpacerItem(QSpacerItem(1, 5))
        layout.addWidget(self.group)
