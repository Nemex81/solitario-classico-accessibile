"""Gameplay orchestration with keyboard command mapping.

Maps 60+ keyboard commands to GameEngine methods with TTS feedback.
Provides same UX as legacy scr/game_play.py for audiogame interface.

Migrated from: scr/game_play.py
"""

import pygame
from pygame.locals import KMOD_SHIFT, KMOD_CTRL
from typing import Dict, Callable, Optional

from src.application.game_engine import GameEngine
from src.application.options_controller import OptionsWindowController
from src.domain.services.game_settings import GameSettings


class GamePlayController:
    """UI orchestrator for audiogame keyboard commands.
    
    Maps keyboard events to GameEngine operations with voice feedback.
    Supports 60+ commands including navigation, actions, info queries,
    and virtual options window with HYBRID navigation.
    
    Args:
        engine: GameEngine facade for game logic
        screen_reader: ScreenReader with TTS provider for voice feedback
    """
    
    def __init__(self, engine: GameEngine, screen_reader):
        self.engine = engine
        self.sr = screen_reader
        
        # Create GameSettings instance (not available in GameEngine yet)
        # TODO: In future, bind to engine.game_service.game_state for validation
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
        """Navigate to base pile (1-7 keys).
        
        Double-tap detection handled by CursorManager.
        """
        self.engine.jump_to_pile(pile_idx)
    
    def _nav_pile_semi(self, pile_idx: int) -> None:
        """Navigate to foundation pile (SHIFT+1-4).
        
        Args:
            pile_idx: Foundation pile index (7-10)
        """
        self.engine.jump_to_pile(pile_idx)
    
    def _nav_pile_scarti(self) -> None:
        """Navigate to waste pile (SHIFT+S)."""
        self.engine.jump_to_pile(11)
    
    def _nav_pile_mazzo(self) -> None:
        """Navigate to stock pile (SHIFT+M)."""
        self.engine.jump_to_pile(12)
    
    # === NAVIGAZIONE CURSORE ===
    
    def _cursor_up(self) -> None:
        """Arrow UP: Previous card in current pile."""
        self.engine.move_cursor("up")
    
    def _cursor_down(self) -> None:
        """Arrow DOWN: Next card in current pile."""
        self.engine.move_cursor("down")
    
    def _cursor_left(self) -> None:
        """Arrow LEFT: Previous pile."""
        self.engine.move_cursor("left")
    
    def _cursor_right(self) -> None:
        """Arrow RIGHT: Next pile."""
        self.engine.move_cursor("right")
    
    def _cursor_home(self) -> None:
        """HOME: First card in current pile."""
        self.engine.move_cursor("home")
    
    def _cursor_end(self) -> None:
        """END: Last card in current pile."""
        self.engine.move_cursor("end")
    
    def _cursor_tab(self) -> None:
        """TAB: Jump to different pile type."""
        self.engine.move_cursor("tab")
    
    # === AZIONI CARTE ===
    
    def _select_card(self) -> None:
        """ENTER: Select card under cursor.
        
        Special behavior:
        - On stock pile: Draw cards
        - On other piles: Select/toggle card
        - CTRL+ENTER: Select from waste pile
        """
        mods = pygame.key.get_mods()
        
        if mods & KMOD_CTRL:
            # CTRL+ENTER: Seleziona da scarti
            self.engine.select_from_waste()
        else:
            # ENTER normale: Seleziona carta o pesca
            self.engine.select_card_at_cursor()
    
    def _move_cards(self) -> None:
        """SPACE: Move selected cards to target pile."""
        success, message = self.engine.execute_move()
        # Message already vocalized by engine
    
    def _cancel_selection(self) -> None:
        """DELETE: Cancel current card selection."""
        self.engine.clear_selection()
    
    def _draw_cards(self) -> None:
        """D or P: Draw cards from stock pile."""
        success, message = self.engine.draw_from_stock()
        # Message already vocalized by engine
    
    # === QUERY INFORMAZIONI ===
    
    def _get_focus(self) -> None:
        """F: Get current cursor position."""
        self.engine.get_cursor_info()
    
    def _get_table_info(self) -> None:
        """G: Get complete table state."""
        self.engine.get_table_overview()
    
    def _get_game_report(self) -> None:
        """R: Get game report (time, moves, stats)."""
        state = self.engine.get_game_state()
        stats = state.get('statistics', {})
        moves = stats.get('move_count', 0)
        elapsed = int(stats.get('elapsed_time', 0))
        
        # Format time as MM:SS
        minutes = elapsed // 60
        seconds = elapsed % 60
        time_str = f"{minutes}:{seconds:02d}"
        
        report = f"Report partita.\n"
        report += f"Mosse: {moves}.\n"
        report += f"Tempo trascorso: {time_str}.\n"
        
        # Foundation progress
        foundations = state.get('piles', {}).get('foundations', [])
        total_in_foundations = sum(foundations)
        report += f"Carte nelle pile semi: {total_in_foundations}.\n"
        
        self._vocalizza(report, interrupt=True)
    
    def _get_card_info(self) -> None:
        """X: Get detailed info about card under cursor."""
        self.engine.get_card_at_cursor()
    
    def _get_selected_cards(self) -> None:
        """C: Get list of currently selected cards."""
        self.engine.get_selected_info()
    
    def _get_scarto_top(self) -> None:
        """S: Get top card from waste pile (read-only)."""
        pile_info = self.engine.get_pile_info(11)  # Waste pile
        
        if pile_info and pile_info.get('top_card'):
            card_name = pile_info['top_card']['name']
            self._vocalizza(f"Carta in cima agli scarti: {card_name}")
        else:
            self._vocalizza("Pila scarti vuota")
    
    def _get_deck_count(self) -> None:
        """M: Get remaining cards in stock pile."""
        state = self.engine.get_game_state()
        count = state.get('piles', {}).get('stock', 0)
        
        if count == 0:
            self._vocalizza("Il mazzo è vuoto")
        elif count == 1:
            self._vocalizza("Rimane 1 carta nel mazzo")
        else:
            self._vocalizza(f"Rimangono {count} carte nel mazzo")
    
    def _get_timer(self) -> None:
        """T: Get elapsed time."""
        state = self.engine.get_game_state()
        elapsed = int(state.get('statistics', {}).get('elapsed_time', 0))
        
        minutes = elapsed // 60
        seconds = elapsed % 60
        
        self._vocalizza(f"Tempo trascorso: {minutes} minuti e {seconds} secondi")
    
    def _get_settings(self) -> None:
        """I: Get current game settings (outside options window)."""
        settings = "Impostazioni di gioco.\n"
        settings += "Mazzo: carte francesi.\n"
        settings += "Difficoltà: livello 1.\n"
        settings += "Timer: disabilitato.\n"
        
        self._vocalizza(settings)
    
    def _show_help(self) -> None:
        """H: Show available commands help."""
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
        """N: Start new game (with confirmation if game running)."""
        state = self.engine.get_game_state()
        game_over = state.get('game_over', {}).get('is_over', True)
        
        if not game_over:
            # TODO: Implementare dialog conferma in futuro
            # Per ora avvia direttamente
            pass
        
        self.engine.new_game()
        # Message vocalized by engine.new_game()
    
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
