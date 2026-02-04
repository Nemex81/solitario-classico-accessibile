"""Unit tests for Pile model."""

import pytest

from src.domain.models.card import Card, Rank, Suit
from src.domain.models.pile import (
    Pile,
    PileType,
    create_foundation_pile,
    create_stock_pile,
    create_tableau_pile,
    create_waste_pile,
)


class TestPile:
    """Test suite for Pile model."""

    def test_empty_pile(self) -> None:
        """Test empty pile creation."""
        pile = Pile(PileType.FOUNDATION)
        assert len(pile.cards) == 0
        assert pile.top_card() is None

    def test_top_card(self) -> None:
        """Test getting top card."""
        pile = Pile(PileType.FOUNDATION, ("AH", "2H"))
        top = pile.top_card()
        assert top is not None
        assert top.rank == Rank.TWO
        assert top.suit == Suit.HEARTS

    def test_add_card(self) -> None:
        """Test adding card to pile."""
        pile = Pile(PileType.FOUNDATION, ("AH",))
        card = Card(Rank.TWO, Suit.HEARTS)
        new_pile = pile.add_card(card)

        assert len(new_pile.cards) == 2
        assert new_pile.cards[-1] == "2♥"
        assert len(pile.cards) == 1  # Original unchanged

    def test_remove_top(self) -> None:
        """Test removing top cards."""
        pile = Pile(PileType.TABLEAU, ("AH", "2D", "3C"))
        new_pile = pile.remove_top(2)

        assert len(new_pile.cards) == 1
        assert new_pile.cards[0] == "AH"

    def test_tableau_visible_cards(self) -> None:
        """Test getting visible cards from tableau."""
        pile = create_tableau_pile(("KH", "QD", "JC", "10S"), face_down_count=2)
        visible = pile.visible_cards()

        assert len(visible) == 2
        assert visible[0].rank == Rank.JACK
        assert visible[1].rank == Rank.TEN

    def test_flip_top_card(self) -> None:
        """Test flipping face-down card."""
        pile = create_tableau_pile(("KH", "QD", "JC"), face_down_count=2)
        flipped = pile.flip_top_card()

        assert flipped.face_down_count == 1
        assert pile.face_down_count == 2  # Original unchanged

    def test_factory_functions(self) -> None:
        """Test pile factory functions."""
        tableau = create_tableau_pile(("KH",), 0)
        foundation = create_foundation_pile(("AH",))
        stock = create_stock_pile(("KH", "QD"))
        waste = create_waste_pile()

        assert tableau.pile_type == PileType.TABLEAU
        assert foundation.pile_type == PileType.FOUNDATION
        assert stock.pile_type == PileType.STOCK
        assert waste.pile_type == PileType.WASTE
