from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget
from loguru import logger
from pylizlib.core.os.snap import Snapshot
from pylizlib.qtfw.util.ui import UiUtils

from devliz.domain.data import DevlizData
from devliz.view.util.frame import DevlizQFrame
from devliz.view.widgets.catalogue import SnapshotCatalogueWidget
from devliz.view.widgets.catalogue_imp_dialog import DialogConfig


class CatalogueController:

    def __init__(
            self,
            cached_data: DevlizData,
            catalogue_widget: SnapshotCatalogueWidget,
            signal_update: Signal | None = None
    ):
        self.cached_data: DevlizData | None = cached_data
        self.view = catalogue_widget
        self.signal_update = signal_update

    def init(self):
        self.view.signal_import_requested.connect(lambda: self.__open_config_dialog(False, None))

    def __open_config_dialog(self, edit_mode: bool, snap: Snapshot | None = None):
        dialog = DialogConfig(self.cached_data, edit_mode, snap)
        try:
            if dialog.exec():
                #ConfigManager.create(dialog.output_data, edit_mode)
                titolo = "Configurazione creata" if not edit_mode else "Configurazione modificata"
                testo = "La configurazione è stata creata con successo." if not edit_mode else "La configurazione è stata modificata con successo."
                UiUtils.show_message(titolo, testo)
                #self.signal_update.emit()
        except Exception as e:
            logger.error(str(e))
            UiUtils.show_message("Attenzione", "Si è verificato un errore: " + str(e))
