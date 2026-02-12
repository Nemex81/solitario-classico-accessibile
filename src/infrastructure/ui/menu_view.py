"""MenuView - Native wxPython menu with button widgets (hs_deckmanager pattern).

This module provides the main menu view using real wx.Button widgets instead
of virtual text-based navigation. Improves NVDA accessibility with native
focus management.

Pattern: hs_deckmanager MenuView
Clean Architecture Layer: Infrastructure/UI
Dependency: wxPython 4.1.x+
Platform: Windows (primary), Linux (tested), macOS (untested)

Usage:
    >>> menu = MenuView(parent=None, controller=my_ctrl)
    >>> menu.Show()
    # User navigates with TAB, activates with ENTER
    # NVDA announces button labels on focus
"""

import wx
from .basic_view import BasicView


class MenuView(BasicView):
    """Main menu view with native wxPython buttons (hs_deckmanager pattern).
    
    Replaces pygame-based virtual menu with real wx.Button widgets that are
    navigable via TAB and accessible to screen readers.
    
    Features:
    - wx.Button widgets for menu items (TAB-navigable)
    - Automatic NVDA announcements on button focus
    - Callbacks to controller for actions
    - Bold title label
    - Centered layout
    
    Menu Items:
    1. "Gioca al solitario classico" → start_gameplay()
    2. "Opzioni di gioco" → show_options()
    3. "Esci dal gioco" → show_exit_dialog()
    
    Example:
        >>> controller = SolitarioController()
        >>> menu = MenuView(None, controller)
        >>> menu.Show()
        # User presses TAB → NVDA announces "Gioca al solitario classico"
        # User presses ENTER → calls controller.start_gameplay()
    
    Note:
        Based on hs_deckmanager HearthstoneAppFrame pattern.
        Requires controller with methods: start_gameplay(), show_options(),
        show_exit_dialog().
    """
    
    def __init__(self, parent, controller, **kwargs):
        """Initialize MenuView with controller.
        
        Args:
            parent: Parent frame (None for independent window)
            controller: Application controller with menu action methods
            **kwargs: Additional arguments passed to BasicView
        
        Note:
            Automatically shows menu with focus on first button and
            announces "Menu principale. 3 opzioni disponibili."
        """
        super().__init__(
            parent=parent,
            controller=controller,
            title="Solitario Classico Accessibile - Menu",
            size=(600, 400),
            **kwargs
        )
    
    def init_ui_elements(self) -> None:
        """Create menu buttons with accessibility (hs_deckmanager pattern).
        
        Creates:
        - Title label (bold, 16pt)
        - Play button → controller.start_gameplay()
        - Options button → controller.show_options()
        - Exit button → controller.show_exit_dialog()
        
        Each button binds:
        - EVT_BUTTON: Click handler
        - EVT_SET_FOCUS: Accessibility announcement
        
        Layout:
        - Title centered at top
        - Buttons vertically stacked with 20px padding
        - First button receives initial focus
        
        Note:
            Buttons are expanded horizontally with wx.EXPAND flag.
            Focus announcements use self.announce() for TTS.
        """
        # Title label (bold, 16pt)
        title = wx.StaticText(self.panel, label="Menu Principale")
        title.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.sizer.Add(title, flag=wx.CENTER | wx.TOP, border=20)
        
        # Create buttons
        btn_play = wx.Button(self.panel, label="Gioca al solitario classico")
        btn_play.Bind(wx.EVT_BUTTON, self.on_play_click)
        btn_play.Bind(wx.EVT_SET_FOCUS, self.on_button_focus)
        
        btn_options = wx.Button(self.panel, label="Opzioni di gioco")
        btn_options.Bind(wx.EVT_BUTTON, self.on_options_click)
        btn_options.Bind(wx.EVT_SET_FOCUS, self.on_button_focus)
        
        btn_exit = wx.Button(self.panel, label="Esci dal gioco")
        btn_exit.Bind(wx.EVT_BUTTON, self.on_exit_click)
        btn_exit.Bind(wx.EVT_SET_FOCUS, self.on_button_focus)
        
        # Add buttons to vertical sizer (hs_deckmanager layout)
        btn_sizer = wx.BoxSizer(wx.VERTICAL)
        for btn in [btn_play, btn_options, btn_exit]:
            btn_sizer.Add(btn, 0, wx.ALL | wx.EXPAND, 20)
        
        self.sizer.Add(btn_sizer, 1, wx.ALIGN_CENTER)
        
        # Set initial focus and announce menu opened
        btn_play.SetFocus()
        self.announce("Menu principale. 3 opzioni disponibili.", interrupt=True)
    
    def on_button_focus(self, event: wx.FocusEvent) -> None:
        """Announce button label when focused (accessibility).
        
        Called automatically when user TABs to a button or when SetFocus()
        is called programmatically. Announces button label via TTS for
        screen reader users.
        
        Args:
            event: wx.FocusEvent from button focus change
        
        Example:
            User presses TAB → Focus moves to "Opzioni di gioco" button
            → This method calls announce("Opzioni di gioco")
            → NVDA reads "Opzioni di gioco"
        
        Note:
            Always calls event.Skip() to allow normal focus processing.
        """
        button = event.GetEventObject()
        self.announce(button.GetLabel(), interrupt=False)
        event.Skip()
    
    def on_play_click(self, event: wx.ButtonEvent) -> None:
        """Handle "Gioca al solitario classico" button click.
        
        Delegates to controller.start_gameplay() which should:
        1. Hide this menu view
        2. Push GameplayView onto ViewManager stack
        3. Initialize new game
        
        Args:
            event: wx.ButtonEvent from button click or ENTER key
        
        Note:
            Controller is responsible for view management and game initialization.
        """
        if self.controller:
            self.controller.start_gameplay()
    
    def on_options_click(self, event: wx.ButtonEvent) -> None:
        """Handle "Opzioni di gioco" button click.
        
        Delegates to controller.show_options() which should display
        the options configuration dialog or view.
        
        Args:
            event: wx.ButtonEvent from button click or ENTER key
        
        Note:
            Controller is responsible for showing options dialog.
        """
        if self.controller:
            self.controller.show_options()
    
    def on_exit_click(self, event: wx.ButtonEvent) -> None:
        """Handle "Esci dal gioco" button click.
        
        Delegates to controller.show_exit_dialog() which should show
        a confirmation dialog before exiting the application.
        
        Args:
            event: wx.ButtonEvent from button click or ENTER key
        
        Note:
            Controller is responsible for confirmation dialog and exit logic.
        """
        if self.controller:
            self.controller.show_exit_dialog()


# Module-level documentation
__all__ = ['MenuView']
