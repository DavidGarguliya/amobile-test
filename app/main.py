"""FastAPI application factory and wiring (ADR-002, ADR-003)."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import (
    admin_clients,
    admin_integration,
    audit,
    employees,
    integration,
    tickets,
)
from app.core.config import settings
from app.core.errors import register_error_handlers
from app.core.logging import configure_logging
from app.db.session import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Dev convenience: ensure tables exist (SQLite). Production relies on Alembic migrations.
    init_db()
    yield


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
    register_error_handlers(app)

    for module in (employees, tickets, admin_clients, integration, admin_integration, audit):
        app.include_router(module.router)

    @app.get("/health", tags=["meta"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
