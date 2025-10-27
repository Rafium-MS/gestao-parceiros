"""Repository for partner (parceiro) related operations."""

from __future__ import annotations

import sqlite3
from typing import Iterable, Sequence


class ParceirosRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def add(
        self,
        nome: str,
        distribuidora: str,
        cidade: str,
        estado: str,
        cnpj: str,
        telefone: str,
        email: str,
        dia_pagamento: int | None,
        banco: str,
        agencia: str,
        conta: str,
        chave_pix: str,
        valor_20l: float | None,
        valor_10l: float | None,
        valor_cx_copo: float | None,
        valor_1500ml: float | None,
    ) -> None:
        cursor = self._connection.cursor()
        cursor.execute(
            """
            INSERT INTO parceiros (
                nome_parceiro, distribuidora, cidade, estado, cnpj, telefone,
                email, dia_pagamento, banco, agencia, conta, chave_pix,
                valor_20l, valor_10l, valor_cx_copo, valor_1500ml
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                nome,
                distribuidora,
                cidade,
                estado,
                cnpj,
                telefone,
                email,
                dia_pagamento,
                banco,
                agencia,
                conta,
                chave_pix,
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
            "SELECT id, nome_parceiro, cidade, estado, cnpj, telefone FROM parceiros ORDER BY nome_parceiro"
        )
        return cursor.fetchall()

    def delete(self, parceiro_id: int) -> None:
        cursor = self._connection.cursor()
        cursor.execute("DELETE FROM parceiros WHERE id = ?", (parceiro_id,))
        self._connection.commit()

    def combo_values(self) -> Iterable[str]:
        cursor = self._connection.cursor()
        cursor.execute("SELECT id, nome_parceiro FROM parceiros ORDER BY nome_parceiro")
        return [f"{row[0]} - {row[1]}" for row in cursor.fetchall()]

    def count_all(self) -> int:
        cursor = self._connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM parceiros")
        return cursor.fetchone()[0]

    def list_with_last_delivery(self) -> Sequence[tuple]:
        cursor = self._connection.cursor()
        cursor.execute(
            """
            SELECT p.nome_parceiro,
                   CASE WHEN c.ultima_entrega IS NOT NULL THEN 'Enviado' ELSE 'Pendente' END,
                   COALESCE(c.ultima_entrega, 'Sem entregas')
            FROM parceiros p
            LEFT JOIN (
                SELECT parceiro_id, MAX(data_entrega) as ultima_entrega
                FROM comprovantes
                GROUP BY parceiro_id
            ) c ON p.id = c.parceiro_id
            ORDER BY p.nome_parceiro
            """
        )
        return cursor.fetchall()

