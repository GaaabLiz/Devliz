from pathlib import Path

from loguru import logger
from pylizlib.qt.domain.view import UiWidgetMode
from qfluentwidgets import FluentIcon, NavigationItemPosition

from devliz.application.app import app_settings, AppSettings, snap_settings
from devliz.application.action_history import log_action, ActionCategory, ActionType
from devliz.controller.action_history import ActionHistoryController
from devliz.controller.backup import BackupController
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
        self.backup = BackupController(self.model.snap_catalogue)
        self.help = HelpController()
        self.catalogue = CatalogueController(self.model, self.__open_search_page)
        self.settings = SettingController(self.model)

        self.view.addSubInterface(self.home.view, FluentIcon.HOME, self.home.view.window_name, NavigationItemPosition.TOP)
        self.view.addSubInterface(self.catalogue.view, FluentIcon.BOOK_SHELF, self.catalogue.view.window_name, NavigationItemPosition.TOP)
        self.view.addSubInterface(self.searcher.view, FluentIcon.SEARCH, self.searcher.view.window_name, NavigationItemPosition.TOP)
        self.view.addSubInterface(self.history.view, FluentIcon.HISTORY, self.history.view.window_name, NavigationItemPosition.TOP)
        self.view.addSubInterface(self.backup.view, FluentIcon.SAVE, self.backup.view.window_name, NavigationItemPosition.TOP)
        self.view.addSubInterface(self.help.view, FluentIcon.HELP, self.help.view.window_name, NavigationItemPosition.BOTTOM)
        self.view.addSubInterface(self.settings.view, FluentIcon.SETTING, self.settings.view.window_name,NavigationItemPosition.BOTTOM)


        self.cached_data: DevlizData | None = None



    def __handle_data_updated(self, data: DevlizData):
        logger.debug("Updated dashboard data received in controller. Updating view...")
        logger.debug(data)
        snap_data = DevlizSnapshotData(snapshot_list=data.snapshots) # TODO: sistemare
        self.cached_data = data
        self.catalogue.update_data(snap_data)
        self.home.update_data(snap_data)
        self.searcher.open()
        self.backup.update_data()
        self.history.reload()
        log_action(ActionCategory.DASHBOARD, ActionType.DASHBOARD_DATA_LOADED, f"snapshots={len(data.snapshots)}")

        self.model.snap_catalogue.path_catalogue = Path(app_settings.get(AppSettings.catalogue_path))

        # Sync snap_settings with current app_settings values
        snap_settings.backup_path = Path(app_settings.get(AppSettings.backup_path))
        snap_settings.backup_pre_install = app_settings.get(AppSettings.backup_before_install)
        snap_settings.backup_pre_modify = app_settings.get(AppSettings.backup_before_edit)
        snap_settings.backup_pre_delete = app_settings.get(AppSettings.backup_before_delete)


    def __handle_update_started(self):
        log_action(ActionCategory.DASHBOARD, ActionType.DASHBOARD_REFRESH_STARTED, "F5/dashboard refresh")
        self.home.view.set_state(UiWidgetMode.UPDATING)
        self.catalogue.view.set_state(UiWidgetMode.UPDATING)
        self.searcher.view.set_state(UiWidgetMode.UPDATING)
        self.history.view.set_state(UiWidgetMode.UPDATING)
        self.backup.view.set_state(UiWidgetMode.UPDATING)
        self.help.view.set_state(UiWidgetMode.UPDATING)

    def __handle_update_complete(self):
        log_action(ActionCategory.DASHBOARD, ActionType.DASHBOARD_REFRESH_COMPLETED, "")
        self.home.view.set_state(UiWidgetMode.DISPLAYING)
        self.catalogue.view.set_state(UiWidgetMode.DISPLAYING)
        self.searcher.view.set_state(UiWidgetMode.DISPLAYING)
        self.history.view.set_state(UiWidgetMode.DISPLAYING)
        self.backup.view.set_state(UiWidgetMode.DISPLAYING)
        self.help.view.set_state(UiWidgetMode.DISPLAYING)

    def __open_search_page(self, snapshot=None):
        self.searcher.open(snapshot)
        self.view.switchTo(self.searcher.view)
        if snapshot is None:
            log_action(ActionCategory.SEARCH, ActionType.SEARCH_PAGE_OPENED, "scope=all")
        else:
            log_action(ActionCategory.SEARCH, ActionType.SEARCH_PAGE_OPENED, f"scope=snapshot:{snapshot.name}")

    def __on_f5_pressed(self):
        log_action(ActionCategory.DASHBOARD, ActionType.DASHBOARD_F5_PRESSED, "")
        self.model.update()

    def __on_page_changed(self, index: int):
        widget = self.view.stackedWidget.widget(index)
        page_name = getattr(widget, "window_name", "")
        if page_name:
            log_action(ActionCategory.DASHBOARD, ActionType.DASHBOARD_PAGE_CHANGED, page_name)

    def __connect_signals(self):
        self.view.f5_pressed.connect(self.__on_f5_pressed)
        self.view.stackedWidget.currentChanged.connect(self.__on_page_changed)
        self.model.signal_on_update_started.connect(self.__handle_update_started)
        self.model.signal_on_update_complete.connect(self.__handle_update_complete)
        self.model.signal_on_updated_data_available.connect(self.__handle_data_updated)
        self.model.signal_on_update_progress.connect(self.__handle_update_progress)
        self.model.signal_on_update_text.connect(self.__handle_update_text)
        self.backup.signal_request_refresh.connect(self.model.update)
        
    def __handle_update_progress(self, progress: int):
        self.home.view.set_updating_progress(progress)
        self.catalogue.view.set_updating_progress(progress)
        self.searcher.view.set_updating_progress(progress)
        self.history.view.set_updating_progress(progress)
        self.backup.view.set_updating_progress(progress)
        self.help.view.set_updating_progress(progress)

    def __handle_update_text(self, text: str):
        self.home.view.set_updating_text(text)
        self.catalogue.view.set_updating_text(text)
        self.searcher.view.set_updating_text(text)
        self.history.view.set_updating_text(text)
        self.backup.view.set_updating_text(text)
        self.help.view.set_updating_text(text)

    def start(self):
        logger.info("Application is starting...")
        log_action(ActionCategory.DASHBOARD, ActionType.DASHBOARD_APPLICATION_STARTED, "")
        self.view.show()
        self.__connect_signals()
        self.history.reload()
        self.model.update()
        self.catalogue.init()
