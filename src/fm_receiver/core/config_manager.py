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
        """Get default configuration file path"""
        home_dir = Path.home()
        config_dir = home_dir / '.fm_receiver'
        config_dir.mkdir(exist_ok=True)
        return config_dir / 'config.json'
    
    def load(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
                logger.info(f"Configuration loaded from {self.config_path}")
            else:
                self.config = self._get_default_config()
                logger.info("Using default configuration")
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.config = self._get_default_config()
    
    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
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
            'last_frequency': 88.5,
            'last_volume': 50,
            'window_geometry': None,
            'auto_scan_enabled': True,
            'rds_enabled': True
        }