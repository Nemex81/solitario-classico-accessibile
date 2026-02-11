# TODO: Fix CTRL+ALT+W Debug Victory Command - wxDialog Integration

**Version**: v1.6.2  
**Date**: 2026-02-11  
**Status**: 🔴 IN PROGRESS  
**Priority**: HIGH  
**Type**: BUG FIX  
**Branch**: `copilot/implement-victory-flow-dialogs`  
**Estimated Time**: 60-90 minutes

---

## Executive Summary 📋

**Problem**: Pressing CTRL+ALT+W during gameplay does NOT show wxPython dialog with statistics and does NOT return to game menu after end_game().

**Root Causes**:
1. `use_native_dialogs=True` NOT passed to `GameEngine.create()` in test.py → `self.dialogs = None`
2. `end_game()` has NO UI state management → doesn't set `is_menu_open=True`
3. Missing callback pattern between GameEngine and test.py for end game flow
4. No separation of concerns: engine handles game logic + UI state (anti-pattern)

**Solution**: Implement callback pattern to delegate UI state management to test.py after game ends.

---

## Implementation Checklist ✅

### Phase 1: Enable Dialog Provider (5 min)
- [x] **Task 1.1**: Modify `test.py` line ~111 → Add `use_native_dialogs=True` parameter
- [x] **Verify**: Console log shows "✓ Dialog nativi wxPython attivi"

### Phase 2: Add Callback Support in GameEngine (15 min)
- [x] **Task 2.1**: Modify `game_engine.py` `__init__()` line ~85 → Add `on_game_ended` parameter
- [x] **Task 2.2**: Modify `game_engine.py` `end_game()` lines 1070-1111 → Call callback instead of direct reset
- [x] **Task 2.3**: Update `game_engine.py` `create()` docstring → Document callback injection pattern
- [x] **Verify**: No circular dependencies, callback stored correctly

### Phase 3: Implement Callback in test.py (25 min)
- [ ] **Task 3.1**: Add new method `handle_game_ended(wants_rematch)` in test.py line ~665
- [ ] **Task 3.2**: Inject callback in `test.py` `__init__()` line ~117 → `self.engine.on_game_ended = self.handle_game_ended`
- [ ] **Verify**: Callback wired correctly, no runtime errors

### Phase 4: Testing & Validation (15-30 min)
- [ ] **Test 4.1**: Start game → Press CTRL+ALT+W → wxDialog appears with statistics
- [ ] **Test 4.2**: In dialog → Press ESC (No rematch) → Returns to game submenu
- [ ] **Test 4.3**: Start game → Press CTRL+ALT+W → Choose "Sì" → New game starts
- [ ] **Test 4.4**: Real victory (complete all 4 suits) → Same behavior as CTRL+ALT+W
- [ ] **Verify**: All 4 scenarios work correctly with NVDA screen reader

---

## Detailed Implementation Plan 🛠️

### PHASE 1: Enable Dialog Provider in test.py ✅

**File**: `test.py`  
**Location**: `__init__()` method, line ~111  
**Time**: 5 minutes

**Current Code**:
```python
# Application: Game engine setup (now with settings!)
print("Inizializzazione motore di gioco...")
self.engine = GameEngine.create(
    audio_enabled=(self.screen_reader is not None),
    tts_engine="auto",
    verbose=1,
    settings=self.settings  # NEW PARAMETER (v1.4.2.1)
)
print("✓ Game engine pronto")
```

**Modified Code**:
```python
# Application: Game engine setup (now with settings AND dialogs!)
print("Inizializzazione motore di gioco...")
self.engine = GameEngine.create(
    audio_enabled=(self.screen_reader is not None),
    tts_engine="auto",
    verbose=1,
    settings=self.settings,  # v1.4.2.1
    use_native_dialogs=True  # 🆕 v1.6.2 - ENABLE WX DIALOGS
)
print("✓ Game engine pronto")
```

**Rationale**: 
- Enables `WxDialogProvider` creation in `GameEngine.create()`
- Populates `self.engine.dialogs` with functional dialog provider
- Graceful degradation: if wxPython unavailable, logs warning but continues

**Verification**:
```bash
python test.py
# Expected output:
# ✓ Dialog nativi wxPython attivi
# ✓ Game engine pronto
```

---

### PHASE 2: Add Callback Support in GameEngine 🔄

**File**: `src/application/game_engine.py`  
**Locations**: 3 methods to modify  
**Time**: 15 minutes

#### Task 2.1: Modify `__init__()` to Accept Callback

**Location**: Line ~85  
**Add Parameter**:

```python
def __init__(
    self,
    table: GameTable,
    service: GameService,
    rules: SolitaireRules,
    cursor: CursorManager,
    selection: SelectionManager,
    screen_reader: Optional[ScreenReader] = None,
    settings: Optional[GameSettings] = None,
    score_storage: Optional[ScoreStorage] = None,
    dialog_provider: Optional['DialogProvider'] = None,
    on_game_ended: Optional[Callable[[bool], None]] = None  # 🆕 NEW PARAMETER
):
    """Initialize game engine.
    
    Args:
        # ... existing args ...
        dialog_provider: Optional dialog provider for native UI dialogs (NEW v1.6.0)
        on_game_ended: Optional callback when game ends, receives wants_rematch bool (NEW v1.6.2)
    """
    # ... existing initialization ...
    
    # ✨ NEW v1.6.0: Dialog integration (opt-in)
    self.dialogs = dialog_provider
    
    # 🆕 NEW v1.6.2: End game callback (opt-in)
    self.on_game_ended = on_game_ended
    
    # ... rest of initialization ...
```

**Import Addition** (top of file):
```python
from typing import Optional, Tuple, Dict, Any, List, TYPE_CHECKING, Callable  # Add Callable
```

---

#### Task 2.2: Refactor `end_game()` to Use Callback

**Location**: Lines 1070-1111  
**Current Logic**: Direct `new_game()` call or `reset_game()`  
**New Logic**: Delegate to callback with rematch decision

**Modified Code**:
```python
def end_game(self, is_victory: bool) -> None:
    """Handle game end with full reporting and rematch prompt.
    
    Complete flow:
    1. Snapshot statistics (including suits)
    2. Calculate final score (if scoring enabled)
    3. Save score to storage (if available)
    4. Generate complete Italian report
    5. Announce via TTS (always)
    6. Show native dialog (if available)
    7. Prompt for rematch (if dialogs available)
    8. 🆕 Call on_game_ended callback to return control to test.py
    
    Args:
        is_victory: True if all 4 suits completed
        
    Side effects:
        - Stops game timer
        - Saves score to JSON (if scoring enabled)
        - May start new game (if user chooses rematch AND no callback)
        
    Note (v1.6.2):
        If on_game_ended callback is set, this method NO LONGER handles
        UI state management (is_menu_open, menu announcements). 
        All UI logic delegated to test.py.handle_game_ended().
        
    Example:
        >>> engine.end_game(is_victory=True)
        # TTS announces: "Hai Vinto! ..."
        # Dialog shows full report
        # Prompts: "Vuoi giocare ancora?"
        # Calls: self.on_game_ended(wants_rematch=False)
    """
    
    # ═══════════════════════════════════════════════════════════
    # STEP 1: Snapshot Statistics
    # ═══════════════════════════════════════════════════════════
    self.service._snapshot_statistics()
    final_stats = self.service.get_final_statistics()
    
    # ═══════════════════════════════════════════════════════════
    # STEP 2: Calculate Final Score
    # ═══════════════════════════════════════════════════════════
    final_score = None
    if self.settings and self.settings.scoring_enabled and self.service.scoring:
        final_score = self.service.scoring.calculate_final_score(
            elapsed_seconds=final_stats['elapsed_time'],
            move_count=final_stats['move_count'],
            is_victory=is_victory,
            timer_strict_mode=self.settings.timer_strict_mode if self.settings else True
        )
    
    # ═══════════════════════════════════════════════════════════
    # STEP 3: Save Score
    # ═══════════════════════════════════════════════════════════
    if final_score and self.score_storage:
        self.score_storage.save_score(final_score)
    
    # ═══════════════════════════════════════════════════════════
    # STEP 4: Generate Report
    # ═══════════════════════════════════════════════════════════
    from src.presentation.formatters.report_formatter import ReportFormatter
    
    deck_type = self.settings.deck_type if self.settings else "french"
    report = ReportFormatter.format_final_report(
        stats=final_stats,
        final_score=final_score,
        is_victory=is_victory,
        deck_type=deck_type
    )
    
    # ═══════════════════════════════════════════════════════════
    # STEP 5: TTS Announcement (Always, even if dialogs enabled)
    # ═══════════════════════════════════════════════════════════
    if self.screen_reader:
        self.screen_reader.tts.speak(report, interrupt=True)
    
    # ═══════════════════════════════════════════════════════════
    # STEP 6: Native Statistics Dialog (Structured, Accessible)
    # ═══════════════════════════════════════════════════════════
    wants_rematch = False
    if self.dialogs:
        # Show statistics dialog (v1.6.1+)
        self.dialogs.show_statistics_report(
            stats=final_stats,
            final_score=final_score,
            is_victory=is_victory,
            deck_type=deck_type
        )
        
        # ═══════════════════════════════════════════════════════
        # STEP 7: Rematch Prompt
        # ═══════════════════════════════════════════════════════
        wants_rematch = self.dialogs.show_yes_no(
            "Vuoi giocare ancora?", 
            "Rivincita?"
        )
    
    # ═══════════════════════════════════════════════════════════
    # STEP 8: 🆕 Delegate to test.py via Callback (v1.6.2)
    # ═══════════════════════════════════════════════════════════
    if self.on_game_ended:
        # NEW BEHAVIOR (v1.6.2): Pass control back to test.py
        # test.py will handle:
        # - UI state management (is_menu_open)
        # - Menu announcements
        # - Rematch logic (call start_game if wanted)
        self.on_game_ended(wants_rematch)
    else:
        # FALLBACK: Old behavior (no callback set)
        # This path used for backward compatibility or unit tests
        if wants_rematch:
            self.new_game()
            return  # Exit early (new_game() already resets)
        else:
            self.service.reset_game()
```

**Key Changes**:
1. **Callback check** at end: `if self.on_game_ended:`
2. **Delegate UI logic**: Pass `wants_rematch` to callback
3. **Fallback preserved**: Old behavior if callback not set (backward compat)

---

#### Task 2.3: Update `create()` Docstring

**Location**: Line ~110  
**Add Documentation**:

```python
@classmethod
def create(
    cls,
    audio_enabled: bool = True,
    tts_engine: str = "auto",
    verbose: int = 1,
    settings: Optional[GameSettings] = None,
    use_native_dialogs: bool = False
) -> "GameEngine":
    """Factory method to create fully initialized game engine.
    
    Args:
        audio_enabled: Enable audio feedback
        tts_engine: TTS engine ("auto", "nvda", "sapi5")
        verbose: Audio verbosity level (0-2)
        settings: GameSettings instance for configuration
        use_native_dialogs: Enable native wxPython dialogs (NEW v1.6.0)
        
    Returns:
        Initialized GameEngine instance ready to play
    
    Note (v1.6.2):
        on_game_ended callback must be set manually after creation:
        
        >>> engine = GameEngine.create(use_native_dialogs=True)
        >>> engine.on_game_ended = my_callback_function
        >>> # Now end_game() will call my_callback_function(wants_rematch)
        
    Example Callback:
        >>> def handle_end(wants_rematch: bool):
        ...     if wants_rematch:
        ...         engine.new_game()
        ...     else:
        ...         # Return to menu
        ...         app.is_menu_open = True
        ...         app.announce_menu()
    """
    # ... existing code unchanged ...
    
    # ✨ NEW v1.6.0: Create dialog provider if requested
    dialog_provider = None
    if use_native_dialogs:
        try:
            from src.infrastructure.ui.wx_dialog_provider import WxDialogProvider
            dialog_provider = WxDialogProvider()
        except ImportError:
            # wxPython not available, graceful degradation
            dialog_provider = None
    
    # 🆕 v1.6.2: Pass on_game_ended=None (caller must set manually)
    return cls(
        table, service, rules, cursor, selection, 
        screen_reader, settings, score_storage, 
        dialog_provider,
        on_game_ended=None  # 🆕 Caller must inject callback after creation
    )
```

---

### PHASE 3: Implement Callback Handler in test.py 📞

**File**: `test.py`  
**Locations**: 2 modifications  
**Time**: 25 minutes

#### Task 3.1: Add `handle_game_ended()` Method

**Location**: After `_handle_game_over_by_timeout()`, line ~665  
**New Method**:

```python
def handle_game_ended(self, wants_rematch: bool) -> None:
    """Handle game end callback from GameEngine.end_game().
    
    This is the CENTRAL handler for ALL game end scenarios:
    - Victory detected (all 4 suits complete)
    - CTRL+ALT+W debug command used
    - Timer expired in STRICT mode (via _handle_game_over_by_timeout)
    
    Responsibilities:
    - Reset timer flags for next game
    - Handle rematch: Start new game OR return to game submenu
    - Manage UI state: Set is_menu_open flag correctly
    - Announce actions via TTS
    
    Args:
        wants_rematch: True if user chose "Sì" in rematch dialog
    
    Flow:
        wants_rematch=True:
            1. Call start_game() → stays in gameplay mode
            2. TTS announces "Nuova partita avviata!"
        
        wants_rematch=False:
            1. Set is_menu_open = True
            2. TTS announces "Ritorno al menu di gioco."
            3. Call game_submenu.announce_welcome()
    
    Side Effects:
        - Resets self._timer_expired_announced flag
        - Changes self.is_menu_open state
        - May trigger new game via start_game()
    
    Note:
        This method is ONLY called from GameEngine.end_game() via callback.
        It separates game logic (engine) from UI state management (test.py).
        
    Example:
        >>> # From GameEngine.end_game():
        >>> if self.on_game_ended:
        ...     self.on_game_ended(wants_rematch=False)
        >>> # Result: UI returns to game submenu
    """
    print("\n" + "="*60)
    print(f"CALLBACK: Game ended - Rematch requested: {wants_rematch}")
    print("="*60)
    
    # ═══════════════════════════════════════════════════════════
    # STEP 1: Reset Timer Flags
    # ═══════════════════════════════════════════════════════════
    # Important for next game! Prevents "timeout" message on fresh game
    self._timer_expired_announced = False
    
    # ═══════════════════════════════════════════════════════════
    # STEP 2: Handle Rematch Decision
    # ═══════════════════════════════════════════════════════════
    
    if wants_rematch:
        # ─────────────────────────────────────────────────────────
        # USER WANTS REMATCH: Stay in gameplay, start new game
        # ─────────────────────────────────────────────────────────
        print("→ User chose rematch - Starting new game")
        
        # start_game() will:
        # - Call engine.reset_game() + engine.new_game()
        # - Reset ESC timer
        # - Announce "Nuova partita avviata!"
        self.start_game()
        
    else:
        # ─────────────────────────────────────────────────────────
        # USER DECLINED REMATCH: Return to game submenu
        # ─────────────────────────────────────────────────────────
        print("→ User declined rematch - Returning to game submenu")
        
        # 🆕 CRITICAL: Enable menu state
        # This allows menu navigation to work again
        self.is_menu_open = True
        
        # Announce return to menu with TTS
        if self.screen_reader:
            self.screen_reader.tts.speak(
                "Ritorno al menu di gioco.",
                interrupt=True
            )
            pygame.time.wait(400)  # Pause for TTS readability
            
            # Re-announce game submenu with welcome message
            # This helps user orient after game end
            self.game_submenu.announce_welcome()
    
    print("="*60)
```

**Key Features**:
1. **Handles both paths**: rematch (start new game) + no rematch (return to menu)
2. **Resets flags**: `_timer_expired_announced` for clean state
3. **Sets UI state**: `is_menu_open = True` when returning to menu
4. **TTS feedback**: Announces actions clearly
5. **Comprehensive docs**: Explains all scenarios and side effects

---

#### Task 3.2: Inject Callback After Engine Creation

**Location**: `__init__()` method, line ~117  
**Context**: Right after `self.engine = GameEngine.create(...)`

**Current Code**:
```python
# Application: Game engine setup (now with settings!)
print("Inizializzazione motore di gioco...")
self.engine = GameEngine.create(
    audio_enabled=(self.screen_reader is not None),
    tts_engine="auto",
    verbose=1,
    settings=self.settings,
    use_native_dialogs=True  # Added in Phase 1
)
print("✓ Game engine pronto")
```

**Modified Code**:
```python
# Application: Game engine setup (now with settings AND dialogs!)
print("Inizializzazione motore di gioco...")
self.engine = GameEngine.create(
    audio_enabled=(self.screen_reader is not None),
    tts_engine="auto",
    verbose=1,
    settings=self.settings,
    use_native_dialogs=True  # v1.6.2 - Enables wxDialogs
)

# 🆕 v1.6.2: Inject end game callback for UI state management
# This allows engine to delegate UI logic back to test.py after game ends
self.engine.on_game_ended = self.handle_game_ended

print("✓ Game engine pronto con callback UI")
```

**Rationale**:
- **Separation of concerns**: Engine handles game logic, test.py handles UI state
- **Testability**: Engine can be tested without UI dependencies
- **Flexibility**: Different UIs can provide different callbacks

---

## Verification & Testing 🧪

### Manual Testing Scenarios

#### Scenario 1: Debug Victory with Dialog (CTRL+ALT+W)

**Steps**:
1. Start application: `python test.py`
2. Navigate menu: Gioca al solitario → Nuova partita
3. Execute 2-3 moves (any cards)
4. Press: **CTRL+ALT+W**

**Expected Behavior**:
- ✅ TTS announces complete game report (time, moves, stats)
- ✅ wxPython dialog appears with structured statistics
- ✅ Dialog shows: Victory message, time, moves, suits completed, score
- ✅ Dialog is keyboard-navigable (Tab, Enter work)
- ✅ NVDA reads dialog content automatically when opened

**Verification Points**:
- Console log: `CALLBACK: Game ended - Rematch requested: False` (if ESC pressed)
- Console log: `→ User declined rematch - Returning to game submenu`
- TTS says: "Ritorno al menu di gioco."
- UI state: Menu navigation works (UP/DOWN arrows)

---

#### Scenario 2: Decline Rematch → Return to Menu

**Steps**:
1. Continue from Scenario 1 (dialog open)
2. Press: **ESC** or navigate to "No" and press ENTER

**Expected Behavior**:
- ✅ Dialog closes
- ✅ TTS announces: "Ritorno al menu di gioco."
- ✅ Game submenu welcome message plays
- ✅ Menu navigation works (UP/DOWN/ENTER)
- ✅ Can select "Nuova partita" to start new game

**Verification Points**:
- `self.is_menu_open == True`
- `self._timer_expired_announced == False` (reset)
- Menu responds to keyboard input

---

#### Scenario 3: Accept Rematch → Start New Game

**Steps**:
1. Start game → Press CTRL+ALT+W (or win legitimately)
2. In dialog, press: **S** (Sì) or navigate to "Yes" and press ENTER

**Expected Behavior**:
- ✅ Dialog closes
- ✅ TTS announces: "Nuova partita avviata! Usa H per l'aiuto comandi."
- ✅ New game starts immediately (no menu)
- ✅ Cursor at pile base 1, card 1
- ✅ Timer reset to 0
- ✅ Move count reset to 0

**Verification Points**:
- `self.is_menu_open == False` (stays in gameplay)
- `self.engine.service.move_count == 0`
- `self.engine.service.get_elapsed_time() < 1` (timer just started)
- Card positions reset (fresh distribution)

---

#### Scenario 4: Real Victory (Complete All Suits)

**Steps**:
1. Play game to completion (or use debug tricks to speed up)
2. Place last card in foundation (e.g., King of Spades)

**Expected Behavior**:
- ✅ TTS announces: "Mossa eseguita. [card details]"
- ✅ TTS announces: "Hai vinto! Mosse: X, Tempo: Y secondi"
- ✅ Complete game report vocalized
- ✅ wxDialog appears with statistics (same as CTRL+ALT+W)
- ✅ Rematch prompt appears

**Verification Points**:
- Same flow as Scenario 1 (dialog + callback)
- `is_victory=True` passed to `end_game()`
- Score calculated and saved (if scoring enabled)

---

#### Scenario 5: NVDA Screen Reader Compatibility

**Steps**:
1. Start NVDA screen reader (Windows)
2. Start application: `python test.py`
3. Navigate to gameplay
4. Press CTRL+ALT+W

**Expected NVDA Behavior**:
- ✅ NVDA reads TTS report (may overlap slightly)
- ✅ When dialog opens, NVDA announces: "Congratulazioni!" (title)
- ✅ NVDA auto-reads TextCtrl content (full report)
- ✅ TAB key moves focus to "OK" button
- ✅ NVDA announces: "OK, pulsante"
- ✅ ENTER or SPACE closes dialog

**Verification Points**:
- NVDA reads dialog content without manual intervention
- Keyboard navigation works (Tab, Enter, ESC)
- No focus traps or accessibility issues

---

### Automated Testing (Optional)

**Unit Test for Callback**:
```python
def test_end_game_with_callback():
    """Test end_game calls on_game_ended callback correctly."""
    callback_called = False
    rematch_decision = None
    
    def mock_callback(wants_rematch: bool):
        nonlocal callback_called, rematch_decision
        callback_called = True
        rematch_decision = wants_rematch
    
    engine = GameEngine.create(use_native_dialogs=False)  # No dialogs in test
    engine.on_game_ended = mock_callback
    engine.new_game()
    
    # Trigger end game
    engine.end_game(is_victory=True)
    
    # Verify
    assert callback_called, "Callback should be called"
    assert rematch_decision == False, "Default rematch decision should be False"
```

---

## Expected Outcomes ✨

### Before Fix (Current Broken State ❌)
- Press CTRL+ALT+W → TTS only, NO dialog
- Game state reset BUT UI stuck in gameplay mode
- Can't navigate menu, must press ESC to unstuck
- Poor UX: unclear what happened

### After Fix (Expected Working State ✅)
- Press CTRL+ALT+W → TTS + wxDialog with full statistics
- Dialog keyboard-navigable, NVDA-compatible
- Decline rematch → Returns cleanly to game submenu
- Accept rematch → New game starts immediately
- Consistent with natural victory flow (same behavior)
- Clear UX: user always knows where they are

---

## Rollback Plan 🔄

If implementation causes regressions:

1. **Revert `test.py` changes**:
   ```bash
   git checkout HEAD -- test.py
   ```

2. **Revert `game_engine.py` changes**:
   ```bash
   git checkout HEAD -- src/application/game_engine.py
   ```

3. **Expected behavior after rollback**:
   - CTRL+ALT+W will vocalize via TTS only (no dialog)
   - Game will reset but UI may be stuck
   - Original bug remains, but no new issues introduced

---

## Additional Notes 📝

### Why Callback Pattern?

**Anti-pattern** (current):
```python
# GameEngine.end_game() directly manages UI state
def end_game(self, is_victory: bool):
    # ... game logic ...
    if wants_rematch:
        self.new_game()  # OK (game logic)
    else:
        # ❌ BAD: Engine shouldn't know about app.is_menu_open
        app.is_menu_open = True  # Tight coupling!
```

**Good pattern** (new):
```python
# GameEngine.end_game() delegates UI to callback
def end_game(self, is_victory: bool):
    # ... game logic ...
    if self.on_game_ended:
        self.on_game_ended(wants_rematch)  # ✅ Clean delegation
```

**Benefits**:
- **Separation of concerns**: Engine = game logic, test.py = UI state
- **Testability**: Engine testable without pygame/UI dependencies
- **Flexibility**: Different UIs (GUI, CLI, web) can provide different callbacks
- **Maintainability**: Changes to UI flow don't require engine modifications

---

### Compatibility Notes

- ✅ **Backward compatible**: If callback not set, falls back to old behavior
- ✅ **Graceful degradation**: If wxPython unavailable, TTS-only mode still works
- ✅ **No breaking changes**: Existing unit tests continue to pass
- ✅ **Optional feature**: `use_native_dialogs=False` disables dialogs (default)

---

## Implementation Time Estimate ⏱️

| Phase | Task | Time | Running Total |
|-------|------|------|---------------|
| 1 | Enable use_native_dialogs | 5 min | 5 min |
| 2 | Add callback to GameEngine | 15 min | 20 min |
| 3 | Implement callback in test.py | 25 min | 45 min |
| 4 | Manual testing (5 scenarios) | 15-30 min | 60-75 min |
| Buffer | Unexpected issues | 10-15 min | **70-90 min** |

**Total Estimated Time**: **1.0-1.5 hours**

---

## Success Criteria 🎯

Implementation is complete when:

1. ✅ CTRL+ALT+W shows wxDialog with statistics
2. ✅ Dialog is keyboard-navigable (Tab, Enter, ESC)
3. ✅ NVDA screen reader reads dialog content
4. ✅ "No rematch" returns cleanly to game submenu
5. ✅ "Yes rematch" starts new game immediately
6. ✅ Real victory (4 suits complete) has same behavior
7. ✅ No console errors or warnings
8. ✅ Backward compatible (no breaking changes)

---

**Last Updated**: 2026-02-11 23:11 CET  
**Next Action**: Begin Phase 1 implementation