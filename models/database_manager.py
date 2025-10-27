"""Utilities for managing database connections used across the project."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from projeto.config.settings import DATABASE_PATH


class DatabaseManager:
    """Simple SQLite database manager with a context-managed connection."""

    def __init__(self, database_path: Path | str | None = None) -> None:
        self.database_path = Path(database_path or DATABASE_PATH)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        """Yield a SQLite connection and ensure it is committed and closed."""
        connection = sqlite3.connect(self.database_path)
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def execute_script(self, script: str) -> None:
        """Execute a raw SQL script and commit the changes."""
        with self.connect() as connection:
            connection.executescript(script)

    def run_query(self, query: str, parameters: tuple | None = None) -> list[tuple]:
        """Run a query returning all fetched rows."""
        with self.connect() as connection:
            cursor = connection.execute(query, parameters or ())
            return cursor.fetchall()
