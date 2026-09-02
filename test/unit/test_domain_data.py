import sys
import types
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path


def _import_domain_data_module(monkeypatch):
    unit_module = types.ModuleType("pylizlib.core.data.unit")
    unit_module.get_normalized_gb_mb_str = lambda value: f"{value}B"

    snap_module = types.ModuleType("pylizlib.core.os.snap")

    @dataclass
    class Snapshot:
        directories: list

    snap_module.Snapshot = Snapshot

    sw_module = types.ModuleType("pylizlib.qtfw.domain.sw")

    @dataclass
    class SoftwareData:
        path: Path | None = None

    sw_module.SoftwareData = SoftwareData

    monkeypatch.setitem(sys.modules, "pylizlib.core.data.unit", unit_module)
    monkeypatch.setitem(sys.modules, "pylizlib.core.os.snap", snap_module)
    monkeypatch.setitem(sys.modules, "pylizlib.qtfw.domain.sw", sw_module)

    sys.modules.pop("devliz.domain.data", None)
    import devliz.domain.data as data_module

    return data_module


def _make_snapshot(path: Path, mb_size=10.0, date_created=None):
    return types.SimpleNamespace(
        directories=[types.SimpleNamespace(original_path=str(path))],
        date_created=date_created,
        get_assoc_dir_mb_size=mb_size
    )


def test_snapshot_count(monkeypatch, tmp_path):
    data_module = _import_domain_data_module(monkeypatch)
    snap_data = data_module.DevlizSnapshotData(snapshot_list=[_make_snapshot(tmp_path), _make_snapshot(tmp_path)])
    assert snap_data.count == 2


def test_get_mb_size(monkeypatch, tmp_path):
    data_module = _import_domain_data_module(monkeypatch)
    snap_data = data_module.DevlizSnapshotData(snapshot_list=[_make_snapshot(tmp_path, mb_size=1.0)])
    # 1.0 MB = 1 * 1024 * 1024 bytes
    assert snap_data.get_mb_size == f"{1024 * 1024}B"


def test_compute_home_statistics(monkeypatch, tmp_path):
    data_module = _import_domain_data_module(monkeypatch)
    snap_data = data_module.DevlizSnapshotData(snapshot_list=[
        _make_snapshot(tmp_path, mb_size=2.0, date_created=datetime(2023, 1, 5)),
        _make_snapshot(tmp_path, mb_size=4.0, date_created=datetime(2023, 1, 1))
    ])
    stats = snap_data.compute_home_statistics()

    assert stats.snapshot_count == 2
    assert stats.total_files == 0
    assert stats.total_dirs == 0
    # 6.0 MB = 6 * 1024 * 1024 bytes
    assert stats.total_size_bytes == 6 * 1024 * 1024
    assert stats.heaviest_file_size == 0
    assert stats.heaviest_file_path == ""
    assert stats.total_size_str == f"{6 * 1024 * 1024}B"
    assert stats.oldest_snapshot_date == "2023-01-01"
    assert stats.last_snapshot_date == "2023-01-05"
    assert stats.average_snapshot_size_bytes == (6 * 1024 * 1024) // 2

def test_compute_home_statistics_no_dates(monkeypatch, tmp_path):
    data_module = _import_domain_data_module(monkeypatch)
    snap_data = data_module.DevlizSnapshotData(snapshot_list=[
        _make_snapshot(tmp_path, mb_size=0.0, date_created=None)
    ])
    stats = snap_data.compute_home_statistics()

    assert stats.oldest_snapshot_date == "—"
    assert stats.last_snapshot_date == "—"
    assert stats.average_snapshot_size_bytes == 0

def test_home_statistics_str_properties(monkeypatch):
    data_module = _import_domain_data_module(monkeypatch)
    stats = data_module.HomeStatistics(heaviest_file_size=1024, average_snapshot_size_bytes=2048)
    assert stats.heaviest_file_size_str == "1024B"
    assert stats.average_snapshot_size_str == "2048B"
