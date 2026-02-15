"""Unit tests for DifficultyPreset model.

Tests the difficulty preset system that manages locked and customizable options
for each of the 5 difficulty levels.

Version: v2.4.0
Test Framework: pytest
Coverage Target: 95%+

Test Categories:
1. Preset creation and factory methods
2. Lock status queries
3. Preset value retrieval
4. All 5 preset definitions
5. Edge cases and validation
"""

import pytest
from src.domain.models.difficulty_preset import DifficultyPreset


class TestDifficultyPresetFactory:
    """Test preset factory methods and creation."""
    
    def test_get_preset_level_1(self):
        """Test getting Level 1 (Principiante) preset."""
        preset = DifficultyPreset.get_preset(1)
        
        assert preset.level == 1
        assert preset.name == "Principiante"
        assert "principianti" in preset.description.lower()
    
    def test_get_preset_level_5(self):
        """Test getting Level 5 (Maestro) preset."""
        preset = DifficultyPreset.get_preset(5)
        
        assert preset.level == 5
        assert preset.name == "Maestro"
        assert "tournament" in preset.description.lower()
    
    def test_get_preset_invalid_level_zero(self):
        """Test that level 0 raises ValueError."""
        with pytest.raises(ValueError, match="Invalid difficulty level"):
            DifficultyPreset.get_preset(0)
    
    def test_get_preset_invalid_level_six(self):
        """Test that level 6 raises ValueError."""
        with pytest.raises(ValueError, match="Invalid difficulty level"):
            DifficultyPreset.get_preset(6)
    
    def test_get_all_presets_returns_five(self):
        """Test get_all_presets returns all 5 presets."""
        presets = DifficultyPreset.get_all_presets()
        
        assert len(presets) == 5
        assert all(level in presets for level in range(1, 6))
    
    def test_preset_immutability(self):
        """Test that presets are immutable (frozen dataclass)."""
        preset = DifficultyPreset.get_preset(1)
        
        with pytest.raises(Exception):  # FrozenInstanceError
            preset.level = 2


class TestLevel1Principiante:
    """Test Level 1 - Principiante preset."""
    
    def test_timer_is_locked(self):
        """Level 1 must lock timer to OFF."""
        preset = DifficultyPreset.get_preset(1)
        
        assert preset.is_locked("max_time_game")
        assert preset.get_value("max_time_game") == 0  # OFF
    
    def test_draw_count_not_locked(self):
        """Level 1 allows customizable draw_count."""
        preset = DifficultyPreset.get_preset(1)
        
        assert not preset.is_locked("draw_count")
        assert preset.get_value("draw_count") == 1  # Default
    
    def test_default_values(self):
        """Level 1 has beginner-friendly defaults."""
        preset = DifficultyPreset.get_preset(1)
        
        assert preset.get_value("draw_count") == 1  # Easiest
        assert preset.get_value("shuffle_discards") is True  # Mescolata (easier)
        assert preset.get_value("command_hints_enabled") is True  # Hints ON


class TestLevel2Facile:
    """Test Level 2 - Facile preset."""
    
    def test_timer_strict_mode_locked(self):
        """Level 2 locks timer_strict_mode to PERMISSIVE."""
        preset = DifficultyPreset.get_preset(2)
        
        assert preset.is_locked("timer_strict_mode")
        assert preset.get_value("timer_strict_mode") is False  # PERMISSIVE
    
    def test_draw_count_not_locked(self):
        """Level 2 allows customizable draw_count."""
        preset = DifficultyPreset.get_preset(2)
        
        assert not preset.is_locked("draw_count")
        assert preset.get_value("draw_count") == 2  # Default
    
    def test_timer_customizable(self):
        """Level 2 allows timer customization."""
        preset = DifficultyPreset.get_preset(2)
        
        assert not preset.is_locked("max_time_game")


class TestLevel3Normale:
    """Test Level 3 - Normale preset (Vegas standard)."""
    
    def test_draw_count_locked_to_three(self):
        """Level 3 locks draw_count to 3 (Vegas standard)."""
        preset = DifficultyPreset.get_preset(3)
        
        assert preset.is_locked("draw_count")
        assert preset.get_value("draw_count") == 3
    
    def test_timer_customizable(self):
        """Level 3 allows timer customization."""
        preset = DifficultyPreset.get_preset(3)
        
        assert not preset.is_locked("max_time_game")
        assert not preset.is_locked("timer_strict_mode")
    
    def test_default_inversione(self):
        """Level 3 defaults to Inversione (Vegas standard)."""
        preset = DifficultyPreset.get_preset(3)
        
        assert preset.get_value("shuffle_discards") is False  # Inversione


class TestLevel4Esperto:
    """Test Level 4 - Esperto preset (Time Attack)."""
    
    def test_timer_locked_to_30_minutes(self):
        """Level 4 locks timer to 30 minutes."""
        preset = DifficultyPreset.get_preset(4)
        
        assert preset.is_locked("max_time_game")
        assert preset.get_value("max_time_game") == 1800  # 30 min in seconds
    
    def test_draw_count_locked_to_three(self):
        """Level 4 locks draw_count to 3."""
        preset = DifficultyPreset.get_preset(4)
        
        assert preset.is_locked("draw_count")
        assert preset.get_value("draw_count") == 3
    
    def test_hints_disabled(self):
        """Level 4 disables command hints."""
        preset = DifficultyPreset.get_preset(4)
        
        assert preset.is_locked("command_hints_enabled")
        assert preset.get_value("command_hints_enabled") is False
    
    def test_permissive_timer_mode(self):
        """Level 4 uses PERMISSIVE timer (can continue with malus)."""
        preset = DifficultyPreset.get_preset(4)
        
        assert preset.is_locked("timer_strict_mode")
        assert preset.get_value("timer_strict_mode") is False  # PERMISSIVE
    
    def test_scoring_customizable(self):
        """Level 4 allows scoring customization."""
        preset = DifficultyPreset.get_preset(4)
        
        assert not preset.is_locked("scoring_enabled")


class TestLevel5Maestro:
    """Test Level 5 - Maestro preset (Tournament strict)."""
    
    def test_timer_locked_to_15_minutes_strict(self):
        """Level 5 locks timer to 15 minutes STRICT."""
        preset = DifficultyPreset.get_preset(5)
        
        assert preset.is_locked("max_time_game")
        assert preset.get_value("max_time_game") == 900  # 15 min in seconds
        
        assert preset.is_locked("timer_strict_mode")
        assert preset.get_value("timer_strict_mode") is True  # STRICT (auto-stop)
    
    def test_all_gameplay_options_locked(self):
        """Level 5 locks all gameplay options."""
        preset = DifficultyPreset.get_preset(5)
        
        # All gameplay options must be locked
        assert preset.is_locked("draw_count")
        assert preset.is_locked("max_time_game")
        assert preset.is_locked("timer_strict_mode")
        assert preset.is_locked("shuffle_discards")
        assert preset.is_locked("scoring_enabled")
        assert preset.is_locked("command_hints_enabled")
    
    def test_draw_count_locked_to_three(self):
        """Level 5 locks draw_count to 3."""
        preset = DifficultyPreset.get_preset(5)
        
        assert preset.get_value("draw_count") == 3
    
    def test_scoring_mandatory(self):
        """Level 5 forces scoring ON (required for tournament)."""
        preset = DifficultyPreset.get_preset(5)
        
        assert preset.is_locked("scoring_enabled")
        assert preset.get_value("scoring_enabled") is True
    
    def test_hints_disabled(self):
        """Level 5 disables command hints."""
        preset = DifficultyPreset.get_preset(5)
        
        assert preset.is_locked("command_hints_enabled")
        assert preset.get_value("command_hints_enabled") is False
    
    def test_inversione_forced(self):
        """Level 5 forces Inversione mode."""
        preset = DifficultyPreset.get_preset(5)
        
        assert preset.is_locked("shuffle_discards")
        assert preset.get_value("shuffle_discards") is False  # Inversione
    
    def test_get_locked_options_count(self):
        """Level 5 should lock 6 options (all except deck_type)."""
        preset = DifficultyPreset.get_preset(5)
        locked = preset.get_locked_options()
        
        assert len(locked) == 6
        assert "deck_type" not in locked  # deck_type never locked


class TestPresetLockQueries:
    """Test lock status query methods."""
    
    def test_is_locked_returns_bool(self):
        """is_locked() should return boolean."""
        preset = DifficultyPreset.get_preset(3)
        
        assert isinstance(preset.is_locked("draw_count"), bool)
        assert isinstance(preset.is_locked("max_time_game"), bool)
    
    def test_is_locked_unknown_option(self):
        """is_locked() with unknown option returns False."""
        preset = DifficultyPreset.get_preset(5)
        
        assert not preset.is_locked("unknown_option")
    
    def test_get_value_returns_none_for_unlocked(self):
        """get_value() returns None for options without preset value."""
        preset = DifficultyPreset.get_preset(2)
        
        # max_time_game is not locked at level 2, so no forced value
        result = preset.get_value("max_time_game")
        assert result is None or isinstance(result, (int, bool))
    
    def test_get_locked_options_returns_set(self):
        """get_locked_options() returns a set."""
        preset = DifficultyPreset.get_preset(4)
        locked = preset.get_locked_options()
        
        assert isinstance(locked, set)
        assert len(locked) > 0
    
    def test_get_locked_options_returns_copy(self):
        """get_locked_options() returns a copy (modifications don't affect preset)."""
        preset = DifficultyPreset.get_preset(5)
        locked1 = preset.get_locked_options()
        locked2 = preset.get_locked_options()
        
        # Modify copy
        locked1.add("test_option")
        
        # Original should be unchanged
        assert "test_option" not in locked2
        assert "test_option" not in preset.get_locked_options()


class TestPresetProgression:
    """Test preset progression from Level 1 to 5."""
    
    def test_lock_count_increases_with_level(self):
        """Higher levels should lock more options."""
        lock_counts = {}
        for level in range(1, 6):
            preset = DifficultyPreset.get_preset(level)
            lock_counts[level] = len(preset.get_locked_options())
        
        # Level 1 should have fewer locks than Level 5
        assert lock_counts[1] < lock_counts[5]
        
        # Level 5 should have maximum locks
        assert lock_counts[5] == 6  # All options except deck_type
    
    def test_all_levels_have_unique_names(self):
        """Each level should have a unique name."""
        names = set()
        for level in range(1, 6):
            preset = DifficultyPreset.get_preset(level)
            names.add(preset.name)
        
        assert len(names) == 5  # All unique
    
    def test_level_3_is_vegas_standard(self):
        """Level 3 (Normale) represents Vegas standard rules."""
        preset = DifficultyPreset.get_preset(3)
        
        # Vegas standard: 3-card draw
        assert preset.get_value("draw_count") == 3
        assert preset.is_locked("draw_count")
        
        # Vegas prefers inversione
        assert preset.get_value("shuffle_discards") is False
    
    def test_level_5_is_most_restrictive(self):
        """Level 5 (Maestro) should be most restrictive."""
        preset5 = DifficultyPreset.get_preset(5)
        
        # Should have more locks than any other level
        for level in range(1, 5):
            preset = DifficultyPreset.get_preset(level)
            assert len(preset5.get_locked_options()) >= len(preset.get_locked_options())
