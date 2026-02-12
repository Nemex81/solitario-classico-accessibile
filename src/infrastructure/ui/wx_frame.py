"""Single visible frame for panel-swap architecture (wxPython standard pattern).

This module provides the main application frame that serves as a container
for multiple panels shown/hidden via panel-swap pattern.

Pattern: Single-frame panel-swap (wxPython standard)
Clean Architecture Layer: Infrastructure/UI
Dependency: wxPython 4.1.x+
Platform: Windows (primary), Linux (tested), macOS (untested)

Usage:
    >>> frame = SolitarioFrame(
    ...     on_timer_tick=lambda: check_timeout(),
    ...     on_close=lambda: cleanup()
    ... )
    >>> # Create panels
    >>> menu_panel = MenuPanel(parent=frame.panel_container, controller=ctrl)
    >>> gameplay_panel = GameplayPanel(parent=frame.panel_container, controller=ctrl)
    >>> # Show/hide panels as needed
    >>> menu_panel.Show()
    >>> frame.start_timer(1000)  # 1-second interval
"""

import wx
from typing import Optional, Callable


class SolitarioFrame(wx.Frame):
    """Main application frame for panel-swap architecture (wxPython standard).
    
    This frame serves as the single visible window containing a panel_container
    where multiple panels are shown/hidden. Uses standard wxPython pattern
    for multi-view applications.
    
    Features:
    - Single visible frame (600x450px, centered)
    - Panel container for child panels
    - Timer management (wx.Timer for periodic checks)
    - Close event handling (EVT_CLOSE)
    - No keyboard routing (panels handle their own events)
    
    Attributes:
        on_timer_tick: Optional callback for timer events
            Signature: callback() -> None
        on_close: Optional callback for frame closure
            Signature: callback() -> None
        timer: wx.Timer instance for periodic events (lazy init)
        panel_container: wx.Panel container for child panels
    
    Example:
        >>> def handle_timer():
        ...     print("Timer tick - checking timeout")
        ... 
        >>> frame = SolitarioFrame(
        ...     on_timer_tick=handle_timer,
        ...     on_close=lambda: print("Closing...")
        ... )
        >>> # Create panels as children of frame.panel_container
        >>> menu = MenuPanel(parent=frame.panel_container, controller=ctrl)
        >>> game = GameplayPanel(parent=frame.panel_container, controller=ctrl)
        >>> menu.Show()  # Show menu, hide others
        >>> frame.start_timer(1000)  # 1 second interval
    
    Note:
        Based on wxPython single-frame best practices. Panels handle their
        own keyboard events - frame does not route events.
    """
    
    def __init__(
        self,
        on_timer_tick: Optional[Callable[[], None]] = None,
        on_close: Optional[Callable[[], None]] = None,
        parent: Optional[wx.Window] = None,
        id: int = wx.ID_ANY,
        title: str = "Solitario Classico Accessibile"
    ):
        """Initialize single visible frame for panel-swap architecture.
        
        Args:
            on_timer_tick: Optional callback for timer ticks.
                Called at interval specified in start_timer().
            on_close: Optional callback for frame closure.
                Called before frame is destroyed.
            parent: Optional parent window (None for standalone)
            id: Window ID (default wx.ID_ANY)
            title: Frame title (visible in taskbar and title bar)
        
        Note:
            Frame is automatically shown and centered after creation.
            No keyboard event routing - panels handle their own events.
        """
        # Initialize callbacks
        self.on_timer_tick = on_timer_tick
        self.on_close = on_close
        
        # Create visible frame (600x450, normal style)
        super().__init__(
            parent=parent,
            id=id,
            title=title,
            size=(600, 450),  # Proper size for single-window UI
            style=wx.DEFAULT_FRAME_STYLE  # Standard frame style
        )
        
        # Timer for periodic checks (lazy initialization)
        self._timer: Optional[wx.Timer] = None
        
        # Setup panel container (for child panels)
        self.panel_container = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.panel_container, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        
        # Bind close event
        self.Bind(wx.EVT_CLOSE, self._on_close_event)
        
        # Show and center frame
        self.Centre()
        self.Show()
    
    def _on_close_event(self, event: wx.CloseEvent) -> None:
        """Internal handler for EVT_CLOSE events.
        
        Stops timer if running, calls user callback, then destroys frame.
        
        Args:
            event: wx.CloseEvent from frame closure request
        
        Note:
            This is called when Close() is invoked, or when user closes
            the frame via window controls.
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
