"""Invisible wxPython frame for keyboard event capture.

This module provides an invisible 1x1 pixel frame that acts as an event sink
for keyboard input. Replaces pygame window with wx.Frame that doesn't appear
in taskbar or ALT+TAB switcher.

Clean Architecture Layer: Infrastructure/UI
Dependency: wxPython 4.1.x+
Platform: Windows (primary), Linux (tested), macOS (untested)

Usage:
    >>> frame = SolitarioFrame(
    ...     on_key_event=lambda evt: print(f"Key: {evt.GetKeyCode()}"),
    ...     on_close=lambda: cleanup()
    ... )
    >>> frame.start_timer(1000)  # 1-second interval
    >>> frame.Show()  # Actually stays invisible due to size/style
"""

import wx
from typing import Optional, Callable


class SolitarioFrame(wx.Frame):
    """Invisible frame for keyboard event capture.
    
    This frame serves as an event sink for keyboard input without displaying
    a visible window. It's sized at 1x1 pixel with wx.FRAME_NO_TASKBAR style
    to prevent appearance in taskbar or ALT+TAB switcher.
    
    Features:
    - Invisible window (1x1 pixel, no taskbar entry)
    - Keyboard event capture (EVT_KEY_DOWN, EVT_CHAR)
    - Timer management (wx.Timer for periodic checks)
    - Close event handling (EVT_CLOSE)
    - Focus handling to ensure events are captured
    
    Attributes:
        on_key_event: Callback for keyboard events
            Signature: callback(event: wx.KeyEvent) -> None
        on_timer_tick: Optional callback for timer events
            Signature: callback() -> None
        on_close: Optional callback for frame closure
            Signature: callback() -> None
        timer: wx.Timer instance for periodic events (lazy init)
    
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
        >>> frame.Show()
    
    Note:
        Despite calling Show(), the frame remains invisible due to:
        - 1x1 pixel size (imperceptible)
        - wx.FRAME_NO_TASKBAR flag (no taskbar entry)
        - No parent window (standalone but hidden)
    """
    
    def __init__(
        self,
        on_key_event: Callable[[wx.KeyEvent], None],
        on_timer_tick: Optional[Callable[[], None]] = None,
        on_close: Optional[Callable[[], None]] = None,
        parent: Optional[wx.Window] = None,
        id: int = wx.ID_ANY,
        title: str = "Solitario Event Sink"
    ):
        """Initialize invisible frame with event callbacks.
        
        Args:
            on_key_event: Required callback for keyboard events.
                Called for both EVT_KEY_DOWN and EVT_CHAR events.
            on_timer_tick: Optional callback for timer ticks.
                Called at interval specified in start_timer().
            on_close: Optional callback for frame closure.
                Called before frame is destroyed.
            parent: Optional parent window (None for standalone)
            id: Window ID (default wx.ID_ANY)
            title: Frame title (not visible, used for debugging)
        
        Note:
            Frame is created but not shown. Call Show() after creation,
            though it will remain invisible due to size and style.
        """
        # Initialize callbacks
        self.on_key_event = on_key_event
        self.on_timer_tick = on_timer_tick
        self.on_close = on_close
        
        # Create invisible frame (1x1 pixel, no taskbar)
        super().__init__(
            parent=parent,
            id=id,
            title=title,
            pos=(0, 0),  # Top-left corner (off-screen on some systems)
            size=(1, 1),  # Minimum size (imperceptible)
            style=wx.FRAME_NO_TASKBAR  # Critical: no ALT+TAB appearance
        )
        
        # Timer for periodic checks (lazy initialization)
        self._timer: Optional[wx.Timer] = None
        
        # Bind keyboard events
        self.Bind(wx.EVT_KEY_DOWN, self._on_key_down)
        self.Bind(wx.EVT_CHAR, self._on_char)
        
        # Bind close event
        self.Bind(wx.EVT_CLOSE, self._on_close_event)
        
        # Set focus to ensure events are captured
        # Note: This may not work reliably if frame is not shown
        self.SetFocus()
    
    def _on_key_down(self, event: wx.KeyEvent) -> None:
        """Internal handler for EVT_KEY_DOWN events.
        
        Forwards event to user-provided callback, then calls Skip()
        to allow normal event processing (e.g., for screen readers).
        
        Args:
            event: wx.KeyEvent from keyboard
        
        Note:
            event.Skip() is critical for NVDA integration - it ensures
            screen readers can process the event after our handler.
        """
        # Call user callback
        if self.on_key_event is not None:
            self.on_key_event(event)
        
        # Allow event to propagate (critical for screen readers)
        event.Skip()
    
    def _on_char(self, event: wx.KeyEvent) -> None:
        """Internal handler for EVT_CHAR events.
        
        EVT_CHAR provides character-level input (e.g., 'a', 'A', '1').
        Forwards to on_key_event callback for consistency.
        
        Args:
            event: wx.KeyEvent from keyboard
        
        Note:
            Some keys only generate EVT_CHAR (not EVT_KEY_DOWN), so
            binding both events ensures comprehensive capture.
        """
        # Call user callback (same handler as KEY_DOWN)
        if self.on_key_event is not None:
            self.on_key_event(event)
        
        # Allow event to propagate
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
