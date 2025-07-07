#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Informações de Versão
--------------------
Define a versão atual do sistema e funções auxiliares relacionadas.
"""

# Informações de versão
VERSION_MAJOR = 1
VERSION_MINOR = 1
VERSION_PATCH = 1

# Data de lançamento
RELEASE_DATE = "2025-07-07"

# Informações adicionais
BUILD_TYPE = "stable"  # 'alpha', 'beta', 'rc', 'stable'


def get_version_string(include_build_type=True):
    """
    Retorna a string formatada da versão atual.

    Args:
        include_build_type (bool): Se True, inclui o tipo de build na string.

    Returns:
        str: String formatada da versão.
    """
    version = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"

    if include_build_type and BUILD_TYPE != "stable":
        version += f"-{BUILD_TYPE}"

    return version


def get_version_info():
    """
    Retorna um dicionário com todas as informações de versão.

    Returns:
        dict: Dicionário com informações detalhadas da versão.
    """
    return {
        "major": VERSION_MAJOR,
        "minor": VERSION_MINOR,
        "patch": VERSION_PATCH,
        "full": get_version_string(),
        "release_date": RELEASE_DATE,
        "build_type": BUILD_TYPE
    }