from pathlib import Path

from loguru import logger
from pylizlib.core.os.snap import SnapshotCatalogue
from pylizlib.core.os.utils import is_software_installed, WindowsOsUtils
from pylizlib.qt.handler.operation_core import Task
from pylizlib.qtfw.domain.sw import SoftwareData
from qfluentwidgets import FluentIcon

from devliz.application.app import app_settings, AppSettings
from devliz.application.i18n import tr


class TaskGetMonitoredSoftware(Task):
    """
    Task to retrieve the list of monitored software.

    This task fetches the configured software executables from settings and 
    checks their installation status, running state, and version.
    """

    def __init__(self):
        """
        Initializes the TaskGetMonitoredSoftware task.
        """
        super().__init__(tr("Retrieving Monitored Software"))

    def execute(self) -> list[SoftwareData]:
        """
        Executes the task to fetch and process monitored software.

        Returns:
            list[SoftwareData]: A list of SoftwareData objects representing the monitored applications.
        """
        logger.debug("Fetching monitored software list...")
        data_list: list[str] = app_settings.get(AppSettings.starred_exes)
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
    """
    Task to retrieve all saved snapshots from the catalogue.
    """

    def __init__(self, catalogue: SnapshotCatalogue):
        """
        Initializes the TaskGetSnapshots task.

        Args:
            catalogue (SnapshotCatalogue): The snapshot catalogue instance to query.
        """
        super().__init__(tr("Retrieving saved snapshots"))
        self.catalogue = catalogue

    def execute(self):
        """
        Executes the task to fetch all snapshots.

        Returns:
            list[Snapshot]: A list of all available snapshots in the catalogue.
        """
        logger.debug("Fetching saved snapshots...")
        return self.catalogue.get_all()
