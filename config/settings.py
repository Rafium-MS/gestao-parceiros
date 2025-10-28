"""Project-wide configuration settings."""

from pathlib import Path

# Base directory of the project (repository root)
BASE_DIR = Path(__file__).resolve().parent.parent

# Directory where exported files will be stored.
EXPORT_DIR = BASE_DIR / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

__all__ = ["BASE_DIR", "EXPORT_DIR"]
