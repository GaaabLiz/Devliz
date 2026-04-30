import sys
import types


def _import_dashboard_model_module(monkeypatch):
    logs = {"info": [], "debug": [], "error": []}

    class FakeSignal:
        def __init__(self, *_args, **_kwargs):
            self._slots = []

        def connect(self, slot):
            self._slots.append(slot)

        def emit(self, *args, **kwargs):
            for slot in list(self._slots):
                slot(*args, **kwargs)

    class FakeQObject:
        pass

    class FakeOperation:
        def __init__(self, tasks, operation_info):
            self.tasks = tasks
            self.operation_info = operation_info
            self._results = {}

        def get_task_result_by_id(self, task_id):
            return self._results[task_id]

    class FakeOperationInfo:
        def __init__(self, name, description, delay_each_task):
            self.name = name
            self.description = description
            self.delay_each_task = delay_each_task

    class FakeRunnerStatistics:
        def __init__(self, operations=None, failed=False, first_error="boom"):
            self.operations = operations or []
            self._failed = failed
            self._first_error = first_error

        def has_ops_failed(self):
            return self._failed

        def get_first_error(self):
            return self._first_error

    class FakeOperationRunner:
        def __init__(self, abort_all_on_error):
            self.abort_all_on_error = abort_all_on_error
            self.runner_start = FakeSignal()
            self.runner_stop = FakeSignal()
            self.runner_finish = FakeSignal()
            self.clear_count = 0
            self.added_ops = []
            self.start_count = 0

        def clear(self):
            self.clear_count += 1

        def add(self, op):
            self.added_ops.append(op)

        def start(self):
            self.start_count += 1

    class FakeSnapshotCatalogue:
        def __init__(self, path_catalogue, settings):
            self.path_catalogue = path_catalogue
            self.settings = settings

    class FakeTask:
        next_id = 1

        def __init__(self, name="task"):
            self.name = name
            self.id = f"t{FakeTask.next_id}"
            FakeTask.next_id += 1

    class FakeTaskGetMonitoredSoftware(FakeTask):
        def __init__(self):
            super().__init__("monitored")

    class FakeTaskGetSnapshots(FakeTask):
        def __init__(self, catalogue):
            super().__init__("snapshots")
            self.catalogue = catalogue

    class FakeDevlizData:
        def __init__(self, snapshots=None, monitored_software=None):
            self.snapshots = snapshots
            self.monitored_software = monitored_software

    fake_qtcore = types.ModuleType("PySide6.QtCore")
    fake_qtcore.QObject = FakeQObject
    fake_qtcore.Signal = FakeSignal

    fake_runner_module = types.ModuleType("pylizlib.qt.handler.operation_runner")
    fake_runner_module.OperationRunner = FakeOperationRunner
    fake_runner_module.RunnerStatistics = FakeRunnerStatistics

    fake_operation_core_module = types.ModuleType("pylizlib.qt.handler.operation_core")
    fake_operation_core_module.Operation = FakeOperation

    fake_operation_domain_module = types.ModuleType("pylizlib.qt.handler.operation_domain")
    fake_operation_domain_module.OperationInfo = FakeOperationInfo

    fake_snap_module = types.ModuleType("pylizlib.core.os.snap")
    fake_snap_module.SnapshotCatalogue = FakeSnapshotCatalogue

    fake_data_module = types.ModuleType("devliz.domain.data")
    fake_data_module.DevlizData = FakeDevlizData

    fake_update_module = types.ModuleType("devliz.model.devliz_update")
    fake_update_module.TaskGetMonitoredSoftware = FakeTaskGetMonitoredSoftware
    fake_update_module.TaskGetSnapshots = FakeTaskGetSnapshots

    fake_view_module = types.ModuleType("devliz.view.dashboard")

    class FakeDashboardView:
        pass

    fake_view_module.DashboardView = FakeDashboardView

    fake_app_module = types.ModuleType("devliz.application.app")

    class FakeAppSettings:
        @staticmethod
        def get(_key):
            return "/tmp/catalogue"

    class FakeAppSettingsKeys:
        catalogue_path = "catalogue_path"

    fake_app_module.app_settings = FakeAppSettings()
    fake_app_module.AppSettings = FakeAppSettingsKeys
    fake_app_module.PATH_BACKUPS = "/tmp/backups"
    fake_app_module.snap_settings = "snap-settings"

    fake_i18n_module = types.ModuleType("devliz.application.i18n")
    fake_i18n_module.tr = lambda key: key

    fake_ui_mode_module = types.ModuleType("pylizlib.qt.domain.view")
    fake_ui_mode_module.UiWidgetMode = types.SimpleNamespace()

    fake_logger_module = types.ModuleType("loguru")
    fake_logger_module.logger = types.SimpleNamespace(
        info=lambda msg: logs["info"].append(msg),
        debug=lambda msg: logs["debug"].append(msg),
        error=lambda msg: logs["error"].append(msg),
    )

    monkeypatch.setitem(sys.modules, "PySide6.QtCore", fake_qtcore)
    monkeypatch.setitem(sys.modules, "pylizlib.qt.handler.operation_runner", fake_runner_module)
    monkeypatch.setitem(sys.modules, "pylizlib.qt.handler.operation_core", fake_operation_core_module)
    monkeypatch.setitem(sys.modules, "pylizlib.qt.handler.operation_domain", fake_operation_domain_module)
    monkeypatch.setitem(sys.modules, "pylizlib.core.os.snap", fake_snap_module)
    monkeypatch.setitem(sys.modules, "devliz.domain.data", fake_data_module)
    monkeypatch.setitem(sys.modules, "devliz.model.devliz_update", fake_update_module)
    monkeypatch.setitem(sys.modules, "devliz.view.dashboard", fake_view_module)
    monkeypatch.setitem(sys.modules, "devliz.application.app", fake_app_module)
    monkeypatch.setitem(sys.modules, "devliz.application.i18n", fake_i18n_module)
    monkeypatch.setitem(sys.modules, "pylizlib.qt.domain.view", fake_ui_mode_module)
    monkeypatch.setitem(sys.modules, "loguru", fake_logger_module)

    sys.modules.pop("devliz.model.dashboard", None)
    import devliz.model.dashboard as dashboard_model_module

    return dashboard_model_module, logs


def test_update_builds_operation_and_starts_runner(monkeypatch):
    dashboard_model_module, _logs = _import_dashboard_model_module(monkeypatch)
    model = dashboard_model_module.DashboardModel(view=object())

    model.update()

    assert model.runner.clear_count == 1
    assert len(model.runner.added_ops) == 1
    assert model.runner.start_count == 1

    operation = model.runner.added_ops[0]
    assert operation.tasks == [model.task_monitored_soft, model.task_snap]
    assert operation.operation_info is model.operation_info


def test_on_runner_started_emits_signal(monkeypatch):
    dashboard_model_module, _logs = _import_dashboard_model_module(monkeypatch)
    model = dashboard_model_module.DashboardModel(view=object())

    calls = []
    model.signal_on_update_started.connect(lambda: calls.append("started"))

    model.on_runner_started()
    assert calls == ["started"]


def test_on_runner_finished_success_emits_data_and_caches(monkeypatch):
    dashboard_model_module, _logs = _import_dashboard_model_module(monkeypatch)
    model = dashboard_model_module.DashboardModel(view=object())

    fake_operation = types.SimpleNamespace(
        get_task_result_by_id=lambda task_id: ["s1"] if task_id == model.task_snap.id else ["soft1"]
    )
    stats = dashboard_model_module.RunnerStatistics(operations=[fake_operation], failed=False)

    received = []
    model.signal_on_updated_data_available.connect(lambda data: received.append(data))

    model.on_runner_finished(stats)

    assert len(received) == 1
    assert received[0].snapshots == ["s1"]
    assert received[0].monitored_software == ["soft1"]
    assert model.get_cached_data() is received[0]


def test_on_runner_finished_failure_logs_and_does_not_emit_data(monkeypatch):
    dashboard_model_module, logs = _import_dashboard_model_module(monkeypatch)
    model = dashboard_model_module.DashboardModel(view=object())

    stats = dashboard_model_module.RunnerStatistics(operations=[], failed=True, first_error="fatal")

    received = []
    model.signal_on_updated_data_available.connect(lambda data: received.append(data))

    model.on_runner_finished(stats)

    assert received == []
    assert model.get_cached_data() is None
    assert any("fatal" in msg for msg in logs["error"])


def test_update_logs_error_if_runner_add_raises(monkeypatch):
    dashboard_model_module, logs = _import_dashboard_model_module(monkeypatch)
    model = dashboard_model_module.DashboardModel(view=object())

    def raise_on_add(_op):
        raise RuntimeError("cannot add")

    model.runner.add = raise_on_add

    model.update()

    assert model.runner.start_count == 0
    assert any("cannot add" in msg for msg in logs["error"])

