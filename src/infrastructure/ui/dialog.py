"""Virtual dialog box for confirmation prompts.

Provides accessible dialog boxes for audiogame interface with:
- Keyboard navigation (arrows + ENTER/ESC)
- Button focus management
- Single-key shortcuts
- TTS announcements
- Configurable callbacks

Designed for blind users with screen reader feedback.
"""

import pygame
from typing import List, Callable, Optional
from src.infrastructure.accessibility.screen_reader import ScreenReader


class VirtualDialogBox:
    """Virtual dialog box with keyboard navigation and TTS.
    
    Displays a message with multiple buttons (typically 2: Yes/No or OK/Cancel).
    User navigates with arrow keys and confirms with ENTER.
    All interactions are announced via TTS for accessibility.
    
    Attributes:
        message: Dialog message text
        buttons: List of button labels (e.g., ["Sì", "No"])
        default_button: Index of initially focused button (0-based)
        on_confirm: Callback when first button confirmed
        on_cancel: Callback when other buttons confirmed or ESC pressed
        screen_reader: ScreenReader instance for TTS
        is_open: Whether dialog is currently active
        current_button: Index of currently focused button
    
    Example:
        >>> dialog = VirtualDialogBox(
        ...     message="Vuoi uscire?",
        ...     buttons=["OK", "Annulla"],
        ...     default_button=0,
        ...     on_confirm=quit_app,
        ...     on_cancel=stay_in_menu,
        ...     screen_reader=sr
        ... )
        >>> dialog.open()
        >>> # User navigates with ↑↓←→, confirms with ENTER
    """
    
    def __init__(
        self,
        message: str,
        buttons: List[str],
        default_button: int = 0,
        on_confirm: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None,
        screen_reader: Optional[ScreenReader] = None
    ):
        """Initialize dialog box.
        
        Args:
            message: Dialog message to announce
            buttons: List of button labels (minimum 2)
            default_button: Index of button with initial focus
            on_confirm: Callback when first button (index 0) selected
            on_cancel: Callback when other buttons selected or ESC pressed
            screen_reader: ScreenReader for TTS announcements
        
        Raises:
            ValueError: If buttons list has less than 2 items
            ValueError: If default_button out of range
        """
        if len(buttons) < 2:
            raise ValueError("Dialog must have at least 2 buttons")
        
        if not (0 <= default_button < len(buttons)):
            raise ValueError(f"default_button must be 0-{len(buttons)-1}")
        
        self.message = message
        self.buttons = buttons
        self.default_button = default_button
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.screen_reader = screen_reader
        
        # State
        self._is_open = False
        self.current_button = default_button
    
    @property
    def is_open(self) -> bool:
        """Check if dialog is currently open.
        
        Returns:
            True if dialog is active and accepting input
        """
        return self._is_open
    
    def open(self) -> None:
        """Open dialog and announce message + focused button.
        
        Announces:
        1. Dialog message
        2. Currently focused button label
        
        Sets is_open to True and enables keyboard handling.
        """
        self._is_open = True
        self.current_button = self.default_button
        
        # Announce message + current button
        announcement = f"{self.message}\n{self.buttons[self.current_button]}."
        self._announce(announcement, interrupt=True)
    
    def close(self) -> None:
        """Close dialog and disable keyboard handling.
        
        Sets is_open to False. No TTS announcement.
        """
        self._is_open = False
    
    def handle_keyboard_events(self, event: pygame.event.Event) -> None:
        """Handle keyboard input for dialog navigation.
        
        Supported keys:
        - Arrow keys (↑↓←→): Navigate between buttons
        - ENTER/SPACE: Confirm current button
        - ESC: Cancel (calls on_cancel)
        - S/N/O/A: Shortcuts for specific buttons
        
        Args:
            event: Pygame keyboard event to process
        """
        if not self._is_open:
            return
        
        if event.type != pygame.KEYDOWN:
            return
        
        # Navigation keys
        if event.key in (pygame.K_RIGHT, pygame.K_DOWN):
            msg = self.navigate_next()
            self._announce(msg, interrupt=True)
        
        elif event.key in (pygame.K_LEFT, pygame.K_UP):
            msg = self.navigate_prev()
            self._announce(msg, interrupt=True)
        
        # Confirmation keys
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.confirm_selection()
        
        # Cancel key
        elif event.key == pygame.K_ESCAPE:
            self._execute_cancel()
        
        # Shortcut keys (case-insensitive)
        elif event.key == pygame.K_s:
            self._shortcut_select("sì")
        
        elif event.key == pygame.K_n:
            self._shortcut_select("no")
        
        elif event.key == pygame.K_o:
            self._shortcut_select("ok")
        
        elif event.key == pygame.K_a:
            self._shortcut_select("annulla")
    
    def navigate_next(self) -> str:
        """Move focus to next button (with wrap-around).
        
        Returns:
            Label of newly focused button
        """
        self.current_button = (self.current_button + 1) % len(self.buttons)
        return f"{self.buttons[self.current_button]}."
    
    def navigate_prev(self) -> str:
        """Move focus to previous button (with wrap-around).
        
        Returns:
            Label of newly focused button
        """
        self.current_button = (self.current_button - 1) % len(self.buttons)
        return f"{self.buttons[self.current_button]}."
    
    def confirm_selection(self) -> None:
        """Confirm currently focused button.
        
        Executes:
        - on_confirm if first button (index 0) selected
        - on_cancel for all other buttons
        
        Closes dialog after executing callback.
        """
        if self.current_button == 0:
            # First button = confirm action
            self._execute_confirm()
        else:
            # Other buttons = cancel action
            self._execute_cancel()
    
    def _shortcut_select(self, target_label: str) -> None:
        """Auto-select button matching target label (case-insensitive).
        
        Args:
            target_label: Button label to search for (e.g., "sì", "ok")
        """
        # Search for matching button
        for idx, button in enumerate(self.buttons):
            if button.lower() == target_label.lower():
                self.current_button = idx
                self.confirm_selection()
                return
        
        # No match found - ignore keypress
    
    def _execute_confirm(self) -> None:
        """Execute confirm callback and close dialog."""
        self.close()
        if self.on_confirm:
            self.on_confirm()
    
    def _execute_cancel(self) -> None:
        """Execute cancel callback and close dialog."""
        self.close()
        if self.on_cancel:
            self.on_cancel()
    
    def _announce(self, text: str, interrupt: bool = True) -> None:
        """Announce text via TTS.
        
        Args:
            text: Text to speak
            interrupt: Whether to interrupt current speech
        """
        if self.screen_reader:
            self.screen_reader.tts.speak(text, interrupt=interrupt)
            pygame.time.wait(80)  # Short pause for clarity
