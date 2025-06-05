"""
Main Application Window
"""
import logging
from qtpy.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QMenuBar, QStatusBar, QAction)
from qtpy.QtCore import Qt
from .control_panel import ControlPanel
from .spectrum_widget import SpectrumWidget
from .rds_panel import RDSPanel

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()
        
        # Load window settings
        self.load_settings()
        
        logger.info("Main window created")
    
    def setup_ui(self):
        """Setup the main user interface"""
        self.setWindowTitle("FM Receiver - GNU Radio Demo")
        self.setMinimumSize(800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Top section: Controls and RDS
        top_layout = QHBoxLayout()
        
        # Control panel (left side)
        self.control_panel = ControlPanel(self.config)
        top_layout.addWidget(self.control_panel)
        
        # RDS panel (right side)
        self.rds_panel = RDSPanel()
        top_layout.addWidget(self.rds_panel)
        
        main_layout.addLayout(top_layout)
        
        # Bottom section: Spectrum analyzer
        self.spectrum_widget = SpectrumWidget()
        main_layout.addWidget(self.spectrum_widget)
        
        # Connect signals
        self.control_panel.frequency_changed.connect(self.on_frequency_changed)
        self.control_panel.volume_changed.connect(self.on_volume_changed)
    
    def setup_menu(self):
        """Setup application menu"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        exit_action = QAction('&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('&Tools')
        
        scan_action = QAction('&Scan Stations', self)
        scan_action.setShortcut('Ctrl+S')
        scan_action.triggered.connect(self.scan_stations)
        tools_menu.addAction(scan_action)
    
    def setup_status_bar(self):
        """Setup status bar"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
    
    def load_settings(self):
        """Load window settings from config"""
        # Load last frequency, volume, etc.
        frequency = self.config.get('last_frequency', 88.5)
        volume = self.config.get('last_volume', 50)
        
        self.control_panel.set_frequency(frequency)
        self.control_panel.set_volume(volume)
    
    def on_frequency_changed(self, frequency):
        """Handle frequency change"""
        logger.info(f"Frequency changed to: {frequency} MHz")
        self.status_bar.showMessage(f"Tuned to {frequency} MHz")
        self.config.set('last_frequency', frequency)
        
        # Update RDS with mock data
        self.rds_panel.update_station_info(f"Station {frequency}")
    
    def on_volume_changed(self, volume):
        """Handle volume change"""
        logger.info(f"Volume changed to: {volume}%")
        self.config.set('last_volume', volume)
    
    def scan_stations(self):
        """Start station scanning"""
        logger.info("Starting station scan")
        self.status_bar.showMessage("Scanning for stations...")
        # This would start the actual scanning process
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Save settings before closing
        self.config.save()
        logger.info("Application closing")
        event.accept()