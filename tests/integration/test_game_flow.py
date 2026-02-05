"""Integration tests for game flow."""

import pytest

from src.application.game_controller import GameController
from src.domain.models.game_state import GameStatus
from src.domain.rules.move_validator import MoveValidator
from src.domain.services.game_service import GameService
from src.infrastructure.di_container import DIContainer
from src.presentation.game_formatter import GameFormatter


class TestGameFlowIntegration:
    """Integration tests for complete game flow."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.container = DIContainer()
        self.controller = self.container.get_game_controller()

    def test_new_game_initialization(self) -> None:
        """Test complete new game initialization flow."""
        result = self.controller.start_new_game()

        # Verify game is initialized
        assert self.controller.current_state is not None
        assert self.controller.current_state.status == GameStatus.IN_PROGRESS
        assert len(self.controller.current_state.tableaus) == 7
        assert len(self.controller.current_state.foundations) == 4

        # Verify formatting works
        assert "Stato:" in result
        assert "TABLEAU" in result

    def test_draw_from_stock_flow(self) -> None:
        """Test complete draw from stock flow."""
        self.controller.start_new_game()
        initial_stock = len(self.controller.current_state.stock)

        success, message = self.controller.execute_move("draw")

        assert success is True
        assert len(self.controller.current_state.stock) < initial_stock
        assert len(self.controller.current_state.waste) > 0

    def test_multiple_draws(self) -> None:
        """Test multiple draw operations."""
        self.controller.start_new_game()

        # Draw multiple times
        for _ in range(3):
            if len(self.controller.current_state.stock) > 0:
                success, _ = self.controller.execute_move("draw")
                assert success is True

    def test_recycle_waste_flow(self) -> None:
        """Test complete recycle waste flow."""
        self.controller.start_new_game()

        # Draw all cards
        while len(self.controller.current_state.stock) > 0:
            self.controller.execute_move("draw")

        # Recycle
        success, message = self.controller.execute_move("recycle")

        assert success is True
        assert len(self.controller.current_state.stock) > 0
        assert len(self.controller.current_state.waste) == 0

    def test_formatter_integration(self) -> None:
        """Test formatter integration with game state."""
        self.controller.start_new_game()

        # Get formatted state
        formatted = self.controller.get_current_state_formatted()

        assert "Mosse:" in formatted
        assert "Punteggio:" in formatted
        assert "BASI" in formatted
        assert "TABLEAU" in formatted

    def test_cursor_position_formatting(self) -> None:
        """Test cursor position formatting integration."""
        self.controller.start_new_game()

        cursor_info = self.controller.get_cursor_position_formatted()

        assert isinstance(cursor_info, str)
        assert len(cursor_info) > 0

    def test_game_service_validator_integration(self) -> None:
        """Test integration between GameService and MoveValidator."""
        validator = self.container.get_move_validator()
        service = self.container.get_game_service()

        assert service.validator is validator

        # Create a new game
        from src.domain.models.game_state import GameConfiguration

        config = GameConfiguration()
        state = service.new_game(config)

        assert state.status == GameStatus.IN_PROGRESS
        assert len(state.tableaus) == 7

    def test_di_container_integration(self) -> None:
        """Test DI container provides consistent instances."""
        controller1 = self.container.get_game_controller()
        controller2 = self.container.get_game_controller()

        assert controller1 is controller2
        assert controller1.game_service is controller2.game_service

    def test_error_handling_flow(self) -> None:
        """Test error handling in complete flow."""
        # Try to execute move without game
        success, message = self.controller.execute_move("draw")

        assert success is False
        assert "Nessuna partita in corso" in message

    def test_unknown_action_handling(self) -> None:
        """Test handling of unknown actions."""
        self.controller.start_new_game()

        success, message = self.controller.execute_move("invalid_action")

        assert success is False
        assert "sconosciuta" in message


class TestEndToEndGameScenario:
    """End-to-end game scenario tests."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        validator = MoveValidator()
        service = GameService(validator)
        formatter = GameFormatter()
        self.controller = GameController(service, formatter)

    def test_complete_game_session(self) -> None:
        """Test a complete game session from start to multiple actions."""
        # Start game
        result = self.controller.start_new_game()
        assert "In corso" in result

        # Check initial state
        assert self.controller.current_state.moves_count == 0

        # Draw cards
        self.controller.execute_move("draw")
        assert self.controller.current_state.moves_count > 0

        # Draw more
        self.controller.execute_move("draw")
        moves_after_draw = self.controller.current_state.moves_count

        # Format state
        formatted = self.controller.get_current_state_formatted()
        assert f"Mosse: {moves_after_draw}" in formatted

    def test_game_state_persistence(self) -> None:
        """Test game state persists through operations."""
        self.controller.start_new_game()

        initial_state = self.controller.current_state
        initial_stock_size = len(initial_state.stock)

        # Perform action
        self.controller.execute_move("draw")

        # State should be updated
        assert self.controller.current_state is not initial_state
        assert len(self.controller.current_state.stock) < initial_stock_size

    def test_formatter_with_different_languages(self) -> None:
        """Test formatter works with different languages."""
        formatter_it = GameFormatter("it")
        formatter_en = GameFormatter("en")

        from src.domain.models.game_state import GameState

        state = GameState(moves_count=5)

        # Both should format without errors
        result_it = formatter_it.format_game_state(state)
        result_en = formatter_en.format_game_state(state)

        assert "Mosse: 5" in result_it
        # English formatter would have different text, but for now just verify it works
        assert isinstance(result_en, str)


class TestComponentIntegration:
    """Test integration between different components."""

    def test_validator_service_integration(self) -> None:
        """Test validator integrates correctly with service."""
        validator = MoveValidator()
        service = GameService(validator)

        from src.domain.models.game_state import GameConfiguration

        config = GameConfiguration(deck_type="french")
        state = service.new_game(config)

        # Verify deck was created correctly
        total_cards = sum(len(t) for t in state.tableaus) + len(state.stock) + len(state.waste)
        assert total_cards == 52  # Full French deck

    def test_formatter_handles_empty_state(self) -> None:
        """Test formatter handles empty game state."""
        formatter = GameFormatter()
        from src.domain.models.game_state import GameState

        empty_state = GameState()
        result = formatter.format_game_state(empty_state)

        assert "vuota" in result or "vuoto" in result.lower()

    def test_controller_state_transitions(self) -> None:
        """Test controller properly transitions game state."""
        validator = MoveValidator()
        service = GameService(validator)
        formatter = GameFormatter()
        controller = GameController(service, formatter)

        # Initial state - no game
        assert controller.current_state is None

        # After starting game
        controller.start_new_game()
        state_after_start = controller.current_state
        assert state_after_start is not None

        # After action
        controller.execute_move("draw")
        state_after_action = controller.current_state

        assert state_after_action is not state_after_start
        assert state_after_action.moves_count > state_after_start.moves_count
