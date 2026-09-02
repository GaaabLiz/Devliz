import sys
import types
from pathlib import Path

from pylizlib.core.os.snap.domain import BackupType


def test_setting_controller(monkeypatch, tmp_path):
    import devliz.application.i18n
    monkeypatch.setattr(devliz.application.i18n, "tr", lambda x, **kw: x.format(**kw) if kw else x)
    
    # Mock log_action
    import devliz.model.history as hist_mod
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
        def processEvents(self, *args, **kwargs): pass
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
    backup_dir = tmp_path / "custom-backups"
    backup_dir.mkdir()
    default_backup_dir = tmp_path / "default-backups"
    default_backup_dir.mkdir()
    managed_backup = backup_dir / "backup_beforeDelete_id_sd_20260831_120000.zip"
    exported_backup = backup_dir / "export_id_sd_20260831_120001.zip"
    unknown_backup = backup_dir / "backup_unknown.zip"
    unrelated_file = backup_dir / "notes.txt"
    default_backup = default_backup_dir / "backup_default_id_sd_20260831_120002.zip"
    for path in (
        managed_backup,
        exported_backup,
        unknown_backup,
        unrelated_file,
        default_backup,
    ):
        path.touch()

    class FakeQFileDialog:
        ret = str(backup_dir)
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
    
    class FakeSignal:
        def __init__(self): self.c = None
        def connect(self, f): self.c = f
        def emit(self, *args): self.c(*args) if self.c else None

    # Mock app_settings
    app_mod = types.ModuleType("devliz.application.app")
    class FakeConfigItem:
        def __init__(self, key):
            self.key = key
            self.valueChanged = FakeSignal()
    class ASK:
        catalogue_path = FakeConfigItem("c")
        backup_path = FakeConfigItem("b")
        backup_before_install = FakeConfigItem("bi")
        backup_before_edit = FakeConfigItem("be")
        backup_before_delete = FakeConfigItem("bd")
        clear_snap_attached_folders_before_install = FakeConfigItem("cb")
    class AS:
        def __init__(self):
            self.values = {"b": str(backup_dir)}
        def set(self, k, v):
            key = k.key if hasattr(k, 'key') else k
            self.values[key] = v
        def get(self, k):
            key = k.key if hasattr(k, 'key') else k
            return self.values.get(key)
    settings = AS()
    app_mod.AppSettings = ASK
    app_mod.app_settings = settings
    app_mod.snap_settings = types.SimpleNamespace(backup_path=None)
    app_mod.PATH_BACKUPS = default_backup_dir
    app_mod.RESOURCE_ID_LOGO = "logo.png"
    class FakeApp: path = "/app_path"; name="app"; version="1.0"
    app_mod.app = FakeApp()
    monkeypatch.setitem(sys.modules, "devliz.application.app", app_mod)
    
    # Mock View & Model
    view_mod = types.ModuleType("devliz.view.setting")
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
        def __init__(self):
            self.list_calls = []
            self.deleted_paths = []
            self.list_error = None
            self.backups = [
                types.SimpleNamespace(
                    path=managed_backup,
                    is_export=False,
                    backup_type=BackupType.SNAPSHOT_DIRECTORY,
                ),
                types.SimpleNamespace(
                    path=exported_backup,
                    is_export=True,
                    backup_type=BackupType.SNAPSHOT_DIRECTORY,
                ),
                types.SimpleNamespace(
                    path=unknown_backup,
                    is_export=False,
                    backup_type=None,
                ),
            ]
        def set_catalogue_path(self, p): pass
        def list_backups(self, path):
            self.list_calls.append(path)
            if self.list_error:
                raise self.list_error
            return self.backups
        def delete_backup(self, path):
            self.deleted_paths.append(path)
            path.unlink()
    class FakeDash:
        def __init__(self): self.snap_catalogue = FakeCat()
        def update(self): pass
    dash_mod.DashboardModel = FakeDash
    monkeypatch.setitem(sys.modules, "devliz.model.dashboard", dash_mod)
    
    sys.modules.pop("devliz.controller.setting_controller", None)
    from devliz.controller.setting_controller import SettingController
    dash = FakeDash()
    ctrl = SettingController(dash)
    
    from devliz.model.history import ActionType
    
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
    assert settings.values["b"] == backup_dir
    assert app_mod.snap_settings.backup_path == backup_dir
    
    # clear backups
    ctrl.view.signal_clear_backups_request.emit()
    assert actions[-1][1] == ActionType.SETTINGS_BACKUP_CLEANED
    assert actions[-1][2] == f"path={backup_dir}; deleted=1"
    assert dash.snap_catalogue.list_calls == [backup_dir]
    assert dash.snap_catalogue.deleted_paths == [managed_backup]
    assert not managed_backup.exists()
    assert exported_backup.exists()
    assert unknown_backup.exists()
    assert unrelated_file.exists()
    assert default_backup.exists()
    
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

    list_calls_before_cancel = len(dash.snap_catalogue.list_calls)
    ctrl.view.signal_language_changed.emit()
    ctrl.view.signal_ask_catalogue_path.emit()
    ctrl.view.signal_ask_backup_path.emit()
    ctrl.view.signal_clear_backups_request.emit()
    assert len(dash.snap_catalogue.list_calls) == list_calls_before_cancel
    
    # info dialog fail
    FakeAbout.exec_ = lambda self: False
    ctrl.view.signal_open_about_dialog_request.emit()
    
    # test clear backups error
    FakeMessageBox.res = True
    dash.snap_catalogue.list_error = OSError("list fail")
    ctrl.view.signal_clear_backups_request.emit()
    assert "list fail" in msgs[-1]

    # A missing configured directory is treated as an empty backup folder.
    dash.snap_catalogue.list_error = None
    missing_dir = tmp_path / "missing-backups"
    settings.values["b"] = missing_dir
    list_calls_before_missing = len(dash.snap_catalogue.list_calls)
    ctrl.view.signal_clear_backups_request.emit()
    assert len(dash.snap_catalogue.list_calls) == list_calls_before_missing
    assert actions[-1][2] == f"path={missing_dir}; deleted=0"
