from typing import Callable

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget
from loguru import logger
from pylizlib.core.os.snap import Snapshot
from pylizlib.qtfw.util.ui import UiUtils
from qfluentwidgets import MessageBox

from devliz.domain.data import DevlizData
from devliz.model.dash_model import DashboardModel
from devliz.view.util.frame import DevlizQFrame
from devliz.view.widgets.catalogue import SnapshotCatalogueWidget
from devliz.view.widgets.catalogue_imp_dialog import DialogConfig


class CatalogueController:

    def __init__(
            self,
            catalogue_widget: SnapshotCatalogueWidget,
            dash_model: DashboardModel
    ):
        self.view = catalogue_widget
        self.dash_model = dash_model

    def init(self):
        self.view.signal_import_requested.connect(lambda: self.__open_config_dialog(False, None))
        self.view.signal_install_requested.connect(self.__install_snapshot)
        self.view.signal_edit_requested.connect(self.__edit_snapshot)
        self.view.signal_delete_requested.connect(self.__delete_snapshot)
        self.view.signal_open_folder_requested.connect(self.__open_snap_directory)
        self.view.signal_duplicate_requested.connect(self.__duplicate_snapshot)

    def __open_config_dialog(self, edit_mode: bool, snap: Snapshot | None = None):
        dialog = DialogConfig(self.dash_model.cached_data, edit_mode, snap)
        try:
            if dialog.exec():
                print(dialog.output_data)
                if edit_mode:
                    old = snap
                    new = dialog.output_data
                    self.dash_model.snap_catalogue.update_snapshot_by_objs(old, new)
                else:
                    self.dash_model.snap_catalogue.add(dialog.output_data)
                titolo = "Configurazione creata" if not edit_mode else "Configurazione modificata"
                testo = "La configurazione è stata creata con successo." if not edit_mode else "La configurazione è stata modificata con successo."
                UiUtils.show_message(titolo, testo)
                self.dash_model.update()
        except Exception as e:
            logger.error(str(e))
            UiUtils.show_message("Attenzione", "Si è verificato un errore: " + str(e))

    def __install_snapshot(self, snap: Snapshot):
        try:
            w = MessageBox("Installa configurazione", "Sei sicuro di voler installare lo snapshot selezionato ? Tutte le directory presenti attualmente verranno rimpiazzate con quelle contenute nello snapshot.", parent=self.view)
            if w.exec_():
                self.dash_model.snap_catalogue.install(snap)
                self.dash_model.update()
        except Exception as e:
            UiUtils.show_message("Errore di installazione", "Si è verificato un errore durante l'installazione: " + str(e))

    def __edit_snapshot(self, snap: Snapshot):
        try:
            self.__open_config_dialog(True, snap)
        except Exception as e:
            UiUtils.show_message("Errore di modifica", "Si è verificato un errore durante la modifica: " + str(e))

    def __delete_snapshot(self, snap: Snapshot):
        try:
            w = MessageBox("Elimina configurazione", "Sei sicuro di voler eliminare lo snapshot selezionato ?\n\n Verranno eliminati tutti i file associati in ", parent=self.view)
            if w.exec_():
                self.dash_model.snap_catalogue.delete(snap)
                self.dash_model.update()
        except Exception as e:
            UiUtils.show_message("Errore di eliminazione", "Si è verificato un errore durante l'eliminazione: " + str(e))

    def __open_snap_directory(self, path):
        pass

    def __duplicate_snapshot(self, snap: Snapshot):
        try:
            w = MessageBox("Duplica configurazione", "Sei sicuro di voler duplicare la configurazione selezionata ?", parent=self.view)
            if w.exec_():
                self.dash_model.snap_catalogue.duplicate_by_id(snap.id)
                self.dash_model.update()
        except Exception as e:
            UiUtils.show_message("Errore di duplicazione", "Si è verificato un errore durante la duplicazione: " + str(e))