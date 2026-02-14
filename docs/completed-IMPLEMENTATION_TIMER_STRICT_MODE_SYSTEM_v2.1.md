# Implementazione Sistema Timer Strict Mode - Guida per GitHub Copilot

## Metadata Documento
- **Versione Target**: 2.1
- **Branch**: `copilot/remove-pygame-migrate-wxpython`
- **Autore**: Assistente AI
- **Data Creazione**: 2026-02-14
- **Scopo**: Guidare GitHub Copilot nell'implementazione sistemica del pattern Timer Strict Mode

---

## 📋 Panoramica Implementazione

Questo documento guida l'implementazione di un **sistema robusto e consistente** per la gestione della scadenza del timer in modalità STRICT. L'obiettivo è integrare a livello architetturale il pattern già implementato con successo nella versione 2.0.9 (uso di `self.app.CallAfter()` per transizioni UI differite).

### Principi Architetturali

1. **Dependency on wx.App Instance**: Tutte le transizioni UI differite DEVONO usare `self.app.CallAfter()` invece di `wx.CallAfter()`
2. **Event Handler Pattern**: Separazione completa tra event handlers sincri e callback differiti
3. **Clean Transitions**: Hide → Reset → Show pattern per panel swaps
4. **Single Responsibility**: Ogni metodo ha una responsabilità chiara (handler O callback, mai entrambi)

### Contesto Tecnico

**Problema Risolto nella v2.0.9**:
```python
# ❌ PRIMA (v2.0.4-2.0.8): causava AssertionError/PyNoAppError
wx.CallAfter(func)  # Dipende da wx.App.Get() globale

# ✅ DOPO (v2.0.9): funziona sempre
self.app.CallAfter(func)  # Usa istanza diretta dell'app
```

**Root Cause Originale**:
- `wx.CallAfter()` chiama internamente `wx.GetApp()` che può ritornare `None` durante certi stati del ciclo di vita dell'app
- `self.app.CallAfter()` è una chiamata diretta al metodo dell'istanza, nessuna lookup globale necessaria

---

## 🎯 Obiettivi Implementazione

### Obiettivo Primario
Integrare il pattern `self.app.CallAfter()` in **TUTTI** i punti del codice dove vengono eseguite transizioni UI differite, garantendo coerenza architetturale e prevenendo regressioni future.

### Obiettivi Specifici

1. **Audit Completo del Codice**
   - Identificare TUTTI gli usi di `wx.CallAfter()` nel codebase
   - Verificare se sono legati a transizioni UI o altri meccanismi

2. **Refactoring Pattern**
   - Sostituire `wx.CallAfter(method)` con `self.app.CallAfter(method)` dove applicabile
   - Documentare ogni sostituzione con commenti inline esplicativi

3. **Validazione Architetturale**
   - Verificare che TUTTE le transizioni panel usino il pattern corretto
   - Controllare consistency nei metodi di deferred execution

4. **Documentazione Aggiornata**
   - Aggiornare docstrings con version history (v2.1)
   - Creare/aggiornare file di documentazione tecnica

---

## 📂 File da Modificare (Priorità)

### 🔴 Priorità CRITICA

#### 1. `test.py` (Main Application Controller)

**Contesto**: File principale che gestisce event loop wxPython e tutte le transizioni UI.

**Metodi Target** (già corretti nella v2.0.9, verificare consistency):
```python
# Line ~372
def show_abandon_game_dialog(self):
    # ... dialog logic ...
    # ✅ Già corretto in v2.0.9
    self.app.CallAfter(self._safe_abandon_to_menu)

# Line ~504
def handle_game_ended(self, is_victory: bool):
    # ... victory logic ...
    if rematch_accepted:
        # ✅ Già corretto in v2.0.9
        self.app.CallAfter(self.start_gameplay)
    else:
        # ✅ Già corretto in v2.0.9
        self.app.CallAfter(self._safe_decline_to_menu)

# Line ~677
def _handle_game_over_by_timeout(self):
    # ✅ Già corretto in v2.0.9
    self.app.CallAfter(self._safe_timeout_to_menu)
```

**Azioni Richieste**:
1. ✅ Verificare che TUTTE le istanze siano `self.app.CallAfter()` (non `wx.CallAfter()`)
2. ✅ Controllare che non ci siano altri metodi con transizioni UI differite
3. ✅ Aggiungere commenti header che spiegano il pattern:
   ```python
   # CRITICAL PATTERN (v2.0.9): Use self.app.CallAfter() for deferred UI transitions
   # Reason: wx.CallAfter() depends on wx.GetApp() which can return None during app lifecycle
   # Direct instance method call ensures app availability: self.app (Python object) always exists
   ```

4. ✅ Aggiornare docstrings dei metodi deferred (`_safe_*_to_menu`) con version history:
   ```python
   """
   ...existing docstring...
   
   Version History:
   - v2.0.3: Initial implementation with panel swap logic
   - v2.0.4: Added deferred execution via wx.CallAfter()
   - v2.0.6: Changed to self.frame.CallAfter()
   - v2.0.7: Reverted to wx.CallAfter() for backward compatibility
   - v2.0.9: DEFINITIVE FIX - self.app.CallAfter() for reliability
   - v2.1: Architectural integration and consistency validation
   """
   ```

#### 2. `src/infrastructure/ui/view_manager.py`

**Contesto**: Manager per panel swaps, usa `wx.SafeYield()` che fu RIMOSSO nella v2.0.8.

**Verifica Necessaria**:
1. ✅ Controllare che `wx.SafeYield()` NON sia presente nel metodo `show_panel()`
2. ✅ Verificare commenti inline che spiegano perché NON usare SafeYield:
   ```python
   # NO wx.SafeYield() - Hide() and Show() are synchronous C++ operations!
   # SafeYield() was added in v2.0.3 but caused RuntimeError (nested event loop)
   # Removed in v2.0.8 - unnecessary and harmful
   ```

3. ✅ Se SafeYield presente, rimuoverlo e documentare nel commit

**Azioni Richieste**:
- Audit completo di `view_manager.py`
- Verificare che non ci siano pattern anti-pattern legacy
- Aggiornare docstring del metodo `show_panel()` con note architetturali

#### 3. `src/application/gameplay_controller.py`

**Contesto**: Controller che potrebbe avere logica di transizioni UI.

**Verifica Necessaria**:
1. Search per `wx.CallAfter` nel file
2. Se presente, verificare contesto d'uso:
   - È una transizione UI? → Sostituire con `self.app.CallAfter()`
   - È altro meccanismo? → Valutare caso per caso

**Azioni Richieste**:
- Audit completo del file
- Documentare ogni istanza trovata
- Applicare pattern consistency se necessario

### 🟡 Priorità MEDIA

#### 4. Altri file in `src/application/`

**File Candidati**:
- `options_controller.py`
- `dialog_manager.py`
- `game_engine.py`

**Verifica Necessaria**:
- Search globale per `wx.CallAfter` o `CallAfter`
- Identificare contesti d'uso
- Applicare pattern se legato a transizioni UI

#### 5. File in `src/infrastructure/ui/`

**File Candidati**:
- `wx_frame.py`
- `wx_app.py`
- Altri componenti UI

**Verifica Necessaria**:
- Audit per pattern deferred execution
- Verificare consistency con architectural guidelines

### 🟢 Priorità BASSA

#### 6. Test Files

**Contesto**: Unit/integration tests potrebbero mockare wx.CallAfter.

**Azioni Richieste**:
- Verificare che i test non dipendano da `wx.CallAfter()` globale
- Aggiornare mock se necessario per `self.app.CallAfter()`

---

## 🔧 Pattern di Implementazione

### Pattern 1: Event Handler → Deferred Callback

**Template**:
```python
def on_user_action(self):
    """
    Event handler per azione utente che richiede transizione UI.
    
    CRITICAL: Usa self.app.CallAfter() per deferire UI transition.
    
    Flow:
    1. User action → Event handler (questo metodo)
    2. Dialog/Validation logic (sincrona)
    3. self.app.CallAfter(deferred_callback) → Schedula transizione
    4. Return → Event handler completa
    5. [wxPython idle loop] → Esegue deferred_callback
    6. Deferred callback → Panel swap (safe, nessun nested event loop)
    
    Version: v2.1
    """
    # Step 1: Validazione/Dialog (sincrono)
    if not self._validate_action():
        return
    
    # Step 2: Deferire transizione UI
    # CRITICAL: self.app.CallAfter (NOT wx.CallAfter) per reliability
    self.app.CallAfter(self._deferred_transition_callback)
    
    # Step 3: Return immediatamente (event handler completa)
    # Transizione verrà eseguita DOPO da wx idle loop

def _deferred_transition_callback(self):
    """
    Callback differito per transizione UI sicura.
    
    Eseguito da wx idle loop DOPO che event handler è completato.
    Nessun rischio di nested event loops.
    
    Version: v2.1
    """
    # Step 1: Hide current panel
    self.view_manager.show_panel('menu')  # Handles hide/show internally
    
    # Step 2: Reset state
    self.engine.reset_game()
    
    # Step 3: Clear flags
    self._reset_internal_state()
```

### Pattern 2: Timer Expiration → Deferred Transition

**Template**:
```python
def _check_timer_expiration(self):
    """
    Controllo periodico scadenza timer (chiamato da wx.Timer).
    
    CRITICAL: Se timer scaduto in STRICT mode, deferire transizione menu.
    
    Version: v2.1
    """
    if not self._is_timer_expired():
        return
    
    if self.settings.timer_strict_mode:
        # STRICT: Termina partita immediatamente
        # CRITICAL: Usa self.app.CallAfter per deferred transition
        self.app.CallAfter(self._handle_game_over_by_timeout)
    else:
        # PERMISSIVE: Annuncia e continua (no transition)
        self._announce_overtime_penalty()

def _handle_game_over_by_timeout(self):
    """
    Handler differito per game over da timeout STRICT.
    
    Eseguito da wx idle loop, safe per panel transitions.
    
    Flow:
    1. Hide gameplay panel
    2. Reset engine state
    3. Show menu panel
    4. Reset timer flags
    
    Version: v2.1
    """
    # Clean transition pattern: Hide → Reset → Show
    self.view_manager.show_panel('menu')
    self.engine.reset_game()
    self._timer_expired_announced = False
```

### Pattern 3: Victory/Defeat → Conditional Deferred Transition

**Template**:
```python
def handle_game_ended(self, is_victory: bool):
    """
    Handler sincono per fine partita (vittoria o sconfitta).
    
    Dialog rematch è MODAL (blocking), transizione è DEFERRED.
    
    Version: v2.1
    """
    # Step 1: Calcola statistiche (sincrono)
    stats = self.engine.calculate_final_stats()
    
    # Step 2: Mostra dialog rematch (MODAL, blocking)
    rematch = self.dialog_manager.show_yes_no(
        "Vuoi giocare ancora?",
        "Rematch"
    )
    
    # Step 3: Deferire transizione appropriata
    if rematch:
        # CRITICAL: self.app.CallAfter per deferred new game
        self.app.CallAfter(self.start_gameplay)
    else:
        # CRITICAL: self.app.CallAfter per deferred menu return
        self.app.CallAfter(self._safe_decline_to_menu)
```

---

## 📝 Commit Strategy (Incrementale e Atomica)

### Commit 1: Audit e Documentazione
**Scope**: Identificazione completa pattern esistenti

**File Modificati**: Nessuno (solo analisi)

**Deliverable**:
- Report completo istanze `wx.CallAfter()` nel codebase
- Categorizzazione per contesto d'uso (UI transitions vs altro)
- Identification di inconsistenze

**Commit Message**:
```
docs(v2.1): Audit complete codebase for wx.CallAfter usage patterns

- Identified all instances of wx.CallAfter() vs self.app.CallAfter()
- Categorized by context: UI transitions, event callbacks, timers
- Documented inconsistencies for systematic refactoring
- No code changes in this commit (audit only)
```

### Commit 2: Refactoring test.py (Main Controller)
**Scope**: Consistency check e documentazione main controller

**File Modificati**: `test.py`

**Modifiche**:
1. Verifica che TUTTE le transizioni usino `self.app.CallAfter()`
2. Aggiungi commenti header pattern-explaining
3. Aggiorna docstrings metodi deferred con version history
4. NO LOGIC CHANGES (solo documentazione)

**Commit Message**:
```
refactor(v2.1): Validate and document deferred UI pattern in test.py

- Verified all UI transitions use self.app.CallAfter() (v2.0.9 pattern)
- Added architectural comments explaining pattern rationale
- Updated docstrings with complete version history (v2.0.3 → v2.1)
- No behavioral changes (documentation only)

Affected methods:
- show_abandon_game_dialog()
- handle_game_ended()
- _handle_game_over_by_timeout()
- _safe_abandon_to_menu()
- _safe_decline_to_menu()
- _safe_timeout_to_menu()
```

### Commit 3: Refactoring view_manager.py
**Scope**: Verifica assenza anti-patterns legacy

**File Modificati**: `src/infrastructure/ui/view_manager.py`

**Modifiche**:
1. Verifica assenza `wx.SafeYield()` (rimosso in v2.0.8)
2. Aggiungi/aggiorna commenti inline
3. Aggiorna docstring `show_panel()` con note architetturali
4. NO LOGIC CHANGES

**Commit Message**:
```
refactor(v2.1): Validate ViewManager panel swap pattern consistency

- Confirmed wx.SafeYield() removal (v2.0.8 fix maintained)
- Added inline comments explaining synchronous Hide/Show operations
- Updated show_panel() docstring with architectural notes
- No behavioral changes (documentation only)

Pattern validated:
- Hide() and Show() are synchronous C++ operations (immediate)
- No SafeYield needed (causes nested event loop crashes)
- Panel swaps safe when called from deferred callbacks
```

### Commit 4: Audit Application Layer
**Scope**: Verifica consistency in tutti i controller

**File Modificati**: 
- `src/application/gameplay_controller.py`
- `src/application/options_controller.py`
- Altri se trovati pattern inconsistenti

**Modifiche**:
1. Search globale `wx.CallAfter` in application layer
2. Se trovato in contesto UI transition → Sostituire con `self.app.CallAfter()`
3. Se trovato in altro contesto → Documentare e valutare
4. Aggiungere commenti esplicativi

**Commit Message**:
```
refactor(v2.1): Ensure deferred UI pattern consistency in application layer

- Audited all application controllers for wx.CallAfter usage
- [IF FOUND] Replaced wx.CallAfter with self.app.CallAfter in UI contexts
- [IF NOT FOUND] Confirmed no UI transitions in application layer
- Added architectural comments where applicable

Files audited:
- gameplay_controller.py
- options_controller.py
- game_engine.py
- [altri se applicabile]
```

### Commit 5: Documentazione Architetturale
**Scope**: Aggiornamento documentazione tecnica globale

**File Modificati**:
- `docs/ARCHITECTURE.md` (se esiste, altrimenti creare)
- `README.md` (sezione tecnica)
- Questo documento (`IMPLEMENTATION_TIMER_STRICT_MODE_SYSTEM_v2.1.md`)

**Modifiche**:
1. Creare/aggiornare sezione "Deferred UI Transitions Pattern"
2. Documentare decision tree: quando usare `self.app.CallAfter()`
3. Esempi best practices e anti-patterns
4. Link a version history relevant

**Commit Message**:
```
docs(v2.1): Add architectural documentation for deferred UI pattern

- Created comprehensive guide for self.app.CallAfter() pattern
- Documented decision tree and best practices
- Added anti-patterns section (wx.CallAfter, wx.SafeYield)
- Updated ARCHITECTURE.md with complete pattern rationale

New sections:
- "Deferred UI Transitions Pattern" in ARCHITECTURE.md
- "Common Anti-Patterns to Avoid" with examples
- Complete version history (v2.0.3 → v2.1 evolution)
```

### Commit 6: Aggiornamento CHANGELOG e README
**Scope**: Finalizzazione rilascio v2.1

**File Modificati**:
- `CHANGELOG.md`
- `README.md`

**Modifiche**:
1. Aggiungere sezione completa v2.1 in CHANGELOG
2. Includere tutti i commit precedenti con dettagli
3. Aggiornare README con note versione corrente

**Commit Message**:
```
chore(release): Prepare v2.1 - Timer Strict Mode system integration

- Updated CHANGELOG.md with complete v2.1 release notes
- Documented all architectural improvements and consistency checks
- Updated README.md version references
- Incremented version number to 2.1

Release highlights:
- Systematic integration of deferred UI pattern (self.app.CallAfter)
- Complete architectural documentation and consistency validation
- Zero breaking changes (internal refactoring only)
- Enhanced code maintainability and reliability
```

---

## ✅ Checklist Validazione Finale

### Pre-Commit Validation

Prima di OGNI commit, verificare:

- [ ] **Sintassi**: Nessun errore Python syntax
- [ ] **Import**: Tutti gli import necessari presenti
- [ ] **Type Hints**: Type hints corretti e completi
- [ ] **Docstrings**: Docstrings aggiornati con version history
- [ ] **Commenti**: Commenti inline chiari e informativi
- [ ] **Consistency**: Pattern applicato uniformemente
- [ ] **No Breaking Changes**: Comportamento identico a v2.0.9
- [ ] **Manual Testing**: Test manuali su scenari critici

### Post-Commit Validation

Dopo ogni commit, verificare:

- [ ] **Build Success**: Nessun errore durante import
- [ ] **Regression Tests**: Test esistenti passano
- [ ] **Manual Testing**: Scenari critici funzionano
  - [ ] ESC abandon game → Menu transition
  - [ ] Victory decline rematch → Menu transition
  - [ ] Timer STRICT expiration → Menu transition
- [ ] **Log Review**: Nessun warning/error nei log

### Final Release Validation (v2.1)

Prima del merge finale:

- [ ] **Complete Audit**: Tutti i file critici verificati
- [ ] **Documentation Complete**: Tutti i documenti aggiornati
- [ ] **CHANGELOG Updated**: v2.1 entry completa e dettagliata
- [ ] **README Updated**: Versione corrente documentata
- [ ] **No Regressions**: Zero breaking changes confermato
- [ ] **Manual Test Suite**: Tutti gli scenari critici testati
  - [ ] Tutte le transizioni UI differite funzionano
  - [ ] Nessun crash/hang con transizioni multiple
  - [ ] Timer STRICT/PERMISSIVE comportamenti corretti
  - [ ] Dialog interactions non causano nested loops

---

## 🚨 Common Pitfalls da Evitare

### Pitfall 1: Usare wx.CallAfter() invece di self.app.CallAfter()

**Sintomo**: AssertionError o PyNoAppError durante transizioni UI

**Soluzione**:
```python
# ❌ WRONG
wx.CallAfter(self._safe_abandon_to_menu)

# ✅ CORRECT
self.app.CallAfter(self._safe_abandon_to_menu)
```

### Pitfall 2: Aggiungere wx.SafeYield() in show_panel()

**Sintomo**: RuntimeError "wxYield called recursively"

**Soluzione**:
```python
# ❌ WRONG - Causes nested event loop
def show_panel(self, name):
    wx.SafeYield()  # DON'T DO THIS
    panel.Hide()
    panel.Show()

# ✅ CORRECT - No SafeYield needed
def show_panel(self, name):
    # Hide() and Show() are synchronous C++ operations
    panel.Hide()
    panel.Show()
```

### Pitfall 3: Chiamare panel swap direttamente da event handler

**Sintomo**: Nested event loops, hang app, crash random

**Soluzione**:
```python
# ❌ WRONG - Direct panel swap from event handler
def on_esc_pressed(self):
    self.view_manager.show_panel('menu')  # BAD: synchronous call

# ✅ CORRECT - Deferred panel swap
def on_esc_pressed(self):
    self.app.CallAfter(self._safe_return_to_menu)  # GOOD: deferred
```

### Pitfall 4: Dimenticare di resettare state prima di show_panel

**Sintomo**: State inconsistencies, carte residue, timer attivo

**Soluzione**:
```python
# ❌ WRONG - Show panel before reset
def _safe_return_to_menu(self):
    self.view_manager.show_panel('menu')
    self.engine.reset_game()  # TOO LATE

# ✅ CORRECT - Hide → Reset → Show pattern
def _safe_return_to_menu(self):
    # Step 1: Hide current panel
    self.view_manager.show_panel('menu')  # Handles hide internally
    
    # Step 2: Reset state (panel already hidden, safe)
    self.engine.reset_game()
    
    # Step 3: Clear flags
    self._timer_expired_announced = False
```

---

## 📚 Riferimenti Tecnici

### Documentazione wxPython Rilevante

- [wx.App.CallAfter()](https://docs.wxpython.org/wx.App.html#wx.App.CallAfter): Instance method, sempre disponibile
- [wx.CallAfter()](https://docs.wxpython.org/wx.functions.html#wx.CallAfter): Global function, dipende da wx.GetApp()
- [wx.SafeYield()](https://docs.wxpython.org/wx.functions.html#wx.SafeYield): **AVOID** - causes nested event loops

### File di Documentazione Correlati

- `docs/ARCHITECTURE.md`: Architettura generale applicazione
- `docs/FIX_DEFERRED_TRANSITIONS_FRAME_CALLAFTER.md`: Storia v2.0.3 → v2.0.9
- `README.md`: Overview progetto e versioni

### Commit History Rilevante

- v2.0.3: Aggiunto wx.SafeYield() (errore, poi rimosso)
- v2.0.4: Introdotto wx.CallAfter() per deferred execution
- v2.0.6: Cambiato a self.frame.CallAfter()
- v2.0.7: Revertito a wx.CallAfter() (backward compatibility)
- v2.0.8: Rimosso wx.SafeYield() (causa crash)
- v2.0.9: **DEFINITIVE FIX** - self.app.CallAfter()
- v2.1: **Integrazione sistemica e validazione consistency**

---

## 🎯 Obiettivi di Successo (Definition of Done)

### Successo Tecnico

- ✅ **Zero istanze di `wx.CallAfter()` in contesti UI transition**
- ✅ **Tutte le transizioni UI usano `self.app.CallAfter()`**
- ✅ **Nessun `wx.SafeYield()` nel codebase**
- ✅ **Documentazione completa e aggiornata**
- ✅ **Consistency verificata in tutti i layer**

### Successo Funzionale

- ✅ **Tutte le transizioni UI funzionano senza crash**
- ✅ **Nessun hang o nested event loop**
- ✅ **Timer STRICT mode termina partita correttamente**
- ✅ **ESC abandon game funziona in tutti i contesti**
- ✅ **Victory/Defeat rematch flow robusto**

### Successo Qualitativo

- ✅ **Codice più leggibile e manutenibile**
- ✅ **Pattern architetturale chiaro e consistente**
- ✅ **Commenti inline esplicativi ovunque**
- ✅ **Docstrings complete con version history**
- ✅ **Documentazione tecnica accessibile**

---

## 🤖 Note per GitHub Copilot Agent

### Comportamento Richiesto

1. **Leggi TUTTO questo documento** prima di iniziare qualsiasi modifica
2. **Segui la commit strategy esattamente** (6 commit atomici incrementali)
3. **NON fare modifiche comportamentali** - solo refactoring e documentazione
4. **Testa manualmente OGNI commit** prima di procedere al successivo
5. **Documenta OGNI modifica** con commenti inline chiari

### Domande da Porti Prima di Modificare

- ❓ Questo è un contesto UI transition?
- ❓ Sto usando `self.app.CallAfter()` invece di `wx.CallAfter()`?
- ❓ Ho aggiunto commenti inline esplicativi?
- ❓ Ho aggiornato il docstring con version history?
- ❓ Questa modifica rompe backward compatibility?

### In Caso di Dubbio

- **STOP** - Non procedere se non sei sicuro
- **ASK** - Chiedi conferma all'utente prima di modifiche ambigue
- **DOCUMENT** - Se fai qualcosa di non standard, documenta perché

---

## 📦 Deliverable Finale

Alla fine dell'implementazione v2.1, dovresti consegnare:

1. **6 commit atomici** seguendo esattamente la strategy descritta
2. **CHANGELOG.md aggiornato** con entry completa v2.1
3. **README.md aggiornato** con versione corrente
4. **Documentazione tecnica completa** in `docs/`
5. **Zero breaking changes** - comportamento identico a v2.0.9
6. **Test manuali passati** su tutti gli scenari critici

---

## ✨ Reminder Finale

> **L'obiettivo NON è aggiungere nuove funzionalità, ma consolidare e documentare il pattern esistente per garantire manutenibilità futura e prevenire regressioni.**

**Versione Target**: 2.1 (NON 3.0)  
**Branch**: `copilot/remove-pygame-migrate-wxpython`  
**Tipo Release**: MINOR (refactoring interno, no breaking changes)

---

Al termine della prima lettura di qeusto documento, copilot dovrà impegnarsi nella creazione di unfile todo, che funga come sommario delle mdoifiche richeiste inquesto documento. salva il file sempr enella cartella docs e utilizza il file exaple TODO.md come modello di creazione per il file richeisto.
Dopo la creazione di questo file copilot potrà impegnarsi nella codifica delelmodficmdelel modifiche richeiste cominciando con ilconsultare proprio ilfikel todo appena creato. nel file todo specifica di seguire rigorosamente questo file di documentazione in ogni fase dell'implementazione. L'implementazioen deve procedere in modo incrementale su più commit.
**Fine Documento**
