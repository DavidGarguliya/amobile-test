# ADR-005: Машина состояний статусов заявки

## Status
Accepted

## Context
Бриф §3.6 задаёт жёсткие правила перехода статусов; §3.5 — побочные эффекты назначения и закрытия.
Требования FR-T9, FR-T11, FR-T12; инварианты INV-P5, INV-P6, INV-P7.

## Decision
Заявка моделируется явной машиной состояний:

```
new ──assign──▶ in_progress
new ──status:in_progress──▶ in_progress
new ──status:rejected──▶ rejected
in_progress ──status:resolved──▶ resolved   (set resolved_at)
in_progress ──status:rejected──▶ rejected
resolved ─▶ (terminal)
rejected ─▶ (terminal)
```

- Создание → всегда `new` (INV-P3).
- `PATCH .../assign` устанавливает assigned_to и переводит new→in_progress (INV-P6).
- `PATCH .../status` разрешает только переходы из таблицы; иначе 409 `INVALID_STATUS_TRANSITION`.
- Переход в `resolved` обязан проставить resolved_at (INV-P7).
- Переходы из resolved/rejected запрещены (терминальность).

Граф переходов кодируется как данные (таблица разрешённых пар), а не как разбросанные `if`.

## Consequences
### Positive
- Централизованная таблица переходов = единая точка истины, легко тестируется (AC-T6..T8).
- Невозможны несогласованные состояния (resolved без resolved_at).
### Negative
- Добавление статусов требует обновления таблицы и тестов — приемлемо.

## Alternatives considered
### Свободная смена статуса с проверками на местах
Отклонено: размазанная логика нарушает INV-X3 и легко расходится с §3.6.

---

*Graph: [[AGENT_CONTEXT]] · [[INVARIANTS]] · [[REQUIREMENTS]] · [[TEST_PLAN]]*
