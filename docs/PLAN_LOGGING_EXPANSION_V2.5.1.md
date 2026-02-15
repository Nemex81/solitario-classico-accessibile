# Piano di Implementazione: Logging System Expansion v2.5.1

**Versione Target**: v2.5.1  
**Branch**: `refactoring-engine`  
**Effort Totale**: 15 commit atomici (20-30 minuti per Copilot)  
**TODO Master**: `docs/TODO_LOGGING_EXPANSION_V2.5.1.md`

---

## 🎯 Obiettivo

Espandere il sistema di logging esistente per tracciare **24 categorie di eventi** attualmente non loggati. Il sistema `src/infrastructure/logging/game_logger.py` è già implementato (v2.3.0) e fornisce funzioni semantiche pronte all'uso.

**NO Nuove Funzioni**: Usare SOLO le funzioni esistenti in `game_logger.py`.

---

## 📖 Sistema Logging Esistente (Referenza Rapida)

### Funzioni Disponibili (v2.3.0)

```python
from src.infrastructure.logging import game_logger as log

# Lifecycle
log.game_started(deck_type, difficulty, timer_enabled)  # INFO
log.game_won(elapsed_time, moves_count, score)           # INFO
log.game_abandoned(elapsed_time, moves_count)            # INFO

# Player Actions
log.card_moved(from_pile, to_pile, card, success)       # INFO/WARNING
log.cards_drawn(count)                                   # DEBUG
log.waste_recycled(recycle_count)                        # INFO
log.invalid_action(action, reason)                       # WARNING

# UI Navigation
log.panel_switched(from_panel, to_panel)                 # INFO
log.dialog_shown(dialog_type, title)                     # DEBUG
log.dialog_closed(dialog_type, result)                   # DEBUG
log.keyboard_command(command, context)                   # DEBUG

# Errors & Warnings
log.error_occurred(error_type, details, exception)       # ERROR
log.warning_issued(warning_type, message)                # WARNING

# Debug Helpers
log.debug_state(state_name, state_data: dict)            # DEBUG

# Settings Changes
log.settings_changed(setting_name, old_value, new_value) # INFO

# Timer
log.timer_started(duration)                              # INFO
log.timer_expired()                                      # WARNING

# Navigation Tracking
log.cursor_moved(from_position, to_position)             # DEBUG
log.pile_jumped(from_pile, to_pile)                      # DEBUG

# Query Commands
log.info_query_requested(query_type, context)            # INFO
```

### Livelli Log Raccomandati

| Livello | Quando Usare | Esempi |
|---------|--------------|--------|
| **DEBUG** | Operazioni frequenti, dettagli interni | Cursor move, TTS vocalization, card selection |
| **INFO** | Eventi significativi, UX analytics | Panel switch, settings change, game won |
| **WARNING** | Situazioni anomale ma gestite | Invalid action, timer expired, file not found |
| **ERROR** | Errori critici con eccezione | File corrupted, TTS initialization failed |

---

## FASE 1: UI LIFECYCLE & PANEL TRANSITIONS (⭐⭐⭐ Alta Priorità)

**Obiettivo**: Tracciare ogni transizione panel per debug UI freeze (Bug #68 storia).  
**Commits**: 4 atomici  
**Tempo Stimato Copilot**: 5-8 minuti

---

### COMMIT 1.1: Log panel transitions in acs_wx.py

**File**: `acs_wx.py`  
**Linee Modificate**: ~218, ~264  
**Funzione Usata**: `log.panel_switched(from_panel, to_panel)`

#### Modifiche Richieste

**1. Metodo `start_gameplay()` (linea ~218)**

```python
def start_gameplay(self) -> None:
    """Start gameplay (called from MenuPanel or rematch)."""
    if self.view_manager:
        # CRITICAL: Hide current panel before showing gameplay
        current_panel_name = self.view_manager.get_current_view()
        
        # ✅ ADD THIS LOG
        log.panel_switched(current_panel_name or "none", "gameplay")
        
        if current_panel_name:
            current_panel = self.view_manager.get_panel(current_panel_name)
            if current_panel:
                current_panel.Hide()
        
        # Show gameplay panel
        self.view_manager.show_panel('gameplay')
        # ... rest of method ...
```

**Rationale**: Traccia transizione menu→gameplay e rematch (gameplay→gameplay).

**2. Metodo `return_to_menu()` (linea ~264)**

```python
def return_to_menu(self) -> None:
    """Return from gameplay to menu."""
    if not self.view_manager:
        print("⚠ ViewManager not initialized")
        return
    
    # ✅ ADD THIS LOG
    current_view = self.view_manager.get_current_view()
    log.panel_switched(current_view or "unknown", "menu")
    
    # Show menu panel
    self.view_manager.show_panel('menu')
    # ... rest of method ...
```

**Rationale**: Traccia ritorno a menu da gameplay/opzioni.

#### Testing

```bash
# Avvia app
python acs_wx.py

# Azioni:
1. Menu → "Nuova Partita" (menu→gameplay)
2. ESC → Conferma abbandono (gameplay→menu)
3. Opzioni → Salva (menu→menu)

# Verifica solitaire.log:
# INFO - ui - Panel transition: menu → gameplay
# INFO - ui - Panel transition: gameplay → menu
```

#### Commit Message

```
feat(logging): add panel transition logs in start_gameplay and return_to_menu

Adds log.panel_switched() calls to track:
- Menu to gameplay transitions
- Gameplay to menu transitions (abandon/timeout)
- Rematch transitions (gameplay to gameplay)

Helps debug UI freeze issues (Bug #68 history).

Version: v2.5.1 - FASE 1 (1/4)
```

---

### COMMIT 1.2: Log panel hiding in safe handlers

**File**: `acs_wx.py`  
**Linee Modificate**: ~485, ~698, ~722, ~768  
**Funzione Usata**: `log.debug_state(state_name, state_data: dict)`

#### Modifiche Richieste

**1. Metodo `_safe_abandon_to_menu()` (linea ~485)**

```python
def _safe_abandon_to_menu(self) -> None:
    """Deferred handler for abandon game → menu transition."""
    print("\n→ Executing deferred abandon transition...")
    
    # ✅ ADD THIS LOG
    log.debug_state("abandon_transition", {
        "trigger": "ESC_confirmed",
        "from_panel": "gameplay"
    })
    
    # Hide gameplay panel
    if self.view_manager:
        gameplay_panel = self.view_manager.get_panel('gameplay')
        if gameplay_panel:
            gameplay_panel.Hide()
            
            # ✅ ADD THIS LOG
            log.debug_state("panel_hidden", {"panel": "gameplay"})
    
    # Reset game engine
    self.engine.reset_game()
    self._timer_expired_announced = False
    
    # Return to menu
    self.return_to_menu()
    
    print("→ Abandon transition completed\n")
```

**2. Metodo `_safe_timeout_to_menu()` (linea ~768)**

Pattern identico:

```python
def _safe_timeout_to_menu(self) -> None:
    print("\n→ Executing deferred timeout transition...")
    
    # ✅ ADD THIS LOG
    log.debug_state("timeout_transition", {
        "trigger": "timer_expired",
        "from_panel": "gameplay"
    })
    
    # Hide gameplay panel
    if self.view_manager:
        gameplay_panel = self.view_manager.get_panel('gameplay')
        if gameplay_panel:
            gameplay_panel.Hide()
            
            # ✅ ADD THIS LOG
            log.debug_state("panel_hidden", {"panel": "gameplay"})
    
    # ... rest of method ...
```

**3. Metodo `_safe_return_to_main_menu()` (linea ~722)**

Pattern identico:

```python
def _safe_return_to_main_menu(self) -> None:
    print("→ _safe_return_to_main_menu() called")
    
    # ✅ ADD THIS LOG
    log.debug_state("decline_rematch_transition", {
        "trigger": "rematch_declined",
        "from_panel": "gameplay"
    })
    
    # 0. Hide gameplay panel
    if self.view_manager:
        gameplay_panel = self.view_manager.get_panel('gameplay')
        if gameplay_panel:
            gameplay_panel.Hide()
            
            # ✅ ADD THIS LOG
            log.debug_state("panel_hidden", {"panel": "gameplay"})
    
    # ... rest of method ...
```

#### Testing

```bash
# Test Scenario 1: ESC Abandon
python acs_wx.py
# Gameplay → ESC → Conferma
# Verifica log:
# DEBUG - game - State [abandon_transition]: {'trigger': 'ESC_confirmed', ...}
# DEBUG - game - State [panel_hidden]: {'panel': 'gameplay'}

# Test Scenario 2: Timer Timeout (strict mode)
# Abilita timer strict 1 minuto
# Aspetta timeout
# Verifica log:
# DEBUG - game - State [timeout_transition]: {'trigger': 'timer_expired', ...}

# Test Scenario 3: Decline Rematch
# Vinci partita → Rematch NO
# Verifica log:
# DEBUG - game - State [decline_rematch_transition]: {'trigger': 'rematch_declined', ...}
```

#### Commit Message

```
feat(logging): add panel hiding logs in safe deferred handlers

Adds log.debug_state() calls to track panel hiding in:
- _safe_abandon_to_menu() (ESC confirmed)
- _safe_timeout_to_menu() (timer expired)
- _safe_return_to_main_menu() (rematch declined)

Helps debug UI freeze when panels remain visible.

Version: v2.5.1 - FASE 1 (2/4)
```

---

### COMMIT 1.3: Log ViewManager panel swaps

**File**: `src/infrastructure/ui/view_manager.py`  
**Linee Modificate**: ~40-60 (metodo `show_panel`)  
**Funzione Usata**: `log.panel_switched()`, `log.warning_issued()`

#### Modifiche Richieste

**Aggiungere import all'inizio del file**:

```python
# Existing imports...
from src.infrastructure.logging import game_logger as log  # ✅ ADD
```

**Modificare metodo `show_panel()`**:

```python
def show_panel(self, panel_name: str) -> None:
    """Show specific panel by name.
    
    Args:
        panel_name: Name of panel to show ('menu' or 'gameplay')
    """
    # Store previous view
    prev_panel = self._current_view
    
    # Validate panel exists
    if panel_name not in self._panels:
        # ✅ ADD THIS LOG
        log.warning_issued("ViewManager", f"Panel '{panel_name}' not registered")
        print(f"⚠ Panel '{panel_name}' not found in ViewManager")
        return
    
    # Hide current panel if any
    if self._current_view and self._current_view in self._panels:
        current_panel = self._panels[self._current_view]
        if current_panel:
            current_panel.Hide()
    
    # Show target panel
    target_panel = self._panels[panel_name]
    if target_panel:
        target_panel.Show()
        target_panel.SetFocus()
    
    # ✅ ADD THIS LOG (BEFORE updating _current_view)
    log.panel_switched(prev_panel or "none", panel_name)
    
    # Update current view
    self._current_view = panel_name
    
    print(f"✓ ViewManager: Switched to '{panel_name}' panel")
```

**Rationale**: Centralizza logging di TUTTE le transizioni panel. Questo log cattura anche transizioni indirette (es. opzioni che chiamano `show_panel` direttamente).

#### Testing

```bash
# Ciclo completo:
python acs_wx.py

# Azioni:
1. Menu → Nuova Partita
2. Gameplay → ESC → Conferma
3. Menu → Opzioni → Salva
4. Menu → Esci

# Verifica solitaire.log:
# Ogni show_panel() genera:
# INFO - ui - Panel transition: [prev] → [next]

# Se provi panel inesistente:
# WARNING - error - WARNING [ViewManager]: Panel 'invalid' not registered
```

#### Commit Message

```
feat(logging): add ViewManager panel swap logs

Adds centralized logging in ViewManager.show_panel():
- Logs every panel transition (menu, gameplay, options)
- Warns if panel not registered

Centralizes all panel transition tracking in one place.

Version: v2.5.1 - FASE 1 (3/4)
```

---

### COMMIT 1.4: Log options dialog lifecycle

**File**: `acs_wx.py`  
**Linee Modificate**: ~277-310 (metodo `show_options`)  
**Funzione Usata**: `log.dialog_shown()`, `log.dialog_closed()`

#### Modifiche Richieste

```python
def show_options(self) -> None:
    """Show options window using OptionsDialog."""
    from src.infrastructure.ui.options_dialog import OptionsDialog
    
    print("\n" + "="*60)
    print("APERTURA FINESTRA OPZIONI (OptionsDialog - Native Widgets)")
    print("="*60)
    
    self.is_options_mode = True
    
    # Initialize controller state
    open_msg = self.gameplay_controller.options_controller.open_window()
    if self.screen_reader:
        self.screen_reader.tts.speak(open_msg, interrupt=True)
        wx.MilliSleep(500)
    
    # ✅ ADD THIS LOG (BEFORE ShowModal)
    log.dialog_shown("options", "Impostazioni di Gioco")
    
    # Create and show modal options dialog
    dlg = OptionsDialog(
        parent=self.frame,
        controller=self.gameplay_controller.options_controller,
        screen_reader=self.screen_reader
    )
    result = dlg.ShowModal()
    
    # ✅ ADD THIS LOG (AFTER ShowModal, BEFORE Destroy)
    result_str = "saved" if result == wx.ID_OK else "cancelled"
    log.dialog_closed("options", result_str)
    
    dlg.Destroy()
    
    self.is_options_mode = False
    
    # Log dialog result (for debugging)
    result_str_display = "OK (saved)" if result == wx.ID_OK else "CANCEL (discarded)"
    print(f"Finestra opzioni chiusa: {result_str_display}")
    print("="*60)
```

**Rationale**: Traccia apertura/chiusura opzioni dialog con risultato (salva/annulla). Utile per capire se utenti modificano spesso impostazioni.

#### Testing

```bash
python acs_wx.py

# Test 1: Save changes
Menu → Opzioni → Modifica qualcosa → Salva
# Verifica log:
# DEBUG - ui - Dialog shown: options - 'Impostazioni di Gioco'
# DEBUG - ui - Dialog closed: options - result: saved

# Test 2: Cancel changes
Menu → Opzioni → Modifica qualcosa → Annulla (o ESC)
# Verifica log:
# DEBUG - ui - Dialog shown: options - 'Impostazioni di Gioco'
# DEBUG - ui - Dialog closed: options - result: cancelled
```

#### Commit Message

```
feat(logging): add options dialog lifecycle logs

Adds log.dialog_shown() and log.dialog_closed() to track:
- Options dialog opening
- User choice (saved/cancelled)

Helps analytics: frequency of settings changes.

Version: v2.5.1 - FASE 1 (4/4 COMPLETE)
```

---

## FASE 2: SETTINGS & DIFFICULTY PRESETS (⭐⭐⭐ Alta Priorità)

**Obiettivo**: Tracciare modifiche settings e applicazione preset difficoltà.  
**Commits**: 5 atomici  
**Tempo Stimato Copilot**: 7-10 minuti

---

### COMMIT 2.1: Log settings persistence

**File**: `src/domain/services/game_settings.py`  
**Linee Modificate**: Metodi `load_from_file()`, `save_to_file()`  
**Funzione Usata**: `log.settings_changed()`, `log.warning_issued()`, `log.error_occurred()`, `log.info_query_requested()`

#### Modifiche Richieste

**Aggiungere import all'inizio del file**:

```python
# Existing imports...
from src.infrastructure.logging import game_logger as log  # ✅ ADD
```

**1. Metodo `load_from_file()`**:

```python
def load_from_file(self) -> bool:
    """Load settings from JSON file.
    
    Returns:
        True if loaded successfully, False otherwise
    """
    try:
        with open(self.settings_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Apply loaded settings (existing code...)
        self.difficulty_level = data.get('difficulty_level', 1)
        self.draw_count = data.get('draw_count', 1)
        # ... all other settings ...
        
        # ✅ ADD THIS LOG (AFTER successful load)
        log.settings_changed("all_settings", "default", "loaded_from_file")
        log.info_query_requested("settings_load", f"Loaded from {self.settings_file}")
        
        return True
        
    except FileNotFoundError:
        # ✅ ADD THIS LOG
        log.warning_issued("Settings", f"File not found: {self.settings_file}, using defaults")
        return False
        
    except json.JSONDecodeError as e:
        # ✅ ADD THIS LOG
        log.error_occurred("Settings", f"Corrupted JSON: {self.settings_file}", e)
        return False
        
    except Exception as e:
        # ✅ ADD THIS LOG
        log.error_occurred("Settings", f"Unexpected error loading {self.settings_file}", e)
        return False
```

**2. Metodo `save_to_file()`**:

```python
def save_to_file(self) -> bool:
    """Save settings to JSON file.
    
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        data = {
            'difficulty_level': self.difficulty_level,
            'draw_count': self.draw_count,
            # ... all other settings ...
        }
        
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        
        # ✅ ADD THIS LOG (AFTER successful save)
        log.info_query_requested("settings_save", f"Saved to {self.settings_file}")
        return True
        
    except Exception as e:
        # ✅ ADD THIS LOG
        log.error_occurred("Settings", f"Failed to save: {self.settings_file}", e)
        return False
```

#### Testing

```bash
# Test 1: First run (no settings file)
rm game_settings.json  # Delete if exists
python acs_wx.py
# Verifica log:
# WARNING - error - WARNING [Settings]: File not found: game_settings.json, using defaults

# Test 2: Normal load
python acs_wx.py  # Second run
# Verifica log:
# INFO - game - Setting changed: all_settings = default → loaded_from_file
# INFO - game - Info query: settings_load (Loaded from game_settings.json)

# Test 3: Save settings
Opzioni → Modifica qualcosa → Salva → Esci
# Verifica log:
# INFO - game - Info query: settings_save (Saved to game_settings.json)

# Test 4: Corrupted file
echo "invalid json" > game_settings.json
python acs_wx.py
# Verifica log:
# ERROR - error - ERROR [Settings]: Corrupted JSON: game_settings.json
# (Include traceback)
```

#### Commit Message

```
feat(logging): add settings persistence logs

Adds logging to GameSettings load/save operations:
- Successful load: INFO level
- File not found: WARNING level (expected on first run)
- JSON corrupted: ERROR level with traceback
- Save success: INFO level

Helps debug settings persistence issues.

Version: v2.5.1 - FASE 2 (1/5)
```

---

### COMMIT 2.2: Log difficulty preset applications

**File**: `src/application/controllers/options_controller.py` (o file equivalente contenente logica preset)  
**Funzione Usata**: `log.settings_changed()`, `log.debug_state()`

#### Identificazione Metodo Target

**IMPORTANTE**: Questo commit richiede di identificare il metodo che applica i difficulty preset. Possibili locazioni:

1. `src/application/controllers/options_controller.py` → metodo `_apply_difficulty_preset()`
2. `src/presentation/dialogs/options_dialog.py` → event handler `OnDifficultyChanged()`
3. `src/domain/services/game_settings.py` → property setter `difficulty_level.setter`

**Copilot**: Cerca nel codice il metodo che:
- Riceve `difficulty_level` come parametro
- Chiama `DifficultyPreset.get_preset(level)`
- Applica `locked_options` e preset values

#### Modifiche Richieste (Pattern Generico)

```python
# Aggiungere import
from src.infrastructure.logging import game_logger as log

def _apply_difficulty_preset(self, level: int) -> None:
    """Apply difficulty preset for given level."""
    preset = DifficultyPreset.get_preset(level)
    
    # ✅ ADD THIS LOG (BEFORE applying preset)
    old_level = self._current_difficulty_level  # Store old value
    log.settings_changed("difficulty_level", old_level, level)
    
    # Apply locked options
    for option_name in preset.locked_options:
        # Get preset value
        preset_value = getattr(preset, option_name, None)
        
        # ✅ ADD THIS LOG (for each locked option)
        log.debug_state("option_locked", {
            "option": option_name,
            "difficulty": level,
            "preset_value": preset_value,
            "locked": True
        })
        
        # Apply value (existing code...)
        # ...
    
    # Apply preset values (timer, draw_count, etc.)
    # ... existing code ...
```

**Esempio Output Log**:

```
INFO - game - Setting changed: difficulty_level = 1 → 5
DEBUG - game - State [option_locked]: {'option': 'max_time_game', 'difficulty': 5, 'preset_value': 900, 'locked': True}
DEBUG - game - State [option_locked]: {'option': 'timer_strict_mode', 'difficulty': 5, 'preset_value': True, 'locked': True}
DEBUG - game - State [option_locked]: {'option': 'draw_count', 'difficulty': 5, 'preset_value': 3, 'locked': True}
# ... (6 total locked options for level 5)
```

#### Testing

```bash
python acs_wx.py

# Test: Change difficulty 1 → 5
Opzioni → Difficoltà: Facile → Maestro → Salva

# Verifica solitaire.log:
# 1. Level change log:
#    INFO - game - Setting changed: difficulty_level = 1 → 5
# 2. Locked options logs (6 total):
#    DEBUG - game - State [option_locked]: {'option': 'max_time_game', ...}
#    DEBUG - game - State [option_locked]: {'option': 'timer_strict_mode', ...}
#    # ... (remaining 4 locked options)
```

#### Commit Message

```
feat(logging): add difficulty preset application logs

Adds logging when difficulty level changes:
- Level change: INFO level (old → new)
- Each locked option: DEBUG level (option name + preset value)

Helps debug progressive locking system (v2.4.0 feature).

Version: v2.5.1 - FASE 2 (2/5)
```

---

### COMMIT 2.3: Log individual setting changes

**File**: `src/domain/services/game_settings.py`  
**Linee Modificate**: Tutti i property setter  
**Funzione Usata**: `log.settings_changed(setting_name, old_value, new_value)`

#### Modifiche Richieste

**Pattern da replicare per OGNI property setter**:

```python
# 1. draw_count
@draw_count.setter
def draw_count(self, value: int) -> None:
    old_value = self._draw_count  # ✅ STORE OLD
    self._draw_count = max(1, min(3, value))
    
    # ✅ ADD THIS LOG (only if changed)
    if old_value != self._draw_count:
        log.settings_changed("draw_count", old_value, self._draw_count)

# 2. timer_strict_mode
@timer_strict_mode.setter
def timer_strict_mode(self, value: bool) -> None:
    old_value = self._timer_strict_mode  # ✅ STORE OLD
    self._timer_strict_mode = value
    
    # ✅ ADD THIS LOG
    if old_value != self._timer_strict_mode:
        log.settings_changed("timer_strict_mode", old_value, self._timer_strict_mode)

# 3. shuffle_discards
@shuffle_discards.setter
def shuffle_discards(self, value: bool) -> None:
    old_value = self._shuffle_discards
    self._shuffle_discards = value
    
    if old_value != self._shuffle_discards:
        log.settings_changed("shuffle_discards", old_value, self._shuffle_discards)

# 4. command_hints_enabled
@command_hints_enabled.setter
def command_hints_enabled(self, value: bool) -> None:
    old_value = self._command_hints_enabled
    self._command_hints_enabled = value
    
    if old_value != self._command_hints_enabled:
        log.settings_changed("command_hints_enabled", old_value, self._command_hints_enabled)

# 5. scoring_enabled
@scoring_enabled.setter
def scoring_enabled(self, value: bool) -> None:
    old_value = self._scoring_enabled
    self._scoring_enabled = value
    
    if old_value != self._scoring_enabled:
        log.settings_changed("scoring_enabled", old_value, self._scoring_enabled)

# 6. max_time_game
@max_time_game.setter
def max_time_game(self, value: int) -> None:
    old_value = self._max_time_game
    self._max_time_game = max(0, min(3600, value))
    
    if old_value != self._max_time_game:
        log.settings_changed("max_time_game", old_value, self._max_time_game)

# 7. deck_type
@deck_type.setter
def deck_type(self, value: str) -> None:
    old_value = self._deck_type
    if value in ["french", "neapolitan"]:
        self._deck_type = value
        
        if old_value != self._deck_type:
            log.settings_changed("deck_type", old_value, self._deck_type)
```

**IMPORTANTE**: Aggiungi log SOLO se valore effettivamente cambia (`if old_value != new_value`). Evita log ridondanti quando setter chiamato con stesso valore.

#### Testing

```bash
python acs_wx.py

# Test: Modifica OGNI impostazione singolarmente
Opzioni → Modifica:
1. Difficoltà: 1 → 2
2. Timer: Disabilitato → 10 minuti
3. Modalità Timer: Permissiva → Rigorosa
4. Pesca carte: 1 → 3
5. Mischia scarti: NO → SI
6. Hint comandi: SI → NO
7. Punteggio: NO → SI
8. Tipo mazzo: Francese → Napoletano

Salva → Verifica solitaire.log:

# Deve contenere 8 log (uno per ogni modifica):
INFO - game - Setting changed: difficulty_level = 1 → 2
INFO - game - Setting changed: max_time_game = 0 → 600
INFO - game - Setting changed: timer_strict_mode = False → True
INFO - game - Setting changed: draw_count = 1 → 3
INFO - game - Setting changed: shuffle_discards = False → True
INFO - game - Setting changed: command_hints_enabled = True → False
INFO - game - Setting changed: scoring_enabled = False → True
INFO - game - Setting changed: deck_type = french → neapolitan
```

#### Commit Message

```
feat(logging): add individual setting change logs

Adds log.settings_changed() to all GameSettings property setters:
- draw_count, timer_strict_mode, shuffle_discards
- command_hints_enabled, scoring_enabled
- max_time_game, deck_type

Logs only when value actually changes (no redundant logs).

Version: v2.5.1 - FASE 2 (3/5)
```

---

### COMMIT 2.4: Log deck type change in new_game

**File**: `src/application/game_engine.py`  
**Linee Modificate**: Metodo `new_game()` (linea ~389)  
**Funzione Usata**: `log.settings_changed("deck_type", old_deck, new_deck)`

#### Modifiche Richieste

**Import già presente** (verificare):

```python
from src.infrastructure.logging import game_logger as log
```

**Metodo `new_game()` (linea ~389)**:

```python
def new_game(self) -> None:
    """Start a new game with settings integration."""
    deck_changed = False
    
    # 1️⃣ Check if deck type changed
    if self.settings:
        # Detect current deck type
        current_is_neapolitan = isinstance(self.table.mazzo, NeapolitanDeck)
        should_be_neapolitan = (self.settings.deck_type == "neapolitan")
        
        # Deck type mismatch → recreate deck and table
        if current_is_neapolitan != should_be_neapolitan:
            deck_changed = True
            
            # ✅ ADD THESE LOGS (BEFORE _recreate_deck_and_table)
            old_deck = "neapolitan" if current_is_neapolitan else "french"
            new_deck = "neapolitan" if should_be_neapolitan else "french"
            log.settings_changed("deck_type", old_deck, new_deck)
            
            # ⚠️ IMPORTANT: This creates GameTable which already deals cards!
            self._recreate_deck_and_table(should_be_neapolitan)
    
    # ... rest of method (no changes) ...
```

**Rationale**: Traccia cambio tipo mazzo (Bug #3 storia). Questo evento è raro ma critico, merita log INFO esplicito.

#### Testing

```bash
python acs_wx.py

# Test 1: Change deck type
Opzioni → Tipo Mazzo: Francese → Napoletano → Salva
Menu → Nuova Partita

# Verifica solitaire.log:
INFO - game - Setting changed: deck_type = french → neapolitan
INFO - game - New game started - Deck: draw_one, Difficulty: easy, Timer: False

# Test 2: Change back
Opzioni → Tipo Mazzo: Napoletano → Francese → Salva
Menu → Nuova Partita

# Verifica solitaire.log:
INFO - game - Setting changed: deck_type = neapolitan → french
INFO - game - New game started - Deck: draw_one, Difficulty: easy, Timer: False
```

#### Commit Message

```
feat(logging): add deck type change log in new_game

Adds log.settings_changed() when deck type switches:
- Tracks french ↔ neapolitan transitions
- Logged in new_game() when deck recreation triggered

Helps debug deck change issues (Bug #3 history).

Version: v2.5.1 - FASE 2 (4/5)
```

---

### COMMIT 2.5: Log settings reset to defaults

**File**: `src/domain/services/game_settings.py`  
**Linee Modificate**: Metodo `reset_to_defaults()`  
**Funzione Usata**: `log.warning_issued()`, `log.settings_changed()`

#### Modifiche Richieste

```python
def reset_to_defaults(self) -> None:
    """Reset all settings to default values."""
    # ✅ ADD THIS LOG (BEFORE reset)
    log.warning_issued("Settings", "Resetting all settings to defaults")
    
    # Reset all settings (existing code...)
    self._difficulty_level = 1
    self._draw_count = 1
    self._timer_strict_mode = False
    self._shuffle_discards = False
    self._command_hints_enabled = True
    self._scoring_enabled = False
    self._max_time_game = 0
    self._deck_type = "french"
    
    # ✅ ADD THIS LOG (AFTER reset)
    log.settings_changed("all_settings", "custom", "default")
```

**Rationale**: Reset è un'azione distruttiva (perde configurazione utente). Merita WARNING level per visibilità.

#### Testing

```bash
python acs_wx.py

# Setup: Modifica alcune impostazioni
Opzioni → Difficoltà: 5, Timer: 15 min, ecc. → Salva

# Test: Reset
Opzioni → [Bottone Reset/Default se esiste] → Conferma

# Verifica solitaire.log:
WARNING - error - WARNING [Settings]: Resetting all settings to defaults
INFO - game - Setting changed: all_settings = custom → default

# Verifica settings tornate a default:
Opzioni → Verifica: Difficoltà = 1, Timer = 0, ecc.
```

**NOTA**: Se `reset_to_defaults()` non è chiamato da nessuna parte nel codice (bottone mancante), puoi comunque aggiungere i log per future implementazioni. Includi commento:

```python
# TODO: Implement "Reset to Defaults" button in OptionsDialog
# This method is ready with logging support
```

#### Commit Message

```
feat(logging): add settings reset to defaults logs

Adds logging to GameSettings.reset_to_defaults():
- WARNING level: Destructive action alert
- INFO level: Confirms reset completion

Prepares for future "Reset" button in options dialog.

Version: v2.5.1 - FASE 2 (5/5 COMPLETE)
```

---

## FASE 3: GAME OPERATIONS & SCORING (⭐⭐ Media Priorità)

**Obiettivo**: UX analytics e debug scoring system.  
**Commits**: 6 atomici  
**Tempo Stimato Copilot**: 8-12 minuti

---

### COMMIT 3.1: Log card selection/deselection

**File**: `src/application/game_engine.py`  
**Funzione Usata**: `log.debug_state(state_name, state_data: dict)`

#### Identificazione Metodi Target

**Copilot**: Cerca metodi in `game_engine.py` che:

1. **Selection**: Chiama `self.selection.select_card()` o equivalente
2. **Deselection**: Chiama `self.selection.clear_selection()` o equivalente

Possibili nomi metodi:
- `select_card_at_cursor()`
- `deselect_cards()`
- `handle_card_selection()`

#### Modifiche Richieste (Pattern Generico)

**Import già presente** (verificare):

```python
from src.infrastructure.logging import game_logger as log
```

**1. Metodo selezione carte**:

```python
def select_card_at_cursor(self) -> Tuple[bool, str]:
    """Select card(s) at current cursor position."""
    # ... existing validation logic ...
    
    # Execute selection
    success = self.selection.select_card(card, pile_name)
    
    if success:
        # Get card representation
        card_repr = f"{card.rank}{card.suit}" if card else "unknown"
        
        # ✅ ADD THIS LOG
        log.debug_state("card_selected", {
            "card": card_repr,
            "pile": pile_name,
            "count": len(self.selection.selected_cards)
        })
    
    # Generate message...
    return (success, msg)
```

**2. Metodo deselezione carte**:

```python
def deselect_cards(self) -> str:
    """Clear current card selection."""
    count = len(self.selection.selected_cards)
    
    # ✅ ADD THIS LOG (BEFORE clearing)
    if count > 0:
        log.debug_state("cards_deselected", {"count": count})
    
    self.selection.clear_selection()
    
    # Generate message...
    return msg
```

#### Testing

```bash
python acs_wx.py

# Test: Select and deselect cards
Nuova Partita → Gameplay:
1. Naviga a tableau_3 con carta selezionabile
2. Premi SPACE (selezione)
3. Premi SPACE di nuovo (deselezione)

# Verifica solitaire.log:
DEBUG - game - State [card_selected]: {'card': '7♥', 'pile': 'tableau_3', 'count': 1}
DEBUG - game - State [cards_deselected]: {'count': 1}

# Test 2: Select multiple cards (se supportato)
Seleziona sequenza K♠ Q♥ J♠ (3 carte)
# Verifica log:
DEBUG - game - State [card_selected]: {'card': 'K♠', 'pile': 'tableau_5', 'count': 3}
```

#### Commit Message

```
feat(logging): add card selection/deselection logs

Adds log.debug_state() for:
- Card selected: tracks card, pile, selection count
- Cards deselected: tracks deselection count

Helps UX analytics: understand selection patterns.

Version: v2.5.1 - FASE 3 (1/6)
```

---

### COMMIT 3.2: Log auto-selection (double-tap)

**File**: `src/application/game_engine.py`  
**Linee Modificate**: Metodo `jump_to_pile()` (linea ~474)  
**Funzione Usata**: `log.info_query_requested(query_type, context)`

#### Modifiche Richieste

```python
def jump_to_pile(self, pile_idx: int) -> Tuple[str, Optional[str]]:
    """Jump to specific pile with double-tap auto-selection support."""
    # ... existing code ...
    
    # Get cursor movement feedback, auto-selection flag, and hint
    msg, should_auto_select, hint = self.cursor.jump_to_pile(
        pile_idx,
        enable_double_tap=True
    )
    
    # 🔥 SECOND TAP: Execute automatic card selection
    if should_auto_select:
        # ✅ ADD THIS LOG (BEFORE selection)
        log.info_query_requested(
            "auto_selection",
            f"Double-tap on pile_{pile_idx}"
        )
        
        msg_deselect = ""
        
        # Cancel previous selection if present (silent reset)
        if self.selection.has_selection():
            self.selection.clear_selection()
            msg_deselect = "Selezione precedente annullata. "
        
        # Execute automatic selection
        success, msg_select = self.select_card_at_cursor()
        
        # Combine messages
        msg = msg_deselect + msg_select
        hint = None  # No hint after auto-selection
    
    # ... rest of method ...
```

**Rationale**: Auto-selection (double-tap) è feature importante (v1.5.0). Log INFO permette di capire quanto viene usata.

#### Testing

```bash
python acs_wx.py

# Test: Double-tap feature
Nuova Partita → Gameplay:
1. Premi "3" (jump to tableau_3)
2. Premi "3" di nuovo SUBITO (double-tap)

# Verifica solitaire.log:
INFO - game - Info query: auto_selection (Double-tap on pile_2)
DEBUG - game - State [card_selected]: {'card': '7♥', 'pile': 'tableau_3', 'count': 1}

# Test 2: Try on stock/waste (should not auto-select)
Premi "0" → "0" (double-tap su mazzo)
# Verifica: NO log auto_selection (feature solo per tableau/foundation)
```

#### Commit Message

```
feat(logging): add auto-selection (double-tap) logs

Adds log.info_query_requested() when double-tap triggers:
- Tracks pile index where double-tap occurred
- INFO level: significant UX event

Helps analytics: frequency of double-tap feature usage.

Version: v2.5.1 - FASE 3 (2/6)
```

---

### COMMIT 3.3: Log hint requests

**File**: `src/application/gameplay_controller.py`  
**Funzione Usata**: `log.info_query_requested()`, `log.debug_state()`

#### Identificazione Metodo Target

**Copilot**: Cerca metodo in `gameplay_controller.py` che:
- Gestisce tasto H (hint)
- Chiama `self.engine.get_hint()` o logica equivalente

Possibili nomi:
- `handle_hint_key()`
- `get_hint()`
- `on_H_pressed()`

#### Modifiche Richieste (Pattern Generico)

**Aggiungere import**:

```python
from src.infrastructure.logging import game_logger as log
```

**Metodo gestione hint**:

```python
def handle_hint_key(self) -> None:
    """Handle H key (show hint for next move)."""
    # ✅ ADD THIS LOG (BEFORE getting hint)
    log.info_query_requested("hint", "User requested move hint")
    
    # Get hint from engine
    hint_data = self.engine.get_hint()
    
    if hint_data:
        # Hint found
        source_pile = hint_data.get('from_pile', 'unknown')
        target_pile = hint_data.get('to_pile', 'unknown')
        card_repr = hint_data.get('card', 'unknown')
        
        # ✅ ADD THIS LOG (AFTER successful hint)
        log.debug_state("hint_provided", {
            "from": source_pile,
            "to": target_pile,
            "card": card_repr
        })
        
        # Vocalize hint...
        msg = f"Suggerimento: muovi {card_repr} da {source_pile} a {target_pile}"
    else:
        # No hint available
        msg = "Nessun suggerimento disponibile al momento."
    
    # Announce via TTS...
```

#### Testing

```bash
python acs_wx.py

# Test 1: Hint available
Nuova Partita → Gameplay → Premi H

# Verifica solitaire.log:
INFO - game - Info query: hint (User requested move hint)
DEBUG - game - State [hint_provided]: {'from': 'tableau_3', 'to': 'foundation_1', 'card': 'A♥'}

# Test 2: No hint available
Nuova Partita → (situation with no valid moves) → Premi H

# Verifica solitaire.log:
INFO - game - Info query: hint (User requested move hint)
# (NO debug_state log if hint not found)
```

#### Commit Message

```
feat(logging): add hint request logs

Adds logging when user presses H key:
- Request: INFO level (every H press)
- Hint provided: DEBUG level (source, target, card)

Helps analytics: frequency of hint feature usage.

Version: v2.5.1 - FASE 3 (3/6)
```

---

### COMMIT 3.4: Log auto-complete & undo operations

**File**: `src/domain/services/game_service.py`  
**Funzione Usata**: `log.info_query_requested()`, `log.game_won()`, `log.invalid_action()`, `log.debug_state()`

#### Modifiche Richieste

**Aggiungere import**:

```python
from src.infrastructure.logging import game_logger as log
```

**1. Metodo `auto_complete()`**:

```python
def auto_complete(self) -> Tuple[bool, str]:
    """Attempt to auto-complete game by moving all cards to foundations."""
    # ✅ ADD THIS LOG (BEFORE attempting)
    log.info_query_requested("auto_complete", "User triggered auto-complete")
    
    # ... existing auto-complete logic ...
    
    if completed:
        # Game completed successfully
        elapsed_time = self.get_elapsed_time()
        moves = self.get_move_count()
        score = self.scoring.get_final_score() if self.scoring else 0
        
        # ✅ VERIFY THIS LOG EXISTS (already in game_logger v2.3.0)
        log.game_won(elapsed_time, moves, score)
        
        msg = "Auto-completamento riuscito! Hai vinto!"
    else:
        # Auto-complete failed
        reason = "Non tutte le carte possono essere spostate automaticamente"
        
        # ✅ ADD THIS LOG
        log.invalid_action("auto_complete", reason)
        
        msg = "Auto-completamento non possibile al momento."
    
    return (completed, msg)
```

**2. Metodo `undo_last_move()`**:

```python
def undo_last_move(self) -> Tuple[bool, str]:
    """Undo the last move."""
    # ✅ ADD THIS LOG (BEFORE undo)
    log.info_query_requested("undo", "User undid last move")
    
    if not self.move_history:
        msg = "Nessuna mossa da annullare."
        return (False, msg)
    
    # Get last move
    last_move = self.move_history.pop()
    
    # ... existing undo logic ...
    
    if success:
        # ✅ ADD THIS LOG (AFTER successful undo)
        move_repr = f"{last_move['card']} from {last_move['to']} to {last_move['from']}"
        log.debug_state("undo_success", {
            "move": move_repr,
            "history_size": len(self.move_history)
        })
        
        msg = f"Mossa annullata: {move_repr}"
    else:
        msg = "Impossibile annullare questa mossa."
    
    return (success, msg)
```

#### Testing

```bash
python acs_wx.py

# Test 1: Auto-complete success
Nuova Partita → Gioca fino a quasi vittoria → Premi A (auto-complete)

# Verifica solitaire.log:
INFO - game - Info query: auto_complete (User triggered auto-complete)
INFO - game - Game WON - Time: 120s, Moves: 45, Score: 850

# Test 2: Auto-complete failure
Nuova Partita → Premi A subito (carte coperte)

# Verifica solitaire.log:
INFO - game - Info query: auto_complete (User triggered auto-complete)
WARNING - game - Invalid action 'auto_complete': Non tutte le carte possono...

# Test 3: Undo move
Nuova Partita → Muovi una carta → Premi U (undo)

# Verifica solitaire.log:
INFO - game - Info query: undo (User undid last move)
DEBUG - game - State [undo_success]: {'move': '7♥ from foundation_1 to tableau_3', ...}
```

#### Commit Message

```
feat(logging): add auto-complete and undo logs

Adds logging for:
- Auto-complete: request (INFO), success (game_won), failure (invalid_action)
- Undo: request (INFO), success (debug_state with move details)

Helps analytics: frequency of auto-complete/undo usage.

Version: v2.5.1 - FASE 3 (4/6)
```

---

### COMMIT 3.5: Log score storage persistence

**File**: `src/infrastructure/storage/score_storage.py`  
**Funzione Usata**: `log.info_query_requested()`, `log.error_occurred()`, `log.warning_issued()`

#### Modifiche Richieste

**Aggiungere import**:

```python
from src.infrastructure.logging import game_logger as log
```

**1. Metodo `save_statistics()`**:

```python
def save_statistics(self, stats: Dict[str, Any]) -> bool:
    """Save game statistics to persistent storage."""
    try:
        # Prepare data for save...
        data = {
            'total_games': stats.get('total_games', 0),
            'wins': stats.get('wins', 0),
            # ... other stats ...
        }
        
        # Write to file
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        
        # ✅ ADD THIS LOG (AFTER successful save)
        log.info_query_requested(
            "score_save",
            f"Statistics saved to {self.file_path}"
        )
        
        return True
        
    except Exception as e:
        # ✅ ADD THIS LOG
        log.error_occurred(
            "ScoreStorage",
            f"Failed to save: {self.file_path}",
            e
        )
        return False
```

**2. Metodo `load_statistics()`**:

```python
def load_statistics(self) -> Dict[str, Any]:
    """Load game statistics from persistent storage."""
    try:
        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # ✅ ADD THIS LOG (AFTER successful load)
        log.info_query_requested(
            "score_load",
            f"Statistics loaded from {self.file_path}"
        )
        
        return data
        
    except FileNotFoundError:
        # ✅ ADD THIS LOG
        log.warning_issued(
            "ScoreStorage",
            f"File not found: {self.file_path}, returning empty stats"
        )
        return {}
        
    except json.JSONDecodeError as e:
        # ✅ ADD THIS LOG
        log.error_occurred(
            "ScoreStorage",
            f"Corrupted file: {self.file_path}",
            e
        )
        return {}
        
    except Exception as e:
        # ✅ ADD THIS LOG
        log.error_occurred(
            "ScoreStorage",
            f"Unexpected error loading {self.file_path}",
            e
        )
        return {}
```

#### Testing

```bash
# Test 1: First run (no stats file)
rm score_statistics.json  # Delete if exists
python acs_wx.py

# Verifica solitaire.log:
WARNING - error - WARNING [ScoreStorage]: File not found: score_statistics.json, returning empty stats

# Test 2: Win game and save stats
Vinci partita → Esci app

# Verifica solitaire.log:
INFO - game - Info query: score_save (Statistics saved to score_statistics.json)

# Test 3: Load stats on next run
python acs_wx.py

# Verifica solitaire.log:
INFO - game - Info query: score_load (Statistics loaded from score_statistics.json)

# Test 4: Corrupt stats file
echo "invalid json" > score_statistics.json
python acs_wx.py

# Verifica solitaire.log:
ERROR - error - ERROR [ScoreStorage]: Corrupted file: score_statistics.json
# (Include traceback)
```

#### Commit Message

```
feat(logging): add score storage persistence logs

Adds logging to ScoreStorage load/save operations:
- Successful load/save: INFO level
- File not found: WARNING level (expected on first run)
- JSON corrupted: ERROR level with traceback

Helps debug statistics persistence issues.

Version: v2.5.1 - FASE 3 (5/6)
```

---

### COMMIT 3.6: Log scoring penalties/bonuses

**File**: `src/domain/services/scoring_service.py`  
**Funzione Usata**: `log.warning_issued()`, `log.info_query_requested()`

#### Identificazione Metodi Target

**Copilot**: Cerca metodi in `scoring_service.py` che:

1. **Penalità**: Sottraggono punti (overtime, undo, invalid move)
2. **Bonus**: Aggiungono punti (fast completion, streak)

Possibili nomi:
- `apply_penalty()`
- `apply_bonus()`
- `calculate_time_penalty()`
- `calculate_time_bonus()`

#### Modifiche Richieste (Pattern Generico)

**Aggiungere import**:

```python
from src.infrastructure.logging import game_logger as log
```

**1. Metodo apply_penalty (se esiste)**:

```python
def apply_penalty(self, penalty_type: str, amount: int) -> None:
    """Apply scoring penalty.
    
    Args:
        penalty_type: Type of penalty (e.g., "undo", "overtime", "invalid_move")
        amount: Penalty amount (positive value, will be subtracted)
    """
    # ✅ ADD THIS LOG
    log.warning_issued(
        "Scoring",
        f"Penalty applied: {penalty_type} = -{amount} points"
    )
    
    # Apply penalty to score
    self.current_score = max(0, self.current_score - amount)
```

**2. Metodo apply_bonus (se esiste)**:

```python
def apply_bonus(self, bonus_type: str, amount: int) -> None:
    """Apply scoring bonus.
    
    Args:
        bonus_type: Type of bonus (e.g., "fast_completion", "streak", "no_undo")
        amount: Bonus amount (positive value)
    """
    # ✅ ADD THIS LOG
    log.info_query_requested(
        "scoring_bonus",
        f"{bonus_type} = +{amount} points"
    )
    
    # Apply bonus to score
    self.current_score += amount
```

**3. Alternative: Log in calculate methods**

Se `apply_penalty/bonus` non esistono, aggiungi log dove penalty/bonus vengono calcolati:

```python
def calculate_final_score(self) -> int:
    """Calculate final score with all modifiers."""
    base_score = self.base_score
    
    # Time bonus/penalty
    if self.elapsed_time < self.time_limit / 2:
        bonus = 200
        # ✅ ADD THIS LOG
        log.info_query_requested("scoring_bonus", f"fast_completion = +{bonus} points")
        base_score += bonus
    elif self.elapsed_time > self.time_limit:
        penalty = 100 * ((self.elapsed_time - self.time_limit) // 60)
        # ✅ ADD THIS LOG
        log.warning_issued("Scoring", f"Penalty applied: overtime = -{penalty} points")
        base_score -= penalty
    
    # ... other modifiers ...
    
    return max(0, base_score)
```

#### Testing

```bash
python acs_wx.py

# Test 1: Overtime penalty
Opzioni → Timer: 5 min, Rigoroso: NO → Salva
Nuova Partita → Aspetta 6+ minuti → Continua partita

# Verifica solitaire.log:
WARNING - error - WARNING [Scoring]: Penalty applied: overtime = -100 points

# Test 2: Fast completion bonus
Opzioni → Timer: 30 min → Salva
Nuova Partita → Vinci in meno di 15 minuti

# Verifica solitaire.log:
INFO - game - Info query: scoring_bonus (fast_completion = +200 points)

# Test 3: Undo penalty (if implemented)
Nuova Partita → Undo move (U key)

# Verifica solitaire.log:
WARNING - error - WARNING [Scoring]: Penalty applied: undo = -50 points
```

#### Commit Message

```
feat(logging): add scoring penalties/bonuses logs

Adds logging to ScoringService:
- Penalties: WARNING level (overtime, undo, etc.)
- Bonuses: INFO level (fast completion, streak, etc.)

Helps debug scoring calculations and understand score impact.

Version: v2.5.1 - FASE 3 (6/6 COMPLETE)
```

---

## 🎯 TESTING FINALE COMPLETO

Dopo aver completato tutti i 15 commit, esegui questo test end-to-end:

### Scenario Completo

```bash
# 1. Avvio app (caricamento settings)
python acs_wx.py
# Verifica log: settings_load, score_load

# 2. Modifica impostazioni
Menu → Opzioni:
- Difficoltà: 1 → 3
- Timer: 0 → 10 minuti
- Pesca: 1 → 3
- Tipo mazzo: Francese → Napoletano
Salva
# Verifica log: dialog_shown, settings_changed (4x), dialog_closed, settings_save

# 3. Nuova partita
Menu → Nuova Partita
# Verifica log: panel_switched (menu→gameplay), deck_type change, game_started

# 4. Gameplay actions
- Naviga pile (frecce)
- Seleziona carta (SPACE)
# Verifica log: card_selected

- Muovi carta valida
# Verifica log: card_moved (success=True)

- Richiedi hint (H)
# Verifica log: info_query_requested (hint)

- Undo move (U)
# Verifica log: info_query_requested (undo), undo_success

- Double-tap su pile (es. "3" "3")
# Verifica log: info_query_requested (auto_selection)

# 5. Abbandono partita
ESC → Conferma
# Verifica log: debug_state (abandon_transition), panel_hidden, panel_switched

# 6. Chiusura app
Menu → Esci → Conferma
# Verifica log: app_shutdown
```

### Verifica `solitaire.log`

**Deve contenere**:

```
INFO - game - Application started - wxPython solitaire v2.3.0
INFO - game - Info query: settings_load (Loaded from game_settings.json)
INFO - game - Info query: score_load (Statistics loaded from score_statistics.json)

DEBUG - ui - Dialog shown: options - 'Impostazioni di Gioco'
INFO - game - Setting changed: difficulty_level = 1 → 3
INFO - game - Setting changed: max_time_game = 0 → 600
INFO - game - Setting changed: draw_count = 1 → 3
INFO - game - Setting changed: deck_type = french → neapolitan
DEBUG - ui - Dialog closed: options - result: saved
INFO - game - Info query: settings_save (Saved to game_settings.json)

INFO - ui - Panel transition: menu → gameplay
INFO - game - Setting changed: deck_type = french → neapolitan
INFO - game - New game started - Deck: draw_three, Difficulty: hard, Timer: True

DEBUG - game - State [card_selected]: {'card': '7♥', 'pile': 'tableau_3', 'count': 1}
INFO - game - Move SUCCESS: 7♥ from tableau_3 to foundation_1

INFO - game - Info query: hint (User requested move hint)
DEBUG - game - State [hint_provided]: {'from': 'tableau_2', 'to': 'foundation_2', 'card': 'A♠'}

INFO - game - Info query: undo (User undid last move)
DEBUG - game - State [undo_success]: {'move': '7♥ from foundation_1 to tableau_3', ...}

INFO - game - Info query: auto_selection (Double-tap on pile_2)

DEBUG - game - State [abandon_transition]: {'trigger': 'ESC_confirmed', 'from_panel': 'gameplay'}
DEBUG - game - State [panel_hidden]: {'panel': 'gameplay'}
INFO - ui - Panel transition: gameplay → menu

INFO - game - Application shutdown requested
```

---

## ⚠️ ATTENZIONE COPILOT

### Pattern da EVITARE

❌ **NON fare**:

```python
# WRONG: Creare nuove funzioni in game_logger.py
def log_panel_transition(from_panel, to_panel):  # ❌ NO!
    pass
```

✅ **Fare invece**:

```python
# CORRECT: Usare funzioni esistenti
log.panel_switched(from_panel, to_panel)  # ✅ YES!
```

---

❌ **NON fare**:

```python
# WRONG: Log senza parametri contestuali
log.debug_state("card_selected", {})  # ❌ NO!
```

✅ **Fare invece**:

```python
# CORRECT: Sempre includere dati contestuali
log.debug_state("card_selected", {
    "card": card_repr,
    "pile": pile_name,
    "count": selection_count
})  # ✅ YES!
```

---

❌ **NON fare**:

```python
# WRONG: Log sempre, anche se valore non cambia
log.settings_changed("draw_count", old, new)  # Anche se old == new
```

✅ **Fare invece**:

```python
# CORRECT: Log solo se effettivo cambiamento
if old_value != new_value:
    log.settings_changed("draw_count", old_value, new_value)
```

---

## 📄 COMMIT MESSAGE TEMPLATE

Ogni commit DEVE seguire questo template:

```
feat(logging): add [event] logs

[Descrizione dettagliata modifiche]

Adds [funzione_log()] to track:
- [Evento 1]
- [Evento 2]

Helps [utilità/rationale].

Version: v2.5.1 - FASE [N] ([X]/[Y])
```

---

## 🎯 CRITERI DI SUCCESSO

### Per Ogni Commit:
- ✅ Usa SOLO funzioni esistenti `game_logger.py`
- ✅ Livello log appropriato (INFO/DEBUG/WARNING/ERROR)
- ✅ Parametri contestuali completi
- ✅ Zero breaking changes
- ✅ Commit message convenzionale

### Per Ogni Fase:
- ✅ Testing manuale completato
- ✅ `solitaire.log` contiene log attesi
- ✅ Nessun crash durante test
- ✅ TODO aggiornato (caselle spuntate)

### Globale (Dopo FASE 3):
- ✅ 15 commit atomici pushati
- ✅ Test end-to-end passato
- ✅ Log file completo e leggibile
- ✅ Zero warning Python
- ✅ Documentazione aggiornata

---

**Versione**: v2.5.1  
**Autore**: Nemex81  
**Data Creazione**: 2026-02-15  
**Ultima Revisione**: 2026-02-15
