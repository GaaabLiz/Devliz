from pylizlib.core.os.snap import SnapshotCatalogue

from devliz.model.catalogue_seacher_model import CatalogueSearcherModel
from devliz.view.widgets.catalogue_searcher_view import CatalogueSearcherView


class CatalogueSearcherController:

    def __init__(self, catalogue: SnapshotCatalogue, parent=None):
        self.view = CatalogueSearcherView(parent)
        self.model = CatalogueSearcherModel(catalogue)

        # Connect view and model
        self.view.setModel(self.model.table_model)

        # Connect signals
        self.view.action_start.triggered.connect(self._perform_search)
        self.view.action_stop.triggered.connect(self._stop_search)
        self.view.signal_delete_requested.connect(self._on_delete_requested)

    def _on_delete_requested(self, row: int):
        """Handles the request to delete a snapshot from the table."""
        self.model.table_model.remove_snapshot(row)

    def _perform_search(self):
        """Triggers a search in the model."""
        self.view.set_operation_status(True)
        search_text = self.view.search_bar.text()
        search_type = self.view.get_selected_search_type()
        extensions = self.view.get_selected_extensions()

        # Toggle button states
        self.view.action_start.setEnabled(False)
        self.view.action_stop.setEnabled(True)

        self.model.search(search_text, search_type, extensions)

    def _stop_search(self):
        """Stops the search in the model."""
        self.view.set_operation_status(False)
        # In a real implementation, this would stop a background thread.
        self.model.stop_search()

        # Toggle button states
        self.view.action_start.setEnabled(True)
        self.view.action_stop.setEnabled(False)

    def open(self):
        self.model.load_snapshots_from_catalogue()
        self.view.exec_()