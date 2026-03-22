# Framework Copilot — Changelog

Tutte le modifiche rilevanti al Framework Copilot sono documentate qui.
Formato: [Conventional Changelog](https://keepachangelog.com/it/1.0.0/)
Versioning: [SemVer](https://semver.org/lang/it/)

---

## [Unreleased]

### Added
- Instructions files: `python.instructions.md`, `tests.instructions.md`,
  `domain.instructions.md` — regole contestuali per filetype attivate
  automaticamente da VS Code Copilot.
- Agent Skills: `validate-accessibility.skill.md`,
  `conventional-commit.skill.md`, `semver-bump.skill.md` — abilità
  atomiche riutilizzabili tra agenti.

### Changed
- `copilot-instructions.md`: sezioni Python standards, testing e
  critical warnings migrate nelle instructions contestuali.
  File alleggerito di circa un terzo.
- Framework bumped a v1.5.0.

## [1.4.0] — 2026-03-22

### Added

- Agent-FrameworkDocs: agente dedicato alla manutenzione di documenti e changelog del framework. Scope esclusivo `.github/**`. Attivazione manuale o tramite prompt `framework-*`.
- `.github/README.md`: guida all'installazione e importazione del framework su un nuovo progetto.
- `.github/FRAMEWORK_CHANGELOG.md`: questo file, storico indipendente del framework separato da `CHANGELOG.md` del progetto.
- `framework-update.prompt.md`: prompt per aggiornare AGENTS.md e copilot-instructions.md dopo aggiunta/modifica di agenti o prompt.
- `framework-changelog.prompt.md`: prompt per aggiungere voci a FRAMEWORK_CHANGELOG.md sezione [Unreleased].
- `framework-release.prompt.md`: prompt per consolidare [Unreleased] in una versione rilasciata del framework.

### Changed

- AGENTS.md: versione framework bumped a v1.4.0, conteggio agenti da 8 a 9, aggiunta sezione Dual-Track Documentation.
- copilot-instructions.md: versione bumped a v1.4.0, aggiornati tabella componenti, lista agenti e tabella comandi.

---

## [1.3.0] — 2026-03-21

### Added

- Agent-Orchestrator: coordinatore E2E con subagent delegation e gate CLI oggettivi.
- `orchestrate.prompt.md`: entry point per il ciclo E2E completo.
- `git-commit.prompt.md`: prompt per commit atomici con Conventional Commits.
- `git-merge.prompt.md`: prompt per merge e PR con policy no-fast-forward.
- `status.prompt.md`: mostra stato workflow corrente.
- `help.prompt.md`: spiega come funziona un agente specifico.

### Changed

- AGENTS.md aggiornato con workflow E2E dettagliato e flusso 7 fasi.
- copilot-instructions.md: aggiornata sezione Quick Start con riferimento ad Agent-Orchestrator.

---

## [1.2.0] — 2026-02-28 (stimata)

### Added

- 8 script Python di automazione in `scripts/`:
  - `detect_agent.py`: rileva l'agente appropriato dalla descrizione di un task.
  - `validate_gates.py`: valida frontmatter YAML dei documenti DESIGN/PLAN/TODO.
  - `ci-local-validate.py`: pre-commit checklist (syntax, types, coverage).
  - `generate-changelog.py`: generazione SemVer e CHANGELOG.md.
  - `build-release.py`: build cx_freeze e checksum.
  - `sync-documentation.py`: validazione API.md, ARCHITECTURE.md, link interni.
  - `create-project-files.py`: scaffolding DESIGN/PLAN/TODO.
  - `pre-commit-hook-template.sh`: git hook template pre-commit.
- Template DESIGN/PLAN/TODO con frontmatter YAML in `docs/1 - templates/`.
- CI workflow GitHub Actions in `.github/workflows/ci.yml` (4 job: lint, type-check, test, coverage).

### Changed

- Agenti aggiornati con trigger di attivazione, gate di validazione e deliverable espliciti.
- copilot-instructions.md: aggiunta sezione Pre-Commit Checklist con 6 step.

---

## [1.0.0] — 2026-02-12 (stimata)

### Added

- Framework iniziale: 8 agenti nativi VS Code con ruoli distinti nel ciclo di sviluppo.
  - Agent-Orchestrator: coordinatore E2E.
  - Agent-Analyze: discovery e analisi codebase (read-only).
  - Agent-Design: decisioni architetturali, creazione documenti DESIGN_*.md.
  - Agent-Plan: breaking down in fasi, PLAN_*.md e docs/TODO.md.
  - Agent-Code: implementazione incrementale, commit atomici.
  - Agent-Validate: test coverage, quality gates (85%+ threshold).
  - Agent-Docs: sync API.md, ARCHITECTURE.md, CHANGELOG.md.
  - Agent-Release: versioning SemVer, build cx_freeze, release.
- Prompt files iniziali: `init.prompt.md`, `start.prompt.md`, `sync-docs.prompt.md`, `release.prompt.md`.
- `copilot-instructions.md`: istruzioni globali Copilot con standard Clean Architecture, naming conventions, type hints, logging, error handling, accessibilità.
- `AGENTS.md`: documento di riferimento del framework con lista agenti, prompt files, flusso di lavoro.
