import sys
import types

def test_splash_controller(monkeypatch):
    import devliz.application.i18n
    monkeypatch.setattr(devliz.application.i18n, "tr", lambda x, **kw: x.format(**kw) if kw else x)
    
    # Mock QTimer, QEventLoop
    import PySide6.QtCore
    class FakeLoop:
        def quit(self): pass
        def exec(self): pass
    class FakeTimer:
        @classmethod
        def singleShot(cls, t, f): f()
    monkeypatch.setattr(PySide6.QtCore, "QEventLoop", FakeLoop)
    monkeypatch.setattr(PySide6.QtCore, "QTimer", FakeTimer)
    
    # Mock MessageBox
    import qfluentwidgets
    class FakeButton:
        def setText(self, t): pass
    class FakeMessageBox:
        res = True
        def __init__(self, t, d, parent=None):
            self.yesButton = FakeButton()
            self.cancelButton = FakeButton()
        def exec(self): return self.res
    monkeypatch.setattr(qfluentwidgets, "MessageBox", FakeMessageBox)
    
    # Mock View & Model
    view_mod = types.ModuleType("devliz.view.splash")
    class FakeView:
        def show_splash(self): pass
        def hide_overlay(self): pass
        def close_splash(self): pass
    view_mod.SplashWindow = FakeView
    monkeypatch.setitem(sys.modules, "devliz.view.splash", view_mod)
    
    model_mod = types.ModuleType("devliz.model.splash")
    class FakeModel:
        def __init__(self):
            self.valid = True
            self.default_set = False
        def check_catalogue_path(self): return self.valid
        def get_catalogue_path_str(self): return "cat"
        def set_default_catalogue_path(self): self.default_set = True
    model_mod.SplashModel = FakeModel
    monkeypatch.setitem(sys.modules, "devliz.model.splash", model_mod)
    
    sys.modules.pop("devliz.controller.splash", None)
    from devliz.controller.splash import SplashController
    
    ctrl = SplashController()
    
    # start valid
    ctrl.start()
    assert not ctrl.model.default_set
    
    # start invalid, user says yes (use default)
    ctrl.model.valid = False
    ctrl.start()
    assert ctrl.model.default_set
    
    # start invalid, user says cancel (sys.exit)
    FakeMessageBox.res = False
    exits = []
    monkeypatch.setattr(sys, "exit", lambda c: exits.append(c))
    ctrl.start()
    assert len(exits) == 1
    assert exits[0] == 0

