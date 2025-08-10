from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout




class InfoWindow(QWidget):
    def __init__(self, message, timeout=3000, parent=None):
        super().__init__(parent)

        # Window flags for a floating notification
        self.setWindowFlags(
            Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_ShowWithoutActivating)  # Don't grab focus

        # Layout + label
        layout = QVBoxLayout()
        label = QLabel(message)
        label.setStyleSheet("color: white; font-size: 12pt; padding: 8px;")
        layout.addWidget(label)
        self.setLayout(layout)

        # Styling
        self.setStyleSheet("""
            QWidget {
                background-color: #333333;
                border: 2px solid black;
                border-radius: 5px;
            }
        """)

        # Position near mouse cursor
        mouse_pos = QCursor.pos()
        self.move(mouse_pos + QPoint(10, 10))

        # Auto-close
        QTimer.singleShot(timeout, self.close)
