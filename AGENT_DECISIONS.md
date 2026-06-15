# AGENT_DECISIONS.md
Agent Decision Log (ADR-lite)

> **Reconciliation (2026-06-15).** Этот файл — комплементарный legacy-журнал принципов. Каноничный
> источник архитектурной истины теперь — дерево `docs/ARCHITECTURE/` (приоритет: `INVARIANTS.md` >
> `FINAL_SYSTEM_SPEC.md` > `ADR/*`), порядок авторитета задан в `AGENTS.md`. Решения `Dx` ниже
> согласованы с инвариантами `INV-*` и ADR-001..008. Упомянутый в D11 файл
> `docs/PROCESS/IMPLEMENTATION_LEDGER.md` создаётся в момент старта основной разработки (сейчас
> bootstrap; разработка не начата).

Purpose:
- Provide non-negotiable architectural truths and operational constraints for AI agents.
- Prevent repeated architecture violations and accidental drift.
- Enable consistent decision-making across tasks.

Rules for agents:
- Read this file before making any code changes.
- If a task conflicts with any decision here, STOP and propose an alternative.
- If a new permanent rule is discovered, append it to this file (docs-only atomic commit).

---

## D0 — System Goal and Quality Bar

We optimize for:
- determinism
- reproducibility
- risk containment
- operational stability
- auditability

We do NOT optimize for:
- fastest iteration speed at the expense of correctness
- clever abstractions
- hidden state
- "just make it work" shortcuts

---

## D1 — Determinism as an Invariant

All core outputs must be reproducible from the same inputs:
- state transitions
- diagnostics snapshots
- report pages that claim deterministic information

Avoid:
- time-dependent values without explicit injection
- random() without seeded deterministic PRNG
- non-deterministic ordering (maps/sets/object keys) in outputs
- environment-dependent behavior

If any nondeterminism is required, it MUST be:
- explicit
- isolated
- test-covered
- documented in code comments

---

## D2 — State Ownership and Persistence Policy

Single source of truth for state.
No hidden persistence.

Unless explicitly approved:
- no localStorage
- no sessionStorage
- no ad-hoc file persistence
- no silent caching that changes behavior

If caching is needed:
- make it explicit
- ensure invalidation is deterministic
- add tests for cache correctness

---

## D3 — Networking Contract (UI and Clients)

All network traffic must go through the approved client/service layer.
No direct fetch/axios usage if a centralized HTTP client exists.

Requirements (typical):
- replay protection / request-id support
- consistent error mapping
- consistent auth/session behavior
- consistent tracing/logging hooks

Do not bypass these.

---

## D4 — Contracts and Schema Discipline

API contracts are controlled artifacts.

Rules:
- Do not change request/response shapes silently.
- If a contract changes, update:
  - validators / schema checks
  - snapshot tests (if used)
  - diagnostics surfaces that display contracts
- Prefer additive changes over breaking ones.
- Always consider versioning or compatibility strategy.

---

## D5 — Security Baseline

Default stance: least privilege.

Rules:
- role-gate admin controls
- avoid leaking secrets into UI artifacts/logs
- do not weaken auth/session rules
- protect endpoints from replay where required
- do not store tokens in browser persistent storage (unless explicitly approved)

---

## D6 — Observability and Diagnostics

Diagnostics must remain:
- deterministic where possible
- useful for incident analysis
- stable enough for tests and CI checks

Do not:
- remove diagnostic signals to "reduce noise"
- replace structured data with unstructured strings
- introduce intermittent log output in deterministic checks

---

## D7 — Change Scope and Refactor Policy

Bias: minimal, localized changes.

No broad refactors unless:
- explicitly requested
- justified with clear benefit
- staged with a migration plan
- accompanied by test coverage

---

## D8 — Tests are Part of the Feature

If behavior changes, tests must change accordingly.

Prohibited:
- weakening assertions to make tests pass
- deleting tests without replacement
- adding flaky tests
- hiding failures with retries

Preferred:
- deterministic tests
- stable snapshots
- clear Arrange/Act/Assert structure

---

## D9 — Documentation and Atomicity

Any change that updates docs or decisions must be:
- in a docs-only atomic commit
- with clean worktree
- no mixed code+docs unless explicitly required

When a new invariant/decision emerges:
- append it here under a new Dx entry
- keep it short and enforceable

---

## D10 — Escalation Rule (When Uncertain)

If requirements are ambiguous:
- make explicit assumptions
- propose 2–3 options with trade-offs
- implement only after constraints are stable (unless asked to proceed)

## D11 — Implementation Continuity Record

During active implementation, the repository must maintain a living continuity record in:
- `docs/PROCESS/IMPLEMENTATION_LEDGER.md`

Rules:
- update it in the same task when code or contracts change
- record what changed, why, how it was verified, and what remains
- read it before resuming implementation in a new session/window

Purpose:
- preserve architectural context
- prevent repeated rediscovery
- keep execution history explicit and auditable

## D12 — PR Generation Is Part of Done

After a slice passes required gates, the agent must produce a PR-ready package:
- PR title
- PR description matching `.github/pull_request_template.md`
- local squash-merge command sequence
- proposed milestone tag

Allowed facts for PR generation:
- `git diff --stat`
- `git diff`
- `git status --porcelain`
- `git log -n 10 --oneline`
- `npm run docs:golden`
- `npm test`
- referenced ADRs/docs

If a section does not apply:
- write `N/A` with a reason

No invented tests, invariants, or rollout claims.

## D13 — Local Integration Branch Is Mandatory

Until publication to GitHub, the canonical local integration branch is:
- `feat/next-stage-baseline`

Rules:
- finish a slice on a short-lived branch
- pass gates there first
- merge it locally into `feat/next-stage-baseline`
- start the next slice from a fresh short-lived branch created from `feat/next-stage-baseline`

This prevents branch drift, stale feature chains, and accidental continuation on the wrong branch.
