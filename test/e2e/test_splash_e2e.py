import sys
from devliz.controller.splash import SplashController

def test_splash_e2e_catalogue_exists(qtbot, monkeypatch):
    """Test splash screen when catalogue exists."""
    controller = SplashController()
    qtbot.addWidget(controller.view)

    # Mock so it doesn't block for 1 second
    monkeypatch.setattr("PySide6.QtCore.QEventLoop.exec", lambda self: None)
    monkeypatch.setattr(controller.model, "check_catalogue_path", lambda: True)

    controller.start()
    
    assert controller.view.isHidden()

def test_splash_e2e_catalogue_missing_use_default(qtbot, monkeypatch):
    """Test splash screen when catalogue is missing and user clicks yes."""
    controller = SplashController()
    qtbot.addWidget(controller.view)

    # Mock so it doesn't block for 1 second
    monkeypatch.setattr("PySide6.QtCore.QEventLoop.exec", lambda self: None)
    monkeypatch.setattr(controller.model, "check_catalogue_path", lambda: False)

    from qfluentwidgets import MessageBox
    monkeypatch.setattr(MessageBox, "exec", lambda self: True)
    monkeypatch.setattr(MessageBox, "exec_", lambda self: True)

    controller.start()
    
    # In case 1 (yes), it sets default catalogue path
    from devliz.application.app import app_settings, AppSettings, app
    from pathlib import Path
    assert app_settings.get(AppSettings.catalogue_path) == str(Path(app.path) / "Catalogue")

def test_splash_e2e_catalogue_missing_exit(qtbot, monkeypatch):
    """Test splash screen when catalogue is missing and user clicks cancel."""
    controller = SplashController()
    qtbot.addWidget(controller.view)

    # Mock so it doesn't block for 1 second
    monkeypatch.setattr("PySide6.QtCore.QEventLoop.exec", lambda self: None)
    monkeypatch.setattr(controller.model, "check_catalogue_path", lambda: False)

    from qfluentwidgets import MessageBox
    monkeypatch.setattr(MessageBox, "exec", lambda self: False)
    monkeypatch.setattr(MessageBox, "exec_", lambda self: False)

    # Mock sys.exit
    import sys
    exits = []
    monkeypatch.setattr(sys, "exit", lambda c: exits.append(c))

    controller.start()
    
    # Ensure it exited
    assert len(exits) == 1
    assert exits[0] == 0
