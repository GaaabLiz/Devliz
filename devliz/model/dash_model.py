from pathlib import Path
from typing import List, Callable, Optional


from pylizlib.core.os.utils import WindowsOsUtils, is_software_installed
from pylizlib.qtfw.domain.sw import SoftwareData
from pylizlib.qtfw.util.progress import SimpleProgressManager
from qfluentwidgets import FluentIcon, FluentStyleSheet, BodyLabel, ProgressBar

from devliz.application.app import app_settings, DevlizSettings
from devliz.domain.data import DevlizData, DevlizSnapshotData


# noinspection PyMethodMayBeStatic
class DashboardModel:

    def __init__(self, parent_widget=None):
        self.progress_manager = SimpleProgressManager(parent_widget)


    def update(self):
        """Il tuo metodo che aggiorna lo stato"""
        # Le tue operazioni
        operazioni = [
            lambda status_callback=None: self.sleep(status_callback),
            lambda status_callback=None: self.sleep(status_callback),
        ]

        # Avvia con progress
        self.progress_manager.start_operations(
            operazioni,
            callback=lambda success: print(f"Finito: {success}")
        )

    def sleep(self, status_callback=None):
        import time

        status_callback("Eseguendo sleep 1...")
        time.sleep(1)
        status_callback("Eseguendo sleep 2...")
        time.sleep(1)
        status_callback("Eseguendo sleep 3...")
        time.sleep(1)
        status_callback("Sleep completato.")

    def __get_monitored_software(self) -> list[SoftwareData]:
        data_list: list[str] = app_settings.get(DevlizSettings.starred_exes)
        data_objs: list[SoftwareData] = []
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

    def __get_monitored_Services(self) -> list[SoftwareData]:
        data_list: list[str] = app_settings.get(DevlizSettings.starred_services)
        data_objs: list[SoftwareData] = []
        for data in data_list:
            service_path = WindowsOsUtils.get_service_executable_path(data)
            if service_path is None:
                continue
            obj = SoftwareData(
                path=Path(data),
                is_service=True,
                icon=FluentIcon.SETTING,
                installed=service_path is not None,
                running=WindowsOsUtils.is_service_running(data),
                version=WindowsOsUtils.get_service_version(data)
            )
            data_objs.append(obj)
        return data_objs


    def get_starred_exes(self) -> list[Path]:
        return [Path(e) for e in app_settings.get(DevlizSettings.starred_exes)]

    def get_starred_files(self) -> list[Path]:
        return [Path(f) for f in app_settings.get(DevlizSettings.starred_files)]

    def get_starred_dirs(self) -> list[Path]:
        return [Path(d) for d in app_settings.get(DevlizSettings.starred_dirs)]

    def __get_configs(self) -> DevlizSnapshotData:
        return DevlizSnapshotData([])

    def __get_tags(self) -> list[str]:
        return app_settings.get(DevlizSettings.config_tags)

    def gen_devliz_data(self) -> DevlizData:
        return DevlizData(
            monitored_software=self.__get_monitored_software(),
            monitored_services=self.__get_monitored_Services(),
            starred_dirs=self.get_starred_dirs(),
            starred_files=self.get_starred_files(),
            starred_exes=self.get_starred_exes(),
            configurations=self.__get_configs(),
            tags=self.__get_tags()
        )
