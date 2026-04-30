import sys
import types
from dataclasses import dataclass
from pathlib import Path


def _import_domain_data_module(monkeypatch):
    # Stub minimi delle dipendenze esterne usate solo per typing/utility.
    unit_module = types.ModuleType("pylizlib.core.data.unit")
    unit_module.get_normalized_gb_mb_str = lambda value: f"{value}B"

    snap_module = types.ModuleType("pylizlib.core.os.snap")

    @dataclass
    class Snapshot:  # pragma: no cover - usato come placeholder di tipo
        directories: list

    snap_module.Snapshot = Snapshot

    sw_module = types.ModuleType("pylizlib.qtfw.domain.sw")

    @dataclass
    class SoftwareData:  # pragma: no cover - usato come placeholder di tipo
        path: Path | None = None

    sw_module.SoftwareData = SoftwareData

    monkeypatch.setitem(sys.modules, "pylizlib.core.data.unit", unit_module)
    monkeypatch.setitem(sys.modules, "pylizlib.core.os.snap", snap_module)
    monkeypatch.setitem(sys.modules, "pylizlib.qtfw.domain.sw", sw_module)

    sys.modules.pop("devliz.domain.data", None)
    import devliz.domain.data as data_module

    return data_module


def _make_snapshot(path: Path):
    dir_assoc = types.SimpleNamespace(original_path=str(path))
    return types.SimpleNamespace(directories=[dir_assoc])


def test_snapshot_count(monkeypatch, tmp_path):
    data_module = _import_domain_data_module(monkeypatch)

    snap_data = data_module.DevlizSnapshotData(snapshot_list=[_make_snapshot(tmp_path), _make_snapshot(tmp_path)])
    assert snap_data.count == 2


def test_get_mb_size_sums_all_files(monkeypatch, tmp_path):
    data_module = _import_domain_data_module(monkeypatch)

    root = tmp_path / "proj"
    root.mkdir()
    (root / "a.txt").write_bytes(b"abc")
    (root / "b.bin").write_bytes(b"12345")

    snap_data = data_module.DevlizSnapshotData(snapshot_list=[_make_snapshot(root)])
    assert snap_data.get_mb_size == "8B"


def test_compute_home_statistics_counts_files_dirs_and_heaviest(monkeypatch, tmp_path):
    data_module = _import_domain_data_module(monkeypatch)

    root = tmp_path / "snap"
    sub = root / "folder"
    sub.mkdir(parents=True)
    small = root / "small.txt"
    heavy = sub / "heavy.txt"
    small.write_bytes(b"12")
    heavy.write_bytes(b"123456")

    snap_data = data_module.DevlizSnapshotData(snapshot_list=[_make_snapshot(root)])
    stats = snap_data.compute_home_statistics()

    assert stats.snapshot_count == 1
    assert stats.total_files == 2
    assert stats.total_dirs >= 1
    assert stats.total_size_bytes == 8
    assert stats.heaviest_file_size == 6
    assert stats.heaviest_file_path.endswith("heavy.txt")
    assert stats.total_size_str == "8B"


def test_compute_home_statistics_logs_permission_error(monkeypatch, tmp_path):
    data_module = _import_domain_data_module(monkeypatch)

    blocked = tmp_path / "blocked"
    blocked.mkdir()
    snap_data = data_module.DevlizSnapshotData(snapshot_list=[_make_snapshot(blocked)])

    warnings = []
    monkeypatch.setattr(data_module.logger, "warning", lambda message: warnings.append(message))

    original_rglob = Path.rglob

    def fake_rglob(self, pattern):
        if self == blocked:
            raise PermissionError("denied")
        return original_rglob(self, pattern)

    monkeypatch.setattr(Path, "rglob", fake_rglob)

    stats = snap_data.compute_home_statistics()
    assert stats.total_files == 0
    assert len(warnings) == 1
    assert "Permesso negato" in warnings[0]

