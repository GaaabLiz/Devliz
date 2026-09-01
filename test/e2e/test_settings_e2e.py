import pytest
from PySide6.QtCore import Qt

def test_settings_toggle_switch(qtbot):
    """
    Test E2E for the Settings page.
    Navigates to settings and toggles a SwitchSettingCard.
    """
    from devliz.controller.dashboard import DashboardController
    from devliz.application.app import AppSettings, snap_settings

    # Initialize
    dashboard = DashboardController()
    qtbot.addWidget(dashboard.view)
    dashboard.start()

    # Wait for the view to be fully loaded
    with qtbot.waitSignal(dashboard.model.signal_on_update_complete, timeout=5000):
        pass

    # Navigate to Settings
    dashboard.view.switchTo(dashboard.settings.view)
    qtbot.waitUntil(
        lambda: dashboard.view.stackedWidget.currentWidget() == dashboard.settings.view,
        timeout=2000
    )

    # Get the view
    settings_view = dashboard.settings.view

    # Find the backup_before_install card
    card = settings_view.card_backup_before_install

    # Check the initial state of the switch
    initial_value = card.switchButton.isChecked()
    initial_snap_value = snap_settings.backup_pre_install

    # It should match the model
    assert initial_value == initial_snap_value

    # We toggle the switch button directly to simulate UI interaction
    qtbot.mouseClick(card.switchButton, Qt.LeftButton)

    # Allow events to process
    qtbot.waitUntil(lambda: card.switchButton.isChecked() != initial_value, timeout=1000)

    # Verify that changing the UI actually updated the application settings!
    assert card.switchButton.isChecked() != initial_value
    
    # Wait for the valueChanged signal to propagate to controllers
    qtbot.wait(100)
    
    assert snap_settings.backup_pre_install == card.switchButton.isChecked()

