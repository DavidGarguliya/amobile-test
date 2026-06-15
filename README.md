# amobile-test — Backend test assignment (three API modules)

Backend-сервис из трёх REST API-модулей: справочник сотрудников, внутренние IT-заявки и
защищённое интеграционное API для внешних систем. Все три модуля **реализованы** (FastAPI +
SQLAlchemy + Alembic); исполняемый контур API-тестов (POM, pytest + httpx) — **green, 55/55**.

> Источник требований — [docs/PRODUCT/SOURCE_BRIEF.md](docs/PRODUCT/SOURCE_BRIEF.md) (дословная копия).

## Стек

- **Продукт:** Python 3.11+, FastAPI + SQLAlchemy 2 + Alembic, PostgreSQL (SQLite для dev) — см.
  [ADR-002](docs/ARCHITECTURE/ADR/ADR-002-backend-stack.md). Документация API: Swagger `/docs`,
  `docs/openapi.json`, Postman-коллекция `postman/`.
- **Тесты:** pytest, httpx, pydantic, POM (см. [ADR-001](docs/ARCHITECTURE/ADR/ADR-001-test-stack-and-pom.md)).

## Структура репозитория

```
.
├── app/                      # приложение FastAPI
│   ├── api/                  # роутеры (EP-01..EP-17) + deps
│   ├── services/             # бизнес-логика и инварианты
│   ├── repositories/         # доступ к данным (SQLAlchemy)
│   ├── models/               # ORM-модели
│   ├── schemas/              # pydantic request/response
│   ├── core/                 # config, errors (конверт), security, rate_limit, logging
│   ├── db/                   # base + session
│   └── main.py               # app factory, /health, OpenAPI
├── alembic/                  # миграции (initial revision) + env.py
├── postman/                  # Postman collection
├── tests/                    # POM-контур API-тестов (см. tests/README.md)
│   └── api/{clients,models,schemas,fixtures,config,utils,specs}
├── docs/
│   ├── AGENT_CONTEXT.md      # хаб графа: всегда-актуальный снимок проекта
│   ├── API_EXAMPLES.md       # примеры запросов/ответов; openapi.json — экспорт схемы
│   ├── ARCHITECTURE/         # INVARIANTS, FINAL_SYSTEM_SPEC, SYSTEM_OVERVIEW, ADR/*
│   ├── PRODUCT/              # SOURCE_BRIEF, REQUIREMENTS, AC, TECH_DECISIONS, ADDITIONAL_QUESTIONS
│   ├── PROCESS/              # STATE, CHRONICLE, ROADMAP, IMPLEMENTATION_LEDGER, BRANCHING, PR_GEN
│   ├── OPERATIONS/           # RUNBOOK
│   └── QA/                   # TEST_PLAN (+ матрица трассируемости)
├── memory/                   # семантическая память проекта (+ MEMORY.md индекс)
├── AGENTS.md ENGINEER_MODE.md AGENT_DECISIONS.md   # операционный контракт агента
├── requirements.txt requirements-test.txt
├── alembic.ini  pytest.ini  .env.example  .github/
```

## Старт новой сессии (для агента)

1. Прочитать [AGENTS.md](AGENTS.md).
2. Затем [docs/AGENT_CONTEXT.md](docs/AGENT_CONTEXT.md) — снимок состояния и индекс.
3. Открывать отдельные доки только когда AGENT_CONTEXT недостаточно (порядок авторитета — в AGENTS.md).

## Запуск приложения

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                 # при необходимости задать DATABASE_URL (по умолчанию SQLite)
alembic upgrade head                 # применить миграции (создать таблицы)
uvicorn app.main:app --port 8000     # запуск; Swagger на http://localhost:8000/docs
```

БД: по умолчанию SQLite (`sqlite:///./app.db`); для PostgreSQL задать
`DATABASE_URL=postgresql+psycopg://user:pass@host:5432/db`. Примеры запросов/ответов —
[docs/API_EXAMPLES.md](docs/API_EXAMPLES.md); полная процедура — [docs/OPERATIONS/RUNBOOK.md](docs/OPERATIONS/RUNBOOK.md).

## Как запускать тесты

```bash
pip install -r requirements-test.txt
cp .env.example .env                 # API_BASE_URL=http://localhost:8000 (см. .env.example)
pytest --collect-only                # сборка контура (гейт)
API_BASE_URL=http://localhost:8000 pytest -q   # полный прогон против поднятого сервиса → 55 passed
```

Подробно (переменные окружения, маркеры, матрица покрытия) — [tests/README.md](tests/README.md)
и [docs/QA/TEST_PLAN.md](docs/QA/TEST_PLAN.md).

## Документы

- Принятые решения и улучшения — [docs/PRODUCT/TECH_DECISIONS.md](docs/PRODUCT/TECH_DECISIONS.md).
- Ответы на доп. вопросы (§43–52) — [docs/PRODUCT/ADDITIONAL_QUESTIONS.md](docs/PRODUCT/ADDITIONAL_QUESTIONS.md).
- Открытые вопросы и допущения — [docs/PRODUCT/REQUIREMENTS.md](docs/PRODUCT/REQUIREMENTS.md).
- Журнал реализации — [docs/PROCESS/IMPLEMENTATION_LEDGER.md](docs/PROCESS/IMPLEMENTATION_LEDGER.md).

## Статус

Все три модуля реализованы; контур тестов green (55/55). Работа на ветке `feat/next-stage-baseline`
(PR в `main`). Открытые вопросы Q-1..Q-8 реализованы по дефолтам — ждут подтверждения заказчика.

---

*Graph: [[AGENT_CONTEXT]] · [[REQUIREMENTS]] · [[ROADMAP]] · [[TEST_PLAN]]*
