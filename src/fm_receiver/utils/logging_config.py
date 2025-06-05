"""
Logging Configuration
"""
import logging
import sys
from pathlib import Path

def setup_logging(debug=False):
    """Setup application logging"""
    
    # Create logs directory
    log_dir = Path.home() / '.fm_receiver' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure logging level
    level = logging.DEBUG if debug else logging.INFO
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # File handler
    file_handler = logging.FileHandler(log_dir / 'fm_receiver.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Reduce matplotlib logging
    logging.getLogger('matplotlib').setLevel(logging.WARNING)