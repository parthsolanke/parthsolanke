import logging
import sys
import os
from typing import Optional

def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Configure and return a logger with consistent formatting and handling.
    
    Args:
        name: The name of the logger
        level: Optional logging level (defaults to INFO if not specified)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='[%(asctime)s][%(levelname)s][%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Only add handlers if the logger doesn't already have any
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler - using a single log file for all modules
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)  # Create logs directory if it doesn't exist
        log_file = os.path.join(log_dir, 'app.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Set level (default to INFO if not specified)
    logger.setLevel(level or logging.INFO)
    
    return logger
