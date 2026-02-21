📋 TODO – Unificazione Sistema di Logging (v3.2.2)
Branch: `refactoring-engine`
Tipo: REFACTOR
Priorità: HIGH
Stato: IN PROGRESS

---

📖 Riferimento Documentazione
Prima di iniziare qualsiasi implementazione, consultare obbligatoriamente:
`docs/3 - coding plans/PLAN-logging-unificazione-v3.2.2.md`

Questo file TODO è solo un sommario operativo da consultare e aggiornare durante ogni fase dell'implementazione.
Il piano completo contiene analisi, architettura, edge case e dettagli tecnici.

---

🤖 Istruzioni per Copilot Agent

Implementare le modifiche in modo **incrementale** su più commit atomici e logici.

**Workflow per ogni fase:**

1. **Leggi questo TODO** → Identifica la prossima fase da implementare
2. **Consulta piano completo** → Rivedi dettagli tecnici, architettura, edge case della fase
3. **Implementa modifiche** → Codifica solo la fase corrente (scope limitato)
4. **Commit atomico** → Messaggio conventional, scope chiaro, riferimento fase
5. **Aggiorna questo TODO** → Spunta checkbox completate per la fase
6. **Acquisisci info sommarie** → Rivedi stato globale prima di proseguire
7. **RIPETI** → Passa alla fase successiva (torna al punto 1)

⚠️ **REGOLE FONDAMENTALI:**

- ✅ **Un commit per fase logica** (no mega-commit con tutto)
- ✅ **Dopo ogni commit**: aggiorna questo TODO spuntando checkbox
- ✅ **Prima di ogni fase**: rileggi sezione pertinente nel piano completo
- ✅ **Approccio sequenziale**: fase → commit → aggiorna TODO → fase successiva
- ✅ **Commit message format**: `type(scope): description [Phase N/M]`
- ❌ **NO commit multipli senza aggiornare TODO** (perde tracciabilità)
- ❌ **NO implementazione completa in un colpo** (viola incrementalità)

---

🎯 Obiettivo Implementazione

- Eliminare TUTTI i `print()` dal codice di produzione (priorità: `acs_wx.py`)
- Collegare tutti gli eventi mancanti al sistema `game_logger`
- Garantire che ogni evento significativo (lifecycle, gameplay, UI, settings, timer, dialogs) sia tracciato su file via `RotatingFileHandler`
- Non modificare logica di gioco, TTS o UI — solo sostituire output console con logging semantico

---

📂 File Coinvolti

- `acs_wx.py` → MODIFY (rimozione print, migrazione a log.*)
- `src/application/game_engine.py` → MODIFY (rimozione print residui)
- `src/application/dialog_manager.py` → MODIFY (aggiunta log import + dialog_shown/closed)
- `src/application/timer_manager.py` → MODIFY (aggiunta log import + timer_started/expired/paused)
- `docs/3 - coding plans/PLAN-logging-unificazione-v3.2.2.md` → UPDATE (3 correzioni naming)
- `docs/todo.md` → CREATE

---

🛠 Checklist Implementazione

**Preparazione**
- [x] Correzioni piano PLAN-logging-unificazione-v3.2.2.md (3 fix)
- [x] Creazione docs/todo.md

**Fase 1 — `acs_wx.py`**
- [x] Rimozione banner startup (`"="*60` e blocco print info)
- [x] Sostituzione print DEBUG in `_register_dependencies`
- [x] Sostituzione print in `_create_dummy_sr` → `log.tts_spoken`
- [x] Sostituzione print in `return_to_menu` → `log.warning_issued`
- [x] Rimozione print in `show_options`
- [x] Sostituzione print in `show_exit_dialog` → `log.warning_issued`
- [x] Sostituzione print DEBUG in `_safe_abandon_to_menu` → `log.debug_state`
- [x] Sostituzione print in `confirm_abandon_game` → `log.debug_state`
- [x] Rimozione print orfano (riga "Premi ESC per tornare al menu")
- [x] Sostituzione print DEBUG in `handle_game_ended` → `log.debug_state`
- [x] Sostituzione print in `_safe_decline_to_menu` → `log.debug_state`
- [x] Sostituzione print DEBUG in `_safe_return_to_main_menu` → `log.debug_state`
- [x] Rimozione/sostituzione print in `quit_app` → `log.debug_state`
- [x] Sostituzione print in `run()` → `log.debug_state`
- [x] Rimozione/sostituzione print in `main()` → rimozione banner, log.error_occurred già presente

**Fase 2 — Application layer**
- [x] `game_engine.py`: rimozione print DEBUG residui → `log.debug_state`
- [x] `dialog_manager.py`: aggiunta import `game_logger`, `dialog_shown/closed` in tutti i metodi
- [x] `timer_manager.py`: aggiunta import `game_logger`, `timer_started/expired/paused`

---

✅ Criteri di Completamento

L'implementazione è considerata completa quando:

- [x] Nessun `print()` rimane nel codice di produzione dei file in scope
- [ ] Tutti i metodi dialog hanno `dialog_shown`/`dialog_closed`
- [ ] `timer_manager.py` chiama `timer_started`, `timer_expired`, `timer_paused`
- [ ] `pytest` passa senza regressioni
- [ ] Smoke test manuale: avvio app → opzioni → partita → abbandono → chiusura → verifica `logs/solitario.log`

---

📝 Aggiornamenti Obbligatori a Fine Implementazione

- [ ] Aggiornare `CHANGELOG.md` con entry dettagliata
- [ ] Commit con messaggio convenzionale
- [ ] Push su branch `refactoring-engine`

---

📌 Note

- `gameplay_controller.py` e `options_controller.py` sono già completi (logging già implementato)
- `game_engine.py` ha già import e chiamate principali, rimangono solo print DEBUG da rimuovere
- Import da usare sempre: `from src.infrastructure.logging import game_logger as log`
- Non inventare nuovi eventi: usare solo gli helper semantici già esistenti in `game_logger.py`

---

**Fine.**
# TODO – Refactoring Architetturale Clean Architecture (v1.1)

**Branch:** `refactor/architecture-layer-separation`  
**Tipo:** REFACTOR  
**Priorità:** CRITICA  
**Stato:** DA INIZIARE  
**Piano completo:** `docs/3 - coding plans/REFACTORING_PLAN_ARCHITECTURE_FIX.md`

---

## Riferimento Documentazione

Prima di iniziare qualsiasi fase, consultare obbligatoriamente:

`docs/3 - coding plans/REFACTORING_PLAN_ARCHITECTURE_FIX.md`

Questo file è solo il **cruscotto operativo**. Il piano completo contiene analisi, architettura, comandi esatti, edge case e codice di riferimento per ogni step.

---

## Istruzioni per l'Implementazione

Implementare le modifiche in modo **incrementale e sequenziale**, su più commit atomici e logici.

**Workflow obbligatorio per ogni fase:**

1. **Leggi questo TODO** → identifica la prossima fase/step da implementare
2. **Consulta il piano completo** → sezione specifica della fase corrente in `REFACTORING_PLAN_ARCHITECTURE_FIX.md`
3. **Verifica lo stato attuale** → controlla cosa è già stato fatto (git status, grep, test)
4. **Implementa solo la fase corrente** → scope limitato, nessun salto in avanti
5. **Esegui commit atomico** → formato: `type(scope): description [Fase N - Step M]`
6. **Aggiorna questo TODO** → spunta le checkbox completate
7. **Consulta il prossimo step** → rileggi questo TODO + piano completo per la fase successiva
8. **RIPETI** fino al completamento di tutte le fasi

**Regole fondamentali:**

- Un commit per step logico, nessun mega-commit
- Dopo ogni commit: aggiorna subito questo TODO
- Prima di ogni step: rileggi la sezione pertinente del piano completo
- Sequenzialità stretta: fase → commit → aggiorna TODO → fase successiva
- Formato commit: `refactor(scope): descrizione [Fase N - Step M/T]`
- Non passare alla Fase 2 se la Fase 1 non è completata e testata

---

## Obiettivo

- Correggere la violazione della Dependency Rule: i moduli `presentation/dialogs/` e `presentation/widgets/` usano `wx` direttamente e appartengono al layer Infrastructure
- Eliminare i `print()` runtime sostituendoli con `game_logger`
- Allineare la documentazione tecnica al codice reale

---

## File Coinvolti

**Spostamenti (Fase 1):**
- `src/presentation/dialogs/abandon_dialog.py` → MOVE a `src/infrastructure/ui/dialogs/`
- `src/presentation/dialogs/detailed_stats_dialog.py` → MOVE a `src/infrastructure/ui/dialogs/`
- `src/presentation/dialogs/game_info_dialog.py` → MOVE a `src/infrastructure/ui/dialogs/`
- `src/presentation/dialogs/last_game_dialog.py` → MOVE a `src/infrastructure/ui/dialogs/`
- `src/presentation/dialogs/leaderboard_dialog.py` → MOVE a `src/infrastructure/ui/dialogs/`
- `src/presentation/dialogs/victory_dialog.py` → MOVE a `src/infrastructure/ui/dialogs/`
- `src/presentation/widgets/timer_combobox.py` → MOVE a `src/infrastructure/ui/widgets/`

**Import da aggiornare (Fase 1):**
- `src/infrastructure/ui/wx_dialog_provider.py` → MODIFY (import dialogs)
- `src/infrastructure/ui/options_dialog.py` → MODIFY (import timer_combobox, riga 228)
- `src/application/game_engine.py` → MODIFY (lazy import a righe 1353, 1354, 1374, 1525)
- `src/infrastructure/ui/profile_menu_panel.py` → MODIFY (lazy import riga 686)
- `src/infrastructure/ui/dialogs/__init__.py` → CREATE
- `src/infrastructure/ui/widgets/__init__.py` → CREATE

**Fix logging (Fase 2):**
- `src/infrastructure/ui/wx_frame.py` → MODIFY (righe 161, 166, 171, 182)
- `src/infrastructure/ui/wx_dialog_provider.py` → MODIFY (riga 529)
- `src/infrastructure/storage/score_storage.py` → MODIFY (riga 270)

**Documentazione (Fase 3):**
- `docs/API.md` → UPDATE (path dialogs/widgets + `ensure_guest_profile -> bool`)
- `docs/ARCHITECTURE.md` → UPDATE (struttura file + `move_validator.py` → `solitaire_rules.py`)
- `README.md` → UPDATE (se impatto visibile all'utente)
- `CHANGELOG.md` → UPDATE (entry refactor + fixed, incremento versione)

---

## Checklist Implementazione

### Fase 1 — Riorganizzazione Layer Presentation/Infrastructure
> Piano completo: sezione `## Fase 1` di `REFACTORING_PLAN_ARCHITECTURE_FIX.md`

**Step 1.1 — Creare nuove directory**
- [ ] Creata directory `src/infrastructure/ui/dialogs/`
- [ ] Creata directory `src/infrastructure/ui/widgets/`

**Step 1.2 — Spostare i 6 dialog**
- [ ] `abandon_dialog.py` spostato in `src/infrastructure/ui/dialogs/`
- [ ] `detailed_stats_dialog.py` spostato in `src/infrastructure/ui/dialogs/`
- [ ] `game_info_dialog.py` spostato in `src/infrastructure/ui/dialogs/`
- [ ] `last_game_dialog.py` spostato in `src/infrastructure/ui/dialogs/`
- [ ] `leaderboard_dialog.py` spostato in `src/infrastructure/ui/dialogs/`
- [ ] `victory_dialog.py` spostato in `src/infrastructure/ui/dialogs/`
- [ ] Commit: `refactor(infrastructure): move dialogs from presentation to infrastructure [Fase 1 - Step 1.2]`

**Step 1.3 — Spostare widget**
- [ ] `timer_combobox.py` spostato in `src/infrastructure/ui/widgets/`
- [ ] Commit: `refactor(infrastructure): move timer_combobox from presentation to infrastructure [Fase 1 - Step 1.3]`

**Step 1.4 — Aggiornare import nei file dipendenti** ⚠️ *Attenzione import lazy in game_engine.py — consultare piano*
- [ ] Import aggiornati in `wx_dialog_provider.py`
- [ ] Import aggiornati in `options_dialog.py` (riga 228 — lazy import)
- [ ] Import lazy aggiornati in `game_engine.py` (righe 1353, 1354, 1374, 1525 — DENTRO metodi, non spostare in cima al file)
- [ ] Import lazy aggiornato in `profile_menu_panel.py` (riga 686)
- [ ] Verifica grep: `grep -rn "from src.presentation.dialogs" src/` → zero match
- [ ] Verifica grep: `grep -rn "from src.presentation.widgets" src/` → zero match
- [ ] Commit: `refactor(imports): update import paths after dialogs/widgets relocation [Fase 1 - Step 1.4]`

**Step 1.5 — Creare/aggiornare `__init__.py`**
- [ ] Creato `src/infrastructure/ui/dialogs/__init__.py` con export di tutti e 6 i dialog
- [ ] Creato `src/infrastructure/ui/widgets/__init__.py` con export `TimerComboBox`
- [ ] Commit: `refactor(infrastructure): add __init__.py for new dialogs and widgets packages [Fase 1 - Step 1.5]`

**Step 1.6 — Rimuovere directory vuote** ⚠️ *Eseguire SOLO dopo verifica Step 1.4 completato — consultare piano*
- [ ] Verificato che `src/presentation/dialogs/__init__.py` è vuoto
- [ ] Verificato che `src/presentation/widgets/__init__.py` è vuoto
- [ ] Verificato che grep su import presentation/dialogs e presentation/widgets restituisce zero match
- [ ] Directory `src/presentation/dialogs/` rimossa
- [ ] Directory `src/presentation/widgets/` rimossa
- [ ] Commit: `refactor(presentation): remove empty dialogs and widgets directories [Fase 1 - Step 1.6]`

**Step 1.7 — Verifica `formatters/` in Presentation**
- [ ] Confermato che `src/presentation/formatters/` non importa `wx`
- [ ] Confermato che `game_formatter.py` e `options_formatter.py` non importano `wx`

**Step 1.8 — Verifica struttura finale**
- [ ] Struttura `src/infrastructure/ui/dialogs/` corretta (6 file + `__init__.py`)
- [ ] Struttura `src/infrastructure/ui/widgets/` corretta (1 file + `__init__.py`)
- [ ] Layer `src/presentation/` contiene solo: `formatters/`, `game_formatter.py`, `options_formatter.py`

---

### Fase 2 — Refactoring Logging
> Piano completo: sezione `## Fase 2` di `REFACTORING_PLAN_ARCHITECTURE_FIX.md`

**Step 2.1 — Sostituire `print()` runtime con `game_logger`** ⚠️ *NON aggiungere import duplicati — `game_logger` già presente*
- [ ] `wx_frame.py` riga 161: `print` → `log.debug("close_event", ...)`
- [ ] `wx_frame.py` riga 166: `print` → `log.debug("close_event", ...)`
- [ ] `wx_frame.py` riga 171: `print` → `log.debug("close_event", ...)`
- [ ] `wx_frame.py` riga 182: `print` → `log.warning("close_event", ...)`
- [ ] `wx_dialog_provider.py` riga 529: `print` → `log.debug("dialog_provider", ...)`
- [ ] `score_storage.py` riga 270: `print` → `log.error("score_storage", ..., exc_info=True)`
- [ ] Commit: `refactor(logging): replace runtime print() with game_logger [Fase 2 - Step 2.1]`

**Step 2.2 — Verifica entry point**
- [ ] Confermato che `acs_wx.py` usa già `setup_logging` e `game_logger` (nessuna modifica necessaria)

**Step 2.3 — Verifica post-intervento**
- [ ] Grep `print(` in `src/` escludendo docstring: zero match runtime residui
- [ ] Comando: `grep -rn "print(" src/ --include="*.py" | grep -v ">>>" | grep -v "\.\.\."`

---

### Fase 3 — Verifica, Validazione e Documentazione
> Piano completo: sezione `## Fase 3` di `REFACTORING_PLAN_ARCHITECTURE_FIX.md`

**Step 3.1 — Eseguire test suite**
- [ ] `pytest tests/ -v --cov=src --cov-report=term-missing` → tutti i test passano
- [ ] Nessun import error
- [ ] Coverage non diminuita rispetto a baseline

**Step 3.2 — Verifica con linter/mypy**
- [ ] `flake8 src/ --select=F401` → nessun import inutilizzato
- [ ] `mypy src/ --python-version 3.11` → nessun errore di tipo

**Step 3.3 — Test manuale applicazione**
- [ ] Avviata applicazione: `python acs_wx.py`
- [ ] Dialog di abbandono si apre correttamente
- [ ] Dialog di vittoria si apre correttamente
- [ ] Dialog statistiche dettagliate si apre correttamente
- [ ] Dialog classifica si apre correttamente
- [ ] Dialog info partita si apre correttamente
- [ ] Widget timer nelle opzioni funziona correttamente

**Step 3.4 — Aggiornare documentazione**
- [ ] `docs/API.md`: path `src.presentation.dialogs` → `src.infrastructure.ui.dialogs`
- [ ] `docs/API.md`: path `src.presentation.widgets` → `src.infrastructure.ui.widgets`
- [ ] `docs/API.md`: firma `ensure_guest_profile() -> None` corretta in `-> bool`
- [ ] `docs/ARCHITECTURE.md`: struttura file organization aggiornata
- [ ] `docs/ARCHITECTURE.md`: tutte le occorrenze `move_validator.py` → `solitaire_rules.py`
- [ ] `README.md`: aggiornato se impatto visibile all'utente

**Step 3.5 — Analisi comparativa finale**
- [ ] Confronto tra `REFACTORING_PLAN_ARCHITECTURE_FIX.md` e codice reale implementato
- [ ] Verifica che ogni punto del piano corrisponda all'implementazione
- [ ] Nessuna deviazione non documentata

**Step 3.6 — Aggiornare `CHANGELOG.md`**
- [ ] Aggiunta sezione `[Unreleased]` con:
  - `### Changed` per rinominazione layer dialogs/widgets
  - `### Fixed` per `print()` → `game_logger` e `ensure_guest_profile` return type in docs
- [ ] Versione incrementata in modo coerente (MINOR per refactor strutturale)
- [ ] Commit: `docs: update API.md, ARCHITECTURE.md and CHANGELOG.md after architecture refactoring [Fase 3 - Step 3.4-3.6]`

---

## Criteri di Completamento

L'implementazione è considerata completa quando:

- [ ] Tutte le checkbox della Fase 1 sono spuntate
- [ ] Tutte le checkbox della Fase 2 sono spuntate
- [ ] Tutti i test passano (Fase 3 Step 3.1)
- [ ] Analisi comparativa piano vs codice superata (Fase 3 Step 3.5)
- [ ] Documentazione aggiornata (Fase 3 Step 3.4)
- [ ] `CHANGELOG.md` aggiornato con versione coerente (Fase 3 Step 3.6)
- [ ] Nessuna regressione funzionale rilevata
- [ ] Zero `print()` runtime residui in `src/`
- [ ] Zero import `from src.presentation.dialogs` o `from src.presentation.widgets` in `src/`

---

## Note Operative

- Questo file è il cruscotto operativo: consultalo all'inizio e aggiornalo dopo ogni step.
- Il piano completo è la fonte di verità tecnica: consultalo prima di ogni implementazione.
- Se un test fallisce dopo uno step, **non proseguire** alla fase successiva — analizzare e correggere prima.
- Gli import lazy in `game_engine.py` devono restare **dentro i metodi** (non spostare in cima al file).
- `game_logger` è già importato nei 3 file target della Fase 2: non aggiungere import duplicati.
- Entry point reale: `acs_wx.py` (non `main.py`).

---

**Fine.**

Cruscotto operativo — consultabile in 30 secondi per sapere dove si è e cosa fare dopo.
Piano completo: `docs/3 - coding plans/REFACTORING_PLAN_ARCHITECTURE_FIX.md`
