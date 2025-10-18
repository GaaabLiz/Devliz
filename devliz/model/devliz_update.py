from pathlib import Path
from time import sleep

from pylizlib.core.os.snap import Snapshot, SnapshotUtils
from pylizlib.core.os.utils import is_software_installed, WindowsOsUtils
from pylizlib.qt.handler.operation_core import Task
from pylizlib.qtfw.domain.sw import SoftwareData
from qfluentwidgets import FluentIcon

from devliz.application.app import app_settings, DevlizSettings
from devliz.domain.data import DevlizSettingsData


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


class TaskGetSnapshots(Task):

    def __init__(self):
        super().__init__("Recupero snapshots salvati")

    def execute(self):
        list = []
        list.append(SnapshotUtils.gen_random_snap(Path(r"C:\Users\Gabriele\Documents")))
        list.append(SnapshotUtils.gen_random_snap(Path(r"C:\Users\Gabriele\Documents")))
        sleep(1)
        return list

class TaskGetSettingsData(Task):

    def __init__(self):
        super().__init__("Recupero dati di configurazione")

    def execute(self):
        return DevlizSettingsData(
            starred_exes=app_settings.get(DevlizSettings.starred_exes),
            starred_files=app_settings.get(DevlizSettings.starred_files),
            starred_dirs=app_settings.get(DevlizSettings.starred_dirs),
            tags=app_settings.get(DevlizSettings.config_tags),
        )