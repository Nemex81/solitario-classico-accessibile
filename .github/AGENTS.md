# Framework Copilot — Solitario Classico Accessibile

> **Versione Framework**: v1.2.0 -- 21 Marzo 2026

Questo framework orchestra lo sviluppo del progetto tramite 7 agenti specializzati
e prompt files nativi di VS Code. Ogni agente ha un ruolo specifico nel ciclo di
sviluppo (dal concept al rilascio) con trigger di attivazione, output e gate di
validazione. Il flusso E2E completo e descritto in [docs/WORKFLOW.md](../docs/WORKFLOW.md).

---

## Agenti Nativi

Gli agenti sono disponibili nel dropdown agenti della chat di VS Code.
Ogni file agente contiene: scopo, trigger, deliverable, gate e workflow.

- [Agent-Analyze](agents/Agent-Analyze.md) — Discovery e analisi codebase (read-only)
- [Agent-Design](agents/Agent-Design.md) — Decisioni architetturali, creazione DESIGN_*.md
- [Agent-Plan](agents/Agent-Plan.md) — Breaking down in fasi, PLAN_*.md e docs/TODO.md
- [Agent-Code](agents/Agent-Code.md) — Implementazione incrementale, commit atomici
- [Agent-Validate](agents/Agent-Validate.md) — Test coverage, quality gates
- [Agent-Docs](agents/Agent-Docs.md) — Sync API.md, ARCHITECTURE.md, CHANGELOG.md
- [Agent-Release](agents/Agent-Release.md) — Versioning SemVer, build cx_freeze, release

---

## Prompt Files

I prompt files si attivano dal file picker di VS Code (scrivi # in chat) o digitando
il nome del file. Usano variabili di input con sintassi `${input:label}`.

- `#init.prompt.md` — Avvia nuovo task, suggerisce agente appropriato
- `#start.prompt.md` — Riprendi codifica dal primo task non completato in TODO.md
- `#status.prompt.md` — Mostra stato attuale del workflow in corso
- `#sync-docs.prompt.md` — Avvia Agent-Docs per sync documentazione
- `#release.prompt.md` — Avvia Agent-Release per versioning e build
- `#help.prompt.md` — Spiega come funziona un agente specifico

I file si trovano in `.github/prompts/`.

---

## Flusso di Lavoro (Overview)

```
1. ANALYZE  — Agent-Analyze (read-only, findings report)
2. DESIGN   — Agent-Design (DESIGN_*.md: DRAFT -> REVIEWED)
3. PLAN     — Agent-Plan (PLAN_*.md: DRAFT -> READY, + TODO.md)
4. CODE     — Agent-Code (loop per fase, commit atomici)
5. VALIDATE — Agent-Validate (coverage >= 85%, test skeletons)
6. DOCS     — Agent-Docs (sync API.md, ARCHITECTURE.md, CHANGELOG.md)
7. RELEASE  — Agent-Release (SemVer, build, tag proposal)
```

Per il flusso dettagliato: [docs/WORKFLOW.md](../docs/WORKFLOW.md)

---

## File di Stato Critici (da non eliminare mai)

- `docs/TODO.md` — cruscotto operativo durante il branch
- `CHANGELOG.md` — source of truth per versioni
- `pyproject.toml` — entry point build
- `.github/workflows/` -- CI/CD (GitHub Actions: ci.yml, assistant-commit.yml)

---

## Script di Supporto

Script Python per automazione del framework:

- `scripts/detect_agent.py` -- Rileva l'agente appropriato dalla descrizione di un task
- `scripts/validate_gates.py` -- Valida il frontmatter YAML dei documenti DESIGN/PLAN/TODO
- `scripts/ci-local-validate.py` -- Pre-commit checklist (syntax, types, coverage)
- `scripts/generate-changelog.py` -- Generazione SemVer + CHANGELOG.md
- `scripts/build-release.py` -- Build cx_freeze + checksums
- `scripts/sync-documentation.py` -- Validazione API.md, ARCHITECTURE.md, links
- `scripts/create-project-files.py` -- Scaffolding DESIGN/PLAN/TODO
- `scripts/pre-commit-hook-template.sh` -- Git hook template

---

## Riferimenti

- **Regole globali Copilot**: [.github/copilot-instructions.md](copilot-instructions.md)
- **Workflow E2E dettagliato**: [docs/WORKFLOW.md](../docs/WORKFLOW.md)
- **Automazione CLI**: [docs/CI_AUTOMATION.md](../docs/CI_AUTOMATION.md)
- **Quick Start**: [.vscode/copilot-quick-start.md](../.vscode/copilot-quick-start.md)
- **Template Progetti**: [docs/1 - templates/](../docs/1%20-%20templates/)
