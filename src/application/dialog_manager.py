"""Centralized dialog management for application-wide wxPython dialogs.

This module provides a high-level manager for common confirmation dialogs
used throughout the application (abandon game, new game, exit, options save).

NEW in v1.6.1: Replaces VirtualDialogBox (TTS-only) with native wxPython
dialogs for improved accessibility and user experience.

The manager wraps WxDialogProvider with semantic methods that include
Italian-localized messages and sensible defaults. Provides graceful
degradation if wxPython is not available.
"""

from typing import Optional

from src.infrastructure.ui.dialog_provider import DialogProvider


class SolitarioDialogManager:
    """Centralized manager for application-wide confirmation dialogs.
    
    Provides semantic methods for common dialog scenarios:
    - Abandon current game
    - Start new game (with active game confirmation)
    - Return to main menu
    - Exit application
    - Save modified options
    
    Uses native wxPython dialogs via WxDialogProvider for accessibility.
    Gracefully degrades if wxPython unavailable (returns False).
    
    Attributes:
        dialogs: Optional DialogProvider instance (WxDialogProvider or None)
        
    Example:
        >>> manager = SolitarioDialogManager()
        >>> if manager.is_available:
        ...     if manager.show_abandon_game_prompt():
        ...         # User confirmed, abandon game
        ...         abandon_current_game()
    """
    
    def __init__(self, dialog_provider: Optional[DialogProvider] = None):
        """Initialize dialog manager with optional provider.
        
        Args:
            dialog_provider: Optional DialogProvider instance.
                If None, attempts to create WxDialogProvider.
                If ImportError (wxPython unavailable), sets to None.
        """
        if dialog_provider is not None:
            self.dialogs = dialog_provider
        else:
            # Try to create WxDialogProvider, handle ImportError gracefully
            try:
                from src.infrastructure.ui.wx_dialog_provider import WxDialogProvider
                self.dialogs = WxDialogProvider()
            except ImportError:
                # wxPython not available, graceful degradation
                self.dialogs = None
    
    @property
    def is_available(self) -> bool:
        """Check if native dialogs are available.
        
        Returns:
            True if wxPython dialogs available, False otherwise
            
        Example:
            >>> manager = SolitarioDialogManager()
            >>> if manager.is_available:
            ...     print("Native dialogs enabled")
        """
        return self.dialogs is not None
    
    def show_abandon_game_prompt(self) -> bool:
        """Show confirmation dialog for abandoning current game.
        
        Asks user if they want to abandon the game and return to menu.
        
        Returns:
            True if user confirms (Yes), False if declines (No) or unavailable
            
        Italian message:
            Title: "Abbandono Partita"
            Message: "Vuoi abbandonare la partita e tornare al menu di gioco?"
            
        Example:
            >>> if manager.show_abandon_game_prompt():
            ...     abandon_and_return_to_menu()
        """
        if not self.is_available:
            return False
        
        return self.dialogs.show_yes_no(
            "Vuoi abbandonare la partita e tornare al menu di gioco?",
            "Abbandono Partita"
        )
    
    def show_new_game_prompt(self) -> bool:
        """Show confirmation dialog for starting new game over existing one.
        
        Asks user if they want to abandon current game and start new one.
        
        Returns:
            True if user confirms (Yes), False if declines (No) or unavailable
            
        Italian message:
            Title: "Nuova Partita"
            Message: "Una partita è già in corso. Vuoi abbandonarla e avviarne una nuova?"
            
        Example:
            >>> if manager.show_new_game_prompt():
            ...     start_new_game()
        """
        if not self.is_available:
            return False
        
        return self.dialogs.show_yes_no(
            "Una partita è già in corso. Vuoi abbandonarla e avviarne una nuova?",
            "Nuova Partita"
        )
    
    def show_return_to_main_prompt(self) -> bool:
        """Show confirmation dialog for returning to main menu.
        
        Asks user if they want to return to main menu from submenu.
        
        Returns:
            True if user confirms (Yes), False if declines (No) or unavailable
            
        Italian message:
            Title: "Torna al Menu"
            Message: "Vuoi tornare al menu principale?"
            
        Example:
            >>> if manager.show_return_to_main_prompt():
            ...     return_to_main_menu()
        """
        if not self.is_available:
            return False
        
        return self.dialogs.show_yes_no(
            "Vuoi tornare al menu principale?",
            "Torna al Menu"
        )
    
    def show_exit_app_prompt(self) -> bool:
        """Show confirmation dialog for exiting application.
        
        Asks user if they want to exit the application.
        Default is NO for safety (prevent accidental exits).
        
        Returns:
            True if user confirms (Yes), False if declines (No) or unavailable
            
        Italian message:
            Title: "Chiusura Applicazione"
            Message: "Vuoi uscire dall'applicazione?"
            
        Note:
            This is a critical operation, so default is NO to prevent
            accidental application closure.
            
        Example:
            >>> if manager.show_exit_app_prompt():
            ...     quit_application()
        """
        if not self.is_available:
            return False
        
        return self.dialogs.show_yes_no(
            "Vuoi uscire dall'applicazione?",
            "Chiusura Applicazione"
        )
    
    def show_options_save_prompt(self) -> Optional[bool]:
        """Show confirmation dialog for saving modified options.
        
        Asks user if they want to save changes before closing options.
        
        Returns:
            True if user confirms save (Yes)
            False if user wants to discard (No)
            None if wxPython unavailable (caller should use fallback)
            
        Italian message:
            Title: "Modifiche Non Salvate"
            Message: "Hai modifiche non salvate. Vuoi salvare le modifiche prima di chiudere?"
            
        Note:
            With current WxDialogProvider API, ESC returns False (No).
            Future enhancement: show_yes_no_cancel() for explicit cancel.
            
        Example:
            >>> result = manager.show_options_save_prompt()
            >>> if result is True:
            ...     save_options()
            >>> elif result is False:
            ...     discard_changes()
            >>> else:  # None
            ...     use_tts_fallback()
        """
        if not self.is_available:
            return None
        
        return self.dialogs.show_yes_no(
            "Hai modifiche non salvate. Vuoi salvare le modifiche prima di chiudere?",
            "Modifiche Non Salvate"
        )
    
    def show_alert(self, title: str, message: str) -> None:
        """Show informational alert dialog.
        
        Displays a simple alert with OK button.
        
        Args:
            title: Dialog title
            message: Alert message content
            
        Example:
            >>> manager.show_alert(
            ...     "Operazione Completata",
            ...     "Le impostazioni sono state salvate con successo."
            ... )
        """
        if not self.is_available:
            return
        
        self.dialogs.show_alert(message, title)
