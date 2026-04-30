import sqlite3
import sys
import types
from pathlib import Path


def _import_action_history_module(monkeypatch, db_root: Path):
    fake_app_module = types.ModuleType("devliz.application.app")

    class FakeApp:
        @staticmethod
        def get_path():
            return str(db_root)

    fake_app_module.app = FakeApp()

    monkeypatch.setitem(sys.modules, "devliz.application.app", fake_app_module)
    sys.modules.pop("devliz.application.action_history", None)

    import devliz.application.action_history as action_history
    return action_history


def test_init_action_history_db_creates_database(monkeypatch, tmp_path):
    action_history = _import_action_history_module(monkeypatch, tmp_path)

    db_path = tmp_path / "ActionHistory.db"
    assert db_path.exists()

    with sqlite3.connect(db_path) as conn:
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='action_history'").fetchall()

    assert len(tables) == 1
    assert action_history.PATH_ACTION_HISTORY_DB == db_path


def test_log_action_and_list_actions_desc_order(monkeypatch, tmp_path):
    action_history = _import_action_history_module(monkeypatch, tmp_path)

    action_history.log_action("Home", "open", "one")
    action_history.log_action("Catalogue", "refresh", "two")

    rows = action_history.list_actions()
    assert len(rows) == 2

    # L'ordinamento e' DESC per id: l'ultima azione deve essere la prima.
    assert rows[0]["screen_key"] == "Catalogue"
    assert rows[0]["action_key"] == "refresh"
    assert rows[0]["details"] == "two"

    assert rows[1]["screen_key"] == "Home"
    assert rows[1]["action_key"] == "open"
    assert rows[1]["details"] == "one"

