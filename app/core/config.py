"""Application configuration from the environment (NFR-9, INV-X5)."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database. SQLite for local dev (NFR-1); switch to a PostgreSQL DSN in production, e.g.
    # postgresql+psycopg://user:pass@host:5432/db
    database_url: str = "sqlite:///./app.db"

    # API key handling (ADR-004). The pepper is a server-side secret: a DB dump alone cannot be
    # used to verify guessed keys offline. MUST be overridden in production.
    api_key_prefix: str = "company_live_"
    api_key_header: str = "X-API-Key"
    api_key_pepper: str = "dev-insecure-pepper-change-me"

    # Default per-minute rate limit applied when a client does not specify one.
    default_rate_limit_per_minute: int = 60
    # Optional Redis DSN for distributed rate limiting / queue. Falls back to in-process when unset.
    redis_url: str | None = None

    # Admin authn/authz (ADR-009). JWT (HS256). Secret MUST be overridden in production.
    auth_enabled: bool = True
    jwt_secret: str = "dev-insecure-jwt-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_ttl_minutes: int = 60
    # Bootstrap admin user, seeded on startup if absent.
    admin_email: str = "admin@example.com"
    admin_password: str = "admin12345"

    # Observability.
    sentry_dsn: str | None = None
    log_level: str = "INFO"
    log_json: bool = False

    app_name: str = "amobile-test backend"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
