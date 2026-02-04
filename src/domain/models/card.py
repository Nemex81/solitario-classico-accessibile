"""Card model and related types."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Suit(Enum):
    """Card suit enumeration - supports French and Italian decks."""

    # French deck
    HEARTS = "H"
    DIAMONDS = "D"
    CLUBS = "C"
    SPADES = "S"

    # Neapolitan deck (Italian)
    COPPE = "COPPE"
    DENARI = "DENARI"
    SPADE_IT = "SPADE_IT"  # Avoid conflict with SPADES
    BASTONI = "BASTONI"

    @property
    def color(self) -> str:
        """Get suit color (red or black)."""
        red_suits = (Suit.HEARTS, Suit.DIAMONDS, Suit.COPPE, Suit.DENARI)
        return "red" if self in red_suits else "black"

    @property
    def symbol(self) -> str:
        """Get unicode symbol for suit."""
        symbols = {
            # French
            Suit.HEARTS: "♥",
            Suit.DIAMONDS: "♦",
            Suit.CLUBS: "♣",
            Suit.SPADES: "♠",
            # Italian
            Suit.COPPE: "🍷",
            Suit.DENARI: "🪙",
            Suit.SPADE_IT: "🗡️",
            Suit.BASTONI: "🏑",
        }
        return symbols[self]

    @property
    def is_italian(self) -> bool:
        """Check if suit belongs to Italian deck."""
        return self in (Suit.COPPE, Suit.DENARI, Suit.SPADE_IT, Suit.BASTONI)


class Rank(Enum):
    """Card rank enumeration."""

    ACE = "A"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"

    @property
    def numeric_value(self) -> int:
        """Get numeric value of rank (1-13)."""
        values = {
            Rank.ACE: 1,
            Rank.TWO: 2,
            Rank.THREE: 3,
            Rank.FOUR: 4,
            Rank.FIVE: 5,
            Rank.SIX: 6,
            Rank.SEVEN: 7,
            Rank.EIGHT: 8,
            Rank.NINE: 9,
            Rank.TEN: 10,
            Rank.JACK: 11,
            Rank.QUEEN: 12,
            Rank.KING: 13,
        }
        return values[self]


@dataclass(frozen=True)
class Card:
    """
    Immutable playing card.

    Represents a standard playing card with rank and suit.
    Uses frozen dataclass for immutability.

    Attributes:
        rank: Card rank (A, 2-10, J, Q, K)
        suit: Card suit (Hearts, Diamonds, Clubs, Spades)
    """

    rank: Rank
    suit: Suit

    @property
    def color(self) -> str:
        """Get card color based on suit."""
        return self.suit.color

    @property
    def value(self) -> int:
        """Get numeric value of card (1-13)."""
        return self.rank.numeric_value

    def can_stack_on_foundation(self, other: Optional["Card"]) -> bool:
        """
        Check if this card can be placed on foundation pile.

        Foundation rules:
        - Must start with Ace
        - Must be same suit
        - Must be one rank higher

        Args:
            other: Card currently on top of foundation (None if empty)

        Returns:
            True if card can be placed on foundation
        """
        if other is None:
            return self.rank == Rank.ACE

        return self.suit == other.suit and self.value == other.value + 1

    def can_stack_on_tableau(self, other: Optional["Card"]) -> bool:
        """
        Check if this card can be placed on tableau pile.

        Tableau rules:
        - Can place King on empty pile
        - Must be opposite color
        - Must be one rank lower

        Args:
            other: Card currently on top of tableau (None if empty)

        Returns:
            True if card can be placed on tableau
        """
        if other is None:
            return self.rank == Rank.KING

        return self.color != other.color and self.value == other.value - 1

    def __str__(self) -> str:
        """String representation (e.g., 'A♥', 'K♠')."""
        return f"{self.rank.value}{self.suit.symbol}"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"Card(rank={self.rank}, suit={self.suit})"

    @classmethod
    def from_string(cls, card_str: str) -> "Card":
        """
        Create Card from string notation.

        Examples:
            'AH' -> Ace of Hearts
            '10D' -> Ten of Diamonds
            'KS' -> King of Spades

        Args:
            card_str: String representation (rank + suit code)

        Returns:
            Card instance

        Raises:
            ValueError: If string format is invalid
        """
        if len(card_str) < 2:
            raise ValueError(f"Invalid card string: {card_str}")

        # Handle 10 specially (2 characters for rank)
        if card_str[:2] == "10":
            rank_str = "10"
            suit_str = card_str[2:]
        else:
            rank_str = card_str[0]
            suit_str = card_str[1:]

        # Find matching rank
        rank = None
        for r in Rank:
            if r.value == rank_str:
                rank = r
                break

        if rank is None:
            raise ValueError(f"Invalid rank: {rank_str}")

        # Find matching suit
        suit = None
        for s in Suit:
            if s.value == suit_str:
                suit = s
                break

        if suit is None:
            raise ValueError(f"Invalid suit: {suit_str}")

        return cls(rank=rank, suit=suit)
