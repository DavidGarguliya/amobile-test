"""Test-suite configuration.

All configuration comes from environment variables only (no hardcoded secrets) — see ADR-008 and
invariant INV-X5. A local ``.env`` (git-ignored) may be used; ``.env.example`` documents the keys.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache

try:  # python-dotenv is optional; absence must not break collection.
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover - defensive: env still works without dotenv
    pass


def _get(name: str, default: str) -> str:
    value = os.getenv(name)
    return value if value is not None and value != "" else default


def _get_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _get_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return float(raw)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    """Immutable, environment-derived settings shared by the whole suite."""

    base_url: str = field(default_factory=lambda: _get("API_BASE_URL", "http://localhost:8000").rstrip("/"))
    http_timeout: float = field(default_factory=lambda: _get_float("HTTP_TIMEOUT", 10.0))

    # Admin authorization is not specified by the brief (OPEN QUESTION Q-4). It is configurable:
    # when ADMIN_AUTH_HEADER is empty, admin endpoints are treated as open.
    admin_auth_header: str = field(default_factory=lambda: _get("ADMIN_AUTH_HEADER", ""))
    admin_auth_token: str = field(default_factory=lambda: _get("ADMIN_AUTH_TOKEN", ""))

    # The brief does not fix success codes for create operations (Q-5). Configurable expectation.
    expect_created_code: int = field(default_factory=lambda: _get_int("EXPECT_CREATED_CODE", 201))

    # How many extra requests to fire when probing the per-minute rate limit (0 → derive from the
    # client's configured limit at runtime). See FR-I8 / AC-I6.
    rate_limit_probe_count: int = field(default_factory=lambda: _get_int("RATE_LIMIT_PROBE_COUNT", 0))

    # Header name used by the integration endpoint for the API key (brief §4.5).
    api_key_header: str = field(default_factory=lambda: _get("API_KEY_HEADER", "X-API-Key"))

    log_level: str = field(default_factory=lambda: _get("LOG_LEVEL", "INFO"))

    @property
    def admin_headers(self) -> dict[str, str]:
        """Headers applied to admin requests, empty when admin auth is not configured."""
        if self.admin_auth_header and self.admin_auth_token:
            return {self.admin_auth_header: self.admin_auth_token}
        return {}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
