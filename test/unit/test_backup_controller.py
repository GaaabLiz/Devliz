import sys
import types
from pathlib import Path

def test_backup_controller(monkeypatch):
    import devliz.application.i18n
    monkeypatch.setattr(devliz.application.i18n, "tr", lambda x, **kw: x.format(**kw) if kw else x)
    
    # Mock action history
    import devliz.application.action_history as hist_mod
    actions = []
    def fake_log(c, t, d): actions.append((c, t, d))
    monkeypatch.setattr(hist_mod, "log_action", fake_log)
    
    # Mock UiUtils
    import pylizlib.qtfw.util.ui
    msgs = []
    class FakeUiUtils:
        @classmethod
        def show_message(cls, t, m): msgs.append(m)
    monkeypatch.setattr(pylizlib.qtfw.util.ui, "UiUtils", FakeUiUtils)
    
    # Mock app_settings
    app_mod = types.ModuleType("devliz.application.app")
    class ASK: backup_path = "b"
    class AS:
        def get(self, k): return "/backup/path"
    app_mod.AppSettings = ASK
    app_mod.app_settings = AS()
    monkeypatch.setitem(sys.modules, "devliz.application.app", app_mod)
    
    # Mock View & Signals
    view_mod = types.ModuleType("devliz.view.backup")
    class FakeSignal:
        def __init__(self): self.c = None
        def connect(self, f): self.c = f
        def emit(self, *args): self.c(*args) if self.c else None
    class FakeView:
        def __init__(self, _model=None):
            self.signal_open_requested = FakeSignal()
            self.signal_restore_requested = FakeSignal()
            self.signal_delete_requested = FakeSignal()
            self.reloaded = False
        def reload_data(self):
            self.reloaded = True
    view_mod.BackupView = FakeView
    monkeypatch.setitem(sys.modules, "devliz.view.backup", view_mod)
    
    model_mod = types.ModuleType("devliz.model.backup")
    class FakeModel:
        def load_backups(self, c, p): pass
        def get_all_backups(self, p): return []
    model_mod.BackupModel = FakeModel
    monkeypatch.setitem(sys.modules, "devliz.model.backup", model_mod)
    
    # Fake catalogue
    class FakeCat:
        def restore_backup(self, p):
            if "error" in str(p): raise Exception("fail restore")
        def delete_backup(self, p):
            if "error" in str(p): raise Exception("fail delete")
            
    # Mock QDesktopServices
    opened = []
    class FakeQDS:
        @classmethod
        def openUrl(cls, u): opened.append(u.toLocalFile())
    
    # Mock MessageBox
    class FakeMessageBox:
        res = True
        def __init__(self, t, d, parent=None): pass
        def exec_(self): return self.res

    # Import Controller
    sys.modules.pop("devliz.controller.backup", None)
    from devliz.controller.backup import BackupController
    from pylizlib.core.os.snap.domain import SnapshotBackupInfo
    
    monkeypatch.setattr("devliz.controller.backup.QDesktopServices", FakeQDS)
    monkeypatch.setattr("devliz.controller.backup.MessageBox", FakeMessageBox)
    
    cat = FakeCat()
    ctrl = BackupController(cat)
    
    # update_data
    ctrl.update_data()
    assert ctrl.view.reloaded
    
    refreshes = []
    ctrl.signal_request_refresh.connect(lambda: refreshes.append(1))
    
    # test __handle_open
    b1 = SnapshotBackupInfo(file_name="f1", path=Path("/a/b/f1"), snapshot_id=None, backup_type=None, created_at=None, prefix="", is_export=False)
    ctrl.view.signal_open_requested.emit(b1)
    assert opened == ["/a/b"]
    assert actions[-1][1] == hist_mod.ActionType.BACKUP_OPENED_IN_FINDER
    
    # test __handle_restore
    ctrl.view.signal_restore_requested.emit(b1)
    assert len(refreshes) == 1
    assert actions[-1][1] == hist_mod.ActionType.BACKUP_RESTORED
    
    # test __handle_delete
    ctrl.view.signal_delete_requested.emit(b1)
    assert len(refreshes) == 1
    assert actions[-1][1] == hist_mod.ActionType.BACKUP_DELETED
    
    # test MessageBox cancel
    FakeMessageBox.res = False
    ctrl.view.signal_restore_requested.emit(b1)
    assert len(refreshes) == 1 # no change
    ctrl.view.signal_delete_requested.emit(b1)
    assert len(refreshes) == 1 # no change
    
    # test exceptions
    FakeMessageBox.res = True
    b_err = SnapshotBackupInfo(file_name="error", path=Path("/a/b/error"), snapshot_id=None, backup_type=None, created_at=None, prefix="", is_export=False)
    ctrl.view.signal_restore_requested.emit(b_err)
    assert "fail restore" in msgs[-1]
    
    ctrl.view.signal_delete_requested.emit(b_err)
    assert "fail delete" in msgs[-1]
    
    # open exception
    def fake_openUrl_err(u): raise Exception("open error")
    FakeQDS.openUrl = fake_openUrl_err
    ctrl.view.signal_open_requested.emit(b_err)
    # just asserts it doesn't crash

