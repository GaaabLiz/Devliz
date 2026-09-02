import sys

from PySide6.QtCore import QLocale
from PySide6.QtWidgets import QApplication
from qfluentwidgets import FluentTranslator

from devliz.application.app import app_settings, AppSettings
from devliz.application.i18n import set_language
from devliz.controller.dashboard import DashboardController
from devliz.controller.splash import SplashController
from devliz.model.history import init_action_history_db

def main():
    """
    The main entry point for the Devliz application.
    
    This function initializes the application settings, sets the language,
    initializes the action history database, and configures the main Qt 
    application instance with necessary translators. Finally, it starts 
    the splash and dashboard controllers and begins the Qt event loop.
    
    Returns:
        int: The exit code of the Qt application.
    """
    # Initialize language from settings
    lang = app_settings.get(AppSettings.language)
    set_language(lang)
    
    init_action_history_db()

    qt_app = QApplication(sys.argv)

    # Install FluentTranslator for built-in component translations
    locale = QLocale(QLocale.Language.Italian, QLocale.Country.Italy) if lang == "it" else QLocale(QLocale.Language.English)
    translator = FluentTranslator(locale)
    qt_app.installTranslator(translator)

    splash_controller = SplashController()
    splash_controller.start()

    dashboard = DashboardController()
    dashboard.start()
    return qt_app.exec()


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())