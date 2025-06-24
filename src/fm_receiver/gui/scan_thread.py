from PyQt5.QtCore import QThread, pyqtSignal
from utils.fm_scanner import scan_fm
import numpy as np

class ScanThread(QThread):
    """FM station scanning"""
    scan_finished = pyqtSignal(list)
    progress_updated = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._is_running = True  # Flag to control stopping

    def run(self):
        stations = []
        
        center_freqs = np.arange(88e6,110e6,1e6)
                
        for i, freq in enumerate(center_freqs):
            if not self._is_running:
                break
            self.progress_updated.emit(f"Scanning {freq/1e6:.1f} MHz...")

            station = scan_fm(freq)
            
            stations += station

        self.progress_updated.emit(f"Detected {len(stations)}")           
        self.scan_finished.emit(list(set(stations)))

    def stop(self):
        self._is_running = False
