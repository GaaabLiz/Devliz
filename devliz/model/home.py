from pathlib import Path

from PySide6.QtCore import QObject, Signal
from loguru import logger

from devliz.application.app import app_settings, AppSettings
from devliz.domain.data import DevlizSnapshotData


class HomeModel(QObject):
    """
    Model for the Home screen.

    Responsible for computing statistics from snapshots and reading 
    global settings like backup counts and catalogue paths.
    Communicates with the Controller exclusively via Signals.
    """
    
    # Emits stats object, backup_count, catalogue_path
    statistics_updated = Signal(object, int, str)

    def __init__(self, parent=None):
        """
        Initializes the HomeModel.

        Args:
            parent (QObject, optional): Parent object. Defaults to None.
        """
        super().__init__(parent)

    def compute_and_emit_statistics(self, snapshot_data: DevlizSnapshotData):
        """
        Computes the latest statistics from snapshot_data and reads global configuration
        (backup counts, catalogue path). Once done, emits the statistics_updated signal.

        Args:
            snapshot_data (DevlizSnapshotData): The snapshot data block to analyze.
        """
        logger.debug("Calculating Home statistics...")
        stats = snapshot_data.compute_home_statistics()
        logger.debug(f"Statistics calculated: {stats}")

        # Compute backup count
        backup_path = Path(app_settings.get(AppSettings.backup_path))
        backup_count = 0
        if backup_path.exists() and backup_path.is_dir():
            backup_count = len(list(backup_path.glob("*.zip")))

        # Get catalogue path
        catalogue_path = app_settings.get(AppSettings.catalogue_path)
        
        # Emit signal to notify that data has changed
        self.statistics_updated.emit(stats, backup_count, str(catalogue_path))
