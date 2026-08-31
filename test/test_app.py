import sys
from devliz.application import app

def test_network_folder_validator():
    validator = app.NetworkFolderValidator()
    assert validator.validate("some string") is True
    assert validator.validate(123) is False
    assert validator.validate(None) is False
    
    assert validator.correct("test") == "test"
    assert validator.correct(123) == "123"
    assert validator.correct(None) == ""

def test_sync_snap_settings_immediate():
    from devliz.application.app import app_settings, AppSettings, snap_settings
    from devliz.controller.setting_controller import SettingController
    from PySide6.QtWidgets import QApplication
    import qfluentwidgets
    
    # Needs a QApplication for WidgetSettings
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    
    # Initialize the controller so it attaches the signals
    class DummyModel:
        def update(self): pass
    ctrl = SettingController(DummyModel())
    
    # Inizialmente impostiamo un valore noto
    qfluentwidgets.qconfig.set(AppSettings.backup_before_install, False)
    assert snap_settings.backup_pre_install is False
    
    # Modifichiamo il setting tramite l'interfaccia qconfig (simulando l'UI)
    qfluentwidgets.qconfig.set(AppSettings.backup_before_install, True)
    
    # Verifichiamo che il valore sia stato sincronizzato istantaneamente senza refresh
    assert snap_settings.backup_pre_install is True


