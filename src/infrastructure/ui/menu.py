"""Virtual menu for audiogame navigation.

Provides keyboard-navigable menu without visual widgets,
using only screen reader feedback for accessibility.

Migrated from: scr/pygame_menu.py
"""

import pygame
from typing import List, Callable, Optional


class VirtualMenu:
    """Keyboard-navigable virtual menu for audiogame.
    
    Pure audio interface without visual widgets. Uses TTS
    for all feedback. Navigation via UP/DOWN arrows, selection
    via ENTER.
    
    Args:
        items: List of menu item strings
        callback: Function called with selected index on ENTER
        screen: PyGame surface (audiogame - blank screen)
        screen_reader: TTS provider for voice feedback
    """
    
    def __init__(
        self,
        items: List[str],
        callback: Callable[[int], None],
        screen: pygame.Surface,
        screen_reader
    ):
        self.items = items
        self.callback = callback
        self.screen = screen
        self.sr = screen_reader
        self.selected_index = 0
        
        # Annuncia apertura menu
        self._announce_menu_open()
    
    def _announce_menu_open(self) -> None:
        """Announce menu opening with item count and first item."""
        count_msg = f"Menu aperto. {len(self.items)} opzioni disponibili."
        self.sr.speak(count_msg, interrupt=True)
        pygame.time.wait(300)
        self.sr.speak(self.items[self.selected_index], interrupt=False)
    
    def next_item(self) -> None:
        """Move to next menu item (Arrow DOWN).
        
        Wraps around to first item if at end.
        """
        if self.selected_index < len(self.items) - 1:
            self.selected_index += 1
        else:
            self.selected_index = 0  # Wrap to beginning
        
        self.sr.speak(self.items[self.selected_index], interrupt=True)
    
    def prev_item(self) -> None:
        """Move to previous menu item (Arrow UP).
        
        Wraps around to last item if at beginning.
        """
        if self.selected_index > 0:
            self.selected_index -= 1
        else:
            self.selected_index = len(self.items) - 1  # Wrap to end
        
        self.sr.speak(self.items[self.selected_index], interrupt=True)
    
    def execute(self) -> None:
        """Execute callback for selected item (ENTER key)."""
        self.callback(self.selected_index)
    
    def handle_keyboard_events(self, event: pygame.event.Event) -> None:
        """Handle keyboard input for menu navigation.
        
        Args:
            event: PyGame event to process
        
        Supported keys:
            - K_DOWN: Next item
            - K_UP: Previous item
            - K_RETURN: Execute selected item
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.next_item()
            elif event.key == pygame.K_UP:
                self.prev_item()
            elif event.key == pygame.K_RETURN:
                self.execute()
