"""Unit tests for GameSettings v2.0.0 validation and constraints.

Tests new features:
- 5 difficulty levels (extended from 3)
- Draw count cycling (separated from difficulty)
- Scoring system toggle
- Level 4-5 constraint validation and auto-adjustment
"""

import pytest

from src.domain.services.game_settings import GameSettings, GameState


@pytest.fixture
def game_state_no_game():
    """GameState with no active game."""
    state = GameState()
    state.is_running = False
    return state


@pytest.fixture
def game_state_with_game():
    """GameState with active game (should block modifications)."""
    state = GameState()
    state.is_running = True
    return state


@pytest.fixture
def settings_no_game(game_state_no_game):
    """GameSettings with no active game."""
    return GameSettings(game_state=game_state_no_game)


@pytest.fixture
def settings_with_game(game_state_with_game):
    """GameSettings with active game."""
    return GameSettings(game_state=game_state_with_game)


class TestDifficultyLevels:
    """Tests for 5-level difficulty system."""
    
    def test_difficulty_cycles_1_to_5(self, settings_no_game):
        """Test difficulty cycles through all 5 levels."""
        settings = settings_no_game
        
        assert settings.difficulty_level == 1
        
        success, msg = settings.cycle_difficulty()
        assert success is True
        assert settings.difficulty_level == 2
        
        settings.cycle_difficulty()
        assert settings.difficulty_level == 3
        
        settings.cycle_difficulty()
        assert settings.difficulty_level == 4
        
        settings.cycle_difficulty()
        assert settings.difficulty_level == 5
        
        settings.cycle_difficulty()
        assert settings.difficulty_level == 1  # Wraps around
    
    def test_difficulty_display_names(self, settings_no_game):
        """Test difficulty display includes level names."""
        settings = settings_no_game
        
        settings.difficulty_level = 1
        assert "Facile" in settings.get_difficulty_display()
        
        settings.difficulty_level = 2
        assert "Medio" in settings.get_difficulty_display()
        
        settings.difficulty_level = 3
        assert "Difficile" in settings.get_difficulty_display()
        
        settings.difficulty_level = 4
        assert "Esperto" in settings.get_difficulty_display()
        
        settings.difficulty_level = 5
        assert "Maestro" in settings.get_difficulty_display()
    
    def test_difficulty_cannot_change_during_game(self, settings_with_game):
        """Test difficulty cannot be changed during active game."""
        settings = settings_with_game
        original_level = settings.difficulty_level
        
        success, msg = settings.cycle_difficulty()
        
        assert success is False
        assert "durante una partita" in msg
        assert settings.difficulty_level == original_level


class TestLevel4Constraints:
    """Tests for Level 4 (Esperto) constraint validation."""
    
    def test_level4_adjusts_timer_if_below_30min(self, settings_no_game):
        """Test cycling to level 4 adjusts timer to minimum 30 min."""
        settings = settings_no_game
        
        # Set timer to 10 minutes (below minimum)
        settings.max_time_game = 600
        settings.difficulty_level = 3
        
        success, msg = settings.cycle_difficulty()
        
        assert success is True
        assert settings.difficulty_level == 4
        assert settings.max_time_game == 1800  # 30 minutes
        assert "Timer aumentato" in msg
    
    def test_level4_keeps_timer_if_above_30min(self, settings_no_game):
        """Test level 4 keeps timer if already ≥30 min."""
        settings = settings_no_game
        
        # Set timer to 45 minutes (above minimum)
        settings.max_time_game = 2700
        settings.difficulty_level = 3
        
        success, msg = settings.cycle_difficulty()
        
        assert success is True
        assert settings.max_time_game == 2700  # Unchanged
        assert "Timer" not in msg  # No adjustment message
    
    def test_level4_ignores_timer_off(self, settings_no_game):
        """Test level 4 doesn't adjust timer when OFF."""
        settings = settings_no_game
        
        # Timer OFF
        settings.max_time_game = -1
        settings.difficulty_level = 3
        
        success, msg = settings.cycle_difficulty()
        
        assert success is True
        assert settings.max_time_game == -1  # Still OFF
    
    def test_level4_adjusts_draw_count_if_below_2(self, settings_no_game):
        """Test cycling to level 4 adjusts draw_count to minimum 2."""
        settings = settings_no_game
        
        settings.draw_count = 1
        settings.difficulty_level = 3
        
        success, msg = settings.cycle_difficulty()
        
        assert success is True
        assert settings.draw_count == 2
        assert "Carte pescate" in msg
    
    def test_level4_keeps_draw_count_if_2_or_3(self, settings_no_game):
        """Test level 4 keeps draw_count if already ≥2."""
        settings = settings_no_game
        
        settings.draw_count = 3
        settings.difficulty_level = 3
        
        success, msg = settings.cycle_difficulty()
        
        assert success is True
        assert settings.draw_count == 3  # Unchanged
    
    def test_level4_locks_shuffle_to_invert(self, settings_no_game):
        """Test cycling to level 4 locks shuffle to invert mode."""
        settings = settings_no_game
        
        settings.shuffle_discards = True  # Random shuffle
        settings.difficulty_level = 3
        
        success, msg = settings.cycle_difficulty()
        
        assert success is True
        assert settings.shuffle_discards is False  # Locked to invert
        assert "Riciclo" in msg


class TestLevel5Constraints:
    """Tests for Level 5 (Maestro) constraint validation."""
    
    def test_level5_adjusts_timer_if_below_15min(self, settings_no_game):
        """Test cycling to level 5 adjusts timer to minimum 15 min."""
        settings = settings_no_game
        
        settings.max_time_game = 300  # 5 minutes
        settings.difficulty_level = 4
        
        success, msg = settings.cycle_difficulty()
        
        assert success is True
        assert settings.difficulty_level == 5
        assert settings.max_time_game == 900  # 15 minutes
        assert "Timer aumentato" in msg
    
    def test_level5_adjusts_timer_if_above_30min(self, settings_no_game):
        """Test cycling to level 5 adjusts timer to maximum 30 min."""
        settings = settings_no_game
        
        settings.max_time_game = 3600  # 60 minutes
        settings.difficulty_level = 4
        
        success, msg = settings.cycle_difficulty()
        
        assert success is True
        assert settings.max_time_game == 1800  # 30 minutes
        assert "Timer ridotto" in msg
    
    def test_level5_keeps_timer_in_range(self, settings_no_game):
        """Test level 5 keeps timer if in 15-30 min range."""
        settings = settings_no_game
        
        settings.max_time_game = 1200  # 20 minutes (in range)
        settings.difficulty_level = 4
        
        success, msg = settings.cycle_difficulty()
        
        assert success is True
        assert settings.max_time_game == 1200  # Unchanged
    
    def test_level5_forces_draw_count_3(self, settings_no_game):
        """Test cycling to level 5 forces draw_count to exactly 3."""
        settings = settings_no_game
        
        # Test with draw_count = 1
        settings.draw_count = 1
        settings.difficulty_level = 4
        
        success, msg = settings.cycle_difficulty()
        
        assert success is True
        assert settings.draw_count == 3
        assert "Carte pescate" in msg
        
        # Test with draw_count = 2
        settings.difficulty_level = 4
        settings.draw_count = 2
        
        success, msg = settings.cycle_difficulty()
        
        assert success is True
        assert settings.draw_count == 3
    
    def test_level5_locks_shuffle_to_invert(self, settings_no_game):
        """Test cycling to level 5 locks shuffle to invert mode."""
        settings = settings_no_game
        
        settings.shuffle_discards = True
        settings.difficulty_level = 4
        
        success, msg = settings.cycle_difficulty()
        
        assert success is True
        assert settings.shuffle_discards is False


class TestDrawCountCycling:
    """Tests for draw_count cycling (v2.0.0 new feature)."""
    
    def test_draw_count_cycles_1_to_3(self, settings_no_game):
        """Test draw_count cycles through 1 -> 2 -> 3 -> 1."""
        settings = settings_no_game
        
        settings.draw_count = 1
        
        success, msg = settings.cycle_draw_count()
        assert success is True
        assert settings.draw_count == 2
        assert "2" in msg
        
        settings.cycle_draw_count()
        assert settings.draw_count == 3
        
        settings.cycle_draw_count()
        assert settings.draw_count == 1  # Wraps around
    
    def test_draw_count_display(self, settings_no_game):
        """Test draw_count display formatting."""
        settings = settings_no_game
        
        settings.draw_count = 1
        assert settings.get_draw_count_display() == "1 carta"
        
        settings.draw_count = 2
        assert settings.get_draw_count_display() == "2 carte"
        
        settings.draw_count = 3
        assert settings.get_draw_count_display() == "3 carte"
    
    def test_draw_count_cannot_change_during_game(self, settings_with_game):
        """Test draw_count cannot be changed during active game."""
        settings = settings_with_game
        original_count = settings.draw_count
        
        success, msg = settings.cycle_draw_count()
        
        assert success is False
        assert "durante una partita" in msg
        assert settings.draw_count == original_count
    
    def test_draw_count_validates_level4_constraint(self, settings_no_game):
        """Test draw_count validates level 4 constraint (≥2)."""
        settings = settings_no_game
        
        settings.difficulty_level = 4
        settings.draw_count = 3
        
        # Cycling from 3 -> 1 should auto-correct to 2
        success, msg = settings.cycle_draw_count()
        
        assert success is True
        assert settings.draw_count == 2  # Auto-corrected from 1
        assert "Esperto" in msg
    
    def test_draw_count_validates_level5_constraint(self, settings_no_game):
        """Test draw_count validates level 5 constraint (=3)."""
        settings = settings_no_game
        
        settings.difficulty_level = 5
        settings.draw_count = 3
        
        # Cycling from 3 -> 1 should auto-correct back to 3
        success, msg = settings.cycle_draw_count()
        
        assert success is True
        assert settings.draw_count == 3  # Auto-corrected
        assert "Maestro" in msg


class TestScoringToggle:
    """Tests for scoring system toggle (v2.0.0 new feature)."""
    
    def test_scoring_toggles_on_off(self, settings_no_game):
        """Test scoring_enabled toggles between True and False."""
        settings = settings_no_game
        
        assert settings.scoring_enabled is True  # Default
        
        success, msg = settings.toggle_scoring()
        assert success is True
        assert settings.scoring_enabled is False
        assert "disattivato" in msg.lower()
        
        success, msg = settings.toggle_scoring()
        assert success is True
        assert settings.scoring_enabled is True
        assert "attivo" in msg.lower()
    
    def test_scoring_display(self, settings_no_game):
        """Test scoring display formatting."""
        settings = settings_no_game
        
        settings.scoring_enabled = True
        assert settings.get_scoring_display() == "Attivo"
        
        settings.scoring_enabled = False
        assert settings.get_scoring_display() == "Disattivato"
    
    def test_scoring_cannot_change_during_game(self, settings_with_game):
        """Test scoring cannot be changed during active game."""
        settings = settings_with_game
        original_state = settings.scoring_enabled
        
        success, msg = settings.toggle_scoring()
        
        assert success is False
        assert "durante una partita" in msg
        assert settings.scoring_enabled == original_state


class TestShuffleModeLocking:
    """Tests for shuffle mode locking at levels 4-5."""
    
    def test_shuffle_cannot_toggle_at_level4(self, settings_no_game):
        """Test shuffle mode locked at level 4."""
        settings = settings_no_game
        
        settings.difficulty_level = 4
        settings.shuffle_discards = False
        
        success, msg = settings.toggle_shuffle_mode()
        
        assert success is False  # Blocked
        assert settings.shuffle_discards is False  # Remains invert
        assert "Esperto" in msg or "Maestro" in msg
    
    def test_shuffle_cannot_toggle_at_level5(self, settings_no_game):
        """Test shuffle mode locked at level 5."""
        settings = settings_no_game
        
        settings.difficulty_level = 5
        settings.shuffle_discards = False
        
        success, msg = settings.toggle_shuffle_mode()
        
        assert success is False  # Blocked
        assert settings.shuffle_discards is False
    
    def test_shuffle_can_toggle_at_levels_1_to_3(self, settings_no_game):
        """Test shuffle mode can toggle at levels 1-3."""
        settings = settings_no_game
        
        for level in [1, 2, 3]:
            settings.difficulty_level = level
            settings.shuffle_discards = False
            
            success, msg = settings.toggle_shuffle_mode()
            
            assert success is True
            assert settings.shuffle_discards is True


class TestIntegration:
    """Integration tests for combined constraint validation."""
    
    def test_cycling_through_all_levels_with_adjustments(self, settings_no_game):
        """Test cycling through all levels applies adjustments correctly."""
        settings = settings_no_game
        
        # Start with restrictive settings
        settings.max_time_game = 300  # 5 minutes
        settings.draw_count = 1
        settings.shuffle_discards = True
        settings.difficulty_level = 1
        
        # Cycle to level 2 (no adjustments)
        success, msg = settings.cycle_difficulty()
        assert success is True
        assert settings.difficulty_level == 2
        assert settings.max_time_game == 300  # Unchanged
        assert settings.draw_count == 1  # Unchanged
        
        # Cycle to level 3 (no adjustments)
        settings.cycle_difficulty()
        assert settings.difficulty_level == 3
        
        # Cycle to level 4 (should adjust all)
        success, msg = settings.cycle_difficulty()
        assert success is True
        assert settings.difficulty_level == 4
        assert settings.max_time_game == 1800  # Adjusted to 30 min
        assert settings.draw_count == 2  # Adjusted
        assert settings.shuffle_discards is False  # Locked
        assert "Regolazioni automatiche" in msg
        
        # Cycle to level 5 (should adjust timer down and draw up)
        # First set timer above 30 min
        settings.max_time_game = 3600  # 60 minutes
        settings.draw_count = 2  # Below required 3
        
        success, msg = settings.cycle_difficulty()
        assert success is True
        assert settings.difficulty_level == 5
        assert settings.max_time_game == 1800  # Reduced to 30 min
        assert settings.draw_count == 3  # Forced to 3
    
    def test_default_values_v2(self, settings_no_game):
        """Test default values for v2.0.0."""
        settings = settings_no_game
        
        assert settings.difficulty_level == 1
        assert settings.draw_count == 1
        assert settings.scoring_enabled is True
        assert settings.deck_type == "french"
        assert settings.max_time_game == -1
        assert settings.shuffle_discards is False
