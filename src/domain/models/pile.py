"""Domain model for card pile.

Provides a simple pile structure compatible with legacy scr/pile.py interface.
Manages collections of cards for tableau, foundation, stock, and waste piles.
"""

from typing import List, Optional

from src.domain.models.card import Card


class Pile:
    """Represents a pile of cards.
    
    A pile is a collection of cards that can be added to or removed from.
    Used for tableau piles, foundation piles, stock, and waste in Solitaire.
    """
    
    def __init__(self) -> None:
        """Initialize an empty pile."""
        self.cards: List[Card] = []
    
    def aggiungi_carta(self, card: Card) -> None:
        """Add a card to the top of the pile.
        
        Args:
            card: The card to add
        """
        self.cards.append(card)
    
    def rimuovi_carta(self) -> Optional[Card]:
        """Remove and return the top card from the pile.
        
        Returns:
            The card removed from the top, or None if pile is empty
        """
        if not self.cards:
            return None
        return self.cards.pop()
    
    def get_top_card(self) -> Optional[Card]:
        """Get the top card without removing it.
        
        Returns:
            The top card, or None if pile is empty
        """
        if not self.cards:
            return None
        return self.cards[-1]
    
    def is_empty(self) -> bool:
        """Check if the pile is empty.
        
        Returns:
            True if the pile has no cards
        """
        return len(self.cards) == 0
    
    def get_size(self) -> int:
        """Get the number of cards in the pile.
        
        Returns:
            Number of cards in the pile
        """
        return len(self.cards)
    
    def get_all_cards(self) -> List[Card]:
        """Get all cards in the pile.
        
        Returns:
            Copy of the list of all cards in the pile
        """
        return self.cards.copy()
    
    def clear(self) -> None:
        """Remove all cards from the pile."""
        self.cards.clear()
    
    def remove_last_card(self) -> Optional[Card]:
        """Remove and return the last card from the pile (same as rimuovi_carta).
        
        Returns:
            The card removed from the top, or None if pile is empty
        """
        return self.rimuovi_carta()
    
    def get_card_count(self) -> int:
        """Get the number of cards in the pile (same as get_size).
        
        Returns:
            Number of cards in the pile
        """
        return self.get_size()
