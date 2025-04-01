#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Validadores e Formatadores
--------------------------
Funções para validação e formatação de dados como CPF, CNPJ, email, datas.
"""

import re
import logging
import datetime

# Configuração de logging
logger = logging.getLogger(__name__)

def validar_data(data_str):
    """
    Valida uma data no formato YYYY-MM-DD.

    Args:
        data_str (str): Data no formato 'YYYY-MM-DD'.

    Returns:
        bool: True se a data for válida, False caso contrário.
    """
    try:
        if not data_str:
            return False

        # Tentar converter para datetime
        if '-' in data_str:
            ano, mes, dia = data_str.split('-')
            datetime.date(int(ano), int(mes), int(dia))
        elif '/' in data_str:
            dia, mes, ano = data_str.split('/')
            datetime.date(int(ano), int(mes), int(dia))
        else:
            return False

        return True
    except (ValueError, TypeError):
        return False


def formatar_data(data_str):
    """
    Formata uma data para exibição.
    Converte de YYYY-MM-DD para DD/MM/YYYY.

    Args:
        data_str (str): Data no formato 'YYYY-MM-DD'.

    Returns:
        str: Data formatada ou string vazia se inválida.
    """
    try:
        if not data_str:
            return ""

        # Se já estiver no formato DD/MM/YYYY, retornar
        if '/' in data_str and len(data_str.split('/')[0]) == 2:
            return data_str

        # Converter de YYYY-MM-DD para DD/MM/YYYY
        if '-' in data_str:
            ano, mes, dia = data_str.split('-')
            return f"{dia.zfill(2)}/{mes.zfill(2)}/{ano}"

        return data_str
    except (ValueError, TypeError, IndexError):
        return data_str


def formatar_data_iso(data_str):
    """
    Formata uma data para o formato ISO (YYYY-MM-DD).
    Converte de DD/MM/YYYY para YYYY-MM-DD.

    Args:
        data_str (str): Data no formato 'DD/MM/YYYY'.

    Returns:
        str: Data formatada ou string vazia se inválida.
    """
    try:
        if not data_str:
            return ""

        # Se já estiver no formato YYYY-MM-DD, retornar
        if '-' in data_str and len(data_str.split('-')[0]) == 4:
            return data_str

        # Converter de DD/MM/YYYY para YYYY-MM-DD
        if '/' in data_str:
            dia, mes, ano = data_str.split('/')
            return f"{ano}-{mes.zfill(2)}-{dia.zfill(2)}"

        return data_str
    except (ValueError, TypeError, IndexError):
        return data_str

def limpar_formatacao(texto):
    """
    Remove caracteres não numéricos de um texto.

    Args:
        texto (str): Texto a ser limpo.

    Returns:
        str: Texto contendo apenas caracteres numéricos.
    """
    if not texto:
        return ""
    return re.sub(r'[^0-9]', '', texto)


def validar_cpf(cpf):
    """
    Valida um número de CPF.

    Args:
        cpf (str): Número de CPF, pode incluir formatação.

    Returns:
        bool: True se o CPF é válido, False caso contrário.
    """
    # Limpar formatação
    cpf = limpar_formatacao(cpf)

    # Verificar tamanho
    if len(cpf) != 11:
        return False

    # Verificar se todos os dígitos são iguais
    if len(set(cpf)) == 1:
        return False

    # Cálculo do primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto

    # Verificar o primeiro dígito
    if digito1 != int(cpf[9]):
        return False

    # Cálculo do segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto

    # Verificar o segundo dígito
    if digito2 != int(cpf[10]):
        return False

    return True


def formatar_cpf(cpf):
    """
    Formata um número de CPF no padrão XXX.XXX.XXX-XX.

    Args:
        cpf (str): Número de CPF, pode incluir formatação.

    Returns:
        str: CPF formatado ou string vazia se inválido.
    """
    # Limpar formatação
    cpf = limpar_formatacao(cpf)

    # Verificar tamanho
    if len(cpf) != 11:
        return cpf

    # Formatar CPF
    return f"{cpf[0:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}"


def validar_cnpj(cnpj):
    """
    Valida um número de CNPJ.

    Args:
        cnpj (str): Número de CNPJ, pode incluir formatação.

    Returns:
        bool: True se o CNPJ é válido, False caso contrário.
    """
    # Limpar formatação
    cnpj = limpar_formatacao(cnpj)

    # Verificar tamanho
    if len(cnpj) != 14:
        return False

    # Verificar se todos os dígitos são iguais
    if len(set(cnpj)) == 1:
        return False

    # Calcular o primeiro dígito verificador
    pesos = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * pesos[i] for i in range(12))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto

    # Verificar o primeiro dígito
    if digito1 != int(cnpj[12]):
        return False

    # Calcular o segundo dígito verificador
    pesos = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * pesos[i] for i in range(13))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto

    # Verificar o segundo dígito
    if digito2 != int(cnpj[13]):
        return False

    return True


def formatar_cnpj(cnpj):
    """
    Formata um número de CNPJ no padrão XX.XXX.XXX/XXXX-XX.

    Args:
        cnpj (str): Número de CNPJ, pode incluir formatação.

    Returns:
        str: CNPJ formatado ou string vazia se inválido.
    """
    # Limpar formatação
    cnpj = limpar_formatacao(cnpj)

    # Verificar tamanho
    if len(cnpj) != 14:
        return cnpj

    # Formatar CNPJ
    return f"{cnpj[0:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}"


def validar_email(email):
    """
    Valida um endereço de e-mail.

    Args:
        email (str): Endereço de e-mail a ser validado.

    Returns:
        bool: True se o e-mail é válido, False caso contrário.
    """
    if not email:
        return True  # E-mail vazio é considerado válido (campo opcional)

    # Padrão básico de validação de e-mail
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(padrao, email))


def formatar_telefone(telefone):
    """
    Formata um número de telefone.

    Args:
        telefone (str): Número de telefone, pode incluir formatação.

    Returns:
        str: Telefone formatado ou string original se não for possível formatar.
    """
    # Limpar formatação
    telefone = limpar_formatacao(telefone)

    # Verificar tamanho
    if len(telefone) == 10:  # Telefone fixo: (XX) XXXX-XXXX
        return f"({telefone[0:2]}) {telefone[2:6]}-{telefone[6:10]}"
    elif len(telefone) == 11:  # Celular: (XX) XXXXX-XXXX
        return f"({telefone[0:2]}) {telefone[2:7]}-{telefone[7:11]}"
    else:
        return telefone  # Retorna o original se não conseguir formatar


def validar_data(data, formato="%d/%m/%Y"):
    """
    Valida uma data no formato especificado.

    Args:
        data (str): Data a ser validada.
        formato (str, optional): Formato da data. Padrão: "%d/%m/%Y".

    Returns:
        bool: True se a data é válida, False caso contrário.
        datetime.datetime: Objeto datetime se a data for válida, None caso contrário.
    """
    try:
        import datetime
        data_obj = datetime.datetime.strptime(data, formato)
        return True, data_obj
    except (ValueError, TypeError):
        return False, None