import sys
import types
from pathlib import Path


def _import_devliz_update_module(monkeypatch, starred_exes=None):
    call_log = {
        "installed": [],
        "running": [],
        "version": [],
    }
    starred_exes = starred_exes or []

    class FakeTask:
        def __init__(self, name):
            self.name = name

    class FakeSoftwareData:
        def __init__(self, path, is_service, icon, installed, running, version):
            self.path = path
            self.is_service = is_service
            self.icon = icon
            self.installed = installed
            self.running = running
            self.version = version

    class FakeWindowsOsUtils:
        @staticmethod
        def is_exe_running(path):
            call_log["running"].append(path)
            return path.name.startswith("run")

        @staticmethod
        def get_windows_exe_version(path):
            call_log["version"].append(path)
            return f"v-{path.stem}"

    def fake_is_software_installed(path):
        call_log["installed"].append(path)
        return path.suffix == ".exe"

    class FakeAppSettings:
        @staticmethod
        def get(_key):
            return list(starred_exes)

    class FakeAppSettingsKeys:
        starred_exes = "starred_exes"

    class FakeFluentIcon:
        APPLICATION = "APPLICATION"

    fake_snap_module = types.ModuleType("pylizlib.core.os.snap")
    fake_snap_module.Snapshot = object
    fake_snap_module.SnapshotUtils = object
    fake_snap_module.SnapshotCatalogue = object

    fake_utils_module = types.ModuleType("pylizlib.core.os.utils")
    fake_utils_module.is_software_installed = fake_is_software_installed
    fake_utils_module.WindowsOsUtils = FakeWindowsOsUtils

    fake_task_module = types.ModuleType("pylizlib.qt.handler.operation_core")
    fake_task_module.Task = FakeTask

    fake_sw_module = types.ModuleType("pylizlib.qtfw.domain.sw")
    fake_sw_module.SoftwareData = FakeSoftwareData

    fake_qfluentwidgets_module = types.ModuleType("qfluentwidgets")
    fake_qfluentwidgets_module.FluentIcon = FakeFluentIcon

    fake_app_module = types.ModuleType("devliz.application.app")
    fake_app_module.app_settings = FakeAppSettings()
    fake_app_module.AppSettings = FakeAppSettingsKeys

    fake_i18n_module = types.ModuleType("devliz.application.i18n")
    fake_i18n_module.tr = lambda key: f"TR:{key}"

    monkeypatch.setitem(sys.modules, "pylizlib.core.os.snap", fake_snap_module)
    monkeypatch.setitem(sys.modules, "pylizlib.core.os.utils", fake_utils_module)
    monkeypatch.setitem(sys.modules, "pylizlib.qt.handler.operation_core", fake_task_module)
    monkeypatch.setitem(sys.modules, "pylizlib.qtfw.domain.sw", fake_sw_module)
    monkeypatch.setitem(sys.modules, "qfluentwidgets", fake_qfluentwidgets_module)
    monkeypatch.setitem(sys.modules, "devliz.application.app", fake_app_module)
    monkeypatch.setitem(sys.modules, "devliz.application.i18n", fake_i18n_module)

    sys.modules.pop("devliz.model.devliz_update", None)
    import devliz.model.devliz_update as devliz_update_module

    return devliz_update_module, call_log


def test_task_get_monitored_software_execute_builds_objects(monkeypatch):
    module, call_log = _import_devliz_update_module(
        monkeypatch,
        starred_exes=["/apps/run_tool.exe", "/apps/not_running.bin"],
    )

    task = module.TaskGetMonitoredSoftware()
    result = task.execute()

    assert task.name == "TR:Retrieving Monitored Software"
    assert len(result) == 2

    first = result[0]
    assert isinstance(first.path, Path)
    assert first.path == Path("/apps/run_tool.exe")
    assert first.icon == "APPLICATION"
    assert first.is_service is False
    assert first.installed is True
    assert first.running is True
    assert first.version == "v-run_tool"

    second = result[1]
    assert second.path == Path("/apps/not_running.bin")
    assert second.installed is False
    assert second.running is False
    assert second.version == "v-not_running"

    assert call_log["installed"] == [Path("/apps/run_tool.exe"), Path("/apps/not_running.bin")]
    assert call_log["running"] == [Path("/apps/run_tool.exe"), Path("/apps/not_running.bin")]
    assert call_log["version"] == [Path("/apps/run_tool.exe"), Path("/apps/not_running.bin")]


def test_task_get_monitored_software_empty_list(monkeypatch):
    module, call_log = _import_devliz_update_module(monkeypatch, starred_exes=[])

    task = module.TaskGetMonitoredSoftware()
    result = task.execute()

    assert result == []
    assert call_log["installed"] == []
    assert call_log["running"] == []
    assert call_log["version"] == []


def test_task_get_snapshots_execute_delegates_to_catalogue(monkeypatch):
    module, _call_log = _import_devliz_update_module(monkeypatch)

    class FakeCatalogue:
        def __init__(self):
            self.calls = 0

        def get_all(self):
            self.calls += 1
            return ["s1", "s2"]

    catalogue = FakeCatalogue()
    task = module.TaskGetSnapshots(catalogue)

    assert task.name == "TR:Retrieving saved snapshots"
    result = task.execute()

    assert result == ["s1", "s2"]
    assert catalogue.calls == 1

