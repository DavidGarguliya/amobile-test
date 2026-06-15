# ADR-002: Бэкенд-стек продукта

## Status
Accepted

## Context
Бриф ([[SOURCE_BRIEF]] §5.1) допускает любой стек, БД — PostgreSQL (SQLite для dev, NFR-1).
Нужно зафиксировать стек продукта для точности README/RUNBOOK/ADR. Код продукта в этой сессии
не пишется (bootstrap), но документация должна быть конкретной. Заказчик подтвердил Python/FastAPI.

## Decision
Продукт реализуется на **Python + FastAPI + SQLAlchemy 2.x + Alembic**, БД — **PostgreSQL**
(SQLite допустим для локального запуска). Слои: `api/ → services/ → repositories/ → db` плюс
`schemas/` (pydantic), `models/` (ORM), `core/` (конфиг, ошибки, безопасность, логирование).
См. [[FINAL_SYSTEM_SPEC]] §2.

## Consequences
### Positive
- FastAPI даёт OpenAPI/Swagger из коробки → закрывает NFR-8 малой ценой.
- pydantic-валидация на входе закрывает NFR-4; единый exception handler — NFR-5/INV-X3.
- Alembic — миграции (NFR-9); SQLAlchemy абстрагирует SQLite↔PostgreSQL (INV-D4).
- Совпадает со стеком тестов (ADR-001) — единая экосистема.
### Negative
- ORM-абстракция может скрыть нюансы SQL — митигируется ревью миграций и индексов (бриф §47).

## Alternatives considered
### Node.js + NestJS + Prisma
Отклонено заказчиком в пользу Python, хотя ранний каркас репозитория упоминал npm.
### Go / Java / PHP
Отклонено: нет преимуществ под данный объём; Python выбран явно.

---

*Graph: [[AGENT_CONTEXT]] · [[FINAL_SYSTEM_SPEC]] · [[INVARIANTS]] · [[RUNBOOK]]*
