import sys
from PySide6.QtCore import QEventLoop, QTimer
from qfluentwidgets import MessageBox

from devliz.model.splash import SplashModel
from devliz.view.splash import SplashWindow
from devliz.application.i18n import tr

class SplashController:
    def __init__(self):
        self.model = SplashModel()
        self.view = SplashWindow()

    def start(self):
        """
        Avvia la logica dello splash screen:
        1. Mostra la finestra.
        2. Attende 1 secondo per visualizzare il logo.
        3. Controlla l'esistenza del path del catalogo.
        4. Mostra MessageBox d'errore se non esiste.
        5. Chiude la splash screen e permette al chiamante di continuare.
        """
        self.view.show_splash()

        # Attesa di 1 secondo (stessa logica originaria della view)
        loop = QEventLoop()
        QTimer.singleShot(1000, loop.quit)
        loop.exec()

        self.__check_catalogue()

        self.view.close_splash()

    def __check_catalogue(self):
        """
        Esegue il controllo sul percorso del catalogo ed eventualmente chiede all'utente come procedere.
        """
        if not self.model.check_catalogue_path():
            catalogue_path_str = self.model.get_catalogue_path_str()

            msg_box = MessageBox(
                tr("Catalogue Error"),
                tr("The catalogue path is not reachable or does not exist:\n{path}\n\nDo you want to use the default catalogue or close the program?", path=catalogue_path_str),
                self.view  # Impostiamo la view dello splash screen come parent
            )
            msg_box.yesButton.setText(tr("Use default catalogue"))
            msg_box.cancelButton.setText(tr("Close"))
            
            if msg_box.exec():
                self.model.set_default_catalogue_path()
            else:
                sys.exit(0)
