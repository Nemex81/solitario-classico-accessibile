"""Integration tests for complete game flow."""

import pytest

from src.application.commands import CommandHistory, DrawCommand, MoveCommand
from src.application.game_controller import GameController
from src.domain.models.card import Card, Rank, Suit
from src.domain.models.game_state import (
    GameConfiguration,
    GameState,
    GameStatus,
)
from src.domain.rules.move_validator import MoveValidator
from src.domain.services.game_service import GameService
from src.infrastructure.di_container import DIContainer
from src.presentation.game_formatter import GameFormatter


class TestGameFlowIntegration:
    """Integration tests for complete game flow."""

    def setup_method(self) -> None:
        """Set up test fixtures using DI container."""
        self.container = DIContainer()
        self.controller = self.container.get_game_controller()
        self.game_service = self.container.get_game_service()
        self.formatter = self.container.get_formatter()

    def test_complete_game_initialization(self) -> None:
        """Test complete game initialization through all layers."""
        # Start game through controller
        result = self.controller.start_new_game()

        # Verify state through all layers
        assert self.controller.current_state is not None
        assert self.controller.current_state.status == GameStatus.IN_PROGRESS

        # Verify formatted output
        assert "Stato: In corso" in result
        assert "TABLEAU" in result
        assert "BASI" in result

    def test_game_service_validator_integration(self) -> None:
        """Test GameService and MoveValidator work together."""
        config = GameConfiguration()
        state = self.game_service.new_game(config)

        # Verify initial state is valid
        assert len(state.tableaus) == 7
        assert len(state.foundations) == 4
        assert state.status == GameStatus.IN_PROGRESS

        # Verify stock has cards
        assert len(state.stock) > 0

        # Draw from stock
        new_state = self.game_service.draw_from_stock(state)
        assert len(new_state.waste) > 0
        assert new_state.moves_count == 1

    def test_draw_and_recycle_cycle(self) -> None:
        """Test drawing all cards and recycling waste."""
        self.controller.start_new_game()
        initial_stock_count = len(self.controller.current_state.stock)

        # Draw until stock is empty
        draw_count = 0
        while self.controller.current_state.stock:
            success, _ = self.controller.execute_move("draw")
            assert success is True
            draw_count += 1

        # Verify all cards are in waste
        assert len(self.controller.current_state.stock) == 0
        assert len(self.controller.current_state.waste) == initial_stock_count

        # Recycle waste
        success, message = self.controller.execute_move("recycle")
        assert success is True
        assert "Scarti rimescolati" in message

        # Verify cards are back in stock
        assert len(self.controller.current_state.stock) == initial_stock_count
        assert len(self.controller.current_state.waste) == 0

    def test_controller_formatter_integration(self) -> None:
        """Test GameController uses formatter correctly."""
        self.controller.start_new_game()

        # Get formatted state
        state_output = self.controller.get_current_state_formatted()
        cursor_output = self.controller.get_cursor_position_formatted()

        # Verify formatting
        assert "Stato: In corso" in state_output
        assert "Mosse: 0" in state_output
        assert "Tableau" in cursor_output

    def test_di_container_provides_working_components(self) -> None:
        """Test DI container provides fully functional components."""
        container = DIContainer()

        # Get all components
        validator = container.get_move_validator()
        service = container.get_game_service()
        formatter = container.get_formatter()
        controller = container.get_game_controller()

        # Verify they work together
        result = controller.start_new_game()
        assert "In corso" in result

        # Verify service uses validator
        state = controller.current_state
        assert service.validator is validator

        # Verify controller uses service and formatter
        assert controller.game_service is service
        assert controller.formatter is formatter


class TestMoveValidationIntegration:
    """Integration tests for move validation."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.validator = MoveValidator()
        self.game_service = GameService(self.validator)

    def test_foundation_move_validation_flow(self) -> None:
        """Test foundation move validation through service."""
        # Create state with Ace in tableau
        state = GameState(
            status=GameStatus.IN_PROGRESS,
            tableaus=(("AH",), (), (), (), (), (), ()),
            foundations=((), (), (), ()),
        )

        # Validate and execute move
        card = Card(Rank.ACE, Suit.HEARTS)
        can_move = self.validator.can_move_to_foundation(card, 0, state)
        assert can_move is True

        # Execute through service
        new_state = self.game_service.move_to_foundation(state, "tableau", 0, 0)
        assert len(new_state.foundations[0]) == 1
        assert new_state.foundations[0][0] == "AH"
        assert len(new_state.tableaus[0]) == 0

    def test_tableau_move_validation_flow(self) -> None:
        """Test tableau move validation."""
        # Create state with King ready to move to empty tableau
        state = GameState(
            status=GameStatus.IN_PROGRESS,
            tableaus=(("KH",), (), (), (), (), (), ()),
            foundations=((), (), (), ()),
        )

        # Validate King can move to empty tableau
        king = Card(Rank.KING, Suit.HEARTS)
        can_move = self.validator.can_move_to_tableau((king,), 1, state)
        assert can_move is True


class TestCommandHistoryIntegration:
    """Integration tests for command history with game state."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.history = CommandHistory()
        self.validator = MoveValidator()
        self.game_service = GameService(self.validator)

    def test_undo_preserves_state(self) -> None:
        """Test undo restores previous game state."""
        # Create initial state
        config = GameConfiguration()
        initial_state = self.game_service.new_game(config)
        initial_stock_count = len(initial_state.stock)

        # Execute draw command
        command = DrawCommand()
        self.history.execute(command, initial_state)

        # Draw actually changes state
        new_state = self.game_service.draw_from_stock(initial_state)
        assert len(new_state.stock) < initial_stock_count

        # Undo returns to initial state
        restored_state = self.history.undo(new_state)
        assert restored_state is initial_state

    def test_multiple_commands_undo_redo(self) -> None:
        """Test undo/redo with multiple commands."""
        config = GameConfiguration()
        state = self.game_service.new_game(config)

        # Execute multiple draws
        states = [state]
        for i in range(3):
            command = DrawCommand()
            current_state = self.history.execute(command, states[-1])
            states.append(self.game_service.draw_from_stock(states[-1]))

        # Undo all
        for i in range(3):
            assert self.history.can_undo() is True
            self.history.undo(states[-1])

        # Redo all
        for i in range(3):
            assert self.history.can_redo() is True
            self.history.redo(states[0])


class TestFormatterIntegration:
    """Integration tests for formatter with game state."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.formatter = GameFormatter(language="it")
        self.validator = MoveValidator()
        self.game_service = GameService(self.validator)

    def test_format_new_game_state(self) -> None:
        """Test formatting newly started game."""
        config = GameConfiguration()
        state = self.game_service.new_game(config)

        output = self.formatter.format_game_state(state)

        # Verify all sections present
        assert "Stato: In corso" in output
        assert "Mosse: 0" in output
        assert "Punteggio: 0" in output
        assert "BASI (Foundation)" in output
        assert "TABLEAU" in output
        assert "Mazzo (Stock)" in output
        assert "Scarti (Waste)" in output

    def test_format_after_moves(self) -> None:
        """Test formatting after making moves."""
        config = GameConfiguration()
        state = self.game_service.new_game(config)

        # Draw some cards
        state = self.game_service.draw_from_stock(state)
        state = self.game_service.draw_from_stock(state)

        output = self.formatter.format_game_state(state)

        assert "Mosse: 2" in output
        assert "Scarti (Waste)" in output

    def test_format_cursor_navigation(self) -> None:
        """Test cursor position formatting."""
        config = GameConfiguration()
        state = self.game_service.new_game(config)

        # Default cursor is on tableau 0
        cursor_output = self.formatter.format_cursor_position(state)
        assert "Tableau 1" in cursor_output

    def test_format_move_results(self) -> None:
        """Test move result formatting."""
        success_output = self.formatter.format_move_result(True, "Carta spostata")
        failure_output = self.formatter.format_move_result(False, "Mossa non valida")

        assert "✓" in success_output
        assert "Carta spostata" in success_output
        assert "✗" in failure_output
        assert "Mossa non valida" in failure_output
