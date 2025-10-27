"""Repository for managing the relacionamento between parceiros and lojas."""

from __future__ import annotations

import sqlite3
from typing import Iterable, Sequence


class ParceiroLojaRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def list_vinculadas(self, parceiro_id: int) -> Sequence[tuple]:
        cursor = self._connection.cursor()
        cursor.execute(
            """
            SELECT l.id, l.nome, l.municipio, l.estado
            FROM lojas l
            JOIN parceiro_loja pl ON l.id = pl.loja_id
            WHERE pl.parceiro_id = ?
            ORDER BY l.nome
            """,
            (parceiro_id,),
        )
        return cursor.fetchall()

    def list_disponiveis(self, parceiro_id: int) -> Sequence[tuple]:
        cursor = self._connection.cursor()
        cursor.execute(
            """
            SELECT l.id, l.nome, l.municipio, l.estado
            FROM lojas l
            WHERE l.id NOT IN (
                SELECT loja_id FROM parceiro_loja WHERE parceiro_id = ?
            )
            ORDER BY l.nome
            """,
            (parceiro_id,),
        )
        return cursor.fetchall()

    def vincular(self, parceiro_id: int, loja_id: int) -> None:
        cursor = self._connection.cursor()
        cursor.execute(
            "INSERT INTO parceiro_loja (parceiro_id, loja_id) VALUES (?, ?)",
            (parceiro_id, loja_id),
        )
        self._connection.commit()

    def desvincular(self, parceiro_id: int, loja_id: int) -> None:
        cursor = self._connection.cursor()
        cursor.execute(
            "DELETE FROM parceiro_loja WHERE parceiro_id = ? AND loja_id = ?",
            (parceiro_id, loja_id),
        )
        self._connection.commit()

    def lojas_para_parceiro(self, parceiro_id: int) -> Iterable[str]:
        cursor = self._connection.cursor()
        cursor.execute(
            """
            SELECT l.id, l.nome
            FROM lojas l
            JOIN parceiro_loja pl ON l.id = pl.loja_id
            WHERE pl.parceiro_id = ?
            ORDER BY l.nome
            """,
            (parceiro_id,),
        )
        return [f"{row[0]} - {row[1]}" for row in cursor.fetchall()]

