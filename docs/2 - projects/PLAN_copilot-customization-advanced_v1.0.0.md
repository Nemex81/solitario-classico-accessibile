# PLAN — Copilot Pro Advanced Customization

## Executive Summary

| Campo | Valore |
|---|---|
| **Tipo** | Enhancement / Infrastructure |
| **Priorità** | Alta |
| **Stato** | DRAFT — in attesa di convalida |
| **Branch target** | `feature/copilot-advanced-customization` |
| **Versione target** | nessuna (infrastructure-only, nessuna modifica a `.py`) |
| **Autore piano** | Perplexity AI (da convalidare con Copilot + utente) |
| **Data creazione** | 2026-03-07 |
| **Data ultima revisione** | 2026-03-07 |

---

## Contesto e Problema

### Situazione attuale

Il repository usa già `.github/copilot-instructions.md` come file di istruzioni globali per Copilot. Il file è solido e completo (~25KB, ~700 righe), ma presenta un problema architetturale: è un **monolite cognitivo**.

Copilot carica l'intero file ad ogni sessione, indipendentemente dal contesto. Quando un agente lavora su `src/domain/entities/card.py`, porta in contesto anche le regole di branching Git, i protocolli di accessibilità wxPython e i template per la documentazione — che in quel momento sono rumore puro.

### Strumenti disponibili non usati

GitHub Copilot Pro supporta sei livelli di customizzazione. Attualmente ne viene usato uno solo:

| Strumento | Stato attuale | Gap |
|---|---|---|
| `copilot-instructions.md` (globale) | ✅ Attivo, completo | Troppo denso — 25KB monolite |
| Path-specific instructions (`*.instructions.md`) | ❌ Non usato | Nessun contesto layer-specifico |
| Prompt files (`*.prompt.md`) | ❌ Non usato | Procedure manuali non automatizzate |
| Custom agents (`AGENT-NAME.md`) | ❌ Non usato | Nessuna specializzazione per ruolo |
| Agent skills | ❌ Non usato | Script pre-commit non agganciati |
| MCP server config | ⚠️ Implicito | Non dichiarato nel repo |

### Obiettivo del piano

Decomporre le istruzioni Copilot in unità contestuali precise, automatizzare le procedure ripetitive del workflow, e creare agenti specializzati per i task ricorrenti più costosi in termini di attenzione cognitiva.

**Risultato atteso:** Copilot riceve istruzioni pertinenti al contesto corrente (non l'intero manuale), le procedure DESIGN/PLAN/TODO diventano comandi singoli, i check di accessibilità e documentazione vengono eseguiti da agenti dedicati senza ripetere ogni volta il briefing.

---

## Analisi dei Rischi

| Rischio | Probabilità | Impatto | Mitigazione |
|---|---|---|---|
| Conflitti tra istruzioni globali e path-specific | Media | Alto | Rimuovere dal globale ogni sezione migrata a path-specific |
| Prompt files che contraddicono le istruzioni globali | Bassa | Medio | Ogni prompt file include riferimento esplicito alle regole globali |
| Agente che bypassa il TODO Gate | Media | Alto | TODO Gate replicato nei custom agent rilevanti |
| Regressione nel flusso esistente | Bassa | Alto | Nessun file `.py` viene modificato — solo infrastruttura Copilot |

---

## File Coinvolti

### File da CREARE

```
.github/
├── instructions/
│   ├── domain.instructions.md          # Regole layer Domain
│   ├── application.instructions.md     # Regole layer Application
│   ├── ui.instructions.md              # Regole UI/wxPython + accessibilità
│   ├── tests.instructions.md           # Regole testing + pytest markers
│   └── docs.instructions.md            # Regole documentazione + protocollo DESIGN/PLAN/TODO
├── prompts/
│   ├── crea-design-doc.prompt.md       # Procedura creazione DESIGN document
│   ├── crea-plan.prompt.md             # Procedura creazione PLAN di implementazione
│   ├── accessibility-review.prompt.md  # Checklist accessibilità NVDA/keyboard
│   ├── genera-unit-tests.prompt.md     # Generazione test unitari da firma metodo
│   └── sync-docs.prompt.md             # Allineamento API.md + ARCHITECTURE.md + CHANGELOG.md
└── agents/
    ├── accessibility-auditor.md        # Agente specializzato in audit accessibilità
    └── docs-sync.md                    # Agente specializzato in sincronizzazione docs
```

### File da MODIFICARE

```
.github/copilot-instructions.md         # MODIFY: rimozione sezioni migrate, aggiunta indice e link
```

### File da NON TOCCARE

- Qualsiasi file `.py` in `src/`
- Qualsiasi file in `tests/`
- `docs/API.md`, `docs/ARCHITECTURE.md`, `docs/CHANGELOG.md`, `docs/README.md`
- `requirements.txt`, `pyproject.toml`, `pytest.ini`, `mypy.ini`

---

## Fasi di Implementazione

### FASE 1 — Scaffolding directory e refactor globale

**Obiettivo:** creare la struttura cartelle `.github/instructions/`, `.github/prompts/`, `.github/agents/` e snellire il file globale.

**Step 1.1 — Crea le directory (file placeholder)**
- Crea `.github/instructions/.gitkeep`
- Crea `.github/prompts/.gitkeep`
- Crea `.github/agents/.gitkeep`

**Step 1.2 — Refactor `copilot-instructions.md`**

Rimuovere le sezioni che verranno migrate a file specifici. Il file globale deve diventare un **hub di navigazione** con:
- Profilo utente e vincoli trasversali (NVDA, Windows 11, VSCode)
- Naming conventions (trasversali a tutti i layer)
- Logging categorizzato (trasversale)
- Git conventions e branch workflow (trasversali)
- Critical Warnings (trasversali — mai spostare)
- Indice con link ai file path-specific

**Sezioni da rimuovere dal globale (migrate a path-specific):**
- Sezione `Clean Architecture` dettaglio layer → `domain.instructions.md` + `application.instructions.md`
- Sezione `Accessibilità UI (WAI-ARIA + Keyboard)` → `ui.instructions.md`
- Sezione `Testing e Validazione` completa → `tests.instructions.md`
- Sezione `Protocollo Allineamento Documentazione` completa → `docs.instructions.md`
- Sezione `Pre-Commit Checklist` → `docs.instructions.md`

**Commit:** `docs(github): refactor copilot-instructions.md in hub di navigazione`

---

### FASE 2 — Path-specific instructions

**Obiettivo:** ogni layer ha istruzioni dedicate che si attivano solo quando Copilot lavora in quel contesto.

#### File 1: `.github/instructions/domain.instructions.md`

**applyTo:** `src/domain/**`

**Contenuto:**
- Regole Clean Architecture per il Domain layer (zero dipendenze esterne)
- Lista import vietati con esempi di errore/corretto
- Type hints enforcement per entity e value objects
- Regola `pile.get_card_count()` vs `pile.count()` (critical bug warning)
- Pattern per domain services (ritornano dati, mai UI)
- Guest Profile Protection (`profile_000`)
- Logging: solo dependency injection nel Domain, mai `logging.getLogger` diretto

**Commit:** `docs(github): aggiunge domain.instructions.md per layer Domain`

---

#### File 2: `.github/instructions/application.instructions.md`

**applyTo:** `src/application/**`

**Contenuto:**
- Ruolo del layer Application (use cases, orchestrazione, command patterns)
- Dipendenze consentite: solo da Domain
- Game engine patterns: GameEngine come orchestratore, non come domain service
- Timer Overtime distinzione: `EndReason.VICTORY` vs `EndReason.VICTORY_OVERTIME`
- Draw Count Duality: `GameService.draw_count` vs `ScoringService.stock_draw_count`
- Logging: `_game_logger` e `_timer_logger` come logger primari

**Commit:** `docs(github): aggiunge application.instructions.md per layer Application`

---

#### File 3: `.github/instructions/ui.instructions.md`

**applyTo:** `src/infrastructure/ui/**`, `src/presentation/**`

**Contenuto:**
- Regola: `wx` importabile solo in questo perimetro
- Checklist accessibilità obbligatoria (SetLabel, SetTitle, SetFocus, ESC, TAB)
- No business logic nei dialog
- No jargon visivo nei testi UI (screen reader unfriendly)
- Pattern focus management per NVDA
- TTS feedback: quando e come usarlo
- Logger da usare: `_ui_logger`

**Commit:** `docs(github): aggiunge ui.instructions.md per UI/accessibilità`

---

#### File 4: `.github/instructions/tests.instructions.md`

**applyTo:** `tests/**`

**Contenuto:**
- Test coverage minimum (85% domain + application, 90% globale)
- Naming convention test: `test_<method>_<scenario>_<expected_behavior>`
- Marker obbligatori: `@pytest.mark.unit` vs `@pytest.mark.gui`
- Fixture pattern con `tmp_path`
- Isolamento logging: fixture `reset_logging` obbligatoria per test che chiamano `setup_logging()`
- Riferimento canonico: `tests/infrastructure/test_categorized_logger.py`
- Comandi standard: `pytest -m "not gui" -v` per CI-safe

**Commit:** `docs(github): aggiunge tests.instructions.md per convenzioni testing`

---

#### File 5: `.github/instructions/docs.instructions.md`

**applyTo:** `docs/**`, `.github/**`

**Contenuto:**
- Struttura cartella `docs/` con ruolo di ogni sottocartella
- Protocollo DESIGN/PLAN/TODO completo (flusso canonico)
- Quando creare DESIGN vs PLAN vs TODO (trigger conditions)
- Pre-Commit Checklist completa (6 check)
- Trigger events per aggiornamento docs (API.md, ARCHITECTURE.md, CHANGELOG.md, README.md)
- Formato SemVer e release process

**Commit:** `docs(github): aggiunge docs.instructions.md per protocollo documentazione`

---

### FASE 3 — Prompt files

**Obiettivo:** trasformare le procedure più ripetitive del workflow in comandi singoli attivabili da chat.

#### File 1: `.github/prompts/crea-design-doc.prompt.md`

**Scopo:** Guida Copilot attraverso la creazione di un DESIGN document completo a partire da una descrizione feature dell'utente.

**Workflow interno al prompt:**
1. Chiedi all'utente: feature slug, versione target, problema da risolvere
2. Leggi `docs/1 - templates/TEMPLATE_example_DESIGN_DOCUMENT.md`
3. Genera il file `docs/2 - projects/DESIGN_<slug>.md` compilato
4. Proponi i prossimi step (convalida → PLAN)

**Commit:** `docs(github): aggiunge prompt crea-design-doc`

---

#### File 2: `.github/prompts/crea-plan.prompt.md`

**Scopo:** Genera un PLAN di implementazione completo a partire da un DESIGN approvato o da una descrizione diretta.

**Workflow interno al prompt:**
1. Chiedi: DESIGN doc di riferimento (o descrizione diretta), versione target, branch
2. Leggi `docs/1 - templates/TEMPLATE_example_PIANO_IMPLEMENTAZIONE.md`
3. Identifica file coinvolti per layer
4. Genera il file `docs/2 - projects/PLAN_<slug>_vX.Y.Z.md` con fasi sequenziali
5. Propone la creazione del TODO come passo successivo

**Commit:** `docs(github): aggiunge prompt crea-plan`

---

#### File 3: `.github/prompts/accessibility-review.prompt.md`

**Scopo:** Audit accessibilità NVDA/keyboard su un file o componente UI indicato dall'utente.

**Workflow interno al prompt:**
1. Richiedi il file o la classe da analizzare
2. Applica checklist: SetLabel, SetTitle, SetFocus, ESC, TAB, acceleratori
3. Verifica assenza di jargon visivo nelle stringhe
4. Verifica che `_ui_logger` sia usato (non print)
5. Produce report testuale strutturato: OK / WARN / FAIL per ogni check

**Commit:** `docs(github): aggiunge prompt accessibility-review`

---

#### File 4: `.github/prompts/genera-unit-tests.prompt.md`

**Scopo:** Genera test unitari completi per un metodo o una classe indicata.

**Workflow interno al prompt:**
1. Richiedi file sorgente e nome metodo/classe
2. Identifica layer (domain/application → `@pytest.mark.unit`; ui → `@pytest.mark.gui`)
3. Leggi signature e docstring del metodo
4. Genera classe test con: fixture setup, happy path, edge cases, error cases
5. Verifica naming convention `test_<method>_<scenario>_<expected>`
6. Stima coverage incrementale

**Commit:** `docs(github): aggiunge prompt genera-unit-tests`

---

#### File 5: `.github/prompts/sync-docs.prompt.md`

**Scopo:** Esegue l'audit documentazione post-modifica e propone aggiornamenti a API.md, ARCHITECTURE.md, CHANGELOG.md.

**Workflow interno al prompt:**
1. Chiedi: lista file `.py` modificati nell'ultima sessione
2. Per ogni file: verifica presenza in `docs/API.md`
3. Verifica se struttura o data flow è cambiata → propone update `ARCHITECTURE.md`
4. Chiede tipo di modifica (feat/fix/refactor) → prepara entry `CHANGELOG.md`
5. Produce riepilogo testuale: "N documenti da aggiornare, M già sincronizzati"

**Commit:** `docs(github): aggiunge prompt sync-docs`

---

### FASE 4 — Custom agents

**Obiettivo:** agenti con identità specializzata per task che richiedono un focus esclusivo e un set di regole ristretto.

#### Agent 1: `.github/agents/accessibility-auditor.md`

**Nome:** `accessibility-auditor`

**Identità:** Specialista di accessibilità per applicazioni wxPython con utenti non vedenti che usano NVDA su Windows 11. Ignora completamente architettura, business logic e performance. Guarda solo il codice dal punto di vista di un utente con screen reader.

**Capabilities:**
- Analisi statica di file `.py` con componenti wx
- Verifica checklist WAI-ARIA adattata a wxPython
- Test keyboard navigation flow
- Verifica stringhe TTS (no gergo visivo, no emoji, no ASCII art)
- Suggerisce acceleratori mancanti
- Segnala focus trap e focus loss

**Output format:** report testuale strutturato con severity FAIL / WARN / OK, navigabile con screen reader (no tabelle complesse, no ASCII box).

**Commit:** `docs(github): aggiunge agente accessibility-auditor`

---

#### Agent 2: `.github/agents/docs-sync.md`

**Nome:** `docs-sync`

**Identità:** Guardiano della documentazione. Non scrive codice. Legge file `.py` modificati, confronta con la documentazione esistente, identifica gap e propone aggiornamenti puntuali.

**Capabilities:**
- Diff tra signature attuali e quelle in `docs/API.md`
- Rilevamento di nuovi moduli non documentati
- Generazione entry CHANGELOG.md in formato corretto
- Verifica cross-references tra docs (link rotti, anchor mancanti)
- Aggiornamento `docs/TODO.md` post-commit

**Vincolo esplicito:** non propone mai modifiche a file `.py`. Se rileva un bug durante la lettura del codice, lo segnala come osservazione separata ma non genera codice.

**Commit:** `docs(github): aggiunge agente docs-sync`

---

## Test Plan

Questo piano non modifica codice Python, quindi non genera test unitari. La validazione è operativa:

| Check | Come verificare | Responsabile |
|---|---|---|
| Path-specific instructions attive | Aprire un file in `src/domain/`, chiedere a Copilot una modifica e verificare che rispetti le regole domain-specific | Utente |
| Prompt files disponibili | In VS Code, `@workspace /crea-design-doc` deve essere riconosciuto | Utente |
| Agenti disponibili | In Copilot chat, `@accessibility-auditor` deve rispondere con identità corretta | Utente |
| Monolite snellito | `copilot-instructions.md` deve essere < 8KB dopo la migrazione | Verifica dimensione file |
| Nessuna regressione logica | Le regole trasversali (naming, logging, critical warnings) devono rimanere nel globale | Review manuale |

---

## Criteri di Completamento

- [ ] Directory `.github/instructions/`, `.github/prompts/`, `.github/agents/` create
- [ ] 5 file `*.instructions.md` creati e verificati
- [ ] 5 file `*.prompt.md` creati e verificati
- [ ] 2 file agente creati e verificati
- [ ] `copilot-instructions.md` refactorizzato come hub (< 8KB)
- [ ] Nessun file `.py` modificato
- [ ] Nessuna entry in CHANGELOG.md richiesta (infrastructure-only)
- [ ] Validazione operativa completata (4 check nella tabella Test Plan)

---

## Ordine di Commit Raccomandato

```
1. docs(github): refactor copilot-instructions.md in hub di navigazione
2. docs(github): aggiunge domain.instructions.md per layer Domain
3. docs(github): aggiunge application.instructions.md per layer Application
4. docs(github): aggiunge ui.instructions.md per UI/accessibilità
5. docs(github): aggiunge tests.instructions.md per convenzioni testing
6. docs(github): aggiunge docs.instructions.md per protocollo documentazione
7. docs(github): aggiunge prompt crea-design-doc
8. docs(github): aggiunge prompt crea-plan
9. docs(github): aggiunge prompt accessibility-review
10. docs(github): aggiunge prompt genera-unit-tests
11. docs(github): aggiunge prompt sync-docs
12. docs(github): aggiunge agente accessibility-auditor
13. docs(github): aggiunge agente docs-sync
```

**Nota:** i commit 2-6 (path-specific instructions) possono essere eseguiti in parallelo se si lavora su branch separati. I commit 7-11 (prompt files) sono indipendenti tra loro. I commit 12-13 (agenti) richiedono che il refactor del globale (commit 1) sia già completato per evitare duplicazioni.

---

## Istruzioni per Convalida con Copilot (Claude Sonnet 4.6 / Opus)

Per sottoporre questo piano a revisione critica, usa questo prompt nel chat Copilot:

```
Leggi il file docs/2 - projects/PLAN_copilot-customization-advanced_v1.0.0.md

Esegui una revisione critica del piano con focus su:
1. Conflitti potenziali tra istruzioni globali e path-specific (sezione FASE 1 e FASE 2)
2. Completezza dei prompt files: mancano scenari d'uso rilevanti?
3. Scope degli agenti: sono troppo ampi o troppo ristretti per essere utili?
4. Ordine di commit: ci sono dipendenze non dichiarate?
5. Rischi non coperti nella tabella Analisi dei Rischi

Produci:
- Lista di problemi critici (bloccanti per l'implementazione)
- Lista di suggerimenti migliorativi (non bloccanti)
- Valutazione complessiva: APPROVED / APPROVED WITH CHANGES / NEEDS REWORK
```
