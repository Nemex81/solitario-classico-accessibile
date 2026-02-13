# FIX: Panel Swap Crash During Event Handling

**Status**: 🔴 CRITICAL BUG - App closes instead of returning to menu  
**Branch**: `copilot/remove-pygame-migrate-wxpython`  
**Affected Version**: v2.0.2  
**Priority**: P0 (Blocks release)  
**Created**: 2026-02-14  

---

## 📋 Table of Contents

1. [Problem Summary](#problem-summary)
2. [Root Cause Analysis](#root-cause-analysis)
3. [Comparative Analysis: Working Pattern](#comparative-analysis-working-pattern)
4. [Solution Design](#solution-design)
5. [Implementation Plan](#implementation-plan)
6. [Testing Checklist](#testing-checklist)
7. [References](#references)

---

## Problem Summary

### Current Behavior (❌ BROKEN)

When user presses ESC during gameplay to abandon game and return to menu:

1. ✅ Abandon confirmation dialog shows correctly
2. ✅ User confirms abandon (clicks "Sì")
3. ✅ Step 1/4: Gameplay panel hidden successfully
4. ✅ Step 2/4: Game engine reset complete
5. ✅ Step 3/4: Showing menu panel starts...
6. ❌ **APP CLOSES** during `view_manager.show_panel('menu')`

### Expected Behavior (✅ CORRECT)

After ESC confirm:
1. Game engine resets
2. Gameplay panel hides
3. Menu panel shows
4. User can navigate menu again

### Log Evidence

```
============================================================
ABANDON GAME: User confirmed - Starting safe transition
============================================================
→ STEP 1/4: Hiding gameplay panel...
  ✓ Gameplay panel hidden successfully
→ STEP 2/4: Resetting game engine...
  ✓ Game engine reset complete
→ STEP 3/4: Showing menu panel...
============================================================
RETURN_TO_MENU: Start UI transition
============================================================
→ Current panel: gameplay
→ Menu panel reference: <src.infrastructure.ui.menu_panel.MenuPanel object at 0x000002410A539F30>
→ Menu panel valid: True
→ Calling view_manager.show_panel('menu')...
(audiopygamemaker311) PS C:\Users\nemex\OneDrive\Documenti\GitHub\solitario-classico-accessibile>
```

**Critical**: No output after `→ Calling view_manager.show_panel('menu')...`  
**Conclusion**: Crash happens INSIDE `show_panel()` before it returns.

---

## Root Cause Analysis

### 🔍 Investigation Path

#### Attempt #1: "Hide → Reset → Show" Pattern (v2.0.2)

**Hypothesis**: Engine reset invalidates panel references during hide.  
**Fix Applied**: Hide panel BEFORE engine reset.  
**Result**: ❌ Still crashes (same symptoms).

#### Attempt #2: ViewManager SafeYield/Force Hide

**Hypothesis**: `IsShown()` doesn't update immediately after manual `Hide()`.  
**Fix Applied**: Added `wx.SafeYield()` before hide loop.  
**Result**: ❌ Still crashes (Copilot confirmed).

#### Attempt #3: Comparative Analysis with hs_deckmanager

**Discovery**: Working project uses **DIFFERENT architecture pattern**.

### 🎯 Root Cause Identified

**Problem**: Panel swap during wxPython event handling causes undefined behavior.

**Technical Details**:

1. **Event Stack Corruption**:
   ```python
   # ESC key event handler (GameplayPanel._handle_esc)
   def _handle_esc(self, event):
       controller.show_abandon_game_dialog()  # ← INSIDE event handler
           → dialog.ShowModal()  # ← Nested event loop
           → if confirmed:
               → gameplay_panel.Hide()  # ← Step 1 (manual)
               → engine.reset_game()    # ← Step 2
               → return_to_menu()       # ← Step 3
                   → show_panel('menu')  # ← CRASH HERE
   ```

2. **Double Hide Issue**:
   - Step 1: Manual `gameplay_panel.Hide()` called
   - Step 3: `show_panel('menu')` loops all panels:
     ```python
     for panel_name, panel in self.panels.items():
         if panel.IsShown():  # ← Returns True even after Hide()!
             panel.Hide()      # ← SECOND Hide() on same panel
     ```
   - Second `Hide()` triggers layout corruption → frame closes

3. **wxPython Event Loop Constraints**:
   - Panel swap during event handler = **UNDEFINED BEHAVIOR**
   - Modal dialog creates nested event loop = **DANGEROUS**
   - Layout operations during event processing = **CRASH PRONE**

### 📊 Comparative Analysis: Working Pattern

#### hs_deckmanager Architecture (✅ WORKS)

```python
class MainController:
    def open_window(self, window_key, parent=None, **kwargs):
        """Opens a separate wx.Frame window."""
        if self.current_window:
            log.info("Nascondo la finestra corrente prima di aprirne una nuova.")
            self.current_window().Hide()  # ← Hides SEPARATE frame
        
        # Creates NEW frame (not panel swap)
        self.win_controller.create_window(parent=parent, key=window_key, **kwargs)
        self.win_controller.open_window(window_key, parent=parent)
```

**Key Differences**:
- ✅ Each "view" = **separate `wx.Frame`**
- ✅ Hide/Show operates on **different frames**
- ✅ NO panel swap inside same frame
- ✅ NO layout corruption possible

#### solitario Architecture (❌ BROKEN)

```python
class ViewManager:
    def show_panel(self, name: str):
        """Swaps panels inside SAME frame."""
        # Hide all panels
        for panel_name, panel in self.panels.items():
            if panel.IsShown():
                panel.Hide()  # ← Hides panels in SAME frame
        
        # Show target panel
        target_panel.Show()
```

**Key Differences**:
- ❌ All panels = **children of SAME frame**
- ❌ Hide/Show operates on **same frame's children**
- ❌ Panel swap inside same frame = **RISKY**
- ❌ Layout corruption during event handling = **CRASH**

---

## Solution Design

### ✅ Strategy: Defer UI Transitions with `wx.CallAfter()`

**Core Principle**: NEVER perform panel swap during event handling.

**Implementation**:
1. Event handler completes FIRST
2. UI transition deferred with `wx.CallAfter()`
3. Transition executes AFTER event stack clears

### 🔧 Technical Pattern

```python
# ❌ BEFORE (crashes)
def show_abandon_game_dialog(self):
    result = self.dialog_manager.show_abandon_game_prompt()
    if result:
        gameplay_panel.Hide()      # ← DURING event handling
        self.engine.reset_game()
        self.return_to_menu()      # ← Panel swap DURING event handling

# ✅ AFTER (safe)
def show_abandon_game_dialog(self):
    result = self.dialog_manager.show_abandon_game_prompt()
    if result:
        wx.CallAfter(self._safe_abandon_to_menu)  # ← DEFER to after event

def _safe_abandon_to_menu(self):
    """Executed AFTER event handler completes."""
    self.engine.reset_game()
    self._timer_expired_announced = False
    self.return_to_menu()  # ← Panel swap AFTER event stack cleared
```

### 🎯 Benefits

1. **Event Stack Safety**: Transition happens outside event handler
2. **No Double Hide**: Only `show_panel()` calls `Hide()` (once)
3. **wxPython Compliance**: Follows recommended deferred execution pattern
4. **Simpler Code**: Removes manual hide logic (Steps 1/4 eliminated)

---

## Implementation Plan

### Files to Modify

1. **`test.py`** (main entry point)
   - `show_abandon_game_dialog()` (line ~362-450)
   - `handle_game_ended()` (line ~454-521)
   - `_handle_game_over_by_timeout()` (line ~552-642)
   - Add 3 new deferred methods

2. **Impact**: ~180 lines modified, +30 lines added

### Detailed Changes

#### Change #1: show_abandon_game_dialog() - ESC Abandon

**Location**: `test.py` lines 362-452

**Current Code** (v2.0.2):
```python
def show_abandon_game_dialog(self) -> None:
    result = self.dialog_manager.show_abandon_game_prompt()
    
    if result:
        print("\n" + "="*60)
        print("ABANDON GAME: User confirmed - Starting safe transition")
        print("="*60)
        
        # ✅ STEP 1: Hide gameplay panel BEFORE engine reset
        print("→ STEP 1/4: Hiding gameplay panel...")
        if self.view_manager:
            gameplay_panel = self.view_manager.get_panel('gameplay')
            if gameplay_panel:
                try:
                    gameplay_panel.Hide()
                    print("  ✓ Gameplay panel hidden successfully")
                except Exception as e:
                    print(f"  ⚠ Error hiding gameplay panel: {e}")
                    import traceback
                    traceback.print_exc()
        
        # ✅ STEP 2: Reset engine AFTER UI hidden (safe now)
        print("→ STEP 2/4: Resetting game engine...")
        try:
            self.engine.reset_game()
            print("  ✓ Game engine reset complete")
        except Exception as e:
            print(f"  ⚠ Error resetting game engine: {e}")
        
        # ✅ STEP 3: Show menu panel (UI transition)
        print("→ STEP 3/4: Showing menu panel...")
        try:
            self.return_to_menu()
            print("  ✓ Menu panel shown successfully")
        except Exception as e:
            print(f"  ⚠ Error showing menu panel: {e}")
        
        # ✅ STEP 4: Reset timer announcement flag
        print("→ STEP 4/4: Resetting timer flag...")
        self._timer_expired_announced = False
        print("  ✓ Timer flag reset")
```

**New Code** (v2.0.3):
```python
def show_abandon_game_dialog(self) -> None:
    """Show abandon game confirmation dialog (ESC during gameplay).
    
    Defers UI transition to avoid wxPython event handling conflicts.
    
    Order of Operations (SAFE - Deferred Execution):
        1. Show confirmation dialog (modal - creates nested event loop)
        2. If confirmed:
           a. Defer transition with wx.CallAfter()
           b. Dialog closes, event handler completes
           c. wxPython calls deferred method AFTER event stack clears
           d. Safe panel swap happens outside event handling
    
    Version:
        v1.7.5: Fixed to use semantic API without parameters
        v2.0.2: Fixed operation order (Hide → Reset → Show)
        v2.0.3: FIXED - Defer transition to prevent crash during event handling
    """
    # Show confirmation dialog using SEMANTIC API
    result = self.dialog_manager.show_abandon_game_prompt()
    
    if result:
        # ✅ DEFER transition to after event handler completes
        # This prevents panel swap during event handling (wxPython crash)
        print("\n[ABANDON] User confirmed - Deferring safe transition")
        wx.CallAfter(self._safe_abandon_to_menu)
    # else: User cancelled (No or ESC), do nothing (dialog already closed)

def _safe_abandon_to_menu(self) -> None:
    """Safe deferred transition: abandon game → menu.
    
    Called by wx.CallAfter() AFTER event handler completes.
    Performs panel swap outside event handling context (safe).
    
    Order of Operations:
        1. Reset game engine (invalidates game state)
        2. Reset timer flag (prepare for next game)
        3. Show menu panel (panel swap - safe now)
    
    Note:
        NO manual Hide() needed - show_panel() handles it automatically.
        Single Hide() call prevents double-hide crash.
    
    Version:
        v2.0.3: New method - deferred execution pattern
    """
    print("\n" + "="*60)
    print("ABANDON GAME: Safe deferred transition (outside event handler)")
    print("="*60)
    
    try:
        # Reset engine first (clears game state)
        print("→ STEP 1/3: Resetting game engine...")
        self.engine.reset_game()
        print("  ✓ Engine reset complete")
        
        # Reset timer flag
        print("→ STEP 2/3: Resetting timer flag...")
        self._timer_expired_announced = False
        print("  ✓ Timer flag reset")
        
        # Show menu (panel swap - safe outside event handling)
        print("→ STEP 3/3: Showing menu panel...")
        self.return_to_menu()
        print("  ✓ Menu shown successfully")
        
        print("="*60)
        print("ABANDON GAME: Transition completed successfully")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"⚠ ERROR during deferred transition: {e}")
        import traceback
        traceback.print_exc()
```

**Changes Summary**:
- ✅ Replaced 4-step manual transition with `wx.CallAfter()` defer
- ✅ Removed manual `gameplay_panel.Hide()` (prevents double hide)
- ✅ Added new `_safe_abandon_to_menu()` deferred method
- ✅ Simplified error handling (single try/except)
- ✅ Updated docstrings with defer pattern explanation

---

#### Change #2: handle_game_ended() - Decline Rematch

**Location**: `test.py` lines 454-521

**Current Code** (v2.0.2 - decline branch):
```python
def handle_game_ended(self, wants_rematch: bool) -> None:
    self._timer_expired_announced = False
    
    if wants_rematch:
        print("→ User chose rematch - Starting new game")
        self.start_gameplay()
    else:
        print("→ User declined rematch - Starting safe transition")
        
        # ✅ STEP 1: Hide gameplay panel BEFORE engine reset
        print("→ STEP 1/4: Hiding gameplay panel...")
        if self.view_manager:
            gameplay_panel = self.view_manager.get_panel('gameplay')
            if gameplay_panel:
                try:
                    gameplay_panel.Hide()
                    print("  ✓ Gameplay hidden")
                except Exception as e:
                    print(f"  ⚠ Error hiding gameplay: {e}")
        
        # ✅ STEP 2: Reset engine AFTER UI hidden
        print("→ STEP 2/4: Resetting game engine...")
        try:
            self.engine.reset_game()
            print("  ✓ Engine reset complete")
        except Exception as e:
            print(f"  ⚠ Error resetting engine: {e}")
        
        # ✅ STEP 3: Show menu panel
        print("→ STEP 3/4: Showing menu panel...")
        try:
            self.return_to_menu()
            print("  ✓ Menu shown")
        except Exception as e:
            print(f"  ⚠ Error showing menu: {e}")
```

**New Code** (v2.0.3):
```python
def handle_game_ended(self, wants_rematch: bool) -> None:
    """Handle game end callback from GameEngine.
    
    Called after game victory or defeat (timeout excluded).
    User is prompted for rematch via dialog.
    
    Args:
        wants_rematch: True if user wants rematch, False to return to menu
    
    Order of Operations (SAFE - Deferred Execution):
        If rematch: Defer start_gameplay() (avoid event handling conflict)
        If decline: Defer return_to_menu() (avoid panel swap during event)
    
    Version:
        v2.0.2: Fixed operation order for decline rematch path
        v2.0.3: FIXED - Defer both branches to prevent crash
    """
    print("\n" + "="*60)
    print(f"CALLBACK: Game ended - Rematch requested: {wants_rematch}")
    print("="*60)
    
    self._timer_expired_announced = False
    
    if wants_rematch:
        # ✅ DEFER rematch (avoid event handling conflict)
        print("→ User chose rematch - Deferring new game start")
        wx.CallAfter(self.start_gameplay)
    else:
        # ✅ DEFER decline (avoid panel swap during event)
        print("→ User declined rematch - Deferring safe transition")
        wx.CallAfter(self._safe_decline_to_menu)

def _safe_decline_to_menu(self) -> None:
    """Safe deferred transition: decline rematch → menu.
    
    Called by wx.CallAfter() AFTER game end callback completes.
    
    Version:
        v2.0.3: New method - deferred execution pattern
    """
    print("\n[DECLINE] Safe deferred transition to menu")
    
    try:
        print("→ Resetting game engine...")
        self.engine.reset_game()
        print("  ✓ Engine reset")
        
        print("→ Showing menu panel...")
        self.return_to_menu()
        print("  ✓ Menu shown\n")
        
    except Exception as e:
        print(f"⚠ ERROR during decline transition: {e}")
        import traceback
        traceback.print_exc()
```

**Changes Summary**:
- ✅ Replaced manual transition with `wx.CallAfter()` defer
- ✅ Added `_safe_decline_to_menu()` deferred method
- ✅ Also defer rematch path (`start_gameplay()`) for consistency
- ✅ Simplified logging (removed 4-step verbose output)

---

#### Change #3: _handle_game_over_by_timeout() - Strict Mode Timeout

**Location**: `test.py` lines 552-642

**Current Code** (v2.0.2):
```python
def _handle_game_over_by_timeout(self) -> None:
    # ... (calculate timeout message + stats) ...
    
    # ✅ Safe transition: Hide → Reset → Show pattern
    print("\n" + "="*60)
    print("TIMEOUT DEFEAT: Starting safe transition to menu")
    print("="*60)
    
    # ✅ STEP 1: Hide gameplay panel BEFORE engine reset
    print("→ STEP 1/4: Hiding gameplay panel...")
    if self.view_manager:
        gameplay_panel = self.view_manager.get_panel('gameplay')
        if gameplay_panel:
            try:
                gameplay_panel.Hide()
                print("  ✓ Gameplay panel hidden")
            except Exception as e:
                print(f"  ⚠ Error hiding gameplay: {e}")
    
    # ... (similar 4-step pattern) ...
```

**New Code** (v2.0.3):
```python
def _handle_game_over_by_timeout(self) -> None:
    """Handle game over by timeout in STRICT mode.
    
    Order of Operations (SAFE - Deferred Execution):
        1. Calculate timeout message + statistics
        2. Show defeat message via TTS
        3. Defer transition with wx.CallAfter()
        4. Timer check completes, event stack clears
        5. Deferred method executes (safe panel swap)
    
    Version:
        v2.0.2: Fixed operation order to prevent crash (Hide → Reset → Show)
        v2.0.3: FIXED - Defer transition to prevent crash during timer check
    """
    max_time = self.settings.max_time_game
    elapsed = self.engine.service.get_elapsed_time()
    
    minutes_max = max_time // 60
    seconds_max = max_time % 60
    minutes_elapsed = int(elapsed) // 60
    seconds_elapsed = int(elapsed) % 60
    
    defeat_msg = "⏰ TEMPO SCADUTO!\n\n"
    defeat_msg += f"Tempo limite: {minutes_max} minuti"
    if seconds_max > 0:
        defeat_msg += f" e {seconds_max} secondi"
    defeat_msg += ".\n"
    defeat_msg += f"Tempo trascorso: {minutes_elapsed} minuti"
    if seconds_elapsed > 0:
        defeat_msg += f" e {seconds_elapsed} secondi"
    defeat_msg += ".\n\n"
    
    report, _ = self.engine.service.get_game_report()
    defeat_msg += "--- STATISTICHE FINALI ---\n"
    defeat_msg += report
    
    print(defeat_msg)
    
    if self.screen_reader:
        self.screen_reader.tts.speak(defeat_msg, interrupt=True)
        wx.MilliSleep(2000)
    
    # ✅ DEFER transition to after timer check completes
    print("\n[TIMEOUT] Deferring safe transition to menu")
    wx.CallAfter(self._safe_timeout_to_menu)

def _safe_timeout_to_menu(self) -> None:
    """Safe deferred transition: timeout defeat → menu.
    
    Called by wx.CallAfter() AFTER timer check completes.
    
    Version:
        v2.0.3: New method - deferred execution pattern
    """
    print("\n" + "="*60)
    print("TIMEOUT DEFEAT: Safe deferred transition (outside timer check)")
    print("="*60)
    
    try:
        print("→ Resetting game engine...")
        self.engine.reset_game()
        print("  ✓ Engine reset")
        
        print("→ Resetting timer flag...")
        self._timer_expired_announced = False
        print("  ✓ Timer flag reset")
        
        print("→ Showing menu panel...")
        self.return_to_menu()
        print("  ✓ Menu shown")
        
        print("="*60)
        print("TIMEOUT DEFEAT: Transition completed")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"⚠ ERROR during timeout transition: {e}")
        import traceback
        traceback.print_exc()
```

**Changes Summary**:
- ✅ Replaced 4-step manual transition with `wx.CallAfter()` defer
- ✅ Added `_safe_timeout_to_menu()` deferred method
- ✅ Kept defeat message calculation (unchanged)
- ✅ Simplified error handling

---

#### Change #4: return_to_menu() - Simplify Diagnostics

**Location**: `test.py` lines 196-271

**Current Code** (v2.0.2):
```python
def return_to_menu(self) -> None:
    print("\n" + "="*60)
    print("RETURN_TO_MENU: Start UI transition")
    print("="*60)
    
    # ... (extensive diagnostic logging - 50+ lines) ...
    
    shown = self.view_manager.show_panel('menu')
    # ... (more diagnostics) ...
```

**New Code** (v2.0.3):
```python
def return_to_menu(self) -> None:
    """Return from gameplay to menu (show MenuPanel only).
    
    IMPORTANT: This method handles ONLY UI transition (show/hide panels).
    Engine reset MUST be done BEFORE calling this method.
    
    Caller Pattern (SAFE - Deferred Execution):
        1. Defer transition with wx.CallAfter(deferred_method)
        2. Event handler completes
        3. Deferred method calls this (outside event stack)
        4. Panel swap happens safely
    
    Example:
        >>> # ✅ CORRECT - Deferred execution
        >>> def show_abandon_game_dialog(self):
        ...     result = self.dialog_manager.show_abandon_game_prompt()
        ...     if result:
        ...         wx.CallAfter(self._safe_abandon_to_menu)
        >>> 
        >>> def _safe_abandon_to_menu(self):
        ...     self.engine.reset_game()
        ...     self.return_to_menu()  # Safe - outside event handler
        >>> 
        >>> # ❌ WRONG - During event handling (CRASHES)
        >>> def show_abandon_game_dialog(self):
        ...     result = self.dialog_manager.show_abandon_game_prompt()
        ...     if result:
        ...         self.return_to_menu()  # CRASH - inside event handler
    
    Version:
        v2.0.2: Added diagnostics + clarified caller responsibility
        v2.0.3: FIXED - Simplified (diagnostics removed, defer pattern documented)
    """
    if not self.view_manager:
        print("⚠ ViewManager not initialized - Cannot show menu")
        return
    
    # Perform panel swap (safe outside event handling)
    self.view_manager.show_panel('menu')
    
    # Update application state flag
    self.is_menu_open = True
    
    # Announce return via TTS
    if self.screen_reader:
        self.screen_reader.tts.speak(
            "Ritorno al menu di gioco.",
            interrupt=True
        )
```

**Changes Summary**:
- ✅ Removed extensive diagnostic logging (~50 lines)
- ✅ Simplified to essential operations only
- ✅ Updated docstring with defer pattern examples
- ✅ Kept TTS announcement (user feedback)

---

### Summary of Changes

| Method | Lines Changed | New Methods | Impact |
|--------|--------------|-------------|---------|
| `show_abandon_game_dialog()` | ~90 → 20 | `_safe_abandon_to_menu()` (+20) | Simplified |
| `handle_game_ended()` | ~70 → 25 | `_safe_decline_to_menu()` (+15) | Simplified |
| `_handle_game_over_by_timeout()` | ~90 → 25 | `_safe_timeout_to_menu()` (+20) | Simplified |
| `return_to_menu()` | ~75 → 20 | None | Simplified |
| **Total** | **~325 → 90** | **+55 new** | **-180 lines** |

**Net Result**: -180 lines removed, +55 lines added = **-125 lines total**  
**Code Quality**: Simpler, safer, more maintainable

---

## Testing Checklist

### Automated Tests (Manual Verification Required)

#### Test #1: ESC Abandon Game
**Preconditions**:
- Game in progress (cards dealt)
- Timer running

**Steps**:
1. Press ESC during gameplay
2. Confirm abandon in dialog (click "Sì")

**Expected Results**:
- ✅ Game resets (cards cleared)
- ✅ Timer stops
- ✅ Menu panel shows
- ✅ TTS announces "Ritorno al menu di gioco"
- ✅ **NO crash, NO app close**

**Log Verification**:
```
[ABANDON] User confirmed - Deferring safe transition
ABANDON GAME: Safe deferred transition (outside event handler)
→ STEP 1/3: Resetting game engine...
  ✓ Engine reset complete
→ STEP 2/3: Resetting timer flag...
  ✓ Timer flag reset
→ STEP 3/3: Showing menu panel...
  ✓ Menu shown successfully
ABANDON GAME: Transition completed successfully
```

---

#### Test #2: Game Victory - Decline Rematch
**Preconditions**:
- Game in progress
- Complete game successfully (move all cards to foundations)

**Steps**:
1. Win game (trigger victory dialog)
2. Click "No" in rematch prompt

**Expected Results**:
- ✅ Victory message + stats shown
- ✅ Game resets
- ✅ Menu panel shows
- ✅ TTS announces return to menu
- ✅ **NO crash, NO app close**

**Log Verification**:
```
CALLBACK: Game ended - Rematch requested: False
→ User declined rematch - Deferring safe transition
[DECLINE] Safe deferred transition to menu
→ Resetting game engine...
  ✓ Engine reset
→ Showing menu panel...
  ✓ Menu shown
```

---

#### Test #3: Game Victory - Accept Rematch
**Preconditions**:
- Game in progress
- Complete game successfully

**Steps**:
1. Win game
2. Click "Sì" in rematch prompt

**Expected Results**:
- ✅ New game starts immediately
- ✅ Gameplay panel stays visible
- ✅ Cards dealt for new game
- ✅ Timer resets
- ✅ **NO crash, NO app close**

**Log Verification**:
```
CALLBACK: Game ended - Rematch requested: True
→ User chose rematch - Deferring new game start
(new game logs...)
```

---

#### Test #4: Timeout Defeat (Strict Mode)
**Preconditions**:
- Strict timer mode enabled (`settings.timer_strict_mode = True`)
- Set short timer (e.g., `settings.max_time_game = 60` seconds)
- Game in progress

**Steps**:
1. Wait for timer to expire (do NOT complete game)
2. Timeout triggers automatic defeat

**Expected Results**:
- ✅ Defeat message + stats shown via TTS
- ✅ Game resets automatically
- ✅ Menu panel shows
- ✅ **NO crash, NO app close**

**Log Verification**:
```
⏰ TEMPO SCADUTO!
(stats output...)
[TIMEOUT] Deferring safe transition to menu
TIMEOUT DEFEAT: Safe deferred transition (outside timer check)
→ Resetting game engine...
  ✓ Engine reset
→ Showing menu panel...
  ✓ Menu shown
```

---

### Regression Tests

#### RT #1: Menu Navigation
**Steps**:
1. Launch app (menu shows)
2. Use arrow keys to navigate menu
3. Press ENTER on each option

**Expected**: ✅ All menu options work (Nuova Partita, Opzioni, Esci)

---

#### RT #2: Gameplay Commands
**Steps**:
1. Start new game
2. Test all keyboard commands:
   - Arrow keys (navigate cards)
   - ENTER (move card)
   - SPACE (flip waste)
   - D (draw from stock)
   - H (help)
   - O (announce game state)

**Expected**: ✅ All commands work correctly

---

#### RT #3: Options Window
**Steps**:
1. Open Opzioni from menu
2. Modify settings
3. Save with "Salva" button
4. Close with ESC (test smart ESC)

**Expected**: ✅ Settings save correctly, smart ESC works

---

#### RT #4: Exit Flows
**Steps**:
1. Test menu ESC → Exit dialog → Confirm
2. Test menu "Esci" button → Exit dialog → Confirm
3. Test ALT+F4 → Exit dialog → Confirm

**Expected**: ✅ All exit methods work, no crashes

---

### Stress Tests

#### ST #1: Rapid ESC Spam
**Steps**:
1. Start game
2. Press ESC 10 times rapidly
3. Confirm all dialogs quickly

**Expected**: ✅ No crashes, proper cleanup each time

---

#### ST #2: Panel Swap Loop
**Steps**:
1. Menu → Nuova Partita → ESC confirm → Menu (repeat 20x)

**Expected**: ✅ No memory leaks, no crashes, consistent behavior

---

## References

### Related Issues
- ❌ Issue #1: App closes on ESC abandon (v2.0.0 - v2.0.2)
- ✅ Fix #1: Hide → Reset → Show pattern (v2.0.2) - **INCOMPLETE**
- ✅ Fix #2: wx.CallAfter() defer pattern (v2.0.3) - **THIS FIX**

### Documentation
- [wxPython Best Practices: Deferred Execution](https://docs.wxpython.org/wx.CallAfter.html)
- [wxPython Panel Management Guide](https://wiki.wxpython.org/WorkingWithPanels)
- `docs/FIX_PANEL_LIFECYCLE_CRASH.md` (v2.0.2 - superseded by this doc)

### Code References
- Working pattern: `hs_deckmanager/scr/controller.py` (lines 550-570)
- Affected file: `test.py` (lines 196-642)
- Panel manager: `src/infrastructure/ui/view_manager.py` (lines 131-164)

### wxPython API
- `wx.CallAfter(callable, *args, **kwargs)` - Defer execution
- `wx.Panel.Hide()` - Hide panel (layout operation)
- `wx.Panel.Show()` - Show panel (layout operation)
- `wx.Panel.IsShown()` - Check visibility state

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v2.0.2 | 2026-02-13 | Copilot | Hide → Reset → Show pattern (incomplete fix) |
| v2.0.3 | 2026-02-14 | Manual + Copilot | wx.CallAfter() defer pattern (complete fix) |

---

## Implementation Notes for Copilot

### Critical Requirements

1. **Preserve All Existing Functionality**:
   - DO NOT change menu navigation logic
   - DO NOT change gameplay command handling
   - DO NOT change dialog behavior (except defer pattern)
   - DO NOT change TTS announcements

2. **Apply Pattern Consistently**:
   - ALL panel transitions MUST use `wx.CallAfter()`
   - NO panel swap during event handling
   - NO manual `Hide()` before `show_panel()`

3. **Testing Mandatory**:
   - Run ALL 4 automated tests
   - Run ALL 4 regression tests
   - Run BOTH stress tests
   - Fix ANY failures before marking complete

4. **Documentation Updates**:
   - Update CHANGELOG.md with v2.0.3 release notes
   - Mark this document as COMPLETED in filename
   - Update version string in test.py docstring

### Expected Commit Structure

```
fix(ui): prevent panel swap crash with deferred execution pattern

Replace synchronous panel transitions with wx.CallAfter() deferred
execution to prevent crashes during event handling.

## Root Cause
Panel swap during wxPython event handling causes undefined behavior:
- Modal dialogs create nested event loops
- Panel.Hide() during event processing triggers layout corruption
- Second Hide() call on already-hidden panel closes frame

## Solution
Defer all UI transitions with wx.CallAfter():
- Event handler completes first
- Transition executes after event stack clears
- No panel swap during event handling

## Changes
- show_abandon_game_dialog(): Added wx.CallAfter() defer
- handle_game_ended(): Added wx.CallAfter() for both branches
- _handle_game_over_by_timeout(): Added wx.CallAfter() defer
- return_to_menu(): Simplified (removed diagnostics)
- New methods: _safe_abandon_to_menu(), _safe_decline_to_menu(), _safe_timeout_to_menu()

## Testing
✅ ESC abandon game → No crash → Menu shown
✅ Decline rematch → No crash → Menu shown
✅ Timeout strict mode → No crash → Menu shown
✅ All regression tests pass

## Impact
BREAKING: None (internal fix only)
API: No changes to public interfaces
Behavior: Same UX, crash-free now
Performance: Negligible (deferred execution overhead minimal)

Version: v2.0.3 (critical bugfix)
Closes: Panel swap crash during event handling

Co-authored-by: Nemex81 <68394029+Nemex81@users.noreply.github.com>
```

---

## Success Criteria

- ✅ All 4 automated tests pass
- ✅ All 4 regression tests pass
- ✅ Both stress tests pass
- ✅ No crashes when pressing ESC during gameplay
- ✅ No crashes when declining rematch
- ✅ No crashes on timeout defeat
- ✅ User experience unchanged (same behavior, no crashes)
- ✅ Code reduced by ~125 lines (simpler, more maintainable)

---

**END OF DOCUMENT**
