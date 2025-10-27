"""Central configuration for the gestão de parceiros application."""

from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
BACKUP_DIR = LOG_DIR / "backups"
DATABASE_PATH = DATA_DIR / "gestao_parceiros.sqlite3"

for directory in (DATA_DIR, LOG_DIR, BACKUP_DIR):
    directory.mkdir(parents=True, exist_ok=True)

if not DATABASE_PATH.exists():
    DATABASE_PATH.touch()
