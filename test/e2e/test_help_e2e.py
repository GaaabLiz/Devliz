from PySide6.QtCore import Qt

def test_help_e2e(qtbot, monkeypatch):
    """
    Test E2E for the Help page.
    Navigates to the Help view and clicks a card.
    """
    from devliz.controller.dashboard import DashboardController

    dashboard = DashboardController()
    qtbot.addWidget(dashboard.view)
    dashboard.start()

    # Wait for initial load
    with qtbot.waitSignal(dashboard.model.signal_on_update_complete, timeout=5000):
        pass

    # Navigate to Help
    dashboard.view.switchTo(dashboard.help.view)
    qtbot.waitUntil(
        lambda: dashboard.view.stackedWidget.currentWidget() == dashboard.help.view,
        timeout=2000
    )

    help_view = dashboard.help.view

    # Mock HelpDetailDialog
    import devliz.view.help
    class FakeHelpDialog:
        def __init__(self, t, s, d, parent=None): pass
        def exec(self): return True
        def exec_(self): return True
    monkeypatch.setattr(devliz.view.help, "HelpDetailDialog", FakeHelpDialog)

    # Click a card
    # We find the first card in the view
    card = help_view.findChildren(devliz.view.help.HelpGuideCard)[0]
    
    # We'll click it
    qtbot.mouseClick(card, Qt.LeftButton)

    # Since we mocked MessageBox, it won't block
    qtbot.wait(200)

    dashboard.model.runner.thread_pool.waitForDone()
