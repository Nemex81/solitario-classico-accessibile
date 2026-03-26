<!-- markdownlint-disable MD024 -->

# Framework Copilot — Changelog

Tutte le modifiche rilevanti al Framework Copilot sono documentate qui.
Formato: [Conventional Changelog](https://keepachangelog.com/it/1.0.0/)
Versioning: [SemVer](https://semver.org/lang/it/)

---

## [Unreleased]

### Added

- `.github/templates/project.md`, `coding_plan.md`, `report.md`, `todo_task.md`,
  `todo_coordinator.md`, `readme_folder.md`: sei template framework operativi per il
  sistema di tracciamento documenti. Struttura H2 fissa (`## Metadati`, `## Contenuto`,
  `## Stato Avanzamento`) in tutti i template tranne `readme_folder.md` (parametrico
  con 6 placeholder). `todo_coordinator.md` usato solo al bootstrap iniziale di
  `docs/TODO.md`; dopo il bootstrap il file reale viene aggiornato direttamente.
- `.github/skills/docs_manager.md`: skill operativa per la gestione documenti.
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

<!-- Le voci non rilasciate vanno inserite qui. Rimane vuoto dopo la release. -->

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

