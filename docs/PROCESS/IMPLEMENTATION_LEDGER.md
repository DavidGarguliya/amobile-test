# IMPLEMENTATION_LEDGER

Живой журнал реализации (mandated by AGENT_DECISIONS D11). Читать перед возобновлением разработки.
Новые записи — сверху.

---

## 2026-06-15 — Слайсы 1–4: полная реализация трёх модулей

**Что сделано.** Реализован backend на FastAPI + SQLAlchemy 2 (ADR-002), все три модуля брифа:

- **Слой приложения:** `app/core` (config, errors-конверт ADR-003, logging, security=hash ключа,
  rate_limit), `app/db` (Base+timestamp mixin, session, init_db), `app/main.py` (factory, lifespan,
  /health, авто-OpenAPI `/docs`).
- **Модель данных:** `app/models/*` — employees (+`external_id`, Q-8), tickets, api_clients,
  integration_requests, audit_logs.
- **Слои:** `repositories/*` (тонкий доступ к данным), `services/*` (бизнес-правила и инварианты),
  `api/*` (роутеры EP-01..EP-17 + deps).
- **Миграции:** Alembic (`alembic.ini`, `alembic/env.py`, initial revision `5ed0618a97bd`),
  применяется на чистую БД; переносимо на PostgreSQL (NFR-1, render_as_batch для SQLite).

**Ключевые правила/инварианты реализованы.** INV-P1 (soft delete), INV-P2 (unique email),
INV-P3/P5/P6/P7 (статус-машина заявок, ADR-005), INV-P8 (хеш ключа, показ один раз, ADR-004),
INV-P9 (401/403/429), INV-P10 (аудит каждой попытки с ip/UA), INV-P11 (идемпотентность process),
INV-P12 (employee_sync: external_id→email), INV-X1..X3 (единый конверт + централизованные хендлеры).

**Как проверено.** Поднят uvicorn (SQLite), весь POM-контур: **55 passed** дважды (детерминизм,
0 flaky). Миграция Alembic применяется на пустую БД, создаёт все таблицы. `pytest --collect-only`
проходит. Тип контура с red переведён в **green**.

**Принятые решения по OPEN QUESTIONS (дефолты, всё ещё под подтверждение заказчика).**
- Q-1 id = int autoincrement. Q-5 create → 201. Q-4 admin открыт (без auth). Q-7 дубликат email →
  422 `VALIDATION_ERROR` (сохраняет маппинг ADR-003). Q-3 rate limit — in-memory fixed window.
  Q-8 добавлена колонка `employees.external_id` (unique, nullable).

**Затронутые требования.** FR-E1..E10, FR-T1..T14, FR-I1..I19; NFR-1/2/4/5/6/8/10.

**Что осталось / follow-ups.**
- NFR-8: OpenAPI генерируется FastAPI (`/docs`); Postman-коллекция — опционально (Слайс 5).
- Admin-авторизация (Q-4), очередь обработки (§48), Redis для rate limit (§49), роли (§46),
  гонка двух process через БД-локу (§45) — отмечены как улучшения.
- `app.db` (SQLite) — локальный dev-артефакт, в git не коммитится (.gitignore).

---

*Graph: [[AGENT_CONTEXT]] · [[FINAL_SYSTEM_SPEC]] · [[INVARIANTS]] · [[TEST_PLAN]] · [[STATE]]*
