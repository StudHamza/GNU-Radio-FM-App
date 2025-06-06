"""
Modern FM Radio Main Window - Dark Theme UI
"""
import logging
from qtpy.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout)
from .sidebar import Sidebar
from .station_list import StationList
from .media_player import MediaPlayer

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Modern FM Radio Main Window"""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        # self.setup_dark_theme()
        self.setup_ui()
        self.load_settings()
        logger.info("Modern FM Radio UI created")
    
    def setup_dark_theme(self):
        """Setup dark theme styling"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
                color: #ffffff;
            }
            QWidget {
                background-color: #1a1a1a;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QScrollArea {
                border: none;
                background-color: #2d2d2d;
            }
            QScrollBar:vertical {
                background-color: #3d3d3d;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #5d5d5d;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #7d7d7d;
            }
        """)
    
    def setup_ui(self):
        """Setup the main user interface"""
        self.setWindowTitle("GNU Radio FM Receiver")
        self.setMinimumSize(1200, 700)
        self.resize(1400, 800)
        
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main horizontal layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left sidebar
        self.sidebar = Sidebar()
        self.sidebar.setFixedWidth(200)
        main_layout.addWidget(self.sidebar)
        
        # Right content area
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Station list area
        self.station_list = StationList()
        content_layout.addWidget(self.station_list)
        
        # Bottom media player
        self.media_player = MediaPlayer()
        self.media_player.setFixedHeight(100)
        content_layout.addWidget(self.media_player)
        
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget)
        
        # Connect signals
        self.sidebar.home_clicked.connect(self.show_home)
        self.sidebar.fft_clicked.connect(self.show_fft)
        self.sidebar.debug_clicked.connect(self.show_debug)
        self.sidebar.settings_clicked.connect(self.show_settings)
        
        self.station_list.station_selected.connect(self.on_station_selected)
        self.media_player.play_clicked.connect(self.toggle_playback)
    
    def load_settings(self):
        """Load application settings"""
        # Load mock stations
        mock_stations = [
            {
                'frequency': 94.5,
                'name': '94.5 FM RDS information',
                'artist': 'Pritam, Mohit Chauhan, Sandeep Shrivastava',
                'song': 'Tune Jo Na Kaha',
                'image': 'station1.jpg'
            },
            {
                'frequency': 96.3,
                'name': '96.3 Classic Rock',
                'artist': 'Led Zeppelin',
                'song': 'Stairway to Heaven',
                'image': 'station2.jpg'
            },
            {
                'frequency': 98.7,
                'name': '98.7 Jazz FM',
                'artist': 'Miles Davis',
                'song': 'Kind of Blue',
                'image': 'station3.jpg'
            },
            {
                'frequency': 101.1,
                'name': '101.1 Pop Hits',
                'artist': 'Taylor Swift',
                'song': 'Anti-Hero',
                'image': 'station4.jpg'
            },
            {
                'frequency': 103.5,
                'name': '103.5 News Radio',
                'artist': 'BBC News',
                'song': 'World Service',
                'image': 'station5.jpg'
            }
        ]
        
        self.station_list.load_stations(mock_stations)
        
        # Set first station as current
        if mock_stations:
            self.media_player.set_current_track(mock_stations[0])
    
    def show_home(self):
        """Show home view"""
        logger.info("Home clicked")
        self.station_list.show()
    
    def show_fft(self):
        """Show FFT spectrum analyzer"""
        logger.info("FFT clicked")
        # This would switch to spectrum view
    
    def show_debug(self):
        """Show debug mode"""
        logger.info("Debug mode clicked")
        # This would show debug information
    
    def show_settings(self):
        """Show settings dialog"""
        logger.info("Settings clicked")
        # This would open settings dialog
    
    def on_station_selected(self, station_data):
        """Handle station selection"""
        logger.info(f"Station selected: {station_data['name']}")
        self.media_player.set_current_track(station_data)
    
    def toggle_playback(self):
        """Toggle play/pause"""
        logger.info("Playback toggled")
        # This would control actual playback
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.config.save()
        logger.info("Application closing")
        event.accept()