"""Virtual menu for audiogame navigation.

Provides keyboard-navigable menu without visual widgets,
using only screen reader feedback for accessibility.

This is a pure audiogame component - the pygame surface is blank,
all interaction happens through TTS voice feedback.

Migrated from: scr/pygame_menu.py
Enhanced with type hints and improved documentation.

New in v1.4.1:
- Hierarchical menu support (parent/child submenus)
- ESC key handling for submenu closure
- Active submenu tracking and event delegation
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
    - Hierarchical submenus with ESC to close
    
    Attributes:
        items: List of menu item text (in order)
        callback: Function called with selected index on ENTER
        screen: PyGame surface (blank for audiogame)
        sr: ScreenReader instance for TTS feedback
        selected_index: Current menu selection (0-based)
        parent_menu: Parent menu reference (None if root menu)
        _active_submenu: Currently open child menu (None if no submenu)
    
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
        >>> 
        >>> # Create submenu
        >>> submenu = VirtualMenu(
        ...     items=["Nuova partita", "Opzioni", "Chiudi"],
        ...     callback=handle_submenu_selection,
        ...     screen=pygame_screen,
        ...     screen_reader=sr_instance,
        ...     parent_menu=menu
        ... )
        >>> menu.open_submenu(submenu)
    """
    
    def __init__(
        self,
        items: List[str],
        callback: Callable[[int], None],
        screen: pygame.Surface,
        screen_reader: 'ScreenReader',
        parent_menu: Optional['VirtualMenu'] = None
    ) -> None:
        """Initialize virtual menu.
        
        Args:
            items: List of menu item strings (order preserved)
            callback: Function to call on ENTER with selected index
            screen: PyGame surface (audiogame - typically blank)
            screen_reader: ScreenReader with TTS provider for voice output
            parent_menu: Parent menu for hierarchical navigation (None for root)
            
        Side Effects:
            Immediately announces menu opening with item count and
            first item name via TTS.
        """
        self.items = items
        self.callback = callback
        self.screen = screen
        self.sr = screen_reader
        self.selected_index = 0
        self.parent_menu = parent_menu
        self._active_submenu: Optional['VirtualMenu'] = None
        
        # Announce menu opening on initialization
        self._announce_menu_open()
    
    def _announce_menu_open(self) -> None:
        """Announce menu opening with item count and first item.
        
        Provides context to user:
        1. "Menu aperto. N opzioni disponibili." (or "Sottomenu aperto" if child)
        2. Brief pause (300ms)
        3. First menu item name
        
        This helps orient the user in the menu structure.
        """
        if self.parent_menu:
            # This is a submenu
            count_msg = f"Sottomenu aperto. {len(self.items)} voci disponibili."
        else:
            # This is the root menu
            count_msg = f"Menu aperto. {len(self.items)} opzioni disponibili."
        
        self.sr.tts.speak(count_msg, interrupt=True)
        pygame.time.wait(300)  # Pause between announcement and first item
        self.sr.tts.speak(f"1 di {len(self.items)}: {self.items[self.selected_index]}", interrupt=False)
    
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
        
        # Announce new selection with position (interrupt current speech for responsiveness)
        position = self.selected_index + 1
        announcement = f"{position} di {len(self.items)}: {self.items[self.selected_index]}"
        self.sr.tts.speak(announcement, interrupt=True)
    
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
        
        # Announce new selection with position (interrupt current speech for responsiveness)
        position = self.selected_index + 1
        announcement = f"{position} di {len(self.items)}: {self.items[self.selected_index]}"
        self.sr.tts.speak(announcement, interrupt=True)
    
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
    
    def open_submenu(self, submenu: 'VirtualMenu') -> None:
        """Open a child submenu.
        
        Sets the provided submenu as active, causing all keyboard
        events to be delegated to it. The submenu should have this
        menu set as its parent_menu for proper ESC handling.
        
        Args:
            submenu: VirtualMenu instance to open as child
        
        Side Effects:
            - Sets _active_submenu to provided menu
            - Submenu announces opening via its _announce_menu_open()
        
        Example:
            >>> main_menu.open_submenu(game_submenu)
            # TTS: "Sottomenu aperto. 3 voci disponibili. 1 di 3: Nuova partita"
        """
        self._active_submenu = submenu
        # Submenu announces itself via __init__
    
    def close_submenu(self) -> None:
        """Close currently active submenu and return to this menu.
        
        Clears the _active_submenu reference and re-announces
        the current menu item.
        
        Side Effects:
            - Sets _active_submenu to None
            - Announces current menu selection via TTS
        
        Example:
            >>> # User in submenu, presses ESC
            >>> parent_menu.close_submenu()
            # TTS: "Sottomenu chiuso. 1 di 2: Gioca al solitario classico"
        """
        if self._active_submenu:
            self._active_submenu = None
            
            # Announce return to parent menu
            self.sr.tts.speak("Sottomenu chiuso.", interrupt=True)
            pygame.time.wait(300)
            
            # Re-announce current item
            position = self.selected_index + 1
            announcement = f"{position} di {len(self.items)}: {self.items[self.selected_index]}"
            self.sr.tts.speak(announcement, interrupt=False)
    
    def handle_keyboard_events(self, event: pygame.event.Event) -> None:
        """Handle keyboard input for menu navigation.
        
        Processes PyGame keyboard events and maps them to menu actions.
        Only handles KEYDOWN events; ignores other event types.
        
        If a submenu is active, delegates all events to it.
        ESC key closes active submenu and returns to parent.
        
        Args:
            event: PyGame event to process
        
        Supported keys:
            - K_DOWN (Arrow Down): Move to next menu item
            - K_UP (Arrow Up): Move to previous menu item
            - K_RETURN (Enter): Execute selected item callback
            - K_ESCAPE (Escape): Close submenu (if active)
        
        Ignored keys:
            All other keys are silently ignored (no-op).
        
        Example:
            >>> for event in pygame.event.get():
            ...     if is_menu_open:
            ...         menu.handle_keyboard_events(event)
        """
        # If submenu is active, delegate all events to it
        if self._active_submenu:
            self._active_submenu.handle_keyboard_events(event)
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.next_item()
            elif event.key == pygame.K_UP:
                self.prev_item()
            elif event.key == pygame.K_RETURN:
                self.execute()
            elif event.key == pygame.K_ESCAPE:
                # Close this menu if it has a parent
                if self.parent_menu:
                    self.parent_menu.close_submenu()
