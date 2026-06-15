# ADR-003: Единый конверт ошибок и набор кодов

## Status
Accepted

## Context
Бриф §5.3 задаёт единый формат ошибок и набор кодов. Требования NFR-2, NFR-3, NFR-5 и инварианты
INV-X1..INV-X3 требуют, чтобы любой ошибочный ответ был унифицирован, а обработка — централизована.

## Decision
Все ошибочные ответы возвращаются конвертом:
```json
{ "error": true, "code": "<ERROR_CODE>", "message": "<human-readable>", "details": { } }
```
Разрешённый набор `code`: `VALIDATION_ERROR`, `NOT_FOUND`, `UNAUTHORIZED`, `FORBIDDEN`,
`RATE_LIMIT_EXCEEDED`, `INVALID_STATUS_TRANSITION`, `ALREADY_PROCESSED`, `INTERNAL_ERROR`.

Маппинг код↔HTTP (целевой): VALIDATION_ERROR→422, NOT_FOUND→404, UNAUTHORIZED→401,
FORBIDDEN→403, RATE_LIMIT_EXCEEDED→429, INVALID_STATUS_TRANSITION→409, ALREADY_PROCESSED→409,
INTERNAL_ERROR→500. Конверт реализуется единым обработчиком исключений (продукт) и проверяется
контрактной схемой `ErrorEnvelope` в тест-контуре (`tests/api/schemas`).

## Consequences
### Positive
- Предсказуемость для клиентов и тестов; контрактные негативные проверки тривиальны (AC-X1).
- Централизация исключает «забытые» неунифицированные ответы (INV-X3).
### Negative
- Дубликат email и конфликт статуса делят HTTP 409 — различаются по `code` (INV-X2).

## Alternatives considered
### RFC 7807 (application/problem+json)
Отклонено: бриф явно задаёт собственный конверт; соответствие брифу важнее.

---

*Graph: [[AGENT_CONTEXT]] · [[INVARIANTS]] · [[REQUIREMENTS]] · [[TEST_PLAN]]*
