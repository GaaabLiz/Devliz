from pathlib import Path

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from pylizlib.core.os.snap import SnapshotCatalogue
from pylizlib.core.os.snap.domain import SnapshotBackupInfo, BackupType

from devliz.application.i18n import tr


class BackupTableModel(QAbstractTableModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._backups: list[SnapshotBackupInfo] = []
        self._headers = [tr("File Name"), tr("Snapshot ID"), tr("Backup Type"), tr("Created At")]

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._backups)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None
        try:
            backup = self._backups[index.row()]
            col = index.column()
            if col == 0:
                return backup.file_name
            elif col == 1:
                return backup.snapshot_id or "-"
            elif col == 2:
                if backup.backup_type == BackupType.ASSOCIATED_DIRECTORIES:
                    return "Associated Directories"
                elif backup.backup_type == BackupType.SNAPSHOT_DIRECTORY:
                    return "Snapshot Directory"
                return "-"
            elif col == 3:
                if backup.created_at:
                    return backup.created_at.strftime("%Y-%m-%d %H:%M:%S")
                return "-"
        except IndexError:
            return None
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            try:
                return self._headers[section]
            except IndexError:
                return None
        return None

    def set_backups(self, backups: list[SnapshotBackupInfo]):
        self.beginResetModel()
        self._backups = backups if backups is not None else []
        self.endResetModel()

    def get_backup(self, row: int) -> SnapshotBackupInfo | None:
        try:
            return self._backups[row]
        except IndexError:
            return None


class BackupModel:

    def __init__(self):
        self._backups: list[SnapshotBackupInfo] = []
        self.table_model = BackupTableModel()

    def load_backups(self, catalogue: SnapshotCatalogue, backup_path: Path):
        if not backup_path.exists():
            backup_path.mkdir(parents=True, exist_ok=True)
        self._backups = catalogue.list_backups(backup_path)
        self.table_model.set_backups(self._backups)

    def get_backup_at(self, row: int) -> SnapshotBackupInfo | None:
        return self.table_model.get_backup(row)

    def count(self) -> int:
        return len(self._backups)
