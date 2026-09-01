import pytest
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

    # Mock MessageBox
    import devliz.controller.splash
    class FakeMessageBox:
        def __init__(self, t, d, parent=None): 
            self.yesButton = type('obj', (object,), {'setText': lambda self, s: None})()
            self.cancelButton = type('obj', (object,), {'setText': lambda self, s: None})()
        def exec(self): return True
    monkeypatch.setattr(devliz.controller.splash, "MessageBox", FakeMessageBox)
    
    # Mock set_default_catalogue_path
    called = []
    monkeypatch.setattr(controller.model, "set_default_catalogue_path", lambda: called.append(True))

    controller.start()
    
    assert called == [True]
    assert controller.view.isHidden()

def test_splash_e2e_catalogue_missing_exit(qtbot, monkeypatch):
    """Test splash screen when catalogue is missing and user clicks cancel."""
    controller = SplashController()
    qtbot.addWidget(controller.view)

    # Mock so it doesn't block for 1 second
    monkeypatch.setattr("PySide6.QtCore.QEventLoop.exec", lambda self: None)
    monkeypatch.setattr(controller.model, "check_catalogue_path", lambda: False)

    # Mock MessageBox
    import devliz.controller.splash
    class FakeMessageBox:
        def __init__(self, t, d, parent=None): 
            self.yesButton = type('obj', (object,), {'setText': lambda self, s: None})()
            self.cancelButton = type('obj', (object,), {'setText': lambda self, s: None})()
        def exec(self): return False
    monkeypatch.setattr(devliz.controller.splash, "MessageBox", FakeMessageBox)
    
    # Mock sys.exit
    exited = []
    monkeypatch.setattr(sys, "exit", lambda code: exited.append(code))

    controller.start()
    
    assert exited == [0]
