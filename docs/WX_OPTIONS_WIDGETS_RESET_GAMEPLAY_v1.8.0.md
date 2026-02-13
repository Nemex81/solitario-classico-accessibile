# 🔧 Piano Implementazione: Opzioni wx Widgets + Reset Gameplay

**Branch target**: `copilot/remove-pygame-migrate-wxpython`  
**Versione**: `v1.8.0` (MINOR increment - feature + bug fix critici)  
**Data**: 2026-02-13

---

## 📊 Riepilogo Modifiche

### 🎨 Feature Nuove (v1.8.0)
1. **OptionsDialog con wx widgets reali**:
   - Pulsanti Salva/Annulla visibili e TAB-navigabili
   - ESC intelligente con conferma se modifiche presenti
   - Apertura finestra con `open_window()` per tracking stato

### 🐛 Bug Fix Critici
2. **Reset gameplay su abbandono**:
   - ESC (con conferma) → reset carte + stato
   - Doppio ESC (< 2s) → reset carte + stato
   - Timeout STRICT → reset carte + stato
   - No rematch → reset carte + stato

### 🎯 Obiettivo
Garantire **parità funzionale completa** con vecchia versione (refactoring-engine), usando **wx widgets nativi** per migliore accessibilità NVDA.

---

## 🗂️ File Coinvolti

| File | Modifiche | Tipo |
|------|-----------|------|
| `src/infrastructure/ui/options_dialog.py` | Pulsanti + ESC intelligente | Feature |
| `test.py` | Reset gameplay + open_window() | Fix |
| `CHANGELOG.md` | Aggiornamento v1.8.0 | Docs |

---

## 📋 Piano Incrementale (3 commit)

> **Copilot**: Implementa in ordine, **un commit per STEP**. Non mescolare modifiche.

---

## STEP 1: Aggiungi Pulsanti Salva/Annulla a OptionsDialog

**File**: `src/infrastructure/ui/options_dialog.py`

**Obiettivo**: Convertire da dialog "virtuale" (solo label) a dialog con **wx.Button reali** per Salva/Annulla.

### 1.1 Modifica `_create_ui()` - Aggiungi pulsanti

In `src/infrastructure/ui/options_dialog.py`, metodo `_create_ui()` (linee ~115-135):

**PRIMA** (solo label istruzioni):
```python
def _create_ui(self) -> None:
    """Create dialog UI elements.
    
    Creates a simple layout with informational text.
    In STEP 3, this is minimal - just shows instructions.
    """
    # Main sizer
    sizer = wx.BoxSizer(wx.VERTICAL)
    
    # Instructional label
    label = wx.StaticText(
        self,
        label="Finestra opzioni. Usa frecce e invio per modificare.\n\n"
              "Premere ESC per chiudere."
    )
    label.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
    
    # Add to sizer with padding
    sizer.Add(label, 0, wx.ALL | wx.EXPAND, 10)
    
    self.SetSizer(sizer)
```

**DOPO** (label + pulsanti Salva/Annulla):
```python
def _create_ui(self) -> None:
    """Create dialog UI elements with native wx.Button controls.
    
    Layout (v1.8.0 - native widgets):
    - Instructional label (audiogame instructions)
    - Horizontal button sizer with:
      * Salva modifiche (wx.ID_OK)
      * Annulla modifiche (wx.ID_CANCEL)
    
    Features:
    - TAB-navigable buttons (standard wx behavior)
    - NVDA announces button labels
    - Click or SPACE/ENTER to activate
    - ESC key also triggers cancel (see on_key_down)
    
    Note:
        This provides visual/accessible UI while maintaining
        full keyboard-driven options navigation (arrows/numbers).
        Users can choose: keyboard shortcuts OR button clicks.
    """
    # Main vertical sizer
    sizer = wx.BoxSizer(wx.VERTICAL)
    
    # Instructional label (audiogame mode)
    label = wx.StaticText(
        self,
        label="Finestra opzioni di gioco.\n\n"
              "Usa frecce SU/GIÙ per navigare tra le opzioni.\n"
              "Premi INVIO per modificare l'opzione corrente.\n"
              "Premi numeri 1-8 per saltare direttamente a un'opzione.\n\n"
              "Comandi speciali:\n"
              "  T = Attiva/disattiva timer\n"
              "  + = Aumenta timer di 5 minuti\n"
              "  - = Diminuisci timer di 5 minuti\n"
              "  I = Leggi tutte le impostazioni\n"
              "  H = Mostra aiuto completo\n\n"
              "ESC = Chiudi finestra (conferma se modifiche presenti)"
    )
    label.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
    
    # Add label with padding
    sizer.Add(label, 0, wx.ALL | wx.EXPAND, 10)
    
    # Spacer before buttons
    sizer.Add((0, 20), 0, wx.EXPAND)
    
    # Horizontal button sizer (Salva | Annulla)
    button_sizer = wx.BoxSizer(wx.HORIZONTAL)
    
    # Save button (wx.ID_OK for standard dialog behavior)
    self.btn_save = wx.Button(self, id=wx.ID_OK, label="&Salva modifiche")
    self.btn_save.SetToolTip("Salva le modifiche e chiudi la finestra opzioni")
    self.btn_save.Bind(wx.EVT_BUTTON, self.on_save_click)
    
    # Cancel button (wx.ID_CANCEL for standard dialog behavior)
    self.btn_cancel = wx.Button(self, id=wx.ID_CANCEL, label="&Annulla modifiche")
    self.btn_cancel.SetToolTip("Annulla le modifiche e chiudi la finestra opzioni")
    self.btn_cancel.Bind(wx.EVT_BUTTON, self.on_cancel_click)
    
    # Add buttons to horizontal sizer
    button_sizer.Add(self.btn_save, 0, wx.ALL, 5)
    button_sizer.Add(self.btn_cancel, 0, wx.ALL, 5)
    
    # Add button sizer to main sizer (centered)
    sizer.Add(button_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 10)
    
    # Set main sizer
    self.SetSizer(sizer)
    
    # Set default button (ENTER when not on a button activates this)
    self.btn_save.SetDefault()
```

**Note**:
- `&Salva` / `&Annulla`: `&` crea mnemonic (ALT+S, ALT+A)
- `wx.ID_OK` / `wx.ID_CANCEL`: ID standard wxPython per dialog
- `SetDefault()`: ENTER fuori dai button attiva Salva

### 1.2 Aggiungi metodi handler pulsanti

In `src/infrastructure/ui/options_dialog.py`, dopo `_create_ui()` (linea ~200):

```python
def on_save_click(self, event: wx.CommandEvent) -> None:
    """Handle Save button click.
    
    Calls controller.save_and_close() which:
    1. Updates settings snapshot (modifications become permanent)
    2. Resets controller state to CLOSED
    3. Returns TTS confirmation message
    
    Args:
        event: wx.CommandEvent from button click
    
    Flow:
        User clicks "Salva" → save_and_close() → vocalize → EndModal(OK)
    
    Note:
        EndModal(wx.ID_OK) signals parent that dialog closed with save.
        In current implementation, parent doesn't use this signal,
        but it's good practice for future extensibility.
    """
    msg = self.options_controller.save_and_close()
    
    # Vocalize confirmation
    if self.screen_reader and self.screen_reader.tts:
        self.screen_reader.tts.speak(msg, interrupt=True)
    
    # Close dialog with OK status
    self.EndModal(wx.ID_OK)

def on_cancel_click(self, event: wx.CommandEvent) -> None:
    """Handle Cancel button click.
    
    Calls controller.discard_and_close() which:
    1. Restores original settings snapshot (undo modifications)
    2. Resets controller state to CLOSED
    3. Returns TTS confirmation message
    
    Args:
        event: wx.CommandEvent from button click
    
    Flow:
        User clicks "Annulla" → discard_and_close() → vocalize → EndModal(CANCEL)
    
    Note:
        Restores ALL settings to values at dialog open time.
        This includes deck_type, difficulty, timer, shuffle_mode, etc.
    """
    msg = self.options_controller.discard_and_close()
    
    # Vocalize confirmation
    if self.screen_reader and self.screen_reader.tts:
        self.screen_reader.tts.speak(msg, interrupt=True)
    
    # Close dialog with Cancel status
    self.EndModal(wx.ID_CANCEL)
```

**Commit 1**:
```
feat(options): add Save/Cancel buttons to OptionsDialog

- Replace minimal label-only UI with native wx.Button controls
- Add btn_save (wx.ID_OK) and btn_cancel (wx.ID_CANCEL)
- Implement on_save_click() → controller.save_and_close()
- Implement on_cancel_click() → controller.discard_and_close()
- Buttons are TAB-navigable and NVDA-accessible
- Update label with complete keyboard command list

Provides visual UI for mouse users while maintaining
full keyboard-driven experience for audiogame mode.

Refs: v1.8.0 feature - native wx widgets in options
```

---

## STEP 2: ESC Intelligente + open_window() Call

**File**: `src/infrastructure/ui/options_dialog.py`, `test.py`

**Obiettivo**: ESC chiama `close_window()` che gestisce conferma automatica se modifiche presenti.

### 2.1 Modifica `on_key_down()` - ESC intelligente

In `src/infrastructure/ui/options_dialog.py`, metodo `on_key_down()` (linee ~145-160):

**PRIMA** (ESC chiude sempre direttamente):
```python
# ESC: Cancel and close dialog
if key_code == wx.WXK_ESCAPE:
    msg = self.options_controller.cancel_close()
    self.EndModal(wx.ID_CANCEL)
    return
```

**DOPO** (ESC chiama close_window con logica DIRTY/CLEAN):
```python
# ESC: Close with confirmation if modifications present
if key_code == wx.WXK_ESCAPE:
    # Call close_window() which handles DIRTY/CLEAN states:
    # - OPEN_CLEAN: Close directly
    # - OPEN_DIRTY: Show save confirmation dialog (if dialog_manager available)
    msg = self.options_controller.close_window()
    
    # Check if dialog was actually closed
    # (controller sets state to CLOSED if user confirmed save/discard)
    if self.options_controller.state == "CLOSED":
        # Closing confirmed (saved or discarded)
        if self.screen_reader and self.screen_reader.tts:
            self.screen_reader.tts.speak(msg, interrupt=True)
        
        # Determine exit code based on message
        # ("Salva" in msg means user chose to save)
        exit_code = wx.ID_OK if "salv" in msg.lower() else wx.ID_CANCEL
        self.EndModal(exit_code)
    else:
        # Closing cancelled (user pressed Cancel in save dialog)
        # or fallback mode (no dialog_manager)
        if self.screen_reader and self.screen_reader.tts:
            self.screen_reader.tts.speak(msg, interrupt=True)
        # Stay open (don't call EndModal)
    
    return
```

**Note importanti**:
- `close_window()` usa `dialog_manager.show_options_save_prompt()` se `state == "OPEN_DIRTY"`
- Dialog prompt ha 3 pulsanti: **Sì** (salva), **No** (annulla), **Annulla** (rimani aperto)
- Se user sceglie "Annulla", `state` rimane `"OPEN_DIRTY"` → non chiudiamo il dialog

### 2.2 Modifica `show_options()` - Call open_window()

In `test.py`, metodo `show_options()` (linee ~208-228):

**PRIMA** (no open_window call):
```python
def show_options(self) -> None:
    """Show options window using OptionsDialog (STEP 3)."""
    from src.infrastructure.ui.options_dialog import OptionsDialog
    
    print("\n" + "="*60)
    print("APERTURA FINESTRA OPZIONI (OptionsDialog)")
    print("="*60)
    
    self.is_options_mode = True
    
    # Create and show modal options dialog (with TTS support)
    dlg = OptionsDialog(
        parent=self.frame,
        controller=self.gameplay_controller.options_controller,
        screen_reader=self.screen_reader
    )
    dlg.ShowModal()
    dlg.Destroy()
    
    self.is_options_mode = False
    
    print("Finestra opzioni chiusa.")
    print("="*60)
```

**DOPO** (chiama open_window prima di mostrare dialog):
```python
def show_options(self) -> None:
    """Show options window using OptionsDialog with wx.Button controls.
    
    Opens modal OptionsDialog with OptionsWindowController and ScreenReader.
    Calls controller.open_window() to initialize state tracking.
    
    Flow:
    1. Set is_options_mode flag
    2. Call controller.open_window() (sets state=OPEN_CLEAN, saves snapshot)
    3. Vocalize opening message
    4. Create OptionsDialog with controller + screen_reader
    5. Show modal (blocks until closed)
    6. Clean up and reset flag
    
    State Management:
    - controller.open_window() saves settings snapshot for change tracking
    - Any modifications set state to OPEN_DIRTY
    - ESC with OPEN_DIRTY triggers save confirmation dialog
    - Buttons or ESC with OPEN_CLEAN close directly
    
    Note:
        screen_reader enables TTS feedback for navigation (UP/DOWN/numbers).
        All controller messages are vocalized via ScreenReader TTS.
    """
    from src.infrastructure.ui.options_dialog import OptionsDialog
    
    print("\n" + "="*60)
    print("APERTURA FINESTRA OPZIONI (OptionsDialog con wx.Button)")
    print("="*60)
    
    self.is_options_mode = True
    
    # Initialize controller state (OPEN_CLEAN, save snapshot)
    open_msg = self.gameplay_controller.options_controller.open_window()
    if self.screen_reader:
        self.screen_reader.tts.speak(open_msg, interrupt=True)
        wx.MilliSleep(500)  # Brief pause before showing dialog
    
    # Create and show modal options dialog (with TTS support + native buttons)
    dlg = OptionsDialog(
        parent=self.frame,
        controller=self.gameplay_controller.options_controller,
        screen_reader=self.screen_reader
    )
    result = dlg.ShowModal()
    dlg.Destroy()
    
    self.is_options_mode = False
    
    # Log dialog result (for debugging)
    result_str = "OK (saved)" if result == wx.ID_OK else "CANCEL (discarded)"
    print(f"Finestra opzioni chiusa: {result_str}")
    print("="*60)
```

**Commit 2**:
```
feat(options): implement smart ESC with save confirmation

- Modify on_key_down() ESC handler to call close_window()
- close_window() shows save prompt if state == OPEN_DIRTY
- Save prompt has 3 options: Sì (save), No (discard), Annulla (cancel)
- If user cancels, dialog stays open (state remains OPEN_DIRTY)
- Add open_window() call in show_options() to initialize state
- Vocalize opening message with TTS

Provides consistent behavior with refactoring-engine branch:
- No changes = ESC closes directly
- Has changes = ESC asks "Vuoi salvare?"

Refs: v1.8.0 feature - smart close with change tracking
```

---

## STEP 3: Fix Reset Gameplay su Abbandono

**File**: `test.py`

**Obiettivo**: Garantire che `engine.reset_game()` sia chiamato in TUTTI gli scenari di abbandono partita.

### 3.1 Fix `show_abandon_game_dialog()` - Aggiungi reset

In `test.py`, metodo `show_abandon_game_dialog()` (linee ~255-262):

**PRIMA** (no reset esplicito):
```python
def show_abandon_game_dialog(self) -> None:
    """Show abandon game confirmation dialog (called from GameplayView)."""
    result = self.dialog_manager.show_yes_no(
        "Vuoi abbandonare la partita e tornare al menu di gioco?",
        "Abbandono Partita"
    )
    if result:
        self.return_to_menu()
```

**DOPO** (reset esplicito prima di return_to_menu):
```python
def show_abandon_game_dialog(self) -> None:
    """Show abandon game confirmation dialog (called from GameplayPanel ESC).
    
    Shows native wxDialog asking user to confirm game abandonment.
    If confirmed, resets game engine and returns to main menu.
    
    Flow:
        User presses ESC in gameplay → GameplayPanel calls this
        → Dialog "Vuoi abbandonare?"
        → If Yes: reset_game() + return_to_menu()
        → If No: stay in gameplay
    
    Note:
        engine.reset_game() clears:
        - All card positions (deck, foundations, tableau, waste)
        - Score and move counter
        - Timer elapsed time
        - Game state flags (is_running, game_over)
    """
    # Validate dialog_manager
    if not self.dialog_manager:
        print("⚠ Dialog manager not available, aborting abandon")
        return
    
    # Show confirmation dialog
    result = self.dialog_manager.show_yes_no(
        "Vuoi abbandonare la partita e tornare al menu di gioco?",
        "Abbandono Partita"
    )
    
    if result:
        # Reset game engine (clear cards, score, timer)
        print("\n→ User confirmed abandon - Resetting game engine")
        self.engine.reset_game()
        
        # Return to main menu
        self.return_to_menu()
```

### 3.2 Fix `confirm_abandon_game()` - Aggiungi reset (doppio ESC)

In `test.py`, metodo `confirm_abandon_game()` (linee ~282-294):

**PRIMA** (no reset esplicito):
```python
def confirm_abandon_game(self, skip_dialog: bool = False) -> None:
    """Abandon game immediately without dialog (double-ESC from GameplayView).
    
    Args:
        skip_dialog: If True, skips confirmation (for double-ESC)
    """
    if self.screen_reader and skip_dialog:
        self.screen_reader.tts.speak(
            "Partita abbandonata.",
            interrupt=True
        )
        wx.MilliSleep(300)
    
    self._timer_expired_announced = False
    self.return_to_menu()
```

**DOPO** (reset esplicito prima di return_to_menu):
```python
def confirm_abandon_game(self, skip_dialog: bool = False) -> None:
    """Abandon game immediately without dialog (double-ESC quick exit).
    
    Called when user presses ESC twice within 2 seconds in GameplayPanel.
    Provides instant game abandonment without confirmation dialog.
    
    Args:
        skip_dialog: If True, skips confirmation (always True for double-ESC)
    
    Flow:
        User presses ESC twice (< 2s) → GameplayPanel calls this with skip_dialog=True
        → Announce "Partita abbandonata"
        → reset_game() + return_to_menu()
    
    Note:
        This is the "quick exit" feature for experienced users.
        Same as show_abandon_game_dialog() but no confirmation required.
    """
    if self.screen_reader and skip_dialog:
        self.screen_reader.tts.speak(
            "Partita abbandonata.",
            interrupt=True
        )
        wx.MilliSleep(300)
    
    # Reset game engine (clear cards, score, timer)
    print("\n→ Double-ESC detected - Resetting game engine")
    self.engine.reset_game()
    
    self._timer_expired_announced = False
    self.return_to_menu()
```

### 3.3 Fix `_handle_game_over_by_timeout()` - Verifica reset

In `test.py`, metodo `_handle_game_over_by_timeout()` (linee ~390-420):

**PRIMA** (no reset esplicito):
```python
def _handle_game_over_by_timeout(self) -> None:
    """Handle game over by timeout in STRICT mode."""
    # ... build defeat_msg ...
    
    print(defeat_msg)
    
    if self.screen_reader:
        self.screen_reader.tts.speak(defeat_msg, interrupt=True)
        wx.MilliSleep(2000)
    
    self._timer_expired_announced = False
    self.return_to_menu()
```

**DOPO** (reset esplicito prima di return_to_menu):
```python
def _handle_game_over_by_timeout(self) -> None:
    """Handle game over by timeout in STRICT mode.
    
    Called when timer expires and settings.timer_strict_mode == True.
    Shows defeat message with game statistics, then returns to menu.
    
    Flow:
        Timer expires → _check_timer_expiration() calls this
        → Build defeat message with stats
        → Vocalize message (2s pause)
        → reset_game() + return_to_menu()
    
    Note:
        In STRICT mode, timeout = automatic defeat (no overtime).
        In PERMISSIVE mode, timeout = penalty points (game continues).
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
    
    # Reset game engine (clear cards, score, timer)
    print("\n→ Timeout defeat - Resetting game engine")
    self.engine.reset_game()
    
    self._timer_expired_announced = False
    self.return_to_menu()
```

### 3.4 Fix `handle_game_ended()` - Aggiungi reset se no rematch

In `test.py`, metodo `handle_game_ended()` (linee ~305-325):

**PRIMA** (no reset se user rifiuta rematch):
```python
def handle_game_ended(self, wants_rematch: bool) -> None:
    """Handle game end callback from GameEngine."""
    print("\n" + "="*60)
    print(f"CALLBACK: Game ended - Rematch requested: {wants_rematch}")
    print("="*60)
    
    self._timer_expired_announced = False
    
    if wants_rematch:
        print("→ User chose rematch - Starting new game")
        self.start_gameplay()
    else:
        print("→ User declined rematch - Returning to menu")
        self.return_to_menu()
    
    print("="*60)
```

**DOPO** (reset esplicito se user rifiuta rematch):
```python
def handle_game_ended(self, wants_rematch: bool) -> None:
    """Handle game end callback from GameEngine.
    
    Called when game ends (victory or defeat dialog shown by GameEngine).
    User chooses between rematch or return to menu.
    
    Args:
        wants_rematch: True if user clicked "Nuova Partita", False if "Menu"
    
    Flow:
        Game ends → GameEngine shows victory/defeat dialog
        → User chooses → GameEngine calls this callback
        → If rematch: start_gameplay() (which calls reset + new_game internally)
        → If no rematch: reset_game() + return_to_menu()
    
    Note:
        start_gameplay() already calls engine.reset_game() + engine.new_game(),
        so we only need explicit reset when user declines rematch.
    """
    print("\n" + "="*60)
    print(f"CALLBACK: Game ended - Rematch requested: {wants_rematch}")
    print("="*60)
    
    self._timer_expired_announced = False
    
    if wants_rematch:
        print("→ User chose rematch - Starting new game")
        # start_gameplay() calls engine.reset_game() + engine.new_game() internally
        self.start_gameplay()
    else:
        print("→ User declined rematch - Returning to menu")
        # Reset game engine before returning to menu
        self.engine.reset_game()
        self.return_to_menu()
    
    print("="*60)
```

**Commit 3**:
```
fix(gameplay): add explicit reset_game() on all abandon scenarios

- show_abandon_game_dialog(): Add reset before return_to_menu()
- confirm_abandon_game(): Add reset before return_to_menu() (double-ESC)
- _handle_game_over_by_timeout(): Add reset before return_to_menu() (STRICT)
- handle_game_ended(): Add reset if user declines rematch

Bug Fix:
Previously, abandoning a game left cards and state in memory,
causing potential issues on next game start.

Now all abandon paths call engine.reset_game() which clears:
- Card positions (deck, foundations, tableau, waste)
- Score and move counter
- Timer elapsed time
- Game state flags (is_running, game_over)

Ensures clean state on return to main menu.

Refs: v1.8.0 critical bug fix
```

---

## STEP 4: Aggiorna CHANGELOG.md

**File**: `CHANGELOG.md`

**Obiettivo**: Documentare release v1.8.0 con tutte le feature e fix.

### 4.1 Aggiungi sezione v1.8.0 in cima

In `CHANGELOG.md`, aggiungi questa sezione **PRIMA** di `## [1.7.5]`:

```markdown
## [1.8.0] - 2026-02-13

### Added
- **OptionsDialog con wx.Button nativi**: Pulsanti "Salva modifiche" e "Annulla modifiche" TAB-navigabili e NVDA-accessibili
- **ESC intelligente in opzioni**: Chiede conferma salvataggio solo se ci sono modifiche non salvate
- **Tracking stato opzioni**: `open_window()` salva snapshot impostazioni per rilevare modifiche
- **Label istruzioni completa**: Mostra tutti i comandi tastiera disponibili (frecce, numeri, T/+/-, I, H)

### Fixed
- **Reset gameplay su abbandono ESC**: `engine.reset_game()` ora chiamato quando si abbandona partita con conferma
- **Reset gameplay su doppio ESC**: `engine.reset_game()` chiamato anche per uscita rapida (< 2 secondi)
- **Reset gameplay su timeout STRICT**: `engine.reset_game()` chiamato quando timer scade in modalità STRICT
- **Reset gameplay su rifiuto rematch**: `engine.reset_game()` chiamato quando utente rifiuta nuova partita dopo vittoria/sconfitta
- **Validazione dialog_manager**: Controllo esistenza dialog_manager in `show_abandon_game_dialog()` per evitare crash

### Changed
- **OptionsDialog UI completa**: Da dialog virtuale (solo label) a dialog con widget wx nativi (pulsanti + label istruzioni)
- **Pulsanti con mnemonics**: ALT+S per Salva, ALT+A per Annulla (accessibilità keyboard)
- **Default button**: INVIO su label istruzioni attiva "Salva modifiche" (comportamento standard dialogs)

### Technical
- `OptionsDialog._create_ui()`: Aggiunti `wx.Button` per Salva/Annulla con bind a `on_save_click()` / `on_cancel_click()`
- `OptionsDialog.on_key_down()`: ESC ora chiama `controller.close_window()` invece di `cancel_close()` diretto
- `SolitarioController.show_options()`: Chiama `options_controller.open_window()` prima di mostrare dialog
- `SolitarioController.show_abandon_game_dialog()`: Aggiunta chiamata `engine.reset_game()` prima di `return_to_menu()`
- `SolitarioController.confirm_abandon_game()`: Aggiunta chiamata `engine.reset_game()` prima di `return_to_menu()`
- `SolitarioController._handle_game_over_by_timeout()`: Aggiunta chiamata `engine.reset_game()` prima di `return_to_menu()`
- `SolitarioController.handle_game_ended()`: Aggiunta chiamata `engine.reset_game()` se user rifiuta rematch

### Migration Notes
Aggiornamento da v1.7.5 a v1.8.0:
- **Comportamento opzioni**: ESC ora chiede conferma se hai modificato impostazioni (prima chiudeva sempre direttamente)
- **Interfaccia opzioni**: Ora ci sono pulsanti visibili "Salva" e "Annulla" in fondo al dialog
- **Esperienza utente**: Puoi scegliere tra:
  - Navigazione tastiera pura (frecce/numeri + ESC)
  - Click sui pulsanti (mouse/touch)
  - Mnemonics (ALT+S / ALT+A)
- **Stato gioco**: Abbandonare partita ora resetta completamente lo stato (prima lasciava carte in memoria)

### Breaking Changes
Nessuna breaking change. Tutte le modifiche sono retrocompatibili.
```

**Commit 4**:
```
docs(changelog): add v1.8.0 release notes

- Document new OptionsDialog native wx.Button UI
- Document smart ESC with save confirmation
- Document all reset_game() bug fixes (4 scenarios)
- Add technical details for each modification
- Add migration notes for users upgrading from v1.7.5

Version increment: 1.7.5 → 1.8.0 (MINOR)
Reason: New features (wx buttons, smart ESC) + critical bug fixes (reset)
```

---

## 🧪 Testing Checklist Completo

### Test 1: Opzioni - Pulsanti Salva/Annulla

✅ **Test 1A**: Pulsanti visibili e navigabili
1. Avvia app: `python test.py`
2. Menu → TAB a "Opzioni" → INVIO
3. **Atteso**: Dialog opzioni con label istruzioni + 2 pulsanti in fondo
4. Premi TAB ripetutamente
5. **Atteso**: Focus passa a "Salva modifiche" → "Annulla modifiche" → wraparound

✅ **Test 1B**: Pulsante Salva funziona
1. Nel dialog opzioni, premi DOWN per navigare opzioni
2. Premi INVIO per modificare un'opzione (es. difficoltà)
3. **Atteso**: TTS annuncia "Difficoltà impostata su..."
4. TAB a "Salva modifiche" → INVIO
5. **Atteso**: TTS "Modifiche salvate", dialog si chiude
6. Riapri opzioni → verifica che modifica sia persistita

✅ **Test 1C**: Pulsante Annulla funziona
1. Nel dialog opzioni, modifica un'opzione
2. TAB a "Annulla modifiche" → INVIO
3. **Atteso**: TTS "Modifiche annullate", dialog si chiude
4. Riapri opzioni → verifica che modifica NON sia persistita

✅ **Test 1D**: Mnemonics ALT+S / ALT+A
1. Nel dialog opzioni, premi ALT+S
2. **Atteso**: Salva e chiudi (equivalente a click su Salva)
3. Riapri opzioni, modifica opzione, premi ALT+A
4. **Atteso**: Annulla e chiudi (equivalente a click su Annulla)

### Test 2: ESC Intelligente

✅ **Test 2A**: ESC senza modifiche chiude direttamente
1. Apri opzioni
2. NON modificare nulla
3. Premi ESC
4. **Atteso**: Dialog si chiude direttamente, TTS "Chiusura finestra opzioni"

✅ **Test 2B**: ESC con modifiche chiede conferma
1. Apri opzioni
2. Modifica un'opzione (es. premi INVIO su difficoltà)
3. **Atteso**: TTS "Difficoltà impostata..."
4. Premi ESC
5. **Atteso**: Dialog conferma "Vuoi salvare le modifiche?"
6. Clicca "Sì"
7. **Atteso**: Dialog opzioni si chiude, modifiche salvate

✅ **Test 2C**: ESC + conferma "No" annulla modifiche
1. Apri opzioni, modifica opzione, premi ESC
2. Nel dialog conferma, clicca "No"
3. **Atteso**: Dialog opzioni si chiude, TTS "Modifiche annullate"
4. Riapri opzioni → verifica che modifica NON sia persistita

✅ **Test 2D**: ESC + conferma "Annulla" rimane aperto
1. Apri opzioni, modifica opzione, premi ESC
2. Nel dialog conferma, clicca "Annulla"
3. **Atteso**: Dialog conferma si chiude, dialog opzioni RIMANE APERTO
4. Premi ESC di nuovo → dialog conferma riappare

### Test 3: Reset Gameplay

✅ **Test 3A**: ESC (con conferma) resetta partita
1. Avvia nuova partita
2. Fai alcune mosse (es. sposta carte)
3. Premi ESC
4. **Atteso**: Dialog "Vuoi abbandonare la partita?"
5. Clicca "Sì"
6. **Atteso**: Console mostra "→ User confirmed abandon - Resetting game engine"
7. Torna al menu
8. Avvia nuova partita → verifica che NON ci siano carte della partita precedente

✅ **Test 3B**: Doppio ESC (< 2s) resetta partita
1. Avvia nuova partita, fai mosse
2. Premi ESC 2 volte velocemente (< 2 secondi)
3. **Atteso**: TTS "Uscita rapida!", console "→ Double-ESC detected - Resetting game engine"
4. Torna al menu
5. Avvia nuova partita → verifica reset completo

✅ **Test 3C**: Timeout STRICT resetta partita
1. Apri opzioni → imposta Timer 1 minuto, Modalità Timer STRICT
2. Avvia partita, aspetta 1 minuto senza fare mosse
3. **Atteso**: TTS "TEMPO SCADUTO!", console "→ Timeout defeat - Resetting game engine"
4. Torna al menu automaticamente
5. Avvia nuova partita → verifica reset

✅ **Test 3D**: Rifiuto rematch resetta partita
1. Avvia partita, completa il solitario (vinci)
2. **Atteso**: Dialog vittoria con pulsanti "Nuova Partita" / "Menu"
3. Clicca "Menu"
4. **Atteso**: Console "→ User declined rematch - Returning to menu", reset chiamato
5. Torna al menu
6. Avvia nuova partita → verifica reset

### Test 4: Regressione (verifica che non abbiamo rotto nulla)

✅ **Test 4A**: Comando "N" (nuova partita) funziona ancora
1. Avvia partita
2. Premi "N"
3. **Atteso**: Dialog "Vuoi iniziare una nuova partita? Progressi persi"
4. Clicca "Sì"
5. **Atteso**: Reset + nuova partita avviata (TTS "Nuova partita avviata!")

✅ **Test 4B**: Rematch funziona ancora
1. Vinci partita
2. Clicca "Nuova Partita" nel dialog vittoria
3. **Atteso**: Reset + nuova partita avviata

✅ **Test 4C**: Tutte le opzioni funzionano (frecce, numeri, T/+/-/I/H)
1. Apri opzioni
2. Premi DOWN → **Atteso**: TTS "2 di 8: Difficoltà..."
3. Premi 6 → **Atteso**: TTS "6 di 8: Suggerimenti Comandi..."
4. Premi T → **Atteso**: TTS "Timer attivato/disattivato..."
5. Premi I → **Atteso**: TTS legge tutte le impostazioni
6. Premi H → **Atteso**: TTS legge aiuto completo

---

## 📊 Riepilogo Commit (4 totali)

1. **feat(options): add Save/Cancel buttons to OptionsDialog**
   - Aggiungi `wx.Button` nativi per Salva/Annulla
   - Label istruzioni completa con tutti i comandi

2. **feat(options): implement smart ESC with save confirmation**
   - ESC chiama `close_window()` con logica DIRTY/CLEAN
   - `show_options()` chiama `open_window()` per tracking stato

3. **fix(gameplay): add explicit reset_game() on all abandon scenarios**
   - 4 fix: ESC conferma, doppio ESC, timeout STRICT, rifiuto rematch
   - Garantisce reset completo carte + stato

4. **docs(changelog): add v1.8.0 release notes**
   - Documenta feature + bug fix
   - Migration notes per upgrade da v1.7.5

---

## ⚠️ Note Importanti per Copilot

1. **NON modificare** file non elencati in questo documento
2. **NON refactorare** codice non correlato alle modifiche specifiche
3. **MANTIENI** tutti i commenti esistenti, aggiungi solo dove necessario
4. **TESTA** manualmente dopo commit 3 (reset gameplay) con scenario Test 3A
5. **RISPETTA** l'ordine dei commit (1 → 2 → 3 → 4) per dipendenze corrette
6. **VERIFICA** che `engine.reset_game()` esista nel `GameEngine` (dovrebbe essere già presente)

---

## 🎯 Stato Finale Atteso

### Opzioni (v1.8.0)

✅ **Widget nativi wx**: Pulsanti Salva/Annulla visibili e TAB-navigabili
✅ **ESC intelligente**: Conferma solo se modifiche presenti (OPEN_DIRTY)
✅ **Tracking stato**: `open_window()` salva snapshot, modifiche settano DIRTY
✅ **Esperienza ibrida**: Tastiera pura (frecce/numeri/ESC) + pulsanti (mouse/mnemonic)
✅ **Accessibilità NVDA**: Pulsanti annunciati, mnemonics ALT+S/ALT+A
✅ **Label istruzioni**: Tutti i comandi documentati nel dialog

### Gameplay Reset (v1.8.0)

✅ **ESC + conferma**: Reset completo prima di return_to_menu()
✅ **Doppio ESC**: Reset completo prima di return_to_menu()
✅ **Timeout STRICT**: Reset completo prima di return_to_menu()
✅ **Rifiuto rematch**: Reset completo prima di return_to_menu()
✅ **Comando "N"**: Reset già presente (nessuna modifica necessaria)

### Parità Funzionale

✅ **refactoring-engine**: 100% feature parity raggiunta
✅ **wxPython nativi**: Migliore accessibilità NVDA rispetto a widget virtuali
✅ **Architettura pulita**: Separazione UI (dialog) vs Logic (controller)
✅ **Stato consistente**: Nessuna carta o dato residuo tra partite

---

**Copilot**: Inizia con STEP 1 (commit 1). Dopo ogni commit, attendi conferma prima di procedere al STEP successivo.

**Fine documento di implementazione v1.8.0**