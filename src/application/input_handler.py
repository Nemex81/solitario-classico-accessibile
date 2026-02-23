"""Input handling for game commands.

Maps keyboard events to game commands with support for
modifiers (SHIFT, CTRL) and accessibility shortcuts.

Separates low-level input handling from high-level game logic,
following Clean Architecture principles.
"""

import pygame
from typing import Optional, Dict, Callable
from enum import Enum, auto


class GameCommand(Enum):
    """Semantic game commands.
    
    Represents high-level game actions that can be triggered
    by keyboard input. Separates "what" (command) from "how" (key).
    
    Navigation:
        MOVE_UP, MOVE_DOWN: Navigate cards in pile
        MOVE_LEFT, MOVE_RIGHT: Navigate between piles
    
    Selection:
        SELECT_CARD: Select card at cursor (ENTER)
        CANCEL_SELECTION: Cancel current selection (DELETE)
    
    Card Actions:
        DRAW_CARDS: Draw from stock pile (ENTER on mazzo)
        AUTO_MOVE: Auto-move to foundation (A key)
    
    Quick Access:
        QUICK_PILE_1-7: Jump to tableau pile 1-7 (keys 1-7)
        QUICK_FOUNDATION_1-4: Jump to foundation (SHIFT+1-4)
        QUICK_WASTE: Jump to waste pile (SHIFT+S)
        QUICK_STOCK: Jump to stock pile (SHIFT+M)
    
    Game Management:
        NEW_GAME: Start new game (N)
        HELP: Show help (H)
        STATS: Show statistics (S)
        QUIT: Return to menu (ESC)
    
    Settings (Function Keys):
        TOGGLE_DECK: Switch deck type (F1)
        TOGGLE_TIMER: Timer control (F2)
        DECREASE_TIMER: Decrease timer (F3)
        INCREASE_TIMER: Increase timer (F4)
        TOGGLE_SHUFFLE: Shuffle mode (F5)
    """
    
    # Navigation
    MOVE_UP = auto()
    MOVE_DOWN = auto()
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    
    # Selection
    SELECT_CARD = auto()
    CANCEL_SELECTION = auto()
    
    # Card actions
    DRAW_CARDS = auto()
    AUTO_MOVE = auto()
    
    # Quick access - Tableau (1-7)
    QUICK_PILE_1 = auto()
    QUICK_PILE_2 = auto()
    QUICK_PILE_3 = auto()
    QUICK_PILE_4 = auto()
    QUICK_PILE_5 = auto()
    QUICK_PILE_6 = auto()
    QUICK_PILE_7 = auto()
    
    # Quick access - Foundation (SHIFT+1-4)
    QUICK_FOUNDATION_1 = auto()
    QUICK_FOUNDATION_2 = auto()
    QUICK_FOUNDATION_3 = auto()
    QUICK_FOUNDATION_4 = auto()
    
    # Quick access - Special piles
    QUICK_WASTE = auto()   # SHIFT+S (scarti)
    QUICK_STOCK = auto()   # SHIFT+M (mazzo)
    
    # Game management
    NEW_GAME = auto()
    HELP = auto()
    STATS = auto()
    QUIT = auto()
    
    # Settings
    TOGGLE_DECK = auto()      # F1
    TOGGLE_TIMER = auto()     # F2
    DECREASE_TIMER = auto()   # F3
    INCREASE_TIMER = auto()   # F4
    TOGGLE_SHUFFLE = auto()   # F5


class InputHandler:
    """Handles keyboard input and command dispatch.
    
    **v3.4.0:** riceve un `audio_manager` opzionale per la generazione di
    AudioEvent (navigazione, selezione, cancellazione). Se non fornito,
    il comportamento è identico a prima (degradazione graziosa).
    
    Translates low-level PyGame keyboard events into high-level
    GameCommand enums. Supports modifiers (SHIFT, CTRL) and
    provides extensible key binding system.
    
    The handler is stateless - it only translates events to commands
    without storing game state.
    
    Attributes:
        key_bindings: Dict mapping (key, modifiers) to GameCommand
    
    Example:
        >>> handler = InputHandler()
        >>> event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
        >>> command = handler.handle_event(event)
        >>> if command == GameCommand.MOVE_UP:
        ...     game.move_cursor_up()
    """
    
    def __init__(self, audio_manager: Optional[object] = None) -> None:
        """Initialize input handler with default bindings.

        Args:
            audio_manager: Optional AudioManager instance (DI). Se fornito,
                verranno emessi AudioEvent per alcune azioni di navigazione e UI.
        """
        self.key_bindings: Dict[tuple, GameCommand] = {}
        self._audio = audio_manager
        self._initialize_bindings()
    
    def _initialize_bindings(self) -> None:
        """Setup default keyboard bindings.
        
        Bindings format: (key_code, shift, ctrl) -> GameCommand
        - shift/ctrl are booleans indicating if modifier is required
        
        This supports the full v1.3.3 keyboard interface including:
        - Arrow navigation
        - Number keys for quick pile access
        - SHIFT+numbers for foundation access (v1.3.0)
        - SHIFT+S/M for waste/stock (v1.3.0)
        - Function keys for settings
        """
        # Arrow keys - Navigation
        self.key_bindings[(pygame.K_UP, False, False)] = GameCommand.MOVE_UP
        self.key_bindings[(pygame.K_DOWN, False, False)] = GameCommand.MOVE_DOWN
        self.key_bindings[(pygame.K_LEFT, False, False)] = GameCommand.MOVE_LEFT
        self.key_bindings[(pygame.K_RIGHT, False, False)] = GameCommand.MOVE_RIGHT
        
        # Selection
        self.key_bindings[(pygame.K_RETURN, False, False)] = GameCommand.SELECT_CARD
        self.key_bindings[(pygame.K_DELETE, False, False)] = GameCommand.CANCEL_SELECTION
        
        # Card actions
        self.key_bindings[(pygame.K_a, False, False)] = GameCommand.AUTO_MOVE
        
        # Quick access - Tableau piles (1-7)
        self.key_bindings[(pygame.K_1, False, False)] = GameCommand.QUICK_PILE_1
        self.key_bindings[(pygame.K_2, False, False)] = GameCommand.QUICK_PILE_2
        self.key_bindings[(pygame.K_3, False, False)] = GameCommand.QUICK_PILE_3
        self.key_bindings[(pygame.K_4, False, False)] = GameCommand.QUICK_PILE_4
        self.key_bindings[(pygame.K_5, False, False)] = GameCommand.QUICK_PILE_5
        self.key_bindings[(pygame.K_6, False, False)] = GameCommand.QUICK_PILE_6
        self.key_bindings[(pygame.K_7, False, False)] = GameCommand.QUICK_PILE_7
        
        # Quick access - Foundation piles (SHIFT+1-4) [v1.3.0]
        self.key_bindings[(pygame.K_1, True, False)] = GameCommand.QUICK_FOUNDATION_1
        self.key_bindings[(pygame.K_2, True, False)] = GameCommand.QUICK_FOUNDATION_2
        self.key_bindings[(pygame.K_3, True, False)] = GameCommand.QUICK_FOUNDATION_3
        self.key_bindings[(pygame.K_4, True, False)] = GameCommand.QUICK_FOUNDATION_4
        
        # Quick access - Special piles (SHIFT+S/M) [v1.3.0]
        self.key_bindings[(pygame.K_s, True, False)] = GameCommand.QUICK_WASTE
        self.key_bindings[(pygame.K_m, True, False)] = GameCommand.QUICK_STOCK
        
        # Game management
        self.key_bindings[(pygame.K_n, False, False)] = GameCommand.NEW_GAME
        self.key_bindings[(pygame.K_h, False, False)] = GameCommand.HELP
        self.key_bindings[(pygame.K_s, False, False)] = GameCommand.STATS
        self.key_bindings[(pygame.K_ESCAPE, False, False)] = GameCommand.QUIT
        
        # Function keys - Settings
        self.key_bindings[(pygame.K_F1, False, False)] = GameCommand.TOGGLE_DECK
        self.key_bindings[(pygame.K_F2, False, False)] = GameCommand.TOGGLE_TIMER
        self.key_bindings[(pygame.K_F3, False, False)] = GameCommand.DECREASE_TIMER
        self.key_bindings[(pygame.K_F4, False, False)] = GameCommand.INCREASE_TIMER
        self.key_bindings[(pygame.K_F5, False, False)] = GameCommand.TOGGLE_SHUFFLE
    
    def handle_event(self, event: pygame.event.Event) -> Optional[GameCommand]:
        """Convert pygame event to game command.
        
        Detects modifier keys (SHIFT, CTRL) and looks up the
        corresponding GameCommand from bindings.
        
        Args:
            event: PyGame keyboard event
        
        Returns:
            GameCommand if key is bound, None if unrecognized or not KEYDOWN
        
        Example:
            >>> event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_1)
            >>> handler.handle_event(event)  # GameCommand.QUICK_PILE_1
            >>> 
            >>> # With SHIFT modifier
            >>> mods = pygame.key.get_mods()
            >>> # If SHIFT pressed: GameCommand.QUICK_FOUNDATION_1
        """
        # Only process KEYDOWN events
        if event.type != pygame.KEYDOWN:
            return None
        
        # Detect modifiers
        mods = pygame.key.get_mods()
        shift = bool(mods & pygame.KMOD_SHIFT)
        ctrl = bool(mods & pygame.KMOD_CTRL)
        
        # Lookup command
        key = event.key
        binding_key = (key, shift, ctrl)
        
        command = self.key_bindings.get(binding_key, None)
        # Emit audio feedback for navigation / UI events if available
        if self._audio and command is not None:
            try:
                from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
                if command in (
                    GameCommand.MOVE_UP,
                    GameCommand.MOVE_DOWN,
                    GameCommand.MOVE_LEFT,
                    GameCommand.MOVE_RIGHT,
                ):
                    # generic navigation sound
                    self._audio.play_event(AudioEvent(event_type=AudioEventType.UI_NAVIGATE))
                elif command == GameCommand.SELECT_CARD:
                    self._audio.play_event(AudioEvent(event_type=AudioEventType.UI_SELECT))
                elif command == GameCommand.CANCEL_SELECTION:
                    self._audio.play_event(AudioEvent(event_type=AudioEventType.UI_CANCEL))
            except Exception:
                pass  # degrade gracefully if audio subsystem fails
        return command
    
    def add_binding(
        self,
        key: int,
        command: GameCommand,
        shift: bool = False,
        ctrl: bool = False
    ) -> None:
        """Add or override a key binding.
        
        Allows customization of keyboard shortcuts.
        
        Args:
            key: PyGame key constant (e.g., pygame.K_a)
            command: GameCommand to bind
            shift: Require SHIFT modifier
            ctrl: Require CTRL modifier
        
        Example:
            >>> handler.add_binding(pygame.K_SPACE, GameCommand.AUTO_MOVE)
        """
        self.key_bindings[(key, shift, ctrl)] = command
    
    def remove_binding(
        self,
        key: int,
        shift: bool = False,
        ctrl: bool = False
    ) -> None:
        """Remove a key binding.
        
        Args:
            key: PyGame key constant
            shift: SHIFT modifier requirement
            ctrl: CTRL modifier requirement
        """
        binding_key = (key, shift, ctrl)
        if binding_key in self.key_bindings:
            del self.key_bindings[binding_key]
