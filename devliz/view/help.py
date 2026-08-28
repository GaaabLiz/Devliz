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

from devliz.application.action_history import log_action, ActionCategory, ActionType
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
        super().__init__(
            name=tr("Help"), 
            parent=parent, 
            subtitle=tr("A complete guide to every screen and workflow in Devliz.")
        )
        self.__setup_ui()

    def __setup_ui(self):
        self.install_label_title()

        scroll_layout = self.get_scroll_layout()

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
                tr("Devliz is a robust, locally hosted snapshot and configuration manager tailored for developers, system administrators, and power users.\n\n"
                   "At its core, Devliz allows you to capture the exact state of specific folders and files on your system. These captures—called \"Snapshots\"—are securely stored in your Catalogue. "
                   "Once a snapshot is saved, you can freely experiment with your local files. If something goes wrong, or if you simply need to switch context to another project state, you can \"Install\" the snapshot to instantly restore your files exactly as they were.\n\n"
                   "Key benefits include:\n"
                   "• Rapid Context Switching: Move between different environments or branches of work without worrying about losing uncommitted local changes.\n"
                   "• State Experimentation: Try out new setups, install unstable packages, or alter configurations with the peace of mind that a clean state is just a click away.\n"
                   "• Centralized Organization: Use Tags and Custom Fields to categorize your setups. Never lose track of how a specific project was configured.\n"
                   "• Built-in Safety: Devliz employs an automated backup system that protects your local data before it gets overwritten by a snapshot installation.\n\n"
                   "Welcome to a safer, more organized workflow."),
            ),
            "home": (
                tr("Home screen"),
                tr("System and snapshot indicators"),
                tr("The Home screen acts as your high-level command center, providing a unified dashboard of your entire Devliz environment.\n\n"
                   "This screen is designed to give you an immediate understanding of your system's footprint. The metrics displayed are calculated in real-time by scanning your active Catalogue:\n\n"
                   "• Total Snapshots: The absolute number of saved configurations currently managed by Devliz.\n"
                   "• Total Storage Space: The physical disk space consumed by all your snapshots combined. This is crucial for managing your storage and deciding when to prune old data.\n"
                   "• File & Folder Counts: A deep dive into the total number of individual files and directories archived across your entire catalogue.\n"
                   "• Heaviest File: Identifies the single largest file stored in your snapshots, helping you track down large binaries, databases, or media files that might be bloating your backups.\n\n"
                   "Use the Home screen to regularly audit your usage and ensure your snapshot catalogue remains healthy and performant."),
            ),
            "catalogue": (
                tr("Catalogue screen"),
                tr("Manage snapshot configurations"),
                tr("The Catalogue is the beating heart of Devliz. It is where you browse, organize, and interact with all your saved snapshots.\n\n"
                   "The interface provides a powerful grid view of your configurations, sortable by Name, Author, Creation Date, Modification Date, and Size. You can use the search bar to filter snapshots instantly.\n\n"
                   "Right-clicking any snapshot reveals a comprehensive context menu:\n"
                   "• Install: Restores the snapshot's files back to their original local directories. You can configure Devliz to clear the target folders before installing to ensure a pristine state.\n"
                   "• Update with local: Quickly updates the saved snapshot by pulling the latest changes from the associated local directories, without opening the full edit window.\n"
                   "• Edit: Modify the snapshot's metadata (Name, Tags, Author, Description) or alter its contents.\n"
                   "• Duplicate: Clones the snapshot entirely. Perfect for creating a base configuration and branching off different variations.\n"
                   "• Search content: Opens the Search screen pre-filtered to scan only within this specific snapshot.\n"
                   "• Open: Quickly open either the archived Snapshot folder or the original Associated local folders in your OS file explorer.\n"
                   "• Export: Package the snapshot or its associated folders into a standalone `.zip` archive for sharing, archiving, or transferring to another machine.\n"
                   "• Delete: Remove the snapshot entirely to free up space, or choose to delete only the installed local folders."),
            ),
            "search": (
                tr("Search screen"),
                tr("Search inside snapshots"),
                tr("The Search screen is a powerful, integrated search engine that lets you peer inside your snapshots without having to install or extract them first.\n\n"
                   "Whether you forgot which snapshot contains a specific code snippet, or you're looking for a lost configuration file, the Search tool can find it.\n\n"
                   "Search Capabilities:\n"
                   "• Scope: By default, it searches across your entire Catalogue. You can also right-click a snapshot in the Catalogue to restrict the search to just that item.\n"
                   "• Target Content vs. Target Names: Choose whether the search engine should look inside the actual text content of the files, or if it should only match against file and folder names.\n"
                   "• Plain Text & Regex: Perform standard literal searches, or toggle Regular Expressions (Regex) for advanced pattern matching.\n"
                   "• Extension Filters: Drastically speed up your searches and reduce noise by limiting the scan to specific file types (e.g., `.py`, `.json`, `.txt`).\n\n"
                   "The results pane provides rich context, showing you the exact file path and highlighting the matching text snippet. You can double-click a result to inspect it further."),
            ),
            "settings": (
                tr("Settings screen"),
                tr("Customize the application"),
                tr("The Settings screen allows you to deeply customize Devliz to fit your specific needs and technical environment.\n\n"
                   "Key Configuration Areas:\n"
                   "• Catalogue Path: The absolute path on your system where all snapshots are physically stored. You can change this to a secondary drive or a synced cloud folder.\n"
                   "• Organization: Define your globally available 'Tags' and 'Custom Fields' to standardize how you categorize snapshots.\n"
                   "• Favorites: Register your most-used Directories, Files, Executables, and Services. This allows Devliz to provide quick-access shortcuts throughout the app.\n"
                   "• Safety & Backups: Toggle the automatic backup triggers (Before Install, Before Edit, Before Delete). You can also define the directory where these temporary safety backups are kept.\n"
                   "• Installation Rules: Toggle 'Clear snap attached folders before install'. When enabled, Devliz will completely wipe the target directory before copying the snapshot files, preventing stale files from lingering.\n"
                   "• Appearance & Locale: Switch between Light and Dark themes, and change the application language. (Note: Theme and language changes require an application restart)."),
            ),
            "history": (
                tr("Action History"),
                tr("Track application events"),
                tr("The Action History screen serves as an unalterable audit trail of your activities within Devliz.\n\n"
                   "Every significant operation you perform is logged here chronologically. This includes creating new snapshots, installing configurations, deleting data, refreshing the dashboard, and altering application settings.\n\n"
                   "Understanding the Log:\n"
                   "• Timestamp: The exact date and time the action occurred.\n"
                   "• Screen: Identifies which module of Devliz triggered the event (e.g., Dashboard, Catalogue, Search).\n"
                   "• Action: A technical identifier of what happened (e.g., 'dashboard.refresh.completed', 'search.page.opened').\n"
                   "• Details: Context-specific payloads, such as the name of the snapshot you installed or the number of snapshots loaded during a refresh.\n\n"
                   "This screen is invaluable for retracing your steps. If you return to a project after a long break and wonder, 'Which snapshot did I install last?', the Action History provides the definitive answer."),
            ),
            "backup": (
                tr("Backup and safety"),
                tr("Protect local data"),
                tr("Devliz is designed to manipulate your local files, and with that power comes a strict commitment to data safety. The Backup system is your automated safety net.\n\n"
                   "How it Works:\n"
                   "When you perform a destructive action, Devliz intercepts the command and automatically creates a temporary backup of the affected local files before proceeding.\n\n"
                   "Trigger Events (Configurable in Settings):\n"
                   "• Pre-Install: Before a snapshot overwrites your local files, the current local state is archived.\n"
                   "• Pre-Edit / Pre-Update: Before modifying an existing snapshot, its previous state is backed up.\n"
                   "• Pre-Delete: Before permanently erasing a snapshot from the catalogue, a final backup is made.\n\n"
                   "Managing Backups:\n"
                   "These backups consume disk space. From the Backup screen, you can review all currently held safety backups. Once you are confident that your recent operations were successful and you no longer need to revert, you can safely clear the backup storage to reclaim disk space."),
            ),
            "refresh": (
                tr("Refresh and shortcuts"),
                tr("Keep data updated"),
                tr("Devliz monitors its internal state, but sometimes changes happen externally. If you manually edit files inside the Catalogue directory using your OS explorer, or if you sync the folder via cloud storage, Devliz needs to rescan the data.\n\n"
                   "The Global Refresh (F5):\n"
                   "At any point, from any screen, you can press the 'F5' key on your keyboard.\n\n"
                   "What happens during a refresh:\n"
                   "1. The entire application interface will temporarily lock and display 'Updating...' indicators.\n"
                   "2. Devliz will rescan your Catalogue path, recalculating file sizes, validating snapshot metadata, and discovering any new or deleted folders.\n"
                   "3. Once the scan is complete, all dashboards, tables, and search indexes are repopulated with the fresh data.\n\n"
                   "It is highly recommended to perform a refresh if you believe external programs have modified your snapshot files."),
            ),
            "workflow": (
                tr("Recommended workflow"),
                tr("Suggested daily usage"),
                tr("To maximize the value of Devliz, we recommend adopting the following structured workflow:\n\n"
                   "1. Setup & Environment\n"
                   "Start in the Settings screen. Define a robust Catalogue path (preferably on a fast drive). Set up your standard 'Tags' (e.g., 'Production', 'Testing', 'Broken') so you don't have to type them manually every time.\n\n"
                   "2. Capture Base States\n"
                   "Once your local project is working perfectly, open the Catalogue and 'Import' a new snapshot. Give it a descriptive name and tag it as 'Base' or 'Stable'. This is your anchor.\n\n"
                   "3. Branching and Experimentation\n"
                   "When you need to test a risky change, 'Duplicate' your base snapshot in the Catalogue. Install the duplicate. You can now break things locally. If it fails, simply re-install the 'Stable' snapshot to instantly revert. If it succeeds, use 'Update with local' to save the new successful state.\n\n"
                   "4. Auditing and Maintenance\n"
                   "Periodically check the Home screen to monitor your storage usage. Visit the Backup screen to clear out old safety backups, and delete obsolete snapshots from the Catalogue to keep your environment lean and fast."),
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
        log_action(ActionCategory.HELP, ActionType.HELP_CARD_OPENED, title)
        dialog = HelpDetailDialog(title, subtitle, details, self)
        dialog.exec()
