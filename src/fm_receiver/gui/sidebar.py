"""
Modern Sidebar Navigation
"""
from qtpy.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame, QSizePolicy
from qtpy.QtCore import Qt, Signal, QSize
from qtpy.QtGui import QFont, QIcon, QPixmap

class Sidebar(QWidget):
    """Modern sidebar navigation"""
    
    # Signals
    home_clicked = Signal()
    fft_clicked = Signal()
    debug_clicked = Signal()
    settings_clicked = Signal()
    
    def __init__(self):
        super().__init__()
        self.current_button = None  # Initialize before setup_ui
        self.setup_ui()
    
    def setup_ui(self):
        """Setup sidebar UI"""
        # self.setStyleSheet("""
        #     QWidget {
        #         background-color: #0f0f0f;
        #         border-right: 1px solid #333;
        #     }
        #     QPushButton {
        #         background-color: transparent;
        #         border: none;
        #         color: #888;
        #         padding: 15px 20px;
        #         text-align: left;
        #         font-size: 14px;
        #         border-radius: 0px;
        #     }
        #     QPushButton:hover {
        #         background-color: #2a2a2a;
        #         color: #fff;
        #     }
        #     QPushButton:pressed {
        #         background-color: #ff4444;
        #         color: #fff;
        #     }
        #     QPushButton.active {
        #         background-color: #ff4444;
        #         color: #fff;
        #         border-left: 3px solid #ff6666;
        #     }
        #     QLabel {
        #         color: #ff4444;
        #         font-size: 18px;
        #         font-weight: bold;
        #         padding: 20px;
        #     }
        # """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Logo/Title
        title_label = QLabel("🎵GNU Radio")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Navigation buttons
        self.home_btn = self.create_nav_button("🏠  Home")
        self.fft_btn = self.create_nav_button("📊  FFT")
        self.debug_btn = self.create_nav_button("🔧  Debug Mode")
        self.settings_btn = self.create_nav_button("⚙️  Settings")
        
        layout.addWidget(self.home_btn)
        layout.addWidget(self.fft_btn)
        layout.addWidget(self.debug_btn)
        layout.addWidget(self.settings_btn)
        
        # Spacer
        layout.addStretch()
        
        # Connect signals
        self.home_btn.clicked.connect(lambda: self.button_clicked(self.home_btn, self.home_clicked))
        self.fft_btn.clicked.connect(lambda: self.button_clicked(self.fft_btn, self.fft_clicked))
        self.debug_btn.clicked.connect(lambda: self.button_clicked(self.debug_btn, self.debug_clicked))
        self.settings_btn.clicked.connect(lambda: self.button_clicked(self.settings_btn, self.settings_clicked))
        
        # Set home as active by default
        self.set_active_button(self.home_btn)
    
    def create_nav_button(self, text):
        """Create navigation button"""
        button = QPushButton(text)
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button.setFixedHeight(50)
        return button
    
    def button_clicked(self, button, signal):
        """Handle button click"""
        self.set_active_button(button)
        signal.emit()
    
    def set_active_button(self, button):
        """Set active button styling"""
        if self.current_button:
            self.current_button.setProperty("class", "")
            self.current_button.style().unpolish(self.current_button)
            self.current_button.style().polish(self.current_button)
        
        button.setProperty("class", "active")
        button.style().unpolish(button)
        button.style().polish(button)
        self.current_button = button