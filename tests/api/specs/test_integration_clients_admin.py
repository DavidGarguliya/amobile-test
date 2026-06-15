"""Specs for Module 3 — API client administration (EP-12, EP-13). Traceability: FR-I1..FR-I3."""

from __future__ import annotations

import allure
import pytest

from tests.api.fixtures import factories
from tests.api.schemas.integration import ClientCreatedOut
from tests.api.utils.allure_meta import EPIC_INTEGRATION
from tests.api.utils.asserts import assert_schema, assert_status
from tests.api.utils.markers import req

pytestmark = pytest.mark.integration

CREATED = (200, 201)


@req("FR-I1", "FR-I2", "INV-P8")
@allure.epic(EPIC_INTEGRATION)
@allure.feature("Управление API-клиентами")
@allure.story("Ключ выдаётся ровно один раз при создании клиента")
@allure.title("Создание клиента: ответ содержит client_id и plaintext api_key")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.positive
@pytest.mark.contract
def test_create_client_returns_key_once(admin_clients):
    """POST /api/admin/clients создаёт клиента и единожды возвращает plaintext-ключ
    (в БД хранится только хеш, INV-P8); ответ соответствует схеме ClientCreatedOut."""
    # Act: создаём API-клиента
    response = admin_clients.create(factories.client_payload())
    # Assert: код создания, схема и наличие ключа
    with allure.step("Проверка: код создания, схема ClientCreatedOut, наличие api_key и client_id"):
        assert_status(response, *CREATED)
        body = assert_schema(response.json, ClientCreatedOut)
        assert body.api_key, "plaintext api_key must be returned exactly once on creation"
        assert body.client_id


@req("FR-I2", "NFR-7")
@allure.epic(EPIC_INTEGRATION)
@allure.feature("Управление API-клиентами")
@allure.story("Ключ выглядит как непрозрачный токен")
@allure.title("Создание клиента: api_key является непрозрачным строковым токеном (>= 16 символов)")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.positive
@pytest.mark.boundary
def test_create_client_key_looks_like_token(admin_clients):
    """Выданный api_key должен быть непрозрачным токеном (NFR-7): строка достаточной
    длины без раскрытия внутренней структуры, пригодная для использования как секрет."""
    # Act: создаём API-клиента
    response = admin_clients.create(factories.client_payload())
    # Assert: ключ — строка-токен достаточной длины
    with allure.step("Проверка: api_key — строка длиной не менее 16 символов (непрозрачный токен)"):
        assert_status(response, *CREATED)
        api_key = response.json["api_key"]
        assert isinstance(api_key, str) and len(api_key) >= 16, "api_key должен быть непрозрачным токеном"


@req("FR-I2", "INV-P8")
@allure.epic(EPIC_INTEGRATION)
@allure.feature("Управление API-клиентами")
@allure.story("Ключи разных клиентов различаются")
@allure.title("Создание двух клиентов: api_key и client_id уникальны для каждого")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.positive
def test_create_two_clients_keys_are_distinct(admin_clients):
    """Два независимо созданных клиента получают разные api_key и разные client_id
    (INV-P8): ключи не должны коллизировать или переиспользоваться между клиентами."""
    # Arrange/Act: создаём двух независимых клиентов
    first = admin_clients.create(factories.client_payload())
    second = admin_clients.create(factories.client_payload())
    # Assert: коды создания и уникальность ключей/идентификаторов
    with allure.step("Проверка: оба клиента созданы, их api_key и client_id попарно различаются"):
        assert_status(first, *CREATED)
        assert_status(second, *CREATED)
        assert first.json["api_key"] != second.json["api_key"], "ключи разных клиентов должны отличаться"
        assert first.json["client_id"] != second.json["client_id"]


@req("FR-I3")
@allure.epic(EPIC_INTEGRATION)
@allure.feature("Управление API-клиентами")
@allure.story("Деактивация клиента")
@allure.title("Деактивация клиента: запрос успешно завершается кодом 200")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.positive
def test_deactivate_client(admin_clients, active_client_key):
    """POST деактивации существующего активного клиента (FR-I3) должен успешно
    завершаться: клиент переводится в неактивное состояние."""
    # Act: деактивируем активного клиента по его client_id
    response = admin_clients.deactivate(active_client_key["client_id"])
    # Assert: код успешной деактивации
    with allure.step("Проверка: код ответа 200 (клиент деактивирован)"):
        assert_status(response, 200)


@req("FR-I2", "NFR-7")
@allure.epic(EPIC_INTEGRATION)
@allure.feature("Управление API-клиентами")
@allure.story("Ротация ключа")
@allure.title("Ротация ключа: выдаётся новый api_key, отличный от прежнего")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.positive
def test_rotate_client_key_issues_new_key(admin_clients, active_client_key):
    """Ротация ключа существующего клиента (NFR-7) единожды возвращает новый
    plaintext api_key, отличающийся от прежнего; ответ соответствует ClientCreatedOut."""
    # Act: запрашиваем ротацию ключа для активного клиента
    response = admin_clients.rotate_key(active_client_key["client_id"])
    # Assert: код, схема и факт смены ключа
    with allure.step("Проверка: код, схема ClientCreatedOut, новый api_key отличается от прежнего"):
        assert_status(response, *CREATED)
        rotated = assert_schema(response.json, ClientCreatedOut)
        assert rotated.api_key and rotated.api_key != active_client_key["api_key"], "ротация должна выдать новый ключ"
