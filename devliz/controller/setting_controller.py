import os
import sys
from pathlib import Path

from PySide6.QtCore import QProcess, QUrl
from PySide6.QtGui import QIcon, QDesktopServices
from PySide6.QtWidgets import QFileDialog, QApplication
from pylizlib.qtfw.util.ui import UiUtils
from pylizlib.qtfw.widgets.dialog.about import AboutMessageBox
from qfluentwidgets import MessageBox

from devliz.application.app import app, RESOURCE_ID_LOGO
from devliz.application.i18n import tr
from devliz.model.dashboard import DashboardModel
from devliz.model.setting import SettingModel
from devliz.view.setting import WidgetSettings


class SettingController:
    """
    Controller for managing application settings.

    This controller handles interactions on the settings view, allowing the user
    to modify application configurations such as paths, language, theme, and more.
    It orchestrates the SettingModel and WidgetSettings by connecting their signals.
    """

    def __init__(self, dash_model: DashboardModel):
        """
        Initializes the SettingController.

        Args:
            dash_model (DashboardModel): The dashboard model, required to trigger UI updates
                and access the catalogue when settings change.
        """
        self.dash_model = dash_model
        
        # Instantiate Model and View
        self.model = SettingModel(dash_model)
        self.view = WidgetSettings()

        # Connections: View -> Controller/Model
        self.view.signal_request_update.connect(self.dash_model.update)
        self.view.signal_ask_catalogue_path.connect(self.__ask_catalogue_path)
        self.view.signal_ask_backup_path.connect(self.__ask_backup_path)
        self.view.signal_open_dir_request.connect(self.__open_directory)
        self.view.signal_clear_backups_request.connect(self.__clear_backup_directory)
        self.view.signal_open_about_dialog_request.connect(self.__open_info_dialog)
        self.view.signal_language_changed.connect(self.__on_language_or_theme_changed)
        self.view.signal_theme_changed.connect(self.__on_language_or_theme_changed)

        # Connections: Model -> View/Controller
        self.model.catalogue_path_updated.connect(self.__on_catalogue_path_updated)
        self.model.backup_path_updated.connect(self.__on_backup_path_updated)
        self.model.backup_cleared.connect(self.__on_backup_cleared)
        self.model.cleanup_failed.connect(self.__on_cleanup_failed)

    def __on_catalogue_path_updated(self, directory: str):
        self.view.update_catalogue_path(directory)

    def __on_backup_path_updated(self, directory: str):
        self.view.update_backup_path(directory)

    def __on_backup_cleared(self, deleted_count: int, backup_path: str):
        # We could notify the user via UI, but for now we mirror the old logic which just logs it in the model
        pass

    def __on_cleanup_failed(self, error_message: str):
        UiUtils.show_message(tr("Error"), tr("An error occurred while cleaning the backup folder: {error}", error=error_message))

    def __on_language_or_theme_changed(self):
        """
        Handles language or theme changes by prompting the user to restart the application.

        If confirmed, it logs the restart and restarts the application programmatically.
        """
        w = MessageBox(tr("Restart required"), tr("The application needs to restart to apply the changes. Restart now?"), parent=self.view)
        if w.exec_():
            self.model.log_restart_confirmed()
            args = sys.argv[:]
            args[0] = os.path.abspath(args[0])
            QProcess.startDetached(sys.executable, args)
            QApplication.instance().quit()

    def __ask_catalogue_path(self):
        """
        Opens a directory selection dialog to choose a new catalogue path.
        Delegates the logic to the model.
        """
        directory = QFileDialog.getExistingDirectory(None, tr("Select the catalogue folder"))
        if directory:
            self.model.set_catalogue_path(directory)

    def __ask_backup_path(self):
        """
        Opens a directory selection dialog to choose a new backup path.
        Delegates the logic to the model.
        """
        directory = QFileDialog.getExistingDirectory(None, tr("Select the backup folder"))
        if directory:
            self.model.set_backup_path(directory)

    def __open_directory(self):
        """
        Opens the application's internal configuration directory in the file explorer.
        """
        path = app.path
        if Path(path).exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def __clear_backup_directory(self):
        """
        Prompts the user for confirmation and then commands the model to delete 
        all application-managed backups.
        """
        w = MessageBox(
            tr("Backup folder cleanup"),
            tr(
                "Are you sure you want to delete all backups created by the application? "
                "Other files in the folder will be preserved."
            ),
            parent=self.view,
        )
        if not w.exec_():
            return
            
        self.model.clear_backup_directory()

    def __open_info_dialog(self):
        """
        Opens the 'About' dialog displaying application information and version details.
        """
        w = AboutMessageBox(QIcon(RESOURCE_ID_LOGO), app.name, app.version, self.view)
        if w.exec_():
            pass
