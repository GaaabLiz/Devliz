import pytest
from PySide6.QtCore import Qt, QPoint
from devliz.view.catalogue import SnapshotCatalogueWidget
from pylizlib.core.os.snap import SnapshotSortKey
from qfluentwidgets import Action

def test_catalogue_view(qtbot):
    from PySide6.QtGui import QStandardItemModel
    class DummyModel:
        def get_all_snapshots(self): return []
        def filter(self, *args): pass
        table_model = QStandardItemModel()
    view = SnapshotCatalogueWidget(DummyModel())
    qtbot.addWidget(view)
    
    # Sort Type changed
    view._on_sort_type_changed(SnapshotSortKey.NAME)
    assert view._current_sort_key == SnapshotSortKey.NAME
    
    # Sort Direction changed
    view._on_sort_direction_changed(True)
    assert view._current_sort_reverse == True
    
    # Selection changed
    view.table.clearSelection()
    view._on_item_selection_changed()
    assert view.action_edit.isEnabled() == False
    

