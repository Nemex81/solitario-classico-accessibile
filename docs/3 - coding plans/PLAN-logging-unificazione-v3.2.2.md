
# Piano Implementazione: Unificazione Sistema di Logging v2.6.2

## Obiettivo
Garantire che **tutti** gli eventi di sistema e di gioco vengano tracciati tramite il sistema di logging centralizzato con salvataggio su file (RotatingFileHandler), eliminando ogni dipendenza da `print()`/output diretto su terminale nel branch `refactoring-engine`.

Versione target progetto: v3.2.2.1
Branch: `refactoring-engine`

---

## 1. Scope e criteri di completamento

### 1.1 Scope

Rientrano nel perimetro:

- File di entry point e orchestrazione UI:
  - `acs_wx.py`
- Layer Application:
  - `src/application/game_engine.py`
  - `src/application/gameplay_controller.py`
  - `src/application/options_controller.py`
  - `src/application/dialog_manager.py`
  - `src/application/timer_manager.py`
- Layer Presentation (da verificare e rifinire durante implementazione):
  - `src/presentation/**` (dialog, pannelli, formatter solo se usano `print()` o logging proprio)
- Layer Domain (solo I/O e gestione file settings/score, se non già wrappato):
  - `src/domain/services/game_settings.py` (solo verifica; wrapping già pianificato nel doc logging)

Sono esplicitamente **fuori scope**:

- Vecchio codice `scr/` (pygame-based) usato solo come legacy/storico.
- Test (`tests/**`), salvo piccoli aggiustamenti di aspettative se i log venivano letti da stdout (al momento non risultano).

### 1.2 Definition of Done

Il lavoro è considerato completo quando:

1. Non esiste più **alcun `print()`** nel codice di produzione considerato (eccezione: `print()` usati nei test/doc o in codice legacy `scr/`).
2. Tutte le precedenti stampe su terminale in `acs_wx.py` sono state sostituite con chiamate a `game_logger` o rimosse se ridondanti.
3. Tutti gli eventi chiave di gameplay, UI e settings sono tracciati tramite funzioni semantiche di `src/infrastructure/logging/game_logger.py`.
4. `setup_logging()` viene inizializzato una sola volta, all’avvio, e i file di log vengono effettivamente popolati durante una sessione di gioco reale.
5. I test automatici (`pytest`) passano senza modifiche strutturali.
6. Viene eseguito un smoke test manuale con verifica dei log generati.

---

## 2. Stato attuale logging (sintesi)

### 2.1 Infrastruttura logging

Già implementata e production-ready:

- `src/infrastructure/logging/logger_setup.py`
  - `setup_logging(level=logging.INFO, console_output: bool)`
  - Configurazione root logger con `RotatingFileHandler` su `logs/solitario.log`.
- `src/infrastructure/logging/game_logger.py`
  - Oltre 20 helper semantici:
    - Lifecycle: `app_started`, `app_shutdown`, `game_started`, `game_won`, `game_abandoned`, `game_reset`.
    - Gameplay: `card_moved`, `cards_drawn`, `waste_recycled`, `invalid_action`.
    - UI: `panel_switched`, `dialog_shown`, `dialog_closed`, `keyboard_command`.
    - Errori: `error_occurred`, `warning_issued`.
    - Debug/Analytics: `debug_state`, `cursor_moved`, `pile_jumped`, `info_query_requested`, `tts_spoken`, `settings_changed`, `timer_started`, `timer_expired`, `timer_paused`.

### 2.2 Gap principali

- `acs_wx.py` utilizza massicciamente `print()` per debug e messaggi utente → da migrare.
- I file `src/application/*.py` non importano né usano `game_logger`, salvo log aggiunti in precedenza per settings e carte.
- Alcuni eventi chiave sono ancora visibili solo in TTS o in comportamenti, non nei log (es. certe transizioni UI/panel).

---

## 3. Modifiche per file

### 3.1 `acs_wx.py` — pulizia output console e aggancio logging

#### 3.1.1 Import e setup

- Verificare che siano presenti (o aggiungere se mancanti):
  - `from src.infrastructure.logging.logger_setup import setup_logging`
  - `from src.infrastructure.logging import game_logger as log`
- Assicurarsi che `setup_logging(...)` sia chiamato **subito all’avvio**, prima della creazione di `SolitarioController`.
  - Default: `setup_logging(level=logging.INFO, console_output=False)`.
  - Eventuale flag CLI `--debug` può abilitare `console_output=True` per sviluppo.
- All’avvio applicazione:
  - Chiamare `log.app_started()`.
- Alla chiusura pulita (punto unico di uscita, es. in `quit_app` o blocco `finally` principale):
  - Chiamare `log.app_shutdown()`.

#### 3.1.2 Sostituzione `print()` categoria DEBUG tracing

Metodi coinvolti (non esaustivo, da rifinire in implementazione):

- `_register_dependencies`
- `_safe_abandon_to_menu`
- `handle_game_ended`
- `_safe_decline_to_menu`
- `_safe_return_to_main_menu`
- `confirm_abandon_game`
- eventuali altri metodi con prefisso `[DEBUG ...]` nelle stringhe.

Strategia sostituzione:

- Per messaggi puramente diagnostici:
  - `print("[DEBUG ...] ...")` → `log.debug_state("nome_evento", {"msg": "...", ...})`.
- Per messaggi con chiaro warning (⚠, errori non fatali):
  - `print("⚠ ...")` → `log.warning_issued("SolitarioController", "...")`.
- Per messaggi di tracing di flusso (inizio/fine metodo):
  - `print("[DEBUG ...] INIZIO")` → `log.debug_state("nome_metodo", {"phase": "start"})`.
  - `print("[DEBUG ...] FINE")` → `log.debug_state("nome_metodo", {"phase": "end"})`.

#### 3.1.3 Sostituzione `print()` categoria UX/console banner

- Banner di avvio in `main()` / `run()` (linee con `"="*60`, “APERTURA FINESTRA OPZIONI”, ecc.).
  - Da **rimuovere**: la UX reale è via TTS e UI wx, non terminale.
  - Dove serve una traccia, usare `log.debug_state("options_dialog", {"status": "opening"})`.

- Messaggi informativi tipo:
  - `print("↩ Ritorno al menu principale")` → generalmente **rimossi**, perché ridondanti con TTS.

#### 3.1.4 Errori fatali e fallback

- Blocco `try/except` principale in `main()` o `if __name__ == "__main__"`:
  - Sostituire qualsiasi `print(f"ERRORE FATALE: {e}")` + `traceback.print_exc()` con:
    ```python
    log.error_occurred("Application", "Unhandled exception in main loop", e)
    ```

- Fallback `show_exit_dialog()` quando `dialog_manager` non disponibile:
  - `print("⚠ Dialog manager not available, exiting directly")`
    → `log.warning_issued("DialogManager", "Not available, exiting directly")`.

#### 3.1.5 Dummy screen reader

- Nel metodo `_create_dummy_sr`:
  - Sostituire:
    ```python
    print(f"[TTS] {text}")
    ```
    con:
    ```python
    log.tts_spoken(f"[DUMMY_MODE] {text}", interrupt)
    ```

#### 3.1.6 Print orfani / fuori contesto

- Eliminare eventuali `print()` non indentati correttamente (es. riga con “Premi ESC per tornare al menu...”) non appartenenti a nessun metodo.


### 3.2 `src/application/game_engine.py` — eventi di gioco

Obiettivo: garantire che tutte le transizioni di stato di partita vengano loggate.

Interventi previsti:

1. Import in testa file:
   ```python
   from src.infrastructure.logging import game_logger as log
   ```

2. In factory `GameEngine.create(...)` o equivalente punto di creazione nuova partita:
   - Dopo l’impostazione di deck type, difficulty e timer:
     ```python
     log.game_started(deck_type=settings.deck_type, difficulty=settings.difficulty_level, timer_enabled=settings.timer_enabled)
     ```

3. Nella logica di vittoria (es. `end_game` o metodo equivalente che determina vittoria):
   - Alla creazione del risultato vittoria:
     ```python
     log.game_won(elapsed_time=stats.elapsed_time, moves_count=stats.moves, score=stats.score)
     ```

4. Nella logica di abbandono (abandon/abandon_exit):
   - Prima del reset finale:
     ```python
     log.game_abandoned(elapsed_time=stats.elapsed_time, moves_count=stats.moves)
     ```

5. In eventuale metodo di reset esplicito partita (`reset_game`):
   ```python
   log.game_reset()
   ```

6. In punti critici con eccezioni catturate:
   - Blocchi `try/except` che intercettano errori di dominio o I/O:
     ```python
     except Exception as e:
         log.error_occurred("GameEngine", "Unexpected error during ...", e)
         raise
     ```

### 3.3 `src/application/gameplay_controller.py` — input tastiera e azioni

Obiettivo: tracciare cosa fa davvero il giocatore.

1. Import:
   ```python
   from src.infrastructure.logging import game_logger as log
   ```

2. Nel router centrale `handle_wx_key_event` (corretto da handlewx_key_event, underscore obbligatorio) (o equivalente):

   - Per comandi significativi (non frecce di pura navigazione se si vuole evitare rumore):
     ```python
     log.keyboard_command("ENTER", "gameplay")
     log.keyboard_command("CTRL+ENTER", "gameplay")
     log.keyboard_command("ESC", "gameplay")
     log.keyboard_command("N", "gameplay")
     log.keyboard_command("O", "main_menu")
     # ecc. mappando solo i comandi principali
     ```

3. Dove viene effettuato un movimento di carta (dopo validazione, nel punto dove già ora viene tracciato il contesto):
   ```python
   log.card_moved(from_pile, to_pile, card_name, success=True)
   ```
   - In caso di azione non valida:
     ```python
     log.invalid_action("move_card", reason)
     ```

4. Nel punto in cui si pescano carte dal mazzo:
   ```python
   log.cards_drawn(count)
   ```

5. Nel punto in cui si ricicla la pila scarti:
   ```python
   log.waste_recycled(recycle_count)
   ```

6. Per richieste di info da tastiera (F, G, SHIFT+G, ecc.):
   ```python
   log.info_query_requested("table_info", "during_gameplay")
   log.info_query_requested("cursor_position", "during_gameplay")
   ```

7. Error handling opzionale (Commit 3 del vecchio piano):
   - Eventuale wrapper leggero attorno al router key events:
     ```python
     def handle_wx_key_event(self, event: wx.KeyEvent) -> bool:
         try:
             return self._handle_wx_key_event_impl(event)
         except Exception as e:
             log.error_occurred("InputParsing", "Failed to handle key event", e)
             return False
     ```
   - Implementare `_handle_wx_key_event_impl` spostando la logica esistente, **solo se** decidi di fare ora il wrapping.


### 3.4 `src/application/options_controller.py` — settings

Nota: parte del logging settings è già implementata (Commit 2 della fase 2). Qui serve solo garantirne completezza e coerenza.
Stato attuale: 7/9 già fatti (Commit 2 PR 60), mancano modify_timer_strict_mode e modify_score_warning_level.

1. Verificare che ogni metodo che modifica le impostazioni chiami `log.settings_changed(...)`:

   - `modify_difficulty`
   - `cycle_timer_preset`
   - `increment_timer`, `decrement_timer`, `toggle_timer`
   - `modify_draw_count`
   - `modify_shuffle_mode`
   - `modify_command_hints`
   - `modify_scoring`
   - `modify_timer_strict_mode`
   - `modify_score_warning_level` (nuova opzione 9)

2. Pattern standard:
   ```python
   old_value = settings.difficulty
   settings.difficulty = new_value
   log.settings_changed("difficulty", old_value, new_value)
   ```

3. In caso di errore di validazione o I/O:
   ```python
   log.error_occurred("Settings", "Invalid difficulty value", e)
   ```


### 3.5 `src/application/dialog_manager.py` — dialoghi

Obiettivo: avere traccia coerente dell’apertura/chiusura dei dialog.

1. Import `game_logger` come negli altri file.

2. In ogni metodo che mostra un dialog (sincrono o asincrono):

   - All’apertura:
     ```python
     log.dialog_shown("yes_no", "Abbandono Partita")
     ```
   - Alla chiusura (dopo `ShowModal` o callback async):
     ```python
     result = "yes" if user_choice else "no"
     log.dialog_closed("yes_no", result)
     ```

3. Per dialog informativi (es. errori, info, statistiche):

   - Tipi coerenti: `"info"`, `"error"`, `"stats"`, `"leaderboard"`.


### 3.6 `src/application/timer_manager.py` — timer di gioco (o logica timer in GameEngine se file assente)

Obiettivo: tracciare timer start/stop/expire.

1. Import `game_logger`.

2. Quando il timer di partita viene avviato:
   ```python
   log.timer_started(duration_seconds)
   ```

3. Quando il timer scade e genera un game over automatico:
   ```python
   log.timer_expired()
   ```

4. Se esiste una funzione di pausa timer (anche futura):
   ```python
   log.timer_paused(remaining_seconds)
   ```


### 3.7 `src/presentation/**` — UI e pannelli

Obiettivo: eliminare eventuali `print()` di debug e tracciare transizioni panel.

Attività:

1. Ricerca globale in `src/presentation` di:
   - `print(`
   - `logging.`

2. Per ogni `print()` trovata:
   - Se puro debug/diagnostica → `log.debug_state("nome_panel", {...})`.
   - Se warning/errore UI → `log.warning_issued("UI", "...")`.

3. In `ViewManager` / `WindowController` / pannelli di alto livello (MenuPanel, GameplayPanel, OptionsDialog):
   - In punti di switch panel espliciti:
     ```python
     log.panel_switched("menu", "gameplay")
     log.panel_switched("gameplay", "menu")
     log.panel_switched("menu", "options")
     ```

4. Nessun log nei percorsi ultra-hot di rendering puro (UI grafica), per non aumentare il rumore nei file.


### 3.8 `src/domain/services/game_settings.py` — I/O settings (solo verifica)

1. Verificare che i metodi `save_to_file` / `load_from_file` (o equivalenti) siano già wrappati con `try/except` e usino `log.error_occurred("FileIO", ...)` in caso di errori.

2. Se non presente, implementare pattern:
   ```python
   def save_to_file(self, path: str) -> bool:
       try:
           # logica attuale di salvataggio
           return True
       except Exception as e:
           log.error_occurred("FileIO", f"Failed to save settings to {path}", e)
           return False
   ```

---

## 4. Ordine di implementazione consigliato

1. **Fase 1 — `acs_wx.py`**
   - Eliminazione `print()` e sostituzione con `game_logger`.
   - Verifica che `setup_logging()` venga chiamato correttamente.
   - Smoke test manuale: avvio app, apertura opzioni, abbandono partita, chiusura app.

2. **Fase 2 — Application layer**
   - `game_engine.py`: lifecycle game.
   - `gameplay_controller.py`: keyboard commands, moves, draws, recycles.
   - `options_controller.py`: settings_changed completamento.
   - `dialog_manager.py`: dialog_shown/closed ovunque.
   - `timer_manager.py`: timer_started/expired.

3. **Fase 3 — Presentation layer**
   - Rimozione `print()` residui.
   - Aggiunta di `panel_switched` nei punti chiave.

4. **Fase 4 — Domain I/O (se necessario)**
   - Wrapping I/O settings con `error_occurred`.

5. **Fase 5 — Test & verifica**
   - `pytest` completo.
   - Esecuzione manuale con scenario tipo:
     1. Avvio app.
     2. Nuova partita, qualche mossa valida e non valida.
     3. Pesca da stock, riciclo scarti.
     4. Apertura e chiusura opzioni con variazioni.
     5. Vittoria artificiale o abbandono.
     6. Chiusura app.
   - Controllo di `logs/solitario.log` per verificare presenza e coerenza degli eventi.

---

## 5. Considerazioni di performance e rumore log

- Livelli consigliati:
  - INFO: lifecycle, eventi principali di gioco, cambi settings.
  - WARNING: azioni invalide, condizioni anomale ma gestite.
  - ERROR: eccezioni non previste, problemi I/O.
  - DEBUG: `debug_state`, `cursor_moved`, `pile_jumped`, `tts_spoken` solo se necessario.

- In produzione:
  - Usare `level=logging.INFO` e non chiamare le funzioni DEBUG in percorsi hot, o lasciare l’uso di DEBUG solo per sessioni di diagnostica.

---

## 6. Note operative

- Tutte le modifiche devono mantenere intatti i comportamenti TTS e la logica di gioco.
- Nel dubbio, preferire log “semanticamente ricchi” (deck_type, difficulty, card name) rispetto a log generici.
- Ogni volta che viene introdotto un nuovo flusso importante (nuovo dialog, nuovo tipo di azione), ricordarsi di aggiungere la corrispondente traccia nel logging.

