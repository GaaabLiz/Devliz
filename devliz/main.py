import sys
import os

from PySide6.QtCore import QLocale
from PySide6.QtWidgets import QApplication
from qfluentwidgets import FluentTranslator

from devliz.application.app import app_settings, AppSettings
from devliz.application.i18n import set_language
from devliz.controller.dashboard import DashboardController
from devliz.view.splash import SplashWindow


def main():
    # Initialize language from settings
    lang = app_settings.get(AppSettings.language)
    set_language(lang)

    qt_app = QApplication(sys.argv)

    # Install FluentTranslator for built-in component translations
    locale = QLocale(QLocale.Language.Italian, QLocale.Country.Italy) if lang == "it" else QLocale(QLocale.Language.English)
    translator = FluentTranslator(locale)
    qt_app.installTranslator(translator)

    splash = SplashWindow()
    splash.show()
    splash.close()
    dashboard = DashboardController()
    dashboard.start()
    return qt_app.exec()


if __name__ == "__main__":
    sys.exit(main())