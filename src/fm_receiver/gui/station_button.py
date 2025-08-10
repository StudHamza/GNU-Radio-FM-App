from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout
from PyQt5.QtCore import pyqtSignal, Qt


class StationButton(QWidget):
    # Signals for main click, delete, and record
    clicked = pyqtSignal(float)
    delete_clicked = pyqtSignal(float)
    record_clicked = pyqtSignal(float)

    def __init__(self, frequency_hz, parent=None):
        super().__init__(parent)
        self.frequency = frequency_hz
        self.is_recording = False

        # Main button
        self.main_btn = QPushButton(f"{self.frequency / 10**6:.1f} FM")
        self.main_btn.setMinimumHeight(50)
        self.main_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: 600;
                padding: 12px 20px;
                margin: 0;
                border: 2px solid #3498db;
                border-radius: 8px;
                background-color: #ffffff;
                color: #2c3e50;
            }
            QPushButton:hover {
                background-color: #e8f4f8;
                border-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #d5e8f3;
                border-color: #1f5f8b;
            }
        """)
        self.main_btn.clicked.connect(self._emit_clicked)

        # Delete button (X)
        self.delete_btn = QPushButton("✕")
        self.delete_btn.setFixedSize(32, 32)
        self.delete_btn.setToolTip("Delete Station")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                padding: 0;
                margin: 0;
                border: 1px solid #e74c3c;
                border-radius: 16px;
                background-color: #ffffff;
                color: #e74c3c;
            }
            QPushButton:hover {
                background-color: #e74c3c;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #c0392b;
                border-color: #c0392b;
            }
        """)
        self.delete_btn.clicked.connect(self._emit_delete)

        # Record button (⏺)
        self.record_btn = QPushButton("⏺")
        self.record_btn.setFixedSize(32, 32)
        self.record_btn.setToolTip("Record Station")
        self.record_btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                padding: 0;
                margin: 0;
                border: 1px solid #e67e22;
                border-radius: 16px;
                background-color: #ffffff;
                color: #e67e22;
            }
            QPushButton:hover {
                background-color: #e67e22;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #d35400;
                border-color: #d35400;
            }
        """)
        self.record_btn.clicked.connect(self._emit_record)

        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        layout.addWidget(self.main_btn, 1)
        layout.addWidget(self.delete_btn, 0, Qt.AlignCenter)
        layout.addWidget(self.record_btn, 0, Qt.AlignCenter)

        # Widget styling
        self.setFixedWidth(260)
        self.setMinimumHeight(66)
        self.setStyleSheet("""
            StationButton {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 12px;
            }
        """)

    def get_freq(self) -> int:
        return self.frequency

    def get_recording(self) -> bool:
        return self.is_recording

    def _emit_clicked(self):
        self.clicked.emit(self.frequency)

    def _emit_delete(self):
        self.delete_clicked.emit(self.frequency)

    def _emit_record(self):
        self.record_clicked.emit(self.frequency)

    def set_recording_state(self, is_recording):
        """Update record button appearance based on recording state"""
        self.is_recording = is_recording

        if is_recording:
            self.record_btn.setText("⏹")
            self.record_btn.setToolTip("Stop Recording")
            self.record_btn.setStyleSheet("""
                QPushButton {
                    font-size: 18px;
                    padding: 0;
                    margin: 0;
                    border: 1px solid #e74c3c;
                    border-radius: 16px;
                    background-color: #e74c3c;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                    border-color: #c0392b;
                }
                QPushButton:pressed {
                    background-color: #a93226;
                    border-color: #a93226;
                }
            """)
        else:
            self.record_btn.setText("⏺")
            self.record_btn.setToolTip("Record Station")
            self.record_btn.setStyleSheet("""
                QPushButton {
                    font-size: 18px;
                    padding: 0;
                    margin: 0;
                    border: 1px solid #e67e22;
                    border-radius: 16px;
                    background-color: #ffffff;
                    color: #e67e22;
                }
                QPushButton:hover {
                    background-color: #e67e22;
                    color: #ffffff;
                }
                QPushButton:pressed {
                    background-color: #d35400;
                    border-color: #d35400;
                }
            """)
        
        self._update_main_button_text()

    def _update_main_button_text(self):
        """Update main button text to show recording status"""
        base_text = f"{self.frequency / 10**6:.1f} FM"
        if self.is_recording:
            self.main_btn.setText(f"🔴 {base_text}")
        else:
            self.main_btn.setText(base_text)

    def set_selected_state(self, is_selected):
        """Update main button appearance based on selection state"""
        if is_selected:
            self.main_btn.setStyleSheet("""
                QPushButton {
                    font-size: 16px;
                    font-weight: 600;
                    padding: 12px 20px;
                    margin: 0;
                    border: 2px solid #2980b9;
                    border-radius: 8px;
                    background-color: #3498db;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                    border-color: #1f5f8b;
                }
                QPushButton:pressed {
                    background-color: #1f5f8b;
                    border-color: #174a6b;
                }
            """)
        else:
            self.main_btn.setStyleSheet("""
                QPushButton {
                    font-size: 16px;
                    font-weight: 600;
                    padding: 12px 20px;
                    margin: 0;
                    border: 2px solid #3498db;
                    border-radius: 8px;
                    background-color: #ffffff;
                    color: #2c3e50;
                }
                QPushButton:hover {
                    background-color: #e8f4f8;
                    border-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #d5e8f3;
                    border-color: #1f5f8b;
                }
            """)
