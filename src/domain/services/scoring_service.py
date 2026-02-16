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
        self.stock_draw_count = 0  # v2.0 NEW: Cumulative stock draw counter
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
        
        Special handling for:
        - RECYCLE_WASTE: Progressive penalty (0, 0, -10, -20, -35, -55, -80)
        - STOCK_DRAW: Progressive penalty (0 for first 20, then -1, then -2)
        
        Args:
            event_type: Type of event
            
        Returns:
            Points to award/deduct
        """
        # Special case: STOCK_DRAW progressive penalty (v2.0)
        if event_type == ScoreEventType.STOCK_DRAW:
            self.stock_draw_count += 1
            return self._calculate_stock_draw_penalty()
        
        # Special case: RECYCLE_WASTE progressive penalty (v2.0)
        if event_type == ScoreEventType.RECYCLE_WASTE:
            self.recycle_count += 1
            return self._calculate_recycle_penalty(self.recycle_count)
        
        # All other events: use base points from config
        points = self.config.event_points[event_type]
        return points
    
    def _calculate_stock_draw_penalty(self) -> int:
        """Calculate progressive penalty for stock draws (v2.0).
        
        Penalty tiers:
        - Draws 1-20: 0 points (free)
        - Draws 21-40: -1 point per draw
        - Draws 41+: -2 points per draw
        
        Returns:
            Penalty points for current stock_draw_count
        """
        if self.stock_draw_count <= self.config.stock_draw_thresholds[0]:
            return 0  # First 20 draws are free
        elif self.stock_draw_count <= self.config.stock_draw_thresholds[1]:
            return self.config.stock_draw_penalties[1]  # -1pt
        else:
            return self.config.stock_draw_penalties[2]  # -2pt
    
    def _calculate_recycle_penalty(self, recycle_count: int) -> int:
        """Calculate progressive penalty for waste recycling (v2.0).
        
        Guard against invalid recycle_count <= 0.
        
        Penalty schedule:
        - Recycle 1-2: 0 points (free)
        - Recycle 3: -10 points
        - Recycle 4: -20 points
        - Recycle 5: -35 points
        - Recycle 6: -55 points
        - Recycle 7+: -80 points (clamped)
        
        Args:
            recycle_count: Number of recycles (1-indexed)
            
        Returns:
            Penalty points for this recycle
        """
        # Guard: Invalid recycle count
        if recycle_count <= 0:
            return 0
        
        # Index into penalty array (recycle_count-1), clamped to max index
        index = min(recycle_count - 1, len(self.config.recycle_penalties) - 1)
        penalty = self.config.recycle_penalties[index]
        
        # Log recycle penalty if non-zero
        if penalty != 0:
            log.warning_issued(
                "Scoring",
                f"Recycle penalty: {penalty} points (recycle #{recycle_count})"
            )
        
        return penalty
    
    # ========================================
    # NUMERIC HELPERS (v2.0)
    # ========================================
    
    def _safe_truncate(self, value: float, context: str = "") -> int:
        """Safe truncation with Rule 5 invariant enforcement (v2.0).
        
        Truncates float to int using Python's int() (floor for positive numbers).
        Enforces non-negativity constraint to guarantee consistent behavior.
        
        Args:
            value: Float value to truncate
            context: Context string for error message
            
        Returns:
            Truncated integer value
            
        Raises:
            ValueError: If value < 0 (domain invariant violation)
            
        Note:
            Python int() behavior differs for negative numbers:
            - int(1.9) → 1 (floor)
            - int(-1.9) → -1 (NOT floor, truncation toward zero)
            
            To guarantee floor behavior, we enforce non-negativity.
        """
        if value < 0:
            raise ValueError(
                f"Truncation safety violated: {value} < 0 "
                f"(context: {context}). Domain logic bug - values "
                f"must be clamped to min_score before truncation."
            )
        return int(value)
    
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
            - Draw bonus: levels 1-3 get full (low), levels 4-5 get 50% (high)
            - Score cannot go below min_score (0)
        """
        base_score = self.get_base_score()
        deck_bonus = self.config.deck_type_bonuses[self.deck_type]
        
        # Draw bonus: v2.0 tier system (low/high)
        draw_bonus = 0
        if self.difficulty_level <= 3:
            # Levels 1-3: full bonus (low tier)
            draw_bonus = self.config.draw_count_bonuses[self.draw_count]["low"]
        else:
            # Levels 4-5: 50% bonus (high tier)
            draw_bonus = self.config.draw_count_bonuses[self.draw_count]["high"]
        
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
        total_before_clamp = total_score
        total_score = max(self.config.min_score, total_score)
        
        # Log score clamping if occurred
        if total_before_clamp < self.config.min_score:
            log.warning_issued(
                "Scoring",
                f"Score clamped: {total_before_clamp} → {total_score} (minimum enforced)"
            )
        
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
        """Calculate time bonus based on elapsed time (v2.0 values).
        
        Logic differs based on timer state:
        
        Timer OFF:
            Linear decay formula: max(0, 1200 - (elapsed_minutes * 40))
            - Max bonus: 1200 points (instant win)
            - Decay: -40 points per minute
            - Zero bonus: 30 minutes
            
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
            # Timer OFF: Linear decay formula (v2.0)
            elapsed_minutes = elapsed_seconds / 60.0
            
            # max(0, 1200 - (elapsed_minutes * 40))
            bonus_float = self.config.time_bonus_max_timer_off - (
                elapsed_minutes * self.config.time_bonus_decay_per_minute
            )
            bonus_clamped = max(0, bonus_float)
            return self._safe_truncate(bonus_clamped, "time_bonus_timer_off")
        
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
                    # PERMISSIVE mode (v1.5.2.2): Calculate overtime malus
                    overtime_seconds = abs(time_remaining)
                    overtime_minutes = max(1, int(overtime_seconds // 60))  # At least 1 minute
                    malus = self.config.overtime_penalty_per_minute * overtime_minutes
                    
                    # Log overtime penalty
                    log.warning_issued(
                        "Scoring",
                        f"Penalty applied: overtime = {malus} points ({overtime_minutes} min)"
                    )
                    
                    return malus
            
            # Within time limit: percentage-based bonus (v2.0)
            time_remaining_percentage = time_remaining / self.timer_limit_seconds
            
            bonus = 0
            if time_remaining_percentage >= 0.50:
                bonus = self.config.time_bonus_max_timer_on  # ≥50% remaining: 1000pt
            elif time_remaining_percentage >= 0.25:
                bonus = self.config.time_bonus_max_timer_on // 2  # ≥25% remaining: 500pt
            elif time_remaining_percentage > 0:
                bonus = self.config.time_bonus_max_timer_on // 5  # >0% remaining: 200pt
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
    # QUALITY FACTORS (v2.0)
    # ========================================
    
    def _calculate_time_quality(self, elapsed_seconds: float) -> float:
        """Calculate time quality factor for victory bonus (v2.0).
        
        Quality depends on timer state:
        
        Timer OFF (absolute minutes):
            - ≤10 min: 1.5 (velocissimo)
            - ≤20 min: 1.2 (veloce)
            - ≤30 min: 1.0 (medio)
            - ≤45 min: 0.8 (lento)
            - >45 min: 0.7 (molto lento)
        
        Timer ON (percentage remaining):
            - ≥80%: 1.5 (ottimo)
            - ≥50%: 1.2 (buono)
            - ≥25%: 1.0 (medio)
            - >0%:  0.8 (appena entro limite)
            - ≤0%:  0.7 (overtime)
        
        Args:
            elapsed_seconds: Time taken to complete game
            
        Returns:
            Quality factor in range [0.7, 1.5]
        """
        if not self.timer_enabled or self.timer_limit_seconds <= 0:
            # Timer OFF: absolute time thresholds
            elapsed_minutes = elapsed_seconds / 60.0
            
            if elapsed_minutes <= 10:
                return 1.5  # Velocissimo
            elif elapsed_minutes <= 20:
                return 1.2  # Veloce
            elif elapsed_minutes <= 30:
                return 1.0  # Medio
            elif elapsed_minutes <= 45:
                return 0.8  # Lento
            else:
                return 0.7  # Molto lento
        else:
            # Timer ON: percentage-based thresholds
            time_remaining = self.timer_limit_seconds - elapsed_seconds
            time_remaining_pct = time_remaining / self.timer_limit_seconds
            
            if time_remaining_pct >= 0.80:
                return 1.5  # 80%+ remaining
            elif time_remaining_pct >= 0.50:
                return 1.2  # 50%+ remaining
            elif time_remaining_pct >= 0.25:
                return 1.0  # 25%+ remaining
            elif time_remaining_pct > 0:
                return 0.8  # Entro limite
            else:
                return 0.7  # Overtime
    
    def _calculate_move_quality(self, move_count: int) -> float:
        """Calculate move quality factor for victory bonus (v2.0).
        
        Quality thresholds based on move efficiency:
        - ≤80 moves:  1.3 (ottimale)
        - ≤120 moves: 1.1 (buono)
        - ≤180 moves: 1.0 (medio)
        - ≤250 moves: 0.85 (basso)
        - >250 moves: 0.7 (brute force)
        
        Args:
            move_count: Total moves made
            
        Returns:
            Quality factor in range [0.7, 1.3]
        """
        if move_count <= 80:
            return 1.3  # Ottimale
        elif move_count <= 120:
            return 1.1  # Buono
        elif move_count <= 180:
            return 1.0  # Medio
        elif move_count <= 250:
            return 0.85  # Basso
        else:
            return 0.7  # Brute force
    
    def _calculate_recycle_quality(self, recycle_count: int) -> float:
        """Calculate recycle quality factor for victory bonus (v2.0).
        
        Quality thresholds based on waste recycling:
        - 0 recycles:  1.2 (perfetto - zero ricicli)
        - ≤2 recycles: 1.1 (ottimo)
        - ≤4 recycles: 1.0 (medio)
        - ≤7 recycles: 0.8 (molti)
        - >7 recycles: 0.5 (tantissimi)
        
        Args:
            recycle_count: Number of times waste was recycled
            
        Returns:
            Quality factor in range [0.5, 1.2]
        """
        if recycle_count == 0:
            return 1.2  # Perfetto (zero ricicli)
        elif recycle_count <= 2:
            return 1.1  # Ottimo
        elif recycle_count <= 4:
            return 1.0  # Medio
        elif recycle_count <= 7:
            return 0.8  # Molti
        else:
            return 0.5  # Tantissimi
    
    def _calculate_victory_bonus_with_quality(
        self,
        elapsed_seconds: float,
        move_count: int,
        recycle_count: int
    ) -> tuple[int, float]:
        """Calculate composite victory bonus with quality multiplier (v2.0).
        
        Combines three quality factors with weighted average:
        - Time quality: 35% weight
        - Move quality: 35% weight
        - Recycle quality: 30% weight
        
        Formula:
            quality_multiplier = (
                time_quality * 0.35 +
                move_quality * 0.35 +
                recycle_quality * 0.30
            )
            victory_bonus = BASE_VICTORY * quality_multiplier
        
        Args:
            elapsed_seconds: Time taken to complete game
            move_count: Total moves made
            recycle_count: Number of times waste was recycled
            
        Returns:
            Tuple of (victory_bonus, quality_multiplier)
            - victory_bonus: Integer points in range [252, 536]
            - quality_multiplier: Float in range [0.63, 1.34]
        
        Note:
            Theoretical max: 1.5*0.35 + 1.3*0.35 + 1.2*0.30 = 1.34 → 536pt
            Theoretical min: 0.7*0.35 + 0.7*0.35 + 0.5*0.30 = 0.63 → 252pt
        """
        # Calculate individual quality factors
        time_quality = self._calculate_time_quality(elapsed_seconds)
        move_quality = self._calculate_move_quality(move_count)
        recycle_quality = self._calculate_recycle_quality(recycle_count)
        
        # Weighted average using config weights
        quality_multiplier = (
            time_quality * self.config.victory_weights["time"] +
            move_quality * self.config.victory_weights["moves"] +
            recycle_quality * self.config.victory_weights["recycles"]
        )
        
        # Calculate victory bonus with safe truncation
        victory_bonus_float = self.config.victory_bonus_base * quality_multiplier
        victory_bonus = self._safe_truncate(victory_bonus_float, "victory_bonus")
        
        # Log breakdown for debugging
        log.info_query_requested(
            "scoring_victory_bonus",
            f"Victory bonus breakdown: time_q={time_quality:.2f} "
            f"move_q={move_quality:.2f} recycle_q={recycle_quality:.2f} "
            f"→ quality={quality_multiplier:.3f} → bonus={victory_bonus}pt"
        )
        
        return victory_bonus, quality_multiplier
    
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
        
        Clears all events, recycle count, and stock draw count.
        Does not reset configuration.
        """
        self.events = []
        self.recycle_count = 0
        self.stock_draw_count = 0  # v2.0 NEW
