from pathlib import Path

from loguru import logger

from devliz.application.app import app_settings, AppSettings, PATH_BACKUPS
from devliz.domain.data import DevlizSnapshotData
from devliz.view.home import HomeView


class HomeController:

    def __init__(self):
        self.view = HomeView()

    def update_data(self, snapshot_data: DevlizSnapshotData):
        logger.debug("Calcolo statistiche Home...")
        stats = snapshot_data.compute_home_statistics()
        logger.debug(f"Statistiche calcolate: {stats}")

        backup_path = Path(app_settings.get(AppSettings.backup_path))
        backup_count = 0
        if backup_path.exists() and backup_path.is_dir():
            backup_count = len(list(backup_path.glob("*.zip")))

        catalogue_path = app_settings.get(AppSettings.catalogue_path)
        self.view.update_statistics(stats, backup_count=backup_count, catalogue_path=catalogue_path)
