"""Game engine facade orchestrating all refactored layers.

Provides a clean interface for game initialization, move execution,
and state management by coordinating domain services and infrastructure.
"""

from typing import Optional, Tuple, Dict, Any

from src.domain.models.table import GameTable
from src.domain.models.deck import Deck, FrenchDeck
from src.domain.models.pile import Pile
from src.domain.services.game_service import GameService
from src.domain.rules.solitaire_rules import SolitaireRules
from src.infrastructure.audio.screen_reader import ScreenReader
from src.infrastructure.audio.tts_provider import create_tts_provider


class GameEngine:
    """Facade for game orchestration.
    
    Coordinates all refactored components:
    - GameTable (domain model)
    - GameService (game logic orchestration)
    - SolitaireRules (rule validation)
    - ScreenReader (audio feedback)
    
    Provides high-level API for:
    - Game initialization and reset
    - Move execution with feedback
    - Game state queries
    - Statistics and progress tracking
    
    Attributes:
        table: Game table with all piles
        service: Game service for logic orchestration
        rules: Game rules validator
        screen_reader: Audio feedback service (optional)
        audio_enabled: Whether audio feedback is active
    """
    
    def __init__(
        self,
        table: GameTable,
        service: GameService,
        rules: SolitaireRules,
        screen_reader: Optional[ScreenReader] = None
    ):
        """Initialize game engine.
        
        Args:
            table: Initialized game table
            service: Game service instance
            rules: Rules validator
            screen_reader: Optional screen reader for audio feedback
        """
        self.table = table
        self.service = service
        self.rules = rules
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
        deck.shuffle_deck()
        table = GameTable(deck)
        rules = SolitaireRules()
        service = GameService(table, rules)
        
        # Create infrastructure (optional)
        screen_reader = None
        if audio_enabled:
            try:
                tts = create_tts_provider(tts_engine)
                screen_reader = ScreenReader(tts, enabled=True, verbose=verbose)
            except RuntimeError:
                # Graceful degradation if TTS not available
                screen_reader = None
        
        return cls(table, service, rules, screen_reader)
    
    # ========================================
    # GAME LIFECYCLE
    # ========================================
    
    def new_game(self) -> None:
        """Start a new game.
        
        Resets game state, redistributes cards, and starts timer.
        """
        # Reset service state
        self.service.reset_game()
        
        # Redistribute cards
        self.table.mazzo.shuffle_deck()
        self.table.distribuisci_carte()
        
        # Start timer
        self.service.start_game()
        
        # Announce game start
        if self.screen_reader:
            self.screen_reader.announce_move(
                success=True,
                message="Nuova partita iniziata",
                interrupt=True
            )
    
    def reset_game(self) -> None:
        """Reset current game without redistributing cards."""
        self.service.reset_game()
        
        if self.screen_reader:
            self.screen_reader.announce_move(
                success=True,
                message="Partita resettata",
                interrupt=True
            )
    
    # ========================================
    # MOVE EXECUTION
    # ========================================
    
    def move_card(
        self,
        source_idx: int,
        target_idx: int,
        card_count: int = 1
    ) -> Tuple[bool, str]:
        """Move card(s) between piles with audio feedback.
        
        Args:
            source_idx: Source pile index (0-6=tableau, 10=waste)
            target_idx: Target pile index (0-6=tableau, 7-10=foundations)
            card_count: Number of cards to move (for sequences)
            
        Returns:
            Tuple of (success, message)
        """
        # Get piles
        source_pile = self._get_pile(source_idx)
        target_pile = self._get_pile(target_idx)
        
        if source_pile is None or target_pile is None:
            msg = "Indice pila non valido"
            if self.screen_reader:
                self.screen_reader.announce_error(msg)
            return False, msg
        
        # Check if target is foundation
        is_foundation = 7 <= target_idx <= 10
        
        # Execute move
        success, message = self.service.move_card(
            source_pile,
            target_pile,
            card_count,
            is_foundation
        )
        
        # Audio feedback
        if self.screen_reader:
            self.screen_reader.announce_move(success, message, interrupt=False)
        
        # Check victory
        if success:
            is_over, status = self.service.check_game_over()
            if is_over and "Vittoria" in status:
                if self.screen_reader:
                    stats = self.service.get_statistics()
                    self.screen_reader.announce_victory(
                        moves=stats["move_count"],
                        time=int(stats["elapsed_time"])
                    )
        
        return success, message
    
    def draw_from_stock(self, count: int = 1) -> Tuple[bool, str]:
        """Draw cards from stock to waste.
        
        Args:
            count: Number of cards to draw (1 or 3)
            
        Returns:
            Tuple of (success, message)
        """
        success, message, cards = self.service.draw_cards(count)
        
        if self.screen_reader:
            self.screen_reader.announce_move(success, message, interrupt=False)
        
        return success, message
    
    def recycle_waste(self, shuffle: bool = False) -> Tuple[bool, str]:
        """Recycle waste pile back to stock.
        
        Args:
            shuffle: Whether to shuffle recycled cards
            
        Returns:
            Tuple of (success, message)
        """
        success, message = self.service.recycle_waste(shuffle)
        
        if self.screen_reader:
            self.screen_reader.announce_move(success, message, interrupt=False)
        
        return success, message
    
    def auto_move_to_foundation(self) -> Tuple[bool, str]:
        """Attempt automatic move to foundation.
        
        Returns:
            Tuple of (success, message)
        """
        success, message, card = self.service.auto_move_to_foundation()
        
        if self.screen_reader:
            if success and card:
                self.screen_reader.announce_card(card)
            self.screen_reader.announce_move(success, message, interrupt=False)
        
        return success, message
    
    # ========================================
    # STATE QUERIES
    # ========================================
    
    def get_game_state(self) -> Dict[str, Any]:
        """Get complete game state.
        
        Returns:
            Dictionary with:
            - statistics: move_count, elapsed_time, etc.
            - game_over: (bool, message)
            - piles: tableau, foundations, stock, waste card counts
        """
        stats = self.service.get_statistics()
        is_over, status = self.service.check_game_over()
        
        return {
            "statistics": stats,
            "game_over": {"is_over": is_over, "status": status},
            "piles": {
                "tableau": [p.get_card_count() for p in self.table.pile_base],
                "foundations": [p.get_card_count() for p in self.table.pile_semi],
                "stock": self.table.pile_mazzo.get_card_count() if self.table.pile_mazzo else 0,
                "waste": self.table.pile_scarti.get_card_count() if self.table.pile_scarti else 0
            }
        }
    
    def is_victory(self) -> bool:
        """Check if game is won.
        
        Returns:
            True if all foundations complete
        """
        return self.service.is_victory()
    
    def get_pile_info(self, pile_idx: int) -> Optional[Dict[str, Any]]:
        """Get information about specific pile.
        
        Args:
            pile_idx: Pile index
            
        Returns:
            Dictionary with pile info or None if invalid index
        """
        pile = self._get_pile(pile_idx)
        if pile is None:
            return None
        
        return {
            "card_count": pile.get_card_count(),
            "is_empty": pile.is_empty(),
            "top_card": {
                "name": pile.get_top_card().get_name,
                "suit": pile.get_top_card().get_suit,
                "covered": pile.get_top_card().get_covered
            } if not pile.is_empty() else None
        }
    
    # ========================================
    # AUDIO CONTROL
    # ========================================
    
    def set_audio_enabled(self, enabled: bool) -> None:
        """Enable/disable audio feedback.
        
        Args:
            enabled: True to enable, False to disable
        """
        if self.screen_reader:
            self.screen_reader.set_enabled(enabled)
            self.audio_enabled = enabled
    
    def set_audio_verbose(self, level: int) -> None:
        """Set audio verbosity level.
        
        Args:
            level: Verbosity (0=minimal, 1=normal, 2=detailed)
        """
        if self.screen_reader:
            self.screen_reader.set_verbose(level)
    
    # ========================================
    # HELPERS
    # ========================================
    
    def _get_pile(self, idx: int) -> Optional[Pile]:
        """Get pile by index.
        
        Indices:
        - 0-6: Tableau piles
        - 7-10: Foundation piles
        - 11: Stock
        - 12: Waste
        
        Args:
            idx: Pile index
            
        Returns:
            Pile instance or None if invalid
        """
        if 0 <= idx <= 6:
            return self.table.pile_base[idx]
        elif 7 <= idx <= 10:
            return self.table.pile_semi[idx - 7]
        elif idx == 11:
            return self.table.pile_mazzo
        elif idx == 12:
            return self.table.pile_scarti
        return None
