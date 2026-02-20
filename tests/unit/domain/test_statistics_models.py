"""Unit tests for statistics aggregate models."""

import pytest
from src.domain.models.statistics import (
    GlobalStats,
    TimerStats,
    DifficultyStats,
    ScoringStats
)
from src.domain.models.profile import SessionOutcome
from src.domain.models.game_end import EndReason


class TestGlobalStats:
    """Test suite for GlobalStats model."""
    
    def test_initial_state(self) -> None:
        """Test initial state of GlobalStats."""
        stats = GlobalStats()
        
        assert stats.total_games == 0
        assert stats.total_victories == 0
        assert stats.total_defeats == 0
        assert stats.winrate == 0.0
        assert stats.total_playtime == 0.0
        assert stats.current_streak == 0
        assert stats.longest_streak == 0
    
    def test_update_from_victory(self) -> None:
        """Test updating stats from a victory session."""
        stats = GlobalStats()
        session = SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=180.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False,
            final_score=1500
        )
        
        stats.update_from_session(session)
        
        assert stats.total_games == 1
        assert stats.total_victories == 1
        assert stats.total_defeats == 0
        assert stats.winrate == 1.0
        assert stats.current_streak == 1
        assert stats.longest_streak == 1
        assert stats.highest_score == 1500
    
    def test_update_from_defeat(self) -> None:
        """Test updating stats from a defeat session."""
        stats = GlobalStats()
        session = SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.ABANDON_EXIT,
            is_victory=False,
            elapsed_time=60.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False
        )
        
        stats.update_from_session(session)
        
        assert stats.total_games == 1
        assert stats.total_victories == 0
        assert stats.total_defeats == 1
        assert stats.winrate == 0.0
        assert stats.current_streak == 0
    
    def test_winrate_calculation(self) -> None:
        """Test winrate calculation with mixed results."""
        stats = GlobalStats()
        
        # Add 3 victories
        for _ in range(3):
            victory = SessionOutcome.create_new(
                profile_id="test",
                end_reason=EndReason.VICTORY,
                is_victory=True,
                elapsed_time=100.0,
                timer_enabled=False,
                timer_limit=0,
                timer_mode="OFF",
                timer_expired=False
            )
            stats.update_from_session(victory)
        
        # Add 2 defeats
        for _ in range(2):
            defeat = SessionOutcome.create_new(
                profile_id="test",
                end_reason=EndReason.ABANDON_EXIT,
                is_victory=False,
                elapsed_time=50.0,
                timer_enabled=False,
                timer_limit=0,
                timer_mode="OFF",
                timer_expired=False
            )
            stats.update_from_session(defeat)
        
        assert stats.total_games == 5
        assert stats.total_victories == 3
        assert stats.total_defeats == 2
        assert stats.winrate == pytest.approx(0.6, rel=0.01)
    
    def test_streak_tracking(self) -> None:
        """Test streak tracking with victories and defeats."""
        stats = GlobalStats()
        
        # Win 3 times
        for _ in range(3):
            stats.update_from_session(SessionOutcome.create_new(
                profile_id="test",
                end_reason=EndReason.VICTORY,
                is_victory=True,
                elapsed_time=100.0,
                timer_enabled=False,
                timer_limit=0,
                timer_mode="OFF",
                timer_expired=False
            ))
        
        assert stats.current_streak == 3
        assert stats.longest_streak == 3
        
        # Lose once - should break streak
        stats.update_from_session(SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.ABANDON_EXIT,
            is_victory=False,
            elapsed_time=50.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False
        ))
        
        assert stats.current_streak == 0
        assert stats.longest_streak == 3  # Longest preserved
        
        # Win 2 more times
        for _ in range(2):
            stats.update_from_session(SessionOutcome.create_new(
                profile_id="test",
                end_reason=EndReason.VICTORY,
                is_victory=True,
                elapsed_time=100.0,
                timer_enabled=False,
                timer_limit=0,
                timer_mode="OFF",
                timer_expired=False
            ))
        
        assert stats.current_streak == 2
        assert stats.longest_streak == 3  # Still 3
    
    def test_time_records(self) -> None:
        """Test fastest and slowest victory tracking."""
        stats = GlobalStats()
        
        # Fast victory
        stats.update_from_session(SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=120.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False
        ))
        
        assert stats.fastest_victory == 120.0
        assert stats.slowest_victory == 120.0
        
        # Slower victory
        stats.update_from_session(SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=300.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False
        ))
        
        assert stats.fastest_victory == 120.0
        assert stats.slowest_victory == 300.0
        
        # Faster victory
        stats.update_from_session(SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=90.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False
        ))
        
        assert stats.fastest_victory == 90.0
        assert stats.slowest_victory == 300.0
    
    def test_serialization(self) -> None:
        """Test to_dict and from_dict roundtrip."""
        stats = GlobalStats()
        stats.update_from_session(SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=180.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False,
            final_score=1500
        ))
        
        data = stats.to_dict()
        restored = GlobalStats.from_dict(data)
        
        assert restored.total_games == stats.total_games
        assert restored.total_victories == stats.total_victories
        assert restored.winrate == stats.winrate
        assert restored.highest_score == stats.highest_score


class TestTimerStats:
    """Test suite for TimerStats model."""
    
    def test_initial_state(self) -> None:
        """Test initial state of TimerStats."""
        stats = TimerStats()
        
        assert stats.games_with_timer == 0
        assert stats.victories_within_time == 0
        assert stats.victories_overtime == 0
        assert stats.defeats_timeout == 0
    
    def test_skip_non_timer_games(self) -> None:
        """Test that non-timer games are skipped."""
        stats = TimerStats()
        session = SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=100.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False
        )
        
        stats.update_from_session(session)
        
        assert stats.games_with_timer == 0
    
    def test_victory_within_time(self) -> None:
        """Test tracking victory within time limit."""
        stats = TimerStats()
        session = SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=250.0,
            timer_enabled=True,
            timer_limit=300,
            timer_mode="STRICT",
            timer_expired=False
        )
        
        stats.update_from_session(session)
        
        assert stats.games_with_timer == 1
        assert stats.victories_within_time == 1
        assert stats.victories_overtime == 0
    
    def test_victory_overtime(self) -> None:
        """Test tracking victory with overtime."""
        stats = TimerStats()
        session = SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.VICTORY_OVERTIME,
            is_victory=True,
            elapsed_time=420.0,
            timer_enabled=True,
            timer_limit=300,
            timer_mode="PERMISSIVE",
            timer_expired=True,
            overtime_duration=120.0
        )
        
        stats.update_from_session(session)
        
        assert stats.games_with_timer == 1
        assert stats.victories_overtime == 1
        assert stats.total_overtime == 120.0
        assert stats.max_overtime == 120.0
        assert stats.average_overtime == 120.0
    
    def test_timeout_defeat(self) -> None:
        """Test tracking timeout defeat."""
        stats = TimerStats()
        session = SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.TIMEOUT_STRICT,
            is_victory=False,
            elapsed_time=300.0,
            timer_enabled=True,
            timer_limit=300,
            timer_mode="STRICT",
            timer_expired=True
        )
        
        stats.update_from_session(session)
        
        assert stats.games_with_timer == 1
        assert stats.defeats_timeout == 1
    
    def test_overtime_averaging(self) -> None:
        """Test overtime average calculation."""
        stats = TimerStats()
        
        # First overtime victory
        stats.update_from_session(SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.VICTORY_OVERTIME,
            is_victory=True,
            elapsed_time=420.0,
            timer_enabled=True,
            timer_limit=300,
            timer_mode="PERMISSIVE",
            timer_expired=True,
            overtime_duration=120.0
        ))
        
        # Second overtime victory
        stats.update_from_session(SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.VICTORY_OVERTIME,
            is_victory=True,
            elapsed_time=380.0,
            timer_enabled=True,
            timer_limit=300,
            timer_mode="PERMISSIVE",
            timer_expired=True,
            overtime_duration=80.0
        ))
        
        assert stats.victories_overtime == 2
        assert stats.total_overtime == 200.0
        assert stats.average_overtime == 100.0
        assert stats.max_overtime == 120.0
    
    def test_serialization(self) -> None:
        """Test to_dict and from_dict roundtrip."""
        stats = TimerStats()
        stats.update_from_session(SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.VICTORY_OVERTIME,
            is_victory=True,
            elapsed_time=420.0,
            timer_enabled=True,
            timer_limit=300,
            timer_mode="PERMISSIVE",
            timer_expired=True,
            overtime_duration=120.0
        ))
        
        data = stats.to_dict()
        restored = TimerStats.from_dict(data)
        
        assert restored.games_with_timer == stats.games_with_timer
        assert restored.victories_overtime == stats.victories_overtime
        assert restored.total_overtime == stats.total_overtime


class TestDifficultyStats:
    """Test suite for DifficultyStats model."""
    
    def test_initial_state(self) -> None:
        """Test initial state of DifficultyStats."""
        stats = DifficultyStats()
        
        assert len(stats.games_by_level) == 0
        assert len(stats.victories_by_level) == 0
    
    def test_first_game_at_level(self) -> None:
        """Test tracking first game at a difficulty level."""
        stats = DifficultyStats()
        session = SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=100.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False,
            difficulty_level=3
        )
        
        stats.update_from_session(session)
        
        assert stats.games_by_level[3] == 1
        assert stats.victories_by_level[3] == 1
        assert stats.winrate_by_level[3] == 1.0
    
    def test_multiple_levels(self) -> None:
        """Test tracking games at multiple difficulty levels."""
        stats = DifficultyStats()
        
        # Easy victory
        stats.update_from_session(SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=100.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False,
            difficulty_level=1
        ))
        
        # Hard defeat
        stats.update_from_session(SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.ABANDON_EXIT,
            is_victory=False,
            elapsed_time=50.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False,
            difficulty_level=5
        ))
        
        assert stats.games_by_level[1] == 1
        assert stats.victories_by_level[1] == 1
        assert stats.winrate_by_level[1] == 1.0
        
        assert stats.games_by_level[5] == 1
        assert stats.victories_by_level[5] == 0
        assert stats.winrate_by_level[5] == 0.0
    
    def test_winrate_calculation_per_level(self) -> None:
        """Test winrate calculation per difficulty level."""
        stats = DifficultyStats()
        
        # 2 victories at level 3
        for _ in range(2):
            stats.update_from_session(SessionOutcome.create_new(
                profile_id="test",
                end_reason=EndReason.VICTORY,
                is_victory=True,
                elapsed_time=100.0,
                timer_enabled=False,
                timer_limit=0,
                timer_mode="OFF",
                timer_expired=False,
                difficulty_level=3
            ))
        
        # 1 defeat at level 3
        stats.update_from_session(SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.ABANDON_EXIT,
            is_victory=False,
            elapsed_time=50.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False,
            difficulty_level=3
        ))
        
        assert stats.games_by_level[3] == 3
        assert stats.victories_by_level[3] == 2
        assert stats.winrate_by_level[3] == pytest.approx(0.6667, rel=0.01)
    
    def test_average_score_tracking(self) -> None:
        """Test average score calculation per level."""
        stats = DifficultyStats()
        
        # First game with scoring
        stats.update_from_session(SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=100.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False,
            difficulty_level=3,
            scoring_enabled=True,
            final_score=1000
        ))
        
        assert stats.average_score_by_level[3] == 1000.0
        
        # Second game with scoring
        stats.update_from_session(SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=100.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False,
            difficulty_level=3,
            scoring_enabled=True,
            final_score=1200
        ))
        
        assert stats.average_score_by_level[3] == 1100.0
    
    def test_serialization(self) -> None:
        """Test to_dict and from_dict roundtrip."""
        stats = DifficultyStats()
        stats.update_from_session(SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=100.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False,
            difficulty_level=3,
            scoring_enabled=True,
            final_score=1500
        ))
        
        data = stats.to_dict()
        restored = DifficultyStats.from_dict(data)
        
        assert restored.games_by_level[3] == stats.games_by_level[3]
        assert restored.victories_by_level[3] == stats.victories_by_level[3]
        assert restored.winrate_by_level[3] == stats.winrate_by_level[3]


class TestScoringStats:
    """Test suite for ScoringStats model."""
    
    def test_initial_state(self) -> None:
        """Test initial state of ScoringStats."""
        stats = ScoringStats()
        
        assert stats.games_with_scoring == 0
        assert stats.total_score == 0
        assert stats.average_score == 0.0
    
    def test_skip_non_scoring_games(self) -> None:
        """Test that non-scoring games are skipped."""
        stats = ScoringStats()
        session = SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=100.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False,
            scoring_enabled=False
        )
        
        stats.update_from_session(session)
        
        assert stats.games_with_scoring == 0
    
    def test_score_tracking(self) -> None:
        """Test score tracking for scoring-enabled games."""
        stats = ScoringStats()
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
            final_score=1500
        )
        
        stats.update_from_session(session)
        
        assert stats.games_with_scoring == 1
        assert stats.total_score == 1500
        assert stats.average_score == 1500.0
        assert stats.highest_score == 1500
        assert stats.lowest_score == 1500
    
    def test_quality_classification_perfect(self) -> None:
        """Test quality classification for perfect games."""
        stats = ScoringStats()
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
            final_score=2000,
            quality_multiplier=1.9
        )
        
        stats.update_from_session(session)
        
        assert stats.perfect_games == 1
        assert stats.good_games == 0
        assert stats.average_games == 0
    
    def test_quality_classification_good(self) -> None:
        """Test quality classification for good games."""
        stats = ScoringStats()
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
            final_score=1500,
            quality_multiplier=1.5
        )
        
        stats.update_from_session(session)
        
        assert stats.perfect_games == 0
        assert stats.good_games == 1
        assert stats.average_games == 0
    
    def test_quality_classification_average(self) -> None:
        """Test quality classification for average games."""
        stats = ScoringStats()
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
            final_score=1000,
            quality_multiplier=1.2
        )
        
        stats.update_from_session(session)
        
        assert stats.perfect_games == 0
        assert stats.good_games == 0
        assert stats.average_games == 1
    
    def test_average_score_calculation(self) -> None:
        """Test average score calculation."""
        stats = ScoringStats()
        
        stats.update_from_session(SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=100.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False,
            scoring_enabled=True,
            final_score=1000
        ))
        
        stats.update_from_session(SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=100.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False,
            scoring_enabled=True,
            final_score=1200
        ))
        
        assert stats.games_with_scoring == 2
        assert stats.total_score == 2200
        assert stats.average_score == 1100.0
    
    def test_serialization(self) -> None:
        """Test to_dict and from_dict roundtrip."""
        stats = ScoringStats()
        stats.update_from_session(SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=100.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False,
            scoring_enabled=True,
            final_score=1500,
            quality_multiplier=1.9
        ))
        
        data = stats.to_dict()
        restored = ScoringStats.from_dict(data)
        
        assert restored.games_with_scoring == stats.games_with_scoring
        assert restored.total_score == stats.total_score
        assert restored.average_score == stats.average_score
        assert restored.perfect_games == stats.perfect_games
