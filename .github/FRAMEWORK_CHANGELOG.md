<!-- markdownlint-disable MD024 -->

# Framework Copilot — Changelog

Tutte le modifiche rilevanti al Framework Copilot sono documentate qui.
Formato: [Conventional Changelog](https://keepachangelog.com/it/1.0.0/)
Versioning: [SemVer](https://semver.org/lang/it/)

---

## [Unreleased]

<!-- Le voci non rilasciate vanno inserite qui. Rimane vuoto dopo la release. -->

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

