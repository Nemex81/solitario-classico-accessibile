"""Domain service for scoring system logic v2.0.0.

Provides pure business logic for:
- Recording score events
- Calculating provisional scores (in-progress)
- Calculating final scores (with time and victory bonuses)
- Querying score history and statistics

All calculations are pure (no I/O, no side effects).
"""

import math
from typing import List, Optional

from src.domain.models.scoring import (
    ScoreEvent,
    ScoreEventType,
    ScoringConfig,
    ProvisionalScore,
    FinalScore,
)
from src.infrastructure.logging import game_logger as log


class ScoringService:
    """Pure domain service for scoring calculations.
    
    Manages score state and calculations during gameplay without
    side effects or I/O operations. All storage and presentation
    concerns handled in infrastructure and presentation layers.
    
    Attributes:
        config: Scoring configuration (points, bonuses, multipliers)
        events: List of all scoring events in current game
        recycle_count: Number of times waste has been recycled
        difficulty_level: Current difficulty level (1-5)
        deck_type: Current deck type ("french" or "neapolitan")
        draw_count: Cards drawn per click (1-3)
        timer_enabled: Whether timer is active
        timer_limit_seconds: Timer limit in seconds (-1 if OFF)
    
    Example:
        >>> config = ScoringConfig()
        >>> service = ScoringService(
        ...     config=config,
        ...     difficulty_level=4,
        ...     deck_type="french",
        ...     draw_count=2,
        ...     timer_enabled=True,
        ...     timer_limit_seconds=1800
        ... )
        >>> service.record_event(ScoreEventType.WASTE_TO_FOUNDATION, "Asso di Cuori")
        >>> provisional = service.calculate_provisional_score()
        >>> print(provisional.total_score)
        325  # (10 base + 150 deck + 100 draw) * 2.0 difficulty
    """
    
    def __init__(
        self,
        config: ScoringConfig,
        difficulty_level: int,
        deck_type: str,
        draw_count: int,
        timer_enabled: bool = False,
        timer_limit_seconds: int = -1
    ):
        """Initialize scoring service with game configuration.
        
        Args:
            config: Scoring configuration with points and bonuses
            difficulty_level: Difficulty level (1-5)
            deck_type: Deck type ("french" or "neapolitan")
            draw_count: Cards drawn per click (1-3)
            timer_enabled: Whether timer is active
            timer_limit_seconds: Timer limit in seconds (-1 if OFF)
        """
        self.config = config
        self.events: List[ScoreEvent] = []
        self.recycle_count = 0
        self.difficulty_level = difficulty_level
        self.deck_type = deck_type
        self.draw_count = draw_count
        self.timer_enabled = timer_enabled
        self.timer_limit_seconds = timer_limit_seconds
    
    # ========================================
    # EVENT RECORDING
    # ========================================
    
    def record_event(
        self,
        event_type: ScoreEventType,
        context: Optional[str] = None
    ) -> ScoreEvent:
        """Record a scoring event.
        
        Args:
            event_type: Type of event that occurred
            context: Optional context (e.g., card name, pile name)
            
        Returns:
            The created ScoreEvent (for testing/logging)
            
        Example:
            >>> event = service.record_event(
            ...     ScoreEventType.CARD_REVEALED,
            ...     "7 di Cuori"
            ... )
            >>> event.points
            5
        """
        points = self._calculate_event_points(event_type)
        event = ScoreEvent(
            event_type=event_type,
            points=points,
            context=context
        )
        self.events.append(event)
        return event
    
    def _calculate_event_points(self, event_type: ScoreEventType) -> int:
        """Calculate points for an event.
        
        Special handling for RECYCLE_WASTE: only applies penalty
        after 3rd recycle (first 3 recycles are free).
        
        Args:
            event_type: Type of event
            
        Returns:
            Points to award/deduct
        """
        points = self.config.event_points[event_type]
        
        # Special case: Recycle penalty only after 3rd recycle
        if event_type == ScoreEventType.RECYCLE_WASTE:
            self.recycle_count += 1
            if self.recycle_count <= 3:
                return 0  # First 3 recycles are free
        
        return points
    
    # ========================================
    # SCORE CALCULATIONS
    # ========================================
    
    def get_base_score(self) -> int:
        """Get sum of all event points.
        
        Returns:
            Sum of points from all recorded events
        """
        return sum(event.points for event in self.events)
    
    def calculate_provisional_score(self) -> ProvisionalScore:
        """Calculate current provisional score (without victory bonus).
        
        Used during gameplay to show current progress.
        
        Returns:
            ProvisionalScore with current totals
            
        Note:
            - Draw bonus only applies at levels 1-3
            - Score cannot go below min_score (0)
        """
        base_score = self.get_base_score()
        deck_bonus = self.config.deck_type_bonuses[self.deck_type]
        
        # Draw bonus only for levels 1-3
        draw_bonus = 0
        if self.difficulty_level <= 3:
            draw_bonus = self.config.draw_count_bonuses[self.draw_count]
        
        difficulty_multiplier = self.config.difficulty_multipliers[self.difficulty_level]
        
        provisional = ProvisionalScore(
            base_score=base_score,
            deck_bonus=deck_bonus,
            draw_bonus=draw_bonus,
            difficulty_multiplier=difficulty_multiplier
        )
        
        # Clamp to minimum score
        if provisional.total_score < self.config.min_score:
            # Return new provisional with adjusted base_score
            adjusted_base = self.config.min_score - deck_bonus - draw_bonus
            return ProvisionalScore(
                base_score=adjusted_base,
                deck_bonus=deck_bonus,
                draw_bonus=draw_bonus,
                difficulty_multiplier=1.0  # Reset multiplier to avoid negative
            )
        
        return provisional
    
    def calculate_final_score(
        self,
        elapsed_seconds: float,
        move_count: int,
        is_victory: bool,
        timer_strict_mode: bool = True  # 🆕 NEW PARAMETER v1.5.2.2
    ) -> FinalScore:
        """Calculate final score at game end with overtime malus support.
        
        Args:
            elapsed_seconds: Time taken to complete game
            move_count: Total moves made
            is_victory: Whether game was won
            timer_strict_mode: Timer expiration behavior (v1.5.2.2)
                - True: STRICT mode (game stops at timeout, no overtime possible)
                - False: PERMISSIVE mode (overtime allowed with penalty)
            
        Returns:
            FinalScore with complete breakdown including overtime malus
            
        Note:
            Time bonus calculation differs based on timer state:
            - Timer OFF: Progressive decay (10000/sqrt(seconds))
            - Timer ON within limit: Percentage-based (≥50%: +1000, ≥25%: +500, etc.)
            - Timer ON in overtime (PERMISSIVE only): -100 points per minute
        """
        provisional = self.calculate_provisional_score()
        
        # Calculate time bonus (handles overtime in PERMISSIVE mode)
        time_bonus = self._calculate_time_bonus(elapsed_seconds, timer_strict_mode)
        
        # Victory bonus (only if won)
        victory_bonus = self.config.victory_bonus if is_victory else 0
        
        # Calculate total (formula from specification)
        total_before_time = provisional.total_score
        total_score = total_before_time + time_bonus + victory_bonus
        
        # Clamp to minimum
        total_score = max(self.config.min_score, total_score)
        
        return FinalScore(
            base_score=provisional.base_score,
            deck_bonus=provisional.deck_bonus,
            draw_bonus=provisional.draw_bonus,
            difficulty_multiplier=provisional.difficulty_multiplier,
            time_bonus=time_bonus,
            victory_bonus=victory_bonus,
            total_score=total_score,
            is_victory=is_victory,
            elapsed_seconds=elapsed_seconds,
            difficulty_level=self.difficulty_level,
            deck_type=self.deck_type,
            draw_count=self.draw_count,
            recycle_count=self.recycle_count,
            move_count=move_count
        )
    
    def _calculate_time_bonus(self, elapsed_seconds: float, timer_strict_mode: bool = True) -> int:
        """Calculate time bonus based on elapsed time with overtime malus support.
        
        Logic differs based on timer state:
        
        Timer OFF:
            Progressive decay formula: min(2000, 10000/sqrt(elapsed_seconds))
            Faster completion = higher bonus
            
        Timer ON (within limit):
            Percentage-based:
            - ≥50% time remaining: +1000
            - ≥25% time remaining: +500
            - >0% time remaining: +200
            
        Timer ON (overtime - PERMISSIVE mode only):
            Malus penalty: -100 points per overtime minute
            - Example: 10min limit, finished in 12min = -200pts
            - Note: STRICT mode never reaches this (game stops at timeout)
        
        Args:
            elapsed_seconds: Time taken to complete game
            timer_strict_mode: Whether timer stops game at expiration (v1.5.2.2)
            
        Returns:
            Time bonus points (can be negative if overtime in PERMISSIVE mode)
        """
        if not self.timer_enabled or self.timer_limit_seconds <= 0:
            # Timer OFF: Progressive decay formula
            if elapsed_seconds <= 0:
                return 2000  # Instant win (theoretical max)
            
            bonus = int(10000 / math.sqrt(elapsed_seconds))
            return min(2000, bonus)  # Cap at 2000
        
        else:
            # Timer ON: Percentage-based or overtime malus
            time_remaining = self.timer_limit_seconds - elapsed_seconds
            
            if time_remaining < 0:
                # Timer expired - check mode
                if timer_strict_mode:
                    # STRICT mode: Game stops at timeout, this shouldn't happen
                    # But return penalty just in case
                    return -500
                else:
                    # 🆕 PERMISSIVE mode (v1.5.2.2): Calculate overtime malus
                    overtime_seconds = abs(time_remaining)
                    overtime_minutes = max(1, int(overtime_seconds // 60))  # At least 1 minute
                    malus = -100 * overtime_minutes
                    
                    # Log overtime penalty
                    log.warning_issued(
                        "Scoring",
                        f"Penalty applied: overtime = {malus} points ({overtime_minutes} min)"
                    )
                    
                    return malus
            
            # Within time limit: percentage-based bonus
            time_used_percentage = elapsed_seconds / self.timer_limit_seconds
            time_remaining_percentage = 1.0 - time_used_percentage
            
            bonus = 0
            if time_remaining_percentage >= 0.50:
                bonus = 1000  # ≥50% remaining
            elif time_remaining_percentage >= 0.25:
                bonus = 500   # ≥25% remaining
            elif time_remaining_percentage > 0:
                bonus = 200   # >0% remaining
            else:
                bonus = -500  # Timer expired (edge case)
            
            # Log time bonus if positive
            if bonus > 0:
                log.info_query_requested(
                    "scoring_bonus",
                    f"fast_completion = +{bonus} points ({int(time_remaining_percentage * 100)}% time remaining)"
                )
            
            return bonus
    
    # ========================================
    # QUERIES
    # ========================================
    
    def get_event_count(self) -> int:
        """Get total number of events recorded.
        
        Returns:
            Number of events in history
        """
        return len(self.events)
    
    def get_recent_events(self, count: int = 5) -> List[ScoreEvent]:
        """Get most recent scoring events.
        
        Args:
            count: Number of events to return (default 5)
            
        Returns:
            List of most recent events (newest first)
            
        Example:
            >>> events = service.get_recent_events(3)
            >>> for event in events:
            ...     print(event)
        """
        return list(reversed(self.events[-count:]))
    
    # ========================================
    # STATE MANAGEMENT
    # ========================================
    
    def reset(self) -> None:
        """Reset scoring state for new game.
        
        Clears all events and recycle count.
        Does not reset configuration.
        """
        self.events = []
        self.recycle_count = 0
