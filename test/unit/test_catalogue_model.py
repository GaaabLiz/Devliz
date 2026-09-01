import sys
import types
from datetime import datetime

from PySide6.QtCore import Qt
from pylizlib.core.os.snap import Snapshot, SnapshotSortKey

def _import_catalogue_module(monkeypatch):
    # Mock app_settings
    app_module = types.ModuleType("devliz.application.app")
    class FakeAppSettings:
        def get(self, key):
            if key == "snap_custom_data":
                return ["Author", "Version"]
            return None
    class FakeAppSettingsKeys:
        snap_custom_data = "snap_custom_data"
        
    app_module.app_settings = FakeAppSettings()
    app_module.AppSettings = FakeAppSettingsKeys
    
    # Mock DevlizSnapshotData
    data_module = types.ModuleType("devliz.domain.data")
    class FakeDevlizSnapshotData:
        def __init__(self, snapshot_list):
            self.snapshot_list = snapshot_list
        @property
        def get_mb_size(self):
            return f"{len(self.snapshot_list)}MB"
    data_module.DevlizSnapshotData = FakeDevlizSnapshotData
    
    # Mock i18n
    i18n_module = types.ModuleType("devliz.application.i18n")
    i18n_module.tr = lambda x: x
    
    monkeypatch.setitem(sys.modules, "devliz.application.app", app_module)
    monkeypatch.setitem(sys.modules, "devliz.domain.data", data_module)
    monkeypatch.setitem(sys.modules, "devliz.application.i18n", i18n_module)
    
    sys.modules.pop("devliz.model.catalogue", None)
    import devliz.model.catalogue as catalogue_module
    return catalogue_module

def test_snapshot_table_model_empty(monkeypatch):
    catalogue_module = _import_catalogue_module(monkeypatch)
    model = catalogue_module.SnapshotTableModel()
    
    assert model.rowCount() == 0
    assert model.columnCount() == 8
    
    # Test valid parent in rowCount and columnCount
    assert model.rowCount(model.createIndex(0, 0)) == 0
    assert model.columnCount(model.createIndex(0, 0)) == 0
    
    assert model.data(model.createIndex(0, 0)) is None
    assert model.data(model.createIndex(0, 0), role=Qt.ItemDataRole.EditRole) is None
    
    assert model.headerData(0, Qt.Orientation.Horizontal) == "Name"
    assert model.headerData(2, Qt.Orientation.Horizontal) == "Author"
    assert model.headerData(10, Qt.Orientation.Horizontal) is None
    assert model.headerData(0, Qt.Orientation.Horizontal, role=Qt.ItemDataRole.EditRole) is None
    assert model.headerData(0, Qt.Orientation.Vertical) is None

def test_snapshot_table_model_with_data(monkeypatch):
    catalogue_module = _import_catalogue_module(monkeypatch)
    model = catalogue_module.SnapshotTableModel()
    
    snap1 = Snapshot(
        id="1",
        name="Snap1",
        desc="Description 1",
        date_created=datetime(2023, 1, 1),
        tags=["tag1", "tag2"],
        data={"Author": "John", "Version": "1.0"},
        directories=[]
    )
    snap2 = Snapshot(
        id="2",
        name="Snap2",
        desc="Description 2",
        date_created=datetime(2023, 1, 2),
        tags=[],
        data={},
        directories=[]
    )
    
    model.set_snapshots([snap1, snap2])
    
    assert model.rowCount() == 2
    # table_data from Snapshot.get_for_table_array(custom_data_keys)
    # array format: name, desc, *custom_data_values, date_time_str, tags_str
    assert model.data(model.createIndex(0, 0)) == "Snap1"
    assert model.data(model.createIndex(0, 1)) == "Description 1"
    assert model.data(model.createIndex(0, 2)) == "John"
    assert model.data(model.createIndex(0, 3)) == "1.0"
    
    # invalid index
    assert model.data(model.createIndex(2, 0)) is None
    
    assert model.get_snapshot(0) == snap1
    assert model.get_snapshot(1) == snap2
    assert model.get_snapshot(2) is None
    
    # set None
    model.set_snapshots(None)
    assert model.rowCount() == 0

def test_catalogue_model(monkeypatch):
    catalogue_module = _import_catalogue_module(monkeypatch)
    cat_model = catalogue_module.CatalogueModel()
    
    snap1 = Snapshot(id="1", name="Snap1", desc="Desc 1", date_created=datetime(2023, 1, 1), tags=["foo"], data={}, directories=[])
    snap2 = Snapshot(id="2", name="Snap2", desc="Desc 2", date_created=datetime(2023, 1, 2), tags=["bar"], data={"Author": "Test"}, directories=[])
    
    cat_model.set_snapshots([snap1, snap2])
    assert cat_model.count() == 2
    assert cat_model.get_mb_size() == "2MB"
    assert cat_model.get_snapshot_at(0) == snap1
    
    cat_model.set_snapshots(None)
    assert cat_model.count() == 0

def test_catalogue_model_sort(monkeypatch):
    catalogue_module = _import_catalogue_module(monkeypatch)
    cat_model = catalogue_module.CatalogueModel()
    
    snap1 = Snapshot(id="1", name="B", desc="Desc 1", date_created=datetime(2023, 1, 1), tags=[], data={}, directories=[])
    snap2 = Snapshot(id="2", name="A", desc="Desc 2", date_created=datetime(2023, 1, 2), tags=[], data={}, directories=[])
    
    cat_model.set_snapshots([snap1, snap2])
    cat_model.sort(SnapshotSortKey.NAME)
    
    assert cat_model.get_snapshot_at(0).name == "A"
    assert cat_model.get_snapshot_at(1).name == "B"

def test_catalogue_model_filter(monkeypatch):
    catalogue_module = _import_catalogue_module(monkeypatch)
    cat_model = catalogue_module.CatalogueModel()
    
    snap1 = Snapshot(id="1", name="Alpha", desc="One", date_created=datetime(2023, 1, 1), tags=["foo"], data={"Author": "Dev1"}, directories=[])
    snap2 = Snapshot(id="2", name="Beta", desc="Two", date_created=datetime(2023, 1, 2), tags=["bar"], data={"Version": "2.0"}, directories=[])
    
    cat_model.set_snapshots([snap1, snap2])
    
    # filter by name
    cat_model.filter("alpha")
    assert cat_model.table_model.rowCount() == 1
    assert cat_model.get_snapshot_at(0).name == "Alpha"
    
    # filter by tag
    cat_model.filter("bar")
    assert cat_model.table_model.rowCount() == 1
    assert cat_model.get_snapshot_at(0).name == "Beta"
    
    # filter by custom data value
    cat_model.filter("dev1")
    assert cat_model.table_model.rowCount() == 1
    assert cat_model.get_snapshot_at(0).name == "Alpha"
    
    # filter empty -> show all
    cat_model.filter("")
    assert cat_model.table_model.rowCount() == 2
