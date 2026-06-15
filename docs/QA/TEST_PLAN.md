# TEST_PLAN

Стратегия тестирования и **матрица трассируемости** требование → тест-кейс. Источник требований —
[[REQUIREMENTS]]; критерии — [[ACCEPTANCE_CRITERIA]]; инварианты — [[INVARIANTS]]; стек — [[ADR INDEX]]
(ADR-001, ADR-008).

## 1. Тип и стратегия

- **Тип контура: B (TDD-спецификация).** Часть тестов `red` до реализации продукта — ожидаемо.
- **Уровень:** чёрный ящик, API/контракт. Тесты ходят в реальный сервис по `API_BASE_URL`.
- **Архитектура:** POM для API (BaseApiClient + `<Resource>Client`), pydantic-схемы для контракта,
  фабрики уникальных данных. Спеки используют только client-объекты (INV-X4).
- **Категории кейсов:** positive (happy path), negative (валидация, несуществующие id, дубликаты,
  конфликты), boundary (пустые/макс. длина/спецсимволы/границы пагинации), auth (401/403),
  contract (статус + схема тела), behavioral (идемпотентность, пагинация/фильтры, переходы статусов).

## 2. Окружения и данные

- Конфиг — только из env (`tests/api/config/settings.py`), без хардкода секретов (INV-X5, ADR-008).
  Ключевые переменные: `API_BASE_URL`, `ADMIN_AUTH_HEADER`/`ADMIN_AUTH_TOKEN`, `HTTP_TIMEOUT`,
  `EXPECT_CREATED_CODE`. Полный список — `.env.example` и `tests/README.md`.
- Тестовые данные генерируются фабриками с уникальными значениями (email/имя) на каждый прогон —
  изоляция и детерминизм (INV-O2). Где доступно — teardown деактивирует созданное.

## 3. Критерии прохождения

- Каждое FR покрыто ≥1 позитивным кейсом; каждое FR с ветками ошибок — ≥1 негативным.
- Контрактные проверки сверяют статус-код И схему тела (для эндпоинтов с телом).
- Все негативные кейсы проверяют единый конверт ошибки (INV-X1/X2).
- Прогон детерминирован (0 flaky). «Зелёным» контур становится по мере реализации продукта.

## 4. Маркеры pytest

`employees`, `tickets`, `integration`, `audit`, `positive`, `negative`, `contract`, `auth`,
`boundary`, `smoke`. Маркер требования — через `@pytest.mark.req("FR-T11")` (хелпер в `utils`).

## 5. Матрица трассируемости (требование → спецификации/кейсы)

> Кейсы именуются по ресурсу; точные имена функций — в `tests/api/specs/*`. Ниже — соответствие
> требований файлам спеков и типам покрытия (P=positive, N=negative, C=contract, A=auth, B=boundary).

| Требование | Спецификация | Покрытие |
|------------|--------------|----------|
| FR-E1 | specs/test_employees.py::test_create_employee_* | P, C |
| FR-E2 | specs/test_employees.py::test_create_employee_missing_required_* | N, C |
| FR-E3 | specs/test_employees.py::test_create_employee_duplicate_email | N, C |
| FR-E4 | specs/test_employees.py::test_list_employees_filter_* | P |
| FR-E5 | specs/test_employees.py::test_list_employees_pagination | P, B |
| FR-E6 | specs/test_employees.py::test_search_employees_* | P |
| FR-E7 | specs/test_employees.py::test_get_employee_by_id, test_get_employee_not_found | P, N, C |
| FR-E8 | specs/test_employees.py::test_update_employee_* | P, C |
| FR-E9 | specs/test_employees.py::test_deactivate_employee_keeps_record | P, C |
| FR-E10 | specs/test_employees.py::test_create_employee_has_timestamps | P, C |
| FR-T1 | specs/test_tickets.py::test_create_ticket_* | P, C |
| FR-T2 | specs/test_tickets.py::test_create_ticket_status_is_new | P |
| FR-T3 | specs/test_tickets.py::test_create_ticket_invalid_priority | N |
| FR-T4 | specs/test_tickets.py::test_status_transition_invalid_value | N |
| FR-T5 | specs/test_tickets.py::test_create_ticket_nonexistent_employee | N, C |
| FR-T6 | specs/test_tickets.py::test_list_tickets_filter_* | P |
| FR-T7 | specs/test_tickets.py::test_get_ticket_by_id, test_get_ticket_not_found | P, N, C |
| FR-T8 | specs/test_tickets.py::test_assign_ticket_*, test_assign_nonexistent_assignee | P, N, C |
| FR-T9 | specs/test_tickets.py::test_assign_sets_in_progress | P |
| FR-T10 | specs/test_tickets.py::test_status_transition_allowed_* | P |
| FR-T11 | specs/test_tickets.py::test_status_transition_forbidden_*, test_terminal_* | N, C |
| FR-T12 | specs/test_tickets.py::test_resolve_sets_resolved_at | P |
| FR-T13 | specs/test_tickets.py::test_tickets_stats_* | P, C |
| FR-T14 | specs/test_tickets.py::test_list_tickets_pagination | P, B |
| FR-I1 | specs/test_integration_clients_admin.py::test_create_client_* | P, C |
| FR-I2 | specs/test_integration_clients_admin.py::test_create_client_returns_key_once | P, C |
| FR-I3 | specs/test_integration_clients_admin.py::test_deactivate_client | P |
| FR-I4 | specs/test_integration_requests.py::test_submit_request_* | P, C |
| FR-I5 | specs/test_integration_requests.py::test_submit_without_api_key_401 | N, A, C |
| FR-I6 | specs/test_integration_requests.py::test_submit_invalid_api_key_401 | N, A, C |
| FR-I7 | specs/test_integration_requests.py::test_submit_deactivated_client_403 | N, A, C |
| FR-I8 | specs/test_integration_requests.py::test_submit_rate_limit_429 | N, B, C |
| FR-I9 | specs/test_integration_requests.py::test_submit_empty_request_type_422 | N, C |
| FR-I10 | specs/test_integration_requests.py::test_submit_persists_accepted | P |
| FR-I11 | specs/test_audit.py::test_audit_records_each_attempt | P |
| FR-I12 | specs/test_audit.py::test_audit_has_ip_and_user_agent | P, C |
| FR-I13 | specs/test_integration_requests.py::test_list_requests_filter_* | P |
| FR-I14 | specs/test_integration_requests.py::test_process_request_* | P, C |
| FR-I15 | specs/test_integration_requests.py::test_process_employee_sync_creates_or_updates | P |
| FR-I16 | specs/test_integration_requests.py::test_process_failure_sets_failed | N, C |
| FR-I17 | specs/test_integration_requests.py::test_process_already_processed_409 | N, C |
| FR-I18 | specs/test_audit.py::test_list_audit_filter_* | P |
| FR-I19 | specs/test_integration_requests.py::test_request_status_enum_contract | C |
| NFR-1 | (миграции/разработка) — проверяется на этапе реализации | — |
| NFR-2 | utils/asserts.py::assert_error_envelope (во всех негативных кейсах) | C |
| NFR-3 | schemas/common.py::ErrorEnvelope (валидация code из набора) | C |
| NFR-4 | все negative-кейсы валидации (FR-E2, FR-T3, FR-I9, ...) | N |
| NFR-5 | централизованная обработка — косвенно через единообразие конверта | C |
| NFR-6 | (логирование/разработка) | — |
| NFR-7 | test_integration_*: 401/403/429 + одноразовый ключ + хеш | A, N, C |
| NFR-8 | (OpenAPI/Swagger; smoke-проверка доступности схемы при реализации) | — |
| NFR-9 | (README/миграции/структура — артефакты проекта) | — |
| NFR-10 | сам контур = тесты ключевой бизнес-логики | P, N |

> Требования с пометкой «—» (NFR-1/5/6/8/9) проверяются артефактами разработки или smoke-проверками,
> добавляемыми по мере реализации продукта; они отслеживаются, но не блокируют bootstrap.

## 6. CI

`.github/workflows/tests.yml` ставит Python, ставит зависимости, выполняет `pytest --collect-only`
(гейт сборки контура для типа B) и опционально полный прогон, если задан `API_BASE_URL` доступного
сервиса. Подробнее — `tests/README.md`.

---

*Graph: [[AGENT_CONTEXT]] · [[REQUIREMENTS]] · [[ACCEPTANCE_CRITERIA]] · [[INVARIANTS]] · [[STATE]]*
