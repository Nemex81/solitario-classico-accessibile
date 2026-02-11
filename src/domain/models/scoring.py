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
    - RECYCLE_WASTE: -20 points (penalty, only after 3rd recycle)
    - UNDO_MOVE: -0 points (reserved for future undo feature)
    - HINT_USED: -0 points (reserved for future hint penalty)
    """
    
    WASTE_TO_FOUNDATION = "waste_to_foundation"
    TABLEAU_TO_FOUNDATION = "tableau_to_foundation"
    CARD_REVEALED = "card_revealed"
    FOUNDATION_TO_TABLEAU = "foundation_to_tableau"
    RECYCLE_WASTE = "recycle_waste"
    UNDO_MOVE = "undo_move"
    HINT_USED = "hint_used"


@dataclass(frozen=True)
class ScoringConfig:
    """Configuration for scoring system with all bonuses and multipliers.
    
    Defines point values for events, difficulty multipliers, and various
    bonuses. All values match Microsoft Solitaire scoring standards.
    
    Attributes:
        event_points: Point values for each event type
        difficulty_multipliers: Score multipliers by difficulty level (1-5)
        deck_type_bonuses: Bonus points by deck type
        draw_count_bonuses: Bonus points by draw count (levels 1-3 only)
        victory_bonus: Bonus points awarded for winning
        min_score: Minimum possible score (clamp floor)
    """
    
    # Event point values (Microsoft Solitaire standard)
    event_points: Dict[ScoreEventType, int] = field(default_factory=lambda: {
        ScoreEventType.WASTE_TO_FOUNDATION: 10,
        ScoreEventType.TABLEAU_TO_FOUNDATION: 10,
        ScoreEventType.CARD_REVEALED: 5,
        ScoreEventType.FOUNDATION_TO_TABLEAU: -15,
        ScoreEventType.RECYCLE_WASTE: -20,  # Only after 3rd recycle
        ScoreEventType.UNDO_MOVE: 0,  # Reserved for future
        ScoreEventType.HINT_USED: 0,  # Reserved for future
    })
    
    # Difficulty multipliers (progressive scaling)
    difficulty_multipliers: Dict[int, float] = field(default_factory=lambda: {
        1: 1.0,   # Facile (Easy)
        2: 1.25,  # Medio (Medium)
        3: 1.5,   # Difficile (Hard)
        4: 2.0,   # Esperto (Expert)
        5: 2.5,   # Maestro (Master)
    })
    
    # Deck type bonuses (more cards = more bonus)
    deck_type_bonuses: Dict[str, int] = field(default_factory=lambda: {
        "neapolitan": 0,    # 40 cards (baseline)
        "french": 150,      # 52 cards (+12 cards bonus)
    })
    
    # Draw count bonuses (levels 1-3 only, higher draw = more bonus)
    draw_count_bonuses: Dict[int, int] = field(default_factory=lambda: {
        1: 0,      # Draw 1 card (easiest)
        2: 100,    # Draw 2 cards
        3: 200,    # Draw 3 cards (hardest)
    })
    
    # Victory bonus (awarded only when game is won)
    victory_bonus: int = 500
    
    # Minimum score (never go below 0)
    min_score: int = 0


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
