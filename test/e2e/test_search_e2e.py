import pytest
from PySide6.QtCore import Qt

def test_search_e2e(qtbot):
    """
    Test E2E for the Search page.
    Navigates to the search page, types a query, and triggers a search.
    """
    from devliz.controller.dashboard import DashboardController

    dashboard = DashboardController()
    qtbot.addWidget(dashboard.view)
    dashboard.start()

    # Wait for the view to be fully loaded
    with qtbot.waitSignal(dashboard.model.signal_on_update_complete, timeout=5000):
        pass

    # Navigate to Search Page
    dashboard.view.switchTo(dashboard.searcher.view)
    qtbot.waitUntil(
        lambda: dashboard.view.stackedWidget.currentWidget() == dashboard.searcher.view,
        timeout=2000
    )

    searcher_view = dashboard.searcher.view

    # Type something into the search bar
    qtbot.keyClicks(searcher_view.search_bar, "test query")

    assert searcher_view.search_bar.text() == "test query"

    # Trigger the search directly
    searcher_view.action_start.trigger()
    
    # Give it a short time to process since there are no snapshots
    qtbot.wait(200)

    # Cleanup any running threads to avoid teardown crashes
    dashboard.model.runner.thread_pool.waitForDone()
    dashboard.searcher.model.runner.thread_pool.waitForDone()

