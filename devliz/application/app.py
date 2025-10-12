from pathlib import Path

from pylizlib.core.app.pylizapp import PylizApp
from pylizlib.core.os.utils import PATH_DEFAULT_GIT_BASH
from pylizlib.qtfw.qconfig import TextListValidator, ExecutableValidator
from qfluentwidgets import QConfig, ConfigItem, BoolValidator, qconfig, FolderValidator

from devliz.project import version, name, authors

# Devliz Application
app = PylizApp(name, version, name, authors[0][0])

# Application directories
DEVLIZ_PATH_CATALOGUE = Path(app.get_path()).joinpath("Catalogue")
DEVLIZ_PATH_SCRIPTS = Path(app.get_path()).joinpath("Scripts")
DEVLIZ_PATH_TRASH = Path(app.get_path()).joinpath("Trash")
DEVLIZ_PATH_LOGS = Path(app.get_path()).joinpath("Logs")
DEVLIZ_PATH_TEMP = Path(app.get_path()).joinpath("Temp")
DEVLIZ_PATH_BACKUPS = Path(app.get_path()).joinpath("Backups")
DEVLIZ_PATH_JSON_SETTING_FILE = Path(app.get_path()).joinpath("Settings.json")

# VALORI DI DEFAULT DELLE IMPOSTAZIONI
DEFAULT_SETTING_CATALOGUE_PATH = DEVLIZ_PATH_CATALOGUE.__str__()
DEFAULT_SETTING_STARRED_DIRS = []
DEFAULT_SETTING_STARRED_FILES = []
DEFAULT_SETTING_STARRED_EXES = []
DEFAULT_SETTING_STARRED_SERVICES = []
DEFAULT_SETTING_CONFIGURATION_TAGS = []
DEFAULT_SETTING_PATH_GIT_BASH = PATH_DEFAULT_GIT_BASH.__str__()
DEFAULT_SETTING_CONFIG_BACKUP_BEFORE_INSTALL = True

# DEFINIZIONI COSTANTI DELLE CONFIGURAZIONI
CONFIG_ID_SIZE = 10

# DEFINIZIONE DEI GRUPPI DI IMPOSTAZIONI
SETTING_GROUP_CONFIGS = "Configurazioni"
SETTING_GROUP_SCRIPTS = "Scripts"
SETTING_GROUP_FAVORITES = "Preferiti"
SETTING_GROUP_APP = "App"

# GESTIONE RISORSE


# DEFINIZIONE DELLE IMPOSTAZIONI DELL'APPLICAZIONE
class DevlizSettings(QConfig):
    config_tags = ConfigItem(SETTING_GROUP_CONFIGS, "Tag configurazioni", DEFAULT_SETTING_CONFIGURATION_TAGS, TextListValidator())
    catalogue_path = ConfigItem(SETTING_GROUP_CONFIGS, "Catalogue Path", DEFAULT_SETTING_CATALOGUE_PATH, FolderValidator())
    backup_before_install = ConfigItem(SETTING_GROUP_CONFIGS, "Backup Before Install", DEFAULT_SETTING_CONFIG_BACKUP_BEFORE_INSTALL, BoolValidator())
    git_bash_path = ConfigItem(SETTING_GROUP_SCRIPTS, "Git Bash path", DEFAULT_SETTING_PATH_GIT_BASH, ExecutableValidator())
    starred_dirs = ConfigItem(SETTING_GROUP_FAVORITES,"Cartelle preferite", DEFAULT_SETTING_STARRED_DIRS, TextListValidator())
    starred_files = ConfigItem(SETTING_GROUP_FAVORITES,"File preferiti", DEFAULT_SETTING_STARRED_FILES, TextListValidator())
    starred_exes = ConfigItem(SETTING_GROUP_FAVORITES, "Eseguibili Preferiti", DEFAULT_SETTING_STARRED_EXES, TextListValidator())
    starred_services = ConfigItem(SETTING_GROUP_FAVORITES, "Servizi Preferiti", DEFAULT_SETTING_STARRED_SERVICES, TextListValidator())
    debug_test_mode = ConfigItem(SETTING_GROUP_APP, "DebugTestMode", False, BoolValidator())


# CARICAMENTO IMPOSTAZIONI
app_settings = DevlizSettings()
qconfig.load(DEVLIZ_PATH_JSON_SETTING_FILE, app_settings)