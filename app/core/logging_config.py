import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIRECTORY = "logs"
ERROR_LOG_FILE = os.path.join(LOG_DIRECTORY, "error.log")
WARNING_LOG_FILE = os.path.join(LOG_DIRECTORY, "warning.log")
INFO_LOG_FILE = os.path.join(LOG_DIRECTORY, "info.log")

# Ensure log directory exists
os.makedirs(LOG_DIRECTORY, exist_ok=True)

def setup_logging():
    """Set up centralized logging configuration."""
    
    # Create a logger that will be used globally
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Capture all levels of logs (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    # Define the log format
    log_format = '%(asctime)s - %(levelname)s - %(message)s - %(pathname)s - Line: %(lineno)d'
    formatter = logging.Formatter(log_format)

    # Handlers: These define where the logs will go (file, console, etc.)

    # Log to error file
    error_handler = RotatingFileHandler(ERROR_LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=3)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # Log to warning file
    warning_handler = RotatingFileHandler(WARNING_LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=3)
    warning_handler.setLevel(logging.WARNING)
    warning_handler.setFormatter(formatter)

    # Log to info file
    info_handler = RotatingFileHandler(INFO_LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=3)
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)

    # Console logging (for real-time debugging)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Add handlers to the global logger
    logger.addHandler(error_handler)
    logger.addHandler(warning_handler)
    logger.addHandler(info_handler)
    logger.addHandler(console_handler)

    # Log the successful setup of logging
    logger.info("Logging has been set up successfully.")
