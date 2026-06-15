# PR_GENERATION

Что обязан содержать каждый PR. Согласовано с `.github/pull_request_template.md`. Применяется после
bootstrap для всех слайсов из [[ROADMAP]].

## Обязательные разделы PR
1. **Summary** — что и зачем изменено (1 абзац).
2. **Files changed** — перечень изменённых файлов (`git diff --stat`).
3. **ADR references** — какие решения из [[ADR INDEX]] затронуты/применены.
4. **Invariants preserved** — чек-лист затронутых INV-* из [[INVARIANTS]] (что сохранено и как).
5. **Traceability** — какие FR/NFR покрыты и какими тест-кейсами (ссылка на [[TEST_PLAN]]).
6. **Test results** — вывод прогона: `pytest` (и `pytest --collect-only` как минимум для типа B).
7. **Data/Env impact** — миграции, изменения схемы, переменные окружения.
8. **Risks / follow-ups** — известные риски, открытые вопросы.
9. **Rollback plan** — как откатить (`git revert <sha>`, откат миграции).

## Разрешённые факты для генерации PR
Только верифицируемое: `git diff --stat`, `git diff`, `git status --porcelain`,
`git log -n 10 --oneline`, фактический вывод `pytest`, ссылки на существующие ADR/доки.
**Нельзя** выдумывать тесты, инварианты или результаты прогона. Неприменимый раздел → `N/A` с причиной.

## Definition of Done для PR
- Гейты PASS (или явно отмечен TDD-red статус с обоснованием для типа B).
- Матрица трассируемости в [[TEST_PLAN]] обновлена.
- Обновлены [[STATE]], [[CHRONICLE]], [[AGENT_CONTEXT]] и семантическая память.

---

*Graph: [[AGENT_CONTEXT]] · [[BRANCHING_AND_RELEASE]] · [[TEST_PLAN]] · [[INVARIANTS]]*
