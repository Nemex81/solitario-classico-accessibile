"""Domain models for card decks.

Migrated from legacy scr/decks.py with all v1.3.3 fixes.
Supports French (52 cards) and Neapolitan (40 cards) decks.
"""

from typing import List, Optional, Dict
import random

from src.domain.models.card import Card


class ProtoDeck:
    """Base class for card deck management.
    
    Provides common functionality for different deck types (French, Neapolitan)
    with polymorphic behavior for deck-specific rules like King validation.
    
    Attributes:
        SUITES: List of suit names for this deck type
        VALUES: List of card values for this deck type  
        FIGURE_VALUES: Dictionary mapping figure names to numeric values
        cards: List of Card objects in the deck
        tipo: String describing the deck type
    """
    
    # Constants (to be overridden by subclasses)
    SUITES: List[str] = []
    VALUES: List[str] = []
    FIGURE_VALUES: Dict[str, int] = {}
    
    def __init__(self) -> None:
        """Initialize an empty deck."""
        self.cards: List[Card] = []
        self.tipo: Optional[str] = None
    
    def get_suits(self) -> List[str]:
        """Get the list of suits for this deck.
        
        Returns:
            List of suit names
        """
        return self.SUITES
    
    def crea(self) -> List[Card]:
        """Create the deck of cards.
        
        To be implemented by subclasses.
        
        Returns:
            List of created cards
        """
        return []
    
    def inserisci_carte(self, carte_aggiuntive: List[Card]) -> None:
        """Insert additional cards into the deck.
        
        Can be used for other types of solitaire games that use multiple decks.
        
        Args:
            carte_aggiuntive: List of cards to add to the deck
        """
        for carta in carte_aggiuntive:
            self.cards.append(carta)
    
    def rimuovi_carte(self, n: int) -> List[Card]:
        """Remove n cards from the deck and return them.
        
        Args:
            n: Number of cards to remove from the top of the deck
            
        Returns:
            List of removed cards
        """
        carte_rimosse = self.cards[:n]
        self.cards = self.cards[n:]
        return carte_rimosse
    
    def pesca(self) -> Card:
        """Draw a card from the deck.
        
        Returns:
            The card drawn from the top of the deck
            
        Raises:
            IndexError: If the deck is empty
        """
        carta_pescata = self.cards.pop(0)
        return carta_pescata
    
    def get_carta(self, i: int) -> Optional[Card]:
        """Get the card at position i if it exists.
        
        Args:
            i: Index of the card to retrieve
            
        Returns:
            Card at position i, or None if index is out of bounds
        """
        if i < len(self.cards):
            return self.cards[i]
        return None
    
    def get_len(self) -> int:
        """Get the number of cards in the deck.
        
        Returns:
            Number of cards currently in the deck
        """
        return len(self.cards)
    
    def get_type(self) -> Optional[str]:
        """Get the deck type.
        
        Returns:
            String describing the deck type
        """
        return self.tipo
    
    @staticmethod
    def get_type_suits(deck: 'ProtoDeck') -> List[str]:
        """Get the list of suits for this deck type.
        
        Args:
            deck: The deck instance
            
        Returns:
            List of suit names
        """
        return deck.SUITES
    
    def mischia(self) -> None:
        """Shuffle the cards in the deck."""
        random.shuffle(self.cards)
    
    def is_french_deck(self) -> bool:
        """Check if this is a French deck.
        
        Returns:
            True if this is a French (52-card) deck
        """
        if self.SUITES == ["cuori", "quadri", "fiori", "picche"]:
            return True
        return False
    
    def is_neapolitan_deck(self) -> bool:
        """Check if this is a Neapolitan deck.
        
        Returns:
            True if this is a Neapolitan (40-card) deck
        """
        if self.SUITES == ["bastoni", "coppe", "denari", "spade"]:
            return True
        return False
    
    def is_empty_dek(self) -> bool:
        """Check if the deck is empty.
        
        Returns:
            True if the deck has no cards
        """
        return len(self.cards) == 0
    
    def is_king(self, card: Card) -> bool:
        """Check if a card is a King for this deck type.
        
        This method resolves bugs #28 and #29 by correctly identifying Kings
        regardless of deck type. French Kings have value 13, Neapolitan Kings
        have value 10.
        
        Args:
            card: The card to check
            
        Returns:
            True if the card is a King (value 13 for French, 10 for Neapolitan)
        """
        # The King is always in FIGURE_VALUES with key "Re"
        king_value = self.FIGURE_VALUES.get("Re")
        if king_value is None:
            # If the deck doesn't have a King defined, no card can be a King
            return False
        return card.get_value == king_value
    
    def reset(self) -> None:
        """Reset the deck.
        
        Clears all cards, recreates the deck, and shuffles it.
        """
        self.cards = []
        self.crea()
        self.mischia()


class NeapolitanDeck(ProtoDeck):
    """Neapolitan playing cards deck (40 cards).
    
    Traditional Italian deck with 4 suits (bastoni, coppe, denari, spade)
    and 10 ranks per suit (Asso, 2-7, Regina, Cavallo, Re).
    
    Note: There are no 8, 9, 10 numeric cards. Instead:
    - Regina (Queen) has value 8
    - Cavallo (Knight) has value 9
    - Re (King) has value 10
    """
    
    # Constants
    SUITES = ["bastoni", "coppe", "denari", "spade"]
    VALUES = ["Asso", "2", "3", "4", "5", "6", "7", "Regina", "Cavallo", "Re"]
    FIGURE_VALUES = {"Regina": 8, "Cavallo": 9, "Re": 10, "Asso": 1}
    
    def __init__(self) -> None:
        """Initialize a Neapolitan deck."""
        self.tipo = "carte napoletane"
        self.cards: List[Card] = []
        self.reset()
    
    def get_total_cards(self) -> int:
        """Get the total number of cards in a complete Neapolitan deck.
        
        Returns:
            Total number of cards (40 = 4 suits × 10 values)
        """
        return len(self.SUITES) * len(self.VALUES)  # 4 * 10 = 40
    
    def crea(self) -> List[Card]:
        """Create the Neapolitan deck of 40 cards.
        
        Creates all combinations of suits and values, assigning proper
        numeric values to each card including figure cards.
        
        Returns:
            List of 40 Card objects
        """
        semi = self.SUITES
        valori = self.VALUES
        mazzo: List[Card] = []
        i = 0
        
        for seme in semi:
            for valore in valori:
                carta = Card(valore, seme)
                carta.set_name(f"{valore} di {seme}")
                
                if valore in ["Regina", "Cavallo", "Re", "Asso"]:
                    carta.set_int_value(int(self.FIGURE_VALUES[valore]))
                else:
                    carta.set_int_value(int(valore))
                
                carta.set_id(i)
                carta.set_color(carta._determine_color(seme))
                mazzo.append(carta)
                i += 1
        
        self.cards = mazzo
        return mazzo


class FrenchDeck(ProtoDeck):
    """French playing cards deck (52 cards).
    
    Standard international deck with 4 suits (cuori, quadri, fiori, picche)
    and 13 ranks per suit (Asso, 2-10, Jack, Regina, Re).
    """
    
    # Constants
    SUITES = ["cuori", "quadri", "fiori", "picche"]
    VALUES = ["Asso", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Regina", "Re"]
    FIGURE_VALUES = {"Jack": 11, "Regina": 12, "Re": 13, "Asso": 1}
    
    def __init__(self) -> None:
        """Initialize a French deck."""
        self.tipo = "carte francesi"
        self.cards: List[Card] = []
        self.reset()
    
    def get_total_cards(self) -> int:
        """Get the total number of cards in a complete French deck.
        
        Returns:
            Total number of cards (52 = 4 suits × 13 values)
        """
        return len(self.SUITES) * len(self.VALUES)  # 4 * 13 = 52
    
    def crea(self) -> List[Card]:
        """Create the French deck of 52 cards.
        
        Creates all combinations of suits and values, assigning proper
        numeric values to each card including figure cards.
        
        Returns:
            List of 52 Card objects
        """
        semi = self.SUITES
        valori = self.VALUES
        mazzo: List[Card] = []
        i = 0
        
        for seme in semi:
            for valore in valori:
                carta = Card(valore, seme)
                carta.set_name(f"{valore} di {seme}")
                
                if valore in ["Jack", "Regina", "Re", "Asso"]:
                    carta.set_int_value(int(self.FIGURE_VALUES[valore]))
                else:
                    carta.set_int_value(int(valore))
                
                carta.set_id(i)
                carta.set_color(carta._determine_color(seme))
                mazzo.append(carta)
                i += 1
        
        self.cards = mazzo
        return mazzo
