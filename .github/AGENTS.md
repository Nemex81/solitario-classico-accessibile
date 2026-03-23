# Framework Copilot — Solitario Classico Accessibile

> **Versione Framework**: v1.6.0 — 23 Marzo 2026

Questo framework orchestra lo sviluppo del progetto tramite 12 agenti specializzati
e prompt files nativi di VS Code. Ogni agente ha un ruolo specifico nel ciclo di
sviluppo (dal concept al rilascio) con trigger di attivazione, output e gate di
validazione. Il flusso E2E completo e descritto in [docs/WORKFLOW.md](../docs/WORKFLOW.md).

---

## Agenti Nativi

Gli agenti sono disponibili nel dropdown agenti della chat di VS Code.
Ogni file agente contiene: scopo, trigger, deliverable, gate e workflow.

- [Agent-Orchestrator](agents/Agent-Orchestrator.md) — Coordinatore E2E
  Orchestratore del ciclo completo. Usa subagent delegation per
  coordinare tutti gli agenti specializzati. Gate oggettivi verificati
  tramite script CLI. Checkpoint di controllo con conferma utente.
  Invocazione: seleziona dal dropdown o usa #orchestrate.prompt.md
- [Agent-Analyze](agents/Agent-Analyze.md) — Discovery e analisi codebase (read-only)
- [Agent-Design](agents/Agent-Design.md) — Decisioni architetturali, creazione DESIGN_*.md
- [Agent-Plan](agents/Agent-Plan.md) — Breaking down in fasi, PLAN_*.md e docs/TODO.md
- [Agent-CodeRouter](agents/Agent-CodeRouter.md) — Dispatcher sotto-ciclo codifica
  Coordinatore del sotto-ciclo implementazione. Classifica le fasi del TODO
  come GUI o non-GUI e delega ad Agent-CodeUI o Agent-Code.
  Invocato da Agent-Orchestrator in sostituzione diretta di Agent-Code.
- [Agent-Code](agents/Agent-Code.md) — Implementazione incrementale, commit atomici
  (invariato, ora sub-agente di Agent-CodeRouter per fasi non-GUI)
- [Agent-CodeUI](agents/Agent-CodeUI.md) — Implementazione GUI wxPython + accessibilità NVDA
  Sub-agente di Agent-CodeRouter per fasi che coinvolgono componenti UI.
  Ogni componente deve superare checklist WAI-ARIA + NVDA prima del commit.
- [Agent-Validate](agents/Agent-Validate.md) — Test coverage, quality gates
- [Agent-Docs](agents/Agent-Docs.md) — Sync API.md, ARCHITECTURE.md, CHANGELOG.md
- [Agent-Release](agents/Agent-Release.md) — Versioning SemVer, build cx_freeze, release
- [Agent-FrameworkDocs](agents/Agent-FrameworkDocs.md) — Manutenzione Framework
  Agente esclusivo per documentazione e changelog del Framework Copilot.
  Scope: `.github/**`. Attivazione: solo manuale o tramite prompt `framework-*`.
  Non partecipa al ciclo E2E del progetto.
- [Agent-Git](agents/Agent-Git.md) — Operazioni Git autorizzate
  Unico agente autorizzato a eseguire git tramite run_in_terminal.
  Gestisce commit, push, merge, tag con conferme esplicite obbligatorie.
  Modello: gpt-5-mini. Invocabile dal dropdown o come subagente.

---

## Dual-Track Documentation

Il framework adotta una separazione netta tra documentazione del framework
e documentazione del progetto ospite.

**Binario Framework** — gestito da Agent-FrameworkDocs:

- `.github/FRAMEWORK_CHANGELOG.md`: storico evoluzione framework
- `.github/AGENTS.md`: questo file
- `.github/README.md`: guida importazione framework
- `.github/agents/README.md`, `.github/prompts/README.md`

**Binario Progetto** — gestito da Agent-Docs nel ciclo E2E:

- `CHANGELOG.md` della root: storico del progetto applicativo
- `docs/API.md`, `docs/ARCHITECTURE.md`: documentazione tecnica progetto

**Regola invariante**: Agent-FrameworkDocs non tocca mai `CHANGELOG.md`
della root. Agent-Docs non tocca mai `FRAMEWORK_CHANGELOG.md`.
I due binari non si incrociano.

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
- `#framework-update.prompt.md` — Aggiorna AGENTS.md e copilot-instructions.md dopo modifica al framework
- `#framework-changelog.prompt.md` — Aggiunge voce a FRAMEWORK_CHANGELOG.md sezione [Unreleased]
- `#framework-release.prompt.md` — Consolida [Unreleased] in una versione rilasciata del framework

I file si trovano in `.github/prompts/`.

---

## Instructions Files

Le instructions si attivano automaticamente in base al file aperto.
Si trovano in `.github/instructions/`.

- `python.instructions.md` — standard Python (applyTo: `**/*.py`)
- `tests.instructions.md` — standard test (applyTo: `tests/**/*.py`)
- `domain.instructions.md` — regole layer domain (applyTo: `src/domain/**/*.py`)
- `ui.instructions.md` — regole wxPython + accessibilità NVDA (applyTo: `src/presentation/**/*.py`)

## Agent Skills

Le skills sono abilità atomiche richiamabili da più agenti.
Si trovano in `.github/skills/`.

- `validate-accessibility.skill.md` — checklist WAI-ARIA + NVDA (UI)
- `conventional-commit.skill.md` — regole Conventional Commits
- `semver-bump.skill.md` — logica SemVer per release
- `clean-architecture-rules.skill.md` — regole Clean Architecture 4 layer
- `document-template.skill.md` — struttura DESIGN, PLAN e TODO
- `accessibility-output.skill.md` — standard output accessibile (tutti gli agenti)
- `git-execution.skill.md` — matrice autorizzazioni comandi git per contesto
- `file-deletion-guard.skill.md` — guardia con conferma
  obbligatoria prima di eliminare file o directory
- `changelog-entry.skill.md` — regole generazione voce
  CHANGELOG da git diff: sezione, formato, struttura file
- `code-routing.skill.md` — classificazione fasi GUI/non-GUI per Agent-CodeRouter

| Agente | Skills referenziate |
| ------ | ------------------ |
| Agent-Analyze | clean-architecture-rules, accessibility-output |
| Agent-Design | clean-architecture-rules, document-template, accessibility-output |
| Agent-Plan | document-template, accessibility-output |
| Agent-Code | conventional-commit, validate-accessibility, clean-architecture-rules, accessibility-output, git-execution, file-deletion-guard |
| Agent-Validate | tests (instructions), validate-accessibility, accessibility-output |
| Agent-Docs | semver-bump, accessibility-output |
| Agent-Release | semver-bump, accessibility-output |
| Agent-FrameworkDocs | accessibility-output, file-deletion-guard |
| Agent-Git | git-execution, conventional-commit, changelog-entry, accessibility-output, file-deletion-guard |
| Agent-Orchestrator | accessibility-output, git-execution |
| Agent-CodeRouter | code-routing, accessibility-output, git-execution |
| Agent-CodeUI | validate-accessibility, conventional-commit, accessibility-output, git-execution |

---

## Flusso di Lavoro (Overview)

```text
1. ANALYZE  — Agent-Analyze (read-only, findings report)
2. DESIGN   — Agent-Design (DESIGN_*.md: DRAFT -> REVIEWED)
3. PLAN     — Agent-Plan (PLAN_*.md: DRAFT -> READY, + TODO.md)
4. CODE     — Agent-CodeRouter (dispatcher)
               4a. Agent-Code    (fasi non-GUI)
               4b. Agent-CodeUI  (fasi GUI + accessibilità)
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
