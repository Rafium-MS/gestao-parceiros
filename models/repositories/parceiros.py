"""Repository for partner (parceiro) related operations."""

from __future__ import annotations

import logging
import sqlite3
from typing import Iterable, Sequence


logger = logging.getLogger(__name__)


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
        logger.info("Salvando parceiro: %s", nome)
        cursor = self._connection.cursor()
        try:
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
            logger.info("Parceiro salvo com sucesso: %s", nome)
        except sqlite3.Error as exc:
            self._connection.rollback()
            logger.error("Falha ao salvar parceiro %s: %s", nome, exc)
            raise
        finally:
            cursor.close()

    def list_all(self) -> Sequence[tuple]:
        logger.info("Listando todos os parceiros")
        cursor = self._connection.cursor()
        try:
            cursor.execute(
                "SELECT id, nome_parceiro, cidade, estado, cnpj, telefone FROM parceiros ORDER BY nome_parceiro"
            )
            parceiros = cursor.fetchall()
            logger.info("Total de parceiros encontrados: %s", len(parceiros))
            return parceiros
        except sqlite3.Error as exc:
            logger.error("Erro ao listar parceiros: %s", exc)
            raise
        finally:
            cursor.close()

    def delete(self, parceiro_id: int) -> None:
        logger.info("Removendo parceiro com ID: %s", parceiro_id)
        cursor = self._connection.cursor()
        try:
            cursor.execute("DELETE FROM parceiros WHERE id = ?", (parceiro_id,))
            self._connection.commit()
            logger.info("Parceiro removido: %s", parceiro_id)
        except sqlite3.Error as exc:
            self._connection.rollback()
            logger.error("Falha ao remover parceiro %s: %s", parceiro_id, exc)
            raise
        finally:
            cursor.close()

    def combo_values(self) -> Iterable[str]:
        logger.info("Obtendo valores para combo de parceiros")
        cursor = self._connection.cursor()
        try:
            cursor.execute("SELECT id, nome_parceiro FROM parceiros ORDER BY nome_parceiro")
            valores = [f"{row[0]} - {row[1]}" for row in cursor.fetchall()]
            logger.info("Total de valores encontrados para combo: %s", len(valores))
            return valores
        except sqlite3.Error as exc:
            logger.error("Erro ao obter valores para combo de parceiros: %s", exc)
            raise
        finally:
            cursor.close()

    def count_all(self) -> int:
        logger.info("Contando todos os parceiros")
        cursor = self._connection.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM parceiros")
            total = cursor.fetchone()[0]
            logger.info("Total de parceiros cadastrados: %s", total)
            return total
        except sqlite3.Error as exc:
            logger.error("Erro ao contar parceiros: %s", exc)
            raise
        finally:
            cursor.close()

    def list_with_last_delivery(self) -> Sequence[tuple]:
        logger.info("Listando parceiros com status da última entrega")
        cursor = self._connection.cursor()
        try:
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
            parceiros = cursor.fetchall()
            logger.info("Total de parceiros com status de entrega: %s", len(parceiros))
            return parceiros
        except sqlite3.Error as exc:
            logger.error("Erro ao listar parceiros com última entrega: %s", exc)
            raise
        finally:
            cursor.close()

