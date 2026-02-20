"""Unit tests for StatsAggregator service."""

import pytest
from src.domain.services.stats_aggregator import StatsAggregator
from src.domain.models.profile import SessionOutcome
from src.domain.models.statistics import GlobalStats, TimerStats, DifficultyStats, ScoringStats
from src.domain.models.game_end import EndReason


class TestStatsAggregator:
    """Test suite for StatsAggregator."""
    
    def test_create_initial_stats(self) -> None:
        """Test creating initial empty statistics."""
        global_stats, timer_stats, difficulty_stats, scoring_stats = (
            StatsAggregator.create_initial_stats()
        )
        
        assert isinstance(global_stats, GlobalStats)
        assert isinstance(timer_stats, TimerStats)
        assert isinstance(difficulty_stats, DifficultyStats)
        assert isinstance(scoring_stats, ScoringStats)
        
        assert global_stats.total_games == 0
        assert timer_stats.games_with_timer == 0
    
    def test_update_all_stats_victory(self) -> None:
        """Test updating all stats from a victory session."""
        stats = StatsAggregator.create_initial_stats()
        global_stats, timer_stats, difficulty_stats, scoring_stats = stats
        
        session = SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=180.0,
            timer_enabled=True,
            timer_limit=300,
            timer_mode="STRICT",
            timer_expired=False,
            scoring_enabled=True,
            final_score=1500,
            difficulty_level=3
        )
        
        StatsAggregator.update_all_stats(
            session, global_stats, timer_stats, difficulty_stats, scoring_stats
        )
        
        # Verify all stats were updated
        assert global_stats.total_games == 1
        assert global_stats.total_victories == 1
        assert timer_stats.games_with_timer == 1
        assert timer_stats.victories_within_time == 1
        assert difficulty_stats.games_by_level[3] == 1
        assert scoring_stats.games_with_scoring == 1
    
    def test_update_all_stats_defeat(self) -> None:
        """Test updating all stats from a defeat session."""
        stats = StatsAggregator.create_initial_stats()
        global_stats, timer_stats, difficulty_stats, scoring_stats = stats
        
        session = SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.ABANDON_EXIT,
            is_victory=False,
            elapsed_time=60.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False,
            scoring_enabled=False
        )
        
        StatsAggregator.update_all_stats(
            session, global_stats, timer_stats, difficulty_stats, scoring_stats
        )
        
        assert global_stats.total_games == 1
        assert global_stats.total_defeats == 1
        assert timer_stats.games_with_timer == 0  # Timer was off
        assert scoring_stats.games_with_scoring == 0  # Scoring was off
    
    def test_update_all_stats_multiple_sessions(self) -> None:
        """Test updating stats from multiple sessions."""
        stats = StatsAggregator.create_initial_stats()
        global_stats, timer_stats, difficulty_stats, scoring_stats = stats
        
        # Add 3 victories
        for i in range(3):
            session = SessionOutcome.create_new(
                profile_id="test",
                end_reason=EndReason.VICTORY,
                is_victory=True,
                elapsed_time=100.0 + i * 10,
                timer_enabled=True,
                timer_limit=300,
                timer_mode="STRICT",
                timer_expired=False,
                difficulty_level=3
            )
            StatsAggregator.update_all_stats(
                session, global_stats, timer_stats, difficulty_stats, scoring_stats
            )
        
        # Add 1 defeat
        session = SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.ABANDON_EXIT,
            is_victory=False,
            elapsed_time=50.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False,
            difficulty_level=3
        )
        StatsAggregator.update_all_stats(
            session, global_stats, timer_stats, difficulty_stats, scoring_stats
        )
        
        assert global_stats.total_games == 4
        assert global_stats.total_victories == 3
        assert global_stats.total_defeats == 1
        assert global_stats.winrate == pytest.approx(0.75, rel=0.01)
    
    def test_validate_session_valid(self) -> None:
        """Test session validation for valid session."""
        session = SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=180.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False
        )
        
        assert StatsAggregator.validate_session(session) is True
    
    def test_validate_session_invalid_negative_time(self) -> None:
        """Test session validation rejects negative elapsed time."""
        session = SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=-10.0,  # Invalid
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False
        )
        
        assert StatsAggregator.validate_session(session) is False
    
    def test_validate_session_invalid_timer_limit(self) -> None:
        """Test session validation rejects invalid timer configuration."""
        session = SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=100.0,
            timer_enabled=True,  # Timer enabled
            timer_limit=0,  # But limit is 0 - invalid
            timer_mode="STRICT",
            timer_expired=False
        )
        
        assert StatsAggregator.validate_session(session) is False
    
    def test_validate_session_invalid_overtime(self) -> None:
        """Test session validation rejects negative overtime."""
        session = SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.VICTORY_OVERTIME,
            is_victory=True,
            elapsed_time=400.0,
            timer_enabled=True,
            timer_limit=300,
            timer_mode="PERMISSIVE",
            timer_expired=True,
            overtime_duration=-10.0  # Invalid
        )
        
        assert StatsAggregator.validate_session(session) is False
    
    def test_validate_session_invalid_score(self) -> None:
        """Test session validation rejects negative score."""
        session = SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=100.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False,
            scoring_enabled=True,
            final_score=-100  # Invalid
        )
        
        assert StatsAggregator.validate_session(session) is False
    
    def test_recalculate_all_stats(self) -> None:
        """Test recalculating all stats from session list."""
        sessions = []
        
        # Create 5 sessions
        for i in range(5):
            is_victory = i < 3  # 3 victories, 2 defeats
            session = SessionOutcome.create_new(
                profile_id="test",
                end_reason=EndReason.VICTORY if is_victory else EndReason.ABANDON_EXIT,
                is_victory=is_victory,
                elapsed_time=100.0 + i * 10,
                timer_enabled=True,
                timer_limit=300,
                timer_mode="STRICT",
                timer_expired=False,
                difficulty_level=3
            )
            sessions.append(session)
        
        global_stats, timer_stats, difficulty_stats, scoring_stats = (
            StatsAggregator.recalculate_all_stats(sessions)
        )
        
        assert global_stats.total_games == 5
        assert global_stats.total_victories == 3
        assert global_stats.total_defeats == 2
        assert global_stats.winrate == pytest.approx(0.6, rel=0.01)
        assert timer_stats.games_with_timer == 5
        assert difficulty_stats.games_by_level[3] == 5
    
    def test_recalculate_all_stats_skips_invalid(self) -> None:
        """Test that recalculation skips invalid sessions."""
        sessions = []
        
        # Valid session
        sessions.append(SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=100.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False
        ))
        
        # Invalid session (negative time)
        invalid = SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=-10.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False
        )
        sessions.append(invalid)
        
        global_stats, timer_stats, difficulty_stats, scoring_stats = (
            StatsAggregator.recalculate_all_stats(sessions)
        )
        
        # Only valid session should be counted
        assert global_stats.total_games == 1
    
    def test_recalculate_empty_sessions(self) -> None:
        """Test recalculating from empty session list."""
        global_stats, timer_stats, difficulty_stats, scoring_stats = (
            StatsAggregator.recalculate_all_stats([])
        )
        
        assert global_stats.total_games == 0
        assert timer_stats.games_with_timer == 0
