"""Common behaviour shared by data models in the application."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar

from .database_manager import DatabaseManager


@dataclass
class BaseModel:
    """Base class that exposes a database manager for child models."""

    table_name: ClassVar[str]
    database: DatabaseManager = field(default_factory=DatabaseManager, init=False)

    def all(self) -> list[tuple]:
        """Return all rows for the model's table."""
        query = f"SELECT * FROM {self.table_name}"
        return self.database.run_query(query)

    def filter(self, where_clause: str, parameters: tuple | None = None) -> list[tuple]:
        """Return rows filtered by the provided ``WHERE`` clause."""
        query = f"SELECT * FROM {self.table_name} WHERE {where_clause}"
        return self.database.run_query(query, parameters)
