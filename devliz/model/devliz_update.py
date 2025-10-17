from pathlib import Path
from typing import Callable

from pylizlib.core.os.utils import is_software_installed, WindowsOsUtils
from pylizlib.qt.handler.operation_core import Operation, Task
from pylizlib.qt.handler.operation_domain import OperationInfo
from pylizlib.qtfw.domain.sw import SoftwareData
from qfluentwidgets import FluentIcon

from devliz.application.app import app_settings, DevlizSettings


class TaskGetMonitoredSoftware(Task):

    def __init__(self):
        super().__init__("Recupero Software Monitorati")

    def execute(self):
        data_list: list[str] = app_settings.get(DevlizSettings.starred_exes)
        data_objs: list[SoftwareData] = []
        # for i in range(1, 50000000):
        #     progress = int((i / 50000000) * 100)
            #self.update_task_progress(progress)
        for data in data_list:
            obj = SoftwareData(
                path=Path(data),
                is_service=False,
                icon=FluentIcon.APPLICATION,
                installed=is_software_installed(Path(data)),
                running=WindowsOsUtils.is_exe_running(Path(data)),
                version=WindowsOsUtils.get_windows_exe_version(Path(data))
            )
            data_objs.append(obj)

        return data_objs
