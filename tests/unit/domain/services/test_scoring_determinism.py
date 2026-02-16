"""Unit tests for scoring system determinism (v2.0).

Tests verify:
- Commutativity: Event order doesn't affect final score
- Truncation bias: Rounding errors bounded to acceptable range

CRITICAL tests for mathematical correctness.
"""

import pytest
import random

from src.domain.models.scoring import ScoreEventType, ScoringConfig
from src.domain.services.scoring_service import ScoringService


@pytest.fixture
def config():
    """Standard scoring configuration."""
    return ScoringConfig()


class TestScoringDeterminism:
    """CRITICAL: Tests for deterministic scoring behavior."""
    
    def test_scoring_commutativity_CRITICAL(self, config):
        """CRITICAL: Test that event order doesn't affect final score (commutativity).
        
        Shuffles events 10 times and verifies final score remains identical.
        This ensures order-independent scoring as specified in v2.0.
        """
        # Define a set of events
        events = [
            (ScoreEventType.WASTE_TO_FOUNDATION, None),
            (ScoreEventType.WASTE_TO_FOUNDATION, None),
            (ScoreEventType.TABLEAU_TO_FOUNDATION, None),
            (ScoreEventType.TABLEAU_TO_FOUNDATION, None),
            (ScoreEventType.CARD_REVEALED, None),
            (ScoreEventType.CARD_REVEALED, None),
            (ScoreEventType.CARD_REVEALED, None),
            (ScoreEventType.FOUNDATION_TO_TABLEAU, None),
            (ScoreEventType.RECYCLE_WASTE, None),
            (ScoreEventType.RECYCLE_WASTE, None),
        ]
        
        # Calculate score with original order
        service_original = ScoringService(
            config=config,
            difficulty_level=3,
            deck_type="french",
            draw_count=2,
            timer_enabled=False
        )
        
        for event_type, context in events:
            service_original.record_event(event_type, context)
        
        original_score = service_original.calculate_final_score(
            elapsed_seconds=20 * 60,
            move_count=150,
            is_victory=True
        )
        
        # Shuffle and test 10 times
        for shuffle_num in range(10):
            shuffled_events = events.copy()
            random.shuffle(shuffled_events)
            
            service_shuffled = ScoringService(
                config=config,
                difficulty_level=3,
                deck_type="french",
                draw_count=2,
                timer_enabled=False
            )
            
            for event_type, context in shuffled_events:
                service_shuffled.record_event(event_type, context)
            
            shuffled_score = service_shuffled.calculate_final_score(
                elapsed_seconds=20 * 60,
                move_count=150,
                is_victory=True
            )
            
            # Scores must be identical (order-independent)
            assert shuffled_score.total_score == original_score.total_score, \
                f"Shuffle {shuffle_num}: Score mismatch! " \
                f"Original={original_score.total_score}, Shuffled={shuffled_score.total_score}"
            
            # All components should match too
            assert shuffled_score.base_score == original_score.base_score, \
                f"Base score mismatch on shuffle {shuffle_num}"
            assert shuffled_score.victory_bonus == original_score.victory_bonus, \
                f"Victory bonus mismatch on shuffle {shuffle_num}"
    
    def test_truncation_bias_bounded_CRITICAL(self, config):
        """CRITICAL: Test that truncation bias is bounded to acceptable range.
        
        Verifies that accumulated rounding errors don't exceed 3pt on typical 1500pt score.
        This ensures Rule 5 (_safe_truncate) prevents systematic bias.
        """
        # Create a scenario with typical score ~1500pt
        service = ScoringService(
            config=config,
            difficulty_level=4,  # 1.8x multiplier
            deck_type="french",
            draw_count=3,
            timer_enabled=False
        )
        
        # Record many events to get typical score
        for _ in range(20):
            service.record_event(ScoreEventType.WASTE_TO_FOUNDATION)  # +10 each
        for _ in range(10):
            service.record_event(ScoreEventType.CARD_REVEALED)  # +5 each
        for _ in range(5):
            service.record_event(ScoreEventType.STOCK_DRAW)  # First 20 free
        
        final_score = service.calculate_final_score(
            elapsed_seconds=18 * 60,  # 18 minutes
            move_count=120,
            is_victory=True
        )
        
        # Calculate theoretical score without truncation (float arithmetic)
        base = service.get_base_score()  # 20*10 + 10*5 = 250
        deck_bonus = 50  # french
        draw_bonus = 100  # draw 3 at level 4 (50% of 200)
        difficulty_mult = 1.8
        
        provisional_float = (base + deck_bonus + draw_bonus) * difficulty_mult
        # provisional_float = (250 + 50 + 100) * 1.8 = 720.0
        
        # Time bonus: max(0, 1200 - 18*40) = 1200 - 720 = 480
        time_bonus_expected = 480
        
        # Victory bonus: depends on quality factors
        # For these conditions: time_q=1.2 (18min), move_q=1.1 (120 moves), recycle_q=1.2 (0 recycles)
        # quality = 1.2*0.35 + 1.1*0.35 + 1.2*0.30 = 0.42 + 0.385 + 0.36 = 1.165
        # victory_bonus = 400 * 1.165 = 466
        
        # Total theoretical: 720 + 480 + 466 = 1666
        theoretical_total = provisional_float + time_bonus_expected + final_score.victory_bonus
        
        # Calculate bias (difference between actual and theoretical)
        bias = abs(final_score.total_score - theoretical_total)
        
        # Bias should be bounded to small value (<3pt on ~1500pt score)
        # This is <0.2% error, acceptable for integer truncation
        assert bias < 3, \
            f"Truncation bias {bias}pt exceeds acceptable bound 3pt " \
            f"(Actual={final_score.total_score}, Theoretical={theoretical_total})"
        
        # Verify score is in reasonable range
        assert 1400 <= final_score.total_score <= 1800, \
            f"Score {final_score.total_score} outside expected range [1400, 1800]"
    
    def test_same_input_same_output_determinism(self, config):
        """Test that identical inputs always produce identical outputs."""
        # Create two identical services
        service1 = ScoringService(
            config=config,
            difficulty_level=3,
            deck_type="neapolitan",
            draw_count=2,
            timer_enabled=False
        )
        
        service2 = ScoringService(
            config=config,
            difficulty_level=3,
            deck_type="neapolitan",
            draw_count=2,
            timer_enabled=False
        )
        
        # Record identical events
        for i in range(15):
            service1.record_event(ScoreEventType.WASTE_TO_FOUNDATION)
            service2.record_event(ScoreEventType.WASTE_TO_FOUNDATION)
        
        # Calculate identical final scores
        score1 = service1.calculate_final_score(
            elapsed_seconds=1122.7,  # Specific float value
            move_count=100,
            is_victory=True
        )
        
        score2 = service2.calculate_final_score(
            elapsed_seconds=1122.7,  # Same float value
            move_count=100,
            is_victory=True
        )
        
        # All fields must match exactly
        assert score1.total_score == score2.total_score
        assert score1.base_score == score2.base_score
        assert score1.time_bonus == score2.time_bonus
        assert score1.victory_bonus == score2.victory_bonus
        assert score1.victory_quality_multiplier == score2.victory_quality_multiplier
