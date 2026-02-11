"""Unit tests for scoring system domain models.

Tests all dataclasses for:
- Immutability (frozen=True)
- Default values
- Calculated fields
- String representations
- Type safety
"""

import pytest
from dataclasses import FrozenInstanceError
from datetime import datetime

from src.domain.models.scoring import (
    ScoreEventType,
    ScoringConfig,
    ScoreEvent,
    ProvisionalScore,
    FinalScore,
)


class TestScoreEventType:
    """Tests for ScoreEventType enum."""
    
    def test_enum_values_exist(self):
        """Test all required event types are defined."""
        assert ScoreEventType.WASTE_TO_FOUNDATION
        assert ScoreEventType.TABLEAU_TO_FOUNDATION
        assert ScoreEventType.CARD_REVEALED
        assert ScoreEventType.FOUNDATION_TO_TABLEAU
        assert ScoreEventType.RECYCLE_WASTE
        assert ScoreEventType.UNDO_MOVE
        assert ScoreEventType.HINT_USED
    
    def test_enum_values_are_strings(self):
        """Test enum values are string identifiers."""
        assert ScoreEventType.WASTE_TO_FOUNDATION.value == "waste_to_foundation"
        assert ScoreEventType.CARD_REVEALED.value == "card_revealed"
        assert ScoreEventType.RECYCLE_WASTE.value == "recycle_waste"


class TestScoringConfig:
    """Tests for ScoringConfig dataclass."""
    
    def test_default_event_points(self):
        """Test default event point values match specification."""
        config = ScoringConfig()
        
        assert config.event_points[ScoreEventType.WASTE_TO_FOUNDATION] == 10
        assert config.event_points[ScoreEventType.TABLEAU_TO_FOUNDATION] == 10
        assert config.event_points[ScoreEventType.CARD_REVEALED] == 5
        assert config.event_points[ScoreEventType.FOUNDATION_TO_TABLEAU] == -15
        assert config.event_points[ScoreEventType.RECYCLE_WASTE] == -20
        assert config.event_points[ScoreEventType.UNDO_MOVE] == 0
        assert config.event_points[ScoreEventType.HINT_USED] == 0
    
    def test_default_difficulty_multipliers(self):
        """Test difficulty multipliers scale from 1.0 to 2.5."""
        config = ScoringConfig()
        
        assert config.difficulty_multipliers[1] == 1.0
        assert config.difficulty_multipliers[2] == 1.25
        assert config.difficulty_multipliers[3] == 1.5
        assert config.difficulty_multipliers[4] == 2.0
        assert config.difficulty_multipliers[5] == 2.5
    
    def test_default_deck_type_bonuses(self):
        """Test French deck gets +150 bonus."""
        config = ScoringConfig()
        
        assert config.deck_type_bonuses["neapolitan"] == 0
        assert config.deck_type_bonuses["french"] == 150
    
    def test_default_draw_count_bonuses(self):
        """Test draw count bonuses scale with difficulty."""
        config = ScoringConfig()
        
        assert config.draw_count_bonuses[1] == 0
        assert config.draw_count_bonuses[2] == 100
        assert config.draw_count_bonuses[3] == 200
    
    def test_default_victory_bonus(self):
        """Test victory bonus is 500."""
        config = ScoringConfig()
        assert config.victory_bonus == 500
    
    def test_default_min_score(self):
        """Test minimum score is 0."""
        config = ScoringConfig()
        assert config.min_score == 0
    
    def test_config_is_frozen(self):
        """Test ScoringConfig is immutable."""
        config = ScoringConfig()
        
        with pytest.raises(FrozenInstanceError):
            config.victory_bonus = 1000  # type: ignore


class TestScoreEvent:
    """Tests for ScoreEvent dataclass."""
    
    def test_create_event_with_all_fields(self):
        """Test creating event with explicit values."""
        timestamp = datetime(2026, 2, 11, 10, 30, 0)
        event = ScoreEvent(
            event_type=ScoreEventType.WASTE_TO_FOUNDATION,
            points=10,
            timestamp=timestamp,
            context="7 di Cuori"
        )
        
        assert event.event_type == ScoreEventType.WASTE_TO_FOUNDATION
        assert event.points == 10
        assert event.timestamp == timestamp
        assert event.context == "7 di Cuori"
    
    def test_create_event_with_defaults(self):
        """Test creating event with default timestamp."""
        event = ScoreEvent(
            event_type=ScoreEventType.CARD_REVEALED,
            points=5
        )
        
        assert event.event_type == ScoreEventType.CARD_REVEALED
        assert event.points == 5
        assert isinstance(event.timestamp, datetime)
        assert event.context is None
    
    def test_event_is_frozen(self):
        """Test ScoreEvent is immutable."""
        event = ScoreEvent(
            event_type=ScoreEventType.WASTE_TO_FOUNDATION,
            points=10
        )
        
        with pytest.raises(FrozenInstanceError):
            event.points = 20  # type: ignore
    
    def test_event_str_positive_points(self):
        """Test string representation for positive points."""
        event = ScoreEvent(
            event_type=ScoreEventType.WASTE_TO_FOUNDATION,
            points=10,
            context="Asso di Cuori"
        )
        
        result = str(event)
        assert "waste_to_foundation" in result
        assert "+10 punti" in result
        assert "Asso di Cuori" in result
    
    def test_event_str_negative_points(self):
        """Test string representation for negative points."""
        event = ScoreEvent(
            event_type=ScoreEventType.FOUNDATION_TO_TABLEAU,
            points=-15
        )
        
        result = str(event)
        assert "foundation_to_tableau" in result
        assert "-15 punti" in result


class TestProvisionalScore:
    """Tests for ProvisionalScore dataclass."""
    
    def test_create_provisional_score(self):
        """Test creating provisional score with all fields."""
        score = ProvisionalScore(
            base_score=100,
            deck_bonus=150,
            draw_bonus=100,
            difficulty_multiplier=2.0
        )
        
        assert score.base_score == 100
        assert score.deck_bonus == 150
        assert score.draw_bonus == 100
        assert score.difficulty_multiplier == 2.0
    
    def test_total_before_multiplier_calculation(self):
        """Test total_before_multiplier is calculated correctly."""
        score = ProvisionalScore(
            base_score=100,
            deck_bonus=150,
            draw_bonus=100,
            difficulty_multiplier=2.0
        )
        
        # 100 + 150 + 100 = 350
        assert score.total_before_multiplier == 350
    
    def test_total_score_calculation(self):
        """Test total_score applies multiplier correctly."""
        score = ProvisionalScore(
            base_score=100,
            deck_bonus=150,
            draw_bonus=100,
            difficulty_multiplier=2.0
        )
        
        # (100 + 150 + 100) * 2.0 = 700
        assert score.total_score == 700
    
    def test_total_score_rounds_to_int(self):
        """Test total_score is rounded to integer."""
        score = ProvisionalScore(
            base_score=100,
            deck_bonus=0,
            draw_bonus=0,
            difficulty_multiplier=1.25
        )
        
        # 100 * 1.25 = 125 (exact)
        assert score.total_score == 125
        assert isinstance(score.total_score, int)
    
    def test_provisional_score_is_frozen(self):
        """Test ProvisionalScore is immutable."""
        score = ProvisionalScore(
            base_score=100,
            deck_bonus=150,
            draw_bonus=100,
            difficulty_multiplier=2.0
        )
        
        with pytest.raises(FrozenInstanceError):
            score.base_score = 200  # type: ignore


class TestFinalScore:
    """Tests for FinalScore dataclass."""
    
    def test_create_final_score(self):
        """Test creating final score with all fields."""
        score = FinalScore(
            base_score=100,
            deck_bonus=150,
            draw_bonus=100,
            difficulty_multiplier=2.0,
            time_bonus=345,
            victory_bonus=500,
            total_score=1045,
            is_victory=True,
            elapsed_seconds=180.5,
            difficulty_level=4,
            deck_type="french",
            draw_count=2,
            recycle_count=1,
            move_count=42
        )
        
        assert score.base_score == 100
        assert score.total_score == 1045
        assert score.is_victory is True
        assert score.elapsed_seconds == 180.5
        assert score.difficulty_level == 4
        assert score.deck_type == "french"
    
    def test_final_score_is_frozen(self):
        """Test FinalScore is immutable."""
        score = FinalScore(
            base_score=100,
            deck_bonus=0,
            draw_bonus=0,
            difficulty_multiplier=1.0,
            time_bonus=0,
            victory_bonus=0,
            total_score=100,
            is_victory=False,
            elapsed_seconds=120.0,
            difficulty_level=1,
            deck_type="neapolitan",
            draw_count=1,
            recycle_count=0,
            move_count=20
        )
        
        with pytest.raises(FrozenInstanceError):
            score.total_score = 200  # type: ignore
    
    def test_get_breakdown_all_components(self):
        """Test breakdown includes all non-zero components."""
        score = FinalScore(
            base_score=85,
            deck_bonus=150,
            draw_bonus=100,
            difficulty_multiplier=2.0,
            time_bonus=345,
            victory_bonus=500,
            total_score=1015,
            is_victory=True,
            elapsed_seconds=180.0,
            difficulty_level=4,
            deck_type="french",
            draw_count=2,
            recycle_count=1,
            move_count=50
        )
        
        breakdown = score.get_breakdown()
        
        assert "Punteggio base: 85 punti" in breakdown
        assert "Bonus mazzo: 150 punti" in breakdown
        assert "Bonus carte pescate: 100 punti" in breakdown
        assert "Moltiplicatore difficoltà: 2.0" in breakdown
        assert "Bonus tempo: 345 punti" in breakdown
        assert "Bonus vittoria: 500 punti" in breakdown
        assert "Punteggio totale: 1015 punti" in breakdown
    
    def test_get_breakdown_minimal_components(self):
        """Test breakdown excludes zero bonuses."""
        score = FinalScore(
            base_score=50,
            deck_bonus=0,
            draw_bonus=0,
            difficulty_multiplier=1.0,
            time_bonus=0,
            victory_bonus=0,
            total_score=50,
            is_victory=False,
            elapsed_seconds=300.0,
            difficulty_level=1,
            deck_type="neapolitan",
            draw_count=1,
            recycle_count=5,
            move_count=100
        )
        
        breakdown = score.get_breakdown()
        
        assert "Punteggio base: 50 punti" in breakdown
        assert "Bonus mazzo" not in breakdown
        assert "Bonus carte pescate" not in breakdown
        assert "Moltiplicatore difficoltà: 1.0" in breakdown
        assert "Bonus tempo" not in breakdown
        assert "Bonus vittoria" not in breakdown
        assert "Punteggio totale: 50 punti" in breakdown
    
    def test_get_breakdown_is_italian(self):
        """Test breakdown is in Italian (no English)."""
        score = FinalScore(
            base_score=100,
            deck_bonus=150,
            draw_bonus=0,
            difficulty_multiplier=1.5,
            time_bonus=200,
            victory_bonus=500,
            total_score=875,
            is_victory=True,
            elapsed_seconds=240.0,
            difficulty_level=3,
            deck_type="french",
            draw_count=3,
            recycle_count=2,
            move_count=75
        )
        
        breakdown = score.get_breakdown()
        
        # Check for Italian keywords
        assert "punti" in breakdown
        assert "Punteggio" in breakdown
        assert "Bonus" in breakdown
        
        # Check no English keywords
        assert "score" not in breakdown.lower()
        assert "bonus" not in breakdown.lower() or "Bonus" in breakdown  # Allow capitalized Italian
        assert "points" not in breakdown.lower()
