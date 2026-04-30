import os
import shutil
import sys
from pathlib import Path

from PySide6.QtCore import QProcess
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFileDialog, QApplication
from loguru import logger
from pylizlib.qtfw.util.ui import UiUtils
from pylizlib.qtfw.widgets.dialog.about import AboutMessageBox
from qfluentwidgets import MessageBox

from devliz.application.app import app_settings, AppSettings, PATH_BACKUPS, RESOURCE_ID_LOGO, app
from devliz.application.action_history import log_action
from devliz.application.i18n import tr
from devliz.model.dashboard import DashboardModel
from devliz.view.setting import WidgetSettings


class SettingController:

    def __init__(self, dash_model: DashboardModel):
        self.view = WidgetSettings()
        self.dash_model = dash_model

        self.view.signal_request_update.connect(self.dash_model.update)
        self.view.signal_ask_catalogue_path.connect(self.__ask_catalogue_path)
        self.view.signal_open_dir_request.connect(self.__open_directory)
        self.view.signal_clear_backups_request.connect(self.__clear_backup_directory)
        self.view.signal_open_about_dialog_request.connect(self.__open_info_dialog)
        self.view.signal_language_changed.connect(self.__on_language_or_theme_changed)
        self.view.signal_theme_changed.connect(self.__on_language_or_theme_changed)

    def __on_language_or_theme_changed(self):
        w = MessageBox(tr("Restart required"), tr("The application needs to restart to apply the changes. Restart now?"), parent=self.view)
        if w.exec_():
            log_action("Settings", "settings.restart.confirmed", "theme/language change")
            QProcess.startDetached(sys.executable, sys.argv)
            QApplication.instance().quit()

    def __ask_catalogue_path(self):
        directory = QFileDialog.getExistingDirectory(None, tr("Select the catalogue folder"))
        if directory:
            logger.trace(f"Percorso selezionato: {directory}")
            app_settings.set(AppSettings.catalogue_path, Path(directory))
            self.view.card_general_catalogue.setContent(directory)
            self.dash_model.snap_catalogue.set_catalogue_path(Path(directory))
            log_action("Settings", "settings.catalogue.path.changed", directory)
            self.dash_model.update()
        else:
            logger.trace("Nessun percorso selezionato.")

    def __open_directory(self):
        import subprocess
        import platform

        path = app.path

        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def __clear_backup_directory(self):
        try:
            w = MessageBox(tr("Backup folder cleanup"), tr("Are you sure you want to clean the backup folder? This operation will delete all files in the backup folder."), parent=self.view)
            if  w.exec_():
                shutil.rmtree(PATH_BACKUPS)
                log_action("Settings", "settings.backup.cleaned", str(PATH_BACKUPS))
        except Exception as e:
            logger.error(f"Errore durante la pulizia della cartella di backup: {str(e)}")
            UiUtils.show_message(tr("Error"), tr("An error occurred while cleaning the backup folder: {error}", error=str(e)))
            return

    def __open_info_dialog(self):
        w = AboutMessageBox(QIcon(RESOURCE_ID_LOGO), app.name,app.version, self.view)
        if w.exec_():
            pass
