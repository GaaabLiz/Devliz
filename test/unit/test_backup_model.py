import datetime
from pathlib import Path

from PySide6.QtCore import Qt
from pylizlib.core.os.snap.domain import SnapshotBackupInfo, BackupType

from devliz.model.backup import BackupTableModel, BackupModel

class FakeSnapshotCatalogue:
    def __init__(self, backups):
        self._backups = backups

    def list_backups(self, backup_path):
        return self._backups

def test_backup_table_model_empty():
    model = BackupTableModel()
    assert model.rowCount() == 0
    assert model.columnCount() == 4
    
    # Test valid parent in rowCount and columnCount
    assert model.rowCount(model.createIndex(0, 0)) == 0
    assert model.columnCount(model.createIndex(0, 0)) == 0
    
    # Test invalid index in data
    assert model.data(model.createIndex(0, 0)) is None
    
    # Test invalid role in data
    assert model.data(model.createIndex(0, 0), role=Qt.ItemDataRole.EditRole) is None
    
    # Test valid role and orientation in headerData
    assert model.headerData(0, Qt.Orientation.Horizontal) == "File Name"
    assert model.headerData(10, Qt.Orientation.Horizontal) is None
    
    # Test invalid role in headerData
    assert model.headerData(0, Qt.Orientation.Horizontal, role=Qt.ItemDataRole.EditRole) is None
    
    # Test invalid orientation in headerData
    assert model.headerData(0, Qt.Orientation.Vertical) is None
    
def test_backup_table_model_with_data():
    model = BackupTableModel()
    
    dt = datetime.datetime(2023, 5, 12, 10, 30, 0)
    info1 = SnapshotBackupInfo(file_name="test1.zip", snapshot_id="snap-123", backup_type=BackupType.ASSOCIATED_DIRECTORIES, created_at=dt, path=Path("test1.zip"), prefix="", is_export=False)
    info2 = SnapshotBackupInfo(file_name="test2.zip", snapshot_id=None, backup_type=BackupType.SNAPSHOT_DIRECTORY, created_at=None, path=Path("test2.zip"), prefix="", is_export=False)
    
    # Cast an unknown type to hit the fallback
    info3 = SnapshotBackupInfo(file_name="test3.zip", snapshot_id=None, backup_type="UNKNOWN", created_at=None, path=Path("test3.zip"), prefix="", is_export=False)
    
    model.set_backups([info1, info2, info3])
    
    assert model.rowCount() == 3
    assert model.columnCount() == 4
    
    # Row 0
    assert model.data(model.createIndex(0, 0)) == "test1.zip"
    assert model.data(model.createIndex(0, 1)) == "snap-123"
    assert model.data(model.createIndex(0, 2)) == "Associated Directories"
    assert model.data(model.createIndex(0, 3)) == "2023-05-12 10:30:00"
    
    # Row 1
    assert model.data(model.createIndex(1, 0)) == "test2.zip"
    assert model.data(model.createIndex(1, 1)) == "-"
    assert model.data(model.createIndex(1, 2)) == "Snapshot Directory"
    assert model.data(model.createIndex(1, 3)) == "-"
    
    # Row 2 (unknown backup type)
    assert model.data(model.createIndex(2, 2)) == "-"
    
    # Invalid index
    assert model.data(model.createIndex(3, 0)) is None
    assert model.data(model.createIndex(0, 5)) is None
    
    assert model.get_backup(0) == info1
    assert model.get_backup(1) == info2
    assert model.get_backup(2) == info3
    assert model.get_backup(3) is None

def test_backup_model_load(tmp_path):
    catalogue = FakeSnapshotCatalogue([
        SnapshotBackupInfo(file_name="fake.zip", snapshot_id="1", backup_type=BackupType.ASSOCIATED_DIRECTORIES, created_at=None, path=Path("fake.zip"), prefix="", is_export=False)
    ])
    
    model = BackupModel()
    assert model.count() == 0
    
    model.load_backups(catalogue, tmp_path / "backups")
    assert model.count() == 1
    assert model.get_backup_at(0).file_name == "fake.zip"
    assert model.get_backup_at(1) is None
    assert (tmp_path / "backups").exists()
