# 🔧 Fix: Panel Sizer Registration (Critical Bug)

**Branch**: `copilot/remove-pygame-migrate-wxpython`  
**Issue**: Menu buttons non funzionano, panel invisibili  
**Versione**: v1.7.3 (PATCH - critical fix)  
**Stima**: 15 minuti (1 commit, 5 fix)

---

## 📊 Sintomi Riportati

**Utente**:
- ✅ Finestra principale caricata (600x450px)
- ✅ 3 voci menu visibili: "Gioca", "Opzioni", "Esci"
- ❌ ENTER su "Opzioni" → nulla
- ❌ ENTER su "Gioca" → apre finestra opzioni (sbagliato)
- ❌ Nessuna azione correlata

---

## 🔍 Root Cause: 5 Problemi Critici

### 1. `panel_container` Senza Sizer

**File**: `src/infrastructure/ui/wx_frame.py` (~linea 111)

**Problema**:
```python
self.panel_container = wx.Panel(self)  # ✅ Created
self.sizer = wx.BoxSizer(wx.VERTICAL)
self.sizer.Add(self.panel_container, 1, wx.EXPAND)
self.SetSizer(self.sizer)  # ✅ Frame has sizer
# ❌ MISSING: panel_container.SetSizer(...)
```

**Conseguenza**: Panel figli non vengono layouttati, `GetSizer()` ritorna `None`.

---

### 2. ViewManager Non Ottiene Sizer

**File**: `src/infrastructure/ui/view_manager.py` (~linea 73)

**Problema**:
```python
def __init__(self, parent_frame: wx.Frame):
    self.parent_frame = parent_frame
    self.panels = {}
    # ❌ MISSING: self.panel_container
    # ❌ MISSING: self.container_sizer
```

**Conseguenza**: ViewManager non può aggiungere panel al sizer.

---

### 3. Panel Non Aggiunti al Sizer

**File**: `src/infrastructure/ui/view_manager.py` (~linea 97)

**Problema**:
```python
def register_panel(self, name: str, panel: wx.Panel):
    self.panels[name] = panel
    panel.Hide()
    # ❌ MISSING: self.container_sizer.Add(panel, 1, wx.EXPAND)
```

**Conseguenza**: Panel esistono in memoria ma non nel layout tree → invisibili.

---

### 4. Metodo `open_options()` Duplicato

**File**: `test.py` (~linea 314)

**Problema**: Metodo legacy `open_options()` ancora presente oltre a `show_options()` (linea 206).

**Conseguenza**: Routing confuso, possibili chiamate errate.

---

### 5. Layout Refresh Incompleto

**File**: `src/infrastructure/ui/view_manager.py` (~linea 146)

**Problema**: `show_panel()` chiama `Layout()` solo su container, non su frame.

**Conseguenza**: Edge case dove layout non propaga completamente.

---

## 🛠️ Implementazione: 5 Fix

### FIX 1: Aggiungi Sizer a `panel_container`

**File**: `src/infrastructure/ui/wx_frame.py`

**PRIMA** (~linea 111-116):
```python
# Setup panel container (for child panels)
self.panel_container = wx.Panel(self)
self.sizer = wx.BoxSizer(wx.VERTICAL)
self.sizer.Add(self.panel_container, 1, wx.EXPAND)
self.SetSizer(self.sizer)
```

**DOPO**:
```python
# Setup panel container (for child panels)
self.panel_container = wx.Panel(self)
container_sizer = wx.BoxSizer(wx.VERTICAL)  # ✅ Sizer for container
self.panel_container.SetSizer(container_sizer)  # ✅ Assign sizer

# Frame sizer (contains the container)
self.sizer = wx.BoxSizer(wx.VERTICAL)
self.sizer.Add(self.panel_container, 1, wx.EXPAND)
self.SetSizer(self.sizer)
```

---

### FIX 2: ViewManager Ottieni Container Sizer

**File**: `src/infrastructure/ui/view_manager.py`

**PRIMA** (~linea 73-78):
```python
def __init__(self, parent_frame: wx.Frame):
    self.parent_frame = parent_frame
    self.panels: Dict[str, wx.Panel] = {}
    self.current_panel_name: Optional[str] = None
```

**DOPO**:
```python
def __init__(self, parent_frame: wx.Frame):
    """Initialize with container sizer reference."""
    self.parent_frame = parent_frame
    
    # Get panel container and sizer
    if not hasattr(parent_frame, 'panel_container'):
        raise AttributeError("Frame must have 'panel_container'")
    
    self.panel_container = parent_frame.panel_container
    self.container_sizer = self.panel_container.GetSizer()
    
    if self.container_sizer is None:
        raise ValueError("panel_container must have sizer")
    
    self.panels: Dict[str, wx.Panel] = {}
    self.current_panel_name: Optional[str] = None
    
    logger.debug(f"ViewManager initialized with sizer: {self.container_sizer}")
```

---

### FIX 3: Aggiungi Panel al Sizer

**File**: `src/infrastructure/ui/view_manager.py`

**PRIMA** (~linea 97-113):
```python
def register_panel(self, name: str, panel: wx.Panel) -> None:
    if name in self.panels:
        logger.warning(f"Overwriting panel: {name}")
    
    self.panels[name] = panel
    panel.Hide()
    logger.debug(f"Registered panel: {name}")
```

**DOPO**:
```python
def register_panel(self, name: str, panel: wx.Panel) -> None:
    """Register panel and add to container sizer."""
    if name in self.panels:
        logger.warning(f"Overwriting panel: {name}")
    
    self.panels[name] = panel
    
    # CRITICAL: Add to container sizer
    # proportion=1: Takes all space
    # wx.EXPAND: Expands to fill
    self.container_sizer.Add(panel, 1, wx.EXPAND)
    logger.debug(f"Added panel '{name}' to sizer")
    
    panel.Hide()  # Initially hidden
    logger.debug(f"Registered panel: {name}")
```

---

### FIX 4: Rimuovi `open_options()` Duplicato

**File**: `test.py`

**PRIMA** (~linea 314-328):
```python
# === OPTIONS HANDLING ===

def open_options(self) -> None:  # ❌ DUPLICATE
    """Open virtual options window."""
    print("\n" + "="*60)
    print("APERTURA FINESTRA OPZIONI")
    print("="*60)
    
    self.is_menu_open = False  # ❌ Wrong flag
    self.is_options_mode = True
    
    msg = self.gameplay_controller.options_controller.open_window()
    
    if self.screen_reader:
        self.screen_reader.tts.speak(msg, interrupt=True)
    
    print("Finestra opzioni aperta.")
    print("="*60)
```

**DOPO**:
```python
# === OPTIONS HANDLING ===
# (Section now empty - open_options() removed)
# show_options() already exists at line ~206 ✅
```

---

### FIX 5: Layout Completo in `show_panel()`

**File**: `src/infrastructure/ui/view_manager.py`

**PRIMA** (~linea 146-150):
```python
# Show requested panel
target_panel = self.panels[name]
target_panel.Show()

# Refresh layout
parent = target_panel.GetParent()
if parent:
    parent.Layout()
    parent.Refresh()

target_panel.SetFocus()
```

**DOPO**:
```python
# Show requested panel
target_panel = self.panels[name]
target_panel.Show()

# Refresh layout (container + frame)
parent = target_panel.GetParent()  # panel_container
if parent:
    parent.Layout()  # Layout container
    parent.Refresh()  # Repaint
    
    # Also layout frame hierarchy
    frame = parent.GetParent()  # SolitarioFrame
    if frame:
        frame.Layout()  # Complete propagation
        logger.debug(f"Laid out frame for panel: {name}")

target_panel.SetFocus()
```

---

## ✅ Testing Checklist

### 1. Import Validation
```bash
python -c "from src.infrastructure.ui.view_manager import ViewManager; print('✓')"
python -c "from src.infrastructure.ui.wx_frame import SolitarioFrame; print('✓')"
```

### 2. Sizer Verification
```python
import wx
from src.infrastructure.ui.wx_frame import SolitarioFrame
app = wx.App()
frame = SolitarioFrame()
assert frame.panel_container.GetSizer() is not None
print('✓ Container has sizer')
```

### 3. Panel Registration Logs
```bash
python test.py
# Verify logs:
# ✓ "Added panel 'menu' to sizer"
# ✓ "Added panel 'gameplay' to sizer"
```

### 4. Menu Button Functionality
```bash
python test.py

# Test:
# 1. ENTER "Gioca" → Gameplay panel ✓
# 2. ESC → Menu ✓
# 3. TAB → "Opzioni"
# 4. ENTER → Options window ✓
# 5. ESC → Menu ✓
# 6. TAB → "Esci"
# 7. ENTER → Exit dialog ✓
```

### 5. Panel Swap Stability
```bash
# Stress test:
# - 10x "Gioca" → ESC → Menu
# - Verify: No crashes, layout correct
# - Timer runs during gameplay
```

### 6. Visual Check
```bash
# Verify:
# ✓ 1 window (600x450, centered)
# ✓ Menu: 3 buttons vertical
# ✓ Gameplay: "Partita in corso" label
# ✓ Smooth swap, no flicker
```

---

## 📝 Commit Message

```bash
git add test.py
git add src/infrastructure/ui/wx_frame.py
git add src/infrastructure/ui/view_manager.py

git commit -m "fix(ui): Fix panel sizer registration (critical)

Resolve panel visibility and button routing issues.

Root Causes:
1. panel_container had no sizer → children not layouted
2. ViewManager didn't add panels to sizer → invisible
3. Duplicate open_options() method → routing confusion
4. ViewManager lacked sizer reference → couldn't register
5. Layout refresh incomplete → edge cases

Fixed:
1. wx_frame.py: panel_container.SetSizer(container_sizer)
2. view_manager.py (__init__): Get container_sizer reference
3. view_manager.py (register_panel): Add panel to sizer
4. test.py: Remove duplicate open_options() method
5. view_manager.py (show_panel): Layout frame hierarchy

Testing:
- Menu buttons respond to ENTER ✅
- \"Gioca\" opens gameplay ✅
- \"Opzioni\" opens options ✅
- Panel swap smooth ✅
- Timer stable 30+ sec ✅

Fixes: Panel visibility, button routing, layout tree
Version: v1.7.3 (PATCH)"
```

---

## 🎯 Acceptance Criteria

**Functionality**:
- [ ] Menu buttons clickable with ENTER
- [ ] "Gioca" → Gameplay panel visible
- [ ] "Opzioni" → Options window opens
- [ ] "Esci" → Exit dialog shown
- [ ] Panel swap menu ↔ gameplay smooth
- [ ] TAB navigates menu buttons
- [ ] Timer works during gameplay
- [ ] ESC abandons game

**Architecture**:
- [ ] `panel_container` has sizer set
- [ ] `ViewManager` has `container_sizer` reference
- [ ] Panels added to sizer via `Add(panel, 1, wx.EXPAND)`
- [ ] `register_panel()` calls `container_sizer.Add()`
- [ ] `show_panel()` calls `Layout()` on container AND frame
- [ ] No duplicate `open_options()` in `test.py`
- [ ] Panels in layout tree (`GetContainingSizer()` not None)

**Testing**:
- [ ] Import modules: OK
- [ ] Container sizer not None: OK
- [ ] Panel registration logs: OK
- [ ] 10x panel swap: OK
- [ ] Visual verification: OK
- [ ] Button clicks: OK

---

## 🔗 Riferimenti

- [wxPython Panel Swap Pattern](https://stackoverflow.com/questions/31138061/wxpython-switch-between-multiple-panels)
- [Sizer Management](https://docs.wxpython.org/sizers_overview.html)
- [Layout Best Practices](https://wiki.wxpython.org/Getting%20Started#Layout)

**Pattern**: Container panel must have sizer, all children added via `sizer.Add()`, Show/Hide for swap.

---

## 📌 Verifica Finale

```bash
# 1. Check duplicate removed
grep -n "def open_options" test.py
# Output: (empty)

# 2. Check container sizer
grep -n "panel_container.SetSizer" src/infrastructure/ui/wx_frame.py
# Output: ~113: self.panel_container.SetSizer(container_sizer)

# 3. Check ViewManager sizer ref
grep -n "self.container_sizer" src/infrastructure/ui/view_manager.py
# Output: Multiple lines (init, Add)

# 4. Run app
python test.py
# Expected: All buttons work correctly
```

---

**Stato**: Ready for implementation  
**Prossimo**: Implementa 5 fix, testa, commit
