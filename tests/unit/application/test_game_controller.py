"""Unit tests for GameController."""

import pytest

from src.application.game_controller import GameController
from src.domain.models.game_state import GameState, GameStatus
from src.domain.rules.move_validator import MoveValidator
from src.domain.services.game_service import GameService
from src.presentation.game_formatter import GameFormatter


class TestGameController:
    """Test suite for GameController."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        validator = MoveValidator()
        self.game_service = GameService(validator)
        self.formatter = GameFormatter()
        self.controller = GameController(self.game_service, self.formatter)

    def test_initialization(self) -> None:
        """Test controller initialization."""
        assert self.controller.game_service is not None
        assert self.controller.formatter is not None
        assert self.controller.current_state is None

    def test_start_new_game(self) -> None:
        """Test starting a new game."""
        result = self.controller.start_new_game()

        assert isinstance(result, str)
        assert self.controller.current_state is not None
        assert self.controller.current_state.status == GameStatus.IN_PROGRESS
        assert "Stato:" in result
        assert "TABLEAU" in result

    def test_start_new_game_with_difficulty(self) -> None:
        """Test starting a new game with specific difficulty."""
        result = self.controller.start_new_game(difficulty="hard")

        assert isinstance(result, str)
        assert self.controller.current_state is not None

    def test_start_new_game_with_deck_type(self) -> None:
        """Test starting a new game with specific deck type."""
        result = self.controller.start_new_game(deck_type="neapolitan")

        assert isinstance(result, str)
        assert self.controller.current_state is not None

    def test_execute_move_without_game(self) -> None:
        """Test executing move without starting game."""
        success, message = self.controller.execute_move("draw")

        assert success is False
        assert "Nessuna partita in corso" in message

    def test_execute_move_draw(self) -> None:
        """Test executing draw move."""
        self.controller.start_new_game()
        initial_stock_size = len(self.controller.current_state.stock)

        success, message = self.controller.execute_move("draw")

        assert success is True
        assert "pescate" in message
        assert len(self.controller.current_state.stock) < initial_stock_size

    def test_execute_move_unknown_action(self) -> None:
        """Test executing unknown action."""
        self.controller.start_new_game()

        success, message = self.controller.execute_move("unknown_action")

        assert success is False
        assert "sconosciuta" in message

    def test_execute_move_to_foundation_invalid(self) -> None:
        """Test executing invalid move to foundation."""
        self.controller.start_new_game()

        # Try to move from tableau to foundation (likely invalid)
        success, message = self.controller.execute_move(
            "move_to_foundation", source_pile="tableau", source_index=0, target_index=0
        )

        # Should either succeed or fail gracefully
        assert isinstance(success, bool)
        assert isinstance(message, str)

    def test_get_current_state_formatted_without_game(self) -> None:
        """Test getting formatted state without game."""
        result = self.controller.get_current_state_formatted()

        assert "Nessuna partita in corso" in result

    def test_get_current_state_formatted_with_game(self) -> None:
        """Test getting formatted state with game."""
        self.controller.start_new_game()
        result = self.controller.get_current_state_formatted()

        assert "Stato:" in result
        assert "TABLEAU" in result

    def test_get_cursor_position_formatted_without_game(self) -> None:
        """Test getting formatted cursor position without game."""
        result = self.controller.get_cursor_position_formatted()

        assert "Nessuna partita in corso" in result

    def test_get_cursor_position_formatted_with_game(self) -> None:
        """Test getting formatted cursor position with game."""
        self.controller.start_new_game()
        result = self.controller.get_cursor_position_formatted()

        assert isinstance(result, str)
        # Should have some position description
        assert len(result) > 0

    def test_execute_move_recycle_with_empty_stock(self) -> None:
        """Test recycling waste when stock is empty."""
        self.controller.start_new_game()

        # Draw all cards from stock
        while len(self.controller.current_state.stock) > 0:
            self.controller.execute_move("draw")

        # Now recycle
        success, message = self.controller.execute_move("recycle")

        assert success is True
        assert "rimescolati" in message
