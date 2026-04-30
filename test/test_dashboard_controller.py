import sys
import types
from pathlib import Path


def _import_dashboard_module(monkeypatch):
    actions = []

    class FakeSignal:
        def __init__(self):
            self._slots = []

        def connect(self, slot):
            self._slots.append(slot)

        def emit(self, *args, **kwargs):
            for slot in list(self._slots):
                slot(*args, **kwargs)

    class FakePageView:
        def __init__(self, window_name):
            self.window_name = window_name
            self.states = []

        def set_state(self, state):
            self.states.append(state)

    class FakeStackedWidget:
        def __init__(self):
            self.currentChanged = FakeSignal()
            self.widgets = {}

        def widget(self, index):
            return self.widgets.get(index, types.SimpleNamespace())

    class FakeDashboardView:
        def __init__(self):
            self.f5_pressed = FakeSignal()
            self.stackedWidget = FakeStackedWidget()
            self.added_sub_interfaces = []
            self.switched_to = None
            self.shown = False

        def addSubInterface(self, view, icon, name, position):
            self.added_sub_interfaces.append((view, icon, name, position))

        def switchTo(self, view):
            self.switched_to = view

        def show(self):
            self.shown = True

    class FakeHomeController:
        def __init__(self):
            self.view = FakePageView("Home")
            self.update_data_calls = []

        def update_data(self, data):
            self.update_data_calls.append(data)

    class FakeSearcherController:
        def __init__(self, _snap_catalogue, _view):
            self.view = FakePageView("Search")
            self.open_calls = []

        def open(self, snapshot=None):
            self.open_calls.append(snapshot)

    class FakeActionHistoryController:
        def __init__(self):
            self.view = FakePageView("History")
            self.reload_count = 0

        def reload(self):
            self.reload_count += 1

    class FakeHelpController:
        def __init__(self):
            self.view = FakePageView("Help")

    class FakeCatalogueController:
        def __init__(self, _model, _open_search_page):
            self.view = FakePageView("Catalogue")
            self.update_data_calls = []
            self.init_count = 0

        def update_data(self, data):
            self.update_data_calls.append(data)

        def init(self):
            self.init_count += 1

    class FakeSettingController:
        def __init__(self, _model):
            self.view = FakePageView("Settings")

    class FakeDashboardModel:
        def __init__(self, _view):
            self.signal_on_update_started = FakeSignal()
            self.signal_on_update_complete = FakeSignal()
            self.signal_on_updated_data_available = FakeSignal()
            self.snap_catalogue = types.SimpleNamespace(path_catalogue=None)
            self.update_count = 0

        def update(self):
            self.update_count += 1

    class FakeUiWidgetMode:
        UPDATING = "UPDATING"
        DISPLAYING = "DISPLAYING"

    class FakeFluentIcon:
        HOME = "HOME"
        BOOK_SHELF = "BOOK_SHELF"
        SEARCH = "SEARCH"
        HISTORY = "HISTORY"
        HELP = "HELP"
        SETTING = "SETTING"

    class FakeNavigationItemPosition:
        TOP = "TOP"
        BOTTOM = "BOTTOM"

    class FakeAppSettings:
        @staticmethod
        def get(_key):
            return "/tmp/devliz-catalogue"

    class FakeAppSettingsKeys:
        catalogue_path = "catalogue_path"

    class FakeDevlizSnapshotData:
        def __init__(self, snapshot_list):
            self.snapshot_list = snapshot_list

    class FakeDevlizData:
        def __init__(self, snapshots=None):
            self.snapshots = snapshots or []

    fake_action_history_module = types.ModuleType("devliz.application.action_history")

    def fake_log_action(screen_key, action_key, details=""):
        actions.append((screen_key, action_key, details))

    fake_action_history_module.log_action = fake_log_action

    fake_app_module = types.ModuleType("devliz.application.app")
    fake_app_module.app_settings = FakeAppSettings()
    fake_app_module.AppSettings = FakeAppSettingsKeys

    fake_data_module = types.ModuleType("devliz.domain.data")
    fake_data_module.DevlizData = FakeDevlizData
    fake_data_module.DevlizSnapshotData = FakeDevlizSnapshotData

    fake_qfluentwidgets = types.ModuleType("qfluentwidgets")
    fake_qfluentwidgets.FluentIcon = FakeFluentIcon
    fake_qfluentwidgets.NavigationItemPosition = FakeNavigationItemPosition

    fake_ui_module = types.ModuleType("pylizlib.qt.domain.view")
    fake_ui_module.UiWidgetMode = FakeUiWidgetMode

    fake_logger_module = types.ModuleType("loguru")
    fake_logger_module.logger = types.SimpleNamespace(debug=lambda *a, **k: None, info=lambda *a, **k: None)

    monkeypatch.setitem(sys.modules, "devliz.application.action_history", fake_action_history_module)
    monkeypatch.setitem(sys.modules, "devliz.application.app", fake_app_module)
    monkeypatch.setitem(sys.modules, "devliz.domain.data", fake_data_module)
    monkeypatch.setitem(sys.modules, "qfluentwidgets", fake_qfluentwidgets)
    monkeypatch.setitem(sys.modules, "pylizlib.qt.domain.view", fake_ui_module)
    monkeypatch.setitem(sys.modules, "loguru", fake_logger_module)

    for module_name, cls_name, cls in [
        ("devliz.controller.action_history", "ActionHistoryController", FakeActionHistoryController),
        ("devliz.controller.catalogue_searcher", "CatalogueSearcherController", FakeSearcherController),
        ("devliz.controller.catalogue", "CatalogueController", FakeCatalogueController),
        ("devliz.controller.help", "HelpController", FakeHelpController),
        ("devliz.controller.home", "HomeController", FakeHomeController),
        ("devliz.controller.setting_controller", "SettingController", FakeSettingController),
        ("devliz.model.dashboard", "DashboardModel", FakeDashboardModel),
        ("devliz.view.dashboard", "DashboardView", FakeDashboardView),
    ]:
        module = types.ModuleType(module_name)
        setattr(module, cls_name, cls)
        monkeypatch.setitem(sys.modules, module_name, module)

    sys.modules.pop("devliz.controller.dashboard", None)
    import devliz.controller.dashboard as dashboard_module

    return dashboard_module, actions


def test_start_connects_signals_and_runs_initial_refresh(monkeypatch):
    dashboard_module, actions = _import_dashboard_module(monkeypatch)
    controller = dashboard_module.DashboardController()

    assert len(controller.view.added_sub_interfaces) == 6

    controller.start()

    assert controller.view.shown is True
    assert controller.history.reload_count == 1
    assert controller.model.update_count == 1
    assert controller.catalogue.init_count == 1
    assert ("Dashboard", "dashboard.application.started", "") in actions

    controller.view.f5_pressed.emit()
    assert controller.model.update_count == 2
    assert ("Dashboard", "dashboard.f5.pressed", "") in actions

    controller.view.stackedWidget.widgets[3] = types.SimpleNamespace(window_name="Catalogue")
    controller.view.stackedWidget.currentChanged.emit(3)
    assert ("Dashboard", "dashboard.page.changed", "Catalogue") in actions


def test_open_search_page_switches_view_and_logs_scope(monkeypatch):
    dashboard_module, actions = _import_dashboard_module(monkeypatch)
    controller = dashboard_module.DashboardController()

    controller._DashboardController__open_search_page()
    assert controller.searcher.open_calls[-1] is None
    assert controller.view.switched_to is controller.searcher.view
    assert ("Search", "search.page.opened", "scope=all") in actions

    snap = types.SimpleNamespace(name="snap-1")
    controller._DashboardController__open_search_page(snap)
    assert controller.searcher.open_calls[-1] is snap
    assert ("Search", "search.page.opened", "scope=snapshot:snap-1") in actions


def test_update_started_and_complete_toggle_all_states(monkeypatch):
    dashboard_module, actions = _import_dashboard_module(monkeypatch)
    controller = dashboard_module.DashboardController()

    controller._DashboardController__handle_update_started()
    assert controller.home.view.states[-1] == "UPDATING"
    assert controller.catalogue.view.states[-1] == "UPDATING"
    assert controller.searcher.view.states[-1] == "UPDATING"
    assert controller.history.view.states[-1] == "UPDATING"
    assert controller.help.view.states[-1] == "UPDATING"
    assert ("Dashboard", "dashboard.refresh.started", "F5/dashboard refresh") in actions

    controller._DashboardController__handle_update_complete()
    assert controller.home.view.states[-1] == "DISPLAYING"
    assert controller.catalogue.view.states[-1] == "DISPLAYING"
    assert controller.searcher.view.states[-1] == "DISPLAYING"
    assert controller.history.view.states[-1] == "DISPLAYING"
    assert controller.help.view.states[-1] == "DISPLAYING"
    assert ("Dashboard", "dashboard.refresh.completed", "") in actions


def test_handle_data_updated_updates_children_and_catalogue_path(monkeypatch):
    dashboard_module, actions = _import_dashboard_module(monkeypatch)
    controller = dashboard_module.DashboardController()

    data = types.SimpleNamespace(snapshots=["s1", "s2", "s3"])
    controller._DashboardController__handle_data_updated(data)

    assert controller.cached_data is data
    assert len(controller.catalogue.update_data_calls) == 1
    assert len(controller.home.update_data_calls) == 1
    assert controller.catalogue.update_data_calls[0].snapshot_list == ["s1", "s2", "s3"]
    assert controller.searcher.open_calls[-1] is None
    assert controller.history.reload_count == 1
    assert controller.model.snap_catalogue.path_catalogue == Path("/tmp/devliz-catalogue")
    assert ("Dashboard", "dashboard.data.loaded", "snapshots=3") in actions

