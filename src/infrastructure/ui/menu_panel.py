"""MenuPanel - Native wxPython menu with button widgets (single-frame pattern).

This module provides the main menu panel using real wx.Button widgets instead
of virtual text-based navigation. Improves NVDA accessibility with native
focus management.

Pattern: Single-frame panel-swap (wxPython standard)
Clean Architecture Layer: Infrastructure/UI
Dependency: wxPython 4.1.x+
Platform: Windows (primary), Linux (tested), macOS (untested)

Usage:
    >>> menu = MenuPanel(parent=frame.panel_container, controller=my_ctrl)
    >>> menu.Show()
    # User navigates with TAB, activates with ENTER
    # NVDA announces button labels on focus
"""

import wx
from .basic_panel import BasicPanel


class MenuPanel(BasicPanel):
    """Main menu panel with native wxPython buttons (single-frame pattern).
    
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
        >>> menu = MenuPanel(parent=frame.panel_container, controller=controller)
        >>> menu.Show()
        # User presses TAB → NVDA announces "Gioca al solitario classico"
        # User presses ENTER → calls controller.start_gameplay()
    
    Note:
        Based on wxPython single-frame panel-swap pattern.
        Requires controller with methods: start_gameplay(), show_options(),
        show_exit_dialog().
    """
    
    def __init__(self, parent, controller, container=None, audio_manager=None, **kwargs):
        """Initialize MenuPanel with controller and optional audio manager.
        
        Args:
            parent: Parent panel container (frame.panel_container)
            controller: Application controller with menu action methods
            container: Optional DependencyContainer for future DI needs (v2.2.0)
            audio_manager: Optional AudioManager for sound effects (v3.5.0)
            **kwargs: Additional arguments passed to BasicPanel
        
        Note:
            Automatically announces "Menu principale. 3 opzioni disponibili."
            after initialization.
        
        Version:
            v2.2.0: Added optional container parameter for DI pattern
            v3.5.0: Added optional audio_manager parameter
        """
        self.container = container
        self.audio_manager = audio_manager
        super().__init__(
            parent=parent,
            controller=controller,
            **kwargs
        )
    
    def init_ui_elements(self) -> None:
        """Create menu buttons with accessibility (single-frame pattern).
        
        Creates:
        - Title label (bold, 16pt)
        - Play button → controller.start_gameplay()
        - Last Game button → controller.show_last_game_summary() (v3.1.0)
        - Leaderboard button → controller.show_leaderboard() (v3.1.0)
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
            Parent is self (not self.panel) in single-frame pattern.
            
        Version:
            v3.1.0: Added Last Game and Leaderboard buttons
        """
        # Title label (bold, 16pt)
        title = wx.StaticText(self, label="Menu Principale")
        title.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.sizer.Add(title, flag=wx.CENTER | wx.TOP, border=20)
        
        # Create buttons
        btn_play = wx.Button(self, label="Gioca al solitario classico")
        btn_play.Bind(wx.EVT_BUTTON, self.on_play_click)
        btn_play.Bind(wx.EVT_SET_FOCUS, self.on_button_focus)
        
        # NEW v3.1.0: Last game summary button
        btn_last_game = wx.Button(self, label="Ultima Partita (risultati)")
        btn_last_game.Bind(wx.EVT_BUTTON, self.on_last_game_click)
        btn_last_game.Bind(wx.EVT_SET_FOCUS, self.on_button_focus)
        
        # NEW v3.1.0: Leaderboard button
        btn_leaderboard = wx.Button(self, label="Leaderboard Globale")
        btn_leaderboard.Bind(wx.EVT_BUTTON, self.on_leaderboard_click)
        btn_leaderboard.Bind(wx.EVT_SET_FOCUS, self.on_button_focus)
        
        # NEW v3.1.0 Phase 10: Profile Menu button
        btn_profile_menu = wx.Button(self, label="Gestione Profili")
        btn_profile_menu.Bind(wx.EVT_BUTTON, self.on_profile_menu_click)
        btn_profile_menu.Bind(wx.EVT_SET_FOCUS, self.on_button_focus)
        
        btn_options = wx.Button(self, label="Opzioni di gioco")
        btn_options.Bind(wx.EVT_BUTTON, self.on_options_click)
        btn_options.Bind(wx.EVT_SET_FOCUS, self.on_button_focus)
        
        btn_exit = wx.Button(self, label="Esci dal gioco")
        btn_exit.Bind(wx.EVT_BUTTON, self.on_exit_click)
        btn_exit.Bind(wx.EVT_SET_FOCUS, self.on_button_focus)
        
        # Add buttons to vertical sizer
        btn_sizer = wx.BoxSizer(wx.VERTICAL)
        for btn in [btn_play, btn_last_game, btn_leaderboard, btn_profile_menu, btn_options, btn_exit]:
            btn_sizer.Add(btn, 0, wx.ALL | wx.EXPAND, 20)
        
        self.sizer.Add(btn_sizer, 1, wx.ALIGN_CENTER)
        
        # Set initial focus and announce menu opened
        btn_play.SetFocus()
        self.announce("Menu principale. 6 opzioni disponibili.", interrupt=True)
    
    def on_button_focus(self, event: wx.FocusEvent) -> None:
        """Announce button label when focused (accessibility).
        
        Called automatically when user TABs to a button or when SetFocus()
        is called programmatically. Announces button label via TTS for
        screen reader users.
        
        🆕 v3.5.0: Plays UI_BUTTON_HOVER sound effect.
        
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
        
        # ✨ NUOVO v3.5.0: Play button hover sound
        if self.audio_manager:
            from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
            self.audio_manager.play_event(AudioEvent(
                event_type=AudioEventType.UI_BUTTON_HOVER
            ))
        
        event.Skip()
    
    def on_play_click(self, event: wx.CommandEvent) -> None:
        """Handle "Gioca al solitario classico" button click.
        
        Delegates to controller.start_gameplay() which should:
        1. Hide this menu view
        2. Push GameplayView onto ViewManager stack
        3. Initialize new game
        
        🆕 v3.5.0: Plays UI_BUTTON_CLICK sound effect before action.
        
        Args:
            event: wx.CommandEvent from button click or ENTER key
        
        Note:
            Controller is responsible for view management and game initialization.
            wxPython button events are wx.CommandEvent, not wx.ButtonEvent.
        """
        # ✨ NUOVO v3.5.0: Play button click sound
        if self.audio_manager:
            from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
            self.audio_manager.play_event(AudioEvent(
                event_type=AudioEventType.UI_BUTTON_CLICK
            ))
        
        if self.controller:
            self.controller.start_gameplay()
    
    def on_last_game_click(self, event: wx.CommandEvent) -> None:
        """Handle "Ultima Partita" button click (v3.1.0).
        
        Delegates to controller.show_last_game_summary() which displays
        the LastGameDialog with summary of most recent game.
        
        🆕 v3.5.0: Plays UI_BUTTON_CLICK sound before action.
        
        Args:
            event: wx.CommandEvent from button click or ENTER key
        
        Version:
            v3.1.0 Phase 9.1
            v3.5.0: Added audio feedback
        """
        # ✨ NUOVO v3.5.0: Play button click sound
        if self.audio_manager:
            from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
            self.audio_manager.play_event(AudioEvent(
                event_type=AudioEventType.UI_BUTTON_CLICK
            ))
        
        if self.controller and hasattr(self.controller, 'show_last_game_summary'):
            self.controller.show_last_game_summary()
    
    def on_leaderboard_click(self, event: wx.CommandEvent) -> None:
        """Handle "Leaderboard Globale" button click (v3.1.0).
        
        Delegates to controller.show_leaderboard() which displays
        the LeaderboardDialog with global rankings.
        
        🆕 v3.5.0: Plays UI_BUTTON_CLICK sound before action.
        
        Args:
            event: wx.CommandEvent from button click or ENTER key
        
        Version:
            v3.1.0 Phase 9.2
            v3.5.0: Added audio feedback
        """
        # ✨ NUOVO v3.5.0: Play button click sound
        if self.audio_manager:
            from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
            self.audio_manager.play_event(AudioEvent(
                event_type=AudioEventType.UI_BUTTON_CLICK
            ))
        
        if self.controller and hasattr(self.controller, 'show_leaderboard'):
            self.controller.show_leaderboard()
    
    def on_profile_menu_click(self, event: wx.CommandEvent) -> None:
        """Handle "Gestione Profili" button click (v3.1.0 Phase 10).
        
        Delegates to controller.show_profile_menu() which displays
        the ProfileMenuPanel modal dialog.
        
        🆕 v3.5.0: Plays UI_BUTTON_CLICK sound before action.
        
        Args:
            event: wx.CommandEvent from button click or ENTER key
        
        Version:
            v3.1.0 Phase 10.4
            v3.5.0: Added audio feedback
        """
        # ✨ NUOVO v3.5.0: Play button click sound
        if self.audio_manager:
            from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
            self.audio_manager.play_event(AudioEvent(
                event_type=AudioEventType.UI_BUTTON_CLICK
            ))
        
        if self.controller and hasattr(self.controller, 'show_profile_menu'):
            self.controller.show_profile_menu()
    
    def on_options_click(self, event: wx.CommandEvent) -> None:
        """Handle "Opzioni di gioco" button click.
        
        Delegates to controller.show_options() which should display
        the options configuration dialog or view.
        
        🆕 v3.5.0: Plays UI_BUTTON_CLICK sound before action.
        
        Args:
            event: wx.CommandEvent from button click or ENTER key
        
        Note:
            Controller is responsible for showing options dialog.
            wxPython button events are wx.CommandEvent, not wx.ButtonEvent.
        """
        # ✨ NUOVO v3.5.0: Play button click sound
        if self.audio_manager:
            from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
            self.audio_manager.play_event(AudioEvent(
                event_type=AudioEventType.UI_BUTTON_CLICK
            ))
        
        if self.controller:
            self.controller.show_options()
    
    def on_exit_click(self, event: wx.CommandEvent) -> None:
        """Handle "Esci dal gioco" button click.
        
        Delegates to controller.show_exit_dialog() which should show
        a confirmation dialog before exiting the application.
        
        🆕 v3.5.0: Plays UI_BUTTON_CLICK sound before action.
        
        Args:
            event: wx.CommandEvent from button click or ENTER key
        
        Note:
            Controller is responsible for confirmation dialog and exit logic.
            wxPython button events are wx.CommandEvent, not wx.ButtonEvent.
        """
        # ✨ NUOVO v3.5.0: Play button click sound
        if self.audio_manager:
            from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
            self.audio_manager.play_event(AudioEvent(
                event_type=AudioEventType.UI_BUTTON_CLICK
            ))
        
        if self.controller:
            self.controller.show_exit_dialog()
    
    def on_key_down(self, event: wx.KeyEvent) -> None:
        """Handle keyboard events in menu panel.
        
        ESC in menu → show exit confirmation dialog.
        Other keys → propagate to parent.
        
        Args:
            event: wx.KeyEvent from keyboard
        
        Pattern:
            Similar to GameplayPanel ESC handling, but calls show_exit_dialog
            instead of show_abandon_game_dialog.
        """
        key_code = event.GetKeyCode()
        
        # ESC: Show exit confirmation
        if key_code == wx.WXK_ESCAPE:
            if self.controller:
                self.controller.show_exit_dialog()
            return
        
        # Other keys: propagate
        event.Skip()


# Module-level documentation
__all__ = ['MenuPanel']
