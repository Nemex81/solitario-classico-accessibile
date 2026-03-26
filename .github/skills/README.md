# Agent Skills — Framework Copilot

Le skills sono abilità atomiche riutilizzabili tra più agenti.
Non si attivano automaticamente: gli agenti le referenziano
esplicitamente nella sezione "Riferimenti Skills".

## Skills presenti

- `validate-accessibility.skill.md` — checklist WAI-ARIA + NVDA (UI)
- `conventional-commit.skill.md` — regole Conventional Commits
- `semver-bump.skill.md` — logica SemVer per release
- `clean-architecture-rules.skill.md` — regole Clean Architecture 4 layer
- `document-template.skill.md` — struttura DESIGN, PLAN e TODO
- `docs_manager.skill.md` — sistema di tracciamento documenti: path canonici docs/,
  distinzione template framework vs template utente, convenzione naming file,
  flusso salvataggio per tipo, idempotenza coordinatore, regola additiva,
  bootstrap struttura docs/ portabile e non distruttivo
- `error-recovery.skill.md` — procedura standardizzata di retry (max 2 tentativi)
  e escalata quando un subagente fallisce (Orchestrator)
- `semantic-gate.skill.md` — criteri minimi osservabili per avanzamento tra fasi
  Analyze→Design→Plan: sezioni obbligatorie nei findings, status REVIEWED/READY
- `rollback-procedure.skill.md` — decision tree e procedura standard per rollback
  E2E dopo commit parziali: git revert (pushati) vs git reset --soft (locali)

## Agenti e skills associate

| Agente | Skills referenziate |
| ------ | ------------------ |
| Agent-Welcome | project-profile, accessibility-output, file-deletion-guard, framework-guard, verbosity, personality, style-setup, docs_manager |
| Agent-Analyze | clean-architecture-rules, accessibility-output, verbosity, personality |
| Agent-Design | clean-architecture-rules, document-template, docs_manager, accessibility-output, verbosity, personality |
| Agent-Plan | document-template, docs_manager, accessibility-output, verbosity, personality |
| Agent-Code | conventional-commit, validate-accessibility, clean-architecture-rules, accessibility-output, git-execution, file-deletion-guard, verbosity, personality |
| Agent-Validate | tests (instructions), validate-accessibility, accessibility-output, verbosity, personality |
| Agent-Docs | semver-bump, accessibility-output, framework-guard, verbosity, personality |
| Agent-Release | semver-bump, accessibility-output, framework-guard, verbosity, personality |
| Agent-FrameworkDocs | accessibility-output, file-deletion-guard, framework-guard, verbosity, personality |
| Agent-Git | git-execution, conventional-commit, changelog-entry, accessibility-output, file-deletion-guard, rollback-procedure |
| Agent-Orchestrator | docs_manager, error-recovery, semantic-gate, rollback-procedure, accessibility-output, git-execution, framework-guard, verbosity, personality |
| Agent-CodeRouter | code-routing, accessibility-output, git-execution, verbosity, personality |
| Agent-CodeUI | validate-accessibility, conventional-commit, accessibility-output, git-execution, verbosity, personality |
| Agent-Helper | framework-query, framework-index, agent-selector, framework-scope-guard, accessibility-output, verbosity, personality, style-setup |
