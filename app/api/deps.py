"""Shared API dependencies: DB session, request metadata, pagination params."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Query, Request

from app.db.session import get_db  # re-exported for routers

__all__ = ["get_db", "client_ip", "user_agent", "PageParams", "page_params"]


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
