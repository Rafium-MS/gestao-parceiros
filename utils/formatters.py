"""Formatting helpers for display purposes."""

from __future__ import annotations

from datetime import date


def format_currency(value: float, symbol: str = "R$") -> str:
    """Return a human friendly currency representation."""
    return f"{symbol} {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_date(value: date, fmt: str = "%d/%m/%Y") -> str:
    """Format a :class:`datetime.date` instance using the configured format."""
    return value.strftime(fmt)
