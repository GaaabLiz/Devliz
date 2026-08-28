import sqlite3
from pathlib import Path

from devliz.application.app import app
from enum import Enum

class ActionCategory(str, Enum):
    BACKUPS = "Backups"
    CATALOGUE = "Catalogue"
    SEARCH = "Search"
    DASHBOARD = "Dashboard"
    SETTINGS = "Settings"
    HELP = "Help"
    HOME = "Home"

class ActionType(str, Enum):
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
    PATH_ACTION_HISTORY_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(PATH_ACTION_HISTORY_DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_action_history_db():
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
    with _get_connection() as conn:
        conn.execute(
            "INSERT INTO action_history (screen_key, action_key, details) VALUES (?, ?, ?)",
            ((screen_key.value if isinstance(screen_key, ActionCategory) else screen_key), (action_key.value if isinstance(action_key, ActionType) else action_key), details),
        )
        conn.commit()


def list_actions() -> list[dict[str, str]]:
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


init_action_history_db()
