"""
Standardized Application Logging Configuration.

Configures structured console and file loggers with appropriate log levels.
"""

import logging
import sys
from typing import Optional


def setup_logger(name: str = "ecommerce_iq", level: Optional[str] = None) -> logging.Logger:
    """
    Initialize and return a configured logger instance.
    """
    log_level = getattr(logging, (level or "INFO").upper(), logging.INFO)
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(log_level)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
