---
name: project-scope-and-status
description: Цель, объём, тип задания (B) и статус bootstrap проекта amobile-test
metadata:
  type: project
---

Проект `amobile-test` — тестовое задание для backend-разработчика: backend-сервис из трёх REST
API-модулей (справочник сотрудников; внутренние IT-заявки; защищённое интеграционное API с
X-API-Key, аудитом и обработкой администратором). Источник истины — `docs/PRODUCT/SOURCE_BRIEF.md`.

**Тип задания: B** — готового API нет, продукт нужно построить; контур API-тестов — это
TDD-спецификация (часть тестов red до реализации).

**Статус (2026-06-15):** реализация (Слайсы 1–4) и финализация (Слайс 5) завершены. Backend на
FastAPI + SQLAlchemy + Alembic (`app/`), все три модуля, весь POM-контур **green (55/55)**.
Готовы API-доки: Swagger `/docs`, `docs/openapi.json`, Postman `postman/`, примеры
`docs/API_EXAMPLES.md`, ответы §43–52 `docs/PRODUCT/ADDITIONAL_QUESTIONS.md`. Работа на ветке
`feat/next-stage-baseline` (PR #1 в `main`). Детали — `docs/PROCESS/IMPLEMENTATION_LEDGER.md`.

**Ключевые ограничения:** БД PostgreSQL (SQLite для dev); единый конверт ошибок; API-ключ только
хешем + показ один раз; строгая машина статусов заявок; идемпотентная обработка интеграции.

См. [[reference-source-brief-and-remote]], [[assumptions-to-confirm]], [[reference-how-to-run-tests]],
[[feedback-stack-choice]].
