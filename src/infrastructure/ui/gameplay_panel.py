"""GameplayPanel - Audiogame panel for gameplay (single-frame pattern).

This module provides the gameplay panel which is essentially invisible (audiogame
mode) but captures all keyboard input and routes it to GameplayController.

Pattern: Single-frame panel-swap (wxPython standard)
Clean Architecture Layer: Infrastructure/UI
Dependency: wxPython 4.1.x+
Platform: Windows (primary), Linux (tested), macOS (untested)

Usage:
    >>> gameplay = GameplayPanel(parent=frame.panel_container, controller=my_ctrl)
    >>> gameplay.Show()
    # User presses H → GameplayController.handle_wx_key_event(H)
    # User presses ESC → _handle_esc() with double-ESC detection
"""

import wx
import time
from .basic_panel import BasicPanel


class GameplayPanel(BasicPanel):
    """Gameplay panel for audiogame mode (single-frame pattern).
    
    Provides minimal UI (just a label) but captures all keyboard events
    and routes them to GameplayController. Implements double-ESC detection
    for quick game abandonment.
    
    Features:
    - Minimal UI (audiogame mode - no visual gameplay)
    - Full keyboard capture via EVT_CHAR_HOOK
    - Routes all keys to GameplayController.handle_wx_key_event()
    - ESC handling with double-tap detection (< 2 seconds)
    - Simple label showing instructions
    
    Double-ESC Detection:
    - First ESC (>2s since last): Show abandon dialog
    - Second ESC (<2s since first): Instant abandon (no dialog)
    - Threshold: 2.0 seconds (same as original pygame version)
    
    Example:
        >>> controller = SolitarioController()
        >>> gameplay = GameplayPanel(parent=frame.panel_container, controller=controller)
        >>> gameplay.Show()
        # User presses 1 → Handled by GameplayController
        # User presses H → Shows help
        # User presses ESC twice → Instant abandon
    
    Note:
        Based on wxPython single-frame pattern. All gameplay logic remains in
        GameplayController - this panel is just a keyboard event sink.
    """
    
    # Double-ESC threshold in seconds
    DOUBLE_ESC_THRESHOLD = 2.0
    
    def __init__(self, parent, controller, **kwargs):
        """Initialize GameplayPanel with controller.
        
        Args:
            parent: Parent panel container (frame.panel_container)
            controller: Application controller with gameplay_controller attribute
            **kwargs: Additional arguments passed to BasicPanel
        
        Attributes:
            last_esc_time: Timestamp of last ESC press (for double-ESC detection)
        
        Note:
            Controller must have:
            - gameplay_controller: GamePlayController instance
            - show_abandon_game_dialog(): Method to show abandon confirmation
            - confirm_abandon_game(skip_dialog=True): Method to abandon without dialog
        """
        # Initialize double-ESC detection
        self.last_esc_time = 0.0
        
        super().__init__(
            parent=parent,
            controller=controller,
            **kwargs
        )
    
    def init_ui_elements(self) -> None:
        """Create minimal UI (audiogame mode).
        
        Creates a simple label with instructions. The actual gameplay has
        no visual representation - all interaction is via keyboard and TTS.
        
        Label text:
        "Partita in corso\n\nPremi H per comandi disponibili"
        
        Note:
            This is just a placeholder. Real audiogame has no visual UI,
            but wxPython requires some window content for proper operation.
            Parent is self (not self.panel) in single-frame pattern.
        """
        # Simple label (audiogame mode - no visual gameplay)
        label = wx.StaticText(
            self,
            label="Partita in corso\n\nPremi H per comandi disponibili"
        )
        label.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        self.sizer.Add(label, 1, wx.ALIGN_CENTER)
    
    def on_key_down(self, event: wx.KeyEvent) -> None:
        """Route keyboard events to gameplay controller or handle ESC.
        
        All keys except ESC are forwarded to GameplayController.handle_wx_key_event()
        for processing. ESC is handled specially for double-tap detection.
        
        Args:
            event: wx.KeyEvent from keyboard
        
        Key Routing:
        - ESC → _handle_esc() (double-tap detection)
        - All other keys → GameplayController.handle_wx_key_event()
        
        Supported Keys (handled by GameplayController):
        - Numbers 1-7: Navigate to pile
        - Arrows: Navigate cursor
        - SPACE/ENTER: Select/move card
        - D/P: Draw from deck
        - H: Help
        - O: Options
        - And 50+ more commands...
        
        Note:
            Always calls event.Skip() after routing to ensure screen readers
            can also process the event.
        """
        key_code = event.GetKeyCode()
        
        # ESC: Handle with double-tap detection
        if key_code == wx.WXK_ESCAPE:
            self._handle_esc(event)
            return  # Don't skip - we handled it
        
        # All other keys: Route to gameplay controller
        if self.controller and hasattr(self.controller, 'gameplay_controller'):
            handled = self.controller.gameplay_controller.handle_wx_key_event(event)
            if handled:
                return  # Key consumed, don't propagate
        
        event.Skip()  # Allow screen readers to process unhandled keys
    
    def _handle_esc(self, event: wx.KeyEvent) -> None:
        """Handle ESC with context-aware double-tap detection.
        
        Implements double-ESC quick exit feature:
        - First ESC: Show abandon game confirmation dialog
        - Second ESC (within 2 seconds): Instant abandon (no dialog)
        
        Timing:
        - If time since last ESC > 2.0s: Show dialog (fresh ESC)
        - If time since last ESC ≤ 2.0s: Instant abandon (double-ESC)
        
        Flow:
        First ESC:
            1. Record current time
            2. Call controller.show_abandon_game_dialog()
            3. User chooses Yes/No in dialog
        
        Second ESC (< 2s):
            1. Detect time since first < 2.0s
            2. Announce "Uscita rapida!"
            3. Call controller.confirm_abandon_game(skip_dialog=True)
            4. Reset last_esc_time to 0
        
        Args:
            event: wx.KeyEvent for ESC key
        
        Example:
            User presses ESC → Dialog shown
            User presses ESC again within 2s → "Uscita rapida!" + instant abandon
        
        Note:
            This implements the same double-ESC behavior as the original
            pygame version for consistency.
        """
        current_time = time.time()
        
        # Check for double-ESC (< 2 second threshold)
        if self.last_esc_time > 0 and current_time - self.last_esc_time <= self.DOUBLE_ESC_THRESHOLD:
            # Double-ESC detected: Instant abandon
            self.announce("Uscita rapida!", interrupt=True)
            
            if self.controller:
                # Skip dialog and abandon immediately
                self.controller.confirm_abandon_game(skip_dialog=True)
            
            # Reset timer
            self.last_esc_time = 0.0
        else:
            # First ESC: Show dialog
            self.last_esc_time = current_time
            
            if self.controller:
                self.controller.show_abandon_game_dialog()


# Module-level documentation
__all__ = ['GameplayPanel']
