# TODO: Fix Debug Victory Command (CTRL+ALT+W)

**Status**: 🔴 IN PROGRESS  
**Branch**: `copilot/implement-victory-flow-dialogs`  
**Priority**: HIGH (blocca testing victory flow)  
**Estimated Time**: 15 minutes

---

## 📋 Problem Statement

### Current Behavior (BROKEN)
Premendo **CTRL+ALT+W** durante una partita:
- ✅ Il comando viene riconosciuto
- ✅ TTS annuncia "Vittoria simulata attivata!"
- ❌ Il dialog wxPython **NON viene mostrato**
- ❌ La partita **NON viene resettata**
- ❌ Il report statistiche **NON viene generato**

### Root Cause
**File**: `src/application/game_engine.py`  
**Metodo**: `_debug_force_victory()` (linea ~1238)

```python
def _debug_force_victory(self) -> str:
    if not self.is_game_running():
        return "Nessuna partita in corso da simulare!"
    
    # ❌ BUG: Questo setta is_game_running = False PRIMA di end_game()
    self.service.is_game_running = False  # <-- PROBLEMA QUI!
    
    # Trigger complete victory flow
    self.end_game(is_victory=True)  # <-- Fallisce perché gioco già fermato
    
    return "Vittoria simulata attivata! Report finale in arrivo."
```

**Perché fallisce**:
1. `_debug_force_victory()` setta manualmente `self.service.is_game_running = False`
2. `end_game()` chiama `self.service._snapshot_statistics()` che si aspetta `is_game_running = True`
3. `_snapshot_statistics()` ferma il timer e congela le statistiche **solo se** il gioco è running
4. Risultato: statistiche vuote/errate → report non generato → dialog non mostrato

### Expected Behavior (FIXED)
Premendo **CTRL+ALT+W** durante una partita:
- ✅ Il comando viene riconosciuto
- ✅ `end_game()` viene chiamato con `is_victory=True`
- ✅ `_snapshot_statistics()` ferma il timer e congela statistiche
- ✅ Report completo viene generato (tempo, mosse, semi)
- ✅ TTS annuncia il report statistiche
- ✅ wxDialog mostra report + prompt "Vuoi giocare ancora?"
- ✅ Se "Sì" → nuova partita, se "No" → reset game state

---

## 🎯 Implementation Plan

### STEP 1: Fix `_debug_force_victory()` Method (5 min)
**File**: `src/application/game_engine.py`
**Location**: Linea ~1238-1248

**Action**: Rimuovere manipolazione manuale di `is_game_running`

#### PRIMA (Buggy Code)
```python
def _debug_force_victory(self) -> str:
    """🔥 DEBUG ONLY: Simulate victory for testing end_game flow.
    
    Keyboard binding: CTRL+ALT+W
    
    ⚠️ WARNING: This is a debug feature for testing the victory flow!
    
    Simulates victory without actually completing the game.
    Useful for testing:
    - Final report formatting
    - Dialog appearance and accessibility
    - Score calculation accuracy
    - Rematch flow behavior
    - Suit statistics display
    
    Returns:
        Confirmation message for TTS announcement
        
    Example:
        >>> msg = engine._debug_force_victory()
        >>> print(msg)
        "Vittoria simulata attivata! Report finale in arrivo."
        
        # TTS announces victory report
        # Dialog shows full statistics
        # Prompts for rematch
    """
    if not self.is_game_running():
        return "Nessuna partita in corso da simulare!"
    
    # ❌ BUG: Stop game timer (preserves elapsed_time)
    self.service.is_game_running = False  # <-- RIMUOVERE QUESTA RIGA!
    
    # Trigger complete victory flow
    self.end_game(is_victory=True)
    
    return "Vittoria simulata attivata! Report finale in arrivo."
```

#### DOPO (Fixed Code)
```python
def _debug_force_victory(self) -> str:
    """🔥 DEBUG ONLY: Simulate victory for testing end_game flow.
    
    Keyboard binding: CTRL+ALT+W
    
    ⚠️ WARNING: This is a debug feature for testing the victory flow!
    
    Simulates victory without actually completing the game.
    Useful for testing:
    - Final report formatting
    - Dialog appearance and accessibility
    - Score calculation accuracy
    - Rematch flow behavior
    - Suit statistics display
    
    Returns:
        Confirmation message for TTS announcement
        
    Example:
        >>> msg = engine._debug_force_victory()
        >>> print(msg)
        "Vittoria simulata attivata! Report finale in arrivo."
        
        # TTS announces victory report
        # Dialog shows full statistics
        # Prompts for rematch
    """
    if not self.is_game_running():
        return "Nessuna partita in corso da simulare!"
    
    # ✅ FIX: Let end_game() handle timer stop via _snapshot_statistics()
    # Trigger complete victory flow
    self.end_game(is_victory=True)
    
    return "Vittoria simulata attivata! Report finale in arrivo."
```

**Razionale**:
- `end_game()` chiama internamente `self.service._snapshot_statistics()`
- `_snapshot_statistics()` ferma il timer **correttamente** e congela le statistiche
- Non dobbiamo manipolare manualmente `is_game_running`
- Delega la responsabilità al metodo progettato per questo (Single Responsibility Principle)

---

### STEP 2: Verify Flow in `end_game()` (2 min)
**File**: `src/application/game_engine.py`
**Location**: Linea ~1070-1150

**Action**: Conferma che `end_game()` gestisce correttamente il flusso

#### Checklist di Verifica
- [ ] `end_game()` chiama `self.service._snapshot_statistics()` (STEP 1)
- [ ] `_snapshot_statistics()` ferma il timer se `is_game_running == True`
- [ ] Statistiche finali vengono congelate in `self.service._final_stats`
- [ ] Report viene generato da `ReportFormatter.format_final_report()`
- [ ] TTS annuncia il report (sempre)
- [ ] wxDialog mostra report (se `self.dialogs` disponibile)
- [ ] Prompt rematch via `self.dialogs.show_yes_no()` (se `self.dialogs` disponibile)
- [ ] Reset game state se rematch rifiutato

**NO CODE CHANGES NEEDED** - Solo verifica che il flusso sia completo.

---

### STEP 3: Testing Manual (5 min)
**Platform**: Windows con NVDA (se disponibile) o TTS generico

#### Test Scenario 1: Debug Victory con wxDialogs Enabled
**Precondizioni**:
- `use_native_dialogs=True` in `test.py`
- Partita in corso (qualche mossa eseguita)
- Timer attivo (tempo trascorso > 0)

**Passi**:
1. Avvia partita: `python test.py`
2. Esegui 2-3 mosse (seleziona/sposta carte)
3. Premi **CTRL+ALT+W**

**Expected Results**:
- [ ] TTS annuncia: "Vittoria simulata attivata! Report finale in arrivo."
- [ ] TTS legge report completo (tempo, mosse, semi)
- [ ] wxDialog mostra report testuale con statistiche
- [ ] wxDialog mostra prompt "Vuoi giocare ancora?" con bottoni Sì/No/ESC
- [ ] Premendo "Sì" → nuova partita inizia
- [ ] Premendo "No" → gioco torna a stato iniziale
- [ ] Premendo "ESC" → gioco torna a stato iniziale

#### Test Scenario 2: Debug Victory SENZA wxDialogs (Fallback)
**Precondizioni**:
- `use_native_dialogs=False` in `test.py` (o wxPython non installato)
- Partita in corso

**Passi**:
1. Avvia partita: `python test.py`
2. Esegui 2-3 mosse
3. Premi **CTRL+ALT+W**

**Expected Results**:
- [ ] TTS annuncia: "Vittoria simulata attivata! Report finale in arrivo."
- [ ] TTS legge report completo (tempo, mosse, semi)
- [ ] Nessun dialog grafico (fallback mode)
- [ ] Game state viene resettato automaticamente
- [ ] Partita pronta per nuovo gioco

#### Test Scenario 3: Debug Victory SENZA Partita Attiva
**Precondizioni**:
- Nessuna partita in corso (main menu)

**Passi**:
1. Avvia app: `python test.py`
2. Resta nel menu principale
3. Premi **CTRL+ALT+W**

**Expected Results**:
- [ ] TTS annuncia: "Nessuna partita in corso da simulare!"
- [ ] Nessun dialog mostrato
- [ ] Menu principale resta attivo

#### Test Scenario 4: NVDA Accessibility (SOLO SE WINDOWS)
**Precondizioni**:
- Windows con NVDA attivo
- wxDialogs enabled
- Partita in corso

**Passi**:
1. Avvia partita con NVDA attivo
2. Esegui 2-3 mosse
3. Premi **CTRL+ALT+W**
4. Quando dialog appare, usa TAB per navigare

**Expected Results**:
- [ ] NVDA legge titolo dialog: "Congratulazioni!"
- [ ] NVDA legge contenuto report (tempo, mosse, semi)
- [ ] NVDA annuncia focus su bottone "Sì" (default)
- [ ] TAB naviga tra bottoni: Sì → No → ESC
- [ ] NVDA annuncia ogni bottone al focus
- [ ] Shortcut keys funzionano: S (Sì), N (No), ESC (Annulla)

---

## ✅ Acceptance Criteria

### Functional Requirements (4/4)
- [ ] CTRL+ALT+W durante partita → `end_game()` viene chiamato
- [ ] Report completo viene generato (tempo, mosse, semi)
- [ ] wxDialog mostra report + rematch prompt (se dialogs disponibili)
- [ ] Game state viene resettato correttamente (dopo rematch rifiutato)

### Code Quality (3/3)
- [ ] Nessuna manipolazione manuale di `is_game_running` in `_debug_force_victory()`
- [ ] Delega completa a `end_game()` per gestione flusso vittoria
- [ ] Commento esplicativo nel codice sul perché NON manipolare `is_game_running`

### Testing (4/4)
- [ ] Scenario 1 (wxDialogs enabled) testato e passato
- [ ] Scenario 2 (fallback mode) testato e passato
- [ ] Scenario 3 (nessuna partita) testato e passato
- [ ] Scenario 4 (NVDA accessibility) testato se disponibile

---

## 📝 Commit Message Template

```
fix: debug victory command now triggers complete end_game flow

- Removed manual is_game_running manipulation in _debug_force_victory()
- Let end_game() handle timer stop via _snapshot_statistics()
- Fixes issue where CTRL+ALT+W would not show dialog or reset game
- Debug command now properly tests complete victory flow:
  * Statistics snapshot with timer stop
  * Report generation with suit details
  * wxDialog display with rematch prompt
  * Correct game state reset

Root cause: Setting is_game_running=False before end_game() 
blocked _snapshot_statistics() from capturing final stats.

Tested:
- Scenario 1: wxDialogs enabled ✓
- Scenario 2: Fallback mode (no wxPython) ✓
- Scenario 3: No active game ✓
- Scenario 4: NVDA accessibility ✓ (if Windows available)

Refs: PR #57, TODO_FIX_DEBUG_VICTORY_COMMAND.md
```

---

## 🔍 Verification Checklist (Post-Implementation)

### Code Review
- [ ] `_debug_force_victory()` NON manipola `is_game_running`
- [ ] `_debug_force_victory()` chiama solo `self.end_game(is_victory=True)`
- [ ] Commento esplicativo aggiunto sul perché delegare a `end_game()`
- [ ] Nessuna altra modifica necessaria (bugfix minimale)

### Manual Testing
- [ ] Test Scenario 1: PASSED
- [ ] Test Scenario 2: PASSED
- [ ] Test Scenario 3: PASSED
- [ ] Test Scenario 4: PASSED (se Windows + NVDA)

### Regression Testing
- [ ] Vittoria reale (completando 4 semi) funziona normalmente
- [ ] Dialog rematch funziona (Sì/No/ESC)
- [ ] Reset game state dopo vittoria/sconfitta corretto
- [ ] Nessun altro comando debug impattato

---

## 📚 Related Documentation

- **Planning**: `docs/PLAN_WX_DIALOGS_INTEGRATION_v1.6.1.md`
- **Original TODO**: `docs/TODO_WX_DIALOGS_INTEGRATION_v1.6.1.md`
- **PR**: #57 "Implement wxDialogs for all interactive contexts"
- **Victory Flow Docs**: `docs/TODO_VICTORY_FLOW_DIALOGS.md` (completed in v1.6.0)

---

## 🎯 Summary for Copilot

**Quick Fix**:
1. Apri `src/application/game_engine.py`
2. Vai al metodo `_debug_force_victory()` (linea ~1238)
3. Rimuovi questa riga: `self.service.is_game_running = False`
4. Aggiungi commento esplicativo:
   ```python
   # ✅ FIX: Let end_game() handle timer stop via _snapshot_statistics()
   ```
5. Commit con messaggio template sopra
6. Testa con CTRL+ALT+W durante partita
7. Verifica che dialog wxPython appare con report completo

**Tempo totale stimato**: 15 minuti (5 min fix + 5 min test + 5 min commit/push)

---

**🚀 Ready for Copilot Implementation!**
