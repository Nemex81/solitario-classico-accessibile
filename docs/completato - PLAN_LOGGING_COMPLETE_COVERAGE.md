# 📋 Piano Implementazione: Coverage Completa Sistema Logging

> Integrazione eventi gameplay/domain/settings per analytics e debug avanzato

---

## 📊 Executive Summary

**Tipo**: FEATURE EXTENSION  
**Priorità**: 🟠 ALTA  
**Stato**: READY  
**Branch**: `copilot/implement-centralized-logging-system`  
**Versione Target**: `v2.3.0` (stesso branch logging foundation)  
**Data Creazione**: 2026-02-14  
**Autore**: AI Assistant + Nemex81  
**Effort Stimato**: 2.5 ore totali (1.5 ore implementazione + 1 ora testing)  
**Commits Previsti**: 4 commit incrementali

---

### Problema/Obiettivo

**STATO ATTUALE (Post-Copilot)**:
Infrastruttura logging completata (foundation + semantic helpers) ma **integrazione parziale**:
- ✅ App lifecycle (startup/shutdown)
- ✅ Panel transitions (WindowController)
- ✅ Dialog lifecycle (WxDialogProvider)
- ❌ GameplayController events (60+ comandi tastiera)
- ❌ Domain events (mosse carte, vittoria, riciclo)
- ❌ Settings changes (difficulty, timer, deck type)
- ❌ Error handling sistemico
- ❌ Navigation granular (arrow keys, pile jumps)
- ❌ Query commands tracking (info requests)
- ❌ Timer lifecycle events

**Coverage attuale**: ~15% eventi sistema (solo infra + UI base)
**Coverage target**: 95%+ eventi sistema (gameplay + domain + settings + errors)

**OBIETTIVO**:
Integrare logging in tutti i punti critici del sistema per:
1. **Debug facilitato**: Tracciare sequenze azioni utente che portano a bug
2. **Analytics gameplay**: Win rate, tempo medio, mosse per vittoria, strategy patterns
3. **UX insights**: Comandi più usati, info query frequency, navigation heatmap
4. **Crash reports**: Full stacktrace + game state per ogni exception
5. **Settings analytics**: Difficulty distribution, timer usage, preferences trends

---

### Root Cause Analysis: Perché Coverage Incompleta

**Causa 1: GameplayController non modificato**
- File `src/application/gameplay_controller.py` ancora versione legacy
- Zero import `game_logger`, nessuna chiamata log helpers
- Gestisce 60+ comandi tastiera ma non logga nulla
- **Impact**: Missing 70% eventi user-facing (mosse, draw, navigation)

**Causa 2: Domain Layer ignorato**
- GameEngine/GameService eseguono state transitions ma non loggano
- Eventi critici (vittoria, riciclo, validazione mosse) non tracciati
- **Impact**: Analytics impossibili (win rate, strategy patterns)

**Causa 3: Settings Changes non tracciati**
- OptionsController modifica settings ma non logga cambiamenti
- Impossibile capire user preferences o A/B test effectiveness
- **Impact**: No visibility su configurazioni più popolari

**Causa 4: Exception Handling ad-hoc**
- Try-except blocks sparsi nel codice senza logging
- Eccezioni catturate ma non registrate con stacktrace
- **Impact**: Bug reports incompleti, debug post-mortem impossibile

---

### Soluzione Proposta

**Approccio 4-Layer Incremental Integration**:

```
┌─────────────────────────────────────────────────────────────┐
│ COMMIT 1: GameplayController (User Actions)                 │
│ - Card moves (select, move, cancel)                         │
│ - Draw cards / waste recycle                                │
│ - Game lifecycle (new, abandon)                             │
│ Coverage: +50% (60+ comandi tastiera)                       │
└─────────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ COMMIT 2: Domain Layer (Game Events)                        │
│ - Victory detection + stats                                 │
│ - Move validation failures                                  │
│ - Waste recycle counter                                     │
│ Coverage: +20% (state transitions critiche)                 │
└─────────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ COMMIT 3: Settings + Error Handling                         │
│ - Settings changes tracking                                 │
│ - Exception handlers con stacktrace                         │
│ - Timer lifecycle events                                    │
│ Coverage: +15% (configuration + reliability)                │
└─────────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ COMMIT 4: Granular Events (Analytics Advanced)              │
│ - Navigation tracking (DEBUG level)                         │
│ - Query commands (info requests)                            │
│ - TTS feedback tracking                                     │
│ Coverage: +10% (UX analytics dettagliate)                   │
└─────────────────────────────────────────────────────────────┘

Coverage Finale: 95%+ eventi sistema
```

**Pattern Architetturale**:
1. **Non-intrusive**: Log come side-effect, zero alterazioni business logic
2. **Strategic placement**: Log DOPO operazione (quando success/failure noto)
3. **Context-rich**: Include pile names, card details, reason failures
4. **Level-appropriate**: INFO per eventi user-facing, DEBUG per granular, ERROR per exceptions
5. **Performance-conscious**: Skip verbose logs in hot paths (arrow keys solo DEBUG level)

---

## 🎯 Requisiti Funzionali Dettagliati

### COMMIT 1: GameplayController Integration

#### 1.1 Card Move Tracking

**Comportamento Atteso**:
1. User presses ENTER → select card under cursor
2. System logs: `Move SUCCESS: 7♥ from tableau_3 to selected`
3. User presses SPACE → move to foundation
4. System logs: `Move SUCCESS: 7♥ from selected to foundation_1`
5. Invalid move attempt → `Move FAILED: 7♥ from tableau_3 to foundation_1`

**Helper Function Call**:
```python
log.card_moved(
    from_pile="tableau_3",  # Source pile name
    to_pile="foundation_1",  # Target pile name
    card="7♥",               # Card representation
    success=True             # Move result
)
```

**Integration Points** (GameplayController):
- `_select_card()` - Line ~370
- `_move_cards()` - Line ~385
- `_select_from_waste()` - Line ~355 (CTRL+ENTER)

**Context Extraction**:
```python
# Get current pile name
pile_name = self.engine.cursor_manager.get_current_pile_name()

# Format card (rank + suit symbols)
card_str = self._format_card(card_obj)  # "A♠", "10♦", etc.

# Extract from/to from move result
move_result = self.engine.execute_move()
from_pile = move_result.source_pile
to_pile = move_result.target_pile
```

**File Coinvolti**:
- `src/application/gameplay_controller.py` - MODIFIED: Add log calls

---

#### 1.2 Draw Cards Tracking

**Comportamento Atteso**:
1. User presses D or P → draw from stock
2. System logs: `Drew 3 card(s) from stock` (DEBUG level)
3. Stock empty → recycle triggered → logged in domain layer

**Helper Function Call**:
```python
log.cards_drawn(
    count=3  # 1 or 3 based on settings.deck_type
)
```

**Integration Points**:
- `_draw_cards()` - Line ~395

**Rationale DEBUG Level**:
- Draw action molto frequente (50+ volte per partita)
- INFO level creerebbe noise eccessivo
- DEBUG level permette analisi dettagliata quando necessario

---

#### 1.3 Game Lifecycle Tracking

**Comportamento Atteso**:
1. User presses N (new game)
2. System logs: `New game started - Deck: draw_three, Difficulty: medium, Timer: True`
3. User presses ESC (abandon)
4. System logs: `Game ABANDONED - Time: 180s, Moves: 45`

**Helper Function Calls**:
```python
# New game
log.game_started(
    deck_type="draw_three",  # or "draw_one"
    difficulty="medium",     # easy/medium/hard/expert/master
    timer_enabled=True
)

# Abandon game
log.game_abandoned(
    elapsed_time=180,        # Seconds from game start
    moves_count=45           # Total moves made
)
```

**Integration Points**:
- `_new_game()` - Line ~550
- `_esc_handler()` → abandon flow - Line ~660

**Context Extraction**:
```python
# Settings
deck_type = self.settings.deck_type  # "draw_one" or "draw_three"
difficulty = self.settings.difficulty
timer_enabled = self.settings.timer_enabled

# Game state
state = self.engine.get_game_state()
elapsed = state['elapsed_time']
moves = state['moves_count']
```

---

#### 1.4 Invalid Actions Tracking

**Comportamento Atteso**:
1. User attempts invalid move
2. GameEngine validates move → failure
3. System logs: `Invalid action 'move_cards': Cannot place red on red`
4. TTS speaks failure reason to user

**Helper Function Call**:
```python
log.invalid_action(
    action="move_cards",              # Action type
    reason="Cannot place red on red"  # Validation failure reason
)
```

**Integration Points**:
- `_move_cards()` when `success=False` - Line ~385
- `_select_card()` when selection fails - Line ~370

**Rationale**:
- Capire errori comuni utenti (UX improvement)
- Identificare validation logic bugs (se troppi FAILED per mosse valide)

---

### COMMIT 2: Domain Layer Integration

#### 2.1 Victory Detection Tracking

**Comportamento Atteso**:
1. User completes last foundation (all 4 suits K)
2. GameService detects victory
3. System logs: `Game WON - Time: 320s, Moves: 89, Score: 1250`
4. TTS announces victory + stats

**Helper Function Call**:
```python
log.game_won(
    elapsed_time=320,  # Total game duration (seconds)
    moves_count=89,    # Total moves to win
    score=1250         # Final score (if scoring implemented)
)
```

**Integration Point**:
- `src/domain/services/game_service.py` - `_check_victory()` method
- Called after every move to foundation

**Existing Code Pattern**:
```python
def _check_victory(self):
    if self._all_foundations_complete():
        self.is_game_won = True
        # ADD HERE: log.game_won(...)
        self._announce_victory()
```

**Context Extraction**:
```python
elapsed = self._get_elapsed_time()  # Timer service
moves = self.moves_counter          # GameState attribute
score = self._calculate_score()     # Scoring service (or 0 if disabled)
```

**File Coinvolti**:
- `src/domain/services/game_service.py` - MODIFIED: Add victory log
- `src/application/game_engine.py` - MAYBE: If victory check happens here

---

#### 2.2 Waste Recycle Tracking

**Comportamento Atteso**:
1. User draws from empty stock → recycle triggered
2. System moves waste back to stock
3. System logs: `Waste recycled (total recycles: 3)`
4. Analytics: Track recycle frequency (strategy complexity metric)

**Helper Function Call**:
```python
log.waste_recycled(
    recycle_count=3  # Cumulative recycles this game
)
```

**Integration Point**:
- `src/domain/services/game_service.py` - `recycle_waste()` method

**Existing Code Pattern**:
```python
def recycle_waste(self):
    self.recycle_count += 1
    # ADD HERE: log.waste_recycled(self.recycle_count)
    self._move_waste_to_stock()
```

**Analytics Use Case**:
- Win rate correlation con recycle count
- Difficulty metric (hard games = more recycles)
- Strategy detection (aggressive vs conservative play)

---

#### 2.3 Move Validation Failures

**Comportamento Atteso**:
1. GameService validates move before execution
2. Validation fails (wrong suit, wrong rank, etc.)
3. System logs: `Invalid action 'validate_move': Cannot place red on red`
4. Move rejected, no state change

**Helper Function Call**:
```python
log.invalid_action(
    action="validate_move",
    reason="Cannot place 7♥ on 6♦ - same color"  # Specific failure reason
)
```

**Integration Point**:
- `src/domain/services/solitaire_rules.py` - Validation methods
- Called before every move execution

**Existing Code Pattern**:
```python
def can_move_to_foundation(self, card, foundation):
    if not self._is_valid_foundation_move(card, foundation):
        reason = self._get_failure_reason(card, foundation)
        # ADD HERE: log.invalid_action("validate_move", reason)
        return False
    return True
```

**Rationale**:
- Capire validation logic bugs (se troppi failures per mosse teoricamente valide)
- UX improvement (quali errori più frequenti)

---

### COMMIT 3: Settings + Error Handling

#### 3.1 Settings Changes Tracking

**Comportamento Atteso**:
1. User opens options window (O key)
2. User changes difficulty: Medium → Hard
3. System logs: `Setting changed: difficulty = medium → hard`
4. User changes timer: OFF → ON
5. System logs: `Setting changed: timer_enabled = False → True`

**NEW Helper Function** (add to `game_logger.py`):
```python
def settings_changed(setting_name: str, old_value: Any, new_value: Any) -> None:
    """
    Log configuration change.
    
    Args:
        setting_name: Name of setting (e.g. "difficulty", "timer_enabled")
        old_value: Previous value
        new_value: New value
    
    Example:
        >>> settings_changed("difficulty", "medium", "hard")
        2026-02-14 15:00:00 - INFO - game - Setting changed: difficulty = medium → hard
    """
    _game_logger.info(
        f"Setting changed: {setting_name} = {old_value} → {new_value}"
    )
```

**Integration Points**:
- `src/application/options_controller.py` - All setting modification methods
- `src/domain/services/game_settings.py` - Setter methods

**Existing Code Pattern**:
```python
def set_difficulty(self, new_difficulty):
    old_val = self.difficulty
    self.difficulty = new_difficulty
    # ADD HERE: log.settings_changed("difficulty", old_val, new_difficulty)
```

**Settings da Tracciare**:
- `difficulty` (easy/medium/hard/expert/master)
- `deck_type` (draw_one/draw_three)
- `timer_enabled` (True/False)
- `max_time_game` (seconds)
- `command_hints_enabled` (True/False)
- `tts_rate` (speech speed)
- `tts_volume` (0-100)

**Analytics Use Case**:
- Most popular difficulty level
- Timer usage percentage
- A/B testing new features (command hints adoption rate)

---

#### 3.2 Exception Handling Sistemico

**Comportamento Atteso**:
1. Unexpected exception occurs (FileNotFoundError, AttributeError, etc.)
2. Try-except block catches exception
3. System logs full stacktrace: `ERROR [FileIO]: Config file not found: config.json`
4. Fallback logic executed (default config, graceful degradation)
5. Log persisted for post-mortem debugging

**Helper Function Call**:
```python
try:
    risky_operation()
except FileNotFoundError as e:
    log.error_occurred(
        error_type="FileIO",
        details=f"Config file not found: {e}",
        exception=e  # Include for full stacktrace
    )
    # Fallback logic
except Exception as e:
    log.error_occurred(
        error_type="Application",
        details=f"Unexpected error in {context}: {e}",
        exception=e
    )
    raise  # Re-raise if unhandled
```

**Integration Points (esempi)**:
- `test.py` - Main loop exception handler
- `src/infrastructure/ui/wx_dialog_provider.py` - Dialog creation failures
- `src/domain/services/game_service.py` - State corruption handling
- `src/infrastructure/tts/screen_reader.py` - TTS initialization failures

**Error Categories**:
- `FileIO`: Config load/save, log file creation
- `StateCorruption`: Invalid game state (should never happen)
- `Application`: Unhandled exceptions
- `UI`: wxPython dialog/panel creation failures
- `TTS`: Screen reader initialization/speech failures

**Rationale**:
- Crash reports automatici con stacktrace completo
- Identify regression bugs from user logs
- Monitor production error rates

---

#### 3.3 Timer Lifecycle Tracking

**Comportamento Atteso**:
1. User starts game with timer enabled
2. System logs: `Timer started - Duration: 600s`
3. Timer expires during game
4. System logs: `Timer EXPIRED - Game auto-abandoned`
5. User disables timer in options
6. System logs: `Setting changed: timer_enabled = True → False`

**NEW Helper Functions** (add to `game_logger.py`):
```python
def timer_started(duration: int) -> None:
    """Log timer start with max duration."""
    _game_logger.info(f"Timer started - Duration: {duration}s")

def timer_expired() -> None:
    """Log timer expiration (game over event)."""
    _game_logger.warning("Timer EXPIRED - Game auto-abandoned")

def timer_paused(remaining: int) -> None:
    """Log timer pause (if pause feature exists)."""
    _game_logger.debug(f"Timer paused - Remaining: {remaining}s")
```

**Integration Points**:
- `src/domain/services/timer_service.py` - Timer logic (if exists)
- `src/application/game_engine.py` - Timer check in main loop

**Analytics Use Case**:
- Timer expiration rate (too strict?)
- Average completion time vs timer limit
- Difficulty correlation (harder games timeout more)

---

### COMMIT 4: Granular Analytics Events

#### 4.1 Navigation Tracking (DEBUG Level)

**Comportamento Atteso**:
1. User presses Arrow UP → cursor moves to previous card
2. System logs (DEBUG): `Cursor moved: tableau_3[5] → tableau_3[4]`
3. User presses 3 → jump to tableau pile 3
4. System logs (DEBUG): `Pile jump: tableau_1 → tableau_3`

**NEW Helper Function** (add to `game_logger.py`):
```python
def cursor_moved(from_position: str, to_position: str) -> None:
    """
    Log cursor movement (DEBUG level - verbose).
    
    Args:
        from_position: Previous cursor position (e.g. "tableau_3[5]")
        to_position: New cursor position
    
    Note:
        DEBUG level to avoid noise in INFO logs.
        Useful for UX heatmap analytics (which piles/cards focused most).
    
    Example:
        >>> cursor_moved("tableau_3[5]", "tableau_3[4]")
        2026-02-14 15:05:00 - DEBUG - game - Cursor: tableau_3[5] → tableau_3[4]
    """
    _game_logger.debug(f"Cursor: {from_position} → {to_position}")

def pile_jumped(from_pile: str, to_pile: str) -> None:
    """
    Log direct pile jump (1-7 keys, SHIFT+1-4, etc.).
    
    Args:
        from_pile: Previous pile (e.g. "tableau_1")
        to_pile: Target pile (e.g. "foundation_2")
    
    Example:
        >>> pile_jumped("tableau_1", "foundation_2")
        2026-02-14 15:05:05 - DEBUG - game - Pile jump: tableau_1 → foundation_2
    """
    _game_logger.debug(f"Pile jump: {from_pile} → {to_pile}")
```

**Integration Points**:
- `_cursor_up/down/left/right()` - GameplayController lines ~410-450
- `_nav_pile_base()` / `_nav_pile_semi()` - Lines ~310-350

**Why DEBUG Level**:
- Arrow keys pressed 500+ times per game (too verbose for INFO)
- Enable solo quando serve analytics dettagliate (navigation heatmap)
- Log file size manageable (DEBUG disabilitato in production)

**Analytics Use Case**:
- UX heatmap: Quali pile/carte più navigate
- Navigation efficiency: Paths taken to complete moves
- Accessibility patterns: How blind users explore board

---

#### 4.2 Query Commands Tracking

**Comportamento Atteso**:
1. User presses G (get table info)
2. System vocalizes full table state
3. System logs (INFO): `Info query: table_info`
4. User presses F (focus position)
5. System logs (INFO): `Info query: cursor_position`

**NEW Helper Function** (add to `game_logger.py`):
```python
def info_query_requested(query_type: str, context: str = "") -> None:
    """
    Log information query command.
    
    Args:
        query_type: Type of info requested (e.g. "table_info", "cursor_position")
        context: Optional context (e.g. current pile)
    
    Note:
        INFO level - questi comandi sono meno frequenti delle navigation keys.
        Utile per capire quali info users cercano più spesso.
    
    Example:
        >>> info_query_requested("table_info", "during_gameplay")
        2026-02-14 15:10:00 - INFO - game - Info query: table_info (during_gameplay)
    """
    if context:
        _game_logger.info(f"Info query: {query_type} ({context})")
    else:
        _game_logger.info(f"Info query: {query_type}")
```

**Integration Points** (GameplayController):
- `_get_focus()` - F key - Line ~500
- `_get_table_info()` - G key - Line ~510
- `_get_game_report()` - R key - Line ~520
- `_get_card_info()` - X key - Line ~530
- `_get_selected_cards()` - C key - Line ~540
- `_get_scarto_top()` - S key - Line ~470
- `_get_deck_count()` - M key - Line ~480
- `_get_timer()` - T key - Line ~490
- `_get_settings()` - I key - Line ~560
- `_show_help()` - H key - Line ~570

**Query Types**:
- `cursor_position` (F key)
- `table_info` (G key)
- `game_report` (R key)
- `card_info` (X key)
- `selected_cards` (C key)
- `waste_top` (S key)
- `stock_count` (M key)
- `timer_status` (T key)
- `settings_info` (I key)
- `help` (H key)

**Analytics Use Case**:
- Most requested info types (improve TTS defaults)
- Help command frequency (user confusion indicator)
- Query timing (early game vs late game patterns)

---

#### 4.3 TTS Feedback Tracking (Optional)

**Comportamento Atteso**:
1. System vocalizes message via screen reader
2. System logs (DEBUG): `TTS spoken: "7 di cuori su 8 di picche" (interrupt=True)`
3. Analytics: Track TTS usage patterns

**NEW Helper Function** (add to `game_logger.py`):
```python
def tts_spoken(message: str, interrupt: bool) -> None:
    """
    Log TTS vocalization (DEBUG level).
    
    Args:
        message: Text vocalized
        interrupt: Whether previous speech interrupted
    
    Note:
        DEBUG level - molto verboso (ogni azione genera TTS).
        Utile per accessibility audits e TTS testing.
    
    Example:
        >>> tts_spoken("7 di cuori su 8 di picche", True)
        2026-02-14 15:15:00 - DEBUG - ui - TTS: "7 di cuori su 8 di picche" (interrupt=True)
    """
    _ui_logger.debug(f'TTS: "{message}" (interrupt={interrupt})')
```

**Integration Point**:
- `src/infrastructure/tts/screen_reader.py` - `speak()` method

**Existing Code Pattern**:
```python
def speak(self, message: str, interrupt: bool = True):
    # ADD HERE: log.tts_spoken(message, interrupt)
    self.tts_provider.speak(message, interrupt)
```

**Analytics Use Case**:
- TTS message length distribution (too verbose?)
- Interrupt frequency (UX irritation metric)
- Accessibility audit (ensure all actions vocalized)

**Rationale DEBUG Level**:
- TTS chiamato 100+ volte per game session
- INFO level creerebbe log giganteschi
- Enable solo per accessibility testing specifico

---

## 📝 Implementation Checklist

### ✅ COMMIT 1: GameplayController Integration
**Branch**: `copilot/implement-centralized-logging-system`  
**Files**: 1 modified  
**Lines**: ~50 new log calls  
**Test**: Manual gameplay session (20 moves)

- [ ] Import `game_logger as log` at top
- [ ] `_select_card()`: Log card selection (success/fail)
- [ ] `_select_from_waste()`: Log CTRL+ENTER selection
- [ ] `_move_cards()`: Log card moves with from/to piles
- [ ] `_cancel_selection()`: Log selection cancellation (optional)
- [ ] `_draw_cards()`: Log draw count (DEBUG level)
- [ ] `_new_game()`: Log game_started with settings
- [ ] `_esc_handler()` → abandon: Log game_abandoned with stats
- [ ] Invalid moves: Log invalid_action with reason
- [ ] Run game, verify logs contain card moves/draws/lifecycle

**Commit Message**:
```
feat(logging): integrate gameplay controller events

Add comprehensive logging for 60+ gameplay commands:
- Card selection and movement tracking
- Draw cards from stock (DEBUG level)
- Game lifecycle (new/abandon with stats)
- Invalid action attempts with failure reasons

Integration:
- Wrap existing GameplayController methods
- Extract context (pile names, cards, move results)
- Strategic log placement (after operations complete)

Impact:
- Coverage: +50% (user-facing gameplay events)
- Analytics: Win patterns, strategy detection
- Debug: User action sequences traceable

Files:
- MODIFIED: src/application/gameplay_controller.py

Testing:
- Manual gameplay (20 moves, draw, abandon)
- Verified log contains card_moved, cards_drawn, game_abandoned

Version: v2.3.0
```

---

### ✅ COMMIT 2: Domain Layer Integration
**Branch**: Same  
**Files**: 2-3 modified  
**Lines**: ~15 new log calls  
**Test**: Win game + recycle waste

- [ ] Import `game_logger as log` in domain files
- [ ] `GameService._check_victory()`: Log game_won with stats
- [ ] `GameService.recycle_waste()`: Log waste_recycled with count
- [ ] `SolitaireRules.validate_move()`: Log invalid_action on failures
- [ ] Extract context: elapsed time, moves counter, score
- [ ] Run game to victory, verify log contains game_won
- [ ] Recycle waste, verify log contains waste_recycled

**Commit Message**:
```
feat(logging): integrate domain layer events

Add logging for critical game state transitions:
- Victory detection with completion stats
- Waste recycle tracking (strategy complexity)
- Move validation failures with specific reasons

Integration:
- GameService._check_victory() logs game_won
- GameService.recycle_waste() logs waste_recycled
- SolitaireRules validation logs invalid_action

Impact:
- Coverage: +20% (domain events)
- Analytics: Win rate, recycle frequency, validation bugs
- Debug: State transition audit trail

Files:
- MODIFIED: src/domain/services/game_service.py
- MODIFIED: src/domain/services/solitaire_rules.py (optional)

Testing:
- Manual game to victory (verified game_won)
- Forced waste recycle (verified waste_recycled)

Version: v2.3.0
```

---

### ✅ COMMIT 3: Settings + Error Handling
**Branch**: Same  
**Files**: 3-5 modified + 1 helper function added  
**Lines**: ~30 new log calls + 10 lines helper  
**Test**: Change settings + trigger exception

- [ ] Add `settings_changed()` helper to `game_logger.py`
- [ ] Add `timer_started/expired()` helpers to `game_logger.py`
- [ ] `OptionsController`: Log settings_changed for all modifications
- [ ] `GameSettings` setters: Log changes (alternative integration point)
- [ ] Wrap try-except blocks: `test.py`, dialog providers, services
- [ ] Log error_occurred with full stacktrace
- [ ] Timer service: Log timer_started/expired
- [ ] Change difficulty in options, verify log contains settings_changed
- [ ] Trigger exception (invalid config), verify error_occurred with trace

**Commit Message**:
```
feat(logging): add settings tracking and error handling

Implement comprehensive configuration and reliability logging:
- Settings changes tracking (all options)
- Timer lifecycle events (start/expire)
- Exception handling with full stacktrace

New helpers:
- settings_changed(name, old, new)
- timer_started(duration)
- timer_expired()

Integration:
- OptionsController logs all setting modifications
- Try-except blocks wrapped with error_occurred()
- Timer service logs lifecycle events

Impact:
- Coverage: +15% (config + reliability)
- Analytics: User preferences, timer usage
- Debug: Crash reports with context

Files:
- MODIFIED: src/infrastructure/logging/game_logger.py (new helpers)
- MODIFIED: src/application/options_controller.py
- MODIFIED: src/domain/services/game_settings.py (optional)
- MODIFIED: test.py (exception handler)
- MODIFIED: various (try-except wrapping)

Testing:
- Changed difficulty → verified settings_changed
- Triggered exception → verified error_occurred with trace

Version: v2.3.0
```

---

### ✅ COMMIT 4: Granular Analytics Events
**Branch**: Same  
**Files**: 2 modified + 3 helper functions added  
**Lines**: ~40 new log calls + 20 lines helpers  
**Test**: Enable DEBUG level, analyze navigation patterns

- [ ] Add `cursor_moved()` / `pile_jumped()` helpers (DEBUG level)
- [ ] Add `info_query_requested()` helper (INFO level)
- [ ] Add `tts_spoken()` helper (DEBUG level, optional)
- [ ] `GameplayController._cursor_*()`: Log cursor movements
- [ ] `GameplayController._nav_pile_*()`: Log pile jumps
- [ ] All query methods (_get_*): Log info_query_requested
- [ ] `ScreenReader.speak()`: Log tts_spoken (optional)
- [ ] Enable DEBUG in test.py, play 10 moves
- [ ] Verify log contains cursor_moved, pile_jumped
- [ ] Press G/F/R keys, verify info_query_requested

**Commit Message**:
```
feat(logging): add granular analytics events (DEBUG level)

Implement detailed UX tracking for advanced analytics:
- Cursor movement tracking (arrow keys)
- Pile jump tracking (1-7, SHIFT+1-4)
- Info query command tracking (F/G/R/etc.)
- TTS vocalization tracking (optional)

New helpers:
- cursor_moved(from, to) - DEBUG
- pile_jumped(from, to) - DEBUG
- info_query_requested(type) - INFO
- tts_spoken(message) - DEBUG (optional)

Integration:
- GameplayController navigation methods
- GameplayController query commands
- ScreenReader.speak() wrapper (optional)

Impact:
- Coverage: +10% (granular UX events)
- Analytics: Navigation heatmap, query frequency
- Debug: User exploration patterns

Note:
- DEBUG level prevents log noise in production
- Enable selectively for UX research sessions

Files:
- MODIFIED: src/infrastructure/logging/game_logger.py (new helpers)
- MODIFIED: src/application/gameplay_controller.py
- MODIFIED: src/infrastructure/tts/screen_reader.py (optional)

Testing:
- Enabled DEBUG level in setup_logging()
- Played 10 moves with navigation
- Verified cursor_moved, pile_jumped in log
- Pressed query keys → verified info_query_requested

Version: v2.3.0
```

---

## 🧪 Testing Strategy Completa

### Unit Tests (Optional - Log Helpers Already Tested)

Log helpers già testati da Copilot in commit foundation. Testing aggiuntivo:

```python
# tests/unit/infrastructure/logging/test_game_logger_extended.py

class TestNewHelpers:
    @patch('src.infrastructure.logging.game_logger._game_logger')
    def test_settings_changed_logs_transition(self, mock_logger):
        log.settings_changed("difficulty", "medium", "hard")
        assert "difficulty" in mock_logger.info.call_args[0][0]
        assert "medium → hard" in mock_logger.info.call_args[0][0]
    
    @patch('src.infrastructure.logging.game_logger._game_logger')
    def test_cursor_moved_uses_debug_level(self, mock_logger):
        log.cursor_moved("tableau_3[5]", "tableau_3[4]")
        mock_logger.debug.assert_called_once()
```

**Verdict**: Unit tests opzionali (helpers triviali, already covered pattern)

---

### Integration Testing (Manual - CRITICAL)

#### Test Session 1: Gameplay Completo (30 min)

**Setup**:
```python
# In test.py
setup_logging(level=logging.DEBUG, console_output=True)
```

**Actions**:
1. Avvia gioco → Verifica log: `Application started`
2. Nuova partita (N key) → Verifica: `New game started - Deck: draw_three, Difficulty: medium, Timer: True`
3. Esegui 20 mosse:
   - ENTER (select) → Verifica: `Move SUCCESS: ... from ... to selected`
   - SPACE (move) → Verifica: `Move SUCCESS: ... from selected to ...`
   - Invalid move → Verifica: `Move FAILED: ...` + `Invalid action: ...`
4. Pesca carte (D key) 10 volte → Verifica: `Drew 3 card(s) from stock` (DEBUG)
5. Forza waste recycle → Verifica: `Waste recycled (total recycles: 1)`
6. Premi query keys (G/F/R/X) → Verifica: `Info query: ...`
7. Naviga con arrow keys → Verifica: `Cursor: ... → ...` (DEBUG, molti logs)
8. Jump pile (3 key) → Verifica: `Pile jump: ... → tableau_3` (DEBUG)
9. Vinci partita (o force victory CTRL+ALT+W) → Verifica: `Game WON - Time: ...s, Moves: ..., Score: ...`
10. ESC (abandon) → Verifica: `Game ABANDONED - Time: ...s, Moves: ...`
11. Chiudi app → Verifica: `Application shutdown requested`

**Expected Log Sample** (excerpt):
```
2026-02-14 15:00:00 - INFO - game - Application started - wxPython solitaire v2.3.0
2026-02-14 15:00:05 - INFO - ui - Panel transition: menu → gameplay
2026-02-14 15:00:10 - INFO - game - New game started - Deck: draw_three, Difficulty: medium, Timer: True
2026-02-14 15:00:15 - DEBUG - game - Cursor: tableau_1[0] → tableau_1[1]
2026-02-14 15:00:18 - INFO - game - Move SUCCESS: 7♥ from tableau_3 to selected
2026-02-14 15:00:20 - INFO - game - Move SUCCESS: 7♥ from selected to foundation_1
2026-02-14 15:00:25 - DEBUG - game - Drew 3 card(s) from stock
2026-02-14 15:00:30 - INFO - game - Info query: table_info
2026-02-14 15:05:00 - INFO - game - Waste recycled (total recycles: 2)
2026-02-14 15:10:00 - INFO - game - Game WON - Time: 600s, Moves: 120, Score: 1500
2026-02-14 15:10:05 - INFO - ui - Panel transition: gameplay → menu
2026-02-14 15:10:10 - INFO - game - Application shutdown requested
```

**Pass Criteria**:
- ✅ Almeno 1 log per ogni categoria evento (lifecycle, move, draw, query, navigation)
- ✅ Log contengono context ricco (pile names, card details, stats)
- ✅ DEBUG logs presenti solo se level=DEBUG
- ✅ File size < 5MB dopo session (rotation non triggered)

---

#### Test Session 2: Settings Changes (10 min)

**Actions**:
1. Apri options (O key)
2. Cambia difficulty: Medium → Hard → Verifica: `Setting changed: difficulty = medium → hard`
3. Toggle timer: OFF → ON → Verifica: `Setting changed: timer_enabled = False → True`
4. Modifica max_time: 600 → 300 → Verifica: `Setting changed: max_time_game = 600 → 300`
5. Save and close
6. Verifica settings salvati + log file aggiornato

**Expected Log**:
```
2026-02-14 15:15:00 - INFO - ui - Panel transition: menu → options
2026-02-14 15:15:10 - INFO - game - Setting changed: difficulty = medium → hard
2026-02-14 15:15:15 - INFO - game - Setting changed: timer_enabled = False → True
2026-02-14 15:15:20 - INFO - game - Setting changed: max_time_game = 600 → 300
2026-02-14 15:15:25 - INFO - ui - Panel transition: options → menu
```

---

#### Test Session 3: Error Handling (5 min)

**Actions**:
1. Rename `config.json` → `config.json.bak` (simulate missing file)
2. Avvia gioco → Trigger FileNotFoundError
3. Verifica log: `ERROR [FileIO]: Config file not found: ...` + full stacktrace
4. Ripristina config, riavvia
5. Force exception in dialog (modify code temporarily)
6. Verifica log: `ERROR [Application]: Unexpected error ...` + trace

**Expected Log**:
```
2026-02-14 15:20:00 - ERROR - error - ERROR [FileIO]: Config file not found: config.json
Traceback (most recent call last):
  File "test.py", line 45, in main
    config = load_config()
  File "config_loader.py", line 12, in load_config
    with open('config.json') as f:
FileNotFoundError: [Errno 2] No such file or directory: 'config.json'
```

---

### Performance Testing

**Obiettivo**: Verificare overhead logging < 1ms per call

**Test**:
```python
import timeit

# Test log call performance
setup = """
from src.infrastructure.logging import game_logger as log
import logging
logging.basicConfig(level=logging.INFO, handlers=[logging.NullHandler()])
"""

stmt = 'log.card_moved("tableau_3", "foundation_1", "7♥", True)'

time = timeit.timeit(stmt, setup=setup, number=1000)
print(f"Average time per log call: {time/1000*1000:.3f}ms")
```

**Expected**: < 0.1ms per call (acceptable overhead)

**If > 1ms**: Investigate (potenziale I/O blocking, disabled buffering)

---

### Log File Validation

**Checklist Post-Session**:
- [ ] File `logs/solitario.log` esiste
- [ ] File size ragionevole (< 5MB per session 30 min)
- [ ] Formato corretto: `YYYY-MM-DD HH:MM:SS - LEVEL - logger - message`
- [ ] Timestamp sequenziali (no gaps temporali sospetti)
- [ ] UTF-8 encoding (no caratteri corrotti per simboli carte ♠♥♦♣)
- [ ] Rotation NON triggered (file < 5MB threshold)

**Test Rotation** (opzionale):
```python
# Script spam per testare rotation
for i in range(100000):
    log.debug_state("test", {"iteration": i, "data": "x" * 200})

# Verifica:
ls -lh logs/
# Expected:
# solitario.log      (5.0M)
# solitario.log.1    (5.0M)
# solitario.log.2    (5.0M)
# ...
```

---

## 📊 Analytics Use Cases Post-Implementation

### Use Case 1: Win Rate Analysis

**Query** (Python script su log file):
```python
import re

wins = len(re.findall(r'Game WON', log_content))
abandons = len(re.findall(r'Game ABANDONED', log_content))
total = wins + abandons

win_rate = wins / total * 100 if total > 0 else 0
print(f"Win rate: {win_rate:.1f}% ({wins}/{total})")
```

**Insight**: Se win_rate < 10% → difficulty troppo alta, frustra utenti

---

### Use Case 2: Strategy Patterns

**Query**:
```python
recycles = re.findall(r'Waste recycled \(total recycles: (\d+)\)', log_content)
avg_recycles = sum(map(int, recycles)) / len(recycles) if recycles else 0

print(f"Average recycles per game: {avg_recycles:.1f}")
```

**Insight**: High recycles → aggressive draw strategy (or difficult game)

---

### Use Case 3: Command Frequency

**Query**:
```python
commands = re.findall(r'Info query: (\w+)', log_content)
from collections import Counter

top_queries = Counter(commands).most_common(5)
print("Most used info commands:")
for cmd, count in top_queries:
    print(f"  {cmd}: {count}")
```

**Insight**: Se `help` in top 3 → users confused, improve UX/docs

---

### Use Case 4: Error Frequency

**Query**:
```python
errors = re.findall(r'ERROR \[(\w+)\]:', log_content)
error_types = Counter(errors)

print("Error distribution:")
for err_type, count in error_types.items():
    print(f"  {err_type}: {count}")
```

**Insight**: High `StateCorruption` errors → critical bug in game logic

---

### Use Case 5: Settings Preferences

**Query**:
```python
difficulties = re.findall(r'difficulty = \w+ → (\w+)', log_content)
from collections import Counter

preferences = Counter(difficulties)
print("Difficulty distribution:")
for diff, count in preferences.items():
    print(f"  {diff}: {count}")
```

**Insight**: Se 80% users play "easy" → add tutorial mode

---

## 🎯 Coverage Matrix Finale

| Categoria Eventi | Pre-Copilot | Post-Copilot | Post-4-Commits | Gap Residuo |
|-----------------|-------------|--------------|----------------|-------------|
| App Lifecycle | ❌ 0% | ✅ 100% | ✅ 100% | - |
| UI Navigation | ❌ 0% | ✅ 50% (panels) | ✅ 95% (panels+cursor) | 5% (undo/redo) |
| Dialog Events | ❌ 0% | ✅ 100% | ✅ 100% | - |
| Card Moves | ❌ 0% | ❌ 0% | ✅ 100% | - |
| Draw/Recycle | ❌ 0% | ❌ 0% | ✅ 100% | - |
| Game Lifecycle | ❌ 0% | ❌ 0% | ✅ 100% | - |
| Victory/Stats | ❌ 0% | ❌ 0% | ✅ 100% | - |
| Settings Changes | ❌ 0% | ❌ 0% | ✅ 100% | - |
| Error Handling | ❌ 0% | ❌ 0% | ✅ 90% | 10% (edge cases) |
| Info Queries | ❌ 0% | ❌ 0% | ✅ 100% | - |
| Timer Events | ❌ 0% | ❌ 0% | ✅ 80% | 20% (pause/resume) |
| TTS Tracking | ❌ 0% | ❌ 0% | ✅ 90% (optional) | 10% (NVDA specifics) |
| **TOTAL** | **5%** | **15%** | **95%** | **5%** |

**Gap Residuo 5%**:
- Undo/Redo events (se feature implementata)
- Timer pause/resume (se feature implementata)
- NVDA-specific TTS events (accessibility deep dive)
- Network events (future multiplayer/cloud save)

---

## 🚀 Deployment Strategy

### Pre-Merge Checklist

- [ ] Tutti i 4 commit completati sequenzialmente
- [ ] Manual testing session completata (30 min gameplay)
- [ ] Log file validato (formato, size, content)
- [ ] Performance test passed (< 0.1ms overhead)
- [ ] No breaking changes (domain layer invariato)
- [ ] Coverage >= 95% (verificato con log analysis)
- [ ] Documentation updated (questo file in docs/)

### Merge Strategy

```bash
# Current branch
git checkout copilot/implement-centralized-logging-system

# Verify all 4 commits present
git log --oneline | head -n 10
# Should show:
# - feat(logging): add granular analytics events
# - feat(logging): add settings tracking and error handling
# - feat(logging): integrate domain layer events
# - feat(logging): integrate gameplay controller events
# - docs(changelog): add v2.3.0 logging system release notes
# - feat(app): integrate logging in controllers and entry point
# - feat(infra): add semantic logging helper functions
# - feat(infra): add centralized logging foundation layer

# Rebase on latest refactoring-engine
git fetch origin refactoring-engine
git rebase origin/refactoring-engine

# Resolve conflicts (if any)
# ... manual resolution ...

# Push updated branch
git push origin copilot/implement-centralized-logging-system --force-with-lease

# Create PR
gh pr create \
  --base refactoring-engine \
  --title "feat: Complete logging system with 95% coverage" \
  --body "See docs/PLAN_LOGGING_COMPLETE_COVERAGE.md"

# Merge after review
gh pr merge --squash  # Or --rebase to preserve atomic commits
```

---

## 📝 Prompt per Copilot (Next 4 Commits)

```markdown
# Task: Complete Logging System Coverage (4 Commits)

## Context
Logging infrastructure already implemented. Need to integrate with gameplay/domain/settings.

## Reference Document
`docs/PLAN_LOGGING_COMPLETE_COVERAGE.md` - Follow implementation checklist EXACTLY.

## Instructions

Implement 4 sequential commits as specified in checklist:

### COMMIT 1: GameplayController Integration
- Import `game_logger as log` in `src/application/gameplay_controller.py`
- Add log calls to: `_select_card()`, `_move_cards()`, `_draw_cards()`, `_new_game()`, `_esc_handler()`
- Extract context: pile names, card details, move results from engine state
- Log levels: INFO for moves/lifecycle, DEBUG for draws
- Use exact commit message from checklist

### COMMIT 2: Domain Layer Integration
- Import `game_logger as log` in `src/domain/services/game_service.py`
- Add log calls to: `_check_victory()`, `recycle_waste()`, validation methods
- Extract: elapsed time, moves counter, score from service state
- Use exact commit message from checklist

### COMMIT 3: Settings + Error Handling
- Add new helpers to `game_logger.py`: `settings_changed()`, `timer_started()`, `timer_expired()`
- Integrate in `src/application/options_controller.py`: log all setting changes
- Wrap try-except blocks in `test.py` and other files with `error_occurred()`
- Use exact commit message from checklist

### COMMIT 4: Granular Analytics
- Add new helpers: `cursor_moved()`, `pile_jumped()`, `info_query_requested()`, `tts_spoken()`
- Integrate in `GameplayController` navigation methods (DEBUG level)
- Integrate in query methods (_get_*): log info queries (INFO level)
- Optional: Integrate in `ScreenReader.speak()`
- Use exact commit message from checklist

## Critical Rules
- Follow checklist exactly (filenames, function names, log levels)
- Use helpers from `game_logger.py`, don't invent new ones
- Extract context from existing code (don't add new state)
- Test each commit before moving to next
- Use conventional commit messages from checklist

## Testing
After each commit:
1. Run `python test.py`
2. Play 10-20 moves
3. Check `logs/solitario.log` contains expected events
4. Verify no exceptions/crashes

## Final Validation
After all 4 commits:
- Play complete game (new → win/abandon)
- Verify log contains: game_started, card_moved (10+), game_won/abandoned
- Change settings → verify settings_changed
- Press query keys → verify info_query_requested
```

---

## 🎉 Success Metrics

**Quantitative**:
- ✅ Coverage >= 95% eventi sistema
- ✅ Log file size < 5MB per session 30 min (INFO level)
- ✅ Performance overhead < 0.1ms per log call
- ✅ Zero exceptions durante logging operations
- ✅ 4 commit atomici con messages convenzionali

**Qualitative**:
- ✅ Debug facilitato (sequence azioni utente chiara)
- ✅ Analytics abilitati (win rate, strategy patterns, preferences)
- ✅ Crash reports completi (stacktrace + context)
- ✅ UX insights (query frequency, navigation heatmap)
- ✅ Zero breaking changes (domain layer invariato)

**Post-Implementation**:
- Script Python per analytics automatiche (win rate, command frequency, error distribution)
- Dashboard Grafana/Kibana per log visualization (future v2.4+)
- A/B testing framework basato su settings tracking (future v3.0+)

---

**Fine Piano Implementazione Coverage Completa**

**Piano Version**: v1.0  
**Data Creazione**: 2026-02-14  
**Autore**: AI Assistant + Nemex81  
**Basato su**: Analisi gap post-Copilot implementation  
**Branch Target**: copilot/implement-centralized-logging-system  
**Versione Software**: v2.3.0  
**Dependencies**: Requires logging foundation (already implemented by Copilot)  

---
