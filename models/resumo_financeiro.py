#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Resumo Financeiro
-------------------
Funções para calcular totais financeiros por parceiro.
"""

import logging
from typing import List, Optional, Tuple


class ResumoFinanceiro:
    """Calcula resumos financeiros a partir do banco de dados."""

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)

    def resumo_por_parceiro(
        self,
        parceiro_id: int,
        data_inicial: Optional[str] = None,
        data_final: Optional[str] = None,
    ) -> Optional[dict]:
        """Retorna o resumo financeiro de um parceiro."""
        try:
            query = "SELECT COUNT(*) FROM comprovantes WHERE parceiro_id = ?"
            params = [parceiro_id]
            if data_inicial and data_final:
                query += " AND data_entrega BETWEEN ? AND ?"
                params.extend([data_inicial, data_final])

            self.db_manager.execute(query, tuple(params))
            total_entregas = self.db_manager.fetchone()[0] or 0

            self.db_manager.execute(
                "SELECT nome, valor_unidade FROM parceiros WHERE id = ?",
                (parceiro_id,),
            )
            row = self.db_manager.fetchone()
            if not row:
                return None
            nome, valor_unidade = row
            valor_unidade = float(valor_unidade or 0)

            total_pagar = total_entregas * valor_unidade
            return {
                "parceiro_id": parceiro_id,
                "parceiro_nome": nome,
                "total_entregas": total_entregas,
                "valor_unidade": valor_unidade,
                "total_pagar": total_pagar,
            }
        except Exception as exc:
            self.logger.error("Erro ao gerar resumo financeiro: %s", exc)
            return None

    def entregas_por_mes(self, parceiro_id: int) -> List[Tuple[str, int, float]]:
        """Retorna uma lista de entregas por mês com total calculado."""
        try:
            self.db_manager.execute(
                "SELECT valor_unidade FROM parceiros WHERE id = ?",
                (parceiro_id,),
            )
            row = self.db_manager.fetchone()
            valor_unidade = float(row[0]) if row else 0.0

            self.db_manager.execute(
                """
                SELECT strftime('%Y-%m', data_entrega) AS mes, COUNT(*) AS total
                FROM comprovantes
                WHERE parceiro_id = ?
                GROUP BY mes
                ORDER BY mes
                """,
                (parceiro_id,),
            )
            resultados = self.db_manager.fetchall()
            return [
                (mes, total, total * valor_unidade) for mes, total in resultados
            ]
        except Exception as exc:
            self.logger.error("Erro ao listar entregas mensais: %s", exc)
            return []