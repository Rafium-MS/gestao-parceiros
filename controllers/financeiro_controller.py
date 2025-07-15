#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Controlador Financeiro
-----------------------
Opera sobre resumos financeiros e geração de recibos.
"""

import configparser
import logging
import os
from typing import Optional

from models.resumo_financeiro import ResumoFinanceiro
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas


class FinanceiroController:
    """Controlador para operações financeiras."""

    def __init__(self, db_manager, config: Optional[configparser.ConfigParser] = None):
        self.db_manager = db_manager
        self.resumo = ResumoFinanceiro(db_manager)
        self.logger = logging.getLogger(__name__)
        self.config = config or configparser.ConfigParser()
        if not self.config.sections():
            self.config.read("config.ini")

    def resumo_parceiro(self, parceiro_id: int, data_inicial: Optional[str] = None, data_final: Optional[str] = None):
        """Retorna o resumo financeiro do parceiro."""
        return self.resumo.resumo_por_parceiro(parceiro_id, data_inicial, data_final)

    def entregas_mensais(self, parceiro_id: int):
        """Obtém entregas agrupadas por mês."""
        return self.resumo.entregas_por_mes(parceiro_id)

    def gerar_recibo_pdf(
        self,
        parceiro_id: int,
        data_inicial: str,
        data_final: str,
        caminho_saida: str,
    ) -> bool:
        """Gera um recibo simples em PDF."""
        resumo = self.resumo_parceiro(parceiro_id, data_inicial, data_final)
        if not resumo:
            return False

        try:
            pdf = canvas.Canvas(caminho_saida, pagesize=A4)
            largura, altura = A4

            logo_path = self.config.get("RELATORIOS", "logo_path", fallback="")
            if logo_path and os.path.exists(logo_path):
                pdf.drawImage(logo_path, 2 * cm, altura - 4 * cm, width=4 * cm, preserveAspectRatio=True, mask="auto")

            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawString(2 * cm, altura - 5 * cm, "Recibo de Pagamento")

            pdf.setFont("Helvetica", 12)
            pdf.drawString(2 * cm, altura - 6 * cm, f"Parceiro: {resumo['parceiro_nome']}")
            pdf.drawString(2 * cm, altura - 7 * cm, f"Per\u00edodo: {data_inicial} a {data_final}")
            pdf.drawString(2 * cm, altura - 8 * cm, f"Entregas: {resumo['total_entregas']}")
            pdf.drawString(2 * cm, altura - 9 * cm, f"Valor unidade: R$ {resumo['valor_unidade']:.2f}")
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(2 * cm, altura - 10 * cm, f"Total a pagar: R$ {resumo['total_pagar']:.2f}")

            pdf.showPage()
            pdf.save()
            self.logger.info("Recibo gerado em %s", caminho_saida)
            return True
        except Exception as exc:
            self.logger.error("Erro ao gerar recibo PDF: %s", exc)
            return False