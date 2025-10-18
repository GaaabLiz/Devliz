from loguru import logger
from pylizlib.qt.domain.view import UiWidgetMode

from devliz.controller.catalogue_controller import CatalogueController
from devliz.domain.data import DevlizData, DevlizSnapshotData
from devliz.model.dash_model import DashboardModel
from devliz.view.dash_view import DashboardView


class DashboardController:

    def __init__(self):
        self.view = DashboardView()
        self.model = DashboardModel(self.view)

        self.catalogue = CatalogueController(self.view.widget_setting)

    def __update_all(self):
        try:
            logger.info("Triggerato aggiornamento")
            self.model.update()
        except Exception as e:
            # UiUtils.show_message("Attenzione", "Si è verificato un errore durante l'aggiornamento dei dati di DEVLIZ: " + str(e))
            logger.error("Errore aggiornamento:" + str(e))

    def __handle_data_updated(self, data: DevlizData):
        print(data)
        snap_data = DevlizSnapshotData(snapshot_list=data.snapshots)
        self.view.widget_catalogue.update_widget(snap_data)

    def __handle_update_started(self):
        self.view.set_state(UiWidgetMode.UPDATING)

    def __handle_update_complete(self):
        self.view.set_state(UiWidgetMode.DISPLAYING)

    def __connect_signals(self):
        self.view.f5_pressed.connect(lambda: self.__update_all())
        self.model.signal_on_update_started.connect(self.__handle_update_started)
        self.model.signal_on_update_complete.connect(self.__handle_update_complete)
        self.model.signal_on_updated_data_available.connect(self.__handle_data_updated)

    def start(self):
        logger.info("Devliz is starting...")
        self.view.show()
        self.__connect_signals()
        self.__update_all()
