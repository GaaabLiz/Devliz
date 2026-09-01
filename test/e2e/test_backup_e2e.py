import pytest
from PySide6.QtCore import Qt, QPoint

def test_backup_e2e_empty(qtbot, monkeypatch):
    """
    Test E2E for Backup view with an empty table.
    """
    from devliz.controller.dashboard import DashboardController

    dashboard = DashboardController()
    qtbot.addWidget(dashboard.view)
    dashboard.start()

    # Wait for initial load
    with qtbot.waitSignal(dashboard.model.signal_on_update_complete, timeout=5000):
        pass

    # Navigate to Backup
    dashboard.view.switchTo(dashboard.backup.view)
    qtbot.waitUntil(
        lambda: dashboard.view.stackedWidget.currentWidget() == dashboard.backup.view,
        timeout=2000
    )

    backup_view = dashboard.backup.view

    # Mock context menu because we don't want it to block if it does
    menu_exec_called = []
    class FakeRoundMenu:
        def __init__(self, parent): pass
        def addAction(self, action): pass
        def exec(self, pos): menu_exec_called.append(True)
    
    import devliz.view.backup
    monkeypatch.setattr(devliz.view.backup, "RoundMenu", FakeRoundMenu)

    # Click on the table (it's empty, so indexAt will be invalid)
    # This triggers the _show_context_menu
    backup_view.table.customContextMenuRequested.emit(QPoint(10, 10))

    # Wait a bit
    qtbot.wait(200)

    # Since there are no rows, it should NOT have opened the menu
    assert len(menu_exec_called) == 0

    dashboard.model.runner.thread_pool.waitForDone()
