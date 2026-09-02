from pathlib import Path

from PySide6.QtWidgets import QFileDialog
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl
from loguru import logger
from pylizlib.core.os.snap import Snapshot
from pylizlib.qtfw.util.ui import UiUtils
from qfluentwidgets import MessageBox

from devliz.application.app import app, AppSettings, app_settings
from devliz.model.action_history import log_action, ActionCategory, ActionType
from devliz.domain.data import DevlizSnapshotData
from devliz.model.catalogue import CatalogueModel
from devliz.model.dashboard import DashboardModel
from devliz.view.catalogue import SnapshotCatalogueWidget
from devliz.view.catalogue_imp_dialog import DialogConfig
from devliz.application.i18n import tr


class CatalogueController:

    def __init__(self, dash_model: DashboardModel, search_page_opener=None):
        self.dash_model = dash_model
        self.model = CatalogueModel()
        self.view = SnapshotCatalogueWidget(self.model)
        self.search_page_opener = search_page_opener


    def init(self):
        self.view.signal_import_requested.connect(lambda: self.__open_config_dialog(False, None))
        self.view.signal_open_catalogue_folder_requested.connect(self.__open_catalogue_directory)
        self.view.signal_install_requested.connect(self.__install_snapshot)
        self.view.signal_edit_requested.connect(self.__edit_snapshot)
        self.view.signal_delete_requested.connect(self.__delete_snapshot)
        self.view.signal_open_folder_requested.connect(self.__open_snap_directory)
        self.view.signal_duplicate_requested.connect(self.__duplicate_snapshot)
        self.view.signal_sort_requested.connect(self.view.sort)
        self.view.signal_search_internal_content_all.connect(self.__open_snapshot_searcher)
        self.view.signal_search_internal_content_single.connect(self.__open_snapshot_searcher_single)
        self.view.signal_export_request_snapshot.connect(self.__export_snapshot)
        self.view.signal_export_request_assoc_folders.connect(self.__export_snapshot_folders)
        self.view.signal_delete_installed_folders_requested.connect(self.__delete_snap_installed_dirs)
        self.view.signal_update_with_local_dirs_requested.connect(self.__update_assoc_dirs_from_installed)
        self.view.signal_open_assoc_folder_requested.connect(self.__open_directory)

    def update_data(self, snapshot_data: DevlizSnapshotData):
        self.model.set_snapshots(snapshot_data.snapshot_list)
        self.model.table_model.update_headers()
        self.view.reload_data()

    def __open_config_dialog(self, edit_mode: bool, snap: Snapshot | None = None):
        log_action(ActionCategory.CATALOGUE, ActionType.CATALOGUE_CONFIG_DIALOG_OPENED, "edit" if edit_mode else "create")
        dialog = DialogConfig(self.dash_model.cached_data, edit_mode, snap)
        try:
            if dialog.exec():
                print(dialog.output_data)
                if edit_mode:
                    op_name = tr("Modify configuration")
                    op_desc = tr("Modifying configuration")
                    
                    def action(task):
                        old = snap
                        new = dialog.output_data
                        self.dash_model.snap_catalogue.update_snapshot_by_objs(old, new, message_callback=task.update_task_message)
                        log_action(ActionCategory.CATALOGUE, ActionType.CATALOGUE_SNAPSHOT_UPDATED, new.name)
                        
                    titolo = tr("Configuration modified")
                    testo = tr("The configuration has been modified successfully.")
                else:
                    op_name = tr("Create configuration")
                    op_desc = tr("Creating configuration")
                    
                    def action(task):
                        self.dash_model.snap_catalogue.add(dialog.output_data, progress_callback=task.update_task_progress, message_callback=task.update_task_message)
                        log_action(ActionCategory.CATALOGUE, ActionType.CATALOGUE_SNAPSHOT_CREATED, dialog.output_data.name)
                        
                    titolo = tr("Configuration created")
                    testo = tr("The configuration has been created successfully.")
                
                self.dash_model.run_heavy_operation(
                    op_name, op_desc, action, 
                    success_msg_title=titolo, success_msg=testo, update_dashboard=True
                )
        except Exception as e:
            logger.error(f"Error executing dialog: {e}")

    def __open_snapshot_searcher(self):
        if self.search_page_opener:
            self.search_page_opener(None)

    def __open_snapshot_searcher_single(self, snapshot: Snapshot):
        if self.search_page_opener:
            self.search_page_opener(snapshot)

    def __install_snapshot(self, snap: Snapshot):
        logger.debug(f"Installation requested for {snap.name}")
        try:
            w = MessageBox(tr("Install configuration"), tr("Are you sure you want to install the selected snapshot? All current directories will be replaced with those contained in the snapshot."), parent=self.view)
            if w.exec_():
                def action(task):
                    clear_dest = app_settings.get(AppSettings.clear_snap_attached_folders_before_install)
                    self.dash_model.snap_catalogue.install(snap, clear_destination=clear_dest, progress_callback=task.update_task_progress, message_callback=task.update_task_message)
                    logger.info(f"Configuration installation {snap.name} completed.")
                    log_action(ActionCategory.CATALOGUE, ActionType.CATALOGUE_SNAPSHOT_INSTALLED, snap.name)
                
                self.dash_model.run_heavy_operation(
                    tr("Install configuration"),
                    tr("Installing configuration"),
                    action,
                    success_msg_title=tr("Configuration installed"),
                    success_msg=tr("The configuration has been installed successfully."),
                    update_dashboard=True
                )
        except Exception as e:
            logger.error(f"Error during install process: {e}")

    def __edit_snapshot(self, snap: Snapshot):
        try:
            self.__open_config_dialog(True, snap)
        except Exception as e:
            UiUtils.show_message(tr("Edit error"), tr("An error occurred during editing: {error}", error=str(e)))

    def __delete_snapshot(self, snap: Snapshot):
        logger.debug(f"Deletion requested for {snap.name}")
        try:
            w = MessageBox(tr("Delete configuration"), tr("Are you sure you want to delete the selected configuration? This operation cannot be undone."), parent=self.view)
            if w.exec_():
                def action(task):
                    self.dash_model.snap_catalogue.delete(snap, message_callback=task.update_task_message)
                    logger.info(f"Configuration deletion {snap.name} completed.")
                    log_action(ActionCategory.CATALOGUE, ActionType.CATALOGUE_SNAPSHOT_DELETED, snap.name)
                
                self.dash_model.run_heavy_operation(
                    tr("Delete configuration"),
                    tr("Deleting configuration"),
                    action,
                    success_msg_title=tr("Configuration deleted"),
                    success_msg=tr("The configuration has been deleted successfully."),
                    update_dashboard=True
                )
        except Exception as e:
            logger.error(f"Error during delete process: {e}")

    def __open_snap_directory(self, snap: Snapshot):
        path = self.dash_model.snap_catalogue.get_snap_directory_path(snap)
        self.__open_directory(path)

    def __duplicate_snapshot(self, snap: Snapshot):
        logger.debug(f"Duplication requested for {snap.name}")
        try:
            def action(task):
                self.dash_model.snap_catalogue.duplicate_by_id(snap.id, message_callback=task.update_task_message)
                logger.info(f"Configuration duplication {snap.name} completed.")
                log_action(ActionCategory.CATALOGUE, ActionType.CATALOGUE_SNAPSHOT_DUPLICATED, snap.name)
            
            self.dash_model.run_heavy_operation(
                tr("Duplicate configuration"),
                tr("Duplicating configuration"),
                action,
                success_msg_title=tr("Configuration duplicated"),
                success_msg=tr("The configuration has been duplicated successfully."),
                update_dashboard=True
            )
        except Exception as e:
            logger.error(f"Error during duplicate process: {e}")

    def __execute_export(
            self,
            snap: Snapshot,
            msg_box_title: str,
            msg_box_text: str,
            file_dialog_text: str,
            export_method,
            action_type: ActionType,
            log_prefix: str,
            op_title: str,
            op_desc: str
    ):
        logger.debug(f"{log_prefix} requested for {snap.name}")
        try:
            w = MessageBox(msg_box_title, msg_box_text, parent=self.view)
            if w.exec_():
                directory = QFileDialog.getExistingDirectory(
                    None,
                    file_dialog_text,
                    app.path.__str__()
                )
                if directory:
                    def action(task):
                        export_method(snap.id, Path(directory), message_callback=task.update_task_message)
                        logger.info(f"{log_prefix} of {snap.name} to {directory} completed.")
                        log_action(ActionCategory.CATALOGUE, action_type, f"{snap.name} -> {directory}")
                    
                    self.dash_model.run_heavy_operation(
                        op_title,
                        op_desc,
                        action,
                        success_msg_title="", success_msg="", update_dashboard=False
                    )
        except Exception as e:
            UiUtils.show_message(tr("Export error"), tr("An error occurred during export: {error}", error=str(e)))

    def __export_snapshot(self, snap: Snapshot):
        self.__execute_export(
            snap,
            msg_box_title=tr("Export snapshot"),
            msg_box_text=tr("Are you sure you want to export the selected snapshot?"),
            file_dialog_text=tr("Select the save folder for the snapshot"),
            export_method=self.dash_model.snap_catalogue.export_snapshot,
            action_type=ActionType.CATALOGUE_SNAPSHOT_EXPORTED,
            log_prefix="Export",
            op_title=tr("Export snapshot"),
            op_desc=tr("Exporting snapshot")
        )

    def __export_snapshot_folders(self, snap: Snapshot):
        self.__execute_export(
            snap,
            msg_box_title=tr("Export associated folders"),
            msg_box_text=tr("Are you sure you want to export the folders associated with the selected snapshot?"),
            file_dialog_text=tr("Select the save folder for the associated folders"),
            export_method=self.dash_model.snap_catalogue.export_assoc_dirs,
            action_type=ActionType.CATALOGUE_ASSOCIATED_FOLDERS_EXPORTED,
            log_prefix="Folder export",
            op_title=tr("Export associated folders"),
            op_desc=tr("Exporting folders")
        )

    def __delete_snap_installed_dirs(self, snap: Snapshot):
        logger.debug(f"Installed folders deletion requested for {snap.name}")
        try:
            w = MessageBox(tr("Delete installed folders"), tr("Are you sure you want to delete the currently installed folders for the selected snapshot?"), parent=self.view)
            if w.exec_():
                def action(task):
                    self.dash_model.snap_catalogue.remove_installed_copies(snap.id, message_callback=task.update_task_message)
                    logger.info(f"Installed folders deletion for {snap.name} completed.")
                    log_action(ActionCategory.CATALOGUE, ActionType.CATALOGUE_INSTALLED_FOLDERS_DELETED, snap.name)
                
                self.dash_model.run_heavy_operation(
                    tr("Delete installed folders"),
                    tr("Deleting folders"),
                    action,
                    success_msg_title="", success_msg="", update_dashboard=False
                )
        except Exception as e:
            UiUtils.show_message(tr("Deletion error"), tr("An error occurred during deletion: {error}", error=str(e)))

    def __update_assoc_dirs_from_installed(self, snap: Snapshot):
        logger.debug(f"Associated folders update requested for {snap.name}")
        try:
            w = MessageBox(tr("Update associated folders"), tr("Are you sure you want to update the associated folders of the selected snapshot with the currently installed ones?"), parent=self.view)
            if w.exec_():
                def action(task):
                    self.dash_model.snap_catalogue.update_assoc_with_installed(snap.id, message_callback=task.update_task_message)
                    logger.info(f"Associated folders update for {snap.name} completed.")
                    log_action(ActionCategory.CATALOGUE, ActionType.CATALOGUE_ASSOCIATED_FOLDERS_UPDATED, snap.name)
                
                self.dash_model.run_heavy_operation(
                    tr("Update associated folders"),
                    tr("Updating folders"),
                    action,
                    success_msg_title="", success_msg="", update_dashboard=False
                )
        except Exception as e:
            UiUtils.show_message(tr("Update error"), tr("An error occurred during update: {error}", error=str(e)))

    def __open_catalogue_directory(self):
        path = app_settings.get(AppSettings.catalogue_path)
        self.__open_directory(Path(path))

    def __open_directory(self, path: Path):
        logger.debug(f"Opening directory {path}")
        if path.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
        else:
            UiUtils.show_message(tr("Warning"), tr("The folder no longer exists in {path}", path=path.__str__()))
