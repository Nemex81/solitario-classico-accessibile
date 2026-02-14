# Piano di Implementazione: Fix Dialog Async e Gestione Eventi

**Data**: 14 Febbraio 2026  
**Branch**: `copilot/remove-pygame-migrate-wxpython`  
**Versione Target**: v2.2.1  
**Autore**: AI Assistant + Nemex81  
**Priorità**: 🔴 CRITICA (blocca funzionalità core)

---

## 📋 Executive Summary

### Problema
I dialog asincroni (`show_yes_no_async`, `show_info_async`, `show_error_async`) **non si chiudono mai** quando l'utente clicca YES/NO, causando:

1. ❌ **ESC in menu** non mostra dialog conferma uscita
2. ❌ **ESC in gameplay** non mostra dialog conferma abbandono
3. ❌ **ALT+F4** chiude app senza conferma
4. ❌ **Tasto N in gameplay** non mostra dialog conferma nuova partita

### Root Cause
`WxDialogProvider.show_yes_no_async()` usa `dialog.Show()` (non-blocking) con `EVT_CLOSE` per intercettare la chiusura.

**Il bug**: `EVT_CLOSE` viene triggerato **SOLO** quando:
- Utente clicca X del dialog
- Utente preme ALT+F4 sul dialog

**NON viene triggerato** quando utente clicca YES/NO!

Risultato:
- Il dialog rimane in memoria
- Mantiene il focus
- Blocca tutti gli eventi futuri dei panel

### Soluzione
**Semi-Modal Pattern**: Usare `ShowModal()` (bloccante) ma chiamato da `wx.CallAfter()` per evitare nested event loops.

**Pattern Flow**:
```
Event Handler → wx.CallAfter(show_modal_and_callback)
                ↓
                [wxPython idle loop]
                ↓
                show_modal_and_callback() executes
                ↓
                ShowModal() blocks (user responds)
                ↓
                Destroy() dialog
                ↓
                callback(result) invoked
                ↓
                Focus returns to panel automatically
```

**Vantaggi**:
- ✅ `ShowModal()` gestisce correttamente YES/NO/ESC/X
- ✅ Dialog si chiude sempre con `Destroy()`
- ✅ Focus torna automaticamente al panel chiamante
- ✅ `wx.CallAfter()` previene nested event loops
- ✅ Callback viene invocato nel giusto contesto (deferred)

---

## 🎯 Requisiti Funzionali

### 1. ESC in Menu Principale
**Comportamento Atteso**:
1. Utente preme ESC mentre è nel menu
2. Si apre dialog: "Vuoi uscire dal gioco?"
3. Utente sceglie:
   - **YES**: App si chiude con `sys.exit(0)`
   - **NO** o **ESC**: Dialog si chiude, resta nel menu

**File Coinvolti**:
- `src/infrastructure/ui/menu_panel.py` (già corretto ✅)
- `test.py` - `show_exit_dialog()` → `quit_app()` (già corretto ✅)
- `src/infrastructure/ui/wx_dialog_provider.py` - `show_yes_no_async()` (DA FIXARE 🔧)

### 2. ESC in Gameplay
**Comportamento Atteso**:
1. Utente preme ESC durante partita
2. Si apre dialog: "Vuoi abbandonare la partita e tornare al menu?"
3. Utente sceglie:
   - **YES**: Reset game → Ritorna al menu
   - **NO** o **ESC**: Dialog si chiude, continua partita

**File Coinvolti**:
- `src/infrastructure/ui/gameplay_panel.py` (già corretto ✅)
- `test.py` - `show_abandon_game_dialog()` → `_safe_abandon_to_menu()` (già corretto ✅)
- `src/infrastructure/ui/wx_dialog_provider.py` - `show_yes_no_async()` (DA FIXARE 🔧)

### 3. ALT+F4 (da qualsiasi schermata)
**Comportamento Atteso**:
1. Utente preme ALT+F4
2. Frame intercetta con `EVT_CLOSE`
3. Veto close event
4. Si apre dialog: "Vuoi uscire dal gioco?"
5. Utente sceglie:
   - **YES**: App si chiude con `sys.exit(0)`
   - **NO** o **ESC**: Veto mantiene app aperta

**File Coinvolti**:
- `src/infrastructure/ui/wx_frame.py` - `_on_close_event()` (DA FIXARE 🔧)
- `test.py` - `quit_app()` (già corretto ✅)
- `src/infrastructure/ui/wx_dialog_provider.py` - `show_yes_no_async()` (DA FIXARE 🔧)

### 4. Tasto N in Gameplay (nuova partita)
**Comportamento Atteso**:
1. Utente preme N durante partita attiva
2. Si apre dialog: "Una partita è già in corso. Vuoi iniziare una nuova partita?"
3. Utente sceglie:
   - **YES**: Reset + Avvia nuova partita
   - **NO** o **ESC**: Dialog si chiude, continua partita

**File Coinvolti**:
- `src/application/gameplay_controller.py` - `_new_game()` (già corretto ✅)
- `test.py` - `show_new_game_dialog()` (già corretto ✅)
- `src/infrastructure/ui/wx_dialog_provider.py` - `show_yes_no_async()` (DA FIXARE 🔧)

---

## 🔍 Analisi Tecnica Dettagliata

### Codice Problematico (wx_dialog_provider.py, linee 141-165)

```python
def show_yes_no_async(
    self,
    title: str,
    message: str,
    callback: Callable[[bool], None]
) -> None:
    """Show non-blocking yes/no dialog with callback."""
    dialog = wx.MessageDialog(
        parent=self._get_parent(),
        message=message,
        caption=title,
        style=wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION
    )
    
    def on_dialog_close(event):
        result = dialog.GetReturnCode() == wx.ID_YES
        dialog.Destroy()
        callback(result)  # Invoke callback with result
    
    dialog.Bind(wx.EVT_CLOSE, on_dialog_close)  # ❌ BUG: Non triggera per YES/NO
    dialog.Show()  # NON-BLOCKING (not ShowModal)
```

**Perché Non Funziona**:

1. `dialog.Show()` mostra il dialog ma **non blocca** il thread
2. `EVT_CLOSE` viene triggerato quando il dialog viene chiuso tramite:
   - Click su X (close button)
   - ALT+F4 sul dialog
3. **PROBLEMA**: Click su YES/NO chiude il dialog con `EndModal()` internamente, ma **non triggera** `EVT_CLOSE`
4. Risultato: `on_dialog_close` non viene mai chiamato
5. `dialog.Destroy()` non viene mai eseguito
6. Dialog rimane in memoria con il focus
7. Eventi futuri dei panel vengono ignorati (focus resta sul dialog "fantasma")

### Perché ShowModal è la Soluzione

`ShowModal()` gestisce internamente tutto il ciclo di vita del dialog:

```python
result = dialog.ShowModal()  # Blocca fino a click YES/NO/ESC/X
# Qui result contiene:
# - wx.ID_YES se click su YES
# - wx.ID_NO se click su NO
# - wx.ID_CANCEL se ESC o X
```

**Vantaggi**:
- Tutti i bottoni (YES/NO/ESC/X) funzionano correttamente
- `GetReturnCode()` è affidabile
- Focus torna automaticamente al parent dopo `Destroy()`
- Nessun dialog "fantasma" in memoria

**Problema con ShowModal**:
- Blocca il thread → Nested event loop se chiamato da event handler

**Soluzione**:
- Usare `wx.CallAfter(show_modal_and_callback)` per deferrire l'intera sequenza

---

## 📝 Piano di Implementazione (5 Commit Incrementali)

### COMMIT 1: Fix show_yes_no_async (Semi-Modal Pattern)
**Priorità**: 🔴 CRITICA  
**File**: `src/infrastructure/ui/wx_dialog_provider.py`  
**Linee**: 141-165

#### Codice Attuale
```python
def show_yes_no_async(
    self,
    title: str,
    message: str,
    callback: Callable[[bool], None]
) -> None:
    """Show non-blocking yes/no dialog with callback.
    
    Args:
        title: Dialog title
        message: Dialog message
        callback: Function called with result (True=Yes, False=No)
    
    Example:
        >>> def on_result(confirmed: bool):
        ...     if confirmed:
        ...         print("User confirmed")
        >>> provider.show_yes_no_async("Title", "Message?", on_result)
    
    Version:
        v2.2: Added async API to prevent nested event loops
    """
    dialog = wx.MessageDialog(
        parent=self._get_parent(),
        message=message,
        caption=title,
        style=wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION
    )
    
    def on_dialog_close(event):
        result = dialog.GetReturnCode() == wx.ID_YES
        dialog.Destroy()
        callback(result)  # Invoke callback with result
    
    dialog.Bind(wx.EVT_CLOSE, on_dialog_close)
    dialog.Show()  # NON-BLOCKING (not ShowModal)
```

#### Codice Nuovo (SOSTITUIRE COMPLETAMENTE)
```python
def show_yes_no_async(
    self,
    title: str,
    message: str,
    callback: Callable[[bool], None]
) -> None:
    """Show yes/no dialog (semi-modal) with deferred callback.
    
    Pattern: ShowModal() called from wx.CallAfter() prevents nested event loops
    while ensuring proper dialog lifecycle (YES/NO/ESC all handled correctly).
    
    Architecture:
        1. Method returns immediately (non-blocking for caller)
        2. wx.CallAfter() schedules show_modal_and_callback() for next idle
        3. [wxPython processes current event handler to completion]
        4. [wxPython idle loop picks up deferred call]
        5. show_modal_and_callback() executes in clean context
        6. ShowModal() blocks until user responds (safe, no nested loop)
        7. Dialog destroyed, callback invoked, focus restored
    
    Why ShowModal is Safe Here:
        - Called from wx.CallAfter() = deferred context (not event handler)
        - No nested event loop because original handler already completed
        - All dialog buttons (YES/NO/ESC/X) work correctly
        - Focus returns to parent automatically after Destroy()
    
    Args:
        title: Dialog title
        message: Dialog message  
        callback: Function called with result (True=Yes, False=No/ESC/X)
    
    Example:
        >>> def on_result(confirmed: bool):
        ...     if confirmed:
        ...         print("User confirmed")
        ...     else:
        ...         print("User declined or cancelled")
        >>> provider.show_yes_no_async("Conferma", "Sei sicuro?", on_result)
        # Returns immediately, callback invoked after user responds
    
    Version:
        v2.2: Added async API to prevent nested event loops
        v2.2.1: Fixed to use semi-modal pattern (ShowModal + CallAfter)
    """
    
    def show_modal_and_callback():
        """Deferred function that shows modal dialog and invokes callback.
        
        This function executes in deferred context (wx.CallAfter), ensuring:
        - No nested event loop (original handler already completed)
        - ShowModal() blocks safely until user responds
        - All dialog buttons work correctly (YES/NO/ESC/X)
        - Dialog always destroyed (no memory leaks)
        - Callback invoked with correct result
        - Focus returns to parent automatically
        """
        # Create modal dialog
        dialog = wx.MessageDialog(
            parent=self._get_parent(),
            message=message,
            caption=title,
            style=wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION
        )
        
        # ShowModal blocks until user clicks YES/NO/ESC/X
        # Returns: wx.ID_YES, wx.ID_NO, or wx.ID_CANCEL
        result_code = dialog.ShowModal()
        
        # Interpret result (True for YES, False for NO/ESC/X)
        result = (result_code == wx.ID_YES)
        
        # CRITICAL: Always destroy dialog (prevents memory leaks)
        dialog.Destroy()
        
        # Invoke callback with result (already in deferred context, safe)
        callback(result)
    
    # Defer entire dialog sequence to next idle cycle
    # This prevents nested event loops and ensures clean execution
    wx.CallAfter(show_modal_and_callback)
```

#### Test di Verifica
Dopo questa modifica, testare:
1. ✅ ESC in menu → Dialog si apre, YES chiude app, NO resta in menu
2. ✅ ESC in gameplay → Dialog si apre, YES abbandona, NO continua
3. ✅ N in gameplay → Dialog si apre, YES nuova partita, NO continua

---

### COMMIT 2: Fix show_info_async (Semi-Modal Pattern)
**Priorità**: 🟡 MEDIA  
**File**: `src/infrastructure/ui/wx_dialog_provider.py`  
**Linee**: 167-199

#### Codice Attuale
```python
def show_info_async(
    self,
    title: str,
    message: str,
    callback: Optional[Callable[[], None]] = None
) -> None:
    """Show non-blocking info dialog with optional callback.
    
    Args:
        title: Dialog title
        message: Info message
        callback: Optional function called when dialog closes
    
    Version:
        v2.2: Added async API
    """
    dialog = wx.MessageDialog(
        parent=self._get_parent(),
        message=message,
        caption=title,
        style=wx.OK | wx.ICON_INFORMATION
    )
    
    def on_dialog_close(event):
        dialog.Destroy()
        if callback:
            callback()
    
    dialog.Bind(wx.EVT_CLOSE, on_dialog_close)
    dialog.Show()
```

#### Codice Nuovo (SOSTITUIRE COMPLETAMENTE)
```python
def show_info_async(
    self,
    title: str,
    message: str,
    callback: Optional[Callable[[], None]] = None
) -> None:
    """Show info dialog (semi-modal) with optional callback.
    
    Pattern: ShowModal() called from wx.CallAfter() for consistency with
    show_yes_no_async(). Ensures proper dialog lifecycle.
    
    Args:
        title: Dialog title
        message: Info message
        callback: Optional function called after dialog closes
    
    Example:
        >>> def on_closed():
        ...     print("Info dialog closed")
        >>> provider.show_info_async("Info", "Partita avviata!", on_closed)
    
    Version:
        v2.2: Added async API
        v2.2.1: Fixed to use semi-modal pattern (ShowModal + CallAfter)
    """
    
    def show_modal_and_callback():
        """Deferred function that shows modal info dialog."""
        dialog = wx.MessageDialog(
            parent=self._get_parent(),
            message=message,
            caption=title,
            style=wx.OK | wx.ICON_INFORMATION
        )
        
        # ShowModal blocks until user clicks OK or ESC
        dialog.ShowModal()
        
        # Always destroy dialog
        dialog.Destroy()
        
        # Invoke optional callback
        if callback:
            callback()
    
    # Defer entire dialog sequence
    wx.CallAfter(show_modal_and_callback)
```

#### Test di Verifica
Verificare che dialoghi informativi si chiudano correttamente (nessun uso corrente nell'app, ma per consistency).

---

### COMMIT 3: Fix show_error_async (Semi-Modal Pattern)
**Priorità**: 🟡 MEDIA  
**File**: `src/infrastructure/ui/wx_dialog_provider.py`  
**Linee**: 201-233

#### Codice Attuale
```python
def show_error_async(
    self,
    title: str,
    message: str,
    callback: Optional[Callable[[], None]] = None
) -> None:
    """Show non-blocking error dialog with optional callback.
    
    Args:
        title: Dialog title
        message: Error message
        callback: Optional function called when dialog closes
    
    Version:
        v2.2: Added async API
    """
    dialog = wx.MessageDialog(
        parent=self._get_parent(),
        message=message,
        caption=title,
        style=wx.OK | wx.ICON_ERROR
    )
    
    def on_dialog_close(event):
        dialog.Destroy()
        if callback:
            callback()
    
    dialog.Bind(wx.EVT_CLOSE, on_dialog_close)
    dialog.Show()
```

#### Codice Nuovo (SOSTITUIRE COMPLETAMENTE)
```python
def show_error_async(
    self,
    title: str,
    message: str,
    callback: Optional[Callable[[], None]] = None
) -> None:
    """Show error dialog (semi-modal) with optional callback.
    
    Pattern: ShowModal() called from wx.CallAfter() for consistency with
    show_yes_no_async(). Ensures proper dialog lifecycle.
    
    Args:
        title: Dialog title
        message: Error message
        callback: Optional function called after dialog closes
    
    Example:
        >>> def on_closed():
        ...     print("Error acknowledged")
        >>> provider.show_error_async("Errore", "Mossa non valida!", on_closed)
    
    Version:
        v2.2: Added async API
        v2.2.1: Fixed to use semi-modal pattern (ShowModal + CallAfter)
    """
    
    def show_modal_and_callback():
        """Deferred function that shows modal error dialog."""
        dialog = wx.MessageDialog(
            parent=self._get_parent(),
            message=message,
            caption=title,
            style=wx.OK | wx.ICON_ERROR
        )
        
        # ShowModal blocks until user clicks OK or ESC
        dialog.ShowModal()
        
        # Always destroy dialog
        dialog.Destroy()
        
        # Invoke optional callback
        if callback:
            callback()
    
    # Defer entire dialog sequence
    wx.CallAfter(show_modal_and_callback)
```

#### Test di Verifica
Verificare che dialoghi di errore si chiudano correttamente (nessun uso corrente nell'app, ma per consistency).

---

### COMMIT 4: Fix ALT+F4 Veto Pattern
**Priorità**: 🔴 CRITICA  
**File**: `src/infrastructure/ui/wx_frame.py`  
**Linee**: 94-157

#### Problema Attuale
Il metodo `_on_close_event()` si aspetta che `quit_app()` ritorni un `bool` sincrono per decidere se fare veto. Ma `quit_app()` ora usa dialog async che ritorna `False` immediatamente.

**Comportamento Attuale**:
```python
def _on_close_event(self, event):
    # ...
    should_close = True
    
    if self.on_close is not None:
        result = self.on_close()  # quit_app() ritorna False (async)
        
        if result is False:
            should_close = False  # ← Sempre False!
    
    if not should_close:
        event.Veto()  # ← Sempre veto, ma dialog non si apre correttamente
        return
    
    self.Destroy()
```

#### Soluzione: Pattern "Always Veto First"
Invece di aspettare risultato sincrono, fare **sempre veto** inizialmente, poi lasciare che il callback del dialog chiami `sys.exit(0)` se confermato.

#### Codice Attuale (linee 94-157)
```python
def _on_close_event(self, event: wx.CloseEvent) -> None:
    """Internal handler for EVT_CLOSE events with veto support.
    
    Saves timer state, calls user callback, and handles veto if needed.
    If callback returns False, veto the close and restart timer.
    If callback returns True (or None for backward compat), proceed with destruction.
    
    Args:
        event: wx.CloseEvent from frame closure request (ALT+F4, X button, etc.)
    
    Version:
        v1.7.5: Added veto support for exit confirmation dialog
    
    Note:
        This is called when Close() is invoked, or when user closes
        the frame via window controls (ALT+F4, X button).
        
        Veto support pattern:
        - User callback can return bool to signal should_close
        - True (or None): Proceed with exit
        - False: Veto close and restore previous state (timer continues)
    """
    print("[Frame] Close event received")
    
    # Save timer state before stopping (for potential restart after veto)
    timer_was_running = False
    timer_interval = 1000  # Default fallback
    
    if self._timer is not None and self._timer.IsRunning():
        timer_was_running = True
        # Retrieve stored interval (set in start_timer)
        timer_interval = getattr(self, '_timer_interval', 1000)
        print(f"[Frame] Timer was running with interval: {timer_interval}ms")
        self.stop_timer()
    
    # Call user callback and check return value
    should_close = True  # Default: allow close
    
    if self.on_close is not None:
        result = self.on_close()
        
        # Handle bool return (v1.7.5+) or None (backward compat)
        if result is False:
            should_close = False
            print("[Frame] Close vetoed by callback (user cancelled)")
        elif result is True or result is None:
            should_close = True
            print("[Frame] Close approved by callback")
    
    # Handle veto if callback returned False
    if not should_close:
        # Check if we can veto (not all close events can be vetoed)
        if event.CanVeto():
            print("[Frame] Vetoing close event - restoring state")
            event.Veto()
            
            # Restart timer if it was running
            if timer_was_running:
                print(f"[Frame] Restarting timer with {timer_interval}ms interval")
                self.start_timer(timer_interval)
            
            return  # Exit without destroying
        else:
            # Forced close (can't veto) - proceed anyway
            print("[Frame] Close event cannot be vetoed (forced)")
    
    # Proceed with destruction
    print("[Frame] Destroying frame")
    self.Destroy()
```

#### Codice Nuovo (SOSTITUIRE COMPLETAMENTE, linee 94-157)
```python
def _on_close_event(self, event: wx.CloseEvent) -> None:
    """Internal handler for EVT_CLOSE events with async dialog support.
    
    Pattern: Always veto initially, show confirmation dialog async, then
    exit programmatically (via sys.exit) if user confirms. This pattern
    works correctly with async dialogs that return immediately.
    
    Flow:
        1. ALT+F4 or X button pressed
        2. EVT_CLOSE triggered
        3. Veto close event (if possible)
        4. Call on_close callback (shows async dialog)
        5. Dialog callback handles:
           - YES: Call sys.exit(0) to close programmatically
           - NO: Do nothing (veto already applied, app continues)
    
    Why This Works:
        - Async dialog returns immediately (no blocking)
        - Veto prevents immediate close
        - Dialog callback has full control over exit
        - If user confirms: sys.exit(0) closes everything cleanly
        - If user cancels: Veto keeps app running
    
    Args:
        event: wx.CloseEvent from frame closure request (ALT+F4, X button, etc.)
    
    Version:
        v1.7.5: Added veto support for exit confirmation dialog
        v2.2.1: Fixed for async dialog pattern (always veto first)
    
    Note:
        Timer state management removed (not needed with async pattern).
        If dialog is cancelled, app simply continues with existing state.
    """
    print("[Frame] Close event received (ALT+F4 or X button)")
    
    # Check if we can veto this close event
    if not event.CanVeto():
        # Forced close (can't be vetoed) - exit immediately
        print("[Frame] Close event cannot be vetoed (forced close)")
        self.Destroy()
        return
    
    # ALWAYS veto initially (we'll exit programmatically if confirmed)
    print("[Frame] Vetoing close event - showing confirmation dialog")
    event.Veto()
    
    # Call on_close callback which shows async confirmation dialog
    # Dialog callback will call sys.exit(0) if user confirms
    # If user cancels, veto keeps app running (no action needed)
    if self.on_close is not None:
        self.on_close()  # Shows async dialog, returns immediately
    else:
        # No callback registered - allow close by calling Destroy directly
        # This should never happen in normal operation
        print("[Frame] No on_close callback registered - destroying frame")
        self.Destroy()
```

#### Verifica Callback in test.py (GIÀ CORRETTO, linee 605-627)
```python
def quit_app(self) -> bool:
    """Graceful application shutdown with confirmation dialog (non-blocking).
    
    Shows exit confirmation dialog. If user confirms, exits application.
    If user cancels, returns control to caller (veto support for ALT+F4).
    
    Uses async dialog API. Note: Currently returns False immediately
    because async dialog doesn't block. For veto support with async
    dialogs, frame close handling needs refactoring.
    
    Called from:
    - show_exit_dialog() (menu "Esci" button, ESC in menu)
    - _on_frame_close() (ALT+F4, X button)
    
    Returns:
        bool: False (dialog shown, callback will handle exit)
    
    Version:
        v1.7.5: Changed return type from None to bool for veto support
        v2.2: Migrated to async dialog API (veto not yet supported)
    """
    def on_quit_result(confirmed: bool):
        if confirmed:
            print("\n" + "="*60)
            print("CHIUSURA APPLICAZIONE")
            print("="*60)
            
            if self.screen_reader:
                self.screen_reader.tts.speak("Chiusura in corso.", interrupt=True)
                wx.MilliSleep(800)
            
            sys.exit(0)  # ← Chiude app programmaticamente
        else:
            print("[quit_app] Exit cancelled by user")
            if self.screen_reader:
                self.screen_reader.tts.speak("Uscita annullata.", interrupt=True)
    
    self.dialog_manager.show_exit_app_prompt_async(
        callback=on_quit_result
    )
    return False  # Async dialog doesn't block, callback handles exit
```

**Questo callback è GIÀ PERFETTO** per il nuovo pattern:
- Se user conferma: `sys.exit(0)` chiude tutto
- Se user cancella: Veto già applicato, app continua

#### Test di Verifica
Dopo COMMIT 4, testare:
1. ✅ ALT+F4 in menu → Dialog si apre, YES chiude app, NO resta in menu
2. ✅ ALT+F4 in gameplay → Dialog si apre, YES chiude app, NO continua partita
3. ✅ Timer continua a girare dopo NO (se era attivo)

---

### COMMIT 5: Verification and Documentation Update
**Priorità**: 🟢 BASSA  
**File**: `docs/CHANGELOG.md`, commenti vari

#### Azioni
1. Aggiornare CHANGELOG.md con entry v2.2.1
2. Aggiornare docstring di `SolitarioDialogManager` per documentare pattern async
3. Aggiungere commenti esplicativi nei punti critici

#### CHANGELOG.md Entry
```markdown
## [2.2.1] - 2026-02-14

### Fixed
- **CRITICO**: Dialog asincroni non si chiudevano quando utente cliccava YES/NO
  - Root cause: `EVT_CLOSE` non triggera per click su bottoni dialog
  - Soluzione: Semi-modal pattern (`ShowModal()` + `wx.CallAfter()`)
  - Impatto: ESC, ALT+F4, tasto N ora funzionano correttamente
  
- **ESC in menu**: Ora mostra dialog conferma uscita correttamente
- **ESC in gameplay**: Ora mostra dialog conferma abbandono correttamente
- **ALT+F4**: Ora mostra dialog conferma uscita (con veto support)
- **Tasto N in gameplay**: Ora mostra dialog conferma nuova partita correttamente

### Changed
- `WxDialogProvider.show_yes_no_async()`: Migrato a semi-modal pattern
- `WxDialogProvider.show_info_async()`: Migrato a semi-modal pattern
- `WxDialogProvider.show_error_async()`: Migrato a semi-modal pattern
- `SolitarioFrame._on_close_event()`: Migrato a "always veto first" pattern

### Technical Details
- **Semi-Modal Pattern**: `ShowModal()` chiamato da `wx.CallAfter()` previene nested event loops
- **Always Veto First Pattern**: Veto applicato immediatamente, dialog callback gestisce `sys.exit(0)`
- **Focus Management**: Dialog modal restituisce focus automaticamente al parent dopo `Destroy()`
```

#### Test di Verifica Finale
Eseguire test completo di tutti i flussi:

**Scenario 1: ESC in Menu**
1. Avvia app → Menu principale
2. Premi ESC
3. Verifica: Dialog "Vuoi uscire dal gioco?" si apre
4. Clicca NO
5. Verifica: Dialog si chiude, resta in menu
6. Premi ESC di nuovo
7. Clicca YES
8. Verifica: App si chiude

**Scenario 2: ESC in Gameplay**
1. Avvia app → Menu → "Gioca al solitario"
2. Premi ESC
3. Verifica: Dialog "Vuoi abbandonare la partita?" si apre
4. Clicca NO
5. Verifica: Dialog si chiude, continua partita
6. Premi ESC di nuovo
7. Clicca YES
8. Verifica: Ritorna al menu

**Scenario 3: ALT+F4**
1. Avvia app → Menu principale
2. Premi ALT+F4
3. Verifica: Dialog "Vuoi uscire dal gioco?" si apre
4. Clicca NO
5. Verifica: Dialog si chiude, resta in menu
6. Vai in gameplay
7. Premi ALT+F4
8. Clicca YES
9. Verifica: App si chiude

**Scenario 4: Tasto N**
1. Avvia app → Menu → "Gioca al solitario"
2. Premi N
3. Verifica: Dialog "Una partita è già in corso..." si apre
4. Clicca NO
5. Verifica: Dialog si chiude, continua partita originale
6. Premi N di nuovo
7. Clicca YES
8. Verifica: Nuova partita avviata (mazzo rimescolato)

**Scenario 5: Focus dopo Dialog**
1. Esegui uno dei scenari sopra con NO
2. Verifica: Focus torna al panel corretto
3. Premi H (help)
4. Verifica: TTS legge comandi (focus funzionante)

---

## 🧪 Testing Checklist

Dopo ogni commit, verificare:

### COMMIT 1 (show_yes_no_async)
- [ ] ESC in menu → Dialog si apre
- [ ] ESC in menu → Click YES → App chiude
- [ ] ESC in menu → Click NO → Resta in menu
- [ ] ESC in menu → ESC su dialog → Resta in menu
- [ ] ESC in gameplay → Dialog si apre
- [ ] ESC in gameplay → Click YES → Ritorna menu
- [ ] ESC in gameplay → Click NO → Continua partita
- [ ] N in gameplay → Dialog si apre
- [ ] N in gameplay → Click YES → Nuova partita
- [ ] N in gameplay → Click NO → Continua partita

### COMMIT 2+3 (show_info_async, show_error_async)
- [ ] Nessun dialog info/error attualmente usato (skip test funzionali)
- [ ] Compilazione OK (no syntax errors)
- [ ] Pattern consistency con show_yes_no_async

### COMMIT 4 (ALT+F4 veto)
- [ ] ALT+F4 in menu → Dialog si apre
- [ ] ALT+F4 in menu → Click YES → App chiude
- [ ] ALT+F4 in menu → Click NO → Resta in menu
- [ ] ALT+F4 in gameplay → Dialog si apre
- [ ] ALT+F4 in gameplay → Click YES → App chiude
- [ ] ALT+F4 in gameplay → Click NO → Continua partita
- [ ] Timer continua dopo NO (se attivo)

### COMMIT 5 (Documentation)
- [ ] CHANGELOG.md aggiornato
- [ ] Commenti inline aggiornati
- [ ] Docstring complete e accurate
- [ ] Test completo tutti gli scenari

---

## 🎓 Architectural Patterns Reference

### Semi-Modal Pattern
**Quando Usare**: Dialog che deve bloccare input ma essere chiamato da event handler

**Pattern**:
```python
def show_dialog_async(callback):
    def show_modal_and_callback():
        dialog = wx.MessageDialog(...)
        result = dialog.ShowModal()  # Blocks safely (deferred context)
        dialog.Destroy()
        callback(result)
    
    wx.CallAfter(show_modal_and_callback)  # Defer to avoid nested loop
```

**Caratteristiche**:
- Metodo ritorna immediatamente (async per chiamante)
- Dialog mostrato in contesto deferito (no nested loop)
- ShowModal blocca fino a risposta utente
- Callback invocato in contesto deferito (safe)

### Always Veto First Pattern
**Quando Usare**: Frame close con dialog async per conferma

**Pattern**:
```python
def _on_close_event(self, event):
    if not event.CanVeto():
        self.Destroy()
        return
    
    event.Veto()  # Always veto first
    
    if self.on_close:
        self.on_close()  # Shows async dialog
        # Dialog callback calls sys.exit(0) if confirmed
        # Veto keeps app running if cancelled
```

**Caratteristiche**:
- Veto applicato immediatamente (sempre)
- Dialog async mostra conferma
- Callback dialog controlla exit (`sys.exit(0)`)
- Veto mantiene app aperta se user cancella

---

## 📚 References

### wxPython Dialog Documentation
- [wx.MessageDialog](https://docs.wxpython.org/wx.MessageDialog.html)
- [wx.Dialog.ShowModal](https://docs.wxpython.org/wx.Dialog.html#wx.Dialog.ShowModal)
- [wx.CallAfter](https://docs.wxpython.org/wx.functions.html#wx.CallAfter)
- [wx.CloseEvent](https://docs.wxpython.org/wx.CloseEvent.html)
- [Event Veto](https://docs.wxpython.org/wx.Event.html#wx.Event.Veto)

### Internal Architecture Docs
- `docs/ARCHITECTURE.md` - Clean Architecture layers
- `docs/UI_PATTERNS.md` - Panel-swap pattern documentation
- `docs/DEFERRED_TRANSITIONS.md` - wx.CallAfter pattern guide

### Related Code Files
- `src/infrastructure/ui/wx_dialog_provider.py` - Dialog provider implementation
- `src/infrastructure/ui/wx_frame.py` - Main frame with close handling
- `src/application/dialog_manager.py` - Dialog manager facade
- `test.py` - Application entry point with callbacks

---

## ✅ Success Criteria

Implementation is considered successful when:

1. **Functional**:
   - ✅ ESC in menu shows exit dialog
   - ✅ ESC in gameplay shows abandon dialog
   - ✅ ALT+F4 shows exit dialog (with veto)
   - ✅ N key shows new game dialog
   - ✅ All dialog buttons (YES/NO/ESC/X) work correctly
   - ✅ Focus returns to panel after dialog closes

2. **Technical**:
   - ✅ No dialog memory leaks (all dialogs destroyed)
   - ✅ No nested event loops (no crashes)
   - ✅ Focus management correct (NVDA reads panel content)
   - ✅ Timer continues after cancelled dialogs

3. **Code Quality**:
   - ✅ All commits compile without errors
   - ✅ Code follows existing patterns and conventions
   - ✅ Docstrings complete and accurate
   - ✅ Comments explain non-obvious logic
   - ✅ CHANGELOG.md updated

4. **Accessibility**:
   - ✅ NVDA reads dialog title and message on open
   - ✅ NVDA reads button labels on focus
   - ✅ TAB navigation works in dialogs
   - ✅ ENTER/SPACE activate focused button
   - ✅ ESC closes dialog (cancels action)

---

## 🚨 Common Pitfalls to Avoid

### ❌ DON'T: Use EVT_CLOSE for Button Clicks
```python
# WRONG - EVT_CLOSE not triggered by YES/NO buttons
dialog.Bind(wx.EVT_CLOSE, on_dialog_close)
dialog.Show()  # Dialog never destroyed when YES/NO clicked
```

### ❌ DON'T: Call ShowModal Directly from Event Handler
```python
# WRONG - Creates nested event loop
def on_key_down(self, event):
    dialog = wx.MessageDialog(...)
    result = dialog.ShowModal()  # CRASH RISK!
```

### ❌ DON'T: Expect Async Dialog to Block
```python
# WRONG - Dialog returns immediately
def quit_app(self):
    result = show_yes_no_async("Exit?")  # Returns None immediately
    if result:  # Will never be True!
        sys.exit(0)
```

### ✅ DO: Use Semi-Modal Pattern
```python
# CORRECT - ShowModal called from deferred context
def show_yes_no_async(callback):
    def show_modal_and_callback():
        dialog = wx.MessageDialog(...)
        result = dialog.ShowModal()
        dialog.Destroy()
        callback(result)
    
    wx.CallAfter(show_modal_and_callback)
```

### ✅ DO: Handle Exit in Dialog Callback
```python
# CORRECT - Callback controls exit
def on_quit_result(confirmed):
    if confirmed:
        sys.exit(0)  # Exit programmatically
    # If cancelled, veto already applied, app continues
```

---

## 📞 Support and Questions

Per domande o problemi durante l'implementazione:

1. **Riferimento**: Questo documento (`docs/PLAN_FIX_DIALOG_ASYNC.md`)
2. **Codice Esistente**: Studiare pattern in `test.py` (già corretto)
3. **wxPython Docs**: https://docs.wxpython.org/
4. **GitHub Issues**: Aprire issue con tag `bug` e `dialog`

---

**Fine del Piano di Implementazione**

**Prossimi Step**:
1. Copilot implementa COMMIT 1 (fix show_yes_no_async)
2. Test funzionale ESC/N keys
3. Copilot implementa COMMIT 2+3 (fix show_info/error_async)
4. Copilot implementa COMMIT 4 (fix ALT+F4 veto)
5. Test funzionale ALT+F4
6. Copilot implementa COMMIT 5 (documentation)
7. Test completo tutti gli scenari
8. Merge su branch principale

**Stima Tempo**: 2-3 ore (implementazione + testing completo)
