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

New in v1.4.2 (Commit #28):
- Welcome message support for submenus
- Configurable controls hint
- Enhanced opening announcements
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
    - Welcome messages for better orientation (v1.4.2)
    
    Attributes:
        items: List of menu item text (in order)
        callback: Function called with selected index on ENTER
        screen: PyGame surface (blank for audiogame)
        sr: ScreenReader instance for TTS feedback
        selected_index: Current menu selection (0-based)
        parent_menu: Parent menu reference (None if root menu)
        welcome_message: Optional welcome text for submenu opening (v1.4.2)
        show_controls_hint: Whether to announce navigation controls (v1.4.2)
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
        >>> # Create submenu with welcome message
        >>> submenu = VirtualMenu(
        ...     items=["Nuova partita", "Opzioni", "Chiudi"],
        ...     callback=handle_submenu_selection,
        ...     screen=pygame_screen,
        ...     screen_reader=sr_instance,
        ...     parent_menu=menu,
        ...     welcome_message="Benvenuto nel menu di gioco!",
        ...     show_controls_hint=True
        ... )
        >>> menu.open_submenu(submenu)
        >>> # TTS: "Benvenuto! Usa frecce... Posizione: Nuova partita"
    """
    
    def __init__(
        self,
        items: List[str],
        callback: Callable[[int], None],
        screen: pygame.Surface,
        screen_reader: 'ScreenReader',
        parent_menu: Optional['VirtualMenu'] = None,
        welcome_message: Optional[str] = None,
        show_controls_hint: bool = True
    ) -> None:
        """Initialize virtual menu.
        
        Args:
            items: List of menu item strings (order preserved)
            callback: Function to call on ENTER with selected index
            screen: PyGame surface (audiogame - typically blank)
            screen_reader: ScreenReader with TTS provider for voice output
            parent_menu: Parent menu for hierarchical navigation (None for root)
            welcome_message: Optional welcome text for submenu opening (v1.4.2)
            show_controls_hint: Whether to announce navigation controls (v1.4.2)
            
        Side Effects:
            Immediately announces menu opening. If opened by parent via
            open_submenu(), uses announce_welcome() if configured, otherwise
            uses standard _announce_menu_open().
        """
        self.items = items
        self.callback = callback
        self.screen = screen
        self.sr = screen_reader
        self.selected_index = 0
        self.parent_menu = parent_menu
        self.welcome_message = welcome_message
        self.show_controls_hint = show_controls_hint
        self._active_submenu: Optional['VirtualMenu'] = None
        
        # Build keyboard command mappings (v1.4.3: added numeric shortcuts)
        self._build_key_handlers()
        
        # Announce menu opening on initialization
        # Note: If opened via open_submenu(), that method will handle announcement
        # This is for root menu initialization
        if parent_menu is None:
            self._announce_menu_open()
    
    def _build_key_handlers(self) -> None:
        """Build keyboard command mappings for menu navigation.
        
        Maps keyboard events to handler methods, including:
        - Arrow keys for navigation (UP/DOWN)
        - ENTER for selection
        - ESC for closing submenu (if has parent)
        - Numeric keys 1-5 for direct item selection (v1.4.3)
        
        The key_handlers dict is used by handle_keyboard_events()
        for efficient event dispatching.
        
        New in v1.4.3: Added numeric shortcuts K_1 through K_5
        for rapid menu item access without arrow navigation.
        """
        self.key_handlers = {
            pygame.K_DOWN: self.next_item,
            pygame.K_UP: self.prev_item,
            pygame.K_RETURN: self.execute,
            pygame.K_ESCAPE: self._handle_esc,
            pygame.K_1: self.press_1,
            pygame.K_2: self.press_2,
            pygame.K_3: self.press_3,
            pygame.K_4: self.press_4,
            pygame.K_5: self.press_5,
        }
    
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
    
    def announce_welcome(self) -> None:
        """Announce welcome message with controls hint (v1.4.2).
        
        Enhanced opening announcement for submenus that provides:
        1. Welcome message (if configured)
        2. Navigation controls hint (if enabled)
        3. Current menu item
        
        This gives better orientation and guidance for blind users
        compared to standard _announce_menu_open().
        
        Structure:
            "[Welcome message]"
            "Usa frecce su e giù per navigare tra le voci. Premi Invio per selezionare."
            "Posizione corrente: [First item]"
        
        Example:
            >>> submenu.announce_welcome()
            # TTS announces:
            # "Benvenuto nel menu di gioco del Solitario!"
            # "Usa frecce su e giù per navigare. Premi Invio per selezionare."
            # "Posizione corrente: Nuova partita."
        """
        # Build announcement parts
        parts = []
        
        # Part 1: Welcome message (if configured)
        if self.welcome_message:
            parts.append(self.welcome_message)
        
        # Part 2: Controls hint (if enabled)
        if self.show_controls_hint:
            controls_hint = (
                "Usa frecce su e giù per navigare tra le voci. "
                "Premi Invio per selezionare."
            )
            parts.append(controls_hint)
        
        # Part 3: Current position
        position_msg = f"Posizione corrente: {self.items[self.selected_index]}."
        parts.append(position_msg)
        
        # Announce all parts with pauses
        for i, part in enumerate(parts):
            self.sr.tts.speak(part, interrupt=(i == 0))  # Interrupt only for first part
            if i < len(parts) - 1:
                pygame.time.wait(400)  # Longer pause between sections
    
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
    
    # === NUMERIC SHORTCUTS (v1.4.3) ===
    
    def press_1(self) -> None:
        """Shortcut: select first menu item and execute.
        
        Equivalent to navigating to item 1 and pressing ENTER.
        Provides rapid access without arrow navigation.
        
        New in v1.4.3: Numeric menu shortcuts for accessibility.
        """
        if len(self.items) >= 1:
            self.selected_index = 0
            self.execute()
    
    def press_2(self) -> None:
        """Shortcut: select second menu item and execute.
        
        Equivalent to navigating to item 2 and pressing ENTER.
        Provides rapid access without arrow navigation.
        
        New in v1.4.3: Numeric menu shortcuts for accessibility.
        """
        if len(self.items) >= 2:
            self.selected_index = 1
            self.execute()
    
    def press_3(self) -> None:
        """Shortcut: select third menu item and execute.
        
        Equivalent to navigating to item 3 and pressing ENTER.
        Provides rapid access without arrow navigation.
        
        New in v1.4.3: Numeric menu shortcuts for accessibility.
        """
        if len(self.items) >= 3:
            self.selected_index = 2
            self.execute()
    
    def press_4(self) -> None:
        """Shortcut: select fourth menu item and execute.
        
        Equivalent to navigating to item 4 and pressing ENTER.
        Provides rapid access without arrow navigation.
        
        New in v1.4.3: Numeric menu shortcuts for accessibility.
        """
        if len(self.items) >= 4:
            self.selected_index = 3
            self.execute()
    
    def press_5(self) -> None:
        """Shortcut: select fifth menu item and execute.
        
        Equivalent to navigating to item 5 and pressing ENTER.
        Provides rapid access without arrow navigation.
        
        New in v1.4.3: Numeric menu shortcuts for accessibility.
        """
        if len(self.items) >= 5:
            self.selected_index = 4
            self.execute()
    
    def _handle_esc(self) -> None:
        """Handle ESC key - close menu if has parent.
        
        Helper method for ESC key handling in key_handlers dict.
        Only closes menu if it has a parent (is a submenu).
        
        New in v1.4.3: Extracted to separate method for key_handlers dict.
        """
        if self.parent_menu:
            self.parent_menu.close_submenu()
    
    # === SUBMENU MANAGEMENT ===
    
    def open_submenu(self, submenu: 'VirtualMenu') -> None:
        """Open a child submenu.
        
        Sets the provided submenu as active, causing all keyboard
        events to be delegated to it. The submenu should have this
        menu set as its parent_menu for proper ESC handling.
        
        New in v1.4.2: Uses announce_welcome() if submenu has
        welcome_message configured, otherwise uses standard announcement.
        
        Args:
            submenu: VirtualMenu instance to open as child
        
        Side Effects:
            - Sets _active_submenu to provided menu
            - Submenu announces opening via announce_welcome() or _announce_menu_open()
        
        Example:
            >>> # Submenu with welcome
            >>> main_menu.open_submenu(game_submenu)
            # TTS: "Benvenuto! Usa frecce... Posizione: Nuova partita"
            
            >>> # Submenu without welcome
            >>> main_menu.open_submenu(other_submenu)
            # TTS: "Sottomenu aperto. 3 voci disponibili. 1 di 3: Prima voce"
        """
        self._active_submenu = submenu
        
        # Choose announcement method based on configuration
        if submenu.welcome_message or submenu.show_controls_hint:
            # Use enhanced welcome announcement
            submenu.announce_welcome()
        else:
            # Use standard announcement
            submenu._announce_menu_open()
    
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
    
    @property
    def active_submenu(self) -> Optional['VirtualMenu']:
        """Get currently active submenu.
        
        Returns:
            Active submenu instance or None if no submenu open
        """
        return self._active_submenu
    
    def handle_keyboard_events(self, event: pygame.event.Event) -> None:
        """Handle keyboard input for menu navigation with numeric shortcuts.
        
        Processes PyGame keyboard events and maps them to menu actions
        using the key_handlers dictionary for efficient dispatch.
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
            - K_1 through K_5: Direct item selection shortcuts (v1.4.3)
        
        Ignored keys:
            All other keys are silently ignored (no-op).
        
        New in v1.4.3: Added numeric shortcuts for rapid menu access.
        Uses key_handlers dict for efficient event dispatching.
        
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
            handler = self.key_handlers.get(event.key)
            if handler:
                handler()
