<!-- Канон требований к PR: docs/PROCESS/PR_GENERATION.md -->

## Summary

<!-- что и зачем изменено, 1 абзац -->

## Files changed

<!-- git diff --stat -->

## ADR references

<!-- какие решения из docs/ARCHITECTURE/ADR/INDEX.md применены/затронуты -->

## Invariants preserved

<!-- чек-лист затронутых INV-* из docs/ARCHITECTURE/INVARIANTS.md: что сохранено и как -->

- [ ] INV-...

## Traceability (requirements → tests)

<!-- какие FR/NFR покрыты и какими тест-кейсами; ссылка на docs/QA/TEST_PLAN.md -->

## Test results

<!-- фактический вывод: pytest (как минимум pytest --collect-only для типа B). Не выдумывать. -->

```text
$ pytest -q
...
```

## Data / Env impact

<!-- миграции, изменения схемы, новые переменные окружения -->

## Risks / follow-ups

<!-- известные риски, открытые вопросы Q-* -->

## Rollback plan

<!-- git revert <sha>; alembic downgrade -1; и т.п. -->

---

<!-- Неприменимый раздел → N/A с причиной. force-push запрещён (docs/PROCESS/BRANCHING_AND_RELEASE.md). -->
