"""
Modern FM Radio Main Window - Cleaned Code
"""
import logging
# pylint: disable=no-name-in-module
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget, QLabel, QPushButton,
    QLineEdit, QTextEdit, QHBoxLayout, QListWidget, QSpinBox, QCheckBox,
    QSlider, QGridLayout, QStackedWidget, QButtonGroup, QSizePolicy, QScrollArea,QComboBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal,pyqtSlot
from flowgraphs.rds_rx import rds_rx
from core.config_manager import ConfigManager
from .frequency_slider import FrequencySlider
from .volume_slider import VolumeSlider
from .scan_thread import ScannerWorker

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Modern FM Radio Main Window"""   
    def __init__(self, config_path:str):
        super().__init__()

        self.config_manager = ConfigManager(config_path)
        self.mute = True
        self.scan_requested = pyqtSignal()
        self.stations = []
        self.fm_receiver = rds_rx()
        self.load_config(self.fm_receiver)
        self.current_station_freq = self.stations[0]
        self.current_station_index = 0
        # Start flowgraph and mute by default
        self.fm_receiver.start()
        self.samp_rate = self.fm_receiver.get_samp_rate()

        # Scanning
        self.scanning_progress = ""
        self.thread = QThread()
        self.worker = None

        # FM band range (88-108 MHz)
        self.fm_min_freq = 88.0 * 10**6
        self.fm_max_freq = 108.0 * 10**6

        # Define Widget Elements
        self.home_widget = QWidget()
        self.bottom_menu_widget = QWidget()
        self.debug_widget = QWidget()
        self.stations_widget = QWidget()

        # --- Home Buttons --- #
        self.mute_button = QPushButton()
        self.scan_btn_home = QPushButton()
        self.record_btn = QPushButton()
        self.volume_slider = VolumeSlider()
        self.prev_station_btn = QPushButton()
        self.next_station_btn = QPushButton()
        self.strength_label = QLabel()
        self.freq_label = QLabel()
        self.rds_info = self.fm_receiver.rds_panel_0
        self.channel_slider = FrequencySlider(
            self.current_station_freq/10**6, 87.5, 110.0
        )
        # --- Bottom Menu Buttons --- #
        self.menu_button_group = QButtonGroup()
        self.home_button = QPushButton("Home")
        self.stations_button = QPushButton("Stations")
        self.debug_button = QPushButton("Debug")
        # --- Station Buttons --- #
        self.title_label = QLabel("Available Stations")
        self.scroll_area = QScrollArea()
        self.stations_container = QWidget()
        self.stations_layout = QGridLayout()

        # --- Debug Widgets --- #
        #Controls
        self.rf_gain_control = self.fm_receiver._gain_win
        self.cuttoff_freq_control = self.fm_receiver._fir_cutoff_win
        self.transition_width_control = self.fm_receiver._fir_transition_width_win
        self.rds_panel_debug = self.fm_receiver.rds_panel_0_0

        # Widgets
        self.fm_demod_debug = self.fm_receiver._qtgui_freq_sink_x_1_win   
        self.waterfall_debug = self.fm_receiver._qtgui_waterfall_sink_x_0_win
        self.l_r_debug = self.fm_receiver._qtgui_freq_sink_x_1_0_win
        self.rds_constellation_debug = self.fm_receiver._qtgui_const_sink_x_0_win
        self.audio_debug = self.fm_receiver._qtgui_time_sink_x_0_win

        self.setup_ui()
        logger.info("Modern FM Radio UI created")

    def setup_ui(self):
        """Setup the main user interface"""
        self.setWindowTitle("GNU Radio FM Receiver")
        self.setMinimumSize(1200, 700)
        self.resize(1600, 900)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        self.stacked_widget = QStackedWidget()
        self.create_home_widget()
        self.create_stations_widget()
        self.create_debug_widget()
        self.stacked_widget.addWidget(self.home_widget) # ID 0  -> Home
        self.stacked_widget.addWidget(self.stations_widget) # ID 1 -> Scan
        self.stacked_widget.addWidget(self.debug_widget)    # ID 2 -> Debug
        self.create_bottom_menu()
        self.main_layout.addWidget(self.stacked_widget, 1)
        self.main_layout.addWidget(self.bottom_menu_widget, 0)

    def create_bottom_menu(self):
        """Create bottom menu with proper button group management"""
        self.bottom_menu_widget.setFixedHeight(60)
        bottom_menu_layout = QHBoxLayout(self.bottom_menu_widget)
        bottom_menu_layout.setContentsMargins(20, 10, 20, 10)
        # Home Button
        self.home_button.setCheckable(True)
        self.home_button.setChecked(True)
        self.home_button.setMinimumHeight(40)
        self.menu_button_group.addButton(self.home_button, 0)
        # Stations Button
        self.stations_button.setCheckable(True)
        self.stations_button.setMinimumHeight(40)
        self.menu_button_group.addButton(self.stations_button, 1)
        # Debug Button
        self.debug_button.setCheckable(True)
        self.debug_button.setMinimumHeight(40)
        self.menu_button_group.addButton(self.debug_button, 2)
        # Button Group
        self.menu_button_group.buttonClicked.connect(self.switch_page)
        bottom_menu_layout.addStretch()
        bottom_menu_layout.addWidget(self.home_button)
        bottom_menu_layout.addWidget(self.stations_button)
        bottom_menu_layout.addWidget(self.debug_button)
        bottom_menu_layout.addStretch()

    def switch_page(self, button):
        """Switch between pages based on button clicked"""
        button_id = self.menu_button_group.id(button)
        self.stacked_widget.setCurrentIndex(button_id)

    def create_debug_widget(self):
        """Create debug widget"""
        layout = QVBoxLayout(self.debug_widget)

        control_layout = QGridLayout()

        # === Tunning and Reception Conrols ===
        tunning_label = QLabel("Tuning & Reception Controls")
        tunning_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; margin-bottom: 20px;"
        )
        control_layout.addWidget(tunning_label, 0, 0, 1, 4)  # full-width header

        # === Gain Control ===
        control_layout.addWidget(self.rf_gain_control, 1, 0, 1, 4)
        # === Filter Control ===
        control_layout.addWidget(self.cuttoff_freq_control, 3, 0, 1, 2)
        control_layout.addWidget(self.transition_width_control , 3, 2, 1, 2)
        # control_layout.addWidget(self.rds_panel_debug, 4, 0, 1, 4)

        # # === Demodulation & Filtering ===
        # demod_label = QLabel("Demodulation & Filtering")
        # demod_label.setStyleSheet(
        #     "font-size: 16px; font-weight: bold; margin-bottom: 20px;"
        # )
        # control_layout.addWidget(demod_label, 2, 0, 1, 4)
        # tau = QComboBox()
        # tau.addItems(["75u", "50u"])
        # tau.currentTextChanged.connect(self.tau_control)
        # control_layout.addWidget(tau, 3, 0, 1, 2, Qt.AlignLeft)  # first control

        # another_control = QSlider(Qt.Horizontal)  # Just an example
        # control_layout.addWidget(another_control, 3, 2, 1, 2)  # second control

        # Stereo decoding toggle — mono vs stereo
        # Pilot tone lock indicator (on/off or locked status).
        # Bandwidth selection — adjustable LPF/HPF for baseband.
        # Freq Slider
        layout.addLayout(control_layout)

        # Tab section
        tab = QTabWidget()

        # RF Spectrum
        # tab.addTab(self.fm_receiver._qtgui_sink_x_0_win, 'RF Band')

        # FM Demod
        tab.addTab(self.fm_demod_debug,'Fm Demod')

        # Water Fall
        tab.addTab(self.waterfall_debug,'Water Fall')

        # L+R
        tab.addTab(self.l_r_debug,'L+R')

        # Constellation Receiver
        tab.addTab(self.rds_constellation_debug,'RDS Constellation')

        # Audio Plot
        tab.addTab(self.audio_debug, 'Audio')

        layout.addWidget(tab)
        # RDS Data
        layout.addWidget(self.rds_panel_debug)




    def create_stations_widget(self):
        """Create stations widget with proper layout and scroll area"""

        layout = QVBoxLayout(self.stations_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title

        self.title_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; margin-bottom: 20px;"
        )
        layout.addWidget(self.title_label)

        # Scrollable area for stations
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Container for grid layout
        self.stations_container.setLayout(self.stations_layout)
        self.scroll_area.setWidget(self.stations_container)
        layout.addWidget(self.scroll_area, stretch=1)
        # Fill grid
        if self.stations:
            self._populate_stations()
        else:
            no_stations_label = QLabel("No stations available")
            no_stations_label.setAlignment(Qt.AlignCenter)
            self.stations_layout.addWidget(no_stations_label, 0, 0, 2, 2)

        layout.addStretch()


    def _populate_stations(self):
        """Populate the stations grid with station buttons"""
        for i, station in enumerate(self.stations):
            row = i // 2
            col = i % 2
            station_btn = QPushButton(f"{station/10**6:.1f} FM")
            station_btn.setProperty("frequency", station)
            station_btn.setMinimumHeight(50)
            station_btn.setStyleSheet("""
                QPushButton {
                    font-size: 16px;
                    padding: 10px;
                    margin: 5px;
                }
            """)
            station_btn.clicked.connect(self.change_channel)
            self.stations_layout.addWidget(station_btn, row, col)

    def create_home_widget(self):
        """Create home widget"""
        layout = QVBoxLayout(self.home_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        control_widget = QWidget()
        control_layout = QGridLayout(control_widget)
        control_layout.setSpacing(15)
        # Sytle UI Elements
        self._create_control_buttons() # Mute,Scan,Record,Volume
        self._create_display_elements() # Strength, Freq
        # Arrange Elements on Home
        self._arrange_control_layout(control_layout)
        layout.addStretch()
        layout.addWidget(control_widget)
        layout.addStretch()

    def _create_control_buttons(self):
        """Create main control buttons"""
        # Mute Button
        self.mute_button.setText("Listen")
        self.mute_button.setCheckable(True)
        self.mute_button.setMinimumHeight(50)
        self.mute_button.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.mute_button.clicked.connect(self.fm_player)
        # Scan Button
        self.scan_btn_home.setText("Scan Stations")
        self.scan_btn_home.setMinimumHeight(50)
        self.scan_btn_home.setStyleSheet("font-size: 16px;")
        self.scan_btn_home.clicked.connect(self.scan_mode)
        # Record Button
        self.record_btn.setText("Record")
        self.record_btn.setMinimumHeight(50)
        self.record_btn.setStyleSheet("font-size: 16px;")
        # Volume slider
        self.volume_slider.setMinimumHeight(50)
        self.volume_slider.volumeChanged.connect(self.set_volume)
        # Previous/Next Button
        self.prev_station_btn.setText("◀ Previous")
        self.next_station_btn.setText("Next ▶")
        self.prev_station_btn.setMinimumHeight(40)
        self.next_station_btn.setMinimumHeight(40)
        self.prev_station_btn.clicked.connect(self.previous_station)
        self.next_station_btn.clicked.connect(self.next_station)


    def _create_display_elements(self):
        """Create display elements for signal and frequency"""
        # Strength label
        self.strength_label.setText("Signal Strength: --")
        self.strength_label.setAlignment(Qt.AlignCenter)
        self.strength_label.setStyleSheet("font-size: 14px;")
        # Freq Label
        self.freq_label.setText(f"{self.current_station_freq/10**6:.1f} FM")
        self.freq_label.setAlignment(Qt.AlignCenter)
        self.freq_label.setStyleSheet(
            "font-size: 32px; font-weight: bold; margin: 20px;"
        )

    def _arrange_control_layout(self, control_layout:QGridLayout):
        """Arrange all control elements in the grid layout"""
        # Row 0
        control_layout.addWidget(self.scan_btn_home, 0, 0, 1, 2)
        control_layout.addWidget(self.record_btn, 0, 2, 1, 2)
        control_layout.addWidget(self.strength_label, 0, 4, 1, 2)
        control_layout.addWidget(self.volume_slider,0,6,4,1)
        # Row 1
        control_layout.addWidget(self.prev_station_btn, 1, 0, 1, 2)
        control_layout.addWidget(self.freq_label, 1, 2, 1, 2)
        control_layout.addWidget(self.next_station_btn, 1, 4, 1, 2)
        # Row 2
        control_layout.addWidget(self.rds_info, 2, 0, 1, 6)
        control_layout.addWidget(self.channel_slider, 3, 0, 1, 6)
        control_layout.addWidget(self.mute_button, 4, 2, 1, 2)
        for i in range(6):
            control_layout.setColumnStretch(i, 1)

    def fm_player(self):
        """Toggle volume on/off"""
        if self.mute: # is muted --> unmute
            self.set_mute(False)
            self.mute_button.setText("Stop Listening")
        else:   # not muted --> mute
            self.mute_button.setText("Listen")
            self.set_mute(True)

    def scan_mode(self):
        self.stacked_widget.setCurrentIndex(1)
        self.stations_button.setChecked(True)
        self.scan_btn_home.setDisabled(True)
        self.set_mute(True)

        # Post scan logic
        self.set_freq(88e6)
        self.fm_receiver.set_mode(0)  # Scan mode
        self.fm_receiver.set_done(0)
        self.fm_receiver.set_freq_offset(0)

        self.samp_rate = self.fm_receiver.get_samp_rate()
        self.fm_receiver.set_samp_rate(2.048e6) # Increase bandwidth for faster scanning

        # Debug
        self.scanning_progress = "Scanning In Progress: "
        self.mute_button.setDisabled(True)

        # Thread setup
        self.worker = ScannerWorker(self.fm_receiver,88e6,110e6)
        self.worker.moveToThread(self.thread)

        # Signals and slots - connect first
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self._report_progress)
        self.worker.finished.connect(self.scan_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Now start the thread
        self.thread.start()

    @pyqtSlot(bool)
    def scan_finished(self, done:bool):
        """Handle completion of station scanning"""
        logger.info("Done Scanning")
        self.title_label.setText("Avaliable Stations")

        self.stations = self.fm_receiver.epy_block_0.get_staions()
        self.fm_receiver.set_mode(1)
        self.fm_receiver.set_freq_offset(250e3)
        self.fm_receiver.set_samp_rate(self.samp_rate)

        self.update_display()
        self.scan_btn_home.setDisabled(False)
        self.mute_button.setDisabled(False)

    def update_display(self):
        """Update the stations display"""
        self.stations = sorted(self.stations)
        while self.stations_layout.count():
            child = self.stations_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        for i, station in enumerate(self.stations):
            row = i // 2
            col = i % 2
            station_btn = QPushButton(f"{station/10**6:.1f} FM")
            station_btn.setProperty("frequency", station)
            station_btn.setMinimumHeight(50)
            station_btn.setStyleSheet("""
                QPushButton {
                    font-size: 16px;
                    padding: 10px;
                    margin: 5px;
                }
            """)
            station_btn.clicked.connect(self.change_channel)
            self.stations_layout.addWidget(station_btn, row, col)


    def _report_progress(self, value):
        """Report scanning progress"""
        self.set_freq(value)
        self.fm_receiver.set_done(0)
        self.scanning_progress +=f"{value/1e6:.1f} MHz, "

        self.title_label.setText(self.scanning_progress)

    def change_channel(self):
        """Change to selected station and switch to home view"""
        button = self.sender()
        freq = button.property("frequency")
        self.set_freq(freq)
        self.stacked_widget.setCurrentIndex(0)
        self.home_button.setChecked(True)

    def set_volume(self, value:int):
        # Logic to set volume
        self.volume_slider.setVolume(value)
        mapped_value = max(min(value, 100), 0)
        vol = (mapped_value / 100) * 30 - 20
        self.fm_receiver.set_volume(vol)
        return

    def get_freq(self):
        return self.current_station_freq

    def set_freq(self, freq):
        """Set frequency and update display"""
        self.freq_label.setText(f"{freq/10**6:.1f} FM")
        self.fm_receiver.set_freq(freq/10**6)
        self.channel_slider.setValue(freq/10**6)
        self.current_station_freq = freq

    def previous_station(self):
        """Navigate to previous station in the list"""
        if not self.stations:
            return
        try:
            current_index = self.stations.index(int(self.current_station_freq))
        except ValueError:
            current_index = 0
            for i, station in enumerate(self.stations):
                if station < self.current_station_freq:
                    current_index = i
                else:
                    break
        previous_index = (current_index - 1) % len(self.stations)
        previous_freq = self.stations[previous_index]
        self.set_freq(previous_freq)
        self.current_station_index = previous_index

    def next_station(self):
        """Navigate to next station in the list"""
        if not self.stations:
            return
        try:
            current_index = self.stations.index(int(self.current_station_freq))
        except ValueError:
            current_index = len(self.stations) - 1
            for i, station in enumerate(self.stations):
                if station > self.current_station_freq:
                    current_index = i
                    break
        next_index = (current_index + 1) % len(self.stations)
        next_freq = self.stations[next_index]
        self.set_freq(next_freq)
        self.current_station_index = next_index

    def tau_control(self,value):
        numeric_value = float(value.replace("u", "")) * 1e-6

        self.fm_receiver.set_tau(numeric_value)

    def load_config(self, rx:rds_rx):
        self.stations = self.config_manager.get('stations')
        rx.set_mute(1)

    def save_config(self):
        self.config_manager.set('stations', self.stations)
        self.config_manager.save()

    def set_mute(self,x:bool):
        self.fm_receiver.set_mute(x)
        self.mute = x

    def close_event(self, event):
        """Handle window close event"""
        self.fm_receiver.stop()
        self.fm_receiver.wait()
        self.save_config()
        logger.info("Application closing")
        event.accept()
        return None
    