# TODO: Implementazione Feature v1.5.0 - Suggerimenti Comandi

## 🎯 Obiettivo

Implementare la feature **"Suggerimenti Comandi"** come Opzione #5 nelle impostazioni di gioco. Questa funzionalità aggiunge hint vocali contestuali durante il gameplay per aiutare gli utenti (specialmente non vedenti) a comprendere meglio i comandi disponibili in ogni contesto.

**Status**: 🚧 **IN PIANIFICAZIONE** (10 Febbraio 2026)

---

## 📋 Specifiche Feature

### Comportamento
- **Opzione #5**: "Suggerimenti Comandi" (toggle Attivi/Disattivati)
- **Default**: ON per massima accessibilità
- **Persistenza**: Solo in-memory (no salvataggio su file)
- **Vocalizzazione**: Messaggi separati con pausa 200ms
- **Frequenza**: Hint vocalizati SEMPRE quando opzione attiva

### Contesti Supportati (17 totali)
1. **Navigazione Pile** (6): Tasti 1-7, SHIFT+1-4, frecce ↑↓←→
2. **Cambio Contesto** (3): TAB, SHIFT+S, SHIFT+M
3. **Comandi Info** (6): S, M, R, G, T, I
4. **Azioni** (2 - opzionali): INVIO, DELETE

### Esempi Hint
- Double-tap pile: "Premi ancora 3 per selezionare Sette di Cuori."
- Navigazione: "Premi INVIO per selezionare Regina di Fiori."
- TAB: "Premi TAB ancora per il prossimo tipo di pila."
- Info: "Usa SHIFT+S per muovere il cursore sugli scarti."

---

## 🏗️ Architettura Clean - Strategia A

### Pattern Implementativo
```python
# Domain: Genera hint sempre (testabilità)
def move_to_pile() -> Tuple[str, Optional[str]]:
    message = "Pila 3. Sette di Cuori."
    hint = "Premi ancora 3 per selezionare."
    return (message, hint)

# Application: Vocalizza condizionalmente (settings)
message, hint = cursor_manager.move_to_pile(3)
screen_reader.speak(message, interrupt=True)
if settings.command_hints_enabled and hint:
    pygame.time.wait(200)
    screen_reader.speak(hint, interrupt=False)
```

**Vantaggi**:
- ✅ Domain indipendente (business logic pura)
- ✅ Application controlla vocalizzazione
- ✅ Testabilità: hint sempre generati
- ✅ Backward compatible: zero breaking changes

---

## 📊 Piano Implementazione - 6 Fasi, 5 Commit

### Stima Complessiva
- **LOC Produzione**: ~375 righe
- **LOC Testing**: ~550 righe
- **Totale**: ~925 righe
- **Effort**: 6-8 ore sviluppo
- **Commit**: 5 atomici

---

## ✅ FASE 1: Domain Layer - GameSettings

**File**: `src/domain/services/game_settings.py`  
**Commit**: #1 "Domain - Settings & Hint Infrastructure"  
**Stima**: ~35 LOC | Complessità: BASSA

### Checklist Implementazione

#### 1.1 Aggiungere Campo Settings
- [ ] Aprire `src/domain/services/game_settings.py`
- [ ] Trovare `@dataclass class GameSettings`
- [ ] Aggiungere campo: `command_hints_enabled: bool = True`
- [ ] Posizione: Dopo `shuffle_on_recycle` (riga ~40)
- [ ] Documentare: "Enable/disable command hints during gameplay (v1.5.0)"

#### 1.2 Implementare Toggle Method
- [ ] Creare metodo `toggle_command_hints(self) -> Tuple[bool, str]`
- [ ] Implementare check `is_game_running()` → blocco modifica durante partita
- [ ] Toggle: `self.command_hints_enabled = not self.command_hints_enabled`
- [ ] Return success + messaggio TTS:
  - Success: "Suggerimenti comandi attivi." / "Suggerimenti comandi disattivati."
  - Blocked: "Non puoi modificare questa opzione durante una partita!"

#### 1.3 Implementare Display Method
- [ ] Creare metodo `get_command_hints_display(self) -> str`
- [ ] Return "Attivi" se enabled, "Disattivati" se disabled
- [ ] Usato da OptionsFormatter per visualizzazione opzione

#### 1.4 Testing
- [ ] Creare file `tests/unit/src/test_game_settings_hints.py`
- [ ] Test `test_default_hints_enabled()` → verifica default True
- [ ] Test `test_toggle_hints_on_off()` → verifica toggle bidirezionale
- [ ] Test `test_display_values()` → verifica "Attivi"/"Disattivati"
- [ ] Test `test_toggle_blocked_during_game()` → verifica blocco durante partita
- [ ] Test `test_reset_on_new_game()` → verifica reset settings (se applicabile)

**Checkpoint Fase 1**: ✅ Settings infrastructure completa, test passing

---

## ✅ FASE 2: Domain Layer - CursorManager Extended Returns

**File**: `src/domain/services/cursor_manager.py`  
**Commit**: #2 "Domain - CursorManager Extended Returns"  
**Stima**: ~100 LOC | Complessità: MEDIA

### Checklist Implementazione

#### 2.1 Refactor Return Type - move_to_pile()
- [ ] Aprire `src/domain/services/cursor_manager.py`
- [ ] Trovare metodo `move_to_pile(pile_index: int) -> str`
- [ ] Cambiare signature: `-> Tuple[str, Optional[str]]`
- [ ] Aggiornare docstring: "Returns: (message, hint)"
- [ ] Implementare logica hint:
  ```python
  hint = f"Premi ancora {pile_index} per selezionare {card_name}." if can_select else None
  return (message, hint)
  ```

#### 2.2 Refactor - move_cursor_up()
- [ ] Cambiare signature: `-> Tuple[str, Optional[str]]`
- [ ] Implementare hint: "Premi INVIO per selezionare {card_name}." se carta selezionabile
- [ ] Return `(message, hint)`

#### 2.3 Refactor - move_cursor_down()
- [ ] Cambiare signature: `-> Tuple[str, Optional[str]]`
- [ ] Implementare hint identico a `move_cursor_up()`
- [ ] Return `(message, hint)`

#### 2.4 Refactor - move_cursor_left()
- [ ] Cambiare signature: `-> Tuple[str, Optional[str]]`
- [ ] Implementare hint: "Usa frecce SU/GIÙ per consultare carte."
- [ ] Return `(message, hint)`

#### 2.5 Refactor - move_cursor_right()
- [ ] Cambiare signature: `-> Tuple[str, Optional[str]]`
- [ ] Implementare hint identico a `move_cursor_left()`
- [ ] Return `(message, hint)`

#### 2.6 Nuovo Metodo - move_cursor_pile_type() (TAB)
- [ ] Verificare se metodo esiste (potrebbe essere in GameEngine)
- [ ] Se necessario, aggiungere metodo con signature: `-> Tuple[str, Optional[str]]`
- [ ] Implementare hint: "Premi TAB ancora per il prossimo tipo di pila."
- [ ] Return `(message, hint)`

#### 2.7 Testing - Parte 1
- [ ] Creare file `tests/unit/src/test_cursor_manager_hints.py`
- [ ] Test `test_move_to_pile_returns_tuple()` → verifica tipo return
- [ ] Test `test_move_to_pile_hint_present()` → verifica hint generato
- [ ] Test `test_move_to_pile_hint_none_when_no_card()` → pile vuota
- [ ] Test `test_move_cursor_up_hint()` → verifica hint navigazione
- [ ] Test `test_move_cursor_down_hint()` → verifica hint navigazione
- [ ] Test `test_move_cursor_left_hint()` → verifica hint cambio pila
- [ ] Test `test_move_cursor_right_hint()` → verifica hint cambio pila

**Checkpoint Fase 2**: ✅ CursorManager return types aggiornati, test passing

---

## ✅ FASE 3: Domain Layer - GameService Info Hints

**File**: `src/domain/services/game_service.py`  
**Commit**: #3 "Domain - GameService Info Hints"  
**Stima**: ~60 LOC | Complessità: BASSA

### Checklist Implementazione

#### 3.1 Refactor - get_waste_info() (S)
- [ ] Aprire `src/domain/services/game_service.py`
- [ ] Trovare metodo `get_waste_info() -> str`
- [ ] Cambiare signature: `-> Tuple[str, Optional[str]]`
- [ ] Implementare hint: "Usa SHIFT+S per muovere il cursore sugli scarti."
- [ ] Return `(message, hint)`

#### 3.2 Refactor - get_stock_info() (M)
- [ ] Cambiare signature: `-> Tuple[str, Optional[str]]`
- [ ] Implementare hint: "Premi D o P per pescare una carta."
- [ ] Return `(message, hint)`

#### 3.3 Refactor - get_game_report() (R)
- [ ] Cambiare signature: `-> Tuple[str, Optional[str]]`
- [ ] Implementare hint: `None` (report completo, no azione suggerita)
- [ ] Return `(message, None)`

#### 3.4 Refactor - get_table_info() (G)
- [ ] Cambiare signature: `-> Tuple[str, Optional[str]]`
- [ ] Implementare hint: `None` (info completa, no azione)
- [ ] Return `(message, None)`

#### 3.5 Refactor - get_timer_info() (T)
- [ ] Cambiare signature: `-> Tuple[str, Optional[str]]`
- [ ] Implementare hint: "Premi O per modificare il timer nelle opzioni."
- [ ] Return `(message, hint)`

#### 3.6 Refactor - get_settings_info() (I)
- [ ] Cambiare signature: `-> Tuple[str, Optional[str]]`
- [ ] Implementare hint: "Premi O per aprire il menu opzioni."
- [ ] Return `(message, hint)`

#### 3.7 Testing - Parte 2
- [ ] Aggiornare `tests/unit/src/test_cursor_manager_hints.py` (o creare nuovo file)
- [ ] Test `test_get_waste_info_hint()` → verifica hint SHIFT+S
- [ ] Test `test_get_stock_info_hint()` → verifica hint D/P
- [ ] Test `test_get_game_report_no_hint()` → verifica None
- [ ] Test `test_get_table_info_no_hint()` → verifica None
- [ ] Test `test_get_timer_info_hint()` → verifica hint opzioni
- [ ] Test `test_get_settings_info_hint()` → verifica hint menu opzioni

**Checkpoint Fase 3**: ✅ GameService info methods estesi, test passing

---

## ✅ FASE 4: Presentation Layer - OptionsFormatter

**File**: `src/presentation/options_formatter.py`  
**Commit**: #4 "Application - Options Integration"  
**Stima**: ~40 LOC | Complessità: BASSA

### Checklist Implementazione

#### 4.1 Formattazione Opzione #5
- [ ] Aprire `src/presentation/options_formatter.py`
- [ ] Aggiungere metodo statico `format_command_hints_item()`
- [ ] Parametri: `value: str, is_current: bool`
- [ ] Implementare formattazione:
  ```python
  position = "5 di 5" if is_current else ""
  hint = "Premi INVIO per modificare." if is_current else ""
  return f"{position}: Suggerimenti Comandi, {value}. {hint}"
  ```

#### 4.2 Formattazione Conferma Toggle
- [ ] Aggiungere metodo statico `format_command_hints_changed()`
- [ ] Parametro: `new_value: str` ("Attivi" / "Disattivati")
- [ ] Return: `f"Suggerimenti comandi {new_value.lower()}."`

#### 4.3 Aggiornare Recap Settings
- [ ] Trovare metodo `format_all_settings()`
- [ ] Aggiungere riga recap: "Suggerimenti comandi: {status}."
- [ ] Usare `settings.get_command_hints_display()` per status

#### 4.4 Aggiornare Help Text
- [ ] Trovare metodo `format_help_text()` (se esiste)
- [ ] Aggiungere documentazione opzione #5 all'help
- [ ] Descrizione: "Opzione 5: Abilita/disabilita suggerimenti comandi durante gameplay"

#### 4.5 Testing
- [ ] Aggiornare test esistenti OptionsFormatter
- [ ] Test `test_format_command_hints_item_current()` → verifica posizione + hint
- [ ] Test `test_format_command_hints_item_not_current()` → senza posizione
- [ ] Test `test_format_command_hints_changed()` → verifica messaggio conferma
- [ ] Test `test_format_all_settings_includes_hints()` → verifica presenza nel recap

**Checkpoint Fase 4**: ✅ Formatter per opzione #5 completo

---

## ✅ FASE 5: Application Layer - OptionsController

**File**: `src/application/options_controller.py`  
**Commit**: #4 "Application - Options Integration" (stesso commit Fase 4)  
**Stima**: ~20 LOC | Complessità: BASSA

### Checklist Implementazione

#### 5.1 Aggiornare Lista Opzioni
- [ ] Aprire `src/application/options_controller.py`
- [ ] Trovare lista `option_items` (o equivalente)
- [ ] Verificare che contenga 5 elementi (0-4)
- [ ] Aggiornare elemento index 4: "Suggerimenti Comandi" (rimuovere placeholder)

#### 5.2 Implementare Handler Opzione #5
- [ ] Trovare metodo `_modify_option(option_index: int)`
- [ ] Aggiungere blocco `elif option_index == 4:`
- [ ] Implementare chiamata: `success, msg = self.settings.toggle_command_hints()`
- [ ] Se success: `self._mark_dirty()`
- [ ] Return messaggio TTS

#### 5.3 Aggiornare Navigation Range
- [ ] Verificare tutti i riferimenti a `range(5)` per navigazione opzioni
- [ ] Confermare che opzione #5 (index 4) sia navigabile
- [ ] Confermare wraparound 0↔4 funzionante

#### 5.4 Formatter Integration
- [ ] Trovare metodo che chiama formatter per visualizzazione opzioni
- [ ] Aggiungere case per opzione #5:
  ```python
  elif index == 4:
      value = settings.get_command_hints_display()
      return formatter.format_command_hints_item(value, is_current)
  ```

#### 5.5 Testing
- [ ] Aggiornare test esistenti OptionsController
- [ ] Test `test_modify_option_5_toggle()` → verifica toggle funzionante
- [ ] Test `test_option_5_marks_dirty()` → verifica dirty flag
- [ ] Test `test_navigation_includes_option_5()` → verifica navigazione 0-4
- [ ] Test `test_save_includes_hints_setting()` → verifica salvataggio (se applicabile)

**Checkpoint Fase 5**: ✅ Opzione #5 completamente funzionale nel menu opzioni

---

## ✅ FASE 6: Application Layer - GameplayController Conditional Hints

**File**: `src/application/gameplay_controller.py`  
**Commit**: #5 "Application - Gameplay Conditional Vocalization"  
**Stima**: ~120 LOC | Complessità: MEDIA-ALTA

### Checklist Implementazione

#### 6.1 Pattern Helper (Template)
- [ ] Creare metodo helper `_speak_with_hint(message: str, hint: Optional[str])`
- [ ] Implementazione:
  ```python
  def _speak_with_hint(self, message: str, hint: Optional[str]) -> None:
      """Speak message and optional hint based on settings."""
      self.screen_reader.speak(message, interrupt=True)
      
      if self.settings.command_hints_enabled and hint:
          pygame.time.wait(200)  # Pause between messages
          self.screen_reader.speak(hint, interrupt=False)
  ```

#### 6.2 Refactor - Navigazione Pile (6 metodi)
- [ ] **Metodo 1**: `_handle_number_key()` (1-7)
  - [ ] Modificare chiamata: `message, hint = self.cursor_manager.move_to_pile(...)`
  - [ ] Sostituire speak con: `self._speak_with_hint(message, hint)`
  
- [ ] **Metodo 2**: `_handle_shift_foundation()` (SHIFT+1-4)
  - [ ] Modificare chiamata CursorManager
  - [ ] Applicare pattern hint
  
- [ ] **Metodo 3**: `_move_cursor_up()` (freccia SU)
  - [ ] Modificare return unpacking
  - [ ] Applicare pattern hint
  
- [ ] **Metodo 4**: `_move_cursor_down()` (freccia GIÙ)
  - [ ] Modificare return unpacking
  - [ ] Applicare pattern hint
  
- [ ] **Metodo 5**: `_move_cursor_left()` (freccia SINISTRA)
  - [ ] Modificare return unpacking
  - [ ] Applicare pattern hint
  
- [ ] **Metodo 6**: `_move_cursor_right()` (freccia DESTRA)
  - [ ] Modificare return unpacking
  - [ ] Applicare pattern hint

#### 6.3 Refactor - Cambio Contesto (3 metodi)
- [ ] **Metodo 7**: `_handle_tab()` (TAB)
  - [ ] Modificare chiamata metodo pile_type
  - [ ] Applicare pattern hint
  
- [ ] **Metodo 8**: `_handle_shift_waste()` (SHIFT+S)
  - [ ] Modificare chiamata CursorManager
  - [ ] Applicare pattern hint
  
- [ ] **Metodo 9**: `_handle_shift_stock()` (SHIFT+M)
  - [ ] Modificare chiamata CursorManager
  - [ ] Applicare pattern hint

#### 6.4 Refactor - Comandi Info (6 metodi)
- [ ] **Metodo 10**: `_show_waste_info()` (S)
  - [ ] Modificare chiamata: `message, hint = self.game_service.get_waste_info()`
  - [ ] Applicare pattern hint
  
- [ ] **Metodo 11**: `_show_stock_info()` (M)
  - [ ] Modificare chiamata GameService
  - [ ] Applicare pattern hint
  
- [ ] **Metodo 12**: `_show_game_report()` (R)
  - [ ] Modificare chiamata (hint sarà None)
  - [ ] Applicare pattern hint (hint None = no secondo messaggio)
  
- [ ] **Metodo 13**: `_show_table_info()` (G)
  - [ ] Modificare chiamata
  - [ ] Applicare pattern hint
  
- [ ] **Metodo 14**: `_show_timer_info()` (T)
  - [ ] Modificare chiamata
  - [ ] Applicare pattern hint
  
- [ ] **Metodo 15**: `_show_settings_info()` (I)
  - [ ] Modificare chiamata
  - [ ] Applicare pattern hint

#### 6.5 Refactor - Azioni (2 metodi - OPZIONALI)
- [ ] **Metodo 16**: `_select_card()` (INVIO)
  - [ ] Dopo selezione, generare hint: "Premi SPAZIO per spostare la carta."
  - [ ] Applicare pattern hint condizionale
  
- [ ] **Metodo 17**: `_cancel_selection()` (DELETE)
  - [ ] Dopo annullamento, generare hint: "Premi INVIO per selezionare un'altra carta."
  - [ ] Applicare pattern hint condizionale

#### 6.6 Testing - Integration
- [ ] Creare file `tests/integration/test_gameplay_hints_integration.py`
- [ ] **Setup**: Mock ScreenReader + Settings con hints ON/OFF
  
- [ ] **Test Gruppo 1: Hints Enabled**
  - [ ] Test `test_number_key_vocalizes_hint_when_enabled()`
  - [ ] Test `test_cursor_up_vocalizes_hint_when_enabled()`
  - [ ] Test `test_tab_vocalizes_hint_when_enabled()`
  - [ ] Test `test_info_command_vocalizes_hint_when_enabled()`
  - [ ] Verifica: `screen_reader.speak.call_count == 2` per ogni test
  
- [ ] **Test Gruppo 2: Hints Disabled**
  - [ ] Test `test_number_key_no_hint_when_disabled()`
  - [ ] Test `test_cursor_up_no_hint_when_disabled()`
  - [ ] Test `test_tab_no_hint_when_disabled()`
  - [ ] Test `test_info_command_no_hint_when_disabled()`
  - [ ] Verifica: `screen_reader.speak.call_count == 1` per ogni test
  
- [ ] **Test Gruppo 3: Timing**
  - [ ] Test `test_pause_between_message_and_hint()` → verifica 200ms wait
  - [ ] Test `test_hint_interrupt_false()` → verifica interrupt=False per hint
  - [ ] Test `test_message_interrupt_true()` → verifica interrupt=True per message
  
- [ ] **Test Gruppo 4: Edge Cases**
  - [ ] Test `test_hint_none_only_one_speak()` → verifica no hint quando None
  - [ ] Test `test_empty_hint_string_treated_as_none()` → verifica string vuota
  - [ ] Test `test_all_17_contexts_covered()` → verifica coverage completo

**Checkpoint Fase 6**: ✅ Tutti i 17 contesti implementati, test integration passing

---

## ✅ DOCUMENTAZIONE E RILASCIO

**Commit**: #5 (parte del commit Fase 6)

### Checklist Documentazione

#### 7.1 Update CHANGELOG.md
- [ ] Aprire `CHANGELOG.md`
- [ ] Aggiungere sezione `## [1.5.0] - 2026-02-XX`
- [ ] Sezione "✨ Nuove Funzionalità"
- [ ] Documentare Opzione #5 completa
- [ ] Elencare tutti i 17 contesti supportati
- [ ] Documentare pattern architetturale (Strategia A)
- [ ] Aggiungere statistiche implementazione (LOC, commit, file modificati)

#### 7.2 Update README.md
- [ ] Sezione "🎮 Utilizzo Programmatico": Menzionare nuova opzione
- [ ] Sezione "⌨️ Comandi Tastiera": Nessuna modifica (comandi invariati)
- [ ] Sezione "🏗️ Architettura": Opzionale - menzionare estensione settings

#### 7.3 Creare IMPLEMENTATION_COMMAND_HINTS.md
- [ ] Documento completo con tutte le decisioni design
- [ ] Esempi codice per ogni fase
- [ ] Diagrammi flusso hint generation → vocalization
- [ ] Testing strategy dettagliata
- [ ] Q&A decisioni architetturali

#### 7.4 Aggiornare TODO.md
- [ ] Marcare tutte le checkbox come completate
- [ ] Aggiungere sezione "Session Log" con timestamp
- [ ] Status finale: "✅ COMPLETATO AL 100%"

**Checkpoint Documentazione**: ✅ Tutta la documentazione aggiornata

---

## 📊 Riepilogo Effort

### LOC per Fase
| Fase | File | LOC Prod | LOC Test | Totale |
|------|------|----------|----------|--------|
| 1 | game_settings.py | 35 | 100 | 135 |
| 2 | cursor_manager.py | 100 | 150 | 250 |
| 3 | game_service.py | 60 | 100 | 160 |
| 4 | options_formatter.py | 40 | 50 | 90 |
| 5 | options_controller.py | 20 | 50 | 70 |
| 6 | gameplay_controller.py | 120 | 100 | 220 |
| **TOTALE** | **6 file** | **375** | **550** | **925** |

### Commit Strategy
1. **Commit #1**: Domain - Settings & Hint Infrastructure (~135 LOC)
2. **Commit #2**: Domain - CursorManager Extended Returns (~250 LOC)
3. **Commit #3**: Domain - GameService Info Hints (~160 LOC)
4. **Commit #4**: Application - Options Integration (~160 LOC)
5. **Commit #5**: Application - Gameplay + Docs (~220 LOC + docs)

### Timeline Stimato
- **Fase 1**: 1 ora
- **Fase 2**: 2 ore (refactor complesso)
- **Fase 3**: 1 ora
- **Fase 4-5**: 1 ora (insieme)
- **Fase 6**: 2-3 ore (17 metodi)
- **Documentazione**: 1 ora
- **TOTALE**: **6-8 ore**

---

## 🎯 Success Criteria

### Funzionalità
- [ ] Opzione #5 presente e funzionante nel menu opzioni
- [ ] Toggle ON/OFF funziona correttamente
- [ ] Default ON all'avvio
- [ ] Hint vocalizati in tutti i 17 contesti quando ON
- [ ] Hint NON vocalizati quando OFF
- [ ] Messaggi separati con pausa 200ms

### Qualità Codice
- [ ] Test coverage ≥ 85% per codice nuovo
- [ ] Tutti i test unitari passing
- [ ] Tutti i test integrazione passing
- [ ] Zero breaking changes (backward compatible)
- [ ] Type hints completi (mypy passing)

### Architettura
- [ ] Clean Architecture rispettata (Domain → Application → Presentation)
- [ ] Domain layer zero dipendenze esterne
- [ ] Application layer controlla vocalizzazione
- [ ] Nessuna violazione Dependency Rule

### Documentazione
- [ ] CHANGELOG.md aggiornato
- [ ] README.md aggiornato (se necessario)
- [ ] IMPLEMENTATION_COMMAND_HINTS.md completo
- [ ] TODO.md completato al 100%
- [ ] Commit messages descrittivi

---

## 📝 Session Log

**2026-02-10 15:00 CET (PIANIFICAZIONE)**
- ✅ Piano implementazione discusso e approvato
- ✅ Strategia A confermata (hint condizionali return value)
- ✅ Decisioni design finalizzate:
  - Default ON per accessibilità
  - Hint sempre vocalizati quando attivo
  - Messaggi separati con pausa 200ms
  - 17 contesti totali (pile, frecce, TAB, info)
  - Solo in-memory (no persistenza file)
- ✅ TODO.md creato con checklist completa
- ✅ IMPLEMENTATION_COMMAND_HINTS.md in creazione
- 🚧 Pronto per iniziare implementazione

---

**Fine TODO v1.5.0**  
Ultimo aggiornamento: 10 Febbraio 2026 - Pianificazione Completa
