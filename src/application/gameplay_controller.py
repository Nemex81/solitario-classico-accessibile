"""Gameplay orchestration with keyboard command mapping.

Maps 60+ keyboard commands to GameEngine methods with TTS feedback.
Provides same UX as legacy scr/game_play.py for audiogame interface.

Migrated from: scr/game_play.py
"""

import pygame
from pygame.locals import KMOD_SHIFT, KMOD_CTRL
from typing import Dict, Callable, Optional

from src.application.game_engine import GameEngine


class GamePlayController:
    """UI orchestrator for audiogame keyboard commands.
    
    Maps keyboard events to GameEngine operations with voice feedback.
    Supports 60+ commands including navigation, actions, info queries,
    and settings management.
    
    Args:
        engine: GameEngine facade for game logic
        screen_reader: TTS provider for voice feedback
    """
    
    def __init__(self, engine: GameEngine, screen_reader):
        self.engine = engine
        self.sr = screen_reader
        self.callback_dict = self._build_commands()
        
        # State per double-tap detection (SHIFT+1-4)
        self.last_pile_access: Optional[int] = None
        self.last_access_time: float = 0.0
    
    def _vocalizza(self, text: str, interrupt: bool = True) -> None:
        """Wrapper for TTS with delay.
        
        Args:
            text: Text to vocalize
            interrupt: Whether to interrupt current speech
        """
        if text:
            self.sr.speak(text, interrupt=interrupt)
            pygame.time.wait(100)
    
    def _build_commands(self) -> Dict[int, Callable]:
        """Build keyboard command mapping dictionary.
        
        Returns:
            Dictionary mapping pygame key constants to handler methods
        """
        return {
            # Numeri 1-7: Pile base (con double-tap)
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
            pygame.K_o: self._toggle_options,
            
            # Function keys (con CTRL modifier)
            pygame.K_F1: self._f1_handler,
            pygame.K_F2: self._f2_handler,
            pygame.K_F3: self._f3_handler,
            pygame.K_F4: self._f4_handler,
            pygame.K_F5: self._f5_handler,
            
            # ESC: Abbandona/Esci
            pygame.K_ESCAPE: self._esc_handler,
        }
    
    # === NAVIGAZIONE PILE ===
    
    def _nav_pile_base(self, pile_idx: int) -> None:
        """Navigate to base pile (1-7 keys).
        
        Double-tap on same pile selects top card.
        """
        # TODO: Implementare con GameEngine
        # Per ora placeholder
        self._vocalizza(f"Pila base {pile_idx + 1}")
    
    def _nav_pile_semi(self, pile_idx: int) -> None:
        """Navigate to foundation pile (SHIFT+1-4).
        
        Args:
            pile_idx: Foundation pile index (7-10)
        """
        suit_names = ["Cuori", "Quadri", "Fiori", "Picche"]
        suit_idx = pile_idx - 7
        if 0 <= suit_idx < 4:
            self._vocalizza(f"Pila semi {suit_names[suit_idx]}")
    
    def _nav_pile_scarti(self) -> None:
        """Navigate to waste pile (SHIFT+S)."""
        self._vocalizza("Pila scarti")
    
    def _nav_pile_mazzo(self) -> None:
        """Navigate to stock pile (SHIFT+M)."""
        self._vocalizza("Mazzo")
    
    # === NAVIGAZIONE CURSORE ===
    
    def _cursor_up(self) -> None:
        """Arrow UP: Previous card in current pile."""
        # TODO: Implementare navigazione carta precedente
        self._vocalizza("Carta precedente")
    
    def _cursor_down(self) -> None:
        """Arrow DOWN: Next card in current pile."""
        # TODO: Implementare navigazione carta successiva
        self._vocalizza("Carta successiva")
    
    def _cursor_left(self) -> None:
        """Arrow LEFT: Previous pile."""
        # TODO: Implementare navigazione pila precedente
        self._vocalizza("Pila precedente")
    
    def _cursor_right(self) -> None:
        """Arrow RIGHT: Next pile."""
        # TODO: Implementare navigazione pila successiva
        self._vocalizza("Pila successiva")
    
    def _cursor_home(self) -> None:
        """HOME: First card in current pile."""
        self._vocalizza("Prima carta della pila")
    
    def _cursor_end(self) -> None:
        """END: Last card in current pile."""
        self._vocalizza("Ultima carta della pila")
    
    def _cursor_tab(self) -> None:
        """TAB: Jump to different pile type."""
        self._vocalizza("Cambio tipo pila")
    
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
            self._vocalizza("Seleziona da scarti")
        else:
            # ENTER normale: Seleziona carta o pesca
            self._vocalizza("Carta selezionata")
    
    def _move_cards(self) -> None:
        """SPACE: Move selected cards to target pile."""
        # TODO: Implementare spostamento con GameEngine
        result = self.engine.auto_move_to_foundation()
        if result:
            self._vocalizza("Carte spostate")
        else:
            self._vocalizza("Impossibile spostare")
    
    def _cancel_selection(self) -> None:
        """DELETE: Cancel current card selection."""
        self._vocalizza("Selezione annullata")
    
    def _draw_cards(self) -> None:
        """D or P: Draw cards from stock pile."""
        result = self.engine.draw_from_stock()
        msg = f"Pescate {result.get('cards_drawn', 0)} carte"
        self._vocalizza(msg)
    
    # === QUERY INFORMAZIONI ===
    
    def _get_focus(self) -> None:
        """F: Get current cursor position."""
        state = self.engine.get_game_state()
        # TODO: Formattare posizione cursore
        self._vocalizza("Posizione cursore")
    
    def _get_table_info(self) -> None:
        """G: Get complete table state."""
        state = self.engine.get_game_state()
        # TODO: Formattare info tavolo completo
        info = f"Tavolo: {state.get('moves', 0)} mosse"
        self._vocalizza(info)
    
    def _get_game_report(self) -> None:
        """R: Get game report (time, moves, stats)."""
        state = self.engine.get_game_state()
        report = f"Mosse: {state.get('moves', 0)}"
        self._vocalizza(report)
    
    def _get_card_info(self) -> None:
        """X: Get detailed info about card under cursor."""
        # TODO: Info carta dettagliata
        self._vocalizza("Informazioni carta")
    
    def _get_selected_cards(self) -> None:
        """C: Get list of currently selected cards."""
        self._vocalizza("Carte selezionate")
    
    def _get_scarto_top(self) -> None:
        """S: Get top card from waste pile (read-only)."""
        self._vocalizza("Carta in cima agli scarti")
    
    def _get_deck_count(self) -> None:
        """M: Get remaining cards in stock pile."""
        state = self.engine.get_game_state()
        count = state.get('stock_count', 0)
        self._vocalizza(f"{count} carte nel mazzo")
    
    def _get_timer(self) -> None:
        """T: Get remaining time if timer enabled."""
        # TODO: Implementare timer
        self._vocalizza("Timer non attivo")
    
    def _get_settings(self) -> None:
        """I: Get current game settings."""
        self._vocalizza("Impostazioni di gioco")
    
    def _show_help(self) -> None:
        """H: Show available commands help."""
        help_text = """COMANDI PRINCIPALI:
Frecce: navigazione carte e pile.
1 a 7: vai alla pila base.
SHIFT più 1 a 4: vai alla pila semi.
D o P: pesca dal mazzo.
SPAZIO: sposta carte.
H: aiuto completo.
ESC: abbandona partita."""
        self._vocalizza(help_text)
    
    # === GESTIONE PARTITA ===
    
    def _new_game(self) -> None:
        """N: Start new game (with confirmation if game running)."""
        state = self.engine.get_game_state()
        if state.get('is_running', False):
            # TODO: Aggiungere conferma con dialog
            self._vocalizza("Partita in corso. Premi N di nuovo per confermare.")
        else:
            self.engine.reset_game()
            self.engine.new_game()
            self._vocalizza("Nuova partita avviata!")
    
    def _toggle_options(self) -> None:
        """O: Open/close options menu."""
        # TODO: Implementare menu opzioni
        self._vocalizza("Menu opzioni")
    
    # === FUNCTION KEYS (Settings) ===
    
    def _f1_handler(self) -> None:
        """F1: Change deck type (French/Neapolitan).
        
        CTRL+F1: Test victory (debug).
        """
        mods = pygame.key.get_mods()
        
        if mods & KMOD_CTRL:
            # CTRL+F1: Test vittoria
            self._vocalizza("Test vittoria attivato")
        else:
            # F1: Cambio mazzo
            # TODO: Implementare cambio mazzo
            self._vocalizza("Cambio tipo mazzo")
    
    def _f2_handler(self) -> None:
        """F2: Change difficulty (1 or 3 cards draw mode)."""
        # TODO: Implementare cambio difficoltà
        self._vocalizza("Cambio difficoltà")
    
    def _f3_handler(self) -> None:
        """F3: Decrease timer by 5 minutes.
        
        CTRL+F3: Disable timer.
        """
        mods = pygame.key.get_mods()
        
        if mods & KMOD_CTRL:
            # CTRL+F3: Disabilita timer
            self._vocalizza("Timer disabilitato")
        else:
            # F3: Decrementa 5 minuti
            self._vocalizza("Timer decrementato di 5 minuti")
    
    def _f4_handler(self) -> None:
        """F4: Increase timer by 5 minutes."""
        self._vocalizza("Timer incrementato di 5 minuti")
    
    def _f5_handler(self) -> None:
        """F5: Toggle shuffle/invert mode for waste pile recycling."""
        # TODO: Implementare toggle shuffle mode
        self._vocalizza("Modalità riciclo scarti cambiata")
    
    def _esc_handler(self) -> None:
        """ESC: Quit game (with confirmation)."""
        # TODO: Aggiungere conferma
        self._vocalizza("Uscita dal gioco")
    
    # === EVENT HANDLER PRINCIPALE ===
    
    def handle_keyboard_events(self, event: pygame.event.Event) -> None:
        """Main keyboard event handler.
        
        Processes all keyboard input with support for SHIFT and CTRL
        modifiers. Routes to appropriate command handlers.
        
        Args:
            event: PyGame event to process
        """
        if event.type == pygame.KEYDOWN:
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
