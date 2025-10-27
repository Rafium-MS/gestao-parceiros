"""Formatting helpers for display purposes."""

from __future__ import annotations

import re
from datetime import date


def _only_digits(value: str | None) -> str:
    """Return only the digits from *value* or an empty string when falsy."""

    if not value:
        return ""
    return re.sub(r"\D", "", value)


def format_currency(value: float, symbol: str = "R$") -> str:
    """Return a human friendly currency representation."""

    return f"{symbol} {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_date(value: date, fmt: str = "%d/%m/%Y") -> str:
    """Format a :class:`datetime.date` instance using the configured format."""

    return value.strftime(fmt)


def formatar_cpf(cpf: str | None) -> str:
    """Return *cpf* formatted as XXX.XXX.XXX-XX when possible."""

    digits = _only_digits(cpf)
    if len(digits) != 11:
        return cpf or ""
    return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"


def formatar_cnpj(cnpj: str | None) -> str:
    """Return *cnpj* formatted as XX.XXX.XXX/XXXX-XX when possible."""

    digits = _only_digits(cnpj)
    if len(digits) != 14:
        return cnpj or ""
    return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"


def formatar_telefone(telefone: str | None) -> str:
    """Return *telefone* formatted according to its length when possible."""

    digits = _only_digits(telefone)
    if len(digits) == 11:
        return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
    if len(digits) == 10:
        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    if len(digits) == 9:
        return f"{digits[:5]}-{digits[5:]}"
    if len(digits) == 8:
        return f"{digits[:4]}-{digits[4:]}"
    return telefone or ""
