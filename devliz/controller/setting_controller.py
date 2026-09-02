import os
import sys
from pathlib import Path

from PySide6.QtCore import QProcess, QUrl
from PySide6.QtGui import QIcon, QDesktopServices
from PySide6.QtWidgets import QFileDialog, QApplication
from loguru import logger
from pylizlib.core.os.snap.domain import BackupType
from pylizlib.qtfw.util.ui import UiUtils
from pylizlib.qtfw.widgets.dialog.about import AboutMessageBox
from qfluentwidgets import MessageBox

from devliz.application.app import app_settings, AppSettings, RESOURCE_ID_LOGO, app, snap_settings
from devliz.model.action_history import log_action, ActionCategory, ActionType
from devliz.application.i18n import tr
from devliz.model.dashboard import DashboardModel
from devliz.view.setting import WidgetSettings


class SettingController:

    def __init__(self, dash_model: DashboardModel):
        self.view = WidgetSettings()
        self.dash_model = dash_model

        self.view.signal_request_update.connect(self.dash_model.update)
        self.view.signal_ask_catalogue_path.connect(self.__ask_catalogue_path)
        self.view.signal_ask_backup_path.connect(self.__ask_backup_path)
        self.view.signal_open_dir_request.connect(self.__open_directory)
        self.view.signal_clear_backups_request.connect(self.__clear_backup_directory)
        self.view.signal_open_about_dialog_request.connect(self.__open_info_dialog)
        self.view.signal_language_changed.connect(self.__on_language_or_theme_changed)
        self.view.signal_theme_changed.connect(self.__on_language_or_theme_changed)

        # Sync snap_settings reactively
        AppSettings.backup_path.valueChanged.connect(self.__sync_snap_settings)
        AppSettings.backup_before_install.valueChanged.connect(self.__sync_snap_settings)
        AppSettings.backup_before_edit.valueChanged.connect(self.__sync_snap_settings)
        AppSettings.backup_before_delete.valueChanged.connect(self.__sync_snap_settings)

    def __sync_snap_settings(self, *args, **kwargs):
        snap_settings.backup_path = Path(app_settings.get(AppSettings.backup_path))
        snap_settings.backup_pre_install = app_settings.get(AppSettings.backup_before_install)
        snap_settings.backup_pre_modify = app_settings.get(AppSettings.backup_before_edit)
        snap_settings.backup_pre_delete = app_settings.get(AppSettings.backup_before_delete)

    def __on_language_or_theme_changed(self):
        w = MessageBox(tr("Restart required"), tr("The application needs to restart to apply the changes. Restart now?"), parent=self.view)
        if w.exec_():
            logger.info("User confirmed restart for language/theme change")
            log_action(ActionCategory.SETTINGS, ActionType.SETTINGS_RESTART_CONFIRMED, "theme/language change")
            args = sys.argv[:]
            args[0] = os.path.abspath(args[0])
            QProcess.startDetached(sys.executable, args)
            QApplication.instance().quit()

    def __ask_catalogue_path(self):
        directory = QFileDialog.getExistingDirectory(None, tr("Select the catalogue folder"))
        if directory:
            logger.info(f"Catalogue path changed to: {directory}")
            app_settings.set(AppSettings.catalogue_path, Path(directory))
            self.view.card_general_catalogue.setContent(directory)
            self.dash_model.snap_catalogue.set_catalogue_path(Path(directory))
            log_action(ActionCategory.SETTINGS, ActionType.SETTINGS_CATALOGUE_PATH_CHANGED, directory)
            self.dash_model.update()
        else:
            logger.debug("Catalogue path selection cancelled.")

    def __ask_backup_path(self):
        directory = QFileDialog.getExistingDirectory(None, tr("Select the backup folder"))
        if directory:
            logger.info(f"Backup path changed to: {directory}")
            backup_path = Path(directory)
            app_settings.set(AppSettings.backup_path, backup_path)
            snap_settings.backup_path = backup_path
            self.view.card_backup_path.setContent(directory)
            log_action(ActionCategory.SETTINGS, ActionType.SETTINGS_BACKUP_PATH_CHANGED, directory)
        else:
            logger.debug("Backup path selection cancelled.")

    def __open_directory(self):
        path = app.path
        logger.debug(f"Opening app directory: {path}")
        if Path(path).exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def __clear_backup_directory(self):
        try:
            w = MessageBox(
                tr("Backup folder cleanup"),
                tr(
                    "Are you sure you want to delete all backups created by the application? "
                    "Other files in the folder will be preserved."
                ),
                parent=self.view,
            )
            if not w.exec_():
                logger.debug("Backup directory cleanup cancelled by user.")
                return

            backup_path = Path(app_settings.get(AppSettings.backup_path))
            deleted_count = 0

            if backup_path.exists():
                if not backup_path.is_dir():
                    raise ValueError(
                        f"Configured backup path '{backup_path}' is not a directory."
                    )

                managed_types = (
                    BackupType.ASSOCIATED_DIRECTORIES,
                    BackupType.SNAPSHOT_DIRECTORY,
                )
                for backup in self.dash_model.snap_catalogue.list_backups(backup_path):
                    if backup.is_export or backup.backup_type not in managed_types:
                        continue
                    self.dash_model.snap_catalogue.delete_backup(backup.path)
                    deleted_count += 1

            logger.info(
                "Backup directory cleanup completed: {} file(s) deleted from {}",
                deleted_count,
                backup_path,
            )
            log_action(
                ActionCategory.SETTINGS,
                ActionType.SETTINGS_BACKUP_CLEANED,
                f"path={backup_path}; deleted={deleted_count}",
            )
        except (OSError, ValueError) as e:
            logger.error(f"Error during backup folder cleanup: {str(e)}")
            UiUtils.show_message(tr("Error"), tr("An error occurred while cleaning the backup folder: {error}", error=str(e)))
            return

    def __open_info_dialog(self):
        w = AboutMessageBox(QIcon(RESOURCE_ID_LOGO), app.name,app.version, self.view)
        if w.exec_():
            pass
