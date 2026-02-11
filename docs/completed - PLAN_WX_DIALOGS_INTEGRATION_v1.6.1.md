# PLAN: wxDialogs Integration in Application Flow (v1.6.1)

**Version**: v1.6.1  
**Date**: 2026-02-11  
**Status**: 📋 PLANNING COMPLETE - READY FOR IMPLEMENTATION  
**Priority**: HIGH  
**Type**: FEATURE INTEGRATION  
**Estimated Time**: 3.5-4 hours  
**Branch**: `copilot/implement-victory-flow-dialogs`

---

## Executive Summary

### Context

In v1.6.0, GitHub Copilot successfully implemented:
- ✅ `DialogProvider` abstract interface
- ✅ `WxDialogProvider` with wxPython native dialogs
- ✅ Integration in `GameEngine.end_game()` for victory/defeat flow

**Gap Identified**: wxDialogs are **NOT** integrated in the main application flow (`test.py`), which still uses `VirtualDialogBox` (TTS-only) for all interactive prompts (ESC confirmations, new game prompts, options save dialogs).

### Objective

Replace **ALL** `VirtualDialogBox` instances in `test.py` with native wxPython dialogs using `WxDialogProvider`, replicating the UX behavior of the legacy version (`scr/game_engine.py`).

### Impact

- **User Experience**: Native keyboard-navigable dialogs instead of virtual TTS prompts
- **Accessibility**: Better NVDA/JAWS integration with native wx widgets
- **Code Quality**: Remove complex dialog state management from event loop (modal dialogs = blocking)
- **Maintainability**: Centralized dialog logic in `SolitarioDialogManager`

### Success Criteria

- ✅ All 6 interactive prompts use wxDialogs (ESC, New Game, Exit, Options, Victory, Defeat)
- ✅ Graceful degradation if wxPython unavailable (fallback to TTS)
- ✅ Zero breaking changes (backward compatibility preserved)
- ✅ Double-ESC feature still functional
- ✅ NVDA/JAWS screen reader compatibility

---

## Architecture Analysis

### Current State (v1.6.0)

#### Infrastructure Layer
```
src/infrastructure/ui/
├── dialog_provider.py         ✅ Abstract interface (show_alert, show_yes_no, show_input)
├── wx_dialog_provider.py      ✅ wxPython implementation
└── dialog.py                  ⚠️ VirtualDialogBox (TTS-only, deprecated after v1.6.1)
```

#### Application Layer
```
src/application/
├── game_engine.py             ✅ Uses WxDialogProvider in end_game() only
└── gameplay_controller.py     ⚠️ No dialog integration
```

#### Entry Point
```
test.py                        ⚠️ Uses VirtualDialogBox for all prompts
                               ❌ No WxDialogProvider integration
                               ❌ Complex dialog event routing in handle_events()
```

### Target State (v1.6.1)

#### Infrastructure Layer
```
src/infrastructure/ui/
├── dialog_provider.py         ✅ No changes
├── wx_dialog_provider.py      ✅ No changes
└── dialog.py                  ⚠️ Kept for backward compat, deprecated
```

#### Application Layer
```
src/application/
├── game_engine.py             ✅ No changes (already integrated)
├── gameplay_controller.py     ✅ No changes (dialogs handled in test.py)
└── dialog_manager.py          🆕 NEW: SolitarioDialogManager
```

#### Entry Point
```
test.py                        ✅ Uses SolitarioDialogManager
                               ✅ Modal wxDialogs (no event loop routing)
                               ✅ Simplified handle_events() (-120 LOC)
```

---

## Gap Analysis

### Interactive Prompts in test.py (Current vs Target)

| Prompt | Current (v1.6.0) | Target (v1.6.1) | Method |
|--------|------------------|-----------------|--------|
| **ESC during gameplay** | VirtualDialogBox | wxDialog | `show_abandon_game_prompt()` |
| **N during gameplay** | VirtualDialogBox | wxDialog | `show_new_game_prompt()` |
| **ESC in game submenu** | VirtualDialogBox | wxDialog | `show_return_to_main_prompt()` |
| **ESC in main menu** | VirtualDialogBox | wxDialog | `show_exit_app_prompt()` |
| **Close options (modified)** | TTS virtual prompt | wxDialog | `show_options_save_prompt()` |
| **Victory/Defeat** | wxDialog ✅ | wxDialog ✅ | Already in `GameEngine.end_game()` |

### Code Complexity Reduction

**Before** (v1.6.0):
```python
# test.py handle_events() - ~180 LOC
if self.exit_dialog and self.exit_dialog.is_open:
    self.exit_dialog.handle_keyboard_events(event)
    continue

if self.return_to_main_dialog and self.return_to_main_dialog.is_open:
    self.return_to_main_dialog.handle_keyboard_events(event)
    continue

if self.abandon_game_dialog and self.abandon_game_dialog.is_open:
    # Double-ESC detection...
    self.abandon_game_dialog.handle_keyboard_events(event)
    continue

if self.new_game_dialog and self.new_game_dialog.is_open:
    self.new_game_dialog.handle_keyboard_events(event)
    continue
```

**After** (v1.6.1):
```python
# test.py handle_events() - ~60 LOC (wxDialogs are modal = blocking)
if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
    # No dialog state checks needed - modal dialogs handle everything
    result = self.dialog_manager.show_abandon_game_prompt()
    if result:
        self.confirm_abandon_game()
```

**Reduction**: -120 LOC in event loop, cleaner state management

---

## Implementation Plan

### STEP 1: Create SolitarioDialogManager

**File**: `src/application/dialog_manager.py` (NEW)

**Purpose**: Application-level dialog orchestration, wrapping `WxDialogProvider` with semantic methods.

**Public API**:
```python
class SolitarioDialogManager:
    def __init__(self, dialog_provider: Optional[DialogProvider] = None)
    
    @property
    def is_available(self) -> bool
    
    def show_abandon_game_prompt(self) -> bool
    def show_new_game_prompt(self) -> bool
    def show_return_to_main_prompt(self) -> bool
    def show_exit_app_prompt(self) -> bool
    def show_options_save_prompt(self) -> Optional[bool]
    def show_alert(self, title: str, message: str) -> None
```

**Key Features**:
- Graceful degradation: Returns `False` if wxPython unavailable
- Semantic method names: `show_abandon_game_prompt()` vs generic `show_yes_no()`
- Italian prompts: Pre-configured messages ("Vuoi abbandonare la partita?", etc)
- Type safety: `Optional[bool]` for save prompt (None = cancelled)

**Implementation Details**:
```python
def show_abandon_game_prompt(self) -> bool:
    """Show 'Abandon game?' confirmation dialog.
    
    Message: "Vuoi abbandonare la partita e tornare al menu di gioco?"
    
    Returns:
        True if user confirmed (Sì), False if cancelled (No/ESC)
    """
    if not self.is_available:
        return False  # Safe default: don't abandon without confirmation
    
    return self.dialogs.show_yes_no(
        title="Abbandono Partita",
        message="Vuoi abbandonare la partita e tornare al menu di gioco?",
        default_yes=True
    )
```

**Testing**:
- Unit test with mock DialogProvider
- Manual test with wxPython installed
- Manual test with wxPython uninstalled (degradation)

**Estimated Time**: 45 minutes

---

### STEP 2: Integrate DialogManager into test.py

**File**: `test.py`

**Changes**:

#### 2.1 Import and Initialize (10 min)

```python
# Add import (line ~35)
from src.application.dialog_manager import SolitarioDialogManager

# In __init__() after GameSettings (line ~130)
print("Inizializzazione dialog manager...")
self.dialog_manager = SolitarioDialogManager()
if self.dialog_manager.is_available:
    print("✓ Dialog nativi wxPython attivi")
else:
    print("⚠ wxPython non disponibile, uso fallback TTS")
```

#### 2.2 Replace Dialog Methods (40 min)

**Pattern**:
```python
# BEFORE (v1.6.0): VirtualDialogBox with event loop routing
def show_abandon_game_dialog(self) -> None:
    self.abandon_game_dialog = VirtualDialogBox(
        message="...",
        buttons=["Sì", "No"],
        on_confirm=self.confirm_abandon_game,
        on_cancel=self.close_abandon_dialog,
        screen_reader=self.screen_reader
    )
    self.abandon_game_dialog.open()

# AFTER (v1.6.1): Modal wxDialog with direct result
def show_abandon_game_dialog(self) -> None:
    result = self.dialog_manager.show_abandon_game_prompt()
    if result:
        self.confirm_abandon_game()
    else:
        self.close_abandon_dialog()
```

**Methods to Update**:
1. `show_abandon_game_dialog()` → Use `show_abandon_game_prompt()`
2. `show_new_game_dialog()` → Use `show_new_game_prompt()`
3. `show_return_to_main_dialog()` → Use `show_return_to_main_prompt()`
4. `show_exit_dialog()` → Use `show_exit_app_prompt()`

#### 2.3 Remove Old Dialog Attributes (5 min)

```python
# DELETE from __init__():
self.exit_dialog = None
self.return_to_main_dialog = None
self.abandon_game_dialog = None
self.new_game_dialog = None
```

#### 2.4 Clean Up handle_events() (30 min)

**Delete dialog state checks** (4 blocks, ~80 LOC):
```python
# DELETE PRIORITY 1-4 checks:
if self.exit_dialog and self.exit_dialog.is_open: ...
if self.return_to_main_dialog and self.return_to_main_dialog.is_open: ...
if self.abandon_game_dialog and self.abandon_game_dialog.is_open: ...
if self.new_game_dialog and self.new_game_dialog.is_open: ...
```

**Rationale**: wxDialogs are modal (blocking), pygame event loop automatically pauses during dialog display.

#### 2.5 Update Callback Methods (5 min)

**Simplify callbacks** (no dialog state management needed):
```python
def confirm_abandon_game(self) -> None:
    """Callback after user confirms abandon."""
    # No need to close dialog (already closed by modal behavior)
    self.last_esc_time = 0
    self.engine.reset_game()
    self._timer_expired_announced = False
    self.is_menu_open = True
    
    # TTS AFTER dialog closed
    if self.screen_reader:
        self.screen_reader.tts.speak("Partita abbandonata.", interrupt=True)
        pygame.time.wait(400)
        self.game_submenu.announce_welcome()
```

**Estimated Time**: 90 minutes

---

### STEP 3: Options Save Confirmation

**File**: `src/application/options_controller.py`

**Current Behavior** (v1.5.0):
- `close_window()` returns "modifiche non salvate..."
- Triggers `_awaiting_save_response` flag in `gameplay_controller.py`
- User presses S/N/ESC keys for action

**New Behavior** (v1.6.1):
- `close_window()` shows wx dialog "Salvare modifiche?"
- User interacts with native dialog (modal)
- Returns result: True=save, False=discard, None=cancel

**Changes**:

#### 3.1 Add DialogManager Parameter (5 min)

```python
class OptionsWindowController:
    def __init__(
        self, 
        settings: GameSettings, 
        dialog_manager: Optional['SolitarioDialogManager'] = None  # NEW
    ):
        self.settings = settings
        self.dialog_manager = dialog_manager  # Store reference
        self.is_open = False
        self.current_option = 0
        self.is_modified = False
        self.snapshot = {}
```

#### 3.2 Update close_window() Method (20 min)

```python
def close_window(self) -> str:
    """Close options with save confirmation (v1.6.1).
    
    Returns:
        TTS message describing action taken
    """
    if not self.is_open:
        return "La finestra opzioni è già chiusa."
    
    # Check for unsaved changes
    if self.is_modified:
        # NEW: Use wx dialog if available
        if self.dialog_manager and self.dialog_manager.is_available:
            result = self.dialog_manager.show_options_save_prompt()
            
            if result is True:
                # Save changes
                self.is_modified = False
                self.is_open = False
                return "Modifiche salvate. Finestra opzioni chiusa."
            
            elif result is False:
                # Discard changes
                self._restore_from_snapshot()
                self.is_modified = False
                self.is_open = False
                return "Modifiche scartate. Finestra opzioni chiusa."
            
            else:
                # result is None: User cancelled (ESC)
                return "Chiusura annullata. Finestra opzioni ancora aperta."
        
        else:
            # FALLBACK: TTS virtual prompt (backward compatible)
            return "Hai modifiche non salvate. Premi S per salvare, N per scartare, ESC per annullare."
    
    # No changes: Close immediately
    self.is_open = False
    return "Finestra opzioni chiusa."
```

#### 3.3 Wire DialogManager in test.py (5 min)

```python
# In test.py __init__() after gameplay_controller creation:
self.gameplay_controller = GamePlayController(...)

# NEW: Pass dialog_manager to options_controller
self.gameplay_controller.options_controller.dialog_manager = self.dialog_manager
```

#### 3.4 Remove Old S/N/ESC Handler (Optional Cleanup)

**File**: `src/application/gameplay_controller.py`

Remove `_handle_save_dialog()` method and `_awaiting_save_response` flag (now obsolete).

**Note**: This is optional cleanup, not critical for v1.6.1 functionality.

**Estimated Time**: 30 minutes

---

### STEP 4: Update Documentation

**Files**: `README.md`, `CHANGELOG.md`

#### 4.1 CHANGELOG.md (15 min)

Add v1.6.1 entry:

```markdown
## [v1.6.1] - 2026-02-12

### Changed
- **Dialog Integration**: Replaced ALL VirtualDialogBox (TTS-only) with native wxPython dialogs
  - ESC during gameplay → wx dialog "Vuoi abbandonare?"
  - New game (game running) → wx dialog "Vuoi abbandonare partita?"
  - Return to main menu → wx dialog "Vuoi tornare al menu principale?"
  - Exit application → wx dialog "Vuoi uscire?"
  - Options save confirmation → wx dialog "Salvare modifiche?"

### Added
- **SolitarioDialogManager**: Centralized dialog management class (~180 LOC)
  - `show_abandon_game_prompt()`: Game abandonment confirmation
  - `show_new_game_prompt()`: New game confirmation (when game running)
  - `show_return_to_main_prompt()`: Return to main menu confirmation
  - `show_exit_app_prompt()`: Exit application confirmation
  - `show_options_save_prompt()`: Options save/discard/cancel dialog
  - Graceful degradation if wxPython not available

### Removed
- **VirtualDialogBox** event loop routing from `test.py` (-120 LOC)
- Dialog state attributes (`exit_dialog`, `abandon_game_dialog`, etc)
- `_awaiting_save_response` flag (superseded by modal dialogs)

### Technical Details
- `src/application/dialog_manager.py`: NEW file (~180 LOC)
- `test.py`: -120 LOC (event handling), +30 LOC (DialogManager init)
- `src/application/options_controller.py`: +25 LOC (wx dialog integration)

### Backward Compatibility
- ✅ Fully backward compatible (falls back to TTS if wxPython unavailable)
- ✅ Double-ESC feature preserved (checked before dialog opens)
- ✅ Menu navigation unchanged

### Accessibility
- All wxDialogs keyboard-navigable (Tab, Enter, ESC, shortcuts S/N)
- Screen reader compatible (NVDA, JAWS tested on Windows)
- Modal dialogs prevent accidental input during confirmations
```

#### 4.2 README.md (15 min)

Update "Victory Flow & Native Dialogs" section:

```markdown
### Victory Flow & Native Dialogs (v1.6.0 + v1.6.1)

Il gioco usa dialog box native wxPython accessibili in **TUTTI** i contesti interattivi.

**Contesti con Dialog Nativi** (v1.6.1):
1. **ESC durante gameplay**: "Vuoi abbandonare la partita?"
2. **N durante gameplay**: "Una partita è già in corso. Vuoi abbandonarla?"
3. **ESC nel menu di gioco**: "Vuoi tornare al menu principale?"
4. **ESC nel menu principale**: "Vuoi uscire dall'applicazione?"
5. **Chiudi opzioni (modifiche)**: "Vuoi salvare le modifiche?"
6. **Fine partita (vittoria/sconfitta)**: Report completo + "Vuoi giocare ancora?"

**Caratteristiche**:
- ✨ **Dialog nativi wxPython**: Tutte le conferme usano widget nativi accessibili
- 🎮 **UX coerente**: Stesso comportamento della versione legacy `scr/`
- 📊 **Report finale dettagliato**: Statistiche complete, punteggio, prompt rivincita
- ⚙️ **Opzioni safe**: Dialog "Salvare modifiche?" previene perdita dati
- 🔄 **Double-ESC**: Uscita rapida durante gameplay (< 2 sec)

**Configurazione**:

```python
# Dialog nativi sono SEMPRE attivi se wxPython installato
# Per disabilitare (solo TTS), disinstalla wxPython:
pip uninstall wxPython

# L'applicazione continua a funzionare con fallback TTS
```

**Accessibilità**:
- Tutti i dialog navigabili solo da tastiera
- Compatibili con NVDA, JAWS (testato su Windows)
- Dialog modali prevengono input accidentale
- Shortcut keys: S (Sì), N (No), ESC (Annulla/Chiudi)
```

**Estimated Time**: 30 minutes

---

### STEP 5: Testing & Validation

**Manual Testing Scenarios** (45 min)

#### Scenario 1: ESC Durante Gameplay
1. Avvia partita
2. Esegui 2-3 mosse
3. Premi **ESC**
4. **VERIFY**: wxDialog "Vuoi abbandonare?" appare
5. Premi **S** (Sì)
6. **VERIFY**: Torna al menu, TTS "Partita abbandonata"

**Expected**:
- ✅ Dialog nativo con focus su "Sì"
- ✅ Shortcut S/N funzionano
- ✅ ESC nel dialog = ripresa gioco

#### Scenario 2: Double-ESC (Fast Exit)
1. Avvia partita
2. Premi **ESC** + **ESC** rapidamente (< 2 sec)
3. **VERIFY**: NO dialog, abbandono immediato
4. **VERIFY**: TTS "Uscita rapida!"

**Expected**:
- ✅ Nessun dialog mostrato
- ✅ Uscita istantanea al menu

#### Scenario 3: Nuova Partita Durante Gameplay
1. Avvia partita
2. Premi **N**
3. **VERIFY**: wxDialog "Partita in corso..."
4. Premi **S** (Sì)
5. **VERIFY**: Nuova partita inizia, vecchia abbandonata

**Expected**:
- ✅ Dialog blocca input di gioco
- ✅ Sì → nuova partita
- ✅ No → continua partita corrente

#### Scenario 4: Opzioni - Salva Modifiche
1. Menu → Opzioni
2. Modifica difficoltà
3. Premi **O** (chiudi)
4. **VERIFY**: wxDialog "Modifiche non salvate..."
5. Premi **S** (Salva)
6. **VERIFY**: Modifiche persistite

**Expected**:
- ✅ Dialog appare solo se modifiche presenti
- ✅ Sì → salva, No → scarta, ESC → resta in opzioni

#### Scenario 5: Vittoria + Rivincita
1. Completa partita o CTRL+ALT+W
2. **VERIFY**: TTS report + wxDialog "Rivincita?"
3. Premi **S** (Sì)
4. **VERIFY**: Nuova partita inizia

**Expected**:
- ✅ Report vocale completo (TTS)
- ✅ Dialog per rivincita
- ✅ Sì → nuova partita, No → menu

#### Scenario 6: Fallback Mode (wxPython Unavailable)
1. Disinstalla wxPython: `pip uninstall wxPython`
2. Avvia `python test.py`
3. **VERIFY**: Console log "⚠ wxPython non disponibile"
4. Premi ESC durante gameplay
5. **VERIFY**: TTS prompt "Vuoi abbandonare?" (no dialog nativo)
6. Premi **S/N** keys
7. **VERIFY**: App continua a funzionare

**Expected**:
- ✅ Nessun crash
- ✅ Fallback a prompt TTS
- ✅ Funzionalità completa preservata

**NVDA Compatibility Check** (15 min):
- Avvia NVDA screen reader
- Esegui scenari 1-5
- **VERIFY**: NVDA legge titoli e messaggi dialog
- **VERIFY**: NVDA annuncia focus su bottoni
- **VERIFY**: NVDA legge shortcut keys

**Estimated Time**: 60 minutes

---

## Total Time Breakdown

| Step | Task | Time | Running Total |
|------|------|------|---------------|
| 1 | Create SolitarioDialogManager | 45 min | 45 min |
| 2 | Integrate into test.py | 90 min | 135 min |
| 3 | Options save confirmation | 30 min | 165 min |
| 4 | Documentation updates | 30 min | 195 min |
| 5 | Testing & validation | 60 min | 255 min |

**Total Estimated Time**: **255 minutes** (~4.25 hours)  
**Contingency Buffer**: +15 min for unexpected issues  
**Final Estimate**: **~4.5 hours**

---

## Acceptance Criteria

### Functional Requirements (7/7)
- [ ] ESC during gameplay shows wx dialog "Abbandona?"
- [ ] N during gameplay shows wx dialog "Nuova partita?"
- [ ] ESC in game submenu shows wx dialog "Torna al menu?"
- [ ] ESC in main menu shows wx dialog "Esci?"
- [ ] Close options (modified) shows wx dialog "Salvare?"
- [ ] Victory/Defeat shows wx dialog "Rivincita?" (already v1.6.0 ✅)
- [ ] Double-ESC works without showing dialog (< 2 sec threshold)

### Code Quality (5/5)
- [ ] SolitarioDialogManager has 6 public methods with docstrings
- [ ] Graceful degradation if wxPython unavailable (returns False)
- [ ] Zero breaking changes (backward compatible)
- [ ] Modal dialogs (no event loop state pollution)
- [ ] Type hints complete (`Optional[bool]` for save prompt)

### Accessibility (4/4)
- [ ] All dialogs keyboard-navigable (Tab, Enter, ESC)
- [ ] Shortcut keys work (S/N for Sì/No)
- [ ] Focus defaults correct (Sì for abandons, No for exit)
- [ ] NVDA/JAWS compatibility verified (Windows test)

### Documentation (3/3)
- [ ] CHANGELOG v1.6.1 entry complete with all changes
- [ ] README updated with 6 dialog contexts
- [ ] Planning and TODO docs created in `docs/`

---

## Architectural Decisions

### Why SolitarioDialogManager?

**Alternative 1**: Use `WxDialogProvider` directly in `test.py`
```python
# ❌ Too low-level, repetitive code
result = self.wx_provider.show_yes_no(
    title="Abbandono Partita",
    message="Vuoi abbandonare la partita e tornare al menu di gioco?",
    default_yes=True
)
```

**Alternative 2**: Keep `VirtualDialogBox` for consistency
```python
# ❌ Inferior UX, complex event loop routing
self.abandon_dialog = VirtualDialogBox(...)
self.abandon_dialog.open()
# ... then handle events in handle_events() with priority checks
```

**Chosen**: `SolitarioDialogManager`
```python
# ✅ Semantic, maintainable, testable
result = self.dialog_manager.show_abandon_game_prompt()
if result:
    self.confirm_abandon_game()
```

**Rationale**:
- Separates application concerns from infrastructure (Clean Architecture)
- Provides semantic methods (`show_abandon_game_prompt` vs generic `show_yes_no`)
- Centralizes all prompts for easy maintenance
- Easier to test (mock DialogProvider)
- Graceful degradation built-in

### Why Remove VirtualDialogBox from Event Loop?

**Before** (v1.6.0):
```python
def handle_events(self):
    # PRIORITY 1: Exit dialog
    if self.exit_dialog and self.exit_dialog.is_open:
        self.exit_dialog.handle_keyboard_events(event)
        return  # Block all input
    
    # PRIORITY 2: Return dialog
    if self.return_to_main_dialog and self.return_to_main_dialog.is_open:
        self.return_to_main_dialog.handle_keyboard_events(event)
        return
    
    # ... 4 more priority checks (80 LOC total)
```

**After** (v1.6.1):
```python
def handle_events(self):
    # wxDialogs are MODAL (blocking)
    # No event routing needed - dialog handles everything
    if event.key == pygame.K_ESCAPE:
        result = self.dialog_manager.show_abandon_game_prompt()
        if result:
            self.confirm_abandon_game()
```

**Rationale**:
- wxDialogs are **modal** (block pygame event loop automatically)
- No need for manual event routing or dialog state flags
- -120 LOC in `handle_events()` method
- Cleaner, more maintainable code

### Why Keep Double-ESC Feature?

**Pattern**: Check ESC timing BEFORE showing dialog
```python
if event.key == pygame.K_ESCAPE:
    current_time = time.time()
    if current_time - self.last_esc_time <= 2.0:
        # Double-ESC: Instant exit (no dialog)
        self.confirm_abandon_game()
        return
    
    # First ESC: Show dialog
    self.last_esc_time = current_time
    result = self.dialog_manager.show_abandon_game_prompt()
```

**Rationale**:
- Power user feature (requested in v1.4.2 #27)
- Skips confirmation for experienced users
- No conflict with modal dialogs (check happens before dialog opens)

---

## Risks & Mitigation

### Risk 1: wxPython Import Failure

**Scenario**: User environment doesn't have wxPython installed

**Impact**: App crashes on `import wx` in `WxDialogProvider`

**Mitigation**:
- ✅ Graceful degradation in `SolitarioDialogManager.__init__()`
- ✅ `is_available` property returns `False`
- ✅ All methods return safe defaults (`False` = don't proceed)
- ✅ Console warning: "⚠ wxPython non disponibile, uso fallback TTS"

**Test**: Scenario 6 validates fallback mode

### Risk 2: Modal Dialogs Block Event Loop

**Scenario**: Dialog open → pygame event loop pauses → timer events stop

**Impact**: Game timer doesn't update during dialog display

**Mitigation**:
- ✅ This is **intended behavior** (pause game during confirmation)
- ✅ Timer resumes after dialog closes
- ✅ No timer check events fired while dialog modal (safe)

**Note**: Not a bug, it's a feature (prevents timer expiration during dialog)

### Risk 3: NVDA Screen Reader Compatibility

**Scenario**: NVDA doesn't read wxDialog content correctly

**Impact**: Blind users can't interact with dialogs

**Mitigation**:
- ✅ wxPython has built-in NVDA support (Windows accessibility API)
- ✅ Already tested in v1.6.0 STEP 5 (victory flow)
- ✅ Will re-test in Scenario 5 (NVDA compatibility check)

**Confidence**: High (wxPython is industry-standard for accessible Python GUIs)

### Risk 4: Double-ESC Timing Issues

**Scenario**: User presses ESC twice, but second ESC registers after 2.0 sec threshold

**Impact**: Dialog shows instead of instant exit

**Mitigation**:
- ✅ 2.0 sec threshold is generous (user feedback in v1.4.2)
- ✅ Clear TTS feedback distinguishes behaviors
- ✅ No data loss risk (both paths safe)

**Note**: Edge case, not critical

---

## Backward Compatibility

### Changes That Break Legacy Code

**None**. All changes are additive or internal refactoring.

### Migration Path for Users

**From v1.6.0 to v1.6.1**:
1. Pull latest code: `git pull origin copilot/implement-victory-flow-dialogs`
2. Install dependencies: `pip install -r requirements.txt` (wxPython already present)
3. Run app: `python test.py`
4. **No configuration changes needed** (auto-detects wxPython)

**Fallback Mode** (no wxPython):
1. App auto-detects missing wxPython
2. Falls back to TTS virtual prompts (v1.4.2 behavior)
3. Full functionality preserved (no feature loss)

### Deprecated Components

**VirtualDialogBox** (kept for backward compat):
- Still available in `src/infrastructure/ui/dialog.py`
- No longer used in `test.py` (deprecated)
- Will be removed in v2.0.0 (breaking change release)

---

## Success Metrics

### Quantitative
- ✅ -120 LOC in `test.py` event loop (30% reduction)
- ✅ +180 LOC in `dialog_manager.py` (centralized)
- ✅ 6/6 dialog contexts use wxPython (100% coverage)
- ✅ 0 breaking changes (100% backward compatible)

### Qualitative
- ✅ NVDA reads all dialog content correctly
- ✅ Keyboard navigation feels native (Tab/Enter/ESC)
- ✅ Code easier to maintain (no complex state management)
- ✅ UX matches legacy version behavior

### User Feedback Criteria
- ✅ Blind users report wxDialogs more accessible than VirtualDialogBox
- ✅ No confusion with dialog shortcuts (S/N clearly announced)
- ✅ Double-ESC feature discovery (power users find it naturally)

---

## Dependencies

**Required**:
- Python ≥ 3.8 (type hints with `Optional`)
- pygame ≥ 2.0.0 (event loop)
- wxPython ≥ 4.1.0 (native dialogs)

**Optional**:
- NVDA screen reader (testing only)

**Note**: wxPython is **optional runtime dependency** (graceful degradation if missing)

---

## Related Documents

- `docs/TODO_WX_DIALOGS_INTEGRATION_v1.6.1.md`: Detailed implementation checklist
- `docs/TODO_VICTORY_FLOW_DIALOGS.md`: v1.6.0 foundation (DialogProvider creation)
- `CHANGELOG.md`: v1.6.1 release notes
- `README.md`: User-facing dialog documentation

---

## Approval & Sign-Off

**Author**: Perplexity AI Assistant  
**Reviewer**: Nemex81  
**Status**: ✅ APPROVED FOR IMPLEMENTATION  
**Date**: 2026-02-11  
**Next Step**: Create `TODO_WX_DIALOGS_INTEGRATION_v1.6.1.md` with atomic checklist

---

**END OF PLANNING DOCUMENT**
