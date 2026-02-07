"""
Deck models for card games.

This module provides base deck functionality and specific implementations
for French (52 cards) and Neapolitan (40 cards) decks.

Part of Clean Architecture migration from scr/decks.py
"""

import random
from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.models.card import Card, Rank, Suit


class ProtoDeck(ABC):
    """
    Abstract base class for deck implementations.

    Provides common deck functionality including shuffling, drawing,
    and card management. Subclasses must implement deck-specific
    creation logic.

    Attributes:
        cards: List of cards currently in the deck
        deck_type: Human-readable deck type name
    """

    # Class constants - to be overridden by subclasses
    SUITS: List[Suit] = []
    RANKS: List[Rank] = []
    KING_VALUE: int = 13  # Default King value for French deck

    def __init__(self) -> None:
        """Initialize an empty deck."""
        self.cards: List[Card] = []
        self.deck_type: str = "generic"

    @abstractmethod
    def create(self) -> List[Card]:
        """
        Create the deck with all cards.

        Returns:
            List of all cards in the newly created deck.
        """
        pass

    @property
    def suits(self) -> List[Suit]:
        """Get the list of suits used by this deck."""
        return self.SUITS

    def insert_cards(self, additional_cards: List[Card]) -> None:
        """
        Add cards to the deck.

        Args:
            additional_cards: List of cards to add to the deck.
        """
        self.cards.extend(additional_cards)

    def remove_cards(self, n: int) -> List[Card]:
        """
        Remove and return n cards from the top of the deck.

        Args:
            n: Number of cards to remove.

        Returns:
            List of removed cards.
        """
        removed = self.cards[:n]
        self.cards = self.cards[n:]
        return removed

    def draw(self) -> Optional[Card]:
        """
        Draw a single card from the top of the deck.

        Returns:
            The drawn card, or None if deck is empty.
        """
        if self.is_empty():
            return None
        return self.cards.pop(0)

    def get_card(self, index: int) -> Optional[Card]:
        """
        Get a card at a specific index without removing it.

        Args:
            index: Position of the card (0-indexed).

        Returns:
            Card at the position, or None if index is out of bounds.
        """
        if 0 <= index < len(self.cards):
            return self.cards[index]
        return None

    def get_length(self) -> int:
        """
        Get the number of cards remaining in the deck.

        Returns:
            Number of cards in the deck.
        """
        return len(self.cards)

    def get_type(self) -> str:
        """
        Get the deck type name.

        Returns:
            Human-readable deck type string.
        """
        return self.deck_type

    def shuffle(self) -> None:
        """Randomly shuffle all cards in the deck."""
        random.shuffle(self.cards)

    def is_french_deck(self) -> bool:
        """
        Check if this is a French (standard 52-card) deck.

        Returns:
            True if this is a French deck, False otherwise.
        """
        french_suits = {Suit.HEARTS, Suit.DIAMONDS, Suit.CLUBS, Suit.SPADES}
        return set(self.SUITS) == french_suits

    def is_neapolitan_deck(self) -> bool:
        """
        Check if this is a Neapolitan (40-card) deck.

        Returns:
            True if this is a Neapolitan deck, False otherwise.
        """
        neapolitan_suits = {Suit.COPPE, Suit.DENARI, Suit.SPADE_IT, Suit.BASTONI}
        return set(self.SUITS) == neapolitan_suits

    def is_empty(self) -> bool:
        """
        Check if the deck is empty.

        Returns:
            True if the deck has no cards, False otherwise.
        """
        return len(self.cards) == 0

    def is_king(self, card: Card) -> bool:
        """
        Check if a card is a King for this deck type.

        This method handles both French and Neapolitan decks correctly:
        - French deck: King has value 13
        - Neapolitan deck: King (Re) has value 10

        Args:
            card: The card to check.

        Returns:
            True if the card is a King, False otherwise.
        """
        return card.value == self.KING_VALUE

    def reset(self) -> None:
        """Reset the deck by recreating and shuffling all cards."""
        self.cards = []
        self.create()
        self.shuffle()

    def get_total_cards(self) -> int:
        """
        Get the total number of cards in a complete deck.

        Returns:
            Total card count for this deck type.
        """
        return len(self.SUITS) * len(self.RANKS)


class FrenchDeck(ProtoDeck):
    """
    French (standard) 52-card deck.

    Contains 4 suits (Hearts, Diamonds, Clubs, Spades) with 13 ranks each
    (Ace through King).

    Attributes:
        SUITS: The four French suits
        RANKS: All 13 ranks from Ace to King
        KING_VALUE: 13 (King's numeric value in French deck)
    """

    SUITS: List[Suit] = [Suit.HEARTS, Suit.DIAMONDS, Suit.CLUBS, Suit.SPADES]
    RANKS: List[Rank] = [
        Rank.ACE,
        Rank.TWO,
        Rank.THREE,
        Rank.FOUR,
        Rank.FIVE,
        Rank.SIX,
        Rank.SEVEN,
        Rank.EIGHT,
        Rank.NINE,
        Rank.TEN,
        Rank.JACK,
        Rank.QUEEN,
        Rank.KING,
    ]
    KING_VALUE: int = 13

    def __init__(self) -> None:
        """Initialize a French deck with 52 shuffled cards."""
        super().__init__()
        self.deck_type = "carte francesi"
        self.reset()

    def create(self) -> List[Card]:
        """
        Create a complete French deck (52 cards).

        Returns:
            List of 52 cards (4 suits × 13 ranks).
        """
        deck: List[Card] = []
        for suit in self.SUITS:
            for rank in self.RANKS:
                card = Card(rank=rank, suit=suit)
                deck.append(card)
        self.cards = deck
        return deck


class NeapolitanDeck(ProtoDeck):
    """
    Neapolitan (Italian) 40-card deck.

    Contains 4 Italian suits (Coppe, Denari, Spade, Bastoni) with 10 ranks each
    (Ace through Re/King). Note: In Neapolitan deck, there's no 8, 9, 10 - instead
    there's Donna (8), Cavallo (9), Re (10).

    Attributes:
        SUITS: The four Italian suits
        RANKS: 10 ranks (Ace, 2-7, Donna, Cavallo, Re)
        KING_VALUE: 10 (Re's numeric value in Neapolitan deck)
    """

    SUITS: List[Suit] = [Suit.BASTONI, Suit.COPPE, Suit.DENARI, Suit.SPADE_IT]
    # Neapolitan deck uses Ace, 2-7, then Donna(8), Cavallo(9), Re(10)
    # We map these to existing Ranks - note the Re (King) = value 10
    RANKS: List[Rank] = [
        Rank.ACE,
        Rank.TWO,
        Rank.THREE,
        Rank.FOUR,
        Rank.FIVE,
        Rank.SIX,
        Rank.SEVEN,
        Rank.EIGHT,   # Donna/Regina
        Rank.NINE,    # Cavallo
        Rank.TEN,     # Re (King)
    ]
    KING_VALUE: int = 10  # CRITICAL: Re in Neapolitan deck has value 10

    def __init__(self) -> None:
        """Initialize a Neapolitan deck with 40 shuffled cards."""
        super().__init__()
        self.deck_type = "carte napoletane"
        self.reset()

    def create(self) -> List[Card]:
        """
        Create a complete Neapolitan deck (40 cards).

        Returns:
            List of 40 cards (4 suits × 10 ranks).
        """
        deck: List[Card] = []
        for suit in self.SUITS:
            for rank in self.RANKS:
                card = Card(rank=rank, suit=suit)
                deck.append(card)
        self.cards = deck
        return deck


# Module execution check
if __name__ == "__main__":
    print(f"compilazione di {__name__} completata.")
else:
    print(f"Carico: {__name__}")
