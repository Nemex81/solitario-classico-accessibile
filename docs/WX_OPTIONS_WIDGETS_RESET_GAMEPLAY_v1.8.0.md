# 🔧 Piano Implementazione Completo: v1.8.0 - Opzioni wx Widgets Nativi + Reset Gameplay

**Branch target**: `copilot/remove-pygame-migrate-wxpython`  
**Versione**: `v1.8.0` (MINOR increment - major feature + bug fix critici)  
**Data**: 2026-02-13

---

## 📊 Riepilogo Modifiche v1.8.0

### 🎨 Feature Principali
1. **OptionsDialog con wx widgets nativi completi**:
   - 8 opzioni convertite da virtuali (audio-only) a widget wx reali
   - RadioBox per scelte multiple (deck type, difficulty, etc.)
   - CheckBox per booleani (suggerimenti, punti)
   - ComboBox per timer (con CheckBox enable/disable)
   - Pulsanti Salva/Annulla TAB-navigabili
   - NVDA legge automaticamente tutti i widget (no TTS custom)

2. **Navigazione standard wxPython**:
   - TAB per navigare tra widget
   - Frecce SU/GIÙ per cambiare valore in RadioBox/ComboBox
   - SPACE per toggle CheckBox
   - INVIO su pulsanti

3. **ESC intelligente con tracking modifiche**:
   - Salva snapshot all'apertura dialog
   - Rileva modifiche automaticamente (DIRTY state)
   - Conferma salvataggio solo se modifiche presenti

### 🐛 Bug Fix Critici
4. **Reset gameplay completo**:
   - ESC con conferma → reset carte + stato
   - Doppio ESC (< 2s) → reset carte + stato  
   - Timeout STRICT → reset carte + stato
   - Rifiuto rematch → reset carte + stato

### 🎯 Obiettivo
Raggiungere **parità funzionale completa** con refactoring-engine, ma con **UI nativa wx** per accessibilità NVDA perfetta.

---

## 🗂️ File Coinvolti

| File | Modifiche | Tipo |
|------|-----------|------|
| `src/infrastructure/ui/options_dialog.py` | Widget nativi (8 opzioni) + pulsanti + ESC | Feature |
| `test.py` | open_window() call + reset gameplay (4 scenari) | Feature + Fix |
| `CHANGELOG.md` | Release notes v1.8.0 | Docs |

---

## 📋 Piano Incrementale (6 commit)

> **Copilot**: Implementa in ordine, **un commit per STEP**. Non mescolare modifiche tra STEP.

---

## STEP 1: Crea Widget Nativi per Opzioni 1-4 (Tipo Mazzo, Difficoltà, Carte, Timer)

**File**: `src/infrastructure/ui/options_dialog.py`

**Obiettivo**: Sostituire dialog virtuale con **wx.RadioBox** e **wx.ComboBox** per prime 4 opzioni.

### 1.1 Modifica `__init__` - Rimuovi navigazione virtuale

In `src/infrastructure/ui/options_dialog.py`, costruttore (linee ~65-100):

**Rimuovi** il bind `EVT_CHAR_HOOK` che gestisce frecce/numeri:
```python
# RIMUOVERE questa riga:
# self.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)
```

**Nota**: La navigazione virtuale (frecce, numeri 1-8) sarà **completamente rimossa**. User userà TAB standard.

### 1.2 Riscrivi `_create_ui()` - Prima metà opzioni (1-4)

In `src/infrastructure/ui/options_dialog.py`, metodo `_create_ui()` (linee ~115-145):

**PRIMA** (label minimale + bind keyboard):
```python
def _create_ui(self) -> None:
    sizer = wx.BoxSizer(wx.VERTICAL)
    label = wx.StaticText(...)
    sizer.Add(label, 0, wx.ALL | wx.EXPAND, 10)
    self.SetSizer(sizer)
```

**DOPO** (widget nativi per opzioni 1-4):
```python
def _create_ui(self) -> None:
    """Create native wx widgets for all game options.
    
    Layout (v1.8.0 - native widgets, no virtual navigation):
    - RadioBox for deck type (Francese/Napoletano)
    - RadioBox for difficulty (1/2/3 carte)
    - RadioBox for draw count (1/2/3 carte)
    - CheckBox + ComboBox for timer (enable + duration)
    - RadioBox for shuffle mode (Inversione/Mescolata)
    - CheckBox for command hints (ON/OFF)
    - CheckBox for scoring system (ON/OFF)
    - RadioBox for timer strict mode (STRICT/PERMISSIVE)
    - Buttons: Salva / Annulla
    
    Navigation:
    - TAB to move between widgets (standard wx behavior)
    - UP/DOWN arrows to change value in RadioBox/ComboBox
    - SPACE to toggle CheckBox
    - ENTER to activate focused button
    
    Accessibility:
    - NVDA reads all widgets automatically (native support)
    - No custom TTS needed - wx handles screen reader communication
    - All widgets have descriptive labels for screen readers
    """
    main_sizer = wx.BoxSizer(wx.VERTICAL)
    
    # ========================================
    # OPZIONE 1: TIPO MAZZO
    # ========================================
    deck_box = wx.StaticBoxSizer(wx.VERTICAL, self, "Tipo Mazzo")
    self.deck_type_radio = wx.RadioBox(
        self,
        label="Seleziona il tipo di mazzo da usare:",
        choices=["Francese (52 carte)", "Napoletano (40 carte)"],
        majorDimension=1,  # Vertical layout
        style=wx.RA_SPECIFY_COLS
    )
    deck_box.Add(self.deck_type_radio, 0, wx.ALL | wx.EXPAND, 5)
    main_sizer.Add(deck_box, 0, wx.ALL | wx.EXPAND, 10)
    
    # ========================================
    # OPZIONE 2: DIFFICOLTÀ
    # ========================================
    diff_box = wx.StaticBoxSizer(wx.VERTICAL, self, "Difficoltà")
    self.difficulty_radio = wx.RadioBox(
        self,
        label="Numero di carte scoperte dal tallone:",
        choices=["1 carta (facile)", "2 carte (medio)", "3 carte (difficile)"],
        majorDimension=3,  # Horizontal layout
        style=wx.RA_SPECIFY_COLS
    )
    diff_box.Add(self.difficulty_radio, 0, wx.ALL | wx.EXPAND, 5)
    main_sizer.Add(diff_box, 0, wx.ALL | wx.EXPAND, 10)
    
    # ========================================
    # OPZIONE 3: CARTE PESCATE
    # ========================================
    draw_box = wx.StaticBoxSizer(wx.VERTICAL, self, "Carte Pescate per Turno")
    self.draw_count_radio = wx.RadioBox(
        self,
        label="Numero di carte pescate dal mazzo ad ogni click:",
        choices=["1 carta", "2 carte", "3 carte"],
        majorDimension=3,  # Horizontal layout
        style=wx.RA_SPECIFY_COLS
    )
    draw_box.Add(self.draw_count_radio, 0, wx.ALL | wx.EXPAND, 5)
    main_sizer.Add(draw_box, 0, wx.ALL | wx.EXPAND, 10)
    
    # ========================================
    # OPZIONE 4: TIMER
    # ========================================
    timer_box = wx.StaticBoxSizer(wx.VERTICAL, self, "Timer Partita")
    
    # CheckBox per abilitare/disabilitare timer
    self.timer_check = wx.CheckBox(self, label="Attiva timer (limite di tempo per partita)")
    timer_box.Add(self.timer_check, 0, wx.ALL, 5)
    
    # ComboBox per selezionare durata (5-60 minuti)
    timer_duration_sizer = wx.BoxSizer(wx.HORIZONTAL)
    timer_label = wx.StaticText(self, label="Durata timer:")
    timer_duration_sizer.Add(timer_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
    
    # Genera choices 5, 10, 15, ..., 60 minuti
    timer_choices = [f"{i} minuti" for i in range(5, 65, 5)]
    self.timer_combo = wx.ComboBox(
        self,
        choices=timer_choices,
        style=wx.CB_READONLY,
        value="10 minuti"  # Default
    )
    timer_duration_sizer.Add(self.timer_combo, 1, wx.EXPAND)
    timer_box.Add(timer_duration_sizer, 0, wx.ALL | wx.EXPAND, 5)
    
    main_sizer.Add(timer_box, 0, wx.ALL | wx.EXPAND, 10)
    
    # Store reference to main_sizer for STEP 2
    self.main_sizer = main_sizer
    
    # Set sizer (will be extended in STEP 2)
    self.SetSizer(main_sizer)
```

### 1.3 Aggiungi metodo `_load_settings_to_widgets()` - Prima metà

Dopo `_create_ui()`, aggiungi:

```python
def _load_settings_to_widgets(self) -> None:
    """Load current settings from controller into widgets.
    
    Called after _create_ui() to populate widgets with values from
    GameSettings (via OptionsWindowController).
    
    Maps GameSettings values to wx widget selections:
    - deck_type: "french" -> 0, "neapolitan" -> 1
    - difficulty_level: 1/2/3 -> RadioBox selection 0/1/2
    - draw_count: 1/2/3 -> RadioBox selection 0/1/2
    - max_time_game: seconds -> CheckBox + ComboBox (minutes)
    
    Note:
        This method will be extended in STEP 2 for options 5-8.
    """
    settings = self.options_controller.settings
    
    # 1. Tipo Mazzo
    deck_selection = 0 if settings.deck_type == "french" else 1
    self.deck_type_radio.SetSelection(deck_selection)
    
    # 2. Difficoltà (1/2/3 -> 0/1/2)
    self.difficulty_radio.SetSelection(settings.difficulty_level - 1)
    
    # 3. Carte Pescate (1/2/3 -> 0/1/2)
    self.draw_count_radio.SetSelection(settings.draw_count - 1)
    
    # 4. Timer
    timer_enabled = settings.max_time_game > 0
    self.timer_check.SetValue(timer_enabled)
    
    if timer_enabled:
        minutes = settings.max_time_game // 60
        self.timer_combo.SetValue(f"{minutes} minuti")
    else:
        self.timer_combo.SetValue("10 minuti")  # Default when disabled
    
    # Enable/disable combo based on checkbox
    self.timer_combo.Enable(timer_enabled)
```

### 1.4 Chiama `_load_settings_to_widgets()` in `_create_ui()`

Alla fine di `_create_ui()`, aggiungi:

```python
    # Set sizer
    self.SetSizer(main_sizer)
    
    # Load current settings into widgets
    self._load_settings_to_widgets()
```

**Commit 1**:
```
feat(options): add native wx widgets for options 1-4

- Replace virtual audio-only navigation with wx.RadioBox controls
- Add deck type RadioBox (Francese/Napoletano)
- Add difficulty RadioBox (1/2/3 carte)
- Add draw count RadioBox (1/2/3 carte)
- Add timer CheckBox + ComboBox (enable + 5-60 minutes)
- Remove EVT_CHAR_HOOK binding (no more arrows/numbers navigation)
- Add _load_settings_to_widgets() to populate from GameSettings

Native widgets provide:
- Automatic NVDA screen reader support
- Standard TAB navigation (wx behavior)
- Visual UI for mouse users
- Consistent accessibility

Refs: v1.8.0 feature - native wx widgets (part 1/2)
```

---

## STEP 2: Aggiungi Widget Nativi per Opzioni 5-8 + Pulsanti

**File**: `src/infrastructure/ui/options_dialog.py`

**Obiettivo**: Completare le restanti 4 opzioni + pulsanti Salva/Annulla.

### 2.1 Estendi `_create_ui()` - Seconda metà opzioni (5-8) + pulsanti

In `src/infrastructure/ui/options_dialog.py`, metodo `_create_ui()`, **DOPO** il timer_box:

```python
    # ========================================
    # OPZIONE 5: RICICLO SCARTI
    # ========================================
    shuffle_box = wx.StaticBoxSizer(wx.VERTICAL, self, "Riciclo Scarti")
    self.shuffle_radio = wx.RadioBox(
        self,
        label="Modalità di riciclo quando il tallone è vuoto:",
        choices=["Inversione (ribalta mazzo scarti)", "Mescolata (rimescola scarti)"],
        majorDimension=1,  # Vertical layout
        style=wx.RA_SPECIFY_COLS
    )
    shuffle_box.Add(self.shuffle_radio, 0, wx.ALL | wx.EXPAND, 5)
    main_sizer.Add(shuffle_box, 0, wx.ALL | wx.EXPAND, 10)
    
    # ========================================
    # OPZIONE 6: SUGGERIMENTI COMANDI
    # ========================================
    self.command_hints_check = wx.CheckBox(
        self,
        label="Suggerimenti comandi attivi (mostra aiuto per comandi disponibili)"
    )
    main_sizer.Add(self.command_hints_check, 0, wx.ALL, 10)
    
    # ========================================
    # OPZIONE 7: SISTEMA PUNTI
    # ========================================
    self.scoring_check = wx.CheckBox(
        self,
        label="Sistema punti attivo (calcola punteggio durante partita)"
    )
    main_sizer.Add(self.scoring_check, 0, wx.ALL, 10)
    
    # ========================================
    # OPZIONE 8: MODALITÀ TIMER
    # ========================================
    strict_box = wx.StaticBoxSizer(wx.VERTICAL, self, "Modalità Timer")
    self.timer_strict_radio = wx.RadioBox(
        self,
        label="Comportamento quando il timer scade:",
        choices=[
            "STRICT (sconfitta automatica)",
            "PERMISSIVE (penalità punti, partita continua)"
        ],
        majorDimension=1,  # Vertical layout
        style=wx.RA_SPECIFY_COLS
    )
    strict_box.Add(self.timer_strict_radio, 0, wx.ALL | wx.EXPAND, 5)
    main_sizer.Add(strict_box, 0, wx.ALL | wx.EXPAND, 10)
    
    # ========================================
    # PULSANTI SALVA / ANNULLA
    # ========================================
    button_sizer = wx.BoxSizer(wx.HORIZONTAL)
    
    self.btn_save = wx.Button(self, id=wx.ID_OK, label="&Salva modifiche")
    self.btn_save.SetToolTip("Salva le modifiche e chiudi la finestra opzioni")
    
    self.btn_cancel = wx.Button(self, id=wx.ID_CANCEL, label="&Annulla modifiche")
    self.btn_cancel.SetToolTip("Annulla le modifiche e chiudi la finestra opzioni")
    
    button_sizer.Add(self.btn_save, 0, wx.ALL, 5)
    button_sizer.Add(self.btn_cancel, 0, wx.ALL, 5)
    
    main_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 15)
    
    # Set sizer and auto-resize dialog
    self.SetSizer(main_sizer)
    self.Fit()  # Auto-resize to fit all widgets
    
    # Load current settings into widgets
    self._load_settings_to_widgets()
```

### 2.2 Estendi `_load_settings_to_widgets()` - Seconda metà

In `_load_settings_to_widgets()`, aggiungi **DOPO** la sezione timer:

```python
    # Enable/disable combo based on checkbox
    self.timer_combo.Enable(timer_enabled)
    
    # === AGGIUNTO IN STEP 2 ===
    
    # 5. Riciclo Scarti (False=Inversione, True=Mescolata)
    shuffle_selection = 1 if settings.shuffle_discards else 0
    self.shuffle_radio.SetSelection(shuffle_selection)
    
    # 6. Suggerimenti Comandi
    self.command_hints_check.SetValue(settings.command_hints_enabled)
    
    # 7. Sistema Punti
    self.scoring_check.SetValue(settings.scoring_enabled)
    
    # 8. Modalità Timer (True=STRICT, False=PERMISSIVE)
    strict_selection = 0 if settings.timer_strict_mode else 1
    self.timer_strict_radio.SetSelection(strict_selection)
```

**Commit 2**:
```
feat(options): add native wx widgets for options 5-8 and buttons

- Add shuffle mode RadioBox (Inversione/Mescolata)
- Add command hints CheckBox (ON/OFF)
- Add scoring system CheckBox (ON/OFF)
- Add timer strict mode RadioBox (STRICT/PERMISSIVE)
- Add Salva/Annulla buttons with mnemonics (ALT+S/ALT+A)
- Extend _load_settings_to_widgets() for options 5-8
- Call Fit() to auto-resize dialog to content

All 8 options now have native wx widgets:
- 5 RadioBox (deck, difficulty, draw, shuffle, strict)
- 3 CheckBox (timer enable, hints, scoring)
- 1 ComboBox (timer duration)
- 2 Buttons (save, cancel)

Complete visual UI with NVDA support.

Refs: v1.8.0 feature - native wx widgets (part 2/2)
```

---

## STEP 3: Implementa Event Binding e Save/Load Logic

**File**: `src/infrastructure/ui/options_dialog.py`

**Obiettivo**: Collegare widget a settings (live update + dirty tracking).

### 3.1 Aggiungi metodo `_bind_widget_events()`

Dopo `_load_settings_to_widgets()`, aggiungi:

```python
def _bind_widget_events(self) -> None:
    """Bind widget events to detect changes and update settings.
    
    All widget changes:
    1. Call _save_widgets_to_settings() (live update)
    2. Mark controller as DIRTY (modifications present)
    3. Enable save confirmation on ESC
    
    Special cases:
    - timer_check: Also enables/disables timer_combo
    - All others: Standard change detection
    
    Note:
        Settings are updated IMMEDIATELY (live mode).
        Original values saved in controller snapshot (for discard).
    """
    # RadioBox widgets
    self.deck_type_radio.Bind(wx.EVT_RADIOBOX, self.on_setting_changed)
    self.difficulty_radio.Bind(wx.EVT_RADIOBOX, self.on_setting_changed)
    self.draw_count_radio.Bind(wx.EVT_RADIOBOX, self.on_setting_changed)
    self.shuffle_radio.Bind(wx.EVT_RADIOBOX, self.on_setting_changed)
    self.timer_strict_radio.Bind(wx.EVT_RADIOBOX, self.on_setting_changed)
    
    # CheckBox widgets
    self.timer_check.Bind(wx.EVT_CHECKBOX, self.on_timer_toggled)  # Special handler
    self.command_hints_check.Bind(wx.EVT_CHECKBOX, self.on_setting_changed)
    self.scoring_check.Bind(wx.EVT_CHECKBOX, self.on_setting_changed)
    
    # ComboBox widget
    self.timer_combo.Bind(wx.EVT_COMBOBOX, self.on_setting_changed)
    
    # Buttons
    self.btn_save.Bind(wx.EVT_BUTTON, self.on_save_click)
    self.btn_cancel.Bind(wx.EVT_BUTTON, self.on_cancel_click)
```

### 3.2 Chiama `_bind_widget_events()` in `_create_ui()`

Alla fine di `_create_ui()`, **DOPO** `_load_settings_to_widgets()`:

```python
    # Load current settings into widgets
    self._load_settings_to_widgets()
    
    # Bind events for change detection
    self._bind_widget_events()
```

### 3.3 Aggiungi handler eventi

Dopo `_bind_widget_events()`, aggiungi:

```python
def on_setting_changed(self, event: wx.Event) -> None:
    """Handle any setting change from widgets.
    
    Called when user modifies any widget (RadioBox, CheckBox, ComboBox).
    
    Actions:
    1. Save current widget values to settings (live update)
    2. Mark controller as DIRTY (enable save confirmation)
    
    Args:
        event: wx.Event from widget (EVT_RADIOBOX, EVT_CHECKBOX, EVT_COMBOBOX)
    
    Note:
        Settings are updated immediately (GameSettings modified live).
        Original snapshot saved by controller.open_window() for rollback.
    """
    # Update GameSettings from current widget values
    self._save_widgets_to_settings()
    
    # Mark controller as dirty (modifications present)
    if self.options_controller.state == "OPEN_CLEAN":
        self.options_controller.state = "OPEN_DIRTY"
    
    # Propagate event
    event.Skip()

def on_timer_toggled(self, event: wx.CommandEvent) -> None:
    """Handle timer checkbox toggle.
    
    Special handler for timer enable/disable:
    - Enables/disables timer_combo based on checkbox state
    - Then calls standard on_setting_changed()
    
    Args:
        event: wx.CommandEvent from timer_check
    """
    enabled = self.timer_check.GetValue()
    self.timer_combo.Enable(enabled)
    
    # Call standard change handler
    self.on_setting_changed(event)

def on_save_click(self, event: wx.CommandEvent) -> None:
    """Handle Save button click.
    
    Calls controller.save_and_close() which:
    1. Updates settings snapshot (modifications become permanent)
    2. Resets controller state to CLOSED
    3. Returns TTS confirmation message
    
    Args:
        event: wx.CommandEvent from btn_save
    
    Note:
        Settings already updated live via on_setting_changed().
        This just commits the snapshot.
    """
    msg = self.options_controller.save_and_close()
    
    # Vocalize confirmation (optional - buttons are visual)
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
        event: wx.CommandEvent from btn_cancel
    
    Note:
        Rollback restores ALL settings to values at dialog open time.
    """
    msg = self.options_controller.discard_and_close()
    
    # Vocalize confirmation (optional - buttons are visual)
    if self.screen_reader and self.screen_reader.tts:
        self.screen_reader.tts.speak(msg, interrupt=True)
    
    # Close dialog with Cancel status
    self.EndModal(wx.ID_CANCEL)
```

### 3.4 Aggiungi metodo `_save_widgets_to_settings()`

Dopo gli handler eventi, aggiungi:

```python
def _save_widgets_to_settings(self) -> None:
    """Save current widget values back to GameSettings.
    
    Called on every widget change (live update mode).
    Maps wx widget selections to GameSettings attributes.
    
    Mappings:
    - deck_type_radio: 0->"french", 1->"neapolitan"
    - difficulty_radio: 0/1/2 -> difficulty_level 1/2/3
    - draw_count_radio: 0/1/2 -> draw_count 1/2/3
    - timer_check + timer_combo: boolean + minutes -> max_time_game seconds
    - shuffle_radio: 0->False (Inversione), 1->True (Mescolata)
    - command_hints_check: boolean -> command_hints_enabled
    - scoring_check: boolean -> scoring_enabled
    - timer_strict_radio: 0->True (STRICT), 1->False (PERMISSIVE)
    
    Note:
        This is "live update" mode - settings changed immediately.
        Original values preserved in controller snapshot for rollback.
    """
    settings = self.options_controller.settings
    
    # 1. Tipo Mazzo
    settings.deck_type = "french" if self.deck_type_radio.GetSelection() == 0 else "neapolitan"
    
    # 2. Difficoltà (0/1/2 -> 1/2/3)
    settings.difficulty_level = self.difficulty_radio.GetSelection() + 1
    
    # 3. Carte Pescate (0/1/2 -> 1/2/3)
    settings.draw_count = self.draw_count_radio.GetSelection() + 1
    
    # 4. Timer
    if self.timer_check.GetValue():
        # Extract minutes from "X minuti" string
        minutes_str = self.timer_combo.GetValue().split()[0]  # "10 minuti" -> "10"
        settings.max_time_game = int(minutes_str) * 60  # Convert to seconds
    else:
        settings.max_time_game = 0  # Disabled
    
    # 5. Riciclo Scarti (0->False, 1->True)
    settings.shuffle_discards = (self.shuffle_radio.GetSelection() == 1)
    
    # 6. Suggerimenti Comandi
    settings.command_hints_enabled = self.command_hints_check.GetValue()
    
    # 7. Sistema Punti
    settings.scoring_enabled = self.scoring_check.GetValue()
    
    # 8. Modalità Timer (0->True STRICT, 1->False PERMISSIVE)
    settings.timer_strict_mode = (self.timer_strict_radio.GetSelection() == 0)
```

**Commit 3**:
```
feat(options): implement widget event binding and settings sync

- Add _bind_widget_events() to connect all widgets to handlers
- Add on_setting_changed() for live settings update
- Add on_timer_toggled() for timer enable/disable logic
- Add on_save_click() / on_cancel_click() for buttons
- Add _save_widgets_to_settings() for widget->settings mapping
- Call binding in _create_ui() after widget creation

Live Update Mode:
- All widget changes update GameSettings immediately
- Controller marks state as DIRTY on first change
- Original values preserved in controller snapshot
- Rollback via discard_and_close() restores snapshot

Dirty Tracking:
- OPEN_CLEAN: No modifications, ESC closes directly
- OPEN_DIRTY: Modifications present, ESC asks confirmation

Refs: v1.8.0 feature - complete settings sync
```

---

## STEP 4: ESC Intelligente + open_window() Call

**File**: `src/infrastructure/ui/options_dialog.py`, `test.py`

**Obiettivo**: ESC chiama `close_window()` con conferma se modifiche presenti.

### 4.1 Aggiungi override `on_key_down()` - ESC intelligente

In `src/infrastructure/ui/options_dialog.py`, dopo `_save_widgets_to_settings()`, aggiungi:

```python
def on_key_down(self, event: wx.KeyEvent) -> None:
    """Handle keyboard events for ESC key only.
    
    ESC behavior (v1.8.0 smart close):
    - If no modifications (OPEN_CLEAN): Close directly
    - If modifications present (OPEN_DIRTY): Show save confirmation dialog
      * Dialog options: Sì (save), No (discard), Annulla (cancel)
      * If user cancels: Stay open (don't close)
    
    Other keys: Propagated normally (TAB, arrows, SPACE handled by wx)
    
    Args:
        event: wx.KeyEvent from keyboard
    
    Note:
        Virtual navigation (arrows/numbers) removed in v1.8.0.
        Use standard wx navigation: TAB between widgets,
        arrows within RadioBox/ComboBox.
    """
    key_code = event.GetKeyCode()
    
    # ESC: Smart close with confirmation if dirty
    if key_code == wx.WXK_ESCAPE:
        # Call close_window() which handles DIRTY/CLEAN states
        msg = self.options_controller.close_window()
        
        # Check if dialog was actually closed
        # (controller sets state to CLOSED if user confirmed save/discard)
        if self.options_controller.state == "CLOSED":
            # Closing confirmed (saved or discarded)
            if self.screen_reader and self.screen_reader.tts:
                self.screen_reader.tts.speak(msg, interrupt=True)
            
            # Determine exit code based on message content
            # ("salv" in msg means user chose to save)
            exit_code = wx.ID_OK if "salv" in msg.lower() else wx.ID_CANCEL
            self.EndModal(exit_code)
        else:
            # Closing cancelled (user pressed Annulla in save dialog)
            # or fallback mode (no dialog_manager available)
            if self.screen_reader and self.screen_reader.tts:
                self.screen_reader.tts.speak(msg, interrupt=True)
            # Stay open (don't call EndModal)
        
        return  # Event handled
    
    # All other keys: Propagate normally (TAB, arrows, SPACE, etc.)
    event.Skip()
```

### 4.2 Bind `EVT_CHAR_HOOK` per ESC

In `__init__()`, **DOPO** `_create_ui()`, aggiungi:

```python
    # Bind ESC key for smart close
    self.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)
```

**Nota**: Questo va aggiunto nell'`__init__`, non nel `_create_ui()`, perché il bind deve avvenire sul dialog, non sui widget interni.

### 4.3 Modifica `show_options()` in test.py - Aggiungi open_window()

In `test.py`, metodo `show_options()` (linee ~208-235):

**PRIMA**:
```python
def show_options(self) -> None:
    from src.infrastructure.ui.options_dialog import OptionsDialog
    
    self.is_options_mode = True
    
    dlg = OptionsDialog(
        parent=self.frame,
        controller=self.gameplay_controller.options_controller,
        screen_reader=self.screen_reader
    )
    dlg.ShowModal()
    dlg.Destroy()
    
    self.is_options_mode = False
```

**DOPO**:
```python
def show_options(self) -> None:
    """Show options window using OptionsDialog with native wx widgets.
    
    Opens modal OptionsDialog with:
    - Native wx.RadioBox, wx.CheckBox, wx.ComboBox for all 8 options
    - Salva/Annulla buttons
    - Smart ESC (confirmation if modifications present)
    
    Flow:
    1. Set is_options_mode flag
    2. Call controller.open_window() (sets state=OPEN_CLEAN, saves snapshot)
    3. Vocalize opening message (optional)
    4. Create OptionsDialog with controller + screen_reader
    5. Show modal (blocks until closed)
    6. Clean up and reset flag
    
    State Management:
    - controller.open_window() saves settings snapshot for change tracking
    - Any widget change sets state to OPEN_DIRTY
    - ESC with OPEN_DIRTY triggers save confirmation dialog
    - Buttons or ESC with OPEN_CLEAN close directly
    
    Navigation:
    - TAB: Move between widgets (standard wx)
    - UP/DOWN: Change value in RadioBox/ComboBox
    - SPACE: Toggle CheckBox
    - ENTER: Activate focused button
    - ESC: Smart close (confirmation if dirty)
    """
    from src.infrastructure.ui.options_dialog import OptionsDialog
    
    print("\n" + "="*60)
    print("APERTURA FINESTRA OPZIONI (OptionsDialog - Native Widgets)")
    print("="*60)
    
    self.is_options_mode = True
    
    # Initialize controller state (OPEN_CLEAN, save snapshot)
    open_msg = self.gameplay_controller.options_controller.open_window()
    if self.screen_reader:
        self.screen_reader.tts.speak(open_msg, interrupt=True)
        wx.MilliSleep(500)  # Brief pause before showing dialog
    
    # Create and show modal options dialog
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

**Commit 4**:
```
feat(options): implement smart ESC with save confirmation

- Add on_key_down() override for ESC key handling
- ESC calls controller.close_window() (handles DIRTY/CLEAN)
- If OPEN_DIRTY: Shows save prompt with Sì/No/Annulla options
- If user cancels: Dialog stays open (state remains OPEN_DIRTY)
- Bind EVT_CHAR_HOOK in __init__ for ESC detection
- Add open_window() call in show_options() to initialize state
- Vocalize opening message with optional TTS
- Log dialog result (OK/CANCEL) for debugging

Smart ESC behavior:
- No changes → ESC closes directly (OPEN_CLEAN)
- Has changes → ESC asks "Vuoi salvare?" (OPEN_DIRTY)
- User can save, discard, or cancel (stay open)

Consistent with refactoring-engine branch behavior.

Refs: v1.8.0 feature - smart close with change tracking
```

---

## STEP 5: Fix Reset Gameplay su Abbandono (4 Scenari)

**File**: `test.py`

**Obiettivo**: Garantire `engine.reset_game()` in TUTTI gli scenari di abbandono partita.

### 5.1 Fix `show_abandon_game_dialog()` - Aggiungi reset

In `test.py`, metodo `show_abandon_game_dialog()` (linee ~255-268):

**CERCA** questo blocco:
```python
if result:
    self.return_to_menu()
```

**SOSTITUISCI** con:
```python
if result:
    # Reset game engine (clear cards, score, timer)
    print("\n→ User confirmed abandon - Resetting game engine")
    self.engine.reset_game()
    
    # Return to main menu
    self.return_to_menu()
```

### 5.2 Fix `confirm_abandon_game()` - Aggiungi reset (doppio ESC)

In `test.py`, metodo `confirm_abandon_game()` (linee ~282-295):

**CERCA** questo blocco:
```python
self._timer_expired_announced = False
self.return_to_menu()
```

**SOSTITUISCI** con:
```python
# Reset game engine (clear cards, score, timer)
print("\n→ Double-ESC detected - Resetting game engine")
self.engine.reset_game()

self._timer_expired_announced = False
self.return_to_menu()
```

### 5.3 Fix `_handle_game_over_by_timeout()` - Aggiungi reset

In `test.py`, metodo `_handle_game_over_by_timeout()` (linee ~390-425):

**CERCA** questo blocco (verso la fine):
```python
if self.screen_reader:
    self.screen_reader.tts.speak(defeat_msg, interrupt=True)
    wx.MilliSleep(2000)

self._timer_expired_announced = False
self.return_to_menu()
```

**SOSTITUISCI** con:
```python
if self.screen_reader:
    self.screen_reader.tts.speak(defeat_msg, interrupt=True)
    wx.MilliSleep(2000)

# Reset game engine (clear cards, score, timer)
print("\n→ Timeout defeat - Resetting game engine")
self.engine.reset_game()

self._timer_expired_announced = False
self.return_to_menu()
```

### 5.4 Fix `handle_game_ended()` - Aggiungi reset se no rematch

In `test.py`, metodo `handle_game_ended()` (linee ~305-325):

**CERCA** questo blocco:
```python
else:
    print("→ User declined rematch - Returning to menu")
    self.return_to_menu()
```

**SOSTITUISCI** con:
```python
else:
    print("→ User declined rematch - Returning to menu")
    # Reset game engine before returning to menu
    self.engine.reset_game()
    self.return_to_menu()
```

**Commit 5**:
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

## STEP 6: Aggiorna CHANGELOG.md

**File**: `CHANGELOG.md`

**Obiettivo**: Documentare release v1.8.0 con feature + bug fix.

### 6.1 Aggiungi sezione v1.8.0

In `CHANGELOG.md`, **IN CIMA** (prima di `## [1.7.5]`), aggiungi:

```markdown
## [1.8.0] - 2026-02-13

### Added
- **OptionsDialog con wx widgets nativi completi**: Tutte le 8 opzioni ora hanno controlli wx visibili
  - RadioBox per Tipo Mazzo (Francese/Napoletano)
  - RadioBox per Difficoltà (1/2/3 carte)
  - RadioBox per Carte Pescate (1/2/3)
  - CheckBox + ComboBox per Timer (enable + durata 5-60 minuti)
  - RadioBox per Riciclo Scarti (Inversione/Mescolata)
  - CheckBox per Suggerimenti Comandi (ON/OFF)
  - CheckBox per Sistema Punti (ON/OFF)
  - RadioBox per Modalità Timer (STRICT/PERMISSIVE)
- **Pulsanti Salva/Annulla**: Controlli nativi TAB-navigabili con mnemonics ALT+S/ALT+A
- **ESC intelligente con tracking modifiche**: Chiede conferma salvataggio solo se ci sono modifiche non salvate
- **Snapshot settings all'apertura**: `open_window()` salva stato iniziale per rollback su annullamento

### Fixed
- **Reset gameplay su abbandono ESC**: `engine.reset_game()` ora chiamato quando si abbandona partita con conferma
- **Reset gameplay su doppio ESC**: `engine.reset_game()` chiamato anche per uscita rapida (< 2 secondi)
- **Reset gameplay su timeout STRICT**: `engine.reset_game()` chiamato quando timer scade in modalità STRICT
- **Reset gameplay su rifiuto rematch**: `engine.reset_game()` chiamato quando utente rifiuta nuova partita dopo vittoria/sconfitta

### Changed
- **Navigazione opzioni completamente riscritta**: Da virtuale (frecce/numeri) a standard wxPython (TAB tra widget, frecce dentro widget)
- **Accessibilità NVDA migliorata**: Widget nativi letti automaticamente da screen reader (no TTS custom)
- **UI ibrida**: Supporto completo mouse (click su widget) + tastiera (TAB navigation)
- **Live update mode**: Settings aggiornati immediatamente quando cambi widget (con rollback su annulla)

### Removed
- **Navigazione virtuale opzioni**: Rimossi comandi frecce SU/GIÙ e numeri 1-8 (sostituiti da TAB standard)
- **EVT_CHAR_HOOK per frecce**: Rimosso handler custom keyboard (tranne ESC)
- **Metodi controller navigate_up/down/jump_to_option**: Non più chiamati da OptionsDialog (logic spostata in widgets)

### Technical
- `OptionsDialog._create_ui()`: Completamente riscritto con 8 wx.RadioBox/CheckBox/ComboBox + 2 wx.Button
- `OptionsDialog._load_settings_to_widgets()`: Popola widget da GameSettings all'apertura
- `OptionsDialog._save_widgets_to_settings()`: Salva widget a GameSettings su ogni modifica (live)
- `OptionsDialog._bind_widget_events()`: Collega tutti i widget a handler change detection
- `OptionsDialog.on_setting_changed()`: Handler generico per widget changes (marca DIRTY)
- `OptionsDialog.on_timer_toggled()`: Handler speciale per timer enable/disable
- `OptionsDialog.on_save_click()` / `on_cancel_click()`: Handler pulsanti (commit/rollback)
- `OptionsDialog.on_key_down()`: ESC intelligente con chiamata `controller.close_window()`
- `SolitarioController.show_options()`: Chiama `options_controller.open_window()` prima di mostrare dialog
- `SolitarioController.show_abandon_game_dialog()`: Aggiunta chiamata `engine.reset_game()`
- `SolitarioController.confirm_abandon_game()`: Aggiunta chiamata `engine.reset_game()`
- `SolitarioController._handle_game_over_by_timeout()`: Aggiunta chiamata `engine.reset_game()`
- `SolitarioController.handle_game_ended()`: Aggiunta chiamata `engine.reset_game()` se no rematch

### Migration Notes
Aggiornamento da v1.7.5 a v1.8.0:

**Opzioni - Nuova Esperienza**:
- **Non più frecce/numeri**: Usa TAB per navigare tra opzioni, frecce SU/GIÙ per cambiare valore dentro RadioBox/ComboBox
- **Widget visibili**: Ora vedi tutti i controlli (radio buttons, checkboxes, dropdown)
- **ESC intelligente**: Se modifichi opzioni, ESC chiede "Vuoi salvare?" prima di chiudere
- **Pulsanti sempre visibili**: "Salva modifiche" e "Annulla modifiche" in fondo al dialog
- **Accessibilità**: NVDA legge automaticamente tutti i widget nativi

**Gameplay - Reset Garantito**:
- Abbandonare partita (qualsiasi metodo) ora resetta completamente lo stato
- Nessuna carta o dato residuo tra partite
- Menu sempre pulito dopo abbandono

### Breaking Changes
**Navigazione Opzioni**: Comandi vecchi (frecce/numeri) **NON funzionano più**. Usa TAB + frecce standard.

Se usavi script/automazione che simulavano frecce/numeri nel dialog opzioni, dovrai aggiornarli per usare TAB navigation.
```

**Commit 6**:
```
docs(changelog): add v1.8.0 release notes

- Document complete OptionsDialog rewrite with native wx widgets
- Document all 8 options now have visual controls
- Document smart ESC with save confirmation
- Document all reset_game() bug fixes (4 scenarios)
- Add technical details for all new methods
- Add migration notes with breaking changes warning
- Document navigation change: arrows/numbers → TAB standard

Version increment: 1.7.5 → 1.8.0 (MINOR)
Reason: Major feature (native widgets + navigation rewrite) + critical bug fixes

Breaking: Virtual navigation (arrows/numbers) removed
```

---

## 🧪 Testing Checklist Completo

### Test 1: Widget Nativi Opzioni (8 test)

✅ **Test 1A**: Tipo Mazzo RadioBox
1. Apri opzioni → verifica che RadioBox "Tipo Mazzo" sia visibile
2. Click su "Napoletano" → verifica selezione
3. Usa freccia GIÙ → verifica che cambi selezione
4. **Atteso**: NVDA legge "Napoletano selezionato"

✅ **Test 1B**: Difficoltà RadioBox
1. TAB a "Difficoltà" → verifica 3 opzioni orizzontali
2. Freccia DESTRA → passa da 1 a 2 a 3 carte
3. **Atteso**: Selezione visibile + NVDA legge

✅ **Test 1C**: Carte Pescate RadioBox
1. TAB a "Carte Pescate" → verifica 3 opzioni
2. Click su "3 carte" → verifica selezione

✅ **Test 1D**: Timer CheckBox + ComboBox
1. TAB a "Timer" → verifica CheckBox + ComboBox
2. SPACE su CheckBox → verifica che ComboBox si abiliti
3. TAB al ComboBox → freccia GIÙ → seleziona "20 minuti"
4. SPACE su CheckBox di nuovo → verifica che ComboBox si disabiliti
5. **Atteso**: ComboBox grigio quando checkbox deselezionato

✅ **Test 1E**: Riciclo Scarti RadioBox
1. TAB a "Riciclo Scarti" → verifica 2 opzioni verticali
2. Freccia GIÙ → cambia da Inversione a Mescolata

✅ **Test 1F**: Suggerimenti Comandi CheckBox
1. TAB a "Suggerimenti comandi" → verifica CheckBox standalone
2. SPACE → toggle ON/OFF
3. **Atteso**: Checkmark visibile quando ON

✅ **Test 1G**: Sistema Punti CheckBox
1. TAB a "Sistema punti" → SPACE → toggle

✅ **Test 1H**: Modalità Timer RadioBox
1. TAB a "Modalità Timer" → verifica 2 opzioni
2. Freccia GIÙ → cambia STRICT ↔ PERMISSIVE

### Test 2: Pulsanti Salva/Annulla (4 test)

✅ **Test 2A**: Pulsante Salva funziona
1. Apri opzioni, modifica Tipo Mazzo
2. TAB fino a "Salva modifiche" → INVIO
3. **Atteso**: Dialog chiuso, modifiche persistite
4. Riapri opzioni → verifica che Tipo Mazzo sia quello selezionato

✅ **Test 2B**: Pulsante Annulla funziona
1. Apri opzioni, modifica Difficoltà
2. TAB a "Annulla modifiche" → INVIO
3. **Atteso**: Dialog chiuso, modifiche NON persistite
4. Riapri opzioni → verifica che Difficoltà sia quella originale

✅ **Test 2C**: Mnemonics ALT+S / ALT+A
1. Apri opzioni, modifica opzione
2. Premi ALT+S
3. **Atteso**: Salva e chiudi
4. Riapri, modifica, premi ALT+A
5. **Atteso**: Annulla e chiudi

✅ **Test 2D**: Click mouse su pulsanti
1. Apri opzioni, modifica opzione
2. Click mouse su "Salva modifiche"
3. **Atteso**: Funziona come INVIO/ALT+S

### Test 3: ESC Intelligente (4 test)

✅ **Test 3A**: ESC senza modifiche chiude direttamente
1. Apri opzioni
2. NON modificare nulla
3. Premi ESC
4. **Atteso**: Dialog chiuso immediatamente, nessun prompt

✅ **Test 3B**: ESC con modifiche chiede conferma
1. Apri opzioni, modifica Tipo Mazzo
2. Premi ESC
3. **Atteso**: Dialog conferma "Vuoi salvare le modifiche?"
4. Clicca "Sì"
5. **Atteso**: Modifiche salvate, dialog chiuso

✅ **Test 3C**: ESC + conferma "No" annulla modifiche
1. Apri opzioni, modifica Difficoltà
2. Premi ESC → clicca "No" nel dialog conferma
3. **Atteso**: Modifiche annullate, dialog chiuso
4. Riapri opzioni → verifica rollback

✅ **Test 3D**: ESC + conferma "Annulla" rimane aperto
1. Apri opzioni, modifica Timer
2. Premi ESC → clicca "Annulla" nel dialog conferma
3. **Atteso**: Dialog conferma chiuso, dialog opzioni RIMANE APERTO
4. Verifica che modifica sia ancora presente (non salvata né annullata)

### Test 4: Reset Gameplay (4 test)

✅ **Test 4A**: ESC con conferma resetta partita
1. Avvia partita, fai alcune mosse
2. Premi ESC → clicca "Sì" in dialog abbandono
3. **Atteso**: Console mostra "→ User confirmed abandon - Resetting game engine"
4. Torna al menu
5. Avvia nuova partita → verifica che NON ci siano carte vecchie

✅ **Test 4B**: Doppio ESC resetta partita
1. Avvia partita, fai mosse
2. Premi ESC 2 volte velocemente (< 2 secondi)
3. **Atteso**: Console "→ Double-ESC detected - Resetting game engine"
4. Torna al menu, avvia nuova partita → verifica reset

✅ **Test 4C**: Timeout STRICT resetta partita
1. Apri opzioni → Timer 1 minuto STRICT
2. Avvia partita, aspetta 1 minuto
3. **Atteso**: Console "→ Timeout defeat - Resetting game engine"
4. Menu automatico, avvia nuova partita → verifica reset

✅ **Test 4D**: Rifiuto rematch resetta partita
1. Vinci partita → clicca "Menu" nel dialog vittoria
2. **Atteso**: Console mostra reset chiamato
3. Avvia nuova partita → verifica reset

### Test 5: Regressione (4 test)

✅ **Test 5A**: Comando "N" (nuova partita) funziona
1. Avvia partita, premi "N"
2. **Atteso**: Dialog conferma → reset + nuova partita

✅ **Test 5B**: Rematch funziona
1. Vinci partita, clicca "Nuova Partita"
2. **Atteso**: Reset + nuova partita

✅ **Test 5C**: Tutte le opzioni si salvano correttamente
1. Apri opzioni, modifica tutte le 8 opzioni
2. Clicca "Salva modifiche"
3. Riapri opzioni → verifica che TUTTE le 8 modifiche siano persistite

✅ **Test 5D**: Annulla ripristina tutte le opzioni
1. Apri opzioni, modifica tutte le 8 opzioni
2. Clicca "Annulla modifiche"
3. Riapri opzioni → verifica che TUTTE le 8 opzioni siano ai valori originali

---

## 📝 Riepilogo Commit (6 totali)

1. **feat(options): add native wx widgets for options 1-4**
   - RadioBox per deck/difficulty/draw + CheckBox/ComboBox per timer

2. **feat(options): add native wx widgets for options 5-8 and buttons**
   - RadioBox shuffle/strict + CheckBox hints/scoring + pulsanti

3. **feat(options): implement widget event binding and settings sync**
   - Event binding + live update + dirty tracking

4. **feat(options): implement smart ESC with save confirmation**
   - ESC intelligente + open_window() call

5. **fix(gameplay): add explicit reset_game() on all abandon scenarios**
   - 4 fix reset (ESC, doppio ESC, timeout, no rematch)

6. **docs(changelog): add v1.8.0 release notes**
   - Release notes complete con breaking changes

---

## ⚠️ Note Importanti per Copilot

1. **NON modificare** file non elencati nel piano
2. **NON refactorare** codice non correlato alle modifiche specifiche
3. **MANTIENI** commenti esistenti, aggiungi solo dove necessario per chiarire
4. **RIMUOVI** completamente il vecchio `on_key_down()` con navigazione frecce/numeri (STEP 1)
5. **TESTA** manualmente dopo commit 3 (widget events) e commit 5 (reset gameplay)
6. **VERIFICA** che `engine.reset_game()` esista e funzioni correttamente
7. **SEGUI** esattamente l'ordine dei commit (1 → 2 → 3 → 4 → 5 → 6)
8. **USA** i messaggi di commit esatti forniti nel piano

---

## 🎯 Stato Finale Atteso v1.8.0

### Opzioni (Native Widgets)

✅ **UI completa**: 8 opzioni con widget wx nativi visibili
✅ **Navigazione standard**: TAB tra widget, frecce dentro widget
✅ **Accessibilità NVDA**: Lettura automatica di tutti i widget
✅ **ESC intelligente**: Conferma solo se modifiche presenti
✅ **Live update**: Settings aggiornati immediatamente con rollback su annulla
✅ **Pulsanti nativi**: Salva/Annulla con mnemonics ALT+S/ALT+A
✅ **Mouse support**: Click funziona su tutti i widget

### Gameplay (Reset Completo)

✅ **ESC + conferma**: Reset garantito prima di tornare al menu
✅ **Doppio ESC**: Reset garantito prima di tornare al menu
✅ **Timeout STRICT**: Reset garantito prima di tornare al menu
✅ **Rifiuto rematch**: Reset garantito prima di tornare al menu
✅ **Comando "N"**: Reset già presente (nessuna modifica)

### Parità Funzionale

✅ **refactoring-engine**: 100% feature parity raggiunta (anzi, superata con UI nativa)
✅ **Accessibilità**: NVDA legge automaticamente tutti i controlli (meglio di vecchia versione)
✅ **UX ibrida**: Supporto completo tastiera + mouse
✅ **Stato consistente**: Nessuna carta o dato residuo tra partite

---

**Copilot**: Inizia con STEP 1 (commit 1). Dopo ogni commit, attendi conferma prima di procedere al STEP successivo.

**Fine documento di implementazione v1.8.0**