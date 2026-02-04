"""Pile models for Klondike solitaire."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

from src.domain.models.card import Card


class PileType(Enum):
    """Pile type enumeration."""

    TABLEAU = "tableau"
    FOUNDATION = "foundation"
    STOCK = "stock"
    WASTE = "waste"


@dataclass(frozen=True)
class Pile:
    """
    Immutable pile representation.

    Represents a pile of cards with specific rules.

    Attributes:
        pile_type: Type of pile (tableau, foundation, stock, waste)
        cards: Tuple of card strings (immutable)
        face_down_count: Number of face-down cards (only for tableau)
    """

    pile_type: PileType
    cards: Tuple[str, ...] = ()
    face_down_count: int = 0

    def top_card(self) -> Optional[Card]:
        """Get the top (last) card of the pile."""
        if not self.cards:
            return None
        return Card.from_string(self.cards[-1])

    def visible_cards(self) -> Tuple[Card, ...]:
        """Get face-up cards."""
        if self.pile_type != PileType.TABLEAU:
            return tuple(Card.from_string(c) for c in self.cards)

        face_up_start = self.face_down_count
        return tuple(Card.from_string(c) for c in self.cards[face_up_start:])

    def with_cards(self, cards: Tuple[str, ...], face_down_count: Optional[int] = None) -> "Pile":
        """Create new pile with updated cards."""
        return Pile(
            pile_type=self.pile_type,
            cards=cards,
            face_down_count=(
                face_down_count if face_down_count is not None else self.face_down_count
            ),
        )

    def add_card(self, card: Card) -> "Pile":
        """Create new pile with card added on top."""
        return self.with_cards(self.cards + (str(card),))

    def remove_top(self, count: int = 1) -> "Pile":
        """Create new pile with top cards removed."""
        if count <= 0 or count > len(self.cards):
            raise ValueError(f"Invalid count: {count}")
        return self.with_cards(self.cards[:-count])

    def flip_top_card(self) -> "Pile":
        """
        Flip top face-down card (tableau only).

        Returns new pile with one less face-down card.
        """
        if self.pile_type != PileType.TABLEAU:
            raise ValueError("Only tableau piles have face-down cards")

        if self.face_down_count == 0:
            return self

        return self.with_cards(self.cards, self.face_down_count - 1)


# Factory functions
def create_tableau_pile(cards: Tuple[str, ...], face_down_count: int) -> Pile:
    """Create tableau pile with face-down cards."""
    return Pile(PileType.TABLEAU, cards, face_down_count)


def create_foundation_pile(cards: Tuple[str, ...] = ()) -> Pile:
    """Create foundation pile."""
    return Pile(PileType.FOUNDATION, cards, 0)


def create_stock_pile(cards: Tuple[str, ...]) -> Pile:
    """Create stock pile."""
    return Pile(PileType.STOCK, cards, 0)


def create_waste_pile(cards: Tuple[str, ...] = ()) -> Pile:
    """Create waste pile."""
    return Pile(PileType.WASTE, cards, 0)
