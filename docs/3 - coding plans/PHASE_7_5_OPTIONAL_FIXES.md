# 🔧 PHASE 7.5: Optional Fixes (Post-Integration Polish)

**Status**: Implementation Ready  
**Estimated Time**: **15-22 minuti** (agent time)  
**Branch**: `copilot/implement-profile-system-v3-1-0`  
**Prerequisiti**: Phase 1-8 completate ✅  
**Priority**: HIGH (2 fix critici) + MEDIUM (2 fix nice-to-have)

---

## 🎯 Obiettivo Phase 7.5

**Problema**: Copilot ha saltato 4 fix opzionali richiesti nel piano originale Phase 7.

**Soluzione**: Implementare i 4 fix in sequenza per completezza al 100%.

**Classificazione**:
- ⚠️ **CRITICAL (2)**: Fix 7.5.2 (typo) + Fix 7.5.3 (timer logic)
- ℹ️ **NICE-TO-HAVE (2)**: Fix 7.5.1 (logging) + Fix 7.5.4 (recovery UI)

---

## 🚨 FIX 7.5.1: Semantic Logging Helpers (8-10 min)

### 🎯 Obiettivo

Creare `ProfileLogger` class con metodi semantic per migliorare developer experience.

### 📝 File da Creare

**File**: `src/infrastructure/logging/profile_logger.py` (NEW)

```python
"""Semantic logging helpers for profile system events."""

import logging
from typing import Optional
from datetime import datetime

from src.domain.models.profile import UserProfile, SessionOutcome


class ProfileLogger:
    """Semantic logger for profile-related events.
    
    Provides descriptive logging methods instead of generic logger.info().
    Improves log readability and debugging.
    """
    
    def __init__(self, logger_name: str = "profile_system"):
        self.logger = logging.getLogger(logger_name)
    
    def log_profile_created(self, profile: UserProfile) -> None:
        """Log profile creation event."""
        self.logger.info(
            f"Profile created: '{profile.profile_name}' "
            f"(ID: {profile.profile_id})"
        )
    
    def log_profile_loaded(self, profile: UserProfile) -> None:
        """Log profile load event."""
        self.logger.info(
            f"Profile loaded: '{profile.profile_name}' "
            f"(last_played: {profile.last_played})"
        )
    
    def log_profile_switched(
        self,
        from_profile: Optional[str],
        to_profile: str
    ) -> None:
        """Log profile switch event."""
        if from_profile:
            self.logger.info(
                f"Profile switched: '{from_profile}' → '{to_profile}'"
            )
        else:
            self.logger.info(f"Profile activated: '{to_profile}'")
    
    def log_session_recorded(
        self,
        profile_name: str,
        outcome: SessionOutcome
    ) -> None:
        """Log session recording event."""
        result = "Victory" if outcome.is_victory else "Defeat"
        self.logger.info(
            f"Session recorded for '{profile_name}': {result} "
            f"(time: {outcome.elapsed_time:.1f}s, "
            f"moves: {outcome.move_count})"
        )
    
    def log_session_recovery(
        self,
        profile_name: str,
        session_count: int
    ) -> None:
        """Log orphaned session recovery."""
        self.logger.warning(
            f"Recovered {session_count} orphaned session(s) "
            f"for profile '{profile_name}'"
        )
    
    def log_profile_deleted(self, profile_name: str) -> None:
        """Log profile deletion event."""
        self.logger.info(f"Profile deleted: '{profile_name}'")
    
    def log_stats_aggregated(
        self,
        profile_name: str,
        session_count: int
    ) -> None:
        """Log stats aggregation event."""
        self.logger.debug(
            f"Stats aggregated for '{profile_name}': "
            f"{session_count} sessions processed"
        )
```

### 📝 File da Modificare: ProfileService

**File**: `src/domain/services/profile_service.py` (MODIFIED)

```python
# Add import
from src.infrastructure.logging.profile_logger import ProfileLogger

class ProfileService:
    def __init__(self, storage: ProfileStorage):
        self.storage = storage
        self.logger = ProfileLogger()  # ADD THIS
        # ... rest of init ...
    
    def create_profile(self, profile_name: str) -> UserProfile:
        # ... existing logic ...
        profile = UserProfile(profile_name=profile_name, ...)
        self.storage.save_profile(profile)
        
        self.logger.log_profile_created(profile)  # ADD THIS
        return profile
    
    def load_profile(self, profile_id: str) -> UserProfile:
        profile = self.storage.load_profile(profile_id)
        self.logger.log_profile_loaded(profile)  # ADD THIS
        return profile
    
    def switch_profile(self, profile_id: str) -> None:
        old_name = self.active_profile.profile_name if self.active_profile else None
        # ... switch logic ...
        new_name = self.active_profile.profile_name
        
        self.logger.log_profile_switched(old_name, new_name)  # ADD THIS
    
    def record_session(self, outcome: SessionOutcome) -> None:
        # ... existing recording logic ...
        
        self.logger.log_session_recorded(
            self.active_profile.profile_name,
            outcome
        )  # ADD THIS
```

### ✅ Validation

**Manual test**:
1. Abilita logging: `logging.basicConfig(level=logging.INFO)`
2. Crea profilo → verifica log: "Profile created: 'TestUser'"
3. Gioca partita → verifica log: "Session recorded: Victory"
4. Check console output per leggibilità

**Commit message**:
```
feat(infrastructure): Add semantic logging helpers [Phase 7.5.1/4]

- Create ProfileLogger class with descriptive methods
- Methods: log_profile_created/loaded/switched/deleted
- Methods: log_session_recorded/recovery, log_stats_aggregated
- Integrate in ProfileService for all critical events
- Improves log readability and debugging
- Uses standard Python logging module

Refs: IMPLEMENTATION_STATS_PRESENTATION.md Phase 7 optional fixes
```

**Time**: 8-10 min

---

## 🚨 FIX 7.5.2: ABANDON_CRASH Typo Fix (1-2 min) ⚠️ CRITICAL

### 🎯 Obiettivo

Correggere typo `ABANDON_CRASH` → `ABANDON_APP_CLOSE` (enum già esistente).

### 📝 File da Modificare

**File**: `src/application/game_engine.py` (MODIFIED)

**Cerca linea ~703** (o cerca stringa "ABANDON_CRASH"):

```python
# PRIMA (ERRATO):
def _build_session_outcome(self, end_reason: EndReason) -> SessionOutcome:
    # ... logic ...
    
    # TODO: usa ABANDON_CRASH quando implementato
    if end_reason == EndReason.ABANDON_EXIT:
        # Handle app close during game
        pass

# DOPO (CORRETTO):
def _build_session_outcome(self, end_reason: EndReason) -> SessionOutcome:
    # ... logic ...
    
    # EndReason.ABANDON_APP_CLOSE già definito in EndReason enum
    if end_reason == EndReason.ABANDON_APP_CLOSE:
        # Handle app close during game
        pass
```

**Se TODO presente ma codice già usa ABANDON_APP_CLOSE correttamente**:
- Rimuovi solo il commento TODO

### ✅ Validation

**Verifica**:
1. Search `ABANDON_CRASH` in codebase → deve restituire 0 risultati
2. Verify `ABANDON_APP_CLOSE` usato correttamente
3. Check `src/domain/models/game_end.py`: enum definisce `ABANDON_APP_CLOSE` ✅

**Commit message**:
```
fix(game-engine): Correct ABANDON_CRASH typo to ABANDON_APP_CLOSE [Phase 7.5.2/4]

- Replace ABANDON_CRASH → EndReason.ABANDON_APP_CLOSE
- Remove outdated TODO comment
- EndReason.ABANDON_APP_CLOSE already defined in enum (Phase 1)
- No functional change, only naming consistency

Refs: IMPLEMENTATION_STATS_PRESENTATION.md Phase 7 optional fixes
```

**Time**: 1-2 min

---

## 🚨 FIX 7.5.3: Timer Expiry Logic Verification (3-5 min) ⚠️ CRITICAL

### 🎯 Obiettivo

Verificare che `on_timer_tick()` triggeri correttamente `end_game()` su timer expiry in STRICT mode.

### 📝 File da Verificare/Modificare

**File**: `src/application/game_engine.py` (VERIFY + MODIFY if needed)

**Pattern atteso**:

```python
def on_timer_tick(self, elapsed_time: float) -> None:
    """Called by timer every second.
    
    Args:
        elapsed_time: Total elapsed seconds
    """
    # Update display
    self._update_timer_display(elapsed_time)
    
    # Check expiry (STRICT mode only)
    if self.game_settings.timer_mode == TimerMode.STRICT:
        if elapsed_time >= self.game_settings.max_time_game:
            # Timer expired → auto-stop game
            self.end_game(EndReason.TIMEOUT_STRICT)  # VERIFY THIS LINE EXISTS
            return
    
    # PERMISSIVE mode: no auto-stop, just track overtime
```

**Se logica mancante o incompleta**, aggiungere:

```python
def on_timer_tick(self, elapsed_time: float) -> None:
    """Timer tick handler with expiry check."""
    self._update_timer_display(elapsed_time)
    
    # NEW: Check timer expiry
    if self._check_timer_expired(elapsed_time):
        self.end_game(EndReason.TIMEOUT_STRICT)
        return

def _check_timer_expired(self, elapsed_time: float) -> bool:
    """Check if timer has expired (STRICT mode only).
    
    Returns:
        True if timer expired and game should auto-stop
    """
    if not self.game_settings.max_time_game:
        return False  # Timer disabled
    
    if self.game_settings.timer_mode != TimerMode.STRICT:
        return False  # PERMISSIVE mode: no auto-stop
    
    return elapsed_time >= self.game_settings.max_time_game
```

### ✅ Validation

**Integration test**:

```python
# tests/integration/test_timer_expiry.py
def test_strict_mode_auto_stop_on_expiry():
    """Test STRICT mode terminates game on timer expiry."""
    engine = GameEngine(timer_mode=TimerMode.STRICT, max_time=10)
    engine.new_game()
    
    # Simulate timer ticks
    for i in range(11):  # 0-10 seconds
        engine.on_timer_tick(i)
    
    # Verify game stopped at 10s
    assert not engine.game_active
    assert engine.last_end_reason == EndReason.TIMEOUT_STRICT
```

**Commit message**:
```
fix(game-engine): Verify/ensure timer expiry triggers end_game() [Phase 7.5.3/4]

- Verify on_timer_tick() calls end_game(TIMEOUT_STRICT) on expiry
- Add _check_timer_expired() helper if missing
- STRICT mode: auto-stop at time limit
- PERMISSIVE mode: no auto-stop (overtime tracking only)
- Add integration test for expiry behavior

Refs: IMPLEMENTATION_STATS_PRESENTATION.md Phase 7 optional fixes
```

**Time**: 3-5 min

---

## ℹ️ FIX 7.5.4: App Startup Recovery Integration (3-5 min)

### 🎯 Obiettivo

Integrare recovery check all'avvio app per gestire sessioni orfane da crash.

### 📝 File da Modificare

**File**: `acs_wx.py` (MODIFIED) - o main entry point

**Pattern atteso**:

```python
class SolitarioApp(wx.App):
    def OnInit(self):
        # ... existing init ...
        
        # Setup GameEngine
        self.game_engine = GameEngine(...)
        
        # NEW: Check for orphaned sessions from previous crash
        self._check_orphaned_sessions()
        
        # Show main menu
        self.game_engine.show_main_menu()
        return True
    
    def _check_orphaned_sessions(self) -> None:
        """Check for and recover orphaned sessions from dirty shutdown."""
        profile_service = self.game_engine.profile_service
        
        if profile_service is None:
            return  # No profile system active
        
        # Get orphaned sessions
        from src.domain.services.session_tracker import SessionTracker
        tracker = SessionTracker(profile_service.storage.base_path)
        
        orphaned = tracker.get_orphaned_sessions()
        
        if not orphaned:
            return  # No orphaned sessions
        
        # Show recovery dialog
        message = (
            f"Rilevate {len(orphaned)} sessioni non completate \n"
            f"da chiusura anomala precedente.\n\n"
            f"Recuperare le sessioni?"
        )
        
        result = wx.MessageBox(
            message,
            "Recupero Sessioni",
            wx.YES_NO | wx.ICON_QUESTION
        )
        
        if result == wx.YES:
            # Recover sessions
            for session_id in orphaned:
                session = tracker.load_session(session_id)
                if session:
                    profile_service.record_session(session)
            
            # Cleanup orphaned session files
            tracker.cleanup_orphaned_sessions()
            
            wx.MessageBox(
                f"{len(orphaned)} sessioni recuperate con successo.",
                "Recupero Completato",
                wx.OK | wx.ICON_INFORMATION
            )
        else:
            # User declined recovery → cleanup anyway
            tracker.cleanup_orphaned_sessions()
```

### ✅ Validation

**Manual test**:
1. Avvia partita
2. Chiudi app forzatamente (kill process)
3. Riavvia app
4. Verifica: dialog "Rilevate X sessioni non completate" appare
5. Scegli "Sì" → verifica sessioni recuperate in profilo
6. Check: file `.sessions/` puliti dopo recovery

**Commit message**:
```
feat(app): Add orphaned session recovery on startup [Phase 7.5.4/4]

- Check for orphaned sessions on app init
- Show recovery dialog if sessions found
- User choice: recover or discard
- Cleanup session files after recovery
- Uses SessionTracker.get_orphaned_sessions()
- Graceful handling: no-op if profile system disabled

Refs: IMPLEMENTATION_STATS_PRESENTATION.md Phase 7 optional fixes
```

**Time**: 3-5 min

---

## ✅ Phase 7.5 COMPLETA!

### 📊 Risultati Finali

**Commit totali**: 4  
**Tempo effettivo**: **15-22 minuti** (agent time)  
**File creati**: 1 (`profile_logger.py`)  
**File modificati**: 2-3 (`profile_service.py`, `game_engine.py`, `acs_wx.py`)

**Fix implementati**:
- ✅ Semantic logging helpers (developer UX)
- ✅ ABANDON_CRASH typo corrected
- ✅ Timer expiry logic verified/fixed
- ✅ Startup recovery integrated

### 📝 Update Documentation

Dopo commit 7.5.4, aggiornare:

```markdown
# In TODO.md
- [x] **Phase 7.5.1**: Semantic logging helpers
- [x] **Phase 7.5.2**: ABANDON_CRASH typo fix
- [x] **Phase 7.5.3**: Timer expiry verification
- [x] **Phase 7.5.4**: Startup recovery integration
```

---

## 🎯 Sequenza Implementazione Completa

**Order of execution**:

```
1. Phase 7.5 (4 fix) → 15-22 min
2. Phase 9 (3 commits) → 18-28 min
   ├─ 9.1: LastGameDialog + menu "U" (8-12 min)
   ├─ 9.2: Menu "L" leaderboard (4-6 min)
   └─ 9.3: Profile menu stats (6-10 min)

Tempo totale: 33-50 minuti
```

**Risultato finale**: Feature 3 al **100%** senza TODO residui! 🎉

---

## 🚀 Ready for Copilot Execution

**Prompt suggerito**:

```
@workspace Implementa Phase 7.5 + Phase 9

SEQUENZA:
1. Phase 7.5: 4 fix opzionali (15-22 min)
   - Leggi: /docs/3 - coding plans/PHASE_7_5_OPTIONAL_FIXES.md
   - Implementa fix 7.5.1 → 7.5.4 in ordine

2. Phase 9: Menu integration (18-28 min)
   - Leggi: /docs/3 - coding plans/PHASE_9_MENU_INTEGRATION_UPDATED.md
   - Implementa commit 9.1 → 9.3 in ordine

Dopo ogni commit, aggiorna TODO.md.
Tempo totale stimato: 33-50 minuti.
```
