import sys
import types
from pathlib import Path

def test_setting_controller(monkeypatch):
    import devliz.application.i18n
    monkeypatch.setattr(devliz.application.i18n, "tr", lambda x, **kw: x.format(**kw) if kw else x)
    
    # Mock log_action
    import devliz.application.action_history as hist_mod
    actions = []
    def fake_log(c, t, n): actions.append((c,t,n))
    monkeypatch.setattr(hist_mod, "log_action", fake_log)
    
    # Mock QDesktopServices and QProcess
    import PySide6.QtGui
    import PySide6.QtCore
    opened = []
    processes = []
    class FakeQDS:
        @classmethod
        def openUrl(cls, u): opened.append(str(u))
    class FakeProcess:
        @classmethod
        def startDetached(cls, cmd, args): processes.append((cmd, args))
    monkeypatch.setattr(PySide6.QtGui, "QDesktopServices", FakeQDS)
    monkeypatch.setattr(PySide6.QtCore, "QProcess", FakeProcess)
    
    # Mock QApplication
    import PySide6.QtWidgets
    quits = []
    class FakeAppInst:
        def quit(self): quits.append(1)
    class FakeQApp:
        @classmethod
        def instance(cls): return FakeAppInst()
    monkeypatch.setattr(PySide6.QtWidgets, "QApplication", FakeQApp)
    
    # Mock MessageBox
    import qfluentwidgets
    class FakeMessageBox:
        res = True
        def __init__(self, t, d, parent=None): pass
        def exec_(self): return self.res
    monkeypatch.setattr(qfluentwidgets, "MessageBox", FakeMessageBox)
    
    # Mock QFileDialog
    class FakeQFileDialog:
        ret = "/some/dir"
        @classmethod
        def getExistingDirectory(cls, *args): return cls.ret
    monkeypatch.setattr("PySide6.QtWidgets.QFileDialog", FakeQFileDialog)
    
    # Mock UiUtils
    import pylizlib.qtfw.util.ui
    msgs = []
    class FakeUiUtils:
        @classmethod
        def show_message(cls, t, text): msgs.append(text)
    monkeypatch.setattr(pylizlib.qtfw.util.ui, "UiUtils", FakeUiUtils)
    
    # Mock AboutMessageBox
    about_mod = types.ModuleType("pylizlib.qtfw.widgets.dialog.about")
    class FakeAbout:
        def __init__(self, *args): pass
        def exec_(self): return True
    about_mod.AboutMessageBox = FakeAbout
    monkeypatch.setitem(sys.modules, "pylizlib.qtfw.widgets.dialog.about", about_mod)
    
    # Mock app_settings
    app_mod = types.ModuleType("devliz.application.app")
    class ASK: catalogue_path="c"; backup_path="b"
    class AS:
        def set(self, k, v): pass
    app_mod.AppSettings = ASK
    app_mod.app_settings = AS()
    app_mod.PATH_BACKUPS = "/backups"
    app_mod.RESOURCE_ID_LOGO = "logo.png"
    class FakeApp: path = "/app_path"; name="app"; version="1.0"
    app_mod.app = FakeApp()
    monkeypatch.setitem(sys.modules, "devliz.application.app", app_mod)
    
    # Mock View & Model
    view_mod = types.ModuleType("devliz.view.setting")
    class FakeSignal:
        def __init__(self): self.c = None
        def connect(self, f): self.c = f
        def emit(self, *args): self.c(*args) if self.c else None
    class FakeCard:
        def setContent(self, c): pass
    class FakeView:
        def __init__(self):
            self.signal_request_update = FakeSignal()
            self.signal_ask_catalogue_path = FakeSignal()
            self.signal_ask_backup_path = FakeSignal()
            self.signal_open_dir_request = FakeSignal()
            self.signal_clear_backups_request = FakeSignal()
            self.signal_open_about_dialog_request = FakeSignal()
            self.signal_language_changed = FakeSignal()
            self.signal_theme_changed = FakeSignal()
            self.card_general_catalogue = FakeCard()
            self.card_backup_path = FakeCard()
    view_mod.WidgetSettings = FakeView
    monkeypatch.setitem(sys.modules, "devliz.view.setting", view_mod)
    
    dash_mod = types.ModuleType("devliz.model.dashboard")
    class FakeCat:
        def set_catalogue_path(self, p): pass
    class FakeDash:
        def __init__(self): self.snap_catalogue = FakeCat()
        def update(self): pass
    dash_mod.DashboardModel = FakeDash
    monkeypatch.setitem(sys.modules, "devliz.model.dashboard", dash_mod)
    
    sys.modules.pop("devliz.controller.setting_controller", None)
    from devliz.controller.setting_controller import SettingController
    
    ctrl = SettingController(FakeDash())
    
    from devliz.application.action_history import ActionType
    
    # theme/lang changed
    ctrl.view.signal_language_changed.emit()
    assert actions[-1][1] == ActionType.SETTINGS_RESTART_CONFIRMED
    assert len(processes) == 1
    assert len(quits) == 1
    
    # ask cat
    ctrl.view.signal_ask_catalogue_path.emit()
    assert actions[-1][1] == ActionType.SETTINGS_CATALOGUE_PATH_CHANGED
    
    # ask backup
    ctrl.view.signal_ask_backup_path.emit()
    assert actions[-1][1] == ActionType.SETTINGS_BACKUP_PATH_CHANGED
    
    # clear backups
    import shutil
    rmtrees = []
    def fake_rmtree(p): rmtrees.append(p)
    monkeypatch.setattr(shutil, "rmtree", fake_rmtree)
    ctrl.view.signal_clear_backups_request.emit()
    assert actions[-1][1] == ActionType.SETTINGS_BACKUP_CLEANED
    assert len(rmtrees) == 1
    
    # open info dialog
    ctrl.view.signal_open_about_dialog_request.emit()
    
    # open directory
    old_exists = Path.exists
    Path.exists = lambda self: True
    ctrl.view.signal_open_dir_request.emit()
    assert len(opened) == 1
    Path.exists = old_exists
    
    # test cancel / None / errors
    FakeQFileDialog.ret = None
    FakeMessageBox.res = False
    
    ctrl.view.signal_language_changed.emit()
    ctrl.view.signal_ask_catalogue_path.emit()
    ctrl.view.signal_ask_backup_path.emit()
    ctrl.view.signal_clear_backups_request.emit()
    
    # info dialog fail
    FakeAbout.exec_ = lambda self: False
    ctrl.view.signal_open_about_dialog_request.emit()
    
    # test clear backups exception
    FakeMessageBox.res = True
    def fake_rm_fail(p): raise Exception("rm fail")
    monkeypatch.setattr(shutil, "rmtree", fake_rm_fail)
    ctrl.view.signal_clear_backups_request.emit()
    assert "rm fail" in msgs[-1]

