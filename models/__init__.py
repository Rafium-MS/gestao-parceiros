"""Data layer package for the gestão de parceiros application."""

from .database_manager import DatabaseManager
from .base_model import BaseModel

__all__ = ["DatabaseManager", "BaseModel"]
