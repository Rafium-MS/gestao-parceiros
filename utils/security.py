"""Security related helpers."""

from __future__ import annotations

import hashlib
import hmac
from secrets import token_hex


def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    """Return a salted SHA-256 hash of the provided password."""
    salt_value = salt or token_hex(16)
    digest = hashlib.sha256(f"{salt_value}{password}".encode("utf-8")).hexdigest()
    return salt_value, digest


def verify_password(password: str, salt: str, expected_hash: str) -> bool:
    """Verify that the password matches the stored hash."""
    _, computed_hash = hash_password(password, salt=salt)
    return hmac.compare_digest(expected_hash, computed_hash)
