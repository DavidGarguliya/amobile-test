"""API key generation and verification (ADR-004, INV-P8).

The plaintext key is shown once at creation; only its hash is stored. A high-entropy random token
is used, so a fast cryptographic hash (SHA-256) with an indexed lookup is sufficient and keeps the
auth hot-path cheap (ADR-004).
"""

from __future__ import annotations

import hashlib
import secrets

from app.core.config import settings


def generate_api_key() -> str:
    """Return a fresh opaque key with the configured prefix (>=128 bits of entropy)."""
    return f"{settings.api_key_prefix}{secrets.token_urlsafe(32)}"


def hash_api_key(api_key: str) -> str:
    """Deterministic hash used both for storage and for lookup on authentication."""
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()
