from devliz.view.catalogue_searcher import CatalogueSearcherView

def test_catalogue_searcher_view(qtbot):
    view = CatalogueSearcherView()
    qtbot.addWidget(view)
    
    class DummySnap:
        def __init__(self, id, name):
            self.id = id
            self.name = name
    view.update_snapshot_menu([DummySnap("id1", "snap1"), DummySnap("id2", "snap2")], [])
    assert len(view.snapshot_menu.actions()) == 3  # All, snap1, snap2
    
    view.update_status_card("Progressing", 50, "1h 00m 00s")
    assert view.status_card_eta_label.text() == "ETA: 1h 00m 00s"
    
    view.set_operation_status(True)
    assert view.target_button.isEnabled() == False
    assert view.target_button.isEnabled() == False
