"""Application configuration from the environment (NFR-9, INV-X5)."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database. SQLite for local dev (NFR-1); switch to a PostgreSQL DSN in production, e.g.
    # postgresql+psycopg://user:pass@host:5432/db
    database_url: str = "sqlite:///./app.db"

    # API key handling (ADR-004).
    api_key_prefix: str = "company_live_"
    api_key_header: str = "X-API-Key"

    # Default per-minute rate limit applied when a client does not specify one.
    default_rate_limit_per_minute: int = 60

    log_level: str = "INFO"
    app_name: str = "amobile-test backend"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
