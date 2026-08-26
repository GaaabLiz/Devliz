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
                "history",
                FluentIcon.HISTORY,
                tr("Action History"),
                tr("Track application events"),
                tr("The History screen displays a chronological log of all the actions you perform within Devliz, including details about snapshot changes, installations, and settings updates."),
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
                tr("Devliz is a robust snapshot-based configuration manager designed for developers and power users. It allows you to create snapshots of specific folders and files, saving their exact state. You can restore these states at any point in the future. This is particularly useful when testing new configurations, experimenting with different setups, or creating a standardized environment that you want to replicate easily. Devliz handles the heavy lifting by securely copying, tracking, and restoring your files while providing a clean and intuitive user interface to manage everything."),
            ),
            "home": (
                tr("Home screen"),
                tr("System and snapshot indicators"),
                tr("The Home screen provides a high-level dashboard of your entire Devliz environment. It calculates real-time metrics based on the snapshots you have stored. You will see the total number of snapshots available, the total storage space they occupy on your disk, the total count of files and folders contained within them, and the single largest file stored across all snapshots. This screen is designed to give you an immediate understanding of your usage and help you identify if you need to perform maintenance or clean up old snapshots to free up space."),
            ),
            "catalogue": (
                tr("Catalogue screen"),
                tr("Manage snapshot configurations"),
                tr("The Catalogue is the core of Devliz, where you manage all your saved snapshots. From here, you can:\n\n• Import new snapshots from your local filesystem.\n• Edit existing snapshots to update their contents or metadata.\n• Install a snapshot, which restores its saved files to their original or specified target locations.\n• Duplicate an existing snapshot to create a variation without starting from scratch.\n• Export snapshots for sharing or backing up to external drives.\n• Delete snapshots you no longer need.\n\nRight-click on any snapshot card to access the context menu for these advanced actions. You can also sort and filter the catalogue to quickly find specific configurations."),
            ),
            "search": (
                tr("Search screen"),
                tr("Search inside snapshots"),
                tr("The Search screen provides powerful tools to find specific content or files within your saved snapshots. You can perform plain text searches or use Regular Expressions for advanced pattern matching.\n\n• Target: Choose whether to search within the file contents or just the file names.\n• Filters: Restrict your search to specific file extensions to speed up the process and reduce noise.\n\nThe results are displayed with detailed context, showing you exactly where the match was found, allowing you to inspect the file or snapshot directly from the search results without having to install it first."),
            ),
            "settings": (
                tr("Settings screen"),
                tr("Customize the application"),
                tr("The Settings screen allows you to tailor Devliz to your preferences and workflow.\n\n• Paths: Define the root catalogue path where all snapshots are stored.\n• Organization: Manage your tags and custom fields to categorize snapshots effectively. Set up your favorite directories for quick access.\n• Safety: Configure backup behaviors before installing, editing, or deleting snapshots to prevent accidental data loss.\n• Appearance: Change the application theme (Light/Dark) and language. Note that changing the theme or language will require restarting the application to take effect fully."),
            ),
            "history": (
                tr("Action History"),
                tr("Track application events"),
                tr("The Action History screen provides a comprehensive audit trail of your activities within Devliz. Every significant action, such as creating, installing, or deleting snapshots, searching for files, and altering settings, is recorded here.\n\n• Timestamp: See exactly when each action occurred.\n• Screen & Action: Identify which part of the application was used and what was done.\n• Details: Review context-specific information, like the name of the snapshot involved or the scope of a search.\n\nThis log is incredibly useful for tracking down what changes were made during a session and verifying that operations like backups or installations were completed as expected."),
            ),
            "backup": (
                tr("Backup and safety"),
                tr("Protect local data"),
                tr("Data safety is a priority in Devliz. The Backup system ensures you never lose important local data when applying snapshot changes.\n\n• Pre-install Backups: Before a snapshot overwrites local files during installation, a backup of the current local state is created.\n• Edit/Delete Backups: When modifying or removing snapshots, temporary backups are made to allow recovery in case of mistakes.\n\nYou can manage these backup policies in the Settings screen and periodically clear the backup storage to free up disk space when you are confident the changes are stable."),
            ),
            "refresh": (
                tr("Refresh and shortcuts"),
                tr("Keep data updated"),
                tr("Devliz is designed to stay in sync with your filesystem. If you make changes to the snapshot directories outside of the application, or if you simply want to ensure you are viewing the most up-to-date information, you can refresh the data.\n\n• Press the F5 key on your keyboard from any screen to trigger a global refresh.\n• During the refresh, a progress indicator will appear, ensuring you know the application is scanning and reloading your snapshot data. Once complete, all dashboards, catalogue entries, and metrics will reflect the current state."),
            ),
            "workflow": (
                tr("Recommended workflow"),
                tr("Suggested daily usage"),
                tr("To get the most out of Devliz, we recommend the following workflow:\n\n1. Initial Setup: Visit the Settings screen to define your primary catalogue path and configure your preferred tags and backup safety nets.\n2. Capture: Go to the Catalogue and create or import your first snapshots representing known good states of your projects.\n3. Iterate: As you work, use Devliz to install different configurations or save new snapshots when you reach milestones.\n4. Search & Inspect: Use the Search screen to find specific snippets or files across all your history without needing to install the snapshot first.\n5. Maintenance: Periodically review your Home screen metrics and clean up outdated snapshots or backups to maintain a healthy disk space."),
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
