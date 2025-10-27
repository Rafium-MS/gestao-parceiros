"""Repository handling CRUD operations for the `marcas` table."""

from __future__ import annotations

import sqlite3
from typing import Iterable, Sequence


class MarcasRepository:
    """Encapsulate database operations for brands."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def add(self, nome: str, codigo_disagua: str) -> None:
        cursor = self._connection.cursor()
        cursor.execute(
            "INSERT INTO marcas (nome, codigo_disagua) VALUES (?, ?)",
            (nome, codigo_disagua),
        )
        self._connection.commit()

    def list_all(self) -> Sequence[tuple]:
        cursor = self._connection.cursor()
        cursor.execute("SELECT id, nome, codigo_disagua FROM marcas ORDER BY nome")
        return cursor.fetchall()

    def delete(self, marca_id: int) -> None:
        cursor = self._connection.cursor()
        cursor.execute("DELETE FROM marcas WHERE id = ?", (marca_id,))
        self._connection.commit()

    def combo_values(self) -> Iterable[str]:
        """Return values formatted for combo boxes."""

        cursor = self._connection.cursor()
        cursor.execute("SELECT id, nome FROM marcas ORDER BY nome")
        return [f"{row[0]} - {row[1]}" for row in cursor.fetchall()]

