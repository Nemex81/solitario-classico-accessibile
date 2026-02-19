"""Unit tests for GameController."""

import pytest

from src.application.game_controller import GameController
from src.domain.models.game_state import GameConfiguration, GameState, GameStatus
from src.domain.rules.move_validator import MoveValidator
from src.domain.services.game_service import GameService
from src.presentation.game_formatter import GameFormatter

pytestmark = pytest.mark.gui


class TestGameController:
    """Test suite for GameController."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.validator = MoveValidator()
        self.game_service = GameService(self.validator)
        self.formatter = GameFormatter(language="it")
        self.controller = GameController(self.game_service, self.formatter)

    def test_init_no_current_state(self) -> None:
        """Test controller initializes with no current state."""
        assert self.controller.current_state is None

    def test_start_new_game(self) -> None:
        """Test starting a new game."""
        result = self.controller.start_new_game()

        assert self.controller.current_state is not None
        assert self.controller.current_state.status == GameStatus.IN_PROGRESS
        assert "Stato: In corso" in result
        assert "TABLEAU" in result

    def test_start_new_game_with_config(self) -> None:
        """Test starting a new game with custom configuration."""
        result = self.controller.start_new_game(difficulty="hard", deck_type="french")

        assert self.controller.current_state is not None
        assert self.controller.current_state.config.difficulty == "hard"
        assert self.controller.current_state.config.deck_type == "french"

    def test_execute_move_no_game_started(self) -> None:
        """Test execute move when no game is started."""
        success, message = self.controller.execute_move("draw")

        assert success is False
        assert "Nessuna partita in corso" in message

    def test_execute_move_draw(self) -> None:
        """Test draw action from stock."""
        self.controller.start_new_game()
        initial_stock = len(self.controller.current_state.stock)

        success, message = self.controller.execute_move("draw")

        assert success is True
        assert "Carte pescate dal mazzo" in message
        assert len(self.controller.current_state.stock) < initial_stock

    def test_execute_move_unknown_action(self) -> None:
        """Test unknown action returns failure."""
        self.controller.start_new_game()

        success, message = self.controller.execute_move("unknown_action")

        assert success is False
        assert "Azione sconosciuta" in message

    def test_execute_move_invalid_move(self) -> None:
        """Test invalid move returns failure with error message."""
        self.controller.start_new_game()
        # Try to move to foundation from empty waste
        self.controller.current_state = self.controller.current_state.with_move(waste=())

        success, message = self.controller.execute_move(
            "move_to_foundation",
            source_pile="waste",
            source_index=0,
            target_index=0,
        )

        assert success is False
        assert len(message) > 0

    def test_execute_move_recycle_success(self) -> None:
        """Test recycle waste to stock."""
        self.controller.start_new_game()
        # Draw all cards from stock first
        while self.controller.current_state.stock:
            self.controller.execute_move("draw")

        success, message = self.controller.execute_move("recycle")

        assert success is True
        assert "Scarti rimescolati nel mazzo" in message

    def test_execute_move_recycle_failure(self) -> None:
        """Test recycle fails when stock is not empty."""
        self.controller.start_new_game()

        success, message = self.controller.execute_move("recycle")

        assert success is False

    def test_get_current_state_formatted_no_game(self) -> None:
        """Test get formatted state when no game is started."""
        result = self.controller.get_current_state_formatted()

        assert "Nessuna partita in corso" in result

    def test_get_current_state_formatted_with_game(self) -> None:
        """Test get formatted state with active game."""
        self.controller.start_new_game()

        result = self.controller.get_current_state_formatted()

        assert "Stato: In corso" in result
        assert "TABLEAU" in result
        assert "BASI" in result

    def test_get_cursor_position_formatted_no_game(self) -> None:
        """Test get cursor position when no game is started."""
        result = self.controller.get_cursor_position_formatted()

        assert "Nessuna partita in corso" in result

    def test_get_cursor_position_formatted_with_game(self) -> None:
        """Test get cursor position with active game."""
        self.controller.start_new_game()

        result = self.controller.get_cursor_position_formatted()

        # Default cursor is on tableau 0
        assert "Tableau 1" in result
