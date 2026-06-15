# ADR-010: Production hardening (rate limit, queue, observability, идемпотентность)

## Status
Accepted

## Context
Переход от MVP к production-готовности: распределённый rate limit, фоновая обработка, наблюдаемость,
устойчивость к гонкам. Инфраструктура (Redis/брокер) не всегда доступна (dev/CI), поэтому всё —
за абстракциями с in-process фолбэком, чтобы приложение и тесты работали без внешней инфры.

## Decision
- **Rate limit за интерфейсом** (`RateLimiter`): `InMemoryRateLimiter` (default) и `RedisRateLimiter`
  (выбирается при `REDIS_URL`). Ответы интеграции несут `X-RateLimit-Limit/Remaining/Reset`; 429 —
  `Retry-After` (ADR-004, §49).
- **Очередь обработки** (`TaskQueue`): `InlineTaskQueue` (синхронно, default) и `ArqTaskQueue`
  (Redis). Воркер `app/worker.py` (arq) с ретраями и **DLQ** (dead-letter → аудит). Админский
  `POST .../process` остаётся синхронным (явное действие); очередь — путь автоматической фоновой
  обработки при масштабировании (§48).
- **Идемпотентность/гонка (§45):** захват строки запроса `SELECT ... FOR UPDATE` на СУБД с
  поддержкой (PostgreSQL); повторная обработка `processed` → 409 `ALREADY_PROCESSED` (INV-P11).
- **Наблюдаемость:** middleware `X-Request-ID` (генерация/проброс), структурные логи (JSON по
  `LOG_JSON`) с request-id в контексте, опциональный **Sentry** (`SENTRY_DSN`). §50.
- **Код `CONFLICT` (409)** добавлен в набор ошибок для нарушений уникальности (Q-7, ADR-003).

## Consequences
### Positive
- Готовность к горизонтальному масштабированию (stateless app + внешнее состояние в БД/Redis).
- Всё работает и тестируется без инфраструктуры; прод-бэкенды включаются конфигом.
### Negative
- Зависимости `redis`/`arq`/`sentry-sdk` опциональны (`requirements-optional.txt`); прод-пути
  покрываются интеграционно, не юнит-тестами контура.

## Alternatives considered
### Жёстко требовать Redis/брокер
Отклонено: ломает dev/CI и локальный запуск; абстракция с фолбэком гибче.

---

*Graph: [[AGENT_CONTEXT]] · [[INVARIANTS]] · [[FINAL_SYSTEM_SPEC]] · [[ADDITIONAL_QUESTIONS]]*
