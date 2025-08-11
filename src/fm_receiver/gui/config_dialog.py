"""SDR Configuration Dialog Module with Enhanced Auto-Selection"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QFrame
)
from PyQt5.QtCore import Qt, QTimer
import SoapySDR


class ConfigDialog(QDialog):
    """Dialog for configuring SDR devices"""

    def __init__(self, auto_select_single=True, auto_close_delay=500):
        """
        Initialize the configuration dialog
        
        Args:
            auto_select_single (bool): Automatically select if only one device found
            auto_close_delay (int): Delay in milliseconds before auto-closing (0 to disable)
        """
        super().__init__()
        self.setWindowTitle("SDR Configuration")
        self.setMinimumWidth(400)
        self.selected_device = None
        self.devices = []
        self.device_selector = None
        self.device_label = None
        self.status_label = None
        self.accept_button = None
        self.rescan_button = None
        self.auto_select_single = auto_select_single
        self.auto_close_delay = auto_close_delay
        self.auto_close_timer = QTimer()
        self.auto_close_timer.setSingleShot(True)
        self.auto_close_timer.timeout.connect(self.accept)
        self.setup_ui()
        self.scan_devices()

    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("SDR Device Configuration")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        # Device selection section
        self.device_label = QLabel("Select an SDR device:")
        self.device_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.device_label)

        self.device_selector = QComboBox()
        self.device_selector.setMinimumHeight(30)
        layout.addWidget(self.device_selector)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)

        # Buttons section
        button_layout = QHBoxLayout()

        # Rescan button
        self.rescan_button = QPushButton("Rescan Devices")
        self.rescan_button.setMinimumHeight(35)
        self.rescan_button.clicked.connect(self.scan_devices)
        self.rescan_button.setStyleSheet("""
            QPushButton {
                background-color: #e3f2fd;
                border: 1px solid #2196f3;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #bbdefb;
            }
        """)
        button_layout.addWidget(self.rescan_button)

        # Spacer
        button_layout.addStretch()

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.setMinimumHeight(35)
        cancel_button.clicked.connect(self.reject)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #ffebee;
                border: 1px solid #f44336;
                border-radius: 5px;
                padding: 5px 15px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #ffcdd2;
            }
        """)
        button_layout.addWidget(cancel_button)

        # Continue/Accept button
        self.accept_button = QPushButton("Continue")
        self.accept_button.setMinimumHeight(35)
        self.accept_button.clicked.connect(self.accept_selection)
        self.accept_button.setStyleSheet("""
            QPushButton {
                background-color: #e8f5e8;
                border: 1px solid #4caf50;
                border-radius: 5px;
                padding: 5px 15px;
                min-width: 80px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c8e6c9;
            }
            QPushButton:disabled {
                background-color: #f5f5f5;
                border-color: #cccccc;
                color: #999999;
            }
        """)
        button_layout.addWidget(self.accept_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def is_sdr_device(self, device):
        """
        Check if a device is an SDR device by examining its properties.
        This filters out audio devices and other non-SDR hardware.

        Args:
            device (SoapySDRKwargs): Device object from SoapySDR enumeration

        Returns:
            bool: True if device is an SDR device, False otherwise
        """
        # Common SDR device drivers and identifiers
        sdr_drivers = {
            'rtlsdr', 'hackrf', 'bladerf', 'uhd', 'sdrplay', 'airspy',
            'limesdr', 'plutosdr', 'redpitaya', 'xtrx', 'soapyremote'
        }

        try:
            # Check driver field
            if 'driver' in device:
                driver = str(device['driver']).lower()
                if driver in sdr_drivers:
                    return True

            # Check for common SDR keywords in device description
            sdr_keywords = {
                'sdr', 'software defined radio', 'rtl', 'hackrf', 'bladerf',
                'uhd', 'usrp', 'airspy', 'limesdr', 'plutosdr', 'adalm'
            }

            # Check various fields for SDR keywords
            fields_to_check = ['label', 'product', 'serial', 'manufacturer']
            for field in fields_to_check:
                if field in device:
                    value = str(device[field]).lower()
                    if any(keyword in value for keyword in sdr_keywords):
                        return True

        except (KeyError, TypeError):
            # If we can't access device properties, assume it's not an SDR
            pass

        return False

    def scan_devices(self):
        """Scan for SDR devices and populate the combo box"""
        # Stop any existing auto-close timer
        self.auto_close_timer.stop()
        
        self.rescan_button.setEnabled(False)
        self.rescan_button.setText("Scanning...")
        self.status_label.setText("Scanning for SDR devices...")

        try:
            # Get all devices
            all_devices = SoapySDR.Device.enumerate()

            # Filter for SDR devices only
            self.devices = [dev for dev in all_devices if self.is_sdr_device(dev)]

            # Clear and populate combo box
            self.device_selector.clear()

            if not self.devices:
                self.status_label.setText(
                    "No SDR devices found. Please check connections and try rescanning."
                )
                self.status_label.setStyleSheet("color: #d32f2f; font-style: italic;")
                self.accept_button.setEnabled(False)
                self.device_label.setText("No SDR devices available:")
            else:
                self.status_label.setText(f"Found {len(self.devices)} SDR device(s)")
                self.status_label.setStyleSheet("color: #388e3c; font-style: italic;")
                self.accept_button.setEnabled(True)
                self.device_label.setText("Select an SDR device:")

                for device in self.devices:
                    # Create a more readable device description
                    parts = []

                    try:
                        # Add driver info
                        if 'driver' in device and device['driver']:
                            parts.append(f"Driver: {device['driver']}")

                        # Add label or product info
                        if 'label' in device and device['label']:
                            parts.append(f"Label: {device['label']}")
                        elif 'product' in device and device['product']:
                            parts.append(f"Product: {device['product']}")

                        # Add serial if available
                        if 'serial' in device and device['serial']:
                            parts.append(f"Serial: {device['serial']}")

                        # Fallback to showing all properties
                        if not parts:
                            # Get all keys from the SoapySDRKwargs object
                            device_keys = list(device.keys()) if hasattr(device, 'keys') else []
                            parts = [f"{k}={device[k]}" for k in device_keys if device[k]]

                    except (KeyError, TypeError):
                        # If we can't access device properties, show a generic description
                        parts = ["Unknown SDR Device"]

                    summary = " | ".join(parts) if parts else "SDR Device"
                    self.device_selector.addItem(summary)

                # Auto-select single device
                if len(self.devices) == 1 and self.auto_select_single:
                    self.device_selector.setCurrentIndex(0)
                    self.selected_device = self.devices[0]
                    
                    # Update status to show auto-selection
                    self.status_label.setText(
                        f"Auto-selected single SDR device" + 
                        (f" (closing in {self.auto_close_delay//1000}s)" if self.auto_close_delay > 0 else "")
                    )
                    self.status_label.setStyleSheet("color: #1976d2; font-style: italic; font-weight: bold;")
                    
                    # Auto-close after delay if enabled
                    if self.auto_close_delay > 0:
                        self.auto_close_timer.start(self.auto_close_delay)
                    else:
                        # If no delay, close immediately
                        self.accept()
                    return

        except Exception as error:
            self.status_label.setText(f"Error scanning devices: {str(error)}")
            self.status_label.setStyleSheet("color: #d32f2f; font-style: italic;")
            self.accept_button.setEnabled(False)

        finally:
            self.rescan_button.setEnabled(True)
            self.rescan_button.setText("Rescan Devices")

    def accept_selection(self):
        """Accept the selected device and close dialog"""
        # Stop auto-close timer if running
        self.auto_close_timer.stop()
        
        if self.devices and self.device_selector.currentIndex() >= 0:
            index = self.device_selector.currentIndex()
            self.selected_device = self.devices[index]
            self.accept()

    def get_selected_device(self):
        """
        Return the selected SDR device

        Returns:
            dict or None: Selected device dictionary or None if no selection
        """
        return self.selected_device

    def closeEvent(self, event):
        """Handle dialog close event"""
        # Stop auto-close timer
        self.auto_close_timer.stop()
        event.accept()
