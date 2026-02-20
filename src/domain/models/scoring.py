"""Domain models for scoring system v2.0.0.

Provides immutable data structures for tracking game scoring including:
- Score events (player actions that affect score)
- Scoring configuration (bonuses, multipliers, point values)
- Provisional and final scores with breakdowns

All dataclasses are frozen for immutability and thread-safety.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional


class ScoreEventType(Enum):
    """Types of scoring events that can occur during gameplay.
    
    Each event type has an associated point value:
    - WASTE_TO_FOUNDATION: +10 points
    - TABLEAU_TO_FOUNDATION: +10 points
    - CARD_REVEALED: +5 points
    - FOUNDATION_TO_TABLEAU: -15 points (penalty)
    - RECYCLE_WASTE: Progressive penalty (0, 0, -10, -20, -35, -55, -80)
    - STOCK_DRAW: Progressive penalty (0 for first 20, then -1, then -2)
    - INVALID_MOVE: 0 points (tracking only, reserved for v2.1+)
    - AUTO_MOVE: 0 points (tracking only, neutral)
    - UNDO_MOVE: 0 points (reserved for future undo feature)
    - HINT_USED: 0 points (reserved for future hint penalty)
    """
    
    WASTE_TO_FOUNDATION = "waste_to_foundation"
    TABLEAU_TO_FOUNDATION = "tableau_to_foundation"
    CARD_REVEALED = "card_revealed"
    FOUNDATION_TO_TABLEAU = "foundation_to_tableau"
    RECYCLE_WASTE = "recycle_waste"
    STOCK_DRAW = "stock_draw"
    INVALID_MOVE = "invalid_move"
    AUTO_MOVE = "auto_move"
    UNDO_MOVE = "undo_move"
    HINT_USED = "hint_used"


@dataclass(frozen=True)
class ScoringConfig:
    """Configuration for scoring system v2.0 with all bonuses and multipliers.
    
    Defines point values for events, difficulty multipliers, and various
    bonuses. Version 2.0 introduces composite victory bonus and external config.
    
    Attributes:
        version: Config version (must start with "2.")
        event_points: Point values for each event type
        difficulty_multipliers: Score multipliers by difficulty level (1-5)
        deck_type_bonuses: Bonus points by deck type
        draw_count_bonuses: Bonus points by draw count (levels 1-3 get full, 4-5 get 50%)
        victory_bonus_base: Base victory bonus before quality multiplier
        victory_weights: Weights for quality factors (time, moves, recycles)
        stock_draw_thresholds: Thresholds for stock draw penalty tiers
        stock_draw_penalties: Penalties for each stock draw tier
        recycle_penalties: Penalties for each recycle count (indexed by count-1)
        time_bonus_max_timer_off: Max time bonus when timer OFF
        time_bonus_decay_per_minute: Decay per minute when timer OFF
        time_bonus_max_timer_on: Max time bonus when timer ON
        overtime_penalty_per_minute: Penalty per overtime minute (PERMISSIVE mode)
        min_score: Minimum possible score (clamp floor)
    """
    
    # Version control
    version: str = "2.0.0"
    
    # Event point values (v2.0 standard)
    event_points: Dict[ScoreEventType, int] = field(default_factory=lambda: {
        ScoreEventType.WASTE_TO_FOUNDATION: 10,
        ScoreEventType.TABLEAU_TO_FOUNDATION: 10,
        ScoreEventType.CARD_REVEALED: 5,
        ScoreEventType.FOUNDATION_TO_TABLEAU: -15,
        ScoreEventType.RECYCLE_WASTE: 0,  # Calculated via recycle_penalties
        ScoreEventType.STOCK_DRAW: 0,  # Calculated via stock_draw_penalties
        ScoreEventType.INVALID_MOVE: 0,  # Tracking only
        ScoreEventType.AUTO_MOVE: 0,  # Tracking only
        ScoreEventType.UNDO_MOVE: 0,  # Reserved for future
        ScoreEventType.HINT_USED: 0,  # Reserved for future
    })
    
    # Difficulty multipliers (v2.0 rebalanced)
    difficulty_multipliers: Dict[int, float] = field(default_factory=lambda: {
        1: 1.0,   # Principiante
        2: 1.2,   # Facile
        3: 1.4,   # Normale
        4: 1.8,   # Esperto
        5: 2.2,   # Maestro
    })
    
    # Deck type bonuses (v2.0 rebalanced)
    deck_type_bonuses: Dict[str, int] = field(default_factory=lambda: {
        "neapolitan": 100,  # 40 cards (harder)
        "french": 50,       # 52 cards (baseline)
    })
    
    # Draw count bonuses (levels 1-3 get full, 4-5 get 50%)
    draw_count_bonuses: Dict[int, Dict[str, int]] = field(default_factory=lambda: {
        1: {"low": 0, "high": 0},      # Draw 1 (easiest)
        2: {"low": 100, "high": 50},   # Draw 2
        3: {"low": 200, "high": 100},  # Draw 3 (hardest)
    })
    
    # Victory bonus v2.0 (composite)
    victory_bonus_base: int = 400
    victory_weights: Dict[str, float] = field(default_factory=lambda: {
        "time": 0.35,
        "moves": 0.35,
        "recycles": 0.30,
    })
    
    # Stock draw progressive penalties
    stock_draw_thresholds: tuple = field(default_factory=lambda: (20, 40))
    stock_draw_penalties: tuple = field(default_factory=lambda: (0, -1, -2))
    
    # Recycle progressive penalties (indexed by recycle_count-1)
    recycle_penalties: tuple = field(default_factory=lambda: (0, 0, -10, -20, -35, -55, -80))
    
    # Time bonus parameters (v2.0 values)
    time_bonus_max_timer_off: int = 1200
    time_bonus_decay_per_minute: int = 40
    time_bonus_max_timer_on: int = 1000
    overtime_penalty_per_minute: int = -100
    
    # Minimum score (never go below 0)
    min_score: int = 0
    
    def __post_init__(self):
        """Validate configuration constraints.
        
        Raises:
            ValueError: If configuration is invalid
        """
        # Version check
        if not self.version.startswith("2."):
            raise ValueError(
                f"Invalid config version '{self.version}'. "
                "Expected version 2.x"
            )
        
        # Validate victory weights sum to ~1.0 (allow 0.99-1.01 for float precision)
        weights_sum = sum(self.victory_weights.values())
        if not (0.99 <= weights_sum <= 1.01):
            raise ValueError(
                f"Victory weights must sum to 1.0, got {weights_sum}. "
                f"Weights: {self.victory_weights}"
            )
        
        # Validate difficulty levels completeness (must have 1-5)
        expected_levels = {1, 2, 3, 4, 5}
        actual_levels = set(self.difficulty_multipliers.keys())
        if actual_levels != expected_levels:
            raise ValueError(
                f"Difficulty multipliers must have levels 1-5. "
                f"Missing: {expected_levels - actual_levels}, "
                f"Extra: {actual_levels - expected_levels}"
            )


@dataclass(frozen=True)
class ScoreEvent:
    """A single scoring event that occurred during gameplay.
    
    Records what happened, when it happened, and contextual details
    for debugging and event history display.
    
    Attributes:
        event_type: Type of event (e.g., WASTE_TO_FOUNDATION)
        points: Points awarded/deducted for this event
        timestamp: When the event occurred (UTC)
        context: Optional details (e.g., "7 di Cuori", "Pile 3")
    """
    
    event_type: ScoreEventType
    points: int
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    context: Optional[str] = None
    
    def __str__(self) -> str:
        """Human-readable event description."""
        sign = "+" if self.points >= 0 else ""
        ctx = f" ({self.context})" if self.context else ""
        return f"{self.event_type.value}: {sign}{self.points} punti{ctx}"


@dataclass(frozen=True)
class ProvisionalScore:
    """Provisional (in-progress) score during gameplay.
    
    Shows current score breakdown before victory bonus is determined.
    Updated in real-time as player makes moves.
    
    Attributes:
        base_score: Sum of all event points
        deck_bonus: Bonus from deck type
        draw_bonus: Bonus from draw count (levels 1-3 only)
        difficulty_multiplier: Multiplier from difficulty level
        total_before_multiplier: base_score + deck_bonus + draw_bonus
        total_score: total_before_multiplier * difficulty_multiplier
    """
    
    base_score: int
    deck_bonus: int
    draw_bonus: int
    difficulty_multiplier: float
    total_before_multiplier: int = field(init=False)
    total_score: int = field(init=False)
    
    def __post_init__(self):
        """Calculate derived fields (immutable workaround)."""
        # Use object.__setattr__ to set fields on frozen dataclass
        object.__setattr__(
            self,
            'total_before_multiplier',
            self.base_score + self.deck_bonus + self.draw_bonus
        )
        object.__setattr__(
            self,
            'total_score',
            int(self.total_before_multiplier * self.difficulty_multiplier)
        )


@dataclass(frozen=True)
class FinalScore:
    """Final score at game end with complete breakdown.
    
    Includes all bonuses, time bonus, and victory status.
    Saved to persistent storage for statistics and leaderboards.
    
    Attributes:
        base_score: Sum of all event points
        deck_bonus: Bonus from deck type
        draw_bonus: Bonus from draw count (0 for levels 4-5)
        difficulty_multiplier: Multiplier from difficulty level
        time_bonus: Bonus based on completion time
        victory_bonus: Bonus if game was won (0 if lost)
        total_score: Final score (clamped to min_score)
        is_victory: Whether the game was won
        elapsed_seconds: Time taken to complete game
        difficulty_level: Difficulty level (1-5)
        deck_type: Deck type used ("french" or "neapolitan")
        draw_count: Cards drawn per click (1-3)
        recycle_count: Number of times waste was recycled
        move_count: Total moves made
        victory_quality_multiplier: Quality multiplier for victory bonus (v2.0)
            Range: 0.0 (abandonment) - 1.34 (perfect)
            -1.0 = legacy score (sentinel value)
    """
    
    base_score: int
    deck_bonus: int
    draw_bonus: int
    difficulty_multiplier: float
    time_bonus: int
    victory_bonus: int
    total_score: int
    is_victory: bool
    elapsed_seconds: float
    difficulty_level: int
    deck_type: str
    draw_count: int
    recycle_count: int
    move_count: int
    victory_quality_multiplier: float = 0.0  # v2.0 NEW field
    
    def get_breakdown(self) -> str:
        """Get Italian TTS-friendly breakdown of score components.
        
        Returns:
            Formatted string with all score components for accessibility.
            
        Example:
            "Punteggio base: 85 punti. Bonus mazzo: 150 punti. 
             Bonus carte pescate: 100 punti. Moltiplicatore difficoltà: 2.0.
             Bonus tempo: 345 punti. Bonus vittoria: 500 punti.
             Punteggio totale: 1015 punti."
        """
        parts = [
            f"Punteggio base: {self.base_score} punti",
            f"Bonus mazzo: {self.deck_bonus} punti" if self.deck_bonus > 0 else None,
            f"Bonus carte pescate: {self.draw_bonus} punti" if self.draw_bonus > 0 else None,
            f"Moltiplicatore difficoltà: {self.difficulty_multiplier}",
            f"Bonus tempo: {self.time_bonus} punti" if self.time_bonus > 0 else None,
            f"Bonus vittoria: {self.victory_bonus} punti" if self.victory_bonus > 0 else None,
        ]
        
        # Filter out None values
        parts = [part for part in parts if part is not None]
        
        # Add total
        parts.append(f"Punteggio totale: {self.total_score} punti")
        
        # Join with periods and spaces for TTS clarity
        return ". ".join(parts) + "."


# ============================================================================
# WARNING LEVELS (v2.6.0)
# ============================================================================

from enum import IntEnum


class ScoreWarningLevel(IntEnum):
    """Livelli di verbosità warnings soglie scoring (v2.6.0).
    
    Controlla quanti avvisi TTS vengono emessi quando il giocatore
    supera soglie di penalità (stock draw, recycle).
    
    I livelli progressivi permettono a principianti di ricevere
    guida completa e a veterani di minimizzare interruzioni.
    
    Attributes:
        DISABLED: Nessun warning (0) - per veterani che non vogliono interruzioni
        MINIMAL: Solo transizioni 0pt → penalità (1) - warnings essenziali
        BALANCED: Transizioni + escalation significative (2) - default consigliato
        COMPLETE: Pre-warnings + tutte le transizioni (3) - per principianti
    
    Usage:
        >>> settings.score_warning_level = ScoreWarningLevel.BALANCED
        >>> if settings.score_warning_level >= ScoreWarningLevel.MINIMAL:
        ...     announce_warning("Attenzione: soglia penalità superata")
    
    Mapping Soglie per Livello:
        - DISABLED: Nessun warning attivo
        - MINIMAL: Draw 21 (prima penalità), Recycle 4 (prima penalità)
        - BALANCED: Draw 21, Draw 41, Recycle 4
        - COMPLETE: Draw 20 (pre-warning), Draw 21, Draw 41, Recycle 3, Recycle 4, Recycle 5
    
    Version: v2.6.0
    """
    
    DISABLED = 0   # Nessun warning (silenzioso, veterani)
    MINIMAL = 1    # Solo transizioni 0pt → penalità (warnings essenziali)
    BALANCED = 2   # Transizioni + escalation (DEFAULT, casual players)
    COMPLETE = 3   # Pre-warnings + tutte soglie (principianti, massima guida)
