from pathlib import Path
from devliz.application.app import app_settings, AppSettings, DEFAULT_SETTING_CATALOGUE_PATH

class SplashModel:
    """
    Model handling the initial splash screen logic and configuration checks.
    """
    
    def __init__(self):
        """
        Initializes the SplashModel.
        """
        pass

    def check_catalogue_path(self) -> bool:
        """
        Checks if the catalogue path exists and is accessible.
        
        Returns:
            bool: True if the path exists, False otherwise.
        """
        catalogue_path = Path(app_settings.get(AppSettings.catalogue_path))
        return catalogue_path.exists()

    def get_catalogue_path_str(self) -> str:
        """
        Returns the currently configured catalogue path as a string.
        
        Returns:
            str: The currently configured path.
        """
        return app_settings.get(AppSettings.catalogue_path)

    def set_default_catalogue_path(self):
        """
        Resets the catalogue path to the default value and saves the settings.
        """
        app_settings.set(AppSettings.catalogue_path, DEFAULT_SETTING_CATALOGUE_PATH)
