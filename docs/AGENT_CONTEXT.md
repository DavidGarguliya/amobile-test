# AGENT_CONTEXT
<!-- Auto-maintained snapshot. Update after each meaningful state change. -->
<!-- Last updated: 2026-06-16 — Allure-отчётность подключена (epic/feature/story/severity/steps/attachments); контур green (61/61). -->
<!-- Obsidian hub: этот файл ссылается на все крупные доки; все доки ссылаются сюда. -->

## Цель продукта
Backend-сервис из трёх REST API-модулей: (1) справочник сотрудников, (2) внутренние IT-заявки,
(3) защищённое интеграционное API для внешних систем (приём по X-API-Key, аудит, обработка
администратором). Источник истины — [[SOURCE_BRIEF]]. Тип задания — **B** (строим продукт).

## Архитектура (кратко)
Монолит FastAPI, слои `api → services → repositories → db`, pydantic-схемы, единый обработчик
ошибок. Источник правды о состоянии — реляционная БД (PostgreSQL; SQLite для dev). Связи: заявки
ссылаются на сотрудников; employee_sync (модуль 3) пишет в справочник (модуль 1). Подробно —
[[FINAL_SYSTEM_SPEC]], [[SYSTEM_OVERVIEW]].

## Инварианты (кратко)
- Сотрудник не удаляется физически — только деактивация (INV-P1).
- Email уникален (INV-P2). Новая заявка = `new` (INV-P3).
- Граф статусов заявки строгий; resolved/rejected терминальны; resolved ⇒ resolved_at (INV-P5/P7).
- API-ключ только хешем, показ один раз (INV-P8); 401/403/429 на интеграции; аудит каждой попытки (INV-P9/P10).
- processed нельзя обработать повторно (INV-P11). Единый конверт ошибок (INV-X1).
Полный список — [[INVARIANTS]].

## Модель данных (кратко)
`employees`, `tickets` (FK→employees), `api_clients` (api_key_hash), `integration_requests`
(FK→api_clients, payload JSON, status enum), `audit_logs` (ip, user_agent, success). Детали —
[[FINAL_SYSTEM_SPEC]] §4.

## API-контур (кратко)
Стек тестов: **Python + pytest + httpx**, POM (BaseApiClient + `<Resource>Client`), pydantic-схемы.
Запуск: `pip install -r requirements-test.txt` → `pytest --collect-only` (гейт) → `pytest`.
Конфиг из env (`API_BASE_URL` и т.д.). Матрица покрытия — [[TEST_PLAN]] §5; как запускать —
`tests/README.md`.

## Текущее состояние
Реализация + production hardening: backend FastAPI (слои `api/services/repositories/models`) для
всех трёх модулей + JWT/RBAC (ADR-009), ключи HMAC+pepper+ротация, CONFLICT/409, фикс гонки (§45),
rate-limit/queue/observability за абстракциями (ADR-010). Весь POM-контур **green (61/61, 0 flaky)**
с Allure-отчётом (epic/feature/story/severity/tags + шаги/вложения из BaseApiClient). Реализация
влита в `main`; Allure/Postman-доработки — на ветке `feat/allure-reporting`. Детали —
[[IMPLEMENTATION_LEDGER]]. Запуск: `uvicorn app.main:app` (логин admin@example.com/admin12345 → JWT;
OpenAPI на `/docs`). Отчёт: `pytest --alluredir=allure-results && allure serve allure-results`.

## Решённые вопросы (подтверждены заказчиком 2026-06-16)
Q-1 BIGINT id · Q-2 ключ HMAC+pepper+ротация · Q-3 rate limit за интерфейсом (InMemory/Redis) ·
Q-4 JWT+RBAC · Q-5 201+Location · Q-6 base URL из env · Q-7 CONFLICT/409 · Q-8 `external_identities`.
Открытых вопросов нет; трассировка — [[REQUIREMENTS]].

## Ключевые команды
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-test.txt
cp .env.example .env
pytest --collect-only      # сборка контура (должна проходить)
pytest -q                  # полный прогон (red до реализации — норма для типа B)
```

## Индекс ADR
| ADR | Заголовок | Статус |
|-----|-----------|--------|
| 001 | Тест-стек и POM (pytest + httpx) | Accepted |
| 002 | Бэкенд-стек (FastAPI + SQLAlchemy + Alembic + PostgreSQL) | Accepted |
| 003 | Единый конверт ошибок | Accepted |
| 004 | Хранение/проверка API-ключей, rate limit | Accepted |
| 005 | Машина состояний статусов заявки | Accepted |
| 006 | Мягкое удаление (деактивация) | Accepted |
| 007 | Обработка интеграции: идемпотентность + employee_sync | Accepted |
| 008 | Тип тест-контура (B) и конфигурация окружения | Accepted |
| 009 | Авторизация админ-поверхности (JWT + RBAC) | Accepted |
| 010 | Production hardening (rate limit, queue, observability) | Accepted |

---

*Graph: [[INVARIANTS]] · [[FINAL_SYSTEM_SPEC]] · [[TEST_PLAN]] · [[STATE]] · [[CHRONICLE]] · [[ROADMAP]] · [[ADR INDEX]]*
