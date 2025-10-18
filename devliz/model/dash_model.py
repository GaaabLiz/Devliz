
from loguru import logger
from pylizlib.qt.domain.view import UiWidgetMode
from pylizlib.qt.handler.operation_core import Operation
from pylizlib.qt.handler.operation_domain import OperationInfo
from pylizlib.qt.handler.operation_runner import OperationRunner, RunnerStatistics
from PySide6.QtCore import QObject, Signal

from devliz.domain.data import DevlizData
from devliz.model.devliz_update import TaskGetMonitoredSoftware, TaskGetSnapshots
from devliz.view.dash_view import DashboardView



# noinspection PyMethodMayBeStatic
class DashboardModel(QObject):

    signal_on_update_started = Signal()
    signal_on_update_complete = Signal()
    signal_on_updated_data_available = Signal(DevlizData)

    def __init__(self, view: DashboardView):
        super().__init__()
        self.view = view
        self.task1 = TaskGetMonitoredSoftware()
        self.task2 = TaskGetMonitoredSoftware()
        self.task_snap = TaskGetSnapshots()
        self.operation_info = OperationInfo(
            name="Aggiornamento Dashboard",
            description="Aggiornamento dati della dashboard",
            delay_each_task=1.0
        )
        self.runner = OperationRunner()
        self.runner.runner_start.connect(self.on_runner_started)
        self.runner.runner_stop.connect(self.on_runner_stopped)
        self.runner.runner_finish.connect(self.on_runner_finished)
        self.runner.op_finished.connect(self.on_operation_finished)

    def update(self):
        try:
            tasks = [
                self.task1,
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
        self.signal_on_updated_data_available.emit(DevlizData(snapshots=snapshots))


    def on_operation_finished(self, operation: Operation):
        logger.info(f"Operazione {operation.info.name} completata.")