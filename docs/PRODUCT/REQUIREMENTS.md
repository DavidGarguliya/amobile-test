# REQUIREMENTS

Трассируемые требования, выведенные из [[SOURCE_BRIEF]]. Каждый ID стабилен и используется
далее в инвариантах ([[INVARIANTS]]), спецификации ([[FINAL_SYSTEM_SPEC]]), ADR и тест-кейсах
([[TEST_PLAN]]). Источник истины — только бриф; домыслы помечены `[ASSUMPTION]` и собраны в конце.

## Task type

**Тип B — «построить продукт/сервис».** Готового работающего API для тестирования не
предоставлено: бриф требует *разработать* backend-сервис. Следовательно тест-контур — это
**TDD-спецификация**: часть тестов будет `red` до появления реализации. Это ожидаемо и корректно.
Контур обязан собираться/коллектиться и запускаться против `API_BASE_URL` из окружения.

---

## Функциональные требования

### Модуль 1 — Справочник сотрудников (Employees)

| ID | Требование | Источник |
|----|------------|----------|
| FR-E1 | Создание сотрудника `POST /api/employees` с полями full_name, position, department, phone, email | §2.3 |
| FR-E2 | Обязательные поля проверяются при создании/обновлении | §2.4.4 |
| FR-E3 | Email уникален среди сотрудников | §2.4.5 |
| FR-E4 | Список `GET /api/employees` с фильтрами department, is_active, search, page, limit | §2.3 |
| FR-E5 | Пагинация списка сотрудников | §2.4.6 |
| FR-E6 | Поиск (`search`) по ФИО (full_name), email и должности (position) | §2.4.7 |
| FR-E7 | Получение сотрудника по ID `GET /api/employees/{id}` | §2.3 |
| FR-E8 | Обновление сотрудника `PUT /api/employees/{id}`; меняется updated_at | §2.3 |
| FR-E9 | Деактивация `PATCH /api/employees/{id}/deactivate` → is_active=false; физическое удаление запрещено | §2.3 |
| FR-E10 | Данные хранятся в БД; поля created_at/updated_at заполняются | §2.4.9, §2.2 |

### Модуль 2 — IT-заявки (Tickets)

| ID | Требование | Источник |
|----|------------|----------|
| FR-T1 | Создание заявки `POST /api/tickets` (employee_id, title, description, priority) | §3.5 |
| FR-T2 | При создании заявка получает статус `new` | §3.5 |
| FR-T3 | priority ∈ {low, medium, high, critical} | §3.3 |
| FR-T4 | status ∈ {new, in_progress, resolved, rejected} | §3.4 |
| FR-T5 | Заявка связана с существующим сотрудником; нельзя создать от несуществующего | §3.7.10, §3.7.11 |
| FR-T6 | Список `GET /api/tickets` с фильтрами status, priority, employee_id, assigned_to, page, limit | §3.5 |
| FR-T7 | Получение заявки по ID `GET /api/tickets/{id}` | §3.5 |
| FR-T8 | Назначение исполнителя `PATCH /api/tickets/{id}/assign`; assigned_to должен существовать | §3.5, §3.7.12 |
| FR-T9 | После назначения исполнителя статус становится `in_progress` | §3.5 |
| FR-T10 | Изменение статуса `PATCH /api/tickets/{id}/status` по правилам перехода | §3.5, §3.6 |
| FR-T11 | Правила переходов: new→{in_progress,rejected}; in_progress→{resolved,rejected}; resolved/rejected — терминальны | §3.6 |
| FR-T12 | При переходе в `resolved` заполняется resolved_at | §3.6 |
| FR-T13 | Статистика `GET /api/tickets/stats`: total, new, in_progress, resolved, rejected, critical_opened | §3.5 |
| FR-T14 | Фильтрация и пагинация списка заявок | §3.7.14 |

### Модуль 3 — Интеграционное API (Integration / Admin)

| ID | Требование | Источник |
|----|------------|----------|
| FR-I1 | Создание API-клиента `POST /api/admin/clients` (name, requests_limit_per_minute) | §4.5 |
| FR-I2 | Ответ создания клиента возвращает api_key ровно один раз; в БД только хеш | §4.2, §4.5 |
| FR-I3 | Деактивация клиента `PATCH /api/admin/clients/{id}/deactivate` | §4.5 |
| FR-I4 | Отправка запроса `POST /api/integration/requests` с заголовком `X-API-Key` | §4.5 |
| FR-I5 | Нет ключа → 401 (UNAUTHORIZED) | §4.6.17 |
| FR-I6 | Неверный ключ → 401 (UNAUTHORIZED) | §4.6.18 |
| FR-I7 | Клиент деактивирован → 403 (FORBIDDEN) | §4.6.19 |
| FR-I8 | Превышен лимит запросов в минуту → 429 (RATE_LIMIT_EXCEEDED) | §4.6.20 |
| FR-I9 | Пустой request_type → 422 (VALIDATION_ERROR) | §4.6.21 |
| FR-I10 | Успешный запрос сохраняется в БД (status=accepted) | §4.6.22 |
| FR-I11 | Каждая попытка обращения пишется в аудит | §4.6.23 |
| FR-I12 | В аудит сохраняются ip_address и user_agent | §4.6.24 |
| FR-I13 | Список запросов `GET /api/admin/integration/requests` с фильтрами client_id, status, request_type, date_from, date_to, page, limit | §4.5 |
| FR-I14 | Обработка `POST /api/admin/integration/requests/{id}/process` | §4.5 |
| FR-I15 | request_type=employee_sync → create/update сотрудника; матч по external_id, иначе по email | §4.5 |
| FR-I16 | Ошибка обработки → status=failed, текст в error_message | §4.5 |
| FR-I17 | Запрещена повторная обработка запроса в статусе processed (идемпотентность) | §4.5 |
| FR-I18 | Аудит `GET /api/admin/audit` с фильтрами client_id, success, action, date_from, date_to, page, limit | §4.5 |
| FR-I19 | Статус интеграционного запроса ∈ {accepted, rejected, processed, failed} | §4.3 |

---

## Нефункциональные требования

| ID | Требование | Источник |
|----|------------|----------|
| NFR-1 | БД: PostgreSQL (SQLite допустим для упрощённого запуска); структура переносима на PostgreSQL | §5.1 |
| NFR-2 | Единый формат ошибок: `{error, code, message, details}` | §5.3 |
| NFR-3 | Набор кодов ошибок: VALIDATION_ERROR, NOT_FOUND, UNAUTHORIZED, FORBIDDEN, RATE_LIMIT_EXCEEDED, INVALID_STATUS_TRANSITION, ALREADY_PROCESSED, INTERNAL_ERROR | §5.3 |
| NFR-4 | Валидация входящих данных | §5.2.32 |
| NFR-5 | Единая (централизованная) обработка ошибок | §5.2.33 |
| NFR-6 | Логирование основных действий | §5.2.34 |
| NFR-7 | Безопасность: API-ключ хранится только хешем, показывается один раз; rate limit; авторизация по X-API-Key | §4.2, §4.5, §4.6 |
| NFR-8 | Документация API: Swagger/OpenAPI или Postman collection | §5.2.30, §5.2.31 |
| NFR-9 | README, описание стека, структурированный код, подключение к БД, миграции/SQL-скрипт | §5.2.25–29 |
| NFR-10 | Минимум несколько тестов на ключевую бизнес-логику | §5.2.35 |

---

## Перечень эндпоинтов (Endpoint IDs)

| EP | Метод | Путь | Авторизация | Ключевые коды |
|----|-------|------|-------------|---------------|
| EP-01 | POST | /api/employees | — (admin) | 201, 422, 409 |
| EP-02 | GET | /api/employees | — (admin) | 200 |
| EP-03 | GET | /api/employees/{id} | — (admin) | 200, 404 |
| EP-04 | PUT | /api/employees/{id} | — (admin) | 200, 404, 422, 409 |
| EP-05 | PATCH | /api/employees/{id}/deactivate | — (admin) | 200, 404 |
| EP-06 | POST | /api/tickets | — (admin) | 201, 422, 404 |
| EP-07 | GET | /api/tickets | — (admin) | 200 |
| EP-08 | GET | /api/tickets/{id} | — (admin) | 200, 404 |
| EP-09 | PATCH | /api/tickets/{id}/assign | — (admin) | 200, 404, 422 |
| EP-10 | PATCH | /api/tickets/{id}/status | — (admin) | 200, 404, 409 (INVALID_STATUS_TRANSITION) |
| EP-11 | GET | /api/tickets/stats | — (admin) | 200 |
| EP-12 | POST | /api/admin/clients | admin | 201 |
| EP-13 | PATCH | /api/admin/clients/{id}/deactivate | admin | 200, 404 |
| EP-14 | POST | /api/integration/requests | X-API-Key | 201/200, 401, 403, 429, 422 |
| EP-15 | GET | /api/admin/integration/requests | admin | 200 |
| EP-16 | POST | /api/admin/integration/requests/{id}/process | admin | 200, 404, 409 (ALREADY_PROCESSED) |
| EP-17 | GET | /api/admin/audit | admin | 200 |

> `[ASSUMPTION] A-AUTH`: способ авторизации admin-эндпоинтов (§4.5, §3.x) в брифе не описан.
> Для интеграционного входа явно задан `X-API-Key`. Admin-доступ помечен как OPEN QUESTION
> (см. ниже). Тесты используют конфигурируемый admin-механизм через env, по умолчанию — без
> заголовка (открытый admin), что отражено в [[TEST_PLAN]].

---

## ASSUMPTIONS / OPEN QUESTIONS

> **Status (production package, 2026-06-15):** реализованы best-practice варианты (ADR-009/010).
> Q-1 BIGINT id (сохранён); Q-2 ключ `company_live_<key_id>_<secret>`, HMAC+pepper, ротация
> (таблица `api_keys`); Q-4 JWT + RBAC (роли admin/operator/viewer); Q-5 201 + `Location`; Q-7
> `CONFLICT`/409; Q-8 таблица `external_identities`. Q-3/Q-6 — без изменений (rate limit за
> интерфейсом + Redis-бэкенд; base URL из env). Дефолты всё ещё под подтверждение заказчика.


- `[OPEN QUESTION] Q-1`: тип идентификаторов (`id`) — целочисленный автоинкремент (примеры в
  брифе используют `1`, `2`) против UUID. Принято `[ASSUMPTION]`: целочисленный, как в примерах.
- `[OPEN QUESTION] Q-2`: формат и префикс API-ключа (`company_live_...`) — генерация/энтропия не
  специфицированы. Принято: непрозрачный токен с префиксом, хеш в БД (алгоритм — решение ADR-004).
- `[OPEN QUESTION] Q-3`: окно rate limit — фиксированное «в минуту» или скользящее. Принято:
  фиксированное окно (sliding допустимо), деталь — решение реализации.
- `[OPEN QUESTION] Q-4`: авторизация admin-эндпоинтов (`/api/admin/*`, employees, tickets) —
  не описана. Принято: вне scope брифа; в тестах конфигурируема через env (`ADMIN_AUTH_*`).
- `[OPEN QUESTION] Q-5`: коды успеха (201 vs 200) для create-операций не заданы. Принято:
  201 для create, 200 для прочих; тесты допускают оба через настраиваемое ожидание.
- `[OPEN QUESTION] Q-6`: `API_BASE_URL` не задан в брифе. Принято: берётся из env, по умолчанию
  `http://localhost:8000`.
- `[OPEN QUESTION] Q-7`: пол behaviour при дубликате email — код 409 (CONFLICT) или 422. Бриф
  требует лишь «уникальность» и «понятный формат». Принято: 409+`VALIDATION_ERROR`/`CONFLICT`;
  тест проверяет «не 2xx» + конверт ошибки.

---

*Graph: [[AGENT_CONTEXT]] · [[INVARIANTS]] · [[FINAL_SYSTEM_SPEC]] · [[ACCEPTANCE_CRITERIA]] · [[TEST_PLAN]]*
