from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QVBoxLayout
from pylizlib.qtfw.widgets.card import MasterListSettingCard
from qfluentwidgets import PushSettingCard, FluentIcon, PushButton, SwitchSettingCard

from devliz.application.app import app, app_settings, DevlizSettings
from devliz.view.util.frame import DevlizQFrame
from devliz.view.util.setting import SettingGroupManager


class WidgetSettingsScrollable(DevlizQFrame):

    signal_open_dir_request = Signal(str)
    signal_close_and_clear_request = Signal()
    signal_open_about_dialog_request = Signal()
    signal_request_update = Signal()
    signal_ask_catalogue_path = Signal()
    signal_open_tags_dialog = Signal()

    def __init__(self, parent=None):
        super().__init__(name="Settings", parent=parent)

        # Label titolo
        self.master_layout.addWidget(self.get_label_title())

        # Aggiungo i widgets
        self.__add_groups(self.get_scroll_layout())

        # Installo lo scroll nel layout principale
        self.install_scroll_on(self.master_layout)



    def __add_groups(self, layout: QVBoxLayout):
        self.__add_group_snapshot(layout)
        self.__add_group_info(layout)

    def __add_group_snapshot(self, layout: QVBoxLayout):

        # Percorso catalogo generale
        self.card_general_catalogue = PushSettingCard(
            text="Scegli directory",
            icon=FluentIcon.BOOK_SHELF,
            title="Percorso del catalogo",
            content=app_settings.get(DevlizSettings.catalogue_path)
        )

        # Tag configurazioni
        self.card_fav_tags = MasterListSettingCard(
            config_item=DevlizSettings.config_tags,
            item_type=MasterListSettingCard.Type.TEXT,
            card_title="Tag configurazioni",
            card_icon=FluentIcon.TAG,
            main_btn=PushButton("Aggiungi tag", self),
            card_content="Aggiungi uno o più tag da assegnare alle configurazioni",
            parent=self,
            dialog_title="Aggiungi tag",
            dialog_content="Inserisci il nome del tag",
            dialog_button_yes="Aggiungi",
            dialog_button_no="Annulla",
            dialog_error="Il tag non può essere vuoto o già esistente",
            deletion_title="Conferma eliminazione",
            deletion_content="Sei sicuro di voler eliminare questo tag?"
        )

        # Tag configurazioni
        self.card_snap_custom_data = MasterListSettingCard(
            config_item=DevlizSettings.snap_custom_data,
            item_type=MasterListSettingCard.Type.TEXT,
            card_title="Snapshots - Dati personalizzati",
            card_icon=FluentIcon.QUICK_NOTE,
            main_btn=PushButton("Aggiungi variabile", self),
            card_content="Aggiungi una o un più variabili personalizzate da assegnare agli snapshots",
            parent=self,
            dialog_title="Aggiungi variabile",
            dialog_content="Inserisci il nome della variabile",
            dialog_button_yes="Aggiungi",
            dialog_button_no="Annulla",
            dialog_error="La variabile non può essere vuota o già esistente",
            deletion_title="Conferma eliminazione",
            deletion_content="Sei sicuro di voler eliminare questa variabile?"
        )

        # Backup pre-installazione
        self.card_backup_before_install = SwitchSettingCard(
            icon=FluentIcon.BASKETBALL,
            title="Abilita backup pre-installazione",
            content="Esegui il backup delle cartelle locali (presenti su questo pc) contenute nella configurazione prima di installarla",
            configItem=DevlizSettings.backup_before_install
        )

        grp_manager = SettingGroupManager(self.tr("Snapshots"), self)
        grp_manager.add_widget(self.card_general_catalogue, self.signal_ask_catalogue_path)
        grp_manager.add_widget(self.card_fav_tags, None)
        grp_manager.add_widget(self.card_snap_custom_data, None)
        grp_manager.add_widget(self.card_backup_before_install,None)
        grp_manager.install_group_on(layout)

    def __add_group_favorites(self, layout: QVBoxLayout):

        # Cartelle preferite
        self.card_fav_dirs = MasterListSettingCard(
            config_item=DevlizSettings.starred_dirs,
            item_type=MasterListSettingCard.Type.FOLDER,
            card_title="Cartelle preferite",
            card_icon=FluentIcon.FOLDER,
            main_btn=PushButton("Aggiungi cartella", self),
            card_content="Aggiungi una o più cartelle preferite",
            parent=self,
            dialog_title="Seleziona cartella",
        )

        # File preferite
        self.card_fav_files = MasterListSettingCard(
            config_item=DevlizSettings.starred_files,
            item_type=MasterListSettingCard.Type.FILE,
            card_title="File preferiti",
            card_icon=FluentIcon.DOCUMENT,
            main_btn=PushButton("Aggiungi file", self),
            card_content="Aggiungi uno o più file preferiti",
            parent=self,
            dialog_title="Seleziona file",
            dialog_file_filter="All Files (*.*)"
        )

        grp_manager = SettingGroupManager(self.tr("Preferiti"), self)
        grp_manager.add_widget(self.card_fav_dirs, None)
        grp_manager.install_group_on(layout)

    def __add_group_info(self, layout: QVBoxLayout):

        # Informazioni applicazione
        self.card_info_app = PushSettingCard(
            text="Informazioni",
            icon=FluentIcon.APPLICATION,
            title="Informazioni su Devliz",
            content=app.version
        )

        grp_manager = SettingGroupManager(self.tr("Informazioni"), self)
        grp_manager.add_widget(self.card_info_app, self.signal_open_about_dialog_request)
        grp_manager.install_group_on(layout)
