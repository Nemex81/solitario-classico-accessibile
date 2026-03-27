---
feature: E2E Resilience — Gate semantici, rollback procedure, coverage SOT
type: todo
status: COMPLETED
version: v1.10.0
plan_ref: docs/3 - coding plans/PLAN_e2e-resilience_v1.10.0.md
date: 2026-03-26
---

# TODO: E2E Resilience v1.10.0

Implementazione del piano `PLAN_e2e-resilience_v1.10.0.md`: gate semantici, rollback E2E, source of truth coverage, smoke test CLI.

## Fasi

### Fase 1 — Coverage single source of truth

- [x] Aggiungi `fail_under = 85` in `pyproject.toml`
- [x] Rimuovi `--cov-fail-under=85` dai percorsi operativi in CI e validazione locale
- [x] Aggiorna instructions, agenti e documentazione interna per puntare alla SOT centralizzata

**Commit Message Fase 1:**

```text
chore(framework): centralizza coverage fail_under in pyproject.toml
```

### Fase 2 — Gate semantici Analyze → Design → Plan

- [x] Crea `semantic-gate.skill.md`
- [x] Aggiorna `Agent-Orchestrator.md` con gate qualitativo findings e precondizioni di stato DESIGN/PLAN
- [x] Aggiorna `README.md` delle skill con la nuova referenza

**Commit Message Fase 2:**

```text
docs(framework): aggiungi gate semantici tra analyze design e plan
```

### Fase 3 — Rollback / Revert E2E

- [x] Crea `rollback-procedure.skill.md`
- [x] Aggiorna `Agent-Orchestrator.md` con il flusso di rollback E2E
- [x] Aggiorna `Agent-Git.md` e `git-execution.skill.md` con la procedura di revert
- [x] Aggiorna `README.md` delle skill

**Commit Message Fase 3:**

```text
docs(framework): definisci procedura rollback e revert e2e
```

### Fase 4 — Smoke test CLI bootstrap

- [x] Aggiungi smoke test `python scripts/validate_gates.py --help` in Fase 0 Orchestrator
- [x] Documenta il blocco operativo se il check fallisce

**Commit Message Fase 4:**

```text
docs(framework): aggiungi smoke test cli in bootstrap orchestrator
```

## Vincoli espliciti

- [x] Escludere il problema 6 (timeout/stallo subagenti) da questa iterazione
- [x] Mantenere il coordinatore `docs/TODO.md` allineato ai soli lavori ancora attivi

## Prossimi step

1. Implementare le fasi in ordine, partendo dalla coverage single source of truth
2. Aggiornare il changelog framework una volta integrate le modifiche
