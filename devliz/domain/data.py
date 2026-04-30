from dataclasses import dataclass, field
from pathlib import Path

from loguru import logger
from pylizlib.core.data.unit import get_normalized_gb_mb_str
from pylizlib.core.os.snap import Snapshot
from pylizlib.qtfw.domain.sw import SoftwareData


@dataclass
class HomeStatistics:
    snapshot_count: int = 0
    total_size_bytes: int = 0
    total_files: int = 0
    total_dirs: int = 0
    heaviest_file_path: str = ""
    heaviest_file_size: int = 0

    @property
    def total_size_str(self) -> str:
        return get_normalized_gb_mb_str(self.total_size_bytes)

    @property
    def heaviest_file_size_str(self) -> str:
        return get_normalized_gb_mb_str(self.heaviest_file_size)


@dataclass
class DevlizSnapshotData:
    snapshot_list: list[Snapshot]

    @property
    def count(self) -> int:
        return len(self.snapshot_list)

    @property
    def get_mb_size(self) -> str:
        total_size = 0
        for config in self.snapshot_list:
            for dir_assoc in config.directories:
                path = Path(dir_assoc.original_path)
                if path.exists() and path.is_dir():
                    for file in path.rglob('*'):
                        if file.is_file():
                            total_size += file.stat().st_size
        return get_normalized_gb_mb_str(total_size)

    def compute_home_statistics(self) -> HomeStatistics:
        stats = HomeStatistics(snapshot_count=self.count)
        heaviest_size = 0
        heaviest_path = ""

        for snap in self.snapshot_list:
            for dir_assoc in snap.directories:
                path = Path(dir_assoc.original_path)
                if not path.exists() or not path.is_dir():
                    continue
                try:
                    for entry in path.rglob('*'):
                        if entry.is_file():
                            stats.total_files += 1
                            try:
                                size = entry.stat().st_size
                            except OSError:
                                continue
                            stats.total_size_bytes += size
                            if size > heaviest_size:
                                heaviest_size = size
                                heaviest_path = str(entry)
                        elif entry.is_dir():
                            stats.total_dirs += 1
                except PermissionError:
                    logger.warning(f"Permesso negato per la directory: {path}")

        stats.heaviest_file_path = heaviest_path
        stats.heaviest_file_size = heaviest_size
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
    monitored_software: list[SoftwareData] = None
    monitored_services: list[SoftwareData] = None
    snapshots: DevlizSnapshotData = None

