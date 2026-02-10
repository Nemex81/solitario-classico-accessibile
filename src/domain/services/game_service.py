"""Domain service for game state management and gameplay orchestration.

Coordinates game logic using domain models (GameTable, Card, Pile) and
rules (SolitaireRules). Maintains game state including move count,
timer, and score tracking.
"""

from typing import Optional, List, Tuple, Dict, Any
import time

from src.domain.models.table import GameTable
from src.domain.models.card import Card
from src.domain.models.pile import Pile
from src.domain.rules.solitaire_rules import SolitaireRules


class GameService:
    """Core game logic service with state management.
    
    Orchestrates gameplay by:
    - Validating moves using SolitaireRules
    - Executing state changes on GameTable
    - Tracking game statistics (moves, time, score)
    - Checking win/loss conditions
    
    Attributes:
        table: The game table with all piles
        rules: Game rules validator
        is_game_running: Flag indicating if game is active
        move_count: Number of moves made
        start_time: Game start timestamp (None if not started)
        draw_count: Number of times drawn from stock
    """
    
    def __init__(self, table: GameTable, rules: SolitaireRules):
        """Initialize game service.
        
        Args:
            table: GameTable instance with initialized piles
            rules: SolitaireRules for move validation
        """
        self.table = table
        self.rules = rules
        self.is_game_running = False
        self.move_count = 0
        self.start_time: Optional[float] = None
        self.draw_count = 0
    
    # ========================================
    # GAME LIFECYCLE
    # ========================================
    
    def start_game(self) -> None:
        """Start the game timer and set running flag."""
        self.is_game_running = True
        if self.start_time is None:
            self.start_time = time.time()
    
    def reset_game(self) -> None:
        """Reset game state for new game."""
        self.is_game_running = False
        self.move_count = 0
        self.start_time = None
        self.draw_count = 0
    
    def get_elapsed_time(self) -> float:
        """Get elapsed game time in seconds.
        
        Returns:
            Elapsed seconds, or 0.0 if game not started
        """
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time
    
    # ========================================
    # CARD MOVEMENT
    # ========================================
    
    def move_card(
        self,
        source_pile: Pile,
        target_pile: Pile,
        card_count: int = 1,
        is_foundation_target: bool = False
    ) -> Tuple[bool, str]:
        """Move card(s) from source to target pile.
        
        Args:
            source_pile: Pile to take cards from
            target_pile: Pile to place cards on
            card_count: Number of cards to move (for tableau sequences)
            is_foundation_target: True if target is foundation pile
            
        Returns:
            Tuple of (success: bool, message: str)
            
        Examples:
            >>> success, msg = service.move_card(tableau1, tableau2, 1)
            >>> if success:
            ...     print(msg)  # "Carta spostata con successo"
        """
        # Validate source pile has cards
        if source_pile.is_empty():
            return False, "Pila di origine vuota"
        
        # Get card(s) to move
        if card_count == 1:
            card = source_pile.get_top_card()
            if card is None:
                return False, "Nessuna carta disponibile"
            
            # Validate move
            if is_foundation_target:
                if not self.rules.can_place_on_foundation(card, target_pile):
                    return False, "Mossa non valida per fondazione"
            else:
                if not self.rules.can_place_on_tableau(card, target_pile):
                    return False, "Mossa non valida per tableau"
            
            # Execute move
            source_pile.remove_last_card()
            target_pile.aggiungi_carta(card)
            
        else:
            # Moving sequence (only for tableau)
            cards = self._get_movable_sequence(source_pile, card_count)
            if not cards:
                return False, "Sequenza non valida"
            
            # Validate sequence move
            if not self.rules.can_move_sequence(cards, target_pile):
                return False, "Sequenza non può essere spostata"
            
            # Execute sequence move
            for _ in range(card_count):
                source_pile.remove_last_card()
            for card in cards:
                target_pile.aggiungi_carta(card)
        
        # Update game state
        self.move_count += 1
        self._uncover_top_card(source_pile)
        
        return True, f"Mossa eseguita (#{self.move_count})"
    
    def _get_movable_sequence(
        self,
        pile: Pile,
        count: int
    ) -> List[Card]:
        """Extract movable card sequence from pile.
        
        Args:
            pile: Source pile
            count: Number of cards in sequence
            
        Returns:
            List of cards in sequence (bottom to top), or empty if invalid
        """
        if count <= 0 or count > pile.get_card_count():
            return []
        
        # Get last N cards
        all_cards = pile.get_all_cards()
        sequence = all_cards[-count:]
        
        # All cards must be uncovered
        if any(card.get_covered for card in sequence):
            return []
        
        return sequence
    
    def _uncover_top_card(self, pile: Pile) -> None:
        """Uncover top card of pile if it's covered.
        
        Args:
            pile: Pile to check
        """
        if not pile.is_empty():
            top = pile.get_top_card()
            if top and top.get_covered:
                top.set_uncover()
    
    # ========================================
    # STOCK/WASTE MANAGEMENT
    # ========================================
    
    def draw_cards(self, count: int = 1) -> Tuple[bool, str, List[Card]]:
        """Draw cards from stock to waste pile.
        
        Args:
            count: Number of cards to draw (1 or 3)
            
        Returns:
            Tuple of (success, message, drawn_cards)
            
        Examples:
            >>> success, msg, cards = service.draw_cards(3)
            >>> if success:
            ...     print(f"Pescate {len(cards)} carte")
        """
        stock = self.table.pile_mazzo
        waste = self.table.pile_scarti
        
        if stock is None or waste is None:
            return False, "Pile tallone non inizializzate", []
        
        # Check if can draw
        if not self.rules.can_draw_from_stock(stock):
            # ✅ BUG #4 IMPROVEMENT: Better error message
            if waste.is_empty():
                # Both piles empty - true game over state
                return False, "Tallone e scarti vuoti - impossibile pescare", []
            else:
                # Only stock empty - should have been recycled by caller
                return False, "Tallone vuoto - riciclo automatico fallito", []
        
        # Draw cards
        drawn_cards: List[Card] = []
        for _ in range(min(count, stock.get_card_count())):
            card = stock.remove_last_card()
            if card:
                card.set_uncover()
                waste.aggiungi_carta(card)
                drawn_cards.append(card)
        
        self.draw_count += 1
        return True, f"Pescate {len(drawn_cards)} carte", drawn_cards
    
    def recycle_waste(
        self,
        shuffle: bool = False
    ) -> Tuple[bool, str]:
        """Recycle waste pile back to stock.
        
        Args:
            shuffle: If True, shuffle cards; if False, invert order
            
        Returns:
            Tuple of (success, message)
        """
        stock = self.table.pile_mazzo
        waste = self.table.pile_scarti
        
        if stock is None or waste is None:
            return False, "Pile tallone non inizializzate"
        
        # Check if can recycle
        if not self.rules.can_recycle_waste(waste, stock):
            return False, "Impossibile riciclare tallone"
        
        # Get all waste cards
        cards = waste.get_all_cards()
        waste.clear()
        
        # Cover all cards
        for card in cards:
            card.set_cover()
        
        if shuffle:
            # Shuffle (F5 toggle mode)
            import random
            random.shuffle(cards)
        else:
            # Invert order (default)
            cards.reverse()
        
        # Move to stock
        for card in cards:
            stock.aggiungi_carta(card)
        
        return True, f"Tallone riciclato ({len(cards)} carte)"
    
    # ========================================
    # AUTO-MOVE LOGIC
    # ========================================
    
    def auto_move_to_foundation(self) -> Tuple[bool, str, Optional[Card]]:
        """Attempt automatic move from tableau/waste to foundation.
        
        Finds the first valid card that can be automatically moved to
        a foundation pile following game rules.
        
        Returns:
            Tuple of (success, message, moved_card)
        """
        # Check waste pile first
        if self.table.pile_scarti and not self.table.pile_scarti.is_empty():
            card = self.table.pile_scarti.get_top_card()
            if card:
                for foundation in self.table.pile_semi:
                    if self.rules.can_place_on_foundation(card, foundation):
                        self.table.pile_scarti.remove_last_card()
                        foundation.aggiungi_carta(card)
                        self.move_count += 1
                        return True, "Carta spostata automaticamente", card
        
        # Check tableau piles
        for tableau_pile in self.table.pile_base:
            if tableau_pile.is_empty():
                continue
            
            card = tableau_pile.get_top_card()
            if card and not card.get_covered:
                for foundation in self.table.pile_semi:
                    if self.rules.can_place_on_foundation(card, foundation):
                        tableau_pile.remove_last_card()
                        foundation.aggiungi_carta(card)
                        self.move_count += 1
                        self._uncover_top_card(tableau_pile)
                        return True, "Carta spostata automaticamente", card
        
        return False, "Nessuna mossa automatica disponibile", None
    
    # ========================================
    # GAME STATUS CHECKS
    # ========================================
    
    def check_game_over(self) -> Tuple[bool, str]:
        """Check if game is won or lost.
        
        Returns:
            Tuple of (is_game_over, status_message)
            - (True, "Vittoria!") if all foundations complete
            - (True, "Tempo scaduto") if timer expired
            - (False, "In corso") if still playable
        """
        # Check victory
        if self.rules.is_victory(self.table.pile_semi):
            elapsed = self.get_elapsed_time()
            return True, f"Vittoria! Completato in {int(elapsed)}s con {self.move_count} mosse"
        
        # Game continues
        return False, "Partita in corso"
    
    def is_victory(self) -> bool:
        """Quick check if game is won.
        
        Returns:
            True if all 4 foundation piles are complete
        """
        return self.rules.is_victory(self.table.pile_semi)
    
    # ========================================
    # STATISTICS
    # ========================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current game statistics.
        
        Returns:
            Dictionary with game stats:
            - move_count: Number of moves
            - elapsed_time: Time in seconds
            - draw_count: Times drawn from stock
            - foundation_progress: Cards in foundations per suit
        """
        foundation_progress = []
        for pile in self.table.pile_semi:
            foundation_progress.append(pile.get_card_count())
        
        return {
            "move_count": self.move_count,
            "elapsed_time": self.get_elapsed_time(),
            "draw_count": self.draw_count,
            "foundation_progress": foundation_progress,
            "total_foundation_cards": sum(foundation_progress)
        }
