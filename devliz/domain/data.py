from dataclasses import dataclass

from loguru import logger
from pylizlib.core.data.unit import get_normalized_gb_mb_str
from pylizlib.core.os.snap import Snapshot
from pylizlib.qtfw.domain.sw import SoftwareData


@dataclass
class HomeStatistics:
    """
    Data class representing statistics for the home dashboard.
    
    This class stores aggregated information about snapshots, sizes, and file counts
    to provide a summary view on the application's main dashboard.
    """
    snapshot_count: int = 0
    total_size_bytes: int = 0
    total_files: int = 0
    total_dirs: int = 0
    heaviest_file_path: str = ""
    heaviest_file_size: int = 0
    last_snapshot_date: str = ""
    oldest_snapshot_date: str = ""
    average_snapshot_size_bytes: int = 0

    @property
    def total_size_str(self) -> str:
        """
        Get the total size of all snapshots formatted as a human-readable string (MB/GB).
        
        Returns:
            str: The normalized string representation of total_size_bytes.
        """
        return get_normalized_gb_mb_str(self.total_size_bytes)

    @property
    def heaviest_file_size_str(self) -> str:
        """
        Get the size of the heaviest file formatted as a human-readable string (MB/GB).
        
        Returns:
            str: The normalized string representation of heaviest_file_size.
        """
        return get_normalized_gb_mb_str(self.heaviest_file_size)
    
    @property
    def average_snapshot_size_str(self) -> str:
        """
        Get the average snapshot size formatted as a human-readable string (MB/GB).
        
        Returns:
            str: The normalized string representation of average_snapshot_size_bytes.
        """
        return get_normalized_gb_mb_str(self.average_snapshot_size_bytes)


@dataclass
class DevlizSnapshotData:
    """
    Data class representing a collection of application snapshots.
    
    This class encapsulates a list of Snapshot objects and provides 
    properties and methods to compute aggregate metrics and statistics.
    """
    snapshot_list: list[Snapshot]

    @property
    def count(self) -> int:
        """
        Get the total number of snapshots in the collection.
        
        Returns:
            int: The number of snapshots.
        """
        return len(self.snapshot_list)

    @property
    def get_mb_size(self) -> str:
        """
        Get the total size of all associated directories in the snapshot list.
        
        Returns:
            str: The normalized string representation of the total size in MB/GB.
        """
        total_size_mb = 0
        for config in self.snapshot_list:
            total_size_mb += config.get_assoc_dir_mb_size
        return get_normalized_gb_mb_str(int(total_size_mb * 1024 * 1024))

    def compute_home_statistics(self) -> HomeStatistics:
        """
        Compute and return home dashboard statistics based on the snapshot data.
        
        This method aggregates total sizes, tracks the oldest and newest snapshot 
        dates, and calculates the average snapshot size. File-level statistics 
        are skipped to optimize dashboard loading performance.
        
        Returns:
            HomeStatistics: A populated HomeStatistics object with the calculated metrics.
        """
        logger.debug("Starting statistics calculation for Home...")
        stats = HomeStatistics(snapshot_count=self.count)
        
        dates = []

        for snap in self.snapshot_list:
            if snap.date_created:
                dates.append(snap.date_created)

            # Optimize: use pre-calculated size from snapshot instead of scanning disk
            stats.total_size_bytes += int(snap.get_assoc_dir_mb_size * 1024 * 1024)

        # File-level statistics are no longer computed to prevent slow dashboard loading
        stats.heaviest_file_path = ""
        stats.heaviest_file_size = 0
        stats.total_files = 0
        stats.total_dirs = 0
        
        if dates:
            dates.sort()
            stats.oldest_snapshot_date = dates[0].strftime("%Y-%m-%d")
            stats.last_snapshot_date = dates[-1].strftime("%Y-%m-%d")
        else:
            stats.oldest_snapshot_date = "—"
            stats.last_snapshot_date = "—"
            
        if self.count > 0:
            stats.average_snapshot_size_bytes = stats.total_size_bytes // self.count
            
        logger.debug(f"Statistics calculation completed: {stats.snapshot_count} snapshots processed.")
        return stats


# @dataclass
# class DevlizSettingsData:
#     starred_dirs: list[Path] = None
#     starred_files: list[Path] = None
#     starred_exes: list[Path] = None
#     tags: list[str] = None
#     custom_snap_data: list[str] = None


@dataclass
class DevlizData:
    """
    Data class representing the overall application data model.
    
    This class holds the state for monitored software, monitored services, 
    and all tracked snapshot data.
    """
    monitored_software: list[SoftwareData] = None
    monitored_services: list[SoftwareData] = None
    snapshots: DevlizSnapshotData = None

