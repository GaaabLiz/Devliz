
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex, Signal, QObject
from PySide6.QtGui import QStandardItemModel, QStandardItem

from loguru import logger
from pylizlib.core.os.snap import SnapshotCatalogue, Snapshot, SnapshotSearchParams, QueryType, SearchTarget, SnapshotSearcher, \
    SnapshotSearchResult
from pylizlib.qt.handler.operation_core import Operation, Task
from pylizlib.qt.handler.operation_domain import OperationInfo, OperationStatus
from pylizlib.qt.handler.operation_runner import OperationRunner, RunnerStatistics

from devliz.application.i18n import tr


class SearchResultsTableModel(QAbstractTableModel):
    """
    A table model for displaying snapshots being searched.

    This model manages the data for a table view that shows a list of snapshots,
    their search status, the number of results found, and the progress of the
    search operation for each.
    """

    def __init__(self, parent=None):
        """
        Initializes the SearchResultsTableModel.

        Args:
            parent (QObject, optional): The parent object. Defaults to None.
        """
        super().__init__(parent)
        self._headers = [tr("Snapshot name"), tr("Status"), tr("Values found"), tr("Progress"), "ETA"]
        self._data: list[Snapshot] = []
        self._progress_data = {}
        self._status_data = {}
        self._results_count_data = {}

    def rowCount(self, parent=QModelIndex()):
        """Returns the number of rows in the model."""
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        """Returns the number of columns in the model."""
        return len(self._headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        """
        Returns the data for a given index and role.

        Args:
            index (QModelIndex): The index to retrieve data for.
            role (Qt.ItemDataRole): The role for which to retrieve data.

        Returns:
            Any: The data for the specified index and role.
        """
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None

        snapshot = self._data[index.row()]
        col = index.column()

        if col == 0:
            return snapshot.name
        elif col == 1:
            return self._status_data.get(snapshot.id, tr("Pending"))
        elif col == 2:
            return self._results_count_data.get(snapshot.id, "")
        elif col == 3:
            progress = self._progress_data.get(snapshot.id, 0)
            return f"{progress}%"
        elif col == 4:
            return "--"  # ETA
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        """Returns the header data for a given section, orientation, and role."""
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self._headers[section]
        return None

    def update_data(self, new_data: list[Snapshot]):
        """
        Updates the model's data with a new list of snapshots and notifies the view.
        
        Args:
            new_data (list[Snapshot]): The new list of snapshots to display.
        """
        self.beginResetModel()
        self._data = new_data
        self._progress_data.clear()
        self._status_data.clear()
        self.endResetModel()

    def remove_snapshot(self, row: int):
        """
        Removes a snapshot from the model at the given row.

        Args:
            row (int): The row index of the snapshot to remove.
        """
        if 0 <= row < self.rowCount():
            self.beginRemoveRows(QModelIndex(), row, row)
            del self._data[row]
            self.endRemoveRows()

    def reset_search_state(self):
        """Resets the progress, status, and results data for all rows."""
        if not self._data:
            return
        self._progress_data.clear()
        self._status_data.clear()
        self._results_count_data.clear()
        # Emit dataChanged for all rows and the relevant columns (status, progress, results)
        top_left = self.index(0, 1)
        bottom_right = self.index(self.rowCount() - 1, 3)
        self.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.DisplayRole])

    def get_data(self) -> list[Snapshot]:
        """
        Returns the list of all snapshots currently in the model.

        Returns:
            list[Snapshot]: The list of snapshots.
        """
        return self._data

    def _emit_data_changed(self, snap_id: str, column: int):
        """
        Helper method to emit dataChanged for a specific snapshot and column.
        """
        for i, snapshot in enumerate(self._data):
            if snapshot.id == snap_id:
                index = self.index(i, column)
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
                return

    def update_progress_for_snapshot(self, snap_id: str, progress: int):
        """
        Finds a snapshot by its ID and updates its progress percentage.

        Args:
            snap_id (str): The ID of the snapshot to update.
            progress (int): The new progress value (0-100).
        """
        self._progress_data[snap_id] = progress
        self._emit_data_changed(snap_id, 3)

    def update_status_for_snapshot(self, snap_id: str, status: str):
        """
        Finds a snapshot by its ID and updates its status message.

        Args:
            snap_id (str): The ID of the snapshot to update.
            status (str): The new status string.
        """
        self._status_data[snap_id] = status
        self._emit_data_changed(snap_id, 1)

    def update_results_for_snapshot(self, snap_id: str, count: str):
        """
        Finds a snapshot by its ID and updates its results count.

        Args:
            snap_id (str): The ID of the snapshot to update.
            count (str): The new results count as a string.
        """
        self._results_count_data[snap_id] = count
        self._emit_data_changed(snap_id, 2)


class SnapSearchTask(Task):
    """A background task for searching within a single snapshot."""

    def __init__(self, params: SnapshotSearchParams, snapshot: Snapshot, catalogue: SnapshotCatalogue):
        """
        Initializes the SnapSearchTask.

        Args:
            params (SnapshotSearchParams): The parameters for the search.
            snapshot (Snapshot): The snapshot to search within.
            catalogue (SnapshotCatalogue): The catalogue manager instance.
        """
        super().__init__(f"Search in {snapshot.name}")
        self.params = params
        self.snapshot = snapshot
        self.searcher = SnapshotSearcher(catalogue)

    def execute(self) -> list[SnapshotSearchResult]:
        """
        Executes the search task.

        Connects a progress callback and runs the search using SnapshotSearcher.

        Returns:
            list[SnapshotSearchResult]: A list of results found in the snapshot.
        """
        def on_progress(file_name: str, total_files: int, current_file: int):
            self.task_update_message.emit(self.name, tr("Scan: {file_name}", file_name=file_name))
            if total_files > 0:
                self.gen_update_task_progress(current_file, total_files)

        results = self.searcher.search(self.snapshot, self.params, on_progress=on_progress)
        return results


class SearchResultsTreeModel:
    """Manages the data model for the search results tree view."""

    def __init__(self):
        """Initializes the SearchResultsTreeModel."""
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels([tr('Results')])

    def clear(self):
        """Clears the tree model and resets the header."""
        self.model.clear()
        self.model.setHorizontalHeaderLabels([tr('Results')])

    def populate_from_results(self, results: list[SnapshotSearchResult]):
        """
        Populates the tree model with search results, grouped by snapshot.

        Args:
            results (list[SnapshotSearchResult]): The list of search results to display.
        """
        self.clear()
        self.model.setHorizontalHeaderLabels([tr("Results ({count})", count=len(results))])

        results_by_snapshot = {}
        for res in results:
            if res.snapshot_name not in results_by_snapshot:
                results_by_snapshot[res.snapshot_name] = []
            results_by_snapshot[res.snapshot_name].append(res)

        for snapshot_name, snapshot_results in results_by_snapshot.items():
            snapshot_item = QStandardItem(f"{snapshot_name} ({len(snapshot_results)})")
            snapshot_item.setEditable(False)

            files_in_snapshot = {}
            for res in snapshot_results:
                file_path_str = str(res.file_path)
                if file_path_str not in files_in_snapshot:
                    files_in_snapshot[file_path_str] = []
                files_in_snapshot[file_path_str].append(res)

            for file_path_str, file_results in files_in_snapshot.items():
                file_item = QStandardItem(file_path_str)
                file_item.setEditable(False)
                snapshot_item.appendRow(file_item)

            self.model.appendRow(snapshot_item)


class CatalogueSearcherModel(QObject):
    """
    The model for the catalogue searcher component.

    This class orchestrates the search process. It holds the data models for the
    views, manages the background search operations using an OperationRunner,
    and communicates state changes back to the UI via signals.

    Signals:
        signal_search_started: Emitted when the search runner starts.
        signal_search_stopped: Emitted when the search runner is stopped.
        signal_search_finished: Emitted when the search runner completes all operations.
        signal_status_card_update(str, int, str): Emitted to update the main status card
                                                   with a message, progress, and ETA.
    """
    signal_search_started = Signal()
    signal_search_stopped = Signal()
    signal_search_finished = Signal()
    signal_status_card_update = Signal(str, int, str)

    def __init__(self, catalogue: SnapshotCatalogue):
        """
        Initializes the CatalogueSearcherModel.

        Args:
            catalogue (SnapshotCatalogue): The catalogue to be searched.
        """
        super().__init__()
        self.catalogue = catalogue
        self.table_model = SearchResultsTableModel()
        self.tree_model_manager = SearchResultsTreeModel()
        self.runner = OperationRunner()

        self._current_message = tr("Waiting...")
        self._current_progress = 0
        self._current_eta = "--:--"

        self.runner.runner_start.connect(self.signal_search_started)
        self.runner.runner_stop.connect(self.signal_search_stopped)
        self.runner.runner_finish.connect(self.on_runner_finished)
        self.runner.op_finished.connect(self.on_operation_finished)
        self.runner.op_update_status.connect(self.on_operation_status_changed)
        self.runner.op_update_progress.connect(self.on_operation_progress_changed)
        self.runner.task_start.connect(self.on_task_start)
        self.runner.task_update_message.connect(self.on_task_update_message)
        self.runner.runner_update_progress.connect(self.on_runner_progress)
        self.runner.op_eta_update.connect(self.on_eta_update)

        self._op_id_to_snap_id = {}

    def __get_runner_operations(self, params: SnapshotSearchParams) -> list[Operation]:
        """
        Creates a list of search operations for the runner.

        Args:
            params (SnapshotSearchParams): The search parameters to use for each operation.

        Returns:
            list[Operation]: A list of configured search operations.
        """
        ops = []
        self._op_id_to_snap_id.clear()
        for snap in self.table_model.get_data():
            current_task = SnapSearchTask(params=params, snapshot=snap, catalogue=self.catalogue)
            op = Operation([current_task], OperationInfo(delay_each_task=0.0, name=f"Search in {snap.name})",
                                                 description="Searching snapshot contents"))
            self._op_id_to_snap_id[op.id] = snap.id
            ops.append(op)
        return ops

    def load_snapshots_from_catalogue(self, snapshot_or_snapshots: Snapshot | list[Snapshot] | None = None):
        """
        Loads snapshot names from the catalogue and populates the table model.
        If snapshots are provided, only those are loaded. Otherwise, all snapshots are loaded.
        
        Args:
            snapshot_or_snapshots: A specific snapshot, a list of snapshots, or None. Defaults to None.
        """
        if snapshot_or_snapshots:
            if isinstance(snapshot_or_snapshots, list):
                snapshots = snapshot_or_snapshots
            else:
                snapshots = [snapshot_or_snapshots]
        else:
            snapshots = self.catalogue.get_all()
        self.table_model.update_data(snapshots)

    def search(self, text: str, query_type: QueryType, search_target: SearchTarget, extensions: list[str]):
        """
        Starts a new search operation.

        Resets the current state, creates search parameters and operations,
        and starts the operation runner.

        Args:
            text (str): The text or regex pattern to search for.
            query_type (QueryType): The type of query (TEXT or REGEX).
            search_target (SearchTarget): The target of the search (FILE_NAME or FILE_CONTENT).
            extensions (list[str]): A list of file extensions to filter by.
        """
        self.table_model.reset_search_state()
        self.tree_model_manager.clear()
        self._current_message = tr("Starting...")
        self._current_progress = 0
        self._current_eta = "--:--"
        self._emit_status_card_update()

        params = SnapshotSearchParams(
            query=text,
            query_type=query_type,
            search_target=search_target,
            extensions=extensions
        )
        operations = self.__get_runner_operations(params)
        self.runner.clear()
        self.runner.adds(operations)
        logger.debug("Starting search operations in model")
        self.runner.start()

    def stop_search(self):
        """Stops the ongoing search operation."""
        logger.debug("Stopping search operations in model")
        self.runner.stop()

    def on_operation_status_changed(self, op_id: str, status: OperationStatus):
        """
        Slot to handle status changes for an operation. Updates the table view.

        Args:
            op_id (str): The ID of the operation that changed status.
            status (OperationStatus): The new status.
        """
        if op_id in self._op_id_to_snap_id:
            snap_id = self._op_id_to_snap_id[op_id]
            self.table_model.update_status_for_snapshot(snap_id, status.value)

    def on_operation_progress_changed(self, op_id: str, progress: int):
        """
        Slot to handle progress changes for an operation. Updates the table view.

        Args:
            op_id (str): The ID of the operation.
            progress (int): The new progress value (0-100).
        """
        if op_id in self._op_id_to_snap_id:
            snap_id = self._op_id_to_snap_id[op_id]
            self.table_model.update_progress_for_snapshot(snap_id, progress)

    def _emit_status_card_update(self):
        """Helper to emit the signal_status_card_update signal."""
        self.signal_status_card_update.emit(self._current_message, self._current_progress, self._current_eta)

    def on_task_start(self, task_name: str):
        """
        Slot to handle the start of a task. Updates the main status card.

        Args:
            task_name (str): The name of the task that started.
        """
        self._current_message = tr("Searching...")
        self._current_eta = "--:--"
        self._emit_status_card_update()

    def on_task_update_message(self, task_name: str, message: str):
        """
        Slot to handle a message update from a task. Updates the main status card.

        Args:
            task_name (str): The name of the task.
            message (str): The new message.
        """
        self._current_message = message
        self._emit_status_card_update()

    def on_runner_progress(self, progress: int):
        """
        Slot to handle overall progress updates from the runner.

        Args:
            progress (int): The overall progress percentage.
        """
        self._current_progress = progress
        self._emit_status_card_update()

    def on_eta_update(self, op_id: str, eta: str):
        """
        Slot to handle ETA updates from an operation. Updates the main status card.

        Args:
            op_id (str): The ID of the operation.
            eta (str): The new estimated time remaining string.
        """
        self._current_eta = eta
        self._emit_status_card_update()

    def _get_operation_results(self, op: Operation) -> list[SnapshotSearchResult]:
        """Helper to extract search results from an operation's tasks."""
        task_results = op.get_task_results()
        if task_results and isinstance(task_results[0], list):
            return task_results[0]
        return []

    def on_runner_finished(self, statistics: RunnerStatistics):
        """
        Slot to handle the completion of all search operations.

        Aggregates all results and populates the results tree.

        Args:
            statistics (RunnerStatistics): Statistics about the completed run.
        """
        logger.info("Model search finished. Processing statistics...")
        self.signal_search_finished.emit()
        all_results = []
        for op in self.runner._all_operations:
            all_results.extend(self._get_operation_results(op))

        self.tree_model_manager.populate_from_results(all_results)

    def get_results_for_snapshot(self, snap_id: str) -> list[SnapshotSearchResult]:
        """
        Retrieves the search results for a specific snapshot.
        """
        results = []
        for op in self.runner._all_operations:
            if self._op_id_to_snap_id.get(op.id) == snap_id:
                results.extend(self._get_operation_results(op))
                break
        return results

    def on_operation_finished(self, op: Operation):
        """
        Slot to handle the completion of a single search operation.

        Updates the results count for the corresponding snapshot in the table.

        Args:
            op (Operation): The operation that finished.
        """
        if op.id not in self._op_id_to_snap_id:
            return

        snap_id = self._op_id_to_snap_id[op.id]
        count_str = ""
        if op.is_completed():
            op_results = self._get_operation_results(op)
            count_str = str(len(op_results))
        elif op.is_failed():
            count_str = "?"

        self.table_model.update_results_for_snapshot(snap_id, count_str)