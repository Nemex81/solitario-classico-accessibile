"""Statistics aggregation service for profile data.

Provides centralized logic for updating all statistics from session outcomes.
Encapsulates the aggregation rules and ensures consistency across all stat types.
"""

from src.domain.models.profile import SessionOutcome
from src.domain.models.statistics import GlobalStats, TimerStats, DifficultyStats, ScoringStats


class StatsAggregator:
    """Service for aggregating session outcomes into statistics.
    
    Provides a single entry point for updating all stat categories from a session.
    Ensures consistent application of aggregation rules.
    """
    
    @staticmethod
    def update_all_stats(
        session: SessionOutcome,
        global_stats: GlobalStats,
        timer_stats: TimerStats,
        difficulty_stats: DifficultyStats,
        scoring_stats: ScoringStats
    ) -> None:
        """Update all statistics from a session outcome.
        
        This is the main aggregation method that updates all 4 stat categories.
        
        Args:
            session: The completed session to aggregate
            global_stats: Global statistics to update (in-place)
            timer_stats: Timer statistics to update (in-place)
            difficulty_stats: Difficulty statistics to update (in-place)
            scoring_stats: Scoring statistics to update (in-place)
        """
        global_stats.update_from_session(session)
        timer_stats.update_from_session(session)
        difficulty_stats.update_from_session(session)
        scoring_stats.update_from_session(session)
    
    @staticmethod
    def create_initial_stats() -> tuple[GlobalStats, TimerStats, DifficultyStats, ScoringStats]:
        """Create initial empty statistics for a new profile.
        
        Returns:
            Tuple of (global_stats, timer_stats, difficulty_stats, scoring_stats)
        """
        return (
            GlobalStats(),
            TimerStats(),
            DifficultyStats(),
            ScoringStats()
        )
    
    @staticmethod
    def validate_session(session: SessionOutcome) -> bool:
        """Validate that a session outcome is ready for aggregation.
        
        Args:
            session: Session to validate
            
        Returns:
            True if session is valid for aggregation
        """
        # Basic validation
        if not session.session_id:
            return False
        if not session.profile_id:
            return False
        if session.elapsed_time < 0:
            return False
        
        # Ensure timer consistency
        if session.timer_enabled:
            if session.timer_limit <= 0:
                return False
            if session.overtime_duration < 0:
                return False
        
        # Ensure scoring consistency
        if session.scoring_enabled:
            if session.final_score < 0:
                return False
        
        return True
    
    @staticmethod
    def recalculate_all_stats(
        sessions: list[SessionOutcome]
    ) -> tuple[GlobalStats, TimerStats, DifficultyStats, ScoringStats]:
        """Recalculate all statistics from a list of sessions.
        
        Useful for:
        - Rebuilding stats after corruption
        - Validating aggregated stats
        - Migration/import scenarios
        
        Args:
            sessions: List of all sessions for a profile
            
        Returns:
            Tuple of freshly calculated statistics
        """
        stats = StatsAggregator.create_initial_stats()
        global_stats, timer_stats, difficulty_stats, scoring_stats = stats
        
        for session in sessions:
            if StatsAggregator.validate_session(session):
                StatsAggregator.update_all_stats(
                    session,
                    global_stats,
                    timer_stats,
                    difficulty_stats,
                    scoring_stats
                )
        
        return global_stats, timer_stats, difficulty_stats, scoring_stats
