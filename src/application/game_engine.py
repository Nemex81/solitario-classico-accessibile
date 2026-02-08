"""Game engine facade orchestrating all refactored layers.

Provides a clean interface for game initialization, move execution,
navigation, selection, and state management.

Extended with CursorManager and SelectionManager for gameplay.
"""

from typing import Optional, Tuple, Dict, Any, List

from src.domain.models.table import GameTable
from src.domain.models.deck import FrenchDeck
from src.domain.models.pile import Pile
from src.domain.models.card import Card
from src.domain.services.game_service import GameService
from src.domain.services.cursor_manager import CursorManager
from src.domain.services.selection_manager import SelectionManager
from src.domain.rules.solitaire_rules import SolitaireRules
from src.infrastructure.audio.screen_reader import ScreenReader
from src.infrastructure.audio.tts_provider import create_tts_provider


class GameEngine:
    """Facade for game orchestration.
    
    Coordinates all refactored components:
    - GameTable (domain model)
    - GameService (game logic orchestration)
    - SolitaireRules (rule validation)
    - CursorManager (navigation)
    - SelectionManager (card selection)
    - ScreenReader (audio feedback)
    
    Provides high-level API for:
    - Game initialization and reset
    - Cursor navigation
    - Card selection/deselection
    - Move execution with feedback
    - Game state queries
    - Statistics and progress tracking
    
    Attributes:
        table: Game table with all piles
        service: Game service for logic orchestration
        rules: Game rules validator
        cursor: Cursor navigation manager
        selection: Selection manager
        screen_reader: Audio feedback service (optional)
        audio_enabled: Whether audio feedback is active
    """
    
    def __init__(
        self,
        table: GameTable,
        service: GameService,
        rules: SolitaireRules,
        cursor: CursorManager,
        selection: SelectionManager,
        screen_reader: Optional[ScreenReader] = None
    ):
        """Initialize game engine.
        
        Args:
            table: Initialized game table
            service: Game service instance
            rules: Rules validator
            cursor: Cursor manager
            selection: Selection manager
            screen_reader: Optional screen reader for audio feedback
        """
        self.table = table
        self.service = service
        self.rules = rules
        self.cursor = cursor
        self.selection = selection
        self.screen_reader = screen_reader
        self.audio_enabled = screen_reader is not None
    
    @classmethod
    def create(
        cls,
        audio_enabled: bool = True,
        tts_engine: str = "auto",
        verbose: int = 1
    ) -> "GameEngine":
        """Factory method to create fully initialized game engine.
        
        Args:
            audio_enabled: Enable audio feedback
            tts_engine: TTS engine ("auto", "nvda", "sapi5")
            verbose: Audio verbosity level (0-2)
            
        Returns:
            Initialized GameEngine instance ready to play
            
        Example:
            >>> engine = GameEngine.create(audio_enabled=True)
            >>> engine.new_game()
            >>> success, msg = engine.move_card(source_idx=0, target_idx=7)
        """
        # Create domain components
        deck = FrenchDeck()
        deck.crea()
        deck.mischia()
        table = GameTable(deck)
        rules = SolitaireRules(deck)
        service = GameService(table, rules)
        cursor = CursorManager(table)
        selection = SelectionManager()
        
        # Create infrastructure (optional)
        screen_reader = None
        if audio_enabled:
            try:
                tts = create_tts_provider(tts_engine)
                screen_reader = ScreenReader(tts, enabled=True, verbose=verbose)
            except RuntimeError:
                # Graceful degradation if TTS not available
                screen_reader = None
        
        return cls(table, service, rules, cursor, selection, screen_reader)
    
    # ========================================
    # GAME LIFECYCLE
    # ========================================
    
    def new_game(self) -> None:
        """Start a new game.
        
        Resets game state, redistributes cards, and starts timer.
        """
        # Reset service state
        self.service.reset_game()
        
        # Gather all cards back to deck
        all_cards = []
        for pile in self.table.pile_base:
            all_cards.extend(pile.get_all_cards())
            pile.clear()
        for pile in self.table.pile_semi:
            all_cards.extend(pile.get_all_cards())
            pile.clear()
        if self.table.pile_mazzo:
            all_cards.extend(self.table.pile_mazzo.get_all_cards())
            self.table.pile_mazzo.clear()
        if self.table.pile_scarti:
            all_cards.extend(self.table.pile_scarti.get_all_cards())
            self.table.pile_scarti.clear()
        
        # Put cards back in deck and shuffle
        self.table.mazzo.cards = all_cards
        self.table.mazzo.mischia()
        
        # Redistribute cards
        self.table.distribuisci_carte()
        
        # Reset cursor/selection
        self.cursor.pile_idx = 0
        self.cursor.card_idx = 0
        self.cursor.last_quick_pile = None
        self.selection.clear_selection()
        
        # Start timer
        self.service.start_game()
        
        # Announce game start
        if self.screen_reader:
            self.screen_reader.tts.speak(
                "Nuova partita iniziata. Usa H per l'aiuto comandi.",
                interrupt=True
            )
    
    def reset_game(self) -> None:
        """Reset current game without redistributing cards."""
        self.service.reset_game()
        self.cursor.pile_idx = 0
        self.cursor.card_idx = 0
        self.cursor.last_quick_pile = None
        self.selection.clear_selection()
        
        if self.screen_reader:
            self.screen_reader.tts.speak("Partita resettata", interrupt=True)
    
    # ========================================
    # NAVIGATION METHODS (7)
    # ========================================
    
    def move_cursor(self, direction: str) -> str:
        """Move cursor in specified direction.
        
        Args:
            direction: "up", "down", "left", "right", "tab", "home", "end"
            
        Returns:
            Feedback message for screen reader
        """
        direction = direction.lower()
        
        if direction == "up":
            msg = self.cursor.move_up()
        elif direction == "down":
            msg = self.cursor.move_down()
        elif direction == "left":
            msg = self.cursor.move_left()
        elif direction == "right":
            msg = self.cursor.move_right()
        elif direction == "tab":
            msg = self.cursor.move_tab()
        elif direction == "home":
            msg = self.cursor.move_home()
        elif direction == "end":
            msg = self.cursor.move_end()
        else:
            msg = "Direzione non valida!\n"
        
        if self.screen_reader:
            self.screen_reader.tts.speak(msg, interrupt=True)
        
        return msg
    
    def jump_to_pile(self, pile_idx: int) -> str:
        """Jump to specific pile (1-7 for tableau, SHIFT+1-4 for foundations).
        
        Args:
            pile_idx: Pile index (0-12)
            
        Returns:
            Feedback message
        """
        msg = self.cursor.jump_to_pile(pile_idx, enable_double_tap=True)
        
        if self.screen_reader:
            self.screen_reader.tts.speak(msg, interrupt=True)
        
        return msg
    
    def get_cursor_position(self) -> Tuple[int, int]:
        """Get current cursor position.
        
        Returns:
            Tuple of (card_index, pile_index)
        """
        return self.cursor.get_position()
    
    def get_cursor_info(self) -> str:
        """Get detailed info about cursor position.
        
        Returns:
            Formatted position info
        """
        msg = self.cursor.get_position_info()
        
        if self.screen_reader:
            self.screen_reader.tts.speak(msg, interrupt=True)
        
        return msg
    
    def get_card_at_cursor(self) -> str:
        """Get detailed info about card at cursor.
        
        Returns:
            Card details formatted for screen reader
        """
        msg = self.cursor.get_card_details()
        
        if self.screen_reader:
            self.screen_reader.tts.speak(msg, interrupt=True)
        
        return msg
    
    def get_pile_at_cursor(self) -> str:
        """Get info about pile at cursor.
        
        Returns:
            Pile info
        """
        pile = self.cursor.get_current_pile()
        msg = f"Pila: {pile.name}\n"
        msg += f"Tipo: {pile.pile_type}\n"
        msg += f"Carte: {pile.get_card_count()}\n"
        
        if not pile.is_empty():
            top = pile.get_top_card()
            msg += f"In cima: {top.get_name}\n"
        
        if self.screen_reader:
            self.screen_reader.tts.speak(msg, interrupt=True)
        
        return msg
    
    def get_table_overview(self) -> str:
        """Get overview of all piles.
        
        Returns:
            Complete table status
        """
        msg = "Stato tavolo:\n"
        
        # Tableau
        msg += "Pile base:\n"
        for i, pile in enumerate(self.table.pile_base):
            if not pile.is_empty():
                top = pile.get_top_card()
                msg += f"  Pila {i+1}: {top.get_name}\n"
            else:
                msg += f"  Pila {i+1}: vuota\n"
        
        # Foundations
        msg += "Pile semi:\n"
        for i, pile in enumerate(self.table.pile_semi):
            count = pile.get_card_count()
            msg += f"  Seme {i+1}: {count} carte\n"
        
        # Stock/Waste
        msg += f"Mazzo: {self.table.pile_mazzo.get_card_count()} carte\n"
        msg += f"Scarti: {self.table.pile_scarti.get_card_count()} carte\n"
        
        if self.screen_reader:
            self.screen_reader.tts.speak(msg, interrupt=True)
        
        return msg
    
    # ========================================
    # SELECTION METHODS (5)
    # ========================================
    
    def select_card_at_cursor(self) -> Tuple[bool, str]:
        """Select card at current cursor position.
        
        Returns:
            Tuple of (success, message)
        """
        pile = self.cursor.get_current_pile()
        card_idx, pile_idx = self.cursor.get_position()
        
        # Stock: draw cards
        if pile_idx == 12:
            return self.draw_from_stock()
        
        # Empty pile
        if pile.is_empty():
            msg = "La pila è vuota!\n"
            if self.screen_reader:
                self.screen_reader.tts.speak(msg, interrupt=True)
            return False, msg
        
        # Select card
        msg = self.selection.select_card_sequence(pile, card_idx)
        success = self.selection.has_selection()
        
        if self.screen_reader:
            self.screen_reader.tts.speak(msg, interrupt=True)
        
        return success, msg
    
    def select_from_waste(self) -> Tuple[bool, str]:
        """Select top card from waste (CTRL+ENTER).
        
        Returns:
            Tuple of (success, message)
        """
        msg = self.selection.select_top_card_from_waste(self.table.pile_scarti)
        success = self.selection.has_selection()
        
        if self.screen_reader:
            self.screen_reader.tts.speak(msg, interrupt=True)
        
        return success, msg
    
    def clear_selection(self) -> str:
        """Clear current card selection.
        
        Returns:
            Feedback message
        """
        msg = self.selection.clear_selection()
        
        if self.screen_reader:
            self.screen_reader.tts.speak(msg, interrupt=True)
        
        return msg
    
    def get_selected_info(self) -> str:
        """Get info about current selection.
        
        Returns:
            Selection details
        """
        msg = self.selection.get_selection_info()
        
        if self.screen_reader:
            self.screen_reader.tts.speak(msg, interrupt=True)
        
        return msg
    
    def execute_move(self) -> Tuple[bool, str]:
        """Execute move with selected cards to cursor position.
        
        Returns:
            Tuple of (success, message)
        """
        if not self.selection.has_selection():
            msg = "Devi prima selezionare la carta da spostare!\n"
            if self.screen_reader:
                self.screen_reader.tts.speak(msg, interrupt=True)
            return False, msg
        
        # Get destination
        dest_pile = self.cursor.get_current_pile()
        origin_pile = self.selection.origin_pile
        cards = self.selection.selected_cards
        
        # Can't move to same pile
        if dest_pile == origin_pile:
            msg = "Non puoi spostare le carte sulla stessa pila!\n"
            if self.screen_reader:
                self.screen_reader.tts.speak(msg, interrupt=True)
            return False, msg
        
        # Check if destination is foundation
        dest_idx = self.cursor.pile_idx
        is_foundation = 7 <= dest_idx <= 10
        
        # Execute move
        success, message = self.service.move_card(
            origin_pile,
            dest_pile,
            len(cards),
            is_foundation
        )
        
        # Clear selection on success
        if success:
            self.selection.clear_selection()
            
            # Move cursor to destination
            self.cursor.pile_idx = dest_idx
            if not dest_pile.is_empty():
                self.cursor.card_idx = dest_pile.get_card_count() - 1
            else:
                self.cursor.card_idx = 0
        
        # Audio feedback
        if self.screen_reader:
            self.screen_reader.tts.speak(message, interrupt=True)
        
        # Check victory
        if success and self.is_victory():
            if self.screen_reader:
                stats = self.service.get_statistics()
                victory_msg = f"Hai vinto! Mosse: {stats['move_count']}, Tempo: {int(stats['elapsed_time'])} secondi\n"
                self.screen_reader.tts.speak(victory_msg, interrupt=True)
        
        return success, message
    
    # ========================================
    # MOVE EXECUTION (Legacy compatibility)
    # ========================================
    
    def move_card(
        self,
        source_idx: int,
        target_idx: int,
        card_count: int = 1
    ) -> Tuple[bool, str]:
        """Move card(s) between piles with audio feedback.
        
        Legacy method for direct pile-to-pile moves.
        
        Args:
            source_idx: Source pile index
            target_idx: Target pile index
            card_count: Number of cards to move
            
        Returns:
            Tuple of (success, message)
        """
        source_pile = self._get_pile(source_idx)
        target_pile = self._get_pile(target_idx)
        
        if source_pile is None or target_pile is None:
            msg = "Indice pila non valido"
            if self.screen_reader:
                self.screen_reader.tts.speak(msg, interrupt=True)
            return False, msg
        
        is_foundation = 7 <= target_idx <= 10
        
        success, message = self.service.move_card(
            source_pile,
            target_pile,
            card_count,
            is_foundation
        )
        
        if self.screen_reader:
            self.screen_reader.tts.speak(message, interrupt=False)
        
        if success and self.is_victory():
            if self.screen_reader:
                stats = self.service.get_statistics()
                victory_msg = f"Hai vinto! Mosse: {stats['move_count']}\n"
                self.screen_reader.tts.speak(victory_msg, interrupt=True)
        
        return success, message
    
    def draw_from_stock(self, count: int = 1) -> Tuple[bool, str]:
        """Draw cards from stock to waste.
        
        Args:
            count: Number of cards to draw
            
        Returns:
            Tuple of (success, message)
        """
        success, message, cards = self.service.draw_cards(count)
        
        if self.screen_reader:
            self.screen_reader.tts.speak(message, interrupt=True)
        
        return success, message
    
    def recycle_waste(self, shuffle: bool = False) -> Tuple[bool, str]:
        """Recycle waste pile back to stock.
        
        Args:
            shuffle: Whether to shuffle
            
        Returns:
            Tuple of (success, message)
        """
        success, message = self.service.recycle_waste(shuffle)
        
        if self.screen_reader:
            self.screen_reader.tts.speak(message, interrupt=False)
        
        return success, message
    
    def auto_move_to_foundation(self) -> Tuple[bool, str]:
        """Attempt automatic move to foundation.
        
        Returns:
            Tuple of (success, message)
        """
        success, message, card = self.service.auto_move_to_foundation()
        
        if self.screen_reader:
            self.screen_reader.tts.speak(message, interrupt=False)
        
        return success, message
    
    # ========================================
    # STATE QUERIES
    # ========================================
    
    def get_game_state(self) -> Dict[str, Any]:
        """Get complete game state.
        
        Returns:
            Dictionary with statistics, game_over status, and piles
        """
        stats = self.service.get_statistics()
        is_over, status = self.service.check_game_over()
        
        return {
            "statistics": stats,
            "game_over": {"is_over": is_over, "status": status},
            "piles": {
                "tableau": [p.get_card_count() for p in self.table.pile_base],
                "foundations": [p.get_card_count() for p in self.table.pile_semi],
                "stock": self.table.pile_mazzo.get_card_count(),
                "waste": self.table.pile_scarti.get_card_count()
            },
            "cursor": self.cursor.get_position(),
            "has_selection": self.selection.has_selection()
        }
    
    def is_victory(self) -> bool:
        """Check if game is won."""
        return self.service.is_victory()
    
    def get_pile_info(self, pile_idx: int) -> Optional[Dict[str, Any]]:
        """Get information about specific pile."""
        pile = self._get_pile(pile_idx)
        if pile is None:
            return None
        
        top_card = pile.get_top_card() if not pile.is_empty() else None
        
        return {
            "card_count": pile.get_card_count(),
            "is_empty": pile.is_empty(),
            "top_card": {
                "name": top_card.get_name,
                "suit": top_card.get_suit,
                "covered": top_card.get_covered
            } if top_card is not None else None
        }
    
    # ========================================
    # AUDIO CONTROL
    # ========================================
    
    def set_audio_enabled(self, enabled: bool) -> None:
        """Enable/disable audio feedback."""
        if self.screen_reader:
            self.screen_reader.enabled = enabled
            self.audio_enabled = enabled
    
    def set_audio_verbose(self, level: int) -> None:
        """Set audio verbosity level (0-2)."""
        if self.screen_reader:
            self.screen_reader.verbose = level
    
    # ========================================
    # HELPERS
    # ========================================
    
    def _get_pile(self, idx: int) -> Optional[Pile]:
        """Get pile by index (0-12)."""
        if 0 <= idx <= 6:
            return self.table.pile_base[idx]
        elif 7 <= idx <= 10:
            return self.table.pile_semi[idx - 7]
        elif idx == 11:
            return self.table.pile_scarti
        elif idx == 12:
            return self.table.pile_mazzo
        return None
