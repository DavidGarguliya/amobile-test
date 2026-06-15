# RUNBOOK

Операционные процедуры: как запускать, проверять и откатывать. На этапе bootstrap продукт ещё не
реализован — раздел «Сервис» описывает целевые команды (стек по [[ADR INDEX]] ADR-002), раздел
«Тест-контур» актуален уже сейчас.

## Тест-контур (актуально сейчас)

Требования: Python 3.11+, pip.

```bash
# 1) виртуальное окружение
python3 -m venv .venv && source .venv/bin/activate

# 2) зависимости тест-контура
pip install -r requirements-test.txt

# 3) конфигурация окружения (без секретов в репозитории)
cp .env.example .env   # отредактировать API_BASE_URL и при необходимости admin-креды

# 4) сборка контура (гейт для типа B — должен проходить всегда)
pytest --collect-only

# 5) полный прогон (red, пока нет реализации/запущенного API — это ожидаемо)
pytest -q

# по маркерам
pytest -m employees
pytest -m "integration and negative"
```

Переменные окружения: `API_BASE_URL` (default `http://localhost:8000`), `HTTP_TIMEOUT`,
`ADMIN_AUTH_HEADER`, `ADMIN_AUTH_TOKEN`, `EXPECT_CREATED_CODE`, `RATE_LIMIT_PROBE_COUNT`.
Полное описание — `tests/README.md` и `.env.example`.

## Сервис (целевые команды — после реализации, ADR-002)

```bash
# зависимости приложения
pip install -r requirements.txt

# миграции (Alembic)
alembic upgrade head

# запуск (dev) — на старте сидируется admin из ADMIN_EMAIL/ADMIN_PASSWORD
uvicorn app.main:app --reload --port 8000

# OpenAPI/Swagger
open http://localhost:8000/docs

# фоновый воркер обработки (опционально, требует Redis + arq)
arq app.worker.WorkerSettings
```

БД: PostgreSQL через `DATABASE_URL`; для упрощённого запуска допустим SQLite (NFR-1).

### Аутентификация (ADR-009)

```bash
# получить JWT (admin сидируется на старте)
curl -s -X POST http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@example.com","password":"admin12345"}'
# далее: Authorization: Bearer <access_token> на /api/admin/* и мутациях
```

Секреты `JWT_SECRET`, `API_KEY_PEPPER`, `ADMIN_PASSWORD` обязательно переопределить в проде (env).
Опциональные бэкенды: `REDIS_URL` (rate limit/очередь), `SENTRY_DSN` (ошибки), `LOG_JSON=true`
(структурные логи). Зависимости — `requirements-optional.txt`.

## Проверка здоровья
- `GET /docs` (Swagger) доступен → приложение поднято.
- `pytest -m smoke` против поднятого сервиса → базовые контракты живы.

## Откат
- Код: `git revert <sha>` (без перезаписи истории, см. [[BRANCHING_AND_RELEASE]]).
- Миграции: `alembic downgrade -1`.
- Конфиг: восстановить `.env` из `.env.example` / секрет-хранилища.

## Логирование/диагностика
Основные действия логируются (NFR-6/INV-O1). На проде ошибки — в структурированный логгер/Sentry
(бриф §50) — вне scope bootstrap.

---

*Graph: [[AGENT_CONTEXT]] · [[FINAL_SYSTEM_SPEC]] · [[BRANCHING_AND_RELEASE]] · [[TEST_PLAN]]*
