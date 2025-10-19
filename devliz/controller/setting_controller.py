from pathlib import Path

from PySide6.QtWidgets import QFileDialog
from loguru import logger

from devliz.application.app import app_settings, DevlizSettings
from devliz.model.dash_model import DashboardModel
from devliz.view.widgets.setting import WidgetSettings


class SettingController:

    def __init__(self, view: WidgetSettings, dash_model: DashboardModel):
        self.view = view
        self.dash_model = dash_model

        self.view.signal_request_update.connect(self.dash_model.update)
        self.view.signal_ask_catalogue_path.connect(self.__ask_catalogue_path)

    def __ask_catalogue_path(self):
        directory = QFileDialog.getExistingDirectory(None, "Seleziona la cartella del catalogo")
        if directory:
            logger.trace(f"Percorso selezionato: {directory}")
            app_settings.set(DevlizSettings.catalogue_path, Path(directory))
            self.view.card_general_catalogue.setContent(directory)
            self.dash_model.update()
        else:
            logger.trace("Nessun percorso selezionato.")

