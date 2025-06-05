"""
RDS Information Display Panel
"""
from qtpy.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame

class RDSPanel(QWidget):
    """Panel for displaying RDS information"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup RDS panel UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("RDS Information")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # Create frame for RDS info
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        frame_layout = QVBoxLayout(frame)
        
        # Station name
        self.station_label = QLabel("Station: --")
        frame_layout.addWidget(self.station_label)
        
        # Song info
        self.song_label = QLabel("Song: --")
        frame_layout.addWidget(self.song_label)
        
        # Artist info
        self.artist_label = QLabel("Artist: --")
        frame_layout.addWidget(self.artist_label)
        
        # Signal strength
        self.signal_label = QLabel("Signal: --")
        frame_layout.addWidget(self.signal_label)
        
        layout.addWidget(frame)
        layout.addStretch()
    
    def update_station_info(self, station_name):
        """Update station information"""
        self.station_label.setText(f"Station: {station_name}")
        # Mock some additional info
        self.song_label.setText("Song: Demo Track")
        self.artist_label.setText("Artist: Demo Artist")
        self.signal_label.setText("Signal: Strong")