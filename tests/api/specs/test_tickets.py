"""Specs for Module 2 — Tickets (EP-06..EP-11). Traceability: FR-T1..FR-T14, INV-P3..P7."""

from __future__ import annotations

import allure
import pytest

from tests.api.fixtures import factories
from tests.api.schemas.ticket import TicketOut, TicketStatsOut
from tests.api.utils.allure_meta import EPIC_TICKETS
from tests.api.utils.asserts import (
    assert_error_envelope,
    assert_not_success,
    assert_pagination,
    assert_schema,
    assert_status,
)
from tests.api.utils.markers import req

pytestmark = pytest.mark.tickets

CREATED = (200, 201)


def _make_employee(employees) -> int:
    response = employees.create(factories.employee_payload())
    assert_status(response, *CREATED)
    return response.json["id"]


def _move_to_in_progress(tickets, employees, ticket_id) -> int:
    assignee = _make_employee(employees)
    response = tickets.assign(ticket_id, {"assigned_to": assignee})
    assert_status(response, 200)
    return assignee


# -- create ----------------------------------------------------------------------------------
@req("FR-T1", "FR-T2", "INV-P3")
@allure.epic(EPIC_TICKETS)
@allure.feature("Создание заявки")
@allure.story("Новая заявка создаётся в статусе new")
@allure.title("Создание заявки: статус new, resolved_at пустой")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.positive
@pytest.mark.contract
def test_create_ticket_status_is_new(tickets, created_employee):
    """Свежесозданная заявка должна получить статус new и пустой resolved_at:
    это базовый инвариант жизненного цикла заявки (INV-P3)."""
    # Act: создаём заявку для существующего сотрудника
    response = tickets.create(factories.ticket_payload(employee_id=created_employee["id"]))
    # Assert: успешный код, валидная схема, статус new и пустой resolved_at
    with allure.step("Проверка: статус new и resolved_at = None"):
        assert_status(response, *CREATED)
        body = assert_schema(response.json, TicketOut)
        assert body.status == "new"
        assert body.resolved_at is None


@req("FR-T5", "INV-P4")
@allure.epic(EPIC_TICKETS)
@allure.feature("Создание заявки")
@allure.story("Заявку нельзя создать на несуществующего сотрудника")
@allure.title("Создание заявки на несуществующего сотрудника → ошибка")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.negative
@pytest.mark.contract
def test_create_ticket_nonexistent_employee(tickets):
    """Заявка должна ссылаться на реального сотрудника: при несуществующем employee_id
    сервис обязан отклонить запрос (NOT_FOUND или VALIDATION_ERROR), сохраняя
    целостность связи заявка↔сотрудник (INV-P4)."""
    # Act: пытаемся создать заявку с заведомо отсутствующим employee_id
    response = tickets.create(factories.ticket_payload(employee_id=999_999_999))
    # Assert: запрос не успешен и возвращён единый конверт ошибки
    with allure.step("Проверка: ошибка + NOT_FOUND / VALIDATION_ERROR"):
        assert_not_success(response)
        assert_error_envelope(response, "NOT_FOUND", "VALIDATION_ERROR")


@req("FR-T3")
@allure.epic(EPIC_TICKETS)
@allure.feature("Создание заявки")
@allure.story("Невалидный priority отклоняется")
@allure.title("Создание заявки с невалидным priority → 422 VALIDATION_ERROR")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.negative
def test_create_ticket_invalid_priority(tickets, created_employee):
    """Поле priority принимает только значения {low, medium, high, critical}:
    значение вне множества должно вызывать 422 с кодом VALIDATION_ERROR."""
    # Arrange: формируем корректный payload и подменяем priority на недопустимое значение
    payload = factories.ticket_payload(employee_id=created_employee["id"]).model_dump()
    payload["priority"] = "urgent"  # not in {low, medium, high, critical}
    # Act: отправляем заявку с невалидным priority
    response = tickets.create(payload)
    # Assert: код 422 и единый конверт ошибки валидации
    with allure.step("Проверка: 422 + VALIDATION_ERROR"):
        assert_status(response, 422)
        assert_error_envelope(response, "VALIDATION_ERROR")


# -- get -------------------------------------------------------------------------------------
@req("FR-T7")
@allure.epic(EPIC_TICKETS)
@allure.feature("Список, фильтры и пагинация")
@allure.story("Получение заявки по идентификатору")
@allure.title("Получение заявки по id → 200 и валидная схема")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.positive
@pytest.mark.contract
def test_get_ticket_by_id(tickets, new_ticket):
    """Существующую заявку можно получить по её id: сервис возвращает 200
    и тело, соответствующее контрактной схеме TicketOut."""
    # Act: запрашиваем ранее созданную заявку по id
    response = tickets.get(new_ticket["id"])
    # Assert: код 200 и валидная схема ответа
    with allure.step("Проверка: 200 и схема TicketOut"):
        assert_status(response, 200)
        assert_schema(response.json, TicketOut)


@req("FR-T7", "NFR-2")
@allure.epic(EPIC_TICKETS)
@allure.feature("Список, фильтры и пагинация")
@allure.story("Запрос несуществующей заявки")
@allure.title("Получение несуществующей заявки → 404 NOT_FOUND")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.negative
@pytest.mark.contract
def test_get_ticket_not_found(tickets):
    """Запрос заявки с несуществующим id должен возвращать 404 с кодом NOT_FOUND,
    а не 500 или пустой успех (NFR-2)."""
    # Act: запрашиваем заведомо отсутствующую заявку
    response = tickets.get(999_999_999)
    # Assert: код 404 и единый конверт ошибки
    with allure.step("Проверка: 404 + NOT_FOUND"):
        assert_status(response, 404)
        assert_error_envelope(response, "NOT_FOUND")


# -- assign ----------------------------------------------------------------------------------
@req("FR-T8", "FR-T9", "INV-P6")
@allure.epic(EPIC_TICKETS)
@allure.feature("Назначение исполнителя")
@allure.story("Назначение исполнителя переводит заявку в in_progress")
@allure.title("Назначение исполнителя → статус in_progress")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.positive
@pytest.mark.contract
def test_assign_sets_in_progress(tickets, employees, new_ticket):
    """Назначение исполнителя на заявку в статусе new должно проставить assigned_to
    и автоматически перевести заявку в статус in_progress (INV-P6)."""
    # Arrange: создаём сотрудника-исполнителя
    assignee = _make_employee(employees)
    # Act: назначаем исполнителя на заявку
    response = tickets.assign(new_ticket["id"], {"assigned_to": assignee})
    # Assert: код 200, валидная схема, проставлен исполнитель и статус in_progress
    with allure.step("Проверка: 200, assigned_to и статус in_progress"):
        assert_status(response, 200)
        body = assert_schema(response.json, TicketOut)
        assert body.assigned_to == assignee
        assert body.status == "in_progress"


@req("FR-T8", "INV-P4")
@allure.epic(EPIC_TICKETS)
@allure.feature("Назначение исполнителя")
@allure.story("Назначение на несуществующего сотрудника отклоняется")
@allure.title("Назначение на несуществующего исполнителя → ошибка")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.negative
@pytest.mark.contract
def test_assign_nonexistent_assignee(tickets, new_ticket):
    """Исполнителем можно назначить только реального сотрудника: при несуществующем
    assigned_to сервис обязан отклонить запрос (NOT_FOUND или VALIDATION_ERROR),
    сохраняя целостность связи заявка↔сотрудник (INV-P4)."""
    # Act: пытаемся назначить заведомо отсутствующего исполнителя
    response = tickets.assign(new_ticket["id"], {"assigned_to": 999_999_999})
    # Assert: запрос не успешен и возвращён единый конверт ошибки
    with allure.step("Проверка: ошибка + NOT_FOUND / VALIDATION_ERROR"):
        assert_not_success(response)
        assert_error_envelope(response, "NOT_FOUND", "VALIDATION_ERROR")


# -- status transitions ----------------------------------------------------------------------
@req("FR-T10", "FR-T11", "INV-P5")
@allure.epic(EPIC_TICKETS)
@allure.feature("Машина статусов")
@allure.story("Прямой переход new → rejected разрешён")
@allure.title("Смена статуса: new → rejected → 200")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.positive
def test_status_transition_new_to_rejected(tickets, new_ticket):
    """Заявку в статусе new допустимо сразу отклонить (перевести в rejected):
    это разрешённый переход машины статусов (INV-P5)."""
    # Act: переводим заявку из new в rejected
    response = tickets.set_status(new_ticket["id"], {"status": "rejected"})
    # Assert: код 200 и итоговый статус rejected
    with allure.step("Проверка: 200 и статус rejected"):
        assert_status(response, 200)
        assert response.json.get("status") == "rejected"


@req("FR-T11", "FR-T12", "INV-P7")
@allure.epic(EPIC_TICKETS)
@allure.feature("Машина статусов")
@allure.story("Перевод в resolved заполняет resolved_at")
@allure.title("Смена статуса: in_progress → resolved заполняет resolved_at")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.positive
@pytest.mark.contract
def test_resolve_sets_resolved_at(tickets, employees, new_ticket):
    """При переводе заявки в resolved сервис обязан зафиксировать момент решения
    в поле resolved_at: оно не может оставаться пустым (INV-P7)."""
    # Arrange: переводим заявку в in_progress (назначаем исполнителя)
    _move_to_in_progress(tickets, employees, new_ticket["id"])
    # Act: переводим заявку в resolved
    response = tickets.set_status(new_ticket["id"], {"status": "resolved"})
    # Assert: код 200, статус resolved и заполненный resolved_at
    with allure.step("Проверка: 200, статус resolved и заполненный resolved_at"):
        assert_status(response, 200)
        body = assert_schema(response.json, TicketOut)
        assert body.status == "resolved"
        assert body.resolved_at is not None, "resolved_at must be filled on resolve (INV-P7)"


@req("FR-T11", "INV-P5")
@allure.epic(EPIC_TICKETS)
@allure.feature("Машина статусов")
@allure.story("Прямой переход new → resolved запрещён")
@allure.title("Смена статуса: new → resolved → 409 INVALID_STATUS_TRANSITION")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.negative
@pytest.mark.contract
def test_status_transition_forbidden_new_to_resolved(tickets, new_ticket):
    """Заявку в статусе new нельзя сразу перевести в resolved (минуя in_progress):
    сервис обязан вернуть 409 с кодом INVALID_STATUS_TRANSITION (INV-P5)."""
    # Act: пытаемся выполнить запрещённый переход new → resolved
    response = tickets.set_status(new_ticket["id"], {"status": "resolved"})
    # Assert: код 409 и единый конверт ошибки
    with allure.step("Проверка: 409 + INVALID_STATUS_TRANSITION"):
        assert_status(response, 409)
        assert_error_envelope(response, "INVALID_STATUS_TRANSITION")


@req("FR-T11", "INV-P5")
@allure.epic(EPIC_TICKETS)
@allure.feature("Машина статусов")
@allure.story("Терминальный статус нельзя изменить")
@allure.title("Смена статуса из терминального resolved → 409 INVALID_STATUS_TRANSITION")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.negative
@pytest.mark.contract
def test_terminal_status_cannot_change(tickets, employees, new_ticket):
    """Статус resolved является терминальным: после перехода в него любая дальнейшая
    смена статуса должна отклоняться кодом 409 INVALID_STATUS_TRANSITION (INV-P5)."""
    # Arrange: доводим заявку до терминального статуса resolved (через in_progress)
    _move_to_in_progress(tickets, employees, new_ticket["id"])
    assert_status(tickets.set_status(new_ticket["id"], {"status": "resolved"}), 200)
    # Act: пытаемся сменить статус терминальной заявки resolved → in_progress
    # resolved is terminal — any further transition is rejected.
    response = tickets.set_status(new_ticket["id"], {"status": "in_progress"})
    # Assert: код 409 и единый конверт ошибки
    with allure.step("Проверка: 409 + INVALID_STATUS_TRANSITION"):
        assert_status(response, 409)
        assert_error_envelope(response, "INVALID_STATUS_TRANSITION")


@req("FR-T4")
@allure.epic(EPIC_TICKETS)
@allure.feature("Машина статусов")
@allure.story("Невалидное значение статуса отклоняется")
@allure.title("Смена статуса на невалидное значение → 422 VALIDATION_ERROR")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.negative
def test_status_transition_invalid_value(tickets, new_ticket):
    """Поле status принимает только значения из множества допустимых статусов:
    неизвестное значение (например, "done") должно вызывать 422 VALIDATION_ERROR."""
    # Act: пытаемся выставить несуществующий статус
    response = tickets.set_status(new_ticket["id"], {"status": "done"})
    # Assert: код 422 и единый конверт ошибки валидации
    with allure.step("Проверка: 422 + VALIDATION_ERROR"):
        assert_status(response, 422)
        assert_error_envelope(response, "VALIDATION_ERROR")


# -- list / filter / pagination --------------------------------------------------------------
@req("FR-T6")
@allure.epic(EPIC_TICKETS)
@allure.feature("Список, фильтры и пагинация")
@allure.story("Фильтр списка по статусу new")
@allure.title("Список заявок с фильтром status=new → только new")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.positive
def test_list_tickets_filter_status_new(tickets, new_ticket):
    """Фильтр по статусу должен возвращать только заявки с запрошенным статусом:
    при status=new все элементы выборки обязаны иметь статус new (FR-T6)."""
    # Act: запрашиваем список заявок с фильтром по статусу new
    response = tickets.list(status="new", limit=100)
    # Assert: код 200, валидная пагинация и все элементы в статусе new
    with allure.step("Проверка: 200 и все элементы со статусом new"):
        assert_status(response, 200)
        items = assert_pagination(response.json, limit=100)
        assert all(item.get("status") == "new" for item in items)


@req("FR-T6")
@allure.epic(EPIC_TICKETS)
@allure.feature("Список, фильтры и пагинация")
@allure.story("Фильтр списка по приоритету critical")
@allure.title("Список заявок с фильтром priority=critical → только critical")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.positive
def test_list_tickets_filter_priority(tickets, created_employee):
    """Фильтр по приоритету должен возвращать только заявки с запрошенным priority:
    при priority=critical все элементы выборки обязаны иметь приоритет critical (FR-T6)."""
    # Arrange: создаём заявку с приоритетом critical, чтобы выборка была непустой
    payload = factories.ticket_payload(employee_id=created_employee["id"], priority="critical")
    assert_status(tickets.create(payload), *CREATED)
    # Act: запрашиваем список заявок с фильтром по приоритету critical
    response = tickets.list(priority="critical", limit=100)
    # Assert: код 200, валидная пагинация и все элементы с приоритетом critical
    with allure.step("Проверка: 200 и все элементы с приоритетом critical"):
        assert_status(response, 200)
        items = assert_pagination(response.json, limit=100)
        assert all(item.get("priority") == "critical" for item in items)


@req("FR-T14")
@allure.epic(EPIC_TICKETS)
@allure.feature("Список, фильтры и пагинация")
@allure.story("Постраничная выдача списка заявок")
@allure.title("Список заявок с пагинацией page=1, limit=1")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.positive
@pytest.mark.boundary
def test_list_tickets_pagination(tickets, created_employee):
    """Список заявок должен поддерживать постраничную выдачу: при limit=1 ответ
    обязан содержать корректные метаданные пагинации (FR-T14)."""
    # Arrange: создаём несколько заявок, чтобы было что разбивать на страницы
    for _ in range(2):
        assert_status(tickets.create(factories.ticket_payload(employee_id=created_employee["id"])), *CREATED)
    # Act: запрашиваем первую страницу с размером 1
    response = tickets.list(page=1, limit=1)
    # Assert: код 200 и корректная пагинация при limit=1
    with allure.step("Проверка: 200 и корректная пагинация (limit=1)"):
        assert_status(response, 200)
        assert_pagination(response.json, limit=1)


# -- stats -----------------------------------------------------------------------------------
@req("FR-T13")
@allure.epic(EPIC_TICKETS)
@allure.feature("Статистика")
@allure.story("Контракт сводной статистики по заявкам")
@allure.title("Статистика заявок: сумма по статусам равна total")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.positive
@pytest.mark.contract
def test_tickets_stats_contract(tickets):
    """Сводная статистика должна быть согласованной: сумма счётчиков по статусам
    (new + in_progress + resolved + rejected) равна total, а critical_opened
    неотрицателен (FR-T13)."""
    # Act: запрашиваем сводную статистику по заявкам
    response = tickets.stats()
    # Assert: код 200, валидная схема и согласованность счётчиков
    with allure.step("Проверка: 200, схема и сумма по статусам == total"):
        assert_status(response, 200)
        stats = assert_schema(response.json, TicketStatsOut)
        assert stats.new + stats.in_progress + stats.resolved + stats.rejected == stats.total, (
            "sum of per-status counts must equal total"
        )
        assert stats.critical_opened >= 0
