"""Timer management for timed gameplay.

Provides countdown timer with configurable duration,
warning notifications, and pause/resume functionality.

Integrates with game_over logic to end game when time expires.
"""

import time
from typing import Optional, Callable
from dataclasses import dataclass

from src.infrastructure.logging import game_logger as log


@dataclass
class TimerState:
    """Timer state snapshot.
    
    Attributes:
        elapsed: Seconds elapsed since start
        remaining: Seconds remaining until expiration
        is_running: Whether timer is currently running
        is_paused: Whether timer is paused
        duration: Total timer duration in seconds
    """
    elapsed: float
    remaining: float
    is_running: bool
    is_paused: bool
    duration: float


class TimerManager:
    """Countdown timer with warnings.
    
    Manages game timer with:
    - Configurable duration in minutes
    - Warning callbacks at specified intervals
    - Pause/resume support
    - Expiration detection
    
    The timer uses wall-clock time (time.time()) for accuracy
    and accounts for paused periods.
    
    Attributes:
        duration_seconds: Total timer duration
        start_time: Timestamp when timer started
        pause_time: Timestamp when timer paused (None if running)
        paused_duration: Total seconds paused
        warning_callback: Function to call for warnings
        warnings_issued: Set of warning minutes already triggered
    
    Example:
        >>> def on_warning(minutes_left):
        ...     print(f"Warning: {minutes_left} minutes remaining!")
        >>> 
        >>> timer = TimerManager(minutes=10, warning_callback=on_warning)
        >>> timer.start()
        >>> timer.get_state()  # TimerState with elapsed/remaining
        >>> if timer.is_expired():
        ...     print("Time's up!")
    """
    
    # Default warning intervals in minutes
    DEFAULT_WARNINGS = [5, 2, 1]  # Warn at 5min, 2min, 1min left
    
    def __init__(
        self,
        minutes: int = 10,
        warning_callback: Optional[Callable[[int], None]] = None,
        warning_intervals: Optional[list[int]] = None
    ) -> None:
        """Initialize timer manager.
        
        Args:
            minutes: Timer duration in minutes (1-60)
            warning_callback: Function(minutes_left) for warnings
            warning_intervals: List of minutes at which to warn (default: [5,2,1])
        
        Raises:
            ValueError: If minutes not in valid range 1-60
        """
        if not 1 <= minutes <= 60:
            raise ValueError(f"Timer minutes must be 1-60, got {minutes}")
        
        self.duration_seconds = minutes * 60.0
        self.start_time: Optional[float] = None
        self.pause_time: Optional[float] = None
        self.paused_duration: float = 0.0
        
        self.warning_callback = warning_callback
        self.warning_intervals = warning_intervals or self.DEFAULT_WARNINGS
        self.warnings_issued: set[int] = set()
    
    def start(self) -> None:
        """Start the timer.
        
        Records start time and resets state.
        Safe to call multiple times (restarts timer).
        """
        self.start_time = time.time()
        self.pause_time = None
        self.paused_duration = 0.0
        self.warnings_issued.clear()
        log.timer_started(self.duration_seconds)
    
    def pause(self) -> None:
        """Pause the timer.
        
        Records pause time. Subsequent get_elapsed() calls will
        not include paused time until resume() is called.
        
        No-op if already paused or not started.
        """
        if self.start_time is None or self.pause_time is not None:
            return  # Not started or already paused
        
        self.pause_time = time.time()
        log.timer_paused(self.get_remaining())
    
    def resume(self) -> None:
        """Resume the timer after pause.
        
        Adds paused duration to total and resumes counting.
        No-op if not paused.
        """
        if self.pause_time is None:
            return  # Not paused
        
        # Add this pause period to total
        self.paused_duration += time.time() - self.pause_time
        self.pause_time = None
    
    def get_elapsed(self) -> float:
        """Get elapsed time in seconds.
        
        Returns:
            Seconds elapsed since start (excluding paused time)
            Returns 0.0 if not started.
        """
        if self.start_time is None:
            return 0.0
        
        # If paused, use pause_time as current time
        current_time = self.pause_time if self.pause_time else time.time()
        
        # Elapsed = (now - start) - paused_time
        elapsed = current_time - self.start_time - self.paused_duration
        return max(0.0, elapsed)
    
    def get_remaining(self) -> float:
        """Get remaining time in seconds.
        
        Returns:
            Seconds remaining (0.0 if expired)
        """
        remaining = self.duration_seconds - self.get_elapsed()
        return max(0.0, remaining)
    
    def is_expired(self) -> bool:
        """Check if timer has expired.
        
        Returns:
            True if elapsed time >= duration
        """
        return self.get_elapsed() >= self.duration_seconds
    
    def is_running(self) -> bool:
        """Check if timer is running.
        
        Returns:
            True if started and not paused
        """
        return self.start_time is not None and self.pause_time is None
    
    def is_paused(self) -> bool:
        """Check if timer is paused.
        
        Returns:
            True if started and paused
        """
        return self.start_time is not None and self.pause_time is not None
    
    def get_state(self) -> TimerState:
        """Get current timer state snapshot.
        
        Returns:
            TimerState with all current values
        """
        return TimerState(
            elapsed=self.get_elapsed(),
            remaining=self.get_remaining(),
            is_running=self.is_running(),
            is_paused=self.is_paused(),
            duration=self.duration_seconds
        )
    
    def check_warnings(self) -> None:
        """Check if warnings should be triggered.
        
        Call this periodically (e.g., every update loop) to
        trigger warning callbacks at configured intervals.
        
        Warnings are triggered once per interval (not repeated).
        """
        if not self.is_running() or self.warning_callback is None:
            return
        
        remaining_minutes = int(self.get_remaining() / 60)
        
        # Check each warning interval
        for warning_min in self.warning_intervals:
            # Trigger if we've reached this warning and haven't issued it yet
            if remaining_minutes <= warning_min and warning_min not in self.warnings_issued:
                self.warnings_issued.add(warning_min)
                self.warning_callback(warning_min)
    
    def reset(self, minutes: Optional[int] = None) -> None:
        """Reset timer to initial state.
        
        Args:
            minutes: New duration in minutes (None = keep current)
        
        Raises:
            ValueError: If minutes not in valid range 1-60
        """
        if minutes is not None:
            if not 1 <= minutes <= 60:
                raise ValueError(f"Timer minutes must be 1-60, got {minutes}")
            self.duration_seconds = minutes * 60.0
        
        self.start_time = None
        self.pause_time = None
        self.paused_duration = 0.0
        self.warnings_issued.clear()
