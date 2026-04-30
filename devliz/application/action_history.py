import sqlite3
from pathlib import Path

from devliz.application.app import app

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


def log_action(screen_key: str, action_key: str, details: str = ""):
    with _get_connection() as conn:
        conn.execute(
            "INSERT INTO action_history (screen_key, action_key, details) VALUES (?, ?, ?)",
            (screen_key, action_key, details),
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
