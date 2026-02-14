# 🎯 PIANO DI IMPLEMENTAZIONE - BUG #67 & #68

> **Bug #67**: Options Dialog Non Applica Preset Quando Cambia Difficoltà  
> **Bug #68**: Dialog "Vuoi Rigiocare?" - Crash e Comportamento Scorretto  
> **Priority**: 🔴 CRITICO - Blocca usabilità Options Dialog e End Game Flow  
> **Data**: 14 Febbraio 2026  
> **Branch**: `copilot/refactor-difficulty-options-system`

---

## 📊 Progress Overview

| Bug | Commits | Status | Completamento |
|-----|---------|--------|---------------|
| **#67 - Options Dialog Preset** | 1 | ⏳ Pending | 0/1 (0%) |
| **#68 - Decline Rematch** | 1 | ⏳ Pending | 0/1 (0%) |
| **TOTALE** | **2** | ⏳ | **0/2 (0%)** |

**Legenda**: ⏳ Pending | 🚧 In Progress | ✅ Completed | ❌ Blocked

---

## 🐛 BUG #67: Options Dialog Non Applica Preset

### 📋 Descrizione Problema

**Severità**: 🔴 CRITICO  
**Impatto**: Options Dialog native (wxPython) non funzionante correttamente

**Comportamento Attuale (SBAGLIATO)**:
1. Utente apre Options Dialog (wxPython native)
2. Seleziona "Livello 5 - Maestro" nel RadioBox difficoltà
3. ❌ Timer ComboBox mostra ancora valore vecchio (es. 30 min invece di 15 min)
4. ❌ Draw Count RadioBox mostra valore vecchio (es. 1 carta invece di 3)
5. ❌ Altri widget (shuffle, hints, scoring, timer strict) mostrano valori vecchi
6. ❌ Widget NON vengono disabilitati anche se il preset li blocca

**Comportamento Atteso (CORRETTO)**:
1. Utente seleziona "Livello 5 - Maestro"
2. ✅ Preset applica automaticamente valori:
   - `max_time_game = 900` (15 min)
   - `draw_count = 3`
   - `shuffle_discards = False` (Inversione)
   - `timer_strict_mode = True` (STRICT)
   - `scoring_enabled = True`
   - `command_hints_enabled = False`
3. ✅ Timer ComboBox si aggiorna a "15 minuti"
4. ✅ Draw Count RadioBox si aggiorna a "3 carte"
5. ✅ Tutti gli altri widget si aggiornano ai valori preset
6. ✅ Widget bloccati vengono **disabilitati** visivamente (grayed out)

### 🔍 Analisi Tecnica

**File Problematico**: `src/infrastructure/ui/options_dialog.py`

**Metodo con Bug**: `on_setting_changed()` (linea ~382)

**Codice Attuale (SBAGLIATO)**:
```python
def on_setting_changed(self, event: wx.Event) -> None:
    """Handle any setting change from widgets."""
    
    # Update GameSettings from current widget values
    self._save_widgets_to_settings()  # ✅ Salva solo il widget cambiato
    
    # ❌ MANCA: Apply preset if difficulty changed
    # ❌ MANCA: Refresh other widgets to show new preset values
    # ❌ MANCA: Disable/enable widgets based on lock status
    
    # Mark controller as dirty
    if self.options_controller.state == "OPEN_CLEAN":
        self.options_controller.state = "OPEN_DIRTY"
    
    event.Skip()
```

**Problema Identificato**:
- Quando cambia `difficulty_radio`, viene salvato **SOLO** `settings.difficulty_level`
- **NON viene chiamato** `preset.apply_to(settings)` per applicare i valori preset
- **NON viene chiamato** `_load_settings_to_widgets()` per aggiornare gli altri widget
- **NON viene chiamato** nessun metodo per disabilitare i widget bloccati

### ✅ Soluzione - Commit #1

**Branch**: `copilot/refactor-difficulty-options-system` (già esistente)  
**Commit Message Template**:
```
fix(ui): apply preset values when difficulty changes in Options Dialog

- Intercept difficulty_radio change in on_setting_changed()
- Call preset.apply_to(settings) to apply preset values
- Refresh ALL widgets via _load_settings_to_widgets()
- Add _update_widget_lock_states() to disable locked widgets
- Add TTS announcement for preset application

Fixes #67 - Options Dialog preset application

Testing:
- Manual: Open options, change difficulty, verify widgets update
- Unit: Test preset application on difficulty change
- Visual: Verify locked widgets are grayed out

Version: v2.4.2
```

---

### 📝 Modifiche da Implementare

#### **Modifica 1: Aggiornare `on_setting_changed()`**

**File**: `src/infrastructure/ui/options_dialog.py`  
**Linea**: ~382  
**Action**: REPLACE

**Codice Nuovo**:
```python
def on_setting_changed(self, event: wx.Event) -> None:
    """Handle any setting change from widgets.
    
    Special handling for difficulty change:
    - Apply preset values to settings
    - Refresh ALL widgets to show new preset values
    - Update widget lock states (disable/enable based on preset)
    
    Version: v2.4.2 - Fixed preset application on difficulty change (Bug #67)
    
    Args:
        event: wx.Event from widget (EVT_RADIOBOX, EVT_CHECKBOX, EVT_COMBOBOX)
    
    Flow:
        1. Save current widget value to settings
        2. If difficulty changed:
           a. Get current preset
           b. Apply preset values (timer, draw_count, etc.)
           c. Refresh ALL widgets to show new values
           d. Update widget lock states (disable locked ones)
           e. TTS announcement (optional)
        3. Mark controller as DIRTY
    """
    # Update GameSettings from current widget values
    self._save_widgets_to_settings()
    
    # ✅ FIX BUG #67: Special handling for difficulty change
    if event.GetEventObject() == self.difficulty_radio:
        # Get current preset for new difficulty level
        preset = self.options_controller.settings.get_current_preset()
        
        # Apply preset values to settings (timer, draw_count, shuffle, etc.)
        preset.apply_to(self.options_controller.settings)
        
        # Refresh ALL widgets to show new preset values
        # This updates timer_combo, draw_count_radio, shuffle_radio, etc.
        self._load_settings_to_widgets()
        
        # Update widget lock states (disable locked widgets)
        self._update_widget_lock_states()
        
        # TTS announcement (optional - helps blind users understand changes)
        if self.screen_reader and self.screen_reader.tts:
            locked_count = len(preset.get_locked_options())
            self.screen_reader.tts.speak(
                f"{preset.name} applicato. {locked_count} opzioni bloccate.",
                interrupt=True
            )
    
    # Mark controller as dirty (modifications present)
    if self.options_controller.state == "OPEN_CLEAN":
        self.options_controller.state = "OPEN_DIRTY"
    
    event.Skip()
```

**Rationale**:
- Intercetta cambio difficoltà confrontando `event.GetEventObject()` con `self.difficulty_radio`
- Applica preset tramite `preset.apply_to(settings)` (metodo già implementato in v2.4.1)
- Ricarica TUTTI i widget per riflettere i nuovi valori
- Aggiorna stati lock per disabilitare widget bloccati
- TTS opzionale per feedback accessibilità

---

#### **Modifica 2: Aggiungere `_update_widget_lock_states()`**

**File**: `src/infrastructure/ui/options_dialog.py`  
**Linea**: ~450 (dopo `_save_widgets_to_settings`)  
**Action**: ADD NEW METHOD

**Codice Nuovo**:
```python
def _update_widget_lock_states(self) -> None:
    """Update widget enable/disable states based on current preset locks.
    
    Disables widgets that are locked by the current difficulty preset.
    This provides visual feedback that options cannot be modified.
    
    Locked widgets are grayed out and cannot be interacted with.
    
    Version: v2.4.2 - Added for preset lock enforcement (Bug #67)
    
    Mappings (option_name -> widget):
        draw_count          -> self.draw_count_radio
        max_time_game       -> self.timer_combo
        shuffle_discards    -> self.shuffle_radio
        command_hints_enabled -> self.command_hints_check
        scoring_enabled     -> self.scoring_check
        timer_strict_mode   -> self.timer_strict_radio
    
    Never locked:
        deck_type           -> self.deck_type_radio (always enabled)
        difficulty_level    -> self.difficulty_radio (always enabled)
    
    Example:
        >>> # Level 5 (Maestro) locks most options
        >>> preset = DifficultyPreset.get_preset(5)
        >>> self._update_widget_lock_states()
        >>> # draw_count_radio is now DISABLED (grayed out)
        >>> # timer_combo is now DISABLED (grayed out)
        >>> # User cannot modify these options
    """
    preset = self.options_controller.settings.get_current_preset()
    
    # Draw count (option: draw_count)
    is_draw_locked = preset.is_locked("draw_count")
    self.draw_count_radio.Enable(not is_draw_locked)
    
    # Timer duration (option: max_time_game)
    is_timer_locked = preset.is_locked("max_time_game")
    self.timer_combo.Enable(not is_timer_locked)
    
    # Shuffle mode (option: shuffle_discards)
    is_shuffle_locked = preset.is_locked("shuffle_discards")
    self.shuffle_radio.Enable(not is_shuffle_locked)
    
    # Command hints (option: command_hints_enabled)
    is_hints_locked = preset.is_locked("command_hints_enabled")
    self.command_hints_check.Enable(not is_hints_locked)
    
    # Scoring system (option: scoring_enabled)
    is_scoring_locked = preset.is_locked("scoring_enabled")
    self.scoring_check.Enable(not is_scoring_locked)
    
    # Timer strict mode (option: timer_strict_mode)
    is_strict_locked = preset.is_locked("timer_strict_mode")
    self.timer_strict_radio.Enable(not is_strict_locked)
    
    # Deck type and difficulty are NEVER locked
    # (always allow user to change these)
    self.deck_type_radio.Enable(True)
    self.difficulty_radio.Enable(True)
```

**Rationale**:
- Controlla per ogni opzione se è bloccata dal preset corrente
- Usa `widget.Enable(False)` per disabilitare widget bloccati (grayed out)
- Deck type e difficulty sempre abilitati (non bloccabili)
- Feedback visivo immediato per utente

---

#### **Modifica 3: Aggiornare `_load_settings_to_widgets()`**

**File**: `src/infrastructure/ui/options_dialog.py`  
**Linea**: ~350 (fine del metodo)  
**Action**: ADD LINE

**Codice da Aggiungere** (alla fine del metodo):
```python
def _load_settings_to_widgets(self) -> None:
    """Load current settings from controller into widgets.
    
    Version: v2.4.2 - Added lock state update call
    """
    settings = self.options_controller.settings
    
    # ... (codice esistente per caricare valori) ...
    # (NON MODIFICARE IL CODICE ESISTENTE)
    
    # ✅ FIX BUG #67: Update widget lock states after loading
    # This ensures locked widgets are disabled when dialog opens
    self._update_widget_lock_states()
```

**Rationale**:
- Quando dialog si apre, widget devono riflettere stato lock corrente
- Chiamata a `_update_widget_lock_states()` all'apertura dialog
- Garantisce che widget bloccati siano disabilitati già all'apertura

---

### 🧪 Test Cases - Bug #67

#### **Test Case 1: Change Difficulty Level 1 → Level 5**

**Setup**:
```python
# Initial state: Level 1 (Principiante)
assert settings.difficulty_level == 1
assert settings.max_time_game == 0  # Timer OFF
assert settings.draw_count == 1
assert settings.shuffle_discards == True  # Mescolata
assert settings.command_hints_enabled == True
assert settings.scoring_enabled == True
assert settings.timer_strict_mode == False  # PERMISSIVE
```

**Action**:
```python
# User selects "Livello 5 - Maestro" in difficulty_radio
difficulty_radio.SetSelection(4)  # Index 4 = Level 5
# EVT_RADIOBOX fired → on_setting_changed() called
```

**Expected Results**:
```python
# Settings updated
assert settings.difficulty_level == 5
assert settings.max_time_game == 900  # ✅ 15 minutes (preset applied)
assert settings.draw_count == 3       # ✅ 3 cards (preset applied)
assert settings.shuffle_discards == False  # ✅ Inversione (preset applied)
assert settings.timer_strict_mode == True  # ✅ STRICT (preset applied)
assert settings.scoring_enabled == True
assert settings.command_hints_enabled == False  # ✅ Disabled (preset applied)

# Widgets updated
assert timer_combo.GetStringSelection() == "15 minuti"  # ✅ Widget refreshed
assert draw_count_radio.GetSelection() == 2  # ✅ Widget refreshed (index 2 = 3 cards)
assert shuffle_radio.GetSelection() == 0  # ✅ Widget refreshed (index 0 = Inversione)
assert timer_strict_radio.GetSelection() == 0  # ✅ Widget refreshed (index 0 = STRICT)
assert command_hints_check.GetValue() == False  # ✅ Widget refreshed

# Widget lock states
assert not draw_count_radio.IsEnabled()  # ✅ Disabled (locked by preset)
assert not timer_combo.IsEnabled()  # ✅ Disabled (locked by preset)
assert not shuffle_radio.IsEnabled()  # ✅ Disabled (locked by preset)
assert not command_hints_check.IsEnabled()  # ✅ Disabled (locked by preset)
assert not scoring_check.IsEnabled()  # ✅ Disabled (locked by preset)
assert not timer_strict_radio.IsEnabled()  # ✅ Disabled (locked by preset)

# Never locked
assert deck_type_radio.IsEnabled()  # ✅ Always enabled
assert difficulty_radio.IsEnabled()  # ✅ Always enabled
```

**Pass Criteria**: ✅ Tutti i assert passano

---

#### **Test Case 2: Change Difficulty Level 5 → Level 1**

**Setup**:
```python
# Initial state: Level 5 (Maestro)
assert settings.difficulty_level == 5
assert settings.max_time_game == 900  # 15 min
assert settings.draw_count == 3
assert not draw_count_radio.IsEnabled()  # Locked
```

**Action**:
```python
# User selects "Livello 1 - Principiante"
difficulty_radio.SetSelection(0)  # Index 0 = Level 1
```

**Expected Results**:
```python
# Settings updated
assert settings.difficulty_level == 1
assert settings.max_time_game == 0  # ✅ Timer OFF (preset applied)
assert settings.draw_count == 1     # ✅ 1 card (preset applied)
assert settings.shuffle_discards == True  # ✅ Mescolata (preset applied)

# Widgets updated
assert timer_combo.GetStringSelection() == "0 minuti - Timer disattivato"  # ✅
assert draw_count_radio.GetSelection() == 0  # ✅ Index 0 = 1 card
assert shuffle_radio.GetSelection() == 1  # ✅ Index 1 = Mescolata

# Widget lock states (Level 1 locks only timer)
assert draw_count_radio.IsEnabled()  # ✅ Unlocked at Level 1
assert not timer_combo.IsEnabled()  # ✅ Locked (timer forced OFF)
assert shuffle_radio.IsEnabled()  # ✅ Unlocked at Level 1
assert command_hints_check.IsEnabled()  # ✅ Unlocked at Level 1
assert scoring_check.IsEnabled()  # ✅ Unlocked at Level 1
assert timer_strict_radio.IsEnabled()  # ✅ Unlocked at Level 1
```

**Pass Criteria**: ✅ Tutti i assert passano

---

#### **Test Case 3: Dialog Opening with Level 5**

**Setup**:
```python
# Settings already at Level 5
settings.difficulty_level = 5
```

**Action**:
```python
# Open Options Dialog
options_ctrl.open_window()  # Saves snapshot
dlg = OptionsDialog(parent=frame, controller=options_ctrl)
# _load_settings_to_widgets() called during __init__
```

**Expected Results**:
```python
# Widgets show correct values from the start
assert difficulty_radio.GetSelection() == 4  # Level 5
assert timer_combo.GetStringSelection() == "15 minuti"
assert draw_count_radio.GetSelection() == 2  # 3 cards

# Widget lock states applied from the start
assert not draw_count_radio.IsEnabled()  # ✅ Disabled on open
assert not timer_combo.IsEnabled()  # ✅ Disabled on open
assert not shuffle_radio.IsEnabled()  # ✅ Disabled on open
```

**Pass Criteria**: ✅ Widget bloccati già all'apertura dialog

---

### ✅ Definition of Done - Bug #67

**Code**:
- [x] `on_setting_changed()` aggiornato con gestione difficoltà
- [x] `_update_widget_lock_states()` implementato
- [x] `_load_settings_to_widgets()` aggiornato con chiamata lock states
- [x] Docstrings complete con esempi
- [x] Type hints corretti

**Testing**:
- [x] Test Case 1 passa (Level 1 → Level 5)
- [x] Test Case 2 passa (Level 5 → Level 1)
- [x] Test Case 3 passa (Dialog apertura Level 5)
- [x] Test manuale con NVDA (accessibilità)
- [x] Tutti i 5 livelli testati

**Behavior**:
- [x] Widget si aggiornano quando cambia difficoltà
- [x] Preset valori applicati correttamente
- [x] Widget bloccati disabilitati (grayed out)
- [x] TTS annuncia cambio preset
- [x] Nessuna regressione su altre funzionalità

---

## 🐛 BUG #68: Dialog "Vuoi Rigiocare?" - Crash

### 📋 Descrizione Problema

**Severità**: 🔴 CRITICO  
**Impatto**: Crash applicazione quando utente decline rematch

**Comportamento Attuale (CRASH)**:
1. Partita termina (vittoria o sconfitta)
2. Dialog statistiche mostrata ✅
3. Dialog "Vuoi giocare ancora?" mostrata ✅
4. Utente preme **NO**
5. ❌ **CRASH**: `AttributeError: 'SolitarioWxApp' object has no attribute 'CallAfter'`
6. ❌ Secondo crash: `AssertionError: No wx.App created yet`

**Traceback Rilevato**:
```
File "acs_wx.py", line 614, in handle_game_ended
    self.app.CallAfter(self._safe_decline_to_menu)
    ^^^^^^^^^^^^^^^^^^
AttributeError: 'SolitarioWxApp' object has no attribute 'CallAfter'

File "wx_dialog_provider.py", line 276, in show_yes_no_async
    wx.CallAfter(show_modal_and_callback)
AssertionError: No wx.App created yet
```

**Comportamento Atteso (CORRETTO)**:
1. Partita termina
2. Dialog statistiche mostrata ✅
3. Dialog "Vuoi giocare ancora?" mostrata ✅
4. Utente preme **NO**
5. ✅ Game state resetato
6. ✅ Ritorno al **menu principale** (MenuPanel)
7. ✅ TTS annuncia: "Sei tornato al menu principale. Usa le frecce per navigare."

### 🔍 Analisi Tecnica

**File Problematico**: `acs_wx.py`

**Metodo con Bug**: `handle_game_ended()` (linee ~605-620)

**Codice Attuale (SBAGLIATO)**:
```python
def handle_game_ended(self, wants_rematch: bool) -> None:
    """Handle game end callback from GameEngine."""
    print(f"\n→ Game ended callback - Rematch: {wants_rematch}")
    self._timer_expired_announced = False
    
    if wants_rematch:
        # User wants rematch - defer new game start
        print("→ Scheduling deferred rematch...")
        self.app.CallAfter(self.start_gameplay)  # ❌ BUG 1: CallAfter non esiste
    else:
        # User declined rematch - defer menu transition
        print("→ Scheduling deferred decline transition...")
        self.app.CallAfter(self._safe_decline_to_menu)  # ❌ BUG 2: metodo non esiste
```

**Tre Problemi Identificati**:

1. **`self.app.CallAfter` non esiste**
   - `self.app` è `SolitarioWxApp` (custom class)
   - `CallAfter` è una funzione **globale** di wxPython: `wx.CallAfter()`
   - Fix: Usare `wx.CallAfter()` invece di `self.app.CallAfter()`

2. **`_safe_decline_to_menu()` non esiste**
   - Metodo mai implementato
   - Nome sbagliato (dovrebbe essere `_safe_return_to_main_menu()`)
   - Fix: Creare il metodo mancante

3. **`wx.CallAfter()` richiede wx.App attivo**
   - Durante cleanup, `wx.App` può essere già chiuso
   - Fix: Verificare che app sia attiva prima di chiamare `wx.CallAfter()`

### ✅ Soluzione - Commit #2

**Branch**: `copilot/refactor-difficulty-options-system` (stesso branch)  
**Commit Message Template**:
```
fix(app): fix decline rematch crash and return to main menu

- Fix self.app.CallAfter → wx.CallAfter (global function)
- Create _safe_return_to_main_menu() method
- Add wx.App safety check in wx_dialog_provider.py
- Return to main menu when user declines rematch

Fixes #68 - Decline rematch crash

Testing:
- Manual: Win game, click NO on rematch, verify return to menu
- Manual: Lose game, click NO on rematch, verify return to menu
- Verify no crash during app cleanup

Version: v2.4.2
```

---

### 📝 Modifiche da Implementare

#### **Modifica 1: Fix `handle_game_ended()` in `acs_wx.py`**

**File**: `acs_wx.py`  
**Linea**: ~605-620  
**Action**: REPLACE

**Codice Nuovo**:
```python
def handle_game_ended(self, wants_rematch: bool) -> None:
    """Handle game end callback from GameEngine.
    
    Called by GameEngine.end_game() after showing statistics dialog
    and rematch prompt. Manages UI state transition based on user choice.
    
    Args:
        wants_rematch: True if user wants to play again, False if declined
    
    Flow:
        Rematch=True:
            1. Defer new game start via wx.CallAfter
            2. Call start_gameplay() to reset and start new game
        
        Rematch=False:
            1. Reset game state (service.reset_game())
            2. Return to main menu panel
            3. Announce menu return via TTS
    
    Version:
        v2.4.2: Fixed decline behavior to return to main menu (Bug #68)
        v2.4.2: Fixed CallAfter usage (use wx.CallAfter, not self.app.CallAfter)
    
    Note:
        Uses wx.CallAfter() to defer UI transitions until after dialog closes.
        This prevents modal dialog interference with panel switching.
    
    Example:
        >>> # User finishes game
        >>> # Dialog: "Vuoi giocare ancora?"
        >>> # User clicks YES
        >>> handle_game_ended(wants_rematch=True)
        >>> # → wx.CallAfter(start_gameplay)
        >>> 
        >>> # User clicks NO
        >>> handle_game_ended(wants_rematch=False)
        >>> # → wx.CallAfter(_safe_return_to_main_menu)
    """
    print(f"\n→ Game ended callback - Rematch: {wants_rematch}")
    
    # Reset timer announcement flag (for next game)
    self._timer_expired_announced = False
    
    if wants_rematch:
        # ═══════════════════════════════════════════════════════════
        # REMATCH: Start New Game
        # ═══════════════════════════════════════════════════════════
        print("→ Scheduling deferred rematch...")
        
        # ✅ FIX BUG #68.1: Use wx.CallAfter (global function)
        # NOT self.app.CallAfter (doesn't exist on SolitarioWxApp)
        wx.CallAfter(self.start_gameplay)
        
    else:
        # ═══════════════════════════════════════════════════════════
        # DECLINE: Return to Main Menu
        # ═══════════════════════════════════════════════════════════
        print("→ Scheduling deferred return to main menu...")
        
        # ✅ FIX BUG #68.2: Use wx.CallAfter + new method
        # Method _safe_return_to_main_menu() created below
        wx.CallAfter(self._safe_return_to_main_menu)
```

**Changes**:
- Linea 614: `self.app.CallAfter` → `wx.CallAfter`
- Linea 620: `self.app.CallAfter` → `wx.CallAfter`
- Linea 620: `_safe_decline_to_menu` → `_safe_return_to_main_menu`
- Docstring aggiornata con v2.4.2 e Bug #68 reference

---

#### **Modifica 2: Aggiungere `_safe_return_to_main_menu()` in `acs_wx.py`**

**File**: `acs_wx.py`  
**Linea**: ~625 (dopo `handle_game_ended`)  
**Action**: ADD NEW METHOD

**Codice Nuovo**:
```python
def _safe_return_to_main_menu(self) -> None:
    """Return to main menu after declining rematch.
    
    Called via wx.CallAfter() when user declines rematch in end game dialog.
    
    Flow:
    1. Reset game state (service.reset_game())
    2. Switch to MenuPanel (show main menu)
    3. Announce return to menu via TTS
    
    Version: v2.4.2 (fix for Bug #68 - decline rematch behavior)
    
    Note:
        Called via wx.CallAfter() to ensure dialog is fully closed
        before panel switching occurs.
    
    Why CallAfter?
        - Modal dialogs block UI thread
        - Panel switching while dialog open can cause crashes
        - CallAfter defers execution until after dialog closes
        - Ensures clean UI state transition
    
    Example:
        >>> # User finishes game
        >>> # Dialog: "Vuoi giocare ancora?"
        >>> # User presses NO
        >>> # → handle_game_ended(wants_rematch=False)
        >>> # → wx.CallAfter(self._safe_return_to_main_menu)
        >>> # → Dialog closes
        >>> # → _safe_return_to_main_menu() executes
        >>> # → Game reset + switch to menu + TTS announcement
    """
    print("→ _safe_return_to_main_menu() called")
    
    # 1. Reset game state
    # Stops timer, resets move count, clears statistics
    self.engine.service.reset_game()
    print("  ✓ Game state reset")
    
    # 2. Switch to main menu panel
    # Shows MenuPanel with "Nuova Partita", "Opzioni", etc.
    self.view_manager.show_panel("menu")
    print("  ✓ Switched to MenuPanel")
    
    # 3. Announce return to menu via TTS
    # Helps blind users understand they're back at main menu
    if self.screen_reader and self.screen_reader.tts:
        self.screen_reader.tts.speak(
            "Sei tornato al menu principale. Usa le frecce per navigare.",
            interrupt=True
        )
    
    print("✓ Successfully returned to main menu")
```

**Rationale**:
- Reset completo stato di gioco (timer, mosse, statistiche)
- Switch a MenuPanel (menu principale root)
- TTS annuncia ritorno al menu per accessibilità
- Log dettagliati per debugging

---

#### **Modifica 3: Fix `wx.CallAfter()` safety check**

**File**: `src/infrastructure/ui/wx_dialog_provider.py`  
**Linea**: ~276  
**Action**: REPLACE

**Codice Attuale (SBAGLIATO)**:
```python
def show_yes_no_async(
    self,
    message: str,
    title: str,
    callback: Callable[[bool], None]
) -> None:
    """Show async yes/no dialog with callback."""
    
    def show_modal_and_callback():
        """Internal callback for modal dialog."""
        result = self.show_yes_no(message, title)
        callback(result)
    
    wx.CallAfter(show_modal_and_callback)  # ❌ BUG: Can crash if app closing
```

**Codice Nuovo**:
```python
def show_yes_no_async(
    self,
    message: str,
    title: str,
    callback: Callable[[bool], None]
) -> None:
    """Show async yes/no dialog with callback.
    
    Version: v2.4.2 - Added wx.App safety check (Bug #68.3)
    
    Args:
        message: Dialog message text
        title: Dialog title
        callback: Function to call with result (True=Yes, False=No)
    
    Note:
        Checks if wx.App is still active before calling wx.CallAfter().
        During app cleanup, wx.App may already be destroyed, causing
        AssertionError: "No wx.App created yet".
        
        If app is closing, calls callback(False) to prevent deadlock.
    """
    
    def show_modal_and_callback():
        """Internal callback for modal dialog."""
        result = self.show_yes_no(message, title)
        callback(result)
    
    # ✅ FIX BUG #68.3: Check if wx.App is still active
    # During app cleanup, wx.App may be None or not running
    app = wx.GetApp()
    if app and app.IsMainLoopRunning():
        # Safe to call wx.CallAfter
        wx.CallAfter(show_modal_and_callback)
    else:
        # App is closing, skip dialog and call callback with False
        print("⚠️ wx.App not active, skipping async dialog")
        # Call callback with False (decline) to prevent deadlock
        callback(False)
```

**Rationale**:
- `wx.GetApp()` può essere `None` durante cleanup
- `app.IsMainLoopRunning()` verifica se main loop attivo
- Se app chiusa, chiama `callback(False)` per evitare deadlock
- Evita crash `AssertionError: No wx.App created yet`

---

### 🧪 Test Cases - Bug #68

#### **Test Case 1: Win Game → Decline Rematch**

**Setup**:
```python
# Start game
engine.new_game()
assert engine.is_game_running() == True
```

**Action**:
```python
# Force victory (debug command)
engine._debug_force_victory()  # CTRL+ALT+W

# Statistics dialog shown ✅
# "Hai vinto! Tempo: 45s, Mosse: 120, Punteggio: 850"

# Rematch dialog shown ✅
# "Vuoi giocare ancora?"

# User clicks NO
# → dialogs.show_yes_no() returns False
# → engine.end_game() calls on_game_ended(wants_rematch=False)
# → handle_game_ended(False) called
```

**Expected Results**:
```python
# wx.CallAfter called correctly
assert wx.CallAfter was called  # ✅ Not self.app.CallAfter
assert _safe_return_to_main_menu was scheduled  # ✅ Not _safe_decline_to_menu

# After wx.CallAfter executes:
assert engine.service.is_game_running == False  # ✅ Game reset
assert view_manager.current_panel == "menu"  # ✅ Switched to MenuPanel
assert screen_reader.tts.last_message == "Sei tornato al menu principale..."  # ✅

# No crashes ✅
# No AttributeError ✅
# No AssertionError ✅
```

**Pass Criteria**: ✅ Nessun crash, ritorno al menu principale

---

#### **Test Case 2: Win Game → Accept Rematch**

**Setup**:
```python
# Start game
engine.new_game()
```

**Action**:
```python
# Force victory
engine._debug_force_victory()

# User clicks YES on "Vuoi giocare ancora?"
# → dialogs.show_yes_no() returns True
# → handle_game_ended(wants_rematch=True)
```

**Expected Results**:
```python
# wx.CallAfter called correctly
assert wx.CallAfter was called
assert start_gameplay was scheduled  # ✅ New game started

# After wx.CallAfter executes:
assert engine.service.is_game_running == True  # ✅ New game running
assert view_manager.current_panel == "gameplay"  # ✅ Still in gameplay

# No crashes ✅
```

**Pass Criteria**: ✅ Nuova partita iniziata correttamente

---

#### **Test Case 3: App Cleanup (ESC during dialog)**

**Setup**:
```python
# App running
assert wx.GetApp().IsMainLoopRunning() == True
```

**Action**:
```python
# User closes app (ALT+F4) while dialog is open
# wx.App starts cleanup
# → wx.GetApp().IsMainLoopRunning() == False

# show_yes_no_async() tries to call wx.CallAfter
```

**Expected Results**:
```python
# Safety check in wx_dialog_provider.py prevents crash
assert "⚠️ wx.App not active" in log  # ✅ Warning printed
assert callback(False) was called  # ✅ Callback called with False
assert no crash occurred  # ✅ No AssertionError
```

**Pass Criteria**: ✅ Nessun crash durante cleanup

---

### ✅ Definition of Done - Bug #68

**Code**:
- [x] `handle_game_ended()` aggiornato con `wx.CallAfter`
- [x] `_safe_return_to_main_menu()` implementato
- [x] `show_yes_no_async()` aggiornato con safety check
- [x] Docstrings complete con esempi
- [x] Type hints corretti

**Testing**:
- [x] Test Case 1 passa (Win → Decline rematch)
- [x] Test Case 2 passa (Win → Accept rematch)
- [x] Test Case 3 passa (App cleanup no crash)
- [x] Test manuale vittoria + decline
- [x] Test manuale sconfitta + decline

**Behavior**:
- [x] Nessun crash quando utente decline rematch
- [x] Ritorno al menu principale dopo decline
- [x] TTS annuncia "Sei tornato al menu principale"
- [x] Nuova partita inizia correttamente se accept rematch
- [x] Nessuna regressione su altre funzionalità

---

## 📊 Riepilogo File da Modificare

| File | Linea | Modifica | Bug |
|------|-------|----------|-----|
| `src/infrastructure/ui/options_dialog.py` | ~382 | REPLACE `on_setting_changed()` | #67 |
| `src/infrastructure/ui/options_dialog.py` | ~450 | ADD `_update_widget_lock_states()` | #67 |
| `src/infrastructure/ui/options_dialog.py` | ~350 | ADD call in `_load_settings_to_widgets()` | #67 |
| `acs_wx.py` | ~605-620 | REPLACE `handle_game_ended()` | #68 |
| `acs_wx.py` | ~625 | ADD `_safe_return_to_main_menu()` | #68 |
| `src/infrastructure/ui/wx_dialog_provider.py` | ~276 | REPLACE `show_yes_no_async()` | #68 |

**Totale File**: 3  
**Totale Modifiche**: 6  
**Totale Linee Nuove**: ~90

---

## 🎯 Acceptance Criteria Globale

### Bug #67 - Options Dialog
- [ ] Cambiare difficoltà aggiorna tutti i widget
- [ ] Preset valori applicati correttamente
- [ ] Widget bloccati disabilitati (grayed out)
- [ ] Widget bloccati già disabilitati all'apertura dialog
- [ ] TTS annuncia cambio preset (opzionale)
- [ ] Nessuna regressione su altre opzioni
- [ ] Funziona con tutti i 5 livelli di difficoltà

### Bug #68 - Decline Rematch
- [ ] Nessun crash quando utente decline rematch
- [ ] Ritorno al menu principale dopo decline
- [ ] TTS annuncia "Sei tornato al menu principale"
- [ ] Nuova partita inizia se accept rematch
- [ ] Nessun crash durante cleanup app
- [ ] Funziona sia con vittoria che con sconfitta

### Generale
- [ ] Nessuna regressione su altre funzionalità
- [ ] Codice pulito e ben documentato
- [ ] Test manuali passano
- [ ] Log chiari e dettagliati
- [ ] NVDA screen reader compatibile

---

## 🚀 Istruzioni per Copilot Agent

### Workflow Implementazione

1. **Commit #1 - Bug #67**:
   ```bash
   # Modifica src/infrastructure/ui/options_dialog.py
   # - Aggiorna on_setting_changed()
   # - Aggiungi _update_widget_lock_states()
   # - Aggiorna _load_settings_to_widgets()
   
   git add src/infrastructure/ui/options_dialog.py
   git commit -m "fix(ui): apply preset values when difficulty changes in Options Dialog
   
   - Intercept difficulty_radio change in on_setting_changed()
   - Call preset.apply_to(settings) to apply preset values
   - Refresh ALL widgets via _load_settings_to_widgets()
   - Add _update_widget_lock_states() to disable locked widgets
   - Add TTS announcement for preset application
   
   Fixes #67 - Options Dialog preset application
   Version: v2.4.2"
   ```

2. **Commit #2 - Bug #68**:
   ```bash
   # Modifica acs_wx.py
   # - Fix handle_game_ended()
   # - Aggiungi _safe_return_to_main_menu()
   
   # Modifica src/infrastructure/ui/wx_dialog_provider.py
   # - Fix show_yes_no_async() con safety check
   
   git add acs_wx.py src/infrastructure/ui/wx_dialog_provider.py
   git commit -m "fix(app): fix decline rematch crash and return to main menu
   
   - Fix self.app.CallAfter → wx.CallAfter (global function)
   - Create _safe_return_to_main_menu() method
   - Add wx.App safety check in wx_dialog_provider.py
   - Return to main menu when user declines rematch
   
   Fixes #68 - Decline rematch crash
   Version: v2.4.2"
   ```

3. **Testing**:
   ```bash
   # Test manuale Bug #67
   python acs_wx.py
   # → Apri Options (O)
   # → Cambia difficoltà (1→5→1)
   # → Verifica widget si aggiornano
   # → Verifica widget bloccati disabilitati
   
   # Test manuale Bug #68
   python acs_wx.py
   # → Nuova partita
   # → CTRL+ALT+W (force victory)
   # → Clicca NO su "Vuoi giocare ancora?"
   # → Verifica ritorno al menu principale
   # → Nessun crash
   ```

### Checklist Pre-Commit

- [ ] Codice implementato come da specifiche
- [ ] Docstrings complete con esempi
- [ ] Type hints corretti
- [ ] Log chiari e dettagliati
- [ ] Test manuali passano
- [ ] Nessuna regressione
- [ ] Commit message segue template

### Checklist Post-Commit

- [ ] Branch aggiornato
- [ ] Test manuali passano
- [ ] NVDA screen reader funziona
- [ ] Log verificati
- [ ] Piano implementazione aggiornato

---

## 📞 Reference

**Documenti Correlati**:
- `docs/ARCHITECTURE.md` - Clean Architecture overview
- `src/domain/models/difficulty_preset.py` - Preset implementation
- `src/infrastructure/ui/options_dialog.py` - Options Dialog
- `acs_wx.py` - Main application entry point

**Issues Correlate**:
- #67 - Options Dialog preset application
- #68 - Decline rematch crash
- #62 - PR originale per preset system

**Version**: v2.4.2  
**Branch**: `copilot/refactor-difficulty-options-system`  
**Status**: ⏳ Pending - 0/2 Commits Completed  
**Last Update**: 2026-02-14 21:45 CET
