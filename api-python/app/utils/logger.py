"""Logging configuration"""
import logging
import sys
from typing import Optional
from pythonjsonlogger import jsonlogger
from app.config import get_settings


def setup_logger(name: Optional[str] = None, log_level: Optional[str] = None) -> logging.Logger:
    """
    Set up and configure logger

    Args:
        name: Logger name (defaults to root logger)
        log_level: Log level (defaults to settings)

    Returns:
        Configured logger instance
    """
    settings = get_settings()
    logger = logging.getLogger(name)

    # Set log level
    level = log_level or settings.log_level
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Console handler with JSON formatter
    console_handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        timestamp=True
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if configured
    if settings.log_file:
        file_handler = logging.FileHandler(settings.log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Default logger instance
logger = setup_logger("librechat")
