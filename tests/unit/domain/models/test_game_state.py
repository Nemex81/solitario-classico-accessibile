"""Unit tests for GameState model."""

import pytest

from src.domain.models.game_state import (
    CursorPosition,
    GameConfiguration,
    GameState,
    GameStatus,
    SelectionState,
)


class TestGameState:
    """Test suite for GameState immutable model."""

    def test_default_initialization(self) -> None:
        """Test GameState initializes with correct defaults."""
        state = GameState()

        assert len(state.foundations) == 4
        assert all(len(f) == 0 for f in state.foundations)
        assert len(state.tableaus) == 7
        assert all(len(t) == 0 for t in state.tableaus)
        assert len(state.stock) == 0
        assert len(state.waste) == 0
        assert state.status == GameStatus.NOT_STARTED
        assert state.moves_count == 0
        assert state.score == 0

    def test_immutability(self) -> None:
        """Test that GameState is immutable."""
        state = GameState()

        with pytest.raises(AttributeError):
            state.score = 100  # type: ignore

    def test_with_move_updates_single_field(self) -> None:
        """Test with_move updates only specified fields."""
        state = GameState(score=50, moves_count=10)
        new_state = state.with_move(score=100)

        assert new_state.score == 100
        assert new_state.moves_count == 10  # unchanged
        assert state.score == 50  # original unchanged

    def test_with_move_creates_new_instance(self) -> None:
        """Test with_move creates a new GameState instance."""
        state = GameState()
        new_state = state.with_move(moves_count=1)

        assert state is not new_state
        assert state.moves_count == 0
        assert new_state.moves_count == 1

    def test_is_victory_empty_foundations(self) -> None:
        """Test is_victory returns False for empty foundations."""
        state = GameState()
        assert not state.is_victory()

    def test_is_victory_partial_foundations(self) -> None:
        """Test is_victory returns False for partially filled foundations."""
        state = GameState(foundations=(("AH", "2H", "3H"), ("AS", "2S"), (), ()))
        assert not state.is_victory()

    def test_is_victory_complete_foundations(self) -> None:
        """Test is_victory returns True when all foundations complete."""
        complete_suit = tuple(
            f"{rank}{suit}"
            for rank in [
                "A",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9",
                "10",
                "J",
                "Q",
                "K",
            ]
            for suit in ["H"]
        )

        state = GameState(
            foundations=(
                complete_suit[:13],
                complete_suit[:13],
                complete_suit[:13],
                complete_suit[:13],
            )
        )
        assert state.is_victory()

    def test_cursor_position(self) -> None:
        """Test cursor position tracking."""
        cursor = CursorPosition("tableau", 2, 5)
        state = GameState(cursor=cursor)
        assert state.cursor.pile_type == "tableau"
        assert state.cursor.pile_index == 2
        assert state.cursor.card_index == 5

    def test_selection_state(self) -> None:
        """Test card selection tracking."""
        selection = SelectionState("tableau", 0, (3, 4, 5))
        state = GameState(selection=selection)
        assert state.selection.source_pile_type == "tableau"
        assert state.selection.source_pile_index == 0
        assert len(state.selection.selected_card_indices) == 3

    def test_game_configuration(self) -> None:
        """Test game configuration."""
        config = GameConfiguration(difficulty="hard", deck_type="neapolitan", draw_count=1)
        state = GameState(config=config)
        assert state.config.difficulty == "hard"
        assert state.config.deck_type == "neapolitan"
        assert state.config.draw_count == 1

    def test_with_cursor(self) -> None:
        """Test with_cursor helper method."""
        state = GameState()
        new_cursor = CursorPosition("foundation", 3)
        new_state = state.with_cursor(new_cursor)
        assert new_state.cursor.pile_type == "foundation"
        assert new_state.cursor.pile_index == 3

    def test_with_selection(self) -> None:
        """Test with_selection helper method."""
        state = GameState()
        new_selection = SelectionState("waste", 0, (1, 2))
        new_state = state.with_selection(new_selection)
        assert new_state.selection.source_pile_type == "waste"
        assert len(new_state.selection.selected_card_indices) == 2

    def test_elapsed_seconds(self) -> None:
        """Test elapsed time tracking."""
        state = GameState(elapsed_seconds=120)
        assert state.elapsed_seconds == 120
        new_state = state.with_move(elapsed_seconds=180)
        assert new_state.elapsed_seconds == 180
        assert state.elapsed_seconds == 120  # Original unchanged
