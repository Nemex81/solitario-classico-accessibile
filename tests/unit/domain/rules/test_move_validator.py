"""Unit tests for MoveValidator."""

import pytest

from src.domain.models.card import Card, Rank, Suit
from src.domain.models.game_state import GameState
from src.domain.rules.move_validator import MoveValidator


class TestMoveValidator:
    """Test suite for MoveValidator."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.validator = MoveValidator()

    def test_can_move_ace_to_empty_foundation(self) -> None:
        """Test Ace can move to empty foundation."""
        state = GameState()
        ace = Card(rank=Rank.ACE, suit=Suit.HEARTS)

        assert self.validator.can_move_to_foundation(ace, 0, state)

    def test_cannot_move_non_ace_to_empty_foundation(self) -> None:
        """Test non-Ace cannot move to empty foundation."""
        state = GameState()
        two = Card(rank=Rank.TWO, suit=Suit.HEARTS)

        assert not self.validator.can_move_to_foundation(two, 0, state)

    def test_can_move_sequential_to_foundation(self) -> None:
        """Test sequential card can move to foundation."""
        state = GameState(foundations=(("AH",), (), (), ()))
        two = Card(rank=Rank.TWO, suit=Suit.HEARTS)

        assert self.validator.can_move_to_foundation(two, 0, state)

    def test_cannot_move_wrong_suit_to_foundation(self) -> None:
        """Test wrong suit cannot move to foundation."""
        state = GameState(foundations=(("AH",), (), (), ()))
        two_spades = Card(rank=Rank.TWO, suit=Suit.SPADES)

        assert not self.validator.can_move_to_foundation(two_spades, 0, state)

    def test_can_move_king_to_empty_tableau(self) -> None:
        """Test King can move to empty tableau."""
        state = GameState()
        king = Card(rank=Rank.KING, suit=Suit.SPADES)

        assert self.validator.can_move_to_tableau((king,), 0, state)

    def test_cannot_move_non_king_to_empty_tableau(self) -> None:
        """Test non-King cannot move to empty tableau."""
        state = GameState()
        queen = Card(rank=Rank.QUEEN, suit=Suit.SPADES)

        assert not self.validator.can_move_to_tableau((queen,), 0, state)

    def test_can_move_opposite_color_to_tableau(self) -> None:
        """Test opposite color card can move to tableau."""
        state = GameState(tableaus=(("7H",), (), (), (), (), (), ()))
        black_six = Card(rank=Rank.SIX, suit=Suit.SPADES)

        assert self.validator.can_move_to_tableau((black_six,), 0, state)

    def test_cannot_move_same_color_to_tableau(self) -> None:
        """Test same color card cannot move to tableau."""
        state = GameState(tableaus=(("7H",), (), (), (), (), (), ()))
        red_six = Card(rank=Rank.SIX, suit=Suit.DIAMONDS)

        assert not self.validator.can_move_to_tableau((red_six,), 0, state)

    def test_can_draw_from_stock(self) -> None:
        """Test can draw when stock has cards."""
        state = GameState(stock=("AH", "2D", "3C"))

        assert self.validator.can_draw_from_stock(state)

    def test_cannot_draw_from_empty_stock(self) -> None:
        """Test cannot draw from empty stock."""
        state = GameState(stock=())

        assert not self.validator.can_draw_from_stock(state)

    def test_can_recycle_waste(self) -> None:
        """Test can recycle waste when stock empty."""
        state = GameState(stock=(), waste=("AH", "2D", "3C"))

        assert self.validator.can_recycle_waste(state)

    def test_cannot_recycle_when_stock_not_empty(self) -> None:
        """Test cannot recycle when stock has cards."""
        state = GameState(stock=("KS",), waste=("AH", "2D"))

        assert not self.validator.can_recycle_waste(state)
