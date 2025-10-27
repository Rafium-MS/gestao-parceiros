"""Repository dedicated to CRUD operations of stores (lojas)."""

from __future__ import annotations

import sqlite3
from typing import Iterable, Sequence


class LojasRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def add(
        self,
        marca_id: int,
        nome: str,
        codigo_disagua: str | None,
        local_entrega: str,
        municipio: str,
        estado: str,
        valor_20l: float | None,
        valor_10l: float | None,
        valor_cx_copo: float | None,
        valor_1500ml: float | None,
    ) -> None:
        cursor = self._connection.cursor()
        cursor.execute(
            """
            INSERT INTO lojas (
                marca_id, nome, codigo_disagua, local_entrega, municipio, estado,
                valor_20l, valor_10l, valor_cx_copo, valor_1500ml
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                marca_id,
                nome,
                codigo_disagua,
                local_entrega,
                municipio,
                estado,
                valor_20l,
                valor_10l,
                valor_cx_copo,
                valor_1500ml,
            ),
        )
        self._connection.commit()

    def list_all(self) -> Sequence[tuple]:
        cursor = self._connection.cursor()
        cursor.execute(
            """
            SELECT l.id, COALESCE(m.nome, 'Sem Marca'), l.nome, l.municipio, l.estado, l.valor_20l
            FROM lojas l
            LEFT JOIN marcas m ON l.marca_id = m.id
            ORDER BY l.nome
            """
        )
        return cursor.fetchall()

    def delete(self, loja_id: int) -> None:
        cursor = self._connection.cursor()
        cursor.execute("DELETE FROM lojas WHERE id = ?", (loja_id,))
        self._connection.commit()

    def combo_values(self) -> Iterable[str]:
        cursor = self._connection.cursor()
        cursor.execute("SELECT id, nome FROM lojas ORDER BY nome")
        return [f"{row[0]} - {row[1]}" for row in cursor.fetchall()]

    def count_all(self) -> int:
        cursor = self._connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM lojas")
        return cursor.fetchone()[0]

