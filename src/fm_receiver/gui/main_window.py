"""
Modern FM Radio Main Window

This module implements a comprehensive FM Radio application using GNU Radio for
signal processing and PyQt5 for the graphical user interface. The application
provides FM radio reception, station scanning, recording capabilities, and
debugging tools for SDR-based radio reception.
"""
from datetime import datetime
import logging
import os

from core.config_manager import ConfigManager
from flowgraphs.rds_rx import rds_rx
from flowgraphs.MultipleRecorder import MultipleRecorder
# pylint: disable=no-name-in-module
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QTimer
from PyQt5.QtWidgets import (QButtonGroup, QCheckBox, QComboBox, QGridLayout,
                             QHBoxLayout, QLabel, QLineEdit, QListWidget,
                             QMainWindow, QPushButton, QScrollArea,
                             QSizePolicy, QSlider, QSpinBox, QStackedWidget,
                             QTabWidget, QTextEdit, QVBoxLayout, QWidget, QAction,QFileDialog, QMessageBox)

from .frequency_slider import FrequencySlider
from .scan_thread import ScannerWorker
from .volume_slider import VolumeSlider
from .station_button import StationButton
from .info_window import InfoWindow

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Modern FM Radio Main Window GUI Controller.
    
    This class provides the main user interface for the FM Radio application,
    integrating GNU Radio signal processing with PyQt5 GUI components. It manages
    radio reception, station scanning, audio recording, and provides debugging
    tools for SDR operations.
    
    The interface is organized into three main views:
    - Home: Primary controls and frequency display
    - Stations: Grid of discovered stations
    - Debug: Signal analysis and diagnostic tools
    
    Attributes:
        config_manager (ConfigManager): Handles configuration persistence
        volume (int): Current audio volume level (0-100)
        mute (bool): Audio mute state flag
        recording (bool): Recording state flag
        outdir (str): Directory path for saving recordings
        stations (list): List of discovered FM frequencies in Hz
        fm_receiver (rds_rx): GNU Radio flowgraph for FM processing
        current_station_freq (float): Currently tuned frequency in Hz
        current_station_index (int): Index of current station in stations list
        samp_rate (float): SDR sample rate in Hz
    """
    def __init__(self, config_path:str, sdr_serial:int):
        """Initialize the FM Radio main window.
        
        Sets up the complete FM Radio application including GNU Radio flowgraph,
        UI components, configuration management, and signal processing chain.
        
        Args:
            config_path (str): Path to configuration file for persistence
            sdr_serial (int): Serial number/identifier for SDR device
            
        Raises:
            RuntimeError: If GNU Radio flowgraph initialization fails
            IOError: If configuration file cannot be accessed
        """
        super().__init__()

        self.config_manager = ConfigManager(config_path)
        self.volume = 0
        self.mute = True
        self.recording = False
        self.outdir = ""
        self.scan_requested = pyqtSignal()
        self.stations = []
        self.fm_receiver = rds_rx(serial=sdr_serial)
        self.load_config()
        self.current_station_freq = self.stations[0]
        self.current_station_index = 0
        self.samp_rate = self.fm_receiver.get_samp_rate()
        self.recorders = []

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
        self._init_receiver()
        self.fm_receiver.start()
        logger.info("Modern FM Radio UI created")

    def setup_ui(self):
        """Setup the main user interface layout and components.
        
        Creates the complete UI structure including menu bar, main content area
        with stacked widgets for different views, and bottom navigation menu.
        Establishes the overall window properties and layout hierarchy.
        """
        self.setWindowTitle("GNU Radio FM Receiver")
        self.setMinimumSize(1200, 700)
        self.resize(1600, 900)

        # Create the top menu
        self.create_top_menu()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        self.stacked_widget = QStackedWidget()
        self.create_home_widget()
        self.create_stations_widget()
        self.create_debug_widget()

        self.stacked_widget.addWidget(self.home_widget)    # ID 0 -> Home
        self.stacked_widget.addWidget(self.stations_widget) # ID 1 -> Scan
        self.stacked_widget.addWidget(self.debug_widget)    # ID 2 -> Debug

        self.create_bottom_menu()
        self.main_layout.addWidget(self.stacked_widget, 1)
        self.main_layout.addWidget(self.bottom_menu_widget, 0)


    def create_top_menu(self):
        """Create the application menu bar with File menu.
        
        Sets up the top-level menu structure with File menu containing
        recording directory selection functionality.
        """
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("File")
        save_action = QAction("Record Directory", self)
        file_menu.addAction(save_action)

        # Audio Menu
        # audio_menu = menu_bar.addMenu("Audio")

        save_action.triggered.connect(self.save_file)


    def create_bottom_menu(self):
        """Create bottom navigation menu with view switching buttons.
        
        Sets up the bottom navigation bar with Home, Stations, and Debug
        buttons using a button group for exclusive selection. Configures
        button properties and connects switching signals.
        """
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

    def switch_page(self, button:QPushButton):
        """Switch between main application views based on button selection.
        
        Handles navigation between Home, Stations, and Debug views by
        updating the stacked widget's current index.
        
        Args:
            button (QPushButton): The navigation button that was clicked
        """
        button_id = self.menu_button_group.id(button)
        self.stacked_widget.setCurrentIndex(button_id)

    def create_debug_widget(self):
        """Create the debug interface with controls and visualization widgets.
        
        Sets up comprehensive debugging interface including:
        - RF gain and filter controls from GNU Radio flowgraph
        - Tabbed visualization displays (spectrum, waterfall, constellation)
        - RDS debugging panel
        
        Organizes controls in a grid layout with labeled sections.
        """
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

        # # === Demodulation & Filtering ===
        # demod_label = QLabel("Demodulation & Filtering")
        # demod_label.setStyleSheet(
        #     "font-size: 16px; font-weight: bold; margin-bottom: 20px;"
        # )
        # control_layout.addWidget(demod_label, 2, 0, 1, 4)
        tau = QComboBox()
        tau.addItems(["75u", "50u"])
        tau.currentTextChanged.connect(self.tau_control)
        control_layout.addWidget(tau, 4, 0, 1, 2, Qt.AlignLeft)  # first control

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
        """Create the stations selection interface with scrollable grid.
        
        Sets up a scrollable grid layout containing buttons for all discovered
        FM stations. Handles both populated and empty states with appropriate
        user feedback.
        """
        layout = QVBoxLayout(self.stations_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title

        self.title_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; margin-bottom: 20px;"
        )
        self.title_label.setWordWrap(True)
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
            station_btn = StationButton(station)
            station_btn.clicked.connect(self.change_channel)
            station_btn.delete_clicked.connect(self.delete_station)
            station_btn.record_clicked.connect(self.multiple_record)

            self.stations_layout.addWidget(station_btn, row, col)

    def create_home_widget(self):
        """Create the main control interface (Home view).
        
        Sets up the primary user interface containing frequency display,
        control buttons, volume slider, RDS information, and manual tuning
        controls. Arranges all elements in a responsive grid layout.
        """
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
        """Create and configure main control buttons.
        
        Sets up the primary control buttons including mute/listen toggle,
        station scanning, recording control, volume slider, and station
        navigation buttons. Configures styling and connects signal handlers.
        """
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
        self.record_btn.clicked.connect(self.record)
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
        """Arrange all control elements in the home view grid layout.
        
        Organizes buttons, displays, and controls in a structured 6-column
        grid layout with proper spacing and stretch configuration.
        
        Args:
            control_layout (QGridLayout): The grid layout to populate
        """
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
            self.mute_button.setText("Stop Listening")
            self.mute_button.setChecked(True)
            self.set_mute(False)
        else:   # not muted --> mute
            self.mute_button.setText("Listen")
            self.mute_button.setChecked(False)
            self.set_mute(True)

    def scan_mode(self):
        """Initiate FM band scanning for station discovery.
        
        Starts background scanning process across the FM band (88-108 MHz)
        to discover available stations. Switches to wideband mode for faster
        scanning and creates a worker thread for non-blocking operation.
        Updates UI to show scanning progress and disables controls during scan.
        """

        self.switch_page(self.stations_button)

        if not self.mute: # If not mutted --> Mute
            self.fm_player()

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
        """Handle completion of station scanning process.
        
        Processes the results of the scanning operation, updates the stations
        list, restores normal receiver mode, and updates the UI. Re-enables
        controls and switches back to the home view.
        
        Args:
            done (bool): Indicates whether scanning completed successfully
        """
        logger.info("Done Scanning")
        self.title_label.setText("Avaliable Stations")

        self.stations = self.fm_receiver.epy_block_0.get_staions()
        self.fm_receiver.set_mode(1)
        self.fm_receiver.set_freq_offset(250e3)
        self.fm_receiver.set_samp_rate(self.samp_rate)

        self.update_display()
        self.scan_btn_home.setDisabled(False)
        self.mute_button.setDisabled(False)

        self.switch_page(self.home_button)
        self.set_freq(self.stations[0])


    def update_display(self):
        """Update the stations display with newly discovered stations.
        
        Clears the existing stations grid and repopulates it with buttons
        for all discovered stations, sorted by frequency. Creates new
        station buttons with proper styling and signal connections.
        """
        self.stations = sorted(self.stations)
        while self.stations_layout.count():
            child = self.stations_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self._populate_stations()


    def _report_progress(self, value:float):
        """Report scanning progress updates to the user interface.
        
        Called by the scanner thread to update the scanning progress display.
        Updates the current frequency being scanned and accumulates progress
        information for user feedback.
        
        Args:
            value (float): Current frequency being scanned in Hz
        """
        self.set_freq(value)
        self.fm_receiver.set_done(0)
        self.scanning_progress +=f"{value/1e6:.1f} MHz, "

        self.title_label.setText(self.scanning_progress)

    def change_channel(self):
        """Handle station button clicks to change frequency.
        
        Extracts the frequency from the clicked station button, tunes to
        that frequency, and switches to the home view for immediate playback.
        """
        button:StationButton = self.sender()
        freq = button.get_freq()
        logger.info(f"Setting Frequency to {freq}")
        self.set_freq(freq)
        self.stacked_widget.setCurrentIndex(0)
        self.home_button.setChecked(True)

    def delete_station(self):
        """Handles deletion of station
        
        Removes the clicked station from the station list and redisplays the list
        """
        button:StationButton = self.sender()
        self.stations.remove(button.get_freq())
        self.update_display()

    def record_station(self)->None:
        pass

    def set_volume(self, value:int):
        """Set audio volume level and update display.
        
        Maps the UI volume scale (0-100) to the receiver's dB scale and
        updates both the volume slider display and the GNU Radio receiver.
        
        Args:
            value (int): Volume level from 0-100
        """
        self.volume = value
        self.volume_slider.setVolume(value)
        mapped_value = max(min(value, 100), 0)
        vol = (mapped_value / 100) * 30 - 20
        self.fm_receiver.set_volume(vol)
        return

    def get_freq(self):
        """Get the current tuned frequency.
        
        Returns:
            float: Current frequency in Hz
        """
        return self.current_station_freq

    def set_freq(self, freq):
        """Set the radio frequency and update all related displays.
        
        Tunes the GNU Radio receiver to the specified frequency and updates
        the frequency display label and manual tuning slider position.
        
        Args:
            freq (float): Frequency to tune to in Hz
        """
        self.freq_label.setText(f"{freq/10**6:.1f} FM")
        self.fm_receiver.set_freq(freq/10**6)
        self.channel_slider.setValue(freq/10**6)
        self.current_station_freq = freq

    def previous_station(self):
        """Navigate to the previous station in the discovered stations list.
        
        Moves to the previous station in the sorted stations list, wrapping
        around to the last station if currently on the first. Handles cases
        where the current frequency is not exactly in the stations list.
        """
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
        """Navigate to the next station in the discovered stations list.
        
        Moves to the next station in the sorted stations list, wrapping
        around to the first station if currently on the last. Handles cases
        where the current frequency is not exactly in the stations list.
        """
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
        """Control the FM deemphasis time constant (tau).
        
        Converts the string representation of tau value to numeric format
        and configures the GNU Radio receiver's deemphasis filter.
        
        Args:
            value (str): Time constant value (e.g., "75u", "50u")
        """
        numeric_value = float(value.replace("u", "")) * 1e-6

        self.fm_receiver.set_tau(numeric_value)

    def record(self):
        """Toggle audio recording state.
        
        Starts or stops audio recording to a timestamped WAV file in the
        configured output directory. Updates button text to reflect current
        recording state and manages the GNU Radio WAV file sink.
        """
        if self.recording is False:
            self.recording = True
            self.record_btn.setText("Recording")
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            file_name = os.path.join(self.outdir,f"{current_time}.wav")
            self.fm_receiver.blocks_wavfile_sink_0.open(file_name)
        else:
            self.recording = False
            self.record_btn.setText("Record")
            self.fm_receiver.blocks_wavfile_sink_0.close()

    def multiple_record(self):
        """

        Checks if current button frequency in proximity of the SDR, if so it detection frequency offset and stops the flowgraph to connect a 
        recorder block.
        """
        button:StationButton = self.sender()
        # Check if can record based on proximity
        if abs(freq_off:=(self.get_freq()-button.get_freq())) > self.fm_receiver.get_samp_rate():
            logger.info("Cannot record this frequency")
            self.info = InfoWindow("This channel is out of your SDR center Frequency proximity",
                                   timeout=2000)
            self.info.show()
            return

        # In proximity
        #button.set_recording_state(not button.get_recording())
        # Stop current flowgraph to rewire
        self.fm_receiver.stop()
        self.fm_receiver.wait()

        if button.get_recording() is False: # Start Recording
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            file_name = os.path.join(self.outdir,f"{current_time}_{int(button.get_freq())}.wav")
            logger.info(f"Frequency Offset is {freq_off}")
            self.recorders.append (MultipleRecorder(
                    fname=file_name,
                    freq=self.get_freq(),
                    freq_offset=int(freq_off),
                )
            )
            self.fm_receiver.connect((self.fm_receiver.blocks_selector_0, 1),
                                     (self.recorders[0], 0))
            button.set_recording_state(True)

        else:
            self.fm_receiver.disconnect((self.fm_receiver.blocks_selector_0, 1),
                            (self.recorders[0], 0))
            button.set_recording_state(False)

        self.fm_receiver.start()





    def save_file(self):
        """Open directory selection dialog for recording output.
        
        Presents a directory selection dialog to the user for choosing where
        audio recordings should be saved. Updates the output directory path
        and provides user feedback on the selection status.
        """
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")

        if dir_path:
            self.outdir = dir_path
            logger.info(f"Output directory set to: {self.outdir}")
        else:
            QMessageBox.information(self, "No Directory Selected", "Output directory was not set.")

    def load_config(self):
        """Load application configuration from persistent storage.
        
        Retrieves saved settings including station list, volume level, and
        output directory from the configuration manager. Sets default values
        for any missing configuration items.
        """
        self.stations = self.config_manager.get('stations')
        self.volume = self.config_manager.get('volume')
        #self.outdir = self.config_manager.get('outdir')
        self.outdir = os.path.join((os.getcwd()),"downloads")

    def _init_receiver(self):
        """Initialize GNU Radio receiver with current settings.
        
        Configures the receiver with the current frequency, volume, and mute
        settings. Ensures the WAV file sink is properly closed to prevent
        file handle leaks.
        
        Note: This method is currently unused but preserved for future use.
        """
        self.set_freq(self.current_station_freq)
        self.set_volume(self.volume)
        self.set_mute(int(self.mute))

        # Close Open file
        self.fm_receiver.blocks_wavfile_sink_0.close()


    def save_config(self):
        """Save current application state to persistent storage.
        
        Stores the current stations list, volume setting, and output directory
        to the configuration manager for restoration on next application start.
        """
        self.config_manager.set('stations', self.stations)
        self.config_manager.set('volume',self.volume)
        self.config_manager.set('outdir',self.outdir)
        self.config_manager.save()

    def set_mute(self,x:bool):
        """Set the audio mute state in the GNU Radio receiver.
        
        Controls audio output by setting the mute parameter in the receiver
        and updating the internal mute state tracking.
        
        Args:
            mute_state (bool): True to mute audio, False to unmute
        """
        self.fm_receiver.set_mute(x)
        self.mute = x

    def closeEvent(self, event):
        """Handle application window close event.
        
        Performs cleanup operations before application shutdown including
        stopping the GNU Radio flowgraph, saving configuration, and ensuring
        proper resource cleanup.
        
        Args:
            event (QCloseEvent): The close event object from Qt
        """
        self.save_config()
        self.setEnabled(False)
        try:
            self.fm_receiver.stop()
            self.fm_receiver.wait()
        except Exception as e:
            logger.exception("Error stopping flowgraph: %s", e)
        logger.info("Application closing")
        event.accept()
    