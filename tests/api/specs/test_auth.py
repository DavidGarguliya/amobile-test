"""Specs for admin authn/authz (ADR-009). Traceability: NFR-7, Q-4."""

from __future__ import annotations

import allure
import pytest

from tests.api.fixtures import factories
from tests.api.utils.allure_meta import EPIC_SECURITY
from tests.api.utils.asserts import assert_error_envelope, assert_status
from tests.api.utils.markers import req

pytestmark = pytest.mark.auth


@req("NFR-7")
@allure.epic(EPIC_SECURITY)
@allure.feature("Аутентификация (JWT)")
@allure.story("Успешный вход администратора")
@allure.title("Успешный логин администратора → 200 + access_token и роль admin")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.positive
def test_login_success(auth, settings):
    """Администратор с корректными учётными данными должен успешно проходить аутентификацию:
    сервер возвращает код 200, JWT access_token и роль ``admin`` (ADR-009)."""
    # Act: логин с валидными учётными данными администратора
    response = auth.login(settings.admin_email, settings.admin_password)
    # Assert: 200, наличие токена и корректная роль
    with allure.step("Проверка: 200 + access_token + роль admin"):
        assert_status(response, 200)
        assert response.json.get("access_token"), "login must return an access token"
        assert response.json.get("role") == "admin"


@req("NFR-7")
@allure.epic(EPIC_SECURITY)
@allure.feature("Аутентификация (JWT)")
@allure.story("Отказ при неверном пароле")
@allure.title("Логин с неверным паролем → 401 UNAUTHORIZED")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.negative
@pytest.mark.contract
def test_login_wrong_password(auth, settings):
    """Попытка входа с правильным email, но неверным паролем должна отклоняться
    с кодом 401 и единым конвертом ошибки UNAUTHORIZED (ADR-009)."""
    # Act: логин с заведомо неверным паролем
    response = auth.login(settings.admin_email, "definitely-wrong-password")
    # Assert: 401 и конверт ошибки
    with allure.step("Проверка: 401 + UNAUTHORIZED"):
        assert_status(response, 401)
        assert_error_envelope(response, "UNAUTHORIZED")


@req("NFR-7", "Q-4")
@allure.epic(EPIC_SECURITY)
@allure.feature("Авторизация (RBAC)")
@allure.story("Защищённый эндпоинт требует токен")
@allure.title("Доступ без токена к /api/employees → 401 UNAUTHORIZED")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.negative
@pytest.mark.contract
def test_protected_endpoint_requires_token(anon_client):
    """Обращение к защищённому эндпоинту без заголовка Authorization должно отклоняться
    с кодом 401 и единым конвертом ошибки UNAUTHORIZED (ADR-009)."""
    # Act: запрос без токена
    response = anon_client.get("/api/employees")
    # Assert: 401 и конверт ошибки
    with allure.step("Проверка: 401 + UNAUTHORIZED"):
        assert_status(response, 401)
        assert_error_envelope(response, "UNAUTHORIZED")


@req("NFR-7", "Q-4")
@allure.epic(EPIC_SECURITY)
@allure.feature("Авторизация (RBAC)")
@allure.story("Недостаточная роль на запись")
@allure.title("Запись viewer-ом в /api/employees → 403 FORBIDDEN")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.negative
@pytest.mark.contract
def test_insufficient_role_forbidden(auth, admin_token, anon_client):
    """Пользователь с ролью ``viewer`` может читать, но не имеет прав на запись.
    Попытка создать сотрудника должна отклоняться с кодом 403 и конвертом ошибки
    FORBIDDEN — именно из-за роли, а не из-за отсутствия аутентификации (ADR-009)."""
    # Arrange: администратор создаёт пользователя-viewer и тот логинится за своим токеном
    email = factories.unique_email("viewer")
    created = auth.create_user(
        {"email": email, "password": "viewerpass123", "role": "viewer"}, token=admin_token
    )
    assert_status(created, 201)
    login = auth.login(email, "viewerpass123")
    assert_status(login, 200)
    viewer_token = login.json["access_token"]
    # Act: viewer пытается выполнить запись
    response = anon_client.post(
        "/api/employees",
        json=factories.employee_payload().model_dump(),
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    # Assert: запрещено по роли (403 FORBIDDEN), а не 401
    with allure.step("Проверка: 403 + FORBIDDEN"):
        assert_status(response, 403)
        assert_error_envelope(response, "FORBIDDEN")
