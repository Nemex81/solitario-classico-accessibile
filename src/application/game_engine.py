"""Game engine facade orchestrating all refactored layers.

Provides a clean interface for game initialization, move execution,
navigation, selection, and state management.

Extended with CursorManager and SelectionManager for gameplay.

New in v1.4.1:
- Virtual options window management (open/close/query)
- Validation: options blocked during active game
- Detailed voice formatters for draw/move/reshuffle operations

New in v1.4.2.1 (Bug Fix #3 - Phase 1-5/7):
- Dynamic deck type selection from GameSettings
- Support for both FrenchDeck and NeapolitanDeck
- Settings integration for draw count and shuffle mode
- Deck recreation when deck type changes between games
- Settings application helper for difficulty, timer, shuffle
- new_game() refactored with complete settings integration
"""

from typing import Optional, Tuple, Dict, Any, List

from src.domain.models.table import GameTable
from src.domain.models.deck import FrenchDeck, NeapolitanDeck
from src.domain.models.pile import Pile
from src.domain.models.card import Card
from src.domain.services.game_service import GameService
from src.domain.services.game_settings import GameSettings
from src.domain.services.cursor_manager import CursorManager
from src.domain.services.selection_manager import SelectionManager
from src.domain.rules.solitaire_rules import SolitaireRules
from src.infrastructure.audio.screen_reader import ScreenReader
from src.infrastructure.audio.tts_provider import create_tts_provider
from src.presentation.game_formatter import GameFormatter


class GameEngine:
    """Facade for game orchestration.
    
    Coordinates all refactored components:
    - GameTable (domain model)
    - GameService (game logic orchestration)
    - SolitaireRules (rule validation)
    - CursorManager (navigation)
    - SelectionManager (card selection)
    - ScreenReader (audio feedback)
    - GameFormatter (detailed voice narration)
    
    Provides high-level API for:
    - Game initialization and reset
    - Cursor navigation
    - Card selection/deselection
    - Move execution with detailed feedback
    - Game state queries
    - Statistics and progress tracking
    - Virtual options window management (v1.4.1)
    - Settings integration (v1.4.2.1 Bug #3)
    
    Attributes:
        table: Game table with all piles
        service: Game service for logic orchestration
        rules: Game rules validator
        cursor: Cursor navigation manager
        selection: Selection manager
        screen_reader: Audio feedback service (optional)
        audio_enabled: Whether audio feedback is active
        settings: Game settings instance (v1.4.2.1)
        draw_count: Number of cards to draw from stock (v1.4.2.1)
        shuffle_on_recycle: Whether to shuffle waste on recycle (v1.4.2.1)
        _options_open: Virtual options window state (v1.4.1)
    """
    
    def __init__(
        self,
        table: GameTable,
        service: GameService,
        rules: SolitaireRules,
        cursor: CursorManager,
        selection: SelectionManager,
        screen_reader: Optional[ScreenReader] = None,
        settings: Optional[GameSettings] = None  # NEW (Phase 1/7)
    ):
        """Initialize game engine.
        
        Args:
            table: Initialized game table
            service: Game service instance
            rules: Rules validator
            cursor: Cursor manager
            selection: Selection manager
            screen_reader: Optional screen reader for audio feedback
            settings: Optional game settings for configuration (NEW v1.4.2.1)
        """
        self.table = table
        self.service = service
        self.rules = rules
        self.cursor = cursor
        self.selection = selection
        self.screen_reader = screen_reader
        self.audio_enabled = screen_reader is not None
        
        # Settings integration (Phase 1/7 - Bug #3)
        self.settings = settings
        
        # Configurable attributes with defaults (Phase 1/7)
        # These will be updated from settings in new_game()
        self.draw_count: int = 1  # Default: 1 carta
        self.shuffle_on_recycle: bool = False  # Default: si girano (no shuffle)
        
        # Virtual options window state (v1.4.1)
        self._options_open: bool = False
    
    @classmethod
    def create(
        cls,
        audio_enabled: bool = True,
        tts_engine: str = "auto",
        verbose: int = 1,
        settings: Optional[GameSettings] = None
    ) -> "GameEngine":
        """Factory method to create fully initialized game engine.
        
        Args:
            audio_enabled: Enable audio feedback
            tts_engine: TTS engine ("auto", "nvda", "sapi5")
            verbose: Audio verbosity level (0-2)
            settings: GameSettings instance for configuration
            
        Returns:
            Initialized GameEngine instance ready to play
            
        Example:
            >>> settings = GameSettings()
            >>> settings.deck_type = "neapolitan"
            >>> engine = GameEngine.create(settings=settings)
            >>> engine.new_game()  # Uses Neapolitan deck
            
        Note:
            If settings is None or settings.deck_type is "french",
            defaults to FrenchDeck (backward compatible).
        """
        # Create domain components with dynamic deck selection (v1.4.2.1 fix)
        if settings and settings.deck_type == "neapolitan":
            deck = NeapolitanDeck()
        else:
            # Default to French deck (backward compatible)
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
        
        return cls(table, service, rules, cursor, selection, screen_reader, settings)
    
    # ========================================
    # GAME LIFECYCLE
    # ========================================
    
    def new_game(self) -> None:
        """Start a new game with settings integration.
        
        Flow (Phase 5/7 - Bug #3 fix):
        1. Check if deck_type changed → recreate deck if necessary
        2. If deck unchanged → gather existing cards
        3. Redistribute cards (new deck already shuffled or old collected)
        4. Apply settings (draw count, shuffle mode, timer)
        5. Reset game state and cursor/selection
        6. Start game timer and announce
        
        This method now properly consults GameSettings to:
        - Switch between French/Neapolitan decks dynamically
        - Configure difficulty level (draw count)
        - Configure shuffle mode for waste recycling
        - Announce timer limits (countdown not implemented)
        
        Example:
            >>> settings.deck_type = "neapolitan"
            >>> settings.difficulty_level = 2
            >>> settings.shuffle_discards = True
            >>> engine.new_game()
            >>> # TTS: "Tipo di mazzo cambiato: carte napoletane."
            >>> # TTS: "Livello 2: 2 carta/e per pesca. Scarti si mischiano."
        """
        deck_changed = False
        
        # 1️⃣ Check if deck type changed (Phase 3 integration)
        if self.settings:
            # Detect current deck type
            current_is_neapolitan = isinstance(self.table.mazzo, NeapolitanDeck)
            should_be_neapolitan = (self.settings.deck_type == "neapolitan")
            
            # Deck type mismatch → recreate deck and table
            if current_is_neapolitan != should_be_neapolitan:
                deck_changed = True
                self._recreate_deck_and_table(should_be_neapolitan)
        
        # 2️⃣ If deck NOT changed: gather existing cards
        if not deck_changed:
            # Collect all cards from all piles
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
        
        # 3️⃣ Redistribute cards
        # (new deck already shuffled from _recreate_deck_and_table,
        #  or old deck just collected and shuffled)
        self.table.distribuisci_carte()
        
        # 4️⃣ Apply game settings (Phase 4 integration)
        # Configures: draw_count, shuffle_on_recycle, timer warning
        self._apply_game_settings()
        
        # 5️⃣ Reset game state
        self.service.reset_game()
        
        # Reset cursor position
        self.cursor.pile_idx = 0
        self.cursor.card_idx = 0
        self.cursor.last_quick_pile = None
        
        # ⚠️ CRITICAL: Reset selection (was missing in original!)
        self.selection.clear_selection()
        
        # 6️⃣ Start game timer
        self.service.start_game()
        
        # 7️⃣ Announce game start
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
    
    def is_game_running(self) -> bool:
        """Check if a game is currently active.
        
        Returns:
            True if game is in progress
        """
        return self.service.is_game_running
    
    # ========================================
    # OPTIONS WINDOW MANAGEMENT (v1.4.1)
    # ========================================
    
    def open_options(self) -> str:
        """Open virtual options window.
        
        Enables interactive settings modification via F1-F5 keys.
        Blocked if game is currently running.
        
        Returns:
            Announcement message for TTS
            
        Example:
            >>> msg = engine.open_options()
            "Impostazioni di gioco aperte."
        """
        if self.is_game_running():
            return "Non puoi modificare le impostazioni durante una partita!\n"
        
        self._options_open = True
        return "Impostazioni di gioco aperte.\n"
    
    def close_options(self) -> str:
        """Close virtual options window.
        
        Disables settings modification mode.
        
        Returns:
            Announcement message for TTS
            
        Example:
            >>> msg = engine.close_options()
            "Impostazioni di gioco chiuse."
        """
        self._options_open = False
        return "Impostazioni di gioco chiuse.\n"
    
    def is_options_open(self) -> bool:
        """Check if virtual options window is open.
        
        Returns:
            True if options window is active
            
        Example:
            >>> if engine.is_options_open():
            ...     # Handle F1-F5 settings keys
        """
        return self._options_open
    
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
        
        Uses detailed voice formatter for complete move narration.
        
        Returns:
            Tuple of (success, message)
        """
        if not self.selection.has_selection():
            msg = "Devi prima selezionare la carta da spostare!\n"
            if self.screen_reader:
                self.screen_reader.tts.speak(msg, interrupt=True)
            return False, msg
        
        # Get move context
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
        
        # Capture card under (before move)
        card_under = None
        if not dest_pile.is_empty():
            card_under = dest_pile.get_top_card()
        
        # Execute move
        success, message = self.service.move_card(
            origin_pile,
            dest_pile,
            len(cards),
            is_foundation
        )
        
        # On success: use detailed formatter
        if success:
            # Check revealed card in origin
            revealed_card = None
            if not origin_pile.is_empty():
                top = origin_pile.get_top_card()
                if top and not top.get_covered:
                    revealed_card = top
            
            # Format detailed report
            message = GameFormatter.format_move_report(
                moved_cards=cards,
                origin_pile=origin_pile,
                dest_pile=dest_pile,
                card_under=card_under,
                revealed_card=revealed_card
            )
            
            # Clear selection
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
        """Draw cards from stock to waste with detailed voice feedback.
        
        Uses GameFormatter.format_drawn_cards() for complete card announcement.
        
        Args:
            count: Number of cards to draw
            
        Returns:
            Tuple of (success, message)
            
        Example:
            >>> success, msg = engine.draw_from_stock(3)
            >>> print(msg)
            "Hai pescato: 7 di Cuori, Regina di Quadri, Asso di Fiori."
        """
        success, generic_msg, cards = self.service.draw_cards(count)
        
        # Use detailed formatter
        if success and cards:
            message = GameFormatter.format_drawn_cards(cards)
        else:
            message = generic_msg
        
        if self.screen_reader:
            self.screen_reader.tts.speak(message, interrupt=True)
        
        return success, message
    
    def recycle_waste(self, shuffle: bool = False) -> Tuple[bool, str]:
        """Recycle waste pile back to stock with auto-draw and detailed feedback.
        
        Uses GameFormatter.format_reshuffle_message() to announce:
        - Shuffle mode (random/reverse)
        - Auto-drawn cards after reshuffle
        
        Args:
            shuffle: Whether to shuffle randomly
            
        Returns:
            Tuple of (success, message)
            
        Example:
            >>> success, msg = engine.recycle_waste(shuffle=True)
            >>> print(msg)
            "Rimescolo gli scarti in modo casuale nel mazzo riserve!
             Pescata automatica: Hai pescato: 9 di Quadri, Asso di Fiori."
        """
        # Execute recycle
        success, generic_msg = self.service.recycle_waste(shuffle)
        
        if not success:
            if self.screen_reader:
                self.screen_reader.tts.speak(generic_msg, interrupt=False)
            return success, generic_msg
        
        # Auto-draw after reshuffle
        auto_success, auto_msg, auto_cards = self.service.draw_cards(1)
        
        # Format detailed message
        shuffle_mode = "shuffle" if shuffle else "reverse"
        message = GameFormatter.format_reshuffle_message(
            shuffle_mode=shuffle_mode,
            auto_drawn_cards=auto_cards if auto_success else None
        )
        
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
    # HELPERS (Phase 3-5/7: Settings Integration)
    # ========================================
    
    def _recreate_deck_and_table(self, use_neapolitan: bool) -> None:
        """Recreate deck and table when user changes deck type.
        
        This method is called ONLY when deck_type changes between games.
        Creates a new deck (already shuffled), recreates table, and updates
        all references in service/cursor.
        
        Args:
            use_neapolitan: True for Neapolitan deck, False for French deck
            
        Note:
            This is part of Phase 3/7 for Bug #3 fix. The new deck is
            already created, shuffled, and dealt by GameTable, so we
            don't need to manually gather cards from old deck.
            
        Example:
            >>> # User changes from French to Neapolitan in options
            >>> engine._recreate_deck_and_table(use_neapolitan=True)
            >>> # TTS announces: "Tipo di mazzo cambiato: carte napoletane."
        """
        # 1. Create new deck
        if use_neapolitan:
            new_deck = NeapolitanDeck()
        else:
            new_deck = FrenchDeck()
        
        new_deck.crea()
        new_deck.mischia()
        
        # 2. Recreate table with new deck
        self.table = GameTable(new_deck)
        
        # 3. Update rules (deck-dependent for is_king, validation)
        self.rules = SolitaireRules(new_deck)
        
        # 4. Update service references
        self.service.table = self.table
        self.service.rules = self.rules
        
        # 5. Update cursor reference
        self.cursor.table = self.table
        
        # 6. TTS feedback
        if self.screen_reader:
            deck_name = "napoletane" if use_neapolitan else "francesi"
            self.screen_reader.tts.speak(
                f"Tipo di mazzo cambiato: carte {deck_name}.",
                interrupt=True
            )
    
    def _apply_game_settings(self) -> None:
        """Apply all game settings from GameSettings.
        
        Configures:
        - Draw count from difficulty_level (1→1, 2→2, 3→3)
        - Shuffle mode from shuffle_discards
        - Timer warning announcement (max_time_game)
        
        Note:
            Timer countdown is NOT implemented in GameService.
            This method only announces the configured time limit.
            
        This is part of Phase 4/7 for Bug #3 fix.
        Called from new_game() after deck recreation/card redistribution.
        
        Example:
            >>> # In new_game() after distribuisci_carte()
            >>> self._apply_game_settings()
            >>> # TTS announces: "Livello 2: 2 carta/e per pesca. Scarti si mischiano."
        """
        if not self.settings:
            return
        
        # 1️⃣ Draw count from difficulty
        # CRITICAL: Correct mapping!
        #   Level 1 = 1 card
        #   Level 2 = 2 cards (NOT 3!)
        #   Level 3 = 3 cards (NOT 5!)
        if self.settings.difficulty_level == 1:
            self.draw_count = 1
        elif self.settings.difficulty_level == 2:
            self.draw_count = 2  # ✅ CORRECT
        elif self.settings.difficulty_level == 3:
            self.draw_count = 3  # ✅ CORRECT
        else:
            # Fallback for invalid values
            self.draw_count = 1
        
        # 2️⃣ Shuffle mode
        # CRITICAL: Correct attribute is shuffle_discards (not waste_shuffle!)
        self.shuffle_on_recycle = self.settings.shuffle_discards
        
        # 3️⃣ Timer warning (countdown not implemented)
        # max_time_game: -1 = OFF, 300-3600 = seconds (5-60 min)
        if self.settings.max_time_game > 0 and self.screen_reader:
            minutes = self.settings.max_time_game // 60
            self.screen_reader.tts.speak(
                f"Attenzione: limite tempo configurato a {minutes} minuti. "
                f"Timer countdown non ancora implementato.",
                interrupt=False
            )
        
        # 4️⃣ TTS summary of settings
        if self.screen_reader:
            level_msg = f"Livello {self.settings.difficulty_level}: {self.draw_count} carta/e per pesca."
            shuffle_msg = "Scarti si mischiano." if self.shuffle_on_recycle else "Scarti si girano."
            self.screen_reader.tts.speak(
                f"{level_msg} {shuffle_msg}",
                interrupt=False
            )
    
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
