#!/usr/bin/env python3
"""
FM Receiver Application Entry Point
"""
import argparse
import sys

from flowgraphs import rds_rx_epy_block_0
sys.modules["rds_rx_epy_block_0"] = rds_rx_epy_block_0

from app import FMReceiverApp
from qtpy.QtWidgets import QApplication
from utils.logging_config import setup_logging
from gui.config_dialog import ConfigDialog

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='FM Receiver Application')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    parser.add_argument('--config', type=str,
                       help='Path to configuration file')
    return parser.parse_args()

def main():
    """Main application entry point"""
    args = parse_arguments()

    # Setup logging
    setup_logging(debug=args.debug)


    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("FM Receiver")
    app.setApplicationVersion("0.1.0")

    config_dialog = ConfigDialog()
    result = config_dialog.exec_()  # blocks until user responds

    if result != config_dialog.Accepted:
        sys.exit(0)

    # If accepted, launch main app
    sdr_device = config_dialog.get_selected_device()['serial']

    fm_app = FMReceiverApp(config_path=args.config,serial=sdr_device)
    fm_app.show()

    # Run event loop
    sys.exit(app.exec_())
if __name__ == '__main__':
    main()
    