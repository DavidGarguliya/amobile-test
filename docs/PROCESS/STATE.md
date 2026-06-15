# STATE

<!-- Текущий срез работ. Обновляется при каждом значимом изменении состояния. -->

## Сейчас в работе
**Всё выполнено и влито в `main`.** Backend (FastAPI + SQLAlchemy + Alembic): три модуля + JWT/RBAC,
усиление ключей, CONFLICT/409, атомарная обработка (§45), rate-limit/queue/observability за
абстракциями, Allure-отчётность, auth-aware Postman, аудит-фиксы. Весь POM-контур — **green (62/62)**.
Активной незавершённой работы нет.

## Статус по областям
- Документация: ✅ собрана (PRODUCT, ARCHITECTURE+ADR×8, PROCESS, OPERATIONS, QA) + IMPLEMENTATION_LEDGER.
- Семантическая память: ✅ засеяна и обновлена.
- Тест-контур: ✅ **62/62 passed** против живого сервера (дважды, 0 flaky). `--collect-only` проходит.
- Приложение: ✅ `app/` (core, db, models, schemas, repositories, services, api, main, worker), `/docs` OpenAPI.
- Безопасность: ✅ JWT+RBAC (ADR-009), ключи HMAC+pepper+ротация, CONFLICT/409, фикс гонки (§45).
- Прод-инфра: ✅ за абстракциями (rate-limit/queue/observability), Redis/Arq/Sentry опциональны.
- Миграции: ✅ Alembic, initial revision применяется на чистую БД (NFR-1).
- CI: ✅ `tests.yml` (+ публикация Allure-результатов/отчёта).
- Allure: ✅ каждый тест размечен; шаги/вложения из BaseApiClient.
- Git/GitHub: PR #1 (реализация+hardening) и PR #2 (Allure+Postman+аудит-фиксы) squash-merged в `main`.

## Блокеры / ожидания
- Нет блокеров. Q-1..Q-8 — DECIDED (подтверждены 2026-06-16). Всё влито в `main`.

## Next steps (опционально, по запросу)
1. Deferred-улучшения: blacklist JWT-токенов (отзыв до истечения), per-resource scopes,
   полнотекстовый поиск (GIN/tsvector), проверка путей Redis/Arq/Sentry на реальной инфраструктуре.

---

*Graph: [[AGENT_CONTEXT]] · [[ROADMAP]] · [[CHRONICLE]] · [[TEST_PLAN]]*
