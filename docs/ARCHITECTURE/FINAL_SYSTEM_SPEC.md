# FINAL_SYSTEM_SPEC

Целевая спецификация системы, выведенная из [[REQUIREMENTS]]. Описывает границы, слои, владение
состоянием, потоки данных, модель данных и контракты API. Это **проектная цель**, а не отчёт о
реализации (тип задания — B, см. [[REQUIREMENTS]]). Приоритет ниже [[INVARIANTS]], выше PRODUCT-доков.

## 1. Границы системы

Монолитный backend-сервис, предоставляющий REST API из трёх модулей плюс admin-поверхность.
Внешние акторы:

- **Admin/оператор** — управляет сотрудниками, заявками, API-клиентами, обрабатывает интеграционные запросы.
- **Внешняя система** (например, 1С) — шлёт интеграционные запросы по `X-API-Key`.
- **БД** — единственный источник правды о состоянии (PostgreSQL; SQLite для dev — NFR-1).

Вне границ: внешние очереди, кэш, фронтенд. Помечены как будущие улучшения (см. §8).

## 2. Слои (целевая структура продукта — FastAPI + SQLAlchemy)

```
app/
  api/            # routers: тонкие HTTP-контроллеры, валидация ввода, маппинг в сервисы
  services/       # бизнес-логика, инварианты, оркестрация
  repositories/   # доступ к данным (SQLAlchemy), без бизнес-логики
  schemas/        # pydantic: request/response DTO, валидация
  models/         # ORM-модели (таблицы)
  core/           # конфиг, единый обработчик ошибок, логирование, безопасность (хеш ключа, rate limit)
  db/             # сессия, инициализация
alembic/          # миграции (NFR-9)
```

Поток данных: `router → service → repository → DB` и обратно `repository → service → schema → HTTP`.
Контроллеры не содержат бизнес-правил; правила живут в services и защищают [[INVARIANTS]].

## 3. Владение состоянием

- Единственный источник правды — реляционная БД. Скрытых хранилищ нет (INV-D*, INV-X*).
- Идентификаторы — целочисленный автоинкремент (`[ASSUMPTION] Q-1`).
- Время (created_at/updated_at/resolved_at/processed_at) проставляется сервером (INV-D1).

## 4. Модель данных

### employees
`id PK`, `full_name`, `position`, `department`, `phone`, `email UNIQUE`, `is_active BOOL=true`,
`created_at`, `updated_at`. Индексы: `email UNIQUE`, `department`, `is_active`, поисковый по
full_name/email/position (FR-E6).

### tickets
`id PK`, `employee_id FK→employees`, `title`, `description`, `priority ENUM`, `status ENUM=new`,
`assigned_to FK→employees NULL`, `created_at`, `updated_at`, `resolved_at NULL`. Индексы:
`status`, `priority`, `employee_id`, `assigned_to`.

### api_clients
`id PK`, `name`, `api_key_hash`, `is_active BOOL=true`, `requests_limit_per_minute INT`,
`created_at`. Plaintext-ключ не хранится (INV-P8). Индекс по `api_key_hash` для поиска при auth.

### integration_requests
`id PK`, `client_id FK→api_clients`, `request_type`, `payload JSON`, `status ENUM` (accepted/
rejected/processed/failed), `error_message NULL`, `created_at`, `processed_at NULL`. Индексы:
`client_id`, `status`, `request_type`, `created_at`.

### audit_logs
`id PK`, `client_id FK→api_clients NULL`, `action`, `ip_address`, `user_agent`, `success BOOL`,
`details JSON`, `created_at`. Индексы: `client_id`, `success`, `action`, `created_at`.

## 5. Контракты API

Полный перечень — таблица эндпоинтов в [[REQUIREMENTS]] (EP-01..EP-17). Ключевые контракты:

- **Создание сотрудника (EP-01):** вход — full_name, position, department, phone, email; выход —
  полная сущность employee. Ошибки: 422 (валидация), 409 (дубликат email).
- **Список (EP-02, EP-07, EP-15, EP-17):** query-параметры фильтров + `page`,`limit`; ответ —
  объект `{ items: [...], total, page, limit }` (`[ASSUMPTION]` форма пагинации; см. Q-5/TEST_PLAN).
- **Назначение заявки (EP-09):** вход `{assigned_to}`; побочный эффект — status→in_progress (INV-P6).
- **Смена статуса (EP-10):** вход `{status}`; нарушение графа → 409 `INVALID_STATUS_TRANSITION` (INV-P5).
- **Статистика (EP-11):** ответ `{total,new,in_progress,resolved,rejected,critical_opened}`.
- **Создание клиента (EP-12):** ответ `{client_id, api_key}` — единственный показ ключа (INV-P8).
- **Интеграционный вход (EP-14):** заголовок `X-API-Key`; матрица кодов: нет ключа/неверный→401,
  деактивирован→403, превышен лимит→429, пустой request_type→422; успех→accepted+сохранение (INV-P9).
- **Обработка (EP-16):** employee_sync ⇒ create/update employee (match external_id→email, INV-P12);
  успех→processed; ошибка→failed+error_message; повторная обработка processed→409 `ALREADY_PROCESSED` (INV-P11).

### Единый конверт ошибки (INV-X1, INV-X2)
```json
{ "error": true, "code": "VALIDATION_ERROR", "message": "human-readable", "details": { "field": "email" } }
```

## 6. Безопасность

- API-ключ: генерируется как непрозрачный токен с префиксом, в БД — только хеш (ADR-004, INV-P8).
- Авторизация интеграции: `X-API-Key` → поиск по хешу → проверка is_active и rate limit (INV-P9).
- Rate limit: per-client, окно «в минуту» (`[ASSUMPTION] Q-3`).
- Admin-авторизация: вне scope брифа (`[OPEN QUESTION] Q-4`); в тестах конфигурируема.
- Аудит фиксирует каждую попытку, в т.ч. неуспешную (INV-P10).

## 7. Внешние интеграции

employee_sync — единственный известный `request_type`. Обработка создаёт/обновляет сотрудника в
модуле 1 — связка модуля 3 с модулем 1 (INV-P12). Прочие типы запросов: сохраняются, обработка —
расширяемая точка.

## 8. Будущие улучшения (вне scope bootstrap)

Очередь обработки (§брифа 48), Redis для rate limit/кэша (§49), роли пользователей (§46), индексы
(§47), масштабирование (§51) — фиксируются как направления, не реализуются. См. [[ROADMAP]].

---

*Graph: [[AGENT_CONTEXT]] · [[INVARIANTS]] · [[REQUIREMENTS]] · [[SYSTEM_OVERVIEW]] · [[TEST_PLAN]]*
