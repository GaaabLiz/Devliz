from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout, QSizePolicy, QSpacerItem, QLabel
from pylizlib.qtfw.widgets.text import BoldLabel
from qfluentwidgets import SettingCardGroup, PushSettingCard, FluentIcon

from devliz.application.app import app
from devliz.ui.common.frame import DevlizQFrame


class WidgetSettingsScrollable(DevlizQFrame):

    signal_open_dir_request = Signal(str)
    signal_close_and_clear_request = Signal()
    signal_open_about_dialog_request = Signal()
    signal_request_update = Signal()

    def __init__(self, parent=None):
        super().__init__(name="Settings", parent=parent)

        # Settaggio layout principale
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Label titolo
        self.layout.addWidget(self.get_label_title())

        # Aggiungo i widgets
        self.__add_groups(self.get_scroll_layout())

        # Installo lo scroll nel layout principale
        self.install_scroll_on(self.layout)



    def __add_groups(self, layout: QVBoxLayout):
        self.__add_group_info(layout)

    def __add_group_info(self, layout: QVBoxLayout):
        self.group_info = SettingCardGroup(self.tr("Informazioni"), self)
        self.group_info.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)

        # Informazioni applicazione
        self.card_info_app = PushSettingCard(
            text="Informazioni",
            icon=FluentIcon.APPLICATION,
            title="Informazioni su Devliz",
            content=app.version
        )
        self.card_info_app.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        self.card_info_app.clicked.connect(self.signal_open_about_dialog_request.emit)
        self.group_info.addSettingCard(self.card_info_app)

        layout.addSpacerItem(QSpacerItem(1, 5))
        layout.addWidget(self.group_info)
