import shutil
import sys
import types

def test_home_controller(monkeypatch, tmp_path):
    # Mock view
    view_mod = types.ModuleType("devliz.view.home")
    updated = []
    class FakeHomeView:
        def update_statistics(self, stats, backup_count, catalogue_path):
            updated.append((stats, backup_count, catalogue_path))
    view_mod.HomeView = FakeHomeView
    monkeypatch.setitem(sys.modules, "devliz.view.home", view_mod)
    
    # Mock app_settings
    app_mod = types.ModuleType("devliz.application.app")
    class ASK: backup_path="b"; catalogue_path="c"
    
    # create fake backup path with 2 zips
    b_path = tmp_path / "backups"
    b_path.mkdir()
    (b_path / "1.zip").touch()
    (b_path / "2.zip").touch()
    (b_path / "3.txt").touch()
    
    class AS:
        def get(self, k):
            if k == "b": return str(b_path)
            if k == "c": return "/cat"
    app_mod.AppSettings = ASK
    app_mod.app_settings = AS()
    app_mod.PATH_BACKUPS = "/backups"
    monkeypatch.setitem(sys.modules, "devliz.application.app", app_mod)
    
    sys.modules.pop("devliz.controller.home", None)
    from devliz.controller.home import HomeController
    
    ctrl = HomeController()
    
    class FakeStats: pass
    class FakeSnapData:
        def compute_home_statistics(self): return FakeStats
        
    ctrl.update_data(FakeSnapData())
    
    assert len(updated) == 1
    assert updated[0][0] == FakeStats
    assert updated[0][1] == 2
    assert updated[0][2] == "/cat"
    
    # test backup_path not exists
    shutil.rmtree(b_path)
    ctrl.update_data(FakeSnapData())
    assert updated[-1][1] == 0

