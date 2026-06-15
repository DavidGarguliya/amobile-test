"""Shared API dependencies: DB session, request metadata, pagination params."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, Header, Query, Request
from sqlalchemy.orm import Session

from app.core.auth import TokenError, decode_access_token
from app.core.config import settings
from app.core.errors import forbidden, unauthorized
from app.db.session import get_db  # re-exported for routers
from app.models.user import User
from app.repositories import users as users_repo

__all__ = [
    "get_db",
    "client_ip",
    "user_agent",
    "PageParams",
    "page_params",
    "get_current_user",
    "require_roles",
]


def client_ip(request: Request) -> str:
    return request.client.host if request.client else ""


def user_agent(request: Request) -> str:
    return request.headers.get("user-agent", "")


@dataclass
class PageParams:
    page: int
    limit: int


def page_params(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> PageParams:
    return PageParams(page=page, limit=limit)


# -- authn / authz (ADR-009) -----------------------------------------------------------------
def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User | None:
    if not settings.auth_enabled:
        return None
    if not authorization or not authorization.lower().startswith("bearer "):
        raise unauthorized("Missing or malformed Authorization header")
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = decode_access_token(token)
    except TokenError as exc:
        raise unauthorized(f"Invalid token: {exc}")
    user = users_repo.get(db, int(payload.get("sub", 0)))
    if user is None or not user.is_active:
        raise unauthorized("User not found or inactive")
    return user


def require_roles(*roles: str):
    """Dependency factory: require an authenticated user, optionally with one of ``roles``."""

    def _dependency(user: User | None = Depends(get_current_user)) -> User | None:
        if not settings.auth_enabled:
            return None
        if roles and (user is None or user.role not in roles):
            raise forbidden("Insufficient role for this operation")
        return user

    return _dependency
