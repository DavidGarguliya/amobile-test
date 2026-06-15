"""Test-data factories. Each call produces unique, isolated data (INV-O2) so specs do not collide.

Factories return request DTOs (pydantic models). Specs may convert them to dicts and mutate for
negative cases.
"""

from __future__ import annotations

import itertools
import uuid
from typing import Any

from tests.api.models.employee import EmployeeCreate
from tests.api.models.integration import ClientCreate, IntegrationRequest
from tests.api.models.ticket import TicketCreate

_counter = itertools.count(1)


def unique_suffix() -> str:
    """Short, process-unique token used to keep emails/names/ids non-colliding."""
    return f"{next(_counter)}-{uuid.uuid4().hex[:8]}"


def unique_email(prefix: str = "user") -> str:
    return f"{prefix}.{unique_suffix()}@example.com"


def employee_payload(**overrides: Any) -> EmployeeCreate:
    suffix = unique_suffix()
    data: dict[str, Any] = {
        "full_name": f"Иванов Иван {suffix}",
        "position": "Backend Developer",
        "department": "IT",
        "phone": "+79401234567",
        "email": unique_email("employee"),
    }
    data.update(overrides)
    return EmployeeCreate(**data)


def ticket_payload(employee_id: int, **overrides: Any) -> TicketCreate:
    data: dict[str, Any] = {
        "employee_id": employee_id,
        "title": f"Не работает принтер {unique_suffix()}",
        "description": "Принтер в кабинете 204 не печатает документы",
        "priority": "medium",
    }
    data.update(overrides)
    return TicketCreate(**data)


def client_payload(**overrides: Any) -> ClientCreate:
    data: dict[str, Any] = {
        "name": f"1C Integration {unique_suffix()}",
        "requests_limit_per_minute": 60,
    }
    data.update(overrides)
    return ClientCreate(**data)


def employee_sync_payload(**payload_overrides: Any) -> IntegrationRequest:
    payload: dict[str, Any] = {
        "external_id": f"EMP-{unique_suffix()}",
        "full_name": f"Иванов Иван {unique_suffix()}",
        "department": "IT",
        "position": "Developer",
        "email": unique_email("sync"),
    }
    payload.update(payload_overrides)
    return IntegrationRequest(request_type="employee_sync", payload=payload)
