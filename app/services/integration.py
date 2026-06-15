"""Integration ingress: authenticate, enforce limits, persist request, audit every attempt.

Invariants: INV-P8 (hash lookup), INV-P9 (auth/active/limit), INV-P10 (audit each attempt).
"""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.core.errors import ApiError, forbidden, rate_limited, unauthorized
from app.core.rate_limit import rate_limiter
from app.core.security import hash_api_key
from app.models.integration_request import IntegrationRequest
from app.repositories import api_clients as clients_repo
from app.repositories import audit as audit_repo
from app.repositories import integration_requests as requests_repo
from app.schemas.integration import IntegrationRequestIn

logger = logging.getLogger("app.integration")
ACTION = "integration.submit"


def submit_request(
    db: Session,
    api_key: str | None,
    data: IntegrationRequestIn,
    *,
    ip_address: str,
    user_agent: str,
) -> IntegrationRequest:
    def audit(client_id: int | None, success: bool, details: dict) -> None:
        audit_repo.create(
            db,
            client_id=client_id,
            action=ACTION,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            details=details,
        )

    # 1) Authentication (FR-I5, FR-I6) — every attempt audited even on failure (INV-P10).
    if not api_key:
        audit(None, False, {"error": "UNAUTHORIZED", "reason": "missing api key"})
        raise unauthorized("API key is missing")
    client = clients_repo.get_by_hash(db, hash_api_key(api_key))
    if client is None:
        audit(None, False, {"error": "UNAUTHORIZED", "reason": "invalid api key"})
        raise unauthorized("API key is invalid")

    # 2) Active client (FR-I7).
    if not client.is_active:
        audit(client.id, False, {"error": "FORBIDDEN", "reason": "client deactivated"})
        raise forbidden("API client is deactivated")

    # 3) Rate limit (FR-I8).
    if not rate_limiter.allow(client.id, client.requests_limit_per_minute):
        audit(client.id, False, {"error": "RATE_LIMIT_EXCEEDED"})
        raise rate_limited("Per-minute request limit exceeded")

    # 4) Persist accepted request (FR-I10) and audit success (FR-I11/I12).
    request = requests_repo.create(
        db,
        client_id=client.id,
        request_type=data.request_type,
        payload=data.payload,
        status="accepted",
    )
    audit(client.id, True, {"request_id": request.id, "request_type": data.request_type})
    logger.info("integration request accepted id=%s client=%s", request.id, client.id)
    return request


def authenticate(db: Session, api_key: str | None):
    """Resolve a client by key (used where auditing is not required). Raises ApiError on failure."""
    if not api_key:
        raise unauthorized("API key is missing")
    client = clients_repo.get_by_hash(db, hash_api_key(api_key))
    if client is None:
        raise unauthorized("API key is invalid")
    if not client.is_active:
        raise forbidden("API client is deactivated")
    return client


def list_requests(db: Session, **filters) -> tuple[list[IntegrationRequest], int]:
    return requests_repo.list_requests(db, **filters)


__all__ = ["submit_request", "authenticate", "list_requests", "ApiError"]
