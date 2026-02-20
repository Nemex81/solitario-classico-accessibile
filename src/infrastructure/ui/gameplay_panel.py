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
    # User presses ESC → _handle_esc() shows abandon confirmation dialog
"""

import wx
from .basic_panel import BasicPanel


class GameplayPanel(BasicPanel):
    """Gameplay panel for audiogame mode (single-frame pattern).
    
    Provides minimal UI (just a label) but captures all keyboard events
    and routes them to GameplayController. ESC key always shows abandon
    confirmation dialog.
    
    Features:
    - Minimal UI (audiogame mode - no visual gameplay)
    - Full keyboard capture via EVT_CHAR_HOOK
    - Routes all keys to GameplayController.handle_wx_key_event()
    - ESC handling always shows confirmation dialog
    - Simple label showing instructions
    
    ESC Handling:
    - ESC always shows "Vuoi abbandonare?" dialog
    - User chooses Yes (abandon) or No (continue)
    - Prevents accidental game abandonment
    
    Example:
        >>> controller = SolitarioController()
        >>> gameplay = GameplayPanel(parent=frame.panel_container, controller=controller)
        >>> gameplay.Show()
        # User presses 1 → Handled by GameplayController
        # User presses H → Shows help
        # User presses ESC → Confirmation dialog shown
    
    Note:
        Based on wxPython single-frame pattern. All gameplay logic remains in
        GameplayController - this panel is just a keyboard event sink.
    """
    
    def __init__(self, parent, controller, container=None, **kwargs):
        """Initialize GameplayPanel with controller.
        
        Args:
            parent: Parent panel container (frame.panel_container)
            controller: Application controller with gameplay_controller attribute
            container: Optional DependencyContainer for future DI needs (v2.2.0)
            **kwargs: Additional arguments passed to BasicPanel
        
        Note:
            Controller must have:
            - gameplay_controller: GamePlayController instance
            - show_abandon_game_dialog(): Method to show abandon confirmation
        
        Version:
            v2.2.0: Added optional container parameter for DI pattern
        """
        self.container = container
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
        """Handle ESC key by showing abandon game confirmation dialog.
        
        Always shows confirmation dialog when ESC is pressed during gameplay.
        User must explicitly choose Yes or No to abandon or continue.
        
        Flow:
            1. User presses ESC
            2. Show "Vuoi abbandonare la partita?" dialog
            3. User chooses:
               - Yes: Abandon game and return to menu
               - No: Continue playing
        
        Args:
            event: wx.KeyEvent for ESC key
        
        Example:
            User presses ESC → Dialog shown with Yes/No options
            User selects No → Game continues
            User presses ESC again → Dialog shown again
        
        Note:
            This prevents accidental game abandonment by always requiring
            explicit user confirmation via dialog.
        
        New in v1.7.5: Simplified to always show dialog (removed double-ESC quick exit)
        """
        if self.controller:
            self.controller.show_abandon_game_dialog()


# Module-level documentation
__all__ = ['GameplayPanel']
