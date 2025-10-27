"""Serviços de domínio relacionados aos parceiros."""

from __future__ import annotations

from typing import Any

from models.repositories import ComprovantesRepository, ParceirosRepository
from utils.validators import validate_email, validate_non_empty


class ParceiroService:
    """Centraliza regras de negócio referentes aos parceiros."""

    def __init__(
        self,
        parceiros_repo: ParceirosRepository,
        comprovantes_repo: ComprovantesRepository,
    ) -> None:
        self._parceiros_repo = parceiros_repo
        self._comprovantes_repo = comprovantes_repo

    def validar_parceiro(self, dados: dict[str, Any]) -> tuple[bool, list[str]]:
        """Valida e sanitiza os dados do parceiro.

        O dicionário de entrada é atualizado in-place com os valores sanitizados
        (strings aparadas, números convertidos, campos opcionais definidos como
        ``None``). Retorna ``True`` em caso de sucesso, acompanhado de uma lista
        vazia de mensagens. Em caso de falha retorna ``False`` e as mensagens de
        erro correspondentes.
        """

        mensagens: list[str] = []

        nome = dados.get("nome", "")
        nome = nome.strip()
        if not validate_non_empty(nome):
            mensagens.append("Informe o nome do parceiro.")
        dados["nome"] = nome

        dados["distribuidora"] = dados.get("distribuidora", "").strip()
        dados["cidade"] = dados.get("cidade", "").strip()
        dados["estado"] = dados.get("estado", "").strip()
        dados["cnpj"] = dados.get("cnpj", "").strip()
        dados["telefone"] = dados.get("telefone", "").strip()

        email = dados.get("email", "").strip()
        if email and not validate_email(email):
            mensagens.append("E-mail inválido.")
        dados["email"] = email

        dia_pagamento_raw = str(dados.get("dia_pagamento", "") or "").strip()
        if dia_pagamento_raw:
            try:
                dados["dia_pagamento"] = int(dia_pagamento_raw)
            except ValueError:
                mensagens.append("Dia de pagamento inválido.")
        else:
            dados["dia_pagamento"] = None

        dados["banco"] = dados.get("banco", "").strip()
        dados["agencia"] = dados.get("agencia", "").strip()
        dados["conta"] = dados.get("conta", "").strip()
        dados["pix"] = dados.get("pix", "").strip()

        for campo, rotulo in (
            ("valor_20l", "Valor 20L"),
            ("valor_10l", "Valor 10L"),
            ("valor_cx_copo", "Valor Caixa Copo"),
            ("valor_1500ml", "Valor 1500ml"),
        ):
            valor = self._parse_float(dados.get(campo), rotulo, mensagens)
            dados[campo] = valor

        sucesso = not mensagens
        return sucesso, mensagens

    def calcular_total_a_receber(
        self,
        parceiro_id: int,
        data_inicio: str | None = None,
        data_fim: str | None = None,
    ) -> float:
        """Calcula o valor total a receber de um parceiro no período."""

        total = 0.0
        registros = self._comprovantes_repo.relatorio_por_parceiro(
            parceiro_id, data_inicio, data_fim
        )
        for registro in registros:
            (
                _nome_loja,
                _data_entrega,
                qtd_20l,
                qtd_10l,
                qtd_cx_copo,
                qtd_1500ml,
                valor_20l,
                valor_10l,
                valor_cx_copo,
                valor_1500ml,
            ) = registro
            total += (
                self._safe_multiplica(qtd_20l, valor_20l)
                + self._safe_multiplica(qtd_10l, valor_10l)
                + self._safe_multiplica(qtd_cx_copo, valor_cx_copo)
                + self._safe_multiplica(qtd_1500ml, valor_1500ml)
            )
        return total

    def pode_deletar_parceiro(self, parceiro_id: int) -> tuple[bool, str]:
        """Verifica se o parceiro pode ser removido sem pendências."""

        comprovantes = self._comprovantes_repo.count_by_parceiro(parceiro_id)
        if comprovantes > 0:
            return (
                False,
                f"Parceiro tem {comprovantes} comprovantes. Não pode deletar.",
            )
        return True, "OK"

    @staticmethod
    def _parse_float(valor: Any, rotulo: str, mensagens: list[str]) -> float | None:
        if valor is None:
            return None
        valor_str = str(valor).strip()
        if not valor_str:
            return None
        try:
            return float(valor_str.replace(",", "."))
        except ValueError:
            mensagens.append(f"{rotulo} inválido.")
            return None

    @staticmethod
    def _safe_multiplica(quantidade: Any, valor: Any) -> float:
        quantidade_num = float(quantidade or 0)
        valor_num = float(valor or 0)
        return quantidade_num * valor_num
