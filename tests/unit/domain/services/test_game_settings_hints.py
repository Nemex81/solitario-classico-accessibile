"""Unit tests for command hints feature in GameSettings (v1.5.0).

Tests the new command hints setting including:
- Default value (enabled by default for accessibility)
- Toggle functionality (bidirectional)
- Display method for UI formatting
- Validation (blocked during active game)
"""

import pytest
from src.domain.services.game_settings import GameSettings, GameState


class TestCommandHintsDefaultValue:
    """Test default state of command hints feature."""
    
    def test_default_hints_enabled(self):
        """Command hints should be enabled by default for maximum accessibility."""
        settings = GameSettings()
        assert settings.command_hints_enabled is True
    
    def test_display_default_value(self):
        """Display method should return 'Attivi' for default state."""
        settings = GameSettings()
        display = settings.get_command_hints_display()
        assert display == "Attivi"


class TestCommandHintsToggle:
    """Test toggle functionality for command hints."""
    
    def test_toggle_from_on_to_off(self):
        """Toggle should disable hints when currently enabled."""
        settings = GameSettings()
        assert settings.command_hints_enabled is True
        
        success, message = settings.toggle_command_hints()
        
        assert success is True
        assert settings.command_hints_enabled is False
        assert "disattivati" in message.lower()
    
    def test_toggle_from_off_to_on(self):
        """Toggle should enable hints when currently disabled."""
        settings = GameSettings()
        settings.command_hints_enabled = False
        
        success, message = settings.toggle_command_hints()
        
        assert success is True
        assert settings.command_hints_enabled is True
        assert "attivi" in message.lower()
    
    def test_toggle_bidirectional(self):
        """Multiple toggles should work bidirectionally."""
        settings = GameSettings()
        initial_state = settings.command_hints_enabled
        
        # First toggle
        success1, msg1 = settings.toggle_command_hints()
        assert success1 is True
        assert settings.command_hints_enabled == (not initial_state)
        
        # Second toggle (back to initial)
        success2, msg2 = settings.toggle_command_hints()
        assert success2 is True
        assert settings.command_hints_enabled == initial_state
        
        # Third toggle
        success3, msg3 = settings.toggle_command_hints()
        assert success3 is True
        assert settings.command_hints_enabled == (not initial_state)


class TestCommandHintsDisplay:
    """Test display method for UI formatting."""
    
    def test_display_when_enabled(self):
        """Display should return 'Attivi' when hints enabled."""
        settings = GameSettings()
        settings.command_hints_enabled = True
        
        display = settings.get_command_hints_display()
        
        assert display == "Attivi"
    
    def test_display_when_disabled(self):
        """Display should return 'Disattivati' when hints disabled."""
        settings = GameSettings()
        settings.command_hints_enabled = False
        
        display = settings.get_command_hints_display()
        
        assert display == "Disattivati"
    
    def test_display_reflects_state_changes(self):
        """Display should update after toggle operations."""
        settings = GameSettings()
        
        # Initial state (enabled)
        assert settings.get_command_hints_display() == "Attivi"
        
        # After toggle (disabled)
        settings.toggle_command_hints()
        assert settings.get_command_hints_display() == "Disattivati"
        
        # After second toggle (enabled again)
        settings.toggle_command_hints()
        assert settings.get_command_hints_display() == "Attivi"


class TestCommandHintsValidation:
    """Test validation logic (blocked during active game)."""
    
    def test_toggle_blocked_during_game(self):
        """Cannot toggle hints during active game."""
        game_state = GameState()
        game_state.is_running = True
        settings = GameSettings(game_state=game_state)
        
        initial_value = settings.command_hints_enabled
        success, message = settings.toggle_command_hints()
        
        assert success is False
        assert "durante una partita" in message.lower()
        assert settings.command_hints_enabled == initial_value  # Unchanged
    
    def test_toggle_allowed_when_game_not_running(self):
        """Toggle should work when game is not running."""
        game_state = GameState()
        game_state.is_running = False
        settings = GameSettings(game_state=game_state)
        
        success, message = settings.toggle_command_hints()
        
        assert success is True
        assert "suggerimenti comandi" in message.lower()
    
    def test_multiple_toggle_attempts_during_game(self):
        """Multiple toggle attempts during game should all fail."""
        game_state = GameState()
        game_state.is_running = True
        settings = GameSettings(game_state=game_state)
        initial_value = settings.command_hints_enabled
        
        # First attempt
        success1, msg1 = settings.toggle_command_hints()
        assert success1 is False
        assert settings.command_hints_enabled == initial_value
        
        # Second attempt
        success2, msg2 = settings.toggle_command_hints()
        assert success2 is False
        assert settings.command_hints_enabled == initial_value


class TestCommandHintsMessages:
    """Test TTS message content for accessibility."""
    
    def test_message_contains_setting_name(self):
        """Messages should mention 'Suggerimenti comandi' for clarity."""
        settings = GameSettings()
        
        success, message = settings.toggle_command_hints()
        
        assert "suggerimenti comandi" in message.lower()
    
    def test_message_format_for_enabled(self):
        """Message when enabling should be positive and clear."""
        settings = GameSettings()
        settings.command_hints_enabled = False
        
        success, message = settings.toggle_command_hints()
        
        assert success is True
        assert "attivi" in message.lower()
        assert "suggerimenti comandi" in message.lower()
    
    def test_message_format_for_disabled(self):
        """Message when disabling should be clear about state."""
        settings = GameSettings()
        settings.command_hints_enabled = True
        
        success, message = settings.toggle_command_hints()
        
        assert success is True
        assert "disattivati" in message.lower()
        assert "suggerimenti comandi" in message.lower()
    
    def test_error_message_format(self):
        """Error message during game should explain restriction."""
        game_state = GameState()
        game_state.is_running = True
        settings = GameSettings(game_state=game_state)
        
        success, message = settings.toggle_command_hints()
        
        assert success is False
        assert "non puoi" in message.lower()
        assert "durante una partita" in message.lower()


class TestCommandHintsIntegration:
    """Integration tests with other settings."""
    
    def test_command_hints_independent_of_other_settings(self):
        """Command hints should work independently of other settings."""
        settings = GameSettings()
        
        # Modify other settings
        settings.deck_type = "neapolitan"
        settings.difficulty_level = 3
        settings.max_time_game = 600
        settings.shuffle_discards = True
        
        # Command hints should still toggle normally
        success, message = settings.toggle_command_hints()
        assert success is True
        assert settings.command_hints_enabled is False
    
    def test_new_instance_has_correct_defaults(self):
        """New GameSettings instance should have command hints enabled."""
        settings1 = GameSettings()
        assert settings1.command_hints_enabled is True
        
        # Toggle first instance
        settings1.toggle_command_hints()
        assert settings1.command_hints_enabled is False
        
        # New instance should still have default (enabled)
        settings2 = GameSettings()
        assert settings2.command_hints_enabled is True
