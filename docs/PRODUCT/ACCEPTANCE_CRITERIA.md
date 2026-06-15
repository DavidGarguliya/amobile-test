# ACCEPTANCE_CRITERIA

Проверяемые критерии приёмки в форме Given/When/Then. Каждый критерий ссылается на FR/NFR из
[[REQUIREMENTS]] и проверяется тест-кейсами из [[TEST_PLAN]]. Критерии — Definition of Done
для соответствующего слайса из [[ROADMAP]].

## Module 1 — Employees

- **AC-E1 (FR-E1, FR-E10):** *Given* валидное тело сотрудника, *When* `POST /api/employees`,
  *Then* код 201, тело содержит id, is_active=true, created_at, updated_at, эхо переданных полей.
- **AC-E2 (FR-E2, NFR-2):** *Given* тело без обязательного поля (например, email), *When* создание,
  *Then* код 422, конверт ошибки с `code=VALIDATION_ERROR` и `details.field`.
- **AC-E3 (FR-E3):** *Given* существует сотрудник с email X, *When* создаём второго с email X,
  *Then* ответ не 2xx (409/422), конверт ошибки указывает на конфликт уникальности.
- **AC-E4 (FR-E4, FR-E5):** *Given* набор сотрудников, *When* `GET /api/employees?page=1&limit=N`,
  *Then* код 200, не более N элементов, присутствуют метаданные пагинации (total/page/limit).
- **AC-E5 (FR-E4):** *Given* сотрудники в разных отделах, *When* фильтр `department=IT&is_active=true`,
  *Then* в выдаче только активные сотрудники отдела IT.
- **AC-E6 (FR-E6):** *Given* сотрудник с уникальной подстрокой в ФИО/email/должности, *When* `search`,
  *Then* он присутствует в выдаче; нерелевантные — отсутствуют.
- **AC-E7 (FR-E7):** *Given* существующий id, *When* `GET /api/employees/{id}`, *Then* 200 и сущность;
  для несуществующего id — 404 + `NOT_FOUND`.
- **AC-E8 (FR-E8):** *Given* существующий сотрудник, *When* `PUT`, *Then* 200, поля обновлены,
  updated_at строго позже прежнего.
- **AC-E9 (FR-E9):** *Given* активный сотрудник, *When* `PATCH .../deactivate`, *Then* 200, is_active=false;
  последующий `GET` показывает сотрудника (запись не удалена физически).

## Module 2 — Tickets

- **AC-T1 (FR-T1, FR-T2):** *Given* существующий employee_id, *When* `POST /api/tickets`,
  *Then* 201, status=new, created_at заполнен, resolved_at пуст.
- **AC-T2 (FR-T5):** *Given* несуществующий employee_id, *When* создание, *Then* не 2xx (404/422) + конверт.
- **AC-T3 (FR-T3, FR-T4):** *Given* недопустимое priority/status, *When* запрос, *Then* 422 + `VALIDATION_ERROR`.
- **AC-T4 (FR-T8, FR-T9):** *Given* заявка в статусе new, *When* `PATCH .../assign` на существующего,
  *Then* 200, assigned_to установлен, status=in_progress.
- **AC-T5 (FR-T8):** *Given* assign на несуществующего сотрудника, *Then* не 2xx (404/422) + конверт.
- **AC-T6 (FR-T11):** *Given* заявка new, *When* статус→resolved (запрещённый прямой переход),
  *Then* 409 + `INVALID_STATUS_TRANSITION`.
- **AC-T7 (FR-T11, FR-T12):** *Given* заявка in_progress, *When* статус→resolved, *Then* 200,
  status=resolved, resolved_at заполнен.
- **AC-T8 (FR-T11):** *Given* заявка resolved/rejected, *When* любая смена статуса,
  *Then* 409 + `INVALID_STATUS_TRANSITION` (терминальность).
- **AC-T9 (FR-T6, FR-T14):** *Given* заявки с разными status/priority, *When* фильтры,
  *Then* выдача согласована с фильтром; пагинация работает.
- **AC-T10 (FR-T13):** *Given* набор заявок, *When* `GET /api/tickets/stats`, *Then* 200 и объект
  c ключами total, new, in_progress, resolved, rejected, critical_opened; сумма статусов = total.

## Module 3 — Integration

- **AC-I1 (FR-I1, FR-I2):** *Given* admin, *When* `POST /api/admin/clients`, *Then* 201, тело содержит
  client_id и api_key (plaintext) ровно один раз.
- **AC-I2 (FR-I2, NFR-7):** *Given* созданный клиент, *When* повторное чтение клиента,
  *Then* plaintext-ключ недоступен (контрактная проверка отсутствия `api_key` в последующих ответах).
- **AC-I3 (FR-I5):** *Given* нет заголовка X-API-Key, *When* `POST /api/integration/requests`,
  *Then* 401 + `UNAUTHORIZED`.
- **AC-I4 (FR-I6):** *Given* неверный ключ, *Then* 401 + `UNAUTHORIZED`.
- **AC-I5 (FR-I7):** *Given* деактивированный клиент, *When* запрос с его ключом, *Then* 403 + `FORBIDDEN`.
- **AC-I6 (FR-I8):** *Given* лимит N/мин, *When* (N+1)-й запрос в окне, *Then* 429 + `RATE_LIMIT_EXCEEDED`.
- **AC-I7 (FR-I9):** *Given* пустой request_type, *Then* 422 + `VALIDATION_ERROR`.
- **AC-I8 (FR-I10):** *Given* валидный запрос, *Then* он сохранён со status=accepted и виден в списке.
- **AC-I9 (FR-I11, FR-I12):** *Given* любая попытка обращения, *Then* создаётся запись аудита с
  ip_address и user_agent.
- **AC-I10 (FR-I15):** *Given* accepted-запрос employee_sync, *When* process, *Then* 200,
  status=processed, сотрудник создан/обновлён (матч по external_id, иначе email).
- **AC-I11 (FR-I17):** *Given* запрос в статусе processed, *When* повторный process,
  *Then* 409 + `ALREADY_PROCESSED`.
- **AC-I12 (FR-I16):** *Given* запрос с невалидным payload, *When* process, *Then* status=failed,
  error_message заполнен.
- **AC-I13 (FR-I13, FR-I18):** *Given* запросы/аудит, *When* фильтры (client_id, status, success, даты),
  *Then* выдача согласована с фильтрами; пагинация работает.

## Cross-cutting

- **AC-X1 (NFR-2, NFR-3):** Любой ответ-ошибка соответствует конверту `{error:true, code, message, details}`
  с `code` из разрешённого набора.
- **AC-X2 (NFR-8):** Доступна спецификация OpenAPI/Swagger (или Postman); контрактные проверки тел
  ответов используют схемы из [[TEST_PLAN]].
- **AC-X3 (NFR-1):** Схема данных переносима на PostgreSQL (проверяется на уровне миграций при разработке).

---

*Graph: [[AGENT_CONTEXT]] · [[REQUIREMENTS]] · [[TEST_PLAN]] · [[INVARIANTS]]*
