import sys
import types

def test_action_history_controller(monkeypatch):
    # Mock view
    view_mod = types.ModuleType("devliz.view.action_history")
    class FakeActionHistoryView:
        def __init__(self):
            self.rows = []
        def update_rows(self, rows):
            self.rows = rows
    view_mod.ActionHistoryView = FakeActionHistoryView
    monkeypatch.setitem(sys.modules, "devliz.view.action_history", view_mod)
    
    # Mock list_actions
    app_history_mod = types.ModuleType("devliz.application.action_history")
    app_history_mod.list_actions = lambda: ["action1", "action2"]
    monkeypatch.setitem(sys.modules, "devliz.application.action_history", app_history_mod)
    
    # Import
    sys.modules.pop("devliz.controller.action_history", None)
    import devliz.controller.action_history as c
    
    controller = c.ActionHistoryController()
    controller.reload()
    
    assert controller.view.rows == ["action1", "action2"]
