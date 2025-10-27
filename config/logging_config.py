"""Utilities for configuring application logging."""

from __future__ import annotations

import logging
import logging.config
from copy import deepcopy
from pathlib import Path
from typing import Union

from config.settings import LOG_DIR

DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FILE = LOG_DIR / "app.log"

_BASE_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": DEFAULT_LOG_LEVEL,
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "level": DEFAULT_LOG_LEVEL,
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "encoding": "utf-8",
            "filename": str(DEFAULT_LOG_FILE),
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": DEFAULT_LOG_LEVEL,
    },
}


def setup_logging(
    level: Union[int, str] = DEFAULT_LOG_LEVEL,
    log_file: Union[str, Path, None] = None,
) -> None:
    """Configure the logging system used by the application."""
    resolved_log_file = Path(log_file) if log_file is not None else DEFAULT_LOG_FILE
    resolved_log_file.parent.mkdir(parents=True, exist_ok=True)

    config = deepcopy(_BASE_LOGGING_CONFIG)

    # Update log level configuration.
    if isinstance(level, str):
        normalized_level: Union[int, str] = level.upper()
    else:
        normalized_level = level

    config["handlers"]["console"]["level"] = normalized_level
    config["handlers"]["file"]["level"] = normalized_level
    config["root"]["level"] = normalized_level
    config["handlers"]["file"]["filename"] = str(resolved_log_file)

    logging.config.dictConfig(config)

    logging.getLogger(__name__).debug(
        "Logging configurado com nível %s e arquivo %s",
        normalized_level,
        resolved_log_file,
    )

