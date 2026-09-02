from PySide6.QtCore import Qt
from devliz.view.action_history import ActionHistoryView
from devliz.model.action_history import ActionHistoryTableModel

def test_action_history_model():
    model = ActionHistoryTableModel()
    model.set_rows([
        {"timestamp": "2023-01-01", "category": "CAT", "action_key": "KEY", "details": "Det"}
    ])
    
    # Test valid parent
    valid_parent = model.index(0, 0)
    assert model.rowCount(valid_parent) == 0
    assert model.columnCount(valid_parent) == 0
    
    # Test header
    assert model.headerData(0, Qt.Orientation.Horizontal) == "Timestamp"
    assert model.headerData(0, Qt.Orientation.Vertical) is None
    
    # Test data
    assert model.data(model.index(0, 2)) == "KEY"
    assert model.data(model.index(0, 3)) == "Det"
    assert model.data(model.index(0, 0), Qt.ItemDataRole.ToolTipRole) is None

def test_action_history_view(qtbot):
    view = ActionHistoryView()
    qtbot.addWidget(view)
    
    view.update_rows([
        {"timestamp": "2023-01-01", "category": "CAT", "action_key": "KEY", "details": "Det"}
    ])
    
    assert view.model.rowCount() == 1
    
    # Hit col 99 for coverage
    class MockIndex:
        def isValid(self): return True
        def row(self): return 0
        def column(self): return 99
    
    assert view.model.data(MockIndex()) is None
