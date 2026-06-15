"""Shared Allure taxonomy so every spec uses identical Epic/Feature names (consistent grouping).

Hierarchy: Epic -> Feature -> Story. Use the EPIC_* constants below; Feature/Story are per-spec
literals. Severity guidance:
- BLOCKER  : authentication/authorization, key handling (security gates)
- CRITICAL : core business rules (status state machine, idempotency, ticket↔employee integrity)
- NORMAL   : CRUD happy paths, processing, audit
- MINOR    : pagination/filter/boundary niceties
"""

from __future__ import annotations

EPIC_EMPLOYEES = "ТЗ №1 — Справочник сотрудников"
EPIC_TICKETS = "ТЗ №2 — Внутренние IT-заявки"
EPIC_INTEGRATION = "ТЗ №3 — Интеграционное API"
EPIC_SECURITY = "Безопасность и доступ"
