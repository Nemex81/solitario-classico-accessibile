# 🔧 IMPLEMENTATION PLAN
# Timer Mode & Time Outcome System — v2.7.0

## 📌 Informazioni Generali

**Feature**: Timer Mode & Time Outcome System  
**Versione Target**: v2.7.0  
**Layer**: Domain + Application (GameService + GameEngine)  
**Stato**: Implementation Phase — **READY FOR COPILOT**  
**Data Creazione**: 17 Febbraio 2026  
**Prerequisiti**:
- [DESIGN_TIMER_MODE_SYSTEM.md](../2%20-%20projects/DESIGN_TIMER_MODE_SYSTEM.md) (design logico validato)
- Codebase v2.6.1 (branch `refactoring-engine`)

---

## 🎯 Obiettivo dell'Implementation Plan

Implementare il sistema timer come **evento di gioco reale** con:
- ✅ Scadenza timer come stato esplicito (`timer_expired: bool`)
- ✅ Comportamento STRICT (auto-stop) / PERMISSIVE (overtime tracking)
- ✅ `EndReason` enum per esiti differenziati
- ✅ Overtime tracking per statistiche
- ✅ Annunci TTS accessibili (single-fire)
- ✅ Integration con GameEngine e future ProfileService

**Scope**: Solo backend timer logic. Zero UI changes (dialog finali esistenti).

---

## 🔄 Workflow Copilot Agent (Checkpoint-Driven)

Ogni commit segue questo pattern:

```
1. 📖 READ: Consulta questo piano + design doc
2. ✅ CHECK: Verifica checklist fase corrente
3. 💻 CODE: Implementa modifiche atomiche
4. 🧪 TEST: Scrivi unit/integration tests
5. 📝 COMMIT: Messaggio descrittivo + update checklist
6. ♻️ REPEAT: Passa alla fase successiva
```

**Regola d'oro**: Un commit = una responsabilità. Se una fase ha 2+ componenti logicamente separabili, splitta in 2 commit.

---

## 📊 Progress Tracking (Copilot: Aggiorna Ad Ogni Commit)

### ✅ Phase Completion Checklist

- [ ] **Phase 1**: EndReason enum creato e testato
- [ ] **Phase 2**: Timer state attributes in GameService
- [ ] **Phase 3**: Tick check logic + expire detection
- [ ] **Phase 4**: STRICT mode auto-stop implementato
- [ ] **Phase 5**: PERMISSIVE mode overtime tracking
- [ ] **Phase 6**: TTS announcements + formatter integration
- [ ] **Phase 7**: GameEngine integration + end_game() signature
- [ ] **Phase 8**: Session compatibility (future ProfileService hook)

**Istruzioni per Copilot**: Dopo ogni commit, spunta `[x]` la fase completata e committa l'aggiornamento di questo file insieme al codice.

---

## 🗂️ Struttura File Target

### Directory Tree (Post-Implementation)

```
src/
├── domain/
│   ├── models/
│   │   └── game_end.py              # NEW: EndReason enum
│   │
│   └── services/
│       ├── game_service.py           # MODIFIED: +timer_expired, +overtime tracking
│       └── game_engine.py            # MODIFIED: +tick check, +end_game(EndReason)
│
├── presentation/
│   └── formatters/
│       └── game_formatter.py         # MODIFIED: +timer expiry announcements
│
└── tests/
    ├── unit/
    │   ├── test_game_end.py          # NEW: EndReason enum tests
    │   ├── test_timer_state.py       # NEW: Timer state transitions
    │   └── test_timer_logic.py       # NEW: STRICT/PERMISSIVE logic
    │
    └── integration/
        └── test_timer_integration.py # NEW: End-to-end timer scenarios
```

---

## 🧩 PHASE 1: EndReason Enum (Foundation)

### 🎯 Obiettivo

Creare enum `EndReason` per classificare **motivo di terminazione partita**.

### 📝 Commit 1.1: Create EndReason Enum

**File**: `src/domain/models/game_end.py` (NEW)

```python
"""Game end reason classification for outcome tracking."""

from enum import Enum


class EndReason(Enum):
    """Reasons why a game session ended.
    
    Used to differentiate victory/defeat types for statistics and UI.
    Replaces boolean is_victory with fine-grained classification.
    """
    
    # ========================================
    # VICTORIES
    # ========================================
    VICTORY = "victory"
    """Victory within time limit (or timer disabled)."""
    
    VICTORY_OVERTIME = "victory_overtime"
    """Victory after time limit expired (PERMISSIVE mode only)."""
    
    # ========================================
    # VOLUNTARY ABANDONS
    # ========================================
    ABANDON_NEW_GAME = "abandon_new_game"
    """User started new game during active game."""
    
    ABANDON_EXIT = "abandon_exit"
    """User pressed ESC/menu and confirmed abandon."""
    
    # ========================================
    # NON-VOLUNTARY ABANDONS
    # ========================================
    ABANDON_APP_CLOSE = "abandon_app_close"
    """App closed during game (no clean exit)."""
    
    # ========================================
    # TIMER DEFEATS
    # ========================================
    TIMEOUT_STRICT = "timeout_strict"
    """Time limit expired in STRICT mode (auto-stop)."""
    
    def is_victory(self) -> bool:
        """Check if reason represents a victory."""
        return self in (EndReason.VICTORY, EndReason.VICTORY_OVERTIME)
    
    def is_defeat(self) -> bool:
        """Check if reason represents a defeat."""
        return not self.is_victory()
    
    def is_abandon(self) -> bool:
        """Check if reason is any type of abandon."""
        return self in (
            EndReason.ABANDON_NEW_GAME,
            EndReason.ABANDON_EXIT,
            EndReason.ABANDON_APP_CLOSE
        )
    
    def is_timeout(self) -> bool:
        """Check if reason is timeout-related."""
        return self in (EndReason.TIMEOUT_STRICT, EndReason.VICTORY_OVERTIME)
```

**Test Coverage** (`tests/unit/test_game_end.py`):

```python
import pytest
from src.domain.models.game_end import EndReason


class TestEndReason:
    """Test EndReason enum helper methods."""
    
    def test_victory_detection(self):
        assert EndReason.VICTORY.is_victory() is True
        assert EndReason.VICTORY_OVERTIME.is_victory() is True
        assert EndReason.ABANDON_EXIT.is_victory() is False
        assert EndReason.TIMEOUT_STRICT.is_victory() is False
    
    def test_defeat_detection(self):
        assert EndReason.VICTORY.is_defeat() is False
        assert EndReason.ABANDON_EXIT.is_defeat() is True
        assert EndReason.TIMEOUT_STRICT.is_defeat() is True
    
    def test_abandon_detection(self):
        assert EndReason.ABANDON_NEW_GAME.is_abandon() is True
        assert EndReason.ABANDON_EXIT.is_abandon() is True
        assert EndReason.ABANDON_APP_CLOSE.is_abandon() is True
        assert EndReason.VICTORY.is_abandon() is False
        assert EndReason.TIMEOUT_STRICT.is_abandon() is False
    
    def test_timeout_detection(self):
        assert EndReason.TIMEOUT_STRICT.is_timeout() is True
        assert EndReason.VICTORY_OVERTIME.is_timeout() is True
        assert EndReason.VICTORY.is_timeout() is False
        assert EndReason.ABANDON_EXIT.is_timeout() is False
    
    def test_enum_values(self):
        """Verify enum string values for serialization."""
        assert EndReason.VICTORY.value == "victory"
        assert EndReason.TIMEOUT_STRICT.value == "timeout_strict"
```

**Commit Message**:
```
feat(domain): Add EndReason enum for game outcome classification

- Replace boolean is_victory with fine-grained reasons
- 6 distinct end reasons (victory, abandon, timeout variants)
- Helper methods: is_victory(), is_defeat(), is_abandon(), is_timeout()
- Foundation for timer system and future statistics
- Tested: 5 test cases covering all helpers

Refs: DESIGN_TIMER_MODE_SYSTEM.md
```

**Estimated Time**: 5-8 min  
**Test Count**: 5

**✅ Checkpoint**: Dopo questo commit, spunta Phase 1 e committa update di questo file.

---

## ⏱️ PHASE 2: Timer State in GameService

### 🎯 Obiettivo

Aggiungere attributi timer state a `GameService` (domain layer).

### 📝 Commit 2.1: Add Timer State Attributes

**File**: `src/domain/services/game_service.py` (MODIFIED)

**Changes**:

```python
class GameService:
    def __init__(self):
        # ... existing attributes ...
        
        # ========================================
        # TIMER STATE (NEW v2.7.0)
        # ========================================
        self.timer_expired: bool = False
        """Flag: timer has expired (single-fire event)."""
        
        self.overtime_start: Optional[float] = None
        """Timestamp when overtime started (PERMISSIVE mode only)."""
    
    def reset_game(self) -> None:
        """Reset game state for new game."""
        # ... existing resets ...
        
        # Reset timer state
        self.timer_expired = False
        self.overtime_start = None
    
    def get_overtime_duration(self) -> float:
        """Get current overtime duration in seconds.
        
        Returns:
            0.0 if no overtime, else seconds since overtime_start.
        """
        if self.overtime_start is None:
            return 0.0
        return time.time() - self.overtime_start
```

**Test Coverage** (`tests/unit/test_timer_state.py`):

```python
import pytest
import time
from src.domain.services.game_service import GameService


class TestTimerState:
    """Test timer state attributes in GameService."""
    
    def test_initial_state(self):
        service = GameService()
        assert service.timer_expired is False
        assert service.overtime_start is None
    
    def test_reset_clears_timer_state(self):
        service = GameService()
        service.timer_expired = True
        service.overtime_start = time.time()
        
        service.reset_game()
        
        assert service.timer_expired is False
        assert service.overtime_start is None
    
    def test_overtime_duration_no_overtime(self):
        service = GameService()
        assert service.get_overtime_duration() == 0.0
    
    def test_overtime_duration_active(self):
        service = GameService()
        service.overtime_start = time.time() - 10.0  # 10 sec ago
        
        duration = service.get_overtime_duration()
        assert 9.5 <= duration <= 10.5  # Allow 0.5s tolerance
```

**Commit Message**:
```
feat(game-service): Add timer state tracking attributes

- timer_expired: bool flag for expiry event
- overtime_start: Optional[float] timestamp for PERMISSIVE mode
- get_overtime_duration(): Calculate current overtime seconds
- reset_game() clears timer state
- Tested: 4 test cases for state lifecycle

Refs: DESIGN_TIMER_MODE_SYSTEM.md Phase 2
```

**Estimated Time**: 6-10 min  
**Test Count**: 4

**✅ Checkpoint**: Spunta Phase 2 dopo commit.

---

## 🔍 PHASE 3: Timer Expiry Detection

### 🎯 Obiettivo

Implementare logica di **rilevamento scadenza timer** (tick check).

### 📝 Commit 3.1: Add Timer Expiry Check Logic

**File**: `src/domain/services/game_service.py` (MODIFIED)

**Changes**:

```python
class GameService:
    # ... existing code ...
    
    def check_timer_expiry(self, timer_limit: int) -> bool:
        """Check if timer has expired (single-fire check).
        
        Args:
            timer_limit: Maximum time in seconds (from GameSettings)
        
        Returns:
            True if timer just expired (first detection), False otherwise.
        
        Side Effects:
            - Sets self.timer_expired = True on first expiry
            - This method returns True only ONCE per game
        """
        # Already expired, don't fire again
        if self.timer_expired:
            return False
        
        # Timer disabled
        if timer_limit <= 0:
            return False
        
        elapsed = self.get_elapsed_time()
        
        # Check expiry
        if elapsed >= timer_limit:
            self.timer_expired = True
            return True  # First time expiry detected
        
        return False
```

**Test Coverage** (`tests/unit/test_timer_logic.py`):

```python
import pytest
import time
from src.domain.services.game_service import GameService


class TestTimerExpiryLogic:
    """Test timer expiry detection logic."""
    
    def test_timer_disabled_never_expires(self):
        service = GameService()
        service.start_time = time.time() - 1000  # 1000 sec elapsed
        
        expired = service.check_timer_expiry(timer_limit=0)
        assert expired is False
        assert service.timer_expired is False
    
    def test_timer_not_expired_yet(self):
        service = GameService()
        service.start_time = time.time() - 10  # 10 sec elapsed
        
        expired = service.check_timer_expiry(timer_limit=60)
        assert expired is False
        assert service.timer_expired is False
    
    def test_timer_expires_first_detection(self):
        service = GameService()
        service.start_time = time.time() - 61  # 61 sec elapsed
        
        expired = service.check_timer_expiry(timer_limit=60)
        assert expired is True
        assert service.timer_expired is True
    
    def test_timer_expires_only_once(self):
        service = GameService()
        service.start_time = time.time() - 61
        
        # First check: fires
        first = service.check_timer_expiry(timer_limit=60)
        assert first is True
        
        # Second check: no fire (already expired)
        second = service.check_timer_expiry(timer_limit=60)
        assert second is False
        
        # Third check: still no fire
        third = service.check_timer_expiry(timer_limit=60)
        assert third is False
```

**Commit Message**:
```
feat(game-service): Implement timer expiry detection logic

- check_timer_expiry(): Single-fire expiry detection
- Returns True only on first expiry (no spam)
- Sets timer_expired flag permanently
- Handles disabled timer (limit <= 0)
- Tested: 4 test cases covering all scenarios

Refs: DESIGN_TIMER_MODE_SYSTEM.md Phase 3
```

**Estimated Time**: 8-12 min  
**Test Count**: 4

**✅ Checkpoint**: Spunta Phase 3 dopo commit.

---

## 🚨 PHASE 4: STRICT Mode Implementation

### 🎯 Obiettivo

Implementare comportamento **STRICT mode**: scadenza timer → auto-stop partita.

### 📝 Commit 4.1: Add Timer Tick Check in GameEngine

**File**: `src/application/game_engine.py` (MODIFIED)

**Changes**:

```python
import wx
from src.domain.models.game_end import EndReason


class GameEngine:
    def __init__(self, ...):
        # ... existing init ...
        
        # Timer tick check (wx.Timer for 1 second intervals)
        self.timer_tick = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_timer_tick, self.timer_tick)
    
    def new_game(self):
        """Start new game."""
        # ... existing new game logic ...
        
        # Start timer tick if enabled
        if self.game_settings.max_time_game > 0:
            self.timer_tick.Start(1000)  # Check every 1 second
    
    def _on_timer_tick(self, event: wx.TimerEvent) -> None:
        """Timer tick handler (called every 1 second).
        
        Checks for timer expiry and handles STRICT/PERMISSIVE behavior.
        """
        # Check expiry (single-fire)
        expired = self.game_service.check_timer_expiry(
            self.game_settings.max_time_game
        )
        
        if not expired:
            return  # No expiry, continue
        
        # Timer expired: handle based on mode
        if self.game_settings.timer_strict_mode:
            # STRICT: Auto-stop game
            self._handle_strict_timeout()
        else:
            # PERMISSIVE: Start overtime tracking
            self._handle_permissive_timeout()
    
    def _handle_strict_timeout(self) -> None:
        """Handle timer expiry in STRICT mode.
        
        Auto-stops game immediately with TIMEOUT_STRICT reason.
        """
        # Stop timer tick
        self.timer_tick.Stop()
        
        # Announce expiry (TTS)
        self._announce_timer_expired()
        
        # End game immediately
        self.end_game(EndReason.TIMEOUT_STRICT)
    
    def _handle_permissive_timeout(self) -> None:
        """Handle timer expiry in PERMISSIVE mode.
        
        Allows game to continue, starts overtime tracking.
        """
        # Start overtime tracking
        import time
        self.game_service.overtime_start = time.time()
        
        # Announce expiry (TTS, different message)
        self._announce_timer_expired(permissive=True)
        
        # Game continues, timer tick keeps running (for future features)
    
    def _announce_timer_expired(self, permissive: bool = False) -> None:
        """Announce timer expiry via TTS (placeholder for Phase 6)."""
        # TODO Phase 6: Integrate with GameFormatter
        if permissive:
            message = "Tempo scaduto! Il gioco continua con penalità."
        else:
            message = "Tempo scaduto!"
        
        # Temporary direct announce (will use formatter later)
        self._speak(message)
```

**Test Coverage** (`tests/integration/test_timer_integration.py`):

```python
import pytest
import time
from unittest.mock import Mock, patch
from src.application.game_engine import GameEngine
from src.domain.models.game_end import EndReason


class TestStrictModeTimeout:
    """Integration tests for STRICT mode timer."""
    
    @patch('src.application.game_engine.GameEngine.end_game')
    def test_strict_timeout_ends_game(self, mock_end_game):
        engine = GameEngine()
        engine.game_settings.max_time_game = 60
        engine.game_settings.timer_strict_mode = True
        
        # Simulate game started 61 seconds ago
        engine.game_service.start_time = time.time() - 61
        
        # Trigger tick check
        engine._on_timer_tick(None)
        
        # Verify end_game called with TIMEOUT_STRICT
        mock_end_game.assert_called_once_with(EndReason.TIMEOUT_STRICT)
    
    def test_strict_timeout_stops_tick_timer(self):
        engine = GameEngine()
        engine.game_settings.max_time_game = 60
        engine.game_settings.timer_strict_mode = True
        engine.game_service.start_time = time.time() - 61
        
        # Start timer tick
        engine.timer_tick.Start(1000)
        assert engine.timer_tick.IsRunning()
        
        # Trigger timeout
        engine._on_timer_tick(None)
        
        # Verify timer stopped
        assert not engine.timer_tick.IsRunning()
```

**Commit Message**:
```
feat(game-engine): Implement STRICT mode timer timeout

- Add wx.Timer tick check (1 second intervals)
- _on_timer_tick(): Checks expiry and delegates to mode handlers
- _handle_strict_timeout(): Auto-stop game with TIMEOUT_STRICT
- Timer tick stops on STRICT timeout
- TTS announcement placeholder (Phase 6)
- Tested: 2 integration tests for STRICT behavior

Refs: DESIGN_TIMER_MODE_SYSTEM.md Scenario A
```

**Estimated Time**: 12-18 min  
**Test Count**: 2

**✅ Checkpoint**: Spunta Phase 4 dopo commit.

---

## ⏳ PHASE 5: PERMISSIVE Mode Implementation

### 🎯 Obiettivo

Implementare comportamento **PERMISSIVE mode**: overtime tracking + continua gameplay.

### 📝 Commit 5.1: Implement PERMISSIVE Mode Overtime

**Note**: La logica base è già in `_handle_permissive_timeout()` del commit precedente. Questo commit aggiunge test e integrazione con `end_game()`.

**File**: `src/application/game_engine.py` (MODIFIED)

**Changes**:

```python
class GameEngine:
    # ... existing code ...
    
    def end_game(self, end_reason: EndReason) -> None:
        """End game with specific reason.
        
        CHANGED: New signature (was is_victory: bool).
        
        Args:
            end_reason: Why game ended (EndReason enum)
        """
        # Stop timer tick
        if self.timer_tick.IsRunning():
            self.timer_tick.Stop()
        
        # Determine if victory based on reason
        is_victory = end_reason.is_victory()
        
        # For PERMISSIVE overtime victories, set VICTORY_OVERTIME
        if end_reason == EndReason.VICTORY and self.game_service.overtime_start is not None:
            end_reason = EndReason.VICTORY_OVERTIME
        
        # ... existing end game logic (dialog, scoring, etc.) ...
        # Use end_reason instead of is_victory for future SessionOutcome
        
        self._show_end_game_dialog(end_reason)
    
    def _show_end_game_dialog(self, end_reason: EndReason) -> None:
        """Show end game dialog (existing, minimal changes).
        
        Args:
            end_reason: Game end reason for dialog content
        """
        # Existing dialog code, now aware of EndReason
        # Future: Detailed dialogs based on reason (v3.0.0)
        pass
```

**Test Coverage** (`tests/integration/test_timer_integration.py`):

```python
class TestPermissiveModeTimeout:
    """Integration tests for PERMISSIVE mode timer."""
    
    def test_permissive_timeout_continues_game(self):
        engine = GameEngine()
        engine.game_settings.max_time_game = 60
        engine.game_settings.timer_strict_mode = False
        engine.game_service.start_time = time.time() - 61
        
        # Trigger timeout
        engine._on_timer_tick(None)
        
        # Verify game NOT ended
        assert engine.game_service.overtime_start is not None
        assert engine.timer_tick.IsRunning()  # Tick continues
    
    def test_permissive_overtime_tracking_starts(self):
        engine = GameEngine()
        engine.game_settings.max_time_game = 60
        engine.game_settings.timer_strict_mode = False
        engine.game_service.start_time = time.time() - 61
        
        # Before timeout
        assert engine.game_service.overtime_start is None
        
        # Trigger timeout
        engine._on_timer_tick(None)
        
        # After timeout
        assert engine.game_service.overtime_start is not None
        overtime = engine.game_service.get_overtime_duration()
        assert overtime >= 0.0
    
    def test_permissive_victory_after_overtime(self):
        engine = GameEngine()
        engine.game_settings.max_time_game = 60
        engine.game_settings.timer_strict_mode = False
        engine.game_service.start_time = time.time() - 61
        engine.game_service.overtime_start = time.time() - 10  # 10s overtime
        
        # User wins after overtime
        engine.end_game(EndReason.VICTORY)
        
        # Should be classified as VICTORY_OVERTIME
        # (verification via future SessionOutcome)
```

**Commit Message**:
```
feat(game-engine): Implement PERMISSIVE mode overtime tracking

- PERMISSIVE timeout starts overtime_start timestamp
- Game continues after timeout (tick timer keeps running)
- end_game() upgraded to accept EndReason enum
- Auto-convert VICTORY → VICTORY_OVERTIME if overtime active
- Tested: 3 integration tests for PERMISSIVE scenarios

Refs: DESIGN_TIMER_MODE_SYSTEM.md Scenario B
```

**Estimated Time**: 10-15 min  
**Test Count**: 3

**✅ Checkpoint**: Spunta Phase 5 dopo commit.

---

## 🔊 PHASE 6: TTS Announcements

### 🎯 Obiettivo

Integrare annunci TTS accessibili per scadenza timer.

### 📝 Commit 6.1: Add Timer Expiry TTS Announcements

**File**: `src/presentation/formatters/game_formatter.py` (MODIFIED)

**Changes**:

```python
class GameFormatter:
    """Formatter for game-related TTS announcements."""
    
    # ... existing methods ...
    
    @staticmethod
    def format_timer_expired(strict_mode: bool) -> str:
        """Format timer expiry announcement.
        
        Args:
            strict_mode: True if STRICT mode, False if PERMISSIVE
        
        Returns:
            TTS-friendly message for timer expiry
        """
        if strict_mode:
            return "Tempo scaduto!"
        else:
            return "Tempo scaduto! Il gioco continua con penalità."
    
    @staticmethod
    def format_overtime_warning(minutes_over: int) -> str:
        """Format overtime warning (optional, for future use).
        
        Args:
            minutes_over: Minutes of overtime elapsed
        
        Returns:
            TTS-friendly overtime warning
        """
        if minutes_over == 1:
            return "Hai superato il tempo limite di 1 minuto."
        else:
            return f"Hai superato il tempo limite di {minutes_over} minuti."
```

**File**: `src/application/game_engine.py` (MODIFIED)

**Changes**:

```python
from src.presentation.formatters.game_formatter import GameFormatter


class GameEngine:
    # ... existing code ...
    
    def _announce_timer_expired(self, permissive: bool = False) -> None:
        """Announce timer expiry via TTS.
        
        Args:
            permissive: True if PERMISSIVE mode, False if STRICT
        """
        message = GameFormatter.format_timer_expired(
            strict_mode=not permissive
        )
        self._speak(message)
```

**Test Coverage** (`tests/unit/test_game_formatter.py`):

```python
import pytest
from src.presentation.formatters.game_formatter import GameFormatter


class TestTimerAnnouncements:
    """Test timer-related TTS formatting."""
    
    def test_timer_expired_strict(self):
        message = GameFormatter.format_timer_expired(strict_mode=True)
        assert message == "Tempo scaduto!"
    
    def test_timer_expired_permissive(self):
        message = GameFormatter.format_timer_expired(strict_mode=False)
        assert "Tempo scaduto!" in message
        assert "continua" in message
        assert "penalità" in message
    
    def test_overtime_warning_singular(self):
        message = GameFormatter.format_overtime_warning(minutes_over=1)
        assert "1 minuto" in message
    
    def test_overtime_warning_plural(self):
        message = GameFormatter.format_overtime_warning(minutes_over=5)
        assert "5 minuti" in message
```

**Commit Message**:
```
feat(presentation): Add TTS announcements for timer expiry

- GameFormatter.format_timer_expired(): STRICT/PERMISSIVE messages
- GameFormatter.format_overtime_warning(): Optional overtime alerts
- Integrate with GameEngine._announce_timer_expired()
- Screen-reader friendly Italian messages
- Tested: 4 test cases for formatter methods

Refs: DESIGN_TIMER_MODE_SYSTEM.md Accessibility section
```

**Estimated Time**: 8-12 min  
**Test Count**: 4

**✅ Checkpoint**: Spunta Phase 6 dopo commit.

---

## 🔗 PHASE 7: Backward Compatibility

### 🎯 Obiettivo

Garantire compatibilità con codice esistente che usa `end_game(is_victory: bool)`.

### 📝 Commit 7.1: Add Backward Compatibility Wrapper

**File**: `src/application/game_engine.py` (MODIFIED)

**Changes**:

```python
from typing import Union
from src.domain.models.game_end import EndReason


class GameEngine:
    # ... existing code ...
    
    def end_game(self, end_reason: Union[EndReason, bool]) -> None:
        """End game with reason or legacy boolean.
        
        Args:
            end_reason: EndReason enum (preferred) or bool (legacy)
                       If bool: True=VICTORY, False=ABANDON_EXIT
        
        Deprecated:
            Passing bool is deprecated, use EndReason enum.
        """
        # Backward compatibility: convert bool to EndReason
        if isinstance(end_reason, bool):
            import warnings
            warnings.warn(
                "Passing bool to end_game() is deprecated. Use EndReason enum.",
                DeprecationWarning,
                stacklevel=2
            )
            end_reason = EndReason.VICTORY if end_reason else EndReason.ABANDON_EXIT
        
        # ... rest of end_game() logic (already handles EndReason) ...
```

**Test Coverage** (`tests/unit/test_game_engine.py`):

```python
import pytest
import warnings
from src.application.game_engine import GameEngine
from src.domain.models.game_end import EndReason


class TestEndGameBackwardCompatibility:
    """Test backward compatibility for end_game()."""
    
    def test_end_game_accepts_end_reason(self):
        engine = GameEngine()
        # Should not raise
        engine.end_game(EndReason.VICTORY)
    
    def test_end_game_accepts_bool_with_deprecation(self):
        engine = GameEngine()
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            engine.end_game(True)  # Legacy bool
            
            # Verify deprecation warning
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "deprecated" in str(w[0].message).lower()
    
    def test_bool_true_maps_to_victory(self):
        engine = GameEngine()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Should behave as VICTORY
            engine.end_game(True)
    
    def test_bool_false_maps_to_abandon_exit(self):
        engine = GameEngine()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Should behave as ABANDON_EXIT
            engine.end_game(False)
```

**Commit Message**:
```
feat(game-engine): Add backward compatibility for end_game()

- Accept Union[EndReason, bool] parameter
- Convert bool to EndReason with deprecation warning
- True → VICTORY, False → ABANDON_EXIT
- Allows gradual migration of existing code
- Tested: 4 test cases for legacy bool handling

Refs: Clean Architecture backward compatibility pattern
```

**Estimated Time**: 6-10 min  
**Test Count**: 4

**✅ Checkpoint**: Spunta Phase 7 dopo commit.

---

## 🎯 PHASE 8: Future Profile System Hook

### 🎯 Obiettivo

Preparare integrazione con futuro `ProfileService` (v3.0.0).

### 📝 Commit 8.1: Add Session Outcome Population (Stub)

**File**: `src/application/game_engine.py` (MODIFIED)

**Changes**:

```python
class GameEngine:
    # ... existing code ...
    
    def end_game(self, end_reason: Union[EndReason, bool]) -> None:
        """End game with reason."""
        # ... convert bool to EndReason if needed ...
        # ... stop timer tick ...
        # ... handle VICTORY → VICTORY_OVERTIME conversion ...
        
        # Populate session data for future ProfileService
        session_data = self._build_session_outcome(end_reason)
        
        # TODO v3.0.0: Call ProfileService.record_session(session_data)
        # For now, just prepare the data structure
        
        # ... existing end game logic (dialog, etc.) ...
    
    def _build_session_outcome(self, end_reason: EndReason) -> dict:
        """Build session outcome data for ProfileService.
        
        Returns:
            Dict with all fields needed for SessionOutcome (v3.0.0)
        """
        return {
            "end_reason": end_reason,
            "is_victory": end_reason.is_victory(),
            "elapsed_time": self.game_service.get_elapsed_time(),
            "timer_enabled": self.game_settings.max_time_game > 0,
            "timer_limit": self.game_settings.max_time_game,
            "timer_mode": self._get_timer_mode(),
            "timer_expired": self.game_service.timer_expired,
            "overtime_duration": self.game_service.get_overtime_duration(),
            
            # Gameplay stats (from GameService)
            "move_count": self.game_service.move_count,
            "draw_count_actions": self.game_service.draw_count,
            "recycle_count": self.game_service.recycle_count,
            "foundation_cards": list(self.game_service.carte_per_seme),
            "completed_suits": self.game_service.semi_completati,
            
            # Config
            "difficulty_level": self.game_settings.difficulty_level,
            "deck_type": self.game_settings.deck_type,
            "draw_count": self.game_settings.draw_count,
            "shuffle_mode": self.game_settings.shuffle_mode,
            
            # Scoring (if enabled)
            "scoring_enabled": self.game_settings.scoring_enabled,
            # ... final_score, base_score, etc. from ScoringService ...
        }
    
    def _get_timer_mode(self) -> str:
        """Get timer mode string."""
        if self.game_settings.max_time_game == 0:
            return "OFF"
        return "STRICT" if self.game_settings.timer_strict_mode else "PERMISSIVE"
```

**Test Coverage** (`tests/integration/test_timer_integration.py`):

```python
class TestSessionOutcomePopulation:
    """Test session outcome data population for ProfileService."""
    
    def test_build_session_outcome_victory(self):
        engine = GameEngine()
        engine.game_settings.max_time_game = 600
        engine.game_settings.timer_strict_mode = False
        engine.game_service.start_time = time.time() - 300  # 5 min
        
        outcome = engine._build_session_outcome(EndReason.VICTORY)
        
        assert outcome["end_reason"] == EndReason.VICTORY
        assert outcome["is_victory"] is True
        assert 290 <= outcome["elapsed_time"] <= 310
        assert outcome["timer_enabled"] is True
        assert outcome["timer_limit"] == 600
        assert outcome["timer_mode"] == "PERMISSIVE"
        assert outcome["timer_expired"] is False
        assert outcome["overtime_duration"] == 0.0
    
    def test_build_session_outcome_timeout_strict(self):
        engine = GameEngine()
        engine.game_settings.max_time_game = 300
        engine.game_settings.timer_strict_mode = True
        engine.game_service.start_time = time.time() - 305
        engine.game_service.timer_expired = True
        
        outcome = engine._build_session_outcome(EndReason.TIMEOUT_STRICT)
        
        assert outcome["end_reason"] == EndReason.TIMEOUT_STRICT
        assert outcome["is_victory"] is False
        assert outcome["timer_expired"] is True
        assert outcome["timer_mode"] == "STRICT"
    
    def test_build_session_outcome_overtime(self):
        engine = GameEngine()
        engine.game_settings.max_time_game = 300
        engine.game_settings.timer_strict_mode = False
        engine.game_service.start_time = time.time() - 420  # 7 min
        engine.game_service.timer_expired = True
        engine.game_service.overtime_start = time.time() - 120  # 2 min overtime
        
        outcome = engine._build_session_outcome(EndReason.VICTORY_OVERTIME)
        
        assert outcome["end_reason"] == EndReason.VICTORY_OVERTIME
        assert outcome["is_victory"] is True
        assert outcome["timer_expired"] is True
        assert 110 <= outcome["overtime_duration"] <= 130
```

**Commit Message**:
```
feat(game-engine): Prepare session outcome for ProfileService

- _build_session_outcome(): Populate all timer + gameplay fields
- Returns dict compatible with future SessionOutcome model
- Includes: end_reason, timer state, overtime, gameplay stats
- Stub for v3.0.0 ProfileService.record_session() integration
- Tested: 3 integration tests for outcome data accuracy

Refs: DESIGN_PROFILE_STATISTICS_SYSTEM.md SessionOutcome
```

**Estimated Time**: 10-15 min  
**Test Count**: 3

**✅ Checkpoint**: Spunta Phase 8 dopo commit. Timer System v2.7.0 completo!

---

## ✅ Final Validation Checklist

**Copilot: Esegui questi check prima di dichiarare feature completa**

### Code Quality

- [ ] Tutti i commit seguono Conventional Commits format
- [ ] Nessun TODO rimasto (eccetto v3.0.0 integration)
- [ ] Typing completo (no `Any` type hints)
- [ ] Docstring su tutti i metodi pubblici
- [ ] Logging su eventi critici (expire, timeout)

### Testing

- [ ] Test coverage ≥ 88% (target progetto)
- [ ] Tutti i test passano (`pytest`)
- [ ] Integration tests coprono 5 scenari principali
- [ ] No test warnings o deprecations (eccetto backward compat)

### Functionality

- [ ] Timer STRICT termina partita correttamente
- [ ] Timer PERMISSIVE continua con overtime tracking
- [ ] TTS announce timer expiry (single-fire)
- [ ] `end_game()` accetta sia EndReason che bool (deprecato)
- [ ] Session outcome data popolato correttamente

### Documentation

- [ ] CHANGELOG.md aggiornato con v2.7.0
- [ ] Questo file (IMPLEMENTATION_TIMER_SYSTEM.md) aggiornato con check spuntati
- [ ] API.md aggiornato con nuovi metodi (se pubblici)

---

## 📊 Commit Summary (Final)

| Phase | Commit | Description | Time | Tests |
|---|---|---|---|---|
| **1** | 1.1 | EndReason enum | 5-8 min | 5 |
| **2** | 2.1 | Timer state attributes | 6-10 min | 4 |
| **3** | 3.1 | Timer expiry detection | 8-12 min | 4 |
| **4** | 4.1 | STRICT mode timeout | 12-18 min | 2 |
| **5** | 5.1 | PERMISSIVE mode overtime | 10-15 min | 3 |
| **6** | 6.1 | TTS announcements | 8-12 min | 4 |
| **7** | 7.1 | Backward compatibility | 6-10 min | 4 |
| **8** | 8.1 | Session outcome stub | 10-15 min | 3 |
| **TOTAL** | **8 commits** | | **65-100 min** | **29 tests** |

**Realistic Estimate**: GitHub Copilot Agent completes Timer System in **45-70 minutes**.

---

## 🔗 Next Steps After v2.7.0

1. **Profile System v3.0.0 Backend** (`IMPLEMENTATION_PROFILE_SYSTEM.md`)
   - Uses `EndReason` from this feature
   - Persists `timer_expired`, `overtime_duration` to JSON
   - Aggregates timer statistics

2. **Stats Presentation v3.0.0 Frontend** (`IMPLEMENTATION_STATS_PRESENTATION.md`)
   - Victory/defeat dialogs with timer info
   - Timer performance analytics UI
   - Leaderboard timer filters

---

## 📚 Riferimenti

- **Design Doc**: [DESIGN_TIMER_MODE_SYSTEM.md](../2%20-%20projects/DESIGN_TIMER_MODE_SYSTEM.md)
- **Profile Design**: [DESIGN_PROFILE_STATISTICS_SYSTEM.md](../2%20-%20projects/DESIGN_PROFILE_STATISTICS_SYSTEM.md)
- **Codebase**: [refactoring-engine branch](https://github.com/Nemex81/solitario-classico-accessibile/tree/refactoring-engine)
- **Current Version**: v2.6.1

---

**Documento creato**: 17 Febbraio 2026, 13:45 CET  
**Autore**: Luca (utente) + Perplexity AI (technical planning)  
**Status**: **Ready for Copilot Agent execution** ✅  
**Estimated Completion**: 45-70 minutes agent time
