"""Selection manager for card selection and move preparation.

Handles card selection, multi-card sequences, and move validation
preparation. Works with CursorManager to enable gameplay actions.

Migrated logic from: scr/game_engine.py (selection methods)
"""

from typing import List, Optional
from src.domain.models.card import Card
from src.domain.models.pile import Pile


class SelectionManager:
    """Manages card selection and move validation preparation.
    
    Tracks selected cards, origin pile, and provides methods for
    selection/deselection with validation.
    
    Attributes:
        selected_cards: List of currently selected cards
        origin_pile: Pile where selection originated
        target_card: First card in selection (for validation)
    """
    
    def __init__(self):
        """Initialize selection manager."""
        self.selected_cards: List[Card] = []
        self.origin_pile: Optional[Pile] = None
        self.target_card: Optional[Card] = None
    
    def has_selection(self) -> bool:
        """Check if any cards are selected.
        
        Returns:
            True if cards selected, False otherwise
        """
        return len(self.selected_cards) > 0
    
    def clear_selection(self) -> str:
        """Clear current selection.
        
        Returns:
            Feedback message
        """
        if not self.has_selection():
            return "Non hai selezionato nessuna carta!\n"
        
        self.selected_cards = []
        self.origin_pile = None
        self.target_card = None
        return "Annullo carte selezionate!\n"
    
    def select_card_sequence(self, pile: Pile, card_idx: int) -> str:
        """Select card and all cards above it in pile.
        
        Args:
            pile: Source pile
            card_idx: Index of first card to select
        
        Returns:
            Feedback message with selected cards
        """
        if self.has_selection():
            return "Hai già selezionato le carte da spostare! Premi CANC per annullare.\n"
        
        if pile.is_empty():
            return "La pila è vuota!\n"
        
        if card_idx < 0 or card_idx >= len(pile.cards):
            return "Indice carta non valido!\n"
        
        card = pile.cards[card_idx]
        
        # Cannot select covered card
        if card.covered:
            return "Non puoi selezionare una carta coperta!\n"
        
        # Select card and all above it
        self.selected_cards = pile.cards[card_idx:]
        self.origin_pile = pile
        self.target_card = card
        
        count = len(self.selected_cards)
        msg = f"Carte selezionate: {count}\n"
        
        for c in self.selected_cards:
            msg += f"{c.name}, "
        
        return msg[:-2] + "!\n"  # Remove trailing comma
    
    def select_top_card_from_waste(self, waste_pile: Pile) -> str:
        """Select top card from waste pile (CTRL+ENTER).
        
        Args:
            waste_pile: Waste pile
        
        Returns:
            Feedback message
        """
        if self.has_selection():
            return "Hai già selezionato le carte da spostare! Premi CANC per annullare.\n"
        
        if waste_pile.is_empty():
            return "La pila scarti è vuota!\n"
        
        top_card = waste_pile.cards[-1]
        self.selected_cards = [top_card]
        self.origin_pile = waste_pile
        self.target_card = top_card
        
        return f"Carta selezionata: {top_card.name}!\n"
    
    def get_selection_info(self) -> str:
        """Get info about current selection.
        
        Returns:
            Formatted selection details
        """
        if not self.has_selection():
            return "Nessuna carta selezionata\n"
        
        count = len(self.selected_cards)
        msg = f"Carte selezionate: {count}\n"
        msg += f"Carta target: {self.target_card.name}\n"
        msg += f"Valore: {self.target_card.value}\n"
        
        if self.origin_pile:
            msg += f"Origine: {self.origin_pile.name}\n"
        
        return msg
    
    def can_move_to(self, dest_pile: Pile) -> bool:
        """Quick check if move to destination might be valid.
        
        Note: This is a preliminary check. Full validation happens
        in GameService/SolitaireRules.
        
        Args:
            dest_pile: Destination pile
        
        Returns:
            True if move seems possible, False otherwise
        """
        if not self.has_selection():
            return False
        
        if not self.target_card:
            return False
        
        # Can't move to same pile
        if dest_pile == self.origin_pile:
            return False
        
        return True  # Let rules validate details
