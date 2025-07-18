from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QLabel, QSlider,
                             QVBoxLayout, QWidget)


class FrequencySlider(QWidget):
    valueChanged = pyqtSignal(float)
    
    def __init__(self, current_freq, min_freq=87.5, max_freq=108.0, parent=None):
        super().__init__(parent)
        self.min_freq = min_freq
        self.max_freq = max_freq
        self.current_freq = current_freq
        self.setMinimumSize(400, 80)
        self.setMaximumHeight(80)
        
        # Mouse tracking
        self.setMouseTracking(True)
        self.dragging = False
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get widget dimensions
        w = self.width()
        h = self.height()
        
        # Define slider track area
        track_y = h // 2
        track_start = 40
        track_end = w - 40
        track_width = track_end - track_start
        
        # Draw main track line
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.drawLine(track_start, track_y, track_end, track_y)
        
        # Draw frequency markers and labels
        painter.setFont(QFont("Arial", 8))
        
        # Major ticks every 5 MHz
        for freq in range(int(self.min_freq), int(self.max_freq) + 1, 5):
            if freq >= self.min_freq and freq <= self.max_freq:
                x = track_start + (freq - self.min_freq) / (self.max_freq - self.min_freq) * track_width
                
                # Major tick
                painter.setPen(QPen(QColor(80, 80, 80), 2))
                painter.drawLine(int(x), track_y - 8, int(x), track_y + 8)
                
                # Label
                painter.setPen(QPen(QColor(60, 60, 60), 1))
                painter.drawText(int(x) - 10, track_y + 25, f"{freq}")
        
        # Minor ticks every 1 MHz
        for freq_minor in range(int(self.min_freq), int(self.max_freq) + 1, 1):
            if freq_minor % 5 != 0:  # Skip major ticks
                x = track_start + (freq_minor - self.min_freq) / (self.max_freq - self.min_freq) * track_width
                painter.setPen(QPen(QColor(120, 120, 120), 1))
                painter.drawLine(int(x), track_y - 4, int(x), track_y + 4)
        
        # Draw slider handle
        handle_x = track_start + (self.current_freq - self.min_freq) / (self.max_freq - self.min_freq) * track_width
        
        # Handle shadow
        painter.setBrush(QBrush(QColor(0, 0, 0, 50)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(int(handle_x) - 8, track_y - 8, 18, 18)
        
        # Handle
        painter.setBrush(QBrush(QColor(70, 130, 180)))
        painter.setPen(QPen(QColor(50, 100, 150), 2))
        painter.drawEllipse(int(handle_x) - 8, track_y - 8, 16, 16)
        
        # Handle center dot
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(int(handle_x) - 2, track_y - 2, 4, 4)
        
        # Draw current frequency display
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.setPen(QPen(QColor(70, 130, 180), 1))
        freq_text = f"{self.current_freq:.1f} MHz"
        painter.drawText(int(handle_x) - 30, track_y - 20, freq_text)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.updateFrequency(event.x())
    
    def mouseMoveEvent(self, event):
        if self.dragging:
            self.updateFrequency(event.x())
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
    
    def updateFrequency(self, x):
        track_start = 40
        track_end = self.width() - 40
        
        # Clamp x to track bounds
        x = max(track_start, min(track_end, x))
        
        # Calculate frequency
        ratio = (x - track_start) / (track_end - track_start)
        self.current_freq = self.min_freq + ratio * (self.max_freq - self.min_freq)
        
        # Round to nearest 0.1 MHz
        self.current_freq = round(self.current_freq, 1)
        
        self.update()
        self.valueChanged.emit(self.current_freq)
    
    def setValue(self, freq):
        """Set the frequency value programmatically"""
        self.current_freq = max(self.min_freq, min(self.max_freq, freq))
        self.update()
        self.valueChanged.emit(self.current_freq)
    
    def getValue(self):
        """Get the current frequency value"""
        return self.current_freq
