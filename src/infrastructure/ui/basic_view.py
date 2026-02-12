"""BasicView base class for consistent view structure (hs_deckmanager pattern).

This module provides a base class for all application views with automatic
panel/sizer setup, event bindings, and TTS announcement helpers.

Pattern: hs_deckmanager BasicView
Clean Architecture Layer: Infrastructure/UI
Dependency: wxPython 4.1.x+
Platform: Windows (primary), Linux (tested), macOS (untested)

Usage:
    >>> class MenuView(BasicView):
    ...     def init_ui_elements(self):
    ...         btn = wx.Button(self.panel, label="Gioca")
    ...         self.sizer.Add(btn, flag=wx.ALL, border=10)
    ...         self.announce("Menu principale aperto")
    ...
    >>> view = MenuView(parent=None, controller=my_ctrl, title="Menu")
    >>> view.Show()
"""

import wx
from typing import Optional


class BasicView(wx.Frame):
    """Base class for application views (hs_deckmanager pattern).
    
    Provides automatic setup of panel/sizer, event bindings, and helper
    methods for screen reader accessibility. All views should extend this
    class for consistency.
    
    Features:
    - Automatic panel and sizer setup
    - Focus management with accessibility hooks
    - Keyboard event routing via EVT_CHAR_HOOK
    - Close event handling
    - TTS announcement helper
    - Template method pattern for UI initialization
    
    Attributes:
        controller: Application controller reference
        screen_reader: ScreenReader instance (from controller)
        panel: wx.Panel for UI elements
        sizer: wx.BoxSizer (vertical) for layout
    
    Template Methods (override in subclass):
        init_ui_elements(): Create and add UI elements to sizer
        on_key_down(event): Handle keyboard events
        on_focus(event): Handle focus gained
        on_close(event): Handle close request
    
    Example:
        >>> class MyView(BasicView):
        ...     def init_ui_elements(self):
        ...         label = wx.StaticText(self.panel, label="My View")
        ...         self.sizer.Add(label, flag=wx.ALL, border=20)
        ...
        ...     def on_key_down(self, event):
        ...         if event.GetKeyCode() == wx.WXK_ESCAPE:
        ...             self.Close()
        ...         else:
        ...             event.Skip()
        ...
        >>> view = MyView(None, controller, "My View", (400, 300))
        >>> view.Show()
    
    Note:
        Based on hs_deckmanager BasicView pattern. Subclasses should
        call event.Skip() in event handlers to allow normal processing.
    """
    
    def __init__(
        self,
        parent: Optional[wx.Frame],
        controller: Optional[object],
        title: str,
        size: tuple = (800, 600),
        **kwargs
    ):
        """Initialize BasicView with automatic setup.
        
        Args:
            parent: Optional parent frame (None for independent window)
            controller: Application controller reference (provides screen_reader)
            title: Window title
            size: Window size as (width, height) tuple
            **kwargs: Additional arguments passed to wx.Frame
        
        Note:
            After super().__init__(), this method:
            1. Stores controller and screen_reader references
            2. Creates panel and vertical sizer
            3. Binds global events (CHAR_HOOK, CLOSE, FOCUS)
            4. Calls template method init_ui_elements()
            5. Applies layout and centers window
        """
        # Initialize frame
        super().__init__(parent, title=title, size=size, **kwargs)
        
        # Store controller and screen reader references
        self.controller = controller
        self.screen_reader = controller.screen_reader if controller else None
        
        # Setup base panel and sizer (hs_deckmanager pattern)
        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.sizer)
        
        # Bind global events
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)  # Global keyboard capture
        self.Bind(wx.EVT_CLOSE, self.on_close)          # Close request
        self.Bind(wx.EVT_SET_FOCUS, self.on_focus)      # Focus gained
        
        # Template method: Let subclass add UI elements
        self.init_ui_elements()
        
        # Apply layout and center on screen
        self.Layout()
        self.Centre()
    
    def init_ui_elements(self) -> None:
        """Initialize UI elements (template method - override in subclass).
        
        This method is called after panel/sizer setup but before layout.
        Subclasses should override to add their UI elements.
        
        Example:
            >>> def init_ui_elements(self):
            ...     # Add title
            ...     title = wx.StaticText(self.panel, label="Menu")
            ...     title.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            ...     self.sizer.Add(title, flag=wx.CENTER | wx.TOP, border=20)
            ...     
            ...     # Add button
            ...     btn = wx.Button(self.panel, label="Start")
            ...     self.sizer.Add(btn, flag=wx.ALL, border=10)
        
        Note:
            Do NOT call Layout() or Centre() here - they are called
            automatically after this method returns.
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
            ...         self.Close()
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
        
        Called when this view gains keyboard focus. Can be overridden
        to announce view name or perform focus-related actions.
        
        Args:
            event: wx.FocusEvent
        
        Example:
            >>> def on_focus(self, event):
            ...     self.announce(f"{self.GetTitle()} focused")
            ...     event.Skip()
        
        Note:
            Default implementation propagates event. Override to add
            custom behavior, but always call event.Skip() at the end.
        """
        event.Skip()  # Default: propagate
    
    def on_close(self, event: wx.CloseEvent) -> None:
        """Handle close request (EVT_CLOSE).
        
        Called when user or code requests window closure (e.g., ALT+F4,
        Close button, or Close() call). Default implementation propagates.
        
        Args:
            event: wx.CloseEvent
        
        Example:
            >>> def on_close(self, event):
            ...     # Confirm before closing
            ...     if self.has_unsaved_changes:
            ...         dlg = wx.MessageDialog(self, "Save changes?", 
            ...                               style=wx.YES_NO)
            ...         if dlg.ShowModal() == wx.ID_YES:
            ...             self.save()
            ...     event.Skip()  # Allow default close
        
        Note:
            Call event.Veto() to cancel close request.
            Call event.Skip() to allow close to proceed.
        """
        event.Skip()  # Default: allow close
    
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
__all__ = ['BasicView']
