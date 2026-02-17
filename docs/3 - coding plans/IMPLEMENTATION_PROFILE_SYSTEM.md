# 🔧 IMPLEMENTATION PLAN
# Profile & Statistics System — Backend Layer

## 📌 Informazioni Generali

**Feature**: Profile & Statistics System v3.0.0  
**Layer**: Backend (Storage + Domain Logic)  
**Stato**: Implementation Phase — **REVIEW APPROVED**  
**Data Creazione**: 17 Febbraio 2026  
**Data Aggiornamento**: 17 Febbraio 2026 13:30 CET  
**Prerequisiti**: 
- [DESIGN_PROFILE_STATISTICS_SYSTEM.md](../2%20-%20projects/DESIGN_PROFILE_STATISTICS_SYSTEM.md) (data model)
- [DESIGN_TIMER_MODE_SYSTEM.md](../2%20-%20projects/DESIGN_TIMER_MODE_SYSTEM.md) (EndReason definitions)

---

## 🎯 Obiettivo dell'Implementation Plan

Implementare **solo il backend** del sistema profili:
- ✅ Data models (dataclasses immutabili)
- ✅ JSON storage layer (read/write/index) con **atomic writes**
- ✅ Profile management service (CRUD operations)
- ✅ Session recording (SessionOutcome persistence)
- ✅ Stats aggregation (incremental updates)
- ✅ Session tracking (dirty shutdown recovery)
- ✅ **DI Container integration** (architectural consistency)
- ✅ **Logging integration** (game_logger pattern)

**Scope limitato**: Zero UI in questa fase. Solo API + storage + logic.

**Deliverable**: Dopo questa fase, GameEngine può chiamare `ProfileService.record_session(outcome)` e salvare/aggregare dati in modo **deterministico e resiliente**.

---

## 📋 CHANGELOG da Versione Originale

### 🔴 Critical Fixes Applied

1. **Storage Path Consistency**
   - ❌ Original: `Path("data/profiles")`
   - ✅ Fixed: `Path.home() / ".solitario" / "profiles"`
   - **Rationale**: Consistent with existing `ScoreStorage` pattern

2. **Atomic JSON Writes**
   - ❌ Original: Direct `json.dump()` (corruption risk)
   - ✅ Fixed: `_atomic_write_json()` helper (temp file + rename)
   - **Rationale**: Prevent data loss on app crash during save

3. **Guest Profile Protection**
   - ❌ Original: Soft fail in `ProfileService` only
   - ✅ Fixed: Hard fail (`ValueError`) in `ProfileStorage` layer
   - **Rationale**: Defense-in-depth, cannot bypass protection

4. **Logging Integration**
   - ❌ Original: No logging
   - ✅ Fixed: `game_logger` in all storage methods
   - **Rationale**: Consistent with existing `ScoreStorage` pattern

5. **DI Container Integration**
   - ❌ Original: Direct instantiation
   - ✅ Fixed: New Phase 5 commit + DI-compatible constructors
   - **Rationale**: Architectural consistency, testability

6. **Missing Imports**
   - ❌ Original: `uuid` not imported in `SessionTracker`
   - ✅ Fixed: Explicit imports added in code snippets
   - **Rationale**: Prevent runtime errors

### 🟡 Deferred to v3.1

- **Sessions File Growth**: Archiving/pagination deferred (documented limitation)
- **Backup Strategy**: Manual backup documented, auto-backup in v3.1
- **Stress Tests**: Concurrent writes, race conditions (v3.1+)

---

## 🗂️ Struttura File Target

### Directory Tree (Post-Implementation)

```
src/
├─ domain/
│  ├─ models/
│  │  ├─ profile.py          # UserProfile, SessionOutcome dataclasses
│  │  └─ statistics.py       # GlobalStats, TimerStats, DifficultyStats, ScoringStats
│  │
│  └─ services/
│     ├─ profile_service.py  # ProfileService (CRUD + aggregation)
│     └─ session_tracker.py  # SessionTracker (dirty shutdown recovery)
│
├─ infrastructure/
│  ├─ storage/
│  │  ├─ profile_storage.py  # ProfileStorage (JSON read/write atomic)
│  │  └─ session_storage.py  # SessionStorage (append-only storico)
│  │
│  └─ di_container.py         # EXTENDED: +ProfileService factory methods
│
└─ tests/
   ├─ unit/
   │  ├─ test_profile_models.py
   │  ├─ test_profile_storage.py
   │  └─ test_profile_service.py
   │
   └─ integration/
      └─ test_profile_integration.py  # End-to-end storage scenarios

~/.solitario/profiles/              # CHANGED: System-wide storage
├─ profiles_index.json              # Lista profili + summary
├─ profile_<uuid>.json              # Aggregati + recent sessions cache
├─ sessions_<uuid>.json             # Storico completo (append-only)
└─ session_active.json              # Flag partita in corso (dirty tracking)
```

**⚠️ NOTA STORAGE PATH**: Changed from `./data/profiles/` to `~/.solitario/profiles/` for consistency with `ScoreStorage`.

---

## 🧩 PHASE 1: Data Models (Foundation)

### Commit 1.1: Core Profile Models

**File**: `src/domain/models/profile.py`

```python
"""Domain models for profile and session management."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict
from enum import Enum
import uuid  # ADDED: Explicit import

# ========================================
# EndReason Enum (from Timer System Design)
# ========================================
class EndReason(Enum):
    """Reason why a game session ended."""
    
    # Victories
    VICTORY = "victory"                          # Victory within time (or timer off)
    VICTORY_OVERTIME = "victory_overtime"        # Victory beyond time (PERMISSIVE)
    
    # Voluntary abandons
    ABANDON_NEW_GAME = "abandon_new_game"        # New game during active game
    ABANDON_EXIT = "abandon_exit"                # ESC/menu with confirmation
    
    # Non-voluntary abandons
    ABANDON_APP_CLOSE = "abandon_app_close"      # App closed during game
    
    # Timer defeats
    TIMEOUT_STRICT = "timeout_strict"            # Timer expired (STRICT mode)


# ========================================
# UserProfile
# ========================================
@dataclass
class UserProfile:
    """Represents a player profile with persistent identity."""
    
    # Identity
    profile_id: str                     # UUID or "guest"
    profile_name: str                   # Display name
    created_at: datetime
    last_played: datetime
    is_default: bool = False            # Auto-selected at startup
    is_guest: bool = False              # Special guest profile
    
    # Preferences (future, placeholder)
    preferred_difficulty: int = 3
    preferred_deck: str = "french"
    
    @classmethod
    def create_new(cls, name: str, is_guest: bool = False) -> "UserProfile":
        """Factory method for new profile creation."""
        profile_id = "guest" if is_guest else str(uuid.uuid4())
        now = datetime.utcnow()
        
        return cls(
            profile_id=profile_id,
            profile_name=name,
            created_at=now,
            last_played=now,
            is_default=not is_guest,  # First profile (non-guest) is default
            is_guest=is_guest
        )
    
    @classmethod
    def create_guest(cls) -> "UserProfile":
        """Create the special guest profile (fixed ID)."""
        return cls.create_new("Ospite", is_guest=True)


# ========================================
# SessionOutcome (Atomic Unit)
# ========================================
@dataclass
class SessionOutcome:
    """Complete snapshot of a finished game session.
    
    Immutable once saved (append-only). Feeds aggregates and history.
    """
    
    # ========================================
    # IDENTIFICATION
    # ========================================
    session_id: str                     # UUID unique per session
    profile_id: str                     # Which profile owns this
    timestamp: datetime                 # When it ended (ISO 8601)
    
    # ========================================
    # OUTCOME (from Timer System v2.7.0)
    # ========================================
    end_reason: EndReason               # victory | abandon_* | timeout
    is_victory: bool                    # Shortcut for aggregate queries
    
    # ========================================
    # TIME (from Timer System v2.7.0)
    # ========================================
    elapsed_time: float                 # Total seconds
    timer_enabled: bool                 # Was timer active?
    timer_limit: int                    # Configured limit (seconds, 0=off)
    timer_mode: str                     # "STRICT" | "PERMISSIVE" | "OFF"
    timer_expired: bool                 # Did expiry occur?
    overtime_duration: float = 0.0      # Seconds beyond limit (0 if none)
    
    # ========================================
    # SCORING (from Scoring System v2.0)
    # ========================================
    scoring_enabled: bool               # Was scoring active?
    final_score: int = 0                # Total final score
    base_score: int = 0                 # Base score (moves/time)
    difficulty_multiplier: float = 1.0  # Difficulty multiplier
    deck_bonus: int = 0                 # Deck type bonus
    quality_multiplier: float = 1.0     # Victory quality (1.0-2.0)
    
    # ========================================
    # GAME CONFIGURATION
    # ========================================
    difficulty_level: int = 3           # 1-5
    deck_type: str = "french"           # "french" | "neapolitan"
    draw_count: int = 1                 # 1-3 cards drawn
    shuffle_mode: str = "invert"        # "invert" | "random"
    
    # ========================================
    # GAMEPLAY STATS (from GameService)
    # ========================================
    move_count: int = 0                 # Total moves
    draw_count_actions: int = 0         # Draw actions
    recycle_count: int = 0              # Deck recyclings
    foundation_cards: List[int] = field(default_factory=lambda: [0,0,0,0])  # Per suit
    completed_suits: int = 0            # 0-4 suits completed
    
    # ========================================
    # METADATA
    # ========================================
    game_version: str = "2.6.1"         # App version
    notes: str = ""                      # User notes (future)
    
    @classmethod
    def create_new(cls, profile_id: str, **kwargs) -> "SessionOutcome":
        """Factory method for new session creation."""
        return cls(
            session_id=str(uuid.uuid4()),
            profile_id=profile_id,
            timestamp=datetime.utcnow(),
            **kwargs
        )
    
    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        data = {
            "session_id": self.session_id,
            "profile_id": self.profile_id,
            "timestamp": self.timestamp.isoformat(),
            "end_reason": self.end_reason.value,
            "is_victory": self.is_victory,
            "elapsed_time": self.elapsed_time,
            "timer_enabled": self.timer_enabled,
            "timer_limit": self.timer_limit,
            "timer_mode": self.timer_mode,
            "timer_expired": self.timer_expired,
            "overtime_duration": self.overtime_duration,
            "scoring_enabled": self.scoring_enabled,
            "final_score": self.final_score,
            "base_score": self.base_score,
            "difficulty_multiplier": self.difficulty_multiplier,
            "deck_bonus": self.deck_bonus,
            "quality_multiplier": self.quality_multiplier,
            "difficulty_level": self.difficulty_level,
            "deck_type": self.deck_type,
            "draw_count": self.draw_count,
            "shuffle_mode": self.shuffle_mode,
            "move_count": self.move_count,
            "draw_count_actions": self.draw_count_actions,
            "recycle_count": self.recycle_count,
            "foundation_cards": self.foundation_cards,
            "completed_suits": self.completed_suits,
            "game_version": self.game_version,
            "notes": self.notes
        }
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> "SessionOutcome":
        """Create from JSON dict."""
        # Parse datetime
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        # Parse enum
        data["end_reason"] = EndReason(data["end_reason"])
        return cls(**data)
```

**Test Coverage** (`tests/unit/test_profile_models.py`):
- ✅ UserProfile creation (normal + guest)
- ✅ SessionOutcome creation
- ✅ SessionOutcome to_dict / from_dict roundtrip
- ✅ EndReason enum values
- ✅ UUID generation

**Estimated Time**: 10-12 min  
**Test Count**: 6-8

---

### Commit 1.2: Statistics Aggregates

**File**: `src/domain/models/statistics.py`

```python
"""Aggregate statistics models for profile data."""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class GlobalStats:
    """Global statistics across all games for a profile."""
    
    # Counters
    total_games: int = 0
    total_victories: int = 0
    total_defeats: int = 0                # abandons + timeouts
    
    # Ratios
    winrate: float = 0.0                  # victories / total_games
    
    # Time
    total_playtime: float = 0.0           # Total seconds
    average_game_time: float = 0.0
    fastest_victory: float = float('inf') # Record minimum time
    slowest_victory: float = 0.0          # Record maximum time
    
    # Records
    highest_score: int = 0                # Maximum score
    longest_streak: int = 0               # Best win streak
    current_streak: int = 0               # Current win streak
    
    def update_from_session(self, outcome) -> None:
        """Update stats incrementally from SessionOutcome."""
        self.total_games += 1
        self.total_playtime += outcome.elapsed_time
        
        if outcome.is_victory:
            self.total_victories += 1
            self.current_streak += 1
            
            # Update records
            if outcome.elapsed_time < self.fastest_victory:
                self.fastest_victory = outcome.elapsed_time
            if outcome.elapsed_time > self.slowest_victory:
                self.slowest_victory = outcome.elapsed_time
            if outcome.final_score > self.highest_score:
                self.highest_score = outcome.final_score
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
        else:
            self.total_defeats += 1
            self.current_streak = 0  # Defeat breaks streak
        
        # Recalculate derived stats
        self.winrate = self.total_victories / self.total_games if self.total_games > 0 else 0.0
        self.average_game_time = self.total_playtime / self.total_games if self.total_games > 0 else 0.0


@dataclass
class TimerStats:
    """Statistics for games with timer enabled."""
    
    games_with_timer: int = 0
    
    # Breakdown by outcome
    victories_within_time: int = 0        # EndReason.VICTORY (no overtime)
    victories_overtime: int = 0           # EndReason.VICTORY_OVERTIME
    defeats_timeout: int = 0              # EndReason.TIMEOUT_STRICT
    
    # Overtime analytics
    total_overtime: float = 0.0           # Total overtime seconds
    average_overtime: float = 0.0         # Mean when present
    max_overtime: float = 0.0             # Worst overtime
    
    # Performance
    average_time_vs_limit: float = 0.0    # Time efficiency
    
    def update_from_session(self, outcome) -> None:
        """Update timer stats from SessionOutcome."""
        if not outcome.timer_enabled:
            return  # Skip non-timer games
        
        self.games_with_timer += 1
        
        # Classify outcome
        from .profile import EndReason
        if outcome.end_reason == EndReason.VICTORY:
            self.victories_within_time += 1
        elif outcome.end_reason == EndReason.VICTORY_OVERTIME:
            self.victories_overtime += 1
            self.total_overtime += outcome.overtime_duration
            if outcome.overtime_duration > self.max_overtime:
                self.max_overtime = outcome.overtime_duration
        elif outcome.end_reason == EndReason.TIMEOUT_STRICT:
            self.defeats_timeout += 1
        
        # Recalculate averages
        if self.victories_overtime > 0:
            self.average_overtime = self.total_overtime / self.victories_overtime


@dataclass
class DifficultyStats:
    """Statistics breakdown by difficulty level."""
    
    games_by_level: Dict[int, int] = field(default_factory=dict)
    victories_by_level: Dict[int, int] = field(default_factory=dict)
    winrate_by_level: Dict[int, float] = field(default_factory=dict)
    average_score_by_level: Dict[int, float] = field(default_factory=dict)
    
    def update_from_session(self, outcome) -> None:
        """Update difficulty stats from SessionOutcome."""
        level = outcome.difficulty_level
        
        # Initialize level if not present
        if level not in self.games_by_level:
            self.games_by_level[level] = 0
            self.victories_by_level[level] = 0
            self.winrate_by_level[level] = 0.0
            self.average_score_by_level[level] = 0.0
        
        self.games_by_level[level] += 1
        
        if outcome.is_victory:
            self.victories_by_level[level] += 1
        
        # Recalculate winrate
        self.winrate_by_level[level] = (
            self.victories_by_level[level] / self.games_by_level[level]
        )
        
        # Update average score (if scoring enabled)
        if outcome.scoring_enabled:
            current_avg = self.average_score_by_level[level]
            games = self.games_by_level[level]
            self.average_score_by_level[level] = (
                (current_avg * (games - 1) + outcome.final_score) / games
            )


@dataclass
class ScoringStats:
    """Statistics for games with scoring enabled."""
    
    games_with_scoring: int = 0
    
    total_score: int = 0                  # Sum of all scores
    average_score: float = 0.0
    highest_score: int = 0
    lowest_score: int = float('inf')      # Only victories
    
    # Quality distribution
    perfect_games: int = 0                # quality >= 1.8
    good_games: int = 0                   # quality >= 1.4
    average_games: int = 0                # quality < 1.4
    
    def update_from_session(self, outcome) -> None:
        """Update scoring stats from SessionOutcome."""
        if not outcome.scoring_enabled:
            return  # Skip non-scoring games
        
        self.games_with_scoring += 1
        self.total_score += outcome.final_score
        
        if outcome.is_victory:
            if outcome.final_score > self.highest_score:
                self.highest_score = outcome.final_score
            if outcome.final_score < self.lowest_score:
                self.lowest_score = outcome.final_score
            
            # Quality classification
            quality = outcome.quality_multiplier
            if quality >= 1.8:
                self.perfect_games += 1
            elif quality >= 1.4:
                self.good_games += 1
            else:
                self.average_games += 1
        
        # Recalculate average
        self.average_score = self.total_score / self.games_with_scoring
```

**Test Coverage** (`tests/unit/test_profile_models.py`):
- ✅ GlobalStats incremental update (victory + defeat)
- ✅ GlobalStats winrate calculation
- ✅ GlobalStats streak logic (increment + break)
- ✅ TimerStats overtime tracking
- ✅ DifficultyStats per-level aggregation
- ✅ ScoringStats quality distribution

**Estimated Time**: 12-15 min  
**Test Count**: 10-12

---

## 🗄️ PHASE 2: Storage Layer (with Atomic Writes)

### Commit 2.1: Profile Storage (JSON Read/Write + Atomic)

**File**: `src/infrastructure/storage/profile_storage.py`

```python
"""JSON storage for profile data and index with atomic write safety."""

import json
import os
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime

from src.domain.models.profile import UserProfile
from src.domain.models.statistics import GlobalStats, TimerStats, DifficultyStats, ScoringStats
from src.infrastructure.logging import game_logger as log  # ADDED: Logging integration


class ProfileStorage:
    """Handles JSON persistence for profile data with atomic write safety.
    
    File structure:
    - ~/.solitario/profiles/profiles_index.json (profile list + summary)
    - ~/.solitario/profiles/profile_<uuid>.json (full profile + aggregates + recent sessions)
    """
    
    # CHANGED: System-wide storage path (consistent with ScoreStorage)
    PROFILES_DIR = Path.home() / ".solitario" / "profiles"
    INDEX_FILE = PROFILES_DIR / "profiles_index.json"
    
    def __init__(self, data_dir: Path = None):
        """Initialize storage with optional custom data directory."""
        if data_dir:
            self.PROFILES_DIR = data_dir / "profiles"
            self.INDEX_FILE = self.PROFILES_DIR / "profiles_index.json"
        
        self._ensure_directory_exists()
    
    def _ensure_directory_exists(self) -> None:
        """Create profiles directory if not exists."""
        self.PROFILES_DIR.mkdir(parents=True, exist_ok=True)
        log.info_query_requested(
            "profile_storage_init",
            f"Profile storage initialized at {self.PROFILES_DIR}"
        )
    
    # ========================================
    # ATOMIC WRITE HELPER (NEW)
    # ========================================
    
    def _atomic_write_json(self, file_path: Path, data: dict) -> None:
        """Write JSON atomically using temp file + rename to prevent corruption.
        
        This ensures that even if app crashes during write, the original file
        remains intact (no partial/corrupted JSON).
        """
        temp_path = file_path.with_suffix('.tmp')
        
        try:
            # Write to temp file first
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Atomic replace (OS-level operation)
            shutil.move(str(temp_path), str(file_path))
            
        except Exception as e:
            # Cleanup temp file on error
            if temp_path.exists():
                temp_path.unlink()
            raise e
    
    # ========================================
    # INDEX OPERATIONS
    # ========================================
    
    def load_index(self) -> Dict:
        """Load profiles_index.json.
        
        Returns:
            Dict with 'version', 'default_profile_id', 'profiles' (list).
            Empty structure if file doesn't exist.
        """
        if not self.INDEX_FILE.exists():
            log.warning_issued(
                "ProfileStorage",
                f"Index file not found: {self.INDEX_FILE}, returning empty index"
            )
            return self._create_empty_index()
        
        try:
            with open(self.INDEX_FILE, 'r', encoding='utf-8') as f:
                index = json.load(f)
            
            log.info_query_requested(
                "profile_index_load",
                f"Loaded profile index with {len(index.get('profiles', []))} profiles"
            )
            return index
        
        except (json.JSONDecodeError, IOError) as e:
            # Corrupted index, recreate
            log.error_occurred(
                "ProfileStorage",
                f"Corrupted index file: {self.INDEX_FILE}",
                e
            )
            return self._create_empty_index()
    
    def save_index(self, index_data: Dict) -> None:
        """Save profiles_index.json atomically."""
        try:
            self._atomic_write_json(self.INDEX_FILE, index_data)
            log.info_query_requested(
                "profile_index_save",
                f"Saved profile index with {len(index_data.get('profiles', []))} profiles"
            )
        except Exception as e:
            log.error_occurred(
                "ProfileStorage",
                f"Failed to save index: {self.INDEX_FILE}",
                e
            )
            raise
    
    def _create_empty_index(self) -> Dict:
        """Create empty index structure."""
        return {
            "version": "3.0.0",
            "default_profile_id": None,
            "profiles": []
        }
    
    def add_profile_to_index(self, profile: UserProfile, stats: GlobalStats) -> None:
        """Add/update profile entry in index."""
        index = self.load_index()
        
        # Remove existing entry (if any)
        index["profiles"] = [
            p for p in index["profiles"] if p["profile_id"] != profile.profile_id
        ]
        
        # Add new entry with summary
        index["profiles"].append({
            "profile_id": profile.profile_id,
            "profile_name": profile.profile_name,
            "is_default": profile.is_default,
            "is_guest": profile.is_guest,
            "created_at": profile.created_at.isoformat(),
            "last_played": profile.last_played.isoformat(),
            "total_games": stats.total_games,
            "total_victories": stats.total_victories,
            "winrate": stats.winrate
        })
        
        # Update default_profile_id if this is default
        if profile.is_default:
            index["default_profile_id"] = profile.profile_id
        
        self.save_index(index)
    
    def remove_profile_from_index(self, profile_id: str) -> None:
        """Remove profile from index."""
        index = self.load_index()
        index["profiles"] = [
            p for p in index["profiles"] if p["profile_id"] != profile_id
        ]
        
        # Clear default if removed
        if index["default_profile_id"] == profile_id:
            index["default_profile_id"] = None
        
        self.save_index(index)
        log.info_query_requested(
            "profile_index_remove",
            f"Removed profile {profile_id} from index"
        )
    
    def get_default_profile_id(self) -> Optional[str]:
        """Get default profile ID from index."""
        index = self.load_index()
        return index.get("default_profile_id")
    
    def list_profiles(self) -> List[Dict]:
        """List all profiles from index (lightweight)."""
        index = self.load_index()
        return index.get("profiles", [])
    
    # ========================================
    # PROFILE FILE OPERATIONS
    # ========================================
    
    def _get_profile_file_path(self, profile_id: str) -> Path:
        """Get path for profile_<uuid>.json."""
        return self.PROFILES_DIR / f"profile_{profile_id}.json"
    
    def save_profile(
        self,
        profile: UserProfile,
        global_stats: GlobalStats,
        timer_stats: TimerStats,
        difficulty_stats: DifficultyStats,
        scoring_stats: ScoringStats,
        recent_sessions: List[Dict] = None
    ) -> None:
        """Save complete profile with aggregates to JSON atomically."""
        file_path = self._get_profile_file_path(profile.profile_id)
        
        data = {
            "profile_id": profile.profile_id,
            "profile_name": profile.profile_name,
            "created_at": profile.created_at.isoformat(),
            "last_played": profile.last_played.isoformat(),
            "is_default": profile.is_default,
            "is_guest": profile.is_guest,
            "preferred_difficulty": profile.preferred_difficulty,
            "preferred_deck": profile.preferred_deck,
            
            "global_stats": self._stats_to_dict(global_stats),
            "timer_stats": self._stats_to_dict(timer_stats),
            "difficulty_stats": self._stats_to_dict(difficulty_stats),
            "scoring_stats": self._stats_to_dict(scoring_stats),
            
            "recent_sessions": recent_sessions or []
        }
        
        try:
            self._atomic_write_json(file_path, data)
            log.info_query_requested(
                "profile_save",
                f"Saved profile {profile.profile_id} ({profile.profile_name})"
            )
        except Exception as e:
            log.error_occurred(
                "ProfileStorage",
                f"Failed to save profile {profile.profile_id}",
                e
            )
            raise
        
        # Update index
        self.add_profile_to_index(profile, global_stats)
    
    def load_profile(self, profile_id: str) -> Optional[Dict]:
        """Load complete profile data from JSON.
        
        Returns:
            Dict with profile + all stats, or None if not found.
        """
        file_path = self._get_profile_file_path(profile_id)
        
        if not file_path.exists():
            log.warning_issued(
                "ProfileStorage",
                f"Profile file not found: {profile_id}"
            )
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            log.info_query_requested(
                "profile_load",
                f"Loaded profile {profile_id}"
            )
            return data
        
        except (json.JSONDecodeError, IOError) as e:
            log.error_occurred(
                "ProfileStorage",
                f"Failed to load profile {profile_id}",
                e
            )
            return None
    
    def delete_profile(self, profile_id: str) -> bool:
        """Delete profile file and remove from index.
        
        CHANGED: Hard protection for guest profile (defense-in-depth).
        
        Returns:
            True if deleted, False if not found.
        
        Raises:
            ValueError: If attempting to delete guest profile.
        """
        # ADDED: Hard fail for guest profile (cannot bypass)
        if profile_id == "guest":
            raise ValueError("Cannot delete guest profile (system-protected)")
        
        file_path = self._get_profile_file_path(profile_id)
        
        if file_path.exists():
            file_path.unlink()
            self.remove_profile_from_index(profile_id)
            log.info_query_requested(
                "profile_delete",
                f"Deleted profile {profile_id}"
            )
            return True
        
        log.warning_issued(
            "ProfileStorage",
            f"Attempted to delete non-existent profile: {profile_id}"
        )
        return False
    
    def profile_exists(self, profile_id: str) -> bool:
        """Check if profile file exists."""
        return self._get_profile_file_path(profile_id).exists()
    
    # ========================================
    # HELPER METHODS
    # ========================================
    
    def _stats_to_dict(self, stats) -> Dict:
        """Convert stats dataclass to dict."""
        if hasattr(stats, '__dataclass_fields__'):
            return {k: v for k, v in stats.__dict__.items()}
        return {}
```

**Test Coverage** (`tests/unit/test_profile_storage.py`):
- ✅ Directory creation on init
- ✅ Index load/save (empty + populated)
- ✅ Add/remove profile from index
- ✅ Profile save/load roundtrip
- ✅ Profile deletion (normal + guest protection)
- ✅ Profile existence check
- ✅ Default profile ID handling
- ✅ Atomic write safety (simulate crash during write)

**Estimated Time**: 20-25 min  
**Test Count**: 10-12

---

### Commit 2.2: Session Storage (Append-Only History + Atomic)

**File**: `src/infrastructure/storage/session_storage.py`

```python
"""Append-only JSON storage for session history with atomic write safety."""

import json
from pathlib import Path
from typing import List, Dict

from src.domain.models.profile import SessionOutcome
from src.infrastructure.logging import game_logger as log  # ADDED: Logging integration


class SessionStorage:
    """Handles append-only session history storage with atomic writes.
    
    File structure:
    - ~/.solitario/profiles/sessions_<uuid>.json (complete history per profile)
    """
    
    PROFILES_DIR = Path.home() / ".solitario" / "profiles"  # CHANGED: System-wide
    
    def __init__(self, data_dir: Path = None):
        if data_dir:
            self.PROFILES_DIR = data_dir / "profiles"
        self.PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    
    def _get_sessions_file_path(self, profile_id: str) -> Path:
        """Get path for sessions_<uuid>.json."""
        return self.PROFILES_DIR / f"sessions_{profile_id}.json"
    
    def append_session(self, outcome: SessionOutcome) -> None:
        """Append SessionOutcome to profile's session history atomically.
        
        Creates file if doesn't exist (first session for profile).
        Uses atomic write to prevent corruption on crash.
        """
        file_path = self._get_sessions_file_path(outcome.profile_id)
        
        # Load existing sessions (or create empty)
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                log.error_occurred(
                    "SessionStorage",
                    f"Corrupted sessions file: {file_path}, recreating",
                    e
                )
                data = {
                    "profile_id": outcome.profile_id,
                    "version": "3.0.0",
                    "sessions": []
                }
        else:
            data = {
                "profile_id": outcome.profile_id,
                "version": "3.0.0",
                "sessions": []
            }
        
        # Append new session
        data["sessions"].append(outcome.to_dict())
        
        # Atomic write
        try:
            temp_path = file_path.with_suffix('.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            import shutil
            shutil.move(str(temp_path), str(file_path))
            
            log.info_query_requested(
                "session_append",
                f"Appended session {outcome.session_id} to profile {outcome.profile_id}"
            )
        
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            log.error_occurred(
                "SessionStorage",
                f"Failed to append session {outcome.session_id}",
                e
            )
            raise
    
    def load_all_sessions(self, profile_id: str) -> List[SessionOutcome]:
        """Load all sessions for a profile.
        
        Returns:
            List of SessionOutcome objects, empty if none.
        """
        file_path = self._get_sessions_file_path(profile_id)
        
        if not file_path.exists():
            log.info_query_requested(
                "session_load",
                f"No sessions file for profile {profile_id}, returning empty list"
            )
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                sessions_data = data.get("sessions", [])
                sessions = [SessionOutcome.from_dict(s) for s in sessions_data]
            
            log.info_query_requested(
                "session_load",
                f"Loaded {len(sessions)} sessions for profile {profile_id}"
            )
            return sessions
        
        except (json.JSONDecodeError, IOError) as e:
            log.error_occurred(
                "SessionStorage",
                f"Failed to load sessions for profile {profile_id}",
                e
            )
            return []
    
    def load_recent_sessions(self, profile_id: str, limit: int = 50) -> List[SessionOutcome]:
        """Load most recent N sessions for a profile.
        
        Returns:
            List of SessionOutcome objects (newest first).
        """
        all_sessions = self.load_all_sessions(profile_id)
        return list(reversed(all_sessions[-limit:]))  # Newest first
    
    def get_session_count(self, profile_id: str) -> int:
        """Get total session count for a profile."""
        file_path = self._get_sessions_file_path(profile_id)
        
        if not file_path.exists():
            return 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return len(data.get("sessions", []))
        except (json.JSONDecodeError, IOError):
            return 0
    
    def delete_sessions(self, profile_id: str) -> bool:
        """Delete all sessions for a profile.
        
        Returns:
            True if deleted, False if not found.
        """
        file_path = self._get_sessions_file_path(profile_id)
        
        if file_path.exists():
            file_path.unlink()
            log.info_query_requested(
                "session_delete",
                f"Deleted all sessions for profile {profile_id}"
            )
            return True
        return False
```

**Test Coverage** (`tests/unit/test_session_storage.py`):
- ✅ Append session (first + subsequent)
- ✅ Load all sessions
- ✅ Load recent sessions (limit)
- ✅ Get session count
- ✅ Delete sessions
- ✅ SessionOutcome roundtrip (to_dict/from_dict)
- ✅ Corrupted file recovery
- ✅ Atomic write safety

**Estimated Time**: 12-18 min  
**Test Count**: 8-10

---

## 🧠 PHASE 3: Domain Services

### Commit 3.1: ProfileService (CRUD + Aggregation + DI-Compatible)

**File**: `src/domain/services/profile_service.py`

```python
"""Profile management service with CRUD and statistics aggregation."""

from typing import List, Optional, Dict
from datetime import datetime

from src.domain.models.profile import UserProfile, SessionOutcome
from src.domain.models.statistics import GlobalStats, TimerStats, DifficultyStats, ScoringStats
from src.infrastructure.storage.profile_storage import ProfileStorage
from src.infrastructure.storage.session_storage import SessionStorage
from src.infrastructure.logging import game_logger as log  # ADDED: Logging integration


class ProfileService:
    """High-level service for profile and session management.
    
    DI-Compatible: Accepts optional storage instances for testing/injection.
    """
    
    def __init__(self, profile_storage: ProfileStorage = None, session_storage: SessionStorage = None):
        # CHANGED: DI-compatible constructor
        self.profile_storage = profile_storage or ProfileStorage()
        self.session_storage = session_storage or SessionStorage()
        
        # In-memory cache of active profile
        self.active_profile: Optional[UserProfile] = None
        self.global_stats: GlobalStats = GlobalStats()
        self.timer_stats: TimerStats = TimerStats()
        self.difficulty_stats: DifficultyStats = DifficultyStats()
        self.scoring_stats: ScoringStats = ScoringStats()
        self.recent_sessions: List[Dict] = []
    
    # ========================================
    # INITIALIZATION
    # ========================================
    
    def initialize(self) -> None:
        """Initialize service at app startup.
        
        - Load profiles index
        - Create guest profile if needed
        - Load default profile (or prompt creation)
        """
        log.info_query_requested(
            "profile_service_init",
            "Initializing ProfileService"
        )
        
        index = self.profile_storage.load_index()
        
        # Ensure guest profile exists
        self._ensure_guest_profile()
        
        # Load default profile if exists
        default_id = self.profile_storage.get_default_profile_id()
        if default_id:
            self.load_profile(default_id)
            log.info_query_requested(
                "profile_service_init",
                f"Loaded default profile: {default_id}"
            )
        else:
            # First run: no profiles yet (handled by UI)
            log.info_query_requested(
                "profile_service_init",
                "No default profile found (first run)"
            )
    
    def _ensure_guest_profile(self) -> None:
        """Ensure guest profile exists in storage."""
        if not self.profile_storage.profile_exists("guest"):
            guest = UserProfile.create_guest()
            self._save_profile_to_storage(guest)
            log.info_query_requested(
                "profile_service_init",
                "Created guest profile"
            )
    
    # ========================================
    # PROFILE CRUD
    # ========================================
    
    def create_profile(self, name: str, set_as_default: bool = False) -> UserProfile:
        """Create new profile.
        
        Args:
            name: Display name
            set_as_default: Set as default profile
        
        Returns:
            Created UserProfile
        """
        profile = UserProfile.create_new(name, is_guest=False)
        profile.is_default = set_as_default
        
        # Save to storage with empty stats
        self._save_profile_to_storage(profile)
        
        log.info_query_requested(
            "profile_create",
            f"Created profile {profile.profile_id} ({name})"
        )
        
        return profile
    
    def load_profile(self, profile_id: str) -> bool:
        """Load profile as active.
        
        Args:
            profile_id: Profile UUID or "guest"
        
        Returns:
            True if loaded, False if not found
        """
        data = self.profile_storage.load_profile(profile_id)
        
        if not data:
            log.warning_issued(
                "ProfileService",
                f"Failed to load profile {profile_id} (not found)"
            )
            return False
        
        # Reconstruct profile and stats
        self.active_profile = self._profile_from_dict(data)
        self.global_stats = self._stats_from_dict(GlobalStats, data.get("global_stats", {}))
        self.timer_stats = self._stats_from_dict(TimerStats, data.get("timer_stats", {}))
        self.difficulty_stats = self._stats_from_dict(DifficultyStats, data.get("difficulty_stats", {}))
        self.scoring_stats = self._stats_from_dict(ScoringStats, data.get("scoring_stats", {}))
        self.recent_sessions = data.get("recent_sessions", [])
        
        # Update last_played
        self.active_profile.last_played = datetime.utcnow()
        
        log.info_query_requested(
            "profile_load",
            f"Loaded profile {profile_id} as active"
        )
        
        return True
    
    def save_active_profile(self) -> None:
        """Save active profile and stats to storage."""
        if not self.active_profile:
            raise ValueError("No active profile to save")
        
        self._save_profile_to_storage(self.active_profile)
    
    def delete_profile(self, profile_id: str) -> bool:
        """Delete profile and all associated data.
        
        Args:
            profile_id: Profile UUID (cannot delete guest)
        
        Returns:
            True if deleted, False if not found or guest
        
        Raises:
            ValueError: If attempting to delete guest profile.
        """
        # ADDED: Soft check here too (defense-in-depth)
        if profile_id == "guest":
            log.warning_issued(
                "ProfileService",
                "Attempted to delete guest profile (blocked)"
            )
            raise ValueError("Cannot delete guest profile")
        
        try:
            # Delete profile file (storage layer has hard protection)
            profile_deleted = self.profile_storage.delete_profile(profile_id)
            
            # Delete sessions
            sessions_deleted = self.session_storage.delete_sessions(profile_id)
            
            log.info_query_requested(
                "profile_delete",
                f"Deleted profile {profile_id} (profile={profile_deleted}, sessions={sessions_deleted})"
            )
            
            return profile_deleted
        
        except ValueError as e:
            # Re-raise protection errors
            raise e
    
    def list_all_profiles(self) -> List[Dict]:
        """List all profiles (lightweight from index)."""
        return self.profile_storage.list_profiles()
    
    def set_default_profile(self, profile_id: str) -> bool:
        """Set profile as default.
        
        Returns:
            True if set, False if profile not found
        """
        data = self.profile_storage.load_profile(profile_id)
        if not data:
            return False
        
        # Load profile, set as default, save
        profile = self._profile_from_dict(data)
        profile.is_default = True
        
        # Clear default from other profiles (in index)
        index = self.profile_storage.load_index()
        for p in index["profiles"]:
            if p["profile_id"] != profile_id:
                p["is_default"] = False
        self.profile_storage.save_index(index)
        
        # Save updated profile
        self._save_profile_to_storage(profile)
        
        log.info_query_requested(
            "profile_set_default",
            f"Set profile {profile_id} as default"
        )
        
        return True
    
    # ========================================
    # SESSION RECORDING
    # ========================================
    
    def record_session(self, outcome: SessionOutcome) -> None:
        """Record completed session and update aggregates.
        
        Args:
            outcome: Complete SessionOutcome from game end
        """
        if not self.active_profile:
            raise ValueError("No active profile for session recording")
        
        # Ensure outcome has correct profile_id
        outcome.profile_id = self.active_profile.profile_id
        
        log.info_query_requested(
            "session_record",
            f"Recording session {outcome.session_id} (reason={outcome.end_reason.value}, victory={outcome.is_victory})"
        )
        
        # Update aggregates incrementally
        self.global_stats.update_from_session(outcome)
        self.timer_stats.update_from_session(outcome)
        self.difficulty_stats.update_from_session(outcome)
        self.scoring_stats.update_from_session(outcome)
        
        # Update recent sessions cache (FIFO 50)
        self.recent_sessions.insert(0, outcome.to_dict())  # Newest first
        self.recent_sessions = self.recent_sessions[:50]   # Keep only 50
        
        # Append to session history (storage)
        self.session_storage.append_session(outcome)
        
        # Save updated profile
        self.save_active_profile()
    
    def get_recent_sessions(self, limit: int = 10) -> List[SessionOutcome]:
        """Get recent sessions from cache.
        
        Args:
            limit: Max sessions to return
        
        Returns:
            List of SessionOutcome (newest first)
        """
        return [
            SessionOutcome.from_dict(s) 
            for s in self.recent_sessions[:limit]
        ]
    
    def get_all_sessions(self) -> List[SessionOutcome]:
        """Load all sessions for active profile from storage.
        
        Returns:
            List of SessionOutcome (chronological)
        """
        if not self.active_profile:
            return []
        return self.session_storage.load_all_sessions(self.active_profile.profile_id)
    
    # ========================================
    # HELPER METHODS
    # ========================================
    
    def _save_profile_to_storage(self, profile: UserProfile) -> None:
        """Save profile with current aggregates to storage."""
        # If this is active profile, use in-memory stats
        if self.active_profile and profile.profile_id == self.active_profile.profile_id:
            global_stats = self.global_stats
            timer_stats = self.timer_stats
            difficulty_stats = self.difficulty_stats
            scoring_stats = self.scoring_stats
            recent_sessions = self.recent_sessions
        else:
            # Empty stats for new profiles
            global_stats = GlobalStats()
            timer_stats = TimerStats()
            difficulty_stats = DifficultyStats()
            scoring_stats = ScoringStats()
            recent_sessions = []
        
        self.profile_storage.save_profile(
            profile,
            global_stats,
            timer_stats,
            difficulty_stats,
            scoring_stats,
            recent_sessions
        )
    
    def _profile_from_dict(self, data: Dict) -> UserProfile:
        """Reconstruct UserProfile from JSON dict."""
        return UserProfile(
            profile_id=data["profile_id"],
            profile_name=data["profile_name"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_played=datetime.fromisoformat(data["last_played"]),
            is_default=data["is_default"],
            is_guest=data["is_guest"],
            preferred_difficulty=data.get("preferred_difficulty", 3),
            preferred_deck=data.get("preferred_deck", "french")
        )
    
    def _stats_from_dict(self, stats_class, data: Dict):
        """Reconstruct stats dataclass from dict."""
        return stats_class(**data) if data else stats_class()
```

**Test Coverage** (`tests/unit/test_profile_service.py`):
- ✅ Initialize (guest profile creation)
- ✅ Create profile
- ✅ Load profile
- ✅ Save active profile
- ✅ Delete profile (normal + guest protection)
- ✅ List profiles
- ✅ Set default profile
- ✅ Record session (aggregates update)
- ✅ Get recent sessions (cache)
- ✅ Get all sessions (storage load)

**Estimated Time**: 20-25 min  
**Test Count**: 12-15

---

### Commit 3.2: SessionTracker (Dirty Shutdown Recovery)

**File**: `src/domain/services/session_tracker.py`

```python
"""Session tracking for dirty shutdown recovery."""

import json
import uuid  # ADDED: Explicit import (was missing)
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime

from src.domain.models.profile import SessionOutcome, EndReason
from src.infrastructure.logging import game_logger as log  # ADDED: Logging integration


class SessionTracker:
    """Tracks active game session to recover from unexpected app closure.
    
    Creates a temporary flag file (session_active.json) at game start,
    deletes it on clean exit. If file exists at app startup, recovers
    as ABANDON_APP_CLOSE.
    """
    
    SESSION_FILE = Path.home() / ".solitario" / "profiles" / "session_active.json"  # CHANGED: System-wide
    
    def __init__(self, data_dir: Path = None):
        if data_dir:
            self.SESSION_FILE = data_dir / "profiles" / "session_active.json"
        self.SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    def start_session(self, profile_id: str, game_config: Dict) -> None:
        """Mark session as active (game started).
        
        Args:
            profile_id: Active profile UUID
            game_config: Dict with difficulty, timer, scoring settings
        """
        data = {
            "profile_id": profile_id,
            "session_id": str(uuid.uuid4()),
            "start_time": datetime.utcnow().isoformat(),
            "game_config": game_config
        }
        
        with open(self.SESSION_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        log.info_query_requested(
            "session_tracker_start",
            f"Session {data['session_id']} marked as active"
        )
    
    def end_session(self) -> None:
        """Mark session as ended (clean exit)."""
        if self.SESSION_FILE.exists():
            self.SESSION_FILE.unlink()
            log.info_query_requested(
                "session_tracker_end",
                "Session ended cleanly (flag removed)"
            )
    
    def has_orphaned_session(self) -> bool:
        """Check if there's an orphaned session (dirty shutdown)."""
        return self.SESSION_FILE.exists()
    
    def recover_orphaned_session(self) -> Optional[SessionOutcome]:
        """Recover orphaned session as ABANDON_APP_CLOSE.
        
        Returns:
            SessionOutcome with partial data, or None if no orphan.
        """
        if not self.has_orphaned_session():
            return None
        
        try:
            with open(self.SESSION_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Calculate elapsed time (approximate)
            start_time = datetime.fromisoformat(data["start_time"])
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            
            # Construct outcome with ABANDON_APP_CLOSE
            game_config = data.get("game_config", {})
            
            outcome = SessionOutcome(
                session_id=data["session_id"],
                profile_id=data["profile_id"],
                timestamp=datetime.utcnow(),
                end_reason=EndReason.ABANDON_APP_CLOSE,
                is_victory=False,
                elapsed_time=elapsed,
                
                # Game config fields
                timer_enabled=game_config.get("timer_enabled", False),
                timer_limit=game_config.get("timer_limit", 0),
                timer_mode=game_config.get("timer_mode", "OFF"),
                timer_expired=False,
                scoring_enabled=game_config.get("scoring_enabled", False),
                difficulty_level=game_config.get("difficulty_level", 3),
                deck_type=game_config.get("deck_type", "french"),
                draw_count=game_config.get("draw_count", 1),
                shuffle_mode=game_config.get("shuffle_mode", "invert"),
                
                # Gameplay stats unknown (zeros)
                move_count=0,
                draw_count_actions=0,
                recycle_count=0,
                foundation_cards=[0,0,0,0],
                completed_suits=0
            )
            
            # Clean up orphan file
            self.SESSION_FILE.unlink()
            
            log.info_query_requested(
                "session_tracker_recover",
                f"Recovered orphaned session {outcome.session_id} (profile={outcome.profile_id})"
            )
            
            return outcome
            
        except (json.JSONDecodeError, IOError, KeyError) as e:
            # Corrupted orphan, delete and ignore
            self.SESSION_FILE.unlink()
            log.error_occurred(
                "SessionTracker",
                "Corrupted orphan session file (deleted)",
                e
            )
            return None
```

**Test Coverage** (`tests/unit/test_session_tracker.py`):
- ✅ Start session (file created)
- ✅ End session (file deleted)
- ✅ Has orphaned session check
- ✅ Recover orphaned session (ABANDON_APP_CLOSE)
- ✅ Corrupted orphan handling

**Estimated Time**: 10-12 min  
**Test Count**: 5-6

---

## 🔗 PHASE 4: Integration with GameEngine

### Commit 4.1: GameEngine Hooks (Session Recording)

**File Modification**: `src/domain/services/game_engine.py` (o application layer se GameEngine è lì)

**Changes**:

```python
# ADDED: Imports
from src.domain.models.profile import EndReason, SessionOutcome
from src.domain.services.profile_service import ProfileService
from src.domain.services.session_tracker import SessionTracker
from src.infrastructure.di_container import get_container  # ADDED: DI usage


class GameEngine:
    def __init__(self, ...):
        # ... existing init ...
        
        # CHANGED: Use DI container (not direct instantiation)
        container = get_container()
        self.profile_service = container.get_profile_service()
        self.session_tracker = SessionTracker()
        
        self.current_session_outcome: Optional[SessionOutcome] = None
    
    def new_game(self) -> None:
        """Start new game."""
        # ... existing new game logic ...
        
        # Initialize SessionOutcome
        self.current_session_outcome = SessionOutcome.create_new(
            profile_id=self.profile_service.active_profile.profile_id,
            # Initial values (will be updated at game end)
            end_reason=EndReason.ABANDON_NEW_GAME,  # Placeholder
            is_victory=False,
            elapsed_time=0.0,
            timer_enabled=self.game_settings.max_time_game > 0,
            timer_limit=self.game_settings.max_time_game,
            timer_mode=self._get_timer_mode(),
            timer_expired=False,
            scoring_enabled=self.game_settings.scoring_enabled,
            difficulty_level=self.game_settings.difficulty_level,
            deck_type=self.game_settings.deck_type,
            draw_count=self.game_settings.draw_count,
            shuffle_mode=self.game_settings.shuffle_mode
        )
        
        # Mark session as active (dirty shutdown tracking)
        self.session_tracker.start_session(
            self.profile_service.active_profile.profile_id,
            game_config={
                "timer_enabled": self.current_session_outcome.timer_enabled,
                "timer_limit": self.current_session_outcome.timer_limit,
                "timer_mode": self.current_session_outcome.timer_mode,
                "scoring_enabled": self.current_session_outcome.scoring_enabled,
                "difficulty_level": self.current_session_outcome.difficulty_level,
                "deck_type": self.current_session_outcome.deck_type,
                "draw_count": self.current_session_outcome.draw_count,
                "shuffle_mode": self.current_session_outcome.shuffle_mode
            }
        )
    
    def end_game(self, end_reason: EndReason) -> None:
        """End game and record session.
        
        CHANGED: New signature with EndReason (was is_victory: bool).
        
        Args:
            end_reason: Why game ended (victory, abandon, timeout)
        """
        if not self.current_session_outcome:
            return  # No active game
        
        # Finalize SessionOutcome
        self.current_session_outcome.end_reason = end_reason
        self.current_session_outcome.is_victory = end_reason in (
            EndReason.VICTORY, EndReason.VICTORY_OVERTIME
        )
        self.current_session_outcome.elapsed_time = self.game_service.get_elapsed_time()
        self.current_session_outcome.timer_expired = self.game_service.timer_expired
        self.current_session_outcome.overtime_duration = self._calculate_overtime()
        
        # Populate gameplay stats from GameService
        self.current_session_outcome.move_count = self.game_service.move_count
        self.current_session_outcome.draw_count_actions = self.game_service.draw_count
        self.current_session_outcome.recycle_count = self.game_service.recycle_count
        self.current_session_outcome.foundation_cards = list(self.game_service.carte_per_seme)
        self.current_session_outcome.completed_suits = self.game_service.semi_completati
        
        # Populate scoring if enabled
        if self.current_session_outcome.scoring_enabled:
            final_score = self.scoring_service.calculate_final_score(
                # ... existing params ...
            )
            self.current_session_outcome.final_score = final_score.total_score
            self.current_session_outcome.base_score = final_score.base_score
            self.current_session_outcome.difficulty_multiplier = final_score.difficulty_multiplier
            self.current_session_outcome.deck_bonus = final_score.deck_bonus
            self.current_session_outcome.quality_multiplier = final_score.quality_multiplier
        
        # Record session (update aggregates + save)
        self.profile_service.record_session(self.current_session_outcome)
        
        # Clean session tracker (clean exit)
        self.session_tracker.end_session()
        
        # Clear current session
        self.current_session_outcome = None
    
    def _get_timer_mode(self) -> str:
        """Derive timer mode from settings."""
        if self.game_settings.max_time_game == 0:
            return "OFF"
        return "STRICT" if self.game_settings.timer_strict_mode else "PERMISSIVE"
    
    def _calculate_overtime(self) -> float:
        """Calculate overtime duration."""
        if not self.current_session_outcome.timer_enabled:
            return 0.0
        if not self.current_session_outcome.timer_expired:
            return 0.0
        
        elapsed = self.game_service.get_elapsed_time()
        limit = self.current_session_outcome.timer_limit
        
        return max(0.0, elapsed - limit)
```

**Test Coverage** (`tests/integration/test_profile_integration.py`):
- ✅ New game creates SessionOutcome
- ✅ End game (victory) records session
- ✅ End game (abandon) records session
- ✅ Aggregates updated correctly
- ✅ Session tracker cleaned on end
- ✅ Overtime calculation (PERMISSIVE)

**Estimated Time**: 15-20 min  
**Test Count**: 8-10

---

### Commit 4.2: App Startup Integration (Orphaned Session Recovery)

**File Modification**: `src/main.py` (or equivalent app entry point)

**Changes**:

```python
from src.infrastructure.di_container import get_container
from src.domain.services.session_tracker import SessionTracker
from src.infrastructure.logging import game_logger as log  # ADDED: Logging


class SolitaireApp(wx.App):
    def OnInit(self):
        # ... existing init ...
        
        # Initialize DI Container
        container = get_container()
        
        # Initialize ProfileService
        self.profile_service = container.get_profile_service()
        self.profile_service.initialize()
        
        # Log storage path for user reference
        log.info_query_requested(
            "app_startup",
            f"Profile data stored in: {self.profile_service.profile_storage.PROFILES_DIR}"
        )
        
        # Check for orphaned session (dirty shutdown recovery)
        session_tracker = SessionTracker()
        if session_tracker.has_orphaned_session():
            orphaned = session_tracker.recover_orphaned_session()
            if orphaned:
                # Record as ABANDON_APP_CLOSE
                self.profile_service.record_session(orphaned)
                
                log.warning_issued(
                    "AppStartup",
                    f"Recovered orphaned session: {orphaned.session_id} (registered as defeat)"
                )
        
        # ... continue with existing init ...
        return True
```

**Test Coverage** (`tests/integration/test_profile_integration.py`):
- ✅ App startup with orphaned session
- ✅ Orphaned session recorded as ABANDON_APP_CLOSE
- ✅ Session tracker cleaned after recovery

**Estimated Time**: 8-10 min  
**Test Count**: 3-4

---

## 🏗️ PHASE 5: DI Container Integration (NEW)

### Commit 5.1: Update DI Container with Profile Services

**File Modification**: `src/infrastructure/di_container.py`

**Changes**:

```python
# Add to existing DIContainer class

class DIContainer:
    # ... existing methods ...
    
    # ========================================
    # PROFILE SERVICES (NEW)
    # ========================================
    
    def get_profile_service(self):
        """Get or create ProfileService singleton.
        
        ProfileService manages user profiles and statistics.
        
        Returns:
            ProfileService singleton
        """
        if "profile_service" not in self._instances:
            from src.domain.services.profile_service import ProfileService
            
            # Inject storage dependencies
            profile_storage = self.get_profile_storage()
            session_storage = self.get_session_storage()
            
            self._instances["profile_service"] = ProfileService(
                profile_storage=profile_storage,
                session_storage=session_storage
            )
        
        return self._instances["profile_service"]
    
    def get_profile_storage(self):
        """Get or create ProfileStorage singleton.
        
        Returns:
            ProfileStorage singleton
        """
        if "profile_storage" not in self._instances:
            from src.infrastructure.storage.profile_storage import ProfileStorage
            self._instances["profile_storage"] = ProfileStorage()
        
        return self._instances["profile_storage"]
    
    def get_session_storage(self):
        """Get or create SessionStorage singleton.
        
        Returns:
            SessionStorage singleton
        """
        if "session_storage" not in self._instances:
            from src.infrastructure.storage.session_storage import SessionStorage
            self._instances["session_storage"] = SessionStorage()
        
        return self._instances["session_storage"]
```

**Test Coverage** (`tests/unit/test_di_container.py`):
- ✅ `get_profile_service()` returns singleton
- ✅ `get_profile_storage()` returns singleton
- ✅ `get_session_storage()` returns singleton
- ✅ Dependencies injected correctly

**Estimated Time**: 10-12 min  
**Test Count**: 3-4

---

## ✅ Testing Strategy

### Unit Tests (Per-Commit)

**Coverage Target**: ≥90% per module

**Test Pyramid**:
- **Models** (40% tests): Data integrity, serialization
- **Storage** (30% tests): JSON read/write, edge cases, atomic writes
- **Services** (30% tests): Business logic, aggregation

### Integration Tests (Phase 4)

**Scenarios**:
1. **End-to-end session**: New game → play → victory → aggregates updated
2. **Dirty shutdown**: New game → app close → restart → orphan recovered
3. **Profile switching**: Play as Profile A → switch to Profile B → play → verify isolation
4. **Guest mode**: Play as guest → verify separate stats
5. **Record updates**: Beat personal record → verify update
6. **Atomic write resilience**: Simulate crash during save → verify no corruption

### Test Utilities

**File**: `tests/fixtures/profile_fixtures.py`

```python
"""Test fixtures for profile testing."""

from src.domain.models.profile import UserProfile, SessionOutcome, EndReason
from src.domain.models.statistics import GlobalStats
from datetime import datetime

def create_test_profile(name="Test", is_guest=False) -> UserProfile:
    return UserProfile.create_new(name, is_guest)

def create_test_outcome(is_victory=True, **kwargs) -> SessionOutcome:
    defaults = {
        "profile_id": "test-uuid",
        "end_reason": EndReason.VICTORY if is_victory else EndReason.ABANDON_EXIT,
        "is_victory": is_victory,
        "elapsed_time": 300.0,
        "timer_enabled": False,
        "timer_limit": 0,
        "timer_mode": "OFF",
        "timer_expired": False,
        "scoring_enabled": True,
        "final_score": 800,
        "difficulty_level": 3,
        "deck_type": "french",
        "draw_count": 1,
        "shuffle_mode": "invert",
        "move_count": 50,
        "draw_count_actions": 10,
        "recycle_count": 2,
        "foundation_cards": [13,13,13,13],
        "completed_suits": 4 if is_victory else 0
    }
    defaults.update(kwargs)
    return SessionOutcome.create_new(**defaults)
```

---

## 📊 Commit Strategy Summary (UPDATED)

| Phase | Commit | Description | Time | Tests |
|---|---|---|---|---|
| **1. Models** | 1.1 | Core Profile Models (UserProfile, SessionOutcome, EndReason) | 10-12 min | 6-8 |
| | 1.2 | Statistics Aggregates (GlobalStats, TimerStats, etc.) | 12-15 min | 10-12 |
| **2. Storage** | 2.1 | ProfileStorage (JSON + atomic write + logging) | 20-25 min | 10-12 |
| | 2.2 | SessionStorage (append-only + atomic + logging) | 12-18 min | 8-10 |
| **3. Services** | 3.1 | ProfileService (CRUD + aggregation + DI-compatible) | 20-25 min | 12-15 |
| | 3.2 | SessionTracker (dirty shutdown recovery + logging) | 10-12 min | 5-6 |
| **4. Integration** | 4.1 | GameEngine hooks (session recording + imports fixed) | 15-20 min | 8-10 |
| | 4.2 | App startup (orphan recovery + logging) | 8-10 min | 3-4 |
| **5. DI Container** | 5.1 | DI container extension (profile services) | 10-12 min | 3-4 |
| **TOTAL** | **9 commits** | | **110-141 min** | **63-81 tests** |

**Realistic Estimate**: GitHub Copilot Agent completes backend in **2-2.5 hours** (was 1.5-2h).

**Delta from Original**: +1 commit, +10 min, +5 tests (critical fixes applied).

---

## 🚦 Validation Checklist

Before declaring backend complete:

- [ ] All 9 commits merged to `refactoring-engine`
- [ ] Test coverage ≥90% overall
- [ ] All integration tests passing
- [ ] **Manual test: Create profile → play game → verify JSON files in `~/.solitario/profiles/`**
- [ ] Manual test: Dirty shutdown → restart → verify orphan recovered
- [ ] Manual test: Guest mode → verify isolated stats
- [ ] Manual test: Atomic write safety (kill app during save, verify no corruption)
- [ ] Documentation: Update API.md with ProfileService methods
- [ ] No UI changes in this phase (pure backend)
- [ ] Logging working (check logs for profile operations)

---

## 🎯 Next Steps After Backend

1. **Timer System v2.7.0** implementation (populates `timer_expired`, `overtime_duration`)
2. **Statistics Presentation v3.0.0** frontend (dialog, formatters, TTS)
3. **UI Integration** (Gestione Profili menu, profile selection)

---

## 🔗 Known Limitations (Deferred to v3.1)

### Sessions File Growth

**Issue**: `sessions_<uuid>.json` grows unbounded (append-only).

**Impact**: After 1000+ games (~500KB file), `load_all_sessions()` slows down.

**Mitigation v3.0**:
- UI uses `load_recent_sessions(limit=50)` (cached in profile)
- Full history load only on-demand (user request)

**Solution v3.1**:
- Archiving: Move sessions older than 365 days to `sessions_<uuid>_archive_2025.json`
- Pagination: Always use offset/limit, never load full history

### Backup Strategy

**Issue**: No automated backups.

**Mitigation v3.0**:
- Atomic writes prevent corruption
- User can manually backup `~/.solitario/profiles/` folder
- Log path at startup for discoverability

**Solution v3.1**:
- Automatic daily backups to `~/.solitario/backups/`
- Keep last 7 days (FIFO cleanup)
- Compression with `gzip`

---

## 📚 Riferimenti

- **Design Doc**: [DESIGN_PROFILE_STATISTICS_SYSTEM.md](../2%20-%20projects/DESIGN_PROFILE_STATISTICS_SYSTEM.md)
- **Timer Design**: [DESIGN_TIMER_MODE_SYSTEM.md](../2%20-%20projects/DESIGN_TIMER_MODE_SYSTEM.md)
- **Stats Presentation**: [DESIGN_STATISTICS_PRESENTATION.md](../2%20-%20projects/DESIGN_STATISTICS_PRESENTATION.md)
- **Codebase**: [refactoring-engine branch](https://github.com/Nemex81/solitario-classico-accessibile/tree/refactoring-engine)
- **ScoreStorage Pattern**: [score_storage.py](https://github.com/Nemex81/solitario-classico-accessibile/blob/refactoring-engine/src/infrastructure/storage/score_storage.py)

---

**Documento creato**: 17 Febbraio 2026, 12:50 CET  
**Ultimo Aggiornamento**: 17 Febbraio 2026, 13:30 CET  
**Autore**: Luca (utente) + Perplexity AI (technical planning + review fixes)  
**Status**: **Ready for Copilot Agent execution** ✅  
**Estimated Completion**: 2-2.5 hours agent time
