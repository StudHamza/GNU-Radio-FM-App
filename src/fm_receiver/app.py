"""
Main FM Receiver Application Class
"""
import logging

from gui.main_window import MainWindow
from gui.config_dialog import ConfigDialog,QDialog

logger = logging.getLogger(__name__)

class FMReceiverApp:
    """Main application coordinator"""
    def __init__(self, config_path=None,serial=0):
        logger.info("Initializing FM Receiver Application")

        # Create main window
        self.main_window = MainWindow(config_path,serial)
        logger.info("FM Receiver Application initialized successfully")

    def show(self):
        """Show the main window"""
        self.main_window.show()
    