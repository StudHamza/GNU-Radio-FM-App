from PyQt5.QtCore import QThread, pyqtSignal, QObject
import logging

logger = logging.getLogger(__name__)

class ScannerWorker(QObject):
    progress = pyqtSignal(float)      # Emitting current frequency
    finished = pyqtSignal(bool)       # Emitting stations when done

    def __init__(self, fm_receiver, start_freq,end_freq):
        super().__init__()
        self.fm_receiver = fm_receiver
        self._is_running = True
        self.start_freq = start_freq
        self.end_freq = end_freq

        self.progress.emit(start_freq)
        logger.info("Inialized scanning monitor")



    def run(self):
        freq = self.start_freq
        logger.info("Running scanning monitor")

        while self._is_running:
            while self.fm_receiver.get_done() == 0:
                if not self._is_running:
                    return
                QThread.msleep(10)  # Don't hog the CPU
            logger.info(f"Scanning {freq}")
            freq += 1e6
            if freq > self.end_freq:
                break

            self.progress.emit(freq)
            while self.fm_receiver.get_done() == 1:
                # dont perform next scan
                continue

        # Post-scan logic
        self.finished.emit(True)

    def stop(self):
        self._is_running = False
