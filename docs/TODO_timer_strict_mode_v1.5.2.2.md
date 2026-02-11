# 🚀 TODO: Timer Strict Mode Implementation (v1.5.2.2)

**Branch**: `copilot/implement-scoring-system-v2`  
**Priority**: HIGH (Bug Fix + UX Enhancement)  
**Estimated Time**: 40-50 minutes  
**Status**: 📋 READY FOR IMPLEMENTATION

---

## 📊 OVERVIEW

### **Problem Statement**
Currently, when timer expires during gameplay:
- ❌ Game continues without interruption (BUG #3)
- ❌ No timeout detection in game loop
- ❌ No user feedback about time expiration
- ❌ Final statistics don't reflect timeout status

### **Solution Design**
Implement **configurable timer expiration behavior** with two modes:

1. **STRICT Mode** (default, legacy compatible):
   - Game stops automatically at timeout
   - Shows final statistics
   - Returns to game menu
   - No scoring penalty (game over)

2. **PERMISSIVE Mode** (new feature):
   - Game continues beyond time limit
   - TTS announces timeout + malus
   - Scoring penalty: **-100 points per overtime minute**
   - Ideal for casual play / learning

### **Architecture Impact**
```
Domain Layer:
  └─ GameSettings: +timer_strict_mode field

Application Layer:
  ├─ OptionsController: +Option #8 (toggle strict mode)
  └─ GameEngine: Uses settings.timer_strict_mode

Infrastructure Layer:
  └─ test.py: +Periodic timer check (pygame event)

Domain Services:
  └─ ScoringService: +Overtime malus calculation
```

---

## 📁 FILES TO MODIFY

### File 1: `src/domain/services/game_settings.py`
### File 2: `src/application/options_controller.py`
### File 3: `test.py`
### File 4: `src/domain/services/scoring_service.py`

---

## 🔧 IMPLEMENTATION STEPS

---

## ✅ STEP 1: Add Timer Strict Mode Setting (5 min)

**File**: `src/domain/services/game_settings.py`

### **Task 1.1: Add New Field**

**Location**: In `GameSettings.__init__()` method, after existing timer fields

**Add this code**:

```python
# Timer expiration behavior (v1.5.2.2)
self.timer_strict_mode: bool = True  # Default: auto-stop at timeout (legacy)
#   True  = STRICT: Partita interrotta alla scadenza (comportamento legacy)
#   False = PERMISSIVE: Continua con malus punti (-100/min oltre limite)
```

**Context**: Add after line with `self.max_time_game` and before `self.shuffle_mode_active`

**Expected Result**:
```python
class GameSettings:
    def __init__(self):
        # ... existing fields ...
        self.timer_enabled: bool = False
        self.max_time_game: int = 0  # In seconds
        
        # 🆕 NEW v1.5.2.2
        self.timer_strict_mode: bool = True
        
        self.shuffle_mode_active: bool = False
        # ... rest of fields ...
```

### **Task 1.2: Update Docstring**

**Location**: Class docstring at top of `GameSettings`

**Add to Attributes section**:

```python
"""Game configuration and state management.

Attributes:
    # ... existing attributes ...
    timer_enabled (bool): Whether timer countdown is active
    max_time_game (int): Maximum game time in seconds (0 = disabled)
    timer_strict_mode (bool): Timer expiration behavior (v1.5.2.2)
        - True: STRICT mode (auto-stop at timeout, legacy behavior)
        - False: PERMISSIVE mode (continue with -100pts/min malus)
    # ... rest of attributes ...
"""
```

### **Verification**:
- [ ] Field added with correct type hint
- [ ] Default value is `True` (backward compatible)
- [ ] Inline comment explains both modes
- [ ] Docstring updated

---

## ✅ STEP 2: Add Option #8 in Virtual Options Window (15 min)

**File**: `src/application/options_controller.py`

### **Task 2.1: Add Option to List**

**Location**: `_build_options_list()` method, add as **Option #8**

**Modify return statement**:

```python
def _build_options_list(self) -> List[str]:
    """Build list of option strings for display.
    
    Returns:
        List of formatted option strings (1-8)
    """
    # Timer status for display
    if self.settings.timer_enabled:
        timer_minutes = self.settings.max_time_game // 60
        timer_status = f"ON ({timer_minutes} minuti)"
    else:
        timer_status = "OFF"
    
    # 🆕 Timer mode status (v1.5.2.2)
    timer_mode_status = "STRICT (auto-stop)" if self.settings.timer_strict_mode else "PERMISSIVE (malus)"
    
    return [
        f"1. Tipo di mazzo: {self.settings.deck_type.upper()}",
        f"2. Livello di difficoltà: {self.settings.difficulty_level}",
        f"3. Timer di gioco: {timer_status}",
        f"4. Modalità riciclo scarti: {'MESCOLATA' if self.settings.shuffle_mode_active else 'INVERSIONE'}",
        f"5. Sistema punti: {'ON' if self.settings.scoring_enabled else 'OFF'}",
        f"6. Command Hints (accessibilità): {'ON' if self.settings.command_hints_enabled else 'OFF'}",
        f"7. Moltiplicatore livello: {'ON' if self.settings.difficulty_multiplier_enabled else 'OFF'}",
        f"8. Modalità timer: {timer_mode_status}",  # 🆕 NEW OPTION
    ]
```

### **Task 2.2: Add Toggle Method**

**Location**: Add new method after `_toggle_difficulty_multiplier()`

**Add this method**:

```python
def _toggle_timer_strict_mode(self) -> str:
    """Toggle timer strict mode (v1.5.2.2).
    
    STRICT mode (True):
        - Game stops automatically when timer expires
        - Shows final statistics and returns to menu
        - No scoring penalty (game over by timeout)
        - Legacy behavior from scr/ version
    
    PERMISSIVE mode (False):
        - Game continues beyond time limit
        - TTS announces timeout and malus
        - Scoring penalty: -100 points per overtime minute
        - Allows completing game after timeout
    
    Returns:
        TTS-friendly announcement of new mode
    
    Note:
        - Only affects behavior when timer_enabled = True
        - Default is STRICT (backward compatible)
        - PERMISSIVE mode designed for learning/casual play
    """
    self.settings.timer_strict_mode = not self.settings.timer_strict_mode
    self._mark_dirty()
    
    mode = "STRICT (auto-stop)" if self.settings.timer_strict_mode else "PERMISSIVE (malus)"
    explanation = (
        "Il gioco si interrompe alla scadenza del timer." 
        if self.settings.timer_strict_mode 
        else "Il gioco continua oltre il limite con penalità di 100 punti al minuto."
    )
    
    return f"Modalità timer: {mode}. {explanation} Opzione 8 di 8."
```

### **Task 2.3: Wire Method to Modify Handler**

**Location**: `modify_current_option()` method, add new case

**Add after case `elif self.cursor_position == 6:`**:

```python
def modify_current_option(self) -> str:
    """Modify currently selected option.
    
    Returns:
        TTS-friendly confirmation message
    """
    # ... existing cases 0-6 ...
    
    elif self.cursor_position == 6:  # Option #7
        return self._toggle_difficulty_multiplier()
    
    # 🆕 NEW CASE (v1.5.2.2)
    elif self.cursor_position == 7:  # Option #8
        return self._toggle_timer_strict_mode()
    
    return "Opzione non riconosciuta."
```

### **Task 2.4: Update Jump Method Validation**

**Location**: `jump_to_option()` method

**Update max index validation**:

```python
def jump_to_option(self, index: int) -> str:
    """Jump directly to option by index.
    
    Args:
        index: Option index (0-7)  # 🆕 CHANGED from (0-6)
    
    Returns:
        Announcement of selected option
    """
    if index < 0 or index >= 8:  # 🆕 CHANGED from >= 7
        return "Opzione non valida."
    
    self.cursor_position = index
    return self.options[index]
```

### **Task 2.5: Update Help Text**

**Location**: `show_help()` method

**Update help text**:

```python
def show_help(self) -> str:
    """Show options window help text.
    
    Returns:
        Complete help text for TTS
    """
    help_text = """AIUTO FINESTRA OPZIONI:

NAVIGAZIONE:
- Frecce SU/GIÙ: cambia opzione (con wrap-around)
- Numeri 1-8: salta direttamente all'opzione  # 🆕 CHANGED from 1-7
- TAB: cicla tra le opzioni

MODIFICA:
- INVIO o SPAZIO: modifica opzione corrente
- Per timer: usa + e - per regolare minuti, T per ON/OFF

INFORMAZIONI:
- I: leggi tutte le impostazioni correnti
- H: mostra questo aiuto

CHIUSURA:
- O o ESC: chiudi finestra
  (conferma salvataggio se modifiche presenti)

OPZIONI DISPONIBILI (8 totali):  # 🆕 CHANGED from (7 totali)
1. Tipo mazzo (francesi/napoletane)
2. Difficoltà (1-3)
3. Timer (ON/OFF con minuti)
4. Riciclo scarti (inversione/mescolata)
5. Sistema punti (ON/OFF)
6. Command hints accessibilità (ON/OFF)
7. Moltiplicatore difficoltà (ON/OFF)
8. Modalità timer (STRICT/PERMISSIVE)  # 🆕 NEW LINE

Modifiche salvate premendo S alla chiusura."""
    
    return help_text
```

### **Verification**:
- [ ] Option #8 appears in list with correct formatting
- [ ] Toggle method implemented with full docstring
- [ ] Method wired to `modify_current_option()` case 7
- [ ] Jump validation updated to 0-7 range
- [ ] Help text updated with new option
- [ ] Dirty flag set on modification

---

## ✅ STEP 3: Implement Periodic Timer Check (20 min)

**File**: `test.py`

### **Task 3.1: Add Timer Event Constant**

**Location**: Inside `SolitarioCleanArch` class, after class definition line

**Add this constant**:

```python
class SolitarioCleanArch:
    """Main application class - Audiogame for blind users.
    
    # ... existing docstring ...
    """
    
    # 🆕 NEW v1.5.2.2: Custom pygame event for timer checks
    TIME_CHECK_EVENT = pygame.USEREVENT + 1  # Fires every 1 second
```

### **Task 3.2: Initialize Timer Check Event**

**Location**: `__init__()` method, after `self.is_running = True` line

**Add this code**:

```python
def __init__(self):
    # ... existing initialization ...
    
    # Application state
    self.is_menu_open = True
    self.is_options_mode = False
    self.is_running = True
    
    # 🆕 NEW v1.5.2.2: Setup periodic timer check
    pygame.time.set_timer(self.TIME_CHECK_EVENT, 1000)  # 1000ms = 1 second
    self._timer_expired_announced = False  # Prevents repeated announcements
    
    print("="*60)
    # ... rest of init ...
```

### **Task 3.3: Route Timer Event in Event Loop**

**Location**: `handle_events()` method, add AFTER `QUIT` check and BEFORE dialog checks

**Add this code**:

```python
def handle_events(self) -> None:
    """Main event loop - process all pygame events.
    
    # ... existing docstring ...
    """
    for event in pygame.event.get():
        # Window close event
        if event.type == QUIT:
            self.quit_app()
            return
        
        # 🆕 PRIORITY 0: Timer check event (v1.5.2.2)
        # Fires every 1 second during gameplay to check timeout
        if event.type == self.TIME_CHECK_EVENT:
            self._check_timer_expiration()
            continue  # Don't pass to other handlers
        
        # PRIORITY 1: Exit dialog open
        if self.exit_dialog and self.exit_dialog.is_open:
            # ... existing code ...
```

### **Task 3.4: Implement Timer Check Method**

**Location**: Add new method after `_cancel_new_game()` and before `_start_new_game()`

**Add this complete method**:

```python
def _check_timer_expiration(self) -> None:
    """Check timer expiration every second (v1.5.2.2).
    
    Triggered by TIME_CHECK_EVENT (pygame.USEREVENT+1) every 1000ms.
    
    Behavior based on settings.timer_strict_mode:
    
    STRICT Mode (True):
        - Game stops immediately when timer expires
        - Saves final statistics (elapsed time, moves, etc)
        - Shows complete game report via TTS
        - Returns to game menu
        - Legacy behavior from scr/game_engine.py
    
    PERMISSIVE Mode (False):
        - Game continues beyond time limit
        - Announces timeout + malus ONCE via TTS
        - Scoring penalty applied: -100 points per overtime minute
        - Allows player to complete game
        - New feature for casual/learning mode
    
    Skip Conditions:
        - Not in gameplay (menu or options open)
        - Timer disabled (settings.timer_enabled = False)
        - Max time = 0 (stopwatch mode)
        - Game already over (victory or defeat)
    
    State Management:
        - self._timer_expired_announced: Prevents repeated TTS in PERMISSIVE mode
        - Reset to False when: timer OK, new game starts, return to menu
    """
    # Skip if not in gameplay mode
    if self.is_menu_open or self.is_options_mode:
        return
    
    # Skip if timer disabled or in stopwatch mode
    if not self.settings.timer_enabled or self.settings.max_time_game <= 0:
        return
    
    # Skip if game already concluded
    state = self.engine.get_game_state()
    game_over = state.get('game_over', {}).get('is_over', False)
    if game_over:
        return
    
    # Get current elapsed time
    elapsed = self.engine.service.get_elapsed_time()
    max_time = self.settings.max_time_game
    
    # Timer still OK - reset announcement flag
    if elapsed < max_time:
        self._timer_expired_announced = False
        return
    
    # ⏰ TIMER EXPIRED - Decide action based on mode
    
    if self.settings.timer_strict_mode:
        # === STRICT MODE: Auto-stop game ===
        self._handle_game_over_by_timeout()
    
    else:
        # === PERMISSIVE MODE: Announce malus once, continue playing ===
        if not self._timer_expired_announced:
            overtime_seconds = int(elapsed - max_time)
            overtime_minutes = max(1, overtime_seconds // 60)  # At least 1 min
            
            # Calculate penalty
            penalty_points = 100 * overtime_minutes
            
            # Build announcement
            max_minutes = max_time // 60
            malus_msg = f"Attenzione! Tempo scaduto! "
            malus_msg += f"Hai superato il limite di {max_minutes} minuti. "
            malus_msg += f"Stai giocando in tempo extra. "
            malus_msg += f"Penalità applicata: meno {penalty_points} punti. "
            malus_msg += f"Tempo oltre il limite: {overtime_minutes} minuti."
            
            # Vocalize warning
            if self.screen_reader:
                self.screen_reader.tts.speak(malus_msg, interrupt=True)
                pygame.time.wait(800)  # Longer pause for important warning
            
            # Console log
            print(f"\n[TIMER PERMISSIVE] Overtime: +{overtime_minutes}min → Malus: -{penalty_points}pts")
            
            # Mark as announced (don't repeat)
            self._timer_expired_announced = True
```

### **Task 3.5: Implement Game Over by Timeout Handler**

**Location**: Add new method after `_check_timer_expiration()`

**Add this complete method**:

```python
def _handle_game_over_by_timeout(self) -> None:
    """Handle game over by timeout in STRICT mode (v1.5.2.2).
    
    Called when timer expires and settings.timer_strict_mode = True.
    
    Actions:
    1. Stop timer event checks (set announcement flag)
    2. Retrieve final game statistics from engine
    3. Build comprehensive defeat message with:
       - Time limit exceeded message
       - Elapsed time vs max time comparison
       - Complete game report (moves, cards placed, etc)
    4. Vocalize defeat message via TTS (2 second pause)
    5. Return to game submenu (not main menu!)
    6. Reset timer flags for next game
    
    User Flow After Timeout:
        Game → [Timer expires] → This method → Game Submenu
        User can then:
        - Start new game (N key or menu option 1)
        - Change options (O key or menu option 2)
        - Return to main menu (ESC or menu option 3)
    
    Note:
        This replicates legacy behavior from scr/game_engine.py:
        - you_lost_by_time() method
        - ceck_lost_by_time() detection
        But with improved TTS feedback and Clean Architecture structure.
    """
    print("\n" + "="*60)
    print("⏰ GAME OVER - TEMPO SCADUTO (STRICT MODE)")
    print("="*60)
    
    # Stop timer announcements
    self._timer_expired_announced = True
    
    # Get final statistics
    elapsed = int(self.engine.service.get_elapsed_time())
    max_time = self.settings.max_time_game
    
    # Calculate time values for display
    minutes_elapsed = elapsed // 60
    seconds_elapsed = elapsed % 60
    max_minutes = max_time // 60
    max_seconds = max_time % 60
    
    # Build defeat message header
    defeat_msg = "⏰ TEMPO SCADUTO! PARTITA TERMINATA.\n\n"
    defeat_msg += f"Limite impostato: {max_minutes} minuti"
    if max_seconds > 0:
        defeat_msg += f" e {max_seconds} secondi"
    defeat_msg += ".\n"
    
    defeat_msg += f"Tempo trascorso: {minutes_elapsed} minuti"
    if seconds_elapsed > 0:
        defeat_msg += f" e {seconds_elapsed} secondi"
    defeat_msg += ".\n\n"
    
    # Add complete game report
    report, _ = self.engine.service.get_game_report()
    defeat_msg += "--- STATISTICHE FINALI ---\n"
    defeat_msg += report
    
    # Console output
    print(defeat_msg)
    print("="*60)
    
    # Vocalize with longer pause for readability
    if self.screen_reader:
        self.screen_reader.tts.speak(defeat_msg, interrupt=True)
        pygame.time.wait(2000)  # 2 second pause for long message
    
    # Return to game submenu (not main menu!)
    self.is_menu_open = True
    self._timer_expired_announced = False  # Reset for next game
    
    # Re-announce game submenu
    if self.screen_reader:
        pygame.time.wait(500)  # Small pause before menu
        self.game_submenu.announce_welcome()
```

### **Task 3.6: Reset Timer Flag on Game Start**

**Location**: `start_game()` method, after `self.last_esc_time = 0`

**Add this line**:

```python
def start_game(self) -> None:
    """Start new game session."""
    # ... existing code ...
    
    # Reset e avvia nuova partita
    self.engine.reset_game()
    self.engine.new_game()
    
    # Reset ESC timer
    self.last_esc_time = 0
    
    # 🆕 Reset timer expiration flag (v1.5.2.2)
    self._timer_expired_announced = False
    
    # ... rest of method ...
```

### **Verification**:
- [ ] `TIME_CHECK_EVENT` constant defined
- [ ] Timer event initialized in `__init__()`
- [ ] Event routed in `handle_events()` with PRIORITY 0
- [ ] `_check_timer_expiration()` implemented with full logic
- [ ] `_handle_game_over_by_timeout()` implemented with TTS
- [ ] Timer flag reset in `start_game()`
- [ ] Console logs added for debugging

---

## ✅ STEP 4: Implement Scoring Malus for Overtime (10 min)

**File**: `src/domain/services/scoring_service.py`

### **Task 4.1: Add Parameter to calculate_final_score()**

**Location**: `calculate_final_score()` method signature

**Update signature**:

```python
def calculate_final_score(
    self,
    is_victory: bool,
    elapsed_seconds: float,
    max_time_seconds: int = 0,
    timer_strict_mode: bool = True  # 🆕 NEW PARAMETER v1.5.2.2
) -> FinalScore:
    """Calculate final score with victory/time bonuses and overtime malus.
    
    Args:
        is_victory: Whether player won the game
        elapsed_seconds: Actual time taken to complete game
        max_time_seconds: Maximum time allowed (0 = no limit)
        timer_strict_mode: Timer expiration behavior (v1.5.2.2)
            - True: STRICT mode (game stops at timeout, no overtime possible)
            - False: PERMISSIVE mode (overtime allowed with penalty)
    
    Returns:
        FinalScore with complete breakdown including overtime malus
    
    Time Bonus Logic:
        Timer ON (max_time_seconds > 0):
            Finished within limit:
                → Bonus = (remaining_time / max_time) * 1000
                → Example: 10min limit, finished in 8min = +200 pts
            
            Finished in overtime (PERMISSIVE mode only):
                → Malus = -100 points per overtime minute
                → Example: 10min limit, finished in 12min = -200 pts
            
            Timeout in STRICT mode:
                → Not applicable (game stops, this method not called)
        
        Timer OFF (max_time_seconds = 0):
            → Bonus = sqrt(elapsed_seconds) * 10
            → Rewards faster completion
    
    Note:
        In STRICT mode, if elapsed > max_time, game stops before victory.
        Therefore, overtime malus only applies when:
        - timer_strict_mode = False (PERMISSIVE)
        - is_victory = True (player completed after timeout)
    """
```

### **Task 4.2: Implement Overtime Malus Calculation**

**Location**: In `calculate_final_score()` method, in the time bonus section

**Replace existing time bonus logic with this**:

```python
def calculate_final_score(
    self,
    is_victory: bool,
    elapsed_seconds: float,
    max_time_seconds: int = 0,
    timer_strict_mode: bool = True
) -> FinalScore:
    # ... existing code for base_score, difficulty_bonus, etc ...
    
    # === TIME BONUS/MALUS CALCULATION ===
    time_bonus = 0
    overtime_penalty = 0  # 🆕 Track overtime malus separately (v1.5.2.2)
    
    if max_time_seconds > 0:
        # Timer ON (countdown mode)
        
        if elapsed_seconds <= max_time_seconds:
            # ✅ Finished within time limit → BONUS
            remaining_seconds = max_time_seconds - elapsed_seconds
            time_bonus = int((remaining_seconds / max_time_seconds) * 1000)
            
            print(f"[SCORING] Time bonus: {time_bonus}pts (finished {int(remaining_seconds)}s early)")
        
        elif not timer_strict_mode:
            # ⏰ OVERTIME IN PERMISSIVE MODE → MALUS
            # Note: Only possible in PERMISSIVE mode (STRICT stops game at timeout)
            
            overtime_seconds = elapsed_seconds - max_time_seconds
            overtime_minutes = int(overtime_seconds / 60) + 1  # Round up to next minute
            
            # Malus: -100 points per overtime minute
            overtime_penalty = 100 * overtime_minutes
            time_bonus = -overtime_penalty  # Apply as negative bonus
            
            print(f"[SCORING] Overtime malus: -{overtime_penalty}pts ({overtime_minutes} min over limit)")
        
        else:
            # ⚠️ STRICT mode with overtime: Should never happen!
            # Game should have stopped at max_time_seconds
            print(f"[SCORING] WARNING: Overtime detected in STRICT mode! elapsed={elapsed_seconds}, max={max_time_seconds}")
            time_bonus = 0
    
    else:
        # Timer OFF (stopwatch mode) → Speed bonus
        time_bonus = int(math.sqrt(elapsed_seconds) * 10)
        print(f"[SCORING] Speed bonus (timer OFF): {time_bonus}pts")
    
    # ... rest of method (victory_bonus, total_score calculation) ...
```

### **Task 4.3: Update FinalScore Return with Overtime Info**

**Location**: At end of `calculate_final_score()`, in return statement

**Update to include overtime info**:

```python
def calculate_final_score(...) -> FinalScore:
    # ... calculation logic ...
    
    # Calculate total
    total_score = base_score + difficulty_bonus + time_bonus + victory_bonus
    
    # Prevent negative total
    if total_score < 0:
        print(f"[SCORING] Clamping negative total ({total_score}) to 0")
        total_score = 0
    
    # 🆕 Build detailed time bonus message (v1.5.2.2)
    if max_time_seconds > 0 and elapsed_seconds > max_time_seconds and not timer_strict_mode:
        # Overtime case
        time_bonus_detail = f"Malus tempo (overtime): -{overtime_penalty}"
    elif max_time_seconds > 0 and elapsed_seconds <= max_time_seconds:
        # Early finish
        time_bonus_detail = f"Bonus tempo (anticipo): +{time_bonus}"
    elif max_time_seconds == 0:
        # Timer off
        time_bonus_detail = f"Bonus velocità: +{time_bonus}"
    else:
        time_bonus_detail = f"Tempo: {time_bonus}"
    
    return FinalScore(
        base_score=base_score,
        difficulty_bonus=difficulty_bonus,
        time_bonus=time_bonus,
        victory_bonus=victory_bonus,
        total_score=total_score,
        breakdown={
            "Punteggio base": f"+{base_score}",
            "Moltiplicatore difficoltà": f"x{multiplier:.1f}" if difficulty_multiplier_enabled else "Disabilitato",
            "Bonus difficoltà": f"+{difficulty_bonus}",
            time_bonus_detail: "",  # 🆕 Dynamic message
            "Bonus vittoria": f"+{victory_bonus}" if is_victory else "0 (sconfitta)",
            "TOTALE": f"{total_score}"
        }
    )
```

### **Verification**:
- [ ] New parameter `timer_strict_mode` added with default `True`
- [ ] Docstring updated with overtime malus explanation
- [ ] Overtime malus calculation implemented (-100/min)
- [ ] Console logs added for debugging
- [ ] FinalScore breakdown includes overtime info
- [ ] Negative total clamped to 0

---

## ✅ STEP 5: Integration Testing (10 min)

### **Test Scenario 1: STRICT Mode, Timer Expires During Game**

**Setup**:
1. Start `test.py`
2. Open options (O key)
3. Set: Timer ON, 1 minute, STRICT mode (Option #8 = STRICT)
4. Start new game (N key)

**Actions**:
1. Play game normally (don't win)
2. Wait 61 seconds

**Expected Result**:
- ✅ At 60 seconds: TTS announces "Tempo scaduto! Partita terminata."
- ✅ Game stops immediately
- ✅ Shows final statistics (time, moves, cards placed)
- ✅ Returns to game submenu
- ✅ Console shows: `[TIMER STRICT] Game over by timeout`

### **Test Scenario 2: PERMISSIVE Mode, Timer Expires, Continue Playing**

**Setup**:
1. Start `test.py`
2. Open options (O key)
3. Set: Timer ON, 1 minute, PERMISSIVE mode (Option #8 = PERMISSIVE)
4. Start new game (N key)

**Actions**:
1. Play game normally
2. Wait 61 seconds (don't win yet)
3. Continue playing after timeout
4. Win game at 90 seconds elapsed

**Expected Result**:
- ✅ At 60 seconds: TTS announces "Tempo scaduto! Continui con penalità di 100 punti al minuto."
- ✅ Game continues normally
- ✅ At 90 seconds: Win game normally
- ✅ Final score shows: Overtime malus -100 pts (1 minute over limit)
- ✅ Console shows: `[TIMER PERMISSIVE] Overtime: +1min → Malus: -100pts`

### **Test Scenario 3: PERMISSIVE Mode, Finish Within Time Limit**

**Setup**:
1. Options: Timer ON, 10 minutes, PERMISSIVE mode
2. Start new game

**Actions**:
1. Win game in 8 minutes

**Expected Result**:
- ✅ No timeout announcement
- ✅ Final score shows: Time bonus +200 pts (2 min early)
- ✅ Normal victory flow

### **Test Scenario 4: Timer OFF (Stopwatch Mode)**

**Setup**:
1. Options: Timer OFF
2. Start new game

**Actions**:
1. Play and win

**Expected Result**:
- ✅ No timeout checks
- ✅ Final score shows: Speed bonus (sqrt formula)
- ✅ No malus applied

### **Test Scenario 5: Option Toggle in Virtual Window**

**Setup**:
1. Open options (O key)

**Actions**:
1. Navigate to Option #8 (arrow down or press 8)
2. Press ENTER to toggle
3. Verify mode changes: STRICT ↔ PERMISSIVE
4. Press I to read all settings

**Expected Result**:
- ✅ Option #8 displays correctly in list
- ✅ Toggle works: "Modalità timer: STRICT/PERMISSIVE"
- ✅ TTS explains mode behavior
- ✅ Read all settings includes Option #8
- ✅ Dirty flag set (confirms save prompt on close)

### **Verification Checklist**:
- [ ] All 5 scenarios tested and passing
- [ ] TTS announcements clear and helpful
- [ ] Console logs appear in all scenarios
- [ ] No crashes or exceptions
- [ ] Timer flag resets correctly between games
- [ ] Options save/load correctly

---

## ✅ STEP 6: Documentation Updates (10 min)

### **Task 6.1: Update README.md**

**File**: `README.md`

**Location**: Find "Opzioni di Gioco" section (or equivalent features list)

**Add this entry**:

```markdown
### Modalità Timer (v1.5.2.2)

Il gioco offre **due comportamenti configurabili** quando il timer scade:

#### STRICT Mode (Modalità Rigorosa) - Default
- ⏱️ La partita si **interrompe automaticamente** alla scadenza
- 📊 Vengono mostrate le statistiche finali
- 🔙 Ritorno automatico al menu di gioco
- ⚖️ Nessuna penalità di punteggio (game over per timeout)
- 📜 Comportamento storico dalla versione legacy

#### PERMISSIVE Mode (Modalità Permissiva) - Nuovo
- ✅ La partita **continua oltre il limite** di tempo
- 🔊 Annuncio TTS: "Tempo scaduto! Penalità applicata."
- ⚖️ Penalità punteggio: **-100 punti per ogni minuto** oltre il limite
- 🎓 Ideale per apprendimento e gioco casuale
- 🏆 Permette di completare la partita anche in overtime

**Configurazione**: Opzione #8 nella Finestra Opzioni (tasto O)
```

### **Task 6.2: Update CHANGELOG.md**

**File**: `CHANGELOG.md`

**Location**: Add new section at top

**Add this section**:

```markdown
## [v1.5.2.2] - 2026-02-11

### 🐛 Bug Fix + 🆕 Feature: Timer Expiration Management

#### Fixed
- **BUG #3**: Timer scaduto non interrompeva la partita
  - Implementato controllo periodico ogni 1 secondo (pygame event)
  - Aggiunto handler `_check_timer_expiration()` in `test.py`
  - Replicato comportamento legacy `ceck_lost_by_time()` + `you_lost_by_time()`

#### Added
- **Modalità Timer Configurabile** (Opzione #8 in Finestra Opzioni)
  - **STRICT Mode** (default, compatibilità legacy):
    - Partita si interrompe automaticamente alla scadenza
    - Mostra statistiche finali e ritorna al menu
    - Nessuna penalità di punteggio (game over)
  - **PERMISSIVE Mode** (nuova feature):
    - Partita continua oltre il limite di tempo
    - Annuncio TTS di timeout + malus
    - Penalità: **-100 punti per ogni minuto** in overtime
    - Ideale per apprendimento e gioco casuale

#### Technical Details
- `game_settings.py`: +`timer_strict_mode` field (bool, default True)
- `options_controller.py`: +Option #8 con toggle e help aggiornato
- `test.py`: 
  - +`TIME_CHECK_EVENT` (pygame.USEREVENT+1, ogni 1s)
  - +`_check_timer_expiration()` method
  - +`_handle_game_over_by_timeout()` method
- `scoring_service.py`: 
  - +Overtime malus calculation (-100pts/min)
  - +`timer_strict_mode` parameter in `calculate_final_score()`

#### UX/Accessibility
- TTS annuncia timeout in PERMISSIVE mode: 
  - "Tempo scaduto! Penalità di X punti. Tempo extra: Y minuti."
- TTS mostra report completo in STRICT mode:
  - "Tempo scaduto! Partita terminata. Statistiche finali: ..."
- Opzione #8 navigabile con frecce o tasto 8
- Help text (H key) aggiornato con nuova opzione

#### Backward Compatibility
- ✅ Default STRICT mode = comportamento legacy
- ✅ Partite esistenti non influenzate
- ✅ Salvataggio/caricamento settings compatibile
```

### **Task 6.3: Update Docstring in test.py**

**File**: `test.py`

**Location**: Module docstring at top

**Update version info**:

```python
"""Clean Architecture entry point - Audiogame version.

# ... existing intro ...

New in v1.5.2.2 [Bug Fix + Feature] - COMPLETE:
- Fixed timer expiration detection (#BUG-003)
- Added periodic timer check (pygame event every 1s)
- Implemented STRICT mode (auto-stop, legacy behavior)
- Implemented PERMISSIVE mode (continue with -100pts/min malus)
- Added Option #8: Timer mode toggle in Options Window
- Integrated overtime malus with scoring system
"""
```

### **Verification**:
- [ ] README.md updated with feature description
- [ ] CHANGELOG.md updated with v1.5.2.2 section
- [ ] test.py docstring updated
- [ ] All technical details documented
- [ ] UX/accessibility notes included

---

## 🎯 FINAL VERIFICATION

### **Code Quality Checklist**:
- [ ] All type hints present and correct
- [ ] All docstrings complete and accurate
- [ ] Console logs added for debugging
- [ ] No magic numbers (constants defined)
- [ ] Error handling for edge cases
- [ ] Backward compatibility maintained

### **Architecture Checklist**:
- [ ] Domain layer changes isolated to `GameSettings`
- [ ] Application layer properly orchestrates logic
- [ ] Infrastructure layer (test.py) handles UI events
- [ ] Service layer calculates malus correctly
- [ ] No circular dependencies introduced

### **UX/Accessibility Checklist**:
- [ ] TTS announcements clear and helpful
- [ ] Keyboard navigation works (arrows + number keys)
- [ ] Help text (H key) updated
- [ ] Options save/load correctly
- [ ] No silent failures (all actions vocalized)

### **Testing Checklist**:
- [ ] All 5 test scenarios pass
- [ ] No console errors or exceptions
- [ ] Timer resets correctly between games
- [ ] Overtime malus calculated correctly
- [ ] STRICT mode stops game immediately
- [ ] PERMISSIVE mode announces once, continues

---

## 📋 COMMIT MESSAGE TEMPLATE

```
feat: Add configurable timer expiration behavior (v1.5.2.2)

BREAKING: None (backward compatible, default = legacy STRICT mode)

Fixed:
- BUG #3: Timer expired without stopping game
- Added periodic timer check (pygame event every 1s)
- Implemented game over by timeout handler

Added:
- Option #8: Timer mode toggle (STRICT/PERMISSIVE)
- STRICT mode: Auto-stop at timeout (legacy behavior)
- PERMISSIVE mode: Continue with -100pts/min malus (new)
- Overtime penalty in scoring system

Modified files:
- src/domain/services/game_settings.py (+timer_strict_mode field)
- src/application/options_controller.py (+Option #8 + toggle)
- test.py (+timer event + check methods)
- src/domain/services/scoring_service.py (+overtime malus)
- README.md (feature documentation)
- CHANGELOG.md (v1.5.2.2 section)

Testing:
- All 5 scenarios verified
- TTS announcements tested
- Options save/load tested
- Backward compatibility confirmed
```

---

## 🚀 IMPLEMENTATION ORDER

**Recommended sequence** (copy-paste code in this order):

1. ✅ **STEP 1**: GameSettings (+5 min) - Foundation
2. ✅ **STEP 2**: OptionsController (+15 min) - User configuration
3. ✅ **STEP 3**: test.py (+20 min) - Timer detection logic
4. ✅ **STEP 4**: ScoringService (+10 min) - Malus calculation
5. ✅ **STEP 5**: Testing (+10 min) - Verify all scenarios
6. ✅ **STEP 6**: Documentation (+10 min) - README + CHANGELOG

**Total estimated time**: 70 minutes (with testing)

---

## 💡 NOTES FOR COPILOT

### **Context for AI Assistant**:
This feature implements a **user-configurable timer expiration behavior** to fix a critical bug (timer not stopping game) while adding flexibility for different play styles.

### **Key Design Decisions**:
1. **Default STRICT** (not PERMISSIVE) for backward compatibility
2. **Overtime malus = -100pts/min** (simple, understandable, impactful)
3. **Announce once** in PERMISSIVE mode (not every second)
4. **Return to game submenu** (not main menu) on timeout
5. **Option #8** (last in list, easy to add without breaking existing keys)

### **Edge Cases to Handle**:
- Timer expires exactly at victory moment → Use victory logic (ignore timeout)
- Multiple overtime minutes → Round up (1:30 overtime = -200pts for 2min)
- Negative total score → Clamp to 0
- Timer disabled mid-game → No checks (skip in event handler)

### **Testing Priorities**:
1. STRICT mode auto-stop (legacy compatibility)
2. PERMISSIVE mode single announcement
3. Overtime malus calculation accuracy
4. Options save/load persistence

### **Future Enhancements** (not in this TODO):
- Custom malus value (not fixed -100)
- Grace period (first minute overtime free)
- Visual timer bar (requires GUI)
- Timer pause feature

---

## ✅ COMPLETION CRITERIA

This TODO is **COMPLETE** when:
- [ ] All 4 files modified with provided code
- [ ] All 5 test scenarios passing
- [ ] README and CHANGELOG updated
- [ ] Commit pushed to `copilot/implement-scoring-system-v2` branch
- [ ] No regressions in existing features
- [ ] TTS feedback clear for blind users

**Estimated completion**: 1-1.5 hours for experienced developer

---

**Created**: 2026-02-11 03:23 CET  
**Branch**: `copilot/implement-scoring-system-v2`  
**Version**: v1.5.2.2  
**Priority**: HIGH (Bug Fix + UX Enhancement)  
**Assignee**: GitHub Copilot + Developer

---

END OF TODO
