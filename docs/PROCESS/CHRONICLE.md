# CHRONICLE

Датированная хроника сессий. Новая запись — сверху списка. Index — внизу.

---

## 2026-06-16 — Аудит проекта + фиксы

**Сделано.** Независимый аудит (контур + httpx-пробы + инспекция секретов в БД) → критических багов
нет. Исправлено: §45 (единая транзакция + FOR UPDATE, репозитории получили `commit`-флаг);
аудит-422 (пустой request_type валидируется после auth → пишется в аудит); WARNING при дефолтных
секретах; убран неиспользуемый импорт. Добавлен тест аудита-422. Контур **62 passed**.

**Осознанно оставлено:** PUT как частичное обновление; уникальность email для деактивированных;
кеп лимита ≤100; in-memory rate limit без Redis. Детали — [[IMPLEMENTATION_LEDGER]].

---

## 2026-06-16 — Allure-отчётность + auth-aware Postman

**Сделано.** Подключён Allure (epic/feature/story/title/severity + tag по ID; шаги/вложения из
`BaseApiClient`). 6 spec-файлов размечены параллельными агентами + русские докстринги/комментарии,
видимые ассерты в `allure.step`. CI публикует отчёт. Postman переведён на auth-aware (login→token,
create-client→api_key, base_url по умолчанию) + окружение. README/RUNBOOK/tests-README обновлены.

**Проверка.** `pytest --alluredir` → 61 passed; `allure generate` → HTML. Ветка `feat/allure-reporting`.

**Заметка.** Postman `ECONNREFUSED 127.0.0.1:8000` = сервис не запущен (домен не нужен; всё локально).

---

## 2026-06-16 — Подтверждение дефолтов Q-1..Q-8 и мерж PR #1

**Контекст.** Заказчик подтвердил решения по Q-1..Q-8 (теперь DECIDED, не открытые вопросы) и
дал команду смержить.

**Сделано.** Статус Q-1..Q-8 переведён в DECIDED в [[REQUIREMENTS]], [[AGENT_CONTEXT]] и памяти
([[assumptions-to-confirm]]). PR #1 (`feat/next-stage-baseline` → `main`) **squash-merged**; `main`
теперь содержит весь deliverable (3 модуля + production hardening, контур green 61/61).

**Остаётся.** Follow-up: интеграционная проверка Redis/Arq/Sentry; blacklist токенов; per-resource scopes.

---

## 2026-06-15 — Production hardening (best-practice пакет)

**Контекст.** По запросу заказчика реализованы best-practice варианты по Q-1..Q-8 + §45/48/49/50.

**Сделано.** JWT + RBAC (ADR-009): users/scrypt/JWT, гейтинг роутеров. Ключи: `api_keys`,
`company_live_<key_id>_<secret>`, HMAC+pepper, ротация. CONFLICT/409 (Q-7). Атомарный захват в
обработке (§45). Location + X-RateLimit-* заголовки. RateLimiter/TaskQueue/observability за
абстракциями с in-process фолбэком (ADR-010). Таблица `external_identities` (Q-8). Воркер `app/worker.py`.

**Проверка.** Миграция `d13bf3046d8c` (8 таблиц). Контур: auth-фикстуры, `AuthClient`, `test_auth`,
обновления. **61 passed ×2**; `--collect-only` 61.

**Остаётся.** Подтверждение дефолтов; интеграционная проверка Redis/Arq/Sentry; blacklist токенов.

---

## 2026-06-15 — Реализация: три модуля на FastAPI, контур green

**Контекст.** После апрува («погнали») начата основная разработка по [[ROADMAP]] (Слайсы 1–4).

**Сделано.** Реализован backend FastAPI + SQLAlchemy 2 + Alembic: `app/{core,db,models,schemas,
repositories,services,api,main}`. Все эндпоинты EP-01..EP-17. Безопасность ADR-004 (хеш ключа,
одноразовый показ, rate limit), машина статусов ADR-005, идемпотентная обработка employee_sync
ADR-007. Добавлена колонка `employees.external_id` (Q-8). Alembic initial revision `5ed0618a97bd`.

**Затронутые инварианты.** Реализованы INV-P1..P12, INV-X1..X3, INV-O1 (см. [[INVARIANTS]],
[[IMPLEMENTATION_LEDGER]]).

**Проверка.** uvicorn (SQLite) + весь контур: **55 passed ×2** (детерминизм). Миграция применяется
на чистую БД. `pytest --collect-only` проходит.

**Решения (дефолты по OPEN QUESTIONS).** Q-1 int id, Q-4 admin открыт, Q-5 create→201, Q-7
дубликат email→422 VALIDATION_ERROR, Q-8 external_id добавлен. Под подтверждение заказчика.

**Остаётся.** Слайс 5 (README-примеры, Postman опц., §43–52); ревью/мерж ветки в `main`.

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
- 2026-06-16 — Аудит проекта + фиксы (§45 atomic, аудит-422, secret-warning); контур 62/62.
- 2026-06-16 — Allure-отчётность + auth-aware Postman.
- 2026-06-16 — Подтверждение дефолтов Q-1..Q-8 (DECIDED) и squash-merge PR #1 в main.
- 2026-06-15 — Production hardening: JWT/RBAC, key HMAC+rotation, CONFLICT, race-fix, queue/observability (61/61).
- 2026-06-15 — Финализация (Слайс 5): API-доки, Postman, OpenAPI, ответы §43–52 ([[IMPLEMENTATION_LEDGER]]).
- 2026-06-15 — Реализация: три модуля на FastAPI, контур green (55/55).
- 2026-06-15 — Bootstrap: документация + контур API-тестов.

---

*Graph: [[AGENT_CONTEXT]] · [[STATE]] · [[ROADMAP]] · [[TEST_PLAN]]*
