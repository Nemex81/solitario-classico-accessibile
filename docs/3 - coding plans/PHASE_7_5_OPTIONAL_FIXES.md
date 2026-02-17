# 🔧 PHASE 7.5: Optional Fixes (Post-Integration Polish)

**Status**: ⏸️ Skipped by Copilot Agent  
**Priority**: MEDIUM (2 fix raccomandati) + LOW (2 fix nice-to-have)  
**Estimated Time**: 30-45 minuti (4 fix totali)  
**Branch**: `copilot/implement-profile-system-v3-1-0`  
**Prerequisiti**: Phase 7 completata ✅ (GameEngine integration)

---

## 📋 Cross-References Documentazione

**Questo documento è parte dello stack di implementazione Feature 3:**

- **Piano generale**: [`IMPLEMENTATION_STATS_PRESENTATION.md`](IMPLEMENTATION_STATS_PRESENTATION.md) - Phase 7 overview
- **TODO operativo**: [`../../TODO.md`](../../TODO.md) - Feature 3 tracking (Phase 7 completata, Phase 9 mancante)
- **Phase 9 menu**: [`PHASE_9_MENU_INTEGRATION_UPDATED.md`](PHASE_9_MENU_INTEGRATION_UPDATED.md) - Prossima implementazione (45 min)

**Workflow suggerito**:
```
Phase 7 ✅ → Phase 7.5 ⚡ (questo doc, 12 min critici) → Phase 9 📋 (45 min) → MERGE ✅
```

---

## 🎯 Obiettivo Phase 7.5

Applicare **4 fix opzionali** che Copilot ha saltato durante Phase 7 (GameEngine integration):

1. ✅ **RACCOMANDATO** - Fix 7.5.2: Typo `ABANDON_CRASH` (2 min) - **TRIVIALE**
2. ✅ **RACCOMANDATO** - Fix 7.5.3: Timer expiry verification (10 min) - **POTENZIALE BUG**
3. ⏸️ Nice-to-have - Fix 7.5.1: Semantic logging helpers (15 min) - **DEV UX**
4. ⏸️ Nice-to-have - Fix 7.5.4: App startup recovery (5 min) - **FEATURE GIÀ FUNZIONANTE**

**Strategia consigliata**: Implementare **solo Fix 7.5.2 + 7.5.3** (12 min totali) insieme a Phase 9 per evitare bug. Gli altri 2 fix possono essere Issue GitHub separato post-merge.

---

## 📊 Priorità Fix (Tabella Decisionale)

| Fix | Impatto | Criticità | Tempo | Implementare ORA? | Motivo |
|-----|---------|-----------|-------|-------------------|--------|
| **7.5.2 - Typo** | Low | Nice-to-have | 2 min | ✅ **SÌ** | Triviale, rimuove TODO |
| **7.5.3 - Timer** | **MEDIUM** | **Should-have** | 10 min | ✅ **SÌ** | Potenziale bug silente |
| 7.5.1 - Logging | Low | Nice-to-have | 15 min | ⏸️ OPZIONALE | Solo dev experience |
| 7.5.4 - Recovery | Low | Nice-to-have | 5 min | ⏸️ OPZIONALE | Feature già funziona |

**Tempo critico ORA**: 12 minuti (Fix 7.5.2 + 7.5.3)  
**Tempo totale con Phase 9**: 12 min + 45 min = **~57 minuti** (stack completo Feature 3)

---

## ✅ FIX 7.5.2: Typo ABANDON_CRASH → ABANDON_APP_CLOSE (2 min)

### 🎯 Obiettivo

Rimuovere TODO obsoleto e usare il nome corretto dell'EndReason già definito.

### 🐛 Problema Rilevato

**File**: `src/application/game_engine.py` (linea ~703)

**Codice attuale**:
```python
# In end_game() o metodo simile
# TODO: usa ABANDON_CRASH quando implementato
end_reason = EndReason.ABANDON_NEW_GAME  # Placeholder generico
```

**Problema**: `ABANDON_CRASH` non esiste. L'enum corretto è `ABANDON_APP_CLOSE` (definito in `EndReason` enum da Phase 1).

### ✅ Soluzione

**File**: `src/application/game_engine.py` (MODIFIED)

**Cerca pattern**:
```python
grep -n "TODO.*ABANDON_CRASH" src/application/game_engine.py
grep -n "ABANDON.*CRASH" src/application/game_engine.py
```

**Replace**:
```python
# PRIMA (linea ~703):
# TODO: usa ABANDON_CRASH quando implementato
end_reason = EndReason.ABANDON_NEW_GAME

# DOPO:
end_reason = EndReason.ABANDON_APP_CLOSE
```

**Context**: Questo fix si applica al caso di **app closed during game** (dirty shutdown). SessionTracker rileva sessioni orfane e le marca come `ABANDON_APP_CLOSE` (recovery logic già implementato in Phase 7).

### 📝 Commit Message

```
fix(game-engine): Replace ABANDON_CRASH with correct EndReason name [Phase 7.5.2]

- Remove TODO obsoleto (ABANDON_CRASH non esiste)
- Use EndReason.ABANDON_APP_CLOSE (defined in Phase 1)
- Applies to dirty shutdown case (app closed during game)
- No functional change (logic già corretto, solo naming)

Refs: PHASE_7_5_OPTIONAL_FIXES.md Fix 7.5.2
```

### ⏱️ Tempo Stimato
**2 minuti** (search + replace + commit)

---

## 🔍 FIX 7.5.3: Timer Expiry Logic Verification (10 min)

### 🎯 Obiettivo

Verificare che `on_timer_tick()` chiami correttamente `end_game()` quando timer scade in **STRICT mode**.

### ⚠️ Problema Potenziale

**File**: `src/application/game_engine.py` (metodo `on_timer_tick()`)

**Scenario critico**: Se timer scade in STRICT mode ma `end_game()` **non viene chiamato**, il gioco continua indefinitamente (bug silente).

**Già implementato in Phase 4** (Timer System), ma Copilot potrebbe aver saltato il hook in GameEngine durante Phase 7 integration.

### 🔎 Verifica da Eseguire

**File**: `src/application/game_engine.py`

**Cerca metodo** `on_timer_tick()`:
```python
def on_timer_tick(self, event):
    """Called every second during active game."""
    if not self.game_active:
        return
    
    # Update elapsed time display
    elapsed = self.game_service.get_elapsed_time()
    self._update_timer_display(elapsed)
    
    # CHECK: Esiste questa logica? ↓
    if self.game_service.is_timer_expired():
        if self.game_settings.timer_mode == TimerMode.STRICT:
            # CRITICO: Deve chiamare end_game() qui!
            self.end_game(EndReason.TIMEOUT_STRICT)
            return
        elif self.game_settings.timer_mode == TimerMode.PERMISSIVE:
            # PERMISSIVE: track overtime ma continua gioco
            # (già implementato in GameService.is_overtime())
            pass
```

### ✅ Implementazione Corretta

**Se logica MANCANTE**, aggiungere:

```python
def on_timer_tick(self, event):
    """Handle timer tick during active game."""
    if not self.game_active:
        return
    
    # Update display
    elapsed = self.game_service.get_elapsed_time()
    self._update_timer_display(elapsed)
    
    # Timer expiry check (STRICT mode auto-stop)
    if self.game_service.is_timer_expired():
        timer_mode = self.game_settings.timer_mode
        
        if timer_mode == TimerMode.STRICT:
            # Auto-stop game on timeout
            logger.info(f"Timer expired in STRICT mode - auto-stopping game")
            self.end_game(EndReason.TIMEOUT_STRICT)
            return
        elif timer_mode == TimerMode.PERMISSIVE:
            # Overtime mode: just track, don't stop
            if not self._overtime_announced:
                # Single TTS announcement
                self._announce_overtime()
                self._overtime_announced = True
```

**Inoltre, verificare che `_overtime_announced` sia inizializzato in `new_game()`**:
```python
def new_game(self, ...):
    # ... existing init ...
    self._overtime_announced = False  # Reset overtime flag
    # ... rest of game init ...
```

### 🧪 Test da Eseguire

**Test manuale** (5 min):
1. Avvia partita con **timer 00:30 STRICT**
2. Aspetta scadenza timer (30 sec)
3. **Verifica**: Gioco si ferma automaticamente? ✅
4. **Verifica**: Dialog abbandono mostra `TIMEOUT_STRICT`? ✅
5. **Verifica**: ProfileService registra sconfitta? ✅

**Se test fallisce** → Fix necessario (implementazione sopra).

### 📝 Commit Message

```
fix(game-engine): Verify and fix timer expiry auto-stop in STRICT mode [Phase 7.5.3]

- Add timer expiry check in on_timer_tick()
- STRICT mode: auto-stop game with TIMEOUT_STRICT reason
- PERMISSIVE mode: announce overtime once, continue game
- Reset _overtime_announced flag in new_game()
- Tested: Manual timer expiry test (30 sec STRICT)

Refs: PHASE_7_5_OPTIONAL_FIXES.md Fix 7.5.3
Refs: IMPLEMENTATION_TIMER_SYSTEM.md Phase 4 (original logic)
```

### ⏱️ Tempo Stimato
**10 minuti** (verifica codice + eventuale fix + test manuale)

---

## 📋 FIX 7.5.1: Semantic Logging Helpers (15 min) - OPZIONALE

### 🎯 Obiettivo

Creare helper class `ProfileLogger` con metodi semantic per logging profilo/sessioni (migliora developer experience).

### ⏸️ Priority: Nice-to-have

**Impatto**: Solo developer experience (codice funziona già senza questo fix).  
**Motivo**: Logging attuale usa `logger.info()` generico, ma metodi semantic rendono log più leggibili.

### ✅ Implementazione

**File NUOVO**: `src/infrastructure/logging/profile_logger.py`

```python
"""Semantic logging helpers for profile operations."""

import logging
from typing import Optional
from datetime import datetime

from src.domain.models.profile import UserProfile, SessionOutcome

logger = logging.getLogger(__name__)


class ProfileLogger:
    """Semantic logging for profile/session events."""
    
    @staticmethod
    def log_profile_created(profile_name: str) -> None:
        """Log profile creation."""
        logger.info(f"[PROFILE] Created new profile: '{profile_name}'")
    
    @staticmethod
    def log_profile_loaded(profile_name: str) -> None:
        """Log profile loaded from storage."""
        logger.info(f"[PROFILE] Loaded profile: '{profile_name}'")
    
    @staticmethod
    def log_profile_switched(from_name: str, to_name: str) -> None:
        """Log profile switch."""
        logger.info(f"[PROFILE] Switched: '{from_name}' → '{to_name}'")
    
    @staticmethod
    def log_session_recorded(
        profile_name: str,
        outcome: SessionOutcome,
        new_winrate: float
    ) -> None:
        """Log session recorded in profile."""
        result = "Victory" if outcome.is_victory else "Defeat"
        logger.info(
            f"[SESSION] Recorded {result} for '{profile_name}' | "
            f"Time: {outcome.elapsed_time:.1f}s | "
            f"New winrate: {new_winrate:.1%}"
        )
    
    @staticmethod
    def log_recovery_performed(profile_name: str, orphaned_count: int) -> None:
        """Log session recovery on startup."""
        logger.warning(
            f"[RECOVERY] Recovered {orphaned_count} orphaned sessions "
            f"for profile '{profile_name}'"
        )
    
    @staticmethod
    def log_storage_error(operation: str, error: Exception) -> None:
        """Log storage operation error."""
        logger.error(f"[STORAGE] Failed to {operation}: {error}", exc_info=True)
```

**Integrare in ProfileService** (`src/domain/services/profile_service.py`):

```python
from src.infrastructure.logging.profile_logger import ProfileLogger

class ProfileService:
    def create_profile(self, profile_name: str) -> UserProfile:
        profile = UserProfile(profile_name=profile_name)
        self.storage.save_profile(profile)
        ProfileLogger.log_profile_created(profile_name)  # ADD THIS
        return profile
    
    def record_session(self, outcome: SessionOutcome) -> None:
        # ... existing logic ...
        ProfileLogger.log_session_recorded(  # ADD THIS
            self.active_profile.profile_name,
            outcome,
            self.global_stats.winrate
        )
```

### 📝 Commit Message

```
feat(infrastructure): Add semantic logging helpers for profile operations [Phase 7.5.1]

- Create ProfileLogger class with semantic methods
- log_profile_created(), log_session_recorded(), etc.
- Integrate in ProfileService methods
- Improves log readability for debugging
- No functional changes (dev UX improvement)

Refs: PHASE_7_5_OPTIONAL_FIXES.md Fix 7.5.1
```

### ⏱️ Tempo Stimato
**15 minuti** (create logger + integrate in ProfileService)

---

## 🔄 FIX 7.5.4: App Startup Recovery Call (5 min) - OPZIONALE

### 🎯 Obiettivo

Aggiungere chiamata recovery check all'avvio app (mostra dialog se sessioni orfane rilevate).

### ⏸️ Priority: Nice-to-have

**Impatto**: Low (SessionTracker recovery già funziona in background).  
**Motivo**: Dialog recovery opzionale, non critico per funzionalità base.

### ⚠️ Nota Importante

**SessionTracker recovery è già implementato** in Phase 7 (commit a93f1dd). Il fix 7.5.4 aggiunge solo **UI dialog** per notificare utente.

**Recovery attuale** (automatico in background):
```python
# In ProfileService.__init__() o simile
orphaned = session_tracker.get_orphaned_sessions()
for session in orphaned:
    # Marca come ABANDON_APP_CLOSE e aggiungi a stats
    session_tracker.mark_recovered(session.session_id)
```

**Fix proposto**: Aggiungere **dialog notifica** all'utente.

### ✅ Implementazione

**File**: `acs_wx.py` (main entry point) o `src/application/game_engine.py` (`__init__()`)

**Cerca metodo startup** (es. `on_startup()`, `__init__()`, `OnInit()`).

**Aggiungere recovery check**:

```python
class GameApp(wx.App):  # O classe principale
    def OnInit(self):
        # ... existing init logic ...
        
        # Check for orphaned sessions (app crashed last time)
        self._check_session_recovery()
        
        return True
    
    def _check_session_recovery(self):
        """Check and recover orphaned sessions on startup."""
        if not hasattr(self, 'game_engine') or not self.game_engine.profile_service:
            return
        
        session_tracker = self.game_engine.profile_service.session_tracker
        orphaned = session_tracker.get_orphaned_sessions()
        
        if orphaned:
            # Show recovery dialog
            count = len(orphaned)
            message = (
                f"Rilevate {count} sessioni di gioco non completate "
                f"(chiusura imprevista app).\\n\\n"
                f"Le sessioni saranno recuperate automaticamente e "
                f"marchiate come abbandono."
            )
            
            wx.MessageBox(
                message,
                "Recupero Sessioni",
                wx.OK | wx.ICON_INFORMATION
            )
            
            # Logging
            from src.infrastructure.logging.profile_logger import ProfileLogger
            ProfileLogger.log_recovery_performed(
                self.game_engine.profile_service.active_profile.profile_name,
                count
            )
```

### 📝 Commit Message

```
feat(app): Add startup recovery dialog for orphaned sessions [Phase 7.5.4]

- Check orphaned sessions on app startup
- Show info dialog if recovery needed
- Log recovery event with ProfileLogger
- Recovery logic already implemented (Phase 7), this adds UI notification

Refs: PHASE_7_5_OPTIONAL_FIXES.md Fix 7.5.4
Refs: IMPLEMENTATION_PROFILE_SYSTEM.md Phase 7 (recovery logic)
```

### ⏱️ Tempo Stimato
**5 minuti** (add recovery check in startup + dialog)

---

## ✅ Checklist Implementazione Phase 7.5

**Copilot: Spunta dopo ogni fix completato**

### Fix Critici (RACCOMANDATI ORA - 12 min)
- [ ] **Fix 7.5.2**: Typo ABANDON_CRASH → ABANDON_APP_CLOSE (2 min)
- [ ] **Fix 7.5.3**: Timer expiry verification + test (10 min)

### Fix Opzionali (NICE-TO-HAVE - 20 min)
- [ ] Fix 7.5.1: Semantic logging helpers ProfileLogger (15 min)
- [ ] Fix 7.5.4: App startup recovery dialog (5 min)

---

## 🎯 Workflow Suggerito per Copilot

### **Scenario A: Implementazione Completa (30-45 min)**

```
1. Fix 7.5.2 (2 min) → Commit
2. Fix 7.5.3 (10 min) → Commit + test manuale
3. Fix 7.5.1 (15 min) → Commit
4. Fix 7.5.4 (5 min) → Commit
5. Update TODO.md (spunta Phase 7.5 ✅)
6. Proceed to Phase 9 (45 min)
```

**Tempo totale**: 30-45 min (Phase 7.5) + 45 min (Phase 9) = **75-90 minuti**

---

### **Scenario B: Solo Fix Critici (12 min) ⚡ RACCOMANDATO**

```
1. Fix 7.5.2 (2 min) → Commit
2. Fix 7.5.3 (10 min) → Commit + test manuale
3. Update TODO.md (Phase 7.5: 2/4 fix critici ✅)
4. Proceed to Phase 9 (45 min)
5. Create GitHub Issue: "Phase 7.5: Fix opzionali 7.5.1 + 7.5.4"
```

**Tempo totale**: 12 min (fix critici) + 45 min (Phase 9) = **~57 minuti**  
**Beneficio**: Evita bug timer + rimuove TODO, senza ritardare Phase 9

---

### **Scenario C: Skip Phase 7.5 (Solo Phase 9)**

```
1. Skip Phase 7.5 completamente
2. Proceed to Phase 9 (45 min)
3. Create GitHub Issue: "Phase 7.5: Tutti e 4 i fix opzionali"
```

**Tempo**: 45 min (solo Phase 9)  
**Rischio**: Potenziale bug timer (Fix 7.5.3) non risolto

---

## 📊 Decisione Finale

**Raccomandazione**: **Scenario B** (Fix critici 7.5.2 + 7.5.3)

**Motivi**:
1. ✅ **Fix 7.5.3 critico**: Potenziale bug timer (10 min ben spesi)
2. ✅ **Fix 7.5.2 triviale**: Rimuove TODO in 2 min
3. ✅ **Tempo accettabile**: 12 min non ritarda significativamente Phase 9
4. ✅ **Risk mitigation**: Evita bug silente in produzione
5. ✅ **Issue per resto**: Fix 7.5.1 + 7.5.4 nice-to-have (post-merge)

---

## 🔗 Riferimenti Cross-Documentation

- **Torna a**: [`TODO.md`](../../TODO.md) - Feature 3 tracking generale
- **Prossimo step**: [`PHASE_9_MENU_INTEGRATION_UPDATED.md`](PHASE_9_MENU_INTEGRATION_UPDATED.md) - Menu integration (45 min)
- **Piano originale**: [`IMPLEMENTATION_STATS_PRESENTATION.md`](IMPLEMENTATION_STATS_PRESENTATION.md) - Phase 7 overview
- **Profile System**: [`IMPLEMENTATION_PROFILE_SYSTEM.md`](IMPLEMENTATION_PROFILE_SYSTEM.md) - Phase 7 SessionTracker logic
- **Timer System**: [`IMPLEMENTATION_TIMER_SYSTEM.md`](IMPLEMENTATION_TIMER_SYSTEM.md) - Phase 4 timer expiry logic

---

**Documento creato**: 17 Febbraio 2026, 19:50 CET  
**Status**: Ready for Copilot Agent execution (Scenario B raccomandato)  
**Estimated Time**: 12 minuti (fix critici) o 30-45 minuti (tutti i fix)
