<!-- markdownlint-disable MD012 MD024 -->

# Framework Copilot — Changelog

Tutte le modifiche rilevanti al Framework Copilot sono documentate qui.
Formato: [Conventional Changelog](https://keepachangelog.com/it/1.0.0/)
Versioning: [SemVer](https://semver.org/lang/it/)


## [Unreleased]

<!-- Le voci non rilasciate vanno inserite qui. Rimane vuoto dopo la release. -->

### Added

- `docs/3 - coding plans/PLAN_e2e-resilience_v1.11.0.md`: plan convalidato (DRAFT → REVIEWED) per rafforzamento E2E su 4 aree: gate semantici Analyze→Design→Plan, smoke test CLI bootstrap, procedura rollback E2E, centralizzazione coverage SOT in `pyproject.toml`. Scope negativo esplicito: timeout/stallo subagenti esclusi. Target: v1.11.0.

## [v1.9.2] - 2026-03-26

### Added

- `.github/skills/error-recovery.skill.md`: nuova skill standardizzata per retry ed escalata di subagenti (max 2 tentativi, formato di escalata all'utente).
- `docs/3 - coding plans/PLAN_framework-optimization_v1.10.0.md`: nuovo plan `framework-optimization v1.10.0` (DRAFT).
- `docs/5 - todolist/TODO_framework-optimization_v1.10.0.md`: nuovo TODO per-task associato al plan.

### Changed

- `.github/skills/docs_manager.skill.md`: tabella naming unificata per tipo di documento (DESIGN, PLAN, TODO, REPORT) con motivazioni; corretta tabella bootstrap; aggiunta sezione `File temporanei` (es. findings.md).
- `.github/agents/Agent-Orchestrator.md`: Fase 0 estesa (punti 2a/2b/2c) per ripresa sessione robusta; Fase 2/3 prompt aggiornati per richiedere l'aggiornamento del coordinatore; aggiunto gate informale in Fase 6; referenze skills aggiornate (docs_manager, error-recovery).
- `.github/skills/README.md`: inventario skills aggiornato (aggiunta `error-recovery.skill.md`) e matrice agenti→skills aggiornata (docs_manager su Design/Plan/Orchestrator; error-recovery su Orchestrator).
- `docs/TODO.md`: aggiornato con link al nuovo plan e al nuovo TODO per-task.

## [v1.9.1] - 2026-03-26

### Changed

- `.github/skills/docs_manager.skill.md`: rinomina la skill documentale e allinea i riferimenti legacy.
- `.github/templates/design.md`: sostituisce `project.md` e uniforma il tipo documento `design`.
- `.github/FRAMEWORK_CHANGELOG.md` e `docs/4 - reports/REPORT_gate-validation_2026-03-26.md`: corretti due riferimenti storici allineandoli alla nomenclatura attuale.
- `.github/project-profile.md`: `framework_edit_mode` gestito con #framework-unlock per scritture controllate del framework.

## [v1.9.0] - 2026-03-26

### Added

- `docs/4 - reports/README.md`: nuova cartella canonica per report di validazione prodotti da Agent-Validate,
  con convenzione naming `REPORT_<tipo>_YYYY-MM-DD.md`.
- `docs/5 - todolist/README.md`: nuova cartella canonica per TODO specifici per implementazione prodotti
  da Agent-Plan, con convenzione naming `TODO_<feature>_vX.Y.Z.md`.

### Changed

- `.github/skills/document-template.skill.md`: sezione `docs/TODO.md` riscritta. Aggiunta nuova sezione
  `docs/5 - todolist/TODO_*.md` con struttura obbligatoria per TODO per-task. `docs/TODO.md` ridefinito
  come coordinatore persistente (append-only), non più checklist di task.
- `.github/agents/Agent-Plan.md`: deliverable aggiornato — produce `docs/5 - todolist/TODO_<feature>_vX.Y.Z.md`
  invece di sovrascrivere `docs/TODO.md`. Aggiunto aggiornamento append-only del coordinatore.
  Aggiunto riferimento a `docs_manager.md`. Workflow tipico e regole operative allineati.
- `.github/agents/Agent-Design.md`: ownership esplicita di `docs/2 - projects/` dichiarata nel deliverable.
  Aggiunto riferimento a `docs_manager.md`.
- `.github/agents/Agent-Validate.md`: ownership esplicita di `docs/4 - reports/` dichiarata nel deliverable.
  Aggiunto deliverable `REPORT_<tipo>_YYYY-MM-DD.md`.
- `.github/agents/Agent-Code.md`: TODO Gate Protocol aggiornato — legge prima `docs/TODO.md` (coordinatore)
  poi il TODO per-task in `docs/5 - todolist/`. Spunta il TODO per-task dopo ogni commit.
  Regola esplicita: non sovrascrivere `docs/TODO.md`.
- `.github/agents/Agent-Docs.md`: aggiunto deliverable di validazione strutturale `docs/`.
  Aggiunto step 7 nel workflow (validazione struttura docs/). Aggiornati gate di completamento.
  Aggiunto riferimento a `docs_manager.md`. Regola esplicita: non scrive in cartelle di
  ownership degli agenti specializzati.
- `scripts/validate_gates.py`: scan esteso a `docs/4 - reports/` e `docs/5 - todolist/`.
  Aggiunta funzione `check_docs_structure()` e flag `--check-structure` per verifica
  presenza cartelle canoniche e coordinatore. Aggiornato docstring modulo.
- `.github/copilot-instructions.md`: aggiornata intestazione Framework a `v1.9.0` per allineamento con le modifiche documentate.
- `.github/AGENTS.md`: aggiornata voce `Versione Framework` a `v1.9.0` per coerenza con il changelog.

## [v1.8.1] - 2026-03-26

### Fixed

- `.github/agents/Agent-Git.md`: aggiunto blocco `## AUTORIZZAZIONE OPERATIVA — LEGGI PRIMA DI TUTTO`
  come prima sezione del corpo, prima del testo introduttivo. Il blocco dichiara in modo imperativo
  che l'agente HA autorizzazione completa su `run_in_terminal` e che l'override della policy è
  attivo immediatamente, senza richiedere auto-riconoscimento contestuale da parte del modello.
- `.github/instructions/git-policy.instructions.md`: aggiunto blocco `## ROUTING CONTESTUALE — LEGGI PRIMA`
  come prima sezione del corpo, prima di `## Regola fondamentale`. Il blocco instrada esplicitamente
  Agent-Git alla sezione "Override per Agent-Git" e gli altri agenti alla regola di divieto,
  eliminando l'ambiguità dell'override testuale implicito per modelli conservativi (GPT-5 mini).

## [v1.8.0] - 2026-03-26

### Added

- `.github/templates/project.md`, `coding_plan.md`, `report.md`, `todo_task.md`,
  `todo_coordinator.md`, `readme_folder.md`: sei template framework operativi per il
  sistema di tracciamento documenti. Struttura H2 fissa (`## Metadati`, `## Contenuto`,
  `## Stato Avanzamento`) in tutti i template tranne `readme_folder.md` (parametrico
  con 6 placeholder). `todo_coordinator.md` usato solo al bootstrap iniziale di
  `docs/TODO.md`; dopo il bootstrap il file reale viene aggiornato direttamente.
- `.github/skills/docs_manager.skill.md`: skill operativa per la gestione documenti.
  Definisce path del sistema (unica fonte di verità), distinzione tra template
  framework e template utente, convenzione naming `AAAA-MM-GG_slug.md`, flusso
  salvataggio per tipo, regole idempotenza coordinatore su path relativo, regola
  additiva (no overwrite), sequenza bootstrap strettamente additiva e portabile.

### Changed

- `.github/agents/Agent-Welcome.md`: aggiunto OP-3 "Bootstrap Struttura Documentazione"
  con flusso a due rami (S = bootstrap additivo, N = salta). Aggiunto riferimento
  a `docs_manager.md` nella sezione Riferimenti Skills.

### Docs

- `.github/AGENTS.md`: aggiunta `style-setup` alla riga `Agent-Helper` (documentazione interna aggiornata).
- `.github/AGENTS.md`: aggiornata voce Agent-Welcome con menzione OP-3 e skill docs_manager.
- `.github/skills/README.md`: aggiunta `docs_manager.md` alla lista skill e alla tabella agenti.

## [v1.7.1] - 2026-03-26

### Added

- `style-setup.skill.md`: skill condivisa per presentazione e selezione guidata
  dei parametri `verbosity` e `personality`. Definisce il formato di output per
  valori correnti, opzioni disponibili e branching salta/personalizza. Usata da
  Agent-Welcome in OP-1/OP-2 e da Agent-Helper in modalità read-only. La sezione
  di scrittura è autorizzata solo per Agent-Welcome durante OP-1 o OP-2.

### Docs

- `skills/README.md`: aggiunti `verbosity.skill.md`, `personality.skill.md`,
  `style-setup.skill.md` mancanti dall'elenco; aggiornata tabella agente→skills
  con colonne verbosity e personality per tutti gli agenti.
- `instructions/README.md`: aggiunte `verbosity.instructions.md` e
  `personality.instructions.md` mancanti dall'elenco.
- `.github/README.md`: aggiornata versione a v1.7.0 — 26 Marzo 2026,
  conteggio agenti da 12 a 14, riferimento AGENTS.md allineato.

## [v1.7.0] - 2026-03-26

- chore(framework): improve verbosity/personality discoverability — Agent-Welcome, Agent-Helper

### Added

- `framework-guard.skill.md`, `framework-guard.instructions.md`, `framework-unlock.prompt.md`: introducono il sistema Framework Guard con blocco standardizzato dei path protetti, sblocco temporaneo esplicito e workflow di ripristino automatico del flag di sicurezza.
- `verbosity.skill.md`, `verbosity.instructions.md`, `verbosity.prompt.md` e `project-profile.md`: introducono il sistema di verbosita del framework con profili canonici, cascata di risoluzione, valore globale persistente e aggiornamento controllato per gli agenti conversazionali.
- `personality.skill.md`, `personality.instructions.md` e `personality.prompt.md`: introducono il sistema di personality del framework come secondo asse comunicativo, separato da verbosity, con profili canonici, cascata di risoluzione e aggiornamento controllato del valore globale.

### Changed

- `git-commit.prompt.md` e `git-merge.prompt.md`: rimossi `model: gpt-5-mini` e blocco `tools: - agent` dal frontmatter; delegazione ad Agent-Git rafforzata; aggiunto comportamento esplicito di INTERROMPI in caso di Agent-Git non disponibile.
- `AGENTS.md`, `copilot-instructions.md`, `verbosity.skill.md` e `Agent-Git.md`: allineano la documentazione del framework ai comportamenti reali dei prompt comunicativi e esplicitano il prerequisito di `#framework-unlock` per `#verbosity` e `#personality`.
- `Agent-Welcome.md` e `Agent-Docs.md`: chiariscono l'eccezione di scrittura per `project-profile.md` nel setup.
- `Agent-Helper.md`: aggiornate dichiarazioni comunicative tramite procedura controllata `#framework-unlock`.

## [v1.6.1] - 2026-03-25

### Added

- `scripts/git_runner.py`: nuovo script wrapper CLI Python per operazioni git di Agent-Git.

### Changed

- Normalizzazioni e fix minori su prompt e skills relativi a git e frontmatter.

## [v1.6.0] - 2026-03-24

### Added

- `scripts/git_runner.py`: nuovo script wrapper CLI Python per operazioni git di Agent-Git (dettagli tecnici nel changelog completo).

---

