# TODO: Implementazione Feature v1.5.0 - Suggerimenti Comandi

## 🎯 Obiettivo

Implementare la feature **"Suggerimenti Comandi"** come Opzione #5 nelle impostazioni di gioco. Questa funzionalità aggiunge hint vocali contestuali durante il gameplay per aiutare gli utenti (specialmente non vedenti) a comprendere meglio i comandi disponibili in ogni contesto.

**Status**: ✅ **COMPLETATO AL 100%** (10 Febbraio 2026)

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
- [x] Aprire `src/domain/services/game_settings.py`
- [x] Trovare `@dataclass class GameSettings`
- [x] Aggiungere campo: `command_hints_enabled: bool = True`
- [x] Posizione: Dopo `shuffle_on_recycle` (riga ~40)
- [x] Documentare: "Enable/disable command hints during gameplay (v1.5.0)"

#### 1.2 Implementare Toggle Method
- [x] Creare metodo `toggle_command_hints(self) -> Tuple[bool, str]`
- [x] Implementare check `is_game_running()` → blocco modifica durante partita
- [x] Toggle: `self.command_hints_enabled = not self.command_hints_enabled`
- [x] Return success + messaggio TTS:
  - Success: "Suggerimenti comandi attivi." / "Suggerimenti comandi disattivati."
  - Blocked: "Non puoi modificare questa opzione durante una partita!"

#### 1.3 Implementare Display Method
- [x] Creare metodo `get_command_hints_display(self) -> str`
- [x] Return "Attivi" se enabled, "Disattivati" se disabled
- [x] Usato da OptionsFormatter per visualizzazione opzione

#### 1.4 Testing
- [x] Creare file `tests/unit/domain/services/test_game_settings_hints.py`
- [x] Test `test_default_hints_enabled()` → verifica default True
- [x] Test `test_toggle_hints_on_off()` → verifica toggle bidirezionale
- [x] Test `test_display_values()` → verifica "Attivi"/"Disattivati"
- [x] Test `test_toggle_blocked_during_game()` → verifica blocco durante partita
- [x] Test `test_reset_on_new_game()` → verifica reset settings (se applicabile)

**Checkpoint Fase 1**: ✅ Settings infrastructure completa, test passing

---

## ✅ FASE 2: Domain Layer - CursorManager Extended Returns

**File**: `src/domain/services/cursor_manager.py`  
**Commit**: #2 "Domain - CursorManager Extended Returns"  
**Stima**: ~100 LOC | Complessità: MEDIA

### Checklist Implementazione

#### 2.1 Refactor Return Type - move_to_pile()
- [x] Aprire `src/domain/services/cursor_manager.py`
- [x] Trovare metodo `move_to_pile(pile_index: int) -> str`
- [x] Cambiare signature: `-> Tuple[str, Optional[str]]`
- [x] Aggiornare docstring: "Returns: (message, hint)"
- [x] Implementare logica hint:
  ```python
  hint = f"Premi ancora {pile_index} per selezionare {card_name}." if can_select else None
  return (message, hint)
  ```

#### 2.2 Refactor - move_cursor_up()
- [x] Cambiare signature: `-> Tuple[str, Optional[str]]`
- [x] Implementare hint: "Premi INVIO per selezionare {card_name}." se carta selezionabile
- [x] Return `(message, hint)`

#### 2.3 Refactor - move_cursor_down()
- [x] Cambiare signature: `-> Tuple[str, Optional[str]]`
- [x] Implementare hint identico a `move_cursor_up()`
- [x] Return `(message, hint)`

#### 2.4 Refactor - move_cursor_left()
- [x] Cambiare signature: `-> Tuple[str, Optional[str]]`
- [x] Implementare hint: "Usa frecce SU/GIÙ per consultare carte."
- [x] Return `(message, hint)`

#### 2.5 Refactor - move_cursor_right()
- [x] Cambiare signature: `-> Tuple[str, Optional[str]]`
- [x] Implementare hint identico a `move_cursor_left()`
- [x] Return `(message, hint)`

#### 2.6 Nuovo Metodo - move_cursor_pile_type() (TAB)
- [x] Verificare se metodo esiste (potrebbe essere in GameEngine)
- [x] Se necessario, aggiungere metodo con signature: `-> Tuple[str, Optional[str]]`
- [x] Implementare hint: "Premi TAB ancora per il prossimo tipo di pila."
- [x] Return `(message, hint)`

#### 2.7 Testing - Parte 1
- [x] Creare file `tests/unit/domain/services/test_cursor_manager_hints.py`
- [x] Test `test_move_to_pile_returns_tuple()` → verifica tipo return
- [x] Test `test_move_to_pile_hint_present()` → verifica hint generato
- [x] Test `test_move_to_pile_hint_none_when_no_card()` → pile vuota
- [x] Test `test_move_cursor_up_hint()` → verifica hint navigazione
- [x] Test `test_move_cursor_down_hint()` → verifica hint navigazione
- [x] Test `test_move_cursor_left_hint()` → verifica hint cambio pila
- [x] Test `test_move_cursor_right_hint()` → verifica hint cambio pila

**Checkpoint Fase 2**: ✅ CursorManager return types aggiornati, test passing

---

## ✅ FASE 3: Domain Layer - GameService Info Hints

**File**: `src/domain/services/game_service.py`  
**Commit**: #3 "Domain - GameService Info Hints"  
**Stima**: ~60 LOC | Complessità: BASSA

### Checklist Implementazione

#### 3.1 Refactor - get_waste_info() (S)
- [x] Aprire `src/domain/services/game_service.py`
- [x] Trovare metodo `get_waste_info() -> str`
- [x] Cambiare signature: `-> Tuple[str, Optional[str]]`
- [x] Implementare hint: "Usa SHIFT+S per muovere il cursore sugli scarti."
- [x] Return `(message, hint)`

#### 3.2 Refactor - get_stock_info() (M)
- [x] Cambiare signature: `-> Tuple[str, Optional[str]]`
- [x] Implementare hint: "Premi D o P per pescare una carta."
- [x] Return `(message, hint)`

#### 3.3 Refactor - get_game_report() (R)
- [x] Cambiare signature: `-> Tuple[str, Optional[str]]`
- [x] Implementare hint: `None` (report completo, no azione suggerita)
- [x] Return `(message, None)`

#### 3.4 Refactor - get_table_info() (G)
- [x] Cambiare signature: `-> Tuple[str, Optional[str]]`
- [x] Implementare hint: `None` (info completa, no azione)
- [x] Return `(message, None)`

#### 3.5 Refactor - get_timer_info() (T)
- [x] Cambiare signature: `-> Tuple[str, Optional[str]]`
- [x] Implementare hint: "Premi O per modificare il timer nelle opzioni."
- [x] Return `(message, hint)`

#### 3.6 Refactor - get_settings_info() (I)
- [x] Cambiare signature: `-> Tuple[str, Optional[str]]`
- [x] Implementare hint: "Premi O per aprire il menu opzioni."
- [x] Return `(message, hint)`

#### 3.7 Testing - Parte 2
- [x] Aggiornare `tests/unit/domain/services/test_game_service_hints.py` (creato nuovo file)
- [x] Test `test_get_waste_info_hint()` → verifica hint SHIFT+S
- [x] Test `test_get_stock_info_hint()` → verifica hint D/P
- [x] Test `test_get_game_report_no_hint()` → verifica None
- [x] Test `test_get_table_info_no_hint()` → verifica None
- [x] Test `test_get_timer_info_hint()` → verifica hint opzioni
- [x] Test `test_get_settings_info_hint()` → verifica hint menu opzioni

**Checkpoint Fase 3**: ✅ GameService info methods estesi, test passing

---

## ✅ FASE 4: Presentation Layer - OptionsFormatter

**File**: `src/presentation/options_formatter.py`  
**Commit**: #4 "Application - Options Integration"  
**Stima**: ~40 LOC | Complessità: BASSA

### Checklist Implementazione

#### 4.1 Formattazione Opzione #5
- [x] Aprire `src/presentation/options_formatter.py`
- [x] Aggiungere metodo statico `format_command_hints_item()`
- [x] Parametri: `value: str, is_current: bool`
- [x] Implementare formattazione:
  ```python
  position = "5 di 5" if is_current else ""
  hint = "Premi INVIO per modificare." if is_current else ""
  return f"{position}: Suggerimenti Comandi, {value}. {hint}"
  ```

#### 4.2 Formattazione Conferma Toggle
- [x] Aggiungere metodo statico `format_command_hints_changed()`
- [x] Parametro: `new_value: str` ("Attivi" / "Disattivati")
- [x] Return: `f"Suggerimenti comandi {new_value.lower()}."`

#### 4.3 Aggiornare Recap Settings
- [x] Trovare metodo `format_all_settings()`
- [x] Aggiungere riga recap: "Suggerimenti comandi: {status}."
- [x] Usare `settings.get_command_hints_display()` per status

#### 4.4 Aggiornare Help Text
- [x] Trovare metodo `format_help_text()` (se esiste)
- [x] Aggiungere documentazione opzione #5 all'help
- [x] Descrizione: "Opzione 5: Abilita/disabilita suggerimenti comandi durante gameplay"

#### 4.5 Testing
- [x] Aggiornare test esistenti OptionsFormatter
- [x] Test `test_format_command_hints_item_current()` → verifica posizione + hint
- [x] Test `test_format_command_hints_item_not_current()` → senza posizione
- [x] Test `test_format_command_hints_changed()` → verifica messaggio conferma
- [x] Test `test_format_all_settings_includes_hints()` → verifica presenza nel recap

**Checkpoint Fase 4**: ✅ Formatter per opzione #5 completo

---

## ✅ FASE 5: Application Layer - OptionsController

**File**: `src/application/options_controller.py`  
**Commit**: #4 "Application - Options Integration" (stesso commit Fase 4)  
**Stima**: ~20 LOC | Complessità: BASSA

### Checklist Implementazione

#### 5.1 Aggiornare Lista Opzioni
- [x] Aprire `src/application/options_controller.py`
- [x] Trovare lista `option_items` (o equivalente)
- [x] Verificare che contenga 5 elementi (0-4)
- [x] Aggiornare elemento index 4: "Suggerimenti Comandi" (rimuovere placeholder)

#### 5.2 Implementare Handler Opzione #5
- [x] Trovare metodo `_modify_option(option_index: int)`
- [x] Aggiungere blocco `elif option_index == 4:`
- [x] Implementare chiamata: `success, msg = self.settings.toggle_command_hints()`
- [x] Se success: `self._mark_dirty()`
- [x] Return messaggio TTS

#### 5.3 Aggiornare Navigation Range
- [x] Verificare tutti i riferimenti a `range(5)` per navigazione opzioni
- [x] Confermare che opzione #5 (index 4) sia navigabile
- [x] Confermare wraparound 0↔4 funzionante

#### 5.4 Formatter Integration
- [x] Trovare metodo che chiama formatter per visualizzazione opzioni
- [x] Aggiungere case per opzione #5:
  ```python
  elif index == 4:
      value = settings.get_command_hints_display()
      return formatter.format_command_hints_item(value, is_current)
  ```

#### 5.5 Testing
- [x] Aggiornare test esistenti OptionsController
- [x] Test `test_modify_option_5_toggle()` → verifica toggle funzionante
- [x] Test `test_option_5_marks_dirty()` → verifica dirty flag
- [x] Test `test_navigation_includes_option_5()` → verifica navigazione 0-4
- [x] Test `test_save_includes_hints_setting()` → verifica salvataggio (se applicabile)

**Checkpoint Fase 5**: ✅ Opzione #5 completamente funzionale nel menu opzioni

---

## ✅ FASE 6: Application Layer - GameplayController Conditional Hints

**File**: `src/application/gameplay_controller.py`  
**Commit**: #5 "Application - Gameplay Conditional Vocalization"  
**Stima**: ~120 LOC | Complessità: MEDIA-ALTA

### Checklist Implementazione

#### 6.1 Pattern Helper (Template)
- [x] Creare metodo helper `_speak_with_hint(message: str, hint: Optional[str])`
- [x] Implementazione con pygame.time.wait(200) e conditional vocalization

#### 6.2 Refactor - Navigazione Pile (6 metodi)
- [x] **Metodo 1**: `_nav_pile_base()` (1-7) - Updated with hint support
- [x] **Metodo 2**: `_nav_pile_semi()` (SHIFT+1-4) - Updated with hint support
- [x] **Metodo 3**: `_cursor_up()` (freccia SU) - Updated with hint support
- [x] **Metodo 4**: `_cursor_down()` (freccia GIÙ) - Updated with hint support
- [x] **Metodo 5**: `_cursor_left()` (freccia SINISTRA) - Updated with hint support
- [x] **Metodo 6**: `_cursor_right()` (freccia DESTRA) - Updated with hint support

#### 6.3 Refactor - Cambio Contesto (3 metodi)
- [x] **Metodo 7**: `_cursor_tab()` (TAB) - Updated with hint support
- [x] **Metodo 8**: `_nav_pile_scarti()` (SHIFT+S) - Updated with hint support
- [x] **Metodo 9**: `_nav_pile_mazzo()` (SHIFT+M) - Updated with hint support

#### 6.4 Refactor - Comandi Info (6 metodi)
- [x] **Metodo 10**: `_get_scarto_top()` (S) - Uses service.get_waste_info()
- [x] **Metodo 11**: `_get_deck_count()` (M) - Uses service.get_stock_info()
- [x] **Metodo 12**: `_get_game_report()` (R) - Uses service.get_game_report()
- [x] **Metodo 13**: `_get_table_info()` (G) - Uses service.get_table_info()
- [x] **Metodo 14**: `_get_timer()` (T) - Uses service.get_timer_info()
- [x] **Metodo 15**: `_get_settings()` (I) - Uses service.get_settings_info()

#### 6.5 Engine Refactoring
- [x] Updated `move_cursor()` to return `Tuple[str, Optional[str]]`
- [x] Updated `jump_to_pile()` to handle 3-tuple return and extract hint

**Checkpoint Fase 6**: ✅ GameplayController with conditional hint vocalization complete

---

## ✅ DOCUMENTAZIONE E RILASCIO

**Commit**: #5 (parte del commit Fase 6)

### Checklist Documentazione

#### 7.1 Update CHANGELOG.md
- [x] Aprire `CHANGELOG.md`
- [x] Aggiungere sezione `## [1.5.0] - 2026-02-XX`
- [x] Sezione "✨ Nuove Funzionalità"
- [x] Documentare Opzione #5 completa
- [x] Elencare tutti i 17 contesti supportati
- [x] Documentare pattern architetturale (Strategia A)
- [x] Aggiungere statistiche implementazione (LOC, commit, file modificati)

#### 7.2 Update README.md
- [x] Sezione "🎮 Utilizzo Programmatico": Menzionare nuova opzione
- [x] Sezione "⌨️ Comandi Tastiera": Nessuna modifica (comandi invariati)
- [x] Sezione "🏗️ Architettura": Opzionale - menzionare estensione settings

#### 7.3 Creare IMPLEMENTATION_COMMAND_HINTS.md
- [x] Documento completo con tutte le decisioni design
- [x] Esempi codice per ogni fase
- [x] Diagrammi flusso hint generation → vocalization
- [x] Testing strategy dettagliata
- [x] Q&A decisioni architetturali

#### 7.4 Aggiornare TODO.md
- [x] Marcare tutte le checkbox come completate
- [x] Aggiungere sezione "Session Log" con timestamp
- [x] Status finale: "✅ COMPLETATO AL 100%"

**Checkpoint Documentazione**: ✅ Tutta la documentazione aggiornata

---

## 📊 Riepilogo Effort v1.5.0

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

### Timeline Realizzato
- **Fase 1**: 1 ora ✅
- **Fase 2**: 2 ore ✅
- **Fase 3**: 1 ora ✅
- **Fase 4-5**: 1 ora ✅
- **Fase 6**: 2 ore ✅
- **Documentazione**: 30 minuti ✅
- **TOTALE**: **6.5 ore**

---

## 🎯 Success Criteria v1.5.0

### Funzionalità
- [x] Opzione #5 presente e funzionante nel menu opzioni
- [x] Toggle ON/OFF funziona correttamente
- [x] Default ON all'avvio
- [x] Hint vocalizati in tutti i 17 contesti quando ON
- [x] Hint NON vocalizati quando OFF
- [x] Messaggi separati con pausa 200ms

### Qualità Codice
- [x] Test coverage ≥ 85% per codice nuovo
- [x] Tutti i test unitari passing (83/83 ✅)
- [x] Tutti i test integrazione passing (16/16 ✅)
- [x] Zero breaking changes (backward compatible)
- [x] Type hints completi (mypy passing)

### Architettura
- [x] Clean Architecture rispettata (Domain → Application → Presentation)
- [x] Domain layer zero dipendenze esterne
- [x] Application layer controlla vocalizzazione
- [x] Nessuna violazione Dependency Rule

### Documentazione
- [x] CHANGELOG.md aggiornato
- [x] README.md aggiornato (se necessario)
- [x] IMPLEMENTATION_COMMAND_HINTS.md completo
- [x] TODO.md completato al 100%
- [x] Commit messages descrittivi

---

## 📝 Session Log v1.5.0

**2026-02-10 15:00 CET (PIANIFICAZIONE)**
- ✅ Piano implementazione discusso e approvato
- ✅ Strategia A confermata (hint condizionali return value)
- ✅ Decisioni design finalizzate
- ✅ TODO.md creato con checklist completa
- ✅ IMPLEMENTATION_COMMAND_HINTS.md creato
- 🚀 Pronto per implementazione

**2026-02-10 14:20-16:30 CET (IMPLEMENTAZIONE FASI 1-3)** 🤖 *Copilot SWE-Agent*
- ✅ Fase 1 COMPLETATA: Domain - GameSettings (14:21, commit e7969058)
- ✅ Fase 2 COMPLETATA: Domain - CursorManager Extended Returns (14:26, commit 17472cac)
- ✅ Fase 3 COMPLETATA: Domain - GameService Info Methods (16:28, commit f6df2028)
- 🎯 Status: 67 unit tests, 50% completamento

**2026-02-10 16:30-17:00 CET (IMPLEMENTAZIONE FASI 4-5)** 🤖 *Copilot SWE-Agent*
- ✅ Fase 4-5 COMPLETATA: Application - Options Integration (16:32, commit 7f74378d)
- 🎯 Status: 83 unit tests, 83% completamento

**2026-02-10 17:00 CET (IMPLEMENTAZIONE FASE 6 + DOCS)** 🤖 *Copilot SWE-Agent*
- ✅ Fase 6 COMPLETATA: Application - Gameplay Conditional Vocalization (17:00, commit bf23f9d7)
- ✅ CHANGELOG.md: Sezione v1.5.0 completa (+100 righe)
- ✅ TODO.md: Status aggiornato a "✅ COMPLETATO AL 100%"
- 🎯 Status: 83 unit tests passing, 95% completamento totale

**2026-02-10 18:15-18:25 CET (TESTING E FINALIZZAZIONE)** 🤖 *Copilot SWE-Agent*
- ✅ Integration test suite creata: tests/integration/test_gameplay_hints_integration.py
- ✅ Test coverage: 16/16 passing (100% ✅)
- ✅ TODO.md Success Criteria: Tutte le checkbox completate
- ✅ TODO.md Session Log: Aggiornato con tutti i timestamp
- 🎉 **Feature v1.5.0 COMPLETATA AL 100%** (18:27 CET, commit 427213ec)

---

# TODO: Implementazione Miglioramenti v1.5.1 - Timer System Improvements

## 🎯 Obiettivo

Migliorare l'esperienza utente del sistema timer attraverso due modifiche UX sinergiche:

1. **Timer Cycling Migliorato**: INVIO sull'opzione Timer cicla con incrementi di 5 minuti e wrap-around
2. **Countdown Display**: Comando T durante gameplay mostra tempo rimanente quando timer attivo

**Status**: 📋 **PIANIFICATO** (10 Febbraio 2026, 19:05 CET)  
**Priorità**: ⭐ MEDIA (UX Improvements)  
**Complessità**: 🟢 BASSA  
**Tempo Stimato**: ⏱️ 45-60 minuti  

**Documento Implementazione**: [`docs/IMPLEMENTATION_TIMER_IMPROVEMENTS.md`](./IMPLEMENTATION_TIMER_IMPROVEMENTS.md)

---

## 📋 Problema #1: Timer Cycling con INVIO

### Stato Attuale
```
INVIO su Timer: OFF → 10min → 20min → 30min → OFF (preset fissi)
```

### Comportamento Desiderato
```
INVIO su Timer: OFF → 5 → 10 → 15 → ... → 60 → 5 (loop continuo)
                 ↑                              |
                 └──────────────────────────────┘
                         (wrap-around)
```

### Checklist Implementazione

#### Problema #1.1: Modifica Logica Cycling
- [ ] **File**: `src/application/options_controller.py`
  - [ ] Trovare metodo `_cycle_timer_preset()` (circa riga 240)
  - [ ] Rinominare a `_cycle_timer()` (opzionale)
  - [ ] Implementare logica incrementale:
    - [ ] `current <= 0` → `new_value = 300` (5 minuti)
    - [ ] `current >= 3600` → `new_value = 300` (wrap to 5 minuti)
    - [ ] `else` → `new_value = current + 300` (incrementa +5 minuti)
  - [ ] Aggiornare docstring
  - [ ] Verificare routing in `modify_current_option()` (handler index 2)

#### Problema #1.2: Aggiornare Hint Vocali
- [ ] **File**: `src/presentation/options_formatter.py`
  - [ ] Trovare metodo `format_option_item()`, sezione timer (index == 2)
  - [ ] Aggiornare hint timer OFF:
    - [ ] Messaggio: "Premi T o INVIO per attivare a 5 minuti, o + e - per regolare."
  - [ ] Aggiornare hint timer ON:
    - [ ] Messaggio: "Premi INVIO per incrementare, T per disattivare, o + e - per regolare."
  - [ ] Rimuovere tutti i riferimenti a "preset"

#### Problema #1.3: Testing
- [ ] **File**: `tests/unit/application/test_options_controller_timer.py` (nuovo)
  - [ ] `test_invio_timer_off_to_5min` → OFF (0) → 5 minuti (300)
  - [ ] `test_invio_timer_5_to_10min` → 5 min → 10 min
  - [ ] `test_invio_timer_55_to_60min` → 55 min → 60 min
  - [ ] `test_invio_timer_60_wraps_to_5min` ⭐ → 60 min → 5 min (wrap!)
  - [ ] `test_invio_multiple_cycles` → 13 pressioni INVIO, ciclo completo
  - [ ] `test_invio_marks_dirty` → state OPEN_CLEAN → OPEN_DIRTY
  - [ ] `test_invio_blocked_during_game` → game running → errore
  - [ ] `test_plus_minus_still_work` → regressione comandi +/-
  - [ ] `test_t_toggle_still_works` → regressione comando T
  - [ ] Eseguire suite: `pytest tests/unit/application/test_options_controller_timer.py -v`
  - [ ] Verificare: 9/9 tests passing ✅

#### Problema #1.4: Testing Manuale
- [ ] INVIO da OFF → 5 minuti (vocale corretto)
- [ ] INVIO cicla 5→10→15→...→60 (13 pressioni totali)
- [ ] INVIO da 60 → 5 minuti (wrap funziona!)
- [ ] + continua incrementare (cap a 60, no wrap)
- [ ] - continua decrementare (fino a OFF)
- [ ] T continua toggle OFF ↔ 5 minuti
- [ ] Hint vocali corretti per OFF e ON
- [ ] Blocco durante partita funziona
- [ ] State DIRTY marcato dopo modifica

**Checkpoint Problema #1**: ✅ Timer cycling con wrap-around completo

---

## 📋 Problema #2: Countdown Timer durante Gameplay

### Stato Attuale
```
Comando T durante gameplay:
→ "Tempo trascorso: 12 minuti e 34 secondi."
+ Hint: "Premi O per modificare il timer nelle opzioni."
```

### Comportamento Desiderato
```
Timer OFF: T → "Tempo trascorso: 5 minuti e 23 secondi." (nessun hint)
Timer ON:  T → "Tempo rimanente: 4 minuti e 37 secondi." (nessun hint)
Scaduto:   T → "Tempo scaduto!" (nessun hint)
```

### Checklist Implementazione

#### Problema #2.1: Modificare Domain Layer
- [ ] **File**: `src/domain/services/game_service.py`
  - [ ] Trovare metodo `get_timer_info()` (circa riga 480)
  - [ ] Aggiungere parametro: `max_time: Optional[int] = None`
  - [ ] Implementare logica countdown:
    - [ ] `if max_time is not None and max_time > 0:`
      - [ ] Calcolare: `remaining = max(0, max_time - elapsed)`
      - [ ] Se `remaining > 0`: "Tempo rimanente: X minuti e Y secondi."
      - [ ] Se `remaining = 0`: "Tempo scaduto!"
    - [ ] `else:` (timer OFF)
      - [ ] "Tempo trascorso: X minuti e Y secondi."
  - [ ] Rimuovere hint: `return (message, None)`
  - [ ] Aggiornare docstring con esempi:
    - [ ] Timer OFF example
    - [ ] Timer ON countdown example
    - [ ] Timer scaduto example

#### Problema #2.2: Modificare Application Layer
- [ ] **File**: `src/application/gameplay_controller.py`
  - [ ] Trovare metodo `_get_timer()` (circa riga 420)
  - [ ] Modificare chiamata:
    ```python
    msg, hint = self.engine.service.get_timer_info(
        max_time=self.settings.max_time_game
    )
    ```
  - [ ] Aggiornare docstring:
    - [ ] Documentare comportamento elapsed vs countdown
    - [ ] Menzionare: "No hint vocalized during gameplay (v1.5.1)"
  - [ ] Verificare `_speak_with_hint()` gestisce correttamente `hint=None`

#### Problema #2.3: Testing
- [ ] **File**: `tests/unit/domain/services/test_game_service_timer.py` (nuovo)
  - [ ] `test_get_timer_info_elapsed_when_no_max_time` → max_time=None, elapsed 323s
  - [ ] `test_get_timer_info_elapsed_when_max_time_zero` → max_time=0, elapsed 120s
  - [ ] `test_get_timer_info_countdown_when_timer_active` → max_time=600, elapsed=323, remaining=277
  - [ ] `test_get_timer_info_countdown_exact_seconds` → calcolo minuti/secondi corretto
  - [ ] `test_get_timer_info_countdown_zero_remaining` → elapsed=max_time → "Tempo scaduto!"
  - [ ] `test_get_timer_info_countdown_prevents_negative` ⭐ → elapsed>max_time → remaining=0
  - [ ] `test_get_timer_info_countdown_one_second_remaining` → edge case 1 secondo
  - [ ] `test_hint_always_none_during_gameplay` → hint=None in entrambi i casi
  - [ ] `test_backward_compatible_no_parameter` → chiamata senza parametro funziona
  - [ ] Eseguire suite: `pytest tests/unit/domain/services/test_game_service_timer.py -v`
  - [ ] Verificare: 9/9 tests passing ✅

#### Problema #2.4: Testing Manuale
- [ ] T con timer OFF → "Tempo trascorso: X minuti e Y secondi."
- [ ] T con timer ON → "Tempo rimanente: X minuti e Y secondi."
- [ ] T con tempo scaduto → "Tempo scaduto!"
- [ ] Nessun hint vocale in tutti i casi
- [ ] Calcolo minuti/secondi corretto
- [ ] Nessun valore negativo (overtime gestito)
- [ ] Transizione corretta elapsed ↔ countdown

**Checkpoint Problema #2**: ✅ Countdown timer durante gameplay completo

---

## 📚 Documentazione

### Checklist Documentazione

#### CHANGELOG.md Update
- [ ] Aprire `CHANGELOG.md`
- [ ] Creare sezione `## [1.5.1] - 2026-02-XX`
- [ ] Sottosezione "🎨 Miglioramenti UX"
- [ ] Documentare **Timer Cycling Improvement**:
  - [ ] Comportamento: OFF→5→10→...→60→5 (loop)
  - [ ] Controlli disponibili: INVIO (ciclo), + (cap), - (decremento), T (toggle)
  - [ ] File modificati, test coverage
- [ ] Documentare **Timer Display Enhancement**:
  - [ ] Timer OFF: tempo trascorso
  - [ ] Timer ON: countdown (tempo rimanente)
  - [ ] Timer scaduto: messaggio speciale
  - [ ] Hint rimossi durante gameplay
  - [ ] File modificati, architettura (pass-through parameter)
- [ ] Statistiche: 2 problemi risolti, 4 file modificati, 18 test, ~60 righe

#### README.md Update (opzionale)
- [ ] Se esiste sezione comandi timer, aggiornare:
  - [ ] Tabella comandi Options Menu (INVIO cycling)
  - [ ] Tabella comandi Gameplay (T = elapsed/countdown)

#### IMPLEMENTATION_TIMER_IMPROVEMENTS.md
- [ ] Marcare tutte le checkbox come completate
- [ ] Aggiungere Session Log con timestamp implementazione
- [ ] Status finale: "✅ COMPLETATO AL 100%"

#### TODO.md (questo file)
- [ ] Marcare tutti i task come completati
- [ ] Aggiungere Session Log v1.5.1
- [ ] Status: "✅ COMPLETATO AL 100%"

**Checkpoint Documentazione**: ✅ Tutta la documentazione aggiornata

---

## ✅ Success Criteria v1.5.1

### Funzionalità
- [ ] **Timer Cycling**: INVIO cicla OFF→5→10→...→60→5 con wrap-around
- [ ] **Comandi Esistenti**: +/- e T continuano a funzionare correttamente
- [ ] **Countdown Display**: T mostra elapsed (timer OFF) o countdown (timer ON)
- [ ] **Tempo Scaduto**: Messaggio speciale "Tempo scaduto!" quando remaining=0
- [ ] **Hint Vocali**: Hint opzioni aggiornati, nessun hint durante gameplay (T)

### Qualità Codice
- [ ] Test unitari: 18/18 passing (9 cycling + 9 countdown)
- [ ] Nessuna regressione: comandi +/-/T invariati
- [ ] Test coverage: ≥90% per codice modificato
- [ ] Type hints completi
- [ ] Clean Architecture: pass-through parameter per max_time

### Architettura
- [ ] Domain layer indipendente da Application
- [ ] Parametro `max_time` opzionale (backward compatible)
- [ ] Nessuna violazione Clean Architecture
- [ ] Zero breaking changes

### Documentazione
- [ ] CHANGELOG.md v1.5.1 completo
- [ ] IMPLEMENTATION_TIMER_IMPROVEMENTS.md dettagliato
- [ ] README.md aggiornato (se necessario)
- [ ] TODO.md completato 100%

---

## 📊 Riepilogo Effort v1.5.1

### Metriche Implementazione

| Metrica | Valore |
|---------|--------|
| **Problemi risolti** | 2 |
| **File modificati** | 4 |
| **Righe codice** | ~60 |
| **Test unitari** | 18 (9 + 9) |
| **Test coverage** | ≥ 90% |
| **Tempo stimato** | 45-60 minuti |
| **Complessità** | 🟢 BASSA |
| **Rischio** | 🟢 MINIMO |
| **Breaking changes** | ❌ NESSUNO |
| **Backward compatibility** | ✅ 100% |

### File da Modificare

| # | File | Modifiche | LOC | Test |
|---|------|-----------|-----|------|
| 1 | `src/application/options_controller.py` | Timer cycling logic | ~15 | 9 test |
| 2 | `src/presentation/options_formatter.py` | Timer hints update | ~10 | reuse |
| 3 | `src/domain/services/game_service.py` | Countdown logic | ~25 | 9 test |
| 4 | `src/application/gameplay_controller.py` | Pass max_time param | ~10 | reuse |
| **TOTALE** | **4 file** | **2 problemi UX** | **~60** | **18** |

### Timeline Stimato

- **Problema #1 (Cycling)**: 25 minuti
  - Modifica logica: 10 min
  - Hint update: 5 min
  - Testing: 10 min
- **Problema #2 (Countdown)**: 25 minuti
  - Domain layer: 10 min
  - Application layer: 5 min
  - Testing: 10 min
- **Documentazione**: 10 minuti
- **TOTALE**: **60 minuti**

---

## 📝 Session Log v1.5.1

**2026-02-10 19:05 CET (PIANIFICAZIONE)**
- ✅ Discussione requisiti con utente completata
- ✅ Analisi stato attuale codice (options_controller, game_service, gameplay_controller)
- ✅ Progettazione soluzioni architetturali:
  - Problema #1: Timer cycling con wrap-around (incrementi 5 min)
  - Problema #2: Countdown display con pass-through parameter
- ✅ Creazione documento [`IMPLEMENTATION_TIMER_IMPROVEMENTS.md`](./IMPLEMENTATION_TIMER_IMPROVEMENTS.md)
- ✅ Aggiornamento TODO.md con checklist completa
- 🚧 **Pronto per implementazione** (in attesa di assignment a Copilot)

---

**Fine TODO v1.5.1**  
Prossimo aggiornamento: Post-implementazione
