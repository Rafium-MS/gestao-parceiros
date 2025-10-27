"""Repository for comprovante (delivery receipt) operations."""

from __future__ import annotations

import sqlite3
from typing import Iterable, Sequence


class ComprovantesRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def add(
        self,
        parceiro_id: int,
        loja_id: int,
        data_entrega: str,
        qtd_20l: int,
        qtd_10l: int,
        qtd_cx_copo: int,
        qtd_1500ml: int,
        assinatura: str,
        arquivo: str,
    ) -> None:
        cursor = self._connection.cursor()
        cursor.execute(
            """
            INSERT INTO comprovantes (
                parceiro_id, loja_id, data_entrega,
                qtd_20l, qtd_10l, qtd_cx_copo, qtd_1500ml,
                assinatura, arquivo_comprovante
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                parceiro_id,
                loja_id,
                data_entrega,
                qtd_20l,
                qtd_10l,
                qtd_cx_copo,
                qtd_1500ml,
                assinatura,
                arquivo,
            ),
        )
        self._connection.commit()

    def list_all(self) -> Sequence[tuple]:
        cursor = self._connection.cursor()
        cursor.execute(
            """
            SELECT c.id, c.data_entrega, p.nome_parceiro, l.nome,
                   c.qtd_20l, c.qtd_10l, c.qtd_cx_copo, c.qtd_1500ml
            FROM comprovantes c
            JOIN parceiros p ON c.parceiro_id = p.id
            JOIN lojas l ON c.loja_id = l.id
            ORDER BY c.data_entrega DESC
            """
        )
        return cursor.fetchall()

    def delete(self, comprovante_id: int) -> None:
        cursor = self._connection.cursor()
        cursor.execute("DELETE FROM comprovantes WHERE id = ?", (comprovante_id,))
        self._connection.commit()

    def count_distinct_parceiros(self) -> int:
        cursor = self._connection.cursor()
        cursor.execute("SELECT COUNT(DISTINCT parceiro_id) FROM comprovantes")
        return cursor.fetchone()[0]

    def relatorio_por_marca(
        self, marca_id: int, data_inicio: str | None = None, data_fim: str | None = None
    ) -> Sequence[tuple]:
        query = (
            """
            SELECT l.nome, l.local_entrega, l.municipio,
                   SUM(c.qtd_20l), SUM(c.qtd_10l), SUM(c.qtd_cx_copo), SUM(c.qtd_1500ml),
                   l.valor_20l, l.valor_10l, l.valor_cx_copo, l.valor_1500ml
            FROM comprovantes c
            JOIN lojas l ON c.loja_id = l.id
            WHERE l.marca_id = ?
            """
        )

        params: list[str] = [str(marca_id)]

        if data_inicio:
            query += " AND c.data_entrega >= ?"
            params.append(data_inicio)

        if data_fim:
            query += " AND c.data_entrega <= ?"
            params.append(data_fim)

        query += " GROUP BY l.id ORDER BY l.nome"

        cursor = self._connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def relatorio_por_parceiro(
        self, parceiro_id: int, data_inicio: str | None = None, data_fim: str | None = None
    ) -> Sequence[tuple]:
        query = (
            """
            SELECT l.nome, c.data_entrega,
                   c.qtd_20l, c.qtd_10l, c.qtd_cx_copo, c.qtd_1500ml,
                   p.valor_20l, p.valor_10l, p.valor_cx_copo, p.valor_1500ml
            FROM comprovantes c
            JOIN lojas l ON c.loja_id = l.id
            JOIN parceiros p ON c.parceiro_id = p.id
            WHERE c.parceiro_id = ?
            """
        )

        params: list[str] = [str(parceiro_id)]

        if data_inicio:
            query += " AND c.data_entrega >= ?"
            params.append(data_inicio)

        if data_fim:
            query += " AND c.data_entrega <= ?"
            params.append(data_fim)

        query += " ORDER BY c.data_entrega DESC"

        cursor = self._connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

