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
