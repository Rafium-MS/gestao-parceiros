"""Lightweight password hashing utilities compatible with Werkzeug's API."""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from typing import Tuple

_DEFAULT_METHOD = "pbkdf2:sha256"
_DEFAULT_ITERATIONS = 260000


def _normalize_password(password: str | bytes) -> str:
    if password is None:
        raise ValueError("Password must not be None")
    if isinstance(password, bytes):
        password = password.decode("utf-8")
    if not isinstance(password, str):
        raise TypeError("Password must be a string")
    if password == "":
        raise ValueError("Password must not be empty")
    return password


def _parse_hash(pwhash: str) -> Tuple[str, int, str, str]:
    parts = pwhash.split("$")
    if len(parts) != 3:
        raise ValueError("Invalid hash format")
    method_part, salt, checksum = parts
    method_bits = method_part.split(":")
    if len(method_bits) == 3:
        method = f"{method_bits[0]}:{method_bits[1]}"
        iterations = int(method_bits[2])
    elif len(method_bits) == 2:
        method = method_part
        iterations = _DEFAULT_ITERATIONS
    else:
        raise ValueError("Invalid method specification")
    return method, iterations, salt, checksum


def generate_password_hash(password: str | bytes, method: str = _DEFAULT_METHOD, salt_length: int = 16) -> str:
    """Generate a password hash using PBKDF2-SHA256."""
    password_str = _normalize_password(password)
    if method != _DEFAULT_METHOD:
        raise ValueError("Only pbkdf2:sha256 method is supported in this build")
    if salt_length <= 0:
        raise ValueError("Salt length must be positive")

    salt = secrets.token_hex(salt_length)
    dk = hashlib.pbkdf2_hmac(
        "sha256", password_str.encode("utf-8"), salt.encode("utf-8"), _DEFAULT_ITERATIONS
    )
    digest = base64.b64encode(dk).decode("utf-8")
    return f"{method}:{_DEFAULT_ITERATIONS}${salt}${digest}"


def check_password_hash(pwhash: str, password: str | bytes) -> bool:
    """Check a password against a given hash."""
    if pwhash is None:
        return False
    password_str = _normalize_password(password)
    try:
        method, iterations, salt, checksum = _parse_hash(pwhash)
    except Exception:
        return False
    if method != _DEFAULT_METHOD:
        raise ValueError("Unsupported hash method")

    candidate = hashlib.pbkdf2_hmac(
        "sha256", password_str.encode("utf-8"), salt.encode("utf-8"), iterations
    )
    candidate_digest = base64.b64encode(candidate).decode("utf-8")
    return hmac.compare_digest(candidate_digest, checksum)
