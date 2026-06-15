"""Specs for Module 1 — Employees (EP-01..EP-05). Traceability: FR-E1..FR-E10.

Structure: Arrange-Act-Assert. HTTP is reached only through the EmployeesClient service object.
"""

from __future__ import annotations

import allure
import pytest

from tests.api.fixtures import factories
from tests.api.schemas.employee import EmployeeOut
from tests.api.utils.allure_meta import EPIC_EMPLOYEES
from tests.api.utils.asserts import (
    assert_error_envelope,
    assert_not_success,
    assert_pagination,
    assert_schema,
    assert_status,
)
from tests.api.utils.markers import req

pytestmark = pytest.mark.employees

CREATED = (200, 201)
REQUIRED_FIELDS = ["full_name", "position", "department", "phone", "email"]


# -- positive / contract ---------------------------------------------------------------------
@req("FR-E1", "FR-E10", "INV-D1")
@allure.epic(EPIC_EMPLOYEES)
@allure.feature("Создание сотрудника")
@allure.story("Успешное создание возвращает 201 и корректную сущность")
@allure.title("Создание сотрудника: 201 + контракт EmployeeOut + Location")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.positive
@pytest.mark.contract
def test_create_employee_returns_created(employees):
    """Валидный POST /api/employees создаёт активного сотрудника: 201, схема EmployeeOut,
    is_active=true и заголовок Location, указывающий на новый ресурс."""
    # Arrange: уникальное тело сотрудника
    payload = factories.employee_payload()
    # Act: создаём сотрудника
    response = employees.create(payload)
    # Assert: код, схема и инварианты
    with allure.step("Проверка: код 201, схема EmployeeOut, is_active=true, Location"):
        assert_status(response, *CREATED)
        body = assert_schema(response.json, EmployeeOut)
        assert body.is_active is True
        assert body.email == payload.email
        # REST best practice: 201 carries a Location header pointing at the new resource.
        assert response.headers.get("Location", "").endswith(f"/api/employees/{body.id}")


@req("FR-E10")
@allure.epic(EPIC_EMPLOYEES)
@allure.feature("Создание сотрудника")
@allure.story("Серверные временные метки проставляются при создании")
@allure.title("Создание сотрудника: created_at и updated_at заполнены")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.positive
def test_create_employee_has_timestamps(employees):
    """При создании сотрудника сервер обязан проставить временные метки created_at и updated_at."""
    # Arrange: валидное тело сотрудника
    payload = factories.employee_payload()
    # Act: создаём сотрудника
    response = employees.create(payload)
    # Assert: код успеха и наличие обеих временных меток
    with allure.step("Проверка: код 2xx, created_at и updated_at заданы"):
        assert_status(response, *CREATED)
        assert response.json.get("created_at"), "created_at must be set on creation"
        assert response.json.get("updated_at"), "updated_at must be set on creation"


# -- negative: validation --------------------------------------------------------------------
@req("FR-E2", "NFR-2")
@allure.epic(EPIC_EMPLOYEES)
@allure.feature("Создание сотрудника")
@allure.story("Отсутствие обязательного поля приводит к ошибке валидации")
@allure.title("Создание без обязательного поля {missing} → 422")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.negative
@pytest.mark.contract
@pytest.mark.parametrize("missing", REQUIRED_FIELDS)
def test_create_employee_missing_required_field(employees, missing):
    """Если в теле запроса отсутствует обязательное поле, сервер отвечает 422
    с унифицированным конвертом ошибки VALIDATION_ERROR."""
    # Arrange: валидное тело без одного обязательного поля
    payload = factories.employee_payload().model_dump()
    payload.pop(missing)
    # Act: пытаемся создать сотрудника с неполным телом
    response = employees.create(payload)
    # Assert: код 422 и конверт ошибки валидации
    with allure.step("Проверка: код 422 и конверт VALIDATION_ERROR"):
        assert_status(response, 422)
        assert_error_envelope(response, "VALIDATION_ERROR")


@req("FR-E3", "INV-P2")
@allure.epic(EPIC_EMPLOYEES)
@allure.feature("Создание сотрудника")
@allure.story("Уникальность email: повторный email приводит к конфликту 409")
@allure.title("Создание с дублирующимся email → 409 CONFLICT")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.negative
@pytest.mark.contract
def test_create_employee_duplicate_email(employees):
    """Инвариант уникальности email (INV-P2): повторное создание сотрудника с тем же email
    отклоняется кодом 409 CONFLICT и унифицированным конвертом ошибки."""
    # Arrange: создаём первого сотрудника и готовим дубль с тем же email
    first = factories.employee_payload()
    assert_status(employees.create(first), *CREATED)
    # Arrange: a second employee reusing the same email
    duplicate = factories.employee_payload().model_dump()
    duplicate["email"] = first.email
    # Act: пытаемся создать второго сотрудника с дублирующимся email
    response = employees.create(duplicate)
    # Assert: uniqueness conflict → 409 CONFLICT (Q-7), unified envelope.
    with allure.step("Проверка: код 409 и конверт CONFLICT"):
        assert_status(response, 409)
        assert_error_envelope(response, "CONFLICT")


@req("FR-E2")
@allure.epic(EPIC_EMPLOYEES)
@allure.feature("Создание сотрудника")
@allure.story("Некорректный формат email приводит к ошибке валидации")
@allure.title("Создание с невалидным форматом email → 422")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.negative
def test_create_employee_invalid_email_format(employees):
    """Email с некорректным форматом отклоняется на этапе валидации: 422 и конверт
    VALIDATION_ERROR."""
    # Arrange: валидное тело с заведомо некорректным email
    payload = factories.employee_payload().model_dump()
    payload["email"] = "not-an-email"
    # Act: пытаемся создать сотрудника с невалидным email
    response = employees.create(payload)
    # Assert: код 422 и конверт ошибки валидации
    with allure.step("Проверка: код 422 и конверт VALIDATION_ERROR"):
        assert_status(response, 422)
        assert_error_envelope(response, "VALIDATION_ERROR")


# -- list / filter / search / pagination -----------------------------------------------------
@req("FR-E5")
@allure.epic(EPIC_EMPLOYEES)
@allure.feature("Список, фильтры и поиск")
@allure.story("Пагинация ограничивает размер страницы параметром limit")
@allure.title("Список сотрудников: пагинация page=1, limit=1")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.positive
@pytest.mark.boundary
def test_list_employees_pagination(employees):
    """Список сотрудников поддерживает пагинацию: при limit=1 страница содержит не более
    одного элемента и корректные метаданные пагинации."""
    # Arrange: создаём минимум два сотрудника, чтобы было что пагинировать
    for _ in range(2):
        assert_status(employees.create(factories.employee_payload()), *CREATED)
    # Act: запрашиваем первую страницу с лимитом в один элемент
    response = employees.list(page=1, limit=1)
    # Assert: код 200 и корректная пагинация
    with allure.step("Проверка: код 200 и пагинация с limit=1"):
        assert_status(response, 200)
        assert_pagination(response.json, limit=1)


@req("FR-E4")
@allure.epic(EPIC_EMPLOYEES)
@allure.feature("Список, фильтры и поиск")
@allure.story("Фильтрация списка по департаменту")
@allure.title("Список сотрудников: фильтр по department")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.positive
def test_list_employees_filter_department(employees):
    """Фильтр по департаменту возвращает только сотрудников этого департамента: созданный
    сотрудник присутствует в выдаче при фильтрации по его department."""
    # Arrange: создаём сотрудника с уникальным департаментом
    department = f"DEPT-{factories.unique_suffix()}"
    created = employees.create(factories.employee_payload(department=department))
    assert_status(created, *CREATED)
    # Act: запрашиваем список с фильтром по этому департаменту
    response = employees.list(department=department, limit=50)
    # Assert: код 200, корректная пагинация и наличие созданного сотрудника
    with allure.step("Проверка: код 200 и сотрудник присутствует в отфильтрованной выдаче"):
        assert_status(response, 200)
        items = assert_pagination(response.json, limit=50)
        assert any(item.get("department") == department for item in items)


@req("FR-E4")
@allure.epic(EPIC_EMPLOYEES)
@allure.feature("Список, фильтры и поиск")
@allure.story("Фильтр is_active исключает деактивированных сотрудников")
@allure.title("Список сотрудников: is_active=true исключает деактивированного")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.positive
def test_list_employees_filter_is_active_excludes_deactivated(employees):
    """Фильтр is_active=true не возвращает деактивированных сотрудников: после деактивации
    сотрудник отсутствует в выдаче активных."""
    # Arrange: создаём сотрудника и деактивируем его
    created = employees.create(factories.employee_payload())
    assert_status(created, *CREATED)
    employee_id = created.json["id"]
    assert_status(employees.deactivate(employee_id), 200)
    # Act: запрашиваем список только активных сотрудников
    response = employees.list(is_active=True, limit=100)
    # Assert: код 200 и отсутствие деактивированного сотрудника в выдаче
    with allure.step("Проверка: код 200 и деактивированный сотрудник отфильтрован"):
        assert_status(response, 200)
        items = assert_pagination(response.json, limit=100)
        assert all(item.get("id") != employee_id for item in items), "deactivated employee must be filtered out"


@req("FR-E6")
@allure.epic(EPIC_EMPLOYEES)
@allure.feature("Список, фильтры и поиск")
@allure.story("Полнотекстовый поиск по разным полям сотрудника")
@allure.title("Поиск сотрудников по полю {field}")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.positive
@pytest.mark.parametrize("field", ["full_name", "email", "position"])
def test_search_employees_by_field(employees, field):
    """Поиск по подстроке находит сотрудника независимо от поля (full_name, email, position):
    созданный с уникальным токеном сотрудник присутствует в результатах поиска."""
    # Arrange: создаём сотрудника с уникальным токеном в проверяемом поле
    token = factories.unique_suffix()
    overrides = {field: f"Searchable {token}" if field != "email" else f"search.{token}@example.com"}
    created = employees.create(factories.employee_payload(**overrides))
    assert_status(created, *CREATED)
    # Act: выполняем поиск по уникальному токену
    response = employees.list(search=token, limit=50)
    # Assert: код 200 и наличие созданного сотрудника в результатах поиска
    with allure.step("Проверка: код 200 и сотрудник найден поиском"):
        assert_status(response, 200)
        items = assert_pagination(response.json, limit=50)
        assert any(item.get("id") == created.json["id"] for item in items), f"search by {field} must match"


# -- get by id -------------------------------------------------------------------------------
@req("FR-E7")
@allure.epic(EPIC_EMPLOYEES)
@allure.feature("Получение по ID")
@allure.story("Получение существующего сотрудника по идентификатору")
@allure.title("Получение сотрудника по ID: 200 + контракт EmployeeOut")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.positive
@pytest.mark.contract
def test_get_employee_by_id(employees, created_employee):
    """GET /api/employees/{id} для существующего сотрудника возвращает 200 и тело,
    соответствующее схеме EmployeeOut."""
    # Arrange: используем заранее созданного сотрудника из фикстуры
    # Act: запрашиваем сотрудника по его идентификатору
    response = employees.get(created_employee["id"])
    # Assert: код 200 и соответствие контракту EmployeeOut
    with allure.step("Проверка: код 200 и схема EmployeeOut"):
        assert_status(response, 200)
        assert_schema(response.json, EmployeeOut)


@req("FR-E7", "NFR-2")
@allure.epic(EPIC_EMPLOYEES)
@allure.feature("Получение по ID")
@allure.story("Запрос несуществующего сотрудника возвращает 404")
@allure.title("Получение несуществующего сотрудника → 404 NOT_FOUND")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.negative
@pytest.mark.contract
def test_get_employee_not_found(employees):
    """GET по заведомо несуществующему ID возвращает 404 с унифицированным конвертом
    ошибки NOT_FOUND."""
    # Arrange: заведомо несуществующий идентификатор
    missing_id = 999_999_999
    # Act: запрашиваем несуществующего сотрудника
    response = employees.get(missing_id)
    # Assert: код 404 и конверт ошибки NOT_FOUND
    with allure.step("Проверка: код 404 и конверт NOT_FOUND"):
        assert_status(response, 404)
        assert_error_envelope(response, "NOT_FOUND")


# -- update ----------------------------------------------------------------------------------
@req("FR-E8", "INV-D1")
@allure.epic(EPIC_EMPLOYEES)
@allure.feature("Обновление")
@allure.story("Обновление полей сотрудника отражается в ответе")
@allure.title("Обновление сотрудника: изменение position → 200 + контракт")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.positive
@pytest.mark.contract
def test_update_employee_changes_fields(employees, created_employee):
    """PATCH/PUT сотрудника обновляет переданные поля: новое значение position возвращается
    в ответе, тело соответствует схеме EmployeeOut."""
    # Arrange: новое уникальное значение должности
    new_position = f"Lead {factories.unique_suffix()}"
    # Act: обновляем должность сотрудника
    response = employees.update(created_employee["id"], {"position": new_position})
    # Assert: код 200, контракт EmployeeOut и применённое изменение
    with allure.step("Проверка: код 200, схема EmployeeOut и новое значение position"):
        assert_status(response, 200)
        body = assert_schema(response.json, EmployeeOut)
        assert body.position == new_position


# -- deactivate (soft delete) ----------------------------------------------------------------
@req("FR-E9", "INV-P1")
@allure.epic(EPIC_EMPLOYEES)
@allure.feature("Деактивация (мягкое удаление)")
@allure.story("Деактивация переводит сотрудника в is_active=false без физического удаления")
@allure.title("Деактивация сотрудника: мягкое удаление сохраняет запись")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.positive
@pytest.mark.contract
def test_deactivate_employee_keeps_record(employees, created_employee):
    """Инвариант запрета физического удаления (INV-P1): деактивация переводит сотрудника
    в is_active=false, но запись остаётся доступной для чтения."""
    # Arrange: используем заранее созданного сотрудника из фикстуры
    employee_id = created_employee["id"]
    # Act: deactivate
    deactivated = employees.deactivate(employee_id)
    # Assert: запись не удалена физически — деактивирована и по-прежнему читается
    with allure.step("Проверка: деактивация (is_active=false) и запись остаётся доступной"):
        assert_status(deactivated, 200)
        assert deactivated.json.get("is_active") is False
        # Assert: record is NOT physically deleted — still readable.
        fetched = employees.get(employee_id)
        assert_status(fetched, 200)
        assert fetched.json.get("is_active") is False
