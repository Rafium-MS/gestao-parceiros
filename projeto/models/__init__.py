"""Data layer package for the gestão de parceiros application."""

from .database_manager import DatabaseManager
from .base_model import BaseModel
from .schema import initialize_schema
from .marca_repository import MarcaRepository

__all__ = [
    "DatabaseManager",
    "BaseModel",
    "initialize_schema",
    "MarcaRepository",
]
