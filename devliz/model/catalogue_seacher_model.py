from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex, Signal, QObject
from pylizlib.core.os.snap import SnapshotCatalogue, Snapshot, SnapshotSearchParams, SnapshotSearchType, SnapshotSearcher
from pylizlib.qt.handler.operation_core import Operation, Task
from pylizlib.qt.handler.operation_domain import OperationInfo, OperationStatus
from pylizlib.qt.handler.operation_runner import OperationRunner


class SearchResultsTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._headers = ["Nome snapshot", "Stato", "Valori trovati", "Progresso", "ETA"]
        self._data: list[Snapshot] = []
        self._progress_data = {}
        self._status_data = {}

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
            return self._status_data.get(snapshot.id, "Pending")
        elif col == 2:
            return ""  # Valori trovati
        elif col == 3:
            progress = self._progress_data.get(snapshot.id, 0)
            return f"{progress}%"
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
        self._progress_data.clear()
        self._status_data.clear()
        self.endResetModel()

    def remove_snapshot(self, row: int):
        if 0 <= row < self.rowCount():
            self.beginRemoveRows(QModelIndex(), row, row)
            del self._data[row]
            self.endRemoveRows()

    def get_data(self):
        return self._data

    def update_progress_for_snapshot(self, snap_id: str, progress: int):
        """Finds a snapshot by its ID and updates its progress."""
        self._progress_data[snap_id] = progress
        for i, snapshot in enumerate(self._data):
            if snapshot.id == snap_id:
                # Progress is in column 3
                index = self.index(i, 3)
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
                return

    def update_status_for_snapshot(self, snap_id: str, status: str):
        """Finds a snapshot by its ID and updates its status."""
        self._status_data[snap_id] = status
        for i, snapshot in enumerate(self._data):
            if snapshot.id == snap_id:
                # Status is in column 1
                index = self.index(i, 1)
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
                return


class SnapSearchTask(Task):

    def __init__(self, params: SnapshotSearchParams, snapshot: Snapshot, catalogue: SnapshotCatalogue):
        super().__init__(f"Search in {snapshot.name}")
        self.params = params
        self.snapshot = snapshot
        self.searcher = SnapshotSearcher(catalogue)

    def execute(self):
        def on_progress(file_name: str, total_files: int, current_file: int):
            self.task_update_message.emit(self.name, f"Scansione: {file_name}")
            if total_files > 0:
                self.gen_update_task_progress(current_file, total_files)

        results = self.searcher.search(self.snapshot, self.params, on_progress=on_progress)
        return results


class CatalogueSearcherModel(QObject):

    signal_search_started = Signal()
    signal_search_stopped = Signal()
    signal_search_finished = Signal()
    signal_status_card_update = Signal(str, int, str)

    def __init__(self, catalogue: SnapshotCatalogue):
        super().__init__()
        self.catalogue = catalogue
        self.table_model = SearchResultsTableModel()
        self.runner = OperationRunner()

        self._current_message = "In attesa..."
        self._current_progress = 0
        self._current_eta = "--:--"

        self.runner.runner_start.connect(self.signal_search_started)
        self.runner.runner_stop.connect(self.signal_search_stopped)
        self.runner.runner_finish.connect(self.signal_search_finished)
        self.runner.op_update_status.connect(self.on_operation_status_changed)
        self.runner.op_update_progress.connect(self.on_operation_progress_changed)
        self.runner.task_update_message.connect(self.on_task_update_message)
        self.runner.runner_update_progress.connect(self.on_runner_progress)
        self.runner.op_eta_update.connect(self.on_eta_update)

        self._op_id_to_snap_id = {}

    def __get_runner_operations(self, params: SnapshotSearchParams) -> list[Operation]:
        ops = []
        self._op_id_to_snap_id.clear()
        for snap in self.table_model.get_data():
            current_task = SnapSearchTask(params=params, snapshot=snap, catalogue=self.catalogue)
            op = Operation([current_task], OperationInfo(delay_each_task=1.0, name=f"Search in {snap.name})", description="Searching snapshot contents"))
            self._op_id_to_snap_id[op.id] = snap.id
            ops.append(op)
        return ops

    def load_snapshots_from_catalogue(self):
        """Loads all snapshot names from the catalogue and populates the table model."""
        snapshots = self.catalogue.get_all()
        self.table_model.update_data(snapshots)

    def search(self, text: str, search_type: str, extensions: list[str]):
        self._current_message = "Avvio..."
        self._current_progress = 0
        self._current_eta = "--:--"
        self.signal_status_card_update.emit(self._current_message, self._current_progress, self._current_eta)

        params = SnapshotSearchParams(
            query=text,
            search_type=SnapshotSearchType.TEXT if search_type == "Text" else SnapshotSearchType.REGEX,
            extensions=extensions
        )
        operations = self.__get_runner_operations(params)
        self.runner.clear()
        self.runner.adds(operations)
        self.runner.start()

    def stop_search(self):
        """Stops the ongoing search."""
        self.runner.stop()

    def on_operation_status_changed(self, op_id: str, status: OperationStatus):
        if op_id in self._op_id_to_snap_id:
            snap_id = self._op_id_to_snap_id[op_id]
            self.table_model.update_status_for_snapshot(snap_id, status.value)

    def on_operation_progress_changed(self, op_id: str, progress: int):
        if op_id in self._op_id_to_snap_id:
            snap_id = self._op_id_to_snap_id[op_id]
            self.table_model.update_progress_for_snapshot(snap_id, progress)

    def on_task_update_message(self, task_name: str, message: str):
        self._current_message = message
        self.signal_status_card_update.emit(self._current_message, self._current_progress, self._current_eta)

    def on_runner_progress(self, progress: int):
        self._current_progress = progress
        self.signal_status_card_update.emit(self._current_message, self._current_progress, self._current_eta)

    def on_eta_update(self, op_id: str, eta: str):
        self._current_eta = eta
        self.signal_status_card_update.emit(self._current_message, self._current_progress, self._current_eta)