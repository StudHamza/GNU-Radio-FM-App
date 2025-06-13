"""
Modern FM Radio Main Window - Dark Theme UI
"""
import logging
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                            QTabWidget, QLabel, QPushButton, 
                            QLineEdit, QTextEdit, QHBoxLayout,
                            QListWidget, QSpinBox, QCheckBox,
                            QSlider,QSpinBox)
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
        self.current_station_freq =  87.9*10**6
        self.stations = [88700000,89500000,89900000,90900000,92100000,92500000,92700000,93700000]

        # Qt Variables 

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
        
        # Main horizontal layout
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # content area
        content_area_widget = QWidget()
        content_area_layout = QHBoxLayout()

        # Create home widge
        self.create_home_widget() # Creates self.home_widget 

        # create channel list
        self.create_stations()
        
        # Create Bottom Menu
        self.create_bottom_menu()

        # Add widgets
        content_area_layout.addWidget(self.stations_widget,1)
        content_area_layout.addWidget(self.home_widget,6)
        content_area_widget.setLayout(content_area_layout)

        self.main_layout.addWidget(content_area_widget)
        self.main_layout.addWidget(self.bottom_menu_widget)

    def create_bottom_menu(self):
        """This function creates the bottom menu tabs and connects them with appropriate functions"""
        self.bottom_menu_widget = QWidget()
        bottom_menu_layout = QHBoxLayout()

        # Home 
        home_button = QPushButton("Home")
        home_button.setCheckable(True)
        home_button.setChecked(True)
        home_button.clicked.connect(self.home_widget.setVisible)
        # stations
        stations_button = QPushButton("Stations")
        stations_button.setCheckable(True)
        stations_button.clicked.connect(self.stations_widget.setVisible)

        bottom_menu_layout.addWidget(home_button)
        bottom_menu_layout.addWidget(stations_button)
        self.bottom_menu_widget.setLayout(bottom_menu_layout)

    def create_stations(self):
        """This funcion creates the stations widnow and displays the a list of stations"""
        self.stations_widget = QWidget()
        layout = QVBoxLayout()

        if self.stations:
            layout.addWidget(QLabel("Avaliable Stations"))
            for station in self.stations:
                station_btn = QPushButton(f"{station/10**6}")
                station_btn.setProperty("freq",station)
                station_btn.clicked.connect(self.change_channel)
                layout.addWidget(station_btn)
        else:
            layout.addWidget(QLabel("No stations"))

        layout.addStretch()
        self.stations_widget.setLayout(layout)
        self.stations_widget.setVisible(False)


    def create_home_widget(self):
        # Home tab content
        self.home_widget = QWidget()
        layout = QVBoxLayout()
        
        # Data
        self.freq_label= QLabel(f"{self.current_station_freq/10**6} FM")
        self.freq_label.setAlignment(Qt.AlignCenter)
        self.btn = QPushButton("Listen")
        self.btn.setCheckable(True)
        self.btn.clicked.connect(self.fm_player)   

        # Add widgets to layout
        layout.addWidget(self.freq_label)
        layout.addWidget(self.btn)
        layout.addStretch()  # Push everything to top
        self.home_widget.setLayout(layout)

        

    def fm_player(self):
        if self.flowgraph:
            self.btn.setText("Start listening")
            self.simple_fm_receiver.stop()
            self.simple_fm_receiver.wait()
            self.flowgraph =False
        else: 
            self.btn.setText("Stop Lisenting")
            self.simple_fm_receiver.start()
            self.flowgraph=True
    

    def change_channel(self):

        btn = self.sender()
        self.set_freq(btn.property("freq"))


    def set_freq(self, freq):
        
        self.freq_label.setText(f"{freq/10**6} FM")
        self.simple_fm_receiver.set_freq(freq)
        self.current_station_freq = freq

    
    def closeEvent(self, event):
        """Handle window close event"""
        logger.info("Application closing")
        event.accept()


