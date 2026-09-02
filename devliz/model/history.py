import sqlite3
from enum import Enum
from pathlib import Path

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from devliz.application.app import app
from devliz.application.i18n import tr


class ActionCategory(str, Enum):
    """
    Enumeration representing different categories of actions in the application.
    """
    BACKUPS = "Backups"
    CATALOGUE = "Catalogue"
    SEARCH = "Search"
    DASHBOARD = "Dashboard"
    SETTINGS = "Settings"
    HELP = "Help"
    HOME = "Home"


class ActionType(str, Enum):
    """
    Enumeration representing specific types of actions that can be logged.
    """
    BACKUP_OPENED_IN_FINDER = "backup.opened.in.finder"
    BACKUP_RESTORED = "backup.restored"
    BACKUP_DELETED = "backup.deleted"
    CATALOGUE_CONFIG_DIALOG_OPENED = "catalogue.config.dialog.opened"
    CATALOGUE_SNAPSHOT_UPDATED = "catalogue.snapshot.updated"
    CATALOGUE_SNAPSHOT_CREATED = "catalogue.snapshot.created"
    CATALOGUE_SNAPSHOT_INSTALLED = "catalogue.snapshot.installed"
    CATALOGUE_SNAPSHOT_DELETED = "catalogue.snapshot.deleted"
    CATALOGUE_SNAPSHOT_DUPLICATED = "catalogue.snapshot.duplicated"
    CATALOGUE_SNAPSHOT_EXPORTED = "catalogue.snapshot.exported"
    CATALOGUE_ASSOCIATED_FOLDERS_EXPORTED = "catalogue.associated.folders.exported"
    CATALOGUE_INSTALLED_FOLDERS_DELETED = "catalogue.installed.folders.deleted"
    CATALOGUE_ASSOCIATED_FOLDERS_UPDATED = "catalogue.associated.folders.updated"
    SEARCH_SNAPSHOT_REMOVED = "search.snapshot.removed"
    SEARCH_STARTED = "search.started"
    SEARCH_STOPPED = "search.stopped"
    SEARCH_COMPLETED = "search.completed"
    SEARCH_PAGE_OPENED = "search.page.opened"
    DASHBOARD_DATA_LOADED = "dashboard.data.loaded"
    DASHBOARD_REFRESH_STARTED = "dashboard.refresh.started"
    DASHBOARD_REFRESH_COMPLETED = "dashboard.refresh.completed"
    DASHBOARD_F5_PRESSED = "dashboard.f5.pressed"
    DASHBOARD_PAGE_CHANGED = "dashboard.page.changed"
    DASHBOARD_APPLICATION_STARTED = "dashboard.application.started"
    SETTINGS_RESTART_CONFIRMED = "settings.restart.confirmed"
    SETTINGS_CATALOGUE_PATH_CHANGED = "settings.catalogue.path.changed"
    SETTINGS_BACKUP_PATH_CHANGED = "settings.backup.path.changed"
    SETTINGS_BACKUP_CLEANED = "settings.backup.cleaned"
    HELP_CARD_OPENED = "help.card.opened"
    OPEN = "open"
    REFRESH = "refresh"


PATH_ACTION_HISTORY_DB = Path(app.get_path()).joinpath("ActionHistory.db")


def _get_connection() -> sqlite3.Connection:
    """
    Creates and returns a SQLite database connection for the action history database.

    Returns:
        sqlite3.Connection: The active SQLite database connection.
    """
    PATH_ACTION_HISTORY_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(PATH_ACTION_HISTORY_DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_action_history_db():
    """
    Initializes the action history database by creating the required table if it does not exist.
    """
    with _get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS action_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                screen_key TEXT NOT NULL,
                action_key TEXT NOT NULL,
                details TEXT NOT NULL DEFAULT ''
            )
            """
        )
        conn.commit()


def log_action(screen_key: ActionCategory | str, action_key: ActionType | str, details: str = ""):
    """
    Logs a new action into the action history database.

    Args:
        screen_key (ActionCategory | str): The screen or category where the action occurred.
        action_key (ActionType | str): The specific action that was performed.
        details (str, optional): Additional details about the action. Defaults to an empty string.
    """
    with _get_connection() as conn:
        conn.execute(
            "INSERT INTO action_history (screen_key, action_key, details) VALUES (?, ?, ?)",
            ((screen_key.value if isinstance(screen_key, ActionCategory) else screen_key), (action_key.value if isinstance(action_key, ActionType) else action_key), details),
        )
        conn.commit()


def list_actions() -> list[dict[str, str]]:
    """
    Retrieves a list of all logged actions from the history database.

    Returns:
        list[dict[str, str]]: A list of dictionaries representing the logged actions, sorted by most recent first.
    """
    with _get_connection() as conn:
        rows = conn.execute(
            "SELECT created_at, screen_key, action_key, details FROM action_history ORDER BY id DESC"
        ).fetchall()

    return [
        {
            "created_at": str(row["created_at"]),
            "screen_key": str(row["screen_key"]),
            "action_key": str(row["action_key"]),
            "details": str(row["details"]),
        }
        for row in rows
    ]


class ActionHistoryTableModel(QAbstractTableModel):
    """
    Model representing a table of action history items for a QTableView.
    """

    def __init__(self):
        """
        Initializes the ActionHistoryTableModel.
        """
        super().__init__()
        self._rows: list[dict[str, str]] = []
        self._headers = [tr("Timestamp"), tr("Screen"), tr("Action"), tr("Details")]

    def set_rows(self, rows: list[dict[str, str]]):
        """
        Sets the list of rows to be displayed in the model.

        Args:
            rows (list[dict[str, str]]): The list of action dictionaries to display.
        """
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()) -> int:
        """
        Returns the number of rows in the table model.

        Args:
            parent (QModelIndex, optional): The parent model index. Defaults to QModelIndex().

        Returns:
            int: The number of rows.
        """
        if parent.isValid():
            return 0
        return len(self._rows)

    def columnCount(self, parent=QModelIndex()) -> int:
        """
        Returns the number of columns in the table model.

        Args:
            parent (QModelIndex, optional): The parent model index. Defaults to QModelIndex().

        Returns:
            int: The number of columns.
        """
        if parent.isValid():
            return 0
        return 4

    def headerData(self, section: int, orientation, role=Qt.ItemDataRole.DisplayRole):
        """
        Retrieves the header data for a specific section and orientation.

        Args:
            section (int): The section index (column or row number).
            orientation (Qt.Orientation): The orientation of the header.
            role (Qt.ItemDataRole, optional): The role for which data is requested. Defaults to Qt.ItemDataRole.DisplayRole.

        Returns:
            Any: The header data, or None if not applicable.
        """
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal and 0 <= section < len(self._headers):
            return self._headers[section]
        return None

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        """
        Retrieves the data for a specific index and role.

        Args:
            index (QModelIndex): The index of the item.
            role (Qt.ItemDataRole, optional): The role for which data is requested. Defaults to Qt.ItemDataRole.DisplayRole.

        Returns:
            Any: The data at the specified index and role, or None if not applicable.
        """
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None

        row = self._rows[index.row()]
        col = index.column()
        if col == 0:
            return row.get("created_at", "")
        if col == 1:
            return tr(row.get("screen_key", ""))
        if col == 2:
            return tr(row.get("action_key", ""))
        if col == 3:
            return row.get("details", "")
        return None
