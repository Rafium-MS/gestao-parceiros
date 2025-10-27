"""Repository helpers encapsulating database access for brands."""

from __future__ import annotations

import sqlite3
from typing import Sequence


class MarcaRepository:
    """Provide CRUD helpers for the ``marcas`` table."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def adicionar(self, nome: str, codigo: str) -> None:
        """Insert a new brand record."""
        with self._connection:
            self._connection.execute(
                "INSERT INTO marcas (nome, codigo_disagua) VALUES (?, ?)",
                (nome, codigo),
            )

    def atualizar(self, marca_id: int, nome: str, codigo: str) -> None:
        """Update brand details by identifier."""
        with self._connection:
            self._connection.execute(
                "UPDATE marcas SET nome = ?, codigo_disagua = ? WHERE id = ?",
                (nome, codigo, marca_id),
            )

    def remover(self, marca_id: int) -> None:
        """Delete a brand record by identifier."""
        with self._connection:
            self._connection.execute("DELETE FROM marcas WHERE id = ?", (marca_id,))

    def listar(self) -> list[Sequence[str | int]]:
        """Return all registered brands ordered by name."""
        cursor = self._connection.execute(
            "SELECT id, nome, codigo_disagua FROM marcas ORDER BY nome"
        )
        return cursor.fetchall()

    def opcoes_para_combobox(self) -> list[tuple[int, str]]:
        """Return ``(id, nome)`` tuples used by selection widgets."""
        cursor = self._connection.execute(
            "SELECT id, nome FROM marcas ORDER BY nome"
        )
        return cursor.fetchall()
