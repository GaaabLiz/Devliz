import os
from pathlib import Path

from PySide6.QtWidgets import QFileDialog
from loguru import logger
from pylizlib.core.os.snap import Snapshot
from pylizlib.qtfw.util.ui import UiUtils
from qfluentwidgets import MessageBox
from scipy.optimize import direct

from devliz.application.app import app, AppSettings, app_settings
from devliz.controller.catalogue_searcher import CatalogueSearcherController
from devliz.domain.data import DevlizSnapshotData
from devliz.model.catalogue import CatalogueModel
from devliz.model.dashboard import DashboardModel
from devliz.view.catalogue import SnapshotCatalogueWidget
from devliz.view.catalogue_imp_dialog import DialogConfig
from devliz.application.i18n import tr


class CatalogueController:

    def __init__(self,dash_model: DashboardModel):
        self.dash_model = dash_model
        self.model = CatalogueModel()
        self.view = SnapshotCatalogueWidget(self.model)


    def init(self):
        self.view.signal_import_requested.connect(lambda: self.__open_config_dialog(False, None))
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
                titolo = tr("Configuration created") if not edit_mode else tr("Configuration modified")
                testo = tr("The configuration has been created successfully.") if not edit_mode else tr("The configuration has been modified successfully.")
                UiUtils.show_message(titolo, testo)
                self.dash_model.update()
        except Exception as e:
            logger.error(str(e))
            UiUtils.show_message(tr("Error"), tr("An error occurred: {error}", error=str(e)))

    def __open_snapshot_searcher(self):
        controller = CatalogueSearcherController(self.dash_model.snap_catalogue, self.view)
        controller.open()

    def __open_snapshot_searcher_single(self, snapshot: Snapshot):
        controller = CatalogueSearcherController(self.dash_model.snap_catalogue, self.view)
        controller.open(snapshot=snapshot)

    def __install_snapshot(self, snap: Snapshot):
        try:
            w = MessageBox(tr("Install configuration"), tr("Are you sure you want to install the selected snapshot? All current directories will be replaced with those contained in the snapshot."), parent=self.view)
            if w.exec_():
                if app_settings.get(AppSettings.clear_snap_attached_folders_before_install):
                    self.dash_model.snap_catalogue.remove_installed_copies(snap.id)
                self.dash_model.snap_catalogue.install(snap)
                self.dash_model.update()
        except Exception as e:
            UiUtils.show_message(tr("Installation error"), tr("An error occurred during installation: {error}", error=str(e)))

    def __edit_snapshot(self, snap: Snapshot):
        try:
            self.__open_config_dialog(True, snap)
        except Exception as e:
            UiUtils.show_message(tr("Edit error"), tr("An error occurred during editing: {error}", error=str(e)))

    def __delete_snapshot(self, snap: Snapshot):
        try:
            w = MessageBox(tr("Delete configuration"), tr("Are you sure you want to delete the selected snapshot?\n\nAll associated files will be deleted in "), parent=self.view)
            if w.exec_():
                self.dash_model.snap_catalogue.delete(snap)
                self.dash_model.update()
        except Exception as e:
            UiUtils.show_message(tr("Deletion error"), tr("An error occurred during deletion: {error}", error=str(e)))

    def __open_snap_directory(self, snap: Snapshot):
        path = self.dash_model.snap_catalogue.get_snap_directory_path(snap)
        self.__open_directory(path)

    def __duplicate_snapshot(self, snap: Snapshot):
        try:
            w = MessageBox(tr("Duplicate configuration"), tr("Are you sure you want to duplicate the selected configuration?"), parent=self.view)
            if w.exec_():
                self.dash_model.snap_catalogue.duplicate_by_id(snap.id)
                self.dash_model.update()
        except Exception as e:
            UiUtils.show_message(tr("Duplication error"), tr("An error occurred during duplication: {error}", error=str(e)))

    def __export_snapshot(self, snap: Snapshot):
        try:
            w = MessageBox(tr("Export snapshot"), tr("Are you sure you want to export the selected snapshot?"), parent=self.view)
            if w.exec_():
                directory = QFileDialog.getExistingDirectory(
                    None,
                    tr("Select the save folder for the snapshot"),
                    app.path.__str__()
                )
                if directory:
                    self.dash_model.snap_catalogue.export_snapshot(snap.id, Path(directory))
        except Exception as e:
            UiUtils.show_message(tr("Export error"), tr("An error occurred during export: {error}", error=str(e)))

    def __export_snapshot_folders(self, snap: Snapshot):
        try:
            w = MessageBox(tr("Export associated folders"), tr("Are you sure you want to export the folders associated with the selected snapshot?"), parent=self.view)
            if w.exec_():
                directory = QFileDialog.getExistingDirectory(
                    None,
                    tr("Select the save folder for the associated folders"),
                    app.path.__str__()
                )
                if directory:
                    self.dash_model.snap_catalogue.export_assoc_dirs(snap.id, Path(directory))
        except Exception as e:
            UiUtils.show_message(tr("Export error"), tr("An error occurred during export: {error}", error=str(e)))

    def __delete_snap_installed_dirs(self, snap: Snapshot):
        try:
            w = MessageBox(tr("Delete installed folders"), tr("Are you sure you want to delete the currently installed folders for the selected snapshot?"), parent=self.view)
            if w.exec_():
                self.dash_model.snap_catalogue.remove_installed_copies(snap.id)
        except Exception as e:
            UiUtils.show_message(tr("Deletion error"), tr("An error occurred during deletion: {error}", error=str(e)))

    def __update_assoc_dirs_from_installed(self, snap: Snapshot):
        try:
            w = MessageBox(tr("Update associated folders"), tr("Are you sure you want to update the associated folders of the selected snapshot with the currently installed ones?"), parent=self.view)
            if w.exec_():
                self.dash_model.snap_catalogue.update_assoc_with_installed(snap.id)
        except Exception as e:
            UiUtils.show_message(tr("Update error"), tr("An error occurred during update: {error}", error=str(e)))

    def __open_directory(self, path: Path):
        if path.exists():
            os.startfile(path)
        else:
            UiUtils.show_message(tr("Warning"), tr("The folder no longer exists in {path}", path=path.__str__()))
