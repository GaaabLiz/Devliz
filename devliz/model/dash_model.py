from pathlib import Path
from typing import List, Callable, Optional, Any
from dataclasses import dataclass

from loguru import logger
from pylizlib.core.os.utils import WindowsOsUtils, is_software_installed
from pylizlib.qt.handler.operation_core import Operation
from pylizlib.qt.handler.operation_domain import OperationInfo
from pylizlib.qt.handler.operation_runner import OperationRunner, RunnerStatistics
from PySide6.QtCore import QObject, Signal, Qt

from devliz.model.devliz_update import TaskGetMonitoredSoftware
from devliz.view.dash_view import DashboardView



# noinspection PyMethodMayBeStatic
class DashboardModel(QObject):

    def __init__(self, view: DashboardView):
        super().__init__()
        self.view = view
        self.task1 = TaskGetMonitoredSoftware()
        self.task2 = TaskGetMonitoredSoftware()
        self.operation_info = OperationInfo(
            name="Aggiornamento Dashboard",
            description="Aggiornamento dati della dashboard",
            delay_each_task=1.0
        )

    def update(self):
        try:
            tasks = [
                self.task1,
                self.task2,
                self.task1,
                self.task2,
            ]
            op = Operation(tasks, self.operation_info)
            runner = OperationRunner()
            runner.runner_start.connect(self.on_runner_started)
            runner.runner_stop.connect(self.on_runner_stopped)
            runner.runner_finish.connect(self.on_runner_finished)
            runner.op_finished.connect(self.on_operation_finished)
            runner.add(op)
            runner.start()

        except Exception as e:
            logger.error(f"Errore durante il lancio dell'aggiornamento: {e}")
            return

    def on_runner_started(self):
        logger.info("Aggiornamento Dashboard iniziato.")

    def on_runner_stopped(self):
        logger.info("Aggiornamento Dashboard fermato.")

    def on_runner_finished(self, stats: RunnerStatistics):
        logger.info("Aggiornamento Dashboard completato.")
        if stats.has_ops_failed():
            error = stats.get_first_error()
            logger.error(f"Errore durante l'aggiornamento della dashboard: {error}")
            return

        logger.info("Aggiornamento della dashboard completato con successo.")

    def on_operation_finished(self, operation: Operation):
        logger.info(f"Operazione {operation.info.name} completata.")
        result1 = operation.get_task_result_by_id(operation.tasks[0].id)
        print(result1)

#
# class DashboardUpdaterInteraction(QObject, RunnerInteraction, metaclass=QObjectProtocolMeta):
#     # Signals to safely update the UI from a background thread
#     update_progress_signal = Signal(int, str)
#     close_dialog_signal = Signal()
#
#     def __init__(self):
#         super().__init__()
#         self.current_operation_status = ""
#         self.dialog = SimpleProgressDialog()
#
#         # Connect signals to the dialog's slots
#         self.update_progress_signal.connect(self.dialog.update_progress)
#         self.close_dialog_signal.connect(self.dialog.close)
#
#     def on_runner_start(self):
#         logger.info(f"Aggiornamento Dashboard partito.")
#         self.dialog.show()
#
#     def on_op_update_progress(self, operation_id: str, progress: int):
#         logger.debug("Aggiornamento progresso operazione: " + str(progress))
#         # Emit signal instead of calling UI method directly
#         self.update_progress_signal.emit(progress, self.current_operation_status)
#
#     def on_runner_finish(self, statistics: 'RunnerStatistics'):
#         logger.info(f"Aggiornamento Dashboard Finito.")
#         # Emit signal instead of calling UI method directly
#         self.close_dialog_signal.emit()
#
#     def on_task_start(self, task_name: str):
#         logger.debug(f"Task {task_name} iniziato.")
#         self.update_progress_signal.emit(0, task_name)
#
#     def on_task_finished(self, task_name: str):
#         logger.debug(f"Task {task_name} completato.")
#
#     def on_op_finished(self, operation: Any):
#         op_obj: Operation = operation
#         logger.info(f"Operation {op_obj.info.name} completato.")
#         result1 = op_obj.get_task_result_by_id(op_obj.tasks[0].id)
#         print(result1)
#
#
