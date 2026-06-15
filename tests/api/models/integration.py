"""Request DTOs for the Integration / Admin resources (EP-12, EP-14)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ClientCreate(BaseModel):
    name: str
    requests_limit_per_minute: int


class IntegrationRequest(BaseModel):
    request_type: str
    payload: dict[str, Any] = Field(default_factory=dict)
