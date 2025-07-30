"""
Configuration Manager
"""

import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages application configuration"""

    def __init__(self, config_path=None):
        self.config_path = config_path or self._get_default_config_path()
        self.config = {}
        self.load()

    def _get_default_config_path(self):
        """Get default configuration file path relative to where the script is run"""
        current_dir = Path.cwd()  # Gets the current working directory
        config_dir = current_dir / "config"
        config_dir.mkdir(exist_ok=True)  # Create it if it doesn't exist
        return config_dir / "config.json"

    def load(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    self.config = json.load(f)
                logger.info(f"Configuration loaded from {self.config_path}")

                # Check if 'stations' is missing or empty
                if not self.config.get("stations"):
                    logger.warning(
                        "'stations' is missing or empty. Loading default config."
                    )
                    self.config = self._get_default_config()

            else:
                self.config = self._get_default_config()
                logger.info("Using default configuration")
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.config = self._get_default_config()

    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")

    def get(self, key, default=None):
        """Get configuration value"""
        return self.config.get(key, default)

    def set(self, key, value):
        """Set configuration value"""
        self.config[key] = value

    def _get_default_config(self):
        """Get default configuration"""
        return {
            "stations": [88.7e6],
            "volume": 0,
            "outdir":os.path.join((os.getcwd()),"downloads")
        }
