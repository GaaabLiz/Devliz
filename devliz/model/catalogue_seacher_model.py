from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from pylizlib.core.os.snap import SnapshotCatalogue


class SearchResultsTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._headers = ["Nome snapshot", "Valori trovati", "Progresso", "ETA"]
        self._data = []

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None
        row = index.row()
        col = index.column()
        if 0 <= row < self.rowCount() and 0 <= col < self.columnCount():
            return self._data[row][col]
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self._headers[section]
        return None

    def update_data(self, new_data: list[list]):
        """Updates the model's data and notifies the view."""
        self.beginResetModel()
        self._data = new_data
        self.endResetModel()


class CatalogueSearcherModel:

    def __init__(self, catalogue: SnapshotCatalogue):
        self.catalogue = catalogue
        self.table_model = SearchResultsTableModel()

    def search(self, text: str, search_type: str, extensions: list[str]):
        """
        Performs a search and updates the table model.
        For now, this is a placeholder.
        """
        # Placeholder data
        print(f"Searching for '{text}' using type '{search_type}' in extensions: {extensions}...")
        mock_data = [
            ["Snapshot 1", "15", "100%", "0s"],
            ["Snapshot 2", "0", "100%", "0s"],
            ["Snapshot 3", "234", "50%", "1m 30s"],
            ["Snapshot 4", "8", "10%", "15m 0s"],
        ]
        self.table_model.update_data(mock_data)

    def stop_search(self):
        """Stops the ongoing search."""
        # In a real implementation, this would stop a background thread.
        print("Stopping search in model.")