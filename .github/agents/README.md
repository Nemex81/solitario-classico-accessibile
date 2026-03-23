# Agenti Nativi — Framework Copilot

Indice degli agenti VS Code nella cartella `.github/agents/`.
Ogni file `.md` è un agente nativo attivabile dal dropdown agenti di VS Code.

## Agenti presenti

- [`Agent-Orchestrator`](Agent-Orchestrator.md) — Coordinatore E2E, delega agli agenti specializzati
- [`Agent-Analyze`](Agent-Analyze.md) — Discovery e analisi codebase (read-only)
- [`Agent-Design`](Agent-Design.md) — Decisioni architetturali, crea DESIGN_*.md
- [`Agent-Plan`](Agent-Plan.md) — Breaking down in fasi, crea PLAN_*.md e TODO.md
- [`Agent-CodeRouter`](Agent-CodeRouter.md) — Dispatcher sotto-ciclo codifica GUI/non-GUI
- [`Agent-Code`](Agent-Code.md) — Implementazione incrementale, fasi non-GUI
- [`Agent-CodeUI`](Agent-CodeUI.md) — Implementazione GUI wxPython + accessibilità NVDA
- [`Agent-Validate`](Agent-Validate.md) — Test coverage e quality gates
- [`Agent-Docs`](Agent-Docs.md) — Sync documentazione progetto (API.md, CHANGELOG.md)
- [`Agent-Release`](Agent-Release.md) — Versioning SemVer, build cx_freeze, release
- [`Agent-FrameworkDocs`](Agent-FrameworkDocs.md) — Manutenzione Framework Copilot (scope: .github/**)
- [`Agent-Git`](Agent-Git.md) — Operazioni git autorizzate (modello: gpt-5-mini)

## Note

- Ogni agente è invocabile dal dropdown agenti nella chat di VS Code.
- Documento di riferimento completo: [AGENTS.md](../AGENTS.md)
