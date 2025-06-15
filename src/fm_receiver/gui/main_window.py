"""
Modern FM Radio Main Window - Fixed Layout Issues
"""
import logging
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                            QTabWidget, QLabel, QPushButton, 
                            QLineEdit, QTextEdit, QHBoxLayout,
                            QListWidget, QSpinBox, QCheckBox,
                            QSlider, QSpinBox, QGridLayout, QStackedWidget,
                            QButtonGroup, QSizePolicy)
from PyQt5.QtCore import Qt
from flowgraphs.simple_fm_receiver import simple_fm_receiver
from gnuradio.qtgui import Range, RangeWidget

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Modern FM Radio Main Window"""
    
    def __init__(self):
        super().__init__()

        # Variables
        self.flowgraph = False
        self.simple_fm_receiver = simple_fm_receiver()
        self.current_station_freq = 87.9*10**6
        self.stations = [88700000,89500000,89900000,90900000,92100000,92500000,92700000,93700000]

        # Setup UI
        self.setup_ui()
        logger.info("Modern FM Radio UI created")
    
    def setup_ui(self):
        """Setup the main user interface"""
        self.setWindowTitle("GNU Radio FM Receiver")
        self.setMinimumSize(1200, 700)
        self.resize(1400, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main vertical layout
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # Create stacked widget for content switching
        self.stacked_widget = QStackedWidget()
        
        # Create widgets
        self.create_home_widget()
        self.create_stations_widget()
        self.create_debug_widget()
        
        # Add widgets to stack
        self.stacked_widget.addWidget(self.home_widget)      # Index 0
        self.stacked_widget.addWidget(self.stations_widget)  # Index 1
        self.stacked_widget.addWidget(self.debug_widget)    # Index 2 

        # Create bottom menu
        self.create_bottom_menu()
        
        # Add to main layout
        self.main_layout.addWidget(self.stacked_widget, 1)  # Takes most space
        self.main_layout.addWidget(self.bottom_menu_widget, 0)  # Fixed size

    def create_bottom_menu(self):
        """Create bottom menu with proper button group management"""
        self.bottom_menu_widget = QWidget()
        self.bottom_menu_widget.setFixedHeight(60)
        
        bottom_menu_layout = QHBoxLayout(self.bottom_menu_widget)
        bottom_menu_layout.setContentsMargins(20, 10, 20, 10)
        
        # Create button group for radio button behavior
        self.menu_button_group = QButtonGroup()
        
        # Home button
        self.home_button = QPushButton("Home")
        self.home_button.setCheckable(True)
        self.home_button.setChecked(True)
        self.home_button.setMinimumHeight(40)
        self.menu_button_group.addButton(self.home_button, 0)
        
        # Stations button
        self.stations_button = QPushButton("Stations")
        self.stations_button.setCheckable(True)
        self.stations_button.setMinimumHeight(40)
        self.menu_button_group.addButton(self.stations_button, 1)

        # Debug button
        self.debug_button = QPushButton("Debug")
        self.debug_button.setCheckable(True)
        self.debug_button.setMinimumHeight(40)
        self.menu_button_group.addButton(self.debug_button, 2)
        
        # Connect button group signal
        self.menu_button_group.buttonClicked.connect(self.switch_page)
        
        # Add to layout
        bottom_menu_layout.addStretch()
        bottom_menu_layout.addWidget(self.home_button)
        bottom_menu_layout.addWidget(self.stations_button)
        bottom_menu_layout.addWidget(self.debug_button)
        bottom_menu_layout.addStretch()

    def switch_page(self, button):
        """Switch between home and stations pages"""
        button_id = self.menu_button_group.id(button)
        self.stacked_widget.setCurrentIndex(button_id)

    def create_debug_widget(self):
        self.debug_widget = QWidget()



    def create_stations_widget(self):
        """Create stations widget with proper layout"""
        self.stations_widget = QWidget()
        layout = QVBoxLayout(self.stations_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Available Stations")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title_label)
        
        if self.stations:
            # Create stations grid
            stations_layout = QGridLayout()
            stations_widget = QWidget()
            stations_widget.setLayout(stations_layout)
            
            for i, station in enumerate(self.stations):
                row = i // 2
                col = i % 2
                
                station_btn = QPushButton(f"{station/10**6:.1f} FM")
                station_btn.setProperty("freq", station)
                station_btn.setMinimumHeight(50)
                station_btn.setStyleSheet("""
                    QPushButton {
                        font-size: 16px;
                        padding: 10px;
                        margin: 5px;
                    }
                """)
                station_btn.clicked.connect(self.change_channel)
                stations_layout.addWidget(station_btn, row, col)
            
            layout.addWidget(stations_widget)
        else:
            no_stations_label = QLabel("No stations available")
            no_stations_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_stations_label)
        
        layout.addStretch()

    def create_home_widget(self):
        """Create home widget with improved layout"""
        self.home_widget = QWidget()
        layout = QVBoxLayout(self.home_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Main control area
        control_widget = QWidget()
        control_layout = QGridLayout(control_widget)
        control_layout.setSpacing(15)
        
        # Listen/Stop button
        self.btn = QPushButton("Listen")
        self.btn.setCheckable(True)
        self.btn.setMinimumHeight(50)
        self.btn.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.btn.clicked.connect(self.fm_player)
        
        # Record button
        self.record_btn = QPushButton("Record")
        self.record_btn.setMinimumHeight(50)
        self.record_btn.setStyleSheet("font-size: 16px;")
        
        # Signal strength label
        self.strength_label = QLabel("Signal Strength: --")
        self.strength_label.setAlignment(Qt.AlignCenter)
        self.strength_label.setStyleSheet("font-size: 14px;")
        
        # Frequency display
        self.freq_label = QLabel(f"{self.current_station_freq/10**6:.1f} FM")
        self.freq_label.setAlignment(Qt.AlignCenter)
        self.freq_label.setStyleSheet("font-size: 32px; font-weight: bold; margin: 20px;")
        
        # Navigation buttons
        self.prev_station_btn = QPushButton("◀ Previous")
        self.next_station_btn = QPushButton("Next ▶")
        self.prev_station_btn.setMinimumHeight(40)
        self.next_station_btn.setMinimumHeight(40)
        
        # RDS info
        self.rds_info = QLabel("RDS: No Information")
        self.rds_info.setAlignment(Qt.AlignCenter)
        self.rds_info.setStyleSheet("font-size: 14px; color: #666;")
        
        # Channel slider placeholder
        self.channel_slider = QLabel("Channel Slider (Coming Soon)")
        self.channel_slider.setAlignment(Qt.AlignCenter)
        self.channel_slider.setStyleSheet("font-size: 12px; color: #999;")
        
        # Layout arrangement
        control_layout.addWidget(self.btn, 0, 0, 1, 2)
        control_layout.addWidget(self.record_btn, 0, 2, 1, 2)
        control_layout.addWidget(self.strength_label, 0, 4, 1, 2)
        
        control_layout.addWidget(self.prev_station_btn, 1, 0, 1, 2)
        control_layout.addWidget(self.freq_label, 1, 2, 1, 2)
        control_layout.addWidget(self.next_station_btn, 1, 4, 1, 2)
        
        control_layout.addWidget(self.rds_info, 2, 0, 1, 6)
        control_layout.addWidget(self.channel_slider, 3, 0, 1, 6)
        
        # Set column stretch to make layout responsive
        for i in range(6):
            control_layout.setColumnStretch(i, 1)
        
        layout.addStretch()
        layout.addWidget(control_widget)
        layout.addStretch()

    def fm_player(self):
        """Toggle FM receiver on/off"""
        if self.flowgraph:
            self.btn.setText("Listen")
            self.simple_fm_receiver.stop()
            self.simple_fm_receiver.wait()
            self.flowgraph = False
        else: 
            self.btn.setText("Stop Listening")
            self.simple_fm_receiver.start()
            self.flowgraph = True

    def change_channel(self):
        """Change to selected station and switch to home view"""
        btn = self.sender()
        freq = btn.property("freq")
        self.set_freq(freq)
        
        # Switch back to home page and update button
        self.stacked_widget.setCurrentIndex(0)
        self.home_button.setChecked(True)

    def set_freq(self, freq):
        """Set frequency and update display"""
        self.freq_label.setText(f"{freq/10**6:.1f} FM")
        self.simple_fm_receiver.set_freq(freq)
        self.current_station_freq = freq
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.flowgraph:
            self.simple_fm_receiver.stop()
            self.simple_fm_receiver.wait()
        logger.info("Application closing")
        event.accept()