"""FastAPI application factory and wiring (ADR-002, ADR-003, ADR-009)."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import (
    admin_clients,
    admin_integration,
    audit,
    auth,
    employees,
    integration,
    tickets,
)
from app.core.config import settings
from app.core.errors import register_error_handlers
from app.core.logging import configure_logging
from app.core.observability import RequestIdMiddleware, init_sentry
from app.db.session import SessionLocal, init_db
from app.services.auth import seed_admin


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Dev convenience: ensure tables exist (SQLite). Production relies on Alembic migrations.
    init_db()
    db = SessionLocal()
    try:
        seed_admin(db)
    finally:
        db.close()
    yield


def create_app() -> FastAPI:
    configure_logging()
    init_sentry()
    app = FastAPI(title=settings.app_name, version="2.0.0", lifespan=lifespan)
    app.add_middleware(RequestIdMiddleware)
    register_error_handlers(app)

    for module in (auth, employees, tickets, admin_clients, integration, admin_integration, audit):
        app.include_router(module.router)

    @app.get("/health", tags=["meta"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
