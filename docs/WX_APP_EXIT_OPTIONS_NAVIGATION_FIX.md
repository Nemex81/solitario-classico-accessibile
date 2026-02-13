# 🔧 Piano di Fix: Uscita App + Navigazione Opzioni

**Branch target**: `copilot/remove-pygame-migrate-wxpython`  
**Scope**: Risolvere problemi critici emersi dopo refactoring STEP 1-5

**Problemi rilevati**:
1. **Uscita dall'app non funziona** in 3 modi:
   - INVIO su "Esci dal gioco" non fa nulla
   - ESC dal menu principale non gestito
   - ALT+F4 va in loop infinito (EVT_CLOSE ricorsivo)
2. **Opzioni: frecce e numeri non funzionano**:
   - Frecce UP/DOWN non vocalizzano l'opzione corrente
   - Numeri 1-5 non saltano alle opzioni
   - Mancano opzioni 6, 7, 8 (erano presenti nella versione refactoring-engine)

**Copilot**: Implementa i seguenti FIX in **ordine sequenziale**, con **un commit per FIX**. Non mescolare modifiche tra FIX diversi.

---

## 🔍 Analisi Root Cause

### Problema 1A: INVIO su "Esci" non funziona

**Flusso attuale** (copilot/remove-pygame-migrate-wxpython):
```
MenuPanel.on_exit_click() [menu_panel.py:122]
  → controller.show_exit_dialog() [test.py:222]
    → dialog_manager.show_yes_no(...) [test.py:223]
      → se True: quit_app() [test.py:226]
        → frame.Close() + sys.exit(0) [test.py:287]
```

**Root cause**:
- `dialog_manager` potrebbe essere `None` se inizializzazione fallita.
- `show_yes_no()` potrebbe ritornare `None` invece di `True/False` in caso di errore.
- `quit_app()` chiama `frame.Close()` che triggera `EVT_CLOSE` → loop.

**File coinvolti**:
- `test.py` (linee ~222-227, ~285-291)
- `src/infrastructure/ui/wx_frame.py` (EVT_CLOSE binding)

---

### Problema 1B: ESC dal menu non gestito

**Stato attuale**:
- `MenuPanel` eredita da `BasicPanel`.
- `BasicPanel.on_key_down()` fa solo `event.Skip()` (nessuna gestione ESC).
- Nel `GameplayPanel` invece ESC è gestito correttamente:
  ```python
  if key_code == wx.WXK_ESCAPE:
      if self.controller:
          self.controller.show_abandon_game_dialog()
      return
  ```

**Root cause**:
- `MenuPanel` non ha override di `on_key_down` per ESC.
- ESC nel menu dovrebbe aprire `show_exit_dialog()` (o essere ignorato).

**File coinvolti**:
- `src/infrastructure/ui/menu_panel.py` (aggiungere on_key_down override)

---

### Problema 1C: ALT+F4 loop infinito

**Flusso attuale** (EVT_CLOSE):
```
Utente preme ALT+F4 / X della finestra
  → wx.EVT_CLOSE su SolitarioFrame
    → _on_close_event() [wx_frame.py]
      → chiama on_close callback (SolitarioController._on_frame_close) [test.py:283]
        → quit_app() [test.py:285]
          → frame.Close() [test.py:290]
            → triggera EVT_CLOSE di nuovo → LOOP ♾️
```

**Root cause**:
- `quit_app()` chiama `self.frame.Close()` che ri-triggera l'evento `EVT_CLOSE`.
- Dovrebbe usare `event.Skip()` o `Destroy()` invece di `Close()`.
- Oppure settare un flag `_closing` per evitare ricorsione.

**Soluzione corretta** (pattern wxPython standard):
```python
def _on_close_event(self, event: wx.CloseEvent):
    # Stop timer
    self.timer.Stop()
    
    # Call user callback (optional confirmation)
    if self.on_close:
        self.on_close()  # Può mostrare dialog conferma
    
    # Destroy frame (no recursion)
    self.Destroy()
```

**File coinvolti**:
- `src/infrastructure/ui/wx_frame.py` (linee ~140-150)
- `test.py` (quit_app, linee ~285-291)

---

### Problema 2A: Opzioni - frecce non vocalizzano

**Flusso attuale** (OptionsDialog):
```
Utente preme UP/DOWN
  → OptionsDialog.on_key_down() [options_dialog.py:144]
    → msg = controller.navigate_up() [options_dialog.py:149]
      → controller ritorna "1 di 8: Tipo Mazzo, Francese. Usa INVIO..."
    → Dialog assegna msg ma NON lo vocalizza [options_dialog.py:149]
    → return (msg non usato) [options_dialog.py:200]
```

**Root cause**:
- `OptionsDialog.on_key_down` riceve `msg` ma ha solo un commento TODO:
  ```python
  if msg is not None:
      # TODO (future): Vocalize msg via ScreenReader if available
      # For now, controller handles TTS internally
      return
  ```
- **MA** il controller NON ha accesso a ScreenReader (non è passato nel costruttore).
- Nella versione vecchia (refactoring-engine), l'OptionsWindowController chiamava direttamente `self.screen_reader.tts.speak(msg)` (IMPOSSIBILE ora, non ha riferimento).

**Soluzione**:
- Passare `screen_reader` al dialog nel costruttore.
- Nel `on_key_down`, chiamare `self.screen_reader.tts.speak(msg, interrupt=True)` quando `msg` non è `None`.

**File coinvolti**:
- `src/infrastructure/ui/options_dialog.py` (costruttore + on_key_down)
- `test.py` (show_options, passare screen_reader al dialog)

---

### Problema 2B: Numeri 1-5 non funzionano + mancano opzioni 6-8

**Confronto versioni**:

**refactoring-engine** (FUNZIONANTE):
- `OptionsWindowController` ha **8 opzioni** (cursor_position 0-7):
  0. Tipo Mazzo
  1. Difficoltà
  2. Carte Pescate
  3. Timer
  4. Riciclo Scarti
  5. Suggerimenti Comandi
  6. Sistema Punti
  7. Modalità Timer
- `navigate_up/down` fa wraparound su 8: `(cursor_position ± 1) % 8`
- Tasti numerici 1-8 mappano su `jump_to_option(0-7)`

**copilot/remove-pygame-migrate-wxpython** (ROTTO):
- `OptionsDialog.on_key_down` mappa SOLO numeri **1-5** su `jump_to_option(0-4)`.
- Mancano mappature per 6, 7, 8.
- Il controller fa ancora wraparound su 8, ma dialog non supporta le opzioni 6-8.

**Root cause**:
- Copilot ha implementato solo STEP 3/4 con mappatura parziale (1-5).
- Non ha portato tutte le 8 opzioni dalla versione vecchia.

**Soluzione**:
- Aggiungere mappature per 6, 7, 8 in `OptionsDialog.on_key_down`:
  ```python
  elif key_code in (ord('6'), wx.WXK_NUMPAD6):
      msg = self.options_controller.jump_to_option(5)
  elif key_code in (ord('7'), wx.WXK_NUMPAD7):
      msg = self.options_controller.jump_to_option(6)
  elif key_code in (ord('8'), wx.WXK_NUMPAD8):
      msg = self.options_controller.jump_to_option(7)
  ```

**File coinvolti**:
- `src/infrastructure/ui/options_dialog.py` (on_key_down, aggiungere 6-8)

---

## 🛠️ Piano Implementativo per Copilot (Fix Incrementali)

> **Copilot**: Implementa i seguenti FIX in ordine, con **un commit per FIX**. Non mescolare modifiche tra FIX diversi.

---

### FIX 1 - Risolvi loop ALT+F4 (EVT_CLOSE)

**File coinvolti**:
- `src/infrastructure/ui/wx_frame.py`
- `test.py`

**Obiettivo**: Eliminare loop ricorsivo su chiusura finestra.

#### 1.1 Modifica `SolitarioFrame._on_close_event`

In `src/infrastructure/ui/wx_frame.py` (linee ~140-150):

**PRIMA** (loop ricorsivo):
```python
def _on_close_event(self, event: wx.CloseEvent) -> None:
    """Handle window close event (X button, ALT+F4)."""
    # Stop timer before closing
    if self.timer:
        self.timer.Stop()
    
    # Call user-defined close handler
    if self.on_close:
        self.on_close()
    
    # Destroy frame
    self.Destroy()
```

**DOPO** (no loop):
```python
def _on_close_event(self, event: wx.CloseEvent) -> None:
    """Handle window close event (X button, ALT+F4).
    
    Pattern: wxPython standard close sequence
    1. Stop timer
    2. Call optional user callback (can show confirmation dialog)
    3. Destroy frame (no Close() to avoid recursion)
    
    Note:
        Do NOT call self.Close() here - would trigger EVT_CLOSE again.
        Use Destroy() directly for clean shutdown.
    """
    # Stop timer before closing
    if self.timer:
        self.timer.Stop()
    
    # Call user-defined close handler (optional confirmation)
    if self.on_close:
        self.on_close()
    
    # Destroy frame (no recursion)
    self.Destroy()
```

**Nota**: Il codice è già corretto (usa `Destroy()`), ma verifica che non ci siano altre chiamate a `Close()` nel callback.

#### 1.2 Modifica `SolitarioController.quit_app`

In `test.py` (linee ~285-291):

**PRIMA** (chiama Close che triggera EVT_CLOSE):
```python
def quit_app(self) -> None:
    """Graceful application shutdown."""
    print("\n" + "="*60)
    print("CHIUSURA APPLICAZIONE")
    print("="*60)
    
    if self.screen_reader:
        self.screen_reader.tts.speak("Chiusura in corso.", interrupt=True)
        wx.MilliSleep(800)
    
    # Close frame and exit app
    if self.frame:
        self.frame.Close()  # ❌ TRIGGERA EVT_CLOSE → LOOP
    sys.exit(0)
```

**DOPO** (chiama Destroy direttamente o usa flag):
```python
def quit_app(self) -> None:
    """Graceful application shutdown.
    
    Called from:
    - show_exit_dialog() (menu "Esci")
    - _on_frame_close() (ALT+F4, X button)
    
    Pattern:
    - Do NOT call frame.Close() (would trigger EVT_CLOSE again)
    - Either call frame.Destroy() directly, or let _on_close_event handle it
    - sys.exit(0) ensures complete shutdown
    """
    print("\n" + "="*60)
    print("CHIUSURA APPLICAZIONE")
    print("="*60)
    
    if self.screen_reader:
        self.screen_reader.tts.speak("Chiusura in corso.", interrupt=True)
        wx.MilliSleep(800)
    
    # Exit app (frame destruction handled by EVT_CLOSE)
    sys.exit(0)
```

**Alternativa** (se vuoi distruggere frame esplicitamente):
```python
# Destroy frame directly (skip EVT_CLOSE callback)
if self.frame:
    self.frame.Destroy()
sys.exit(0)
```

**Scelta consigliata**: Rimuovere `frame.Close()` e lasciare solo `sys.exit(0)`, perché `_on_frame_close` è chiamato da `_on_close_event`, che già chiama `Destroy()`.

**Commit suggerito**:
```
fix(ui): resolve ALT+F4 infinite loop in quit_app

- Remove frame.Close() call in quit_app() to avoid EVT_CLOSE recursion
- Let _on_close_event handle Destroy() directly
- sys.exit(0) ensures complete shutdown

Fixes issue where ALT+F4 triggered infinite Close() loop.
```

---

### FIX 2 - Aggiungi gestione ESC nel MenuPanel

**File coinvolti**:
- `src/infrastructure/ui/menu_panel.py`

**Obiettivo**: ESC dal menu → `show_exit_dialog()` (come nel GameplayPanel con abbandono).

#### 2.1 Aggiungi override `on_key_down` in `MenuPanel`

In `src/infrastructure/ui/menu_panel.py`, dopo il metodo `on_exit_click` (linea ~122):

```python
def on_key_down(self, event: wx.KeyEvent) -> None:
    """Handle keyboard events in menu panel.
    
    ESC in menu → show exit confirmation dialog.
    Other keys → propagate to parent.
    
    Args:
        event: wx.KeyEvent from keyboard
    
    Pattern:
        Similar to GameplayPanel ESC handling, but calls show_exit_dialog
        instead of show_abandon_game_dialog.
    """
    key_code = event.GetKeyCode()
    
    # ESC: Show exit confirmation
    if key_code == wx.WXK_ESCAPE:
        if self.controller:
            self.controller.show_exit_dialog()
        return
    
    # Other keys: propagate
    event.Skip()
```

**Note**:
- `BasicPanel` già fa `Bind(wx.EVT_CHAR_HOOK, self.on_key_down)`, quindi questo override sarà chiamato automaticamente.
- ESC nel menu chiamerà `show_exit_dialog()` (conferma uscita).
- Altri tasti (TAB, INVIO) continuano a funzionare normalmente (navigazione button).

**Commit suggerito**:
```
feat(ui): handle ESC in MenuPanel to show exit dialog

- Add on_key_down override in MenuPanel
- ESC → controller.show_exit_dialog() (consistent with GameplayPanel pattern)
- Other keys propagated normally (TAB navigation preserved)

Provides keyboard shortcut for exit without clicking button.
```

---

### FIX 3 - Correggi dialog_manager.show_yes_no in show_exit_dialog

**File coinvolti**:
- `test.py`

**Obiettivo**: Gestire correttamente il caso in cui `dialog_manager` è `None` o `show_yes_no` fallisce.

#### 3.1 Aggiungi validazione in `show_exit_dialog`

In `test.py` (linee ~222-227):

**PRIMA** (nessuna validazione):
```python
def show_exit_dialog(self) -> None:
    """Show exit confirmation dialog (called from MenuView)."""
    result = self.dialog_manager.show_yes_no(
        "Vuoi davvero uscire dal gioco?",
        "Conferma uscita"
    )
    if result:
        self.quit_app()
```

**DOPO** (con validazione):
```python
def show_exit_dialog(self) -> None:
    """Show exit confirmation dialog (called from MenuPanel).
    
    Shows native wxDialog for exit confirmation.
    If dialog_manager not available, falls back to direct quit.
    
    Note:
        dialog_manager.show_yes_no() returns:
        - True: User clicked Yes
        - False: User clicked No or ESC
        - None: Should not happen with current implementation
    """
    # Fallback if dialog_manager not initialized
    if not self.dialog_manager or not self.dialog_manager.is_available:
        print("⚠ Dialog manager not available, exiting directly")
        self.quit_app()
        return
    
    # Show confirmation dialog
    result = self.dialog_manager.show_yes_no(
        "Vuoi davvero uscire dal gioco?",
        "Conferma uscita"
    )
    
    # Handle result
    if result is True:
        self.quit_app()
    elif result is False:
        # User cancelled, do nothing
        if self.screen_reader:
            self.screen_reader.tts.speak("Uscita annullata.", interrupt=True)
    else:
        # result is None (should not happen)
        print("⚠ Unexpected dialog result: None")
```

**Commit suggerito**:
```
fix(ui): add validation to show_exit_dialog for missing dialog_manager

- Check dialog_manager availability before showing dialog
- Handle False result (user cancelled) with TTS feedback
- Fallback to direct quit if dialog_manager not initialized

Prevents crash when dialog_manager is None.
```

---

### FIX 4 - Passa screen_reader al OptionsDialog per TTS feedback

**File coinvolti**:
- `src/infrastructure/ui/options_dialog.py`
- `test.py`

**Obiettivo**: Vocalizzare messaggi quando utente naviga opzioni con frecce/numeri.

#### 4.1 Modifica costruttore `OptionsDialog`

In `src/infrastructure/ui/options_dialog.py` (linee ~65-90):

**PRIMA** (no screen_reader):
```python
def __init__(
    self,
    parent: wx.Window,
    controller: OptionsWindowController,
    title: str = "Opzioni di gioco",
    size: tuple = (500, 400)
):
    # ...
    self.options_controller = controller
    # ...
```

**DOPO** (con screen_reader):
```python
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.infrastructure.accessibility.screen_reader import ScreenReader

class OptionsDialog(wx.Dialog):
    # ...
    
    def __init__(
        self,
        parent: wx.Window,
        controller: OptionsWindowController,
        screen_reader: Optional['ScreenReader'] = None,
        title: str = "Opzioni di gioco",
        size: tuple = (500, 400)
    ):
        """Initialize OptionsDialog with controller and screen reader.
        
        Args:
            parent: Parent window (typically main frame)
            controller: OptionsWindowController instance
            screen_reader: ScreenReader for TTS feedback (optional)
            title: Dialog title (default: "Opzioni di gioco")
            size: Dialog size in pixels (default: 500x400)
        
        Attributes:
            options_controller: Reference to OptionsWindowController
            screen_reader: Reference to ScreenReader for TTS
        """
        super().__init__(
            parent=parent,
            title=title,
            size=size,
            style=wx.DEFAULT_DIALOG_STYLE
        )
        
        self.options_controller = controller
        self.screen_reader = screen_reader
        
        # ... rest of __init__
```

#### 4.2 Modifica `on_key_down` per vocalizzare `msg`

In `src/infrastructure/ui/options_dialog.py` (linee ~195-205):

**PRIMA** (TODO non implementato):
```python
# If key was handled but no message, just return
if msg is not None:
    # TODO (future): Vocalize msg via ScreenReader if available
    # For now, controller handles TTS internally
    return

# Key not handled: propagate
event.Skip()
```

**DOPO** (TTS attivo):
```python
# If key was handled, vocalize message via TTS
if msg is not None:
    if self.screen_reader and self.screen_reader.tts:
        self.screen_reader.tts.speak(msg, interrupt=True)
    return

# Key not handled: propagate
event.Skip()
```

#### 4.3 Modifica `show_options` in `test.py`

In `test.py` (linee ~208-228):

**PRIMA** (no screen_reader passato):
```python
def show_options(self) -> None:
    # ...
    dlg = OptionsDialog(
        parent=self.frame,
        controller=self.gameplay_controller.options_controller
    )
    dlg.ShowModal()
    # ...
```

**DOPO** (passa screen_reader):
```python
def show_options(self) -> None:
    """Show options window using OptionsDialog (STEP 3).
    
    Opens modal OptionsDialog with OptionsWindowController and ScreenReader.
    
    Flow:
    1. Set is_options_mode flag
    2. Create OptionsDialog with controller + screen_reader
    3. Show modal (blocks until closed)
    4. Clean up and reset flag
    """
    from src.infrastructure.ui.options_dialog import OptionsDialog
    
    print("\n" + "="*60)
    print("APERTURA FINESTRA OPZIONI (OptionsDialog)")
    print("="*60)
    
    self.is_options_mode = True
    
    # Create and show modal options dialog (with TTS support)
    dlg = OptionsDialog(
        parent=self.frame,
        controller=self.gameplay_controller.options_controller,
        screen_reader=self.screen_reader  # ← AGGIUNTO
    )
    dlg.ShowModal()
    dlg.Destroy()
    
    self.is_options_mode = False
    
    print("Finestra opzioni chiusa.")
    print("="*60)
```

**Commit suggerito**:
```
fix(options): add screen_reader to OptionsDialog for TTS feedback

- Add screen_reader parameter to OptionsDialog constructor
- Vocalize controller messages in on_key_down (UP/DOWN/numbers)
- Pass self.screen_reader from SolitarioController.show_options()

Fixes issue where arrow keys/numbers were silent (no TTS).
```

---

### FIX 5 - Aggiungi mappatura numeri 6-8 in OptionsDialog

**File coinvolti**:
- `src/infrastructure/ui/options_dialog.py`

**Obiettivo**: Supportare tutte le 8 opzioni (come in refactoring-engine).

#### 5.1 Aggiungi mappature 6-8 in `on_key_down`

In `src/infrastructure/ui/options_dialog.py` (linee ~175-190), dopo la mappatura di `5`:

**PRIMA** (solo 1-5):
```python
# Numbers 1-5: Jump to specific option
elif key_code in (ord('1'), wx.WXK_NUMPAD1):
    msg = self.options_controller.jump_to_option(0)
elif key_code in (ord('2'), wx.WXK_NUMPAD2):
    msg = self.options_controller.jump_to_option(1)
elif key_code in (ord('3'), wx.WXK_NUMPAD3):
    msg = self.options_controller.jump_to_option(2)
elif key_code in (ord('4'), wx.WXK_NUMPAD4):
    msg = self.options_controller.jump_to_option(3)
elif key_code in (ord('5'), wx.WXK_NUMPAD5):
    msg = self.options_controller.jump_to_option(4)

# T: Toggle timer on/off
elif key_code in (ord('T'), ord('t')):
    # ...
```

**DOPO** (1-8 completo):
```python
# Numbers 1-8: Jump to specific option (complete set)
elif key_code in (ord('1'), wx.WXK_NUMPAD1):
    msg = self.options_controller.jump_to_option(0)  # Tipo Mazzo
elif key_code in (ord('2'), wx.WXK_NUMPAD2):
    msg = self.options_controller.jump_to_option(1)  # Difficoltà
elif key_code in (ord('3'), wx.WXK_NUMPAD3):
    msg = self.options_controller.jump_to_option(2)  # Carte Pescate
elif key_code in (ord('4'), wx.WXK_NUMPAD4):
    msg = self.options_controller.jump_to_option(3)  # Timer
elif key_code in (ord('5'), wx.WXK_NUMPAD5):
    msg = self.options_controller.jump_to_option(4)  # Riciclo Scarti
elif key_code in (ord('6'), wx.WXK_NUMPAD6):
    msg = self.options_controller.jump_to_option(5)  # Suggerimenti Comandi
elif key_code in (ord('7'), wx.WXK_NUMPAD7):
    msg = self.options_controller.jump_to_option(6)  # Sistema Punti
elif key_code in (ord('8'), wx.WXK_NUMPAD8):
    msg = self.options_controller.jump_to_option(7)  # Modalità Timer

# T: Toggle timer on/off
elif key_code in (ord('T'), ord('t')):
    # ...
```

#### 5.2 Aggiorna docstring con tutte le 8 opzioni

In `src/infrastructure/ui/options_dialog.py` (linee ~110-130):

**PRIMA** (docstring obsoleto):
```python
def on_key_down(self, event: wx.KeyEvent) -> None:
    """Handle keyboard events for options navigation.
    
    Key Mapping (STEP 4 - complete):
    - ESC: Close dialog with cancel
    - UP/DOWN: Navigate options (navigate_up/down)
    - ENTER: Modify current option (modify_current_option)
    - 1-5: Jump to option 1-5 (jump_to_option)
    - T: Toggle timer on/off (toggle_timer)
    - +: Increment timer value (increment_timer)
    - -: Decrement timer value (decrement_timer)
    """
```

**DOPO** (8 opzioni documentate):
```python
def on_key_down(self, event: wx.KeyEvent) -> None:
    """Handle keyboard events for options navigation.
    
    Routes keyboard input to OptionsWindowController methods.
    All messages from controller are vocalized via ScreenReader TTS.
    
    Args:
        event: wx.KeyEvent from keyboard
    
    Key Mapping (Complete - v1.7.4):
    - ESC: Close dialog with cancel
    - UP/DOWN: Navigate options (navigate_up/down)
    - ENTER: Modify current option (modify_current_option)
    - 1-8: Jump to specific option:
        1. Tipo Mazzo (Francese/Napoletano)
        2. Difficoltà (1-3 carte)
        3. Carte Pescate (1-3)
        4. Timer (OFF, 5-60 min)
        5. Riciclo Scarti (Inversione/Mescolata)
        6. Suggerimenti Comandi (ON/OFF)
        7. Sistema Punti (Attivo/Disattivato)
        8. Modalità Timer (STRICT/PERMISSIVE)
    - T: Toggle timer on/off (toggle_timer)
    - +: Increment timer value (increment_timer)
    - -: Decrement timer value (decrement_timer)
    - I: Read all settings (read_all_settings)
    - H: Show help text (show_help)
    
    Note:
        Both main keyboard and numpad keys are supported.
        Controller methods return TTS messages vocalized by dialog.
    """
```

#### 5.3 (Opzionale) Aggiungi mappature I e H

La versione vecchia supporta anche:
- **I**: `read_all_settings()` - legge tutte le impostazioni
- **H**: `show_help()` - mostra aiuto comandi

Se vuoi aggiungerle (consigliato), dopo la mappatura di `decrement_timer`:

```python
# -/_: Decrement timer value
elif key_code in (ord('-'), ord('_'), wx.WXK_NUMPAD_SUBTRACT):
    msg = self.options_controller.decrement_timer()

# I: Read all settings recap
elif key_code in (ord('I'), ord('i')):
    msg = self.options_controller.read_all_settings()

# H: Show help text
elif key_code in (ord('H'), ord('h')):
    msg = self.options_controller.show_help()

# If key was handled, vocalize message via TTS
if msg is not None:
    # ...
```

**Commit suggerito**:
```
feat(options): add support for options 6-8 and help commands

- Map numbers 6-8 to jump_to_option(5-7):
  * 6 → Suggerimenti Comandi
  * 7 → Sistema Punti
  * 8 → Modalità Timer
- Add I key → read_all_settings() (settings recap)
- Add H key → show_help() (help text)
- Update docstring with complete 8-option mapping

Restores feature parity with refactoring-engine branch.
```

---

## 🧪 Testing Checklist (Dopo Tutti i Fix)

### Test 1: Uscita dall'app

✅ **Test 1A**: Pulsante "Esci dal gioco"
1. Avvia app: `python test.py`
2. Nel menu principale, premi TAB fino a "Esci dal gioco"
3. Premi INVIO
4. **Atteso**: Dialog conferma "Vuoi davvero uscire?"
5. Clicca "Sì"
6. **Atteso**: App si chiude senza errori

✅ **Test 1B**: ESC dal menu
1. Avvia app: `python test.py`
2. Premi ESC
3. **Atteso**: Dialog conferma "Vuoi davvero uscire?"
4. Clicca "No"
5. **Atteso**: Dialog si chiude, rimani nel menu

✅ **Test 1C**: ALT+F4
1. Avvia app: `python test.py`
2. Premi ALT+F4
3. **Atteso**: App si chiude immediatamente, NO loop
4. Verifica console: NO messaggi ripetuti "CHIUSURA APPLICAZIONE"

### Test 2: Opzioni - Navigazione

✅ **Test 2A**: Frecce UP/DOWN
1. Avvia app: `python test.py`
2. TAB a "Opzioni di gioco", premi INVIO
3. **Atteso**: Dialog opzioni aperto
4. Premi DOWN
5. **Atteso**: TTS annuncia "2 di 8: Difficoltà, 1 Carta. Usa INVIO..."
6. Premi UP
7. **Atteso**: TTS annuncia "1 di 8: Tipo Mazzo, Francese. Usa INVIO..."

✅ **Test 2B**: Numeri 1-8
1. Nel dialog opzioni, premi 3
2. **Atteso**: TTS annuncia "3 di 8: Carte Pescate, 1 Carta."
3. Premi 6
4. **Atteso**: TTS annuncia "6 di 8: Suggerimenti Comandi, Attivi."
5. Premi 8
6. **Atteso**: TTS annuncia "8 di 8: Modalità Timer, PERMISSIVE."

✅ **Test 2C**: Comandi I e H (opzionale)
1. Nel dialog opzioni, premi I
2. **Atteso**: TTS legge tutte le impostazioni
3. Premi H
4. **Atteso**: TTS legge l'aiuto comandi

✅ **Test 2D**: ESC chiude opzioni
1. Nel dialog opzioni, premi ESC
2. **Atteso**: Dialog si chiude, torna al menu

---

## 📝 Messaggi di Commit Suggeriti (Riepilogo)

1. `fix(ui): resolve ALT+F4 infinite loop in quit_app`
2. `feat(ui): handle ESC in MenuPanel to show exit dialog`
3. `fix(ui): add validation to show_exit_dialog for missing dialog_manager`
4. `fix(options): add screen_reader to OptionsDialog for TTS feedback`
5. `feat(options): add support for options 6-8 and help commands`

---

## 🎯 Stato Finale Atteso

### Uscita dall'app (3 modi funzionanti)

✅ **INVIO su "Esci"**: Menu → Pulsante "Esci" → Dialog conferma → Chiusura
✅ **ESC dal menu**: Menu → ESC → Dialog conferma → Chiusura
✅ **ALT+F4**: Frame → EVT_CLOSE → Destroy → Chiusura (no loop)

### Opzioni (navigazione completa)

✅ **Frecce UP/DOWN**: Navigano tra 8 opzioni con TTS
✅ **Numeri 1-8**: Saltano a opzione specifica con TTS
✅ **INVIO**: Modifica opzione corrente con TTS
✅ **T/+/-**: Comandi timer con TTS
✅ **I/H**: Recap impostazioni e aiuto (opzionale)
✅ **ESC**: Chiude dialog opzioni

### Architettura pulita

✅ **MenuPanel**: Gestisce ESC → show_exit_dialog()
✅ **GameplayPanel**: Gestisce ESC → show_abandon_game_dialog() (già OK)
✅ **OptionsDialog**: Riceve screen_reader, vocalizza tutti i messaggi
✅ **quit_app()**: Non chiama Close(), evita loop ricorsivo
✅ **_on_close_event**: Chiama Destroy() direttamente, no loop

---

## 🚨 Note Importanti per Copilot

1. **NON modificare** altri file oltre a quelli specificati in ogni FIX.
2. **NON refactorare** codice non correlato ai problemi descritti.
3. **MANTIENI** i commenti esistenti, aggiungi solo dove serve chiarire il fix.
4. **TESTA** manualmente dopo FIX 3 (dialog_manager) e FIX 5 (opzioni complete).
5. **RISPETTA** l'ordine dei FIX (1 → 2 → 3 → 4 → 5) per evitare dipendenze incrociate.

---

**Copilot**: Inizia con FIX 1. Dopo ogni commit, attendi conferma prima di procedere al FIX successivo.