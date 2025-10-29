import yaml
from core import ui

class ConfigManager:
    """Manages loading and accessing application configuration from config.yaml."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        try:
            with open('config/config.yaml', 'r') as f:
                self._config = yaml.safe_load(f)
            ui.print_info("Configuration loaded from config/config.yaml.")
        except FileNotFoundError:
            ui.print_error("config/config.yaml not found. Please ensure it exists.")
            self._config = {}
        except yaml.YAMLError as e:
            ui.print_error(f"Error parsing config/config.yaml: {e}")
            self._config = {}

    def get(self, key: str, default=None):
        """Retrieves a configuration value using a dot-separated key (e.g., 'database.uri')."""
        parts = key.split('.')
        current = self._config
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        return current

    def reload(self):
        """Reloads the configuration from the file."""
        self._load_config()
        ui.print_info("Configuration reloaded.")
