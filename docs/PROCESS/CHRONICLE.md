# CHRONICLE

Датированная хроника сессий. Новая запись — сверху списка. Index — внизу.

---

## 2026-06-15 — Bootstrap: документация + контур API-тестов

**Контекст.** Старт проекта по тестовому заданию «backend-разработчик» (три API-модуля).
Репозиторий содержал ранний каркас операционных правил (`AGENTS.md`, `AGENT_DECISIONS.md`,
`ENGINEER_MODE.md`), ссылавшийся на отсутствующее дерево `docs/`.

**Решения сессии.**
- Тип задания определён как **B** (строим продукт; тест-контур = TDD-spec).
- Стек подтверждён заказчиком: тесты — **Python + pytest + httpx**; продукт — **FastAPI +
  SQLAlchemy + Alembic + PostgreSQL**.
- Приняты ADR-001..ADR-008 (см. [[ADR INDEX]]).
- Зафиксированы открытые вопросы Q-1..Q-8 и безопасные `[ASSUMPTION]`-дефолты.

**Сделано.**
- PRODUCT: SOURCE_BRIEF (дословно), REQUIREMENTS (FR/NFR/EP), ACCEPTANCE_CRITERIA, BUSINESS_METRICS.
- ARCHITECTURE: INVARIANTS, FINAL_SYSTEM_SPEC, SYSTEM_OVERVIEW, ADR-000..008 + INDEX.
- PROCESS: STATE, CHRONICLE, ROADMAP, BRANCHING_AND_RELEASE, PR_GENERATION.
- OPERATIONS: RUNBOOK. QA: TEST_PLAN (+ матрица трассируемости).
- AGENT_CONTEXT (хаб), гармонизированы AGENTS.md / ENGINEER_MODE.md / AGENT_DECISIONS.md, README.
- Семантическая память `memory/` + MEMORY.md.
- Полный POM-контур тестов (clients/models/schemas/fixtures/config/utils/specs), tests/README,
  .env.example, pytest-конфиг, CI workflow, .gitignore.
- git init, атомарные коммиты, привязка remote, push.

**Затронутые инварианты.** Зафиксированы все INV-* (см. [[INVARIANTS]]) — это первичная фиксация,
не нарушение.

**Проверка.** `pytest --collect-only` — контур коллектится; полный прогон против API — **red**
(реализации нет, тип B). Это ожидаемо.

**Остаётся.** Апрув на старт разработки; затем Слайс 1 ([[ROADMAP]]).

---

## Index
- 2026-06-15 — Bootstrap: документация + контур API-тестов.

---

*Graph: [[AGENT_CONTEXT]] · [[STATE]] · [[ROADMAP]] · [[TEST_PLAN]]*
