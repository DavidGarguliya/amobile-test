# amobile-test — Backend test assignment (three API modules)

Backend-сервис из трёх REST API-модулей: справочник сотрудников, внутренние IT-заявки и
защищённое интеграционное API для внешних систем. Репозиторий находится в состоянии **bootstrap**:
собран пакет проектной документации и **исполняемый контур API-тестов** (POM, Python + pytest +
httpx). Код продукта ещё не написан — это TDD-спецификация (тип задания B).

> Источник требований — [docs/PRODUCT/SOURCE_BRIEF.md](docs/PRODUCT/SOURCE_BRIEF.md) (дословная копия).

## Стек

- **Тесты:** Python 3.11+, pytest, httpx, pydantic (см. [ADR-001](docs/ARCHITECTURE/ADR/ADR-001-test-stack-and-pom.md)).
- **Продукт (целевой):** FastAPI + SQLAlchemy + Alembic, PostgreSQL (SQLite для dev) — см.
  [ADR-002](docs/ARCHITECTURE/ADR/ADR-002-backend-stack.md). Реализация начнётся после апрува.

## Структура репозитория

```
.
├── AGENTS.md                 # операционный контракт агента (читать первым → docs/AGENT_CONTEXT.md)
├── ENGINEER_MODE.md          # правила инженерного рассуждения
├── AGENT_DECISIONS.md        # legacy-журнал решений (комплемент к docs/ARCHITECTURE)
├── README.md                 # этот файл
├── docs/
│   ├── AGENT_CONTEXT.md      # хаб графа: всегда-актуальный снимок проекта
│   ├── ARCHITECTURE/         # INVARIANTS, FINAL_SYSTEM_SPEC, SYSTEM_OVERVIEW, ADR/*
│   ├── PRODUCT/              # SOURCE_BRIEF, REQUIREMENTS, ACCEPTANCE_CRITERIA, BUSINESS_METRICS
│   ├── PROCESS/              # STATE, CHRONICLE, ROADMAP, BRANCHING_AND_RELEASE, PR_GENERATION
│   ├── OPERATIONS/           # RUNBOOK
│   └── QA/                   # TEST_PLAN (+ матрица трассируемости)
├── memory/                   # семантическая память проекта (+ MEMORY.md индекс)
├── tests/                    # POM-контур API-тестов (см. tests/README.md)
│   └── api/{clients,models,schemas,fixtures,config,utils,specs}
├── .github/                  # PR-шаблон + CI workflow
├── .env.example              # шаблон переменных окружения (без секретов)
├── pytest.ini
└── requirements-test.txt
```

## Старт новой сессии (для агента)

1. Прочитать [AGENTS.md](AGENTS.md).
2. Затем [docs/AGENT_CONTEXT.md](docs/AGENT_CONTEXT.md) — снимок состояния и индекс.
3. Открывать отдельные доки только когда AGENT_CONTEXT недостаточно (порядок авторитета — в AGENTS.md).

## Как запускать тесты

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-test.txt
cp .env.example .env            # задать API_BASE_URL и при необходимости admin-креды
pytest --collect-only           # сборка контура (гейт; должен проходить всегда)
pytest -q                       # полный прогон (red до реализации продукта — норма для типа B)
```

Подробно (переменные окружения, маркеры, матрица покрытия) — [tests/README.md](tests/README.md)
и [docs/QA/TEST_PLAN.md](docs/QA/TEST_PLAN.md).

## Статус и дальнейшие шаги

bootstrap завершён; ожидается апрув на старт основной разработки. Первый слайс — каркас
FastAPI-приложения (см. [docs/PROCESS/ROADMAP.md](docs/PROCESS/ROADMAP.md)). Открытые вопросы и
принятые допущения — [docs/PRODUCT/REQUIREMENTS.md](docs/PRODUCT/REQUIREMENTS.md).

---

*Graph: [[AGENT_CONTEXT]] · [[REQUIREMENTS]] · [[ROADMAP]] · [[TEST_PLAN]]*
