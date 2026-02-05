"""Unit tests for GameFormatter."""

import pytest

from src.domain.models.game_state import CursorPosition, GameState, GameStatus
from src.presentation.game_formatter import GameFormatter


class TestGameFormatter:
    """Test suite for GameFormatter."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.formatter = GameFormatter(language="it")

    def test_format_game_state(self) -> None:
        """Test formatting complete game state."""
        state = GameState(
            status=GameStatus.IN_PROGRESS,
            moves_count=10,
            score=50,
            foundations=(("AH",), (), (), ()),
            tableaus=(("KS", "QD"), (), (), (), (), (), ()),
        )

        output = self.formatter.format_game_state(state)

        assert "Mosse: 10" in output
        assert "Punteggio: 50" in output
        assert "Base Cuori" in output
        assert "TABLEAU" in output

    def test_format_cursor_position_tableau(self) -> None:
        """Test formatting cursor on tableau."""
        state = GameState(
            tableaus=(("KH", "QD", "JC"), (), (), (), (), (), ()),
            cursor=CursorPosition("tableau", 0, 1),
        )

        output = self.formatter.format_cursor_position(state)

        assert "Tableau 1" in output
        assert "carta 2" in output

    def test_format_cursor_position_empty_pile(self) -> None:
        """Test formatting cursor on empty pile."""
        state = GameState(cursor=CursorPosition("tableau", 0, 0))

        output = self.formatter.format_cursor_position(state)

        assert "vuoto" in output

    def test_format_move_result_success(self) -> None:
        """Test formatting successful move."""
        output = self.formatter.format_move_result(True, "Carta spostata")
        assert "✓" in output
        assert "Carta spostata" in output

    def test_format_move_result_failure(self) -> None:
        """Test formatting failed move."""
        output = self.formatter.format_move_result(False, "Mossa non valida")
        assert "✗" in output
        assert "Mossa non valida" in output

    def test_format_card_list(self) -> None:
        """Test formatting card list."""
        cards = ["AH", "2D", "3C"]
        output = self.formatter.format_card_list(cards)
        assert "AH, 2D, 3C" == output

    def test_format_empty_card_list(self) -> None:
        """Test formatting empty card list."""
        output = self.formatter.format_card_list([])
        assert "nessuna carta" == output

    def test_format_cursor_position_foundation(self) -> None:
        """Test formatting cursor on foundation."""
        state = GameState(
            foundations=(("AH", "2H"), (), (), ()),
            cursor=CursorPosition("foundation", 0, 0),
        )

        output = self.formatter.format_cursor_position(state)

        assert "Base 1" in output
        assert "2H" in output

    def test_format_cursor_position_stock(self) -> None:
        """Test formatting cursor on stock."""
        state = GameState(stock=("KH", "QD", "JC"), cursor=CursorPosition("stock", 0, 0))

        output = self.formatter.format_cursor_position(state)

        assert "Mazzo" in output
        assert "3 carte" in output

    def test_format_cursor_position_waste(self) -> None:
        """Test formatting cursor on waste."""
        state = GameState(waste=("KH", "QD"), cursor=CursorPosition("waste", 0, 0))

        output = self.formatter.format_cursor_position(state)

        assert "Scarti" in output
        assert "QD" in output

    def test_format_game_state_with_victory(self) -> None:
        """Test formatting game state when won."""
        state = GameState(
            status=GameStatus.WON,
            moves_count=150,
            score=500,
            foundations=(
                tuple(
                    f"{r}H"
                    for r in ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
                ),
                tuple(
                    f"{r}D"
                    for r in ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
                ),
                tuple(
                    f"{r}C"
                    for r in ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
                ),
                tuple(
                    f"{r}S"
                    for r in ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
                ),
            ),
        )

        output = self.formatter.format_game_state(state)

        assert "Vinto!" in output
        assert "13 carte" in output
