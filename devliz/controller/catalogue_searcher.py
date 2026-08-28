import os
import sys
import subprocess

from qfluentwidgets import MessageBox
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl

from loguru import logger
from pylizlib.core.os.snap import SnapshotCatalogue, Snapshot

from devliz.application.action_history import log_action, ActionCategory, ActionType
from devliz.model.catalogue_searcher import CatalogueSearcherModel
from devliz.view.catalogue_searcher import CatalogueSearcherView
from devliz.application.i18n import tr

class CatalogueSearcherController:
    """
    Controller for the catalogue searcher component.

    This class connects the CatalogueSearcherView (the UI) with the
    CatalogueSearcherModel (the business logic and data). It handles user
    interactions from the view and invokes the corresponding actions in the model.
    """

    def __init__(self, catalogue: SnapshotCatalogue, parent=None):
        """
        Initializes the CatalogueSearcherController.

        Args:
            catalogue (SnapshotCatalogue): The catalogue data source.
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        self.view = CatalogueSearcherView(parent)
        self.model = CatalogueSearcherModel(catalogue)

        # Connect view and model
        self.view.setModel(self.model.table_model)
        self.view.tree_view.setModel(self.model.tree_model_manager.model)

        # Connect signals
        self.model.signal_search_finished.connect(self._on_search_finished)
        self.view.action_start.triggered.connect(self._perform_search)
        self.view.action_stop.triggered.connect(self._stop_search)
        self.view.signal_delete_requested.connect(self._on_delete_requested)
        self.view.signal_file_double_clicked.connect(self._on_file_double_clicked)
        self.view.signal_tree_open_parent_folder.connect(self._on_tree_open_parent_folder)

        # Connect the status card update signal directly to the view's slot
        self.model.signal_status_card_update.connect(self.view.update_status_card)

    def _on_delete_requested(self, row: int):
        """
        Handles the request to delete a snapshot from the search table.

        Args:
            row (int): The row index of the snapshot to remove.
        """
        logger.debug(f"Removing row {row} from search results")
        self.model.table_model.remove_snapshot(row)
        log_action(ActionCategory.SEARCH, ActionType.SEARCH_SNAPSHOT_REMOVED, f"row={row}")

    def _on_file_double_clicked(self, file_path: str):
        """
        Handles the double-click event on a file in the results tree.
        Attempts to open the file with the default system application.

        Args:
            file_path (str): The path to the file to open.
        """
        logger.info(f"Opening file in search results: {file_path}")
        if os.path.isfile(file_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
        elif os.path.isdir(file_path):
            logger.warning(f"Cannot open directory in _on_file_double_clicked: {file_path}")

    def _on_tree_open_parent_folder(self, file_path: str):
        """
        Handles the context menu action to open the parent folder of a file.

        Args:
            file_path (str): The path to the file whose parent folder should be opened.
        """
        logger.info(f"Opening parent folder for file {file_path}")
        parent_dir = os.path.dirname(file_path)
        if os.path.exists(parent_dir):
            QDesktopServices.openUrl(QUrl.fromLocalFile(parent_dir))

    def _perform_search(self):
        """
        Gathers search parameters from the view and triggers a search in the model.
        """
        search_text = self.view.search_bar.text()
        if not search_text.strip():
            m = MessageBox(
                tr("Missing text"),
                tr("Please enter a text before starting the search."),
                self.view
            )
            m.exec()
            return

        self.view.set_operation_status(True)
        query_type = self.view.get_selected_query_type()
        search_target = self.view.get_selected_search_target()
        extensions = self.view.get_selected_extensions()

        # Toggle button states
        self.view.action_start.setEnabled(False)
        self.view.action_stop.setEnabled(True)

        logger.info(f"Starting search: text='{search_text}', type={query_type}, target={search_target}")
        self.model.search(search_text, query_type, search_target, extensions)
        log_action(ActionCategory.SEARCH, ActionType.SEARCH_STARTED, f"query={search_text}")

    def _stop_search(self):
        """Stops the search operation in the model and updates the UI state."""
        self.view.set_operation_status(False)
        logger.info("Search interrupted by user")
        self.model.stop_search()

        # Toggle button states
        self.view.action_start.setEnabled(True)
        self.view.action_stop.setEnabled(False)
        logger.info("Search completed")
        log_action(ActionCategory.SEARCH, ActionType.SEARCH_STOPPED, "")

    def _on_search_finished(self):
        """Handles the completion of the search operation by updating the UI state."""
        self.view.set_operation_status(False)
        self.view.action_start.setEnabled(True)
        self.view.action_stop.setEnabled(False)
        logger.info("Search completed")
        log_action(ActionCategory.SEARCH, ActionType.SEARCH_COMPLETED, "")

    def open(self, snapshot: Snapshot | None = None):
        """
        Loads snapshots into the search page.

        If a snapshot is provided, the page is scoped to that snapshot only.
        Otherwise it shows all snapshots.

        Args:
            snapshot (Snapshot | None, optional): A specific snapshot to load,
                                                  or None to load all. Defaults to None.
        """
        logger.debug(f"Opening search page with snapshot_scope={snapshot.name if snapshot else 'ALL'}")
        self.model.load_snapshots_from_catalogue(snapshot)