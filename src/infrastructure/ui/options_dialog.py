"""OptionsDialog - wxPython modal dialog for game options.

This module provides a wxPython-based options dialog that wraps the existing
OptionsWindowController, providing native window behavior with keyboard navigation.

Pattern: Modal dialog with keyboard event routing
Clean Architecture Layer: Infrastructure/UI
Dependency: wxPython 4.1.x+
Platform: Windows (primary), Linux (tested), macOS (untested)

Usage:
    >>> from src.application.options_controller import OptionsWindowController
    >>> controller = OptionsWindowController(settings)
    >>> dlg = OptionsDialog(parent=frame, controller=controller)
    >>> dlg.ShowModal()
    >>> dlg.Destroy()
"""

import wx
from typing import Optional

from src.application.options_controller import OptionsWindowController


class OptionsDialog(wx.Dialog):
    """Modal options dialog driven by OptionsWindowController.
    
    Provides a wxPython native dialog for game options configuration.
    Routes keyboard events to OptionsWindowController methods for consistency
    with the existing virtual options system.
    
    Features:
    - Modal dialog (blocks input to parent window)
    - Keyboard navigation (arrows, ENTER, ESC)
    - Routes events to OptionsWindowController
    - ESC closes dialog with cancel
    
    Keyboard Mapping (STEP 3 - basic):
    - ESC: Cancel and close dialog
    - Other keys: To be mapped in STEP 4
    
    Example:
        >>> settings = GameSettings()
        >>> options_ctrl = OptionsWindowController(settings)
        >>> dlg = OptionsDialog(parent=main_frame, controller=options_ctrl)
        >>> result = dlg.ShowModal()  # wx.ID_OK or wx.ID_CANCEL
        >>> dlg.Destroy()
    
    Note:
        Full keyboard mapping (UP/DOWN/ENTER/1-5/T/+/-) will be added in STEP 4.
        This is STEP 3 - minimal dialog with ESC handling only.
    """
    
    def __init__(
        self,
        parent: wx.Window,
        controller: OptionsWindowController,
        title: str = "Opzioni di gioco",
        size: tuple = (500, 400)
    ):
        """Initialize OptionsDialog with controller.
        
        Args:
            parent: Parent window (typically main frame)
            controller: OptionsWindowController instance
            title: Dialog title (default: "Opzioni di gioco")
            size: Dialog size in pixels (default: 500x400)
        
        Attributes:
            options_controller: Reference to OptionsWindowController
        
        Note:
            Controller must be initialized with GameSettings instance.
            The dialog routes keyboard events to controller methods.
        """
        super().__init__(
            parent=parent,
            title=title,
            size=size,
            style=wx.DEFAULT_DIALOG_STYLE
        )
        
        self.options_controller = controller
        
        # Create minimal UI
        self._create_ui()
        
        # Bind keyboard events
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)
        
        # Center dialog on parent
        self.Centre()
    
    def _create_ui(self) -> None:
        """Create dialog UI elements.
        
        Creates a simple layout with informational text.
        In STEP 3, this is minimal - just shows instructions.
        
        Layout:
        - StaticText with usage instructions
        - 10px padding on all sides
        - Vertical sizer for expansion
        
        Note:
            The actual options interface is audio-based (TTS).
            This visual UI is minimal for accessibility.
        """
        # Main sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Instructional label
        label = wx.StaticText(
            self,
            label="Finestra opzioni. Usa frecce e invio per modificare.\n\n"
                  "Premere ESC per chiudere."
        )
        label.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        
        # Add to sizer with padding
        sizer.Add(label, 0, wx.ALL | wx.EXPAND, 10)
        
        self.SetSizer(sizer)
    
    def on_key_down(self, event: wx.KeyEvent) -> None:
        """Handle keyboard events for options navigation.
        
        Routes keyboard input to OptionsWindowController methods.
        
        Args:
            event: wx.KeyEvent from keyboard
        
        Key Mapping (STEP 3 - basic):
        - ESC: Close dialog with cancel
        
        TODO (STEP 4):
        - UP/DOWN: Navigate options
        - ENTER: Modify current option
        - 1-5: Jump to option
        - T: Toggle timer
        - +/-: Increment/decrement timer
        
        Note:
            Full key mapping will be added in STEP 4.
            This is minimal implementation for STEP 3.
        """
        key_code = event.GetKeyCode()
        
        # ESC: Cancel and close dialog
        if key_code == wx.WXK_ESCAPE:
            # Use controller to handle cancel logic
            msg = self.options_controller.cancel_close()
            
            # Vocalize message if present (via controller's screen reader)
            # Note: Screen reader access will be improved in STEP 4
            
            # Close dialog with cancel status
            self.EndModal(wx.ID_CANCEL)
            return
        
        # Other keys: Not handled yet (STEP 4)
        # For now, just propagate
        event.Skip()


# Module exports
__all__ = ['OptionsDialog']
