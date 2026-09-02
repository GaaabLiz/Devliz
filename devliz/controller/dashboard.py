from pathlib import Path

from loguru import logger
from pylizlib.qt.domain.view import UiWidgetMode
from pylizlib.qtfw.util.ui import UiUtils
from qfluentwidgets import FluentIcon, NavigationItemPosition

from devliz.application.app import app_settings, AppSettings
from devliz.model.history import log_action, ActionCategory, ActionType
from devliz.controller.history import ActionHistoryController
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
    """
    Main controller for the application dashboard.

    This class serves as the central hub of the application, initializing and
    coordinating all other major controllers (Home, Catalogue, Search, Backup, etc.).
    It manages the main navigation interface and coordinates global data updates.
    """

    def __init__(self, /):
        """
        Initializes the DashboardController.

        Sets up the main view, model, and all child controllers, and adds their
        respective views as sub-interfaces to the main dashboard navigation.
        """
        super().__init__()

        self.view = DashboardView()
        self.model = DashboardModel()

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
        """
        Handles the event when new dashboard data is loaded.

        Distributes the updated data to the child controllers (Catalogue, Home, Backup, etc.)
        so they can refresh their respective views.

        Args:
            data (DevlizData): The newly updated application data.
        """
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


    def __handle_update_started(self):
        """
        Handles the event when a global data refresh starts.

        Sets all child views to an 'UPDATING' state to display progress indicators.
        """
        log_action(ActionCategory.DASHBOARD, ActionType.DASHBOARD_REFRESH_STARTED, "F5/dashboard refresh")
        self.home.view.set_state(UiWidgetMode.UPDATING)
        self.catalogue.view.set_state(UiWidgetMode.UPDATING)
        self.searcher.view.set_state(UiWidgetMode.UPDATING)
        self.history.view.set_state(UiWidgetMode.UPDATING)
        self.backup.view.set_state(UiWidgetMode.UPDATING)
        self.help.view.set_state(UiWidgetMode.UPDATING)

    def __handle_update_complete(self):
        """
        Handles the event when a global data refresh completes.

        Restores all child views to a 'DISPLAYING' state.
        """
        log_action(ActionCategory.DASHBOARD, ActionType.DASHBOARD_REFRESH_COMPLETED, "")
        self.home.view.set_state(UiWidgetMode.DISPLAYING)
        self.catalogue.view.set_state(UiWidgetMode.DISPLAYING)
        self.searcher.view.set_state(UiWidgetMode.DISPLAYING)
        self.history.view.set_state(UiWidgetMode.DISPLAYING)
        self.backup.view.set_state(UiWidgetMode.DISPLAYING)
        self.help.view.set_state(UiWidgetMode.DISPLAYING)

    def __open_search_page(self, snapshot=None):
        """
        Opens the search page and optionally scopes the search to a specific snapshot.

        Args:
            snapshot: Optional snapshot to restrict the search context.
        """
        self.searcher.open(snapshot)
        self.view.switchTo(self.searcher.view)
        if snapshot is None:
            log_action(ActionCategory.SEARCH, ActionType.SEARCH_PAGE_OPENED, "scope=all")
        else:
            log_action(ActionCategory.SEARCH, ActionType.SEARCH_PAGE_OPENED, f"scope=snapshot:{snapshot.name}")

    def __on_f5_pressed(self):
        """
        Handles the manual refresh action triggered by the F5 key.
        """
        log_action(ActionCategory.DASHBOARD, ActionType.DASHBOARD_F5_PRESSED, "")
        self.model.update()

    def __on_page_changed(self, index: int):
        """
        Logs an action whenever the user navigates to a different page in the dashboard.

        Args:
            index (int): The index of the newly selected page in the stacked widget.
        """
        widget = self.view.stackedWidget.widget(index)
        page_name = getattr(widget, "window_name", "")
        if page_name:
            log_action(ActionCategory.DASHBOARD, ActionType.DASHBOARD_PAGE_CHANGED, page_name)

    def __connect_signals(self):
        """
        Connects all UI and model signals to their respective handler slots.
        """
        self.view.f5_pressed.connect(self.__on_f5_pressed)
        self.view.stackedWidget.currentChanged.connect(self.__on_page_changed)
        self.model.signal_on_update_started.connect(self.__handle_update_started)
        self.model.signal_on_update_complete.connect(self.__handle_update_complete)
        self.model.signal_on_updated_data_available.connect(self.__handle_data_updated)
        self.model.signal_on_update_progress.connect(self.__handle_update_progress)
        self.model.signal_on_update_text.connect(self.__handle_update_text)
        self.model.signal_on_update_detail_text.connect(self.__handle_update_detail_text)
        self.model.signal_on_heavy_operation_success.connect(UiUtils.show_message)
        self.model.signal_on_heavy_operation_error.connect(UiUtils.show_message)
        self.backup.signal_request_refresh.connect(self.model.update)
        
    def __handle_update_progress(self, progress: int):
        """
        Propagates the progress value of an ongoing heavy operation to all child views.

        Args:
            progress (int): The current progress percentage (0-100).
        """
        self.home.view.set_updating_progress(progress)
        self.catalogue.view.set_updating_progress(progress)
        self.searcher.view.set_updating_progress(progress)
        self.history.view.set_updating_progress(progress)
        self.backup.view.set_updating_progress(progress)
        self.help.view.set_updating_progress(progress)

    def __handle_update_text(self, text: str):
        """
        Propagates the main status text of an ongoing heavy operation to all child views.

        Args:
            text (str): The primary status message.
        """
        self.home.view.set_updating_text(text)
        self.catalogue.view.set_updating_text(text)
        self.searcher.view.set_updating_text(text)
        self.history.view.set_updating_text(text)
        self.backup.view.set_updating_text(text)
        self.help.view.set_updating_text(text)
        
    def __handle_update_detail_text(self, text: str):
        """
        Propagates the detailed status text of an ongoing heavy operation to all child views.

        Args:
            text (str): The secondary, detailed status message.
        """
        self.home.view.set_updating_detail_text(text)
        self.catalogue.view.set_updating_detail_text(text)
        self.searcher.view.set_updating_detail_text(text)
        self.history.view.set_updating_detail_text(text)
        self.backup.view.set_updating_detail_text(text)
        self.help.view.set_updating_detail_text(text)

    def start(self):
        """
        Starts the dashboard application flow.

        Shows the main view, establishes signal connections, and initiates the
        first data load for the catalogue, history, and dashboard models.
        """
        logger.info("Application is starting...")
        log_action(ActionCategory.DASHBOARD, ActionType.DASHBOARD_APPLICATION_STARTED, "")
        self.view.show()
        self.__connect_signals()
        self.history.reload()
        self.model.update()
        self.catalogue.init()
