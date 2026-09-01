
def test_dashboard_f5_refresh(qtbot):
    """
    Test E2E for the Dashboard page.
    Simulates the F5 refresh functionality and ensures the UI updates states correctly.
    """
    from devliz.controller.dashboard import DashboardController

    dashboard = DashboardController()
    qtbot.addWidget(dashboard.view)
    dashboard.start()

    # Wait for initial load
    with qtbot.waitSignal(dashboard.model.signal_on_update_complete, timeout=5000):
        pass

    # Simulate pressing F5 by directly updating
    with qtbot.waitSignal(dashboard.model.signal_on_update_complete, timeout=5000):
        dashboard.model.update()

    # The data should be updated
    assert dashboard.cached_data is not None

    dashboard.model.runner.thread_pool.waitForDone()
