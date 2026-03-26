# Framework Copilot — Solitario Classico Accessibile

> **Versione Framework**: v1.7.1 — 26 Marzo 2026

Questo framework orchestra lo sviluppo del progetto tramite 14 agenti specializzati
e prompt files nativi di VS Code. Ogni agente ha un ruolo specifico nel ciclo di
sviluppo (dal concept al rilascio) con trigger di attivazione, output e gate di
validazione. Il flusso E2E completo e descritto in [docs/WORKFLOW.md](../docs/WORKFLOW.md).

---

## Agenti Nativi

Gli agenti sono disponibili nel dropdown agenti della chat di VS Code.
Ogni file agente contiene: scopo, trigger, deliverable, gate e workflow.

- [Agent-Helper](agents/Agent-Helper.md) — Consultivo read-only sul Framework Copilot
  Agente consultivo. Risponde a domande su agenti, prompt, skill, istruzioni
  e struttura del framework. Non modifica file, non esegue comandi git.
  Modalità: read-only. Scope esclusivo: lettura di .github/.
  Modelli: Claude Sonnet 4.6, gpt-5-mini.
- [Agent-Welcome](agents/Agent-Welcome.md) — Setup profilo progetto
  Agente di inizializzazione. Raccoglie le info fondamentali
  del progetto, genera .github/project-profile.md come
  source of truth, adatta i componenti language-specific.
  Non partecipa al ciclo E2E. Invocabile dal dropdown o
  tramite #project-setup.prompt.md e #project-update.prompt.md.
  Modelli: GPT-5 mini nel frontmatter del framework; Raptor mini disponibile
  operativamente nell'ambiente quando supportato dal validator.
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
  Modelli: gpt-5-mini, GPT-5.3-Codex. Invocabile dal dropdown o come subagente.

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

- `#project-setup.prompt.md` — Setup iniziale framework
  per nuovo progetto. Da eseguire prima di qualsiasi
  altra operazione. Delega ad Agent-Welcome OP-1.
- `#project-update.prompt.md` — Aggiorna campi del
  profilo progetto. Delega ad Agent-Welcome OP-2.
- `#verbosity.prompt.md` — Modifica il livello di verbosita
  comunicativa globale degli agenti.
  Richiede `framework_edit_mode: true`; se il framework e lockato,
  usare prima `#framework-unlock.prompt.md`.
- `#personality.prompt.md` — Modifica la postura operativa
  globale degli agenti.
  Richiede `framework_edit_mode: true`; se il framework e lockato,
  usare prima `#framework-unlock.prompt.md`.
- `#init.prompt.md` — Avvia nuovo task, suggerisce agente appropriato
- `#start.prompt.md` — Riprendi codifica dal primo task non completato in TODO.md
- `#status.prompt.md` — Mostra stato attuale del workflow in corso
- `#sync-docs.prompt.md` — Avvia Agent-Docs per sync documentazione
- `#release.prompt.md` — Avvia Agent-Release per versioning e build
- `#help.prompt.md` — Spiega come funziona un agente specifico
- `#git-commit.prompt.md` — Wrapper agent per commit
  (input opzionale `PUSH` per commit + push immediato)
- `#git-merge.prompt.md` — Wrapper agent per merge
  (delega ad Agent-Git senza eseguire git direttamente)
- `#framework-update.prompt.md` — Aggiorna AGENTS.md e copilot-instructions.md dopo modifica al framework
- `#framework-changelog.prompt.md` — Aggiunge voce a FRAMEWORK_CHANGELOG.md sezione [Unreleased]
- `#framework-release.prompt.md` — Consolida [Unreleased] in una versione rilasciata del framework
- `#framework-unlock.prompt.md` — Sblocca temporaneamente i path protetti del framework

I file si trovano in `.github/prompts/`.

---

## Instructions Files

Le instructions si attivano automaticamente in base al file aperto.
Si trovano in `.github/instructions/`.

- `python.instructions.md` — standard Python (applyTo: `**/*.py`)
- `tests.instructions.md` — standard test (applyTo: `tests/**/*.py`)
- `domain.instructions.md` — regole layer domain (applyTo: `src/domain/**/*.py`)
- `ui.instructions.md` — regole wxPython + accessibilità NVDA (applyTo: `src/presentation/**/*.py`)
- `verbosity.instructions.md` — gestione della verbosita comunicativa
  degli agenti framework (applyTo: `.github/**`)
- `personality.instructions.md` — gestione della postura operativa
  e dello stile relazionale degli agenti framework (applyTo: `.github/**`)
- `framework-guard.instructions.md` — guardia scrittura componenti framework
  (applyTo: `**` — prevale sui path protetti)
- `workflow-standard.instructions.md` — sequenza operativa standard
  per ogni richiesta di modifica (applyTo: `**`): TODO gate, pre-commit
  checklist, sync documentazione, feedback strutturato.

## Agent Skills

Le skills sono abilità atomiche richiamabili da più agenti.
Si trovano in `.github/skills/`.

- `validate-accessibility.skill.md` — checklist WAI-ARIA + NVDA (UI)
- `conventional-commit.skill.md` — regole Conventional Commits
- `semver-bump.skill.md` — logica SemVer per release
- `clean-architecture-rules.skill.md` — regole Clean Architecture 4 layer
- `document-template.skill.md` — struttura DESIGN, PLAN e TODO
- `accessibility-output.skill.md` — standard output accessibile (tutti gli agenti)
- `project-profile.skill.md` — struttura project-profile.md,
  matrice componenti per linguaggio, template instructions
- `project-profile.template.md` *(template)* — struttura
  neutra resettabile del profilo progetto. Sorgente canonica
  per Agent-Welcome in OP-1 e OP-2. Percorso:
  `.github/templates/`
- `git-execution.skill.md` — matrice autorizzazioni comandi git per contesto
- `file-deletion-guard.skill.md` — guardia con conferma
  obbligatoria prima di eliminare file o directory
- `framework-guard.skill.md` — blocco standardizzato per modifiche
  ai componenti protetti del framework
- `verbosity.skill.md` — gestione della verbosita comunicativa
  globale e per-agente tramite cascata
- `personality.skill.md` — gestione della postura operativa
  globale e per-agente tramite cascata
- `changelog-entry.skill.md` — regole generazione voce
  CHANGELOG da git diff: sezione, formato, struttura file
- `code-routing.skill.md` — classificazione fasi GUI/non-GUI per Agent-CodeRouter
- `framework-query.skill.md` — contratto output per risposte descrittive,
  comparative e di workflow (Agent-Helper)
- `framework-index.skill.md` — sequenza lettura e formato panoramica
  framework da fonti interne (Agent-Helper, Agent-Orchestrator)
- `agent-selector.skill.md` — routing deterministico per selezione
  agente dato un task (Agent-Helper, Agent-Orchestrator)
- `framework-scope-guard.skill.md` — limiti operativi e risposte
  standard per agenti read-only (Agent-Helper)

| Agente | Skills referenziate |
| ------ | ------------------ |
| Agent-Welcome | project-profile, accessibility-output, verbosity, personality, file-deletion-guard, framework-guard, project-profile-template¹ |
| Agent-Analyze | clean-architecture-rules, accessibility-output, verbosity, personality |
| Agent-Design | clean-architecture-rules, document-template, accessibility-output, verbosity, personality |
| Agent-Plan | document-template, accessibility-output, verbosity, personality |
| Agent-Code | conventional-commit, validate-accessibility, clean-architecture-rules, accessibility-output, verbosity, personality, git-execution, file-deletion-guard |
| Agent-Validate | tests (instructions), validate-accessibility, accessibility-output, verbosity, personality |
| Agent-Docs | semver-bump, accessibility-output, verbosity, personality |
| Agent-Release | semver-bump, accessibility-output, verbosity, personality, git-execution, framework-guard |
| Agent-FrameworkDocs | accessibility-output, verbosity, personality, framework-guard |
| Agent-Git | git-execution, conventional-commit, changelog-entry, accessibility-output, file-deletion-guard |
| Agent-Orchestrator | accessibility-output, verbosity, personality, git-execution, framework-guard |
| Agent-CodeRouter | code-routing, accessibility-output, verbosity, personality, git-execution |
| Agent-CodeUI | validate-accessibility, conventional-commit, accessibility-output, verbosity, personality, git-execution |
| Agent-Helper | framework-query, framework-index, agent-selector, framework-scope-guard, accessibility-output, verbosity, personality |

¹ `project-profile-template` non è una skill ma un template in `.github/templates/`. Agent-Welcome lo usa in lettura; la manutenzione è di Agent-FrameworkDocs.

Nota: `Agent-Git` e un'eccezione intenzionale. Non referenzia
`verbosity`/`personality` per design, perche produce output strutturato
e operativo invece di output conversazionale guidato da quei profili.

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
- `.github/templates/project-profile.template.md` —
  template neutro profilo progetto (non eliminare)

---

## Script di Supporto

Script Python per automazione del framework:

- `scripts/git_runner.py` — Wrapper CLI operazioni git per
  Agent-Git. Sottocomandi: status, commit, push, merge, tag.
  Esegue sequenze git atomiche con gestione exit code e
  output strutturato prefissato GIT_RUNNER: per rilevamento
  esito da parte dell'agente. Dipendenze: solo stdlib Python.
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
