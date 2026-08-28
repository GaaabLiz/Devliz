import platform
import subprocess
from pathlib import Path

from PySide6.QtCore import Signal, QObject
from loguru import logger
from pylizlib.core.os.snap import SnapshotCatalogue
from pylizlib.core.os.snap.domain import SnapshotBackupInfo
from pylizlib.qtfw.util.ui import UiUtils
from qfluentwidgets import MessageBox

from devliz.application.app import app_settings, AppSettings
from devliz.application.action_history import log_action, ActionCategory, ActionType
from devliz.application.i18n import tr
from devliz.model.backup import BackupModel
from devliz.view.backup import BackupView


class BackupController(QObject):

    signal_request_refresh = Signal()

    def __init__(self, snap_catalogue: SnapshotCatalogue):
        super().__init__()
        self.snap_catalogue = snap_catalogue
        self.model = BackupModel()
        self.view = BackupView(self.model)

        self.view.signal_open_requested.connect(self.__handle_open)
        self.view.signal_restore_requested.connect(self.__handle_restore)
        self.view.signal_delete_requested.connect(self.__handle_delete)

    def update_data(self):
        backup_path = Path(app_settings.get(AppSettings.backup_path))
        self.model.load_backups(self.snap_catalogue, backup_path)
        self.view.reload_data()

    def __handle_open(self, backup: SnapshotBackupInfo):
        folder = backup.path.parent
        try:
            from pylizlib.core.os.utils import open_system_folder
            open_system_folder(str(folder))
            log_action(ActionCategory.BACKUPS, ActionType.BACKUP_OPENED_IN_FINDER, backup.file_name)
        except Exception as e:
            logger.error(f"Error opening backup folder: {e}")

    def __handle_restore(self, backup: SnapshotBackupInfo):
        w = MessageBox(
            tr("Confirm Restore"),
            tr("Are you sure you want to restore this backup? This will overwrite current data."),
            parent=self.view
        )
        if not w.exec_():
            return
        try:
            self.snap_catalogue.restore_backup(backup.path)
            log_action(ActionCategory.BACKUPS, ActionType.BACKUP_RESTORED, backup.file_name)
            self.update_data()
            self.signal_request_refresh.emit()
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            UiUtils.show_message(tr("Error"), tr("An error occurred during restore: {error}", error=str(e)))

    def __handle_delete(self, backup: SnapshotBackupInfo):
        w = MessageBox(
            tr("Confirm Delete"),
            tr("Are you sure you want to delete this backup? This action cannot be undone."),
            parent=self.view
        )
        if not w.exec_():
            return
        try:
            self.snap_catalogue.delete_backup(backup.path)
            log_action(ActionCategory.BACKUPS, ActionType.BACKUP_DELETED, backup.file_name)
            self.update_data()
        except Exception as e:
            logger.error(f"Error deleting backup: {e}")
            UiUtils.show_message(tr("Error"), tr("An error occurred during deletion: {error}", error=str(e)))
