from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from pylizlib.core.os.snap import SnapshotCatalogue, Snapshot
from pylizlib.qt.handler.operation_core import Operation, Task
from pylizlib.qt.handler.operation_domain import OperationInfo


class SearchResultsTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._headers = ["Nome snapshot", "Stato", "Valori trovati", "Progresso", "ETA"]
        self._data: list[Snapshot] = []

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None

        snapshot = self._data[index.row()]
        col = index.column()

        if col == 0:
            return snapshot.name
        elif col == 1:
            return ""  # Stato
        elif col == 2:
            return ""  # Valori trovati
        elif col == 3:
            return "0%"  # Progresso
        elif col == 4:
            return "--"  # ETA
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self._headers[section]
        return None

    def update_data(self, new_data: list[Snapshot]):
        """Updates the model's data and notifies the view."""
        self.beginResetModel()
        self._data = new_data
        self.endResetModel()

    def remove_snapshot(self, row: int):
        if 0 <= row < self.rowCount():
            self.beginRemoveRows(QModelIndex(), row, row)
            del self._data[row]
            self.endRemoveRows()

    def get_data(self):
        return self._data


class SnapSearchTask(Task):

    def __init__(self):
        super().__init__("Snapshot Search Task")


class CatalogueSearcherModel:

    def __init__(self, catalogue: SnapshotCatalogue):
        self.catalogue = catalogue
        self.table_model = SearchResultsTableModel()

    def __get_runner_operations(self) -> list[Operation]:
        ops = []
        for snap in self.table_model.get_data():
            current_task = SnapSearchTask()
            op = Operation([current_task], OperationInfo(name=f"Search in {snap.name})", description="Searching snapshot contents"))
            ops.append(op)
        return ops

    def load_snapshots_from_catalogue(self):
        """Loads all snapshot names from the catalogue and populates the table model."""
        snapshots = self.catalogue.get_all()
        self.table_model.update_data(snapshots)

    def search(self, text: str, search_type: str, extensions: list[str]):
        """
        Performs a search and updates the table model.
        For now, this is a placeholder.
        """
        print(f"Searching for '{text}' using type '{search_type}' in extensions: {extensions}...")

    def stop_search(self):
        """Stops the ongoing search."""
        # In a real implementation, this would stop a background thread.
        print("Stopping search in model.")