import sys
import types
from pathlib import Path

from PySide6.QtCore import Qt

from pylizlib.core.os.snap import Snapshot, SnapshotSearchResult, SnapshotSearchParams, QueryType, SearchTarget

def _import_searcher_module(monkeypatch):
    # Mock i18n
    i18n_module = types.ModuleType("devliz.application.i18n")
    i18n_module.tr = lambda x, **kwargs: x.format(**kwargs) if kwargs else x
    
    # Mock operation_runner & operation_core
    runner_module = types.ModuleType("pylizlib.qt.handler.operation_runner")
    class FakeRunnerStatistics:
        pass
    class FakeOperationRunner:
        def __init__(self):
            class FakeSignal:
                def connect(self, fn): pass
                def emit(self, *args): pass
            self.runner_start = FakeSignal()
            self.runner_stop = FakeSignal()
            self.runner_finish = FakeSignal()
            self.op_finished = FakeSignal()
            self.op_update_status = FakeSignal()
            self.op_update_progress = FakeSignal()
            self.task_start = FakeSignal()
            self.task_update_message = FakeSignal()
            self.runner_update_progress = FakeSignal()
            self.op_eta_update = FakeSignal()
            self._all_operations = []
        def clear(self): self._all_operations.clear()
        def adds(self, ops): self._all_operations.extend(ops)
        def start(self): pass
        def stop(self): pass
        
    runner_module.OperationRunner = FakeOperationRunner
    runner_module.RunnerStatistics = FakeRunnerStatistics
    
    core_module = types.ModuleType("pylizlib.qt.handler.operation_core")
    class FakeTask:
        def __init__(self, name):
            self.name = name
            class FakeSignal:
                def emit(self, *args): pass
            self.task_update_message = FakeSignal()
        def gen_update_task_progress(self, c, t): pass
    class FakeOperation:
        def __init__(self, tasks, info):
            self.tasks = tasks
            self.info = info
            self.id = "op-1"
        def get_task_results(self): return []
        def is_completed(self): return True
        def is_failed(self): return False
    core_module.Task = FakeTask
    core_module.Operation = FakeOperation
    
    domain_module = types.ModuleType("pylizlib.qt.handler.operation_domain")
    class FakeOperationInfo:
        def __init__(self, **kwargs): pass
    class FakeOperationStatus:
        def __init__(self, value): self.value = value
    domain_module.OperationInfo = FakeOperationInfo
    domain_module.OperationStatus = FakeOperationStatus
    
    monkeypatch.setitem(sys.modules, "devliz.application.i18n", i18n_module)
    monkeypatch.setitem(sys.modules, "pylizlib.qt.handler.operation_runner", runner_module)
    monkeypatch.setitem(sys.modules, "pylizlib.qt.handler.operation_core", core_module)
    monkeypatch.setitem(sys.modules, "pylizlib.qt.handler.operation_domain", domain_module)
    
    sys.modules.pop("devliz.model.catalogue_searcher", None)
    import devliz.model.catalogue_searcher as searcher_module
    return searcher_module

def test_search_results_table_model(monkeypatch):
    searcher_module = _import_searcher_module(monkeypatch)
    model = searcher_module.SearchResultsTableModel()
    
    snap1 = Snapshot(id="s1", name="Snap1", desc="Desc", date_created=None, tags=[], data={}, directories=[])
    snap2 = Snapshot(id="s2", name="Snap2", desc="Desc", date_created=None, tags=[], data={}, directories=[])
    
    model.update_data([snap1, snap2])
    assert model.rowCount() == 2
    assert model.columnCount() == 5
    
    # row 0 initial
    assert model.data(model.createIndex(0, 0)) == "Snap1"
    assert model.data(model.createIndex(0, 1)) == "Pending"
    assert model.data(model.createIndex(0, 2)) == ""
    assert model.data(model.createIndex(0, 3)) == "0%"
    assert model.data(model.createIndex(0, 4)) == "--"
    
    # updates
    model.update_progress_for_snapshot("s1", 50)
    model.update_status_for_snapshot("s1", "Searching")
    model.update_results_for_snapshot("s1", "5")
    
    assert model.data(model.createIndex(0, 3)) == "50%"
    assert model.data(model.createIndex(0, 1)) == "Searching"
    assert model.data(model.createIndex(0, 2)) == "5"
    assert model.data(model.createIndex(0, 5)) is None
    
    # invalid role
    assert model.data(model.createIndex(0, 0), Qt.ItemDataRole.EditRole) is None
    
    assert model.headerData(0, Qt.Orientation.Horizontal) == "Snapshot name"
    assert model.headerData(0, Qt.Orientation.Vertical) is None
    
    # get_data
    assert model.get_data() == [snap1, snap2]
    
    # reset state
    model.reset_search_state()
    assert model.data(model.createIndex(0, 3)) == "0%"
    assert model.data(model.createIndex(0, 1)) == "Pending"
    assert model.data(model.createIndex(0, 2)) == ""
    
    # remove row
    model.remove_snapshot(0)
    assert model.rowCount() == 1
    assert model.data(model.createIndex(0, 0)) == "Snap2"
    
    model.remove_snapshot(5) # out of bounds

def test_search_results_table_model_empty_reset(monkeypatch):
    searcher_module = _import_searcher_module(monkeypatch)
    model = searcher_module.SearchResultsTableModel()
    model.reset_search_state() # should not crash

def test_search_results_tree_model(monkeypatch):
    searcher_module = _import_searcher_module(monkeypatch)
    tree_model = searcher_module.SearchResultsTreeModel()
    
    res1 = SnapshotSearchResult(snapshot_name="S1", file_path=Path("/a/b.txt"), searched_text="abc")
    res2 = SnapshotSearchResult(snapshot_name="S1", file_path=Path("/a/c.txt"), searched_text="abc")
    res3 = SnapshotSearchResult(snapshot_name="S2", file_path=Path("/a/b.txt"), searched_text="abc")
    
    tree_model.populate_from_results([res1, res2, res3])
    
    # Check tree structure roughly
    assert tree_model.model.rowCount() == 2 # S1 and S2
    item_s1 = tree_model.model.item(0)
    assert "S1" in item_s1.text()
    assert item_s1.rowCount() == 2 # 2 files
    
    tree_model.clear()
    assert tree_model.model.rowCount() == 0

def test_snap_search_task(monkeypatch):
    searcher_module = _import_searcher_module(monkeypatch)
    
    class FakeCatalogue: pass
    snap = Snapshot(id="1", name="Snap", desc="Desc", date_created=None, tags=[], data={}, directories=[])
    params = SnapshotSearchParams(query="abc", query_type=QueryType.TEXT, search_target=SearchTarget.FILE_NAME, extensions=[])
    
    class FakeSearcher:
        def __init__(self, cat): pass
        def search(self, s, p, on_progress):
            on_progress("file.txt", 10, 1)
            on_progress("file2.txt", 0, 0)
            return ["result"]
            
    monkeypatch.setattr(searcher_module, "SnapshotSearcher", FakeSearcher)
    
    task = searcher_module.SnapSearchTask(params, snap, FakeCatalogue())
    assert task.execute() == ["result"]

def test_catalogue_searcher_model(monkeypatch):
    searcher_module = _import_searcher_module(monkeypatch)
    
    class FakeCatalogue:
        def get_all(self): return [Snapshot(id="s1", name="S1", desc="Desc", date_created=None, tags=[], data={}, directories=[])]
        
    model = searcher_module.CatalogueSearcherModel(FakeCatalogue())
    
    # Load
    model.load_snapshots_from_catalogue()
    assert model.table_model.rowCount() == 1
    
    model.load_snapshots_from_catalogue(Snapshot(id="s2", name="S2", desc="Desc", date_created=None, tags=[], data={}, directories=[]))
    assert model.table_model.rowCount() == 1
    
    # Status card updates via signals
    msgs = []
    model.signal_status_card_update.connect(lambda m, p, e: msgs.append((m,p,e)))
    
    # Search
    model.search("text", QueryType.TEXT, SearchTarget.FILE_NAME, [])
    assert len(msgs) > 0
    assert msgs[-1][0] == "Starting..."
    
    # stop
    model.stop_search()
    
    # Fake callbacks
    op_status = searcher_module.OperationStatus("Done")
    model._op_id_to_snap_id["op-1"] = "s2"
    model.on_operation_status_changed("op-1", op_status)
    assert model.table_model._status_data["s2"] == "Done"
    
    model.on_operation_status_changed("invalid-op", op_status)
    
    model.on_operation_progress_changed("op-1", 75)
    assert model.table_model._progress_data["s2"] == 75
    
    model.on_operation_progress_changed("invalid-op", 75)
    
    model.on_task_start("T1")
    assert msgs[-1][0] == "Searching..."
    
    model.on_task_update_message("T1", "Scanning...")
    assert msgs[-1][0] == "Scanning..."
    
    model.on_runner_progress(10)
    assert msgs[-1][1] == 10
    
    model.on_eta_update("op-1", "00:01")
    assert msgs[-1][2] == "00:01"
    
    # Finish
    class FakeOp:
        def __init__(self, comp, fail, res):
            self.id = "op-1"
            self.c = comp
            self.f = fail
            self.r = res
        def is_completed(self): return self.c
        def is_failed(self): return self.f
        def get_task_results(self): return self.r
        
    res = SnapshotSearchResult(snapshot_name="S2", file_path=Path("path"), searched_text="abc")
    model.runner._all_operations = [FakeOp(True, False, [[res]])]
    model.on_runner_finished(None)
    assert model.tree_model_manager.model.rowCount() == 1
    
    # Operation finished
    model.on_operation_finished(FakeOp(True, False, [[res]]))
    assert model.table_model._results_count_data["s2"] == "1"
    
    model.on_operation_finished(FakeOp(True, False, []))
    assert model.table_model._results_count_data["s2"] == "0"
    
    model.on_operation_finished(FakeOp(False, True, []))
    assert model.table_model._results_count_data["s2"] == "?"
    
    # Invalid op
    model.on_operation_finished(FakeOp(False, False, [])) # nothing happens but coverage
    
    # Missing op id
    class MissingOp:
        id = "missing"
    model.on_operation_finished(MissingOp())
