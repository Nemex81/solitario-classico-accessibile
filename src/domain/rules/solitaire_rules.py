"""Domain rules for Solitaire card game.

Implements all game rules for move validation following DDD principles.
Rules are independent from game state and can be tested in isolation.
"""

from typing import List, Optional

from src.domain.models.deck import ProtoDeck
from src.domain.models.card import Card
from src.domain.models.pile import Pile


class SolitaireRules:
    """Encapsulates all Solitaire game rules.
    
    Provides stateless validation methods for all game moves.
    Rules are deck-agnostic using polymorphic deck methods.
    
    Key principles:
    - Rules are stateless (no game state storage)
    - Deck-polymorphic (supports French and Neapolitan)
    - Independently testable
    - Pure business logic
    
    Attributes:
        deck: The deck type being used (for polymorphic checks)
    """
    
    def __init__(self, deck: ProtoDeck) -> None:
        """Initialize rules with a specific deck type.
        
        Args:
            deck: The deck to use for polymorphic rule checks (e.g., is_king)
        """
        self.deck = deck
    
    # ========================================
    # TABLEAU RULES (Pile Base)
    # ========================================
    
    def can_place_on_tableau(self, card: Card, target_pile: Pile) -> bool:
        """Check if a card can be placed on a tableau pile.
        
        Rules:
        - Empty pile: only Kings (uses deck.is_king)
        - Non-empty pile: alternating colors + descending values (value - 1)
        
        Args:
            card: Card to place
            target_pile: Target tableau pile
            
        Returns:
            True if move is valid
            
        Examples:
            >>> # Empty pile
            >>> rules.can_place_on_tableau(king, empty_pile)  # True
            >>> rules.can_place_on_tableau(queen, empty_pile) # False
            >>> 
            >>> # Non-empty pile (red 7 on top)
            >>> rules.can_place_on_tableau(black_6, pile)  # True (alternating)
            >>> rules.can_place_on_tableau(red_6, pile)    # False (same color)
        """
        # CRITICAL: Empty pile accepts only Kings
        if target_pile.is_empty():
            return self.deck.is_king(card)
        
        # Non-empty pile: get top card
        top_card = target_pile.get_top_card()
        if top_card is None:
            return False
        
        # Must alternate colors AND descend by 1
        return (
            card.get_color != top_card.get_color and
            card.get_value == top_card.get_value - 1
        )
    
    def can_move_sequence(self, cards: List[Card], target_pile: Pile) -> bool:
        """Check if a sequence of cards can be moved to a tableau pile.
        
        Rules:
        - All cards must be face-up (uncovered)
        - Cards must form valid descending alternating sequence
        - Bottom card of sequence must be placeable on target
        
        Args:
            cards: List of cards to move (ordered bottom to top)
            target_pile: Target tableau pile
            
        Returns:
            True if entire sequence can be moved
            
        Examples:
            >>> # Valid: [Red 7, Black 6, Red 5] onto Black 8
            >>> rules.can_move_sequence(sequence, pile_with_black_8)  # True
        """
        if not cards:
            return False
        
        # CRITICAL: All cards must be uncovered
        if any(card.get_covered for card in cards):
            return False
        
        # Validate internal sequence consistency
        if not self._is_valid_tableau_sequence(cards):
            return False
        
        # Check if bottom card (first in list) can be placed on target
        return self.can_place_on_tableau(cards[0], target_pile)
    
    def _is_valid_tableau_sequence(self, cards: List[Card]) -> bool:
        """Validate that cards form a proper tableau sequence.
        
        Internal helper method.
        
        Args:
            cards: List of cards (bottom to top)
            
        Returns:
            True if cards form valid descending alternating sequence
        """
        if len(cards) < 2:
            return True  # Single card is always valid
        
        for i in range(len(cards) - 1):
            current = cards[i]
            next_card = cards[i + 1]
            
            # Must alternate colors
            if current.get_color == next_card.get_color:
                return False
            
            # Must descend by exactly 1
            if next_card.get_value != current.get_value - 1:
                return False
        
        return True
    
    # ========================================
    # FOUNDATION RULES (Pile Fondazione)
    # ========================================
    
    def can_place_on_foundation(self, card: Card, target_pile: Pile) -> bool:
        """Check if a card can be placed on a foundation pile.
        
        Rules:
        - Empty pile: only Aces (value == 1)
        - Non-empty pile: same suit + ascending value (value + 1)
        
        Args:
            card: Card to place
            target_pile: Target foundation pile
            
        Returns:
            True if move is valid
            
        Examples:
            >>> rules.can_place_on_foundation(ace_hearts, empty)      # True
            >>> rules.can_place_on_foundation(two_hearts, empty)      # False
            >>> rules.can_place_on_foundation(two_hearts, pile_ace)   # True
            >>> rules.can_place_on_foundation(two_spades, pile_ace)   # False (different suit)
        """
        # CRITICAL: Empty foundation accepts only Aces
        if target_pile.is_empty():
            return card.get_value == 1
        
        # Non-empty foundation: get top card
        top_card = target_pile.get_top_card()
        if top_card is None:
            return False
        
        # Must be same suit AND ascend by 1
        return (
            card.get_suit == top_card.get_suit and
            card.get_value == top_card.get_value + 1
        )
    
    def is_foundation_complete(self, pile: Pile) -> bool:
        """Check if a foundation pile is complete.
        
        Complete = contains all cards from Ace to King for one suit.
        King value is deck-dependent:
        - French deck: King = 13
        - Neapolitan deck: Re = 10
        
        Args:
            pile: Foundation pile to check
            
        Returns:
            True if foundation has all cards up to King
        """
        if pile.is_empty():
            return False
        
        top_card = pile.get_top_card()
        if top_card is None:
            return False
        
        # Top card must be the King (max value for this deck)
        king_value = self.deck.FIGURE_VALUES.get("Re")
        if king_value is None:
            return False
        
        return top_card.get_value == king_value
    
    # ========================================
    # GAME STATE RULES
    # ========================================
    
    def is_victory(self, foundation_piles: List[Pile]) -> bool:
        """Check if the game is won.
        
        Victory condition: all 4 foundation piles are complete.
        Each foundation must have all cards from Ace to King.
        
        Args:
            foundation_piles: List of 4 foundation piles
            
        Returns:
            True if game is won
            
        Examples:
            >>> rules.is_victory([complete1, complete2, complete3, complete4])  # True
            >>> rules.is_victory([complete1, complete2, complete3, empty])      # False
        """
        # Must have exactly 4 foundations
        if len(foundation_piles) != 4:
            return False
        
        # All 4 must be complete
        return all(self.is_foundation_complete(pile) for pile in foundation_piles)
    
    # ========================================
    # STOCK & WASTE RULES (Tallone)
    # ========================================
    
    def can_draw_from_stock(self, stock: Pile) -> bool:
        """Check if cards can be drawn from stock.
        
        Args:
            stock: Stock pile (tallone coperto)
            
        Returns:
            True if stock has cards to draw
        """
        return not stock.is_empty()
    
    def can_recycle_waste(self, waste: Pile, stock: Pile) -> bool:
        """Check if waste can be recycled back to stock.
        
        Rules:
        - Stock must be empty (no more cards to draw)
        - Waste must have cards (something to recycle)
        
        Args:
            waste: Waste pile (tallone scoperto)
            stock: Stock pile (tallone coperto)
            
        Returns:
            True if waste can be recycled to stock
        """
        return stock.is_empty() and not waste.is_empty()
    
    # ========================================
    # UTILITY METHODS
    # ========================================
    
    def get_movable_cards_from_pile(self, pile: Pile) -> List[Card]:
        """Get all cards that can be moved from a tableau pile.
        
        Returns the longest valid sequence of face-up cards from the pile.
        
        Args:
            pile: Tableau pile to analyze
            
        Returns:
            List of movable cards (empty if none)
        """
        if pile.is_empty():
            return []
        
        all_cards = pile.get_all_cards()
        
        # Find first uncovered card
        first_uncovered_idx = -1
        for i, card in enumerate(all_cards):
            if not card.get_covered:
                first_uncovered_idx = i
                break
        
        if first_uncovered_idx == -1:
            return []  # No uncovered cards
        
        # Get sequence from first uncovered to end
        sequence = all_cards[first_uncovered_idx:]
        
        # Validate sequence
        if self._is_valid_tableau_sequence(sequence):
            return sequence
        
        return []
