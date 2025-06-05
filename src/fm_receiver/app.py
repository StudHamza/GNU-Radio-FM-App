"""
Main FM Receiver Application Class
"""
import logging
from qtpy.QtCore import QTimer
from .gui.main_window import MainWindow
from .core.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class FMReceiverApp:
    """Main application coordinator"""
    
    def __init__(self, config_path=None):
        logger.info("Initializing FM Receiver Application")
        
        # Initialize configuration
        self.config = ConfigManager(config_path)
        
        # Create main window
        self.main_window = MainWindow(self.config)

        
        # Setup periodic updates (simulate real-time data)
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_display)
        self.update_timer.start(100)  # Update every 100ms
        
        logger.info("FM Receiver Application initialized successfully")
    
    def show(self):
        """Show the main window"""
        self.main_window.show()
    
    def _update_display(self):
        """Update display elements (placeholder for real data)"""
        # This would normally update spectrum, signal strength, etc.
        pass