"""Gameplay orchestration with keyboard command mapping.

Maps 60+ keyboard commands to GameEngine methods with TTS feedback.
Provides same UX as legacy scr/game_play.py for audiogame interface.

Migrated from: scr/game_play.py

New in v1.4.2.1 (Bug Fix):
- Accept GameSettings parameter for proper settings binding
"""

import pygame
from pygame.locals import KMOD_SHIFT, KMOD_CTRL
from typing import Dict, Callable, Optional

from src.application.game_engine import GameEngine
from src.application.options_controller import OptionsWindowController
from src.domain.services.game_settings import GameSettings
from src.infrastructure.logging import game_logger as log


class GamePlayController:
    """UI orchestrator for audiogame keyboard commands.
    
    Maps keyboard events to GameEngine operations with voice feedback.
    Supports 60+ commands including navigation, actions, info queries,
    and virtual options window with HYBRID navigation.
    
    Args:
        engine: GameEngine facade for game logic
        screen_reader: ScreenReader with TTS provider for voice feedback
        settings: GameSettings instance (optional, creates new if not provided)
            NEW in v1.4.2.1: Allows binding to shared settings instance
    """
    
    def __init__(
        self, 
        engine: GameEngine, 
        screen_reader, 
        settings: Optional[GameSettings] = None,  # NEW PARAMETER (v1.4.2.1)
        on_new_game_request: Optional[Callable[[], None]] = None  # NEW PARAMETER (v1.4.3)
    ):
        """Initialize gameplay controller.
        
        Args:
            engine: GameEngine facade
            screen_reader: ScreenReader for TTS
            settings: GameSettings instance (optional)
                If None, creates new instance (backward compatible)
                If provided, uses shared instance from main app
            on_new_game_request: Callback when user requests new game with game active (v1.4.3)
                If None, starts directly (backward compatible)
                If provided, callback should show confirmation dialog
        """
        self.engine = engine
        self.sr = screen_reader
        
        # Store callback for new game confirmation (v1.4.3)
        self.on_new_game_request = on_new_game_request
        
        # Use provided settings or create new (backward compatibility)
        # NEW in v1.4.2.1: Proper settings binding
        if settings is not None:
            self.settings = settings
        else:
            # Fallback: Create new settings (legacy behavior)
            self.settings = GameSettings()
        
        # Initialize options controller
        self.options_controller = OptionsWindowController(self.settings)
        self._awaiting_save_response = False  # Dialog state
        self._just_opened_options = False  # Prevent immediate close due to key repeat
        
        self.callback_dict = self._build_commands()
    
    def _vocalizza(self, text: str, interrupt: bool = True) -> None:
        """Wrapper for TTS with delay.
        
        Args:
            text: Text to vocalize
            interrupt: Whether to interrupt current speech
        """
        if text:
            self.sr.tts.speak(text, interrupt=interrupt)
            pygame.time.wait(100)
    
    def _speak_with_hint(self, message: str, hint: Optional[str]) -> None:
        """Vocalizza messaggio e hint opzionale basato su settings (v1.5.0).
        
        Implementa conditional vocalization per Command Hints feature:
        - Messaggio principale sempre vocalizzato (interrupt=True)
        - Hint vocalizzato SOLO se settings.command_hints_enabled (interrupt=False)
        - Pausa 200ms tra messaggio e hint
        
        Args:
            message: Messaggio principale da vocalizzare
            hint: Hint opzionale da vocalizzare dopo pausa
        
        Pattern:
            ```python
            message, hint = cursor_manager.move_up()
            self._speak_with_hint(message, hint)
            ```
        """
        # Vocalizza messaggio principale
        self.sr.tts.speak(message, interrupt=True)
        
        # Vocalizza hint se abilitato nelle impostazioni
        if self.settings.command_hints_enabled and hint:
            pygame.time.wait(200)  # Pausa 200ms tra messaggio e hint
            self.sr.tts.speak(hint, interrupt=False)
    
    def _build_commands(self) -> Dict[int, Callable]:
        """Build keyboard command mapping dictionary.
        
        Returns:
            Dictionary mapping pygame key constants to handler methods
            
        Note: F1-F5 keys removed - use O to open options window
        """
        return {
            # Numeri 1-7: Pile base (con double-tap in CursorManager)
            pygame.K_1: lambda: self._nav_pile_base(0),
            pygame.K_2: lambda: self._nav_pile_base(1),
            pygame.K_3: lambda: self._nav_pile_base(2),
            pygame.K_4: lambda: self._nav_pile_base(3),
            pygame.K_5: lambda: self._nav_pile_base(4),
            pygame.K_6: lambda: self._nav_pile_base(5),
            pygame.K_7: lambda: self._nav_pile_base(6),
            
            # Frecce: Navigazione cursore
            pygame.K_UP: self._cursor_up,
            pygame.K_DOWN: self._cursor_down,
            pygame.K_LEFT: self._cursor_left,
            pygame.K_RIGHT: self._cursor_right,
            pygame.K_HOME: self._cursor_home,
            pygame.K_END: self._cursor_end,
            pygame.K_TAB: self._cursor_tab,
            
            # Azioni carte
            pygame.K_RETURN: self._select_card,
            pygame.K_SPACE: self._move_cards,
            pygame.K_DELETE: self._cancel_selection,
            
            # Pesca carte (due alias)
            pygame.K_d: self._draw_cards,
            pygame.K_p: self._draw_cards,
            
            # Query informazioni
            pygame.K_f: self._get_focus,
            pygame.K_g: self._get_table_info,
            pygame.K_r: self._get_game_report,
            pygame.K_x: self._get_card_info,
            pygame.K_c: self._get_selected_cards,
            pygame.K_s: self._get_scarto_top,
            pygame.K_m: self._get_deck_count,
            pygame.K_t: self._get_timer,
            pygame.K_i: self._get_settings,
            pygame.K_h: self._show_help,
            
            # Gestione partita
            pygame.K_n: self._new_game,
            pygame.K_o: self._handle_o_key,
            
            # ESC: Abbandona/Esci o chiude opzioni
            pygame.K_ESCAPE: self._esc_handler,
        }
    
    # === NAVIGAZIONE PILE ===
    
    def _nav_pile_base(self, pile_idx: int) -> None:
        """Navigate to base pile (1-7 keys) with hint support (v1.5.0).
        
        Double-tap detection handled by CursorManager.
        """
        # Temporarily disable engine's internal vocalization
        original_sr = self.engine.screen_reader
        self.engine.screen_reader = None
        
        msg, hint = self.engine.jump_to_pile(pile_idx)
        
        # Restore screen reader
        self.engine.screen_reader = original_sr
        
        # Use conditional hint vocalization
        self._speak_with_hint(msg, hint)
    
    def _nav_pile_semi(self, pile_idx: int) -> None:
        """Navigate to foundation pile (SHIFT+1-4) with hint support (v1.5.0).
        
        Args:
            pile_idx: Foundation pile index (7-10)
        """
        # Temporarily disable engine's internal vocalization
        original_sr = self.engine.screen_reader
        self.engine.screen_reader = None
        
        msg, hint = self.engine.jump_to_pile(pile_idx)
        
        # Restore screen reader
        self.engine.screen_reader = original_sr
        
        # Use conditional hint vocalization
        self._speak_with_hint(msg, hint)
    
    def _nav_pile_scarti(self) -> None:
        """Navigate to waste pile (SHIFT+S) with hint support (v1.5.0)."""
        # Temporarily disable engine's internal vocalization
        original_sr = self.engine.screen_reader
        self.engine.screen_reader = None
        
        msg, hint = self.engine.jump_to_pile(11)
        
        # Restore screen reader
        self.engine.screen_reader = original_sr
        
        # Use conditional hint vocalization
        self._speak_with_hint(msg, hint)
    
    def _nav_pile_mazzo(self) -> None:
        """Navigate to stock pile (SHIFT+M) with hint support (v1.5.0)."""
        # Temporarily disable engine's internal vocalization
        original_sr = self.engine.screen_reader
        self.engine.screen_reader = None
        
        msg, hint = self.engine.jump_to_pile(12)
        
        # Restore screen reader
        self.engine.screen_reader = original_sr
        
        # Use conditional hint vocalization
        self._speak_with_hint(msg, hint)
    
    # === NAVIGAZIONE CURSORE ===
    
    def _cursor_up(self) -> None:
        """Arrow UP: Previous card in current pile with hint support (v1.5.0)."""
        # Temporarily disable engine's internal vocalization
        original_sr = self.engine.screen_reader
        self.engine.screen_reader = None
        
        msg, hint = self.engine.move_cursor("up")
        
        # Restore screen reader
        self.engine.screen_reader = original_sr
        
        # Use conditional hint vocalization
        self._speak_with_hint(msg, hint)
    
    def _cursor_down(self) -> None:
        """Arrow DOWN: Next card in current pile with hint support (v1.5.0)."""
        # Temporarily disable engine's internal vocalization
        original_sr = self.engine.screen_reader
        self.engine.screen_reader = None
        
        msg, hint = self.engine.move_cursor("down")
        
        # Restore screen reader
        self.engine.screen_reader = original_sr
        
        # Use conditional hint vocalization
        self._speak_with_hint(msg, hint)
    
    def _cursor_left(self) -> None:
        """Arrow LEFT: Previous pile with hint support (v1.5.0)."""
        # Temporarily disable engine's internal vocalization
        original_sr = self.engine.screen_reader
        self.engine.screen_reader = None
        
        msg, hint = self.engine.move_cursor("left")
        
        # Restore screen reader
        self.engine.screen_reader = original_sr
        
        # Use conditional hint vocalization
        self._speak_with_hint(msg, hint)
    
    def _cursor_right(self) -> None:
        """Arrow RIGHT: Next pile with hint support (v1.5.0)."""
        # Temporarily disable engine's internal vocalization
        original_sr = self.engine.screen_reader
        self.engine.screen_reader = None
        
        msg, hint = self.engine.move_cursor("right")
        
        # Restore screen reader
        self.engine.screen_reader = original_sr
        
        # Use conditional hint vocalization
        self._speak_with_hint(msg, hint)
    
    def _cursor_home(self) -> None:
        """HOME: First card in current pile."""
        self.engine.move_cursor("home")
    
    def _cursor_end(self) -> None:
        """END: Last card in current pile."""
        self.engine.move_cursor("end")
    
    def _cursor_tab(self) -> None:
        """TAB: Jump to different pile type with hint support (v1.5.0)."""
        # Temporarily disable engine's internal vocalization
        original_sr = self.engine.screen_reader
        self.engine.screen_reader = None
        
        msg, hint = self.engine.move_cursor("tab")
        
        # Restore screen reader
        self.engine.screen_reader = original_sr
        
        # Use conditional hint vocalization
        self._speak_with_hint(msg, hint)
    
    # === AZIONI CARTE ===
    
    def _select_card(self) -> None:
        """ENTER: Select card under cursor (simple selection).
        
        This method is called from handle_wx_key_event() which already
        handles CTRL+ENTER separately via _select_from_waste().
        This method ONLY handles plain ENTER (no modifiers).
        
        Behavior:
        - On stock pile: Draw cards
        - On other piles: Select/toggle card
        
        Note:
            CTRL+ENTER is handled separately in handle_wx_key_event()
            at line ~739 as direct call to _select_from_waste().
            This separation ensures clean wxPython integration.
        
        Version:
            v1.7.5: Simplified for wxPython (removed pygame.key.get_mods)
        """
        # wxPython version: No modifier check needed
        # Modifiers already handled by caller handle_wx_key_event()
        success, message = self.engine.select_card_at_cursor()
        
        # Log card selection for analytics
        if success and "selezionat" in message.lower():
            # Extract card and pile info from current state
            try:
                pile = self.engine.cursor.get_current_pile()
                pile_name = self._get_pile_name(pile)
                # Get the selected card from pile
                card_name = "unknown"
                if pile and not pile.is_empty():
                    card = pile.get_top_card()
                    if card:
                        card_name = card.get_name()
                
                log.card_moved(
                    from_pile=pile_name,
                    to_pile="selected",
                    card=card_name,
                    success=True
                )
            except:
                # If extraction fails, skip logging rather than crash
                pass
    
    def _select_from_waste(self) -> None:
        """CTRL+ENTER: Select card from waste pile directly.
        
        Shortcut command for selecting top card from waste pile
        without needing to navigate cursor to it first.
        
        This is a convenience wrapper around engine.select_from_waste()
        for wxPython keyboard mapping.
        
        Called from:
            - handle_wx_key_event() when CTRL+ENTER pressed (line ~739)
        
        Equivalent pygame command:
            - CTRL+ENTER in handle_keyboard_events()
        
        Example:
            User presses CTRL+ENTER while cursor is on tableau pile.
            Instead of moving cursor to waste, this directly selects
            the top waste card for moving.
        
        Version:
            v1.7.5: New helper method for wxPython keyboard mapping
        """
        success, message = self.engine.select_from_waste()
        
        # Log waste card selection
        if success and "selezionat" in message.lower():
            # Extract card name from waste pile
            try:
                card_name = "unknown"
                waste_pile = self.engine.service.table.waste
                if waste_pile and not waste_pile.is_empty():
                    card = waste_pile.get_top_card()
                    if card:
                        card_name = card.get_name()
                
                log.card_moved(
                    from_pile="waste",
                    to_pile="selected",
                    card=card_name,
                    success=True
                )
            except:
                pass  # Don't crash on logging errors
    
    def _move_cards(self) -> None:
        """SPACE: Move selected cards to target pile."""
        success, message = self.engine.execute_move()
        # Message already vocalized by engine
        
        # Log card move for analytics
        if success:
            try:
                dest_pile = self.engine.cursor.get_current_pile()
                dest_name = self._get_pile_name(dest_pile)
                origin_pile = self.engine.selection.origin_pile if self.engine.selection.has_selection() else None
                origin_name = self._get_pile_name(origin_pile) if origin_pile else "unknown"
                
                # Get card names from selection
                card_names = "unknown"
                if self.engine.selection.has_selection():
                    cards = self.engine.selection.selected_cards
                    if cards:
                        if len(cards) == 1:
                            card_names = cards[0].get_name()
                        else:
                            card_names = f"{len(cards)} cards ({cards[0].get_name()} + {len(cards)-1} more)"
                
                log.card_moved(
                    from_pile=origin_name,
                    to_pile=dest_name,
                    card=card_names,
                    success=True
                )
            except:
                pass  # Don't crash on logging errors
        elif "Invalid" in message or "Non" in message:
            # Failed move - log as invalid action
            log.invalid_action(
                action="move_cards",
                reason=message[:100]  # Truncate if too long
            )
    
    def _cancel_selection(self) -> None:
        """DELETE: Cancel current card selection."""
        self.engine.clear_selection()
    
    def _draw_cards(self) -> None:
        """D or P: Draw cards from stock pile."""
        success, message = self.engine.draw_from_stock()
        # Message already vocalized by engine
        
        # Log card draw (DEBUG level - high frequency event)
        if success:
            # Determine draw count from settings
            draw_count = 3 if self.settings.deck_type == "draw_three" else 1
            log.cards_drawn(count=draw_count)
    
    # === QUERY INFORMAZIONI ===
    
    def _get_focus(self) -> None:
        """F: Get current cursor position."""
        log.info_query_requested("cursor_position")
        self.engine.get_cursor_info()
    
    def _get_table_info(self) -> None:
        """G: Get complete table state with hint support (v1.5.0)."""
        log.info_query_requested("table_info")
        msg, hint = self.engine.service.get_table_info()
        self._speak_with_hint(msg, hint)
    
    def _get_game_report(self) -> None:
        """R: Get game report (time, moves, stats) with hint support (v1.5.0)."""
        log.info_query_requested("game_report")
        msg, hint = self.engine.service.get_game_report()
        self._speak_with_hint(msg, hint)
    
    def _get_card_info(self) -> None:
        """X: Get detailed info about card under cursor."""
        log.info_query_requested("card_info")
        self.engine.get_card_at_cursor()
    
    def _get_selected_cards(self) -> None:
        """C: Get list of currently selected cards."""
        log.info_query_requested("selected_cards")
        self.engine.get_selected_info()
    
    def _get_scarto_top(self) -> None:
        """S: Get top card from waste pile with hint support (v1.5.0)."""
        log.info_query_requested("waste_top")
        msg, hint = self.engine.service.get_waste_info()
        self._speak_with_hint(msg, hint)
    
    def _get_deck_count(self) -> None:
        """M: Get remaining cards in stock pile with hint support (v1.5.0)."""
        log.info_query_requested("stock_count")
        msg, hint = self.engine.service.get_stock_info()
        self._speak_with_hint(msg, hint)
    
    def _get_timer(self) -> None:
        """T: Get timer info (elapsed or countdown based on settings) - v1.5.1.
        
        Behavior:
        - Timer OFF: Shows elapsed time
        - Timer ON: Shows countdown (remaining time)
        - Timer expired: Shows "Tempo scaduto!"
        
        No hint vocalized during gameplay (v1.5.1 user request).
        """
        log.info_query_requested("timer_status")
        # Pass max_time from settings to service (v1.5.1)
        msg, hint = self.engine.service.get_timer_info(
            max_time=self.settings.max_time_game
        )
        
        # Vocalize (hint will be None, so only message speaks)
        self._speak_with_hint(msg, hint)
    
    def _get_settings(self) -> None:
        """I: Get current game settings with hint support (v1.5.0)."""
        log.info_query_requested("settings_info")
        msg, hint = self.engine.service.get_settings_info()
        self._speak_with_hint(msg, hint)
    
    def _show_help(self) -> None:
        """H: Show available commands help."""
        log.info_query_requested("help")
        help_text = """COMANDI PRINCIPALI:
Frecce: navigazione carte e pile.
1 a 7: vai alla pila base.
SHIFT più 1 a 4: vai alla pila semi.
INVIO: seleziona carta.
SPAZIO: sposta carte selezionate.
CANC: annulla selezione.
D o P: pesca dal mazzo.
F: posizione cursore.
X: info carta.
G: stato tavolo.
R: report partita.
N: nuova partita.
O: apri finestra opzioni.
ESC: abbandona partita."""
        
        self._vocalizza(help_text, interrupt=True)
    
    # === GESTIONE PARTITA ===
    
    def _new_game(self) -> None:
        """N: Start new game (with confirmation if game running).
        
        Behavior (v1.4.3):
        - If game NOT running: Start immediately
        - If game running + callback provided: Call callback (shows dialog)
        - If game running + NO callback: Start directly (backward compatible)
        """
        state = self.engine.get_game_state()
        game_over = state.get('game_over', {}).get('is_over', True)
        
        if not game_over:
            # Game is running - check if callback is available (v1.4.3)
            if self.on_new_game_request is not None:
                # Delegate to callback (will show confirmation dialog)
                self.on_new_game_request()
                return  # Don't start game here, callback will handle it
            # else: No callback, fall through to start directly (backward compatible)
        
        # Start new game immediately (no game running OR no callback)
        self.engine.new_game()
        # Message vocalized by engine.new_game()
        
        # Log new game started with settings
        try:
            deck_type = "draw_three" if self.settings.deck_type == "draw_three" else "draw_one"
            difficulty = getattr(self.settings, 'difficulty', 'medium')
            timer_enabled = getattr(self.settings, 'timer_enabled', False)
            
            log.game_started(
                deck_type=deck_type,
                difficulty=str(difficulty),
                timer_enabled=timer_enabled
            )
        except:
            # If settings are unavailable, log minimal info
            log.game_started(deck_type="unknown", difficulty="unknown", timer_enabled=False)
    
    def _handle_o_key(self) -> None:
        """O: Open/close options window.
        
        Behavior:
        - If closed: Open window (only if no game running)
        - If open: Close with save confirmation if modified
        """
        if self.options_controller.is_open:
            # Already open, close it
            msg = self.options_controller.close_window()
            
            # Check if save dialog prompted
            if "modifiche non salvate" in msg:
                self._awaiting_save_response = True
            
            self._vocalizza(msg, interrupt=True)
        else:
            # Open window (block if game running)
            # TODO: Use self.engine.is_game_running() when available
            # For now, check game_state from settings
            if self.settings.game_state.is_running:
                self._vocalizza("Non puoi aprire le opzioni durante una partita! Premi N per nuova partita.", interrupt=True)
            else:
                msg = self.options_controller.open_window()
                self._just_opened_options = True  # Prevent immediate close from key repeat
                self._vocalizza(msg, interrupt=True)
    
    # === OPTIONS WINDOW HANDLERS ===
    
    def _handle_options_events(self, event: pygame.event.Event) -> None:
        """Handle keyboard events when options window is open.
        
        Routes all input to options controller, blocking gameplay.
        
        Args:
            event: Pygame keyboard event
        """
        # Priority: Check if in save dialog
        if self._awaiting_save_response:
            self._handle_save_dialog(event)
            return
        
        # Clear just_opened flag on any key except O
        # This allows first arrow/number key to work and prevents accidental close
        if self._just_opened_options and event.key != pygame.K_o:
            self._just_opened_options = False
        
        # Normal options navigation
        msg = None
        
        if event.key == pygame.K_o:
            # O: Close options (with confirmation)
            # BUT: Ignore if just opened (prevent key repeat double-trigger)
            if self._just_opened_options:
                self._just_opened_options = False  # Consume the flag
                return  # Ignore this O press
            
            msg = self.options_controller.close_window()
            if "modifiche non salvate" in msg:
                self._awaiting_save_response = True
        
        elif event.key == pygame.K_UP:
            msg = self.options_controller.navigate_up()
        
        elif event.key == pygame.K_DOWN:
            msg = self.options_controller.navigate_down()
        
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            msg = self.options_controller.modify_current_option()
        
        elif event.key == pygame.K_ESCAPE:
            msg = self.options_controller.close_window()
            if "modifiche non salvate" in msg:
                self._awaiting_save_response = True
        
        # Number keys 1-5: Jump to option
        elif event.key == pygame.K_1:
            msg = self.options_controller.jump_to_option(0)
        elif event.key == pygame.K_2:
            msg = self.options_controller.jump_to_option(1)
        elif event.key == pygame.K_3:
            msg = self.options_controller.jump_to_option(2)
        elif event.key == pygame.K_4:
            msg = self.options_controller.jump_to_option(3)
        elif event.key == pygame.K_5:
            msg = self.options_controller.jump_to_option(4)
        
        # Timer controls (+/-/T)
        elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
            msg = self.options_controller.increment_timer()
        elif event.key == pygame.K_MINUS:
            msg = self.options_controller.decrement_timer()
        elif event.key == pygame.K_t:
            msg = self.options_controller.toggle_timer()
        
        # Information keys (I/H)
        elif event.key == pygame.K_i:
            msg = self.options_controller.read_all_settings()
        elif event.key == pygame.K_h:
            msg = self.options_controller.show_help()
        
        # Vocalize response
        if msg:
            self._vocalizza(msg, interrupt=True)
    
    def _handle_save_dialog(self, event: pygame.event.Event) -> None:
        """Handle save confirmation dialog.
        
        Keys:
        - S: Save and close
        - N: Discard and close
        - ESC: Cancel (stay in options)
        
        Args:
            event: Pygame keyboard event
        """
        msg = None
        
        if event.key == pygame.K_s:
            # Save and close
            msg = self.options_controller.save_and_close()
            self._awaiting_save_response = False
        
        elif event.key == pygame.K_n:
            # Discard and close
            msg = self.options_controller.discard_and_close()
            self._awaiting_save_response = False
        
        elif event.key == pygame.K_ESCAPE:
            # Cancel (stay in options)
            msg = self.options_controller.cancel_close()
            self._awaiting_save_response = False
        
        if msg:
            self._vocalizza(msg, interrupt=True)
    
    def _esc_handler(self) -> None:
        """ESC: Close options window or quit game.
        
        Priority:
        1. If options open: Close with confirmation
        2. Otherwise: Handled by test.py (return to menu)
        """
        # Se opzioni aperte, chiudile
        if self.options_controller.is_open:
            msg = self.options_controller.close_window()
            
            # Check if save dialog prompted
            if "modifiche non salvate" in msg:
                self._awaiting_save_response = True
            
            self._vocalizza(msg, interrupt=True)
        else:
            # Altrimenti gestito da test.py (ritorno al menu)
            pass
    
    # === EVENT HANDLER PRINCIPALE ===
    
    def handle_wx_key_event(self, event) -> bool:
        """Handle wxPython keyboard events by routing directly to gameplay methods.
        
        Maps wx.KeyEvent to gameplay commands without pygame conversion.
        Returns True if the key was handled, False otherwise.
        
        Args:
            event: wx.KeyEvent from wxPython event loop
        
        Returns:
            bool: True if key was handled, False if not recognized
        
        Mapped Keys (v1.7.5 - complete 60+ command support):
            Navigation:
            - Numbers 1-7: Jump to tableau pile
            - SHIFT+1-4: Jump to foundation pile
            - SHIFT+S: Jump to waste pile
            - SHIFT+M: Jump to stock pile
            - Arrow keys: Cursor navigation
            - HOME/END: First/last card in pile
            - TAB: Jump to different pile type
            - DELETE: Cancel selection
            
            Actions:
            - ENTER/RETURN: Select card
            - CTRL+ENTER: Select from waste
            - SPACE: Move cards
            - D/P: Draw cards
            
            Query Commands (info):
            - F: Focus/cursor position
            - G: Table info (all piles)
            - R: Game report (stats/time)
            - X: Card detailed info
            - C: Selected cards info
            - S: Waste top card
            - M: Stock count
            - T: Timer status
            - I: Current settings
            - H: Help/command list
            
            Game Management:
            - N: New game
            - O: Options window
            - CTRL+ALT+W: Debug force victory
        
        Note:
            Does not call event.Skip() - caller decides whether to propagate.
            All keys are case-insensitive where applicable.
        
        Example:
            >>> # In GameplayPanel.on_key_down():
            >>> handled = controller.gameplay_controller.handle_wx_key_event(event)
            >>> if handled:
            ...     return  # Key consumed
            >>> event.Skip()  # Key not handled, propagate
        
        New in v1.7.5: Complete keyboard mapping (60+ commands)
        """
        # Import wx locally to avoid module-level dependency
        import wx
        
        key_code = event.GetKeyCode()
        
        # Get modifier state
        modifiers = event.GetModifiers()
        has_shift = bool(modifiers & wx.MOD_SHIFT)
        has_ctrl = bool(modifiers & wx.MOD_CONTROL)
        has_alt = bool(modifiers & wx.MOD_ALT)
        
        # ═══════════════════════════════════════════════════════════
        # PRIORITY 1: SHIFT COMBINATIONS (must check before plain keys)
        # ═══════════════════════════════════════════════════════════
        if has_shift:
            # SHIFT+1-4: Foundation piles (semi)
            if key_code == ord('1'):
                self._nav_pile_semi(7)  # Hearts (Cuori)
                return True
            elif key_code == ord('2'):
                self._nav_pile_semi(8)  # Diamonds (Quadri)
                return True
            elif key_code == ord('3'):
                self._nav_pile_semi(9)  # Clubs (Fiori)
                return True
            elif key_code == ord('4'):
                self._nav_pile_semi(10)  # Spades (Picche)
                return True
            
            # SHIFT+S: Waste pile (scarti)
            elif key_code in (ord('S'), ord('s')):
                self._nav_pile_scarti()
                return True
            
            # SHIFT+M: Stock pile (mazzo)
            elif key_code in (ord('M'), ord('m')):
                self._nav_pile_mazzo()
                return True
        
        # ═══════════════════════════════════════════════════════════
        # PRIORITY 2: CTRL COMBINATIONS
        # ═══════════════════════════════════════════════════════════
        if has_ctrl:
            # CTRL+ENTER: Select from waste pile
            if key_code in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
                self._select_from_waste()
                return True
            
            # CTRL+ALT+W: Debug force victory
            if has_alt and key_code in (ord('W'), ord('w')):
                msg = self.engine._debug_force_victory()
                if msg:
                    self._vocalizza(msg)
                return True
        
        # ═══════════════════════════════════════════════════════════
        # NUMBER KEYS 1-7: Tableau piles (pile base) - NO SHIFT
        # ═══════════════════════════════════════════════════════════
        if not has_shift and ord('1') <= key_code <= ord('7'):
            pile_idx = key_code - ord('1')  # 0-6
            self._nav_pile_base(pile_idx)
            return True
        
        # ═══════════════════════════════════════════════════════════
        # ARROW KEYS: Cursor navigation
        # ═══════════════════════════════════════════════════════════
        if key_code == wx.WXK_UP:
            self._cursor_up()
            return True
        elif key_code == wx.WXK_DOWN:
            self._cursor_down()
            return True
        elif key_code == wx.WXK_LEFT:
            self._cursor_left()
            return True
        elif key_code == wx.WXK_RIGHT:
            self._cursor_right()
            return True
        
        # ═══════════════════════════════════════════════════════════
        # ADVANCED NAVIGATION: HOME/END/TAB/DELETE
        # ═══════════════════════════════════════════════════════════
        elif key_code == wx.WXK_HOME:
            self._cursor_home()
            return True
        elif key_code == wx.WXK_END:
            self._cursor_end()
            return True
        elif key_code == wx.WXK_TAB:
            self._cursor_tab()
            return True
        elif key_code == wx.WXK_DELETE:
            self._cancel_selection()
            return True
        
        # ═══════════════════════════════════════════════════════════
        # ACTION KEYS: Select and Move
        # ═══════════════════════════════════════════════════════════
        elif key_code in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            self._select_card()
            return True
        
        elif key_code == wx.WXK_SPACE:
            self._move_cards()
            return True
        
        # ═══════════════════════════════════════════════════════════
        # DRAW KEYS: D or P
        # ═══════════════════════════════════════════════════════════
        elif key_code in (ord('D'), ord('d'), ord('P'), ord('p')):
            self._draw_cards()
            return True
        
        # ═══════════════════════════════════════════════════════════
        # QUERY INFORMATION KEYS (10 commands)
        # ═══════════════════════════════════════════════════════════
        
        # F: Get focus (cursor position)
        elif key_code in (ord('F'), ord('f')):
            self._get_focus()
            return True
        
        # G: Get table info (all piles status)
        elif key_code in (ord('G'), ord('g')):
            self._get_table_info()
            return True
        
        # R: Get game report (stats, time, moves)
        elif key_code in (ord('R'), ord('r')):
            self._get_game_report()
            return True
        
        # X: Get card info (detailed card at cursor)
        elif key_code in (ord('X'), ord('x')):
            self._get_card_info()
            return True
        
        # C: Get selected cards (current selection)
        elif key_code in (ord('C'), ord('c')):
            self._get_selected_cards()
            return True
        
        # S: Get scarto top (waste pile top card)
        # NOTE: SHIFT+S handled above, this is plain S
        elif not has_shift and key_code in (ord('S'), ord('s')):
            self._get_scarto_top()
            return True
        
        # M: Get deck count (stock pile remaining)
        # NOTE: SHIFT+M handled above, this is plain M
        elif not has_shift and key_code in (ord('M'), ord('m')):
            self._get_deck_count()
            return True
        
        # T: Get timer (elapsed or countdown)
        elif key_code in (ord('T'), ord('t')):
            self._get_timer()
            return True
        
        # I: Get settings (current game configuration)
        elif key_code in (ord('I'), ord('i')):
            self._get_settings()
            return True
        
        # H: Show help (command list)
        elif key_code in (ord('H'), ord('h')):
            self._show_help()
            return True
        
        # ═══════════════════════════════════════════════════════════
        # GAME MANAGEMENT KEYS
        # ═══════════════════════════════════════════════════════════
        
        # N: New game
        elif key_code in (ord('N'), ord('n')):
            self._new_game()
            return True
        
        # O: Open/close options window
        elif key_code in (ord('O'), ord('o')):
            self._handle_o_key()
            return True
        
        # ═══════════════════════════════════════════════════════════
        # KEY NOT RECOGNIZED
        # ═══════════════════════════════════════════════════════════
        return False
    
    def handle_keyboard_events(self, event: pygame.event.Event) -> None:
        """Main keyboard event handler.
        
        Processes all keyboard input with priority routing:
        1. PRIORITY: If options window open -> route to _handle_options_events
        2. Otherwise: Normal gameplay commands
        
        Special modes:
        - Options window: Full key remapping (arrows/numbers/etc)
        - Save dialog: Only S/N/ESC accepted
        - Normal gameplay: All gameplay commands available
        
        Args:
            event: PyGame event to process
        """
        if event.type == pygame.KEYDOWN:
            # === PRIORITY 1: OPTIONS WINDOW ROUTING ===
            if self.options_controller.is_open:
                self._handle_options_events(event)
                return  # Block all gameplay commands
            
            # === NORMAL GAMEPLAY ===
            mods = pygame.key.get_mods()
            
            # ═══════════════════════════════════════════════════════
            # 🔥 DEBUG: Force victory (CTRL+ALT+W) - v1.6.0
            # ═══════════════════════════════════════════════════════
            if (event.key == pygame.K_w and 
                (mods & KMOD_CTRL) and 
                (mods & pygame.KMOD_ALT)):
                msg = self.engine._debug_force_victory()
                self._vocalizza(msg)
                return
            
            # === SHIFT MODIFIERS (Priority over normal commands) ===
            if mods & KMOD_SHIFT:
                # SHIFT+1-4: Pile semi (fondazioni)
                if event.key == pygame.K_1:
                    self._nav_pile_semi(7)  # Cuori
                    return
                elif event.key == pygame.K_2:
                    self._nav_pile_semi(8)  # Quadri
                    return
                elif event.key == pygame.K_3:
                    self._nav_pile_semi(9)  # Fiori
                    return
                elif event.key == pygame.K_4:
                    self._nav_pile_semi(10)  # Picche
                    return
                # SHIFT+S: Scarti
                elif event.key == pygame.K_s:
                    self._nav_pile_scarti()
                    return
                # SHIFT+M: Mazzo
                elif event.key == pygame.K_m:
                    self._nav_pile_mazzo()
                    return
            
            # === COMANDI NORMALI ===
            if event.key in self.callback_dict:
                self.callback_dict[event.key]()
    
    def _get_pile_name(self, pile) -> str:
        """Helper to get human-readable pile name for logging.
        
        Args:
            pile: Pile object from game engine
        
        Returns:
            String name like "tableau_1", "foundation_2", "stock", "waste"
        """
        if pile is None:
            return "unknown"
        
        try:
            # Try to get pile type from the engine's pile structure
            tableau_piles = self.engine.service.table.tableau
            for i, tableau_pile in enumerate(tableau_piles, 1):
                if pile == tableau_pile:
                    return f"tableau_{i}"
            
            foundation_piles = self.engine.service.table.foundations
            for i, foundation_pile in enumerate(foundation_piles, 1):
                if pile == foundation_pile:
                    return f"foundation_{i}"
            
            if pile == self.engine.service.table.stock:
                return "stock"
            
            if pile == self.engine.service.table.waste:
                return "waste"
        except:
            pass
        
        return "unknown"
