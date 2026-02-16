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
    
    def test_v2_new_events_exist(self):
        """Test v2.0 new event types are defined."""
        assert ScoreEventType.STOCK_DRAW
        assert ScoreEventType.INVALID_MOVE
        assert ScoreEventType.AUTO_MOVE
    
    def test_v2_new_events_are_strings(self):
        """Test v2.0 event values are string identifiers."""
        assert ScoreEventType.STOCK_DRAW.value == "stock_draw"
        assert ScoreEventType.INVALID_MOVE.value == "invalid_move"
        assert ScoreEventType.AUTO_MOVE.value == "auto_move"


class TestScoringConfig:
    """Tests for ScoringConfig dataclass."""
    
    def test_default_event_points(self):
        """Test default event point values match v2.0 specification."""
        config = ScoringConfig()
        
        assert config.event_points[ScoreEventType.WASTE_TO_FOUNDATION] == 10
        assert config.event_points[ScoreEventType.TABLEAU_TO_FOUNDATION] == 10
        assert config.event_points[ScoreEventType.CARD_REVEALED] == 5
        assert config.event_points[ScoreEventType.FOUNDATION_TO_TABLEAU] == -15
        assert config.event_points[ScoreEventType.RECYCLE_WASTE] == 0  # v2.0: calculated via recycle_penalties
        assert config.event_points[ScoreEventType.STOCK_DRAW] == 0  # v2.0: calculated via stock_draw_penalties
        assert config.event_points[ScoreEventType.INVALID_MOVE] == 0
        assert config.event_points[ScoreEventType.AUTO_MOVE] == 0
        assert config.event_points[ScoreEventType.UNDO_MOVE] == 0
        assert config.event_points[ScoreEventType.HINT_USED] == 0
    
    def test_default_difficulty_multipliers(self):
        """Test difficulty multipliers scale from 1.0 to 2.2 (v2.0)."""
        config = ScoringConfig()
        
        assert config.difficulty_multipliers[1] == 1.0
        assert config.difficulty_multipliers[2] == 1.2
        assert config.difficulty_multipliers[3] == 1.4
        assert config.difficulty_multipliers[4] == 1.8
        assert config.difficulty_multipliers[5] == 2.2
    
    def test_default_deck_type_bonuses(self):
        """Test deck bonuses v2.0: Neapolitan +100, French +50."""
        config = ScoringConfig()
        
        assert config.deck_type_bonuses["neapolitan"] == 100
        assert config.deck_type_bonuses["french"] == 50
    
    def test_default_draw_count_bonuses(self):
        """Test draw count bonuses scale with difficulty (v2.0)."""
        config = ScoringConfig()
        
        assert config.draw_count_bonuses[1]["low"] == 0
        assert config.draw_count_bonuses[2]["low"] == 100
        assert config.draw_count_bonuses[3]["low"] == 200
        assert config.draw_count_bonuses[2]["high"] == 50
        assert config.draw_count_bonuses[3]["high"] == 100
    
    def test_default_victory_bonus_base(self):
        """Test victory bonus base is 400 (v2.0)."""
        config = ScoringConfig()
        assert config.victory_bonus_base == 400
    
    def test_default_victory_weights(self):
        """Test victory weights sum to 1.0 (v2.0)."""
        config = ScoringConfig()
        assert config.victory_weights["time"] == 0.35
        assert config.victory_weights["moves"] == 0.35
        assert config.victory_weights["recycles"] == 0.30
        assert sum(config.victory_weights.values()) == 1.0
    
    def test_default_stock_draw_params(self):
        """Test stock draw progressive penalty params (v2.0)."""
        config = ScoringConfig()
        assert config.stock_draw_thresholds == (20, 40)
        assert config.stock_draw_penalties == (0, -1, -2)
    
    def test_default_recycle_penalties(self):
        """Test recycle progressive penalties (v2.0)."""
        config = ScoringConfig()
        assert config.recycle_penalties == (0, 0, -10, -20, -35, -55, -80)
    
    def test_default_time_bonus_params(self):
        """Test time bonus params v2.0."""
        config = ScoringConfig()
        assert config.time_bonus_max_timer_off == 1200
        assert config.time_bonus_decay_per_minute == 40
        assert config.time_bonus_max_timer_on == 1000
        assert config.overtime_penalty_per_minute == -100
    
    def test_default_min_score(self):
        """Test minimum score is 0."""
        config = ScoringConfig()
        assert config.min_score == 0
    
    def test_default_version(self):
        """Test version is 2.0.0."""
        config = ScoringConfig()
        assert config.version == "2.0.0"
    
    def test_config_is_frozen(self):
        """Test ScoringConfig is immutable."""
        config = ScoringConfig()
        
        with pytest.raises(FrozenInstanceError):
            config.victory_bonus_base = 1000  # type: ignore
    
    def test_validation_victory_weights_sum(self):
        """Test validation raises on invalid victory weights sum."""
        with pytest.raises(ValueError, match="must sum to 1.0"):
            ScoringConfig(
                victory_weights={"time": 0.5, "moves": 0.3, "recycles": 0.1}
            )
    
    def test_validation_difficulty_levels(self):
        """Test validation raises on missing difficulty levels."""
        with pytest.raises(ValueError, match="must have levels 1-5"):
            ScoringConfig(
                difficulty_multipliers={1: 1.0, 2: 1.2, 3: 1.4}  # Missing 4, 5
            )
    
    def test_validation_version_check(self):
        """Test validation raises on invalid version."""
        with pytest.raises(ValueError, match="Expected version 2"):
            ScoringConfig(version="1.5.0")


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
            move_count=42,
            victory_quality_multiplier=1.05
        )
        
        assert score.base_score == 100
        assert score.total_score == 1045
        assert score.is_victory is True
        assert score.elapsed_seconds == 180.5
        assert score.difficulty_level == 4
        assert score.deck_type == "french"
        assert score.victory_quality_multiplier == 1.05
    
    def test_create_final_score_v2_defaults(self):
        """Test v2.0 victory_quality_multiplier defaults to 0.0."""
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
        
        assert score.victory_quality_multiplier == 0.0
    
    def test_create_final_score_legacy_sentinel(self):
        """Test legacy score with -1.0 sentinel value."""
        score = FinalScore(
            base_score=100,
            deck_bonus=50,
            draw_bonus=0,
            difficulty_multiplier=1.0,
            time_bonus=0,
            victory_bonus=500,
            total_score=650,
            is_victory=True,
            elapsed_seconds=300.0,
            difficulty_level=1,
            deck_type="french",
            draw_count=1,
            recycle_count=2,
            move_count=80,
            victory_quality_multiplier=-1.0  # Legacy sentinel
        )
        
        assert score.victory_quality_multiplier == -1.0
    
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
            move_count=20,
            victory_quality_multiplier=0.0
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
            move_count=50,
            victory_quality_multiplier=1.25
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
            move_count=100,
            victory_quality_multiplier=0.0
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
            move_count=75,
            victory_quality_multiplier=1.15
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
