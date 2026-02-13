📋 TODO – Fix Panel Swap Crash with wx.CallAfter Deferred Execution (v2.0.3)
Branch: copilot/remove-pygame-migrate-wxpython
Tipo: FIX (CRITICAL)
Priorità: P0 – HIGH (Blocks release)
Stato: READY

📖 Riferimento Documentazione
Prima di iniziare qualsiasi implementazione, consultare obbligatoriamente:
**docs/FIX_PANEL_SWAP_CRASH_DURING_EVENT_HANDLING.md**

Questo file TODO è solo un sommario operativo da consultare e aggiornare durante ogni fase dell'implementazione.
Il piano completo contiene:
- Analisi comparativa con hs_deckmanager (pattern funzionante)
- Root cause analysis (nested event loop + SafeYield crash)
- Implementazione dettagliata con BEFORE/AFTER code examples
- 10 test cases completi (4 automated + 4 regression + 2 stress)
- Edge cases e architettura tecnica completa

🎯 Obiettivo Implementazione
Breve descrizione in 3–5 righe:

• **Problema**: App crasha/chiude quando si preme ESC durante gameplay per tornare al menu. Crash avviene dentro `view_manager.show_panel()` a causa di panel swap durante event handling.

• **Root Cause**: `wx.SafeYield()` viene chiamato dentro nested event loop (ESC handler → modal dialog → SafeYield), causando stack overflow e crash wxPython.

• **Soluzione**: Usare `wx.CallAfter()` per deferire tutte le UI transitions DOPO che l'event handler completa. Nessun panel swap durante event handling = nessun nested event loop = nessun crash.

• **Impatto**: -125 linee di codice, 3 nuovi metodi deferred, fix completo per 3 scenari (ESC abandon, decline rematch, timeout strict).

📂 File Coinvolti
• `test.py` (lines 196-642) → **MODIFY** (4 metodi esistenti + 3 nuovi metodi deferred)
  - `show_abandon_game_dialog()` → Add wx.CallAfter() defer
  - `handle_game_ended()` → Add wx.CallAfter() defer (both branches)
  - `_handle_game_over_by_timeout()` → Add wx.CallAfter() defer
  - `return_to_menu()` → Simplify (remove diagnostics)
  - `_safe_abandon_to_menu()` → **CREATE** (new deferred method)
  - `_safe_decline_to_menu()` → **CREATE** (new deferred method)
  - `_safe_timeout_to_menu()` → **CREATE** (new deferred method)

• `src/infrastructure/ui/view_manager.py` → **NO CHANGES** (SafeYield già presente)
• `src/infrastructure/ui/gameplay_panel.py` → **NO CHANGES** (event handler corretto)
• `CHANGELOG.md` → **UPDATE** (add v2.0.3 release notes)
• `README.md` → **NO CHANGES** (fix interno, UX invariata)

🛠 Checklist Implementazione

### Logica / Dominio
- [ ] **NESSUNA MODIFICA** (fix è UI-layer only, domain intatto)

### Application / Controller
- [ ] Modificato `show_abandon_game_dialog()` con defer pattern
  - [ ] Rimosso manual `gameplay_panel.Hide()` (Step 1/4)
  - [ ] Rimosso manual `engine.reset_game()` (Step 2/4) 
  - [ ] Rimosso manual `return_to_menu()` sync call (Step 3/4)
  - [ ] Aggiunto `wx.CallAfter(self._safe_abandon_to_menu)`
  - [ ] Creato nuovo metodo `_safe_abandon_to_menu()` con 3 steps
  - [ ] Aggiornato docstring con defer pattern explanation

- [ ] Modificato `handle_game_ended()` con defer pattern
  - [ ] Rimosso 4-step manual transition (decline branch)
  - [ ] Aggiunto `wx.CallAfter(self._safe_decline_to_menu)` (decline)
  - [ ] Aggiunto `wx.CallAfter(self.start_gameplay)` (rematch)
  - [ ] Creato nuovo metodo `_safe_decline_to_menu()` 
  - [ ] Aggiornato docstring

- [ ] Modificato `_handle_game_over_by_timeout()` con defer pattern
  - [ ] Rimosso 4-step manual transition
  - [ ] Aggiunto `wx.CallAfter(self._safe_timeout_to_menu)`
  - [ ] Creato nuovo metodo `_safe_timeout_to_menu()` con 3 steps
  - [ ] Aggiornato docstring

- [ ] Semplificato `return_to_menu()` 
  - [ ] Rimosso ~50 linee di diagnostica verbosa
  - [ ] Mantenuto solo: check ViewManager, show_panel(), set flag, TTS
  - [ ] Aggiornato docstring con defer pattern examples
  - [ ] Aggiunto CORRECT/WRONG usage examples in docstring

- [ ] **VERIFICATO**: Nessuna violazione Clean Architecture
  - [ ] Domain layer intatto
  - [ ] Fix isolato in presentation/infrastructure
  - [ ] Nessun accoppiamento UI → Domain

### Infrastructure (se applicabile)
- [ ] **NO CHANGES** a `view_manager.py` (SafeYield corretto, non è lui il problema)
- [ ] **NO CHANGES** a `gameplay_panel.py` (event handler corretto)
- [ ] **NO CHANGES** a dialog manager (funziona correttamente)

### Presentation / Accessibilità
- [ ] **INVARIATO**: Messaggi TTS identici (nessuna modifica UX)
- [ ] **INVARIATO**: Comandi tastiera identici
- [ ] **VERIFICATO**: Nessuna informazione solo visiva aggiunta
- [ ] **VERIFICATO**: Defer non impatta latenza percepita (CallAfter è immediato)

### Testing

#### Automated Tests (4 scenari critici)
- [ ] **Test #1: ESC Abandon Game**
  - [ ] Start game → Press ESC → Confirm "Sì"
  - [ ] ✅ Game resets, timer stops, menu shows
  - [ ] ✅ TTS announces "Ritorno al menu di gioco"
  - [ ] ✅ NO crash, NO app close
  - [ ] Verificato log: "ABANDON GAME: Safe deferred transition"

- [ ] **Test #2: Victory - Decline Rematch**
  - [ ] Win game → Rematch dialog → Click "No"
  - [ ] ✅ Victory stats shown, game resets, menu shows
  - [ ] ✅ NO crash, NO app close
  - [ ] Verificato log: "[DECLINE] Safe deferred transition"

- [ ] **Test #3: Victory - Accept Rematch**
  - [ ] Win game → Rematch dialog → Click "Sì"
  - [ ] ✅ New game starts immediately
  - [ ] ✅ Gameplay panel stays visible
  - [ ] ✅ Cards dealt, timer resets
  - [ ] ✅ NO crash, NO app close

- [ ] **Test #4: Timeout Defeat (Strict Mode)**
  - [ ] Enable strict timer (settings.timer_strict_mode = True)
  - [ ] Set short timer (e.g., 60 seconds)
  - [ ] Wait for timeout (do NOT complete game)
  - [ ] ✅ Defeat message + stats via TTS
  - [ ] ✅ Game resets automatically, menu shows
  - [ ] ✅ NO crash, NO app close
  - [ ] Verificato log: "[TIMEOUT] Safe deferred transition"

#### Regression Tests (4 scenari base)
- [ ] **RT #1: Menu Navigation**
  - [ ] Launch app → Menu shows
  - [ ] Arrow keys navigate correctly
  - [ ] ENTER activates each option
  - [ ] ✅ All menu options work

- [ ] **RT #2: Gameplay Commands**
  - [ ] Start new game
  - [ ] Test: Arrows (navigate), ENTER (move), SPACE (flip), D (draw)
  - [ ] Test: H (help), O (game state), 1-7 (pile navigation)
  - [ ] ✅ All 80+ commands work correctly

- [ ] **RT #3: Options Window**
  - [ ] Open Opzioni from menu
  - [ ] Modify settings (timer, draw mode, etc.)
  - [ ] Save with "Salva" button
  - [ ] Close with ESC (smart ESC test)
  - [ ] ✅ Settings save correctly

- [ ] **RT #4: Exit Flows**
  - [ ] Test: Menu ESC → Exit dialog → Confirm
  - [ ] Test: Menu "Esci" button → Exit dialog → Confirm  
  - [ ] Test: ALT+F4 → Exit dialog → Confirm
  - [ ] ✅ All exit methods work, no crashes

#### Stress Tests (2 scenari edge)
- [ ] **ST #1: Rapid ESC Spam**
  - [ ] Start game
  - [ ] Press ESC 10 times rapidly
  - [ ] Confirm all dialogs quickly
  - [ ] ✅ No crashes, proper cleanup each time
  - [ ] ✅ No memory leaks (check Task Manager)

- [ ] **ST #2: Panel Swap Loop** 
  - [ ] Menu → Nuova Partita → ESC confirm → Menu (repeat 20x)
  - [ ] ✅ No crashes after 20 iterations
  - [ ] ✅ Consistent behavior each time
  - [ ] ✅ No performance degradation

✅ Criteri di Completamento
L'implementazione è considerata completa quando:

- [ ] **CODICE**:
  - [ ] Tutte le 4 modifiche implementate correttamente
  - [ ] 3 nuovi metodi deferred creati con docstrings complete
  - [ ] return_to_menu() semplificato (~50 linee rimosse)
  - [ ] Nessun warning/errore di import o syntax

- [ ] **TESTING**:
  - [ ] Tutti e 4 gli Automated Tests passano
  - [ ] Tutti e 4 i Regression Tests passano  
  - [ ] Entrambi gli Stress Tests passano
  - [ ] Log verification conferma defer pattern execution
  - [ ] Nessuna regressione rilevata su 80+ comandi gameplay

- [ ] **DOCUMENTAZIONE**:
  - [ ] CHANGELOG.md aggiornato con v2.0.3 release notes
  - [ ] Version string in test.py aggiornata ("v2.0.3")
  - [ ] Questo TODO marcato come DONE
  - [ ] Piano completo marcato come COMPLETED (filename)

- [ ] **QUALITY CHECKS**:
  - [ ] Codice segue convenzioni esistenti
  - [ ] Docstrings complete per tutti i nuovi metodi
  - [ ] Nessuna violazione Clean Architecture
  - [ ] -125 linee nette (semplificazione confermata)

📝 Aggiornamenti Obbligatori a Fine Implementazione

• [ ] **CHANGELOG.md**:
  ```markdown
  ## [2.0.3] - 2026-02-14
  
  ### Fixed
  - **CRITICAL**: Panel swap crash during event handling (ESC abandon, decline rematch, timeout)
    - Root cause: Nested event loop (modal dialog + wx.SafeYield() inside event handler)
    - Solution: Deferred execution with wx.CallAfter() pattern
    - Impact: All UI transitions now happen outside event handling (safe)
    - Files: test.py (3 new deferred methods, 4 methods refactored)
    - Code quality: -125 lines (simpler, safer, maintainable)
    - Tests: 10 test cases pass (4 automated + 4 regression + 2 stress)
  ```

• [ ] **README.md**: NO CHANGES (fix interno, UX invariata)

• [ ] **Versione**: Aggiornare in test.py docstring:
  ```python
  Version: v2.0.3 (CRITICAL bugfix - panel swap crash)
  ```

• [ ] **Commit Message** (Conventional Commits):
  ```
  fix(ui): prevent panel swap crash with deferred execution pattern
  
  Replace synchronous panel transitions with wx.CallAfter() deferred
  execution to prevent crashes during event handling.
  
  Root Cause:
  - Panel swap during wxPython event handling causes undefined behavior
  - Modal dialogs create nested event loops
  - wx.SafeYield() inside nested loop triggers stack overflow
  - Second Hide() on already-hidden panel closes frame
  
  Solution:
  - Defer all UI transitions with wx.CallAfter()
  - Event handler completes first
  - Transition executes after event stack clears
  - No panel swap during event handling
  
  Changes:
  - show_abandon_game_dialog(): Added wx.CallAfter() defer
  - handle_game_ended(): Added wx.CallAfter() for both branches
  - _handle_game_over_by_timeout(): Added wx.CallAfter() defer
  - return_to_menu(): Simplified (removed diagnostics)
  - New: _safe_abandon_to_menu(), _safe_decline_to_menu(), _safe_timeout_to_menu()
  
  Testing:
  ✅ ESC abandon game → No crash → Menu shown
  ✅ Decline rematch → No crash → Menu shown
  ✅ Timeout strict mode → No crash → Menu shown
  ✅ All 80+ gameplay commands work
  ✅ All regression tests pass
  ✅ Stress tests pass (rapid ESC spam, 20x panel swap loop)
  
  Impact:
  - BREAKING: None (internal fix only)
  - API: No changes to public interfaces
  - Behavior: Same UX, crash-free now
  - Performance: Negligible (deferred execution overhead minimal)
  - Code: -125 lines (simpler, safer)
  
  Version: v2.0.3 (critical bugfix)
  Closes: Panel swap crash during event handling
  Ref: docs/FIX_PANEL_SWAP_CRASH_DURING_EVENT_HANDLING.md
  
  Co-authored-by: Nemex81 <68394029+Nemex81@users.noreply.github.com>
  ```

• [ ] **Push**: 
  ```bash
  git add test.py CHANGELOG.md docs/TODO_FIX_PANEL_SWAP_CRASH_WX_CALLAFTER.md
  git commit -m "fix(ui): prevent panel swap crash with deferred execution pattern"
  git push origin copilot/remove-pygame-migrate-wxpython
  ```

• [ ] **Post-Implementation**:
  - [ ] Rinominare `docs/FIX_PANEL_SWAP_CRASH_DURING_EVENT_HANDLING.md` → `completed-FIX_PANEL_SWAP_CRASH_DURING_EVENT_HANDLING.md`
  - [ ] Marcare questo TODO come DONE
  - [ ] Aggiornare branch status (se merge to main)

📌 Note Operative

**Pattern wx.CallAfter() - Reminder Rapido**:
```python
# ❌ BEFORE (crashes)
def show_dialog(self):
    result = dialog.ShowModal()  # Nested event loop
    if result:
        self.return_to_menu()  # Panel swap during event handling → CRASH

# ✅ AFTER (safe)
def show_dialog(self):
    result = dialog.ShowModal()
    if result:
        wx.CallAfter(self._deferred_transition)  # Defer to after event handler

def _deferred_transition(self):
    # Executes OUTSIDE event handler (safe)
    self.engine.reset()
    self.return_to_menu()  # Panel swap safe now
```

**Debugging Tips**:
- Se crash persiste: verificare che TUTTI i path che chiamano `return_to_menu()` usino defer
- Se UI non risponde: verificare che defer non blocchi event loop (CallAfter è non-blocking)
- Se test falliscono: verificare log per "Safe deferred transition" (conferma defer execution)

**Critical Files**:
- `test.py` lines 196-642 → TUTTE le modifiche qui
- `view_manager.py` lines 131-179 → NO CHANGES (SafeYield è OK)
- `gameplay_panel.py` lines 85-98 → NO CHANGES (event handler è OK)

**Expected Outcome**:
- Code: -180 lines removed, +55 lines added = **-125 lines nette**
- Tests: **10/10 pass** (100% success rate)
- Crashes: **0** (ESC abandon, decline rematch, timeout strict)
- UX: **Identical** (nessuna percezione del defer da parte utente)

---

**Fine TODO**

Questo è il cruscotto operativo. Per analisi tecnica completa, edge cases, e architettura dettagliata:
→ **docs/FIX_PANEL_SWAP_CRASH_DURING_EVENT_HANDLING.md** (31KB, 800+ lines)

Implementazione stimata: **1-2 ore** (4 metodi modificati + 3 nuovi metodi + testing completo)
Risk level: **LOW** (soluzione proven, pattern standard wxPython)
Success probability: **95%+** (root cause identificato con certezza)
