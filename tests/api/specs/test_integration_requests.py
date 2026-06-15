"""Specs for Module 3 — integration ingress & processing (EP-14, EP-15, EP-16).

Traceability: FR-I4..FR-I10, FR-I13..FR-I17, FR-I19; invariants INV-P8..P12.
"""

from __future__ import annotations

import allure
import pytest

from tests.api.fixtures import factories
from tests.api.schemas.common import extract_items
from tests.api.schemas.integration import IntegrationRequestOut, ProcessResultOut
from tests.api.utils.allure_meta import EPIC_INTEGRATION
from tests.api.utils.asserts import (
    assert_error_envelope,
    assert_pagination,
    assert_schema,
    assert_status,
)
from tests.api.utils.markers import req

pytestmark = pytest.mark.integration

CREATED = (200, 201)


# -- helpers ---------------------------------------------------------------------------------
def _new_client(admin_clients, **overrides) -> tuple[int, str]:
    response = admin_clients.create(factories.client_payload(**overrides))
    assert_status(response, *CREATED)
    return response.json["client_id"], response.json["api_key"]


def _request_id(submit_response, admin_integration, client_id) -> int:
    body = submit_response.json
    if isinstance(body, dict) and isinstance(body.get("id"), int):
        return body["id"]
    listing = admin_integration.list(client_id=client_id, limit=100)
    assert_status(listing, 200)
    items = extract_items(listing.json)
    assert items, "ожидался хотя бы один сохранённый интеграционный запрос"
    return max(item["id"] for item in items)


# -- submit: positive / persistence ----------------------------------------------------------
@req("FR-I4", "FR-I10")
@allure.epic(EPIC_INTEGRATION)
@allure.feature("Приём интеграционного запроса (авторизация и лимиты)")
@allure.story("Корректный запрос с валидным ключом принимается")
@allure.title("Интеграция с валидным X-API-Key → запрос принят (accepted)")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.positive
def test_submit_request_accepted(admin_clients, integration):
    """Запрос на /api/integration/requests с валидным X-API-Key должен приниматься
    сервисом с кодом 200/201 и статусом accepted (FR-I4, FR-I10)."""
    # Arrange: создаём активного клиента и получаем его API-ключ
    _, api_key = _new_client(admin_clients)
    # Act: отправляем корректный employee_sync запрос с валидным ключом
    response = integration.submit(factories.employee_sync_payload(), api_key=api_key)
    # Assert: запрос принят (200/201)
    with allure.step("Проверка: запрос принят (200/201)"):
        assert_status(response, *CREATED)


@req("FR-I8", "NFR-7")
@allure.epic(EPIC_INTEGRATION)
@allure.feature("Приём интеграционного запроса (авторизация и лимиты)")
@allure.story("Ответ содержит заголовки лимитирования")
@allure.title("Интеграция возвращает заголовки X-RateLimit-*")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.positive
@pytest.mark.contract
def test_submit_returns_rate_limit_headers(admin_clients, integration):
    """Успешный ответ на интеграционный запрос должен содержать заголовки лимитирования
    X-RateLimit-Limit и X-RateLimit-Remaining (FR-I8, NFR-7)."""
    # Arrange: создаём активного клиента и получаем его API-ключ
    _, api_key = _new_client(admin_clients)
    # Act: отправляем корректный запрос с валидным ключом
    response = integration.submit(factories.employee_sync_payload(), api_key=api_key)
    # Assert: запрос принят и присутствуют заголовки X-RateLimit-*
    with allure.step("Проверка: 200/201 + заголовки X-RateLimit-*"):
        assert_status(response, *CREATED)
        assert response.headers.get("X-RateLimit-Limit"), "ожидались заголовки X-RateLimit-*"
        assert response.headers.get("X-RateLimit-Remaining") is not None


@req("FR-I10", "FR-I13")
@allure.epic(EPIC_INTEGRATION)
@allure.feature("Приём интеграционного запроса (авторизация и лимиты)")
@allure.story("Принятый запрос сохраняется и попадает в список")
@allure.title("Принятый интеграционный запрос сохраняется и виден в списке")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.positive
def test_submit_persists_and_is_listed(admin_clients, integration, admin_integration):
    """Принятый интеграционный запрос должен сохраняться в системе и появляться
    в списке запросов клиента (FR-I10, FR-I13)."""
    # Arrange: создаём активного клиента и получаем его API-ключ
    client_id, api_key = _new_client(admin_clients)
    # Act: отправляем запрос и запрашиваем список запросов клиента
    assert_status(integration.submit(factories.employee_sync_payload(), api_key=api_key), *CREATED)
    listing = admin_integration.list(client_id=client_id, limit=100)
    # Assert: список доступен и содержит сохранённый запрос
    with allure.step("Проверка: 200 + сохранённый запрос присутствует в списке"):
        assert_status(listing, 200)
        items = assert_pagination(listing.json, limit=100)
        assert items, "сохранённый запрос должен попадать в список"


@req("FR-I19")
@allure.epic(EPIC_INTEGRATION)
@allure.feature("Список интеграционных запросов")
@allure.story("Статус запроса соответствует контракту перечисления")
@allure.title("Статус интеграционного запроса входит в допустимое множество")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.contract
def test_request_status_enum_contract(admin_clients, integration, admin_integration):
    """Статус интеграционного запроса в выдаче должен принимать только значения
    из допустимого перечисления: accepted/rejected/processed/failed (FR-I19)."""
    # Arrange: создаём клиента и отправляем запрос, чтобы появилась запись в списке
    client_id, api_key = _new_client(admin_clients)
    assert_status(integration.submit(factories.employee_sync_payload(), api_key=api_key), *CREATED)
    # Act: получаем список запросов клиента и валидируем схему первого элемента
    listing = admin_integration.list(client_id=client_id, limit=100)
    # Assert: статус входит в допустимое множество значений
    with allure.step("Проверка: статус принадлежит допустимому множеству"):
        assert_status(listing, 200)
        items = extract_items(listing.json)
        item = assert_schema(items[0], IntegrationRequestOut)
        assert item.status in {"accepted", "rejected", "processed", "failed"}


# -- submit: auth / negative -----------------------------------------------------------------
@req("FR-I5", "INV-P9")
@allure.epic(EPIC_INTEGRATION)
@allure.feature("Приём интеграционного запроса (авторизация и лимиты)")
@allure.story("Запрос без API-ключа отклоняется")
@allure.title("Интеграция без X-API-Key → 401 UNAUTHORIZED")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.negative
@pytest.mark.auth
@pytest.mark.contract
def test_submit_without_api_key_401(integration):
    """Запрос на /api/integration/requests без заголовка X-API-Key должен отклоняться
    с кодом 401 и единым конвертом ошибки UNAUTHORIZED (INV-P9)."""
    # Act: отправляем запрос без ключа
    response = integration.submit(factories.employee_sync_payload())  # no X-API-Key
    # Assert: 401 и конверт ошибки
    with allure.step("Проверка: 401 + UNAUTHORIZED"):
        assert_status(response, 401)
        assert_error_envelope(response, "UNAUTHORIZED")


@req("FR-I6", "INV-P9")
@allure.epic(EPIC_INTEGRATION)
@allure.feature("Приём интеграционного запроса (авторизация и лимиты)")
@allure.story("Запрос с неверным API-ключом отклоняется")
@allure.title("Интеграция с неверным X-API-Key → 401 UNAUTHORIZED")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.negative
@pytest.mark.auth
@pytest.mark.contract
def test_submit_invalid_api_key_401(integration):
    """Запрос с несуществующим/неверным X-API-Key должен отклоняться с кодом 401
    и единым конвертом ошибки UNAUTHORIZED (INV-P9)."""
    # Act: отправляем запрос с заведомо неверным ключом
    response = integration.submit(factories.employee_sync_payload(), api_key="company_live_invalid_key")
    # Assert: 401 и конверт ошибки
    with allure.step("Проверка: 401 + UNAUTHORIZED"):
        assert_status(response, 401)
        assert_error_envelope(response, "UNAUTHORIZED")


@req("FR-I7", "INV-P9")
@allure.epic(EPIC_INTEGRATION)
@allure.feature("Приём интеграционного запроса (авторизация и лимиты)")
@allure.story("Запрос от деактивированного клиента отклоняется")
@allure.title("Интеграция деактивированного клиента → 403 FORBIDDEN")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.negative
@pytest.mark.auth
@pytest.mark.contract
def test_submit_deactivated_client_403(admin_clients, integration):
    """Запрос с валидным ключом, но от деактивированного клиента должен отклоняться
    с кодом 403 и единым конвертом ошибки FORBIDDEN (INV-P9)."""
    # Arrange: создаём клиента и деактивируем его
    client_id, api_key = _new_client(admin_clients)
    assert_status(admin_clients.deactivate(client_id), 200)
    # Act: отправляем запрос ключом деактивированного клиента
    response = integration.submit(factories.employee_sync_payload(), api_key=api_key)
    # Assert: 403 и конверт ошибки
    with allure.step("Проверка: 403 + FORBIDDEN"):
        assert_status(response, 403)
        assert_error_envelope(response, "FORBIDDEN")


@req("FR-I9")
@allure.epic(EPIC_INTEGRATION)
@allure.feature("Приём интеграционного запроса (авторизация и лимиты)")
@allure.story("Запрос с пустым request_type отклоняется")
@allure.title("Интеграция с пустым request_type → 422 VALIDATION_ERROR")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.negative
@pytest.mark.contract
def test_submit_empty_request_type_422(admin_clients, integration):
    """Запрос с пустым полем request_type должен отклоняться валидацией с кодом 422
    и единым конвертом ошибки VALIDATION_ERROR (FR-I9)."""
    # Arrange: создаём активного клиента и получаем его API-ключ
    _, api_key = _new_client(admin_clients)
    # Act: отправляем запрос с пустым request_type
    response = integration.submit({"request_type": "", "payload": {}}, api_key=api_key)
    # Assert: 422 и конверт ошибки валидации
    with allure.step("Проверка: 422 + VALIDATION_ERROR"):
        assert_status(response, 422)
        assert_error_envelope(response, "VALIDATION_ERROR")


@req("FR-I9", "FR-I11", "INV-P10")
@allure.epic(EPIC_INTEGRATION)
@allure.feature("Приём интеграционного запроса (авторизация и лимиты)")
@allure.story("Отклонённый по валидации запрос всё равно аудируется")
@allure.title("Интеграция с пустым request_type: 422 фиксируется в аудите (success=false)")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.negative
def test_submit_empty_request_type_is_audited(admin_clients, integration, audit):
    """Даже отклонённая валидацией попытка (пустой request_type) должна фиксироваться в аудите
    (INV-P10): валидация выполняется после аутентификации, поэтому обращение успевает записаться
    как неуспешное (success=false) по соответствующему клиенту."""
    # Arrange: активный клиент
    client_id, api_key = _new_client(admin_clients)
    # Act: невалидный запрос (пустой request_type) с валидным ключом → 422
    assert_status(integration.submit({"request_type": "", "payload": {}}, api_key=api_key), 422)
    # Assert: по клиенту есть запись аудита с success=false
    with allure.step("Проверка: в аудите клиента есть неуспешная запись об этой попытке"):
        records = audit.list(client_id=client_id, success=False, limit=100)
        assert_status(records, 200)
        items = extract_items(records.json)
        assert any(item.get("client_id") == client_id for item in items), (
            "отклонённая валидацией попытка должна попадать в аудит (success=false)"
        )


@req("FR-I8", "INV-P9")
@allure.epic(EPIC_INTEGRATION)
@allure.feature("Приём интеграционного запроса (авторизация и лимиты)")
@allure.story("Превышение лимита запросов отклоняется")
@allure.title("Интеграция сверх лимита запросов в минуту → 429 TOO_MANY_REQUESTS")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.negative
@pytest.mark.boundary
@pytest.mark.contract
def test_submit_rate_limit_429(admin_clients, integration, settings):
    """При превышении настроенного лимита запросов в минуту сервис должен возвращать
    код 429 хотя бы на одном из запросов сверх лимита (FR-I8, INV-P9)."""
    # Arrange: создаём клиента с маленьким лимитом и определяем число избыточных проб
    limit = 2
    _, api_key = _new_client(admin_clients, requests_limit_per_minute=limit)
    extra = max(3, settings.rate_limit_probe_count)
    # Act: отправляем больше запросов, чем разрешено лимитом, и собираем статусы
    statuses = [
        integration.submit(factories.employee_sync_payload(), api_key=api_key).status_code
        for _ in range(limit + extra)
    ]
    # Assert: среди статусов присутствует 429 (срабатывание лимитера)
    with allure.step("Проверка: среди ответов есть 429"):
        assert 429 in statuses, f"ожидался 429 при превышении лимита {limit}/мин, получено: {statuses}"


# -- listing filters -------------------------------------------------------------------------
@req("FR-I13")
@allure.epic(EPIC_INTEGRATION)
@allure.feature("Список интеграционных запросов")
@allure.story("Фильтрация списка по идентификатору клиента")
@allure.title("Список интеграционных запросов с фильтром client_id возвращает только своего клиента")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.positive
def test_list_requests_filter_by_client(admin_clients, integration, admin_integration):
    """Список интеграционных запросов с фильтром по client_id должен возвращать только
    запросы указанного клиента (FR-I13)."""
    # Arrange: создаём клиента и отправляем от его имени запрос
    client_id, api_key = _new_client(admin_clients)
    assert_status(integration.submit(factories.employee_sync_payload(), api_key=api_key), *CREATED)
    # Act: запрашиваем список с фильтром по client_id
    response = admin_integration.list(client_id=client_id, limit=100)
    # Assert: все элементы относятся к запрошенному клиенту
    with allure.step("Проверка: 200 + все записи принадлежат запрошенному клиенту"):
        assert_status(response, 200)
        items = assert_pagination(response.json, limit=100)
        assert all(item.get("client_id") == client_id for item in items)


# -- processing ------------------------------------------------------------------------------
@req("FR-I14", "FR-I15", "INV-P12")
@allure.epic(EPIC_INTEGRATION)
@allure.feature("Обработка запроса")
@allure.story("Обработка employee_sync создаёт сотрудника")
@allure.title("Обработка employee_sync → статус processed и сотрудник создан в справочнике")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.positive
@pytest.mark.contract
def test_process_employee_sync_creates_employee(admin_clients, integration, admin_integration, employees):
    """Обработка интеграционного запроса типа employee_sync должна завершаться статусом
    processed и приводить к созданию/обновлению сотрудника в справочнике (FR-I14, FR-I15, INV-P12)."""
    # Arrange: создаём клиента и отправляем employee_sync запрос
    client_id, api_key = _new_client(admin_clients)
    sync = factories.employee_sync_payload()
    email = sync.payload["email"]
    submit = integration.submit(sync, api_key=api_key)
    assert_status(submit, *CREATED)
    request_id = _request_id(submit, admin_integration, client_id)
    # Act: запускаем обработку запроса
    result = admin_integration.process(request_id)
    # Assert: обработка успешна, схема результата валидна, статус processed
    with allure.step("Проверка: 200 + схема ProcessResultOut + статус processed"):
        assert_status(result, 200)
        assert_schema(result.json, ProcessResultOut)
        assert result.json.get("status") == "processed"
    # Assert: сотрудник создан/обновлён в справочнике (INV-P12)
    found = employees.list(search=email, limit=50)
    with allure.step("Проверка: сотрудник присутствует в справочнике (INV-P12)"):
        assert_status(found, 200)
        items = extract_items(found.json)
        assert any(item.get("email") == email for item in items), "employee_sync должен создать сотрудника"


@req("FR-I17", "INV-P11")
@allure.epic(EPIC_INTEGRATION)
@allure.feature("Обработка запроса")
@allure.story("Повторная обработка уже обработанного запроса отклоняется")
@allure.title("Повторная обработка processed-запроса → 409 ALREADY_PROCESSED")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.negative
@pytest.mark.contract
def test_process_already_processed_409(admin_clients, integration, admin_integration):
    """Повторная обработка уже обработанного запроса должна отклоняться с кодом 409
    и конвертом ошибки ALREADY_PROCESSED — идемпотентность обработки (FR-I17, INV-P11)."""
    # Arrange: создаём клиента, отправляем запрос и обрабатываем его в первый раз
    client_id, api_key = _new_client(admin_clients)
    submit = integration.submit(factories.employee_sync_payload(), api_key=api_key)
    assert_status(submit, *CREATED)
    request_id = _request_id(submit, admin_integration, client_id)
    assert_status(admin_integration.process(request_id), 200)
    # Act: пытаемся обработать уже обработанный запрос повторно
    response = admin_integration.process(request_id)
    # Assert: 409 и конверт ошибки идемпотентности
    with allure.step("Проверка: 409 + ALREADY_PROCESSED"):
        assert_status(response, 409)
        assert_error_envelope(response, "ALREADY_PROCESSED")


@req("FR-I16")
@allure.epic(EPIC_INTEGRATION)
@allure.feature("Обработка запроса")
@allure.story("Ошибка обработки переводит запрос в статус failed")
@allure.title("Обработка некорректного payload → статус failed и заполненный error_message")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.negative
def test_process_failure_sets_failed_status(admin_clients, integration, admin_integration):
    """При ошибке обработки запрос должен переходить в статус failed с непустым полем
    error_message, доступным в списке запросов (FR-I16)."""
    # Arrange: создаём клиента и отправляем payload, который заведомо нельзя синхронизировать
    client_id, api_key = _new_client(admin_clients)
    # Payload that cannot be synced (no external_id and no email → no match key, cannot create).
    bad = factories.employee_sync_payload()
    bad.payload.pop("external_id", None)
    bad.payload.pop("email", None)
    submit = integration.submit(bad, api_key=api_key)
    assert_status(submit, *CREATED)
    request_id = _request_id(submit, admin_integration, client_id)
    # Act: запускаем обработку (ожидаемо завершится ошибкой)
    admin_integration.process(request_id)  # processing is expected to fail
    # Assert: через список убеждаемся, что запрос в статусе failed и есть error_message (FR-I16)
    listing = admin_integration.list(client_id=client_id, limit=100)
    with allure.step("Проверка: статус failed + непустой error_message"):
        assert_status(listing, 200)
        item = next(i for i in extract_items(listing.json) if i.get("id") == request_id)
        assert item.get("status") == "failed", f"ожидался статус failed, получено {item.get('status')!r}"
        assert item.get("error_message"), "error_message должен быть заполнен при ошибке обработки"
