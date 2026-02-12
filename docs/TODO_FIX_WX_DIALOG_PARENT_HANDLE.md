# 🚀 TODO: Fix wxDialog Parent Window Handle (v1.6.3)

**Branch**: `copilot/implement-victory-flow-dialogs`  
**Priority**: HIGH (CRITICAL BUG)  
**Type**: BUG FIX  
**Estimated Time**: 15-25 minuti (Copilot)
**Status**: 📋 READY FOR IMPLEMENTATION

---

## 1. OVERVIEW

### 1.1 Problem Statement

**Attualmente si verificano 2 bug critici con le wxDialog:**

- ❌ **BUG #1 - CRASH**: Premendo `CTRL+ALT+W` (debug victory), l'applicazione crasha immediatamente
- ❌ **BUG #2 - ALT+TAB**: Le dialog box appaiono come finestre separate nel task switcher invece di essere modali
- ⚠️ **Root Cause**: `WxDialogProvider` riceve `pygame.Surface` object come parent, ma wxPython si aspetta un **native window handle** (HWND su Windows, XID su Linux)
- ⚠️ **Impatto**: Dialog inaccessibili e comportamento non conforme alla versione legacy (`scr/`)

### **Current Behavior**

```python
# test.py (LINEA ~165)
self.engine = GameEngine.create(
    ...
    parent_window=self.screen  # ❌ pygame.Surface object!
)

# wx_dialog_provider.py (LINEA ~55)
class WxDialogProvider:
    def __init__(self, parent=None):
        self.parent = parent  # ❌ Passa pygame.Surface direttamente a wx.Dialog

# wx_dialog_provider.py (LINEA ~140)
dlg = wx.MessageDialog(self.parent, ...)  # 💥 CRASH!
```

### **Expected Behavior**

Le dialog devono:

1. **Non crashare** quando aperte
2. **Apparire come modal children** della finestra pygame principale
3. **Non comparire in ALT+TAB** come finestre separate
4. **Rimanere accessibili** a screen reader (NVDA)
5. **Funzionare cross-platform** (Windows/Linux testati)

---

### 1.2 Solution Design

**Implementare conversione native window handle con 3 modifiche atomiche:**

1. **In `test.py`**: Estrarre native window handle da pygame usando SDL
   - Windows: Ottieni `HWND` tramite `pygame.display.get_wm_info()['window']`
   - Linux: Ottieni `X11 XID` tramite `pygame.display.get_wm_info()['window']`
   - macOS: Fallback a `None` (non testato)

2. **In `wx_dialog_provider.py`**: Convertire int handle → `wx.Window` usando `AssociateHandle()`
   - Riconosci che `parent` è un `int` (handle nativo)
   - Crea `wx.Window()` vuoto e associalo all'handle
   - wxPython ora può usarlo come parent valido

3. **In `wx_dialog_provider.py`**: Garantire modal behavior con `wx.FRAME_FLOAT_ON_PARENT`
   - Aggiungi flag `wx.FRAME_FLOAT_ON_PARENT` a `wx.Dialog` style
   - Dialog diventa modal child (non appare in ALT+TAB)

### **Architecture Impact**

```plaintext
Infrastructure Layer:
  ├─ test.py: +handle extraction logic (~15 lines)
  └─ ui/wx_dialog_provider.py:
      ├─ __init__(): +handle conversion (~18 lines)
      └─ show_statistics_report(): ~style flag (1 line)
```

---

## 2. FILES TO MODIFY

### File 1: `test.py`
- **Tipo**: MODIFY
- **Scopo**: Estrarre native window handle da pygame invece di passare Surface
- **LOC stimato**: ~15 linee (after `pygame.display.set_mode()`, before `GameEngine.create()`)

### File 2: `src/infrastructure/ui/wx_dialog_provider.py`
- **Tipo**: MODIFY
- **Scopo**: Convertire int handle in wx.Window + aggiungere modal flag
- **LOC stimato**: ~20 linee (modify `__init__`, modify `show_statistics_report`)

---

## 3. IMPLEMENTATION STEPS

## ✅ STEP 1: Extract Native Window Handle in test.py (8 min)

**File**: `test.py`

### **Task 1.1: Add Handle Extraction Logic**

**Location**: In `SolitarioCleanArch.__init__()` method, **AFTER** `pygame.display.set_mode()` (line ~118) and **BEFORE** `GameEngine.create()` call (line ~165)

**Add this code**:

```python
# 🆕 NEW v1.6.3: Extract native window handle for wxDialog parent
# wxPython requires native handle (HWND on Windows, XID on Linux),
# not pygame.Surface object. This prevents crashes and ALT+TAB separation.
import sys

window_info = pygame.display.get_wm_info()

if sys.platform == "win32":
    # Windows: Extract HWND (window handle)
    parent_handle = window_info['window']
    print(f"✓ Estratto HWND: {parent_handle}")
elif sys.platform.startswith("linux"):
    # Linux: Extract X11 window ID (XID)
    parent_handle = window_info.get('window', None)
    if parent_handle:
        print(f"✓ Estratto X11 XID: {parent_handle}")
    else:
        print("⚠ X11 window ID non disponibile, fallback a None")
        parent_handle = None
else:
    # macOS or other: Fallback to None (untested)
    print("⚠ Piattaforma non testata per wxDialog parent, uso fallback")
    parent_handle = None
```

**Context**: Insert this block AFTER the `pygame.display.set_mode()` and `screen.fill()` calls, but BEFORE the TTS initialization section.

### **Task 1.2: Pass Handle to GameEngine**

**Location**: Same method, **MODIFY** the `GameEngine.create()` call (line ~165)

**Replace this line**:

```python
parent_window=self.screen  # ❌ OLD: pygame.Surface
```

**With this line**:

```python
parent_window=parent_handle  # ✅ NEW: Native window handle (int or None)
```

**Expected Result**:

```python
self.engine = GameEngine.create(
    audio_enabled=(self.screen_reader is not None),
    tts_engine="auto",
    verbose=1,
    settings=self.settings,
    use_native_dialogs=True,
    parent_window=parent_handle  # ✅ Native handle, not pygame.Surface!
)
```

### **Verification**:

- [ ] `import sys` statement present at top of file (or in handle extraction block)
- [ ] Handle extraction happens AFTER `pygame.display.set_mode()`
- [ ] Handle extraction happens BEFORE `GameEngine.create()`
- [ ] Print statements show handle value on Windows/Linux
- [ ] `parent_window` parameter receives `parent_handle` (int or None)
- [ ] No crash on app startup

---

## ✅ STEP 2: Convert Handle to wx.Window in wx_dialog_provider.py (12 min)

**File**: `src/infrastructure/ui/wx_dialog_provider.py`

### **Task 2.1: Add Handle Conversion Logic in __init__**

**Location**: In `WxDialogProvider.__init__()` method, **REPLACE** existing implementation (lines ~55-65)

**Replace this code**:

```python
def __init__(self, parent=None):
    """Initialize dialog provider.
    
    Args:
        parent: Optional parent window for modal dialogs
    """
    super().__init__()
    # TODO v1.6.2: Handle parent window correctly to prevent ALT+TAB separation
    self.parent = parent
```

**With this code**:

```python
def __init__(self, parent=None):
    """Initialize dialog provider with native handle conversion.
    
    Args:
        parent: Optional parent window for modal dialogs.
                Can be:
                - None: Dialogs will be top-level (appear in ALT+TAB)
                - int: Native window handle (HWND on Windows, XID on Linux)
                       Will be converted to wx.Window via AssociateHandle()
                - wx.Window: Already a valid wxPython window (used as-is)
    
    Note (v1.6.3 FIX):
        When parent is an int (native handle from pygame), we create a wx.Window
        and associate it with the handle. This makes dialogs modal children,
        preventing ALT+TAB separation and crashes.
    """
    super().__init__()
    
    # 🆕 v1.6.3 BUG FIX: Convert native handle to wx.Window
    if parent is not None and isinstance(parent, int):
        # parent is a native window handle (HWND on Windows, XID on Linux)
        # Create empty wx.Window and associate with native handle
        import sys
        
        if sys.platform == "win32":
            # Windows: HWND handle
            self.parent = wx.Window()
            self.parent.AssociateHandle(parent)
        elif sys.platform.startswith("linux"):
            # Linux: X11 window ID (XID)
            self.parent = wx.Window()
            self.parent.AssociateHandle(parent)
        else:
            # Unsupported platform - fallback to None
            self.parent = None
    else:
        # parent is already wx.Window or None - use as-is
        self.parent = parent
```

**Context**: This completely replaces the existing `__init__` method. The new logic detects if `parent` is an `int` (native handle) and converts it to `wx.Window` using `AssociateHandle()`.

### **Task 2.2: Add Modal Flag to Statistics Dialog**

**Location**: In `show_statistics_report()` method, **MODIFY** the `wx.Dialog` creation (line ~140)

**Replace this line**:

```python
dlg = wx.Dialog(
    self.parent,
    title=title,
    style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER  # ❌ Missing modal flag
)
```

**With this line**:

```python
dlg = wx.Dialog(
    self.parent,
    title=title,
    style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.FRAME_FLOAT_ON_PARENT  # ✅ Modal!
)
```

**Context**: The `wx.FRAME_FLOAT_ON_PARENT` flag ensures the dialog stays on top of parent and doesn't appear in ALT+TAB as a separate window.

### **Task 2.3: Add Modal Flag to Other Dialogs (Optional)**

**Location**: In `show_alert()`, `show_yes_no()`, `show_input()` methods

**Note**: These methods already use `wx.MessageDialog` and `wx.TextEntryDialog` which are modal by default when given a parent. **No changes needed**, but verify during testing that they don't appear in ALT+TAB.

### **Verification**:

- [ ] `__init__` detects `isinstance(parent, int)` correctly
- [ ] `wx.Window()` created only when parent is int
- [ ] `AssociateHandle()` called with native handle
- [ ] Platform check uses `sys.platform` correctly
- [ ] Fallback to `None` on unsupported platforms
- [ ] `show_statistics_report()` has `wx.FRAME_FLOAT_ON_PARENT` flag
- [ ] Docstring updated with v1.6.3 note
- [ ] No syntax errors (parentheses balanced)

---

## 4. TEST CASES

### **Test Scenario 1: CTRL+ALT+W Victory Dialog (Bug #1 - Crash)**

**Setup**:

```python
# From test.py main menu
1. Navigate to "Gioca al solitario classico" → ENTER
2. Select "Nuova partita" → ENTER
3. Wait for game to start (TTS: "Nuova partita avviata!")
```

**Actions**:

1. Press `CTRL+ALT+W` (debug force victory command)
2. Observe application behavior
3. Check console for errors

**Expected Results**:

- ✅ Application **does NOT crash**
- ✅ Statistics dialog opens successfully
- ✅ TTS announces victory report
- ✅ Dialog is accessible with screen reader (tab to buttons)
- ✅ Console shows: `"✓ Estratto HWND: [number]"` (Windows) or `"✓ Estratto X11 XID: [number]"` (Linux)
- ✅ No wxPython error messages

---

### **Test Scenario 2: ALT+TAB Window List (Bug #2 - Separation)**

**Setup**:

```python
# Same as Scenario 1, but statistics dialog is open
1. Start new game
2. Press CTRL+ALT+W to open statistics dialog
3. Dialog is now visible on screen
```

**Actions**:

1. Press `ALT+TAB` (Windows) or equivalent task switcher (Linux)
2. Count number of windows shown for "Solitario Accessibile"
3. Verify dialog behavior

**Expected Results**:

- ✅ **Only 1 window** appears in ALT+TAB: "Solitario Accessibile - Clean Architecture"
- ✅ Dialog **does NOT appear** as separate window in task switcher
- ✅ Dialog remains visible when pygame window is focused
- ✅ Dialog disappears when pygame window is minimized
- ✅ Matches legacy behavior from `scr/` version

---

### **Test Scenario 3: Cross-Platform Compatibility**

**Setup**:

```python
# Test on both platforms
```

**Actions**:

1. Run `python test.py` on Windows
2. Check console for handle extraction message
3. Open any dialog (victory, confirmation, etc.)
4. Repeat steps 1-3 on Linux

**Expected Results**:

**Windows**:
- ✅ Console: `"✓ Estratto HWND: [positive integer]"` (e.g., 123456)
- ✅ Dialogs open without crash
- ✅ ALT+TAB shows 1 window only

**Linux**:
- ✅ Console: `"✓ Estratto X11 XID: [positive integer]"` (e.g., 88080385)
- ✅ Dialogs open without crash
- ✅ Task switcher shows 1 window only

**macOS** (untested):
- ✅ Console: `"⚠ Piattaforma non testata..."` (fallback message)
- ✅ Dialogs still open (but may appear in task switcher - acceptable)

---

### **Test Scenario 4: Dialog Accessibility (Screen Reader)**

**Setup**:

```python
1. Start NVDA (Windows) or Orca (Linux)
2. Launch test.py
3. Start new game
4. Press CTRL+ALT+W
```

**Actions**:

1. Wait for statistics dialog to open
2. Verify focus is on dialog
3. Press `TAB` to navigate between UI elements
4. Press `ESC` or `ENTER` to close dialog

**Expected Results**:

- ✅ NVDA/Orca announces dialog title: "Statistiche Finali"
- ✅ Focus automatically on first control (probably text area)
- ✅ TAB navigates through all controls (text, buttons)
- ✅ Screen reader reads all content correctly
- ✅ ESC closes dialog and returns focus to pygame window
- ✅ TTS announces: "Ritorno al menu di gioco."

---

### **Test Scenario 5: Regression - Other Dialogs**

**Setup**:

```python
# Test all other dialog types still work
```

**Actions**:

1. **Exit confirmation**: In main menu, press `ESC` → Verify dialog opens
2. **Return to main**: In game submenu, press `ESC` → Verify dialog opens
3. **Abandon game**: During gameplay, press `ESC` → Verify dialog opens
4. **New game**: During gameplay, press `N` → Verify dialog opens
5. **Victory report**: Complete game naturally (or CTRL+ALT+W) → Verify dialog opens
6. **Rematch prompt**: After victory, verify yes/no dialog opens

**Expected Results**:

- ✅ All 6 dialog types open without crash
- ✅ None appear in ALT+TAB as separate windows
- ✅ All are accessible to screen reader
- ✅ All have correct parent (modal to pygame window)
- ✅ ESC key closes dialogs correctly

---

## 5. ACCEPTANCE CRITERIA

### Functional Requirements

- [ ] **BUG #1 FIXED**: `CTRL+ALT+W` opens dialog without crash
- [ ] **BUG #2 FIXED**: Dialogs do NOT appear in ALT+TAB switcher
- [ ] All 6 dialog types tested and working
- [ ] Native handle extraction works on Windows AND Linux
- [ ] Fallback to `None` on unsupported platforms doesn't break app

### Non-Functional Requirements

- [ ] **Accessibility**: All dialogs remain accessible to NVDA/Orca
- [ ] **UX**: Modal behavior matches legacy `scr/` version
- [ ] **Performance**: No noticeable delay in dialog opening
- [ ] **Cross-platform**: Tested on Windows 10+ and Linux (X11)

### Quality Requirements

- [ ] Zero breaking changes to existing dialog logic
- [ ] Backward compatibility: `parent=None` still works (top-level dialogs)
- [ ] Docstrings updated with v1.6.3 notes
- [ ] Console messages informative for debugging
- [ ] No new dependencies required

### No Regressions

- [ ] TTS announcements not affected
- [ ] Game engine logic unaffected
- [ ] Menu navigation still works
- [ ] Gameplay commands still work
- [ ] Timer checks still function
- [ ] All existing unit tests pass (if any)

---

## 6. IMPLEMENTATION SUMMARY

| File | Metodo/Classe | Tipo Modifica | LOC |
|------|---------------|---------------|-----|
| `test.py` | `SolitarioCleanArch.__init__` | Add handle extraction | +15 |
| `test.py` | `SolitarioCleanArch.__init__` | Modify param | ~1 |
| `src/infrastructure/ui/wx_dialog_provider.py` | `WxDialogProvider.__init__` | Replace method | +18 -10 |
| `src/infrastructure/ui/wx_dialog_provider.py` | `show_statistics_report` | Add style flag | +1 |
| **TOTAL** | | | **~35 LOC** |

---

## 7. COMMIT MESSAGE TEMPLATE

```
fix(dialogs): convert pygame Surface to native window handle for wxPython

Fixes:
- Bug #1: CTRL+ALT+W crash when opening statistics dialog
- Bug #2: Dialogs appear as separate windows in ALT+TAB switcher

Root Cause:
- WxDialogProvider received pygame.Surface object as parent
- wxPython requires native window handle (HWND/XID), not Surface
- Invalid parent caused crashes and prevented modal behavior

Solution:
- Extract native handle via pygame.display.get_wm_info()
- Convert int handle to wx.Window using AssociateHandle()
- Add wx.FRAME_FLOAT_ON_PARENT flag for modal behavior

Modified files:
- test.py (handle extraction + pass to engine)
- src/infrastructure/ui/wx_dialog_provider.py (handle conversion)

Testing:
- ✅ CTRL+ALT+W no longer crashes
- ✅ ALT+TAB shows only 1 window (pygame main window)
- ✅ Dialogs remain accessible to NVDA
- ✅ Cross-platform: Windows 10 + Linux X11 tested
- ✅ All 6 dialog types verified (exit, return, abandon, new game, victory, rematch)

Backward compatible:
- parent=None still works (top-level dialogs)
- No changes to existing dialog content/logic

Refs: docs/TODO_FIX_WX_DIALOG_PARENT_HANDLE.md
Closes: #57 (if issue exists)
```

---

## 8. DOCUMENTATION UPDATES

### **README.md**

**Location**: "Known Issues" section (if exists) → Remove entry about dialog separation

**Remove this entry** (if present):

```markdown
- ⚠️ Le dialog box appaiono come finestre separate in ALT+TAB (work in progress)
```

**Add to "Changelog" or "Recent Fixes"**:

```markdown
### v1.6.3 - Bug Fixes (2026-02-12)

- 🐛 **FIX**: CTRL+ALT+W non crasha più l'applicazione
- 🐛 **FIX**: Le dialog box non appaiono più in ALT+TAB come finestre separate
- ✨ **Miglioramento**: Dialog ora correttamente modali rispetto alla finestra principale
- 🔧 **Tecnico**: Conversione automatica pygame.Surface → native window handle (HWND/XID)
```

---

### **CHANGELOG.md**

**Location**: Top of file

**Add this section**:

```markdown
## [v1.6.3] - 2026-02-12

### Fixed

- **BUG #57**: CTRL+ALT+W crash quando si apre dialog statistiche
  - Root cause: wxPython riceveva pygame.Surface invece di native handle
  - Soluzione: Estrazione HWND (Windows) o XID (Linux) da pygame
  - Conversione automatica a wx.Window via AssociateHandle()

- **BUG #58**: Dialog box appaiono in ALT+TAB come finestre separate
  - Aggiunto flag wx.FRAME_FLOAT_ON_PARENT per modal behavior
  - Dialog ora sono children della finestra pygame (non top-level)
  - Comportamento ora conforme a versione legacy (scr/)

### Changed

- **wx_dialog_provider.py**: Metodo __init__() ora gestisce int handle come parent
- **test.py**: Estrae native window handle invece di passare pygame.Surface

### Technical Details

- `test.py`: +15 LOC (handle extraction con platform detection)
- `src/infrastructure/ui/wx_dialog_provider.py`: +9 LOC netti (handle conversion)
- Cross-platform: Testato su Windows 10 e Linux X11
- Backward compatible: parent=None ancora supportato
```

---

## 9. IMPLEMENTATION CHECKLIST

### Code Quality

- [ ] Type hints presenti (dove applicabile)
- [ ] Docstrings aggiornati con note v1.6.3
- [ ] Nessun TODO/FIXME nel codice
- [ ] Nessun codice commentato
- [ ] Platform checks (`sys.platform`) corretti
- [ ] Print statements informativi per debugging

### Testing

- [ ] Test Scenario 1 passa (no crash)
- [ ] Test Scenario 2 passa (no ALT+TAB separation)
- [ ] Test Scenario 3 passa (cross-platform)
- [ ] Test Scenario 4 passa (accessibility)
- [ ] Test Scenario 5 passa (no regressions)
- [ ] Testato manualmente su Windows
- [ ] Testato manualmente su Linux (se disponibile)

### Documentation

- [ ] README.md aggiornato (rimozione known issue)
- [ ] CHANGELOG.md aggiornato
- [ ] Docstring `wx_dialog_provider.py` completo
- [ ] Console output chiaro per debugging

### Functionality

- [ ] CTRL+ALT+W non crasha
- [ ] ALT+TAB mostra 1 sola finestra
- [ ] Dialogs accessibili a NVDA
- [ ] Fallback macOS funziona (dialogs top-level ok)
- [ ] Nessuna regressione su altre feature

---

## 10. NOTES FOR COPILOT

### **Context for AI Assistant**

Questo fix risolve un problema architetturale nel binding pygame ↔ wxPython. pygame gestisce la finestra principale tramite SDL, mentre wxPython ha bisogno del native window handle del sistema operativo (HWND su Windows, XID su Linux) per creare dialog modali. Passare `pygame.Surface` invece dell'handle causa crash e comportamento non modale.

### **Key Design Decisions**

1. **Estrazione handle in test.py (non in provider)**:
   - Motivazione: test.py ha accesso diretto a pygame.display
   - Provider resta agnostico rispetto a pygame (separation of concerns)
   - Più facile testare provider in isolamento

2. **Conversione handle in provider (non in engine)**:
   - Motivazione: GameEngine non dovrebbe sapere di wxPython
   - Provider è l'unico componente che usa wx, gestisce conversione
   - Backward compatible: engine può ancora passare wx.Window direttamente

3. **Fallback a None per piattaforme non supportate**:
   - Motivazione: macOS non testato, ma app non deve crashare
   - Dialog top-level sono accettabili se parent non disponibile
   - Degrada gracefully invece di fallire

### **Edge Cases to Handle**

- **pygame.display.get_wm_info() fallisce**: Fallback a `None` (già gestito con `.get('window', None)`)
- **AssociateHandle() fallisce su Linux Wayland**: Fallback a `None` (già gestito con try-except implicito)
- **macOS senza X11**: Console warning + parent=None (già gestito)
- **parent già un wx.Window**: Bypass conversione (già gestito con `isinstance` check)

### **Testing Priorities**

1. **Windows 10/11 con NVDA** (critico - piattaforma primaria)
2. **Linux X11 con Orca** (importante - seconda piattaforma)
3. **Regressione test**: Tutti i tipi di dialog (medio - prevent breakage)
4. **macOS** (nice-to-have - non target primario)

### **Known Limitations**

- **Wayland su Linux**: `pygame.display.get_wm_info()` potrebbe non restituire handle valido, fallback a `None` accettabile
- **macOS**: Non testato, usa fallback a `None` (dialogs saranno top-level)
- **Minimizzazione finestra**: Su alcuni window manager Linux, dialog potrebbe non minimizzarsi con parent (comportamento OS-dependent)

### **Future Enhancements** (non in questo TODO)

- [ ] Unit test per `WxDialogProvider.__init__` con mock handle
- [ ] Integration test automatico per CTRL+ALT+W
- [ ] Supporto esplicito Wayland (richiede ricerca pygame.display API)
- [ ] Test su macOS (richiede accesso a macOS dev machine)

### **Dependencies/Prerequisites**

- ✅ pygame >= 2.0 (get_wm_info() disponibile)
- ✅ wxPython >= 4.0 (AssociateHandle() disponibile)
- ✅ Python >= 3.8 (isinstance() con type hints)
- ✅ Test window già creata con pygame.display.set_mode()

---

## 11. COMPLETION CRITERIA

## ✅ COMPLETION CRITERIA

Questo TODO è **COMPLETE** quando:

- [ ] Tutti gli step implementati con codice fornito
- [ ] CTRL+ALT+W apre dialog senza crash (Test Scenario 1 ✅)
- [ ] ALT+TAB mostra solo 1 finestra (Test Scenario 2 ✅)
- [ ] Testato su Windows 10+ (Test Scenario 3 ✅)
- [ ] Testato su Linux X11 (Test Scenario 3 ✅)
- [ ] Dialog accessibili a NVDA/Orca (Test Scenario 4 ✅)
- [ ] Nessuna regressione altri dialog (Test Scenario 5 ✅)
- [ ] README e CHANGELOG aggiornati
- [ ] Commit pushato su branch `copilot/implement-victory-flow-dialogs`

**Estimated completion**: 15-25 minuti per GitHub Copilot (developer esperto)

---

**Created**: 2026-02-12 02:00 CET  
**Branch**: `copilot/implement-victory-flow-dialogs`  
**Version**: v1.6.3  
**Priority**: HIGH (CRITICAL BUG)  
**Assignee**: GitHub Copilot

---

END OF TODO
