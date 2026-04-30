from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QDialog, QVBoxLayout, QWidget
from qfluentwidgets import (
    AdaptiveFlowLayout,
    BodyLabel,
    CaptionLabel,
    FluentIcon,
    IconWidget,
    PrimaryPushButton,
    SingleDirectionScrollArea,
    SimpleCardWidget,
    StrongBodyLabel,
)

from devliz.application.action_history import log_action
from devliz.application.i18n import tr
from devliz.view.util.frame import DevlizQFrame


class HelpGuideCard(SimpleCardWidget):

    signal_clicked = Signal(str)

    def __init__(self, card_id: str, icon: FluentIcon, title: str, subtitle: str, content: str, parent=None):
        super().__init__(parent)
        self.card_id = card_id
        self.setMinimumHeight(220)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(18, 16, 18, 16)
        root_layout.setSpacing(8)

        icon_widget = IconWidget(icon, self)
        icon_widget.setFixedSize(20, 20)

        title_label = StrongBodyLabel(title, self)
        subtitle_label = CaptionLabel(subtitle, self)
        subtitle_label.setWordWrap(True)
        subtitle_label.setTextColor("#707070", "#b0b0b0")

        content_label = BodyLabel(content, self)
        content_label.setWordWrap(True)

        root_layout.addWidget(icon_widget)
        root_layout.addWidget(title_label)
        root_layout.addWidget(subtitle_label)
        root_layout.addWidget(content_label)
        root_layout.addStretch(1)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.signal_clicked.emit(self.card_id)
        super().mousePressEvent(event)


class HelpDetailDialog(QDialog):

    def __init__(self, title: str, subtitle: str, details: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(860, 620)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(18, 18, 18, 18)
        root_layout.setSpacing(12)

        title_label = StrongBodyLabel(title, self)
        subtitle_label = CaptionLabel(subtitle, self)
        subtitle_label.setWordWrap(True)
        subtitle_label.setTextColor("#606060", "#c5c5c5")

        scroll = SingleDirectionScrollArea(orient=Qt.Orientation.Vertical, parent=self)
        scroll.setWidgetResizable(True)
        scroll.enableTransparentBackground()

        content_widget = QWidget(scroll)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(6, 6, 6, 6)

        details_label = BodyLabel(details, content_widget)
        details_label.setWordWrap(True)
        content_layout.addWidget(details_label)
        content_layout.addStretch(1)

        scroll.setWidget(content_widget)

        btn_close = PrimaryPushButton(tr("Close"), self)
        btn_close.clicked.connect(self.accept)

        root_layout.addWidget(title_label)
        root_layout.addWidget(subtitle_label)
        root_layout.addWidget(scroll, 1)
        root_layout.addWidget(btn_close)


class HelpView(DevlizQFrame):

    def __init__(self, parent=None):
        super().__init__(name=tr("Help"), parent=parent)
        self.__setup_ui()

    def __setup_ui(self):
        self.install_label_title()

        intro = CaptionLabel(tr("This page gives you a complete guide to every screen and workflow in Devliz. Click a card to open advanced details."), self)
        intro.setWordWrap(True)
        intro.setTextColor("#606060", "#c5c5c5")

        scroll_layout = self.get_scroll_layout()
        scroll_layout.addWidget(intro)

        cards_container = QWidget(self)
        cards_layout = AdaptiveFlowLayout(cards_container)
        cards_layout.setContentsMargins(4, 8, 4, 8)
        cards_layout.setHorizontalSpacing(12)
        cards_layout.setVerticalSpacing(12)
        cards_layout.setWidgetMinimumWidth(320)
        cards_layout.setWidgetMaximumWidth(560)

        cards = [
            (
                "overview",
                FluentIcon.INFO,
                tr("Overview"),
                tr("What Devliz is for"),
                tr("Devliz manages snapshot-based configurations of folders/files. It helps you save, restore, duplicate and compare project states quickly."),
            ),
            (
                "home",
                FluentIcon.HOME,
                tr("Home screen"),
                tr("System and snapshot indicators"),
                tr("Home shows a quick summary: number of snapshots, total size, number of files/folders and the heaviest file across saved data."),
            ),
            (
                "catalogue",
                FluentIcon.BOOK_SHELF,
                tr("Catalogue screen"),
                tr("Manage snapshot configurations"),
                tr("Use Catalogue to import, edit, install, duplicate, sort, export and delete snapshots. Context menus expose advanced actions per snapshot."),
            ),
            (
                "search",
                FluentIcon.SEARCH,
                tr("Search screen"),
                tr("Search inside snapshots"),
                tr("Use Search to scan snapshot content or file names. You can choose target, query type (text/regex), file extensions and inspect detailed results."),
            ),
            (
                "settings",
                FluentIcon.SETTING,
                tr("Settings screen"),
                tr("Customize the application"),
                tr("Settings lets you configure catalogue path, tags, custom fields, favorites, backups, theme and language. Theme/language changes require restart."),
            ),
            (
                "backup",
                FluentIcon.SAVE,
                tr("Backup and safety"),
                tr("Protect local data"),
                tr("Enable pre-install/edit/delete backups to preserve current local folders before applying changes. You can clean backup storage from Settings."),
            ),
            (
                "refresh",
                FluentIcon.SYNC,
                tr("Refresh and shortcuts"),
                tr("Keep data updated"),
                tr("Press F5 to refresh the dashboard data from all screens. During refresh, the page shows progress until the new snapshot data is loaded."),
            ),
            (
                "workflow",
                FluentIcon.HELP,
                tr("Recommended workflow"),
                tr("Suggested daily usage"),
                tr("1) Configure catalogue/favorites in Settings. 2) Create or import snapshots in Catalogue. 3) Use Search for inspection. 4) Install/export when needed."),
            ),
        ]

        self._detail_payload = {
            "overview": (
                tr("Overview"),
                tr("What Devliz is for"),
                tr("Overview details"),
            ),
            "home": (
                tr("Home screen"),
                tr("System and snapshot indicators"),
                tr("Home details"),
            ),
            "catalogue": (
                tr("Catalogue screen"),
                tr("Manage snapshot configurations"),
                tr("Catalogue details"),
            ),
            "search": (
                tr("Search screen"),
                tr("Search inside snapshots"),
                tr("Search details"),
            ),
            "settings": (
                tr("Settings screen"),
                tr("Customize the application"),
                tr("Settings details"),
            ),
            "backup": (
                tr("Backup and safety"),
                tr("Protect local data"),
                tr("Backup details"),
            ),
            "refresh": (
                tr("Refresh and shortcuts"),
                tr("Keep data updated"),
                tr("Refresh details"),
            ),
            "workflow": (
                tr("Recommended workflow"),
                tr("Suggested daily usage"),
                tr("Workflow details"),
            ),
        }

        for card_id, icon, title, subtitle, content in cards:
            card = HelpGuideCard(card_id, icon, title, subtitle, content, cards_container)
            card.signal_clicked.connect(self.__open_details)
            cards_layout.addWidget(card)

        scroll_layout.addWidget(cards_container)
        scroll_layout.addStretch(1)
        self.install_scroll_on(self.master_layout)

    def __open_details(self, card_id: str):
        title, subtitle, details = self._detail_payload[card_id]
        log_action("Help", "help.card.opened", title)
        dialog = HelpDetailDialog(title, subtitle, details, self)
        dialog.exec()
