"""
Centralized logging configuration.

Provides a pre-configured logger for the entire application.
All modules should use `from app.core.logger import logger` instead of
creating their own logging instances.
"""

import logging
import sys

from app.core.config import settings


def _setup_logger() -> logging.Logger:
    """Create and configure the application logger."""
    log = logging.getLogger(settings.app_name)
    log.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    if not log.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        log.addHandler(handler)

    return log


logger = _setup_logger()
