import sys
import types

def test_help_controller(monkeypatch):
    # Mock view
    view_mod = types.ModuleType("devliz.view.help")
    class FakeHelpView: pass
    view_mod.HelpView = FakeHelpView
    monkeypatch.setitem(sys.modules, "devliz.view.help", view_mod)
    
    sys.modules.pop("devliz.controller.help", None)
    from devliz.controller.help import HelpController
    
    ctrl = HelpController()
    assert isinstance(ctrl.view, FakeHelpView)

