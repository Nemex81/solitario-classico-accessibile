"""Options window controller for virtual modal dialog.

Manages all options window logic including:
- Navigation (arrows, numbers)
- Modifications (toggle/cycle settings)
- State management (CLOSED/OPEN_CLEAN/OPEN_DIRTY)
- Save/discard confirmation
- Input routing and validation

Architecture: Application Layer (Clean Architecture)
Depends on: Domain (GameSettings), Presentation (OptionsFormatter)
"""

from typing import Dict, Optional
from src.domain.services.game_settings import GameSettings
from src.presentation.options_formatter import OptionsFormatter


class OptionsWindowController:
    """Controller for virtual options window.
    
    Manages modal window state and user interactions.
    Uses HYBRID navigation (arrows + numbers) with accessibility focus.
    
    States:
    - CLOSED: Window not active (gameplay normal)
    - OPEN_CLEAN: Window open, no modifications
    - OPEN_DIRTY: Window open, modifications made (requires confirmation)
    
    Attributes:
        settings: Reference to GameSettings (domain service)
        cursor_position: Current option index (0-4)
        is_open: Window state flag
        state: Current state ("CLOSED"/"OPEN_CLEAN"/"OPEN_DIRTY")
        original_settings: Snapshot of settings at window open
    """
    
    def __init__(self, settings: GameSettings):
        """Initialize options controller.
        
        Args:
            settings: Game settings service (domain layer)
        """
        self.settings = settings
        self.cursor_position = 0  # Current option (0-4)
        self.is_open = False
        self.state = "CLOSED"
        
        # Snapshot for change tracking
        self.original_settings: Dict[str, any] = {}
    
    # ========================================
    # WINDOW LIFECYCLE
    # ========================================
    
    def open_window(self) -> str:
        """Open options window and save settings snapshot.
        
        Returns:
            TTS message for window opening
        
        State transition: CLOSED -> OPEN_CLEAN
        """
        self.is_open = True
        self.state = "OPEN_CLEAN"
        self.cursor_position = 0
        
        # Save snapshot for change tracking
        self._save_snapshot()
        
        # Get first option current value
        deck_type = self.settings.get_deck_type_display()
        
        return OptionsFormatter.format_open_message(deck_type)
    
    def close_window(self) -> str:
        """Close window with confirmation if modifications present.
        
        Returns:
            TTS message (direct close or dialog prompt)
        
        State transitions:
        - OPEN_CLEAN -> CLOSED (direct)
        - OPEN_DIRTY -> Show save dialog (stays OPEN_DIRTY until confirmed)
        """
        if self.state == "OPEN_DIRTY":
            # Show confirmation dialog
            return OptionsFormatter.format_save_dialog()
        else:
            # No changes, close directly
            self._reset_state()
            return OptionsFormatter.format_close_message()
    
    def save_and_close(self) -> str:
        """Save modifications and close window.
        
        Returns:
            TTS confirmation message
        
        State transition: OPEN_DIRTY -> CLOSED
        """
        # Modifications already applied live, just update snapshot
        self._save_snapshot()
        self._reset_state()
        return OptionsFormatter.format_save_confirmed()
    
    def discard_and_close(self) -> str:
        """Discard modifications and close window.
        
        Returns:
            TTS confirmation message
        
        State transition: OPEN_DIRTY -> CLOSED
        """
        # Restore original settings
        self._restore_snapshot()
        self._reset_state()
        return OptionsFormatter.format_save_discarded()
    
    def cancel_close(self) -> str:
        """Cancel close operation (stay in window).
        
        Returns:
            TTS message
        
        State: Stays OPEN_DIRTY
        """
        return OptionsFormatter.format_save_cancelled()
    
    # ========================================
    # NAVIGATION
    # ========================================
    
    def navigate_up(self) -> str:
        """Navigate to previous option (wraparound).
        
        Returns:
            TTS message with option name, value, and hint
        """
        self.cursor_position = (self.cursor_position - 1) % 5
        return self._format_current_option(include_hint=True)
    
    def navigate_down(self) -> str:
        """Navigate to next option (wraparound).
        
        Returns:
            TTS message with option name, value, and hint
        """
        self.cursor_position = (self.cursor_position + 1) % 5
        return self._format_current_option(include_hint=True)
    
    def jump_to_option(self, index: int) -> str:
        """Jump directly to option by number (1-5).
        
        Args:
            index: Option index (0-4)
        
        Returns:
            TTS message (concise, no hint)
        
        Example:
            >>> controller.jump_to_option(2)
            "3 di 5: Timer, Disattivato."
        """
        if 0 <= index <= 4:
            self.cursor_position = index
            return self._format_current_option(include_hint=False)
        else:
            return "Opzione non valida."
    
    # ========================================
    # MODIFICATIONS
    # ========================================
    
    def modify_current_option(self) -> str:
        """Modify currently selected option (toggle/cycle).
        
        Returns:
            TTS confirmation message or error
        
        State transition: OPEN_CLEAN -> OPEN_DIRTY (on first modification)
        """
        # Block if game running
        if self.settings.game_state.is_running:
            return OptionsFormatter.format_blocked_during_game()
        
        # Route to appropriate handler
        handlers = [
            self._modify_deck_type,      # 0: Tipo Mazzo
            self._modify_difficulty,     # 1: Difficoltà
            self._cycle_timer_preset,    # 2: Timer (INVIO = cycle presets)
            self._modify_shuffle_mode,   # 3: Riciclo Scarti
            self._modify_command_hints,  # 4: Suggerimenti Comandi (v1.5.0)
        ]
        
        msg = handlers[self.cursor_position]()
        
        # Mark as dirty on successful modification
        msg_lower = msg.lower()
        if ("impostato" in msg_lower or "impostata" in msg_lower or 
            "disattivat" in msg_lower or "attivat" in msg_lower):
            self.state = "OPEN_DIRTY"
        
        return msg
    
    def increment_timer(self) -> str:
        """Increment timer by 5 minutes (tasto +).
        
        Returns:
            TTS message or error
        
        Only works if cursor_position == 2 (Timer selected)
        """
        if self.cursor_position != 2:
            return OptionsFormatter.format_timer_error()
        
        if self.settings.game_state.is_running:
            return OptionsFormatter.format_blocked_during_game()
        
        success, msg = self.settings.increment_timer_validated()
        
        if success and "impostato" in msg:
            self.state = "OPEN_DIRTY"
        
        return msg
    
    def decrement_timer(self) -> str:
        """Decrement timer by 5 minutes (tasto -).
        
        Returns:
            TTS message or error
        
        Only works if cursor_position == 2 (Timer selected)
        """
        if self.cursor_position != 2:
            return OptionsFormatter.format_timer_error()
        
        if self.settings.game_state.is_running:
            return OptionsFormatter.format_blocked_during_game()
        
        success, msg = self.settings.decrement_timer_validated()
        
        if success and ("impostato" in msg or "disattivato" in msg):
            self.state = "OPEN_DIRTY"
        
        return msg
    
    def toggle_timer(self) -> str:
        """Toggle timer ON(5min)/OFF (tasto T).
        
        Returns:
            TTS message or error
        
        Only works if cursor_position == 2 (Timer selected)
        """
        if self.cursor_position != 2:
            return OptionsFormatter.format_timer_error()
        
        if self.settings.game_state.is_running:
            return OptionsFormatter.format_blocked_during_game()
        
        success, msg = self.settings.toggle_timer()
        
        if success:
            self.state = "OPEN_DIRTY"
        
        return msg
    
    # ========================================
    # INFORMATION
    # ========================================
    
    def read_all_settings(self) -> str:
        """Read complete settings recap (tasto I).
        
        Returns:
            TTS message with all current settings
        """
        settings_dict = {
            "Tipo mazzo": self.settings.get_deck_type_display(),
            "Difficoltà": self.settings.get_difficulty_display(),
            "Timer": self.settings.get_timer_display(),
            "Modalità riciclo scarti": self.settings.get_shuffle_mode_display(),
            "Suggerimenti comandi": self.settings.get_command_hints_display()
        }
        
        return OptionsFormatter.format_all_settings(settings_dict)
    
    def show_help(self) -> str:
        """Show complete help text (tasto H).
        
        Returns:
            TTS message with all commands
        """
        return OptionsFormatter.format_help_text()
    
    # ========================================
    # INTERNAL HELPERS
    # ========================================
    
    def _format_current_option(self, include_hint: bool) -> str:
        """Format current option for TTS.
        
        Args:
            include_hint: Add navigation hint
        
        Returns:
            Formatted TTS message
        """
        option_name = OptionsFormatter.OPTION_NAMES[self.cursor_position]
        
        # Get current value
        value_getters = [
            self.settings.get_deck_type_display,
            self.settings.get_difficulty_display,
            self.settings.get_timer_display,
            self.settings.get_shuffle_mode_display,
            self.settings.get_command_hints_display  # v1.5.0
        ]
        
        value = value_getters[self.cursor_position]()
        
        return OptionsFormatter.format_option_item(
            self.cursor_position,
            option_name,
            value,
            include_hint
        )
    
    def _modify_deck_type(self) -> str:
        """Toggle deck type (French <-> Neapolitan)."""
        success, msg = self.settings.toggle_deck_type()
        return msg
    
    def _modify_difficulty(self) -> str:
        """Cycle difficulty (1 -> 2 -> 3 -> 1)."""
        success, msg = self.settings.cycle_difficulty()
        return msg
    
    def _cycle_timer_preset(self) -> str:
        """Cycle timer through presets (OFF -> 10 -> 20 -> 30 -> OFF).
        
        INVIO on Timer option cycles through common presets.
        For fine control, use +/- keys.
        """
        current = self.settings.max_time_game
        
        # Preset cycle: OFF -> 10 -> 20 -> 30 -> OFF
        if current <= 0:
            new_value = 600  # 10 minutes
        elif current == 600:
            new_value = 1200  # 20 minutes
        elif current == 1200:
            new_value = 1800  # 30 minutes
        else:
            new_value = -1  # OFF
        
        self.settings.max_time_game = new_value
        display = self.settings.get_timer_display()
        
        return OptionsFormatter.format_option_changed("Timer", display)
    
    def _modify_shuffle_mode(self) -> str:
        """Toggle shuffle mode (Inversione <-> Mescolata)."""
        success, msg = self.settings.toggle_shuffle_mode()
        return msg
    
    def _modify_command_hints(self) -> str:
        """Toggle command hints (Attivi <-> Disattivati) (v1.5.0)."""
        success, msg = self.settings.toggle_command_hints()
        return msg
    
    # ========================================
    # STATE MANAGEMENT
    # ========================================
    
    def _save_snapshot(self) -> None:
        """Save current settings snapshot for change tracking."""
        self.original_settings = {
            "deck_type": self.settings.deck_type,
            "difficulty": self.settings.difficulty_level,
            "timer": self.settings.max_time_game,
            "shuffle": self.settings.shuffle_discards,
            "command_hints": self.settings.command_hints_enabled  # v1.5.0
        }
    
    def _restore_snapshot(self) -> None:
        """Restore original settings (discard changes)."""
        self.settings.deck_type = self.original_settings["deck_type"]
        self.settings.difficulty_level = self.original_settings["difficulty"]
        self.settings.max_time_game = self.original_settings["timer"]
        self.settings.shuffle_discards = self.original_settings["shuffle"]
        self.settings.command_hints_enabled = self.original_settings["command_hints"]  # v1.5.0
    
    def _reset_state(self) -> None:
        """Reset controller state (close window)."""
        self.is_open = False
        self.state = "CLOSED"
        self.cursor_position = 0
        self.original_settings.clear()
