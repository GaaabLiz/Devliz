from pathlib import Path

from loguru import logger

from devliz.application.app import app_settings, AppSettings
from devliz.domain.data import DevlizSnapshotData
from devliz.view.home import HomeView


class HomeController:
    """
    Controller for the application's home screen.

    This class manages the data displayed on the home view, particularly
    computing and updating statistical information regarding snapshots
    and backups based on the user's configured settings.
    """

    def __init__(self):
        """
        Initializes the HomeController.

        Creates the associated HomeView instance which handles the UI presentation.
        """
        self.view = HomeView()

    def update_data(self, snapshot_data: DevlizSnapshotData):
        """
        Updates the data presented on the home view.

        Computes statistics from the given snapshot data, counts the number of
        available backups in the configured backup directory, and fetches the
        current catalogue path to update the view accordingly.

        Args:
            snapshot_data (DevlizSnapshotData): The current snapshot data used to compute statistics.
        """
        logger.debug("Calculating Home statistics...")
        stats = snapshot_data.compute_home_statistics()
        logger.debug(f"Statistics calculated: {stats}")

        backup_path = Path(app_settings.get(AppSettings.backup_path))
        backup_count = 0
        if backup_path.exists() and backup_path.is_dir():
            backup_count = len(list(backup_path.glob("*.zip")))

        catalogue_path = app_settings.get(AppSettings.catalogue_path)
        self.view.update_statistics(stats, backup_count=backup_count, catalogue_path=catalogue_path)
