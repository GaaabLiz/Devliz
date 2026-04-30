from pathlib import Path

from loguru import logger
from pylizlib.qt.domain.view import UiWidgetMode
from qfluentwidgets import FluentIcon, NavigationItemPosition

from devliz.application.app import app_settings, AppSettings
from devliz.application.action_history import log_action
from devliz.controller.action_history import ActionHistoryController
from devliz.controller.catalogue_searcher import CatalogueSearcherController
from devliz.controller.catalogue import CatalogueController
from devliz.controller.help import HelpController
from devliz.controller.home import HomeController
from devliz.controller.setting_controller import SettingController
from devliz.domain.data import DevlizData, DevlizSnapshotData
from devliz.model.dashboard import DashboardModel
from devliz.view.dashboard import DashboardView


class DashboardController:

    def __init__(self, /):
        super().__init__()

        self.view = DashboardView()
        self.model = DashboardModel(self.view)

        self.home = HomeController()
        self.searcher = CatalogueSearcherController(self.model.snap_catalogue, self.view)
        self.history = ActionHistoryController()
        self.help = HelpController()
        self.catalogue = CatalogueController(self.model, self.__open_search_page)
        self.settings = SettingController(self.model)

        self.view.addSubInterface(self.home.view, FluentIcon.HOME, self.home.view.window_name, NavigationItemPosition.TOP)
        self.view.addSubInterface(self.catalogue.view, FluentIcon.BOOK_SHELF, self.catalogue.view.window_name, NavigationItemPosition.TOP)
        self.view.addSubInterface(self.searcher.view, FluentIcon.SEARCH, self.searcher.view.window_name, NavigationItemPosition.TOP)
        self.view.addSubInterface(self.history.view, FluentIcon.HISTORY, self.history.view.window_name, NavigationItemPosition.TOP)
        self.view.addSubInterface(self.help.view, FluentIcon.HELP, self.help.view.window_name, NavigationItemPosition.BOTTOM)
        self.view.addSubInterface(self.settings.view, FluentIcon.SETTING, self.settings.view.window_name,NavigationItemPosition.BOTTOM)


        self.cached_data : DevlizData | None = None



    def __handle_data_updated(self, data: DevlizData):
        logger.debug("Updated dashboard data received in controller. Updating view...")
        logger.debug(data)
        snap_data = DevlizSnapshotData(snapshot_list=data.snapshots) # TODO: sistemare
        self.cached_data = data
        self.catalogue.update_data(snap_data)
        self.home.update_data(snap_data)
        self.searcher.open()
        self.history.reload()
        log_action("Dashboard", "dashboard.data.loaded", f"snapshots={len(data.snapshots)}")

        self.model.snap_catalogue.path_catalogue = Path(app_settings.get(AppSettings.catalogue_path))


    def __handle_update_started(self):
        log_action("Dashboard", "dashboard.refresh.started", "F5/dashboard refresh")
        self.home.view.set_state(UiWidgetMode.UPDATING)
        self.catalogue.view.set_state(UiWidgetMode.UPDATING)
        self.searcher.view.set_state(UiWidgetMode.UPDATING)
        self.history.view.set_state(UiWidgetMode.UPDATING)
        self.help.view.set_state(UiWidgetMode.UPDATING)

    def __handle_update_complete(self):
        log_action("Dashboard", "dashboard.refresh.completed", "")
        self.home.view.set_state(UiWidgetMode.DISPLAYING)
        self.catalogue.view.set_state(UiWidgetMode.DISPLAYING)
        self.searcher.view.set_state(UiWidgetMode.DISPLAYING)
        self.history.view.set_state(UiWidgetMode.DISPLAYING)
        self.help.view.set_state(UiWidgetMode.DISPLAYING)

    def __open_search_page(self, snapshot=None):
        self.searcher.open(snapshot)
        self.view.switchTo(self.searcher.view)
        if snapshot is None:
            log_action("Search", "search.page.opened", "scope=all")
        else:
            log_action("Search", "search.page.opened", f"scope=snapshot:{snapshot.name}")

    def __on_f5_pressed(self):
        log_action("Dashboard", "dashboard.f5.pressed", "")
        self.model.update()

    def __on_page_changed(self, index: int):
        widget = self.view.stackedWidget.widget(index)
        page_name = getattr(widget, "window_name", "")
        if page_name:
            log_action("Dashboard", "dashboard.page.changed", page_name)

    def __connect_signals(self):
        self.view.f5_pressed.connect(self.__on_f5_pressed)
        self.view.stackedWidget.currentChanged.connect(self.__on_page_changed)
        self.model.signal_on_update_started.connect(self.__handle_update_started)
        self.model.signal_on_update_complete.connect(self.__handle_update_complete)
        self.model.signal_on_updated_data_available.connect(self.__handle_data_updated)

    def start(self):
        logger.info("Application is starting...")
        log_action("Dashboard", "dashboard.application.started", "")
        self.view.show()
        self.__connect_signals()
        self.history.reload()
        self.model.update()
        self.catalogue.init()
