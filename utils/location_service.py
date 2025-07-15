#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Serviço de Localização
----------------------
Funções auxiliares para obter estados e cidades brasileiras utilizando a
API de localidades do IBGE.
"""

from __future__ import annotations

import logging
from typing import List, Dict, Any

import requests

logger = logging.getLogger(__name__)

# URLs da API do IBGE
_ESTADOS_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
_CIDADES_URL = (
    "https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios"
)


def obter_estados() -> List[Dict[str, Any]]:
    """Retorna a lista de estados brasileiros.

    Returns
    -------
    list
        Lista de dicionários contendo ``id``, ``nome`` e ``sigla`` dos estados.
    """

    try:
        resp = requests.get(_ESTADOS_URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        estados = [
            {"id": item["id"], "nome": item["nome"], "sigla": item["sigla"]}
            for item in data
        ]
        return sorted(estados, key=lambda e: e["nome"])
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Erro ao obter estados: %s", exc)
        return []


def obter_cidades_por_estado(uf: str | int) -> List[str]:
    """Retorna a lista de cidades para o estado informado.

    Parameters
    ----------
    uf : str | int
        Sigla ou ID do estado.

    Returns
    -------
    list
        Lista ordenada com os nomes das cidades do estado.
    """

    if not uf:
        return []

    try:
        url = _CIDADES_URL.format(uf=uf)
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        cidades = [item["nome"] for item in data]
        return sorted(cidades)
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Erro ao obter cidades para %s: %s", uf, exc)
        return []