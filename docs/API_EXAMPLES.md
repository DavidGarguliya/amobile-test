# API_EXAMPLES

Примеры запросов и ответов (бриф §6, п.40). Базовый URL — `http://localhost:8000`. Интерактивная
схема — `/docs` (Swagger), `/openapi.json`. Полный конверт ошибок — в конце.

## Employees

### Создание (EP-01)
```bash
curl -X POST http://localhost:8000/api/employees \
  -H 'Content-Type: application/json' \
  -d '{"full_name":"Иванов Иван Иванович","position":"Backend Developer","department":"IT","phone":"+79401234567","email":"ivanov@example.com"}'
```
```json
201 Created
{"id":1,"full_name":"Иванов Иван Иванович","position":"Backend Developer","department":"IT","phone":"+79401234567","email":"ivanov@example.com","is_active":true,"external_id":null,"created_at":"2026-06-15T10:00:00Z","updated_at":"2026-06-15T10:00:00Z"}
```

### Список с фильтрами (EP-02)
```bash
curl 'http://localhost:8000/api/employees?department=IT&is_active=true&search=иван&page=1&limit=20'
```
```json
200 OK
{"items":[{"id":1,"full_name":"Иванов Иван Иванович","position":"Backend Developer","department":"IT","phone":"+79401234567","email":"ivanov@example.com","is_active":true,"external_id":null,"created_at":"...","updated_at":"..."}],"total":1,"page":1,"limit":20}
```

### Получение по ID (EP-03), Обновление (EP-04), Деактивация (EP-05)
```bash
curl http://localhost:8000/api/employees/1
curl -X PUT http://localhost:8000/api/employees/1 -H 'Content-Type: application/json' -d '{"position":"Team Lead"}'
curl -X PATCH http://localhost:8000/api/employees/1/deactivate
```
```json
# деактивация → 200 OK
{"id":1, "...":"...", "is_active":false}
```

## Tickets

### Создание (EP-06)
```bash
curl -X POST http://localhost:8000/api/tickets \
  -H 'Content-Type: application/json' \
  -d '{"employee_id":1,"title":"Не работает принтер","description":"Принтер в кабинете 204 не печатает","priority":"medium"}'
```
```json
201 Created
{"id":1,"employee_id":1,"title":"Не работает принтер","description":"...","priority":"medium","status":"new","assigned_to":null,"created_at":"...","updated_at":"...","resolved_at":null}
```

### Список (EP-07), По ID (EP-08)
```bash
curl 'http://localhost:8000/api/tickets?status=new&priority=critical&page=1&limit=20'
curl http://localhost:8000/api/tickets/1
```

### Назначение исполнителя (EP-09) → статус становится in_progress
```bash
curl -X PATCH http://localhost:8000/api/tickets/1/assign -H 'Content-Type: application/json' -d '{"assigned_to":2}'
```
```json
200 OK
{"id":1,"assigned_to":2,"status":"in_progress", "...":"..."}
```

### Смена статуса (EP-10)
```bash
curl -X PATCH http://localhost:8000/api/tickets/1/status -H 'Content-Type: application/json' -d '{"status":"resolved"}'
```
```json
200 OK
{"id":1,"status":"resolved","resolved_at":"2026-06-15T11:00:00Z", "...":"..."}
# запрещённый переход (например new → resolved):
409 Conflict
{"error":true,"code":"INVALID_STATUS_TRANSITION","message":"Cannot transition ticket from new to resolved","details":{"from":"new","to":"resolved"}}
```

### Статистика (EP-11)
```bash
curl http://localhost:8000/api/tickets/stats
```
```json
200 OK
{"total":120,"new":20,"in_progress":15,"resolved":80,"rejected":5,"critical_opened":3}
```

## Integration (admin + external)

### Создание API-клиента (EP-12) — ключ показывается один раз
```bash
curl -X POST http://localhost:8000/api/admin/clients -H 'Content-Type: application/json' -d '{"name":"1C Integration","requests_limit_per_minute":60}'
```
```json
201 Created
{"client_id":1,"api_key":"company_live_8Kk2...redacted"}
```

### Деактивация клиента (EP-13)
```bash
curl -X PATCH http://localhost:8000/api/admin/clients/1/deactivate
```

### Отправка интеграционного запроса (EP-14)
```bash
curl -X POST http://localhost:8000/api/integration/requests \
  -H 'X-API-Key: company_live_8Kk2...redacted' -H 'Content-Type: application/json' \
  -d '{"request_type":"employee_sync","payload":{"external_id":"EMP-001","full_name":"Иванов Иван Иванович","department":"IT","position":"Developer","email":"ivanov@example.com"}}'
```
```json
201 Created
{"id":1,"client_id":1,"request_type":"employee_sync","payload":{"...":"..."},"status":"accepted","error_message":null,"created_at":"...","processed_at":null}

# без ключа → 401, неверный ключ → 401, деактивирован → 403, превышен лимит → 429, пустой request_type → 422
401 {"error":true,"code":"UNAUTHORIZED","message":"API key is missing","details":null}
429 {"error":true,"code":"RATE_LIMIT_EXCEEDED","message":"Per-minute request limit exceeded","details":null}
```

### Список интеграционных запросов (EP-15)
```bash
curl 'http://localhost:8000/api/admin/integration/requests?client_id=1&status=accepted&page=1&limit=20'
```

### Обработка запроса (EP-16) — employee_sync создаёт/обновляет сотрудника
```bash
curl -X POST http://localhost:8000/api/admin/integration/requests/1/process
```
```json
200 OK
{"status":"processed","message":"Employee synchronized successfully"}
# повторная обработка processed:
409 {"error":true,"code":"ALREADY_PROCESSED","message":"Request has already been processed","details":null}
```

### Аудит (EP-17)
```bash
curl 'http://localhost:8000/api/admin/audit?client_id=1&success=true&page=1&limit=20'
```
```json
200 OK
{"items":[{"id":1,"client_id":1,"action":"integration.submit","ip_address":"127.0.0.1","user_agent":"curl/8.0","success":true,"details":{"request_id":1},"created_at":"..."}],"total":1,"page":1,"limit":20}
```

## Единый формат ошибок (§5.3)
```json
{"error":true,"code":"VALIDATION_ERROR","message":"Поле email обязательно","details":{"field":"email"}}
```
Коды: `VALIDATION_ERROR` (422), `NOT_FOUND` (404), `UNAUTHORIZED` (401), `FORBIDDEN` (403),
`RATE_LIMIT_EXCEEDED` (429), `INVALID_STATUS_TRANSITION` (409), `ALREADY_PROCESSED` (409),
`INTERNAL_ERROR` (500).

---

*Graph: [[AGENT_CONTEXT]] · [[FINAL_SYSTEM_SPEC]] · [[RUNBOOK]] · [[TEST_PLAN]]*
