"""Centralized dialog management for application-wide wxPython dialogs.

This module provides a high-level manager for common confirmation dialogs
used throughout the application (abandon game, new game, exit, options save).

NEW in v1.6.1: Replaces VirtualDialogBox (TTS-only) with native wxPython
dialogs for improved accessibility and user experience.

The manager wraps WxDialogProvider with semantic methods that include
Italian-localized messages and sensible defaults. Provides graceful
degradation if wxPython is not available.
"""

from typing import Optional, Callable

from src.infrastructure.ui.dialog_provider import DialogProvider
from src.infrastructure.logging import game_logger as log


def _make_logged_callback(title: str, callback: Callable[[bool], None]) -> Callable[[bool], None]:
    """Wrap a dialog callback to log dialog_shown and dialog_closed events."""
    log.dialog_shown("yes_no", title)
    
    def _wrapped(result: bool) -> None:
        log.dialog_closed("yes_no", "yes" if result else "no")
        callback(result)
    
    return _wrapped


class SolitarioDialogManager:
    """Centralized manager for application-wide confirmation dialogs.
    
    **v3.4.0**: riceve facoltativamente un AudioManager per riprodurre
    effetti sonori quando i dialoghi vengono mostrati o chiusi.
    
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
    
    def __init__(self, dialog_provider: Optional[DialogProvider] = None, audio_manager: Optional[object] = None):
        """Initialize dialog manager with optional provider and audio.
        
        Args:
            dialog_provider: Optional DialogProvider instance.
                If None, attempts to create WxDialogProvider.
                If ImportError (wxPython unavailable), sets to None.
            audio_manager: Optional AudioManager instance for effects.
        """
        self._audio = audio_manager
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
        """DEPRECATED: Use show_abandon_game_prompt_async().
        
        Synchronous API causes nested event loops.
        Maintained for backward compatibility, will be removed in v3.0.
        
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
        # audio on open
        if self._audio:
            try:
                from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
                self._audio.play_event(AudioEvent(event_type=AudioEventType.MIXER_OPENED))
            except Exception:
                pass
        result = self.dialogs.show_yes_no(
            "Vuoi abbandonare la partita e tornare al menu di gioco?",
            "Abbandono Partita"
        )
        # audio on close
        if self._audio:
            try:
                from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
                ev = AudioEventType.UI_SELECT if result else AudioEventType.UI_CANCEL
                self._audio.play_event(AudioEvent(event_type=ev))
            except Exception:
                pass
        return result
    
    def show_new_game_prompt(self) -> bool:
        """DEPRECATED: Use show_new_game_prompt_async().
        
        Synchronous API causes nested event loops.
        Maintained for backward compatibility, will be removed in v3.0.
        
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
        if self._audio:
            try:
                from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
                self._audio.play_event(AudioEvent(event_type=AudioEventType.MIXER_OPENED))
            except Exception:
                pass
        result = self.dialogs.show_yes_no(
            "Una partita è già in corso. Vuoi abbandonarla e avviarne una nuova?",
            "Nuova Partita"
        )
        if self._audio:
            try:
                from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
                ev = AudioEventType.UI_SELECT if result else AudioEventType.UI_CANCEL
                self._audio.play_event(AudioEvent(event_type=ev))
            except Exception:
                pass
        return result
    
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
        if self._audio:
            try:
                from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
                self._audio.play_event(AudioEvent(event_type=AudioEventType.MIXER_OPENED))
            except Exception:
                pass
        result = self.dialogs.show_yes_no(
            "Vuoi tornare al menu principale?",
            "Torna al Menu"
        )
        if self._audio:
            try:
                from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
                ev = AudioEventType.UI_SELECT if result else AudioEventType.UI_CANCEL
                self._audio.play_event(AudioEvent(event_type=ev))
            except Exception:
                pass
        return result
    
    def show_exit_app_prompt(self) -> bool:
        """DEPRECATED: Use show_exit_app_prompt_async().
        
        Synchronous API causes nested event loops.
        Maintained for backward compatibility, will be removed in v3.0.
        
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
        if self._audio:
            try:
                from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
                self._audio.play_event(AudioEvent(event_type=AudioEventType.MIXER_OPENED))
            except Exception:
                pass
        result = self.dialogs.show_yes_no(
            "Vuoi uscire dall'applicazione?",
            "Chiusura Applicazione"
        )
        if self._audio:
            try:
                from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
                ev = AudioEventType.UI_SELECT if result else AudioEventType.UI_CANCEL
                self._audio.play_event(AudioEvent(event_type=ev))
            except Exception:
                pass
        return result
    
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
        if self._audio:
            try:
                from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
                self._audio.play_event(AudioEvent(event_type=AudioEventType.MIXER_OPENED))
            except Exception:
                pass
        result = self.dialogs.show_yes_no(
            "Hai modifiche non salvate. Vuoi salvare le modifiche prima di chiudere?",
            "Modifiche Non Salvate"
        )
        if self._audio:
            try:
                from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
                ev = AudioEventType.UI_SELECT if result else AudioEventType.UI_CANCEL
                self._audio.play_event(AudioEvent(event_type=ev))
            except Exception:
                pass
        return result
    
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
        # audio open
        if self._audio:
            try:
                from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
                self._audio.play_event(AudioEvent(event_type=AudioEventType.MIXER_OPENED))
            except Exception:
                pass
        self.dialogs.show_alert(message, title)
        # no close event needed for simple OK dialog
    
    def show_abandon_game_prompt_async(self, callback: Callable[[bool], None]) -> None:
        """Show abandon game confirmation dialog (non-blocking).
        
        Args:
            callback: Function called with result (True=abandon, False=continue)
        
        Example:
            >>> def on_result(confirmed):
            ...     if confirmed:
            ...         self._safe_abandon_to_menu()
            >>> dialog_manager.show_abandon_game_prompt_async(on_result)
        
        Version:
            v2.2: Added async API
        """
        if not self.is_available:
            # Fallback TTS (no callback, announce only)
            # Note: TTS needs to be injected if we want to use it here
            # For now, just silently fail (no dialogs available)
            return
        # audio open event
        if self._audio:
            try:
                from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
                self._audio.play_event(AudioEvent(event_type=AudioEventType.MIXER_OPENED))
            except Exception:
                pass
        # wrap callback to emit close event before forwarding
        def _with_audio(result: bool) -> None:
            if self._audio:
                try:
                    from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
                    ev = AudioEventType.UI_SELECT if result else AudioEventType.UI_CANCEL
                    self._audio.play_event(AudioEvent(event_type=ev))
                except Exception:
                    pass
            callback(result)
        self.dialogs.show_yes_no_async(
            title="Abbandono Partita",
            message="Vuoi abbandonare la partita e tornare al menu di gioco?",
            callback=_make_logged_callback("Abbandono Partita", _with_audio)
        )
    
    def show_rematch_prompt_async(self, callback: Callable[[bool], None]) -> None:
        """Show rematch confirmation dialog (non-blocking).
        
        Asks user if they want to play another game after completing current one.
        
        Args:
            callback: Function called with result (True=rematch, False=return to menu)
        
        Italian message:
            Title: "Rivincita?"
            Message: "Vuoi giocare ancora?"
        
        Flow:
            1. Dialog.Show() called (non-blocking)
            2. User responds YES/NO
            3. Dialog closes
            4. [wxPython event loop processes callback]
            5. callback(wants_rematch) invoked (deferred context)
            6. Caller handles rematch logic safely
        
        Note:
            This is the async version of the deprecated show_yes_no() call
            used in GameEngine.end_game(). Provides consistent async pattern
            with abandon_game, new_game, and exit_app prompts.
        
        Example:
            >>> def on_result(wants_rematch):
            ...     if wants_rematch:
            ...         self.start_gameplay()
            ...     else:
            ...         self._safe_return_to_main_menu()
            >>> dialog_manager.show_rematch_prompt_async(on_result)
        
        Version:
            v2.5.0: Added for Bug #68 async refactoring
        """
        if not self.is_available:
            # Fallback: No dialogs available, default to NO rematch
            # Invoke callback with False to maintain async signature
            callback(False)
            return
        # AUDIO open
        if self._audio:
            try:
                from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
                self._audio.play_event(AudioEvent(event_type=AudioEventType.MIXER_OPENED))
            except Exception:
                pass

        def _audio_wrapped2(confirmed: bool) -> None:
            if self._audio:
                try:
                    from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
                    ev = AudioEventType.UI_SELECT if confirmed else AudioEventType.UI_CANCEL
                    self._audio.play_event(AudioEvent(event_type=ev))
                except Exception:
                    pass
            callback(confirmed)

        self.dialogs.show_yes_no_async(
            title="Rivincita?",
            message="Vuoi giocare ancora?",
            callback=_make_logged_callback("Rivincita?", _audio_wrapped2)
        )
    
    def show_new_game_prompt_async(self, callback: Callable[[bool], None]) -> None:
        """Show new game confirmation dialog (non-blocking).
        
        Args:
            callback: Function called with result (True=new game, False=cancel)
        
        Example:
            >>> def on_result(confirmed):
            ...     if confirmed:
            ...         self.engine.reset_game()
            ...         self.engine.new_game()
            >>> dialog_manager.show_new_game_prompt_async(on_result)
        
        Version:
            v2.2: Added async API
        """
        if not self.is_available:
            return
        
        self.dialogs.show_yes_no_async(
            title="Nuova Partita",
            message="Una partita è già in corso. Vuoi abbandonarla e avviarne una nuova?",
            callback=_make_logged_callback("Nuova Partita", callback)
        )
    
    def show_exit_app_prompt_async(self, callback: Callable[[bool], None]) -> None:
        """Show exit confirmation dialog (non-blocking).
        
        Args:
            callback: Function called with result (True=exit, False=cancel)
        
        Example:
            >>> def on_result(confirmed):
            ...     if confirmed:
            ...         sys.exit(0)
            >>> dialog_manager.show_exit_app_prompt_async(on_result)
        
        Version:
            v2.2: Added async API
        """
        if not self.is_available:
            return
        
        self.dialogs.show_yes_no_async(
            title="Chiusura Applicazione",
            message="Vuoi uscire dall'applicazione?",
            callback=_make_logged_callback("Chiusura Applicazione", callback)
        )
