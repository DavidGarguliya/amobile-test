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

**Статус:** bootstrap — пакет документации и контур API-тестов собраны, основная разработка НЕ
начата (ожидается апрув). Следующий слайс — каркас FastAPI-приложения.

**Ключевые ограничения:** БД PostgreSQL (SQLite для dev); единый конверт ошибок; API-ключ только
хешем + показ один раз; строгая машина статусов заявок; идемпотентная обработка интеграции.

См. [[reference-source-brief-and-remote]], [[assumptions-to-confirm]], [[reference-how-to-run-tests]],
[[feedback-stack-choice]].
