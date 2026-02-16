"""Unit tests for ScoringService domain service.

Tests all scoring logic including:
- Event recording and point calculation
- Recycle penalty logic (free for first 3)
- Provisional score calculation
- Final score calculation with time bonus
- Time bonus formulas (timer ON/OFF)
- Query methods
- State management
"""

import pytest
import math

from src.domain.models.scoring import (
    ScoreEventType,
    ScoringConfig,
    ProvisionalScore,
    FinalScore,
)
from src.domain.services.scoring_service import ScoringService


@pytest.fixture
def config():
    """Standard scoring configuration."""
    return ScoringConfig()


@pytest.fixture
def service_level1_neapolitan_timer_off(config):
    """Service with easiest settings, timer OFF."""
    return ScoringService(
        config=config,
        difficulty_level=1,
        deck_type="neapolitan",
        draw_count=1,
        timer_enabled=False,
        timer_limit_seconds=-1
    )


@pytest.fixture
def service_level4_french_timer_on(config):
    """Service with level 4, French deck, 30min timer."""
    return ScoringService(
        config=config,
        difficulty_level=4,
        deck_type="french",
        draw_count=2,
        timer_enabled=True,
        timer_limit_seconds=1800  # 30 minutes
    )


class TestEventRecording:
    """Tests for event recording and point calculation."""
    
    def test_record_waste_to_foundation(self, service_level1_neapolitan_timer_off):
        """Test recording waste→foundation awards 10 points."""
        event = service_level1_neapolitan_timer_off.record_event(
            ScoreEventType.WASTE_TO_FOUNDATION,
            "Asso di Cuori"
        )
        
        assert event.event_type == ScoreEventType.WASTE_TO_FOUNDATION
        assert event.points == 10
        assert event.context == "Asso di Cuori"
        assert service_level1_neapolitan_timer_off.get_event_count() == 1
    
    def test_record_tableau_to_foundation(self, service_level1_neapolitan_timer_off):
        """Test recording tableau→foundation awards 10 points."""
        event = service_level1_neapolitan_timer_off.record_event(
            ScoreEventType.TABLEAU_TO_FOUNDATION,
            "Re di Spade"
        )
        
        assert event.points == 10
        assert service_level1_neapolitan_timer_off.get_base_score() == 10
    
    def test_record_card_revealed(self, service_level1_neapolitan_timer_off):
        """Test recording card reveal awards 5 points."""
        event = service_level1_neapolitan_timer_off.record_event(
            ScoreEventType.CARD_REVEALED
        )
        
        assert event.points == 5
    
    def test_record_foundation_to_tableau(self, service_level1_neapolitan_timer_off):
        """Test recording foundation→tableau deducts 15 points."""
        event = service_level1_neapolitan_timer_off.record_event(
            ScoreEventType.FOUNDATION_TO_TABLEAU
        )
        
        assert event.points == -15
    
    def test_multiple_events_accumulate(self, service_level1_neapolitan_timer_off):
        """Test multiple events accumulate correctly."""
        service = service_level1_neapolitan_timer_off
        
        service.record_event(ScoreEventType.WASTE_TO_FOUNDATION)  # +10
        service.record_event(ScoreEventType.CARD_REVEALED)        # +5
        service.record_event(ScoreEventType.TABLEAU_TO_FOUNDATION)  # +10
        service.record_event(ScoreEventType.FOUNDATION_TO_TABLEAU)  # -15
        
        assert service.get_base_score() == 10  # 10 + 5 + 10 - 15
        assert service.get_event_count() == 4


class TestRecyclePenalty:
    """Tests for recycle penalty logic."""
    
    def test_first_recycle_is_free(self, service_level1_neapolitan_timer_off):
        """Test first recycle awards 0 points (no penalty)."""
        event = service_level1_neapolitan_timer_off.record_event(
            ScoreEventType.RECYCLE_WASTE
        )
        
        assert event.points == 0
        assert service_level1_neapolitan_timer_off.recycle_count == 1
    
    def test_second_recycle_is_free(self, service_level1_neapolitan_timer_off):
        """Test second recycle awards 0 points (no penalty)."""
        service = service_level1_neapolitan_timer_off
        
        service.record_event(ScoreEventType.RECYCLE_WASTE)  # 1st: free
        event = service.record_event(ScoreEventType.RECYCLE_WASTE)  # 2nd: free
        
        assert event.points == 0
        assert service.recycle_count == 2
    
    def test_third_recycle_is_free(self, service_level1_neapolitan_timer_off):
        """Test third recycle awards 0 points (no penalty)."""
        service = service_level1_neapolitan_timer_off
        
        service.record_event(ScoreEventType.RECYCLE_WASTE)  # 1st
        service.record_event(ScoreEventType.RECYCLE_WASTE)  # 2nd
        event = service.record_event(ScoreEventType.RECYCLE_WASTE)  # 3rd
        
        assert event.points == 0
        assert service.recycle_count == 3
        assert service.get_base_score() == 0
    
    def test_fourth_recycle_penalty(self, service_level1_neapolitan_timer_off):
        """Test fourth recycle deducts penalty (v2.0: -20 points)."""
        service = service_level1_neapolitan_timer_off
        
        service.record_event(ScoreEventType.RECYCLE_WASTE)  # 1st: free
        service.record_event(ScoreEventType.RECYCLE_WASTE)  # 2nd: free
        service.record_event(ScoreEventType.RECYCLE_WASTE)  # 3rd: -10
        event = service.record_event(ScoreEventType.RECYCLE_WASTE)  # 4th: -20
        
        assert event.points == -20
        assert service.recycle_count == 4
        assert service.get_base_score() == -30  # 0 + 0 + (-10) + (-20)
    
    def test_recycle_penalty_guard_zero(self, service_level1_neapolitan_timer_off):
        """Test v2.0 CRITICAL: recycle penalty guard against count <= 0."""
        service = service_level1_neapolitan_timer_off
        
        # Direct call with invalid count (shouldn't happen in practice)
        penalty_zero = service._calculate_recycle_penalty(0)
        penalty_negative = service._calculate_recycle_penalty(-1)
        
        assert penalty_zero == 0
        assert penalty_negative == 0
    
    def test_recycle_penalties_v2_progressive(self, service_level1_neapolitan_timer_off):
        """Test v2.0 progressive recycle penalties: 0, 0, -10, -20, -35, -55, -80."""
        service = service_level1_neapolitan_timer_off
        expected_penalties = [0, 0, -10, -20, -35, -55, -80]
        
        for i, expected_penalty in enumerate(expected_penalties, start=1):
            event = service.record_event(ScoreEventType.RECYCLE_WASTE)
            assert event.points == expected_penalty, f"Recycle {i} should be {expected_penalty}, got {event.points}"
        
        # 8th and beyond should clamp to -80
        event8 = service.record_event(ScoreEventType.RECYCLE_WASTE)
        assert event8.points == -80


class TestStockDrawPenalty:
    """Tests for v2.0 STOCK_DRAW progressive penalty."""
    
    def test_stock_draw_first_20_free(self, service_level1_neapolitan_timer_off):
        """Test first 20 stock draws are free (0 points)."""
        service = service_level1_neapolitan_timer_off
        
        for i in range(20):
            event = service.record_event(ScoreEventType.STOCK_DRAW)
            assert event.points == 0, f"Draw {i+1} should be 0, got {event.points}"
        
        assert service.stock_draw_count == 20
        assert service.get_base_score() == 0
    
    def test_stock_draw_boundary_20_last_free(self, service_level1_neapolitan_timer_off):
        """Test v2.0 CRITICAL: draw 20 is last free draw (boundary)."""
        service = service_level1_neapolitan_timer_off
        
        # Draw exactly 20 times
        for _ in range(20):
            service.record_event(ScoreEventType.STOCK_DRAW)
        
        # 20th draw should be free
        assert service.stock_draw_count == 20
        assert service.get_base_score() == 0
    
    def test_stock_draw_boundary_21_first_penalty(self, service_level1_neapolitan_timer_off):
        """Test v2.0 CRITICAL: draw 21 is first penalty (boundary)."""
        service = service_level1_neapolitan_timer_off
        
        # Draw 20 times (free)
        for _ in range(20):
            service.record_event(ScoreEventType.STOCK_DRAW)
        
        # 21st draw should be -1pt
        event21 = service.record_event(ScoreEventType.STOCK_DRAW)
        assert event21.points == -1
        assert service.stock_draw_count == 21
    
    def test_stock_draw_tier_21_40_penalty(self, service_level1_neapolitan_timer_off):
        """Test draws 21-40 have -1pt penalty each."""
        service = service_level1_neapolitan_timer_off
        
        # Draw 20 times (free)
        for _ in range(20):
            service.record_event(ScoreEventType.STOCK_DRAW)
        
        # Draws 21-40 should be -1pt each
        for i in range(21, 41):
            event = service.record_event(ScoreEventType.STOCK_DRAW)
            assert event.points == -1, f"Draw {i} should be -1, got {event.points}"
        
        assert service.stock_draw_count == 40
        assert service.get_base_score() == -20  # 20 draws at -1pt each
    
    def test_stock_draw_boundary_40_last_minus_one(self, service_level1_neapolitan_timer_off):
        """Test v2.0 CRITICAL: draw 40 is last -1pt tier (boundary)."""
        service = service_level1_neapolitan_timer_off
        
        # Draw 40 times
        for _ in range(40):
            service.record_event(ScoreEventType.STOCK_DRAW)
        
        # 40th draw should be -1pt
        assert service.stock_draw_count == 40
        # Score: 0 (first 20) + (-20) (draws 21-40)
        assert service.get_base_score() == -20
    
    def test_stock_draw_boundary_41_first_minus_two(self, service_level1_neapolitan_timer_off):
        """Test v2.0 CRITICAL: draw 41 is first -2pt tier (boundary)."""
        service = service_level1_neapolitan_timer_off
        
        # Draw 40 times
        for _ in range(40):
            service.record_event(ScoreEventType.STOCK_DRAW)
        
        # 41st draw should be -2pt
        event41 = service.record_event(ScoreEventType.STOCK_DRAW)
        assert event41.points == -2
        assert service.stock_draw_count == 41
    
    def test_stock_draw_tier_41_plus_penalty(self, service_level1_neapolitan_timer_off):
        """Test draws 41+ have -2pt penalty each."""
        service = service_level1_neapolitan_timer_off
        
        # Draw 40 times
        for _ in range(40):
            service.record_event(ScoreEventType.STOCK_DRAW)
        
        # Draws 41-50 should be -2pt each
        for i in range(41, 51):
            event = service.record_event(ScoreEventType.STOCK_DRAW)
            assert event.points == -2, f"Draw {i} should be -2, got {event.points}"
        
        assert service.stock_draw_count == 50
        # Score: 0 (first 20) + (-20) (21-40) + (-20) (41-50)
        assert service.get_base_score() == -40
    
    def test_stock_draw_examples_from_spec(self, service_level1_neapolitan_timer_off):
        """Test examples from v2.0 specification."""
        service = service_level1_neapolitan_timer_off
        
        # Example 1: 15 draws → 0pt total
        service_15 = ScoringService(
            config=service.config,
            difficulty_level=1,
            deck_type="neapolitan",
            draw_count=1
        )
        for _ in range(15):
            service_15.record_event(ScoreEventType.STOCK_DRAW)
        assert service_15.get_base_score() == 0
        
        # Example 2: 35 draws → -15pt total
        service_35 = ScoringService(
            config=service.config,
            difficulty_level=1,
            deck_type="neapolitan",
            draw_count=1
        )
        for _ in range(35):
            service_35.record_event(ScoreEventType.STOCK_DRAW)
        # 0 (first 20) + (-15) (draws 21-35 at -1pt each)
        assert service_35.get_base_score() == -15
        
        # Example 3: 60 draws → -55pt total
        service_60 = ScoringService(
            config=service.config,
            difficulty_level=1,
            deck_type="neapolitan",
            draw_count=1
        )
        for _ in range(60):
            service_60.record_event(ScoreEventType.STOCK_DRAW)
        # 0 (first 20) + (-20) (draws 21-40) + (-40) (draws 41-60 at -2pt each)
        assert service_60.get_base_score() == -55
        service.record_event(ScoreEventType.RECYCLE_WASTE)  # 3rd: free
        event = service.record_event(ScoreEventType.RECYCLE_WASTE)  # 4th: penalty
        
        assert event.points == -20
        assert service.recycle_count == 4
        assert service.get_base_score() == -20
    
    def test_fifth_recycle_penalty(self, service_level1_neapolitan_timer_off):
        """Test fifth and subsequent recycles deduct 20 points each."""
        service = service_level1_neapolitan_timer_off
        
        for _ in range(5):
            service.record_event(ScoreEventType.RECYCLE_WASTE)
        
        # First 3 free, then 2 penalties (-40 total)
        assert service.get_base_score() == -40
        assert service.recycle_count == 5


class TestProvisionalScore:
    """Tests for provisional score calculation."""
    
    def test_provisional_score_level1_neapolitan(self, service_level1_neapolitan_timer_off):
        """Test provisional score with level 1, Neapolitan deck, draw 1."""
        service = service_level1_neapolitan_timer_off
        
        service.record_event(ScoreEventType.WASTE_TO_FOUNDATION)  # +10
        service.record_event(ScoreEventType.CARD_REVEALED)        # +5
        
        provisional = service.calculate_provisional_score()
        
        # base=15, deck_bonus=0, draw_bonus=0, multiplier=1.0
        assert provisional.base_score == 15
        assert provisional.deck_bonus == 0
        assert provisional.draw_bonus == 0
        assert provisional.difficulty_multiplier == 1.0
        assert provisional.total_score == 15
    
    def test_provisional_score_level4_french_draw2(self, service_level4_french_timer_on):
        """Test provisional score with level 4, French deck, draw 2."""
        service = service_level4_french_timer_on
        
        service.record_event(ScoreEventType.WASTE_TO_FOUNDATION)  # +10
        
        provisional = service.calculate_provisional_score()
        
        # base=10, deck_bonus=150, draw_bonus=0 (level 4), multiplier=2.0
        # (10 + 150 + 0) * 2.0 = 320
        assert provisional.base_score == 10
        assert provisional.deck_bonus == 150
        assert provisional.draw_bonus == 0  # No draw bonus at level 4
        assert provisional.difficulty_multiplier == 2.0
        assert provisional.total_score == 320
    
    def test_provisional_score_with_draw_bonus(self, config):
        """Test provisional score includes draw bonus for levels 1-3."""
        service = ScoringService(
            config=config,
            difficulty_level=2,
            deck_type="french",
            draw_count=3,
            timer_enabled=False
        )
        
        service.record_event(ScoreEventType.WASTE_TO_FOUNDATION)  # +10
        
        provisional = service.calculate_provisional_score()
        
        # base=10, deck_bonus=150, draw_bonus=200 (draw 3), multiplier=1.25
        # (10 + 150 + 200) * 1.25 = 450
        assert provisional.base_score == 10
        assert provisional.deck_bonus == 150
        assert provisional.draw_bonus == 200
        assert provisional.difficulty_multiplier == 1.25
        assert provisional.total_score == 450
    
    def test_provisional_score_negative_clamped(self, service_level1_neapolitan_timer_off):
        """Test provisional score never goes below 0."""
        service = service_level1_neapolitan_timer_off
        
        # Create large negative base score
        for _ in range(10):
            service.record_event(ScoreEventType.FOUNDATION_TO_TABLEAU)  # -15 each
        
        provisional = service.calculate_provisional_score()
        
        # Base would be -150, but should clamp to 0
        assert provisional.total_score >= 0


class TestFinalScore:
    """Tests for final score calculation."""
    
    def test_final_score_victory(self, service_level1_neapolitan_timer_off):
        """Test final score includes victory bonus when won."""
        service = service_level1_neapolitan_timer_off
        
        service.record_event(ScoreEventType.WASTE_TO_FOUNDATION)  # +10
        
        final = service.calculate_final_score(
            elapsed_seconds=120.0,
            move_count=25,
            is_victory=True
        )
        
        assert final.base_score == 10
        assert final.victory_bonus == 500
        assert final.is_victory is True
        assert final.total_score > 10  # Has time bonus + victory bonus
    
    def test_final_score_no_victory(self, service_level1_neapolitan_timer_off):
        """Test final score excludes victory bonus when lost."""
        service = service_level1_neapolitan_timer_off
        
        service.record_event(ScoreEventType.WASTE_TO_FOUNDATION)  # +10
        
        final = service.calculate_final_score(
            elapsed_seconds=120.0,
            move_count=25,
            is_victory=False
        )
        
        assert final.victory_bonus == 0
        assert final.is_victory is False
    
    def test_final_score_metadata(self, service_level4_french_timer_on):
        """Test final score includes all metadata."""
        service = service_level4_french_timer_on
        
        service.record_event(ScoreEventType.WASTE_TO_FOUNDATION)
        service.record_event(ScoreEventType.RECYCLE_WASTE)
        service.record_event(ScoreEventType.RECYCLE_WASTE)
        
        final = service.calculate_final_score(
            elapsed_seconds=900.0,  # 15 minutes
            move_count=42,
            is_victory=True
        )
        
        assert final.elapsed_seconds == 900.0
        assert final.move_count == 42
        assert final.difficulty_level == 4
        assert final.deck_type == "french"
        assert final.draw_count == 2
        assert final.recycle_count == 2


class TestTimeBonusTimerOff:
    """Tests for time bonus calculation with timer OFF."""
    
    def test_time_bonus_fast_completion(self, service_level1_neapolitan_timer_off):
        """Test time bonus for fast completion (high bonus)."""
        service = service_level1_neapolitan_timer_off
        
        # 100 seconds: 10000/sqrt(100) = 10000/10 = 1000
        bonus = service._calculate_time_bonus(100.0)
        assert bonus == 1000
    
    def test_time_bonus_medium_completion(self, service_level1_neapolitan_timer_off):
        """Test time bonus for medium completion."""
        service = service_level1_neapolitan_timer_off
        
        # 400 seconds: 10000/sqrt(400) = 10000/20 = 500
        bonus = service._calculate_time_bonus(400.0)
        assert bonus == 500
    
    def test_time_bonus_slow_completion(self, service_level1_neapolitan_timer_off):
        """Test time bonus for slow completion (low bonus)."""
        service = service_level1_neapolitan_timer_off
        
        # 10000 seconds: 10000/sqrt(10000) = 10000/100 = 100
        bonus = service._calculate_time_bonus(10000.0)
        assert bonus == 100
    
    def test_time_bonus_capped_at_2000(self, service_level1_neapolitan_timer_off):
        """Test time bonus is capped at 2000."""
        service = service_level1_neapolitan_timer_off
        
        # Very fast: 25 seconds: 10000/sqrt(25) = 10000/5 = 2000
        bonus = service._calculate_time_bonus(25.0)
        assert bonus == 2000
        
        # Even faster: would be higher but capped
        bonus = service._calculate_time_bonus(10.0)
        assert bonus == 2000
    
    def test_time_bonus_instant_win(self, service_level1_neapolitan_timer_off):
        """Test time bonus for instant win (0 seconds)."""
        service = service_level1_neapolitan_timer_off
        
        bonus = service._calculate_time_bonus(0.0)
        assert bonus == 2000  # Maximum bonus


class TestTimeBonusTimerOn:
    """Tests for time bonus calculation with timer ON."""
    
    def test_time_bonus_50_percent_remaining(self, service_level4_french_timer_on):
        """Test time bonus when ≥50% time remaining (+1000)."""
        service = service_level4_french_timer_on
        
        # Used 900 seconds of 1800 (50% remaining)
        bonus = service._calculate_time_bonus(900.0)
        assert bonus == 1000
    
    def test_time_bonus_60_percent_remaining(self, service_level4_french_timer_on):
        """Test time bonus when 60% time remaining (+1000)."""
        service = service_level4_french_timer_on
        
        # Used 720 seconds of 1800 (60% remaining)
        bonus = service._calculate_time_bonus(720.0)
        assert bonus == 1000
    
    def test_time_bonus_25_percent_remaining(self, service_level4_french_timer_on):
        """Test time bonus when ≥25% time remaining (+500)."""
        service = service_level4_french_timer_on
        
        # Used 1350 seconds of 1800 (25% remaining)
        bonus = service._calculate_time_bonus(1350.0)
        assert bonus == 500
    
    def test_time_bonus_10_percent_remaining(self, service_level4_french_timer_on):
        """Test time bonus when 10% time remaining (+200)."""
        service = service_level4_french_timer_on
        
        # Used 1620 seconds of 1800 (10% remaining)
        bonus = service._calculate_time_bonus(1620.0)
        assert bonus == 200
    
    def test_time_bonus_1_second_remaining(self, service_level4_french_timer_on):
        """Test time bonus when 1 second remaining (+200)."""
        service = service_level4_french_timer_on
        
        # Used 1799 seconds of 1800
        bonus = service._calculate_time_bonus(1799.0)
        assert bonus == 200
    
    def test_time_bonus_expired(self, service_level4_french_timer_on):
        """Test time bonus when timer expired (-500)."""
        service = service_level4_french_timer_on
        
        # Used 1900 seconds of 1800 (expired)
        bonus = service._calculate_time_bonus(1900.0)
        assert bonus == -500


class TestQueries:
    """Tests for query methods."""
    
    def test_get_event_count(self, service_level1_neapolitan_timer_off):
        """Test get_event_count returns correct count."""
        service = service_level1_neapolitan_timer_off
        
        assert service.get_event_count() == 0
        
        service.record_event(ScoreEventType.WASTE_TO_FOUNDATION)
        assert service.get_event_count() == 1
        
        service.record_event(ScoreEventType.CARD_REVEALED)
        assert service.get_event_count() == 2
    
    def test_get_recent_events_default(self, service_level1_neapolitan_timer_off):
        """Test get_recent_events returns last 5 events by default."""
        service = service_level1_neapolitan_timer_off
        
        # Record 7 events
        for i in range(7):
            service.record_event(ScoreEventType.WASTE_TO_FOUNDATION, f"Event {i}")
        
        recent = service.get_recent_events()
        
        assert len(recent) == 5
        # Should be in reverse order (newest first)
        assert recent[0].context == "Event 6"
        assert recent[4].context == "Event 2"
    
    def test_get_recent_events_custom_count(self, service_level1_neapolitan_timer_off):
        """Test get_recent_events with custom count."""
        service = service_level1_neapolitan_timer_off
        
        # Record 10 events
        for i in range(10):
            service.record_event(ScoreEventType.CARD_REVEALED, f"Event {i}")
        
        recent = service.get_recent_events(3)
        
        assert len(recent) == 3
        assert recent[0].context == "Event 9"
        assert recent[2].context == "Event 7"
    
    def test_get_recent_events_fewer_than_requested(self, service_level1_neapolitan_timer_off):
        """Test get_recent_events when fewer events exist."""
        service = service_level1_neapolitan_timer_off
        
        service.record_event(ScoreEventType.WASTE_TO_FOUNDATION)
        service.record_event(ScoreEventType.CARD_REVEALED)
        
        recent = service.get_recent_events(5)
        
        assert len(recent) == 2  # Only 2 events exist


class TestStateManagement:
    """Tests for state management methods."""
    
    def test_reset_clears_events(self, service_level1_neapolitan_timer_off):
        """Test reset clears all events."""
        service = service_level1_neapolitan_timer_off
        
        service.record_event(ScoreEventType.WASTE_TO_FOUNDATION)
        service.record_event(ScoreEventType.CARD_REVEALED)
        
        assert service.get_event_count() == 2
        
        service.reset()
        
        assert service.get_event_count() == 0
        assert service.get_base_score() == 0
    
    def test_reset_clears_recycle_count(self, service_level1_neapolitan_timer_off):
        """Test reset clears recycle count."""
        service = service_level1_neapolitan_timer_off
        
        service.record_event(ScoreEventType.RECYCLE_WASTE)
        service.record_event(ScoreEventType.RECYCLE_WASTE)
        
        assert service.recycle_count == 2
        
        service.reset()
        
        assert service.recycle_count == 0
    
    def test_reset_preserves_configuration(self, service_level4_french_timer_on):
        """Test reset does not change configuration."""
        service = service_level4_french_timer_on
        
        service.record_event(ScoreEventType.WASTE_TO_FOUNDATION)
        service.reset()
        
        # Configuration should remain unchanged
        assert service.difficulty_level == 4
        assert service.deck_type == "french"
        assert service.draw_count == 2
        assert service.timer_enabled is True
        assert service.timer_limit_seconds == 1800
