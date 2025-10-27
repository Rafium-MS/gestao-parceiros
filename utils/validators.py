"""Validation helpers for the application."""

from __future__ import annotations

import re

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_email(value: str) -> bool:
    """Return ``True`` when the provided value matches an email format."""
    return bool(EMAIL_PATTERN.match(value))


def validate_non_empty(value: str) -> bool:
    """Ensure the provided value contains non-whitespace characters."""
    return bool(value and value.strip())
