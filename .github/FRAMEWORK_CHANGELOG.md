<!-- markdownlint-disable MD024 -->

# Framework Copilot — Changelog

Tutte le modifiche rilevanti al Framework Copilot sono documentate qui.
Formato: [Conventional Changelog](https://keepachangelog.com/it/1.0.0/)
Versioning: [SemVer](https://semver.org/lang/it/)

---

## [Unreleased]

### Added

- `.github/templates/`: nuova cartella deposito template
  neutri e resettabili. Convenzione naming: `*.template.md`.
  Proprietà: Agent-FrameworkDocs (manutenzione),
  Agent-Welcome (lettura). README.md interno con tabella
  file presenti e regole di accesso.
- `.github/templates/project-profile.template.md`:
  template neutro del profilo progetto. Frontmatter YAML
  completo con tutti i campi vuoti e `initialized: false`.
  Struttura Markdown con placeholder. Sorgente canonica per
  Agent-Welcome in OP-1 e OP-2. Elimina la duplicazione
  della struttura inline in project-profile.skill.md.
- `workflow-standard.instructions.md`: nuova instruction contestuale
  (applyTo: `**`) — centralizza la sequenza operativa standard per
  ogni richiesta di modifica: TODO gate, pre-commit checklist 6 passi,
  regole sync documentazione, feedback strutturato. Estratta da
  copilot-instructions.md per alleggerirlo.
- `Agent-Helper.md`: nuovo agente consultivo read-only sul Framework
  Copilot. Risponde a domande su agenti, prompt, skill, istruzioni e
  struttura del framework. Non modifica file, non esegue comandi git.
  Scope esclusivo: lettura di .github/. Modelli: Claude Sonnet 4.6,
  gpt-5-mini. Invocabile dal dropdown agenti.
- `framework-query.skill.md`: nuova skill — contratto output per
  risposte descrittive (Pattern 1), comparative (Pattern 2) e
  di workflow (Pattern 3) su componenti del framework.
  Referenziata da Agent-Helper.
- `framework-index.skill.md`: nuova skill — sequenza di lettura
  obbligatoria (6 file) e formato indice navigabile per costruire
  una panoramica completa del framework. Riutilizzabile da
  Agent-Helper e Agent-Orchestrator.
- `agent-selector.skill.md`: nuova skill — routing deterministico
  per selezione agente dato un task o una domanda. Pattern matching
  con regola "prima corrispondenza vince". Riutilizzabile da
  Agent-Helper e Agent-Orchestrator.
- `framework-scope-guard.skill.md`: nuova skill — limiti operativi
  e risposte standard per agenti read-only. Definisce path autorizzati
  in lettura, azioni vietate e blocchi di risposta standardizzati.
  Referenziata da Agent-Helper.
- `project-profile.md`: nuovo file — source of truth
  profilo progetto. Frontmatter YAML con campo
  `initialized` in prima riga per intercettazione
  rapida dello stato. Distribuito con initialized: false.
  Compilato da Agent-Welcome in OP-1.
- `Agent-Welcome.md`: nuovo agente — setup iniziale
  e aggiornamento profilo progetto. Flusso guidato
  in 7 passi con conferma riepilogo prima di scrivere
  qualsiasi file. Modelli gpt-5-mini e Raptor mini.
  Non partecipa al ciclo E2E. Delega git ad Agent-Git.
- `project-profile.skill.md`: nuova skill — struttura
  canonica project-profile.md, matrice componenti
  per linguaggio (Python, C/C++, JS, TS, C#, generico),
  template instructions per linguaggi non-Python.
  Referenziata da Agent-Welcome.
- `project-setup.prompt.md`: nuovo prompt — entry point
  setup iniziale framework. Nessun input richiesto.
  Flusso guidato gestito da Agent-Welcome OP-1.
  Da eseguire come primo comando su qualsiasi progetto.
- `project-update.prompt.md`: nuovo prompt — entry point
  aggiornamento profilo progetto. Input opzionale:
  se vuoto mostra help con esempi d'uso. Delega
  ad Agent-Welcome OP-2.
- `project-init-gate.instructions.md`: nuova instruction
  (applyTo: "**") — gate di inizializzazione attivo
  in tutti i contesti. Intercetta initialized: false
  e guida l'utente al setup con messaggio strutturato.
  Eccezione: Agent-Welcome opera sempre senza blocco.
- `agents/README.md`: nuovo file — indice della cartella
  `.github/agents/` con lista dei 12 agenti in ordine di
  flusso E2E, ruolo sintetico e link ai file agente.
  Allinea la struttura a `skills/README.md` e
  `instructions/README.md`. Colma il riferimento già
  presente in AGENTS.md (sezione Dual-Track Documentation)
  che indicava questo file come esistente.

### Fixed

- `git-policy.instructions.md`: aggiunta sezione "Override per
  Agent-Git" con priorità esplicita. Risolve il conflitto tra
  blocco globale applyTo:"**" e autorizzazione Agent-Git, che
  causava output di comandi manuali invece dell'esecuzione
  tramite run_in_terminal.
- `git-commit.prompt.md`: aggiunto run_in_terminal alla lista
  tools del frontmatter. Risolve il fallimento al passo 1
  (git status) del workflow dispatcher.
- `git-execution.skill.md`: corretti delimitatori frontmatter
  da *** a ---. Risolve il mancato parsing YAML da parte di
  VS Code che rendeva la skill invisibile come contesto
  strutturato.
- `git-commit.prompt.md`: aggiunto supporto parametro opzionale
  PUSH. Se l'utente avvia il prompt senza parametri esegue solo
  OP-2 (commit). Se avvia con parametro PUSH, dopo il commit
  Agent-Git avvia automaticamente OP-3 (push) procedendo
  direttamente al gate di conferma "PUSH" maiuscolo, senza
  chiedere conferma intermedia. Aggiunto run_in_terminal ai tools
  e input opzionale push_flag nel frontmatter.
- `Agent-Git.md`: ridotte conferme interattive in OP-2 e OP-3.
  Changelog ora applicato automaticamente in entrambe le modalità.
  Introdotta distinzione modale:
  SOLO_COMMIT (default): conferma messaggio commit mantenuta,
  gate "PUSH" maiuscolo mantenuto.
  COMMIT_E_PUSH (parametro PUSH dal dispatcher): messaggio commit
  applicato automaticamente, push eseguito senza gate,
  riepilogo finale obbligatorio. Totale interazioni: 0.

### Changed

- `project-profile.skill.md`: sezione "Struttura Canonica"
  convertita da definizione inline a puntatore a
  `.github/templates/project-profile.template.md`.
  Aggiunta sezione "Procedura di Caricamento Template"
  con 5 passi espliciti. Matrice componenti e template
  instructions invariati. Campo `description` frontmatter
  aggiornato con riferimento al template.
- `file-deletion-guard.skill.md`: aggiunta sezione
  "Distinzione: cancellazione vs sovrascrittura controllata".
  Definisce le condizioni (3 punti) sotto cui Agent-Welcome
  può sovrascrivere project-profile.md senza attivare
  il gate ELIMINA. Campo `used_by` aggiornato con
  Agent-Welcome.
- `Agent-Welcome.md`: OP-1 Passo 5 e OP-2 Passo 5
  aggiornati per caricare il template canonico come
  sorgente della struttura invece di ricostruirla
  dalla skill. Logica del flusso e regole invarianti
  invariate.
- `project-setup.prompt.md`: corpo prompt riscritto
  con riferimento esplicito al template canonico.
  Condizione di attivazione OP-1 ora copre esplicitamente
  entrambi i casi: file assente e initialized: false.
  Struttura a tre rami distinti per maggiore leggibilità.
- `copilot-instructions.md`: refactor alleggerimento. Rimossi blocchi
  ridondanti (TODO Gate, Pre-Commit Checklist, Convenzioni Git inline,
  lista skill). Sostituiti con rimandi a components già esistenti o a
  workflow-standard.instructions.md. Dimensione stimata: da ~10.446 a
  ~7.000 bytes. Funzionalità invariata per delega a instructions e skill.
- `Agent-Git.md`: refactor OP-2 — logica generazione voce
  CHANGELOG estratta in changelog-entry.skill.md (nuovo),
  logica messaggio commit ora referenzia esplicitamente
  conventional-commit.skill.md. Comportamento invariato,
  corpo agente alleggerito. Sezione Riferimenti Skills
  aggiornata con changelog-entry.
- `skills/README.md`: aggiunta changelog-entry.skill.md
  a lista skills e tabella agenti.
- `AGENTS.md`: aggiornata sezione Agent Skills — aggiunta
  `file-deletion-guard.skill.md` e `changelog-entry.skill.md`
  alla lista testuale. Tabella agenti allineata alla tabella
  completa in skills/README.md (tutte le 12 righe agenti).
- `copilot-instructions.md`: aggiunta sezione
  "Contesto Progetto" in prima posizione. Trigger
  gate inizializzazione con riferimento a
  project-init-gate.instructions.md. Riferimento
  dinamico a project-profile.md come source of truth.
- `AGENTS.md`: contatore aggiornato da 12 a 13 agenti (Agent-Welcome);
  da 13 a 14 agenti (Agent-Helper). Aggiunta voce Agent-Helper
  in cima alla lista, nuove skill e riga tabella Agent-Helper.
  Sezione Instructions Files arricchita con project-init-gate.
- `copilot-instructions.md`: contatore aggiornato a 14 agenti.
  Aggiunte voci 0 Agent-Helper e 0 Agent-Welcome nella lista agenti.
  Tabella Componenti Framework allineata a 14 agenti.
- `agents/README.md`: aggiunta riga Agent-Helper in prima posizione.
- `skills/README.md`: aggiunte 4 skill framework (framework-query,
  framework-index, agent-selector, framework-scope-guard) a lista
  e tabella agente/skill.
  Agent-Welcome aggiunto in cima alla lista.
  project-profile.skill.md aggiunta a lista skills
  e tabella agenti.

## [v1.6.0] - 2026-03-23

### Added

- `Agent-CodeRouter`: nuovo agente dispatcher del sotto-ciclo di codifica.
  Riceve task da Agent-Orchestrator (Fase 4), classifica ogni fase del TODO
  come GUI o non-GUI tramite code-routing.skill.md, delega ad Agent-CodeUI
  o Agent-Code, verifica completamento e aggiorna docs/TODO.md.
  Non scrive codice direttamente.
- `Agent-CodeUI`: nuovo agente specializzato implementazione GUI wxPython
  con accessibilità NVDA obbligatoria. Sub-agente di Agent-CodeRouter.
  Ogni componente UI deve superare checklist validate-accessibility.skill.md
  (7 punti WAI-ARIA + requisiti NVDA) prima del commit.
  Scope commit obbligatorio: presentation.
- `code-routing.skill.md`: skill atomica con regole di classificazione
  deterministiche (pattern matching) per discriminare fasi GUI da fasi non-GUI.
  Gestisce caso ambiguo con prompt strutturato all'utente.
  Espandibile per nuovi agenti specializzati senza modificare Agent-CodeRouter.
- `ui.instructions.md`: instruction file contestuale per `src/presentation/**/*.py`.
  Regole obbligatorie wxPython: SetTitle, SetLabel, SetFocus, TAB order,
  ESC handling, requisiti NVDA, logging apertura/chiusura dialog, marker pytest.gui.
- `file-deletion-guard.skill.md`: nuova skill di protezione contro
  eliminazione non autorizzata di file. Procedura obbligatoria con
  blocco di conferma esplicita (keyword ELIMINA) prima di qualsiasi
  operazione di eliminazione file, inclusi merge con conflitti,
  git rm e git clean. Referenziata da Agent-Git, Agent-Code,
  Agent-FrameworkDocs.
- `.github/instructions/model-policy.instructions.md`: nuova istruzione
  contestuale (applyTo: `.github/**`) con assegnazioni modello per tutti
  e 12 gli agenti, criteri di selezione per tipo di task, lista modelli
  deprecati e fallback ufficiali.

### Changed

- `Agent-Orchestrator.md`: Fase 4 aggiornata — delega ad Agent-CodeRouter
  invece di Agent-Code direttamente. Aggiunta nota sul sotto-ciclo interno.
- `scripts/detect_agent.py`: Agent-Code rinominato in Agent-CodeRouter nei keyword.
  Aggiunta voce Agent-CodeUI con keyword UI/wxPython/accessibilità.
  AGENT_PRIORITY aggiornato con nuovo ordine.
- `AGENTS.md`: versione bumped a v1.6.0, conteggio agenti da 10 a 12,
  lista agenti e flusso Fase 4 aggiornati.
- `copilot-instructions.md`: versione bumped a v1.6.0, tabella componenti
  e lista skills aggiornate con nuovi file.
- `skills/README.md`: aggiunta code-routing.skill.md e tabella agenti aggiornata
  con Agent-CodeRouter e Agent-CodeUI.
- `instructions/README.md`: aggiunta ui.instructions.md.
- `README.md`: versione bumped a v1.6.0, conteggio agenti aggiornato a 12,
  struttura cartelle aggiornata con skills/ e instructions/.
- `model-policy.instructions.md`: aggiunta Agent-CodeRouter e Agent-CodeUI
  nella tabella assegnazioni modello.
- `git-policy.instructions.md`: aggiunta sezione "Protezione eliminazione file"
  con riferimento a file-deletion-guard.skill.md.
- `Agent-Git.md`: aggiunto riferimento a file-deletion-guard.skill.md
  in Riferimenti Skills e Regole Invarianti.
- Model policy: aggiornati `model` e `fallbackModels` nel frontmatter
  di tutti e 12 gli agenti. Rimosso gpt-4o (legacy) come default universale.
- `copilot-instructions.md`: aggiunta sezione `## Model Policy` leggera
  con rimando a model-policy.instructions.md.

## [v1.5.1] - 2026-03-22

### Added

- `git-policy.instructions.md`: policy git dettagliata con comandi
  vietati, consentiti e procedure per agenti. applyTo: `**`.
- `git-execution.skill.md`: matrice autorizzazioni comandi git per
  contesto (agenti, git-commit.prompt.md, git-merge.prompt.md).
- `instructions/README.md`: documentazione instructions files con
  lista, scopo e meccanismo di attivazione.
- `skills/README.md`: documentazione skills con lista completa e
  tabella agenti/skills associate.
- `Agent-Git`: agente dedicato operazioni git (commit, push, merge, tag).
  Modello gpt-5-mini. Unico punto autorizzato all'esecuzione git diretta.
  Invocabile da dropdown, da git-commit.prompt.md, git-merge.prompt.md
  e da Agent-Orchestrator tramite subagent delegation.
- Riferimenti: git-execution.skill.md, conventional-commit.skill.md,
  accessibility-output.skill.md.

### Changed

- `copilot-instructions.md`: sezione Git policy espansa con eccezioni
  autorizzate e riferimenti a instructions e skill.
- `git-commit.prompt.md`: aggiunta dichiarazione autorizzazione git
  esplicita in testa al file con riferimenti a policy e skill.
- `git-merge.prompt.md`: aggiunta dichiarazione autorizzazione git
  esplicita in testa al file con riferimenti a policy e skill.
- Agent-Code: aggiunto riferimento a `git-execution.skill.md`.
- Agent-Orchestrator: sostituita regola git inline con riferimento
  a `git-execution.skill.md`.
- `.github/README.md`: aggiunta sezione Git Policy con descrizione
  struttura a 3 livelli.
- `git-commit.prompt.md`: refactored in dispatcher leggero.
  Logica operativa spostata in Agent-Git. Model: gpt-5-mini.
- `git-merge.prompt.md`: refactored in dispatcher leggero.
  Logica operativa spostata in Agent-Git. Model: gpt-5-mini.
- `copilot-instructions.md`: git policy aggiornata con Agent-Git
  come contesto autorizzato principale.
- `git-policy.instructions.md`: aggiunta sezione Agent-Git
  tra i contesti autorizzati.
- `git-execution.skill.md`: aggiunta matrice autorizzazioni Agent-Git.
- `Agent-Orchestrator`: aggiunto riferimento a Agent-Git per
  subagent delegation nei checkpoint git del workflow E2E.
- `AGENTS.md`: conteggio agenti da 9 a 10, Agent-Git aggiunto.
- `.github/README.md`: sezione Git Policy aggiornata.
- `Agent-Release.md`: passo 4 "CREATE GIT TAG" aggiornato per
  delegare ad Agent-Git (OP-5) invece di proporre testo generico.
  Aggiunte Regole Operative coerenti con git policy centralizzata.
  Aggiunto riferimento a git-execution.skill.md.
- `Agent-Orchestrator.md`: ripristinato da git history e aggiornato
  con modifiche v1.5.1 (riferimento Agent-Git, git-execution.skill.md).
- `Agent-Git.md`: fix frontmatter — delimitatori corretti da `***` a `---`.

### Fixed

- `Agent-Release.md`: ripristinate etichette descrittive nella sezione
  "Riferimenti Skills" per semver-bump e accessibility-output.
  Formattazione uniformata alle altre 3 voci della sezione.
- `git-commit.prompt.md`: fix frontmatter — delimitatori corretti
  da `***` a `---`. Model gpt-5-mini e tools ora parsabili da VS Code.
- `git-merge.prompt.md`: fix frontmatter — delimitatori corretti
  da `***` a `---`. Model gpt-5-mini e tools ora parsabili da VS Code.
- `Agent-Git.md`: rimossa ultima occorrenza di `***` come separatore.
  Tutti i separatori ora uniformi a `---`.

### Note tecniche

- `copilot-instructions.md` e `AGENTS.md`: aggiornate anche le
  2 voci mancanti dalla sessione precedente:
  - tabella Componenti Framework: aggiunta riga git-policy.instructions.md
  - lista skills: aggiunta git-execution.skill.md

## [v1.5.0] - 2026-03-22

### Added

- Instructions files: `python.instructions.md`, `tests.instructions.md`,
  `domain.instructions.md` — regole contestuali per filetype attivate
  automaticamente da VS Code Copilot.
- Agent Skills: `validate-accessibility.skill.md`,
  `conventional-commit.skill.md`, `semver-bump.skill.md` — abilità
  atomiche riutilizzabili tra agenti.
- `clean-architecture-rules.skill.md`: regole Clean Architecture 4 layer,
  DI Container, vincoli di dipendenza tra layer.
- `document-template.skill.md`: struttura e frontmatter YAML per documenti
  DESIGN, PLAN e TODO con ciclo di vita stati.
- `accessibility-output.skill.md`: standard output strutturato e accessibile
  per tutti gli agenti del framework.

### Changed

- `copilot-instructions.md`: sezioni Python standards, testing e
  critical warnings migrate nelle instructions contestuali.
  File alleggerito di circa un terzo.
- Framework bumped a v1.5.0.
- Agent-Code: rimossa Pre-Commit Checklist inline e regole duplicate.
  Sostituita con riferimenti a `python.instructions.md`,
  `conventional-commit.skill.md`, `validate-accessibility.skill.md`.
- Agent-Validate: rimossi marker e naming rules inline duplicati.
  Sostituiti con riferimenti a `tests.instructions.md` e
  `validate-accessibility.skill.md`.
- Agent-Release: rimossa logica SemVer inline duplicata.
  Sostituita con riferimento a `semver-bump.skill.md`.
- Agent-Analyze: aggiunta sezione Riferimenti Skills
  (`clean-architecture-rules`, `accessibility-output`).
- Agent-Design: aggiunta sezione Riferimenti Skills
  (`clean-architecture-rules`, `document-template`, `accessibility-output`).
  Rimosse regole duplicate inline.
- Agent-Plan: aggiunta sezione Riferimenti Skills
  (`document-template`, `accessibility-output`).
- Agent-Code: aggiunti riferimenti a `clean-architecture-rules` e
  `accessibility-output` nella sezione esistente.
- Agent-Validate: aggiunto riferimento a `accessibility-output`.
- Agent-Docs: aggiunta sezione Riferimenti Skills
  (`semver-bump`, `accessibility-output`). Fix workflow SemVer inline.
- Agent-Release: aggiunto riferimento a `accessibility-output`.
- Agent-FrameworkDocs: aggiunta sezione Riferimenti Skills
  (`accessibility-output`).
- Agent-Orchestrator: aggiunto riferimento a `accessibility-output`.
- Tutti gli agenti: rimossa la regola inline sull'output testuale
  strutturato accessibile. Centralizzata in `accessibility-output.skill.md`.
- `AGENTS.md` e `copilot-instructions.md`: lista skills aggiornata a 6 voci.

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
