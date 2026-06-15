---
name: reference-how-to-run-tests
description: Как запускать контур API-тестов и где конфиг окружения
metadata:
  type: reference
---

Стек: Python + pytest + httpx (POM). Конфиг — только из env, без хардкода секретов.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-test.txt
cp .env.example .env          # API_BASE_URL и при необходимости admin-креды
pytest --collect-only          # сборка контура (гейт; должна проходить)
pytest -q                      # полный прогон (red до реализации — норма для типа B)
```

- Конфиг окружения: `tests/api/config/settings.py` (читает env), шаблон — `.env.example`.
- Ключевые переменные: `API_BASE_URL`, `HTTP_TIMEOUT`, `ADMIN_AUTH_HEADER`, `ADMIN_AUTH_TOKEN`,
  `EXPECT_CREATED_CODE`, `RATE_LIMIT_PROBE_COUNT`.
- Маркеры: `employees`, `tickets`, `integration`, `audit`, `positive`, `negative`, `contract`,
  `auth`, `boundary`, `smoke`.
- Матрица покрытия и стратегия: `docs/QA/TEST_PLAN.md`; детали запуска: `tests/README.md`.

См. [[project-scope-and-status]].
