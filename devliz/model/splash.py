from pathlib import Path
from devliz.application.app import app_settings, AppSettings, DEFAULT_SETTING_CATALOGUE_PATH

class SplashModel:
    
    def __init__(self):
        pass

    def check_catalogue_path(self) -> bool:
        """
        Controlla se il percorso del catalogo esiste ed è raggiungibile.
        Returns:
            True se esiste, False altrimenti.
        """
        catalogue_path = Path(app_settings.get(AppSettings.catalogue_path))
        return catalogue_path.exists()

    def get_catalogue_path_str(self) -> str:
        """
        Ritorna il percorso attualmente configurato.
        """
        return app_settings.get(AppSettings.catalogue_path)

    def set_default_catalogue_path(self):
        """
        Ripristina il percorso del catalogo a quello di default e salva le impostazioni.
        """
        app_settings.set(AppSettings.catalogue_path, DEFAULT_SETTING_CATALOGUE_PATH)
