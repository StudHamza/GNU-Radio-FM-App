"""
Control Panel Widget - Frequency and Volume Controls
"""
import logging
from qtpy.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QSlider, QDoubleSpinBox, QPushButton)
from qtpy.QtCore import Qt, Signal

logger = logging.getLogger(__name__)

class ControlPanel(QWidget):
    """Control panel for frequency and volume"""
    
    # Signals
    frequency_changed = Signal(float)
    volume_changed = Signal(int)
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setup_ui()
    
    def setup_ui(self):
        """Setup control panel UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Radio Controls")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # Frequency control
        freq_layout = QVBoxLayout()
        
        freq_label = QLabel("Frequency (MHz)")
        freq_layout.addWidget(freq_label)
        
        self.frequency_spin = QDoubleSpinBox()
        self.frequency_spin.setRange(88.0, 108.0)
        self.frequency_spin.setSingleStep(0.1)
        self.frequency_spin.setDecimals(1)
        self.frequency_spin.setValue(88.5)
        self.frequency_spin.valueChanged.connect(self.on_frequency_changed)
        freq_layout.addWidget(self.frequency_spin)
        
        layout.addLayout(freq_layout)
        
        # Volume control
        vol_layout = QVBoxLayout()
        
        vol_label = QLabel("Volume")
        vol_layout.addWidget(vol_label)
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        vol_layout.addWidget(self.volume_slider)
        
        self.volume_label = QLabel("50%")
        vol_layout.addWidget(self.volume_label)
        
        layout.addLayout(vol_layout)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.toggle_play)
        button_layout.addWidget(self.play_button)
        
        self.scan_button = QPushButton("Scan")
        self.scan_button.clicked.connect(self.start_scan)
        button_layout.addWidget(self.scan_button)
        
        layout.addLayout(button_layout)
        
        # Add stretch to push everything to top
        layout.addStretch()
    
    def set_frequency(self, frequency):
        """Set frequency value"""
        self.frequency_spin.setValue(frequency)
    
    def set_volume(self, volume):
        """Set volume value"""
        self.volume_slider.setValue(volume)
        self.volume_label.setText(f"{volume}%")
    
    def on_frequency_changed(self, frequency):
        """Handle frequency change"""
        self.frequency_changed.emit(frequency)
    
    def on_volume_changed(self, volume):
        """Handle volume change"""
        self.volume_label.setText(f"{volume}%")
        self.volume_changed.emit(volume)
    
    def toggle_play(self):
        """Toggle play/stop"""
        if self.play_button.text() == "Play":
            self.play_button.setText("Stop")
            logger.info("Starting playback")
        else:
            self.play_button.setText("Play")
            logger.info("Stopping playback")
    
    def start_scan(self):
        """Start frequency scan"""
        logger.info("Starting frequency scan")
        # This would start actual scanning