# API test suite (POM, pytest + httpx)

Исполняемая спецификация требований тестового задания. Архитектура — Page/Service Object Model
для API (см. [ADR-001](../docs/ARCHITECTURE/ADR/ADR-001-test-stack-and-pom.md)). Тип — **B**:
часть тестов `red` до реализации продукта; контур обязан коллектиться.

## Запуск

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r ../requirements-test.txt      # из корня: pip install -r requirements-test.txt
cp ../.env.example ../.env                    # из корня: cp .env.example .env
pytest --collect-only                         # сборка контура (гейт; всегда должен проходить)
pytest -q                                     # полный прогон против API_BASE_URL
```

Запуск по маркерам:

```bash
pytest -m employees
pytest -m "tickets and negative"
pytest -m "integration and auth"
pytest -m contract
```

## Переменные окружения

| Переменная | Назначение | Default |
|------------|------------|---------|
| `API_BASE_URL` | базовый URL тестируемого API (Q-6) | `http://localhost:8000` |
| `HTTP_TIMEOUT` | таймаут httpx-клиента, сек | `10` |
| `API_KEY_HEADER` | имя заголовка ключа интеграции (§4.5, Q-2) | `X-API-Key` |
| `ADMIN_AUTH_HEADER` | заголовок admin-авторизации (Q-4); пусто → admin открыт | пусто |
| `ADMIN_AUTH_TOKEN` | значение admin-токена | пусто |
| `EXPECT_CREATED_CODE` | ожидаемый код успешного create (Q-5) | `201` |
| `RATE_LIMIT_PROBE_COUNT` | сколько запросов сверх лимита слать при проверке 429 | `0` (вывести) |
| `ADMIN_EMAIL` | логин для получения JWT (должен совпадать с сидируемым admin) | `admin@example.com` |
| `ADMIN_PASSWORD` | пароль admin для логина | `admin12345` |
| `LOG_LEVEL` | уровень логирования контура | `INFO` |

> Контур аутентифицируется как admin (JWT, ADR-009): сессионная фикстура логинится и проставляет
> `Authorization: Bearer` на общий клиент. Интеграционный вход остаётся на `X-API-Key`.

Секреты — только из окружения, без хардкода (INV-X5). `.env` git-ignored; шаблон — `.env.example`.

## Структура

```
tests/api/
  config/    settings.py     — конфиг из env
  clients/   base_client.py  — BaseApiClient (транспорт), <resource>_client.py — service-объекты
  models/    request DTO (pydantic)
  schemas/   response-схемы для контрактных проверок (pydantic) + ErrorEnvelope
  fixtures/  factories.py    — фабрики уникальных данных
  utils/     asserts.py (кастомные ассерты), markers.py (трассируемость @req)
  specs/     test_*.py       — тесты (Arrange-Act-Assert), сгруппированы по ресурсам
  conftest.py                — фикстуры POM-клиентов и предусловий
```

Спеки ходят в API только через client-объекты (INV-X4); ассерты — только в спеках.

## Покрытие и трассируемость

Матрица требование → тест-кейс — в [docs/QA/TEST_PLAN.md](../docs/QA/TEST_PLAN.md) §5. Каждый тест
помечен `@req("FR-...", "INV-...")` и категориями (`positive`/`negative`/`contract`/`auth`/`boundary`).

## Состояние прогона

Без запущенной реализации полный прогон ожидаемо **red** (нет сервиса по `API_BASE_URL`). Это
корректно для типа B. `pytest --collect-only` должен проходить всегда — это гейт сборки контура.
