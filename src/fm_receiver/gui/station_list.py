"""
Station List Widget
"""
from qtpy.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QScrollArea, QFrame, QSizePolicy,QStyle)
from qtpy.QtCore import Qt, Signal, QSize
from qtpy.QtGui import QPixmap, QFont

class StationList(QWidget):
    """List of radio stations with RDS info"""
    
    station_selected = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.stations = []
        self.setup_ui()
    
    def setup_ui(self):
        """Setup station list UI"""
        # self.setStyleSheet("""
        #     QWidget {
        #         background-color: #2d2d2d;
        #     }
        #     QScrollArea {
        #         border: none;
        #     }
        # """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Container for stations
        self.station_container = QWidget()
        self.station_layout = QVBoxLayout(self.station_container)
        self.station_layout.setContentsMargins(10, 10, 10, 10)
        self.station_layout.setSpacing(5)
        
        scroll_area.setWidget(self.station_container)
        layout.addWidget(scroll_area)
    
    def load_stations(self, stations):
        """Load stations into the list"""
        self.stations = stations
        self.clear_stations()
        
        for station in stations:
            station_widget = StationWidget(station)
            station_widget.clicked.connect(lambda s=station: self.station_selected.emit(s))
            self.station_layout.addWidget(station_widget)
        
        # Add stretch at the end
        self.station_layout.addStretch()
    
    def clear_stations(self):
        """Clear all station widgets"""
        while self.station_layout.count():
            child = self.station_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

class StationWidget(QFrame):
    """Individual station widget"""
    
    clicked = Signal()
    
    def __init__(self, station_data):
        super().__init__()
        self.station_data = station_data
        self.setup_ui()
    
    def setup_ui(self):
        """Setup station widget UI"""
        # self.setStyleSheet("""
        #     StationWidget {
        #         background-color: #3d3d3d;
        #         border-radius: 8px;
        #         margin: 2px;
        #     }
        #     StationWidget:hover {
        #         background-color: #4d4d4d;
        #     }
        #     QLabel {
        #         color: #ffffff;
        #         background-color: transparent;
        #     }
        #     QPushButton {
        #         background-color: #ff4444;
        #         border: none;
        #         border-radius: 15px;
        #         color: white;
        #         font-weight: bold;
        #         padding: 5px;
        #     }
        #     QPushButton:hover {
        #         background-color: #ff6666;
        #     }
        #     QPushButton.record {
        #         background-color: #ff4444;
        #     }
        #     QPushButton.record:hover {
        #         background-color: #ff6666;
        #     }
        # """)
        
        self.setFixedHeight(80)
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Album art placeholder
        art_label = QLabel()
        art_label.setFixedSize(60, 60)
        # art_label.setStyleSheet("""
        #     QLabel {
        #         background-color: #ffa500;
        #         border-radius: 8px;
        #         border: 2px solid #ffb733;
        #     }
        # """)
        art_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        art_label.setText("🎵")
        layout.addWidget(art_label)
        
        # Station info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        # Station name
        name_label = QLabel(self.station_data['name'])
        name_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        info_layout.addWidget(name_label)
        
        # Artist and song
        artist_song = f"{self.station_data['artist']} - {self.station_data['song']}"
        artist_label = QLabel(artist_song)
        artist_label.setFont(QFont("Arial", 10))
        artist_label.setStyleSheet("color: #aaa;")
        info_layout.addWidget(artist_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Play button
        play_icon = self.style().standardIcon(QStyle.SP_MediaPlay)
        play_btn = QPushButton(play_icon,"")
        play_btn.setFixedSize(30, 30)
        play_btn.clicked.connect(self.play_clicked)
        button_layout.addWidget(play_btn)
        
        # Record button
        record_btn = QPushButton("🔴")
        record_btn.setFixedSize(30, 30)
        record_btn.setProperty("class", "record")
        record_btn.clicked.connect(self.record_clicked)
        button_layout.addWidget(record_btn)
        
        layout.addLayout(button_layout)
    
    def play_clicked(self):
        """Handle play button click"""
        self.clicked.emit()
    
    def record_clicked(self):
        """Handle record button click"""
        # This would start recording
        pass
    
    def mousePressEvent(self, event):
        """Handle mouse click on station"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)