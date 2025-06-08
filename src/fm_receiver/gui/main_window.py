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
    
    def __init__(self, config):
        super().__init__()
        self.config = config
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
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Bottom tab area
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.South)

        self.create_home_tab()

        main_layout.addWidget(self.tabs)


    def closeEvent(self, event):
        """Handle window close event"""
        self.config.save()
        logger.info("Application closing")
        event.accept()

    def create_home_tab(self):
        # Home tab content
        home_widget = QWidget()
        layout = QVBoxLayout()
        
        # Data
        self.play = False
        self.title = QLabel("88.7 FM")
        self.title.setAlignment(Qt.AlignCenter)
        self.btn = QPushButton("Listen")
        self.btn.setCheckable(True)
        self.btn.clicked.connect(self.fm_player)   

        # Range 
        self._freq_range = Range(87.9*10**6, 107.9*10**6, 200*10**3, 87.9*10**6, 200)
        self._freq_win = RangeWidget(self._freq_range, self.set_freq, "'freq'", "counter_slider", float, Qt.Horizontal)

        # Add widgets to layout
        layout.addWidget(self.title)
        layout.addWidget(self.btn)
        layout.addWidget(self._freq_win)
        layout.addStretch()  # Push everything to top
        
        home_widget.setLayout(layout)
        self.tabs.addTab(home_widget, "Home")

    def fm_player(self):
        self.tb = simple_fm_receiver()
        if self.play:
            self.btn.setText("Start listening")
            self.tb.stop()
            self.tb.wait()
            self.play =False
        else: 
            self.btn.setText("Stop Lisenting")
            self.tb.start()
            self.play=True
    
    def set_freq(self, freq):
        self.freq = freq
        self.tb.soapy_rtlsdr_source_0.set_frequency(0, self.freq)
        self.title.setText(f"{freq}")