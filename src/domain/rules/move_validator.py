"""Move validation rules for Klondike solitaire."""

from typing import Tuple

from src.domain.models.card import Card
from src.domain.models.game_state import GameState


class MoveValidator:
    """
    Validates game moves according to Klondike solitaire rules.

    This class is responsible for checking if a specific move is legal
    according to the game rules. It does not modify game state.
    """

    def can_move_to_foundation(
        self,
        card: Card,
        foundation_index: int,
        state: GameState,
    ) -> bool:
        """
        Check if card can be moved to specified foundation.

        Args:
            card: Card to move
            foundation_index: Target foundation pile (0-3)
            state: Current game state

        Returns:
            True if move is valid
        """
        if not (0 <= foundation_index < 4):
            return False

        foundation = state.foundations[foundation_index]

        if not foundation:
            return card.rank.numeric_value == 1  # Must be Ace

        top_card = Card.from_string(foundation[-1])
        return card.can_stack_on_foundation(top_card)

    def can_move_to_tableau(
        self,
        cards: Tuple[Card, ...],
        tableau_index: int,
        state: GameState,
    ) -> bool:
        """
        Check if cards can be moved to specified tableau.

        Args:
            cards: Cards to move (can be multiple for tableau-to-tableau)
            tableau_index: Target tableau pile (0-6)
            state: Current game state

        Returns:
            True if move is valid
        """
        if not (0 <= tableau_index < 7):
            return False

        if not cards:
            return False

        tableau = state.tableaus[tableau_index]
        bottom_card = cards[0]

        if not tableau:
            return bottom_card.rank.numeric_value == 13  # Must be King

        top_card = Card.from_string(tableau[-1])
        return bottom_card.can_stack_on_tableau(top_card)

    def can_draw_from_stock(self, state: GameState) -> bool:
        """
        Check if cards can be drawn from stock.

        Args:
            state: Current game state

        Returns:
            True if stock has cards
        """
        return len(state.stock) > 0

    def can_recycle_waste(self, state: GameState) -> bool:
        """
        Check if waste can be recycled to stock.

        Args:
            state: Current game state

        Returns:
            True if stock is empty and waste has cards
        """
        return len(state.stock) == 0 and len(state.waste) > 0
