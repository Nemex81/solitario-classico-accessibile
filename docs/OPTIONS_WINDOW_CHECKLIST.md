# ✅ CHECKLIST: FINESTRA VIRTUALE OPZIONI

> **Feature**: Virtual Options Window (HYBRID design)
> **Commits**: #17-20
> **Branch**: `refactoring-engine`
> **Status**: 🔄 IN PROGRESS

---

## 📊 PROGRESSO GENERALE

```
┌──────────────────────┬────────┬─────────────────┐
│ Commit               │ Status │ Completamento   │
├──────────────────────┼────────┼─────────────────┤
│ #17 Domain Layer     │ ⬜ TODO │ [ ] 0%          │
│ #18 Presentation     │ ⬜ TODO │ [ ] 0%          │
│ #19 Application      │ ⬜ TODO │ [ ] 0%          │
│ #20 Integration      │ ⬜ TODO │ [ ] 0%          │
├──────────────────────┼────────┼─────────────────┤
│ TOTALE               │ ⬜ TODO │ [ ] 0/4 (0%)    │
└──────────────────────┴────────┴─────────────────┘
```

---

## 🔵 COMMIT #17: DOMAIN LAYER

**File**: `src/domain/services/game_settings.py`

**Obiettivo**: Aggiungere metodo `toggle_timer()` per supportare tasto T dedicato.

### Implementazione

- [ ] Aggiungi import `Tuple` da typing
- [ ] Implementa metodo `toggle_timer()` con docstring completa
- [ ] Logica: OFF (-1) → ON (300s / 5min)
- [ ] Logica: ON (>0) → OFF (-1)
- [ ] Validazione: blocca se `is_game_running=True`
- [ ] Return tuple: `(bool, str)` con (success, message)
- [ ] Messaggio ON: "Timer attivato a: 5 minuti."
- [ ] Messaggio OFF: "Timer disattivato."
- [ ] Messaggio error: "Non puoi modificare il timer durante una partita!"

### Testing

- [ ] Test: toggle OFF → ON (risultato: 300s)
- [ ] Test: toggle ON → OFF (risultato: -1)
- [ ] Test: toggle bloccato durante partita
- [ ] Test: messaggi TTS corretti

### Commit

- [ ] Commit con messaggio: `feat(domain): Add toggle_timer() to GameSettings`
- [ ] Push su branch `refactoring-engine`

---

## 🔵 COMMIT #18: PRESENTATION LAYER

**File**: `src/presentation/options_formatter.py` (NUOVO)

**Obiettivo**: Creare formatter per tutti i messaggi TTS della finestra opzioni.

### Implementazione Classe

- [ ] Crea file `src/presentation/options_formatter.py`
- [ ] Aggiungi docstring modulo completo
- [ ] Classe `OptionsFormatter` con docstring
- [ ] Costante `OPTION_NAMES` (lista 5 nomi opzioni)
- [ ] Tutti i metodi `@staticmethod`

### Metodi Formatter

- [ ] `format_open_message(first_option_value: str) -> str`
- [ ] `format_close_message() -> str`
- [ ] `format_option_item(index, name, value, include_hint) -> str`
- [ ] `format_option_changed(name, new_value) -> str`
- [ ] `format_timer_limit_reached(limit_type) -> str`
- [ ] `format_timer_error() -> str`
- [ ] `format_blocked_during_game() -> str`
- [ ] `format_all_settings(settings: Dict) -> str`
- [ ] `format_help_text() -> str`
- [ ] `format_save_dialog() -> str`
- [ ] `format_save_confirmed() -> str`
- [ ] `format_save_discarded() -> str`
- [ ] `format_save_cancelled() -> str`
- [ ] `format_future_option_blocked() -> str`

### Hint Contestuali

- [ ] Opzione 0-1-3: "Premi INVIO per modificare."
- [ ] Opzione 2 (Timer OFF): "Premi T per attivare."
- [ ] Opzione 2 (Timer ON): "Premi T per disattivare o + e - per regolare."
- [ ] Opzione 4: "Opzione non ancora implementata."

### Testing

- [ ] Test: tutti i metodi restituiscono stringhe non vuote
- [ ] Test: hint contestuali corretti per ogni opzione
- [ ] Test: genere italiano corretto (impostato/impostata)
- [ ] Test: output leggibile da screen reader

### Commit

- [ ] Commit con messaggio: `feat(presentation): Create OptionsFormatter for TTS`
- [ ] Push su branch `refactoring-engine`

---

## 🔵 COMMIT #19: APPLICATION LAYER

**File**: `src/application/options_controller.py` (NUOVO)

**Obiettivo**: Creare controller completo per gestione finestra opzioni.

### Implementazione Classe

- [ ] Crea file `src/application/options_controller.py`
- [ ] Aggiungi docstring modulo completo
- [ ] Classe `OptionsWindowController` con docstring
- [ ] Import dipendenze (GameSettings, OptionsFormatter)

### Attributi Inizializzazione

- [ ] `self.settings: GameSettings` (reference)
- [ ] `self.cursor_position: int` (0-4)
- [ ] `self.is_open: bool` (False)
- [ ] `self.state: str` ("CLOSED")
- [ ] `self.original_settings: Dict` (snapshot)
- [ ] `self.current_settings: Dict` (tracking)
- [ ] `self._awaiting_save_response: bool` (dialog state)

### Metodi Lifecycle

- [ ] `open_window() -> str`
  - [ ] Set `is_open=True`, `state="OPEN_CLEAN"`, `cursor_position=0`
  - [ ] Chiama `_save_snapshot()`
  - [ ] Return messaggio apertura con prima opzione
- [ ] `close_window() -> str`
  - [ ] Se `state="OPEN_DIRTY"`: return dialog save
  - [ ] Se `state="OPEN_CLEAN"`: chiama `_reset_state()` e chiudi
- [ ] `save_and_close() -> str`
  - [ ] Chiama `_save_snapshot()` (conferma modifiche)
  - [ ] Chiama `_reset_state()`
  - [ ] Return messaggio "Modifiche salvate"
- [ ] `discard_and_close() -> str`
  - [ ] Chiama `_restore_snapshot()` (ripristina originali)
  - [ ] Chiama `_reset_state()`
  - [ ] Return messaggio "Modifiche scartate"
- [ ] `cancel_close() -> str`
  - [ ] Return messaggio "Annullato, rimango in opzioni"

### Metodi Navigazione

- [ ] `navigate_up() -> str`
  - [ ] `cursor_position = (cursor - 1) % 5`
  - [ ] Return `_format_current_option(include_hint=True)`
- [ ] `navigate_down() -> str`
  - [ ] `cursor_position = (cursor + 1) % 5`
  - [ ] Return `_format_current_option(include_hint=True)`
- [ ] `jump_to_option(index: int) -> str`
  - [ ] Valida `0 <= index <= 4`
  - [ ] Set `cursor_position = index`
  - [ ] Return `_format_current_option(include_hint=False)`

### Metodi Modifiche

- [ ] `modify_current_option() -> str`
  - [ ] Blocca se `is_game_running=True`
  - [ ] Blocca se `cursor_position=4` (futuro)
  - [ ] Route a handler appropriato (0-3)
  - [ ] Set `state="OPEN_DIRTY"` se successo
- [ ] `increment_timer() -> str`
  - [ ] Blocca se `cursor_position != 2`
  - [ ] Blocca se `is_game_running=True`
  - [ ] Chiama `settings.increment_timer_validated()`
  - [ ] Set `state="OPEN_DIRTY"` se successo
- [ ] `decrement_timer() -> str`
  - [ ] Blocca se `cursor_position != 2`
  - [ ] Blocca se `is_game_running=True`
  - [ ] Chiama `settings.decrement_timer_validated()`
  - [ ] Set `state="OPEN_DIRTY"` se successo
- [ ] `toggle_timer() -> str`
  - [ ] Blocca se `cursor_position != 2`
  - [ ] Blocca se `is_game_running=True`
  - [ ] Chiama `settings.toggle_timer()`
  - [ ] Set `state="OPEN_DIRTY"` se successo

### Metodi Informazioni

- [ ] `read_all_settings() -> str`
  - [ ] Genera dict con tutte le impostazioni correnti
  - [ ] Return `OptionsFormatter.format_all_settings(dict)`
- [ ] `show_help() -> str`
  - [ ] Return `OptionsFormatter.format_help_text()`

### Metodi Interni

- [ ] `_format_current_option(include_hint: bool) -> str`
  - [ ] Get option name da `OPTION_NAMES`
  - [ ] Get current value da value_getters list
  - [ ] Return formatted option
- [ ] `_modify_deck_type() -> str` (toggle)
- [ ] `_modify_difficulty() -> str` (cycle)
- [ ] `_cycle_timer_preset() -> str` (OFF→10→20→30→OFF)
- [ ] `_modify_shuffle_mode() -> str` (toggle)
- [ ] `_get_deck_type_display() -> str`
- [ ] `_get_difficulty_display() -> str`
- [ ] `_get_timer_display() -> str`
- [ ] `_get_shuffle_mode_display() -> str`
- [ ] `_save_snapshot() -> None`
  - [ ] Salva deck_type, difficulty, timer, shuffle in `original_settings`
- [ ] `_restore_snapshot() -> None`
  - [ ] Ripristina valori da `original_settings` a `self.settings`
- [ ] `_reset_state() -> None`
  - [ ] Set `is_open=False`, `state="CLOSED"`, `cursor_position=0`
  - [ ] Clear snapshot dicts

### Testing

- [ ] Test: open/close lifecycle
- [ ] Test: navigazione wraparound (↑ da 0 → 4, ↓ da 4 → 0)
- [ ] Test: jump 1-5
- [ ] Test: modifiche opzioni (tutti i toggle/cycle)
- [ ] Test: timer (+/-/T) solo se cursor_position=2
- [ ] Test: blocco durante partita
- [ ] Test: state machine (CLEAN → DIRTY transitions)
- [ ] Test: snapshot save/restore
- [ ] Test: recap e help non cambiano cursor_position

### Commit

- [ ] Commit con messaggio: `feat(application): Create OptionsWindowController`
- [ ] Push su branch `refactoring-engine`

---

## 🔵 COMMIT #20: INTEGRAZIONE GAMEPLAY

**File**: `src/application/gameplay_controller.py`

**Obiettivo**: Integrare controller opzioni con routing prioritario input.

### Importazione

- [ ] Aggiungi import `OptionsWindowController`

### Inizializzazione

- [ ] Aggiungi `self.options_controller = OptionsWindowController(settings)`
- [ ] RIMUOVI `self.change_settings` (deprecato, gestito dal controller)

### Routing Prioritario

- [ ] Modifica `handle_keyboard_events(event)`
  - [ ] PRIORITY 1: Check `if self.options_controller.is_open:`
  - [ ] Se TRUE: chiama `_handle_options_events(event)` e return
  - [ ] Se FALSE: continua con gameplay normale

### Handler Opzioni Dedicato

- [ ] Implementa `_handle_options_events(event)`
  - [ ] Check dialog state (`_awaiting_save_response`)
  - [ ] Se dialog attivo: chiama `_handle_save_dialog(event)` e return
  - [ ] Altrimenti: key_map normale
- [ ] Key map completo:
  - [ ] `K_o`: `_handle_options_close`
  - [ ] `K_UP`: `navigate_up`
  - [ ] `K_DOWN`: `navigate_down`
  - [ ] `K_RETURN`: `modify_current_option`
  - [ ] `K_SPACE`: `modify_current_option`
  - [ ] `K_ESCAPE`: `_handle_options_close`
  - [ ] `K_1`: `jump_to_option(0)`
  - [ ] `K_2`: `jump_to_option(1)`
  - [ ] `K_3`: `jump_to_option(2)`
  - [ ] `K_4`: `jump_to_option(3)`
  - [ ] `K_5`: `jump_to_option(4)`
  - [ ] `K_PLUS`: `increment_timer`
  - [ ] `K_EQUALS`: `increment_timer` (+ senza SHIFT)
  - [ ] `K_MINUS`: `decrement_timer`
  - [ ] `K_t`: `toggle_timer`
  - [ ] `K_i`: `read_all_settings`
  - [ ] `K_h`: `show_help`
- [ ] Chiama `self.speak(msg)` per ogni azione

### Handler Chiusura Opzioni

- [ ] Implementa `_handle_options_close() -> str`
  - [ ] Chiama `options_controller.close_window()`
  - [ ] Check se messaggio contiene "modifiche non salvate"
  - [ ] Se TRUE: set `self._awaiting_save_response = True`
  - [ ] Return messaggio

### Handler Dialog Salvataggio

- [ ] Implementa `_handle_save_dialog(event)`
  - [ ] `K_s`: chiama `save_and_close()`, set flag False, speak
  - [ ] `K_n`: chiama `discard_and_close()`, set flag False, speak
  - [ ] `K_ESCAPE`: chiama `cancel_close()`, set flag False, speak

### Handler Tasto O (Gameplay)

- [ ] Modifica `_handle_o_key()`
  - [ ] Check `if game_service.is_game_running():`
  - [ ] Se TRUE: blocca con messaggio error
  - [ ] Se FALSE: chiama `options_controller.open_window()`
  - [ ] Speak messaggio

### Rimozione Legacy

- [ ] RIMUOVI metodo `_handle_f1_key()` (cambio mazzo)
- [ ] RIMUOVI metodo `_handle_f2_key()` (difficoltà)
- [ ] RIMUOVI metodo `_handle_f3_key()` (timer -)
- [ ] RIMUOVI metodo `_handle_f4_key()` (timer +)
- [ ] RIMUOVI metodo `_handle_f5_key()` (shuffle mode)
- [ ] RIMUOVI handler `CTRL+F3` (timer OFF)
- [ ] RIMUOVI entry `K_F1` da `callback_dict`
- [ ] RIMUOVI entry `K_F2` da `callback_dict`
- [ ] RIMUOVI entry `K_F3` da `callback_dict`
- [ ] RIMUOVI entry `K_F4` da `callback_dict`
- [ ] RIMUOVI entry `K_F5` da `callback_dict`

### Testing Integrazione

- [ ] Test: tasto O apre finestra (solo se no partita)
- [ ] Test: tasti gameplay bloccati quando finestra aperta
- [ ] Test: routing prioritario funziona
- [ ] Test: tasti F1-F5 non funzionano più
- [ ] Test: CTRL+F3 non funziona più
- [ ] Test: dialog salvataggio completo (S/N/ESC)
- [ ] Test: chiusura diretta se nessuna modifica
- [ ] Test: tutte le navigazioni e modifiche funzionano

### Commit

- [ ] Commit con messaggio: `feat(application): Integrate OptionsWindowController in gameplay`
- [ ] Push su branch `refactoring-engine`

---

## 🧪 TESTING FINALE

### Navigazione Completa

- [ ] Apertura con tasto O (solo se no partita)
- [ ] Frecce ↑/↓ navigano tutte le 5 opzioni
- [ ] Wraparound funziona (0↔4)
- [ ] Tasti 1-5 saltano correttamente
- [ ] Feedback TTS conciso con hint

### Modifiche Tutte Opzioni

- [ ] Opzione 0: Toggle mazzo (French ↔ Napoletano)
- [ ] Opzione 1: Ciclo difficoltà (1→2→3→1)
- [ ] Opzione 2: INVIO cicla timer presets
- [ ] Opzione 2: Tasto T toggle OFF↔5min
- [ ] Opzione 2: Tasto + incrementa (max 60)
- [ ] Opzione 2: Tasto - decrementa (min 0)
- [ ] Opzione 3: Toggle riciclo (Inversione ↔ Mescolata)
- [ ] Opzione 4: Bloccata "non implementata"

### Timer Management

- [ ] +/-/T funzionano solo se Timer selezionato
- [ ] Limite max: "già al massimo: 60 minuti"
- [ ] Limite min: "già disattivato"
- [ ] Errore se +/-/T su altre opzioni

### Conferma Salvataggio

- [ ] ESC con modifiche: dialog "Salvare modifiche?"
- [ ] Tasto S: salva e chiudi
- [ ] Tasto N: scarta e chiudi
- [ ] Tasto ESC in dialog: annulla (rimani)
- [ ] ESC senza modifiche: chiudi diretto
- [ ] Tasto O con modifiche: stesso comportamento ESC

### Informazioni

- [ ] Tasto I: recap completo
- [ ] Tasto H: help completo
- [ ] Help/Recap non cambiano cursor_position

### Validazioni

- [ ] Blocco modifiche durante partita
- [ ] Blocco apertura finestra durante partita
- [ ] Tasti +/-/T bloccati se non su Timer
- [ ] Opzione 4 bloccata
- [ ] Snapshot salvato/ripristinato correttamente

### Edge Cases

- [ ] Apertura durante partita: bloccata
- [ ] Chiusura senza modifiche: nessun dialog
- [ ] Multiple modifiche: state DIRTY corretto
- [ ] Timer già al limite: messaggio appropriato
- [ ] Dialog annullato: rimani in opzioni

### Compatibilità Legacy

- [ ] Tasti F1-F5 non funzionano più (verificato)
- [ ] CTRL+F3 non funziona più (verificato)
- [ ] Tasto O è l'unico modo per aprire opzioni
- [ ] Tutte le opzioni accessibili da finestra

---

## 📝 NOTE E ISSUE

### Issue Trovati Durante Implementazione

*(Aggiorna questa sezione durante lo sviluppo)*

- [ ] Issue #1: [Descrizione]
- [ ] Issue #2: [Descrizione]

### Modifiche Rispetto a Piano Originale

*(Documenta eventuali deviazioni dal roadmap)*

- [ ] Modifica #1: [Descrizione e motivazione]
- [ ] Modifica #2: [Descrizione e motivazione]

### Miglioramenti Futuri

*(Idee per iterazioni successive)*

- [ ] Opzione 4: Implementare verbosità TTS
- [ ] Aggiungere suoni/beep per conferme
- [ ] Aggiungere preset timer personalizzabili
- [ ] Salvare preferenze su file (persistent settings)

---

## ✅ APPROVAZIONE FINALE

- [ ] Tutti i commit #17-20 completati
- [ ] Testing manuale completo superato
- [ ] Nessun bug critico rilevato
- [ ] Documentazione aggiornata
- [ ] README.md aggiornato con nuovi comandi
- [ ] Help in-game aggiornato (tasto H)
- [ ] Branch `refactoring-engine` pronto per merge

---

**CHECKLIST ATTIVA**: Aggiorna questa checklist ad ogni step completato usando `[x]` per marcare le voci.

**Ultima modifica**: [Aggiorna data ad ogni commit]

**Status branch**: 🔄 IN PROGRESS → ✅ COMPLETATO
