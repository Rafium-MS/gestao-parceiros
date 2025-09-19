"""Minimal subset of the Werkzeug API required for local password hashing."""

from .security import check_password_hash, generate_password_hash

__all__ = ["generate_password_hash", "check_password_hash"]
