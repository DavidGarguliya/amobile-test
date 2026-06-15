# AGENTS.md — AI Engineering Operating Contract

> Mandatory execution rules for AI coding agents in this repository. Treat as rules, not docs.
> Branching/merge/rollback policy is canonical in `docs/PROCESS/BRANCHING_AND_RELEASE.md`.

## 0. First action (every session)

Before anything else, **read `docs/AGENT_CONTEXT.md`** (the graph hub / always-current snapshot).
Open individual docs only when AGENT_CONTEXT is insufficient. Корневой `CLAUDE.md` требует
читать этот файл первым — это согласовано: `CLAUDE.md → AGENTS.md → docs/AGENT_CONTEXT.md`.

## 1. Authority order (on conflict, higher wins)

1. `docs/ARCHITECTURE/INVARIANTS.md`
2. `docs/ARCHITECTURE/FINAL_SYSTEM_SPEC.md`
3. `docs/ARCHITECTURE/ADR/*`
4. `docs/PRODUCT/*`
5. `docs/QA/TEST_PLAN.md`
6. `docs/OPERATIONS/RUNBOOK.md`
7. `docs/PROCESS/STATE.md`

`AGENT_DECISIONS.md` — комплементарный legacy-журнал решений; при расхождении приоритет имеет
дерево `docs/ARCHITECTURE/` выше.

## 2. Execution protocol (6 steps)

1. **Freeze** — зафиксировать задачу и затрагиваемые требования (FR/NFR) и инварианты; прочитать
   релевантные доки (authority order). Никакого кода до ясности границ и владения состоянием.
2. **Model** — описать модель изменения: компоненты, потоки данных, контракты, влияние на инварианты.
3. **Proof** — спроектировать проверки: какие тест-кейсы из [[TEST_PLAN]] подтверждают изменение
   (позитив + негатив + контракт). Для нового поведения — добавить кейсы и строку в матрицу.
4. **Implement** — минимальное безопасное изменение в нужном слое; без побочных рефакторингов.
5. **Verify** — прогнать гейты (`pytest`, как минимум `pytest --collect-only` для типа B), линт;
   не ослаблять ассерты ради зелёного.
6. **Closeout** — обновить STATE/CHRONICLE/AGENT_CONTEXT, память, матрицу; собрать PR (см. §6).

## 3. Hard rules (из инвариантов и ограничений)

- Single source of truth для состояния; никаких скрытых хранилищ/кэшей (INV-D*, INV-X*).
- Все ошибки — единым конвертом `{error,code,message,details}` с кодом из разрешённого набора (INV-X1/X2).
- Обработка ошибок централизована (INV-X3). HTTP в тестах — только через client-слой (INV-X4).
- Никаких хардкод-секретов; конфиг/секреты — из окружения (INV-X5).
- Сотрудник не удаляется физически (INV-P1). Email уникален (INV-P2). Новая заявка = `new` (INV-P3).
- Переходы статусов — только по графу; resolved/rejected терминальны; resolved ⇒ resolved_at (INV-P5/P7).
- API-ключ — только хешем, показ один раз; 401/403/429; аудит каждой попытки (INV-P8/P9/P10).
- processed нельзя обработать повторно (INV-P11). Детерминизм тестов, без flaky (INV-O2).
- `main` зелёная; изменения через PR + squash; **force-push запрещён** (INV-O3).
- Неоднозначность → явный `[ASSUMPTION]`/`[OPEN QUESTION]`, не молчаливая подмена данных.

## 4. Mandatory agent behavior

Перед изменениями: прочитать затрагиваемые файлы, понять паттерны, сохранить инварианты, не плодить
новые паттерны без необходимости. Не рефакторить несвязанное, не менять публичные контракты молча,
не трогать CI/build без нужды.

## 5. Commit discipline

Атомарный коммит на смысловой слой. Типы коммитов выведены из слоёв проекта:
`docs(architecture|product|process|qa)`, `chore(repo|memory|ci)`, `feat(employees|tickets|integration)`,
`fix(...)`, **`test(api)`** (обязательный слой тест-контура). Сообщения коммитов завершать строкой:

```text
Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

## 6. PR-ready output (Definition of Done)

После прохождения гейтов слайса собрать PR по `.github/pull_request_template.md` (канон —
[[PR_GENERATION]]): Summary, Files changed, ADR references, Invariants preserved, Traceability
(FR/NFR→тесты), Test results (`pytest`), Data/Env impact, Risks/follow-ups, Rollback plan.
Только верифицируемые факты; неприменимый раздел → `N/A` с причиной.

## 7. Task closeout checklist (задача закрыта только когда всё выполнено)

- [ ] перечислены изменённые файлы
- [ ] указан затронутый инвариант/правило
- [ ] добавлены/обновлены тесты (включая покрытие новых требований)
- [ ] обновлена матрица трассируемости требование→тест ([[TEST_PLAN]])
- [ ] отмечено влияние на данные/окружение
- [ ] обновлён `docs/PROCESS/STATE.md`
- [ ] добавлена строка в `docs/PROCESS/CHRONICLE.md`
- [ ] обновлён `docs/AGENT_CONTEXT.md`
- [ ] обновлена семантическая память (`memory/`) + строка в `memory/MEMORY.md`

## 8. Session closeout (по сигналу «закрываем сессию»)

1. Task closeout по каждой задаче.
2. Датированная запись в CHRONICLE.md (+ строка в Index).
3. Обновить «Last updated» и дрейфующие строки в AGENT_CONTEXT.md.
4. Обновить семантическую память.
5. Закоммитить (`docs(*)` / `chore(closeout)`) и запушить.
6. Явно перечислить незакоммиченный WIP.

## 9. Engineer mode

Поведение расширяется `ENGINEER_MODE.md` — следовать дополнительно к этому файлу.

## 10. Obsidian graph rule

Каждый док архитектуры/ADR/продукта/процесса заканчивается футером
`*Graph: [[AGENT_CONTEXT]] · [[...]] · [[...]]*` (минимум 2 связи, всегда ссылка на AGENT_CONTEXT —
он хаб графа).

---

*Graph: [[AGENT_CONTEXT]] · [[INVARIANTS]] · [[BRANCHING_AND_RELEASE]] · [[PR_GENERATION]]*
