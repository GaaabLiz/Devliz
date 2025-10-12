from dataclasses import dataclass
from pathlib import Path

from pylizlib.core.os.snap import Snapshot
from pylizlib.qtfw.domain.sw import SoftwareData


@dataclass
class DevlizSnapshotData:
    configurations: list[Snapshot]

    @property
    def count(self) -> int:
        return len(self.configurations)

    @property
    def get_mb_size(self) -> str:
        total_size = 0
        for config in self.configurations:
            for dir_assoc in config.directories:
                path = Path(dir_assoc.original_path)
                if path.exists() and path.is_dir():
                    for file in path.rglob('*'):
                        if file.is_file():
                            total_size += file.stat().st_size

        size_mb = total_size / (1024 * 1024)
        if size_mb < 1000:
            return f"{size_mb:.2f} MB"
        size_gb = size_mb / 1024
        return f"{size_gb:.2f} GB"



@dataclass
class DevlizData:
    monitored_software: list[SoftwareData] = None
    monitored_services: list[SoftwareData] = None
    starred_dirs: list[Path] = None
    starred_files: list[Path] = None
    starred_exes: list[Path] = None
    configurations: DevlizSnapshotData = None
    tags: list[str] = None
