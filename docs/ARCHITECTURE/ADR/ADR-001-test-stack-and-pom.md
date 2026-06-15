# ADR-001: Тест-стек и архитектура контура по POM

## Status
Accepted

## Context
Главный deliverable bootstrap-сессии — исполняемый контур API-тестов, покрывающий все требования
[[REQUIREMENTS]] (FR/NFR, EP-01..EP-17). Нужно выбрать стек и архитектуру так, чтобы тесты были
читаемыми, детерминированными (INV-O2), не дёргали HTTP напрямую (INV-X4) и не содержали хардкод-
секретов (INV-X5). Бриф допускает любой стек; заказчик подтвердил для тестов **Python + pytest +
httpx**, а для продукта — Python/FastAPI (см. ADR-002).

## Decision
Использовать **Python 3 + pytest + httpx** с архитектурой **Page/Service Object Model для API**:

- `tests/api/clients/base_client.py` — `BaseApiClient`: транспорт (httpx.Client), baseURL, общие
  заголовки, авторизация, логирование запрос/ответ, единый разбор ответа в `ApiResponse`.
- `tests/api/clients/<resource>_client.py` — по объекту на ресурс; методы = операции API
  (create/get/list/update/...), принимают типобезопасные модели, возвращают типизированный ответ.
  Бизнес-ассертов внутри клиентов нет.
- `tests/api/models/` — pydantic-DTO запросов; `tests/api/schemas/` — pydantic-схемы ответов для
  контрактных проверок.
- `tests/api/fixtures/` — фабрики уникальных данных, setup/teardown (conftest.py).
- `tests/api/config/` — конфиг из env (baseURL, креды) — без хардкода.
- `tests/api/specs/` — тесты, сгруппированные по ресурсам; структура Arrange-Act-Assert; в имени
  и/или маркере — ссылка на FR/EP.

Спеки взаимодействуют с API только через client-объекты. Ассерты — только в спеках.

## Consequences
### Positive
- Совпадает со стеком продукта (Python) → единая экосистема, низкий порог входа для ревьюера.
- httpx + pydantic дают строгие контрактные проверки тел ответов, не только статус-кодов.
- POM локализует изменения API в одном слое клиентов.
### Negative
- Часть тестов будет `red` до реализации продукта (тип B) — требует явной коммуникации статуса.
- pytest-параметризация требует дисциплины, чтобы не плодить скрытое состояние.

## Alternatives considered
### TypeScript + Playwright Test (дефолт мета-промпта)
Отклонено: продукт на Python; единый язык тестов и продукта упрощает поддержку и ревью, хотя
существующий каркас упоминал npm-команды (они переопределены под pytest).
### Java + RestAssured + TestNG
Отклонено: избыточно тяжёлый для не-Java продукта.

---

*Graph: [[AGENT_CONTEXT]] · [[INVARIANTS]] · [[TEST_PLAN]] · [[FINAL_SYSTEM_SPEC]]*
