"""Virtual menu for audiogame navigation.

Provides keyboard-navigable menu without visual widgets,
using only screen reader feedback for accessibility.

This is a pure audiogame component - the pygame surface is blank,
all interaction happens through TTS voice feedback.

Migrated from: scr/pygame_menu.py
Enhanced with type hints and improved documentation.
"""

import pygame
from typing import List, Callable, Optional, TYPE_CHECKING

# Type checking import to avoid circular dependencies
if TYPE_CHECKING:
    from src.infrastructure.accessibility.screen_reader import ScreenReader


class VirtualMenu:
    """Keyboard-navigable virtual menu for audiogame.
    
    Pure audio interface without visual widgets. Uses TTS
    for all feedback. Navigation via UP/DOWN arrows, selection
    via ENTER.
    
    This component follows the "audiogame" paradigm where all
    user interaction happens through audio feedback, making the
    game fully accessible to blind users.
    
    Navigation Features:
    - Wrap-around: DOWN on last item → first item
    - Wrap-around: UP on first item → last item
    - Immediate TTS feedback on every navigation
    - Interrupt current speech for responsive navigation
    
    Attributes:
        items: List of menu item text (in order)
        callback: Function called with selected index on ENTER
        screen: PyGame surface (blank for audiogame)
        sr: ScreenReader instance for TTS feedback
        selected_index: Current menu selection (0-based)
    
    Example:
        >>> def handle_selection(index: int):
        ...     if index == 0:
        ...         start_game()
        ...     elif index == 1:
        ...         quit_game()
        >>> 
        >>> menu = VirtualMenu(
        ...     items=["Gioca", "Esci"],
        ...     callback=handle_selection,
        ...     screen=pygame_screen,
        ...     screen_reader=sr_instance
        ... )
        >>> # Menu automatically announces: "Menu aperto. 2 opzioni..."
    """
    
    def __init__(
        self,
        items: List[str],
        callback: Callable[[int], None],
        screen: pygame.Surface,
        screen_reader: 'ScreenReader'
    ) -> None:
        """Initialize virtual menu.
        
        Args:
            items: List of menu item strings (order preserved)
            callback: Function to call on ENTER with selected index
            screen: PyGame surface (audiogame - typically blank)
            screen_reader: ScreenReader with TTS provider for voice output
            
        Side Effects:
            Immediately announces menu opening with item count and
            first item name via TTS.
        """
        self.items = items
        self.callback = callback
        self.screen = screen
        self.sr = screen_reader
        self.selected_index = 0
        
        # Announce menu opening on initialization
        self._announce_menu_open()
    
    def _announce_menu_open(self) -> None:
        """Announce menu opening with item count and first item.
        
        Provides context to user:
        1. "Menu aperto. N opzioni disponibili."
        2. Brief pause (300ms)
        3. First menu item name
        
        This helps orient the user in the menu structure.
        """
        count_msg = f"Menu aperto. {len(self.items)} opzioni disponibili."
        self.sr.tts.speak(count_msg, interrupt=True)
        pygame.time.wait(300)  # Pause between announcement and first item
        self.sr.tts.speak(self.items[self.selected_index], interrupt=False)
    
    def next_item(self) -> None:
        """Move to next menu item (Arrow DOWN).
        
        Implements wrap-around: if at last item, moves to first item.
        Immediately announces new selection via TTS with interrupt.
        
        Keyboard: K_DOWN (Arrow Down)
        """
        if self.selected_index < len(self.items) - 1:
            self.selected_index += 1
        else:
            # Wrap around to beginning
            self.selected_index = 0
        
        # Announce new selection (interrupt current speech for responsiveness)
        self.sr.tts.speak(self.items[self.selected_index], interrupt=True)
    
    def prev_item(self) -> None:
        """Move to previous menu item (Arrow UP).
        
        Implements wrap-around: if at first item, moves to last item.
        Immediately announces new selection via TTS with interrupt.
        
        Keyboard: K_UP (Arrow Up)
        """
        if self.selected_index > 0:
            self.selected_index -= 1
        else:
            # Wrap around to end
            self.selected_index = len(self.items) - 1
        
        # Announce new selection (interrupt current speech for responsiveness)
        self.sr.tts.speak(self.items[self.selected_index], interrupt=True)
    
    def execute(self) -> None:
        """Execute callback for currently selected item.
        
        Calls the callback function provided during initialization
        with the current selected_index as argument.
        
        Keyboard: K_RETURN (Enter)
        
        Example:
            If selected_index = 0 and callback = handle_selection,
            calls: handle_selection(0)
        """
        self.callback(self.selected_index)
    
    def handle_keyboard_events(self, event: pygame.event.Event) -> None:
        """Handle keyboard input for menu navigation.
        
        Processes PyGame keyboard events and maps them to menu actions.
        Only handles KEYDOWN events; ignores other event types.
        
        Args:
            event: PyGame event to process
        
        Supported keys:
            - K_DOWN (Arrow Down): Move to next menu item
            - K_UP (Arrow Up): Move to previous menu item
            - K_RETURN (Enter): Execute selected item callback
        
        Ignored keys:
            All other keys are silently ignored (no-op).
        
        Example:
            >>> for event in pygame.event.get():
            ...     if is_menu_open:
            ...         menu.handle_keyboard_events(event)
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.next_item()
            elif event.key == pygame.K_UP:
                self.prev_item()
            elif event.key == pygame.K_RETURN:
                self.execute()
