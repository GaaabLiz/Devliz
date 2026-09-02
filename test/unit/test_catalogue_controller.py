import sys
import types
from pathlib import Path

def test_catalogue_controller(monkeypatch):
    # Mock i18n
    import devliz.application.i18n
    monkeypatch.setattr(devliz.application.i18n, "tr", lambda x, **kw: x.format(**kw) if kw else x)
    
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
    
    # Mock DialogConfig
    dl_mod = types.ModuleType("devliz.view.catalogue_imp_dialog")
    class FakeSnapshot:
        def __init__(self, id, name): self.id = id; self.name = name
    class FakeDialogConfig:
        res = True
        def __init__(self, d, e, s): self.output_data = FakeSnapshot("d1", "D1")
        def exec(self): return self.res
    dl_mod.DialogConfig = FakeDialogConfig
    monkeypatch.setitem(sys.modules, "devliz.view.catalogue_imp_dialog", dl_mod)
    
    # Mock log_action
    import devliz.model.action_history as hist_mod
    actions = []
    def fake_log(c, t, n): actions.append((c,t,n))
    monkeypatch.setattr(hist_mod, "log_action", fake_log)
    
    # App Settings mock
    import devliz.application.app
    class AS:
        def get(self, k): return True
    monkeypatch.setattr(devliz.application.app, "app_settings", AS())
    class FakeApp: path = Path("/app")
    monkeypatch.setattr(devliz.application.app, "app", FakeApp())
    
    # Mock pylizlib core Utils for open_system_folder
    import pylizlib.core.os.utils
    opened = []
    def fake_open(p): opened.append(p)
    pylizlib.core.os.utils.open_system_folder = fake_open
    
    import PySide6.QtGui
    class FakeQDS:
        @classmethod
        def openUrl(cls, u): opened.append(str(u))
    monkeypatch.setattr(PySide6.QtGui, "QDesktopServices", FakeQDS)
    
    # Mock View & Model
    view_mod = types.ModuleType("devliz.view.catalogue")
    class FakeSignal:
        def __init__(self): self.c = None
        def connect(self, f): self.c = f
        def emit(self, *args): self.c(*args) if self.c else None
    class FakeView:
        def __init__(self, m):
            self.m = m
            self.signal_import_requested = FakeSignal()
            self.signal_open_catalogue_folder_requested = FakeSignal()
            self.signal_install_requested = FakeSignal()
            self.signal_edit_requested = FakeSignal()
            self.signal_delete_requested = FakeSignal()
            self.signal_open_folder_requested = FakeSignal()
            self.signal_duplicate_requested = FakeSignal()
            self.signal_sort_requested = FakeSignal()
            self.signal_search_internal_content_all = FakeSignal()
            self.signal_search_internal_content_single = FakeSignal()
            self.signal_export_request_snapshot = FakeSignal()
            self.signal_export_request_assoc_folders = FakeSignal()
            self.signal_delete_installed_folders_requested = FakeSignal()
            self.signal_update_with_local_dirs_requested = FakeSignal()
            self.signal_open_assoc_folder_requested = FakeSignal()
            self.sort_calls = 0
        def sort(self): self.sort_calls += 1
        def reload_data(self): pass
    view_mod.SnapshotCatalogueWidget = FakeView
    monkeypatch.setitem(sys.modules, "devliz.view.catalogue", view_mod)
    
    model_mod = types.ModuleType("devliz.model.catalogue")
    class FakeTM:
        def update_headers(self): pass
    class FakeModel:
        def __init__(self): self.table_model = FakeTM()
        def set_snapshots(self, l): pass
    model_mod.CatalogueModel = FakeModel
    monkeypatch.setitem(sys.modules, "devliz.model.catalogue", model_mod)
    
    # Mock DashboardModel
    dash_mod = types.ModuleType("devliz.model.dashboard")
    class FakeTask:
        def update_task_progress(self, p): pass
    class FakeCat:
        def update_snapshot_by_objs(self, o, n): pass
        def add(self, o, progress_callback): progress_callback(10)
        def remove_installed_copies(self, id): pass
        def install(self, s, clear_destination=True, progress_callback=None): progress_callback(10) if progress_callback else None
        def delete(self, s): pass
        def get_snap_directory_path(self, s): return Path("/snap/dir")
        def duplicate_by_id(self, id): pass
        def export_snapshot(self, id, d): pass
        def export_assoc_dirs(self, id, d): pass
        def update_assoc_with_installed(self, id): pass
    class FakeDash:
        def __init__(self):
            self.cached_data = None
            self.snap_catalogue = FakeCat()
        def run_heavy_operation(self, n, d, func, success_msg_title="", success_msg="", update_dashboard=True):
            func(FakeTask())
    dash_mod.DashboardModel = FakeDash
    monkeypatch.setitem(sys.modules, "devliz.model.dashboard", dash_mod)

    sys.modules.pop("devliz.controller.catalogue", None)
    from devliz.controller.catalogue import CatalogueController
    from devliz.domain.data import DevlizSnapshotData
    
    search_page_calls = []
    ctrl = CatalogueController(FakeDash(), lambda s: search_page_calls.append(s))
    ctrl.init()
    
    ctrl.update_data(DevlizSnapshotData([]))
    
    snap = FakeSnapshot("s1", "Snap1")
    
    from devliz.model.action_history import ActionType
    # __open_config_dialog (edit_mode=False) -> signal_import_requested
    ctrl.view.signal_import_requested.emit()
    assert actions[-1][1] == ActionType.CATALOGUE_SNAPSHOT_CREATED
    
    # __open_config_dialog (edit_mode=True) -> signal_edit_requested
    ctrl.view.signal_edit_requested.emit(snap)
    assert actions[-1][1] == ActionType.CATALOGUE_SNAPSHOT_UPDATED
    
    # __install_snapshot
    ctrl.view.signal_install_requested.emit(snap)
    assert actions[-1][1] == ActionType.CATALOGUE_SNAPSHOT_INSTALLED
    
    # __delete_snapshot
    ctrl.view.signal_delete_requested.emit(snap)
    assert actions[-1][1] == ActionType.CATALOGUE_SNAPSHOT_DELETED
    
    # __open_snap_directory (exists mock)
    old_exists = Path.exists
    Path.exists = lambda self: True
    ctrl.view.signal_open_folder_requested.emit(snap)
    assert "/snap/dir" in opened[-1]
    
    # __open_snap_directory (not exists mock)
    Path.exists = lambda self: False
    ctrl.view.signal_open_folder_requested.emit(snap)
    assert "no longer exists" in msgs[-1]
    Path.exists = old_exists
    
    # __duplicate_snapshot
    ctrl.view.signal_duplicate_requested.emit(snap)
    assert actions[-1][1] == ActionType.CATALOGUE_SNAPSHOT_DUPLICATED
    
    # sort
    ctrl.view.signal_sort_requested.emit()
    assert ctrl.view.sort_calls == 1
    
    # searcher all
    ctrl.view.signal_search_internal_content_all.emit()
    assert search_page_calls[-1] is None
    
    # searcher single
    ctrl.view.signal_search_internal_content_single.emit(snap)
    assert search_page_calls[-1] == snap
    
    # __export_snapshot
    ctrl.view.signal_export_request_snapshot.emit(snap)
    assert actions[-1][1] == ActionType.CATALOGUE_SNAPSHOT_EXPORTED
    
    # __export_snapshot_folders
    ctrl.view.signal_export_request_assoc_folders.emit(snap)
    assert actions[-1][1] == ActionType.CATALOGUE_ASSOCIATED_FOLDERS_EXPORTED
    
    # __delete_snap_installed_dirs
    ctrl.view.signal_delete_installed_folders_requested.emit(snap)
    assert actions[-1][1] == ActionType.CATALOGUE_INSTALLED_FOLDERS_DELETED
    
    # __update_assoc_dirs_from_installed
    ctrl.view.signal_update_with_local_dirs_requested.emit(snap)
    assert actions[-1][1] == ActionType.CATALOGUE_ASSOCIATED_FOLDERS_UPDATED
    
    # test cancel modal / dialogs
    FakeDialogConfig.res = False
    ctrl.view.signal_import_requested.emit() # does nothing
    
    FakeMessageBox.res = False
    ctrl.view.signal_install_requested.emit(snap)
    ctrl.view.signal_delete_requested.emit(snap)
    ctrl.view.signal_export_request_snapshot.emit(snap)
    ctrl.view.signal_export_request_assoc_folders.emit(snap)
    ctrl.view.signal_delete_installed_folders_requested.emit(snap)
    ctrl.view.signal_update_with_local_dirs_requested.emit(snap)
    
    FakeMessageBox.res = True
    FakeQFileDialog.ret = ""
    ctrl.view.signal_export_request_snapshot.emit(snap)
    ctrl.view.signal_export_request_assoc_folders.emit(snap)
    
    # test exceptions
    def error_action(*args, **kw): raise Exception("fail")
    
    import devliz.controller.catalogue
    old_dc = devliz.controller.catalogue.DialogConfig
    devliz.controller.catalogue.DialogConfig = error_action
    ctrl.view.signal_edit_requested.emit(snap) # emits show_message
    devliz.controller.catalogue.DialogConfig = old_dc
    
    old_exec = FakeDialogConfig.exec
    FakeDialogConfig.exec = error_action
    ctrl.view.signal_import_requested.emit() # caught, no assert
    FakeDialogConfig.exec = old_exec
    
    FakeMessageBox.__init__ = error_action
    ctrl.view.signal_install_requested.emit(snap)
    ctrl.view.signal_delete_requested.emit(snap)
    ctrl.view.signal_export_request_snapshot.emit(snap)
    ctrl.view.signal_export_request_assoc_folders.emit(snap)
    ctrl.view.signal_delete_installed_folders_requested.emit(snap)
    ctrl.view.signal_update_with_local_dirs_requested.emit(snap)
    
    ctrl.search_page_opener = None
    ctrl.view.signal_search_internal_content_all.emit()
    ctrl.view.signal_search_internal_content_single.emit(snap)
    
    # test duplicate exception
    ctrl.dash_model.run_heavy_operation = error_action
    ctrl.view.signal_duplicate_requested.emit(snap)

