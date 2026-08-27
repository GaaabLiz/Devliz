from pathlib import Path

from loguru import logger
from pylizlib.core.os.snap import SnapshotCatalogue
from pylizlib.qt.handler.operation_core import Operation, Task
from pylizlib.qt.handler.operation_domain import OperationInfo
from pylizlib.qt.handler.operation_runner import OperationRunner, RunnerStatistics
from PySide6.QtCore import QObject, Signal

from devliz.application.app import app_settings, AppSettings, PATH_BACKUPS, snap_settings
from devliz.domain.data import DevlizData
from devliz.model.devliz_update import TaskGetMonitoredSoftware, TaskGetSnapshots
from devliz.view.dashboard import DashboardView
from devliz.application.i18n import tr



# noinspection PyMethodMayBeStatic
class DashboardModel(QObject):

    signal_on_update_started = Signal()
    signal_on_update_complete = Signal()
    signal_on_update_progress = Signal(int)
    signal_on_update_text = Signal(str)
    signal_on_updated_data_available = Signal(DevlizData)

    def __init__(self, view: DashboardView):
        super().__init__()
        self.cached_data: DevlizData | None = None
        self.view = view
        self.snap_catalogue = SnapshotCatalogue(
            path_catalogue=Path(app_settings.get(AppSettings.catalogue_path)),
            settings=snap_settings
        )
        self.task_monitored_soft = TaskGetMonitoredSoftware()
        self.task_snap = TaskGetSnapshots(self.snap_catalogue)
        self.operation_info = OperationInfo(
            name=tr("Dashboard Update"),
            description=tr("Dashboard data update"),
            delay_each_task=0.1
        )
        self.runner = OperationRunner(abort_all_on_error=True)
        self.runner.runner_start.connect(self.on_runner_started)
        self.runner.runner_stop.connect(self.on_runner_stopped)
        self.runner.runner_finish.connect(self.on_runner_finished)
        self.runner.runner_update_progress.connect(self.signal_on_update_progress.emit)
        
        # We will need to capture task text from the runner's tasks if we want to show text.
        self.runner.task_update_message.connect(lambda task_name, msg: self.signal_on_update_text.emit(msg))
        
        self._heavy_runners = []

    def run_heavy_operation(
        self, 
        op_name: str, 
        op_desc: str, 
        func: callable, 
        success_msg_title: str = "", 
        success_msg: str = "", 
        update_dashboard: bool = True
    ):
        from pylizlib.qt.handler.operation_core import GenericTask
        from pylizlib.qtfw.util.ui import UiUtils
        
        task = GenericTask(op_name, func)
        op_info = OperationInfo(name=op_name, description=op_desc)
        op = Operation([task], op_info)

        runner = OperationRunner(abort_all_on_error=True)
        self._heavy_runners.append(runner)
        
        def on_finish(stats: RunnerStatistics):
            if runner in self._heavy_runners:
                self._heavy_runners.remove(runner)
            
            if stats.has_ops_failed():
                error = stats.get_first_error()
                logger.error(f"Error during {op_name}: {error}")
                UiUtils.show_message(tr("Error"), tr("An error occurred: {error}", error=str(error)))
                self.signal_on_update_complete.emit()
            else:
                if success_msg_title and success_msg:
                    UiUtils.show_message(success_msg_title, success_msg)
                if update_dashboard:
                    self.update()
                else:
                    self.signal_on_update_complete.emit()

        runner.runner_finish.connect(on_finish)
        runner.runner_update_progress.connect(self.signal_on_update_progress.emit)
        runner.task_update_message.connect(lambda task_name, msg: self.signal_on_update_text.emit(msg))
        
        self.signal_on_update_started.emit()
        self.signal_on_update_text.emit(op_desc)
        self.signal_on_update_progress.emit(0)
        
        runner.add(op)
        runner.start()


    def get_cached_data(self) -> DevlizData | None:
        return self.cached_data

    def update(self):
        try:
            tasks = [
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
        logger.info("Aggiornamento Dashboard iniziato.")
        self.signal_on_update_started.emit()
        self.signal_on_update_text.emit(tr("Updating dashboard data..."))
        self.signal_on_update_progress.emit(0)

    def on_runner_stopped(self):
        logger.info("Aggiornamento Dashboard fermato.")

    def on_runner_finished(self, stats: RunnerStatistics):
        logger.info("Aggiornamento Dashboard completato.")
        self.signal_on_update_complete.emit()
        if stats.has_ops_failed():
            error = stats.get_first_error()
            logger.error(f"Errore durante l'aggiornamento della dashboard: {error}")
            return

        logger.debug("Aggiornamento dashboard completato con successo, recupero dati...")
        op = stats.operations[0]
        snapshots = op.get_task_result_by_id(self.task_snap.id)
        data = DevlizData(
            snapshots=snapshots,
            monitored_software=op.get_task_result_by_id(self.task_monitored_soft.id),
        )
        self.signal_on_updated_data_available.emit(data)
        self.cached_data = data