"""
Spectrum Analyzer Widget
"""
import numpy as np
from qtpy.QtWidgets import QWidget, QVBoxLayout, QLabel
from qtpy.QtCore import QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class SpectrumWidget(QWidget):
    """Widget for displaying spectrum analyzer"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_plot()
        
        # Timer for updating plot
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_plot)
        self.update_timer.start(200)  # Update every 200ms
    
    def setup_ui(self):
        """Setup spectrum widget UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Spectrum Analyzer")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(10, 4))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
    
    def setup_plot(self):
        """Setup the spectrum plot"""
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel('Frequency (MHz)')
        self.ax.set_ylabel('Power (dB)')
        self.ax.set_title('FM Spectrum')
        self.ax.grid(True, alpha=0.3)
        
        # Initialize with dummy data
        self.frequencies = np.linspace(88, 108, 1000)
        self.powers = np.random.normal(-60, 10, 1000)
        
        self.line, = self.ax.plot(self.frequencies, self.powers)
        self.ax.set_xlim(88, 108)
        self.ax.set_ylim(-80, -20)
        
        self.figure.tight_layout()
    
    def update_plot(self):
        """Update spectrum plot with new data"""
        # Generate mock spectrum data
        self.powers = np.random.normal(-60, 10, 1000)
        
        # Add some "stations" at specific frequencies
        stations = [89.1, 91.5, 95.7, 99.3, 103.8, 107.1]
        for freq in stations:
            idx = int((freq - 88) / 20 * 1000)
            if 0 <= idx < len(self.powers):
                self.powers[idx] += np.random.normal(20, 5)
        
        # Update plot
        self.line.set_ydata(self.powers)
        self.canvas.draw_idle()