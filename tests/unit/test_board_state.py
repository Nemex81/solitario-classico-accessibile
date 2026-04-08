"""Unit tests for board_state.py — BoardState DTO and CardView.

Tests cover:
- CardView construction and immutability (frozen=True)
- BoardState default construction (13 empty piles)
- BoardState construction with explicit data
- Behaviour with selection active / inactive
- Type correctness for all fields
"""

from __future__ import annotations

import pytest

from src.application.board_state import BoardState, CardView


# ---------------------------------------------------------------------------
# CardView tests
# ---------------------------------------------------------------------------


class TestCardView:
    """Tests for the CardView frozen dataclass."""

    def test_construction_basic(self) -> None:
        card = CardView(rank="A", suit="cuori", face_up=True, suit_color="red")
        assert card.rank == "A"
        assert card.suit == "cuori"
        assert card.face_up is True
        assert card.suit_color == "red"

    def test_construction_face_down(self) -> None:
        card = CardView(rank="K", suit="picche", face_up=False, suit_color="black")
        assert card.face_up is False
        assert card.suit_color == "black"

    def test_all_ranks(self) -> None:
        ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        for rank in ranks:
            card = CardView(rank=rank, suit="fiori", face_up=True, suit_color="black")
            assert card.rank == rank

    def test_all_suits(self) -> None:
        suits_colors = [
            ("cuori", "red"),
            ("quadri", "red"),
            ("fiori", "black"),
            ("picche", "black"),
        ]
        for suit, color in suits_colors:
            card = CardView(rank="5", suit=suit, face_up=True, suit_color=color)
            assert card.suit == suit
            assert card.suit_color == color

    def test_frozen_immutable(self) -> None:
        card = CardView(rank="7", suit="quadri", face_up=True, suit_color="red")
        with pytest.raises((AttributeError, TypeError)):
            card.rank = "8"  # type: ignore[misc]

    def test_equality(self) -> None:
        c1 = CardView(rank="Q", suit="cuori", face_up=True, suit_color="red")
        c2 = CardView(rank="Q", suit="cuori", face_up=True, suit_color="red")
        assert c1 == c2

    def test_inequality_different_rank(self) -> None:
        c1 = CardView(rank="Q", suit="cuori", face_up=True, suit_color="red")
        c2 = CardView(rank="K", suit="cuori", face_up=True, suit_color="red")
        assert c1 != c2

    def test_hashable(self) -> None:
        card = CardView(rank="J", suit="picche", face_up=True, suit_color="black")
        s: set[CardView] = {card}
        assert card in s


# ---------------------------------------------------------------------------
# BoardState tests
# ---------------------------------------------------------------------------


class TestBoardState:
    """Tests for the BoardState mutable dataclass."""

    def test_default_construction_13_empty_piles(self) -> None:
        bs = BoardState()
        assert len(bs.piles) == 13
        for pile in bs.piles:
            assert pile == []

    def test_default_cursor_values(self) -> None:
        bs = BoardState()
        assert bs.cursor_pile_idx == 0
        assert bs.cursor_card_idx == 0

    def test_default_selection_inactive(self) -> None:
        bs = BoardState()
        assert bs.selection_active is False
        assert bs.selected_pile_idx is None
        assert bs.selected_cards is None

    def test_default_game_over_false(self) -> None:
        bs = BoardState()
        assert bs.game_over is False

    def test_set_cursor(self) -> None:
        bs = BoardState()
        bs.cursor_pile_idx = 5
        bs.cursor_card_idx = 2
        assert bs.cursor_pile_idx == 5
        assert bs.cursor_card_idx == 2

    def test_piles_independent_instances(self) -> None:
        """Each BoardState must have its own list of piles (no shared state)."""
        bs1 = BoardState()
        bs2 = BoardState()
        bs1.piles[0].append(CardView(rank="A", suit="cuori", face_up=True, suit_color="red"))
        assert bs2.piles[0] == []

    def test_add_cards_to_pile(self) -> None:
        bs = BoardState()
        card = CardView(rank="10", suit="quadri", face_up=True, suit_color="red")
        bs.piles[0].append(card)
        assert len(bs.piles[0]) == 1
        assert bs.piles[0][0] == card

    def test_selection_active(self) -> None:
        card = CardView(rank="3", suit="fiori", face_up=True, suit_color="black")
        bs = BoardState(
            selection_active=True,
            selected_pile_idx=2,
            selected_cards=[card],
        )
        assert bs.selection_active is True
        assert bs.selected_pile_idx == 2
        assert bs.selected_cards is not None
        assert len(bs.selected_cards) == 1
        assert bs.selected_cards[0] == card

    def test_game_over_flag(self) -> None:
        bs = BoardState(game_over=True)
        assert bs.game_over is True

    def test_pile_indices_convention(self) -> None:
        """Verify pile index access for all 13 standard piles."""
        bs = BoardState()
        # Tableau 0-6
        for i in range(7):
            assert isinstance(bs.piles[i], list)
        # Foundation 7-10
        for i in range(7, 11):
            assert isinstance(bs.piles[i], list)
        # Waste = 11, Stock = 12
        assert isinstance(bs.piles[11], list)
        assert isinstance(bs.piles[12], list)

    def test_full_board_construction(self) -> None:
        """Construct a realistic minimal board state and verify accessors."""
        ace = CardView(rank="A", suit="picche", face_up=True, suit_color="black")
        two = CardView(rank="2", suit="cuori", face_up=True, suit_color="red")
        hidden = CardView(rank="K", suit="quadri", face_up=False, suit_color="red")

        piles: list[list[CardView]] = [[] for _ in range(13)]
        piles[0] = [hidden, two]   # tableau pile 0: hidden underneath, 2 on top
        piles[7] = [ace]           # foundation 0: ace of spades

        bs = BoardState(
            piles=piles,
            cursor_pile_idx=0,
            cursor_card_idx=1,
            selection_active=False,
            game_over=False,
        )

        assert bs.piles[0][1] == two
        assert bs.piles[7][0] == ace
        assert bs.piles[0][0].face_up is False
        assert bs.cursor_pile_idx == 0
        assert bs.cursor_card_idx == 1
