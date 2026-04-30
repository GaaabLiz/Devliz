from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QVBoxLayout
from pylizlib.core.data.unit import get_normalized_gb_mb_str
from pylizlib.qtfw.widgets.card import MasterListSettingCard
from qfluentwidgets import PushSettingCard, FluentIcon, PushButton, SwitchSettingCard, OptionsSettingCard

from devliz.application.app import app, app_settings, AppSettings
from devliz.view.util.frame import DevlizQFrame
from devliz.view.util.setting import SettingGroupManager
from devliz.application.i18n import tr


class WidgetSettings(DevlizQFrame):

    signal_open_dir_request = Signal()
    signal_close_and_clear_request = Signal()
    signal_open_about_dialog_request = Signal()
    signal_request_update = Signal()
    signal_ask_catalogue_path = Signal()
    signal_open_tags_dialog = Signal()
    signal_clear_backups_request = Signal()
    signal_language_changed = Signal()
    signal_theme_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(name=tr("Settings"), parent=parent)

        # Label titolo
        self.install_label_title()

        # Aggiungo i widgets
        self.__add_groups(self.get_scroll_layout())

        # Installo lo scroll nel layout principale
        self.install_scroll_on(self.master_layout)



    def __add_groups(self, layout: QVBoxLayout):
        self.__add_group_snapshot(layout)
        self.__add_group_favorites(layout)
        self.__add_group_app(layout)
        self.__add_group_info(layout)

    def __add_group_snapshot(self, layout: QVBoxLayout):

        # Percorso catalogo generale
        setting_catalogue = AppSettings.catalogue_path
        self.card_general_catalogue = PushSettingCard(
            text=tr("Choose directory"),
            icon=FluentIcon.BOOK_SHELF,
            title=tr("Catalogue path"),
            content=app_settings.get(setting_catalogue)
        )

        # Tag configurazioni
        setting_tags = AppSettings.config_tags
        self.card_fav_tags = MasterListSettingCard(
            config_item=setting_tags,
            item_type=MasterListSettingCard.Type.TEXT,
            card_title=tr("Configuration tags"),
            card_icon=FluentIcon.TAG,
            main_btn=PushButton(tr("Add tag"), self),
            card_content=tr("Add one or more tags to assign to configurations"),
            parent=self if setting_tags.enabled else None,
            dialog_title=tr("Add tag"),
            dialog_content=tr("Enter the tag name"),
            dialog_button_yes=tr("Add"),
            dialog_button_no=tr("Cancel"),
            dialog_error=tr("The tag cannot be empty or already existing"),
            deletion_title=tr("Confirm deletion"),
            deletion_content=tr("Are you sure you want to delete this tag?")
        )

        # custom data snapshots
        setting_custom_data = AppSettings.snap_custom_data
        self.card_snap_custom_data = MasterListSettingCard(
            config_item=setting_custom_data,
            item_type=MasterListSettingCard.Type.TEXT,
            card_title=tr("Snapshots - Custom data"),
            card_icon=FluentIcon.QUICK_NOTE,
            main_btn=PushButton(tr("Add variable"), self),
            card_content=tr("Add one or more custom variables to assign to snapshots"),
            parent=self if setting_custom_data.enabled else None,
            dialog_title=tr("Add variable"),
            dialog_content=tr("Enter the variable name"),
            dialog_button_yes=tr("Add"),
            dialog_button_no=tr("Cancel"),
            dialog_error=tr("The variable cannot be empty or already existing"),
            deletion_title=tr("Confirm deletion"),
            deletion_content=tr("Are you sure you want to delete this variable?")
        )

        # Backup pre-installazione
        setting_backup_before_install = AppSettings.backup_before_install
        self.card_backup_before_install = SwitchSettingCard(
            icon=FluentIcon.BASKETBALL,
            title=tr("Enable pre-installation backup"),
            content=tr("Backup local folders (on this PC) contained in the configuration before installing it"),
            configItem=setting_backup_before_install
        )

        # Backup pre-modifica
        setting_backup_before_edit = AppSettings.backup_before_edit
        self.card_backup_before_edit = SwitchSettingCard(
            icon=FluentIcon.BASKETBALL,
            title=tr("Enable pre-edit backup"),
            content=tr("Backup local folders (on this PC) contained in the configuration before editing them"),
            configItem=setting_backup_before_edit
        )

        # Backup pre-eliminazione
        setting_backup_before_delete = AppSettings.backup_before_delete
        self.card_backup_before_delete= SwitchSettingCard(
            icon=FluentIcon.BASKETBALL,
            title=tr("Enable pre-deletion backup"),
            content=tr("Backup local folders (on this PC) contained in the configuration before deleting them"),
            configItem=setting_backup_before_delete
        )

        # Cancellazione cartelle allegate prima dell'installazione
        setting_clear_snap_attached_folders_before_install = AppSettings.clear_snap_attached_folders_before_install
        self.card_clear_snap_attached_folders_before_install = SwitchSettingCard(
            icon=FluentIcon.BASKETBALL,
            title=tr("Clear attached folders before installation"),
            content=tr("Before installing a configuration, clear the local attached folders (on this PC)"),
            configItem=setting_clear_snap_attached_folders_before_install
        )

        grp_manager = SettingGroupManager(tr("Snapshots"), self)
        grp_manager.add_widget(setting_catalogue, self.card_general_catalogue, self.signal_ask_catalogue_path)
        grp_manager.add_widget(setting_tags, self.card_fav_tags, None)
        grp_manager.add_widget(setting_custom_data, self.card_snap_custom_data, None)
        grp_manager.add_widget(setting_backup_before_install, self.card_backup_before_install,None)
        grp_manager.add_widget(setting_backup_before_edit, self.card_backup_before_edit, None)
        grp_manager.add_widget(setting_backup_before_delete, self.card_backup_before_delete, None)
        grp_manager.add_widget(setting_clear_snap_attached_folders_before_install, self.card_clear_snap_attached_folders_before_install, None)
        grp_manager.install_group_on(layout)


    def __add_group_favorites(self, layout: QVBoxLayout):

        # Cartelle preferite
        setting_fav_dirs = AppSettings.starred_dirs
        self.card_fav_dirs = MasterListSettingCard(
            config_item=setting_fav_dirs,
            item_type=MasterListSettingCard.Type.FOLDER,
            card_title=tr("Starred folders"),
            card_icon=FluentIcon.FOLDER,
            main_btn=PushButton(tr("Add folder"), self),
            card_content=tr("Add one or more starred folders"),
            parent=self if setting_fav_dirs.enabled else None,
            dialog_title=tr("Select folder"),
        )

        # File preferite
        setting_fav_files = AppSettings.starred_files
        self.card_fav_files = MasterListSettingCard(
            config_item=setting_fav_files,
            item_type=MasterListSettingCard.Type.FILE,
            card_title=tr("Starred files"),
            card_icon=FluentIcon.DOCUMENT,
            main_btn=PushButton(tr("Add file"), self),
            card_content=tr("Add one or more starred files"),
            parent=self if setting_fav_files.enabled else None,
            dialog_title=tr("Select file"),
            dialog_file_filter=tr("All Files (*.*)")
        )

        # Eseguibili preferiti
        setting_fav_exe = AppSettings.starred_exes
        self.card_fav_exes = MasterListSettingCard(
            config_item=setting_fav_exe,
            item_type=MasterListSettingCard.Type.FILE,
            card_title=tr("Starred executables"),
            card_icon=FluentIcon.APPLICATION,
            main_btn=PushButton(tr("Choose an executable"), self),
            card_content=tr("Add one or more starred executables to monitor on the home screen"),
            parent=self if setting_fav_exe.enabled else None,
            dialog_title=tr("Select executable"),
            dialog_file_filter=tr("Executable Files (*.exe);;All Files (*.*)")
        )

        # Servizi preferiti
        setting_fav_services = AppSettings.starred_services
        self.card_fav_services = MasterListSettingCard(
            config_item=setting_fav_services,
            item_type=MasterListSettingCard.Type.TEXT,
            card_title=tr("Starred services"),
            card_icon=FluentIcon.SETTING,
            main_btn=PushButton(tr("Add service"), self),
            card_content=tr("Add one or more Windows services to monitor on the home screen"),
            parent=self if setting_fav_services.enabled else None,
            dialog_title=tr("Add service"),
            dialog_content=tr("Enter the Windows service name (e.g. Spooler)"),
            dialog_button_yes=tr("Add"),
            dialog_button_no=tr("Cancel"),
            dialog_error=tr("The service name cannot be empty or already existing"),
            deletion_title=tr("Confirm deletion"),
            deletion_content=tr("Are you sure you want to delete this service?")
        )

        grp_manager = SettingGroupManager(tr("Favorites"), self)
        grp_manager.add_widget(setting_fav_dirs, self.card_fav_dirs, None)
        grp_manager.add_widget(setting_fav_files, self.card_fav_files, None)
        grp_manager.add_widget(setting_fav_exe, self.card_fav_exes, None)
        grp_manager.add_widget(setting_fav_services, self.card_fav_services, None)
        grp_manager.install_group_on(layout)



    def __add_group_app(self, layout: QVBoxLayout):

        # Directory di lavoro
        self.card_working_folder = PushSettingCard(
            text=tr("Open Folder"),
            icon=FluentIcon.FOLDER,
            title=tr("Working folder of {name}", name=app.name),
            content=app.path.__str__()
        )

        # Cancella backups
        size_str = get_normalized_gb_mb_str(0)
        self.card_clear_backups = PushSettingCard(
            text=tr("Clear backups"),
            icon=FluentIcon.DELETE,
            title=tr("Clear Backups of {name}", name=app.name),
            #content="Questa operazione eliminerà tutti i file di backup creati dall'applicazione. (Attualmente: " + size_str + ")"
            content=tr("This operation will delete all backup files created by the application.")
        )

        # Tema applicazione
        self.card_theme = OptionsSettingCard(
            AppSettings.themeMode,
            icon=FluentIcon.BRUSH,
            title=tr("Application theme"),
            content=tr("Select the application theme"),
            texts=[tr("Light"), tr("Dark")],
        )
        self.card_theme.optionChanged.connect(lambda: self.signal_theme_changed.emit())

        # Lingua applicazione
        self.card_language = OptionsSettingCard(
            AppSettings.language,
            icon=FluentIcon.LANGUAGE,
            title=tr("Language"),
            content=tr("Select the application language"),
            texts=[tr("English"), tr("Italian")],
        )
        self.card_language.optionChanged.connect(lambda: self.signal_language_changed.emit())

        grp_manager = SettingGroupManager(tr("Application"), self)
        grp_manager.add_widget(None, self.card_working_folder, self.signal_open_dir_request)
        grp_manager.add_widget(None, self.card_clear_backups, self.signal_clear_backups_request)
        grp_manager.add_widget(None, self.card_theme, None)
        grp_manager.add_widget(None, self.card_language, None)
        grp_manager.install_group_on(layout)

    def __add_group_info(self, layout: QVBoxLayout):

        # Informazioni applicazione
        self.card_info_app = PushSettingCard(
            text=tr("Information"),
            icon=FluentIcon.APPLICATION,
            title=tr("About {name}", name=app.name),
            content=app.version
        )

        grp_manager = SettingGroupManager(tr("Information"), self)
        grp_manager.add_widget(None, self.card_info_app, self.signal_open_about_dialog_request)
        grp_manager.install_group_on(layout)
