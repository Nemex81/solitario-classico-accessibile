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
    - Stock pile (pile_mazzo) for drawing cards
    - Waste pile (pile_scarti) for discarded cards
    - Game deck (French or Neapolitan)
    
    Attributes:
        mazzo: The deck being used for the game
        pile_base: List of 7 tableau piles (indices 0-6)
        pile_semi: List of 4 foundation piles (one per suit)
        pile_mazzo: Stock pile for drawing cards
        pile_scarti: Waste pile for discarded cards
    """
    
    def __init__(self, deck: ProtoDeck) -> None:
        """Initialize game table with a deck.
        
        Args:
            deck: The deck to use (FrenchDeck or NeapolitanDeck)
        """
        self.mazzo = deck
        
        # 7 tableau piles (0-6) with descriptive names
        self.pile_base: List[Pile] = [
            Pile(name=f"Pila base {i+1}", pile_type="base")
            for i in range(7)
        ]
        
        # 4 foundation piles (one per suit)
        suit_names = ["Cuori", "Quadri", "Fiori", "Picche"]
        self.pile_semi: List[Pile] = [
            Pile(name=f"Pila semi {suit}", pile_type="semi")
            for suit in suit_names
        ]
        
        # Stock pile (tallone coperto)
        self.pile_mazzo: Optional[Pile] = None
        # Waste pile (tallone scoperto)
        self.pile_scarti: Optional[Pile] = None
        self.distribuisci_carte()
    
    @property
    def pile(self) -> List[Pile]:
        """Unified list of all piles for CursorManager compatibility.
        
        Returns list with indices:
        - [0-6]: Tableau piles (pile_base)
        - [7-10]: Foundation piles (pile_semi)
        - [11]: Waste pile (pile_scarti)
        - [12]: Stock pile (pile_mazzo)
        
        This property enables legacy-style access:
            table.pile[0]  # First tableau pile
            table.pile[7]  # First foundation pile
            table.pile[11] # Waste pile
            table.pile[12] # Stock pile
        
        Returns:
            List of all 13 piles in order
        """
        piles = []
        
        # Tableau piles (0-6)
        piles.extend(self.pile_base)
        
        # Foundation piles (7-10)
        piles.extend(self.pile_semi)
        
        # Waste pile (11)
        piles.append(self.pile_scarti if self.pile_scarti else Pile(name="Scarti", pile_type="scarti"))
        
        # Stock pile (12)
        piles.append(self.pile_mazzo if self.pile_mazzo else Pile(name="Mazzo", pile_type="mazzo"))
        
        return piles
    
    def distribuisci_carte(self) -> None:
        """Distribute cards on the table at game start.
        
        Dynamic distribution based on deck type:
        - French deck (52 cards): 28 distributed + 24 remain in stock
        - Neapolitan deck (40 cards): 28 distributed + 12 remain in stock
        
        The 28 cards are distributed across 7 tableau piles:
        - Pile 0: 1 card
        - Pile 1: 2 cards
        - Pile 2: 3 cards
        - ... 
        - Pile 6: 7 cards
        Total: 1+2+3+4+5+6+7 = 28 cards
        
        The last card in each pile is uncovered (face-up).
        Remaining cards are placed in the stock pile (pile_mazzo).
        
        Fixes #25, #26: Prevents IndexError when switching decks by not
        hardcoding the number of cards remaining for stock.
        """
        # Initialize stock and waste piles with names
        self.pile_mazzo = Pile(name="Mazzo", pile_type="mazzo")
        self.pile_scarti = Pile(name="Scarti", pile_type="scarti")
        
        # Distribute 28 cards to the 7 tableau piles
        for i in range(7):
            for j in range(i + 1):
                carta = self.mazzo.pesca()
                # Last card in each pile is face-up
                if j == i:
                    carta.set_uncover()
                self.pile_base[i].aggiungi_carta(carta)
        
        # Remaining cards go to stock pile (pile_mazzo)
        # French: 52 - 28 = 24 cards remain
        # Neapolitan: 40 - 28 = 12 cards remain
        while len(self.mazzo.cards) > 0:
            carta = self.mazzo.pesca()
            carta.set_cover()  # Stock cards are face-down
            self.pile_mazzo.aggiungi_carta(carta)
    
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
            pile_index: Index of target foundation pile (0-3)
        
        Returns:
            True if card was successfully placed, False otherwise
        """
        if pile_index < 0 or pile_index > 3:
            return False
        
        target_pile = self.pile_semi[pile_index]
        
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
        
        # Check ALL 4 foundation piles
        for pile in self.pile_semi:
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
            index: Pile index (0-6 for tableau)
        
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
        # Clear all tableau piles
        for pile in self.pile_base:
            pile.clear()
        
        # Clear all foundation piles
        for pile in self.pile_semi:
            pile.clear()
        
        # Clear stock and waste
        if self.pile_mazzo:
            self.pile_mazzo.clear()
        if self.pile_scarti:
            self.pile_scarti.clear()
        
        # Reset deck
        self.mazzo.reset()
        
        # Redistribute cards
        self.distribuisci_carte()
