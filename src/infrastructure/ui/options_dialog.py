"""OptionsDialog - wxPython modal dialog for game options.

This module provides a wxPython-based options dialog that wraps the existing
OptionsWindowController, providing native window behavior with keyboard navigation.

Pattern: Modal dialog with keyboard event routing
Clean Architecture Layer: Infrastructure/UI
Dependency: wxPython 4.1.x+
Platform: Windows (primary), Linux (tested), macOS (untested)

Usage:
    >>> from src.application.options_controller import OptionsWindowController
    >>> from src.infrastructure.accessibility.screen_reader import ScreenReader
    >>> controller = OptionsWindowController(settings)
    >>> dlg = OptionsDialog(parent=frame, controller=controller, screen_reader=sr)
    >>> dlg.ShowModal()
    >>> dlg.Destroy()
"""

import wx
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.infrastructure.accessibility.screen_reader import ScreenReader

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
        screen_reader: Optional['ScreenReader'] = None,
        title: str = "Opzioni di gioco",
        size: tuple = (500, 400)
    ):
        """Initialize OptionsDialog with controller and screen reader.
        
        Args:
            parent: Parent window (typically main frame)
            controller: OptionsWindowController instance
            screen_reader: ScreenReader for TTS feedback (optional)
            title: Dialog title (default: "Opzioni di gioco")
            size: Dialog size in pixels (default: 500x400)
        
        Attributes:
            options_controller: Reference to OptionsWindowController
            screen_reader: Reference to ScreenReader for TTS
        
        Note:
            Controller must be initialized with GameSettings instance.
            The dialog routes keyboard events to controller methods.
            If screen_reader is provided, vocalize controller messages.
        """
        super().__init__(
            parent=parent,
            title=title,
            size=size,
            style=wx.DEFAULT_DIALOG_STYLE
        )
        
        self.options_controller = controller
        self.screen_reader = screen_reader
        
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
        All messages from controller are vocalized via ScreenReader TTS.
        
        Args:
            event: wx.KeyEvent from keyboard
        
        Key Mapping (Complete - v1.7.5):
        - ESC: Close dialog with cancel
        - UP/DOWN: Navigate options (navigate_up/down)
        - ENTER: Modify current option (modify_current_option)
        - 1-8: Jump to specific option:
            1. Tipo Mazzo (Francese/Napoletano)
            2. Difficoltà (1-3 carte)
            3. Carte Pescate (1-3)
            4. Timer (OFF, 5-60 min)
            5. Riciclo Scarti (Inversione/Mescolata)
            6. Suggerimenti Comandi (ON/OFF)
            7. Sistema Punti (Attivo/Disattivato)
            8. Modalità Timer (STRICT/PERMISSIVE)
        - T: Toggle timer on/off (toggle_timer)
        - +: Increment timer value (increment_timer)
        - -: Decrement timer value (decrement_timer)
        - I: Read all settings (read_all_settings)
        - H: Show help text (show_help)
        
        Note:
            Both main keyboard and numpad keys are supported.
            Controller methods return TTS messages vocalized by dialog.
        """
        key_code = event.GetKeyCode()
        msg = None  # Message from controller
        
        # ESC: Cancel and close dialog
        if key_code == wx.WXK_ESCAPE:
            msg = self.options_controller.cancel_close()
            self.EndModal(wx.ID_CANCEL)
            return
        
        # UP: Navigate to previous option
        elif key_code == wx.WXK_UP:
            msg = self.options_controller.navigate_up()
        
        # DOWN: Navigate to next option
        elif key_code == wx.WXK_DOWN:
            msg = self.options_controller.navigate_down()
        
        # ENTER: Modify current option
        elif key_code in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            msg = self.options_controller.modify_current_option()
        
        # Numbers 1-8: Jump to specific option (complete set)
        elif key_code in (ord('1'), wx.WXK_NUMPAD1):
            msg = self.options_controller.jump_to_option(0)  # Tipo Mazzo
        elif key_code in (ord('2'), wx.WXK_NUMPAD2):
            msg = self.options_controller.jump_to_option(1)  # Difficoltà
        elif key_code in (ord('3'), wx.WXK_NUMPAD3):
            msg = self.options_controller.jump_to_option(2)  # Carte Pescate
        elif key_code in (ord('4'), wx.WXK_NUMPAD4):
            msg = self.options_controller.jump_to_option(3)  # Timer
        elif key_code in (ord('5'), wx.WXK_NUMPAD5):
            msg = self.options_controller.jump_to_option(4)  # Riciclo Scarti
        elif key_code in (ord('6'), wx.WXK_NUMPAD6):
            msg = self.options_controller.jump_to_option(5)  # Suggerimenti Comandi
        elif key_code in (ord('7'), wx.WXK_NUMPAD7):
            msg = self.options_controller.jump_to_option(6)  # Sistema Punti
        elif key_code in (ord('8'), wx.WXK_NUMPAD8):
            msg = self.options_controller.jump_to_option(7)  # Modalità Timer
        
        # T: Toggle timer on/off
        elif key_code in (ord('T'), ord('t')):
            msg = self.options_controller.toggle_timer()
        
        # +/=: Increment timer value
        elif key_code in (ord('+'), ord('='), wx.WXK_NUMPAD_ADD):
            msg = self.options_controller.increment_timer()
        
        # -/_: Decrement timer value
        elif key_code in (ord('-'), ord('_'), wx.WXK_NUMPAD_SUBTRACT):
            msg = self.options_controller.decrement_timer()
        
        # I: Read all settings recap
        elif key_code in (ord('I'), ord('i')):
            msg = self.options_controller.read_all_settings()
        
        # H: Show help text
        elif key_code in (ord('H'), ord('h')):
            msg = self.options_controller.show_help()
        
        # If key was handled, vocalize message via TTS
        if msg is not None:
            if self.screen_reader and self.screen_reader.tts:
                self.screen_reader.tts.speak(msg, interrupt=True)
            return
        
        # Key not handled: propagate
        event.Skip()


# Module exports
__all__ = ['OptionsDialog']
