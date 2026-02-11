# TODO: Fix wxDialog Parent Window - ALT+TAB Behavior

**Version**: v1.6.2 (hotfix)  
**Date**: 2026-02-11  
**Status**: 🔴 NOT STARTED  
**Priority**: MEDIUM  
**Type**: UX BUG FIX  
**Branch**: `copilot/implement-victory-flow-dialogs`  
**Estimated Time**: 15-20 minutes

---

## Executive Summary 📋

**Problem**: wxPython dialogs appear as separate windows in ALT+TAB switcher (Windows), even though they should be modal children of main pygame window.

**Impact**: 
- Non-vedenti users pressing ALT+TAB see TWO windows ("Solitario Accessibile" + "Congratulazioni!")
- Confusing UX: dialogs should not be top-level windows
- Legacy version (scr/) had correct behavior: dialogs were children of main window

**Root Cause**: `WxDialogProvider` creates all dialogs with `parent=None` → top-level windows[cite:90]

**Solution**: Pass pygame window handle to `WxDialogProvider` and use it as `parent` in all wx.Dialog/wx.MessageDialog creations.

---

## Implementation Checklist ✅

### Phase 1: Add parent parameter to WxDialogProvider (10 min)
- [ ] **Task 1.1**: Add `parent` parameter to `WxDialogProvider.__init__()` (line ~31)
- [ ] **Task 1.2**: Store `self.parent = parent` as instance attribute
- [ ] **Task 1.3**: Add docstring explaining parent window usage
- [ ] **Verify**: Constructor accepts optional parent parameter

### Phase 2: Update all dialog methods to use parent (5 min)
- [ ] **Task 2.1**: Modify `show_alert()` → Change `None` to `self.parent` (line ~42)
- [ ] **Task 2.2**: Modify `show_yes_no()` → Change `None` to `self.parent` (line ~62)
- [ ] **Task 2.3**: Modify `show_input()` → Change `None` to `self.parent` (line ~93)
- [ ] **Task 2.4**: Modify `show_statistics_report()` → Change `None` to `self.parent` (line ~132)
- [ ] **Verify**: All 4 methods updated, no `None` parent remaining

### Phase 3: Pass pygame window handle from game_engine.py (5 min)
- [ ] **Task 3.1**: Modify `GameEngine.create()` → Accept `parent_window` parameter (line ~110)
- [ ] **Task 3.2**: Pass `parent_window` to `WxDialogProvider(parent_window)`
- [ ] **Task 3.3**: Update docstring with parent_window usage example
- [ ] **Verify**: Dialog provider receives pygame window handle

### Phase 4: Pass pygame screen from test.py (3 min)
- [ ] **Task 4.1**: Modify `test.py` line ~115 → Add `parent_window=self.screen` parameter
- [ ] **Task 4.2**: Update comment explaining parent window for modal dialogs
- [ ] **Verify**: pygame screen passed to engine creation

### Phase 5: Testing & Validation (5 min)
- [ ] **Test 5.1**: Start app → Press CTRL+ALT+W → Check ALT+TAB: Only 1 window visible
- [ ] **Test 5.2**: Open any dialog → Press ALT+TAB → Dialog should NOT appear separately
- [ ] **Test 5.3**: Dialog still modal (blocks input to main window)
- [ ] **Test 5.4**: NVDA still reads dialog content correctly
- [ ] **Verify**: ALT+TAB shows ONLY "Solitario Accessibile" window

---

## Detailed Implementation Plan 🛠️

### PHASE 1: Add Parent Parameter to WxDialogProvider

**File**: `src/infrastructure/ui/wx_dialog_provider.py`  
**Location**: `__init__()` method, line ~31  
**Time**: 10 minutes

**Current Code**:
```python
class WxDialogProvider(DialogProvider):
    """wxPython implementation of DialogProvider.
    
    Creates wx.App() instance on-demand for each dialog (legacy pattern).
    This approach works because pygame manages the main event loop,
    and wxPython dialogs run in modal mode (blocking).
    
    Example:
        >>> provider = WxDialogProvider()
        >>> provider.show_alert("Hai vinto!", "Congratulazioni")
        # Dialog appears, blocks execution until user clicks OK
        >>> print("Dialog closed")
    """
```

**Modified Code**:
```python
class WxDialogProvider(DialogProvider):
    """wxPython implementation of DialogProvider.
    
    Creates wx.App() instance on-demand for each dialog (legacy pattern).
    This approach works because pygame manages the main event loop,
    and wxPython dialogs run in modal mode (blocking).
    
    Args (NEW v1.6.2):
        parent: Optional pygame window handle to use as dialog parent.
                If provided, dialogs will be modal children (recommended).
                If None, dialogs are top-level windows (legacy fallback).
    
    Behavior:
        - With parent: Dialogs don't appear in ALT+TAB switcher
        - Without parent: Dialogs appear as separate windows (confusing UX)
    
    Example:
        >>> import pygame
        >>> screen = pygame.display.set_mode((800, 600))
        >>> provider = WxDialogProvider(parent=screen)  # RECOMMENDED
        >>> provider.show_alert("Hai vinto!", "Congratulazioni")
        # Dialog is child of pygame window, won't show in ALT+TAB
    """
    
    def __init__(self, parent=None):
        """Initialize dialog provider with optional parent window.
        
        Args:
            parent: pygame display surface or wx.Window. If provided,
                    all dialogs will be created as modal children.
        
        Note:
            Passing pygame.display.get_surface() as parent is safe:
            wxPython will extract the native window handle automatically.
        """
        self.parent = parent  # Store for use in all dialog methods
```

**Key Changes**:
1. Added `parent` parameter to `__init__()`
2. Stored as `self.parent` instance attribute
3. Updated docstring with parent usage examples
4. Explained ALT+TAB behavior difference

---

### PHASE 2: Update All Dialog Methods

**File**: `src/infrastructure/ui/wx_dialog_provider.py`  
**Locations**: 4 methods to modify  
**Time**: 5 minutes

#### Task 2.1: Modify show_alert()

**Location**: Line ~42  
**Change**: `None` → `self.parent`

**Before**:
```python
def show_alert(self, message: str, title: str) -> None:
    app = wx.App()
    dlg = wx.MessageDialog(
        None,  # ❌ Top-level window
        message,
        title,
        wx.OK | wx.ICON_INFORMATION
    )
    dlg.ShowModal()
    dlg.Destroy()
    wx.Yield()
```

**After**:
```python
def show_alert(self, message: str, title: str) -> None:
    app = wx.App()
    dlg = wx.MessageDialog(
        self.parent,  # ✅ Child of pygame window
        message,
        title,
        wx.OK | wx.ICON_INFORMATION
    )
    dlg.ShowModal()
    dlg.Destroy()
    wx.Yield()
```

---

#### Task 2.2: Modify show_yes_no()

**Location**: Line ~62  
**Change**: `None` → `self.parent`

**Before**:
```python
def show_yes_no(self, question: str, title: str) -> bool:
    app = wx.App()
    dlg = wx.MessageDialog(
        None,  # ❌ Top-level window
        question,
        title,
        wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION
    )
    result = dlg.ShowModal() == wx.ID_YES
    dlg.Destroy()
    wx.Yield()
    return result
```

**After**:
```python
def show_yes_no(self, question: str, title: str) -> bool:
    app = wx.App()
    dlg = wx.MessageDialog(
        self.parent,  # ✅ Child of pygame window
        question,
        title,
        wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION
    )
    result = dlg.ShowModal() == wx.ID_YES
    dlg.Destroy()
    wx.Yield()
    return result
```

---

#### Task 2.3: Modify show_input()

**Location**: Line ~93  
**Change**: `None` → `self.parent`

**Before**:
```python
def show_input(
    self,
    question: str,
    title: str,
    default: str = ""
) -> Optional[str]:
    app = wx.App()
    dlg = wx.TextEntryDialog(
        None,  # ❌ Top-level window
        question,
        title,
        value=default
    )
    
    if dlg.ShowModal() == wx.ID_OK:
        result = dlg.GetValue()
        dlg.Destroy()
        wx.Yield()
        return result
    else:
        dlg.Destroy()
        wx.Yield()
        return None
```

**After**:
```python
def show_input(
    self,
    question: str,
    title: str,
    default: str = ""
) -> Optional[str]:
    app = wx.App()
    dlg = wx.TextEntryDialog(
        self.parent,  # ✅ Child of pygame window
        question,
        title,
        value=default
    )
    
    if dlg.ShowModal() == wx.ID_OK:
        result = dlg.GetValue()
        dlg.Destroy()
        wx.Yield()
        return result
    else:
        dlg.Destroy()
        wx.Yield()
        return None
```

---

#### Task 2.4: Modify show_statistics_report()

**Location**: Line ~132  
**Change**: `None` → `self.parent`

**Before**:
```python
def show_statistics_report(
    self,
    stats: Dict[str, Any],
    final_score: Optional[Dict[str, Any]],
    is_victory: bool,
    deck_type: str
) -> None:
    # ... report generation ...
    
    app = wx.App()
    title = "Congratulazioni!" if is_victory else "Partita Terminata"
    
    dlg = wx.Dialog(
        None,  # ❌ Top-level window
        title=title,
        style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
    )
    
    # ... rest of method ...
```

**After**:
```python
def show_statistics_report(
    self,
    stats: Dict[str, Any],
    final_score: Optional[Dict[str, Any]],
    is_victory: bool,
    deck_type: str
) -> None:
    # ... report generation ...
    
    app = wx.App()
    title = "Congratulazioni!" if is_victory else "Partita Terminata"
    
    dlg = wx.Dialog(
        self.parent,  # ✅ Child of pygame window
        title=title,
        style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
    )
    
    # ... rest of method ...
```

---

### PHASE 3: Update GameEngine.create() to Accept Parent

**File**: `src/application/game_engine.py`  
**Location**: `create()` classmethod, line ~110  
**Time**: 5 minutes

**Current Signature**:
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
```

**Modified Signature**:
```python
@classmethod
def create(
    cls,
    audio_enabled: bool = True,
    tts_engine: str = "auto",
    verbose: int = 1,
    settings: Optional[GameSettings] = None,
    use_native_dialogs: bool = False,
    parent_window = None  # 🆕 NEW v1.6.2 - pygame screen for modal dialogs
) -> "GameEngine":
    """Factory method to create fully initialized game engine.
    
    Args:
        audio_enabled: Enable audio feedback
        tts_engine: TTS engine ("auto", "nvda", "sapi5")
        verbose: Audio verbosity level (0-2)
        settings: GameSettings instance for configuration
        use_native_dialogs: Enable native wxPython dialogs (v1.6.0)
        parent_window: pygame.display surface for modal dialog parenting (v1.6.2)
                       If provided, wxDialogs won't appear in ALT+TAB switcher
        
    Returns:
        Initialized GameEngine instance ready to play
    
    Example (v1.6.2):
        >>> import pygame
        >>> screen = pygame.display.set_mode((800, 600))
        >>> engine = GameEngine.create(
        ...     use_native_dialogs=True,
        ...     parent_window=screen  # Dialogs will be modal children
        ... )
        >>> # Now dialogs won't show as separate windows in ALT+TAB
    """
    # ... existing code ...
    
    # ✨ v1.6.0: Create dialog provider if requested
    dialog_provider = None
    if use_native_dialogs:
        try:
            from src.infrastructure.ui.wx_dialog_provider import WxDialogProvider
            dialog_provider = WxDialogProvider(parent=parent_window)  # 🆕 Pass parent
        except ImportError:
            dialog_provider = None
    
    # ... rest of method ...
```

**Key Changes**:
1. Added `parent_window` parameter (default `None` for backward compat)
2. Pass `parent=parent_window` to `WxDialogProvider()` constructor
3. Updated docstring with example showing pygame screen usage

---

### PHASE 4: Pass pygame.screen from test.py

**File**: `test.py`  
**Location**: `__init__()` method, line ~115  
**Time**: 3 minutes

**Current Code**:
```python
# Application: Game engine setup (now with settings AND dialogs!)
print("Inizializzazione motore di gioco...")
self.engine = GameEngine.create(
    audio_enabled=(self.screen_reader is not None),
    tts_engine="auto",
    verbose=1,
    settings=self.settings,
    use_native_dialogs=True  # v1.6.2 - ENABLE WX DIALOGS
)

# 🆕 v1.6.2: Inject end game callback for UI state management
self.engine.on_game_ended = self.handle_game_ended

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
    use_native_dialogs=True,  # v1.6.2 - Enable wxDialogs
    parent_window=self.screen  # 🆕 v1.6.2 - Dialogs as modal children (no ALT+TAB)
)

# 🆕 v1.6.2: Inject end game callback for UI state management
self.engine.on_game_ended = self.handle_game_ended

print("✓ Game engine pronto con dialog modali")
```

**Key Changes**:
1. Added `parent_window=self.screen` parameter
2. Updated console print message to reflect modal dialogs
3. Comment explains purpose (prevent ALT+TAB separation)

---

## Verification & Testing 🧪

### Manual Testing Scenarios

#### Scenario 1: ALT+TAB with Victory Dialog Open

**Steps**:
1. Start application: `python test.py`
2. Navigate to gameplay
3. Press CTRL+ALT+W (debug victory)
4. **While dialog is open**, press ALT+TAB

**Expected Behavior**:
- ✅ ALT+TAB shows ONLY "Solitario Accessibile - Clean Architecture"
- ✅ Dialog does NOT appear as separate window
- ✅ Pressing ALT+TAB switches to other apps (not dialog)

**Verification Points**:
- Windows Taskbar: Only 1 Solitario icon
- ALT+TAB list: No "Congratulazioni!" entry
- Dialog still visible and modal (blocks pygame window)

---

#### Scenario 2: ALT+TAB with Rematch Dialog

**Steps**:
1. Complete game or use CTRL+ALT+W
2. Statistics dialog closes → Rematch dialog appears
3. Press ALT+TAB

**Expected Behavior**:
- ✅ Only "Solitario Accessibile" in ALT+TAB
- ✅ "Vuoi giocare ancora?" dialog NOT in list
- ✅ Dialog remains modal and on top

---

#### Scenario 3: ALT+TAB with Abandon Game Dialog

**Steps**:
1. Start game
2. Press ESC → Abandon dialog appears
3. Press ALT+TAB

**Expected Behavior**:
- ✅ Only 1 window in ALT+TAB
- ✅ Abandon dialog is child (not separate)

---

#### Scenario 4: NVDA Compatibility (Regression Test)

**Steps**:
1. Start NVDA
2. Open any dialog (CTRL+ALT+W or ESC)
3. Listen to NVDA announcements

**Expected Behavior**:
- ✅ NVDA still reads dialog title
- ✅ NVDA still reads content (TextCtrl auto-focus works)
- ✅ TAB navigation works
- ✅ Dialog closes correctly (ESC/ENTER)

**Verification Points**:
- No NVDA focus issues
- Dialog content fully readable
- No regression from parent window change

---

#### Scenario 5: Backward Compatibility (No parent)

**Steps**:
1. Modify test.py: Remove `parent_window=self.screen` parameter
2. Start app and open dialog

**Expected Behavior**:
- ✅ Dialog still appears (no crash)
- ✅ Dialog works normally (fallback to top-level)
- ⚠️ ALT+TAB shows 2 windows (old broken behavior)

**Verification Points**:
- `parent=None` fallback works
- No crashes or errors
- Confirms fix is in the parent parameter

---

## Expected Outcomes ✨

### Before Fix (Current State ❌)
- ALT+TAB shows: "Solitario Accessibile" + "Congratulazioni!" (2 entries)
- Dialogs appear as top-level windows
- Confusing for blind users using ALT+TAB navigation
- Inconsistent with legacy version (scr/) behavior

### After Fix (Expected State ✅)
- ALT+TAB shows: "Solitario Accessibile" ONLY (1 entry)
- Dialogs are modal children of pygame window
- Clean UX matching legacy version
- Consistent with Windows modal dialog conventions

---

## Technical Notes 📝

### Why This Works

**wxPython parent window handling**:
- When `parent` is provided, wx creates dialog as **child window**
- Child windows inherit modality and focus from parent
- Operating system (Windows) hides child windows from taskbar/ALT+TAB

**pygame surface as parent**:
- `pygame.display.get_surface()` returns SDL window handle
- wxPython can extract native HWND (Windows) from pygame surface
- Cross-platform: Works on Windows, Linux, macOS

**Modality unchanged**:
- `ShowModal()` behavior identical with/without parent
- Blocking still works (pygame event loop paused)
- Focus returns to pygame window on close

---

### Legacy Version Reference (scr/)

In the old codebase (`scr/dialogs.py`), you likely had:

```python
# Legacy pattern (working correctly)
class DialogManager:
    def __init__(self, parent_window):
        self.parent = parent_window  # pygame screen
    
    def show_victory_dialog(self):
        dlg = wx.Dialog(
            self.parent,  # ✅ Used parent window
            title="Congratulazioni!"
        )
        # ... rest of dialog creation ...
```

This TODO replicates that pattern in the new Clean Architecture version.

---

## Rollback Plan 🔄

If parent window causes issues (unlikely):

1. **Remove parent_window parameter** from test.py:
   ```python
   use_native_dialogs=True  # Remove parent_window line
   ```

2. **Expected behavior after rollback**:
   - Dialogs work normally (no crash)
   - ALT+TAB shows 2 windows again (original bug returns)
   - No new issues introduced

---

## Success Criteria 🎯

Implementation is complete when:

1. ✅ ALT+TAB shows ONLY "Solitario Accessibile" (1 window)
2. ✅ Dialogs do NOT appear in taskbar separately
3. ✅ Dialogs remain modal (block pygame input)
4. ✅ NVDA screen reader still works correctly (no regression)
5. ✅ All 4 dialog methods use `self.parent`
6. ✅ Backward compatible (works if `parent=None`)
7. ✅ No console errors or warnings
8. ✅ Behavior matches legacy version (scr/)

---

**Last Updated**: 2026-02-11 23:56 CET  
**Next Action**: Begin Phase 1 implementation  
**Estimated Total Time**: 15-20 minutes  
**Complexity**: LOW (simple parameter addition)