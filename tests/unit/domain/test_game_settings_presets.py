"""Unit tests for GameSettings preset integration.

Tests the integration of DifficultyPreset system into GameSettings,
including preset application, lock queries, and cycle_difficulty refactoring.

Version: v2.4.0
Test Framework: pytest
Coverage Target: 95%+

Test Categories:
1. Preset application (apply_difficulty_preset)
2. Lock status queries (is_option_locked, get_locked_options)
3. Current preset retrieval (get_current_preset)
4. Refactored cycle_difficulty with presets
5. Edge cases and validation
"""

import pytest
from src.domain.services.game_settings import GameSettings


class TestApplyDifficultyPreset:
    """Test apply_difficulty_preset method."""
    
    def test_apply_level_1_preset(self):
        """Test applying Level 1 (Principiante) preset."""
        settings = GameSettings()
        settings.difficulty_level = 1
        settings.apply_difficulty_preset(1)
        
        # Level 1 locks timer to OFF
        assert settings.max_time_game == 0
        # Default values
        assert settings.draw_count == 1
        assert settings.shuffle_discards is True  # Mescolata (easier)
    
    def test_apply_level_3_preset(self):
        """Test applying Level 3 (Normale) preset."""
        settings = GameSettings()
        settings.apply_difficulty_preset(3)
        
        # Level 3 locks draw_count to 3
        assert settings.draw_count == 3
        # Vegas standard prefers Inversione
        assert settings.shuffle_discards is False
    
    def test_apply_level_5_preset(self):
        """Test applying Level 5 (Maestro) preset."""
        settings = GameSettings()
        settings.apply_difficulty_preset(5)
        
        # Level 5 locks all options
        assert settings.draw_count == 3
        assert settings.max_time_game == 900  # 15 min
        assert settings.timer_strict_mode is True  # STRICT
        assert settings.shuffle_discards is False  # Inversione
        assert settings.scoring_enabled is True
        assert settings.command_hints_enabled is False
    
    def test_apply_preset_overwrites_existing_values(self):
        """Test that preset application overwrites existing values."""
        settings = GameSettings()
        # Set custom values
        settings.draw_count = 1
        settings.max_time_game = 3600
        
        # Apply Level 5 preset
        settings.apply_difficulty_preset(5)
        
        # Values should be overwritten
        assert settings.draw_count == 3  # Overwritten
        assert settings.max_time_game == 900  # Overwritten


class TestIsOptionLocked:
    """Test is_option_locked method."""
    
    def test_timer_locked_at_level_1(self):
        """Level 1 locks timer to OFF."""
        settings = GameSettings()
        settings.difficulty_level = 1
        
        assert settings.is_option_locked("max_time_game") is True
    
    def test_draw_count_not_locked_at_level_1(self):
        """Level 1 allows draw_count customization."""
        settings = GameSettings()
        settings.difficulty_level = 1
        
        assert settings.is_option_locked("draw_count") is False
    
    def test_draw_count_locked_at_level_3(self):
        """Level 3 locks draw_count to 3."""
        settings = GameSettings()
        settings.difficulty_level = 3
        
        assert settings.is_option_locked("draw_count") is True
    
    def test_all_options_locked_at_level_5(self):
        """Level 5 locks all gameplay options."""
        settings = GameSettings()
        settings.difficulty_level = 5
        
        # All gameplay options locked
        assert settings.is_option_locked("draw_count") is True
        assert settings.is_option_locked("max_time_game") is True
        assert settings.is_option_locked("timer_strict_mode") is True
        assert settings.is_option_locked("shuffle_discards") is True
        assert settings.is_option_locked("scoring_enabled") is True
        assert settings.is_option_locked("command_hints_enabled") is True
    
    def test_deck_type_never_locked(self):
        """Deck type is never locked (aesthetic choice)."""
        settings = GameSettings()
        
        for level in range(1, 6):
            settings.difficulty_level = level
            assert settings.is_option_locked("deck_type") is False
    
    def test_unknown_option_not_locked(self):
        """Unknown options return False."""
        settings = GameSettings()
        settings.difficulty_level = 5
        
        assert settings.is_option_locked("unknown_option") is False


class TestGetLockedOptions:
    """Test get_locked_options method."""
    
    def test_level_1_has_one_lock(self):
        """Level 1 locks only timer."""
        settings = GameSettings()
        settings.difficulty_level = 1
        locked = settings.get_locked_options()
        
        assert len(locked) == 1
        assert "max_time_game" in locked
    
    def test_level_5_has_six_locks(self):
        """Level 5 locks 6 options (all except deck_type)."""
        settings = GameSettings()
        settings.difficulty_level = 5
        locked = settings.get_locked_options()
        
        assert len(locked) == 6
        assert "draw_count" in locked
        assert "max_time_game" in locked
        assert "timer_strict_mode" in locked
        assert "shuffle_discards" in locked
        assert "scoring_enabled" in locked
        assert "command_hints_enabled" in locked
        assert "deck_type" not in locked  # Never locked
    
    def test_lock_count_increases_with_level(self):
        """Higher levels lock more options."""
        settings = GameSettings()
        
        settings.difficulty_level = 1
        locks_level_1 = len(settings.get_locked_options())
        
        settings.difficulty_level = 5
        locks_level_5 = len(settings.get_locked_options())
        
        assert locks_level_5 > locks_level_1


class TestGetCurrentPreset:
    """Test get_current_preset method."""
    
    def test_get_preset_level_1(self):
        """Get preset for Level 1."""
        settings = GameSettings()
        settings.difficulty_level = 1
        preset = settings.get_current_preset()
        
        assert preset.level == 1
        assert preset.name == "Principiante"
    
    def test_get_preset_level_5(self):
        """Get preset for Level 5."""
        settings = GameSettings()
        settings.difficulty_level = 5
        preset = settings.get_current_preset()
        
        assert preset.level == 5
        assert preset.name == "Maestro"
    
    def test_preset_matches_difficulty_level(self):
        """Current preset matches current difficulty level."""
        settings = GameSettings()
        
        for level in range(1, 6):
            settings.difficulty_level = level
            preset = settings.get_current_preset()
            assert preset.level == level


class TestCycleDifficultyWithPresets:
    """Test refactored cycle_difficulty using preset system."""
    
    def test_cycle_from_1_to_2(self):
        """Cycling from 1 to 2 applies Level 2 preset."""
        settings = GameSettings()
        settings.difficulty_level = 1
        
        success, message = settings.cycle_difficulty()
        
        assert success is True
        assert settings.difficulty_level == 2
        assert "Facile" in message
    
    def test_cycle_from_5_to_1(self):
        """Cycling from 5 wraps to 1."""
        settings = GameSettings()
        settings.difficulty_level = 5
        
        success, message = settings.cycle_difficulty()
        
        assert success is True
        assert settings.difficulty_level == 1
        assert "Principiante" in message
    
    def test_cycle_applies_preset_values(self):
        """Cycling to level applies preset values automatically."""
        settings = GameSettings()
        settings.difficulty_level = 2
        settings.draw_count = 1  # Custom value
        
        # Cycle to Level 3
        success, message = settings.cycle_difficulty()
        
        assert success is True
        assert settings.difficulty_level == 3
        # Level 3 preset locks draw_count to 3
        assert settings.draw_count == 3
    
    def test_cycle_to_level_5_applies_all_locks(self):
        """Cycling to Level 5 applies all locked values."""
        settings = GameSettings()
        settings.difficulty_level = 4
        
        # Cycle to Level 5
        success, message = settings.cycle_difficulty()
        
        assert success is True
        assert settings.difficulty_level == 5
        # Verify all Level 5 preset values
        assert settings.draw_count == 3
        assert settings.max_time_game == 900
        assert settings.timer_strict_mode is True
        assert settings.shuffle_discards is False
        assert settings.scoring_enabled is True
        assert settings.command_hints_enabled is False
    
    def test_cycle_message_announces_changes(self):
        """Cycle message announces key changes."""
        settings = GameSettings()
        settings.difficulty_level = 4
        
        success, message = settings.cycle_difficulty()
        
        assert success is True
        assert "Maestro" in message or "5" in message
        # Should mention tournament/strict mode
        assert "Tournament" in message or "STRICT" in message or "bloccate" in message


class TestPresetEdgeCases:
    """Test edge cases and error handling."""
    
    def test_invalid_level_in_is_locked(self):
        """Invalid difficulty level returns False for is_locked."""
        settings = GameSettings()
        settings.difficulty_level = 99  # Invalid
        
        # Should not crash, returns False
        assert settings.is_option_locked("draw_count") is False
    
    def test_invalid_level_in_get_locked_options(self):
        """Invalid difficulty level returns empty set."""
        settings = GameSettings()
        settings.difficulty_level = 0  # Invalid
        
        locked = settings.get_locked_options()
        assert isinstance(locked, set)
        assert len(locked) == 0
    
    def test_preset_integration_backwards_compatible(self):
        """Preset system doesn't break existing behavior."""
        settings = GameSettings()
        
        # Existing attributes still accessible
        assert hasattr(settings, 'deck_type')
        assert hasattr(settings, 'difficulty_level')
        assert hasattr(settings, 'draw_count')
        assert hasattr(settings, 'max_time_game')
        assert hasattr(settings, 'shuffle_discards')
        assert hasattr(settings, 'command_hints_enabled')
        assert hasattr(settings, 'scoring_enabled')
        assert hasattr(settings, 'timer_strict_mode')
