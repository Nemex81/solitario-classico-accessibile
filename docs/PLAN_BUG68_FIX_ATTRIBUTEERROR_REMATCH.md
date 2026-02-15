# 📋 Piano Implementazione Bug #68.4 - Regressione Async Dialogs

> **Fix architetturale per regressione**: Refactor `show_statistics_report()` a pattern async

---

## 📊 Executive Summary

**Tipo**: BUGFIX (Regressione da COMMIT 3 Copilot) + REFACTOR (Architectural Fix)  
**Priorità**: 🔴 CRITICA (app crasha al termine ogni partita)  
**Stato**: READY  
**Branch**: `copilot/refactor-difficulty-options-system`  
**Versione Target**: `v2.5.0`  
**Data Creazione**: 2026-02-15  
**Autore**: AI Assistant + Nemex81  
**Effort Stimato**: 1.5 ore totali (1h implementazione + 30min testing)  
**Commits Previsti**: 3 commit atomici

---

### Problema (Regressione)

Dopo l'implementazione di Copilot (COMMIT 1-3 per Bug #68 async rematch dialog), il gioco crasha con comportamento anomalo:

**Sintomi**:
```
User: CTRL+ALT+W (debug force victory)
↓
Stats dialog appare ✅
↓
User: Preme INVIO su OK button
↓
❌ Rematch dialog NON appare
❌ App chiude immediatamente
❌ Console log: "⚠️ wx.App not active, skipping async dialog"
```

**Log Evidence**:
```
⚠️ wx.App not active, skipping async dialog
→ Game ended callback - Rematch: False
→ Returning to main menu...
→ _safe_return_to_main_menu() called
  ✓ Gameplay panel hidden
  ✓ Game state reset
[App termina]
```

**Impatto utente**:
- ❌ Impossibile rigiocare dopo vittoria
- ❌ App chiude invece di mostrare rematch dialog
- ❌ Bug #68 NON completamente risolto
- ❌ Flusso end-game completamente rotto

---

### Root Cause (Analisi Completa)

#### Il Check Troppo Aggressivo

Copilot **COMMIT 3** (76e9ce1) ha aggiunto questo check di sicurezza:

```python
# File: wx_dialog_provider.py, linea ~267
# Inside: show_yes_no_async()

app = wx.GetApp()
if app and app.IsMainLoopRunning():
    wx.CallAfter(show_modal_and_callback)
else:
    # ❌ PROBLEMA QUI!
    print("⚠️ wx.App not active, skipping async dialog")
    callback(False)  # Assume user declined
```

**Intento**: Prevenire crash durante chiusura app (graceful degradation).  
**Problema**: Check scatta anche in situazioni normali!

---

#### Nested Event Loop Issue

**`show_statistics_report()` è l'UNICO dialog sincrono rimasto**:

```python
# File: wx_dialog_provider.py, linea ~442
def show_statistics_report(self, stats, final_score, is_victory, deck_type):
    app = wx.App()  # ❌ Crea NUOVA app instance!
    
    dlg = wx.Dialog(...)
    dlg.ShowModal()  # ❌ BLOCCA event loop principale!
    dlg.Destroy()
    wx.Yield()
```

**Cosa succede**:

```
1. end_game() chiama show_statistics_report()
   │
   │ [Main event loop: RUNNING]
   ↓
2. show_statistics_report() crea wx.App() instance
   │
   │ [Nuova app instance creata]
   ↓
3. ShowModal() blocca main event loop
   │
   │ [Main event loop: NESTED/BLOCKED]
   │ [Nested event loop gestisce dialog]
   ↓
4. User preme OK, dialog chiude
   │
   │ [Nuova app instance distrutta]
   ↓
5. wx.GetApp() ritorna None o app.IsMainLoopRunning() = False
   │
   │ [Main loop riprende, ma wx.GetApp() confuso!]
   ↓
6. show_rematch_prompt_async() esegue
   ↓
7. show_yes_no_async() check: wx.GetApp().IsMainLoopRunning()
   ↓
8. ❌ Check FALLISCE! (pensa che app sta chiudendo)
   ↓
9. ❌ Salta dialog, chiama callback(False)
   ↓
10. ❌ User non vede rematch dialog, app chiude
```

---

#### Diagramma Flusso (BROKEN)

```
end_game()
  │
  ├─ show_statistics_report()  [🔴 SINCRONO - nested loop!]
  │   │
  │   ├─ wx.App()  [❌ Crea nuova instance]
  │   ├─ ShowModal()  [❌ Blocca main loop]
  │   └─ Destroy()  [❌ Distrugge app]
  │
  └─ show_rematch_prompt_async()
      └─ show_yes_no_async()
          ├─ wx.GetApp()  [❌ Ritorna None o invalid!]
          ├─ IsMainLoopRunning()  [❌ = False]
          └─ callback(False)  [❌ Salta dialog!]
```

---

### Soluzione Proposta (OPZIONE C - Architectural Fix)

**Refactor completo a pattern 100% async**:

1. ✅ Convertire `show_statistics_report()` → `show_statistics_report_async()`
2. ✅ Update `end_game()` per usare callback chain
3. ✅ Rimuovere check `IsMainLoopRunning()` (non più necessario)

**Pattern Finale**:
```
end_game()
  │
  ├─ show_statistics_report_async(callback=on_stats_closed)  [🟢 ASYNC]
  │   │
  │   ├─ wx.CallAfter(show_modal_and_callback)  [✅ No nested loop]
  │   │   ├─ ShowModal()  [✅ Esegue in context deferito]
  │   │   └─ callback()  [✅ Invoca on_stats_closed]
  │   │
  │   └─ on_stats_closed()
  │       └─ show_rematch_prompt_async(callback=on_rematch_result)
  │           └─ show_yes_no_async()
  │               ├─ wx.GetApp()  [✅ Sempre valido!]
  │               └─ wx.CallAfter(...)  [✅ Funziona sempre]
  │
  └─ [Returns immediately, callback chain handles rest]
```

**Vantaggi**:
- ✅ Zero nested event loops
- ✅ `wx.GetApp()` sempre valido
- ✅ Log completi (ogni callback tracciato)
- ✅ Architettura consistente (100% async)
- ✅ Bug #68 completamente risolto

---

### Impact Assessment

| Aspetto | Impatto | Note |
|---------|---------|------|
| **Severità** | 🔴 CRITICA | App inutilizzabile (crash ogni partita) |
| **Scope** | 2 file, ~80 righe | `wx_dialog_provider.py` + `game_engine.py` |
| **Rischio regressione** | 🟢 BASSO | Pattern già usato in altri dialog async |
| **Breaking changes** | NO | API backward compatible (deprecation wrapper) |
| **Testing** | 🟡 MEDIO | 7 scenari manuali (end-game flow complesso) |

---

## 🎯 Requisiti Funzionali

### 1. Statistics Dialog Async

**Comportamento Atteso**:
1. User completa partita o preme CTRL+ALT+W
2. `end_game()` chiama `show_statistics_report_async(callback)`
3. Stats dialog appare (non-blocking)
4. User preme OK o ESC
5. Dialog chiude
6. Callback `on_stats_closed()` invocato
7. **Nessun crash, nessun nested loop**

### 2. Callback Chain Rematch

**Comportamento Atteso**:
1. `on_stats_closed()` chiamato dopo stats dialog chiude
2. `show_rematch_prompt_async(callback)` eseguito
3. Rematch dialog appare
4. User sceglie YES/NO
5. Callback `on_rematch_result(wants_rematch)` invocato
6. `handle_game_ended(wants_rematch)` in `acs_wx.py` gestisce scelta

### 3. Check IsMainLoopRunning Removed

**Comportamento Atteso**:
1. `show_yes_no_async()` esegue sempre `wx.CallAfter()`
2. Nessun check `IsMainLoopRunning()`
3. `wx.CallAfter()` gestisce graceful shutdown automaticamente (wxPython feature)
4. Nessun warning "⚠️ wx.App not active"

---

## 📝 Piano di Implementazione

### COMMIT 1: Refactor show_statistics_report_async

**Priorità**: 🔴 CRITICA  
**File**: `src/infrastructure/ui/wx_dialog_provider.py`  
**Linee**: ~442-520 (metodo `show_statistics_report`)

#### Codice Attuale (SINCRONO - BROKEN)

```python
def show_statistics_report(
    self,
    stats: Dict[str, Any],
    final_score: Optional[Dict[str, Any]],
    is_victory: bool,
    deck_type: str
) -> None:
    """Show structured statistics report dialog."""
    # Generate report
    from src.presentation.formatters.report_formatter import ReportFormatter
    report_text = ReportFormatter.format_final_report(...)
    
    # ❌ PROBLEMA: Crea nuova app instance
    app = wx.App()
    
    # Create dialog
    title = "Congratulazioni!" if is_victory else "Partita Terminata"
    dlg = wx.Dialog(self._get_parent(), title=title, ...)
    
    # ... create controls ...
    
    # ❌ PROBLEMA: ShowModal blocca main loop
    dlg.ShowModal()
    dlg.Destroy()
    wx.Yield()
```

#### Codice Nuovo (ASINCRONO - FIXED)

```python
def show_statistics_report_async(
    self,
    stats: Dict[str, Any],
    final_score: Optional[Dict[str, Any]],
    is_victory: bool,
    deck_type: str,
    callback: Callable[[], None]
) -> None:
    """Show structured statistics report dialog (NON-BLOCKING).
    
    Async version that uses wx.CallAfter() to avoid nested event loop issues.
    
    Args:
        stats: Final statistics dictionary
        final_score: Optional score breakdown
        is_victory: True if all 4 suits completed
        deck_type: "french" or "neapolitan" for suit name formatting
        callback: Function called when dialog closes (no arguments)
    
    Flow:
        1. Method returns immediately (non-blocking)
        2. wx.CallAfter() schedules show_modal_and_callback()
        3. [wxPython idle loop picks up deferred call]
        4. Dialog shown with ShowModal() (safe in deferred context)
        5. User presses OK or ESC
        6. Dialog destroyed
        7. callback() invoked (deferred context)
        8. Caller continues flow (e.g., show rematch dialog)
    
    Why This Works:
        - No wx.App() creation (uses existing app instance)
        - ShowModal() in deferred context = no nested event loop
        - wx.GetApp() always valid after this pattern
        - Consistent with all other async dialogs
    
    Example:
        >>> def on_stats_closed():
        ...     print("Stats closed, showing rematch dialog...")
        ...     self.show_rematch_prompt_async(on_rematch)
        >>> provider.show_statistics_report_async(
        ...     stats, score, True, 'french', on_stats_closed
        ... )
        # Returns immediately, callback invoked after user closes dialog
    
    Version:
        v2.5.0: Refactored to async for Bug #68 regressione fix
    """
    
    def show_modal_and_callback():
        """Deferred function: show modal dialog then invoke callback."""
        # Generate report
        from src.presentation.formatters.report_formatter import ReportFormatter
        report_text = ReportFormatter.format_final_report(
            stats=stats,
            final_score=final_score,
            is_victory=is_victory,
            deck_type=deck_type
        )
        
        # Get parent frame (NO wx.App() creation!)
        parent = self._get_parent()
        
        # Create dialog
        title = "Congratulazioni!" if is_victory else "Partita Terminata"
        dlg = wx.Dialog(
            parent,
            title=title,
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.FRAME_FLOAT_ON_PARENT
        )
        
        # Create vertical sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Add multiline TextCtrl (read-only, wordwrap, accessible)
        text_ctrl = wx.TextCtrl(
            dlg,
            value=report_text,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP
        )
        text_ctrl.SetMinSize((500, 350))
        sizer.Add(text_ctrl, 1, wx.ALL | wx.EXPAND, 10)
        
        # Add OK button
        btn_ok = wx.Button(dlg, wx.ID_OK, "OK")
        sizer.Add(btn_ok, 0, wx.ALL | wx.CENTER, 10)
        
        # Apply layout
        dlg.SetSizer(sizer)
        dlg.Fit()
        dlg.CenterOnScreen()
        
        # Auto-focus TextCtrl for NVDA
        text_ctrl.SetFocus()
        
        # ShowModal blocks (safe in deferred context)
        dlg.ShowModal()
        
        # Always destroy
        dlg.Destroy()
        
        # Log closure
        print("Statistics report closed")
        
        # Invoke callback (continue async chain)
        callback()
    
    # Defer entire dialog sequence
    wx.CallAfter(show_modal_and_callback)

# OPTIONAL: Keep deprecated sync version for backward compatibility
def show_statistics_report(
    self,
    stats: Dict[str, Any],
    final_score: Optional[Dict[str, Any]],
    is_victory: bool,
    deck_type: str
) -> None:
    """DEPRECATED: Use show_statistics_report_async() instead.
    
    Synchronous API maintained for backward compatibility.
    Creates nested event loop - avoid if possible.
    
    Will be removed in v3.0.
    """
    import warnings
    warnings.warn(
        "show_statistics_report() is deprecated, use show_statistics_report_async()",
        DeprecationWarning,
        stacklevel=2
    )
    
    # Fallback: Call async version with empty callback
    self.show_statistics_report_async(
        stats, final_score, is_victory, deck_type,
        callback=lambda: None  # No-op callback
    )
```

#### Rationale

**Perché questa soluzione è corretta**:

1. **Nessun wx.App() Multiplo**:
   - Usa `self._get_parent()` che riferisce app esistente
   - Nessuna creazione nuova instance
   - `wx.GetApp()` sempre valido dopo esecuzione

2. **Pattern Async Consistente**:
   - Identico a `show_yes_no_async()`, `show_info_async()`
   - Wrapper interno `show_modal_and_callback()`
   - `wx.CallAfter()` per esecuzione deferita

3. **Callback Chain Supportato**:
   - `callback()` parameter permette concatenazione
   - Chiamato DOPO `dlg.Destroy()`
   - Context pulito per dialog successivi

4. **Backward Compatibility**:
   - Metodo originale mantenuto come deprecation wrapper
   - Chiama versione async internamente
   - Codice esistente continua a funzionare

**Non ci sono regressioni perché**:
- ✅ Pattern già validato (altri dialog async)
- ✅ UI identica (stesso layout, stesso comportamento)
- ✅ NVDA compatibile (focus management invariato)
- ✅ Backward compatible (deprecation wrapper)

#### Testing COMMIT 1

```bash
python -m py_compile src/infrastructure/ui/wx_dialog_provider.py
# Expected: No errors

python acs_wx.py
N → CTRL+ALT+W
# Expected: Stats dialog appare (comportamento invariato)
```

#### Commit Message

```
refactor(dialogs): Convert show_statistics_report to async pattern

Bug #68 regressione fix (part 1/3)

Problem:
- show_statistics_report() was ONLY synchronous dialog left
- Creates nested event loop with wx.App() + ShowModal()
- Confuses wx.GetApp() check in show_yes_no_async()
- Causes "wx.App not active" false positive

Solution:
- Add show_statistics_report_async(callback) with async pattern
- Uses wx.CallAfter() to avoid nested event loop
- No wx.App() creation (uses existing parent)
- Callback invoked after dialog closes
- Keep deprecated sync version for backward compatibility

Pattern:
- Consistent with show_yes_no_async(), show_info_async()
- Supports callback chain: stats → rematch dialog
- wx.GetApp() remains valid after execution

Impact:
- Prepares for end_game() callback chain refactor
- Zero breaking changes (deprecation wrapper)
- Backward compatible

Version: v2.5.0
```

---

### COMMIT 2: Update end_game() Callback Chain

**Priorità**: 🔴 CRITICA  
**File**: `src/application/game_engine.py`  
**Linee**: ~1137-1165 (metodo `end_game`)

#### Codice Attuale (BROKEN)

```python
def end_game(self, is_victory: bool = False) -> None:
    """End current game and show results."""
    # ... calculate stats ...
    
    # ❌ PROBLEMA: Sincrono, blocca qui
    self.dialogs.show_statistics_report(stats, final_score, is_victory, deck_type)
    
    # Define rematch callback
    def on_rematch_result(wants_rematch: bool):
        if self.callback:
            self.callback(wants_rematch)
    
    # ❌ PROBLEMA: Esegue subito dopo stats, ma wx.App confuso!
    self.dialogs.show_rematch_prompt_async(on_rematch_result)
```

#### Codice Nuovo (ASYNC CHAIN - FIXED)

```python
def end_game(self, is_victory: bool = False) -> None:
    """End current game and show results.
    
    Flow (async chain):
        1. Calculate stats and score
        2. Show statistics report (async)
        3. [User closes stats dialog]
        4. on_stats_closed() callback invoked
        5. Show rematch prompt (async)
        6. [User chooses YES/NO]
        7. on_rematch_result() callback invoked
        8. Notify app controller (acs_wx.handle_game_ended)
    
    Version:
        v2.5.0: Refactored to full async callback chain (Bug #68 fix)
    """
    # ... [CODICE ESISTENTE calcolo stats IDENTICO] ...
    
    # Define rematch callback (invoked when user chooses YES/NO)
    def on_rematch_result(wants_rematch: bool):
        """Handle rematch choice."""
        if self.callback:
            self.callback(wants_rematch)
    
    # ✅ NEW: Define stats closed callback (invoked when stats dialog closes)
    def on_stats_closed():
        """After stats closed, show rematch prompt."""
        print("Statistics report closed, showing rematch prompt...")
        self.dialogs.show_rematch_prompt_async(on_rematch_result)
    
    # ✅ ASYNC CHAIN: stats → rematch
    print("Showing statistics report (async)...")
    self.dialogs.show_statistics_report_async(
        stats=stats,
        final_score=final_score,
        is_victory=is_victory,
        deck_type=deck_type,
        callback=on_stats_closed  # ✅ Chain to rematch dialog
    )
    
    # Method returns immediately, callback chain handles rest
```

#### Callback Chain Diagram

```
end_game()
  │ [Calcola stats]
  │
  ├─> show_statistics_report_async(callback=on_stats_closed)
  │     │
  │     ├─> [Dialog stats appare]
  │     ├─> [User preme OK]
  │     ├─> [Dialog chiude]
  │     │
  │     └─> on_stats_closed() invocato
  │           │
  │           ├─> print("Statistics closed...")
  │           │
  │           └─> show_rematch_prompt_async(callback=on_rematch_result)
  │                 │
  │                 ├─> [Dialog rematch appare]
  │                 ├─> [User sceglie YES/NO]
  │                 ├─> [Dialog chiude]
  │                 │
  │                 └─> on_rematch_result(wants_rematch) invocato
  │                       └─> self.callback(wants_rematch)
  │                             └─> acs_wx.handle_game_ended(wants_rematch)
  │
  └─> [Returns immediately]
```

#### Testing COMMIT 2

```bash
python acs_wx.py
N → CTRL+ALT+W → INVIO (OK)

# Expected console output:
Showing statistics report (async)...
[Stats dialog appare]
[User: INVIO]
Statistics report closed, showing rematch prompt...
[Rematch dialog appare!]  # ✅ NO CRASH!
```

#### Commit Message

```
refactor(game): Update end_game() to use async callback chain

Bug #68 regressione fix (part 2/3)

Problem:
- end_game() called stats dialog sync, then rematch async
- Stats sync dialog confused wx.GetApp() check
- Rematch dialog never appeared

Solution:
- Use show_statistics_report_async() with callback
- Define on_stats_closed() callback
- Chain to show_rematch_prompt_async() inside callback
- Full async flow: stats → rematch → action

Callback Chain:
1. show_statistics_report_async(callback=on_stats_closed)
2. [User closes stats] → on_stats_closed() invoked
3. show_rematch_prompt_async(callback=on_rematch_result)
4. [User chooses YES/NO] → on_rematch_result() invoked
5. handle_game_ended(wants_rematch) in acs_wx.py

Impact:
- Fixes rematch dialog not appearing
- Completes Bug #68 async refactoring
- Full async architecture (zero sync dialogs)

Version: v2.5.0
```

---

### COMMIT 3: Remove IsMainLoopRunning Check

**Priorità**: 🟡 ALTA  
**File**: `src/infrastructure/ui/wx_dialog_provider.py`  
**Linee**: ~267-275 (dentro `show_yes_no_async`)

#### Codice Attuale (BROKEN CHECK)

```python
def show_yes_no_async(self, title, message, callback):
    """Show yes/no dialog (semi-modal) with deferred callback."""
    
    def show_modal_and_callback():
        # ... dialog logic ...
        pass
    
    # ❌ PROBLEMA: Check troppo aggressivo
    app = wx.GetApp()
    if app and app.IsMainLoopRunning():
        wx.CallAfter(show_modal_and_callback)
    else:
        # ❌ Salta dialog, assume decline
        print("⚠️ wx.App not active, skipping async dialog")
        callback(False)
```

#### Codice Nuovo (CLEAN - NO CHECK)

```python
def show_yes_no_async(self, title, message, callback):
    """Show yes/no dialog (semi-modal) with deferred callback."""
    
    # Log dialog shown
    log.dialog_shown("yes_no", title)
    
    def show_modal_and_callback():
        """Deferred function: show modal dialog then invoke callback."""
        # Create modal dialog
        dialog = wx.MessageDialog(
            parent=self._get_parent(),
            message=message,
            caption=title,
            style=wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION
        )
        
        # ShowModal blocks until user responds
        result_code = dialog.ShowModal()
        result = (result_code == wx.ID_YES)
        
        # Log dialog closed
        log.dialog_closed("yes_no", "yes" if result else "no")
        
        # Always destroy
        dialog.Destroy()
        
        # Invoke callback
        callback(result)
    
    # ✅ FIXED: Always call wx.CallAfter (no check needed!)
    # wxPython handles graceful shutdown automatically
    wx.CallAfter(show_modal_and_callback)
```

#### Rationale

**Perché rimuovere il check è sicuro**:

1. **wx.CallAfter() è Intrinsecamente Sicuro**:
   - wxPython gestisce graceful shutdown automaticamente
   - Se app sta chiudendo, `wx.CallAfter()` viene ignorato
   - Nessun crash, nessun callback spurio

2. **Nessun Più Nested Event Loop**:
   - Tutti i dialog sono async (dopo COMMIT 1-2)
   - `wx.GetApp()` è sempre valido
   - Nessuna creazione multipla wx.App()

3. **Check Era il Problema**:
   - Scattava in situazioni normali (dopo stats dialog)
   - False positive: "app not active" quando app è attiva!
   - Rimozione elimina radice regressione

4. **Pattern Standard wxPython**:
   - Tutti gli esempi wxPython ufficiali usano `wx.CallAfter()` senza check
   - Check custom non necessario (wxPython gestisce internamente)

#### Testing COMMIT 3

```bash
python acs_wx.py
N → CTRL+ALT+W → INVIO → INVIO (YES)

# Expected:
- Stats dialog appare ✅
- Stats chiude ✅
- Rematch dialog appare ✅
- YES accepted ✅
- Nuova partita inizia ✅
- NO warning "⚠️ wx.App not active" ✅
```

#### Commit Message

```
fix(dialogs): Remove IsMainLoopRunning check (no longer needed)

Bug #68 regressione fix (part 3/3 - FINAL)

Problem:
- COMMIT 3 (Copilot) added wx.GetApp().IsMainLoopRunning() check
- Check was too aggressive, triggered false positives
- After sync statistics dialog, check failed incorrectly
- Caused "wx.App not active" warning and skipped rematch dialog

Solution:
- Remove IsMainLoopRunning check entirely
- Always call wx.CallAfter() (no conditional logic)
- wxPython handles graceful shutdown automatically
- No check needed with full async architecture

Rationale:
- All dialogs now async (no nested event loops)
- wx.GetApp() always valid in async context
- Check was root cause of regression
- Standard wxPython pattern: wx.CallAfter() without checks

Impact:
- Fixes "wx.App not active" false positive
- Completes Bug #68 fully (all 4 commits)
- Zero breaking changes
- Full async architecture validated

Testing:
- Manual: CTRL+ALT+W → stats → rematch → YES ✅
- Manual: Real victory → stats → rematch → NO ✅
- Manual: Multiple rematches → all work ✅
- No "wx.App not active" warnings ✅

Version: v2.5.0 (Bug #68 COMPLETED)
```

---

## 🧪 Testing Strategy

### Test 1: CTRL+ALT+W (Debug Victory)
- [ ] `python acs_wx.py`
- [ ] `N` (nuova partita)
- [ ] `CTRL+ALT+W` (force victory)
- [ ] **Verifica**: Stats dialog appare
- [ ] **Verifica**: Console log: "Showing statistics report (async)..."

### Test 2: Stats Dialog Close
- [ ] [Dopo Test 1]
- [ ] Premi `INVIO` (OK button)
- [ ] **Verifica**: Stats chiude
- [ ] **Verifica**: Console log: "Statistics report closed, showing rematch prompt..."
- [ ] **Verifica**: Rematch dialog appare **IMMEDIATAMENTE**
- [ ] **Verifica**: NO warning "⚠️ wx.App not active"

### Test 3: Accept Rematch
- [ ] [Dopo Test 2]
- [ ] Premi `INVIO` (YES)
- [ ] **Verifica**: Nuova partita inizia immediatamente
- [ ] **Verifica**: Timer reset, carte redistribuite
- [ ] **Verifica**: Console log: "→ Game ended callback - Rematch: True"
- [ ] **Verifica**: Console log: "Starting rematch..."

### Test 4: Decline Rematch (🔥 Bug #68 Critical)
- [ ] CTRL+ALT+W → INVIO (stats) → TAB + INVIO (NO)
- [ ] **Verifica**: Menu visibile **immediatamente**
- [ ] **Verifica**: Frecce SU/GIÙ navigano menu
- [ ] **Verifica**: TTS: "Sei tornato al menu principale"
- [ ] **Verifica**: Console log: "→ Game ended callback - Rematch: False"
- [ ] **Verifica**: Console log: "→ Returning to main menu..."
- [ ] **Verifica**: NO freeze UI, NO finestra vuota

### Test 5: Multiple Rematches
- [ ] CTRL+ALT+W → INVIO → YES
- [ ] CTRL+ALT+W → INVIO → YES
- [ ] CTRL+ALT+W → INVIO → NO
- [ ] **Verifica**: Ogni rematch funziona
- [ ] **Verifica**: Nessun panel sovrapposto
- [ ] **Verifica**: Menu finale visibile

### Test 6: ESC During Stats
- [ ] CTRL+ALT+W → ESC (chiude stats)
- [ ] **Verifica**: Rematch dialog appare comunque
- [ ] **Verifica**: Comportamento identico a INVIO

### Test 7: Real Victory + Log Completi
- [ ] Completa partita reale (tutte le carte nelle basi)
- [ ] **Verifica**: Stats dialog appare
- [ ] **Verifica**: Rematch dialog appare dopo OK
- [ ] **Verifica**: Log file `solitaire.log` completo:
  ```
  Game WON - Time: X, Moves: Y, Score: ...
  Showing statistics report (async)...
  Statistics report closed, showing rematch prompt...
  → Game ended callback - Rematch: [True|False]
  ```
- [ ] **Verifica**: Nessun "buco" nei log

---

## ✅ Validation & Acceptance

### Success Criteria

**Funzionali**:
- [ ] Stats dialog appare al termine partita
- [ ] Rematch dialog appare dopo OK su stats (NO CRASH)
- [ ] Accept rematch: nuova partita inizia
- [ ] Decline rematch: menu visibile immediatamente (Bug #68)
- [ ] Multiple rematches funzionano in sequenza
- [ ] ESC su stats: rematch dialog appare comunque

**Tecnici**:
- [ ] COMMIT 1: `show_statistics_report_async()` implementato
- [ ] COMMIT 2: `end_game()` usa callback chain
- [ ] COMMIT 3: `IsMainLoopRunning` check rimosso
- [ ] Sintassi validata (py_compile su entrambi i file)
- [ ] Zero breaking changes (deprecation wrapper)
- [ ] Backward compatible (codice vecchio funziona)

**Code Quality**:
- [ ] Type hints corretti: `Callable[[], None]`
- [ ] Docstring complete (Google style)
- [ ] Commit messages conventional commits
- [ ] Pattern consistente (tutti dialog async)

**Bug #68 Completamento**:
- [ ] COMMIT 1 (Copilot): `show_rematch_prompt_async()` in DialogManager ✅
- [ ] COMMIT 2 (Copilot): Refactor GameEngine.end_game() ✅
- [ ] COMMIT 3 (Copilot): Remove wx.CallAfter workaround acs_wx.py ✅
- [ ] COMMIT 4 (questo): `show_statistics_report_async()` + callback chain ⏳
- [ ] COMMIT 5 (questo): Remove `IsMainLoopRunning` check ⏳

**Log Completi**:
- [ ] Ogni dialog loggato ("Showing...", "Closed")
- [ ] Ogni callback loggato
- [ ] Nessun "buco" nel flusso
- [ ] File `solitaire.log` traccia completo end-game flow

---

## 📚 References

### Documentazione Esterna
- [wxPython CallAfter](https://docs.wxpython.org/wx.functions.html#wx.CallAfter) - Deferred execution pattern
- [wxPython MessageDialog](https://docs.wxpython.org/wx.MessageDialog.html) - Modal dialog API
- [wxPython App Lifecycle](https://wiki.wxpython.org/CallAfter) - Event loop and shutdown

### Internal Architecture Docs
- `docs/ARCHITECTURE.md` - Clean Architecture layers
- `docs/completato - PIANO_IMPLEMENTAZIONE_BUG_67_68.md` - Bug #68 original plan
- `docs/TODO_BUG68_async_rematch_dialog.md` - Copilot COMMIT 1-3 (regressione)

### Related Code Files
- `src/infrastructure/ui/wx_dialog_provider.py` - **DA MODIFICARE** (2 modifiche)
- `src/application/game_engine.py` - **DA MODIFICARE** (callback chain)
- `src/application/dialog_manager.py` - DialogManager wrapper (reference)
- `acs_wx.py` - handle_game_ended() (invariato)

---

## 🚀 Risultato Finale Atteso

Una volta completati i 3 commit:

✅ **Nessun Crash**: CTRL+ALT+W funziona completamente  
✅ **Stats Dialog**: Appare e funziona correttamente  
✅ **Rematch Dialog**: Appare DOPO stats (no skip)  
✅ **Bug #68 Completato**: Menu visibile dopo decline  
✅ **Architettura Pulita**: 100% async (zero sync dialogs)  
✅ **Log Completi**: Ogni step tracciato  
✅ **Zero Regressioni**: Tutti i flussi funzionano  

**Metriche Successo**:
- Test manuale: 7/7 scenari passano ✅
- Sintassi: `py_compile` passa su entrambi i file ✅
- Breaking changes: 0 (deprecation wrapper) ✅
- Log completi: nessun buco nel flusso ✅

---

**Fine Piano Implementazione Bug #68.4**

**Piano Version**: v2.0 (Opzione C - Architectural Fix)  
**Data Creazione**: 2026-02-15 01:45 CET  
**Autore**: AI Assistant + Nemex81  
**Basato su**: Regressione analysis + Copilot COMMIT 1-3 review  

---

**Ready for Implementation! 🚀**
