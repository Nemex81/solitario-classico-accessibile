"""Cursor navigation manager for game table.

Handles cursor position tracking and navigation across all piles
with validation and feedback messages for screen reader.

v1.5.0: Extended navigation methods to return (message, hint) tuples
for conditional hint vocalization feature.

Migrated logic from: scr/game_engine.py (cursor methods)
"""

from typing import Tuple, Optional, Dict, Any
from src.domain.models.table import GameTable
from src.domain.models.card import Card
from src.domain.models.pile import Pile


class CursorManager:
    """Manages cursor position and navigation on game table.
    
    Tracks cursor position as (card_index, pile_index) and provides
    methods for navigation with automatic position validation.
    
    Pile indices:
    - 0-6: Tableau (base) piles
    - 7-10: Foundation (semi) piles
    - 11: Waste (scarti) pile
    - 12: Stock (mazzo) pile
    
    Attributes:
        table: Game table reference
        card_idx: Current card index within pile (0-based)
        pile_idx: Current pile index (0-12)
        last_quick_pile: Last pile accessed via quick jump (for double-tap)
    """
    
    def __init__(self, table: GameTable):
        """Initialize cursor manager.
        
        Args:
            table: Game table to navigate
        """
        self.table = table
        self.card_idx = 0
        self.pile_idx = 0
        self.last_quick_pile: Optional[int] = None
    
    def get_position(self) -> Tuple[int, int]:
        """Get current cursor position.
        
        Returns:
            Tuple of (card_index, pile_index)
        """
        return (self.card_idx, self.pile_idx)
    
    def get_current_pile(self) -> Pile:
        """Get pile at current cursor position.
        
        Returns:
            Current Pile instance
        """
        return self.table.pile[self.pile_idx]
    
    def get_card_at_cursor(self) -> Optional[Card]:
        """Get card at current cursor position.
        
        Returns:
            Card instance or None if pile empty or invalid position
        """
        pile = self.get_current_pile()
        if pile.is_empty():
            return None
        
        if self.card_idx < 0 or self.card_idx >= len(pile.cards):
            return None
        
        return pile.cards[self.card_idx]
    
    def validate_position(self) -> None:
        """Validate and auto-correct cursor position.
        
        Ensures cursor points to valid pile and card indices.
        Corrects out-of-bounds values automatically.
        """
        # Validate pile index
        if self.pile_idx < 0 or self.pile_idx >= len(self.table.pile):
            self.pile_idx = 0
        
        # Validate card index
        pile = self.get_current_pile()
        if pile.is_empty():
            self.card_idx = 0
        elif self.card_idx >= len(pile.cards):
            self.card_idx = len(pile.cards) - 1
        elif self.card_idx < 0:
            self.card_idx = 0
    
    def move_to_top_card(self) -> int:
        """Move cursor to top card of current pile.
        
        Returns:
            New card index (last card or 0 if empty)
        """
        pile = self.get_current_pile()
        if not pile.is_empty():
            self.card_idx = len(pile.cards) - 1
        else:
            self.card_idx = 0
        return self.card_idx
    
    # === NAVIGATION METHODS ===
    
    def move_up(self) -> Tuple[str, Optional[str]]:
        """Move cursor up (previous card in pile).
        
        Supported on tableau and waste piles.
        
        Returns:
            Tuple[str, Optional[str]]: (message, hint)
            - message: Feedback for screen reader
            - hint: Optional command hint (v1.5.0)
        """
        self.last_quick_pile = None  # Reset double-tap tracking
        pile = self.get_current_pile()
        
        # Tableau piles
        if self.pile_idx <= 6:
            if pile.is_empty():
                self.card_idx = 0
                return ("La pila è vuota!\n", None)
            
            self.validate_position()
            
            if self.card_idx > 0:
                self.card_idx -= 1
                card = pile.cards[self.card_idx]
                message = f"{self.card_idx + 1}: {card.get_name}\n"
                
                # Generate hint: suggest selection if card is selectable (uncovered)
                if not card.get_covered:
                    hint = f"Premi INVIO per selezionare {card.get_name}."
                else:
                    hint = None
                
                return (message, hint)
            else:
                return ("Sei già alla prima carta della pila!\n", None)
        
        # Waste pile
        elif self.pile_idx == 11:
            if pile.is_empty():
                return ("Scarti vuoti, nessuna carta da consultare.\n", None)
            
            self.validate_position()
            
            if self.card_idx > 0:
                self.card_idx -= 1
                card = pile.cards[self.card_idx]
                total = len(pile.cards)
                is_last = (self.card_idx == total - 1)
                message = f"{self.card_idx + 1} di {total}: {card.get_name}\n"
                
                # Hint only for last card (selectable)
                hint = "Premi CTRL+INVIO per selezionare." if is_last else None
                
                return (message, hint)
            else:
                return ("Sei già alla prima carta degli scarti!\n", None)
        
        # Other piles not navigable
        else:
            return ("Questa pila non è consultabile con le frecce.\n", None)
    
    def move_down(self) -> Tuple[str, Optional[str]]:
        """Move cursor down (next card in pile).
        
        Supported on tableau and waste piles.
        
        Returns:
            Tuple[str, Optional[str]]: (message, hint)
            - message: Feedback for screen reader
            - hint: Optional command hint (v1.5.0)
        """
        self.last_quick_pile = None
        pile = self.get_current_pile()
        
        # Tableau piles
        if self.pile_idx <= 6:
            if pile.is_empty():
                self.card_idx = 0
                return ("La pila è vuota!\n", None)
            
            self.validate_position()
            
            if self.card_idx < len(pile.cards) - 1:
                self.card_idx += 1
                card = pile.cards[self.card_idx]
                message = f"{self.card_idx + 1}: {card.get_name}\n"
                
                # Generate hint: suggest selection if card is selectable (uncovered)
                if not card.get_covered:
                    hint = f"Premi INVIO per selezionare {card.get_name}."
                else:
                    hint = None
                
                return (message, hint)
            else:
                return ("Sei già all'ultima carta della pila!\n", None)
        
        # Waste pile
        elif self.pile_idx == 11:
            if pile.is_empty():
                return ("Scarti vuoti, nessuna carta da consultare.\n", None)
            
            self.validate_position()
            
            if self.card_idx < len(pile.cards) - 1:
                self.card_idx += 1
                card = pile.cards[self.card_idx]
                total = len(pile.cards)
                is_last = (self.card_idx == total - 1)
                message = f"{self.card_idx + 1} di {total}: {card.get_name}\n"
                
                # Hint only for last card (selectable)
                hint = "Premi CTRL+INVIO per selezionare." if is_last else None
                
                return (message, hint)
            else:
                return ("Sei già all'ultima carta degli scarti!\n", None)
        
        else:
            return ("Questa pila non è consultabile con le frecce.\n", None)
    
    def move_left(self) -> Tuple[str, Optional[str]]:
        """Move cursor left (previous pile).
        
        Returns:
            Tuple[str, Optional[str]]: (message, hint)
            - message: Feedback with new pile info
            - hint: Navigation hint (v1.5.0)
        """
        self.last_quick_pile = None
        
        if self.pile_idx > 0:
            self.pile_idx -= 1
            self.validate_position()
            self.move_to_top_card()
            message = self._get_pile_summary()
            hint = "Usa frecce SU/GIÙ per consultare le altre carte della pila."
            return (message, hint)
        else:
            return ("Sei già alla prima pila!\n", None)
    
    def move_right(self) -> Tuple[str, Optional[str]]:
        """Move cursor right (next pile).
        
        Returns:
            Tuple[str, Optional[str]]: (message, hint)
            - message: Feedback with new pile info
            - hint: Navigation hint (v1.5.0)
        """
        self.last_quick_pile = None
        
        if self.pile_idx < len(self.table.pile) - 1:
            self.pile_idx += 1
            self.validate_position()
            self.move_to_top_card()
            message = self._get_pile_summary()
            hint = "Usa frecce SU/GIÙ per consultare le altre carte della pila."
            return (message, hint)
        else:
            return ("Sei già all'ultima pila!\n", None)
    
    def move_tab(self) -> Tuple[str, Optional[str]]:
        """Jump to next pile of different type (TAB key).
        
        Returns:
            Tuple[str, Optional[str]]: (message, hint)
            - message: Feedback with new pile type
            - hint: TAB navigation hint (v1.5.0)
        """
        self.last_quick_pile = None
        current_pile = self.get_current_pile()
        current_type = current_pile.pile_type
        
        # Search for next pile with different type
        for i in range(self.pile_idx + 1, len(self.table.pile)):
            pile = self.table.pile[i]
            if pile.pile_type != current_type:
                self.pile_idx = i
                self.move_to_top_card()
                message = f"Pile {pile.pile_type}: {self._get_pile_summary()}"
                hint = "Premi TAB ancora per passare al prossimo tipo di pila."
                return (message, hint)
        
        # Wrap to beginning (tableau piles)
        self.pile_idx = 0
        self.move_to_top_card()
        message = f"Pile base: {self._get_pile_summary()}"
        hint = "Premi TAB ancora per passare al prossimo tipo di pila."
        return (message, hint)
    
    def move_home(self) -> str:
        """Jump to first card of current pile (HOME key).
        
        Returns:
            Feedback message
        """
        self.last_quick_pile = None
        pile = self.get_current_pile()
        
        # Supported on tableau and waste
        if self.pile_idx <= 6 or self.pile_idx == 11:
            if pile.is_empty():
                return "La pila è vuota!\n"
            
            self.card_idx = 0
            card = pile.cards[0]
            
            if self.pile_idx == 11:
                total = len(pile.cards)
                return f"1 di {total}: {card.get_name} Prima carta.\n"
            else:
                return f"1: {card.get_name} Prima carta.\n"
        
        elif self.pile_idx == 12:
            return "Il mazzo non è consultabile.\n"
        else:
            return "Pile semi non consultabili. Usa SHIFT+(1-4) per accesso rapido.\n"
    
    def move_end(self) -> str:
        """Jump to last card of current pile (END key).
        
        Returns:
            Feedback message
        """
        self.last_quick_pile = None
        pile = self.get_current_pile()
        
        # Supported on tableau and waste
        if self.pile_idx <= 6 or self.pile_idx == 11:
            if pile.is_empty():
                return "La pila è vuota!\n"
            
            self.card_idx = len(pile.cards) - 1
            card = pile.cards[-1]
            
            if self.pile_idx == 11:
                total = len(pile.cards)
                hint = " Premi CTRL+INVIO per selezionare."
                return f"{total} di {total}: {card.get_name} Ultima carta.{hint}\n"
            else:
                return f"{len(pile.cards)}: {card.get_name} Ultima carta.\n"
        
        elif self.pile_idx == 12:
            return "Il mazzo non è consultabile.\n"
        else:
            return "Pile semi non consultabili. Usa SHIFT+(1-4) per accesso rapido.\n"
    
    def jump_to_pile(self, pile_idx: int, enable_double_tap: bool = True) -> Tuple[str, bool, Optional[str]]:
        """Jump to specific pile with optional double-tap auto-selection.
        
        Args:
            pile_idx: Target pile index (0-12)
                - 0-6: Tableau (base) piles
                - 7-10: Foundation (semi) piles
                - 11: Waste (scarti) pile
                - 12: Stock (mazzo) pile
            enable_double_tap: Enable double-tap detection for auto-selection
        
        Returns:
            Tuple of (feedback_message, should_auto_select, hint)
            - feedback_message: String for screen reader announcement
            - should_auto_select: True if second tap should trigger automatic card selection
            - hint: Optional command hint (v1.5.0)
        
        Behavior:
            First tap: Move cursor to pile top card + announce + hint
            Second tap (tableau/foundation): Auto-select top card (empty message + flag True)
            Second tap (stock/waste): No action (hint message + flag False)
        """
        if pile_idx < 0 or pile_idx >= len(self.table.pile):
            return ("Indice pila non valido!\n", False, None)
        
        # ═══════════════════════════════════════════════════════════
        # 🔥 DOUBLE-TAP DETECTION: Second press on same pile
        # ═══════════════════════════════════════════════════════════
        if enable_double_tap and self.pile_idx == pile_idx and self.last_quick_pile == pile_idx:
            pile = self.table.pile[pile_idx]
            
            # ─────────────────────────────────────────────────────
            # Stock/Waste: Disable auto-selection (hint only)
            # ─────────────────────────────────────────────────────
            if pile_idx >= 11:
                self.last_quick_pile = None
                return ("Cursore già sulla pila.\n", False, None)
            
            # ─────────────────────────────────────────────────────
            # Tableau/Foundation: Enable auto-selection
            # ─────────────────────────────────────────────────────
            if pile.is_empty():
                self.last_quick_pile = None
                return ("Pila vuota, nessuna carta da selezionare.\n", False, None)
            
            # ✅ Position cursor on top card BEFORE signaling selection
            self.move_to_top_card()
            
            # ✅ Signal GameEngine to execute automatic selection
            # Empty message because selection feedback will be announced by GameEngine
            self.last_quick_pile = None
            return ("", True, None)
        
        # ═══════════════════════════════════════════════════════════
        # 🎯 FIRST TAP: Move cursor and announce pile info + hint
        # ═══════════════════════════════════════════════════════════
        self.pile_idx = pile_idx
        self.move_to_top_card()
        self.last_quick_pile = pile_idx if enable_double_tap else None
        
        msg = self._get_pile_summary()
        hint = None
        
        # ─────────────────────────────────────────────────────
        # Generate context-specific hints (v1.5.0)
        # ─────────────────────────────────────────────────────
        pile = self.get_current_pile()
        
        if pile_idx == 12 and not pile.is_empty():
            # Stock pile hint
            hint = "Premi INVIO per pescare."
            
        elif pile_idx == 11 and not pile.is_empty():
            # Waste pile hint
            hint = "Usa frecce per navigare. CTRL+INVIO per selezionare ultima carta."
            
        elif not pile.is_empty() and pile_idx <= 10:
            # Tableau/Foundation piles: double-tap hint
            card_name = pile.cards[-1].get_name
            
            if pile_idx <= 6:
                # Tableau (base) piles: number 1-7
                hint = f"Premi ancora {pile_idx + 1} per selezionare {card_name}."
            else:
                # Foundation (semi) piles: SHIFT+1-4
                seme_num = pile_idx - 6
                hint = f"Premi ancora SHIFT+{seme_num} per selezionare {card_name}."
        
        return (msg, False, hint)  # No auto-selection on first tap
    
    # === INFO METHODS ===
    
    def get_position_info(self) -> str:
        """Get detailed info about current cursor position.
        
        Returns:
            Formatted string for screen reader
        """
        pile = self.get_current_pile()
        card = self.get_card_at_cursor()
        
        msg = f"{pile.name}. "
        
        if pile.is_empty():
            msg += "La pila è vuota!\n"
        elif card:
            msg += f"{self.card_idx + 1}: {card.get_name}\n"
        else:
            msg += "Posizione non valida!\n"
        
        return msg
    
    def get_card_details(self) -> str:
        """Get detailed info about card at cursor.
        
        Returns:
            Card information formatted for screen reader
        """
        pile = self.get_current_pile()
        card = self.get_card_at_cursor()
        
        if not card:
            return "Non riesco ad identificare la carta alle coordinate specificate\n"
        
        info = f"Scheda carta:\n"
        info += f"Nome: {card.get_name}\n"
        info += f"Seme: {card.get_suit}\n"
        info += f"Valore: {card.get_value}\n"
        info += f"Stato: {'coperta' if card.get_covered else 'scoperta'}\n"
        info += f"Genitore: {pile.name}\n"
        info += f"Posizione in pila: {self.card_idx + 1}\n"
        
        return info
    
    def _get_pile_summary(self) -> str:
        """Get summary of current pile (name + top card).
        
        Returns:
            Formatted string for screen reader
        """
        pile = self.get_current_pile()
        msg = f"{pile.name}. "
        
        if pile.is_empty():
            msg += "La pila è vuota!\n"
        else:
            top_card = pile.cards[-1]
            msg += f"Carta in cima: {top_card.get_name}\n"
        
        return msg
