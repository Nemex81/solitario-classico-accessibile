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
from src.domain.services.scoring_service import ScoringService
from src.domain.models.scoring import ScoreEventType


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
        scoring: Optional scoring service for tracking points
    """
    
    def __init__(
        self, 
        table: GameTable, 
        rules: SolitaireRules,
        scoring: Optional[ScoringService] = None
    ):
        """Initialize game service.
        
        Args:
            table: GameTable instance with initialized piles
            rules: SolitaireRules for move validation
            scoring: Optional scoring service for tracking points
        """
        self.table = table
        self.rules = rules
        self.is_game_running = False
        self.move_count = 0
        self.start_time: Optional[float] = None
        self.draw_count = 0
        self.scoring = scoring
    
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
        if self.scoring:
            self.scoring.reset()
    
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
            
            # Check if source pile will reveal a card after move
            will_reveal_card = (
                source_pile.get_card_count() > 1 and
                len([c for c in source_pile.get_all_cards()[:-1] if not c.get_covered]) == 0
            )
            
            # Execute move
            source_pile.remove_last_card()
            target_pile.aggiungi_carta(card)
            
            # Record scoring events
            if self.scoring and is_foundation_target:
                # Check if source is waste or tableau
                if source_pile == self.table.pile_scarti:
                    self.scoring.record_event(
                        ScoreEventType.WASTE_TO_FOUNDATION,
                        f"{card}"
                    )
                elif source_pile in self.table.pile_base:
                    self.scoring.record_event(
                        ScoreEventType.TABLEAU_TO_FOUNDATION,
                        f"{card}"
                    )
            
        else:
            # Moving sequence (only for tableau)
            cards = self._get_movable_sequence(source_pile, card_count)
            if not cards:
                return False, "Sequenza non valida"
            
            # Validate sequence move
            if not self.rules.can_move_sequence(cards, target_pile):
                return False, "Sequenza non può essere spostata"
            
            # Check if source pile will reveal a card after move
            will_reveal_card = (
                source_pile.get_card_count() > card_count and
                len([c for c in source_pile.get_all_cards()[:-card_count] if not c.get_covered]) == 0
            )
            
            # Execute sequence move
            for _ in range(card_count):
                source_pile.remove_last_card()
            for card in cards:
                target_pile.aggiungi_carta(card)
        
        # Update game state
        self.move_count += 1
        
        # Check if a card was revealed
        card_was_revealed = False
        if not source_pile.is_empty():
            top = source_pile.get_top_card()
            if top and top.get_covered:
                top.set_uncover()
                card_was_revealed = True
        
        # Record card revealed event
        if self.scoring and card_was_revealed:
            self.scoring.record_event(
                ScoreEventType.CARD_REVEALED,
                f"{source_pile.get_top_card()}"
            )
        
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
        
        # Record scoring event
        if self.scoring:
            self.scoring.record_event(ScoreEventType.RECYCLE_WASTE)
        
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
    
    # ========================================
    # INFO METHODS WITH HINTS (v1.5.0)
    # ========================================
    
    def get_waste_info(self) -> Tuple[str, Optional[str]]:
        """Get waste pile info with navigation hint.
        
        Returns:
            Tuple[str, Optional[str]]: (message, hint)
            - message: Current waste pile status
            - hint: Navigation command hint (v1.5.0)
        
        Examples:
            >>> message, hint = service.get_waste_info()
            >>> # message: "Scarti: 8 carte. Carta in cima: Nove di Cuori."
            >>> # hint: "Usa SHIFT+S per muovere il cursore sugli scarti."
        """
        waste_pile = self.table.pile_scarti
        
        if waste_pile.is_empty():
            message = "Pila scarti vuota."
            hint = None
        else:
            count = waste_pile.get_card_count()
            top_card = waste_pile.get_top_card()
            card_name = top_card.get_name if top_card else "sconosciuta"
            
            if count == 1:
                message = f"Scarti: 1 carta. Carta in cima: {card_name}."
            else:
                message = f"Scarti: {count} carte. Carta in cima: {card_name}."
            
            hint = "Usa SHIFT+S per muovere il cursore sugli scarti."
        
        return (message, hint)
    
    def get_stock_info(self) -> Tuple[str, Optional[str]]:
        """Get stock pile info with draw hint.
        
        Returns:
            Tuple[str, Optional[str]]: (message, hint)
            - message: Remaining cards in stock
            - hint: Draw command hint (v1.5.0)
        
        Examples:
            >>> message, hint = service.get_stock_info()
            >>> # message: "Mazzo riserve: 12 carte rimanenti."
            >>> # hint: "Premi D o P per pescare una carta."
        """
        stock_pile = self.table.pile_mazzo
        count = stock_pile.get_card_count()
        
        if count == 0:
            message = "Il mazzo è vuoto."
            hint = None
        elif count == 1:
            message = "Rimane 1 carta nel mazzo."
            hint = "Premi D o P per pescare una carta."
        else:
            message = f"Rimangono {count} carte nel mazzo."
            hint = "Premi D o P per pescare una carta."
        
        return (message, hint)
    
    def get_game_report(self) -> Tuple[str, Optional[str]]:
        """Get complete game report (no hint - report is complete).
        
        Returns:
            Tuple[str, Optional[str]]: (message, None)
            - message: Complete game statistics
            - hint: None (report is self-contained)
        
        Examples:
            >>> message, hint = service.get_game_report()
            >>> # message: "Report partita. Mosse: 42. Tempo: 5:30. ..."
            >>> # hint: None
        """
        stats = self.get_statistics()
        elapsed = int(stats['elapsed_time'])
        minutes = elapsed // 60
        seconds = elapsed % 60
        time_str = f"{minutes}:{seconds:02d}"
        
        report = "Report partita.\n"
        report += f"Mosse: {stats['move_count']}.\n"
        report += f"Tempo trascorso: {time_str}.\n"
        report += f"Carte nelle pile semi: {stats['total_foundation_cards']}.\n"
        
        return (report, None)
    
    def get_table_info(self) -> Tuple[str, Optional[str]]:
        """Get complete table overview (no hint - info is complete).
        
        Returns:
            Tuple[str, Optional[str]]: (message, None)
            - message: Complete table state
            - hint: None (comprehensive info)
        
        Examples:
            >>> message, hint = service.get_table_info()
            >>> # message: "Panoramica tavolo. Pile base: 7 pile. ..."
            >>> # hint: None
        """
        message = "Panoramica tavolo.\n"
        
        # Base piles
        message += f"Pile base: {len(self.table.pile_base)} pile.\n"
        for i, pile in enumerate(self.table.pile_base):
            count = pile.get_card_count()
            message += f"Pila {i+1}: {count} carte. "
            if not pile.is_empty():
                top = pile.get_top_card()
                if top:
                    message += f"In cima: {top.get_name}.\n"
            else:
                message += "Vuota.\n"
        
        # Foundation piles
        message += f"Pile semi: {len(self.table.pile_semi)} pile.\n"
        for pile in self.table.pile_semi:
            count = pile.get_card_count()
            message += f"{pile.name}: {count} carte.\n"
        
        # Stock and waste
        stock_count = self.table.pile_mazzo.get_card_count()
        waste_count = self.table.pile_scarti.get_card_count()
        message += f"Mazzo: {stock_count} carte.\n"
        message += f"Scarti: {waste_count} carte.\n"
        
        return (message, None)
    
    def get_timer_info(self, max_time: Optional[int] = None) -> Tuple[str, Optional[str]]:
        """Get timer info - elapsed or countdown based on max_time (v1.5.1).
        
        Args:
            max_time: Maximum game time in seconds (optional)
                If None or <= 0: Shows elapsed time
                If > 0: Shows countdown (remaining time)
        
        Returns:
            Tuple[str, Optional[str]]: (message, hint)
            - message: Elapsed time or countdown
            - hint: None (no hint during gameplay per v1.5.1)
        
        Examples:
            >>> # Timer OFF
            >>> message, hint = service.get_timer_info(max_time=None)
            >>> # "Tempo trascorso: 5 minuti e 23 secondi."
            
            >>> # Timer ON (10 minutes = 600 seconds)
            >>> message, hint = service.get_timer_info(max_time=600)
            >>> # "Tempo rimanente: 4 minuti e 37 secondi."
            
            >>> # Timer expired
            >>> message, hint = service.get_timer_info(max_time=300)
            >>> # elapsed = 305, remaining = 0
            >>> # "Tempo scaduto!"
        """
        elapsed = int(self.get_elapsed_time())
        
        # Determine mode: countdown vs elapsed
        if max_time is not None and max_time > 0:
            # Timer attivo → countdown
            remaining = max(0, max_time - elapsed)  # Prevent negative
            minutes = remaining // 60
            seconds = remaining % 60
            
            if remaining > 0:
                message = f"Tempo rimanente: {minutes} minuti e {seconds} secondi."
            else:
                message = "Tempo scaduto!"
        else:
            # Timer disattivo → elapsed
            minutes = elapsed // 60
            seconds = elapsed % 60
            message = f"Tempo trascorso: {minutes} minuti e {seconds} secondi."
        
        # No hint during gameplay (v1.5.1 user request)
        return (message, None)
    
    def get_settings_info(self) -> Tuple[str, Optional[str]]:
        """Get settings summary with options menu hint.
        
        Returns:
            Tuple[str, Optional[str]]: (message, hint)
            - message: Current game settings summary
            - hint: Options menu hint (v1.5.0)
        
        Examples:
            >>> message, hint = service.get_settings_info()
            >>> # message: "Impostazioni di gioco. Mazzo: carte francesi. ..."
            >>> # hint: "Premi O per aprire il menu opzioni."
        """
        # Note: This will need to access actual settings when integrated
        message = "Impostazioni di gioco.\n"
        message += "Mazzo: carte francesi.\n"
        message += "Difficoltà: livello 1.\n"
        message += "Timer: disabilitato.\n"
        
        hint = "Premi O per aprire il menu opzioni."
        
        return (message, hint)
