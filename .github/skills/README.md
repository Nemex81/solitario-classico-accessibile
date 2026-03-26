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
- `accessibility-output.skill.md` — standard output accessibile (tutti gli agenti)
- `project-profile.skill.md` — struttura profilo progetto,
  matrice componenti language-specific, template instructions
- `git-execution.skill.md` — matrice autorizzazioni comandi git per contesto
- `file-deletion-guard.skill.md` — guardia con conferma obbligatoria
  prima di eliminare file o directory
- `framework-guard.skill.md` — blocco standardizzato per modifiche
  ai componenti protetti del framework
- `changelog-entry.skill.md` — regole generazione voce CHANGELOG
  da git diff: classificazione sezione, formato voce, struttura file
- `code-routing.skill.md` — regole di classificazione fasi GUI/non-GUI per Agent-CodeRouter
- `framework-query.skill.md` — contratto output per risposte descrittive,
  comparative e di workflow (Agent-Helper)
- `framework-index.skill.md` — sequenza lettura e formato panoramica
  framework da fonti interne (Agent-Helper, Agent-Orchestrator)
- `agent-selector.skill.md` — routing deterministico per selezione agente
  dato un task (Agent-Helper, Agent-Orchestrator)
- `framework-scope-guard.skill.md` — limiti operativi e risposte standard
  per agenti read-only (Agent-Helper)
- `verbosity.skill.md` — gestione della verbosità comunicativa globale
  e per-agente tramite cascata di risoluzione
- `personality.skill.md` — gestione della postura operativa globale
  e per-agente tramite cascata di risoluzione
- `style-setup.skill.md` — presentazione e selezione guidata dei parametri
  `verbosity` e `personality`; formato output valori correnti e branching
  salta/personalizza. Scrittura autorizzata solo per Agent-Welcome (OP-1/OP-2)
- `docs_manager.md` — sistema di tracciamento documenti: path canonici docs/,
  distinzione template framework vs template utente, convenzione naming file,
  flusso salvataggio per tipo, idempotenza coordinatore, regola additiva,
  bootstrap struttura docs/ portabile e non distruttivo

## Agenti e skills associate

| Agente | Skills referenziate |
| ------ | ------------------ |
| Agent-Welcome | project-profile, accessibility-output, file-deletion-guard, framework-guard, verbosity, personality, style-setup, docs_manager |
| Agent-Analyze | clean-architecture-rules, accessibility-output, verbosity, personality |
| Agent-Design | clean-architecture-rules, document-template, accessibility-output, verbosity, personality |
| Agent-Plan | document-template, accessibility-output, verbosity, personality |
| Agent-Code | conventional-commit, validate-accessibility, clean-architecture-rules, accessibility-output, git-execution, file-deletion-guard, verbosity, personality |
| Agent-Validate | tests (instructions), validate-accessibility, accessibility-output, verbosity, personality |
| Agent-Docs | semver-bump, accessibility-output, framework-guard, verbosity, personality |
| Agent-Release | semver-bump, accessibility-output, framework-guard, verbosity, personality |
| Agent-FrameworkDocs | accessibility-output, file-deletion-guard, framework-guard, verbosity, personality |
| Agent-Git | git-execution, conventional-commit, changelog-entry, accessibility-output, file-deletion-guard |
| Agent-Orchestrator | accessibility-output, git-execution, framework-guard, verbosity, personality |
| Agent-CodeRouter | code-routing, accessibility-output, git-execution, verbosity, personality |
| Agent-CodeUI | validate-accessibility, conventional-commit, accessibility-output, git-execution, verbosity, personality |
| Agent-Helper | framework-query, framework-index, agent-selector, framework-scope-guard, accessibility-output, verbosity, personality, style-setup |
