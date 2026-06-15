---
name: feedback-stack-choice
description: Заказчик зафиксировал стек — тесты на pytest+httpx, продукт на FastAPI
metadata:
  type: feedback
---

Заказчик выбрал (уточнение в начале bootstrap-сессии 2026-06-15):

- **Тест-контур:** Python + pytest + httpx (вместо дефолта мета-промпта TS+Playwright).
- **Бэкенд продукта:** Python + FastAPI + SQLAlchemy + Alembic + PostgreSQL.

**Почему:** единый язык тестов и продукта упрощает поддержку/ревью; FastAPI даёт OpenAPI из коробки
(закрывает требование документации API). Зафиксировано в ADR-001 и ADR-002.

**Как применять:** новые тесты писать на pytest+httpx по POM (клиенты в `tests/api/clients`,
схемы pydantic); продуктовый код — FastAPI со слоями api/services/repositories. Не вводить иной
стек без нового ADR. См. [[project-scope-and-status]], [[reference-how-to-run-tests]].
