from PyQt5.QtWidgets import QWidget, QSlider, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, pyqtSignal


class VolumeSlider(QWidget):
    # Signal to emit volume changes
    volumeChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create label and slider
        self.label = QLabel("Volume: 50")
        self.slider = QSlider(Qt.Vertical)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(50)

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.label, alignment=Qt.AlignHCenter)
        layout.addWidget(self.slider)
        self.setLayout(layout)

        # Connect the slider change to handlers
        self.slider.valueChanged.connect(self.emitVolumeChanged)

    def emitVolumeChanged(self, value):
        self.label.setText(f"Volume: {value}")
        self.volumeChanged.emit(value)

    def setVolume(self, value):
        self.slider.setValue(value)

    def getVolume(self):
        return self.slider.value()
