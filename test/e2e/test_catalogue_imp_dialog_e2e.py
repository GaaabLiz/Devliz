import pytest
from PySide6.QtCore import Qt

def test_catalogue_import_dialog_e2e(qtbot, monkeypatch):
    """
    Test E2E for the Catalogue Import Dialog.
    Navigates to the details tab, inputs text, tests validation, and clicks create.
    """
    from devliz.view.catalogue_imp_dialog import DialogConfig
    from devliz.domain.data import DevlizData
    import PySide6.QtWidgets
    
    # Mock MessageBox to prevent blocking
    class FakeMessageBox:
        res = True
        def __init__(self, t, d, parent=None):
            self.yesButton = type('obj', (object,), {'hide': lambda: None})()
            self.cancelButton = type('obj', (object,), {'setText': lambda s: None})()
        def exec(self): return self.res
        def exec_(self): return self.res
    
    monkeypatch.setattr("qfluentwidgets.MessageBox", FakeMessageBox)

    # Empty data
    data = DevlizData(monitored_software=[], monitored_services=None, snapshots=[])

    dialog = DialogConfig(devliz_data=data, edit_mode=False)
    qtbot.addWidget(dialog)

    # Show the dialog but don't block the event loop with exec()
    dialog.show()
    qtbot.waitForWindowShown(dialog)

    # The create button is enabled by default, but validation will fail if empty
    assert dialog.btn_create.isEnabled()

    # Mock UiUtils to track messages
    import devliz.view.catalogue_imp_dialog
    messages = []
    class FakeUiUtils:
        @classmethod
        def show_message(cls, title, text, parent=None):
            messages.append(text)
    monkeypatch.setattr(devliz.view.catalogue_imp_dialog, "UiUtils", FakeUiUtils)

    # Click create while empty
    qtbot.mouseClick(dialog.btn_create, Qt.LeftButton)

    # Validation message should be shown
    assert len(messages) > 0

    # Get the details tab
    details_tab = dialog._DialogConfig__tabs.tab_details

    # Type name and description
    qtbot.keyClicks(details_tab.form_name_input, "Test Config")
    qtbot.keyClicks(details_tab.form_desc_input, "Test Description")

    # Ensure UI reflects input
    assert details_tab.form_name_input.text() == "Test Config"
    
    # Click tags input to trigger the no-tags MessageBox
    qtbot.mouseClick(details_tab.form_tags_input, Qt.LeftButton)
    
    # Add a directory to pass validation
    directories_tab = dialog._DialogConfig__tabs.tab_directories
    from pathlib import Path
    directories_tab.add_directory(Path("/tmp/some_dir"), execute_checks=False)
    
    # Click the create button again
    qtbot.mouseClick(dialog.btn_create, Qt.LeftButton)

    # Check that output data is formed properly
    assert getattr(dialog, 'output_data', None) is not None
    assert dialog.output_data.name == "Test Config"
    assert dialog.output_data.desc == "Test Description"
    dialog.close()
    dialog.deleteLater()
