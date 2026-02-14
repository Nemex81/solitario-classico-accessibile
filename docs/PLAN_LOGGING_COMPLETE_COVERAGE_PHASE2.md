# 📋 Piano Implementazione: Logging Coverage Completion (Phase 2)

> Completa coverage logging dal 70% al 95% - Settings tracking, Error handling, Context extraction fixes, Navigation analytics

---

## 📊 Executive Summary

**Tipo**: FEATURE (Completamento implementazione parziale)  
**Priorità**: 🟠 ALTA (Prerequisito per production monitoring)  
**Stato**: READY  
**Branch**: `copilot/implement-centralized-logging-system`  
**Versione Target**: `v2.3.1` (hotfix dopo merge v2.3.0)  
**Data Creazione**: 2026-02-14  
**Autore**: AI Assistant + Nemex81  
**Effort Stimato**: 5-6 ore totali (4.5h Copilot + 1.5h testing/review)  
**Commits Previsti**: 4 commit atomici sequenziali

---

### Problema/Obiettivo

La **Phase 1 logging implementation** (completata in PR #60) ha creato l'infrastruttura base e coperto lifecycle events principali (~70% coverage), ma **ha lasciato gap critici**:

❌ **Gap 1: Context Extraction Fallito** (15% missing coverage)
- Placeholders `[card]`, `[cards]` invece di valori reali in `card_moved()` logs
- Impossibile tracciare mosse specifiche per analytics

❌ **Gap 2: Settings Tracking Zero** (15% missing coverage)
- Helper `settings_changed()` esiste ma mai chiamato
- Nessuna integrazione in `OptionsController`
- Audit trail configurazioni utente impossibile

❌ **Gap 3: Error Handling Zero** (5% missing coverage)
- Helper `error_occurred()` esiste ma mai usato
- Nessun try/except wrapping in controllers/services
- Eccezioni crashano silent senza traccia log

❌ **Gap 4: Navigation Analytics Incompleto** (5% missing coverage)
- Arrow keys e number keys non loggano movimento cursore
- UX heatmap pile frequency impossibile
- Solo query commands (F/G/R) loggano

**Coverage Reale**: 70-75% (vs obiettivo 95%+ dichiarato)

---

### Soluzione Proposta

**Phase 2 Implementation**: 4 commit sequenziali per colmare gap residui

1. **COMMIT 1**: Context Extraction Fix (1h) - Priority 🔴 CRITICA
   - Fix placeholders in `gameplay_controller.py`
   - Extract real card names, pile names from game state
   - Impact: +10% coverage (card moves tracciabili)

2. **COMMIT 2**: Settings Tracking Integration (2h) - Priority 🟠 ALTA
   - Integrate `log.settings_changed()` in `OptionsController`
   - Track all 5 settings: difficulty, timer, draw_count, shuffle, command_hints
   - Impact: +10% coverage (audit trail completo)

3. **COMMIT 3**: Error Handling Wrapping (1.5h) - Priority 🟠 ALTA
   - Wrap risky methods in try/except with `log.error_occurred()`
   - Target: `handle_wx_key_event()`, `move_card()`, file I/O
   - Impact: +5% coverage (error traces per debugging)

4. **COMMIT 4**: Navigation Analytics (1h) - Priority 🟡 MEDIA
   - Add DEBUG logging in `cursor.move_*()` and `jump_to_pile()`
   - Optional (can be skipped if time-constrained)
   - Impact: +5% coverage (UX heatmap capability)

**Total Impact**: 70% → 90-95% coverage (30% gap reduction)

---

### Impact Assessment

| Aspetto | Impatto | Note |
|---------|---------|------|
| **Severità** | ALTA | Senza fix, logging system incomplete per production |
| **Scope** | 4 file modificati | `gameplay_controller.py`, `options_controller.py`, `game_service.py`, `cursor_manager.py` |
| **Rischio regressione** | BASSO | Solo aggiunta logging calls, no logic changes |
| **Breaking changes** | NO | Zero cambio API pubblica |
| **Testing** | SEMPLICE | Log validation manuale (run game, check `logs/solitario.log`) |

---

## 🎯 Requisiti Funzionali

### 1. Context Extraction Fix

**Comportamento Atteso**:
1. Utente seleziona 7♠ da tableau_3 e sposta su foundation_1
2. Sistema logga: `"Move SUCCESS: 7 di Picche from tableau_3 to foundation_1"`
3. Log entry contiene valori reali (non placeholders)

**File Coinvolti**:
- `src/application/gameplay_controller.py` - Lines ~490-530 (metodi `_select_card`, `_move_cards`, `_draw_cards`) 🔧 DA FIXARE

**Codice Attuale (ROTTO)**:
```python
# Line ~500 in _select_card()
log.card_moved(
    from_pile=pile_name,
    to_pile="selected",
    card="[card]",  # ❌ PLACEHOLDER
    success=True
)
```

**Codice Corretto**:
```python
card = pile.get_top_card()
card_name = card.get_name if card else "unknown"
log.card_moved(
    from_pile=pile_name,
    to_pile="selected",
    card=card_name,  # ✅ REAL VALUE
    success=True
)
```

---

### 2. Settings Tracking Integration

**Comportamento Atteso**:
1. Utente naviga in Options e preme SPACE su "Difficoltà: Medio"
2. Sistema cicla valore: Medio → Difficile
3. Sistema logga: `"Setting changed: difficulty_level = 2 → 3"`

**File Coinvolti**:
- `src/application/options_controller.py` - Lines 120-250 (metodi `cycle_*`, `toggle_*`) ⚙️ MODIFICARE

**Settings da Tracciare** (5 totali):
1. `difficulty_level` (1-5) - cycling in `cycle_difficulty()`
2. `max_time_game` (0 o 300-3600s) - toggle/modify in `toggle_timer()`, `increment_timer()`, `decrement_timer()`
3. `draw_count` (1-3) - cycling in `cycle_draw_count()`
4. `shuffle_discards` (bool) - toggle in `toggle_shuffle_discards()`
5. `command_hints_enabled` (bool) - toggle in `toggle_command_hints()`

---

### 3. Error Handling Wrapping

**Comportamento Atteso**:
1. Codice esegue operazione rischiosa (es. parsing keycode invalido)
2. Eccezione sollevata viene catturata da try/except
3. Sistema logga: `"ERROR [InputParsing]: Invalid keycode 999" + traceback`
4. Applicazione continua senza crash (graceful degradation)

**File Coinvolti**:
- `src/application/gameplay_controller.py` - Line ~700 (`handle_wx_key_event`) ⚙️ MODIFICARE
- `src/domain/services/game_service.py` - Line ~180 (`move_card`) ⚙️ MODIFICARE

**Target Methods** (3 prioritari):
1. `GameplayController.handle_wx_key_event()` - Input parsing errors
2. `GameService.move_card()` - Validation failures
3. `OptionsController.save_settings()` - File I/O errors

---

### 4. Navigation Analytics

**Comportamento Atteso**:
1. Utente preme Arrow UP (navigazione carta)
2. Sistema logga (DEBUG): `"Cursor: tableau_3[5] → tableau_3[4]"`
3. Utente preme "3" (jump direct pile)
4. Sistema logga (DEBUG): `"Pile jump: tableau_1 → tableau_3"`

**File Coinvolti**:
- `src/domain/services/cursor_manager.py` - Lines 100-300 (metodi `move_up/down/left/right/tab`) ⚙️ MODIFICARE

---

## 📝 Piano di Implementazione

### COMMIT 1: Fix Context Extraction in Gameplay Logging

**Priorità**: 🔴 CRITICA  
**File**: `src/application/gameplay_controller.py`  
**Linee**: 490-530 (metodi `_select_card`, `_move_cards`, `_draw_cards`, `_select_from_waste`)

#### Codice Attuale (ROTTO)

```python
# Line ~500 in _select_card()
def _select_card(self) -> None:
    success, message = self.engine.select_card_at_cursor()
    
    # Log card selection for analytics
    if success and "selezionat" in message.lower():
        try:
            pile = self.engine.cursor.get_current_pile()
            pile_name = self._get_pile_name(pile)
            log.card_moved(
                from_pile=pile_name,
                to_pile="selected",
                card="[card]",  # ❌ PLACEHOLDER - NO REAL VALUE
                success=True
            )
        except:
            pass  # Silent failure
```

**Problemi**:
- ❌ `card="[card]"` placeholder non sostituito con valore reale
- ❌ Try/except troppo ampio maschera errori reali
- ❌ Stesso problema in `_move_cards()` e `_select_from_waste()`

#### Codice Nuovo/Modificato

```python
# Line ~500 in _select_card() - FIXED
def _select_card(self) -> None:
    success, message = self.engine.select_card_at_cursor()
    
    # Log card selection for analytics
    if success and "selezionat" in message.lower():
        try:
            pile = self.engine.cursor.get_current_pile()
            pile_name = self._get_pile_name(pile)
            
            # ✅ FIX: Extract real card name
            card = pile.get_top_card() if pile else None
            card_name = card.get_name if card else "unknown"
            
            log.card_moved(
                from_pile=pile_name,
                to_pile="selected",
                card=card_name,  # ✅ REAL VALUE
                success=True
            )
        except Exception as e:
            # ✅ FIX: Log error instead of silent failure
            log.warning_issued("Logging", f"Failed to log card selection: {e}")
```

**Same Fix Required For** (4 locations total):
1. `_select_card()` - Line ~500
2. `_select_from_waste()` - Line ~550 (card from waste top)
3. `_move_cards()` - Line ~580 (cards from selection.selected_cards)
4. `_new_game()` - Line ~650 (already correct, no fix needed)

#### Rationale

**Perché funziona**:
1. `pile.get_top_card()` returns Card object with accessible `get_name` property
2. `card.get_name` returns formatted string like "7 di Picche"
3. Fallback to "unknown" prevents crashes if pile empty (defensive programming)
4. Logging error instead of silent pass helps debug future issues

**Non ci sono regressioni perché**:
- Solo logging code modificato (no game logic changes)
- Try/except previene crashes anche se logging fallisce
- Fallback "unknown" garantisce sempre string valida

#### Testing Commit 1

**Validazione Manuale**:
1. Run `python test.py`
2. Start new game (N key)
3. Select card with ENTER on tableau pile
4. Open `logs/solitario.log`
5. Verify entry: `"Move SUCCESS: [NOME CARTA REALE] from tableau_X to selected"`
6. ✅ PASS: Se nome carta reale presente (non "[card]")

**Expected Log Output**:
```
2026-02-14 15:30:12 - INFO - game - Move SUCCESS: 7 di Picche from tableau_3 to selected
2026-02-14 15:30:15 - INFO - game - Move SUCCESS: 7 di Picche from selected to foundation_1
2026-02-14 15:30:18 - DEBUG - game - Drew 3 card(s) from stock
```

**Commit Message**:
```
fix(logging): Extract real card names in gameplay events

Replace placeholder strings with actual card.get_name values:
- _select_card(): Extract from pile.get_top_card()
- _select_from_waste(): Extract from waste top
- _move_cards(): Extract from selection.selected_cards[0]

Add defensive fallback "unknown" for empty piles.
Log warnings instead of silent pass on extraction errors.

Impact:
- card_moved() logs now contain real card names ("7 di Picche")
- Analytics traceable per-card move sequences
- Coverage: +10% (gameplay actions now fully traceable)

Testing:
- Manual: Play 10 moves, verify logs/solitario.log contains real card names
- No unit tests (logging validation is manual)

Fixes: Placeholder context extraction issue from Phase 1
```

---

### COMMIT 2: Integrate Settings Change Tracking

**Priorità**: 🟠 ALTA  
**File**: `src/application/options_controller.py`  
**Linee**: 120-250 (tutti i metodi `cycle_*` e `toggle_*`)

#### Codice Attuale (NO LOGGING)

```python
# Line ~130 in cycle_difficulty()
def cycle_difficulty(self) -> str:
    """Cycle through difficulty levels (1-5).
    
    Returns:
        TTS announcement message
    """
    # Cycle difficulty (1 → 2 → 3 → 4 → 5 → 1)
    self.settings.difficulty_level = (self.settings.difficulty_level % 5) + 1
    
    # ❌ NO LOGGING - Missing tracking
    
    return f"Difficoltà: livello {self.settings.difficulty_level}"
```

**Problemi**:
- ❌ Nessun logging quando settings cambiano
- ❌ Audit trail configurazioni utente impossibile
- ❌ Analytics preferenze difficoltà non tracciabili

#### Codice Nuovo/Modificato

```python
# Import at top of file
from src.infrastructure.logging import game_logger as log

# Line ~130 in cycle_difficulty() - FIXED
def cycle_difficulty(self) -> str:
    """Cycle through difficulty levels (1-5).
    
    Returns:
        TTS announcement message
    """
    # ✅ FIX: Capture old value before change
    old_value = self.settings.difficulty_level
    
    # Cycle difficulty (1 → 2 → 3 → 4 → 5 → 1)
    self.settings.difficulty_level = (self.settings.difficulty_level % 5) + 1
    new_value = self.settings.difficulty_level
    
    # ✅ FIX: Log setting change
    log.settings_changed("difficulty_level", old_value, new_value)
    
    return f"Difficoltà: livello {new_value}"
```

**Same Pattern Required For** (8 methods total):

1. **`cycle_difficulty()`** - Line ~130
   ```python
   old = self.settings.difficulty_level
   # ... change ...
   log.settings_changed("difficulty_level", old, self.settings.difficulty_level)
   ```

2. **`toggle_timer()`** - Line ~160
   ```python
   old = self.settings.max_time_game
   # ... toggle ...
   log.settings_changed("timer_enabled", old > 0, self.settings.max_time_game > 0)
   ```

3. **`increment_timer()`** - Line ~185 (if timer enabled)
   ```python
   if self.settings.max_time_game > 0:
       old = self.settings.max_time_game
       self.settings.max_time_game += 60  # +1 minute
       log.settings_changed("max_time_game", old, self.settings.max_time_game)
   ```

4. **`decrement_timer()`** - Line ~200 (if timer enabled)
   ```python
   if self.settings.max_time_game > 300:  # Min 5 minutes
       old = self.settings.max_time_game
       self.settings.max_time_game -= 60  # -1 minute
       log.settings_changed("max_time_game", old, self.settings.max_time_game)
   ```

5. **`cycle_draw_count()`** - Line ~215 (difficulty 1-3 only)
   ```python
   old = self.settings.draw_count
   # ... cycle ...
   log.settings_changed("draw_count", old, self.settings.draw_count)
   ```

6. **`toggle_shuffle_discards()`** - Line ~235
   ```python
   old = self.settings.shuffle_discards
   self.settings.shuffle_discards = not self.settings.shuffle_discards
   log.settings_changed("shuffle_discards", old, self.settings.shuffle_discards)
   ```

7. **`toggle_command_hints()`** - Line ~250 (if exists)
   ```python
   old = self.settings.command_hints_enabled
   self.settings.command_hints_enabled = not self.settings.command_hints_enabled
   log.settings_changed("command_hints_enabled", old, self.settings.command_hints_enabled)
   ```

8. **`cycle_deck_type()`** - Line ~270 (if exists)
   ```python
   old = self.settings.deck_type
   # ... cycle french/neapolitan ...
   log.settings_changed("deck_type", old, self.settings.deck_type)
   ```

#### Rationale

**Perché funziona**:
1. Capture old value BEFORE modification (critical for diff tracking)
2. Log AFTER modification completes (ensures new value committed)
3. Log only when actual change happens (avoid noise for no-ops)
4. Use semantic setting names ("difficulty_level" not "option1")

**Non ci sono regressioni perché**:
- Logging code non influenza game logic (observer pattern)
- Se logging fallisce, try/except in game_logger.py previene crash
- Settings già modificate prima del log (no side effects)

#### Testing Commit 2

**Validazione Manuale**:
1. Run `python test.py`
2. Press O (open options)
3. Press SPACE on "Difficoltà" (cycle: 1 → 2)
4. Press T (toggle timer: OFF → ON)
5. Press SPACE on "Pesca" (cycle draw count)
6. Check `logs/solitario.log`

**Expected Log Output**:
```
2026-02-14 15:35:00 - INFO - game - Setting changed: difficulty_level = 1 → 2
2026-02-14 15:35:05 - INFO - game - Setting changed: timer_enabled = False → True
2026-02-14 15:35:10 - INFO - game - Setting changed: draw_count = 1 → 2
```

**Commit Message**:
```
feat(logging): Track all settings changes in OptionsController

Integrate log.settings_changed() calls in 8 methods:
- cycle_difficulty(): Track difficulty_level (1-5)
- toggle_timer(): Track timer_enabled (bool)
- increment/decrement_timer(): Track max_time_game (seconds)
- cycle_draw_count(): Track draw_count (1-3)
- toggle_shuffle_discards(): Track shuffle_discards (bool)
- toggle_command_hints(): Track command_hints_enabled (bool)
- cycle_deck_type(): Track deck_type (french/neapolitan)

Pattern:
1. Capture old value BEFORE change
2. Modify setting
3. Log change with old/new values

Impact:
- Complete audit trail for user preferences
- Analytics: most popular difficulty levels, timer usage
- Coverage: +10% (settings events now tracked)

Testing:
- Manual: Open options, cycle 5 settings, verify logs
- No unit tests (validation is log inspection)

Closes: Settings tracking gap from Phase 1
```

---

### COMMIT 3: Add Error Handling with Logging

**Priorità**: 🟠 ALTA  
**File**: `src/application/gameplay_controller.py`, `src/domain/services/game_service.py`  
**Linee**: Multiple methods (see below)

#### Codice Attuale (NO ERROR HANDLING)

```python
# Line ~700 in handle_wx_key_event()
def handle_wx_key_event(self, event) -> bool:
    """Handle wxPython keyboard events.
    
    Returns:
        True if key handled, False otherwise
    """
    import wx
    
    key_code = event.GetKeyCode()
    # ❌ NO TRY/EXCEPT - Crashes on invalid key_code
    
    has_shift = bool(event.GetModifiers() & wx.MOD_SHIFT)
    has_ctrl = bool(event.GetModifiers() & wx.MOD_CONTROL)
    
    # ... routing logic ...
```

**Problemi**:
- ❌ Invalid keycode crashes app (no error log)
- ❌ Exception in routing logic non tracciata
- ❌ Debugging issues difficile (no stacktrace in logs)

#### Codice Nuovo/Modificato

```python
# Import at top
from src.infrastructure.logging import game_logger as log

# Line ~700 in handle_wx_key_event() - FIXED
def handle_wx_key_event(self, event) -> bool:
    """Handle wxPython keyboard events.
    
    Returns:
        True if key handled, False otherwise
    """
    try:
        import wx
        
        key_code = event.GetKeyCode()
        has_shift = bool(event.GetModifiers() & wx.MOD_SHIFT)
        has_ctrl = bool(event.GetModifiers() & wx.MOD_CONTROL)
        
        # ... routing logic ...
        
    except Exception as e:
        # ✅ FIX: Log error with full traceback
        log.error_occurred(
            "InputParsing",
            f"Failed to handle key event: {e}",
            exception=e
        )
        return False  # Key not handled due to error
```

**Same Pattern Required For** (3 methods total):

1. **`GameplayController.handle_wx_key_event()`** - Line ~700
   - Wrap entire method body in try/except
   - Category: "InputParsing"
   - Return False on error (key not handled)

2. **`GameService.move_card()`** - Line ~180
   - Wrap validation and execution logic
   - Category: "MoveValidation"
   - Return (False, error_message) on exception
   ```python
   def move_card(self, source_pile, target_pile, card_count=1, is_foundation_target=False):
       try:
           # ... existing validation ...
           # ... execute move ...
       except Exception as e:
           log.error_occurred("MoveValidation", f"Move failed: {e}", exception=e)
           return False, f"Errore interno: {str(e)}"
   ```

3. **`OptionsController.save_settings()`** - (if method exists, check file)
   - Wrap file I/O operations
   - Category: "FileIO"
   - Return error message on failure
   ```python
   def save_settings(self) -> str:
       try:
           # ... save to JSON ...
           return "Settings salvate"
       except Exception as e:
           log.error_occurred("FileIO", f"Failed to save settings: {e}", exception=e)
           return "Errore salvataggio impostazioni"
   ```

#### Rationale

**Perché funziona**:
1. Try/except at method level cattura tutte le exception (comprehensive coverage)
2. `exception=e` parameter in `error_occurred()` triggera `exc_info=True` in logger → full traceback
3. Graceful degradation: return error state instead of crash
4. Error categories ("InputParsing", "MoveValidation", "FileIO") aiutano filtering logs

**Non ci sono regressioni perché**:
- Solo wrapping code esistente (no logic changes)
- Return values preservati (False/error message)
- Normal flow non affetto (try block stesso codice originale)

#### Testing Commit 3

**Validazione Manuale** (hard to trigger exceptions manually):
1. Run `python test.py`
2. Play normally (no errors expected)
3. Optionally: Inject error (modify code temporaneamente)
   ```python
   # In handle_wx_key_event, add after key_code:
   if key_code == ord('Z'):
       raise ValueError("Test error injection")
   ```
4. Press Z key
5. Check `logs/solitario.log` for traceback

**Expected Log Output** (on injected error):
```
2026-02-14 15:40:00 - ERROR - error - ERROR [InputParsing]: Failed to handle key event: Test error injection
Traceback (most recent call last):
  File "src/application/gameplay_controller.py", line 715, in handle_wx_key_event
    raise ValueError("Test error injection")
ValueError: Test error injection
```

**Commit Message**:
```
feat(logging): Add error handling with traceback logging

Wrap risky methods in try/except with log.error_occurred():

1. GameplayController.handle_wx_key_event() (Line ~700)
   - Catches invalid keycode parsing errors
   - Category: "InputParsing"
   - Returns False on error (key not handled)

2. GameService.move_card() (Line ~180)
   - Catches validation and execution errors
   - Category: "MoveValidation"
   - Returns (False, error_msg) on exception

3. OptionsController.save_settings() (if exists)
   - Catches file I/O errors
   - Category: "FileIO"
   - Returns error message instead of crash

Pattern:
- Try/except at method level (comprehensive coverage)
- log.error_occurred(category, message, exception=e)
- Graceful degradation (return error state, no crash)

Impact:
- Full stacktraces in logs for debugging
- App continues on errors (no crash)
- Coverage: +5% (error paths now logged)

Testing:
- Manual: Play normally, no errors expected
- Error injection test: Verify traceback in logs

Closes: Error handling gap from Phase 1
```

---

### COMMIT 4: Add Navigation Analytics (Optional)

**Priorità**: 🟡 MEDIA (Can be skipped if time-constrained)  
**File**: `src/domain/services/cursor_manager.py`  
**Linee**: 100-300 (metodi `move_up/down/left/right/tab`, `jump_to_pile`)

#### Codice Attuale (NO NAVIGATION LOGGING)

```python
# Line ~120 in move_up()
def move_up(self) -> Tuple[str, Optional[str]]:
    """Move cursor to previous card in pile.
    
    Returns:
        Tuple[str, Optional[str]]: (message, hint)
    """
    # ❌ NO LOGGING - Navigation not tracked
    
    if self.card_idx > 0:
        self.card_idx -= 1
        # ... generate message ...
    return (message, hint)
```

**Problemi**:
- ❌ Arrow keys navigation non tracciata
- ❌ UX heatmap impossibile (which piles visited most)
- ❌ User exploration patterns non analizzabili

#### Codice Nuovo/Modificato

```python
# Import at top
from src.infrastructure.logging import game_logger as log

# Line ~120 in move_up() - FIXED
def move_up(self) -> Tuple[str, Optional[str]]:
    """Move cursor to previous card in pile.
    
    Returns:
        Tuple[str, Optional[str]]: (message, hint)
    """
    # ✅ FIX: Capture old position before move
    old_position = f"{self._get_pile_name()}[{self.card_idx}]"
    
    if self.card_idx > 0:
        self.card_idx -= 1
        # ... generate message ...
        
        # ✅ FIX: Log cursor movement (DEBUG level)
        new_position = f"{self._get_pile_name()}[{self.card_idx}]"
        log.cursor_moved(old_position, new_position)
    
    return (message, hint)

def _get_pile_name(self) -> str:
    """Helper to get current pile name for logging.
    
    Returns:
        String like "tableau_3", "foundation_1", "stock", "waste"
    """
    if 0 <= self.pile_idx <= 6:
        return f"tableau_{self.pile_idx + 1}"
    elif 7 <= self.pile_idx <= 10:
        return f"foundation_{self.pile_idx - 6}"
    elif self.pile_idx == 11:
        return "waste"
    elif self.pile_idx == 12:
        return "stock"
    return "unknown"
```

**Same Pattern Required For** (5 methods total):

1. **`move_up()`** - Line ~120
2. **`move_down()`** - Line ~150
3. **`move_left()`** - Line ~180 (pile change → use `pile_jumped` instead)
4. **`move_right()`** - Line ~210 (pile change → use `pile_jumped` instead)
5. **`jump_to_pile()`** - Line ~250 (direct jump → use `pile_jumped`)

**Note**: 
- `move_up/down`: Within same pile → use `cursor_moved()`
- `move_left/right/jump`: Between piles → use `pile_jumped()`

#### Rationale

**Perché funziona**:
1. DEBUG level previene noise in INFO logs (high frequency events)
2. Position format `"tableau_3[5]"` è human-readable e parseable
3. Helper `_get_pile_name()` centralizza naming logic (DRY)
4. Logging AFTER move completes (ensures position valid)

**Non ci sono regressioni perché**:
- Solo logging aggiunto (no cursor logic changes)
- DEBUG level (disabilitabile in production)
- Logging errors catturati da game_logger.py try/except

#### Testing Commit 4

**Validazione Manuale**:
1. Configure log level DEBUG in `logger_setup.py` (if not already)
   ```python
   # In setup_logging():
   file_handler.setLevel(logging.DEBUG)  # Enable DEBUG logs
   ```
2. Run `python test.py`
3. Press Arrow UP/DOWN (navigate cards)
4. Press Arrow LEFT/RIGHT (change piles)
5. Press "3" key (jump to tableau 3)
6. Check `logs/solitario.log`

**Expected Log Output**:
```
2026-02-14 15:45:00 - DEBUG - game - Cursor: tableau_1[3] → tableau_1[2]
2026-02-14 15:45:02 - DEBUG - game - Pile jump: tableau_1 → tableau_3
2026-02-14 15:45:05 - DEBUG - game - Cursor: tableau_3[5] → tableau_3[6]
```

**Commit Message**:
```
feat(logging): Add DEBUG navigation analytics tracking

Integrate cursor movement logging in CursorManager:

1. move_up/move_down (Lines ~120, ~150)
   - Log cursor_moved(old_pos, new_pos)
   - Format: "tableau_3[5] → tableau_3[4]"
   - DEBUG level (high frequency events)

2. move_left/move_right (Lines ~180, ~210)
   - Log pile_jumped(old_pile, new_pile)
   - Format: "tableau_1 → tableau_2"

3. jump_to_pile (Line ~250)
   - Log pile_jumped for direct jumps (1-7 keys)

Add helper _get_pile_name() for consistent naming:
- tableau_1 to tableau_7
- foundation_1 to foundation_4
- stock, waste

Impact:
- UX heatmap analytics capability
- User navigation pattern tracking
- Coverage: +5% (navigation events tracked)
- Optional: Can disable in production (DEBUG level)

Testing:
- Manual: Enable DEBUG logs, navigate with arrows/numbers
- Verify logs contain movement entries

Closes: Navigation analytics gap from Phase 1
```

---

## 🧪 Testing Strategy

### Manual Validation (PRIMARY - No unit tests needed)

Logging validation è intrinsecamente manuale (inspect log files).

#### Full Coverage Test Scenario (20 min)

**Setup**:
1. Delete `logs/solitario.log` (fresh start)
2. Run `python test.py`

**Test Sequence**:

```
1. NEW GAME (N key)
   ✅ Verify: "New game started - Deck: draw_three, Difficulty: medium, Timer: True"

2. CARD SELECTION (ENTER on tableau card)
   ✅ Verify: "Move SUCCESS: [NOME CARTA REALE] from tableau_X to selected"
   ❌ FAIL IF: "Move SUCCESS: [card] from tableau_X to selected" (placeholder)

3. CARD MOVE (SPACE on foundation)
   ✅ Verify: "Move SUCCESS: [NOME CARTA] from selected to foundation_Y"

4. DRAW CARDS (D key)
   ✅ Verify: "Drew 3 card(s) from stock" (DEBUG level)

5. OPEN OPTIONS (O key)
   ✅ Verify: "Panel transition: gameplay → options" (se panel logging presente)

6. CYCLE DIFFICULTY (SPACE on difficulty option)
   ✅ Verify: "Setting changed: difficulty_level = 2 → 3"

7. TOGGLE TIMER (T key in options)
   ✅ Verify: "Setting changed: timer_enabled = True → False"

8. CLOSE OPTIONS (ESC key)
   ✅ Verify: "Panel transition: options → gameplay"

9. NAVIGATION (Arrow UP)
   ✅ Verify: "Cursor: tableau_3[5] → tableau_3[4]" (DEBUG level)

10. PILE JUMP ("3" key)
    ✅ Verify: "Pile jump: tableau_1 → tableau_3" (DEBUG level)

11. INFO QUERY (G key - table info)
    ✅ Verify: "Info query: table_info"

12. GAME END (Force win or abandon with ESC)
    ✅ Verify: "Game WON" or "Game ABANDONED" with stats

13. APP SHUTDOWN (ALT+F4 or close window)
    ✅ Verify: "Application shutdown requested"
```

**Success Criteria**:
- ✅ All 13 verifications PASS
- ✅ Real card names present (no "[card]" placeholders)
- ✅ Settings changes logged with old/new values
- ✅ No crashes during test sequence

#### Error Injection Test (5 min - Optional)

**Inject error in code**:
```python
# In gameplay_controller.py handle_wx_key_event():
if key_code == ord('Z'):
    raise ValueError("Test error injection")
```

**Test**:
1. Press Z key
2. Verify log contains:
   - `"ERROR [InputParsing]: Failed to handle key event: Test error injection"`
   - Full traceback with line numbers
3. Verify app continues (no crash)

**Cleanup**: Remove injected error code

---

## ✅ Validation & Acceptance

### Success Criteria

**Funzionali**:
- [ ] Real card names in all `card_moved()` logs (no placeholders)
- [ ] All 5 settings changes logged when modified in options
- [ ] Errors logged with full traceback (test with injection)
- [ ] Navigation analytics logged at DEBUG level

**Coverage Target**:
- [ ] **90-95% coverage** achieved (from 70% baseline)
- [ ] Gap reduction: 25-30 percentage points

**Tecnici**:
- [ ] Zero breaking changes (no API modifications)
- [ ] No performance regression (<0.1ms per log call)
- [ ] Logs directory auto-created (already working)
- [ ] Log rotation working (5MB max, 5 backups)

**Code Quality**:
- [ ] 4 commit atomici con conventional messages
- [ ] Ogni commit compila senza errori
- [ ] CHANGELOG.md aggiornato per v2.3.1
- [ ] Documentation PLAN file completato

---

## 🚨 Common Pitfalls to Avoid

### ❌ DON'T: Log BEFORE capturing old value

```python
# WRONG - old value already changed!
def cycle_difficulty(self):
    self.settings.difficulty_level += 1  # Changed!
    old = self.settings.difficulty_level  # ❌ This is NEW value
    log.settings_changed("difficulty", old, self.settings.difficulty_level)
```

**Problema**: Old/new values identici (diff impossibile)

### ✅ DO: Capture old BEFORE change

```python
# CORRECT
def cycle_difficulty(self):
    old = self.settings.difficulty_level  # ✅ Capture BEFORE
    self.settings.difficulty_level += 1   # Then change
    log.settings_changed("difficulty", old, self.settings.difficulty_level)
```

---

### ❌ DON'T: Use generic exception without logging

```python
# WRONG - silent failure, no traceback
try:
    dangerous_operation()
except:
    pass  # ❌ Error lost forever
```

### ✅ DO: Log exception with traceback

```python
# CORRECT
try:
    dangerous_operation()
except Exception as e:
    log.error_occurred("Category", f"Operation failed: {e}", exception=e)
    return error_state  # Graceful degradation
```

---

### ❌ DON'T: Log at wrong level

```python
# WRONG - Arrow keys logging at INFO (too noisy)
log.cursor_moved(old, new)  # Called 100+ times per minute
# Result: INFO logs bloated, hard to read
```

### ✅ DO: Use DEBUG for high-frequency events

```python
# CORRECT - Already in game_logger.py
def cursor_moved(from_pos, to_pos):
    _game_logger.debug(f"Cursor: {from_pos} → {to_pos}")  # DEBUG level
```

---

## 📦 Commit Strategy

### Atomic Commits (4 totali)

1. **Commit 1**: Gameplay - Context Extraction Fix
   - `fix(logging): Extract real card names in gameplay events`
   - Files: `src/application/gameplay_controller.py`
   - Tests: Manual log inspection
   - Duration: ~1h

2. **Commit 2**: Settings - Change Tracking Integration
   - `feat(logging): Track all settings changes in OptionsController`
   - Files: `src/application/options_controller.py`
   - Tests: Manual options cycling + log inspection
   - Duration: ~2h

3. **Commit 3**: Error Handling - Wrap Risky Methods
   - `feat(logging): Add error handling with traceback logging`
   - Files: `src/application/gameplay_controller.py`, `src/domain/services/game_service.py`
   - Tests: Manual error injection + log inspection
   - Duration: ~1.5h

4. **Commit 4**: Navigation - Analytics Tracking (Optional)
   - `feat(logging): Add DEBUG navigation analytics tracking`
   - Files: `src/domain/services/cursor_manager.py`
   - Tests: Manual arrow key navigation + log inspection
   - Duration: ~1h

**Total Duration**: 5-6 hours (4.5h implementation + 1-1.5h testing)

---

## 📝 Note Operative per Copilot

### Istruzioni Step-by-Step

#### COMMIT 1: Context Extraction Fix

1. Apri `src/application/gameplay_controller.py`
2. Naviga a line ~500 (metodo `_select_card`)
3. Trova sezione logging esistente con placeholder `card="[card]"`
4. **PRIMA del log call**:
   ```python
   # Extract real card name
   card = pile.get_top_card() if pile else None
   card_name = card.get_name if card else "unknown"
   ```
5. **Modifica log call**:
   ```python
   log.card_moved(
       from_pile=pile_name,
       to_pile="selected",
       card=card_name,  # Changed from "[card]"
       success=True
   )
   ```
6. **Ripeti per altri 2 metodi**:
   - `_select_from_waste()` (line ~550): Extract from `self.table.pile_scarti.get_top_card()`
   - `_move_cards()` (line ~580): Extract from `self.selection.selected_cards[0].get_name`
7. **Modifica exception handling**:
   - Replace `except: pass` with:
   ```python
   except Exception as e:
       log.warning_issued("Logging", f"Failed to log: {e}")
   ```
8. **Test manuale**: Run game, select card, check log
9. **Commit**: Use exact message from "COMMIT 1" section above

---

#### COMMIT 2: Settings Tracking

1. Apri `src/application/options_controller.py`
2. **Top of file**: Add import
   ```python
   from src.infrastructure.logging import game_logger as log
   ```
3. **Per ogni metodo** `cycle_*` e `toggle_*` (8 totali):
   
   a. Trova inizio metodo (es. `def cycle_difficulty(self):`)
   
   b. **PRIMA della modifica setting**, aggiungi:
   ```python
   old_value = self.settings.[NOME_SETTING]
   ```
   
   c. **DOPO la modifica setting**, aggiungi:
   ```python
   log.settings_changed("[NOME_SETTING]", old_value, self.settings.[NOME_SETTING])
   ```
   
   d. **Settings da tracciare**:
   - `cycle_difficulty()` → "difficulty_level"
   - `toggle_timer()` → "timer_enabled" (bool: max_time_game > 0)
   - `increment_timer()` → "max_time_game" (if timer enabled)
   - `decrement_timer()` → "max_time_game" (if timer enabled)
   - `cycle_draw_count()` → "draw_count"
   - `toggle_shuffle_discards()` → "shuffle_discards"
   - `toggle_command_hints()` → "command_hints_enabled"
   - `cycle_deck_type()` → "deck_type" (if exists)

4. **Test manuale**: Open options, cycle 5 settings, check log
5. **Commit**: Use exact message from "COMMIT 2" section above

---

#### COMMIT 3: Error Handling

1. **File 1**: `src/application/gameplay_controller.py`
   - Metodo: `handle_wx_key_event()` (line ~700)
   - **Wrap entire method body**:
   ```python
   def handle_wx_key_event(self, event) -> bool:
       try:
           # EXISTING CODE HERE (all lines)
       except Exception as e:
           log.error_occurred("InputParsing", f"Key event error: {e}", exception=e)
           return False
   ```

2. **File 2**: `src/domain/services/game_service.py`
   - Metodo: `move_card()` (line ~180)
   - **Wrap validation + execution**:
   ```python
   def move_card(self, source, target, count=1, is_foundation=False):
       try:
           # EXISTING VALIDATION + EXECUTION CODE
       except Exception as e:
           log.error_occurred("MoveValidation", f"Move error: {e}", exception=e)
           return False, f"Errore: {str(e)}"
   ```

3. **File 3** (optional): `src/application/options_controller.py`
   - Metodo: `save_settings()` (if exists)
   - **Wrap file I/O**:
   ```python
   def save_settings(self) -> str:
       try:
           # EXISTING SAVE CODE
       except Exception as e:
           log.error_occurred("FileIO", f"Save error: {e}", exception=e)
           return "Errore salvataggio"
   ```

4. **Test manuale**: Inject error (add `if key_code == ord('Z'): raise ValueError("test")`), press Z, check log for traceback
5. **Cleanup**: Remove injected error
6. **Commit**: Use exact message from "COMMIT 3" section above

---

#### COMMIT 4: Navigation Analytics (Optional)

1. Apri `src/domain/services/cursor_manager.py`
2. **Top of file**: Add import
   ```python
   from src.infrastructure.logging import game_logger as log
   ```
3. **Add helper method** (end of class):
   ```python
   def _get_pile_name(self) -> str:
       """Get current pile name for logging."""
       if 0 <= self.pile_idx <= 6:
           return f"tableau_{self.pile_idx + 1}"
       elif 7 <= self.pile_idx <= 10:
           return f"foundation_{self.pile_idx - 6}"
       elif self.pile_idx == 11:
           return "waste"
       elif self.pile_idx == 12:
           return "stock"
       return "unknown"
   ```
4. **Modify 5 methods**:
   - `move_up()` / `move_down()`: Add `log.cursor_moved(old_pos, new_pos)` after move
   - `move_left()` / `move_right()`: Add `log.pile_jumped(old_pile, new_pile)` after move
   - `jump_to_pile()`: Add `log.pile_jumped(old_pile, new_pile)` after jump
   
   **Pattern**:
   ```python
   def move_up(self) -> Tuple[str, Optional[str]]:
       old_pos = f"{self._get_pile_name()}[{self.card_idx}]"
       
       if self.card_idx > 0:
           self.card_idx -= 1
           # ... existing message generation ...
           
           new_pos = f"{self._get_pile_name()}[{self.card_idx}]"
           log.cursor_moved(old_pos, new_pos)
       
       return (message, hint)
   ```

5. **Test manuale**: Enable DEBUG logs, press arrows/numbers, check log
6. **Commit**: Use exact message from "COMMIT 4" section above

---

### Verifica Rapida Pre-Commit

```bash
# Syntax check
python -m py_compile src/application/gameplay_controller.py
python -m py_compile src/application/options_controller.py
python -m py_compile src/domain/services/game_service.py
python -m py_compile src/domain/services/cursor_manager.py

# Run app (manual test)
python test.py
# Play 5 minutes, check logs/solitario.log

# Check log file exists and has content
cat logs/solitario.log | grep "Move SUCCESS" | head -5
cat logs/solitario.log | grep "Setting changed" | head -3
```

---

## 🚀 Risultato Finale Atteso

Una volta completati tutti e 4 i commit:

✅ **Coverage: 90-95%** (da 70% baseline)
✅ **Real card names**: Logs tracciabili per analytics mosse
✅ **Settings audit trail**: Tutte le modifiche configurazioni tracciate
✅ **Error traces**: Full stacktrace per debugging production issues
✅ **Navigation heatmap**: (Optional) UX analytics pile frequency

**Expected Log Sample** (dopo 5 min gameplay):
```
2026-02-14 15:00:00 - INFO - game - Application started - wxPython solitaire v2.3.0
2026-02-14 15:00:05 - INFO - game - New game started - Deck: draw_three, Difficulty: medium, Timer: True
2026-02-14 15:00:10 - INFO - game - Move SUCCESS: 7 di Picche from tableau_3 to selected
2026-02-14 15:00:12 - INFO - game - Move SUCCESS: 7 di Picche from selected to foundation_1
2026-02-14 15:00:15 - DEBUG - game - Drew 3 card(s) from stock
2026-02-14 15:00:20 - INFO - game - Setting changed: difficulty_level = 2 → 3
2026-02-14 15:00:25 - INFO - game - Setting changed: timer_enabled = True → False
2026-02-14 15:00:30 - DEBUG - game - Cursor: tableau_3[5] → tableau_3[4]
2026-02-14 15:00:35 - DEBUG - game - Pile jump: tableau_1 → tableau_3
2026-02-14 15:00:40 - INFO - game - Info query: table_info
2026-02-14 15:05:00 - INFO - game - Game WON - Time: 300s, Moves: 87, Score: 1250
2026-02-14 15:05:10 - INFO - game - Application shutdown requested
```

**Metriche Successo**:
- ✅ Real card names in all move logs (no "[card]" placeholders)
- ✅ All 5+ settings changes logged when modified
- ✅ Error injection test produces full traceback
- ✅ Navigation analytics present (if COMMIT 4 completed)
- ✅ No crashes during 30min gameplay session

---

## 📞 Support and Questions

Per domande durante implementazione:

1. **Riferimento**: Questo documento (`docs/PLAN_LOGGING_COMPLETE_COVERAGE_PHASE2.md`)
2. **Phase 1 Plan**: `docs/PLAN_LOGGING_COMPLETE_COVERAGE.md` (infrastructure base)
3. **Codice Esistente**: Studiare pattern in `src/infrastructure/logging/game_logger.py`
4. **Template Helpers**: Tutti i 20+ helpers già implementati in `game_logger.py`
5. **GitHub PR**: PR #60 contiene Phase 1 implementation

---

## 📊 Progress Tracking

| Fase | Status | Commit SHA | Data Completamento | Note |
|------|--------|-----------|-------------------|------|
| COMMIT 1: Context Fix | [ ] | - | - | Priority 🔴 CRITICA |
| COMMIT 2: Settings | [ ] | - | - | Priority 🟠 ALTA |
| COMMIT 3: Errors | [ ] | - | - | Priority 🟠 ALTA |
| COMMIT 4: Navigation | [ ] | - | - | Priority 🟡 MEDIA (optional) |
| Manual Testing | [ ] | - | - | 20 min full scenario |
| Review & Merge | [ ] | - | - | Final validation |

---

**Plan Version**: v1.0  
**Ultima Modifica**: 2026-02-14  
**Autore**: AI Assistant + Nemex81  
**Based On**: Phase 1 gap analysis + Template v1.0  

---

## 📝 Final Notes

**Priority Execution Order**:
1. **MUST DO**: COMMIT 1 (context fix) + COMMIT 2 (settings) → 80% coverage
2. **SHOULD DO**: COMMIT 3 (errors) → 85% coverage
3. **NICE TO HAVE**: COMMIT 4 (navigation) → 90-95% coverage

**Time Budget**:
- Minimum viable (COMMIT 1+2): 3 hours
- Recommended (COMMIT 1+2+3): 4.5 hours
- Complete (all 4): 5.5-6 hours

**Testing Strategy**:
- NO unit tests (logging validation is manual)
- Manual log inspection after each commit
- Full 20min scenario at end
- Error injection test optional but recommended

**Merge Strategy**:
- All commits on same branch: `copilot/implement-centralized-logging-system`
- Squash NOT recommended (keep atomic commits for git history)
- After merge → create v2.3.1 tag
- Update CHANGELOG.md with Phase 2 completion

---

**Happy Coding! 🚀**
