"""Helpers for creating database backups."""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from projeto.config.settings import BACKUP_DIR, DATABASE_PATH


def create_database_backup(suffix: str | None = None) -> Path:
    """Create a timestamped backup of the SQLite database."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix_part = f"_{suffix}" if suffix else ""
    backup_name = f"backup_{timestamp}{suffix_part}.sqlite3"
    destination = BACKUP_DIR / backup_name
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DATABASE_PATH, destination)
    return destination
