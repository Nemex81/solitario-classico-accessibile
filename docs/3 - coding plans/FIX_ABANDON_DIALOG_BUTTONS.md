# Fix Plan: AbandonDialog Button Event Handlers

**Version**: v3.1.3  
**Date**: 19 Febbraio 2026  
**Type**: Bug Fix  
**Priority**: HIGH (blocks timeout dialog interaction)

---

## 🐛 Bug Report

### Symptoms
- Clicking buttons in AbandonDialog (after timeout or manual abandon) does nothing
- No error messages, buttons simply don't respond
- Only keyboard shortcuts (INVIO/ESC) work for 2-button normal scenario
- All 3 timeout buttons completely non-functional (no keyboard shortcuts)

### Root Cause
**File**: `src/presentation/dialogs/abandon_dialog.py`  
**Lines**: 91-105  

5 buttons created but **NO event handlers bound**:
- 3 timeout buttons: `btn_rematch`, `btn_stats`, `btn_menu` (lines 93-95)
- 2 normal buttons: `btn_new_game`, `btn_menu` (lines 102-103)

No `Bind(wx.EVT_BUTTON, ...)` calls → click events ignored.

### Impact
- **Severity**: CRITICAL for timeout scenario (buttons unusable)
- **Accessibility**: Screen reader users navigating with TAB+SPACE blocked
- **Mouse users**: Cannot interact with dialog at all
- **Keyboard users**: Partial workaround (INVIO/ESC) only for normal scenario

---

## 🎯 Solution Overview

### Goal
Add event handlers for all 5 buttons to properly close dialog with correct return codes.

### Scope
**File Modified**: 1 (`src/presentation/dialogs/abandon_dialog.py`)  
**Lines Added**: ~20 (5 handler methods + 5 bind calls)  
**Breaking Changes**: None (backward compatible)

---

## 📋 Implementation Plan

### Step 1: Add Handler Methods

**Location**: After `_set_focus()` method (around line 167)

**Code to Add**:
```python
# ========================================
# BUTTON EVENT HANDLERS (v3.1.3 - Bug Fix)
# ========================================

def _on_rematch(self, event):
    """Handler for Rematch button (timeout scenario).
    
    Closes dialog with wx.ID_YES to signal rematch request.
    GameEngine will start new game.
    """
    self.EndModal(wx.ID_YES)

def _on_stats(self, event):
    """Handler for Detailed Stats button (timeout scenario).
    
    Closes dialog with wx.ID_MORE to signal stats request.
    GameEngine will open DetailedStatsDialog.
    """
    self.EndModal(wx.ID_MORE)

def _on_menu_timeout(self, event):
    """Handler for Main Menu button (timeout scenario).
    
    Closes dialog with wx.ID_NO to signal menu return.
    GameEngine will return control to main menu.
    """
    self.EndModal(wx.ID_NO)

def _on_new_game(self, event):
    """Handler for New Game button (normal abandon scenario).
    
    Closes dialog with wx.ID_OK to signal new game request.
    GameEngine will start new game.
    """
    self.EndModal(wx.ID_OK)

def _on_menu_normal(self, event):
    """Handler for Main Menu button (normal abandon scenario).
    
    Closes dialog with wx.ID_CANCEL to signal menu return.
    GameEngine will return control to main menu.
    """
    self.EndModal(wx.ID_CANCEL)
```

**Rationale**:
- Each handler calls `EndModal(wx.ID_*)` to close dialog with appropriate return code
- Return codes match existing GameEngine logic (lines 868-897 in `game_engine.py`)
- Separate handlers for clarity (even if logic identical for some)

---

### Step 2: Bind Timeout Scenario Buttons

**Location**: After button creation (around line 98), inside `if self.show_rematch_option:` block

**Code to Add**:
```python
# Bind event handlers (v3.1.3 fix)
self.btn_rematch.Bind(wx.EVT_BUTTON, self._on_rematch)
self.btn_stats.Bind(wx.EVT_BUTTON, self._on_stats)
self.btn_menu.Bind(wx.EVT_BUTTON, self._on_menu_timeout)
```

**Context**:
```python
if self.show_rematch_option:
    # Timeout scenario: 3 buttons (Rematch / Stats / Menu)
    self.btn_rematch = wx.Button(self, wx.ID_YES, "Rivincita")
    self.btn_stats = wx.Button(self, wx.ID_MORE, "Statistiche Dettagliate")
    self.btn_menu = wx.Button(self, wx.ID_NO, "Torna al Menu (ESC)")
    
    # ✅ ADD THESE 3 LINES
    self.btn_rematch.Bind(wx.EVT_BUTTON, self._on_rematch)
    self.btn_stats.Bind(wx.EVT_BUTTON, self._on_stats)
    self.btn_menu.Bind(wx.EVT_BUTTON, self._on_menu_timeout)
    
    btn_sizer.Add(self.btn_rematch, 0, wx.ALL, 5)
    btn_sizer.Add(self.btn_stats, 0, wx.ALL, 5)
    btn_sizer.Add(self.btn_menu, 0, wx.ALL, 5)
```

---

### Step 3: Bind Normal Scenario Buttons

**Location**: After button creation (around line 105), inside `else:` block

**Code to Add**:
```python
# Bind event handlers (v3.1.3 fix)
self.btn_new_game.Bind(wx.EVT_BUTTON, self._on_new_game)
self.btn_menu.Bind(wx.EVT_BUTTON, self._on_menu_normal)
```

**Context**:
```python
else:
    # Normal abandon: 2 buttons (New Game / Menu)
    self.btn_new_game = wx.Button(self, wx.ID_OK, "Nuova Partita (INVIO)")
    self.btn_menu = wx.Button(self, wx.ID_CANCEL, "Menu Principale (ESC)")
    
    # ✅ ADD THESE 2 LINES
    self.btn_new_game.Bind(wx.EVT_BUTTON, self._on_new_game)
    self.btn_menu.Bind(wx.EVT_BUTTON, self._on_menu_normal)
    
    btn_sizer.Add(self.btn_new_game, 0, wx.ALL, 5)
    btn_sizer.Add(self.btn_menu, 0, wx.ALL, 5)
```

---

## ✅ Verification Steps

### Manual Testing

#### Test 1: Timeout Scenario (3 buttons)
1. Start game with timer enabled (Option 4)
2. Wait for timer expiration (or set short timer for testing)
3. AbandonDialog appears with 3 buttons
4. **Test each button**:
   - Click "Rivincita" → Should start new game
   - Click "Statistiche Dettagliate" → Should open DetailedStatsDialog
   - Click "Torna al Menu" → Should return to main menu
5. **Test keyboard**:
   - TAB to each button + SPACE → Should behave like click
   - ESC → Should return to menu (label hint)

#### Test 2: Normal Abandon (2 buttons)
1. Start game
2. Press ESC to abandon (or menu option)
3. AbandonDialog appears with 2 buttons
4. **Test each button**:
   - Click "Nuova Partita" → Should start new game
   - Click "Menu Principale" → Should return to main menu
5. **Test keyboard**:
   - INVIO → Should start new game
   - ESC → Should return to menu
   - TAB + SPACE → Should behave like click

#### Test 3: Screen Reader Navigation
1. With NVDA active, trigger both scenarios
2. TAB through buttons
3. Verify each button announces correctly
4. Press SPACE on focused button → Should close dialog

### Automated Testing (Optional)

**File**: `tests/unit/presentation/dialogs/test_abandon_dialog.py` (if exists)

```python
def test_timeout_buttons_close_dialog(wx_app):
    """Test timeout scenario buttons properly close dialog."""
    from src.presentation.dialogs.abandon_dialog import AbandonDialog
    from src.domain.models.profile import SessionOutcome
    from src.domain.models.game_end import EndReason
    
    outcome = SessionOutcome.create_new(
        profile_id=1,
        end_reason=EndReason.TIMEOUT_STRICT,
        is_victory=False,
        elapsed_time=300.0,
        timer_enabled=True,
        timer_limit=300,
        timer_mode="STRICT",
        timer_expired=True,
        scoring_enabled=False,
        final_score=0,
        difficulty_level=3,
        deck_type="french",
        move_count=10
    )
    
    dialog = AbandonDialog(None, outcome, {}, show_rematch_option=True)
    
    # Simulate button clicks
    import wx
    event = wx.CommandEvent(wx.EVT_BUTTON.typeId)
    
    # Test Rematch button
    dialog.btn_rematch.ProcessEvent(event)
    assert dialog.GetReturnCode() == wx.ID_YES
    
    # Test Stats button
    dialog = AbandonDialog(None, outcome, {}, show_rematch_option=True)
    dialog.btn_stats.ProcessEvent(event)
    assert dialog.GetReturnCode() == wx.ID_MORE
    
    # Test Menu button
    dialog = AbandonDialog(None, outcome, {}, show_rematch_option=True)
    dialog.btn_menu.ProcessEvent(event)
    assert dialog.GetReturnCode() == wx.ID_NO
```

---

## 📊 Success Criteria

- [ ] All 5 buttons respond to click events
- [ ] All 5 buttons respond to TAB+SPACE keyboard navigation
- [ ] Dialog closes with correct `wx.ID_*` return code for each button
- [ ] GameEngine receives correct return code and executes appropriate action:
  - `wx.ID_YES` → New game (rematch)
  - `wx.ID_MORE` → Open DetailedStatsDialog
  - `wx.ID_NO` → Return to menu (timeout)
  - `wx.ID_OK` → New game (normal)
  - `wx.ID_CANCEL` → Return to menu (normal)
- [ ] No regression: INVIO/ESC shortcuts still work for normal scenario
- [ ] Screen reader announces buttons correctly and SPACE works on focused button

---

## 📦 Commit Message Template

```
fix(dialogs): Add missing event handlers for AbandonDialog buttons

FIXES: Timeout and abandon dialog buttons non-responsive to clicks

ROOT CAUSE:
- 5 buttons created without wx.EVT_BUTTON handlers bound
- Clicking buttons had no effect (only INVIO/ESC worked partially)
- Screen reader users with TAB+SPACE navigation blocked

CHANGES:
- Added 5 event handler methods (_on_rematch, _on_stats, etc.)
- Bound handlers to all 5 buttons (3 timeout + 2 normal)
- Each handler calls EndModal(wx.ID_*) with appropriate return code

VERIFICATION:
- Timeout scenario: All 3 buttons (Rematch/Stats/Menu) now functional
- Normal scenario: Both buttons (New Game/Menu) now functional
- Keyboard navigation (TAB+SPACE) works correctly
- Screen reader accessible (NVDA tested)

IMPACT:
- Restores full dialog functionality
- Fixes critical accessibility issue
- No breaking changes (backward compatible)

Refs: FIX_ABANDON_DIALOG_BUTTONS.md
Version: v3.1.3
```

---

## 🔄 Rollout Plan

### Phase 1: Implementation
1. Checkout `refactoring-engine` branch
2. Apply changes to `abandon_dialog.py`
3. Manual testing (both scenarios)
4. Commit with template message

### Phase 2: Integration
1. Push to remote `refactoring-engine`
2. Optional: Create PR for review (if team workflow requires)
3. Merge to main branch after verification

### Phase 3: Release
1. Tag as v3.1.3 (patch release)
2. Update CHANGELOG.md:
   - Add bug fix entry under v3.1.3
   - Reference this plan document
3. Announce fix in release notes

---

## 📝 Notes

### Why Separate Handlers?
- **Clarity**: Each handler has specific semantic purpose
- **Maintainability**: Easy to add logic later (e.g., logging, analytics)
- **Debugging**: Stack traces show which button was clicked
- **Extensibility**: Future enhancements (e.g., confirmation prompts) easier

### Why Not Use Lambda?
```python
# ❌ BAD: Anonymous lambda loses context
self.btn_rematch.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_YES))

# ✅ GOOD: Named method provides clarity
self.btn_rematch.Bind(wx.EVT_BUTTON, self._on_rematch)
```

### Backward Compatibility
- No API changes to `AbandonDialog.__init__()`
- No changes to `game_engine.py` logic
- Existing keyboard shortcuts (INVIO/ESC) preserved
- Return codes unchanged (wx.ID_YES, wx.ID_OK, etc.)

---

## 🚀 Related Issues

- **Original Bug Discovery**: User testing session (19 Feb 2026)
- **Affected Component**: Profile System v3.1.0+ (timeout dialogs)
- **Related Files**:
  - `src/application/game_engine.py` (lines 868-897) - dialog invocation
  - `src/presentation/dialogs/victory_dialog.py` - similar pattern to check
  - `src/presentation/dialogs/detailed_stats_dialog.py` - opened from Stats button

---

**Status**: 📝 READY FOR IMPLEMENTATION  
**Assigned**: GitHub Copilot  
**Estimated Time**: 5 minutes  
**Risk Level**: LOW (isolated change, easy to test)
