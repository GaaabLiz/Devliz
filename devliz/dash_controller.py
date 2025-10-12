from loguru import logger

from devliz.dash_model import DashboardModel
from devliz.dash_view import DashboardView
from devliz.domain.data import DevlizData


class DashboardController:

    def __init__(self):
        self.view = DashboardView()
        self.model = DashboardModel()
        self.cached_data: DevlizData | None = None

    def __update_all(self):
        try:
            logger.info("Triggerato aggiornamento")
            data = self.model.gen_atom_dev_data()
            self.cached_data = data
            # Widget Home
            self.view.widget_home.update_widget(data.monitored_software, data.monitored_services, data.starred_dirs, data.starred_files)
            self.view.widget_config.update_widget(data.configurations)
        except Exception as e:
            # UiUtils.show_message("Attenzione", "Si è verificato un errore durante l'aggiornamento dei dati di DEVLIZ: " + str(e))
            logger.error("Errore aggiornamento app:" + str(e))

    def start(self):
        logger.info("Devliz is starting...")
        self.view.show()
        # self.__connect_signals()
        self.__update_all()
