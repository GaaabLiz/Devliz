
def test_catalogue_searcher_controller(monkeypatch):
    import sys
    import types
    dark_mod = types.ModuleType("darkdetect")
    monkeypatch.setitem(sys.modules, "darkdetect", dark_mod)

    import devliz.application.i18n
    monkeypatch.setattr(devliz.application.i18n, "tr", lambda x, **kw: x.format(**kw) if kw else x)
    
    # Mocks removed from here
    
    # Mock log_action
    import devliz.model.history as hist_mod
    actions = []
    def fake_log(c, t, n): actions.append((c,t,n))
    monkeypatch.setattr(hist_mod, "log_action", fake_log)
    
    # Mock QDesktopServices
    import PySide6.QtGui
    opened = []
    class FakeQDS:
        @classmethod
        def openUrl(cls, u): opened.append(str(u))
    monkeypatch.setattr(PySide6.QtGui, "QDesktopServices", FakeQDS)
    
    # Mock MessageBox
    import qfluentwidgets
    class FakeMessageBox:
        res = True
        def __init__(self, t, d, parent=None): pass
        def exec(self): return self.res
    monkeypatch.setattr(qfluentwidgets, "MessageBox", FakeMessageBox)
    
    # Mock View & Model
    view_mod = types.ModuleType("devliz.view.catalogue_searcher")
    class FakeSignal:
        def __init__(self): self.c = None
        def connect(self, f): self.c = f
        def emit(self, *args): self.c(*args) if self.c else None
    class FakeAction:
        def __init__(self): self.triggered = FakeSignal(); self.enabled = True
        def setEnabled(self, e): self.enabled = e
    class FakeBar:
        def __init__(self): self.t = ""
        def text(self): return self.t
    class FakeView:
        def __init__(self, parent=None):
            self.action_start = FakeAction()
            self.action_stop = FakeAction()
            self.signal_delete_requested = FakeSignal()
            self.signal_file_double_clicked = FakeSignal()
            self.signal_tree_open_parent_folder = FakeSignal()
            self.signal_snapshot_double_clicked = FakeSignal()
            self.signal_snapshot_filter_changed = FakeSignal()
            self.search_bar = FakeBar()
            class FakeTree:
                def setModel(self, m): pass
            self.tree_view = FakeTree()
            self.op_status = None
        def setModel(self, m): pass
        def set_operation_status(self, s): self.op_status = s
        def get_selected_query_type(self): return "Q"
        def get_selected_search_target(self): return "T"
        def get_selected_extensions(self): return []
        def update_status_card(self, *args): pass
        def update_snapshot_menu(self, *args): pass
    view_mod.CatalogueSearcherView = FakeView
    monkeypatch.setitem(sys.modules, "devliz.view.catalogue_searcher", view_mod)
    
    model_mod = types.ModuleType("devliz.model.catalogue_searcher")
    class FakeTM:
        def remove_snapshot(self, row): pass
    class FakeTreeMan:
        def __init__(self): self.model = None
    class FakeCat:
        def get_all(self): return []
    class FakeModel:
        def __init__(self, cat):
            self.table_model = FakeTM()
            self.tree_model_manager = FakeTreeMan()
            self.signal_search_finished = FakeSignal()
            self.signal_status_card_update = FakeSignal()
            self.catalogue = FakeCat()
        def search(self, t, q, s, e): pass
        def stop_search(self): pass
        def load_snapshots_from_catalogue(self, s): pass
    model_mod.CatalogueSearcherModel = FakeModel
    monkeypatch.setitem(sys.modules, "devliz.model.catalogue_searcher", model_mod)
    
    sys.modules.pop("devliz.controller.catalogue_searcher", None)
    from devliz.controller.catalogue_searcher import CatalogueSearcherController
    
    ctrl = CatalogueSearcherController(None)
    
    # open
    ctrl.open()
    
    # delete
    from devliz.model.history import ActionType
    ctrl.view.signal_delete_requested.emit(1)
    assert actions[-1][1] == ActionType.SEARCH_SNAPSHOT_REMOVED
    
    # Mock OS path
    import os
    old_isfile = os.path.isfile
    old_isdir = os.path.isdir
    old_exists = os.path.exists
    os.path.isfile = lambda p: "file" in p if isinstance(p, str) else old_isfile(p)
    os.path.isdir = lambda p: "dir" in p if isinstance(p, str) else old_isdir(p)
    os.path.exists = lambda p: "exist" in p if isinstance(p, str) else old_exists(p)
    
    # file click
    ctrl.view.signal_file_double_clicked.emit("a_file.txt")
    assert opened[-1].endswith("a_file.txt')")
    ctrl.view.signal_file_double_clicked.emit("a_dir/") # prints
    
    # tree parent folder
    ctrl.view.signal_tree_open_parent_folder.emit("a_exist/file.txt")
    assert opened[-1].endswith("a_exist')")
    
    # search missing
    ctrl.view.action_start.triggered.emit() # message box
    
    # search ok
    ctrl.view.search_bar.t = "test"
    ctrl.view.action_start.triggered.emit()
    assert actions[-1][1] == ActionType.SEARCH_STARTED
    assert ctrl.view.op_status is True
    assert not ctrl.view.action_start.enabled
    
    # stop
    ctrl.view.action_stop.triggered.emit()
    assert actions[-1][1] == ActionType.SEARCH_STOPPED
    assert ctrl.view.op_status is False
    assert ctrl.view.action_start.enabled
    
    # finish
    ctrl.model.signal_search_finished.emit()
    assert actions[-1][1] == ActionType.SEARCH_COMPLETED
    
    # filter changed
    ctrl.view.signal_snapshot_filter_changed.emit(["some_id"])
    ctrl.view.signal_snapshot_filter_changed.emit([])
    
    # snapshot double click
    class FakeSnap:
        id = "some_id"
        name = "some_name"
    class FakeTMData:
        def get_data(self): return [FakeSnap()]
    ctrl.model.table_model = FakeTMData()
    
    class FakeResultsDialog:
        def __init__(self, n, v): 
            class FakeTree:
                def setModel(self, m): pass
            self.tree_view = FakeTree()
            self.signal_file_double_clicked = FakeSignal()
            self.signal_tree_open_parent_folder = FakeSignal()
        def exec(self): pass
    view_mod.SnapshotResultsDialog = FakeResultsDialog
    
    class FakeTreeModelManager:
        def __init__(self): self.model = None
        def populate_from_results(self, r): pass
    model_mod.SearchResultsTreeModel = FakeTreeModelManager
    
    def fake_get_results(i): return []
    ctrl.model.get_results_for_snapshot = fake_get_results
    
    ctrl.view.signal_snapshot_double_clicked.emit(0)
    
    os.path.isfile = old_isfile
    os.path.isdir = old_isdir
    os.path.exists = old_exists
