# FIX: wx.CallAfter MainLoop Assertion Error

**Status**: 🔴 CRITICAL BUG - Deferred transitions fail with assertion error  
**Branch**: `copilot/remove-pygame-migrate-wxpython`  
**Affected Version**: v2.0.4  
**Priority**: P0 (Blocks release)  
**Created**: 2026-02-14  
**Supersedes**: `FIX_PANEL_SWAP_CRASH_DURING_EVENT_HANDLING.md` (partial fix)

---

## 📋 Table of Contents

1. [Problem Summary](#problem-summary)
2. [Root Cause Analysis](#root-cause-analysis)
3. [Solution Design](#solution-design)
4. [Implementation Plan](#implementation-plan)
5. [Testing Requirements](#testing-requirements)
6. [References](#references)

---

## Problem Summary

### Current Behavior (❌ BROKEN)

**Symptom**: App no longer crashes, but gets **stuck** on gameplay panel after confirming abandon.

**Error Log**:
```
✓ Menu visualizzato
→ User confirmed abandon - Scheduling deferred transition...
Traceback (most recent call last):
  File "test.py", line 371, in show_abandon_game_dialog
    wx.CallAfter(self._safe_abandon_to_menu)
  File "wx/core.py", line 3422, in CallAfter
    assert app is not None, 'No wx.App created yet'
AssertionError: No wx.App created yet
```

**Repeated 3 times** (user pressing ESC multiple times trying to unstick).

### Expected Behavior (✅ CORRECT)

After ESC → Confirm abandon:
1. Game resets
2. Gameplay panel hides
3. Menu panel shows
4. User can navigate menu again

### Impact

- **User Experience**: App appears frozen (stuck on gameplay screen)
- **Screen Reader**: No announcement (user confused)
- **Workaround**: None (must kill app with ALT+F4)
- **Regression**: v2.0.3 crashes → v2.0.4 hangs (WORSE!)

---

## Root Cause Analysis

### Investigation Path

#### Attempt #1: Deferred Execution with `wx.CallAfter()` (v2.0.4)

**Hypothesis**: Panel swap during event handling causes crashes.  
**Fix Applied**: Replaced direct calls with `wx.CallAfter()` defer pattern.  
**Result**: ❌ No crash, but **AssertionError** instead!

**Error Analysis**:
```python
# wx/core.py line 3422
def CallAfter(func, *args, **kwargs):
    app = wx.App.Get()  # ← Returns None!
    assert app is not None, 'No wx.App created yet'  # ← FAILS HERE
    # ...
```

**Why `wx.App.Get()` returns `None`**:

Looking at test.py initialization sequence:
```python
def run(self):
    print("Avvio wxPython MainLoop()...")
    
    def on_init(app):
        self.frame = SolitarioFrame(...)
        self.dialog_manager = SolitarioDialogManager(...)
        self.view_manager = ViewManager(self.frame)
        # ... panels creation ...
        self.frame.start_timer(1000)
    
    self.app = SolitarioWxApp(on_init_complete=on_init)  # ← App created
    self.app.MainLoop()  # ← MainLoop blocks here
```

**Timeline**:
```
T=0ms:   self.app = SolitarioWxApp(...)  ← wx.App created
T=10ms:  on_init() callback executes      ← Frame + panels setup
T=50ms:  MainLoop() starts processing     ← Event loop ACTIVE
T=100ms: User presses ESC in gameplay
T=101ms: show_abandon_game_dialog() called
T=102ms: wx.CallAfter() executed
         ↓
         wx.App.Get() returns None? ← WHY?!
```

**Answer**: `wx.App.Get()` returns `None` if called **before** `wx.App.__init__()` **completes internally**.

wxPython's `CallAfter()` implementation:
```python
# Simplified wx.CallAfter internals
def CallAfter(func, *args, **kwargs):
    app = wx.App.Get()  # Gets THE CURRENT wx.App instance
    assert app is not None  # FAILS if no app registered yet
    app.CallLater(0, func, *args, **kwargs)  # Delegates to CallLater
```

**Problem**: `wx.App.Get()` relies on C++ side registration that may not be complete during early init phase, even though Python-side `self.app` exists!

### 🎯 Root Cause Identified

**`wx.CallAfter()` is unreliable during app initialization/transition phases.**

Even though `self.app` Python object exists, wxPython's C++ side may not have registered it globally yet, causing `wx.App.Get()` to return `None`.

**Solution**: Use `wx.CallLater(milliseconds, ...)` directly, which:
1. Doesn't rely on `wx.App.Get()` (uses timer system)
2. Works immediately after app creation
3. Still provides deferred execution (after event handler completes)
4. Has explicit delay (10ms = ~1 frame @ 60fps = imperceptible)

---

## Solution Design

### ✅ Strategy: Replace `wx.CallAfter()` with `wx.CallLater(10, ...)`

**Core Principle**: Use timer-based deferral instead of event-queue deferral.

### Technical Comparison

| Aspect | `wx.CallAfter()` | `wx.CallLater(10, ...)` |
|--------|------------------|-------------------------|
| **Implementation** | Event queue append | Timer-based scheduler |
| **Dependency** | `wx.App.Get()` must work | No `wx.App.Get()` needed |
| **Timing** | "As soon as possible" | After 10ms minimum |
| **Reliability** | ❌ Fails during init | ✅ Works always |
| **User Perception** | Instant (0ms) | Instant (~1 frame) |
| **Complexity** | Simple API | Simple API + delay |

### Why 10ms Delay?

```python
10ms = 1/100 second
     = ~0.6 frames @ 60fps
     = ~0.3 frames @ 30fps
     = IMPERCEPTIBLE to human perception (<16.67ms = 1 frame)
```

**Benefits of 10ms**:
1. Guarantees `wx.App` fully initialized
2. Guarantees `MainLoop()` active
3. Guarantees event handler completed
4. Still feels instant to user
5. Screen reader announcement seamless

### Implementation Pattern

```python
# ❌ BEFORE (v2.0.4 - broken)
def show_abandon_game_dialog(self):
    result = self.dialog_manager.show_abandon_game_prompt()
    if result:
        wx.CallAfter(self._safe_abandon_to_menu)  # ← FAILS: wx.App.Get() → None

# ✅ AFTER (v2.0.5 - fixed)
def show_abandon_game_dialog(self):
    result = self.dialog_manager.show_abandon_game_prompt()
    if result:
        wx.CallLater(10, self._safe_abandon_to_menu)  # ← WORKS: Timer-based, no wx.App.Get()
```

**Key Changes**:
- Replace `wx.CallAfter(func)` → `wx.CallLater(10, func)`
- Add 10ms delay parameter (first argument)
- Keep all other code unchanged

---

## Implementation Plan

### Files to Modify

**ONLY ONE FILE**: `test.py`

**Changes**: 4 lines (search/replace)

### Detailed Changes

#### Change #1: ESC Abandon Game

**Location**: `test.py` line ~371

**Current Code** (v2.0.4):
```python
def show_abandon_game_dialog(self) -> None:
    """Show abandon game confirmation dialog (called from GameplayPanel ESC handler).
    
    # ... (docstring omitted for brevity) ...
    """
    result = self.dialog_manager.show_abandon_game_prompt()
    
    if result:
        print("→ User confirmed abandon - Scheduling deferred transition...")
        wx.CallAfter(self._safe_abandon_to_menu)  # ← LINE TO CHANGE
```

**New Code** (v2.0.5):
```python
def show_abandon_game_dialog(self) -> None:
    """Show abandon game confirmation dialog (called from GameplayPanel ESC handler).
    
    # ... (docstring unchanged) ...
    """
    result = self.dialog_manager.show_abandon_game_prompt()
    
    if result:
        print("→ User confirmed abandon - Scheduling deferred transition...")
        wx.CallLater(10, self._safe_abandon_to_menu)  # ← CHANGED: CallAfter → CallLater(10)
```

**Change Summary**:
- Line ~371: `wx.CallAfter(` → `wx.CallLater(10, `
- Docstring: NO CHANGES (defer pattern explanation still valid)
- Logic: NO CHANGES (same deferred execution, just different API)

---

#### Change #2: Victory - Rematch Branch

**Location**: `test.py` line ~460

**Current Code** (v2.0.4):
```python
def handle_game_ended(self, wants_rematch: bool) -> None:
    """Handle game end callback from GameEngine.
    
    # ... (docstring omitted) ...
    """
    print(f"\n→ Game ended callback - Rematch: {wants_rematch}")
    self._timer_expired_announced = False
    
    if wants_rematch:
        print("→ Scheduling deferred rematch...")
        wx.CallAfter(self.start_gameplay)  # ← LINE TO CHANGE
    else:
        print("→ Scheduling deferred decline transition...")
        wx.CallAfter(self._safe_decline_to_menu)  # ← LINE TO CHANGE
```

**New Code** (v2.0.5):
```python
def handle_game_ended(self, wants_rematch: bool) -> None:
    """Handle game end callback from GameEngine.
    
    # ... (docstring unchanged) ...
    """
    print(f"\n→ Game ended callback - Rematch: {wants_rematch}")
    self._timer_expired_announced = False
    
    if wants_rematch:
        print("→ Scheduling deferred rematch...")
        wx.CallLater(10, self.start_gameplay)  # ← CHANGED: CallAfter → CallLater(10)
    else:
        print("→ Scheduling deferred decline transition...")
        wx.CallLater(10, self._safe_decline_to_menu)  # ← CHANGED: CallAfter → CallLater(10)
```

**Change Summary**:
- Line ~460: `wx.CallAfter(self.start_gameplay)` → `wx.CallLater(10, self.start_gameplay)`
- Line ~463: `wx.CallAfter(self._safe_decline_to_menu)` → `wx.CallLater(10, self._safe_decline_to_menu)`
- Docstring: NO CHANGES
- Logic: NO CHANGES

---

#### Change #3: Timeout Defeat (Strict Mode)

**Location**: `test.py` line ~600

**Current Code** (v2.0.4):
```python
def _handle_game_over_by_timeout(self) -> None:
    """Handle game over by timeout in STRICT mode.
    
    # ... (docstring omitted) ...
    """
    # ... (defeat message calculation - ~40 lines) ...
    
    print(defeat_msg)
    
    if self.screen_reader:
        self.screen_reader.tts.speak(defeat_msg, interrupt=True)
        wx.MilliSleep(2000)
    
    print("→ Timeout defeat - Scheduling deferred transition...")
    wx.CallAfter(self._safe_timeout_to_menu)  # ← LINE TO CHANGE
```

**New Code** (v2.0.5):
```python
def _handle_game_over_by_timeout(self) -> None:
    """Handle game over by timeout in STRICT mode.
    
    # ... (docstring unchanged) ...
    """
    # ... (defeat message calculation - unchanged) ...
    
    print(defeat_msg)
    
    if self.screen_reader:
        self.screen_reader.tts.speak(defeat_msg, interrupt=True)
        wx.MilliSleep(2000)
    
    print("→ Timeout defeat - Scheduling deferred transition...")
    wx.CallLater(10, self._safe_timeout_to_menu)  # ← CHANGED: CallAfter → CallLater(10)
```

**Change Summary**:
- Line ~600: `wx.CallAfter(` → `wx.CallLater(10, `
- Docstring: NO CHANGES
- Logic: NO CHANGES

---

### Summary of All Changes

| Method | Line | Change | Status |
|--------|------|--------|--------|
| `show_abandon_game_dialog()` | ~371 | `CallAfter` → `CallLater(10,` | Required |
| `handle_game_ended()` (rematch) | ~460 | `CallAfter` → `CallLater(10,` | Required |
| `handle_game_ended()` (decline) | ~463 | `CallAfter` → `CallLater(10,` | Required |
| `_handle_game_over_by_timeout()` | ~600 | `CallAfter` → `CallLater(10,` | Required |

**Total Changes**: 4 lines modified  
**Files Modified**: 1 (`test.py`)  
**Lines Added**: 0  
**Lines Removed**: 0  
**Lines Changed**: 4  

**Net Impact**: Minimal (search/replace operation)

---

## Testing Requirements

### Critical Tests (4 scenarios)

#### Test #1: ESC Abandon Game ✅

**Steps**:
1. Launch app → Start new game
2. Wait for cards dealt (game active)
3. Press ESC
4. Confirm abandon (click "Sì" button)

**Expected Results**:
- ✅ Dialog shows "Vuoi abbandonare la partita?"
- ✅ After confirm: game resets (cards cleared)
- ✅ After confirm: timer stops
- ✅ After confirm: menu panel shows (~10-20ms delay)
- ✅ TTS announces "Ritorno al menu di gioco"
- ✅ User can navigate menu with arrows
- ✅ **NO crash**
- ✅ **NO hang/freeze**
- ✅ **NO AssertionError in log**

**Log Verification**:
```
→ User confirmed abandon - Scheduling deferred transition...
→ Executing deferred abandon transition...
  → Hiding gameplay panel...
  → Resetting game engine...
  → Returning to menu...
→ Abandon transition completed
```

**Failure Signs**:
- ❌ AssertionError in log
- ❌ App stuck on gameplay screen
- ❌ Menu not showing after 1 second

---

#### Test #2: Victory - Decline Rematch ✅

**Steps**:
1. Start new game
2. Complete game successfully (all cards to foundations)
3. Victory dialog shows
4. Click "No" (decline rematch)

**Expected Results**:
- ✅ Victory message + stats shown
- ✅ After decline: game resets
- ✅ After decline: menu shows (~10-20ms delay)
- ✅ TTS announces return to menu
- ✅ **NO crash, NO hang**

**Log Verification**:
```
→ Game ended callback - Rematch: False
→ Scheduling deferred decline transition...
→ Executing deferred decline transition...
→ Decline transition completed
```

---

#### Test #3: Victory - Accept Rematch ✅

**Steps**:
1. Win game
2. Click "Sì" (accept rematch)

**Expected Results**:
- ✅ New game starts immediately (~10-20ms delay)
- ✅ Gameplay panel stays visible
- ✅ Cards dealt for new game
- ✅ Timer resets
- ✅ **NO crash, NO hang**

**Log Verification**:
```
→ Game ended callback - Rematch: True
→ Scheduling deferred rematch...
(new game initialization logs...)
```

---

#### Test #4: Timeout Defeat (Strict Mode) ✅

**Preconditions**:
- Enable strict timer: `settings.timer_strict_mode = True`
- Set short timer: `settings.max_time_game = 60` (1 minute)

**Steps**:
1. Start new game
2. Wait for timeout (do NOT complete game)
3. Timeout triggers automatic defeat

**Expected Results**:
- ✅ Defeat message + stats announced via TTS
- ✅ After timeout: game resets automatically
- ✅ After timeout: menu shows (~10-20ms delay)
- ✅ **NO crash, NO hang**

**Log Verification**:
```
⏰ TEMPO SCADUTO!
(stats output...)
→ Timeout defeat - Scheduling deferred transition...
→ Executing deferred timeout transition...
→ Timeout transition completed
```

---

### Regression Tests (4 scenarios)

#### RT #1: Menu Navigation ✅
- Launch app → Menu shows
- Arrow keys navigate correctly
- ENTER activates options
- ESC shows exit dialog

#### RT #2: Gameplay Commands ✅
- All 80+ keyboard commands work
- H (help), O (state), 1-7 (piles), arrows, ENTER, SPACE, D

#### RT #3: Options Window ✅
- Open options from menu
- Modify settings
- Save/Cancel works correctly
- Smart ESC works

#### RT #4: Exit Flows ✅
- Menu ESC → Exit dialog → Confirm
- Menu "Esci" button → Exit dialog → Confirm
- ALT+F4 → Exit dialog → Confirm

---

### Stress Tests (2 scenarios)

#### ST #1: Rapid ESC Spam ✅
- Start game → Press ESC 10x rapidly → Confirm all
- Expected: No crashes, no hangs, proper cleanup each time

#### ST #2: Panel Swap Loop ✅
- Menu → Nuova Partita → ESC → Menu (repeat 20x)
- Expected: No crashes after 20 iterations, consistent behavior

---

## Success Criteria

### Code Quality
- ✅ 4 lines changed (search/replace)
- ✅ No new methods added
- ✅ No docstrings changed
- ✅ No logic changed (only API swap)
- ✅ Clean diff (minimal changes)

### Testing
- ✅ All 4 critical tests pass
- ✅ All 4 regression tests pass
- ✅ Both stress tests pass
- ✅ No AssertionError in logs
- ✅ No hangs/freezes

### User Experience
- ✅ ESC abandon works instantly (~10ms imperceptible delay)
- ✅ Victory flows work seamlessly
- ✅ Timeout defeat works automatically
- ✅ Screen reader announcements unchanged
- ✅ Keyboard navigation unchanged

### Documentation
- ✅ CHANGELOG.md updated with v2.0.5
- ✅ Version string updated in test.py
- ✅ This document marked as COMPLETED

---

## Implementation Instructions for Copilot

### Step-by-Step Process

#### Step 1: Locate Lines to Change

Search for these 4 patterns in `test.py`:

```python
# Pattern 1 (line ~371)
wx.CallAfter(self._safe_abandon_to_menu)

# Pattern 2 (line ~460)
wx.CallAfter(self.start_gameplay)

# Pattern 3 (line ~463)
wx.CallAfter(self._safe_decline_to_menu)

# Pattern 4 (line ~600)
wx.CallAfter(self._safe_timeout_to_menu)
```

#### Step 2: Apply Changes

For each pattern, replace `wx.CallAfter(` with `wx.CallLater(10, `:

```python
# BEFORE
wx.CallAfter(self._safe_abandon_to_menu)

# AFTER
wx.CallLater(10, self._safe_abandon_to_menu)
```

**CRITICAL**: Add `10, ` as first argument (10 milliseconds delay).

#### Step 3: Verify Changes

After applying changes, verify:

1. **Syntax Check**:
   ```bash
   python -m py_compile test.py
   ```
   Should output nothing (no syntax errors).

2. **Diff Check**:
   ```bash
   git diff test.py
   ```
   Should show EXACTLY 4 lines changed, each with `CallAfter` → `CallLater(10,`.

3. **No Unintended Changes**:
   - No docstrings modified
   - No print statements modified
   - No logic modified
   - ONLY `CallAfter(` → `CallLater(10,` changes

#### Step 4: Test

Run all 4 critical tests:

```bash
# Test 1: ESC abandon
python test.py
# In-app: Start game → ESC → Confirm → Verify menu shows

# Test 2: Decline rematch
# In-app: Win game → No → Verify menu shows

# Test 3: Accept rematch
# In-app: Win game → Sì → Verify new game starts

# Test 4: Timeout (if strict mode enabled)
# In-app: Wait for timeout → Verify menu shows
```

All tests must pass with NO AssertionError in logs.

#### Step 5: Update Documentation

1. **CHANGELOG.md**:
   ```markdown
   ## [2.0.5] - 2026-02-14
   
   ### Fixed
   - **CRITICAL**: wx.CallAfter AssertionError causing app hang on panel transitions
     - Root cause: wx.App.Get() returns None during early init/transition phases
     - Solution: Replaced wx.CallAfter() with wx.CallLater(10, ...) for reliable deferral
     - Impact: All deferred transitions (ESC abandon, rematch, timeout) now work correctly
     - User experience: Seamless (10ms delay imperceptible)
     - Files: test.py (4 lines changed)
     - Regression: v2.0.4 hang → v2.0.5 fixed
   ```

2. **Version String** (test.py docstring):
   ```python
   """wxPython-based entry point for Solitario Classico Accessibile.
   
   # ... (existing docstring) ...
   
   Version: v2.0.5 (CRITICAL bugfix - wx.CallAfter assertion)
   """
   ```

3. **This Document** (filename):
   ```bash
   # After successful implementation
   git mv docs/FIX_WX_CALLAFTER_MAINLOOP_ASSERTION.md \
         docs/completed-FIX_WX_CALLAFTER_MAINLOOP_ASSERTION.md
   ```

#### Step 6: Commit

```bash
git add test.py CHANGELOG.md
git commit -m "fix(ui): replace wx.CallAfter with wx.CallLater to prevent assertion error

wx.CallAfter() fails with 'No wx.App created yet' assertion during
app initialization/transition phases, even though self.app exists.

Root Cause:
- wx.App.Get() relies on C++ registration not complete during init
- CallAfter depends on wx.App.Get() succeeding
- Result: AssertionError → app hangs on panel transitions

Solution:
- Replace wx.CallAfter(func) with wx.CallLater(10, func)
- CallLater uses timer system (no wx.App.Get() dependency)
- 10ms delay imperceptible (~1 frame @ 60fps)
- Reliable deferral in all app lifecycle phases

Changes:
- show_abandon_game_dialog(): CallAfter → CallLater(10)
- handle_game_ended() (both branches): CallAfter → CallLater(10)
- _handle_game_over_by_timeout(): CallAfter → CallLater(10)

Testing:
✅ ESC abandon → Menu shows (no hang)
✅ Decline rematch → Menu shows (no hang)
✅ Accept rematch → New game starts (no hang)
✅ Timeout defeat → Menu shows (no hang)
✅ All regression tests pass
✅ No AssertionError in logs

Impact:
- BREAKING: None (internal fix only)
- API: No changes to public interfaces
- Behavior: Same UX, now works correctly
- Performance: +10ms imperceptible delay per transition
- Code: 4 lines changed (minimal)

Version: v2.0.5 (critical bugfix)
Closes: wx.CallAfter AssertionError hang
Ref: docs/FIX_WX_CALLAFTER_MAINLOOP_ASSERTION.md

Co-authored-by: Nemex81 <68394029+Nemex81@users.noreply.github.com>"

git push origin copilot/remove-pygame-migrate-wxpython
```

---

## References

### Related Issues
- ❌ Issue #1: App crashes on ESC abandon (v2.0.0-v2.0.2)
- ⚠️ Fix #1: wx.CallAfter() defer pattern (v2.0.4) - **INCOMPLETE** (new issue)
- ✅ Fix #2: wx.CallLater(10) timer-based defer (v2.0.5) - **THIS FIX**

### Documentation
- [wxPython wx.CallAfter API](https://docs.wxpython.org/wx.CallAfter.html)
- [wxPython wx.CallLater API](https://docs.wxpython.org/wx.CallLater.html)
- [wxPython Timer System](https://docs.wxpython.org/wx.Timer.html)
- `docs/FIX_PANEL_SWAP_CRASH_DURING_EVENT_HANDLING.md` (defer pattern rationale)

### Code References
- Affected file: `test.py` (lines 371, 460, 463, 600)
- Deferred methods: `_safe_abandon_to_menu()`, `_safe_decline_to_menu()`, `_safe_timeout_to_menu()`
- Entry point: `show_abandon_game_dialog()`, `handle_game_ended()`, `_handle_game_over_by_timeout()`

### wxPython Internals
```python
# wx.CallAfter simplified implementation (from wxPython source)
def CallAfter(func, *args, **kwargs):
    app = wx.App.Get()  # ← FAILS if C++ registration incomplete
    assert app is not None, 'No wx.App created yet'
    app.CallLater(0, func, *args, **kwargs)  # Delegates to CallLater(0)

# wx.CallLater implementation (timer-based, reliable)
def CallLater(milliseconds, func, *args, **kwargs):
    timer = wx.CallLater(milliseconds)  # Uses wx.Timer system
    timer.Start(milliseconds, oneShot=True)  # No wx.App.Get() needed
    # Timer fires after delay → calls func
```

**Key Insight**: `CallAfter(func)` = `CallLater(0, func)` with extra `wx.App.Get()` check that can fail.

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v2.0.4 | 2026-02-14 | Copilot | wx.CallAfter() defer pattern (incomplete - assertion error) |
| v2.0.5 | 2026-02-14 | Manual + Copilot | wx.CallLater(10) timer-based defer (complete fix) |

---

## Expected Commit Diff

```diff
diff --git a/test.py b/test.py
index 6a3f6f4..XXXXXXX 100644
--- a/test.py
+++ b/test.py
@@ -368,7 +368,7 @@ class SolitarioController:
     if result:
         # User confirmed abandon (Sì button)
         print("→ User confirmed abandon - Scheduling deferred transition...")
-        wx.CallAfter(self._safe_abandon_to_menu)
+        wx.CallLater(10, self._safe_abandon_to_menu)
     # else: User cancelled (No or ESC), do nothing
 
 def _safe_abandon_to_menu(self) -> None:
@@ -457,10 +457,10 @@ class SolitarioController:
     
     if wants_rematch:
         print("→ Scheduling deferred rematch...")
-        wx.CallAfter(self.start_gameplay)
+        wx.CallLater(10, self.start_gameplay)
     else:
         print("→ Scheduling deferred decline transition...")
-        wx.CallAfter(self._safe_decline_to_menu)
+        wx.CallLater(10, self._safe_decline_to_menu)
 
 def _safe_decline_to_menu(self) -> None:
     """Deferred handler for decline rematch → menu transition."""
@@ -597,7 +597,7 @@ class SolitarioController:
         wx.MilliSleep(2000)
     
     print("→ Timeout defeat - Scheduling deferred transition...")
-    wx.CallAfter(self._safe_timeout_to_menu)
+    wx.CallLater(10, self._safe_timeout_to_menu)
 
 def _safe_timeout_to_menu(self) -> None:
     """Deferred handler for timeout defeat → menu transition."""
```

**Total**: 4 lines changed, 4 insertions(+), 4 deletions(-)

---

**END OF DOCUMENT**

---

## Quick Reference Card for Copilot

**Task**: Replace `wx.CallAfter()` with `wx.CallLater(10, ...)` in test.py

**Changes Required**: 4 lines

**Pattern**:
```python
# FIND
wx.CallAfter(some_method)

# REPLACE WITH
wx.CallLater(10, some_method)
```

**Lines to Change**:
1. Line ~371: `wx.CallAfter(self._safe_abandon_to_menu)` → `wx.CallLater(10, self._safe_abandon_to_menu)`
2. Line ~460: `wx.CallAfter(self.start_gameplay)` → `wx.CallLater(10, self.start_gameplay)`
3. Line ~463: `wx.CallAfter(self._safe_decline_to_menu)` → `wx.CallLater(10, self._safe_decline_to_menu)`
4. Line ~600: `wx.CallAfter(self._safe_timeout_to_menu)` → `wx.CallLater(10, self._safe_timeout_to_menu)`

**Test Command**: `python test.py` → Start game → ESC → Confirm → Menu shows (no hang)

**Success Indicator**: No "AssertionError: No wx.App created yet" in logs

**Commit Message**: "fix(ui): replace wx.CallAfter with wx.CallLater to prevent assertion error"

**Estimated Time**: 2 minutes (search/replace + test)
