from devliz.view.help import HelpDetailDialog

def test_help_detail_dialog(qtbot):
    dialog = HelpDetailDialog("Title", "Subtitle", "Details")
    qtbot.addWidget(dialog)
    
    assert dialog.windowTitle() == "Title"
    dialog.accept()
