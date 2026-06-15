# ADR-009: Авторизация админ-поверхности (JWT + RBAC)

## Status
Accepted

## Context
Бриф не описывает авторизацию для `/api/admin/*`, employees и tickets (OPEN QUESTION Q-4). Оставлять
их открытыми небезопасно (best practice — закрывать мутации и админ-операции). Нужна типовая,
расширяемая модель доступа без тяжёлых зависимостей.

## Decision
Ввести **аутентификацию по JWT (HS256) и ролевую модель (RBAC)**:

- Сущность `users` (email, `password_hash` через **scrypt**, `role`, `is_active`). Роли:
  `admin | operator | viewer`.
- `POST /api/auth/login` → JWT (sub=user id, role, exp). `GET /api/auth/me`. `POST /api/auth/users`
  (admin-only) — управление пользователями. Bootstrap-admin сидируется на старте из `ADMIN_EMAIL`/
  `ADMIN_PASSWORD`.
- Зависимость `require_roles(*roles)`: пусто → любой аутентифицированный; иначе — проверка роли.
- Гейтинг: `/api/admin/*` → `admin`; записи employees/tickets → `admin|operator`; чтения → любой
  аутентифицированный. Интеграционный вход остаётся на `X-API-Key` (машина-машина, ADR-004).
- JWT и scrypt реализованы на stdlib (`hmac`, `hashlib.scrypt`) — без дополнительных зависимостей.
- Флаг `AUTH_ENABLED` (default true) позволяет временно отключать для отладки.

## Consequences
### Positive
- Закрыты мутации и админ-операции; роли расширяемы (per-resource scopes позже).
- Нет внешних крипто-зависимостей; секреты (`JWT_SECRET`) — из env (INV-X5), fail-fast в проде.
### Negative
- Чёрно-ящичные тесты теперь логинятся (фикстура admin-токена) — небольшая доработка контура.
- Отзыв токенов до истечения требует blacklist (Redis) — отмечено как улучшение.

## Alternatives considered
### Статический admin-токен из env
Проще, но без ролей и пользователей; оставлен как деградация при `AUTH_ENABLED=false`.
### OAuth2 password flow (form) / сторонний IdP
Избыточно для объёма; JSON-логин проще и достаточен.

---

*Graph: [[AGENT_CONTEXT]] · [[INVARIANTS]] · [[FINAL_SYSTEM_SPEC]] · [[TEST_PLAN]]*
