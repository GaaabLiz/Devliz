import pytest
from PySide6.QtCore import Qt, QPoint
from devliz.view.catalogue_imp_tab_directories import TabDirectories
from pylizlib.core.os.snap import Snapshot, SnapDirAssociation
from pathlib import Path

def test_tab_directories(qtbot, monkeypatch):
    snap = Snapshot(id="1", name="n", desc="d", directories=[SnapDirAssociation("/tmp/dir1", "fid", 0)])
    tab = TabDirectories(payload_data=snap, starred_dirs=["/tmp/dir2"])
    qtbot.addWidget(tab)
    
    assert tab.listWidget.count() == 1
    
    # Test checking if directories changed
    assert tab._check_directories_changed() is None
    tab.add_directory(Path("/tmp/dir3"), execute_checks=False)
    assert tab._check_directories_changed() is None  # it emits signal internally
    
    # Test context menu deletion
    import devliz.view.catalogue_imp_tab_directories
    class FakeRoundMenu:
        def __init__(self, parent=None): self.acts = []
        def addAction(self, a): self.acts.append(a)
        def exec(self, pos):
            for a in self.acts: a.trigger()
    monkeypatch.setattr(devliz.view.catalogue_imp_tab_directories, "RoundMenu", FakeRoundMenu)
    
    tab._TabDirectories__show_context_menu(QPoint(0,0))
    # It deletes selected item if one is selected, but let's mock itemAt
    item = tab.listWidget.item(0)
    tab.listWidget.setCurrentItem(item)
    monkeypatch.setattr(tab.listWidget, "itemAt", lambda pos: item)
    tab._TabDirectories__show_context_menu(QPoint(0,0))
    
    # Test add directory via dialog
    class FakeQFileDialog:
        @classmethod
        def getExistingDirectory(cls, *args): return "/tmp/dir4"
    monkeypatch.setattr(devliz.view.catalogue_imp_tab_directories, "QFileDialog", FakeQFileDialog)
    
    # mock exists
    monkeypatch.setattr(Path, "exists", lambda self: True)
    monkeypatch.setattr(Path, "is_dir", lambda self: True)
    
    tab._TabDirectories__on_add_directory_request()
    
    # Try empty path
    class FakeQFileDialogEmpty:
        @classmethod
        def getExistingDirectory(cls, *args): return ""
    monkeypatch.setattr(devliz.view.catalogue_imp_tab_directories, "QFileDialog", FakeQFileDialogEmpty)
    tab._TabDirectories__on_add_directory_request()
