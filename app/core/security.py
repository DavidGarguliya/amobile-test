"""API key generation/verification (ADR-004, INV-P8).

Key format ``company_live_<key_id>_<secret>`` (Stripe-style):
- ``key_id`` is stored in plaintext and indexed → O(1) lookup without scanning hashes.
- ``secret`` is high-entropy; the DB stores only ``HMAC-SHA256(secret, pepper)`` (a server-side
  pepper means a DB dump alone cannot verify guessed keys offline).
- The plaintext key is shown once at creation; rotation is supported via the ``api_keys`` table.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass

from app.core.config import settings


@dataclass(frozen=True)
class GeneratedKey:
    key_id: str
    secret: str
    plaintext: str
    prefix: str  # safe-to-display prefix, e.g. "company_live_ab12cd34"


def generate_api_key() -> GeneratedKey:
    key_id = secrets.token_hex(6)  # 12 hex chars, contains no "_"
    secret = secrets.token_urlsafe(32)  # >=128 bits
    plaintext = f"{settings.api_key_prefix}{key_id}_{secret}"
    return GeneratedKey(key_id=key_id, secret=secret, plaintext=plaintext, prefix=f"{settings.api_key_prefix}{key_id}")


def parse_api_key(plaintext: str | None) -> tuple[str, str] | None:
    """Split a presented key into (key_id, secret); return None if the format is wrong."""
    if not plaintext or not plaintext.startswith(settings.api_key_prefix):
        return None
    rest = plaintext[len(settings.api_key_prefix):]
    if "_" not in rest:
        return None
    key_id, secret = rest.split("_", 1)
    if not key_id or not secret:
        return None
    return key_id, secret


def hash_secret(secret: str) -> str:
    """Keyed hash (HMAC-SHA256 with server pepper) for storage and constant-time verification."""
    return hmac.new(settings.api_key_pepper.encode(), secret.encode(), hashlib.sha256).hexdigest()


def verify_secret(secret: str, stored_hash: str) -> bool:
    return hmac.compare_digest(hash_secret(secret), stored_hash)
