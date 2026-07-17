# logs/logger.py
import logging
from logging.handlers import RotatingFileHandler
import os
from utils.system import get_base_dir


def setup_logger(name="VigiLo", log_filename="vigilo.log", level=logging.INFO):
    """Sets up a rotating file logger and console logger under the /logs folder."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Check if handlers already exist to avoid duplicate logs
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - [%(levelname)s] - %(message)s"
    )

    # Stream Handler (stdout/console)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Rotating File Handler (Max 5MB per log, max 3 backups)
    log_dir = os.path.join(get_base_dir(), "logs")
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except Exception:
            # Fallback to base execution directory if Program Files is read-only
            log_dir = get_base_dir()

    log_path = os.path.join(log_dir, log_filename)
    try:
        file_handler = RotatingFileHandler(
            log_path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.error(f"Failed to initialize file logger handler at {log_path}: {e}")

    return logger


# Default export instance
logger = setup_logger()
