"""Specs for Module 3 — audit log (EP-17). Traceability: FR-I11, FR-I12, FR-I18; INV-P10."""

from __future__ import annotations

import allure
import pytest

from tests.api.fixtures import factories
from tests.api.schemas.common import extract_items
from tests.api.schemas.integration import AuditOut
from tests.api.utils.allure_meta import EPIC_INTEGRATION
from tests.api.utils.asserts import assert_pagination, assert_schema, assert_status
from tests.api.utils.markers import req

pytestmark = [pytest.mark.integration, pytest.mark.audit]

CREATED = (200, 201)


def _new_client(admin_clients, **overrides) -> tuple[int, str]:
    response = admin_clients.create(factories.client_payload(**overrides))
    assert_status(response, *CREATED)
    return response.json["client_id"], response.json["api_key"]


@req("FR-I11", "INV-P10")
@allure.epic(EPIC_INTEGRATION)
@allure.feature("Аудит")
@allure.story("Каждая попытка обращения к интеграции пишется в аудит")
@allure.title("Аудит: каждая попытка обращения фиксируется в журнале")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.positive
def test_audit_records_each_attempt(admin_clients, integration, audit):
    """Каждое обращение к интеграции должно фиксироваться в аудите (INV-P10):
    после успешной отправки данных по клиенту в журнале аудита появляется хотя бы одна запись."""
    # Arrange: создаём клиента и выполняем обращение к интеграции
    client_id, api_key = _new_client(admin_clients)
    integration.submit(factories.employee_sync_payload(), api_key=api_key)
    # Act: запрашиваем журнал аудита по клиенту
    response = audit.list(client_id=client_id, limit=100)
    # Assert: 200, корректная пагинация и наличие записей аудита
    with allure.step("Проверка: 200, валидная пагинация, аудит содержит записи по обращению"):
        assert_status(response, 200)
        items = assert_pagination(response.json, limit=100)
        assert items, "каждая попытка обращения должна попадать в аудит"


@req("FR-I12", "INV-P10")
@allure.epic(EPIC_INTEGRATION)
@allure.feature("Аудит")
@allure.story("В аудите сохраняются IP-адрес и User-Agent")
@allure.title("Аудит: запись содержит ip_address и user_agent")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.positive
@pytest.mark.contract
def test_audit_has_ip_and_user_agent(admin_clients, integration, audit):
    """Каждая попытка обращения к интеграции фиксируется в аудите с IP и User-Agent
    (INV-P10); запись соответствует схеме AuditOut, поля ip_address и user_agent заполнены."""
    # Arrange: создаём клиента и делаем обращение
    client_id, api_key = _new_client(admin_clients)
    integration.submit(factories.employee_sync_payload(), api_key=api_key)
    # Act: запрашиваем аудит по клиенту
    response = audit.list(client_id=client_id, limit=100)
    # Assert: схема и заполненность ip/user_agent
    with allure.step("Проверка: 200, схема AuditOut, ip_address и user_agent не пусты"):
        assert_status(response, 200)
        items = extract_items(response.json)
        record = assert_schema(items[0], AuditOut)
        assert record.ip_address, "в аудите должен сохраняться IP-адрес"
        assert record.user_agent, "в аудите должен сохраняться User-Agent"


@req("FR-I11", "INV-P10")
@allure.epic(EPIC_INTEGRATION)
@allure.feature("Аудит")
@allure.story("Неуспешная попытка обращения тоже аудируется")
@allure.title("Аудит: неуспешная (неавторизованная) попытка фиксируется с success=false")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.negative
def test_audit_records_failed_attempt(integration, audit):
    """Неуспешное обращение к интеграции также должно попадать в аудит (INV-P10):
    неавторизованная попытка возвращает 401, но фиксируется в журнале с признаком success=false."""
    # Arrange / Act: неавторизованная попытка обращения (401), которая всё равно аудируется
    # Unauthenticated attempt → 401, but the attempt must still be audited (success=false).
    integration.submit(factories.employee_sync_payload(), api_key="company_live_invalid_key")
    # Act: запрашиваем аудит, отфильтрованный по неуспешным попыткам
    response = audit.list(success=False, limit=100)
    # Assert: 200, валидная пагинация и наличие записи с success=false
    with allure.step("Проверка: 200, валидная пагинация, есть запись аудита с success=false"):
        assert_status(response, 200)
        items = assert_pagination(response.json, limit=100)
        assert any(item.get("success") is False for item in items), "неуспешная попытка должна аудироваться"


@req("FR-I18")
@allure.epic(EPIC_INTEGRATION)
@allure.feature("Аудит")
@allure.story("Фильтрация журнала аудита по признаку success")
@allure.title("Аудит: фильтр success=true возвращает только успешные записи")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.positive
def test_list_audit_filter_success_true(admin_clients, integration, audit):
    """Журнал аудита поддерживает фильтрацию по признаку success (FR-I18):
    при запросе с success=true возвращаются только записи об успешных обращениях."""
    # Arrange: создаём клиента и выполняем успешное обращение к интеграции
    client_id, api_key = _new_client(admin_clients)
    integration.submit(factories.employee_sync_payload(), api_key=api_key)
    # Act: запрашиваем аудит по клиенту с фильтром success=true
    response = audit.list(client_id=client_id, success=True, limit=100)
    # Assert: 200, валидная пагинация и все записи успешны
    with allure.step("Проверка: 200, валидная пагинация, все записи имеют success=true"):
        assert_status(response, 200)
        items = assert_pagination(response.json, limit=100)
        assert all(item.get("success") is True for item in items)
