from pathlib import Path

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from pylizlib.core.os.snap import SnapshotCatalogue
from loguru import logger
from pylizlib.core.os.snap.domain import SnapshotBackupInfo, BackupType

from devliz.application.i18n import tr


class BackupTableModel(QAbstractTableModel):
    """
    Model representing a table of backup items for a QTableView.

    This class provides a table model interface for a list of SnapshotBackupInfo 
    objects, allowing them to be displayed.
    """

    def __init__(self, parent=None):
        """
        Initializes the BackupTableModel.

        Args:
            parent: The parent QObject, optional.
        """
        super().__init__(parent)
        self._backups: list[SnapshotBackupInfo] = []
        self._headers = [tr("File Name"), tr("Snapshot ID"), tr("Backup Type"), tr("Created At")]

    def rowCount(self, parent=QModelIndex()) -> int:
        """
        Returns the number of rows in the table model.

        Args:
            parent (QModelIndex, optional): The parent model index. Defaults to QModelIndex().

        Returns:
            int: The number of rows.
        """
        if parent.isValid():
            return 0
        return len(self._backups)

    def columnCount(self, parent=QModelIndex()) -> int:
        """
        Returns the number of columns in the table model.

        Args:
            parent (QModelIndex, optional): The parent model index. Defaults to QModelIndex().

        Returns:
            int: The number of columns.
        """
        if parent.isValid():
            return 0
        return len(self._headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        """
        Retrieves the data for a specific index and role.

        Args:
            index (QModelIndex): The index of the item.
            role (Qt.ItemDataRole, optional): The role for which data is requested. Defaults to Qt.ItemDataRole.DisplayRole.

        Returns:
            Any: The data at the specified index and role, or None if not applicable.
        """
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
                    return tr("Associated Directories")
                elif backup.backup_type == BackupType.SNAPSHOT_DIRECTORY:
                    return tr("Snapshot Directory")
                return "-"
            elif col == 3:
                if backup.created_at:
                    return backup.created_at.strftime("%Y-%m-%d %H:%M:%S")
                return "-"
        except IndexError:
            return None
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        """
        Retrieves the header data for a specific section and orientation.

        Args:
            section (int): The section index (column or row number).
            orientation (Qt.Orientation): The orientation of the header.
            role (Qt.ItemDataRole, optional): The role for which data is requested. Defaults to Qt.ItemDataRole.DisplayRole.

        Returns:
            Any: The header data, or None if not applicable.
        """
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            try:
                return self._headers[section]
            except IndexError:
                return None
        return None

    def set_backups(self, backups: list[SnapshotBackupInfo]):
        """
        Sets the list of backups to be displayed in the model.

        Args:
            backups (list[SnapshotBackupInfo]): The list of backup information objects.
        """
        self.beginResetModel()
        self._backups = backups if backups is not None else []
        self.endResetModel()

    def get_backup(self, row: int) -> SnapshotBackupInfo | None:
        """
        Retrieves the backup object at the specified row.

        Args:
            row (int): The row index.

        Returns:
            SnapshotBackupInfo | None: The backup object, or None if the row is invalid.
        """
        try:
            return self._backups[row]
        except IndexError:
            return None


class BackupModel:
    """
    Manages the data and business logic for snapshot backups.
    """

    def __init__(self):
        """
        Initializes the BackupModel.
        """
        self._backups: list[SnapshotBackupInfo] = []
        self.table_model = BackupTableModel()

    def load_backups(self, catalogue: SnapshotCatalogue, backup_path: Path):
        """
        Loads backups from the specified path using the given catalogue.

        Args:
            catalogue (SnapshotCatalogue): The catalogue to list backups from.
            backup_path (Path): The path to the backup directory.
        """
        logger.debug(f"Loading backups from: {backup_path}")
        if not backup_path.exists():
            backup_path.mkdir(parents=True, exist_ok=True)
        self._backups = catalogue.list_backups(backup_path)
        self.table_model.set_backups(self._backups)
        logger.debug(f"Loaded {len(self._backups)} backups.")

    def get_backup_at(self, row: int) -> SnapshotBackupInfo | None:
        """
        Retrieves the backup object at the specified row from the table model.

        Args:
            row (int): The row index.

        Returns:
            SnapshotBackupInfo | None: The backup object, or None if the row is invalid.
        """
        return self.table_model.get_backup(row)

    def count(self) -> int:
        """
        Returns the total number of loaded backups.

        Returns:
            int: The number of backups.
        """
        return len(self._backups)
