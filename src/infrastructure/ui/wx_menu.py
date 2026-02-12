"""Virtual menu for wxPython-based audiogame navigation.

This module provides keyboard-navigable menu without visual widgets,
using only screen reader feedback for accessibility. Replaces pygame-based
VirtualMenu with wxPython event handling.

Clean Architecture Layer: Infrastructure/UI
Dependency: wxPython 4.1.x+
Platform: Windows (primary), Linux (tested), macOS (untested)

Usage:
    >>> menu = WxVirtualMenu(
    ...     items=["Gioca", "Esci"],
    ...     callback=lambda idx: handle_selection(idx),
    ...     screen_reader=sr_instance
    ... )
    >>> # In wx event handler:
    >>> if event.GetKeyCode() == wx.WXK_DOWN:
    ...     menu.next_item()
    >>> elif event.GetKeyCode() == wx.WXK_RETURN:
    ...     menu.execute()
"""

import wx
from typing import List, Callable, Optional, TYPE_CHECKING, Dict

# Type checking import to avoid circular dependencies
if TYPE_CHECKING:
    from src.infrastructure.accessibility.screen_reader import ScreenReader


class WxVirtualMenu:
    """Keyboard-navigable virtual menu for wxPython audiogame.
    
    Pure audio interface without visual widgets. Uses TTS for all feedback.
    Navigation via UP/DOWN arrows, selection via ENTER.
    
    This component replaces pygame-based VirtualMenu with wxPython events,
    following the "audiogame" paradigm where all user interaction happens
    through audio feedback for full accessibility to blind users.
    
    Navigation Features:
    - Wrap-around: DOWN on last item → first item
    - Wrap-around: UP on first item → last item
    - Immediate TTS feedback on every navigation
    - Interrupt current speech for responsive navigation
    - Hierarchical submenus with ESC to close
    - Welcome messages for better orientation
    - Numeric shortcuts (1-5) for rapid item selection
    
    Attributes:
        items: List of menu item text (in order)
        callback: Function called with selected index on ENTER
        sr: ScreenReader instance for TTS feedback
        selected_index: Current menu selection (0-based)
        parent_menu: Parent menu reference (None if root menu)
        welcome_message: Optional welcome text for submenu opening
        show_controls_hint: Whether to announce navigation controls
        key_handlers: Dict mapping wx key codes to handler methods
    
    Example:
        >>> def handle_selection(index: int):
        ...     if index == 0:
        ...         start_game()
        ...     elif index == 1:
        ...         quit_game()
        >>> 
        >>> menu = WxVirtualMenu(
        ...     items=["Gioca al solitario classico", "Esci dal gioco"],
        ...     callback=handle_selection,
        ...     screen_reader=sr_instance
        ... )
        >>> # Menu automatically announces: "Menu aperto. 2 opzioni..."
        >>> 
        >>> # In wx event handler (e.g., wx_main.py):
        >>> def on_key_event(event):
        ...     if menu.handle_key_event(event):
        ...         return  # Menu handled the event
        ...     # ... other handling
    
    Note:
        Unlike pygame version, this doesn't need pygame.Surface.
        All rendering is audio-only via TTS.
    """
    
    def __init__(
        self,
        items: List[str],
        callback: Callable[[int], None],
        screen_reader: 'ScreenReader',
        parent_menu: Optional['WxVirtualMenu'] = None,
        welcome_message: Optional[str] = None,
        show_controls_hint: bool = True
    ) -> None:
        """Initialize virtual menu.
        
        Args:
            items: List of menu item strings (order preserved)
            callback: Function to call on ENTER with selected index
            screen_reader: ScreenReader with TTS provider for voice output
            parent_menu: Parent menu for hierarchical navigation (None for root)
            welcome_message: Optional welcome text for submenu opening
            show_controls_hint: Whether to announce navigation controls
        
        Side Effects:
            Immediately announces menu opening. If opened by parent via
            open_submenu(), uses announce_welcome() if configured, otherwise
            uses standard _announce_menu_open().
        """
        self.items = items
        self.callback = callback
        self.sr = screen_reader
        self.selected_index = 0
        self.parent_menu = parent_menu
        self.welcome_message = welcome_message
        self.show_controls_hint = show_controls_hint
        self._active_submenu: Optional['WxVirtualMenu'] = None
        
        # Build keyboard command mappings
        self._build_key_handlers()
        
        # Announce menu opening on initialization
        # Note: If opened via open_submenu(), that method will handle announcement
        if parent_menu is None:
            self._announce_menu_open()
    
    def _build_key_handlers(self) -> None:
        """Build keyboard command mappings for menu navigation.
        
        Maps wx key codes to handler methods, including:
        - Arrow keys for navigation (UP/DOWN)
        - ENTER for selection
        - ESC for closing submenu (if has parent)
        - Numeric keys 1-5 for direct item selection
        
        The key_handlers dict is used by handle_key_event()
        for efficient event dispatching.
        """
        self.key_handlers: Dict[int, Callable[[], None]] = {
            wx.WXK_DOWN: self.next_item,
            wx.WXK_UP: self.prev_item,
            wx.WXK_RETURN: self.execute,
            wx.WXK_NUMPAD_ENTER: self.execute,  # Numeric keypad ENTER
            wx.WXK_ESCAPE: self._handle_esc,
            # Numeric shortcuts (main keyboard)
            ord('1'): self.press_1,
            ord('2'): self.press_2,
            ord('3'): self.press_3,
            ord('4'): self.press_4,
            ord('5'): self.press_5,
            # Numeric keypad shortcuts
            wx.WXK_NUMPAD1: self.press_1,
            wx.WXK_NUMPAD2: self.press_2,
            wx.WXK_NUMPAD3: self.press_3,
            wx.WXK_NUMPAD4: self.press_4,
            wx.WXK_NUMPAD5: self.press_5,
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
        wx.MilliSleep(300)  # Pause between announcement and first item
        self.sr.tts.speak(
            f"1 di {len(self.items)}: {self.items[self.selected_index]}", 
            interrupt=False
        )
    
    def announce_welcome(self) -> None:
        """Announce welcome message with controls hint.
        
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
            >>> submenu = WxVirtualMenu(
            ...     items=["Item 1", "Item 2"],
            ...     callback=handler,
            ...     screen_reader=sr,
            ...     welcome_message="Benvenuto nel menu di gioco!",
            ...     show_controls_hint=True
            ... )
            >>> submenu.announce_welcome()
            # TTS: "Benvenuto! Usa frecce... Posizione: Item 1"
        """
        parts = []
        
        # Part 1: Welcome message
        if self.welcome_message:
            parts.append(self.welcome_message)
        
        # Part 2: Controls hint
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
                wx.MilliSleep(400)  # Longer pause between sections
    
    def next_item(self) -> None:
        """Move to next menu item (Arrow DOWN).
        
        Implements wrap-around: if at last item, moves to first item.
        Immediately announces new selection via TTS with interrupt.
        
        Keyboard: WXK_DOWN (Arrow Down)
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
        
        Keyboard: WXK_UP (Arrow Up)
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
        
        Keyboard: WXK_RETURN (Enter), WXK_NUMPAD_ENTER (Numpad Enter)
        
        Example:
            If selected_index = 0 and callback = handle_selection,
            calls: handle_selection(0)
        """
        self.callback(self.selected_index)
    
    # === NUMERIC SHORTCUTS ===
    
    def press_1(self) -> None:
        """Shortcut: select first menu item and execute.
        
        Equivalent to navigating to item 1 and pressing ENTER.
        Provides rapid access without arrow navigation.
        """
        if len(self.items) >= 1:
            self.selected_index = 0
            self.execute()
    
    def press_2(self) -> None:
        """Shortcut: select second menu item and execute.
        
        Equivalent to navigating to item 2 and pressing ENTER.
        Provides rapid access without arrow navigation.
        """
        if len(self.items) >= 2:
            self.selected_index = 1
            self.execute()
    
    def press_3(self) -> None:
        """Shortcut: select third menu item and execute.
        
        Equivalent to navigating to item 3 and pressing ENTER.
        Provides rapid access without arrow navigation.
        """
        if len(self.items) >= 3:
            self.selected_index = 2
            self.execute()
    
    def press_4(self) -> None:
        """Shortcut: select fourth menu item and execute.
        
        Equivalent to navigating to item 4 and pressing ENTER.
        Provides rapid access without arrow navigation.
        """
        if len(self.items) >= 4:
            self.selected_index = 3
            self.execute()
    
    def press_5(self) -> None:
        """Shortcut: select fifth menu item and execute.
        
        Equivalent to navigating to item 5 and pressing ENTER.
        Provides rapid access without arrow navigation.
        """
        if len(self.items) >= 5:
            self.selected_index = 4
            self.execute()
    
    def _handle_esc(self) -> None:
        """Handle ESC key - close menu if has parent.
        
        Helper method for ESC key handling in key_handlers dict.
        Only closes menu if it has a parent (is a submenu).
        Root menu ESC is handled by main application logic.
        """
        if self.parent_menu is not None:
            self.close()
    
    def close(self) -> None:
        """Close this menu and return to parent.
        
        If this is a submenu (has parent), closes itself and
        returns focus to parent menu with announcement.
        
        If this is root menu, does nothing (handled by app).
        """
        if self.parent_menu is not None:
            # Clear active submenu in parent
            self.parent_menu._active_submenu = None
            
            # Announce return to parent
            self.sr.tts.speak("Tornando al menu principale", interrupt=True)
            wx.MilliSleep(200)
            
            # Re-announce parent menu current position
            position = self.parent_menu.selected_index + 1
            announcement = (
                f"{position} di {len(self.parent_menu.items)}: "
                f"{self.parent_menu.items[self.parent_menu.selected_index]}"
            )
            self.sr.tts.speak(announcement, interrupt=False)
    
    def open_submenu(self, submenu: 'WxVirtualMenu') -> None:
        """Open a submenu as child of this menu.
        
        Sets this menu as parent of submenu and announces submenu opening.
        Use submenu's announce_welcome() for enhanced announcement.
        
        Args:
            submenu: Child menu to open
        
        Example:
            >>> main_menu = WxVirtualMenu(...)
            >>> sub_menu = WxVirtualMenu(
            ...     items=["Item 1", "Item 2"],
            ...     callback=handler,
            ...     screen_reader=sr,
            ...     parent_menu=main_menu,
            ...     welcome_message="Benvenuto!",
            ...     show_controls_hint=True
            ... )
            >>> main_menu.open_submenu(sub_menu)
            >>> sub_menu.announce_welcome()  # Enhanced announcement
        """
        self._active_submenu = submenu
        # Submenu will announce itself (already done in __init__ or via announce_welcome())
    
    def handle_key_event(self, event: wx.KeyEvent) -> bool:
        """Handle keyboard event for menu navigation.
        
        Dispatches wx.KeyEvent to appropriate handler method based on
        key code. If submenu is active, delegates to submenu first.
        
        Args:
            event: wx.KeyEvent from keyboard input
        
        Returns:
            bool: True if event was handled by menu, False if not recognized
        
        Example:
            >>> def on_key_down(event):
            ...     if menu.handle_key_event(event):
            ...         return  # Menu handled it
            ...     # Handle other keys...
        
        Note:
            This method does NOT call event.Skip(). The caller should
            decide whether to propagate the event after checking return value.
        """
        # If submenu is active, delegate to it first
        if self._active_submenu is not None:
            return self._active_submenu.handle_key_event(event)
        
        # Get key code from event
        key_code = event.GetKeyCode()
        
        # Look up handler in key_handlers dict
        handler = self.key_handlers.get(key_code)
        
        if handler is not None:
            # Call handler method
            handler()
            return True  # Event was handled
        
        # Event not recognized by menu
        return False


# Module-level documentation
__all__ = ['WxVirtualMenu']
