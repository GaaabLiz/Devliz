from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from pylizlib.core.os.snap import Snapshot, SnapshotSortKey, SnapshotUtils

from devliz.application.app import app_settings, AppSettings
from devliz.domain.data import DevlizSnapshotData
from devliz.application.i18n import tr


class SnapshotTableModel(QAbstractTableModel):
    """
    A table model for displaying Snapshot data in a QTableView.
    """

    def __init__(self, parent=None):
        """
        Initializes the SnapshotTableModel.

        Args:
            parent: The parent QObject, optional.
        """
        super().__init__(parent)
        self._snapshots: list[Snapshot] = []
        self._headers = []
        self.update_headers()

    def update_headers(self):
        """
        Updates the headers based on application settings.
        Dynamically appends any custom snapshot data keys to the header list.
        """
        headers = [tr("Name"), tr("Description")]
        snap_custom_data = app_settings.get(AppSettings.snap_custom_data)
        for i in snap_custom_data:
            headers.append(i)
        headers.append(tr("Size"))
        headers.append(tr("Date/Time"))
        headers.append(tr("Tags"))
        headers.append(tr("Author"))
        self._headers = headers
        self.headerDataChanged.emit(Qt.Orientation.Horizontal, 0, len(self._headers) - 1)

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
        return len(self._snapshots)

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
            snapshot = self._snapshots[index.row()]
            snap_custom_data_keys = app_settings.get(AppSettings.snap_custom_data)
            table_data = snapshot.get_for_table_array(snap_custom_data_keys)
            
            tags = table_data.pop()
            date = table_data.pop()
            
            author = snapshot.author
            size = f"{snapshot.get_assoc_dir_mb_size:.2f} MB"
            
            table_data.append(size)
            table_data.append(date)
            table_data.append(tags)
            table_data.append(author)
            
            return str(table_data[index.column()])
        except (IndexError, KeyError):
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

    def set_snapshots(self, snapshots: list[Snapshot]):
        """
        Resets the model with a new list of snapshots.

        Args:
            snapshots (list[Snapshot]): The list of snapshots to display.
        """
        self.beginResetModel()
        self._snapshots = snapshots if snapshots is not None else []
        self.endResetModel()

    def get_snapshot(self, row: int) -> Snapshot | None:
        """
        Returns the snapshot at a given row.

        Args:
            row (int): The row index.

        Returns:
            Snapshot | None: The snapshot at the given row, or None if the row is invalid.
        """
        try:
            return self._snapshots[row]
        except IndexError:
            return None


class CatalogueModel:
    """
    Manages the data and business logic for the snapshot catalogue.
    """

    def __init__(self):
        """
        Initializes the CatalogueModel and its underlying table model.
        """
        self._all_snapshots: list[Snapshot] = []
        self._filtered_snapshots: list[Snapshot] = []
        self._is_filtered = False
        self.table_model = SnapshotTableModel()

    def build_snapshot_from_raw(self, raw_data: dict, old_snapshot: Snapshot = None) -> Snapshot:
        """
        Factory method to build a rich Snapshot domain object from raw dictionary data
        provided by the View layer. Handles ID generation, timestamps, and authorship.
        
        Args:
            raw_data (dict): The raw data captured from the UI.
            old_snapshot (Snapshot, optional): The existing snapshot if we are in edit mode.

        Returns:
            Snapshot: The newly constructed or updated Snapshot object.
        """
        import datetime
        from pylizlib.core.os.utils import get_system_username
        from pylizlib.core.data.gen import gen_random_string
        from pylizlib.core.os.snap.domain import SnapshotSettings
        from pylizlib.core.os.snap import SnapDirAssociation

        settings = SnapshotSettings()
        assoc = []
        existing_assocs = {a.original_path: a for a in old_snapshot.directories} if old_snapshot else {}

        index = 0
        for path_str in raw_data["directories"]:
            if path_str in existing_assocs:
                old_a = existing_assocs[path_str]
                assoc.append(SnapDirAssociation(
                    original_path=old_a.original_path,
                    folder_id=old_a.folder_id,
                    index=index,
                    mb_size=old_a.mb_size
                ))
            else:
                assoc.append(SnapDirAssociation(
                    original_path=path_str,
                    folder_id=gen_random_string(settings.folder_id_length),
                    index=index
                ))
            index += 1

        if old_snapshot:
            data = old_snapshot.clone()
            data.name = raw_data["name"]
            data.desc = raw_data["desc"]
            data.tags = raw_data["tags"]
            data.directories = assoc
            data.data = raw_data["custom_data"]
            return data
        else:
            return Snapshot(
                id=raw_data["id"],
                name=raw_data["name"],
                desc=raw_data["desc"],
                tags=raw_data["tags"],
                date_created=datetime.datetime.now(),
                author=get_system_username(),
                directories=assoc,
                data=raw_data["custom_data"]
            )

    def set_snapshots(self, snapshots: list[Snapshot]):
        """
        Sets the master list of snapshots and updates the table view.

        Args:
            snapshots (list[Snapshot]): The list of snapshots to manage.
        """
        self._all_snapshots = snapshots if snapshots is not None else []
        self.filter("")  # Apply current filter or show all

    def get_snapshot_at(self, row: int) -> Snapshot | None:
        """
        Gets the snapshot at a specific row of the current view (filtered or not).

        Args:
            row (int): The row index.

        Returns:
            Snapshot | None: The requested snapshot, or None if the row is invalid.
        """
        return self.table_model.get_snapshot(row)

    def sort(self, sort_key: SnapshotSortKey, reverse: bool = False):
        """
        Sorts the master list of snapshots and updates the view.

        Args:
            sort_key (SnapshotSortKey): The key by which to sort the snapshots.
            reverse (bool, optional): Whether to reverse the sort order. Defaults to False.
        """
        self._all_snapshots = SnapshotUtils.sort_snapshots(self._all_snapshots, sort_key, reverse=reverse)
        # After sorting, the view should reflect the sorted, unfiltered data
        self._is_filtered = False
        self._filtered_snapshots = []
        self.table_model.set_snapshots(self._all_snapshots)

    def filter(self, text: str):
        """
        Filters snapshots based on a text query and updates the view.

        Args:
            text (str): The search query to filter snapshots by.
        """
        text = text.lower().strip()
        if not text:
            self._is_filtered = False
            self.table_model.set_snapshots(self._all_snapshots)
        else:
            self._is_filtered = True
            self._filtered_snapshots = [
                config for config in self._all_snapshots
                if (text in config.name.lower() or
                    text in config.desc.lower() or
                    any(text in tag.lower() for tag in config.tags) or
                    (config.data and any(text in str(value).lower() for value in config.data.values())))
            ]
            self.table_model.set_snapshots(self._filtered_snapshots)

    def count(self) -> int:
        """
        Returns the count of snapshots in the current view (filtered or not).

        Returns:
            int: The number of snapshots currently in the view.
        """
        return len(self._all_snapshots)

    def get_mb_size(self) -> str:
        """
        Returns the total size of all snapshots in MB.

        Returns:
            str: The total size formatted as a string.
        """
        return DevlizSnapshotData(snapshot_list=self._all_snapshots).get_mb_size
