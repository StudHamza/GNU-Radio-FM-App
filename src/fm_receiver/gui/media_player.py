"""
Bottom Media Player Widget
"""

from qtpy.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                           QPushButton, QSlider, QFrame, QSizePolicy,QApplication,QStyle)
from qtpy.QtCore import Qt, Signal, QTimer
from qtpy.QtGui import QFont, QPixmap

class MediaPlayer(QWidget):
    """Bottom media player controls"""
    
    play_clicked = Signal()
    
    def __init__(self):
        super().__init__()
        self.current_track = None
        self.is_playing = False
        self.setup_ui()
    
    def setup_ui(self):
        """Setup media player UI"""
        # self.setStyleSheet("""
        #     QWidget {
        #         background-color: #1a1a1a;
        #         border-top: 1px solid #333;
        #     }
        #     QPushButton {
        #         background-color: transparent;
        #         border: none;
        #         color: #fff;
        #         font-size: 16px;
        #         padding: 8px;
        #         border-radius: 20px;
        #     }
        #     QPushButton:hover {
        #         background-color: #3d3d3d;
        #     }
        #     QPushButton.play {
        #         background-color: #ff4444;
        #         color: white;
        #         font-size: 14px;
        #         padding: 12px;
        #     }
        #     QPushButton.play:hover {
        #         background-color: #ff6666;
        #     }
        #     QSlider::groove:horizontal {
        #         border: none;
        #         height: 4px;
        #         background-color: #3d3d3d;
        #         border-radius: 2px;
        #     }
        #     QSlider::handle:horizontal {
        #         background-color: #ff4444;
        #         width: 12px;
        #         height: 12px;
        #         border-radius: 6px;
        #         margin: -4px 0;
        #     }
        #     QSlider::sub-page:horizontal {
        #         background-color: #ff4444;
        #         border-radius: 2px;
        #     }
        #     QLabel {
        #         color: #fff;
        #         background-color: transparent;
        #     }
        # """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Current track info
        track_layout = QVBoxLayout()
        
        self.track_name = QLabel("No track selected")
        self.track_name.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        track_layout.addWidget(self.track_name)
        
        self.track_artist = QLabel("")
        self.track_artist.setFont(QFont("Arial", 10))
        self.track_artist.setStyleSheet("color: #aaa;")
        track_layout.addWidget(self.track_artist)
        
        layout.addLayout(track_layout)
        layout.addStretch()
        
        # Media controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        
        # Previous button
        prev_icon = self.style().standardIcon(QStyle.SP_MediaSeekBackward)
        prev_btn = QPushButton(prev_icon,"")
        prev_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
        """)
        prev_btn.setFixedSize(40, 40)
        controls_layout.addWidget(prev_btn)
        
        # Play/Pause button
        play_icon = self.style().standardIcon(QStyle.SP_MediaPlay)
        self.play_btn = QPushButton(play_icon,"")
        self.play_btn.setFixedSize(50, 50)
        self.play_btn.setProperty("class", "play")
        self.play_btn.clicked.connect(self.toggle_play)
        controls_layout.addWidget(self.play_btn)
        
        # Next button
        next_icon = self.style().standardIcon(QStyle.SP_MediaSeekForward)
        next_btn = QPushButton(next_icon,"")
        next_btn.setFixedSize(40, 40)
        next_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
        """)
        controls_layout.addWidget(next_btn)
        
        layout.addLayout(controls_layout)
        layout.addStretch()
        
        # Volume and recording
        right_layout = QHBoxLayout()
        right_layout.setSpacing(15)
        
        # Record button
        record_btn = QPushButton("🔴")
        right_layout.addWidget(record_btn)
        
        # Volume control
        volume_btn = QPushButton("🔊")
        volume_btn.setFixedSize(30, 30)
        right_layout.addWidget(volume_btn)
        
        volume_slider = QSlider(Qt.Orientation.Horizontal)
        volume_slider.setFixedWidth(100)
        volume_slider.setRange(0, 100)
        volume_slider.setValue(75)
        right_layout.addWidget(volume_slider)
        
        layout.addLayout(right_layout)
    
    def set_current_track(self, track_data):
        """Set current track information"""
        self.current_track = track_data
        self.track_name.setText(track_data['name'])
        self.track_artist.setText(f"{track_data['artist']} - {track_data['song']}")
    
    def toggle_play(self):
        """Toggle play/pause"""
        self.is_playing = not self.is_playing
        if self.is_playing:
            pause_icon = self.style().standardIcon(QStyle.SP_MediaPause)
            self.play_btn.setIcon(pause_icon)
        else:
            play_icon = self.style().standardIcon(QStyle.SP_MediaPlay)
            self.play_btn.setIcon(play_icon)
        self.play_clicked.emit()