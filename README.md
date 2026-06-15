# amobile-test — Backend test assignment (three API modules)

Backend-сервис из трёх REST API-модулей: справочник сотрудников, внутренние IT-заявки и
защищённое интеграционное API для внешних систем. Все три модуля **реализованы** (FastAPI +
SQLAlchemy + Alembic) с production-обвязкой: JWT-аутентификация + RBAC, единый конверт ошибок,
rate limiting, очередь обработки и наблюдаемость. Исполняемый контур API-тестов (POM, pytest +
httpx) — **green, 61/61**, с полным **Allure-отчётом**.

> Источник требований — [docs/PRODUCT/SOURCE_BRIEF.md](docs/PRODUCT/SOURCE_BRIEF.md) (дословная копия).

## Стек

- **Продукт:** Python 3.11+, FastAPI + SQLAlchemy 2 + Alembic, PostgreSQL (SQLite для dev) — см.
  [ADR-002](docs/ARCHITECTURE/ADR/ADR-002-backend-stack.md).
- **Безопасность:** JWT (HS256) + RBAC (ADR-009), API-ключи HMAC+pepper с ротацией (ADR-004).
- **Production-обвязка (ADR-010):** rate limit (InMemory/Redis), очередь (Inline/Arq + DLQ),
  request-id/JSON-логи/Sentry — за интерфейсами с in-process фолбэком; зависимости опциональны
  (`requirements-optional.txt`).
- **Документация API:** Swagger `/docs`, `docs/openapi.json`, Postman (`postman/`).
- **Тесты:** pytest, httpx, pydantic, POM (ADR-001) + Allure-отчёт (`allure-pytest`).

## Структура репозитория

```
.
├── app/                      # приложение FastAPI
│   ├── api/                  # роутеры (EP-01..EP-17, auth) + deps (RBAC)
│   ├── services/             # бизнес-логика и инварианты (вкл. auth, processing)
│   ├── repositories/         # доступ к данным (SQLAlchemy)
│   ├── models/               # ORM: employees, tickets, api_clients, api_keys, users, ...
│   ├── schemas/              # pydantic request/response
│   ├── core/                 # config, errors, security (ключи), auth (JWT), rate_limit, queue, logging, observability
│   ├── db/                   # base + session
│   ├── main.py               # app factory, middleware, /health, OpenAPI, seed admin
│   └── worker.py             # arq-воркер обработки (опционально)
├── alembic/                  # миграции + env.py
├── postman/                  # Postman collection + environment
├── tests/                    # POM-контур API-тестов + Allure (см. tests/README.md)
│   └── api/{clients,models,schemas,fixtures,config,utils,specs}
├── docs/
│   ├── AGENT_CONTEXT.md      # хаб графа: всегда-актуальный снимок проекта
│   ├── API_EXAMPLES.md       # примеры запросов/ответов; openapi.json — экспорт схемы
│   ├── ARCHITECTURE/         # INVARIANTS, FINAL_SYSTEM_SPEC, SYSTEM_OVERVIEW, ADR-001..010
│   ├── PRODUCT/              # SOURCE_BRIEF, REQUIREMENTS, AC, TECH_DECISIONS, ADDITIONAL_QUESTIONS
│   ├── PROCESS/              # STATE, CHRONICLE, ROADMAP, IMPLEMENTATION_LEDGER, BRANCHING, PR_GEN
│   ├── OPERATIONS/           # RUNBOOK
│   └── QA/                   # TEST_PLAN (+ матрица трассируемости)
├── memory/                   # семантическая память проекта (+ MEMORY.md индекс)
├── AGENTS.md ENGINEER_MODE.md AGENT_DECISIONS.md   # операционный контракт агента
├── requirements.txt  requirements-test.txt  requirements-optional.txt
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

На старте сидируется admin (`ADMIN_EMAIL`/`ADMIN_PASSWORD`, по умолчанию
`admin@example.com` / `admin12345`). Получить JWT: `POST /api/auth/login` → `Authorization: Bearer <token>`
на `/api/admin/*` и мутациях. Секреты `JWT_SECRET`/`API_KEY_PEPPER` переопределить в проде.

БД: по умолчанию SQLite (`sqlite:///./app.db`); для PostgreSQL задать
`DATABASE_URL=postgresql+psycopg://user:pass@host:5432/db`. Примеры запросов/ответов —
[docs/API_EXAMPLES.md](docs/API_EXAMPLES.md); полная процедура — [docs/OPERATIONS/RUNBOOK.md](docs/OPERATIONS/RUNBOOK.md).

## API-документация и Postman (локально, домен НЕ нужен)

Сервис работает на твоём компьютере — никакого домена/хостинга не требуется. После
`uvicorn app.main:app --port 8000`:

- **Swagger UI:** <http://localhost:8000/docs> · **ReDoc:** <http://localhost:8000/redoc> ·
  **OpenAPI JSON:** <http://localhost:8000/openapi.json> (плюс закоммиченная копия `docs/openapi.json`).
- **Базовый URL для Postman/тестов:** `http://localhost:8000` (для другого ПК — тот же localhost,
  пока сервис запущен на нём).

**Postman ([postman/amobile-test.postman_collection.json](postman/amobile-test.postman_collection.json)):**
коллекция самодостаточна — `base_url` уже задан, авторизация настроена.

1. Импортировать коллекцию (и опц. окружение `postman/local.postman_environment.json`).
2. Выполнить **Auth → Login** — JWT сохранится в переменную `{{token}}` автоматически, и все
   защищённые запросы пойдут с `Authorization: Bearer {{token}}`.
3. **Integration (admin) → Create API client** — plaintext-ключ сохранится в `{{api_key}}`
   (показывается один раз); далее **Integration (external) → Submit** использует `X-API-Key {{api_key}}`.

Если в Postman `{{base_url}}` «пустой» — открой коллекцию → вкладка **Variables** и убедись, что в
колонке **Current value** стоит `http://localhost:8000` (иногда импортируется только Initial value).

## Как запускать тесты

```bash
pip install -r requirements-test.txt
cp .env.example .env                 # API_BASE_URL=http://localhost:8000 (см. .env.example)
pytest --collect-only                # сборка контура (гейт)
API_BASE_URL=http://localhost:8000 pytest -q --alluredir=allure-results   # → 61 passed + результаты Allure
allure serve allure-results          # открыть отчёт (Allure CLI: brew install allure)
```

Каждый тест размечен Allure (epic/feature/story/title/severity + tag по ID требования); шаги и
вложения request/response добавляются автоматически на уровне POM-клиента. Подробно (переменные
окружения, маркеры, матрица покрытия, Allure) — [tests/README.md](tests/README.md) и
[docs/QA/TEST_PLAN.md](docs/QA/TEST_PLAN.md).

## Документы

- Принятые решения и улучшения — [docs/PRODUCT/TECH_DECISIONS.md](docs/PRODUCT/TECH_DECISIONS.md).
- Ответы на доп. вопросы (§43–52) — [docs/PRODUCT/ADDITIONAL_QUESTIONS.md](docs/PRODUCT/ADDITIONAL_QUESTIONS.md).
- Открытые вопросы и допущения — [docs/PRODUCT/REQUIREMENTS.md](docs/PRODUCT/REQUIREMENTS.md).
- Журнал реализации — [docs/PROCESS/IMPLEMENTATION_LEDGER.md](docs/PROCESS/IMPLEMENTATION_LEDGER.md).

## Статус

Все три модуля + production-обвязка (JWT/RBAC, усиление ключей, rate limit, очередь, наблюдаемость)
реализованы и влиты в `main`; контур тестов **green (61/61)** с Allure-отчётом. Решения по
Q-1..Q-8 — **DECIDED** (подтверждены). Документы: [TECH_DECISIONS](docs/PRODUCT/TECH_DECISIONS.md),
[ADDITIONAL_QUESTIONS](docs/PRODUCT/ADDITIONAL_QUESTIONS.md), [IMPLEMENTATION_LEDGER](docs/PROCESS/IMPLEMENTATION_LEDGER.md).

> **Postman показывает `ECONNREFUSED 127.0.0.1:8000`?** Это значит, что сервис не запущен —
> сначала подними его: `uvicorn app.main:app --port 8000` (см. «Запуск приложения»), проверь
> `http://localhost:8000/health`, затем шли запросы из Postman. Сервис должен оставаться запущенным.

---

*Graph: [[AGENT_CONTEXT]] · [[REQUIREMENTS]] · [[ROADMAP]] · [[TEST_PLAN]]*
