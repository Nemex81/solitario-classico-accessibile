# Implementation Guide: Scoring System v2.0.0

**Feature**: Complete scoring system with configurable difficulty levels, bonuses, and statistics tracking  
**Version**: 2.0.0  
**Branch**: `refactoring-engine`  
**Estimated Effort**: 3.5 hours (Copilot) + 1.5 hours (review/testing)  
**Commits**: 7-8 atomic commits  
**Date**: 2026-02-11

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Phase 1: Domain Models](#phase-1-domain-models)
4. [Phase 2: Domain Service](#phase-2-domain-service)
5. [Phase 3: GameSettings Extension](#phase-3-gamesettings-extension)
6. [Phase 4: GameService Integration](#phase-4-gameservice-integration)
7. [Phase 5: Application Controllers](#phase-5-application-controllers)
8. [Phase 6: Presentation Formatters](#phase-6-presentation-formatters)
9. [Phase 7: Infrastructure Storage](#phase-7-infrastructure-storage)
10. [Testing Strategy](#testing-strategy)
11. [Validation & Acceptance](#validation--acceptance)

---

## Overview

### Goals

Implement a complete, Microsoft Solitaire-style scoring system with:

1. **Real-time score calculation** based on player actions
2. **Configurable difficulty** (5 levels with progressive constraints)
3. **Multiple bonuses/multipliers** (deck type, draw count, timer, difficulty)
4. **Optional system** (ON/OFF toggle for free-play mode)
5. **Persistent statistics** (best scores, history)
6. **Full accessibility** (TTS announcements, screen reader optimized)

### Key Features

- **Base scoring**: Points per action (waste→foundation: +10, reveal card: +5, etc.)
- **Deck type bonus**: +150 for French deck (52 cards vs 40 Neapolitan)
- **Difficulty multiplier**: x1.0 to x2.5 based on level
- **Draw count bonus**: +0/+100/+200 for 1/2/3 cards (levels 1-3 only)
- **Time bonus**: Progressive decay formula (faster = more points)
- **Victory bonus**: +500 if player wins
- **Constraints**: Levels 4-5 enforce timer, draw count, recycle mode restrictions

### Design Principles

1. **Clean Architecture**: Domain → Application → Presentation → Infrastructure
2. **Immutable scoring**: All score results are frozen dataclasses
3. **Optional dependency**: ScoringService can be None (free-play mode)
4. **Zero breaking changes**: Existing gameplay unaffected if scoring disabled
5. **Testability**: Pure functions, mockable dependencies

---

## Architecture

### Layer Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ ScoreFormatter                                        │   │
│  │ - format_provisional_score()                          │   │
│  │ - format_final_score()                                │   │
│  │ - format_score_event()                                │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│  ┌────────────────────────┐  ┌─────────────────────────┐    │
│  │ OptionsController      │  │ GameplayController      │    │
│  │ - cycle_difficulty()   │  │ - show_current_score()  │    │
│  │ - cycle_draw_count()   │  │ - show_score_breakdown()│    │
│  │ - toggle_scoring()     │  └─────────────────────────┘    │
│  └────────────────────────┘                                  │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌─────────────────────────────────────────────────────────────┐
│                      DOMAIN LAYER                            │
│  ┌────────────────────────┐  ┌─────────────────────────┐    │
│  │ GameSettings           │  │ ScoringService          │    │
│  │ - difficulty_level: int│  │ - record_event()        │    │
│  │ - draw_count: int      │  │ - calc_provisional()    │    │
│  │ - scoring_enabled: bool│  │ - calc_final_score()    │    │
│  │ - validate_*()         │  └─────────────────────────┘    │
│  └────────────────────────┘                                  │
│  ┌────────────────────────┐  ┌─────────────────────────┐    │
│  │ Scoring Models         │  │ GameService             │    │
│  │ - ScoringConfig        │  │ - scoring: Optional[...]│    │
│  │ - ScoreEvent           │  │ - move_card() [+event]  │    │
│  │ - ProvisionalScore     │  │ - recycle() [+event]    │    │
│  │ - FinalScore           │  └─────────────────────────┘    │
│  └────────────────────────┘                                  │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌─────────────────────────────────────────────────────────────┐
│                  INFRASTRUCTURE LAYER                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ ScoreStorage                                          │   │
│  │ - save_score(FinalScore)                              │   │
│  │ - load_all_scores() → List[Dict]                      │   │
│  │ - get_best_score(deck, difficulty) → Dict            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### File Structure

```
src/
├── domain/
│   ├── models/
│   │   └── scoring.py                    # NEW: Score models
│   └── services/
│       ├── game_settings.py              # MODIFIED: +draw_count, +scoring_enabled, +validation
│       ├── game_service.py               # MODIFIED: +scoring integration
│       └── scoring_service.py            # NEW: Scoring logic
├── application/
│   ├── game_engine.py                    # MODIFIED: +scoring factory
│   ├── gameplay_controller.py            # MODIFIED: +score commands
│   └── options_controller.py             # MODIFIED: +option 3,7
├── presentation/
│   └── formatters/
│       └── score_formatter.py            # NEW: TTS messages
└── infrastructure/
    └── storage/
        └── score_storage.py              # NEW: JSON persistence

tests/
├── unit/
│   ├── test_scoring_models.py            # NEW: 15 tests
│   ├── test_scoring_service.py           # NEW: 20 tests
│   └── test_game_settings_validation.py  # NEW: 15 tests
└── integration/
    ├── test_scoring_integration.py       # NEW: 12 tests
    └── test_difficulty_constraints.py    # NEW: 8 tests

docs/
├── IMPLEMENTATION_SCORING_SYSTEM.md      # THIS FILE
└── TODO_SCORING.md                       # Tracking checklist
```

---

## Phase 1: Domain Models

### File: `src/domain/models/scoring.py`

**Purpose**: Define immutable data structures for scoring system.

### 1.1 ScoreEventType Enum

```python
from enum import Enum

class ScoreEventType(Enum):
    """Types of scoring events."""
    # Positive events
    WASTE_TO_FOUNDATION = "waste_to_foundation"          # +10 points
    TABLEAU_TO_FOUNDATION = "tableau_to_foundation"      # +10 points
    CARD_REVEALED = "card_revealed"                      # +5 points
    
    # Negative events
    FOUNDATION_TO_TABLEAU = "foundation_to_tableau"      # -15 points
    RECYCLE_WASTE = "recycle_waste"                      # -20 after 3rd
    
    # Neutral events (tracking only)
    CARDS_DRAWN = "cards_drawn"                          # 0 points
    MOVE_TABLEAU = "move_tableau"                        # 0 points
```

### 1.2 ScoringConfig Dataclass

```python
from dataclasses import dataclass, field
from typing import Dict

@dataclass(frozen=True)
class ScoringConfig:
    """Immutable scoring rules configuration."""
    
    # Base points (Microsoft Standard)
    points_waste_to_tableau: int = 5
    points_waste_to_foundation: int = 10
    points_tableau_to_foundation: int = 10
    points_card_revealed: int = 5
    points_foundation_to_tableau: int = -15
    
    # Penalties
    penalty_recycle_after_third: int = -20
    penalty_undo_move: int = -5  # Future
    
    # Deck type bonus (additive)
    deck_type_bonus: Dict[str, int] = field(default_factory=lambda: {
        "napoletano": 0,
        "francese": 150
    })
    
    # Difficulty multiplier (multiplicative)
    difficulty_multiplier: Dict[int, float] = field(default_factory=lambda: {
        1: 1.0,    # Facile
        2: 1.25,   # Medio
        3: 1.5,    # Difficile
        4: 2.0,    # Esperto (constraints)
        5: 2.5     # Maestro (stricter)
    })
    
    # Draw count bonus (additive, levels 1-3 only)
    draw_count_bonus: Dict[int, int] = field(default_factory=lambda: {
        1: 0,
        2: 100,
        3: 200
    })
    
    # Recycle mode multiplier (stock/waste events only)
    recycle_mode_multiplier: Dict[str, float] = field(default_factory=lambda: {
        "inverted": 1.0,    # Harder
        "shuffled": 0.85    # Easier
    })
    
    # Victory bonus
    victory_bonus_base: int = 500
    
    # Minimum score
    min_score: int = 0
```

### 1.3 ScoreEvent Dataclass

```python
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(frozen=True)
class ScoreEvent:
    """Single scoring event (immutable)."""
    event_type: ScoreEventType
    points: int
    timestamp: float
    context: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        return f"{self.event_type.value}: {self.points:+d} punti"
```

### 1.4 ProvisionalScore Dataclass

```python
@dataclass(frozen=True)
class ProvisionalScore:
    """Intermediate score during gameplay."""
    total_score: int
    base_score: int
    deck_bonus: int
    draw_bonus: int
    difficulty_multiplier: float
    estimated_time_bonus: int
```

### 1.5 FinalScore Dataclass

```python
@dataclass(frozen=True)
class FinalScore:
    """Final score with complete breakdown."""
    # Scores
    total_score: int
    base_score: int
    deck_bonus: int
    draw_bonus: int
    difficulty_multiplier: float
    time_bonus: int
    victory_bonus: int
    
    # Events
    events: Tuple[ScoreEvent, ...]
    
    # Game stats
    elapsed_seconds: int
    move_count: int
    recycle_count: int
    cards_revealed: int
    is_victory: bool
    
    # Configuration snapshot
    deck_type: str
    difficulty_level: int
    draw_count: int
    recycle_mode: str
    
    def get_breakdown(self) -> str:
        """Detailed TTS-friendly breakdown."""
        lines = [
            f"Punteggio finale: {self.total_score} punti",
            f"Punteggio base: {self.base_score}",
        ]
        
        if self.deck_bonus > 0:
            lines.append(f"Bonus mazzo: +{self.deck_bonus}")
        
        if self.draw_bonus > 0:
            lines.append(f"Bonus carte: +{self.draw_bonus}")
        
        if self.difficulty_multiplier > 1.0:
            perc = int((self.difficulty_multiplier - 1.0) * 100)
            lines.append(f"Moltiplicatore difficoltà: +{perc}%")
        
        if self.time_bonus > 0:
            lines.append(f"Bonus tempo: +{self.time_bonus}")
        elif self.time_bonus < 0:
            lines.append(f"Penalità tempo: {self.time_bonus}")
        
        if self.victory_bonus > 0:
            lines.append(f"Bonus vittoria: +{self.victory_bonus}")
        
        lines.append(f"Mosse: {self.move_count}, Tempo: {self.elapsed_seconds}s")
        
        return "\n".join(lines)
```

### Testing Phase 1

**File**: `tests/unit/test_scoring_models.py`

```python
def test_scoring_config_defaults():
    """Test default scoring configuration."""
    config = ScoringConfig()
    assert config.points_waste_to_foundation == 10
    assert config.difficulty_multiplier[4] == 2.0
    assert config.deck_type_bonus["francese"] == 150

def test_score_event_immutable():
    """Test ScoreEvent immutability."""
    event = ScoreEvent(
        event_type=ScoreEventType.CARD_REVEALED,
        points=5,
        timestamp=123.45
    )
    with pytest.raises(FrozenInstanceError):
        event.points = 10

def test_final_score_breakdown():
    """Test breakdown message generation."""
    score = FinalScore(
        total_score=1500,
        base_score=800,
        deck_bonus=150,
        difficulty_multiplier=2.0,
        # ... other fields
    )
    breakdown = score.get_breakdown()
    assert "1500 punti" in breakdown
    assert "Bonus mazzo: +150" in breakdown
```

**Commit 1**: `feat(domain): Add scoring system models and configuration`

---

## Phase 2: Domain Service

### File: `src/domain/services/scoring_service.py`

**Purpose**: Pure business logic for score calculation (no I/O, no side effects).

### 2.1 ScoringService Class

```python
from typing import List, Optional
import time
import math

class ScoringService:
    """Domain service for score calculation."""
    
    def __init__(self, config: Optional[ScoringConfig] = None):
        self.config = config or ScoringConfig()
        self._base_score: int = 0
        self._events: List[ScoreEvent] = []
        self._recycle_count: int = 0
        self._cards_revealed: int = 0
    
    def record_event(
        self,
        event_type: ScoreEventType,
        context: Optional[dict] = None
    ) -> int:
        """Record event and return points gained.
        
        Args:
            event_type: Type of scoring event
            context: Optional context (card names, etc.)
            
        Returns:
            Points gained/lost (can be negative)
        """
        points = self._calculate_event_points(event_type)
        
        event = ScoreEvent(
            event_type=event_type,
            points=points,
            timestamp=time.time(),
            context=context or {}
        )
        
        self._events.append(event)
        self._base_score += points
        
        # Update counters
        if event_type == ScoreEventType.RECYCLE_WASTE:
            self._recycle_count += 1
        elif event_type == ScoreEventType.CARD_REVEALED:
            self._cards_revealed += 1
        
        return points
    
    def _calculate_event_points(self, event_type: ScoreEventType) -> int:
        """Calculate points for single event."""
        if event_type == ScoreEventType.WASTE_TO_FOUNDATION:
            return self.config.points_waste_to_foundation
        elif event_type == ScoreEventType.TABLEAU_TO_FOUNDATION:
            return self.config.points_tableau_to_foundation
        elif event_type == ScoreEventType.CARD_REVEALED:
            return self.config.points_card_revealed
        elif event_type == ScoreEventType.FOUNDATION_TO_TABLEAU:
            return self.config.points_foundation_to_tableau
        elif event_type == ScoreEventType.RECYCLE_WASTE:
            # Penalty after 3rd recycle
            if self._recycle_count >= 3:
                return self.config.penalty_recycle_after_third
            return 0
        else:
            return 0
```

### 2.2 Provisional Score Calculation

```python
def calculate_provisional_score(
    self,
    elapsed_seconds: int,
    max_time: Optional[int],
    deck_type: str,
    difficulty_level: int,
    draw_count: int,
    recycle_mode: str
) -> ProvisionalScore:
    """Calculate current score (in-game).
    
    Formula:
    1. base_score (from events)
    2. + deck_bonus
    3. + draw_bonus (levels 1-3 only)
    4. * difficulty_multiplier
    5. + estimated_time_bonus
    6. Clamp to min_score
    """
    score = self._base_score
    
    # Deck bonus
    deck_bonus = self.config.deck_type_bonus.get(deck_type, 0)
    score += deck_bonus
    
    # Draw count bonus (only levels 1-3)
    draw_bonus = 0
    if difficulty_level <= 3:
        draw_bonus = self.config.draw_count_bonus.get(draw_count, 0)
        score += draw_bonus
    
    # Difficulty multiplier
    difficulty_mult = self.config.difficulty_multiplier.get(difficulty_level, 1.0)
    score = int(score * difficulty_mult)
    
    # Time bonus (provisional)
    time_bonus = self._calculate_time_bonus(elapsed_seconds, max_time)
    score += time_bonus
    
    # Clamp
    score = max(self.config.min_score, score)
    
    return ProvisionalScore(
        total_score=score,
        base_score=self._base_score,
        deck_bonus=deck_bonus,
        draw_bonus=draw_bonus,
        difficulty_multiplier=difficulty_mult,
        estimated_time_bonus=time_bonus
    )
```

### 2.3 Final Score Calculation

```python
def calculate_final_score(
    self,
    elapsed_seconds: int,
    max_time: Optional[int],
    deck_type: str,
    difficulty_level: int,
    draw_count: int,
    recycle_mode: str,
    move_count: int,
    is_victory: bool
) -> FinalScore:
    """Calculate final score (game end).
    
    Same as provisional + victory_bonus if won.
    """
    score = self._base_score
    
    deck_bonus = self.config.deck_type_bonus.get(deck_type, 0)
    score += deck_bonus
    
    draw_bonus = 0
    if difficulty_level <= 3:
        draw_bonus = self.config.draw_count_bonus.get(draw_count, 0)
        score += draw_bonus
    
    difficulty_mult = self.config.difficulty_multiplier.get(difficulty_level, 1.0)
    score = int(score * difficulty_mult)
    
    time_bonus = self._calculate_time_bonus(elapsed_seconds, max_time)
    score += time_bonus
    
    victory_bonus = 0
    if is_victory:
        victory_bonus = self.config.victory_bonus_base
        score += victory_bonus
    
    score = max(self.config.min_score, score)
    
    return FinalScore(
        total_score=score,
        base_score=self._base_score,
        deck_bonus=deck_bonus,
        draw_bonus=draw_bonus,
        difficulty_multiplier=difficulty_mult,
        time_bonus=time_bonus,
        victory_bonus=victory_bonus,
        events=tuple(self._events),
        elapsed_seconds=elapsed_seconds,
        move_count=move_count,
        recycle_count=self._recycle_count,
        cards_revealed=self._cards_revealed,
        is_victory=is_victory,
        deck_type=deck_type,
        difficulty_level=difficulty_level,
        draw_count=draw_count,
        recycle_mode=recycle_mode
    )
```

### 2.4 Time Bonus Formula

```python
def _calculate_time_bonus(
    self,
    elapsed_seconds: int,
    max_time: Optional[int]
) -> int:
    """Calculate time bonus with progressive decay.
    
    Timer OFF: 10000 / sqrt(elapsed) - rewards speed
    Timer ON: Percentage-based bonuses
    
    Examples:
        300s (5min), no timer → 577 points
        3600s (60min), timer 3600s → -500 (expired)
        1200s (20min), timer 3600s → 1000 (>50% remaining)
    """
    if max_time is None or max_time <= 0:
        # Timer OFF: inverse square root
        if elapsed_seconds <= 0:
            return 1000
        bonus = int(10000 / math.sqrt(elapsed_seconds))
        return min(bonus, 2000)  # Cap at 2000
    else:
        # Timer ON: percentage-based
        remaining = max(0, max_time - elapsed_seconds)
        percentage = (remaining / max_time) * 100
        
        if remaining <= 0:
            return -500  # Expired
        elif percentage >= 50:
            return 1000  # Fast
        elif percentage >= 25:
            return 500   # Medium
        else:
            return 200   # Just in time
```

### 2.5 State Queries

```python
def get_base_score(self) -> int:
    """Get current base score."""
    return self._base_score

def get_event_count(self) -> int:
    """Get total events recorded."""
    return len(self._events)

def get_recent_events(self, count: int = 5) -> List[ScoreEvent]:
    """Get last N events."""
    return self._events[-count:]

def reset(self) -> None:
    """Reset for new game."""
    self._base_score = 0
    self._events.clear()
    self._recycle_count = 0
    self._cards_revealed = 0
```

### Testing Phase 2

**File**: `tests/unit/test_scoring_service.py`

```python
def test_record_event_waste_to_foundation():
    """Test recording waste→foundation event."""
    service = ScoringService()
    points = service.record_event(ScoreEventType.WASTE_TO_FOUNDATION)
    assert points == 10
    assert service.get_base_score() == 10

def test_recycle_penalty_after_third():
    """Test recycle penalty after 3rd recycle."""
    service = ScoringService()
    
    # First 3 recycles: no penalty
    for _ in range(3):
        points = service.record_event(ScoreEventType.RECYCLE_WASTE)
        assert points == 0
    
    # 4th recycle: -20 penalty
    points = service.record_event(ScoreEventType.RECYCLE_WASTE)
    assert points == -20

def test_time_bonus_no_timer():
    """Test time bonus with timer OFF."""
    service = ScoringService()
    bonus = service._calculate_time_bonus(300, None)  # 5 minutes
    assert 550 <= bonus <= 600  # ~577

def test_provisional_score_calculation():
    """Test provisional score with multipliers."""
    service = ScoringService()
    service.record_event(ScoreEventType.WASTE_TO_FOUNDATION)  # +10
    
    provisional = service.calculate_provisional_score(
        elapsed_seconds=300,
        max_time=None,
        deck_type="francese",
        difficulty_level=4,
        draw_count=3,
        recycle_mode="inverted"
    )
    
    # base=10, deck=+150, draw=0 (level 4), mult=2.0, time=~577
    # (10 + 150) * 2.0 + 577 = 897
    assert 850 <= provisional.total_score <= 950
```

**Commit 2**: `feat(domain): Implement ScoringService with event recording and calculations`

---

## Phase 3: GameSettings Extension

### File: `src/domain/services/game_settings.py` (MODIFY)

**Purpose**: Add new options (draw_count, scoring_enabled) and validation logic.

### 3.1 New Attributes

```python
class GameSettings:
    def __init__(self, game_state=None):
        # Existing attributes
        self.deck_type = "french"
        self.difficulty_level = 1  # NOW: 1-5 (was 1-3)
        self.max_time_game = -1
        self.shuffle_discards = False
        self.command_hints_enabled = True
        
        # NEW: Draw count (separated from difficulty)
        self.draw_count = 1  # 1, 2, or 3 cards per stock draw
        
        # NEW: Scoring system toggle
        self.scoring_enabled = True  # True=scoring, False=free-play
        
        self.game_state = game_state or GameState()
```

### 3.2 Modified: cycle_difficulty (1-5 levels)

```python
def cycle_difficulty(self) -> Tuple[bool, str]:
    """Cycle difficulty: 1 → 2 → 3 → 4 → 5 → 1.
    
    Levels 4-5 enforce constraints on other settings.
    
    Returns:
        Tuple[bool, str]: (success, message)
    """
    if not self.validate_not_running():
        return (False, "Non puoi modificare la difficoltà durante una partita!")
    
    # Cycle through 5 levels
    self.difficulty_level = (self.difficulty_level % 5) + 1
    
    # Apply constraints for levels 4-5
    constraint_msgs = []
    
    # Validate draw count
    valid, adjusted, msg = self.validate_draw_count_for_level(self.draw_count)
    if not valid:
        self.draw_count = adjusted
        constraint_msgs.append(msg)
    
    # Validate timer
    valid, adjusted, msg = self.validate_timer_for_level(self.max_time_game)
    if not valid:
        self.max_time_game = adjusted
        constraint_msgs.append(msg)
    
    # Validate shuffle mode
    valid, msg = self.validate_shuffle_for_level()
    if not valid:
        constraint_msgs.append(msg)
    
    base_msg = f"Difficoltà impostata a: Livello {self.difficulty_level}."
    if constraint_msgs:
        return (True, base_msg + " " + " ".join(constraint_msgs))
    return (True, base_msg)
```

### 3.3 NEW: cycle_draw_count (Option 3)

```python
def cycle_draw_count(self) -> Tuple[bool, str]:
    """Cycle draw count: 1 → 2 → 3 → 1.
    
    Validates against difficulty constraints:
    - Level 4: Minimum 2 cards
    - Level 5: Fixed at 3 cards
    
    Returns:
        Tuple[bool, str]: (success, message)
    """
    if not self.validate_not_running():
        return (False, "Non puoi modificare il numero di carte durante una partita!")
    
    # Cycle
    self.draw_count = (self.draw_count % 3) + 1
    
    # Validate against difficulty
    valid, adjusted, msg = self.validate_draw_count_for_level(self.draw_count)
    if not valid:
        self.draw_count = adjusted
        return (True, msg)
    
    return (True, f"Carte per pesca impostate a: {self.draw_count}.")
```

### 3.4 NEW: toggle_scoring (Option 7)

```python
def toggle_scoring(self) -> Tuple[bool, str]:
    """Toggle scoring system ON/OFF.
    
    Returns:
        Tuple[bool, str]: (success, message)
    """
    if not self.validate_not_running():
        return (False, "Non puoi modificare il sistema punti durante una partita!")
    
    self.scoring_enabled = not self.scoring_enabled
    
    if self.scoring_enabled:
        return (True, "Sistema punti attivo. Punteggi saranno calcolati e salvati.")
    else:
        return (True, "Modalità free-play attiva. Nessun calcolo punteggi.")
```

### 3.5 Validation Helpers

```python
def validate_draw_count_for_level(self, requested: int) -> Tuple[bool, int, str]:
    """Validate draw_count against difficulty constraints.
    
    Returns:
        Tuple[bool, int, str]: (valid, adjusted_value, message)
    """
    if self.difficulty_level <= 3:
        # No constraints
        return True, requested, ""
    elif self.difficulty_level == 4:
        # Level 4: Minimum 2 cards
        if requested < 2:
            return False, 2, "Livello Esperto: minimo 2 carte per pesca."
        return True, requested, ""
    else:  # Level 5
        # Level 5: Fixed at 3 cards
        if requested != 3:
            return False, 3, "Livello Maestro: 3 carte obbligatorie."
        return True, 3, ""

def validate_timer_for_level(self, requested: int) -> Tuple[bool, int, str]:
    """Validate timer against difficulty constraints."""
    if self.difficulty_level <= 3:
        return True, requested, ""
    elif self.difficulty_level == 4:
        # Level 4: Timer required, min 30 min
        if requested <= 0:
            return False, 1800, "Livello Esperto: timer obbligatorio (min 30 minuti)."
        if requested < 1800:  # 30 minutes
            return False, 1800, "Livello Esperto: timer minimo 30 minuti."
        return True, requested, ""
    else:  # Level 5
        # Level 5: Timer required, 15-30 min range
        if requested <= 0:
            return False, 900, "Livello Maestro: timer obbligatorio (min 15 minuti)."
        if requested < 900:  # 15 minutes
            return False, 900, "Livello Maestro: timer minimo 15 minuti."
        if requested > 1800:  # 30 minutes
            return False, 1800, "Livello Maestro: timer massimo 30 minuti."
        return True, requested, ""

def validate_shuffle_for_level(self) -> Tuple[bool, str]:
    """Validate shuffle mode against difficulty constraints."""
    if self.difficulty_level <= 3:
        return True, ""
    else:  # Levels 4-5
        # Shuffle locked to invert-only
        if self.shuffle_discards:
            self.shuffle_discards = False
            return False, f"Livello {self.difficulty_level}: riciclo bloccato su Inversione Semplice."
        return True, ""
```

### 3.6 Updated Getters

```python
def get_draw_count_display(self) -> str:
    """Get human-readable draw count."""
    return f"{self.draw_count} carta/e"

def get_difficulty_display(self) -> str:
    """Get human-readable difficulty with level name."""
    names = {1: "Facile", 2: "Medio", 3: "Difficile", 4: "Esperto", 5: "Maestro"}
    name = names.get(self.difficulty_level, "Livello")
    return f"{name} ({self.difficulty_level})"

def get_scoring_display(self) -> str:
    """Get human-readable scoring status."""
    return "Attivo" if self.scoring_enabled else "Disattivato"
```

### Testing Phase 3

**File**: `tests/unit/test_game_settings_validation.py`

```python
def test_difficulty_level_4_enforces_timer():
    """Test level 4 enforces minimum 30min timer."""
    settings = GameSettings()
    settings.difficulty_level = 3
    settings.max_time_game = -1  # OFF
    
    # Cycle to level 4
    success, msg = settings.cycle_difficulty()
    
    assert settings.difficulty_level == 4
    assert settings.max_time_game == 1800  # Auto-adjusted to 30min
    assert "timer obbligatorio" in msg

def test_difficulty_level_5_enforces_3_cards():
    """Test level 5 forces 3 cards draw."""
    settings = GameSettings()
    settings.difficulty_level = 4
    settings.draw_count = 2
    
    # Cycle to level 5
    success, msg = settings.cycle_difficulty()
    
    assert settings.difficulty_level == 5
    assert settings.draw_count == 3  # Auto-adjusted
    assert "3 carte obbligatorie" in msg

def test_toggle_scoring():
    """Test scoring toggle."""
    settings = GameSettings()
    assert settings.scoring_enabled == True
    
    success, msg = settings.toggle_scoring()
    assert settings.scoring_enabled == False
    assert "free-play" in msg
```

**Commit 3**: `feat(domain): Extend GameSettings with draw_count, scoring toggle, and level 4-5 constraints`

---

## Phase 4: GameService Integration

### File: `src/domain/services/game_service.py` (MODIFY)

**Purpose**: Integrate ScoringService into game logic (record events during gameplay).

### 4.1 Modified Constructor

```python
class GameService:
    def __init__(
        self,
        table: GameTable,
        rules: SolitaireRules,
        scoring: Optional[ScoringService] = None  # NEW: optional dependency
    ):
        self.table = table
        self.rules = rules
        self.is_game_running = False
        self.move_count = 0
        self.start_time: Optional[float] = None
        self.draw_count = 0
        
        # NEW: Scoring integration
        self.scoring = scoring  # Can be None if scoring disabled
```

### 4.2 Modified: move_card (record events)

```python
def move_card(
    self,
    source_pile: Pile,
    target_pile: Pile,
    card_count: int = 1,
    is_foundation_target: bool = False
) -> Tuple[bool, str]:
    """Move card(s) with scoring integration."""
    
    # ... existing validation logic ...
    
    # Execute move
    source_pile.remove_last_card()
    target_pile.aggiungi_carta(card)
    
    # Update game state
    self.move_count += 1
    self._uncover_top_card(source_pile)
    
    # ═══════════════════════════════════════════════════
    # NEW: Record scoring events (if scoring enabled)
    # ═══════════════════════════════════════════════════
    if self.scoring:
        # Foundation move
        if is_foundation_target:
            if source_pile == self.table.pile_scarti:
                self.scoring.record_event(
                    ScoreEventType.WASTE_TO_FOUNDATION,
                    {"card": card.get_name, "foundation": target_pile.name}
                )
            else:
                self.scoring.record_event(
                    ScoreEventType.TABLEAU_TO_FOUNDATION,
                    {"card": card.get_name, "tableau": source_pile.name}
                )
        
        # Check if card was revealed in source pile
        if not source_pile.is_empty():
            top = source_pile.get_top_card()
            if top and not top.get_covered:
                self.scoring.record_event(
                    ScoreEventType.CARD_REVEALED,
                    {"pile": source_pile.name, "card": top.get_name}
                )
    
    return True, f"Mossa eseguita (#{self.move_count})"
```

### 4.3 Modified: recycle_waste (record penalty)

```python
def recycle_waste(self, shuffle: bool = False) -> Tuple[bool, str]:
    """Recycle waste with scoring integration."""
    
    # ... existing recycle logic ...
    
    # ═══════════════════════════════════════════════════
    # NEW: Record recycle event (penalty after 3rd)
    # ═══════════════════════════════════════════════════
    if self.scoring:
        self.scoring.record_event(
            ScoreEventType.RECYCLE_WASTE,
            {"shuffle": shuffle, "card_count": len(cards)}
        )
    
    return True, f"Tallone riciclato ({len(cards)} carte)"
```

### 4.4 Modified: reset_game (reset scoring)

```python
def reset_game(self) -> None:
    """Reset game state including scoring."""
    self.is_game_running = False
    self.move_count = 0
    self.start_time = None
    self.draw_count = 0
    
    # NEW: Reset scoring if present
    if self.scoring:
        self.scoring.reset()
```

### Testing Phase 4

**File**: `tests/integration/test_scoring_integration.py`

```python
def test_move_to_foundation_records_event():
    """Test that moving to foundation records scoring event."""
    scoring = ScoringService()
    service = GameService(table, rules, scoring)
    
    # Execute move
    success, msg = service.move_card(
        source_pile=table.pile_scarti,
        target_pile=table.pile_semi[0],
        is_foundation_target=True
    )
    
    assert success
    assert scoring.get_base_score() == 10  # WASTE_TO_FOUNDATION
    assert scoring.get_event_count() == 1

def test_recycle_penalty_after_third():
    """Test recycle penalty after 3 recycles."""
    scoring = ScoringService()
    service = GameService(table, rules, scoring)
    
    # First 3 recycles: no penalty
    for i in range(3):
        service.recycle_waste()
        assert scoring.get_base_score() == 0
    
    # 4th recycle: -20 penalty
    service.recycle_waste()
    assert scoring.get_base_score() == -20

def test_no_scoring_when_disabled():
    """Test that scoring=None doesn't record events."""
    service = GameService(table, rules, scoring=None)
    
    # Move card
    service.move_card(source, target, is_foundation_target=True)
    
    # No crash, no scoring
    assert service.scoring is None
```

**Commit 4**: `feat(domain): Integrate ScoringService into GameService for event recording`

---

## Phase 5: Application Controllers

### 5.1 File: `src/application/options_controller.py` (MODIFY)

**Purpose**: Add options 3 (draw count) and 7 (scoring toggle).

```python
class OptionsController:
    def __init__(self, settings: GameSettings, screen_reader: Optional[ScreenReader] = None):
        self.settings = settings
        self.screen_reader = screen_reader
        
        # Extended option list (7 options)
        self.option_items = [
            "Tipo Mazzo",             # 0
            "Difficoltà",             # 1
            "Carte Pescate",          # 2 (NEW)
            "Timer",                  # 3
            "Modalità Riciclo",       # 4
            "Suggerimenti Comandi",   # 5
            "Sistema Punti"           # 6 (NEW)
        ]
        
        self.current_option = 0
        self.is_dirty = False
    
    def modify_current_option(self) -> str:
        """Modify selected option."""
        idx = self.current_option
        
        if idx == 0:
            success, msg = self.settings.toggle_deck_type()
        elif idx == 1:
            success, msg = self.settings.cycle_difficulty()
        elif idx == 2:  # NEW
            success, msg = self.settings.cycle_draw_count()
        elif idx == 3:
            success, msg = self.settings.toggle_timer()
        elif idx == 4:
            success, msg = self.settings.toggle_shuffle_mode()
        elif idx == 5:
            success, msg = self.settings.toggle_command_hints()
        elif idx == 6:  # NEW
            success, msg = self.settings.toggle_scoring()
        else:
            return "Opzione non valida"
        
        if success:
            self.is_dirty = True
        
        return msg
```

### 5.2 File: `src/application/gameplay_controller.py` (MODIFY)

**Purpose**: Add commands to query/announce scores.

```python
class GameplayController:
    def __init__(self, game_engine, settings, screen_reader):
        # ... existing attributes ...
        self.score_formatter = ScoreFormatter()  # NEW
    
    def show_current_score(self) -> None:
        """Command 'P': Show current score.
        
        Announces provisional score with breakdown.
        Only works if scoring_enabled=True.
        """
        if not self.settings.scoring_enabled:
            msg = self.score_formatter.format_scoring_disabled()
            self.screen_reader.speak(msg, interrupt=True)
            return
        
        # Check if game is running
        if not self.game_engine.service.is_game_running:
            self.screen_reader.speak("Nessuna partita in corso.", interrupt=True)
            return
        
        # Calculate provisional score
        elapsed = int(self.game_engine.service.get_elapsed_time())
        provisional = self.game_engine.service.scoring.calculate_provisional_score(
            elapsed_seconds=elapsed,
            max_time=self.settings.max_time_game,
            deck_type=self.settings.deck_type,
            difficulty_level=self.settings.difficulty_level,
            draw_count=self.settings.draw_count,
            recycle_mode="inverted" if not self.settings.shuffle_discards else "shuffled"
        )
        
        # Format and announce
        msg = self.score_formatter.format_provisional_score(provisional)
        self.screen_reader.speak(msg, interrupt=True)
    
    def show_score_breakdown(self) -> None:
        """Command 'Shift+P': Show detailed score breakdown.
        
        Announces last 5 scoring events.
        """
        if not self.settings.scoring_enabled:
            msg = self.score_formatter.format_scoring_disabled()
            self.screen_reader.speak(msg, interrupt=True)
            return
        
        if not self.game_engine.service.scoring:
            return
        
        events = self.game_engine.service.scoring.get_recent_events(5)
        
        if not events:
            self.screen_reader.speak("Nessun evento di punteggio registrato.", interrupt=True)
            return
        
        # Announce each event
        for event in events:
            msg = self.score_formatter.format_score_event(event)
            self.screen_reader.speak(msg, interrupt=False)
```

### Testing Phase 5

**File**: `tests/unit/test_options_controller.py`

```python
def test_cycle_draw_count_option():
    """Test option 3 cycles draw count."""
    controller = OptionsController(settings)
    controller.current_option = 2  # Draw count
    
    msg = controller.modify_current_option()
    
    assert settings.draw_count == 2  # Cycled from 1
    assert "2" in msg

def test_toggle_scoring_option():
    """Test option 7 toggles scoring."""
    controller = OptionsController(settings)
    controller.current_option = 6  # Scoring
    
    msg = controller.modify_current_option()
    
    assert settings.scoring_enabled == False
    assert "free-play" in msg
```

**Commit 5**: `feat(application): Add draw_count and scoring toggle options to controllers`

---

## Phase 6: Presentation Formatters

### File: `src/presentation/formatters/score_formatter.py` (NEW)

**Purpose**: TTS-optimized messages for scoring system.

```python
"""Formatter for scoring system messages (TTS-optimized)."""

from typing import Optional, List
from src.domain.models.scoring import ProvisionalScore, FinalScore, ScoreEvent


class ScoreFormatter:
    """Format scoring information for screen reader."""
    
    @staticmethod
    def format_provisional_score(score: ProvisionalScore) -> str:
        """Format current score during gameplay."""
        msg = f"Punteggio attuale: {score.total_score} punti. "
        
        if score.base_score != score.total_score:
            msg += f"Punteggio base: {score.base_score}. "
            
            if score.difficulty_multiplier > 1.0:
                perc = int((score.difficulty_multiplier - 1.0) * 100)
                msg += f"Bonus difficoltà: più {perc} percento. "
            
            if score.deck_bonus > 0:
                msg += f"Bonus mazzo: più {score.deck_bonus}. "
            
            if score.draw_bonus > 0:
                msg += f"Bonus carte: più {score.draw_bonus}. "
        
        return msg
    
    @staticmethod
    def format_final_score(score: FinalScore) -> str:
        """Format final score at game end."""
        lines = []
        
        if score.is_victory:
            lines.append("Partita vinta!")
        else:
            lines.append("Partita terminata.")
        
        lines.append(f"Punteggio finale: {score.total_score} punti.")
        lines.append(f"Punteggio base: {score.base_score} punti.")
        
        if score.deck_bonus > 0:
            lines.append(f"Bonus mazzo francese: più {score.deck_bonus}.")
        
        if score.draw_bonus > 0:
            lines.append(f"Bonus carte pescate: più {score.draw_bonus}.")
        
        if score.difficulty_multiplier > 1.0:
            perc = int((score.difficulty_multiplier - 1.0) * 100)
            lines.append(f"Moltiplicatore difficoltà: più {perc} percento.")
        
        if score.time_bonus > 0:
            lines.append(f"Bonus tempo: più {score.time_bonus}.")
        elif score.time_bonus < 0:
            lines.append(f"Penalità tempo: meno {abs(score.time_bonus)}.")
        
        if score.victory_bonus > 0:
            lines.append(f"Bonus vittoria: più {score.victory_bonus}.")
        
        lines.append(f"Mosse totali: {score.move_count}.")
        lines.append(f"Tempo trascorso: {score.elapsed_seconds} secondi.")
        
        return " ".join(lines)
    
    @staticmethod
    def format_score_event(event: ScoreEvent) -> str:
        """Format single score event."""
        event_names = {
            "waste_to_foundation": "Scarto a fondazione",
            "tableau_to_foundation": "Tableau a fondazione",
            "card_revealed": "Carta scoperta",
            "foundation_to_tableau": "Fondazione a tableau",
            "recycle_waste": "Riciclo scarti"
        }
        
        name = event_names.get(event.event_type.value, event.event_type.value)
        return f"{name}: {event.points:+d} punti"
    
    @staticmethod
    def format_scoring_disabled() -> str:
        """Message when scoring disabled."""
        return "Sistema punti disattivato. Modalità free-play attiva."
    
    @staticmethod
    def format_best_score(score_dict: dict) -> str:
        """Format best score announcement."""
        total = score_dict.get('total_score', 0)
        difficulty = score_dict.get('difficulty_level', 1)
        deck = score_dict.get('deck_type', 'francese')
        
        deck_name = "napoletano" if deck == "napoletano" else "francese"
        
        return (f"Miglior punteggio: {total} punti. "
                f"Livello {difficulty}, mazzo {deck_name}.")
```

**Commit 6**: `feat(presentation): Add ScoreFormatter for TTS-optimized scoring messages`

---

## Phase 7: Infrastructure Storage

### File: `src/infrastructure/storage/score_storage.py` (NEW)

**Purpose**: Persistent JSON storage for scoring statistics.

```python
"""Persistent storage for scoring statistics."""

import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import asdict
from datetime import datetime

from src.domain.models.scoring import FinalScore


class ScoreStorage:
    """Save and load scoring statistics to JSON."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize storage.
        
        Args:
            storage_path: Path to JSON file (default: ~/.solitario/scores.json)
        """
        if storage_path is None:
            storage_path = Path.home() / ".solitario" / "scores.json"
        
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
    
    def save_score(self, score: FinalScore) -> None:
        """Save final score to persistent storage.
        
        Args:
            score: FinalScore to save
        """
        scores = self.load_all_scores()
        
        # Convert to dict and add timestamp
        score_dict = asdict(score)
        score_dict['saved_at'] = datetime.now().isoformat()
        
        scores.append(score_dict)
        
        # Keep only last 100 scores
        scores = scores[-100:]
        
        # Save
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(scores, f, indent=2, ensure_ascii=False)
    
    def load_all_scores(self) -> List[Dict]:
        """Load all saved scores.
        
        Returns:
            List of score dictionaries
        """
        if not self.storage_path.exists():
            return []
        
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    
    def get_best_score(
        self,
        deck_type: Optional[str] = None,
        difficulty: Optional[int] = None
    ) -> Optional[Dict]:
        """Get highest score with optional filters.
        
        Args:
            deck_type: Filter by deck ("napoletano"/"francese")
            difficulty: Filter by difficulty level (1-5)
            
        Returns:
            Dict with best score or None if no scores
        """
        scores = self.load_all_scores()
        
        # Apply filters
        if deck_type:
            scores = [s for s in scores if s.get('deck_type') == deck_type]
        if difficulty:
            scores = [s for s in scores if s.get('difficulty_level') == difficulty]
        
        # Find maximum
        if not scores:
            return None
        
        return max(scores, key=lambda s: s.get('total_score', 0))
    
    def get_statistics(self) -> Dict:
        """Get aggregate statistics.
        
        Returns:
            Dict with total_games, total_wins, average_score, etc.
        """
        scores = self.load_all_scores()
        
        if not scores:
            return {
                'total_games': 0,
                'total_wins': 0,
                'average_score': 0,
                'best_score': 0
            }
        
        total_games = len(scores)
        total_wins = sum(1 for s in scores if s.get('is_victory', False))
        total_score = sum(s.get('total_score', 0) for s in scores)
        average_score = total_score / total_games if total_games > 0 else 0
        best_score = max(s.get('total_score', 0) for s in scores)
        
        return {
            'total_games': total_games,
            'total_wins': total_wins,
            'average_score': int(average_score),
            'best_score': best_score,
            'win_rate': (total_wins / total_games * 100) if total_games > 0 else 0
        }
```

### Integration in GameEngine

**File**: `src/application/game_engine.py` (MODIFY)

```python
class GameEngine:
    def __init__(self, ..., score_storage: Optional[ScoreStorage] = None):
        # ... existing attributes ...
        self.score_storage = score_storage  # NEW
    
    def end_game(self, is_victory: bool) -> None:
        """End game and save final score if scoring enabled."""
        
        if not self.settings.scoring_enabled or not self.service.scoring:
            # Free-play mode: no scoring
            self.service.reset_game()
            return
        
        # Calculate final score
        elapsed = int(self.service.get_elapsed_time())
        final_score = self.service.scoring.calculate_final_score(
            elapsed_seconds=elapsed,
            max_time=self.settings.max_time_game,
            deck_type=self.settings.deck_type,
            difficulty_level=self.settings.difficulty_level,
            draw_count=self.settings.draw_count,
            recycle_mode="inverted" if not self.settings.shuffle_discards else "shuffled",
            move_count=self.service.move_count,
            is_victory=is_victory
        )
        
        # Save to storage
        if self.score_storage:
            self.score_storage.save_score(final_score)
        
        # Announce final score
        if self.screen_reader:
            msg = ScoreFormatter.format_final_score(final_score)
            self.screen_reader.speak(msg, interrupt=True)
        
        # Reset game
        self.service.reset_game()
```

**Commit 7**: `feat(infrastructure): Add ScoreStorage for persistent statistics with JSON backend`

**Commit 8**: `feat(application): Integrate ScoreStorage into GameEngine with end_game flow`

---

## Testing Strategy

### Unit Tests (50+ tests)

#### `tests/unit/test_scoring_models.py` (15 tests)
- Test ScoringConfig defaults
- Test ScoreEvent immutability
- Test ProvisionalScore calculations
- Test FinalScore breakdown formatting
- Test enum values

#### `tests/unit/test_scoring_service.py` (20 tests)
- Test event recording (each event type)
- Test recycle penalty after 3rd
- Test time bonus formulas (timer ON/OFF)
- Test provisional score calculation
- Test final score calculation
- Test reset() clears state
- Test get_recent_events()

#### `tests/unit/test_game_settings_validation.py` (15 tests)
- Test cycle_difficulty 1→5→1
- Test level 4 enforces timer ≥30min
- Test level 5 enforces timer 15-30min
- Test level 4 enforces draw_count ≥2
- Test level 5 enforces draw_count=3
- Test level 4-5 locks shuffle to invert
- Test toggle_scoring()
- Test cycle_draw_count()

### Integration Tests (20+ tests)

#### `tests/integration/test_scoring_integration.py` (12 tests)
- Test move to foundation records +10
- Test move to tableau records +10
- Test reveal card records +5
- Test foundation to tableau records -15
- Test recycle after 3rd records -20
- Test scoring=None doesn't crash
- Test provisional score matches events
- Test final score with victory bonus

#### `tests/integration/test_difficulty_constraints.py` (8 tests)
- Test level 4→5 auto-adjusts timer
- Test level 5→1 removes constraints
- Test draw_count respects level limits
- Test shuffle locked at level 4-5
- Test option interactions (cycle difficulty while draw_count=1)

### Acceptance Tests (End-to-End)

```python
def test_complete_game_with_scoring():
    """Full game: deal, play, win, save score."""
    settings = GameSettings()
    settings.scoring_enabled = True
    settings.difficulty_level = 3
    settings.draw_count = 2
    
    engine = GameEngine.create(settings=settings)
    engine.new_game()
    
    # Play some moves
    engine.move_card(...)
    engine.draw_from_stock()
    
    # Win game
    # ... move all cards to foundations ...
    
    # Check victory
    assert engine.is_victory()
    
    # End game
    engine.end_game(is_victory=True)
    
    # Check score saved
    storage = ScoreStorage()
    scores = storage.load_all_scores()
    assert len(scores) > 0
    assert scores[-1]['is_victory'] == True
    assert scores[-1]['total_score'] > 0

def test_free_play_mode_no_scoring():
    """Test free-play mode doesn't calculate scores."""
    settings = GameSettings()
    settings.scoring_enabled = False
    
    engine = GameEngine.create(settings=settings)
    engine.new_game()
    
    # Play moves
    engine.move_card(...)
    
    # Check no scoring service
    assert engine.service.scoring is None
    
    # End game
    engine.end_game(is_victory=False)
    
    # Check no score saved
    storage = ScoreStorage()
    scores = storage.load_all_scores()
    # No new score added
```

---

## Validation & Acceptance

### Success Criteria

- [ ] All 7 options work correctly (deck, difficulty, draw, timer, recycle, hints, scoring)
- [ ] Difficulty levels 4-5 enforce constraints automatically
- [ ] Scoring system calculates points correctly (verified with manual calculations)
- [ ] Time bonus formula matches specification
- [ ] Final scores saved to JSON correctly
- [ ] Best score queries work with filters
- [ ] TTS messages are clear and complete
- [ ] Free-play mode (scoring OFF) works without crashes
- [ ] Zero breaking changes to existing gameplay
- [ ] Test coverage ≥90% for new code
- [ ] All 70+ tests passing

### Manual Testing Checklist

- [ ] Play game with scoring ON, verify point calculations
- [ ] Play game with scoring OFF, verify no calculations
- [ ] Set difficulty to level 4, verify timer enforced
- [ ] Set difficulty to level 5, verify draw_count=3 enforced
- [ ] Cycle draw_count at level 4, verify minimum 2
- [ ] Win game at level 5, verify score saved with 2.5x multiplier
- [ ] Check best score display with filters
- [ ] Verify TTS announces all scoring events clearly
- [ ] Test "P" command shows current score
- [ ] Test "Shift+P" command shows event breakdown

### Performance Requirements

- [ ] Score calculation < 1ms per event
- [ ] JSON save/load < 50ms
- [ ] No memory leaks (run 100+ games)
- [ ] TTS announcements don't block gameplay

---

## Commit Strategy

### Atomic Commits (7-8 total)

1. **Commit 1**: Domain models (`scoring.py`)
   - `feat(domain): Add scoring system models and configuration`

2. **Commit 2**: Domain service (`scoring_service.py`)
   - `feat(domain): Implement ScoringService with event recording and calculations`

3. **Commit 3**: GameSettings extension
   - `feat(domain): Extend GameSettings with draw_count, scoring toggle, and level 4-5 constraints`

4. **Commit 4**: GameService integration
   - `feat(domain): Integrate ScoringService into GameService for event recording`

5. **Commit 5**: Application controllers
   - `feat(application): Add draw_count and scoring toggle options to controllers`

6. **Commit 6**: Presentation formatters
   - `feat(presentation): Add ScoreFormatter for TTS-optimized scoring messages`

7. **Commit 7**: Infrastructure storage
   - `feat(infrastructure): Add ScoreStorage for persistent statistics with JSON backend`

8. **Commit 8**: Final integration
   - `feat(application): Integrate ScoreStorage into GameEngine with end_game flow`

---

## Notes for Copilot

### Critical Requirements

1. **Immutability**: All score results must be frozen dataclasses
2. **Optional dependency**: `scoring: Optional[ScoringService]` everywhere
3. **Zero breaking changes**: Check `if self.scoring:` before recording events
4. **TTS optimization**: All messages must be screen-reader friendly
5. **Validation order**: Apply constraints in cycle_difficulty() automatically

### Common Pitfalls to Avoid

- ❌ Don't record events if `scoring is None`
- ❌ Don't modify difficulty without checking constraints
- ❌ Don't calculate scores in presentation layer
- ❌ Don't use English in TTS messages (Italian only)
- ❌ Don't forget to reset scoring in `reset_game()`

### Testing Priorities

1. **Highest**: Scoring calculations (formulas must be exact)
2. **High**: Difficulty constraints (auto-adjustment logic)
3. **Medium**: Storage persistence (JSON correctness)
4. **Low**: TTS message formatting (manual verification OK)

---

## Appendix: Formula Reference

### Base Score Calculation

```
base_score = sum(all_event_points)
```

### Final Score Formula

```
final_score = (
    (base_score + deck_bonus + draw_bonus) * difficulty_multiplier
    + time_bonus
    + victory_bonus
)

final_score = max(0, final_score)  # Clamp to minimum
```

### Time Bonus Formulas

**Timer OFF**:
```python
time_bonus = min(2000, int(10000 / sqrt(elapsed_seconds)))
```

**Timer ON**:
```python
remaining_percentage = (max_time - elapsed) / max_time * 100

if remaining_percentage >= 50:
    time_bonus = 1000
elif remaining_percentage >= 25:
    time_bonus = 500
elif remaining_percentage > 0:
    time_bonus = 200
else:
    time_bonus = -500  # Expired
```

### Example Calculations

**Example 1**: Level 3, French deck, 3 cards, no timer, 5 minutes
```
base_score = 150  (from events)
deck_bonus = +150 (francese)
draw_bonus = +200 (3 cards, level ≤3)
difficulty_mult = 1.5 (level 3)
time_bonus = +577 (10000 / sqrt(300))

final = (150 + 150 + 200) * 1.5 + 577 = 1327
```

**Example 2**: Level 5, French deck, 3 cards, 20min timer (30min elapsed - lost)
```
base_score = 200
deck_bonus = +150
draw_bonus = 0 (level 5, not counted)
difficulty_mult = 2.5 (level 5)
time_bonus = -500 (timer expired)

final = (200 + 150 + 0) * 2.5 - 500 = 375
```

---

**End of Implementation Guide**

This document provides all specifications for Copilot to implement the complete scoring system v2.0.0 incrementally across 7-8 atomic commits with full testing coverage.