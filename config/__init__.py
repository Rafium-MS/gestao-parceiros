"""Configuration package for centralised settings."""

from .settings import DATABASE_PATH, BACKUP_DIR, LOG_DIR
from .logging_config import setup_logging

__all__ = ["DATABASE_PATH", "BACKUP_DIR", "LOG_DIR", "setup_logging"]
