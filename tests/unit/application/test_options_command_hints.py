"""Unit tests for options integration with command hints (v1.5.0).

Tests the integration of option #5 (Suggerimenti Comandi) in:
- OptionsFormatter: Formatting methods for option display
- OptionsController: Navigation and modification of option #5
"""

import pytest
from src.presentation.options_formatter import OptionsFormatter
from src.application.options_controller import OptionsWindowController
from src.domain.services.game_settings import GameSettings, GameState

pytestmark = pytest.mark.gui


class TestOptionsFormatterCommandHints:
    """Test OptionsFormatter methods for command hints option."""
    
    def test_option_names_includes_command_hints(self):
        """OPTION_NAMES should include 'Suggerimenti Comandi' at index 4."""
        assert len(OptionsFormatter.OPTION_NAMES) == 5
        assert OptionsFormatter.OPTION_NAMES[4] == "Suggerimenti Comandi"
    
    def test_format_command_hints_item_current(self):
        """format_command_hints_item should format option with position and hint."""
        result = OptionsFormatter.format_command_hints_item("Attivi", True)
        
        assert "5 di 5" in result
        assert "Suggerimenti Comandi" in result
        assert "Attivi" in result
        assert "INVIO" in result or "invio" in result.lower()
    
    def test_format_command_hints_item_not_current(self):
        """format_command_hints_item without hint when not current."""
        result = OptionsFormatter.format_command_hints_item("Disattivati", False)
        
        assert "5 di 5" in result
        assert "Suggerimenti Comandi" in result
        assert "Disattivati" in result
    
    def test_format_command_hints_changed_enabled(self):
        """format_command_hints_changed should format enable message."""
        result = OptionsFormatter.format_command_hints_changed("Attivi")
        
        assert "suggerimenti comandi" in result.lower()
        assert "attivi" in result.lower()
    
    def test_format_command_hints_changed_disabled(self):
        """format_command_hints_changed should format disable message."""
        result = OptionsFormatter.format_command_hints_changed("Disattivati")
        
        assert "suggerimenti comandi" in result.lower()
        assert "disattivati" in result.lower()
    
    def test_format_option_item_handles_option_5(self):
        """format_option_item should handle option #5 (index 4)."""
        result = OptionsFormatter.format_option_item(4, "Suggerimenti Comandi", "Attivi", True)
        
        assert "5 di 5" in result
        assert "Suggerimenti Comandi" in result
        assert "Attivi" in result
        assert "invio" in result.lower()


class TestOptionsControllerCommandHints:
    """Test OptionsController integration with command hints."""
    
    @pytest.fixture
    def setup_controller(self):
        """Create controller with game settings."""
        game_state = GameState()
        game_state.is_running = False
        settings = GameSettings(game_state=game_state)
        controller = OptionsWindowController(settings)
        return controller, settings
    
    def test_navigate_to_option_5(self, setup_controller):
        """Should be able to navigate to option #5."""
        controller, settings = setup_controller
        controller.open_window()
        
        # Navigate to option 5 (index 4)
        result = controller.jump_to_option(4)
        
        assert "5 di 5" in result
        assert "Suggerimenti Comandi" in result
        assert controller.cursor_position == 4
    
    def test_format_current_option_5(self, setup_controller):
        """Should format option #5 with current value."""
        controller, settings = setup_controller
        controller.open_window()
        controller.cursor_position = 4
        
        result = controller._format_current_option(include_hint=True)
        
        assert "Suggerimenti Comandi" in result
        # Default is enabled
        assert "Attivi" in result or "Disattivati" in result
    
    def test_modify_command_hints_toggle(self, setup_controller):
        """Should toggle command hints when modifying option #5."""
        controller, settings = setup_controller
        controller.open_window()
        controller.cursor_position = 4
        
        initial_state = settings.command_hints_enabled
        
        result = controller.modify_current_option()
        
        assert settings.command_hints_enabled != initial_state
        assert "suggerimenti comandi" in result.lower()
        assert controller.state == "OPEN_DIRTY"
    
    def test_read_all_settings_includes_command_hints(self, setup_controller):
        """read_all_settings should include command hints."""
        controller, settings = setup_controller
        controller.open_window()
        
        result = controller.read_all_settings()
        
        assert "Suggerimenti comandi" in result or "suggerimenti" in result.lower()
    
    def test_snapshot_includes_command_hints(self, setup_controller):
        """Settings snapshot should include command_hints_enabled."""
        controller, settings = setup_controller
        settings.command_hints_enabled = False
        
        controller.open_window()  # This saves snapshot
        
        assert "command_hints" in controller.original_settings
        assert controller.original_settings["command_hints"] is False
    
    def test_restore_snapshot_restores_command_hints(self, setup_controller):
        """Restoring snapshot should restore command hints setting."""
        controller, settings = setup_controller
        settings.command_hints_enabled = True
        
        controller.open_window()  # Save snapshot
        
        # Modify setting
        settings.command_hints_enabled = False
        
        # Restore
        controller._restore_snapshot()
        
        assert settings.command_hints_enabled is True
    
    def test_modify_blocked_during_game(self, setup_controller):
        """Should not modify command hints during active game."""
        controller, settings = setup_controller
        settings.game_state.is_running = True
        
        controller.open_window()
        controller.cursor_position = 4
        
        result = controller.modify_current_option()
        
        assert "durante una partita" in result.lower()
    
    def test_full_cycle_open_modify_save(self, setup_controller):
        """Full workflow: open, navigate to option 5, modify, save."""
        controller, settings = setup_controller
        
        # Open window
        open_msg = controller.open_window()
        assert controller.is_open
        
        # Navigate to option 5
        nav_msg = controller.jump_to_option(4)
        assert controller.cursor_position == 4
        
        # Modify (toggle)
        initial = settings.command_hints_enabled
        modify_msg = controller.modify_current_option()
        assert settings.command_hints_enabled != initial
        assert controller.state == "OPEN_DIRTY"
        
        # Save and close
        close_msg = controller.save_and_close()
        assert not controller.is_open
        assert controller.state == "CLOSED"


class TestOptionsIntegration:
    """Integration tests for options system."""
    
    def test_option_5_persists_across_toggle(self):
        """Command hints setting should persist across toggles."""
        settings = GameSettings()
        
        # Start enabled (default)
        assert settings.command_hints_enabled is True
        
        # Toggle off
        success, msg = settings.toggle_command_hints()
        assert success
        assert settings.command_hints_enabled is False
        
        # Toggle back on
        success, msg = settings.toggle_command_hints()
        assert success
        assert settings.command_hints_enabled is True
    
    def test_formatter_and_controller_consistency(self):
        """Formatter and controller should use consistent values."""
        settings = GameSettings()
        controller = OptionsWindowController(settings)
        
        # Enable hints
        settings.command_hints_enabled = True
        display = settings.get_command_hints_display()
        assert display == "Attivi"
        
        # Format with formatter
        formatted = OptionsFormatter.format_command_hints_item(display, True)
        assert "Attivi" in formatted
        
        # Controller should use same value
        controller.open_window()
        controller.cursor_position = 4
        controller_formatted = controller._format_current_option(True)
        assert "Attivi" in controller_formatted
