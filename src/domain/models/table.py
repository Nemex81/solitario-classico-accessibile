"""Domain model for game table.

Migrated from legacy scr/game_table.py with dynamic card distribution.
Manages 7 tableau piles and 4 foundation piles for Solitaire game.

This implementation includes critical fixes:
- #25, #26: Dynamic card distribution based on deck type
- #28, #29: Polymorphic King placement using deck.is_king()
"""

from typing import List, Optional

from src.domain.models.deck import ProtoDeck, FrenchDeck, NeapolitanDeck
from src.domain.models.card import Card
from src.domain.models.pile import Pile


class GameTable:
    """Represents the game table with piles and deck.
    
    Manages the complete game state including:
    - 7 tableau piles (base piles, indices 0-6)
    - 4 foundation piles (one per suit, indices 7-10)
    - Game deck (French or Neapolitan)
    
    Attributes:
        mazzo: The deck being used for the game
        pile_base: List of all 11 piles (7 tableau + 4 foundation)
    """
    
    def __init__(self, deck: ProtoDeck) -> None:
        """Initialize game table with a deck.
        
        Args:
            deck: The deck to use (FrenchDeck or NeapolitanDeck)
        """
        self.mazzo = deck
        # 11 piles total: 7 tableau (0-6) + 4 foundations (7-10)
        self.pile_base: List[Pile] = [Pile() for _ in range(11)]
        self.distribuisci_carte()
    
    def distribuisci_carte(self) -> None:
        """Distribute cards on the table at game start.
        
        Dynamic distribution based on deck type:
        - French deck (52 cards): 28 distributed + 24 remain in deck
        - Neapolitan deck (40 cards): 28 distributed + 12 remain in deck
        
        The 28 cards are distributed across 7 tableau piles:
        - Pile 0: 1 card
        - Pile 1: 2 cards
        - Pile 2: 3 cards
        - ... 
        - Pile 6: 7 cards
        Total: 1+2+3+4+5+6+7 = 28 cards
        
        The last card in each pile is uncovered (face-up).
        Remaining cards stay in the deck for the stock pile.
        
        Fixes #25, #26: Prevents IndexError when switching decks by not
        hardcoding the number of cards remaining for stock.
        """
        # Distribute 28 cards to the 7 tableau piles
        for i in range(7):
            for j in range(i + 1):
                carta = self.mazzo.pesca()
                # Last card in each pile is face-up
                if j == i:
                    carta.set_uncover()
                self.pile_base[i].aggiungi_carta(carta)
        
        # Remaining cards stay in the deck (mazzo)
        # French: 52 - 28 = 24 cards remain
        # Neapolitan: 40 - 28 = 12 cards remain
        # No explicit action needed - cards are already in the deck
    
    def put_to_base(self, card: Card, pile_index: int) -> bool:
        """Place a card on a tableau pile.
        
        Rules:
        - Empty pile: only Kings can be placed (uses polymorphic is_king())
        - Non-empty pile: card must have alternating color and descending value
        
        Args:
            card: Card to place
            pile_index: Index of target tableau pile (0-6)
        
        Returns:
            True if card was successfully placed, False otherwise
            
        Related #28, #29: Uses polymorphic is_king() method from deck,
        correctly handling French King (value 13) and Neapolitan King (value 10).
        """
        if pile_index < 0 or pile_index > 6:
            return False
        
        target_pile = self.pile_base[pile_index]
        
        # CRITICAL: Empty pile - use polymorphic is_king()
        if target_pile.is_empty():
            # Use the is_king() method from the deck (Commit #1 fix)
            # French King = 13, Neapolitan King = 10
            if not self.mazzo.is_king(card):
                return False
            target_pile.aggiungi_carta(card)
            return True
        
        # Non-empty pile: verify rules
        top_card = target_pile.get_top_card()
        if top_card is None:
            return False
        
        # Must have alternating colors AND descending value
        if (card.get_color != top_card.get_color and 
            card.get_value == top_card.get_value - 1):
            target_pile.aggiungi_carta(card)
            return True
        
        return False
    
    def put_to_foundation(self, card: Card, pile_index: int) -> bool:
        """Place a card on a foundation pile.
        
        Rules:
        - Empty foundation: only Aces (value 1) can be placed
        - Non-empty foundation: card must have same suit and ascending value
        
        Args:
            card: Card to place
            pile_index: Index of target foundation pile (7-10)
        
        Returns:
            True if card was successfully placed, False otherwise
        """
        if pile_index < 7 or pile_index > 10:
            return False
        
        target_pile = self.pile_base[pile_index]
        
        # Empty foundation: only Aces
        if target_pile.is_empty():
            if card.get_value != 1:
                return False
            target_pile.aggiungi_carta(card)
            return True
        
        # Non-empty foundation: same suit and ascending value
        top_card = target_pile.get_top_card()
        if top_card is None:
            return False
        
        if (card.get_suit == top_card.get_suit and 
            card.get_value == top_card.get_value + 1):
            target_pile.aggiungi_carta(card)
            return True
        
        return False
    
    def verifica_vittoria(self) -> bool:
        """Check if the player has won.
        
        Victory condition: all 4 foundation piles are complete with the
        maximum value card for the deck type on top:
        - French deck: 13 cards per pile (Ace→King, top card value 13)
        - Neapolitan deck: 10 cards per pile (Asso→Re, top card value 10)
        
        Returns:
            True if all 4 foundations are complete, False otherwise
        """
        # Get the maximum value for this deck type (King value)
        king_value = self.mazzo.FIGURE_VALUES.get("Re")
        if king_value is None:
            return False
        
        # Check ALL 4 foundation piles (indices 7, 8, 9, 10)
        for i in range(7, 11):
            pile = self.pile_base[i]
            
            # Empty pile = not victory
            if pile.is_empty():
                return False
            
            # Top card must be the King (maximum value)
            top_card = pile.get_top_card()
            if top_card is None or top_card.get_value != king_value:
                return False
        
        # All 4 foundations complete!
        return True
    
    def get_pile(self, index: int) -> Optional[Pile]:
        """Get a pile by index.
        
        Args:
            index: Pile index (0-6 for tableau, 7-10 for foundation)
        
        Returns:
            The pile at the given index, or None if index is invalid
        """
        if index < 0 or index >= len(self.pile_base):
            return None
        return self.pile_base[index]
    
    def reset(self) -> None:
        """Reset the game table.
        
        Clears all piles, resets the deck, and redistributes cards.
        """
        # Clear all piles
        for pile in self.pile_base:
            pile.clear()
        
        # Reset deck
        self.mazzo.reset()
        
        # Redistribute cards
        self.distribuisci_carte()
