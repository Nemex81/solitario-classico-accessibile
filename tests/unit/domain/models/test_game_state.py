"""Unit tests for GameState model."""
import pytest

from src.domain.models.game_state import GameState, GameStatus


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
