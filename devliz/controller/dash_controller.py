from loguru import logger

from devliz.controller.catalogue_controller import CatalogueController
from devliz.model.dash_model import DashboardModel
from devliz.view.dash_view import DashboardView
from devliz.domain.data import DevlizData


class DashboardController:

    def __init__(self):
        self.view = DashboardView()
        self.model = DashboardModel(self.view)

        self.catalogue = CatalogueController(self.view.widget_setting)

    def __update_all(self):
        try:
            logger.info("Triggerato aggiornamento")
            self.model.update()
            logger.info("Aggiornamento completato")
        except Exception as e:
            # UiUtils.show_message("Attenzione", "Si è verificato un errore durante l'aggiornamento dei dati di DEVLIZ: " + str(e))
            logger.error("Errore aggiornamento:" + str(e))

    def __handle_data_updated(self):
        pass

    def __connect_signals(self):
        self.view.f5_pressed.connect(lambda: self.__update_all())

    def start(self):
        logger.info("Devliz is starting...")
        self.view.show()
        self.__connect_signals()
        self.__update_all()
