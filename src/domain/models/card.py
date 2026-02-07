"""Domain model for playing cards.

Migrated and modernized from legacy scr/cards.py.
Provides a clean Card model compatible with both French and Neapolitan decks.
"""

from enum import Enum
from typing import Optional


class Suit(Enum):
    """Card suit enumeration with support for French and Italian decks."""
    
    # French suits
    HEARTS = ("cuori", "♥", "red", False)
    DIAMONDS = ("quadri", "♦", "red", False)
    CLUBS = ("fiori", "♣", "black", False)
    SPADES = ("picche", "♠", "black", False)
    
    # Italian/Neapolitan suits
    COPPE = ("coppe", "🍷", "red", True)
    DENARI = ("denari", "🪙", "red", True)
    SPADE_IT = ("spade", "🗡️", "black", True)
    BASTONI = ("bastoni", "🏑", "black", True)
    
    def __init__(self, name_it: str, symbol: str, color: str, is_italian: bool):
        self.name_it = name_it
        self.symbol = symbol
        self.color = color
        self.is_italian = is_italian


class Rank(Enum):
    """Card rank enumeration."""
    
    ACE = (1, "A", "Asso")
    TWO = (2, "2", "2")
    THREE = (3, "3", "3")
    FOUR = (4, "4", "4")
    FIVE = (5, "5", "5")
    SIX = (6, "6", "6")
    SEVEN = (7, "7", "7")
    EIGHT = (8, "8", "8")
    NINE = (9, "9", "9")
    TEN = (10, "10", "10")
    JACK = (11, "J", "Jack")
    QUEEN = (12, "Q", "Regina")
    KING = (13, "K", "Re")
    
    # Italian-specific face cards
    CAVALLO = (9, "C", "Cavallo")  # Italian Knight (9 in Neapolitan deck)
    REGINA_IT = (8, "R", "Regina")  # Italian Queen (8 in Neapolitan deck)
    RE_IT = (10, "K", "Re")  # Italian King (10 in Neapolitan deck)
    
    def __init__(self, numeric_value: int, symbol: str, name_it: str):
        self.numeric_value = numeric_value
        self.symbol = symbol
        self.name_it = name_it


class Card:
    """Represents a playing card.
    
    Compatible with both French (52-card) and Neapolitan (40-card) decks.
    Maintains interface compatibility with legacy scr/cards.py while
    providing a cleaner implementation.
    """
    
    def __init__(
        self,
        valore: str,
        seme: str,
        coperta: bool = True,
        rank: Optional[Rank] = None,
        suit: Optional[Suit] = None
    ):
        """Initialize a Card.
        
        Args:
            valore: String value/rank of the card (legacy interface)
            seme: String suit of the card (legacy interface)
            coperta: Whether the card is face-down
            rank: Optional Rank enum (modern interface)
            suit: Optional Suit enum (modern interface)
        """
        self._valore = valore
        self._seme = seme
        self._coperta = coperta
        self._nome: Optional[str] = None
        self._id: Optional[int] = None
        self._colore: Optional[str] = None
        self._valore_numerico: Optional[int] = None
        self._rank = rank
        self._suit = suit
    
    @property
    def rank(self) -> Optional[Rank]:
        """Get the rank enum."""
        return self._rank
    
    @property
    def suit(self) -> Optional[Suit]:
        """Get the suit enum."""
        return self._suit
    
    @property
    def get_name(self) -> str:
        """Get card name (legacy interface)."""
        if self._nome is None:
            return "nessun nome"
        if self._coperta:
            return "carta coperta"
        return self._nome
    
    @property
    def get_id(self) -> Optional[int]:
        """Get card ID (legacy interface)."""
        return self._id
    
    @property
    def get_suit(self) -> str:
        """Get card suit string (legacy interface)."""
        if self._seme is None:
            return "nessun seme"
        if self._coperta:
            return "carta coperta"
        return self._seme
    
    @property
    def get_value(self) -> int:
        """Get card numeric value (legacy interface).
        
        Returns the actual numeric value regardless of covered state,
        for internal game logic purposes. Use get_name or __str__ for
        display purposes which respect the covered state.
        """
        if self._valore_numerico is None:
            return 0
        return self._valore_numerico
    
    @property
    def get_color(self) -> str:
        """Get card color (legacy interface)."""
        if self._colore is None:
            return "nessun colore"
        if self._coperta:
            return "carta coperta"
        return self._colore
    
    @property
    def get_covered(self) -> bool:
        """Check if card is face-down (legacy interface)."""
        return self._coperta
    
    @property
    def color(self) -> str:
        """Get card color (modern interface)."""
        if self._suit:
            return self._suit.color
        return self._colore or "unknown"
    
    @property
    def value(self) -> int:
        """Get card numeric value (modern interface)."""
        if self._rank:
            return self._rank.numeric_value
        return self._valore_numerico or 0
    
    def set_name(self, name: str) -> None:
        """Set card name."""
        self._nome = name
    
    def set_id(self, card_id: int) -> None:
        """Set card ID."""
        self._id = card_id
    
    def set_suit(self, suit: str) -> None:
        """Set card suit."""
        self._seme = suit
    
    def set_str_value(self, value: str) -> None:
        """Set card string value."""
        self._valore = value
    
    def set_int_value(self, value: int) -> None:
        """Set card numeric value."""
        self._valore_numerico = value
    
    def set_color(self, color: str) -> None:
        """Set card color."""
        self._colore = color
    
    def set_cover(self) -> None:
        """Cover the card (face-down)."""
        self._coperta = True
    
    def set_uncover(self) -> None:
        """Uncover the card (face-up)."""
        self._coperta = False
    
    def flip(self) -> None:
        """Flip the card over."""
        self._coperta = not self._coperta
    
    @staticmethod
    def _determine_color(suit: str) -> str:
        """Determine card color based on suit.
        
        Args:
            suit: Suit name (Italian)
            
        Returns:
            Color string ("rosso" or "blu")
        """
        if suit in ["cuori", "quadri", "coppe", "denari"]:
            return "rosso"
        return "blu"
    
    def can_stack_on_foundation(self, target: Optional['Card']) -> bool:
        """Check if this card can be placed on a foundation pile.
        
        Args:
            target: The top card of the foundation pile (None if empty)
            
        Returns:
            True if the card can be placed
        """
        if self._rank is None:
            return False
        
        # Ace can go on empty foundation
        if target is None:
            return self._rank == Rank.ACE
        
        # Must be same suit and one rank higher
        if target.suit != self._suit:
            return False
        
        return self.value == target.value + 1
    
    def can_stack_on_tableau(self, target: Optional['Card']) -> bool:
        """Check if this card can be placed on a tableau pile.
        
        Args:
            target: The top card of the tableau pile (None if empty)
            
        Returns:
            True if the card can be placed
        """
        if self._rank is None:
            return False
        
        # King can go on empty tableau
        if target is None:
            return self._rank == Rank.KING
        
        # Must be opposite color and one rank lower
        if self.color == target.color:
            return False
        
        return self.value == target.value - 1
    
    @classmethod
    def from_string(cls, card_str: str) -> 'Card':
        """Create a Card from a string representation.
        
        Args:
            card_str: String like "AH" (Ace of Hearts), "10D" (Ten of Diamonds)
            
        Returns:
            Card instance
            
        Raises:
            ValueError: If the string format is invalid
        """
        if len(card_str) < 2:
            raise ValueError(f"Invalid card string: {card_str}")
        
        # Parse rank
        if card_str.startswith("10"):
            rank_str = "10"
            suit_str = card_str[2:]
        else:
            rank_str = card_str[0]
            suit_str = card_str[1:]
        
        # Map rank
        rank_map = {
            "A": Rank.ACE, "2": Rank.TWO, "3": Rank.THREE,
            "4": Rank.FOUR, "5": Rank.FIVE, "6": Rank.SIX,
            "7": Rank.SEVEN, "8": Rank.EIGHT, "9": Rank.NINE,
            "10": Rank.TEN, "J": Rank.JACK, "Q": Rank.QUEEN, "K": Rank.KING
        }
        
        rank = rank_map.get(rank_str)
        if rank is None:
            raise ValueError(f"Invalid rank: {rank_str}")
        
        # Map suit
        suit_map = {
            "H": Suit.HEARTS, "D": Suit.DIAMONDS,
            "C": Suit.CLUBS, "S": Suit.SPADES
        }
        
        suit = suit_map.get(suit_str)
        if suit is None:
            raise ValueError(f"Invalid suit: {suit_str}")
        
        return cls(
            valore=rank.name_it,
            seme=suit.name_it,
            coperta=False,
            rank=rank,
            suit=suit
        )
    
    def __str__(self) -> str:
        """String representation of the card."""
        if self._rank and self._suit:
            return f"{self._rank.symbol}{self._suit.symbol}"
        
        if self._coperta:
            return "carta coperta"
        
        return f"{self._valore} di {self._seme}"
    
    def get_info_card(self) -> str:
        """Get detailed card information."""
        if self._coperta:
            return "carta coperta.\n"
        
        details = f"nome: {self.get_name}.\n"
        details += f"id: {self._id}.\n"
        details += f"seme: {self.get_suit}.\n"
        details += f"valore: {self.get_value}.\n"
        details += f"colore: {self.get_color}.\n"
        return details
