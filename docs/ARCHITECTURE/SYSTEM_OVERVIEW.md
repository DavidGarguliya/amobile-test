# SYSTEM_OVERVIEW

Высокоуровневый обзор системы. Детали — в [[FINAL_SYSTEM_SPEC]] и [[INVARIANTS]].

## Контекст

```mermaid
flowchart LR
    Admin([Admin / Operator]) -->|REST /api/employees, /api/tickets, /api/admin/*| API
    Ext([External system / 1C]) -->|POST /api/integration/requests + X-API-Key| API
    API[(Backend service\nFastAPI)] --> DB[(PostgreSQL / SQLite)]
    Tests([API test suite\npytest + httpx]) -.black-box.-> API
```

## Модули и потоки

```mermaid
flowchart TD
    subgraph M1[Module 1 — Employees]
      E1[POST /api/employees]
      E2[GET /api/employees]
      E5[PATCH .../deactivate]
    end
    subgraph M2[Module 2 — Tickets]
      T1[POST /api/tickets]
      T9[PATCH .../assign → in_progress]
      T10[PATCH .../status]
      T11[GET /api/tickets/stats]
    end
    subgraph M3[Module 3 — Integration]
      I12[POST /api/admin/clients]
      I14[POST /api/integration/requests]
      I16[POST .../requests/id/process]
      I17[GET /api/admin/audit]
    end
    T1 -->|employee_id must exist| M1
    I16 -->|employee_sync: create/update| M1
    I14 -->|every attempt| AUD[(audit_logs)]
```

## Слои (внутри сервиса)

```mermaid
flowchart LR
    R[Router / Controller] --> S[Service\nбизнес-логика, инварианты] --> Repo[Repository] --> DB[(DB)]
    S --> ERR[Centralized error handler\nунифицированный конверт]
```

## Тест-контур (POM для API)

```mermaid
flowchart LR
    Spec[specs/test_*.py\nArrange-Act-Assert] --> Client[<Resource>Client\nService Object]
    Client --> Base[BaseApiClient\nтранспорт, заголовки, auth, логирование]
    Base -->|httpx| API[(API_BASE_URL)]
    Spec --> Schemas[pydantic schemas\nконтрактные проверки]
    Spec --> Fixtures[factories / fixtures]
```

Подробности слоёв тест-контура и матрица покрытия — в [[TEST_PLAN]] и `tests/README.md`.

---

*Graph: [[AGENT_CONTEXT]] · [[FINAL_SYSTEM_SPEC]] · [[INVARIANTS]] · [[TEST_PLAN]]*
