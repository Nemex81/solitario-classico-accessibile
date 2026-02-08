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
        screen_reader: ScreenReader with TTS provider for voice feedback
    """
    
    def __init__(self, engine: GameEngine, screen_reader):
        self.engine = engine
        self.sr = screen_reader
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
        """I: Get current game settings."""
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
    
    def _toggle_options(self) -> None:
        """O: Open/close options menu."""
        # TODO: Implementare menu opzioni in futuro
        self._vocalizza("Menu opzioni non ancora implementato. Usa F1-F5 per cambiare impostazioni.")
    
    # === FUNCTION KEYS (Settings) ===
    
    def _f1_handler(self) -> None:
        """F1: Change deck type (French/Neapolitan).
        
        CTRL+F1: Test victory (debug).
        """
        mods = pygame.key.get_mods()
        
        if mods & KMOD_CTRL:
            # CTRL+F1: Test vittoria (debug mode)
            self._vocalizza("Test vittoria: funzione debug non ancora implementata")
        else:
            # F1: Cambio mazzo
            # TODO: Implementare cambio mazzo in futuro
            self._vocalizza("Cambio tipo mazzo: funzione non ancora implementata")
    
    def _f2_handler(self) -> None:
        """F2: Change difficulty (1 or 3 cards draw mode)."""
        # TODO: Implementare cambio difficoltà in futuro
        self._vocalizza("Cambio difficoltà: funzione non ancora implementata")
    
    def _f3_handler(self) -> None:
        """F3: Decrease timer by 5 minutes.
        
        CTRL+F3: Disable timer.
        """
        mods = pygame.key.get_mods()
        
        if mods & KMOD_CTRL:
            # CTRL+F3: Disabilita timer
            self._vocalizza("Timer: funzione non ancora implementata")
        else:
            # F3: Decrementa 5 minuti
            self._vocalizza("Timer: funzione non ancora implementata")
    
    def _f4_handler(self) -> None:
        """F4: Increase timer by 5 minutes."""
        self._vocalizza("Timer: funzione non ancora implementata")
    
    def _f5_handler(self) -> None:
        """F5: Toggle shuffle/invert mode for waste pile recycling."""
        # TODO: Implementare toggle shuffle mode
        self._vocalizza("Modalità riciclo scarti: funzione non ancora implementata")
    
    def _esc_handler(self) -> None:
        """ESC: Quit game (with confirmation)."""
        # TODO: Implementare conferma in futuro
        self._vocalizza("Uscita dal gioco. Premi ancora ESC per confermare.")
        # Per ora non fa nulla, gestito da test.py
    
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
