"""Game engine facade orchestrating all refactored layers.

Provides a clean interface for game initialization, move execution,
navigation, selection, and state management.

Extended with CursorManager and SelectionManager for gameplay.

New in v1.4.1:
- Virtual options window management (open/close/query)
- Validation: options blocked during active game
- Detailed voice formatters for draw/move/reshuffle operations

New in v1.4.2.1 (Bug Fix #3 - Phase 1-7/7 COMPLETE! + Bug #3.1 FIX):
- Dynamic deck type selection from GameSettings
- Support for both FrenchDeck and NeapolitanDeck
- Settings integration for draw count and shuffle mode
- Deck recreation when deck type changes between games
- Settings application helper for difficulty, timer, shuffle
- new_game() refactored with complete settings integration
- draw_from_stock() and recycle_waste() respect settings
- Bug #3.1 FIX: Prevent double distribution on deck change
"""

from typing import Optional, Tuple, Dict, Any, List, TYPE_CHECKING, Callable, Union

from src.domain.models.table import GameTable
from src.domain.models.deck import FrenchDeck, NeapolitanDeck
from src.domain.models.pile import Pile
from src.domain.models.card import Card
from src.domain.services.game_service import GameService
from src.domain.services.game_settings import GameSettings
from src.domain.services.cursor_manager import CursorManager
from src.domain.services.selection_manager import SelectionManager
from src.domain.services.scoring_service import ScoringService
from src.infrastructure.config.scoring_config_loader import ScoringConfigLoader  # 🆕 MISSING
from src.domain.rules.solitaire_rules import SolitaireRules
from src.domain.models.scoring import ScoringConfig, ScoreWarningLevel  # ✅ v2.6.0: Added ScoreWarningLevel
from src.infrastructure.audio.screen_reader import ScreenReader
from src.infrastructure.audio.tts_provider import create_tts_provider
from src.infrastructure.storage.score_storage import ScoreStorage
from src.presentation.game_formatter import GameFormatter
from src.presentation.formatters.score_formatter import ScoreFormatter
from src.infrastructure.logging import game_logger as log

if TYPE_CHECKING:
    from src.infrastructure.ui.dialog_provider import DialogProvider
    from src.domain.services.profile_service import ProfileService  # 🆕 v3.0.0: Profile System stub


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
    - Settings integration (v1.4.2.1 Bug #3 + #3.1)
    
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
        settings: Optional[GameSettings] = None,  # NEW (Phase 1/7)
        score_storage: Optional[ScoreStorage] = None,  # NEW (Phase 8/8)
        dialog_provider: Optional['DialogProvider'] = None,  # ✨ NEW v1.6.0
        on_game_ended: Optional[Callable[[bool], None]] = None,  # 🆕 NEW v1.6.2
        profile_service: Optional['ProfileService'] = None  # 🆕 NEW v3.1.0
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
            score_storage: Optional score storage for persistent statistics (NEW v2.0.0)
            dialog_provider: Optional dialog provider for native UI dialogs (NEW v1.6.0)
            on_game_ended: Optional callback when game ends, receives wants_rematch bool (NEW v1.6.2)
            profile_service: Optional profile service for statistics (NEW v3.1.0)
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
        
        # Score storage (Phase 8/8 - v2.0.0)
        self.score_storage = score_storage
        
        # ✨ NEW v1.6.0: Dialog integration (opt-in)
        self.dialogs = dialog_provider
        
        # 🆕 NEW v1.6.2: End game callback (opt-in)
        self.on_game_ended = on_game_ended
        
        # 🆕 NEW v3.1.0: Profile service integration
        self.profile_service = profile_service
        
        # 🆕 NEW v3.1.0: Last session storage for "Ultima Partita" menu
        self.last_session_outcome: Optional['SessionOutcome'] = None
        
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
        settings: Optional[GameSettings] = None,
        use_native_dialogs: bool = False,  # ✨ NEW v1.6.0
        parent_window = None,  # 🆕 NEW v1.6.2 - pygame screen for modal dialogs
        profile_service: Optional['ProfileService'] = None  # 🆕 NEW v3.1.0
    ) -> "GameEngine":
        """Factory method to create fully initialized game engine.
        
        Args:
            audio_enabled: Enable audio feedback
            tts_engine: TTS engine ("auto", "nvda", "sapi5")
            verbose: Audio verbosity level (0-2)
            settings: GameSettings instance for configuration
            use_native_dialogs: Enable native wxPython dialogs (NEW v1.6.0)
            parent_window: pygame.display surface for modal dialog parenting (NEW v1.6.2)
                           If provided, wxDialogs won't appear in ALT+TAB switcher
            profile_service: Optional profile service for session tracking (NEW v3.1.0)
            
        Returns:
            Initialized GameEngine instance ready to play
            
        Example (v1.6.2):
            >>> import pygame
            >>> screen = pygame.display.set_mode((800, 600))
            >>> settings = GameSettings()
            >>> engine = GameEngine.create(
            ...     settings=settings,
            ...     use_native_dialogs=True,
            ...     parent_window=screen  # Dialogs will be modal children
            ... )
            >>> # Now dialogs won't show as separate windows in ALT+TAB
            
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
        
        # Create scoring service if enabled (v2.0.0)
        scoring = None
        if settings and settings.scoring_enabled:
            # 🆕 VALIDATE TIMER CONSTRAINTS FOR LEVELS 4-5
            if settings.difficulty_level >= 4:
                if settings.max_time_game <= 0:
                    # Force timer for levels 4-5
                    if settings.difficulty_level == 4:
                        settings.max_time_game = 1800  # 30 min default
                    else:  # Level 5
                        settings.max_time_game = 900   # 15 min default
                elif settings.difficulty_level == 5:
                    # Enforce 5-20 minute range for level 5
                    settings.max_time_game = max(300, min(1200, settings.max_time_game))
                elif settings.difficulty_level == 4:
                    # Enforce 5-60 minute range for level 4
                    settings.max_time_game = max(300, min(3600, settings.max_time_game))
            
            # Create scoring service if enabled (v2.0.0)
            # 🆕 v2.0: Load config from external JSON with fallback
            scoring_config = ScoringConfigLoader.load()
            scoring = ScoringService(
                config=scoring_config,
                difficulty_level=settings.difficulty_level,
                deck_type=settings.deck_type,
                draw_count=settings.draw_count,
                timer_enabled=settings.max_time_game > 0,
                timer_limit_seconds=settings.max_time_game
            )
        
        # Create game service with optional scoring
        service = GameService(table, rules, scoring=scoring)
        cursor = CursorManager(table)
        selection = SelectionManager()
        
        # Create score storage (v2.0.0)
        score_storage = ScoreStorage()
        
        # Create infrastructure (optional)
        screen_reader = None
        if audio_enabled:
            try:
                tts = create_tts_provider(tts_engine)
                screen_reader = ScreenReader(tts, enabled=True, verbose=verbose)
            except RuntimeError:
                # Graceful degradation if TTS not available
                screen_reader = None
        
        # ✨ NEW v1.6.0: Create dialog provider if requested
        # 🆕 v1.6.2: Pass parent_window to prevent ALT+TAB separation
        dialog_provider = None
        if use_native_dialogs:
            try:
                from src.infrastructure.ui.wx_dialog_provider import WxDialogProvider
                dialog_provider = WxDialogProvider(parent_frame=parent_window)
            except ImportError:
                # wxPython not available, graceful degradation
                dialog_provider = None
        
        return cls(
            table, service, rules, cursor, selection, screen_reader,
            settings, score_storage, dialog_provider,
            on_game_ended=None,              # 🆕 Forward callback placeholder
            profile_service=profile_service  # 🆕 Forward profile_service
        )
    
    # ========================================
    # GAME LIFECYCLE
    # ========================================
    
    def new_game(self) -> None:
        """Start a new game with settings integration.
        
        Flow (Phase 5/7 - Bug #3 fix + Bug #3.1 fix):
        1. Check if deck_type changed → recreate deck if necessary
        2. If deck unchanged → gather existing cards AND redistribute
        3. If deck changed → skip redistribution (already dealt by GameTable)
        4. Apply settings (draw count, shuffle mode, timer)
        5. Reset game state and cursor/selection
        6. Start game timer and announce
        
        Bug #3.1 Fix:
            When deck_type changes, _recreate_deck_and_table() creates
            a new GameTable, which automatically distributes cards in __init__().
            We must NOT call distribuisci_carte() again to avoid crash.
        
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
        # ═══════════════════════════════════════════════════════════
        # TODO: Profile System Integration (v3.0.0 - Phase 9)
        # ═══════════════════════════════════════════════════════════
        # At startup, check for orphaned sessions (dirty shutdown recovery):
        # if self.session_tracker:
        #     orphaned = self.session_tracker.get_orphaned_sessions()
        #     if orphaned:
        #         # Recovery logic: record as ABANDON_CRASH, mark recovered
        #         for orphan in orphaned:
        #             if self.profile_service:
        #                 # Create crash recovery session
        #                 crash_session = SessionOutcome.create_new(
        #                     profile_id=orphan['profile_id'],
        #                     end_reason=EndReason.ABANDON_CRASH,
        #                     is_victory=False,
        #                     elapsed_time=0.0,
        #                     timer_enabled=False,
        #                     ...
        #                 )
        #                 self.profile_service.record_session(crash_session)
        #             self.session_tracker.mark_recovered(orphan['session_id'])
        
        deck_changed = False
        
        # 1️⃣ Check if deck type changed (Phase 3 integration)
        if self.settings:
            # Detect current deck type
            current_is_neapolitan = isinstance(self.table.mazzo, NeapolitanDeck)
            should_be_neapolitan = (self.settings.deck_type == "neapolitan")
            
            # Deck type mismatch → recreate deck and table
            if current_is_neapolitan != should_be_neapolitan:
                deck_changed = True
                
                # Log deck type change
                old_deck = "neapolitan" if current_is_neapolitan else "french"
                new_deck = "neapolitan" if should_be_neapolitan else "french"
                log.settings_changed("deck_type", old_deck, new_deck)
                
                # ⚠️ IMPORTANT: This creates GameTable which already deals cards!
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
            
            # ✅ BUG #54 FIX: Cover all cards before redistribution
            # Reset card state to covered to prevent inheriting uncovered state from previous game
            for card in all_cards:
                card.set_cover()
            
            # Put cards back in deck and shuffle
            self.table.mazzo.cards = all_cards
            self.table.mazzo.mischia()
            
            # 3️⃣ Redistribute cards ONLY if deck unchanged
            # ✅ BUG #3.1 FIX: Skip if deck_changed (already dealt by GameTable)
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
    # TIMER TICK HANDLING (v2.7.0)
    # ========================================
    
    def on_timer_tick(self) -> None:
        """Timer tick handler (called every 1 second by external timer).
        
        Checks for timer expiry and handles STRICT/PERMISSIVE behavior.
        This method is designed to be called by wx.Timer or similar
        mechanism in the UI layer.
        """
        # Only check if game is running and timer is enabled
        if not self.service.is_game_running:
            return
        
        if not self.settings or self.settings.max_time_game <= 0:
            return
        
        # Check expiry (single-fire)
        expired = self.service.check_timer_expiry(
            self.settings.max_time_game
        )
        
        if not expired:
            return  # No expiry, continue
        
        # Timer expired: handle based on mode
        if self.settings.timer_strict_mode:
            # STRICT: Auto-stop game
            self._handle_strict_timeout()
        else:
            # PERMISSIVE: Start overtime tracking
            self._handle_permissive_timeout()
    
    def _handle_strict_timeout(self) -> None:
        """Handle timer expiry in STRICT mode.
        
        Auto-stops game immediately with TIMEOUT_STRICT reason.
        """
        # Import EndReason locally to avoid circular dependency
        from src.domain.models.game_end import EndReason
        
        log.timer_expired()
        
        # Announce expiry (TTS)
        self._announce_timer_expired(permissive=False)
        
        # End game immediately
        self.end_game(EndReason.TIMEOUT_STRICT)
    
    def _handle_permissive_timeout(self) -> None:
        """Handle timer expiry in PERMISSIVE mode.
        
        Allows game to continue, starts overtime tracking.
        """
        # Start overtime tracking
        import time
        self.service.overtime_start = time.time()
        
        # Announce expiry (TTS, different message)
        self._announce_timer_expired(permissive=True)
        
        # Game continues, no end_game() call
    
    def _announce_timer_expired(self, permissive: bool = False) -> None:
        """Announce timer expiry via TTS.
        
        Args:
            permissive: True if PERMISSIVE mode, False if STRICT
        """
        # Use GameFormatter for consistent TTS formatting
        from src.presentation.game_formatter import GameFormatter
        
        message = GameFormatter.format_timer_expired(
            strict_mode=not permissive
        )
        
        # Announce via screen reader if available
        self._speak(message)
    
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
    
    def move_cursor(self, direction: str) -> Tuple[str, Optional[str]]:
        """Move cursor in specified direction with hint support (v1.5.0).
        
        Args:
            direction: "up", "down", "left", "right", "tab", "home", "end"
            
        Returns:
            Tuple[str, Optional[str]]: (message, hint)
            - message: Feedback message for screen reader
            - hint: Optional command hint (v1.5.0)
        """
        direction = direction.lower()
        
        if direction == "up":
            msg, hint = self.cursor.move_up()
        elif direction == "down":
            msg, hint = self.cursor.move_down()
        elif direction == "left":
            msg, hint = self.cursor.move_left()
        elif direction == "right":
            msg, hint = self.cursor.move_right()
        elif direction == "tab":
            msg, hint = self.cursor.move_tab()
        elif direction == "home":
            msg = self.cursor.move_home()
            hint = None
        elif direction == "end":
            msg = self.cursor.move_end()
            hint = None
        else:
            msg = "Direzione non valida!\n"
            hint = None
        
        if self.screen_reader:
            self.screen_reader.tts.speak(msg, interrupt=True)
        
        return (msg, hint)
    
    def jump_to_pile(self, pile_idx: int) -> Tuple[str, Optional[str]]:
        """Jump to specific pile with double-tap auto-selection support (v1.5.0).
        
        Args:
            pile_idx: Pile index (0-12)
        
        Returns:
            Tuple[str, Optional[str]]: (message, hint)
            - message: Feedback message for screen reader
            - hint: Optional command hint (v1.5.0)
        
        Behavior:
            First tap: Move cursor to pile top card + announce pile info + hint
            Second tap (tableau/foundation): 
                - Cancel previous selection if present (silent)
                - Auto-select top card
                - Announce: "Selezione precedente annullata. carte selezionate: 1. [nome carta]"
            Second tap (stock/waste): No action (hint only)
        """
        # Get cursor movement feedback, auto-selection flag, and hint (v1.5.0)
        msg, should_auto_select, hint = self.cursor.jump_to_pile(pile_idx, enable_double_tap=True)
        
        # ═══════════════════════════════════════════════════════════
        # 🔥 SECOND TAP: Execute automatic card selection
        # ═══════════════════════════════════════════════════════════
        if should_auto_select:
            msg_deselect = ""
            
            # ─────────────────────────────────────────────────────
            # Cancel previous selection if present (silent reset)
            # ─────────────────────────────────────────────────────
            if self.selection.has_selection():
                self.selection.clear_selection()
                msg_deselect = "Selezione precedente annullata. "
            
            # ─────────────────────────────────────────────────────
            # Execute automatic selection
            # ─────────────────────────────────────────────────────
            success, msg_select = self.select_card_at_cursor()
            
            # Log auto-selection ONLY if successful
            if success:
                log.info_query_requested(
                    "auto_selection",
                    f"Double-tap on pile_{pile_idx}"
                )
            
            # Combine messages: deselection (if any) + selection feedback
            msg = msg_deselect + msg_select
            hint = None  # No hint after auto-selection
        
        # ═══════════════════════════════════════════════════════════
        # 🔊 Vocal announcement
        # ═══════════════════════════════════════════════════════════
        if self.screen_reader and msg:
            self.screen_reader.tts.speak(msg, interrupt=True)
        
        return (msg, hint)
    
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
        
        # Log successful selection
        if success:
            pile_name = f"{pile.type}_{pile_idx}" if hasattr(pile, 'type') else f"pile_{pile_idx}"
            selected_cards = self.selection.selected_cards
            card_repr = f"{selected_cards[0].rank}{selected_cards[0].suit}" if selected_cards else "unknown"
            
            log.debug_state("card_selected", {
                "card": card_repr,
                "pile": pile_name,
                "count": len(selected_cards)
            })
        
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
        
        # Log successful selection from waste
        if success:
            selected_cards = self.selection.selected_cards
            card_repr = f"{selected_cards[0].rank}{selected_cards[0].suit}" if selected_cards else "unknown"
            
            log.debug_state("card_selected", {
                "card": card_repr,
                "pile": "waste",
                "count": len(selected_cards)
            })
        
        if self.screen_reader:
            self.screen_reader.tts.speak(msg, interrupt=True)
        
        return success, msg
    
    def clear_selection(self) -> str:
        """Clear current card selection.
        
        Returns:
            Feedback message
        """
        # Log deselection before clearing
        count = len(self.selection.selected_cards)
        if count > 0:
            log.debug_state("cards_deselected", {"count": count})
        
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
            self.end_game(is_victory=True)
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
            self.end_game(is_victory=True)
            if self.screen_reader:
                stats = self.service.get_statistics()
                victory_msg = f"Hai vinto! Mosse: {stats['move_count']}\n"
                self.screen_reader.tts.speak(victory_msg, interrupt=True)
        
        return success, message
    
    def draw_from_stock(self, count: Optional[int] = None) -> Tuple[bool, str]:
        """Draw cards from stock to waste with auto-recycle support.
        
        Phase 6/7: Now uses self.draw_count from settings when count is None.
        
        Bug #4 FIX: Auto-recycles waste when stock is empty but waste has cards.
        
        Uses GameFormatter.format_drawn_cards() for complete card announcement.
        
        Args:
            count: Number of cards to draw (None = use self.draw_count from settings)
            
        Returns:
            Tuple of (success, message)
            
        Example:
            >>> # With difficulty_level = 2 in settings
            >>> success, msg = engine.draw_from_stock()  # Draws 2 cards
            >>> print(msg)
            "Hai pescato: 7 di Cuori, Regina di Quadri."
            
            >>> # Or with explicit count (overrides settings)
            >>> success, msg = engine.draw_from_stock(count=3)
            >>> print(msg)
            "Hai pescato: 7 di Cuori, Regina di Quadri, Asso di Fiori."
            
            >>> # Mazzo vuoto, scarti con 15 carte, shuffle_discards = True
            >>> success, msg = engine.draw_from_stock()
            >>> print(msg)
            "Rimescolo gli scarti nel mazzo riserve! Hai pescato: 7 di Cuori."
        """
        # ✅ Phase 6: Use settings if count not specified
        if count is None:
            count = self.draw_count
        
        # ✅ BUG #4 FIX: Check if stock empty but waste has cards
        stock = self.table.pile_mazzo
        waste = self.table.pile_scarti
        
        if stock.is_empty() and not waste.is_empty():
            # ✅ BUG #5 FIX: Announce problem first to provide context
            if self.screen_reader:
                self.screen_reader.tts.speak(
                    "Mazzo vuoto.",
                    interrupt=True
                )
            
            # Auto-recycle waste using configured mode from settings
            recycle_success, recycle_msg = self.service.recycle_waste(
                shuffle=self.shuffle_on_recycle
            )
            
            if not recycle_success:
                # Recycle failed (should never happen if waste not empty)
                if self.screen_reader:
                    self.screen_reader.tts.speak(recycle_msg, interrupt=True)
                return False, recycle_msg
            
            # Format recycle announcement
            shuffle_mode = "shuffle" if self.shuffle_on_recycle else "reverse"
            recycle_announcement = GameFormatter.format_reshuffle_message(
                shuffle_mode=shuffle_mode,
                auto_drawn_cards=None  # Will announce cards separately below
            )
            
            # Announce recycle (but don't return yet - continue to draw)
            if self.screen_reader:
                # Remove auto-draw part from message (we handle it below)
                recycle_only = recycle_announcement.split("Pescata automatica")[0].strip()
                self.screen_reader.tts.speak(recycle_only, interrupt=False)
        
        # Now draw cards (original logic)
        success, generic_msg, cards = self.service.draw_cards(count)
        
        # ✅ NEW v2.6.0: TTS threshold warnings (graduated)
        if success and self.settings and self.settings.scoring_enabled and self.service.scoring:
            self._announce_draw_threshold_warning()
        
        # Use detailed formatter
        if success and cards:
            message = GameFormatter.format_drawn_cards(cards)
        else:
            # Both stock AND waste empty
            message = generic_msg
        
        if self.screen_reader:
            self.screen_reader.tts.speak(message, interrupt=False)
        
        return success, message
    
    def recycle_waste(self, shuffle: Optional[bool] = None) -> Tuple[bool, str]:
        """Recycle waste pile back to stock with auto-draw and detailed feedback.
        
        Phase 7/7: Now uses self.shuffle_on_recycle from settings when shuffle is None.
        
        Uses GameFormatter.format_reshuffle_message() to announce:
        - Shuffle mode (random/reverse)
        - Auto-drawn cards after reshuffle
        
        Args:
            shuffle: Shuffle mode (None = use self.shuffle_on_recycle from settings,
                    True = force shuffle, False = force reverse)
            
        Returns:
            Tuple of (success, message)
            
        Example:
            >>> # With shuffle_discards = True in settings
            >>> success, msg = engine.recycle_waste()  # Shuffles
            >>> print(msg)
            "Rimescolo gli scarti in modo casuale nel mazzo riserve!
             Pescata automatica: Hai pescato: 9 di Quadri."
            
            >>> # Or with explicit mode (overrides settings)
            >>> success, msg = engine.recycle_waste(shuffle=False)
            >>> print(msg)
            "Rigiro gli scarti nel mazzo riserve!
             Pescata automatica: Hai pescato: Asso di Fiori."
        """
        # ✅ Phase 7: Use settings if shuffle not specified
        if shuffle is None:
            shuffle = self.shuffle_on_recycle
        
        # Execute recycle
        success, generic_msg = self.service.recycle_waste(shuffle)
        
        if not success:
            if self.screen_reader:
                self.screen_reader.tts.speak(generic_msg, interrupt=False)
            return success, generic_msg
        
        # ✅ NEW v2.6.0: TTS threshold warning for recycle
        if self.settings and self.settings.scoring_enabled and self.service.scoring:
            self._announce_recycle_threshold_warning()
        
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
    
    def end_game(self, is_victory: 'Union[EndReason, bool]') -> None:
        """Handle game end with full reporting and rematch prompt.
        
        Complete flow:
        1. Snapshot statistics (including suits)
        2. Calculate final score (if scoring enabled)
        3. Save score to storage (if available)
        4. Generate complete Italian report
        5. Announce via TTS (always)
        6. Show native dialog (if available)
        7. Prompt for rematch (if dialogs available)
        8. 🆕 Call on_game_ended callback to return control to test.py
        
        Args:
            is_victory: True if all 4 suits completed (legacy bool)
                       OR EndReason enum (v2.7.0)
            
        Side effects:
            - Stops game timer
            - Saves score to JSON (if scoring enabled)
            - May start new game (if user chooses rematch AND no callback)
            
        Note (v1.6.2):
            If on_game_ended callback is set, this method NO LONGER handles
            UI state management (is_menu_open, menu announcements). 
            All UI logic delegated to test.py.handle_game_ended().
        
        Note (v2.7.0):
            Now accepts EndReason enum for fine-grained outcome tracking.
            For PERMISSIVE mode, automatically converts VICTORY to 
            VICTORY_OVERTIME if overtime is active.
            
        Example:
            >>> from src.domain.models.game_end import EndReason
            >>> engine.end_game(EndReason.VICTORY)
            # TTS announces: "Hai Vinto! ..."
            # Dialog shows full report
            # Prompts: "Vuoi giocare ancora?"
            # Calls: self.on_game_ended(wants_rematch=False)
        """
        # ═══════════════════════════════════════════════════════════
        # STEP 0: Handle EndReason and overtime conversion (v2.7.0)
        # ═══════════════════════════════════════════════════════════
        from src.domain.models.game_end import EndReason
        
        # Convert is_victory parameter to EndReason if needed
        if isinstance(is_victory, bool):
            # Legacy bool support (backward compatibility)
            end_reason = EndReason.VICTORY if is_victory else EndReason.ABANDON_EXIT
        else:
            # Already an EndReason
            end_reason = is_victory
        
        # PERMISSIVE mode: Convert VICTORY to VICTORY_OVERTIME if overtime active
        if end_reason == EndReason.VICTORY and self.service.overtime_start is not None:
            end_reason = EndReason.VICTORY_OVERTIME
        
        # Extract boolean is_victory for compatibility with existing code
        is_victory_bool = end_reason.is_victory()
        
        # ═══════════════════════════════════════════════════════════
        # STEP 1: Snapshot Statistics
        # ═══════════════════════════════════════════════════════════
        self.service._snapshot_statistics()
        final_stats = self.service.get_final_statistics()
        
        # Log game end with statistics
        if is_victory_bool:
            # Extract score (0 if scoring disabled)
            score = 0
            if self.settings and self.settings.scoring_enabled and self.service.scoring:
                score = self.service.scoring.calculate_final_score(
                    elapsed_seconds=final_stats['elapsed_time'],
                    move_count=final_stats['move_count'],
                    is_victory=True,
                    timer_strict_mode=self.settings.timer_strict_mode if self.settings else True
                )
            
            log.game_won(
                elapsed_time=int(final_stats['elapsed_time']),
                moves_count=final_stats['move_count'],
                score=score
            )
        else:
            log.game_abandoned(
                elapsed_time=int(final_stats['elapsed_time']),
                moves_count=final_stats['move_count']
            )
        
        # ═══════════════════════════════════════════════════════════
        # STEP 2: Calculate Final Score
        # ═══════════════════════════════════════════════════════════
        final_score = None
        if self.settings and self.settings.scoring_enabled and self.service.scoring:
            final_score = self.service.scoring.calculate_final_score(
                elapsed_seconds=final_stats['elapsed_time'],
                move_count=final_stats['move_count'],
                is_victory=is_victory_bool,
                timer_strict_mode=self.settings.timer_strict_mode if self.settings else True
            )
        
        # ═══════════════════════════════════════════════════════════
        # STEP 3: Save Score
        # ═══════════════════════════════════════════════════════════
        if final_score and self.score_storage:
            self.score_storage.save_score(final_score)
        
        # ═══════════════════════════════════════════════════════════
        # STEP 3.5: Profile System Integration (v3.1.0 - ACTIVATED)
        # ═══════════════════════════════════════════════════════════
        # Record session to active profile
        profile_summary = None
        if self.profile_service and self.profile_service.active_profile:
            from src.domain.models.profile import SessionOutcome
            
            # Build session outcome
            session_outcome = SessionOutcome.create_new(
                profile_id=self.profile_service.active_profile.profile_id,
                end_reason=end_reason,
                is_victory=is_victory_bool,
                elapsed_time=final_stats['elapsed_time'],
                timer_enabled=(self.settings.max_time_game > 0) if self.settings else False,
                timer_limit=self.settings.max_time_game if self.settings else 0,
                timer_mode=("STRICT" if self.settings.timer_strict_mode else "PERMISSIVE") if (self.settings and self.settings.max_time_game > 0) else "OFF",
                timer_expired=(end_reason == EndReason.TIMEOUT_STRICT),
                scoring_enabled=self.settings.scoring_enabled if self.settings else False,
                final_score=final_score.total_score if final_score else 0,
                difficulty_level=self.settings.difficulty_level if self.settings else 3,
                deck_type=self.settings.deck_type if self.settings else "french",
                move_count=final_stats['move_count']
            )
            
            # Store for "Ultima Partita" menu (v3.1.0 Phase 9.1)
            self.last_session_outcome = session_outcome
            
            # Record session (auto-saves profile)
            self.profile_service.record_session(session_outcome)
            
            # Build profile summary for dialogs
            profile_summary = {
                'total_victories': self.profile_service.global_stats.total_victories,
                'total_defeats': self.profile_service.global_stats.total_games - self.profile_service.global_stats.total_victories,
                'winrate': self.profile_service.global_stats.winrate,
                'new_record': self._check_new_record(session_outcome) if is_victory_bool else False,
                'cards_placed': sum(self.table.pile_semi[i].get_card_count() for i in range(4)),
                'streak_broken': not is_victory_bool and self.profile_service.global_stats.current_streak > 0,
                'previous_streak': self.profile_service.global_stats.longest_streak if not is_victory_bool else 0
            }
            
            if profile_summary['new_record']:
                # Get previous record for display
                if len(self.profile_service.recent_sessions) >= 2:
                    # Find previous victory
                    prev_victory_time = None
                    for session in reversed(self.profile_service.recent_sessions[:-1]):
                        if session.is_victory:
                            prev_victory_time = session.elapsed_time
                            break
                    if prev_victory_time:
                        profile_summary['previous_record'] = prev_victory_time
        
        # ═══════════════════════════════════════════════════════════
        # STEP 4: Generate Report
        # ═══════════════════════════════════════════════════════════
        from src.presentation.formatters.report_formatter import ReportFormatter
        
        deck_type = self.settings.deck_type if self.settings else "french"
        report = ReportFormatter.format_final_report(
            stats=final_stats,
            final_score=final_score,
            is_victory=is_victory,
            deck_type=deck_type
        )
        
        # ═══════════════════════════════════════════════════════════
        # STEP 5: TTS Announcement (Always, even if dialogs enabled)
        # ═══════════════════════════════════════════════════════════
        if self.screen_reader:
            self.screen_reader.tts.speak(report, interrupt=True)
        
        # ═══════════════════════════════════════════════════════════
        # STEP 6: Show Victory/Abandon Dialog (v3.1.0)
        # ═══════════════════════════════════════════════════════════
        if profile_summary:
            # Use new stats-integrated dialogs
            try:
                import wx
                from src.presentation.dialogs.victory_dialog import VictoryDialog
                from src.presentation.dialogs.abandon_dialog import AbandonDialog
                from src.domain.models.profile import SessionOutcome
                
                # Show appropriate dialog
                if is_victory_bool:
                    dialog = VictoryDialog(None, session_outcome, profile_summary)
                else:
                    # v3.1.2: For timeout, show rematch option (3 buttons instead of 2)
                    show_rematch = (end_reason == EndReason.TIMEOUT_STRICT)
                    dialog = AbandonDialog(None, session_outcome, profile_summary, 
                                         show_rematch_option=show_rematch)
                
                result = dialog.ShowModal()
                dialog.Destroy()
                
                # Handle user choice
                # v3.1.2: Support timeout rematch options (wx.ID_YES, wx.ID_MORE, wx.ID_NO)
                if result == wx.ID_MORE:
                    # User wants to see detailed stats (timeout scenario)
                    try:
                        from src.presentation.dialogs.detailed_stats_dialog import DetailedStatsDialog
                        
                        stats_dialog = DetailedStatsDialog(
                            None,
                            profile_name=self.profile_service.active_profile.profile_name,
                            global_stats=self.profile_service.global_stats,
                            timer_stats=self.profile_service.timer_stats,
                            difficulty_stats=self.profile_service.difficulty_stats,
                            scoring_stats=self.profile_service.scoring_stats
                        )
                        stats_dialog.ShowModal()
                        stats_dialog.Destroy()
                    except Exception as e:
                        # If stats dialog fails, just log and continue
                        import logging
                        logging.error(f"Failed to show detailed stats: {e}")
                    
                    # After viewing stats, return to menu (don't start new game)
                    if self.on_game_ended:
                        log.debug_state("end_game", {"action": "stats_viewed", "callback": "on_game_ended(False)"})
                        self.on_game_ended(False)  # Don't want rematch
                    else:
                        log.debug_state("end_game", {"action": "stats_viewed", "callback": "none_resetting_locally"})
                        self.service.reset_game()
                
                elif self.on_game_ended:
                    # ✅ CORRECT: Pass control to acs_wx.py
                    # wx.ID_YES (Rivincita) or wx.ID_OK (Nuova Partita) = wants rematch
                    wants_rematch = (result == wx.ID_OK or result == wx.ID_YES)
                    log.debug_state("end_game", {"dialog_result": result, "wants_rematch": wants_rematch})
                    self.on_game_ended(wants_rematch)
                else:
                    # ⚠️ FALLBACK: No callback (test mode or legacy code)
                    log.warning_issued("GameEngine", "end_game: no callback registered, handling locally")
                    if result == wx.ID_OK or result == wx.ID_YES:
                        log.debug_state("end_game", {"local_action": "new_game"})
                        self.new_game()
                    else:
                        log.debug_state("end_game", {"local_action": "reset_game"})
                        self.service.reset_game()
                
                return  # Skip old dialog system below
            except ImportError:
                # wx not available, fallback to old system
                pass
        
        # ═══════════════════════════════════════════════════════════
        # STEP 6 (Fallback): Old Dialog System
        # ═══════════════════════════════════════════════════════════
        if self.dialogs:
            # ═══════════════════════════════════════════════════════
            # STEP 7: 🆕 Async Rematch Prompt (v2.5.0 - Bug #68 fix)
            # ═══════════════════════════════════════════════════════
            def on_rematch_result(wants_rematch: bool):
                """Callback invoked after rematch dialog closes (deferred context).
                
                This callback is invoked by wxPython's event loop AFTER the
                dialog closes and focus is restored. UI is in stable state,
                no need for wx.CallAfter() workaround.
                
                Flow:
                    1. User clicks YES/NO in rematch dialog
                    2. Dialog closes (Show() returns)
                    3. wxPython processes event loop
                    4. [This callback invoked here]
                    5. UI state is stable, safe to call UI transitions
                
                Args:
                    wants_rematch: True if user wants rematch, False to return to menu
                """
                if self.on_game_ended:
                    # NEW BEHAVIOR (v2.5.0): Pass control to acs_wx.py via callback
                    # acs_wx.py will handle UI transitions directly (no CallAfter needed)
                    self.on_game_ended(wants_rematch)
                else:
                    # FALLBACK: Old behavior (no callback set)
                    # Used for backward compatibility or unit tests
                    if wants_rematch:
                        self.new_game()
                    else:
                        self.service.reset_game()
            
            def on_stats_closed():
                """Callback invoked after statistics dialog closes.
                
                After stats closed, show rematch prompt.
                This creates the async callback chain: stats → rematch.
                
                Version:
                    v2.5.0: Created for Bug #68.4 regression fix
                """
                log.debug_state("on_stats_closed", {"phase": "showing_rematch_prompt"})
                # Show rematch dialog with its own callback
                self.dialogs.show_rematch_prompt_async(on_rematch_result)
            
            # Show statistics dialog (async, non-blocking)
            log.debug_state("end_game", {"phase": "showing_statistics_report"})
            self.dialogs.show_statistics_report_async(
                stats=final_stats,
                final_score=final_score,
                is_victory=is_victory,
                deck_type=deck_type,
                callback=on_stats_closed  # Chain to rematch dialog
            )
        else:
            # No dialogs available → fallback to old behavior
            if self.on_game_ended:
                # Default: No rematch (user can't choose without dialog)
                self.on_game_ended(False)
            else:
                self.service.reset_game()
    
    # ========================================
    # PROFILE SYSTEM HELPERS (v3.1.0)
    # ========================================
    
    def _check_new_record(self, outcome) -> bool:
        """Check if session outcome is a new personal record.
        
        Args:
            outcome: SessionOutcome instance
            
        Returns:
            True if this is the fastest victory ever
            
        Version: v3.1.0
        """
        if not outcome.is_victory or not self.profile_service:
            return False
        
        prev_fastest = self.profile_service.global_stats.fastest_victory
        
        # If this is the first victory, it's automatically a record
        if prev_fastest == float('inf'):
            return True
        
        # Check if current time beats previous record
        return outcome.elapsed_time < prev_fastest
    
    def show_last_game_summary(self) -> None:
        """Show last game summary dialog (menu option 'Ultima Partita').
        
        Displays LastGameDialog with summary of most recently completed game.
        Retrieves from ProfileService.recent_sessions (persisted) instead of
        memory-only GameEngine.last_session_outcome.
        
        Version:
            v3.1.0: Initial implementation
            v3.1.2: Fixed to use ProfileService (Single Source of Truth, persisted)
        """
        import wx
        from src.presentation.dialogs.last_game_dialog import LastGameDialog
        
        log.debug_state("last_game_query", {"trigger": "menu_button"})
        
        # v3.1.2: Use ProfileService.recent_sessions (persisted, works after restart)
        if not self.profile_service or not self.profile_service.recent_sessions:
            log.info_query_requested("last_game", "no_recent_game")
            wx.MessageBox(
                "Nessuna partita recente disponibile.\n"
                "Gioca una partita per vedere il riepilogo.",
                "Ultima Partita",
                wx.OK | wx.ICON_INFORMATION
            )
            return
        
        # Get last session from ProfileService (always up-to-date, even after app restart)
        last_session = self.profile_service.recent_sessions[-1]
        
        log.debug_state("last_game_display", {"outcome": last_session.end_reason.value})
        dialog = LastGameDialog(None, last_session)
        dialog.ShowModal()
        dialog.Destroy()
    
    # ========================================
    # THRESHOLD WARNING HELPERS (v2.6.0)
    # ========================================
    
    def _speak(self, message: str, interrupt: bool = False) -> None:
        """Safe TTS adapter with None-check (v2.6.0).
        
        Centralizes TTS access to avoid crashes if screen_reader not initialized.
        Used by warning announcement helpers.
        
        Args:
            message: Text to speak
            interrupt: Whether to interrupt current speech
            
        Version: v2.6.0
        """
        if self.screen_reader and hasattr(self.screen_reader, 'tts'):
            try:
                self.screen_reader.tts.speak(message, interrupt=interrupt)
            except Exception as e:
                # Fail gracefully in tests or if TTS unavailable
                log.warning_issued("GameEngine", f"TTS speak failed: {e}")
        # Else: no-op (test-safe, no crash)
    
    def _announce_draw_threshold_warning(self) -> None:
        """Announce threshold warning for stock draw based on warning level (v2.6.0).
        
        Called after successful draw to check if a scoring threshold
        has been crossed and announce warning to user via TTS.
        
        Warnings depend on score_warning_level setting:
        - DISABLED: No warnings
        - MINIMAL: Warning at 21 (first penalty)
        - BALANCED: Warning at 21 and 41 (escalation)
        - COMPLETE: Warning at 20 (pre), 21, and 41
        
        Version: v2.6.0
        """
        level = self.settings.score_warning_level
        
        # Early exit if disabled
        if level == ScoreWarningLevel.DISABLED:
            return
        
        draw_count = self.service.scoring.stock_draw_count
        warning = None
        
        # COMPLETE level: Pre-warning at 20 (last free draw)
        if level == ScoreWarningLevel.COMPLETE and draw_count == 20:
            warning = (
                f"{ScoreFormatter.SCORING_WARNING_TAG} "
                f"Ultima pescata gratuita. "
                f"Dal prossimo draw penalità -1 punto per pescata."
            )
        
        # ALL levels (MINIMAL, BALANCED, COMPLETE): Warning at 21 (first penalty)
        elif draw_count == 21:
            warning = ScoreFormatter.format_threshold_warning(
                "stock_draw", 21, 20, -1
            )
        
        # BALANCED and COMPLETE: Warning at 41 (penalty doubles)
        elif level >= ScoreWarningLevel.BALANCED and draw_count == 41:
            warning = ScoreFormatter.format_threshold_warning(
                "stock_draw", 41, 40, -2
            )
        
        # Announce warning if any (use safe helper)
        if warning:
            self._speak(warning, interrupt=False)
    
    def _announce_recycle_threshold_warning(self) -> None:
        """Announce threshold warning for waste recycle based on warning level (v2.6.0).
        
        Called after successful recycle to check if a scoring threshold
        has been crossed and announce warning to user via TTS.
        
        Warnings depend on score_warning_level setting:
        - DISABLED: No warnings
        - MINIMAL: Warning at 3rd recycle (first penalty)
        - BALANCED: Warning at 3rd recycle
        - COMPLETE: Warning at 3rd, 4th, and 5th recycle
        
        Version: v2.6.0
        """
        level = self.settings.score_warning_level
        
        # Early exit if disabled
        if level == ScoreWarningLevel.DISABLED:
            return
        
        recycle_count = self.service.scoring.recycle_count
        warning = None
        
        # ALL levels: Warning at 3rd recycle (first penalty)
        if recycle_count == 3:
            warning = ScoreFormatter.format_threshold_warning(
                "recycle", 3, 2, -10
            )
        
        # COMPLETE level: Warning at 4th recycle (penalty doubles)
        elif level == ScoreWarningLevel.COMPLETE and recycle_count == 4:
            warning = (
                f"{ScoreFormatter.SCORING_WARNING_TAG} "
                f"Attenzione: quarto riciclo. Penalità totale -20 punti."
            )
        
        # COMPLETE level: Warning at 5th recycle (acceleration)
        elif level == ScoreWarningLevel.COMPLETE and recycle_count == 5:
            warning = (
                f"{ScoreFormatter.SCORING_WARNING_TAG} "
                f"Attenzione: quinto riciclo. "
                f"Penalità totale -35 punti. Crescita rapida."
            )
        
        # Announce warning if any (use safe helper)
        if warning:
            self._speak(warning, interrupt=False)
    
    def _debug_force_victory(self) -> str:
        """🔥 DEBUG ONLY: Simulate victory for testing end_game flow.
        
        Keyboard binding: CTRL+ALT+W
        
        ⚠️ WARNING: This is a debug feature for testing the victory flow!
        
        Simulates victory without actually completing the game.
        Useful for testing:
        - Final report formatting
        - Dialog appearance and accessibility
        - Score calculation accuracy
        - Rematch flow behavior
        - Suit statistics display
        
        Returns:
            Empty string (end_game() handles all TTS announcements)
            
        Example:
            >>> msg = engine._debug_force_victory()
            >>> print(msg)
            ""
            
            # end_game() announces victory report via TTS
            # Dialog shows full statistics
            # Prompts for rematch
        """
        if not self.is_game_running():
            return "Nessuna partita in corso da simulare!"
        
        # Trigger complete victory flow
        # Note: end_game() handles all TTS announcements and dialogs
        # Return empty string to avoid interrupting the report
        self.end_game(is_victory=True)
        
        return ""
    
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
    # HELPERS (Phase 3-7/7: Settings Integration COMPLETE!)
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
        
        # 1️⃣ Draw count from settings (v1.5.2.4 FIX)
        # Use settings.draw_count directly - respects user's explicit choice in Option #3
        # Level 4-5 constraints already enforced by GameSettings.cycle_draw_count()
        self.draw_count = self.settings.draw_count
        
        # 1.5️⃣ VALIDATE TIMER CONSTRAINTS FOR LEVELS 4-5
        if self.settings.difficulty_level >= 4:
            if self.settings.max_time_game <= 0:
                # Timer not enabled → force default
                if self.settings.difficulty_level == 4:
                    self.settings.max_time_game = 1800  # 30 minutes (middle of 5-60 range)
                else:  # Level 5
                    self.settings.max_time_game = 900   # 15 minutes (middle of 5-20 range)
                
                if self.screen_reader:
                    minutes = self.settings.max_time_game // 60
                    self.screen_reader.tts.speak(
                        f"Livello {self.settings.difficulty_level} richiede timer obbligatorio. "
                        f"Impostato automaticamente a {minutes} minuti.",
                        interrupt=False
                    )
            else:
                # Timer enabled → validate range
                if self.settings.difficulty_level == 4:
                    # Level 4: 5-60 minutes (300-3600 seconds)
                    if self.settings.max_time_game < 300:
                        self.settings.max_time_game = 300
                        if self.screen_reader:
                            self.screen_reader.tts.speak(
                                "Livello Esperto: limite minimo 5 minuti. Timer aumentato.",
                                interrupt=False
                            )
                    elif self.settings.max_time_game > 3600:
                        self.settings.max_time_game = 3600
                        if self.screen_reader:
                            self.screen_reader.tts.speak(
                                "Livello Esperto: limite massimo 60 minuti. Timer ridotto.",
                                interrupt=False
                            )
                else:  # Level 5
                    # Level 5: 5-20 minutes (300-1200 seconds)
                    if self.settings.max_time_game < 300:
                        self.settings.max_time_game = 300
                        if self.screen_reader:
                            self.screen_reader.tts.speak(
                                "Livello Maestro: limite minimo 5 minuti. Timer aumentato.",
                                interrupt=False
                            )
                    elif self.settings.max_time_game > 1200:
                        self.settings.max_time_game = 1200
                        if self.screen_reader:
                            self.screen_reader.tts.speak(
                                "Livello Maestro: limite massimo 20 minuti. Timer ridotto.",
                                interrupt=False
                            )
        
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
    
    # ========================================
    # SESSION OUTCOME (v2.7.0) - PHASE 8
    # ========================================
    
    def _build_session_outcome(self, end_reason: 'Union[EndReason, bool]') -> dict:
        """Build session outcome data for ProfileService.
        
        Args:
            end_reason: EndReason enum for game end classification
        
        Returns:
            Dict with all fields needed for SessionOutcome (v3.0.0)
        
        Note:
            This is a stub for future ProfileService integration.
            v3.0.0 will use this data to record game sessions.
        """
        from src.domain.models.game_end import EndReason
        
        # Convert to EndReason if needed
        if isinstance(end_reason, bool):
            end_reason = EndReason.VICTORY if end_reason else EndReason.ABANDON_EXIT
        
        # Convert VICTORY to VICTORY_OVERTIME if overtime active
        if end_reason == EndReason.VICTORY and self.service.overtime_start is not None:
            end_reason = EndReason.VICTORY_OVERTIME
        
        # Get timer mode
        timer_mode = "OFF"
        if self.settings and self.settings.max_time_game > 0:
            timer_mode = "STRICT" if self.settings.timer_strict_mode else "PERMISSIVE"
        
        # Get statistics
        stats = self.service.get_statistics()
        
        # Get final score if enabled
        final_score = 0
        if self.settings and self.settings.scoring_enabled and self.service.scoring:
            final_score = self.service.scoring.calculate_final_score(
                elapsed_seconds=stats['elapsed_time'],
                move_count=stats['move_count'],
                is_victory=end_reason.is_victory(),
                timer_strict_mode=self.settings.timer_strict_mode if self.settings else True
            )
        
        return {
            "end_reason": end_reason,
            "is_victory": end_reason.is_victory(),
            "elapsed_time": stats['elapsed_time'],
            "timer_enabled": self.settings.max_time_game > 0 if self.settings else False,
            "timer_limit": self.settings.max_time_game if self.settings else 0,
            "timer_mode": timer_mode,
            "timer_expired": self.service.timer_expired,
            "overtime_duration": self.service.get_overtime_duration(),
            
            # Gameplay stats (from GameService)
            "move_count": stats['move_count'],
            "draw_count_actions": stats['draw_count'],
            "recycle_count": self.service.recycle_count,
            "foundation_cards": list(self.service.carte_per_seme),
            "completed_suits": self.service.semi_completati,
            
            # Config
            "difficulty_level": self.settings.difficulty_level if self.settings else 1,
            "deck_type": self.settings.deck_type if self.settings else "french",
            "draw_count": self.draw_count,
            "shuffle_mode": "shuffle" if self.shuffle_on_recycle else "reverse",
            
            # Scoring (if enabled)
            "scoring_enabled": self.settings.scoring_enabled if self.settings else False,
            "final_score": final_score,
        }
