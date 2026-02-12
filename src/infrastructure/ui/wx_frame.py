"""Visible minimized wxPython frame for keyboard event capture.

This module provides a visible but minimized frame that acts as the main
application window for keyboard input. Uses hs_deckmanager pattern with
proper OS focus handling.

CRITICAL FIX (v2.0.1): Previous 1x1px invisible frame was denied focus by OS.
Now uses 400x300px frame that is minimized to maintain OS focus.

Clean Architecture Layer: Infrastructure/UI
Dependency: wxPython 4.1.x+
Platform: Windows (primary), Linux (tested), macOS (untested)
Pattern: hs_deckmanager

Usage:
    >>> frame = SolitarioFrame(
    ...     on_key_event=lambda evt: print(f"Key: {evt.GetKeyCode()}"),
    ...     on_close=lambda: cleanup()
    ... )
    >>> frame.start_timer(1000)  # 1-second interval
    >>> # Frame is shown and minimized automatically
"""

import wx
from typing import Optional, Callable


class SolitarioFrame(wx.Frame):
    """Visible minimized frame for keyboard event capture (hs_deckmanager pattern).
    
    This frame serves as the main application window, sized properly for OS
    focus handling but minimized to taskbar. Uses hs_deckmanager pattern
    for reliable keyboard event capture.
    
    CRITICAL FIX: Previous 1x1px invisible frame was denied focus by OS window
    manager. This version uses proper size (400x300) with Iconize() to minimize
    but maintain focus capability.
    
    Features:
    - Visible frame (400x300px, minimized to taskbar)
    - Global keyboard capture via EVT_CHAR_HOOK
    - Timer management (wx.Timer for periodic checks)
    - Close event handling (EVT_CLOSE)
    - Panel with label for identification
    
    Attributes:
        on_key_event: Callback for keyboard events
            Signature: callback(event: wx.KeyEvent) -> None
        on_timer_tick: Optional callback for timer events
            Signature: callback() -> None
        on_close: Optional callback for frame closure
            Signature: callback() -> None
        timer: wx.Timer instance for periodic events (lazy init)
        panel: wx.Panel for UI elements
    
    Example:
        >>> def handle_key(event):
        ...     print(f"Key pressed: {event.GetKeyCode()}")
        ...     if event.GetKeyCode() == wx.WXK_ESCAPE:
        ...         frame.Close()
        ... 
        >>> def handle_timer():
        ...     print("Timer tick - checking timeout")
        ... 
        >>> frame = SolitarioFrame(
        ...     on_key_event=handle_key,
        ...     on_timer_tick=handle_timer,
        ...     on_close=lambda: print("Closing...")
        ... )
        >>> frame.start_timer(1000)  # 1 second interval
        >>> # Frame is automatically shown and minimized
    
    Note:
        Based on hs_deckmanager pattern. Frame is visible in taskbar but
        minimized to avoid visual distraction while maintaining OS focus.
    """
    
    def __init__(
        self,
        on_key_event: Optional[Callable[[wx.KeyEvent], None]] = None,
        on_timer_tick: Optional[Callable[[], None]] = None,
        on_close: Optional[Callable[[], None]] = None,
        parent: Optional[wx.Window] = None,
        id: int = wx.ID_ANY,
        title: str = "Solitario Classico Accessibile"
    ):
        """Initialize visible minimized frame with event callbacks.
        
        Args:
            on_key_event: Optional callback for keyboard events.
                Called for EVT_CHAR_HOOK events (global capture).
            on_timer_tick: Optional callback for timer ticks.
                Called at interval specified in start_timer().
            on_close: Optional callback for frame closure.
                Called before frame is destroyed.
            parent: Optional parent window (None for standalone)
            id: Window ID (default wx.ID_ANY)
            title: Frame title (visible in taskbar and ALT+TAB)
        
        Note:
            Frame is automatically shown and minimized after creation.
            Uses hs_deckmanager pattern for reliable OS focus.
        """
        # Initialize callbacks
        self.on_key_event = on_key_event
        self.on_timer_tick = on_timer_tick
        self.on_close = on_close
        
        # Create visible frame (400x300, normal style for OS focus)
        super().__init__(
            parent=parent,
            id=id,
            title=title,
            size=(400, 300),  # Proper size for OS focus handling
            style=wx.DEFAULT_FRAME_STYLE  # Standard frame style
        )
        
        # Timer for periodic checks (lazy initialization)
        self._timer: Optional[wx.Timer] = None
        
        # Setup panel with label (hs_deckmanager pattern)
        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        
        label = wx.StaticText(
            self.panel, 
            label="Solitario Classico Accessibile\n\nFrame principale wxPython"
        )
        self.sizer.Add(label, 1, wx.ALIGN_CENTER)
        self.panel.SetSizer(self.sizer)
        
        # Bind keyboard events - use EVT_CHAR_HOOK for global capture
        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)
        
        # Bind close event
        self.Bind(wx.EVT_CLOSE, self._on_close_event)
        
        # hs_deckmanager pattern: Centre, Show, then Iconize
        self.Centre()
        self.Show()
        self.Iconize()  # Minimize to taskbar but maintain focus capability
    
    def _on_char_hook(self, event: wx.KeyEvent) -> None:
        """Internal handler for EVT_CHAR_HOOK events (global keyboard capture).
        
        EVT_CHAR_HOOK provides global keyboard capture before any other
        processing. This is the hs_deckmanager pattern for reliable
        keyboard event handling.
        
        Forwards event to user-provided callback, then calls Skip()
        to allow normal event processing (e.g., for screen readers).
        
        Args:
            event: wx.KeyEvent from keyboard
        
        Note:
            event.Skip() is critical for NVDA integration - it ensures
            screen readers can process the event after our handler.
            EVT_CHAR_HOOK captures all keys globally, replacing the
            previous EVT_KEY_DOWN + EVT_CHAR combination.
        """
        # Call user callback if provided
        if self.on_key_event is not None:
            self.on_key_event(event)
        
        # Allow event to propagate (critical for screen readers)
        event.Skip()
    
    def _on_close_event(self, event: wx.CloseEvent) -> None:
        """Internal handler for EVT_CLOSE events.
        
        Stops timer if running, calls user callback, then destroys frame.
        
        Args:
            event: wx.CloseEvent from frame closure request
        
        Note:
            This is called when Close() is invoked, or when user closes
            the frame (though invisible frames rarely receive close events).
        """
        # Stop timer if active
        if self._timer is not None and self._timer.IsRunning():
            self.stop_timer()
        
        # Call user callback
        if self.on_close is not None:
            self.on_close()
        
        # Destroy frame
        self.Destroy()
    
    def _on_timer_event(self, event: wx.TimerEvent) -> None:
        """Internal handler for timer events.
        
        Called periodically based on interval set in start_timer().
        Forwards to user-provided on_timer_tick callback.
        
        Args:
            event: wx.TimerEvent from timer
        
        Note:
            This replaces pygame.USEREVENT timer events used in original
            pygame-based implementation.
        """
        if self.on_timer_tick is not None:
            self.on_timer_tick()
    
    def start_timer(self, interval_ms: int) -> None:
        """Start periodic timer with specified interval.
        
        Creates and starts wx.Timer that fires at regular intervals.
        Replaces pygame.time.set_timer() from original implementation.
        
        Args:
            interval_ms: Timer interval in milliseconds (e.g., 1000 for 1 second)
        
        Example:
            >>> frame.start_timer(1000)  # Fire every 1 second
            >>> frame.start_timer(500)   # Fire every 500ms
        
        Note:
            If timer is already running, it will be stopped and restarted
            with the new interval.
        """
        # Stop existing timer if running
        if self._timer is not None and self._timer.IsRunning():
            self.stop_timer()
        
        # Create new timer
        self._timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_timer_event, self._timer)
        
        # Start timer with specified interval
        self._timer.Start(interval_ms)
    
    def stop_timer(self) -> None:
        """Stop the periodic timer.
        
        Stops and destroys the wx.Timer if it's running.
        Safe to call even if timer is not active.
        
        Example:
            >>> frame.start_timer(1000)
            >>> # ... later ...
            >>> frame.stop_timer()  # Stop timer
        """
        if self._timer is not None:
            if self._timer.IsRunning():
                self._timer.Stop()
            # Timer will be garbage collected
            self._timer = None
    
    def is_timer_running(self) -> bool:
        """Check if timer is currently active.
        
        Returns:
            bool: True if timer is running, False otherwise
        
        Example:
            >>> frame.start_timer(1000)
            >>> assert frame.is_timer_running() == True
            >>> frame.stop_timer()
            >>> assert frame.is_timer_running() == False
        """
        return self._timer is not None and self._timer.IsRunning()


# Module-level documentation
__all__ = ['SolitarioFrame']
