"""BasicPanel base class for consistent panel structure (single-frame pattern).

This module provides a base class for all application panels with automatic
sizer setup, event bindings, and TTS announcement helpers.

Pattern: Single-frame panel-swap (wxPython standard)
Clean Architecture Layer: Infrastructure/UI
Dependency: wxPython 4.1.x+
Platform: Windows (primary), Linux (tested), macOS (untested)

Usage:
    >>> class MenuPanel(BasicPanel):
    ...     def init_ui_elements(self):
    ...         btn = wx.Button(self, label="Gioca")
    ...         self.sizer.Add(btn, flag=wx.ALL, border=10)
    ...         self.announce("Menu principale aperto")
    ...
    >>> panel = MenuPanel(parent=frame.panel_container, controller=my_ctrl)
    >>> panel.Show()
"""

import wx
from typing import Optional


class BasicPanel(wx.Panel):
    """Base class for application panels (single-frame pattern).
    
    Provides automatic sizer setup, event bindings, and helper methods
    for screen reader accessibility. All panels should extend this class
    for consistency in single-frame architecture.
    
    Features:
    - Automatic sizer setup (vertical BoxSizer)
    - Focus management with accessibility hooks
    - Keyboard event routing via EVT_CHAR_HOOK
    - TTS announcement helper
    - Template method pattern for UI initialization
    
    Attributes:
        controller: Application controller reference
        screen_reader: ScreenReader instance (from controller)
        sizer: wx.BoxSizer (vertical) for layout
    
    Template Methods (override in subclass):
        init_ui_elements(): Create and add UI elements to sizer
        on_key_down(event): Handle keyboard events
        on_focus(event): Handle focus gained
    
    Example:
        >>> class MyPanel(BasicPanel):
        ...     def init_ui_elements(self):
        ...         label = wx.StaticText(self, label="My Panel")
        ...         self.sizer.Add(label, flag=wx.ALL, border=20)
        ...
        ...     def on_key_down(self, event):
        ...         if event.GetKeyCode() == wx.WXK_ESCAPE:
        ...             self.controller.return_to_menu()
        ...         else:
        ...             event.Skip()
        ...
        >>> panel = MyPanel(parent=frame.panel_container, controller=ctrl)
        >>> panel.Show()
    
    Note:
        This panel is shown/hidden within a single frame. Does NOT create
        a new window. Based on wxPython single-frame best practices.
    """
    
    def __init__(
        self,
        parent: wx.Panel,
        controller: Optional[object],
        **kwargs
    ):
        """Initialize BasicPanel with automatic setup.
        
        Args:
            parent: Parent panel container (mandatory, typically frame.panel_container)
            controller: Application controller reference (provides screen_reader)
            **kwargs: Additional arguments passed to wx.Panel
        
        Note:
            After super().__init__(), this method:
            1. Stores controller and screen_reader references
            2. Creates vertical sizer
            3. Binds global events (CHAR_HOOK, FOCUS)
            4. Calls template method init_ui_elements()
            5. Applies layout
        """
        # Initialize panel
        super().__init__(parent, **kwargs)
        
        # Store controller and screen reader references
        self.controller = controller
        self.screen_reader = controller.screen_reader if controller else None
        
        # Setup sizer (no nested panel - this IS the panel)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        
        # Bind global events
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)  # Global keyboard capture
        self.Bind(wx.EVT_SET_FOCUS, self.on_focus)      # Focus gained
        
        # Template method: Let subclass add UI elements
        self.init_ui_elements()
        
        # Apply layout
        self.Layout()
    
    def init_ui_elements(self) -> None:
        """Initialize UI elements (template method - override in subclass).
        
        This method is called after sizer setup but before layout.
        Subclasses should override to add their UI elements.
        
        Example:
            >>> def init_ui_elements(self):
            ...     # Add title
            ...     title = wx.StaticText(self, label="Menu")
            ...     title.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            ...     self.sizer.Add(title, flag=wx.CENTER | wx.TOP, border=20)
            ...     
            ...     # Add button
            ...     btn = wx.Button(self, label="Start")
            ...     self.sizer.Add(btn, flag=wx.ALL, border=10)
        
        Note:
            Do NOT call Layout() here - it's called automatically
            after this method returns. Use self (not self.panel) as parent.
        """
        pass
    
    def on_key_down(self, event: wx.KeyEvent) -> None:
        """Handle keyboard events (EVT_CHAR_HOOK - global capture).
        
        This handler receives all keyboard events before any widget
        processing. Default implementation propagates event.
        
        Args:
            event: wx.KeyEvent from keyboard
        
        Example:
            >>> def on_key_down(self, event):
            ...     key_code = event.GetKeyCode()
            ...     if key_code == wx.WXK_ESCAPE:
            ...         self.controller.return_to_menu()
            ...     elif key_code == wx.WXK_F1:
            ...         self.show_help()
            ...     else:
            ...         event.Skip()  # Let others process
        
        Note:
            ALWAYS call event.Skip() unless you want to block the event.
            Skipping ensures screen readers and other handlers can process it.
        """
        event.Skip()  # Default: propagate to other handlers
    
    def on_focus(self, event: wx.FocusEvent) -> None:
        """Handle focus gained event (EVT_SET_FOCUS).
        
        Called when this panel gains keyboard focus. Can be overridden
        to announce panel name or perform focus-related actions.
        
        Args:
            event: wx.FocusEvent
        
        Example:
            >>> def on_focus(self, event):
            ...     self.announce("Menu panel focused")
            ...     event.Skip()
        
        Note:
            Default implementation propagates event. Override to add
            custom behavior, but always call event.Skip() at the end.
        """
        event.Skip()  # Default: propagate
    
    def announce(self, message: str, interrupt: bool = False) -> None:
        """Announce message via TTS screen reader (accessibility helper).
        
        Provides convenient TTS announcement for screen reader users.
        If screen_reader is not available, fails silently.
        
        Args:
            message: Text to announce
            interrupt: If True, interrupts current speech; if False, queues
        
        Example:
            >>> self.announce("Menu opened. 3 options available.")
            >>> self.announce("Error occurred!", interrupt=True)
        
        Note:
            This is a convenience wrapper around screen_reader.tts.speak().
            If no screen_reader is available (silent mode), does nothing.
        """
        if self.screen_reader:
            self.screen_reader.tts.speak(message, interrupt=interrupt)


# Module-level documentation
__all__ = ['BasicPanel']
