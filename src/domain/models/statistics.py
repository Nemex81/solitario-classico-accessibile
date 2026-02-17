"""Aggregate statistics models for profile data."""

from dataclasses import dataclass, field
from typing import Dict

from src.domain.models.game_end import EndReason


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
    
    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "total_games": self.total_games,
            "total_victories": self.total_victories,
            "total_defeats": self.total_defeats,
            "winrate": self.winrate,
            "total_playtime": self.total_playtime,
            "average_game_time": self.average_game_time,
            "fastest_victory": self.fastest_victory if self.fastest_victory != float('inf') else None,
            "slowest_victory": self.slowest_victory,
            "highest_score": self.highest_score,
            "longest_streak": self.longest_streak,
            "current_streak": self.current_streak
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "GlobalStats":
        """Create from JSON dict."""
        data = data.copy()
        if data.get("fastest_victory") is None:
            data["fastest_victory"] = float('inf')
        return cls(**data)


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
    
    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "games_with_timer": self.games_with_timer,
            "victories_within_time": self.victories_within_time,
            "victories_overtime": self.victories_overtime,
            "defeats_timeout": self.defeats_timeout,
            "total_overtime": self.total_overtime,
            "average_overtime": self.average_overtime,
            "max_overtime": self.max_overtime,
            "average_time_vs_limit": self.average_time_vs_limit
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TimerStats":
        """Create from JSON dict."""
        return cls(**data)


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
    
    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "games_by_level": {str(k): v for k, v in self.games_by_level.items()},
            "victories_by_level": {str(k): v for k, v in self.victories_by_level.items()},
            "winrate_by_level": {str(k): v for k, v in self.winrate_by_level.items()},
            "average_score_by_level": {str(k): v for k, v in self.average_score_by_level.items()}
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "DifficultyStats":
        """Create from JSON dict."""
        return cls(
            games_by_level={int(k): v for k, v in data.get("games_by_level", {}).items()},
            victories_by_level={int(k): v for k, v in data.get("victories_by_level", {}).items()},
            winrate_by_level={int(k): v for k, v in data.get("winrate_by_level", {}).items()},
            average_score_by_level={int(k): v for k, v in data.get("average_score_by_level", {}).items()}
        )


@dataclass
class ScoringStats:
    """Statistics for games with scoring enabled."""
    
    games_with_scoring: int = 0
    
    total_score: int = 0                  # Sum of all scores
    average_score: float = 0.0
    highest_score: int = 0
    lowest_score: int = 0                 # Only victories (0 means no victories yet)
    
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
            if self.lowest_score == 0 or outcome.final_score < self.lowest_score:
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
    
    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "games_with_scoring": self.games_with_scoring,
            "total_score": self.total_score,
            "average_score": self.average_score,
            "highest_score": self.highest_score,
            "lowest_score": self.lowest_score,
            "perfect_games": self.perfect_games,
            "good_games": self.good_games,
            "average_games": self.average_games
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ScoringStats":
        """Create from JSON dict."""
        return cls(**data)
