from pathlib import Path

from loguru import logger
from pylizlib.core.os.snap import SnapshotCatalogue
from pylizlib.qt.domain.view import UiWidgetMode
from pylizlib.qt.handler.operation_core import Operation
from pylizlib.qt.handler.operation_domain import OperationInfo
from pylizlib.qt.handler.operation_runner import OperationRunner, RunnerStatistics
from PySide6.QtCore import QObject, Signal

from devliz.application.app import app_settings, DevlizSettings, DEVLIZ_PATH_BACKUPS
from devliz.domain.data import DevlizData
from devliz.model.devliz_update import TaskGetMonitoredSoftware, TaskGetSnapshots, TaskGetSettingsData
from devliz.view.dash_view import DashboardView



# noinspection PyMethodMayBeStatic
class DashboardModel(QObject):

    signal_on_update_started = Signal()
    signal_on_update_complete = Signal()
    signal_on_updated_data_available = Signal(DevlizData)

    def __init__(self, view: DashboardView):
        super().__init__()
        self.cached_data: DevlizData | None = None
        self.view = view
        self.snap_catalogue = SnapshotCatalogue(
            path_catalogue=Path(app_settings.get(DevlizSettings.catalogue_path)),
            backup_path=DEVLIZ_PATH_BACKUPS,
            backup_pre_install=app_settings.get(DevlizSettings.backup_before_install),
            backup_pre_delete=False, # TODO
            backup_pre_modify=False, # TODO
        )
        self.task_monitored_soft = TaskGetMonitoredSoftware()
        self.task_settings = TaskGetSettingsData()
        self.task_snap = TaskGetSnapshots(self.snap_catalogue)
        self.operation_info = OperationInfo(
            name="Aggiornamento Dashboard",
            description="Aggiornamento dati della dashboard",
            delay_each_task=0.1
        )
        self.runner = OperationRunner(abort_all_on_error=True)
        self.runner.runner_start.connect(self.on_runner_started)
        self.runner.runner_stop.connect(self.on_runner_stopped)
        self.runner.runner_finish.connect(self.on_runner_finished)
        self.runner.op_finished.connect(self.on_operation_finished)


    def get_cached_data(self) -> DevlizData | None:
        return self.cached_data

    def update(self):
        try:
            tasks = [
                self.task_settings,
                self.task_monitored_soft,
                self.task_snap,
            ]
            self.runner.clear()
            op = Operation(tasks, self.operation_info)
            self.runner.add(op)
            self.runner.start()

        except Exception as e:
            logger.error(f"Errore durante il lancio dell'aggiornamento: {e}")
            return

    def on_runner_started(self):
        logger.debug("Aggiornamento Dashboard iniziato.")
        self.signal_on_update_started.emit()

    def on_runner_stopped(self):
        logger.debug("Aggiornamento Dashboard fermato.")

    def on_runner_finished(self, stats: RunnerStatistics):
        logger.info("Aggiornamento Dashboard completato.")
        self.signal_on_update_complete.emit()
        if stats.has_ops_failed():
            error = stats.get_first_error()
            logger.error(f"Errore durante l'aggiornamento della dashboard: {error}")
            return

        logger.debug("Aggiornamento della dashboard completato con successo.")
        op = stats.operations[0]
        snapshots = op.get_task_result_by_id(self.task_snap.id)
        settings = op.get_task_result_by_id(self.task_settings.id)
        data = DevlizData(
            snapshots=snapshots,
            monitored_software=op.get_task_result_by_id(self.task_monitored_soft.id),
            settings=settings
        )
        self.signal_on_updated_data_available.emit(data)
        self.cached_data = data


    def on_operation_finished(self, operation: Operation):
        logger.info(f"Operazione {operation.info.name} completata.")