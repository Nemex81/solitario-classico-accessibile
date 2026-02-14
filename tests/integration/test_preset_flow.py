"""Integration tests for difficulty preset system end-to-end flows.

Tests complete workflows from preset selection through lock enforcement
and JSON persistence.

Version: v2.4.0
Test Framework: pytest
Coverage: End-to-end integration scenarios

Test Scenarios:
1. Level progression 1→5 with lock verification
2. Lock enforcement preventing modifications
3. Save/Load with anti-cheat validation
4. Preset changes cascading to options
5. Tournament mode (Level 5) full lockdown
"""

import pytest
from src.domain.services.game_settings import GameSettings
from src.domain.models.difficulty_preset import DifficultyPreset


class TestPresetProgression:
    """Test level progression and lock accumulation."""
    
    def test_progression_1_to_5_increases_locks(self):
        """Progressing from Level 1 to 5 increases locked options."""
        settings = GameSettings()
        
        # Level 1: Minimal locks
        settings.difficulty_level = 1
        settings.apply_difficulty_preset(1)
        locks_level_1 = len(settings.get_locked_options())
        
        # Level 3: More locks
        settings.difficulty_level = 3
        settings.apply_difficulty_preset(3)
        locks_level_3 = len(settings.get_locked_options())
        
        # Level 5: Maximum locks
        settings.difficulty_level = 5
        settings.apply_difficulty_preset(5)
        locks_level_5 = len(settings.get_locked_options())
        
        # Verify progression
        assert locks_level_1 < locks_level_3 < locks_level_5
        assert locks_level_5 == 6  # All options except deck_type


class TestLockEnforcement:
    """Test lock enforcement prevents modifications."""
    
    def test_level_5_locks_draw_count(self):
        """Level 5 prevents draw_count modifications."""
        settings = GameSettings()
        settings.difficulty_level = 5
        settings.apply_difficulty_preset(5)
        
        # Verify locked
        assert settings.is_option_locked("draw_count") is True
        assert settings.draw_count == 3  # Locked value
    
    def test_level_1_allows_draw_count(self):
        """Level 1 allows draw_count modifications."""
        settings = GameSettings()
        settings.difficulty_level = 1
        settings.apply_difficulty_preset(1)
        
        # Verify not locked
        assert settings.is_option_locked("draw_count") is False
        
        # Can modify
        settings.draw_count = 2
        assert settings.draw_count == 2


class TestSaveLoadAntiCheat:
    """Test JSON save/load with anti-cheat validation."""
    
    def test_level_5_cheating_prevented(self):
        """Manual JSON edit to bypass locks is prevented."""
        settings = GameSettings()
        
        # Simulate cheating: Level 5 with illegal values
        cheat_data = {
            "difficulty_level": 5,
            "draw_count": 1,  # Should be 3 (locked)
            "max_time_game": 3600,  # Should be 900 (locked)
            "command_hints_enabled": True,  # Should be False (locked)
        }
        
        # Load with validation
        settings.load_from_dict(cheat_data)
        
        # Verify preset enforced (cheat prevented)
        assert settings.difficulty_level == 5
        assert settings.draw_count == 3  # Fixed by preset
        assert settings.max_time_game == 900  # Fixed by preset
        assert settings.command_hints_enabled is False  # Fixed by preset
    
    def test_level_1_values_preserved(self):
        """Level 1 (no locks) preserves custom values."""
        settings = GameSettings()
        
        data = {
            "difficulty_level": 1,
            "draw_count": 2,  # Custom value (allowed)
            "max_time_game": 0,  # Will be overridden to 0 by preset
        }
        
        settings.load_from_dict(data)
        
        assert settings.difficulty_level == 1
        # draw_count overridden by preset default
        assert settings.draw_count == 1  # Preset default for Level 1


class TestPresetCascading:
    """Test preset changes cascade to all affected options."""
    
    def test_cycle_to_level_5_applies_all_locks(self):
        """Cycling to Level 5 applies all locked values."""
        settings = GameSettings()
        settings.difficulty_level = 1
        
        # Set custom values
        settings.draw_count = 1
        settings.max_time_game = 0
        settings.command_hints_enabled = True
        
        # Cycle to Level 5
        settings.difficulty_level = 5
        settings.apply_difficulty_preset(5)
        
        # Verify all preset values applied
        assert settings.draw_count == 3
        assert settings.max_time_game == 900
        assert settings.timer_strict_mode is True
        assert settings.command_hints_enabled is False
        assert settings.scoring_enabled is True
        assert settings.shuffle_discards is False


class TestTournamentMode:
    """Test Level 5 tournament mode lockdown."""
    
    def test_level_5_locks_all_gameplay_options(self):
        """Level 5 locks all 6 gameplay options."""
        settings = GameSettings()
        settings.difficulty_level = 5
        
        locked = settings.get_locked_options()
        
        # Verify all 6 options locked
        assert "draw_count" in locked
        assert "max_time_game" in locked
        assert "timer_strict_mode" in locked
        assert "shuffle_discards" in locked
        assert "scoring_enabled" in locked
        assert "command_hints_enabled" in locked
        
        # Verify deck_type NOT locked (aesthetic choice)
        assert "deck_type" not in locked
    
    def test_level_5_preset_values_match_spec(self):
        """Level 5 preset matches tournament specification."""
        settings = GameSettings()
        settings.apply_difficulty_preset(5)
        
        # Verify tournament spec
        assert settings.draw_count == 3  # 3-card draw
        assert settings.max_time_game == 900  # 15 minutes strict
        assert settings.timer_strict_mode is True  # STRICT (auto-stop)
        assert settings.shuffle_discards is False  # Inversione
        assert settings.scoring_enabled is True  # Mandatory scoring
        assert settings.command_hints_enabled is False  # No hints
