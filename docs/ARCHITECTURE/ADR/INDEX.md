# ADR INDEX

Реестр архитектурных решений. Шаблон — [[ADR-000-template]].

| ADR | Заголовок | Статус |
|-----|-----------|--------|
| [ADR-001](ADR-001-test-stack-and-pom.md) | Тест-стек и архитектура контура по POM (Python + pytest + httpx) | Accepted |
| [ADR-002](ADR-002-backend-stack.md) | Бэкенд-стек продукта (FastAPI + SQLAlchemy + Alembic + PostgreSQL) | Accepted |
| [ADR-003](ADR-003-error-envelope.md) | Единый конверт ошибок и набор кодов | Accepted |
| [ADR-004](ADR-004-api-key-handling.md) | Хранение/проверка API-ключей, rate limiting | Accepted |
| [ADR-005](ADR-005-ticket-status-state-machine.md) | Машина состояний статусов заявки | Accepted |
| [ADR-006](ADR-006-soft-delete-policy.md) | Политика мягкого удаления (деактивация) | Accepted |
| [ADR-007](ADR-007-integration-processing.md) | Обработка интеграционных запросов: идемпотентность и employee_sync | Accepted |
| [ADR-008](ADR-008-test-type-and-config.md) | Тип тест-контура (B) и конфигурация окружения | Accepted |
| [ADR-009](ADR-009-admin-auth-rbac.md) | Авторизация админ-поверхности (JWT + RBAC) | Accepted |
| [ADR-010](ADR-010-production-hardening.md) | Production hardening (rate limit, queue, observability) | Accepted |

---

*Graph: [[AGENT_CONTEXT]] · [[INVARIANTS]] · [[FINAL_SYSTEM_SPEC]]*
