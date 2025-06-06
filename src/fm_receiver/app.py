"""
Main FM Receiver Application Class
"""
import logging
from qtpy.QtCore import QTimer
from gui.main_window import MainWindow
from core.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class FMReceiverApp:
    """Main application coordinator"""
    
    def __init__(self, config_path=None):
        logger.info("Initializing FM Receiver Application")
        
        # Initialize configuration
        self.config = ConfigManager(config_path)
        
        # Create main window
        self.main_window = MainWindow(self.config)
        
        logger.info("FM Receiver Application initialized successfully")
    
    def show(self):
        """Show the main window"""
        self.main_window.show()
    