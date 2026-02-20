"""Options window controller for virtual modal dialog.

Manages all options window logic including:
- Navigation (arrows, numbers)
- Modifications (toggle/cycle settings)
- State management (CLOSED/OPEN_CLEAN/OPEN_DIRTY)
- Save/discard confirmation
- Input routing and validation

NEW v1.6.1: Integrated with SolitarioDialogManager for native wxDialog prompts.
NEW v2.4.0: Difficulty preset lock enforcement

Architecture: Application Layer (Clean Architecture)
Depends on: Domain (GameSettings, DifficultyPreset), Presentation (OptionsFormatter)
"""

from typing import Dict, Optional, TYPE_CHECKING
from src.domain.services.game_settings import GameSettings
from src.domain.models.difficulty_preset import DifficultyPreset
from src.presentation.options_formatter import OptionsFormatter
from src.infrastructure.logging import game_logger as log

if TYPE_CHECKING:
    from src.application.dialog_manager import SolitarioDialogManager


class OptionsWindowController:
    """Controller for virtual options window.
    
    Manages modal window state and user interactions.
    Uses HYBRID navigation (arrows + numbers) with accessibility focus.
    
    NEW v1.6.1: Optionally uses native wxDialog for save confirmation.
    
    States:
    - CLOSED: Window not active (gameplay normal)
    - OPEN_CLEAN: Window open, no modifications
    - OPEN_DIRTY: Window open, modifications made (requires confirmation)
    
    Attributes:
        settings: Reference to GameSettings (domain service)
        dialog_manager: Optional SolitarioDialogManager for native dialogs (v1.6.1)
        cursor_position: Current option index (0-4)
        is_open: Window state flag
        state: Current state ("CLOSED"/"OPEN_CLEAN"/"OPEN_DIRTY")
        original_settings: Snapshot of settings at window open
    """
    
    def __init__(
        self, 
        settings: GameSettings,
        dialog_manager: Optional['SolitarioDialogManager'] = None
    ):
        """Initialize options controller.
        
        Args:
            settings: Game settings service (domain layer)
            dialog_manager: Optional dialog manager for native wxDialogs (v1.6.1)
        """
        self.settings = settings
        self.dialog_manager = dialog_manager
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
        
        NEW v1.6.1: Uses native wxDialog if dialog_manager available,
        otherwise falls back to TTS virtual prompt.
        
        Returns:
            TTS message (direct close, dialog result, or prompt for fallback)
        
        State transitions:
        - OPEN_CLEAN -> CLOSED (direct)
        - OPEN_DIRTY -> CLOSED (if saved/discarded via dialog)
        - OPEN_DIRTY -> OPEN_DIRTY (if cancelled or fallback mode)
        """
        if self.state == "OPEN_DIRTY":
            # NEW v1.6.1: Use wx dialog if available
            if self.dialog_manager and self.dialog_manager.is_available:
                result = self.dialog_manager.show_options_save_prompt()
                
                if result is True:
                    # User chose to save
                    self._save_snapshot()
                    self._reset_state()
                    return OptionsFormatter.format_save_confirmed()
                
                elif result is False:
                    # User chose to discard
                    self._restore_snapshot()
                    self._reset_state()
                    return OptionsFormatter.format_save_discarded()
                
                # result is None: Should not happen with current API
                # (ESC returns False). Treat as cancel.
                return OptionsFormatter.format_save_cancelled()
            
            else:
                # FALLBACK: TTS virtual prompt (backward compatible)
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
        self.cursor_position = (self.cursor_position - 1) % 9
        return self._format_current_option(include_hint=True)
    
    def navigate_down(self) -> str:
        """Navigate to next option (wraparound).
        
        Returns:
            TTS message with option name, value, and hint
        """
        self.cursor_position = (self.cursor_position + 1) % 9
        return self._format_current_option(include_hint=True)
    
    def jump_to_option(self, index: int) -> str:
        """Jump directly to option by number (1-8).
        
        Args:
            index: Option index (0-7)
        
        Returns:
            TTS message (concise, no hint)
        
        Example:
            >>> controller.jump_to_option(2)
            "3 di 9: Carte Pescate, 1 Carta."
        """
        if 0 <= index <= 8:
            self.cursor_position = index
            return self._format_current_option(include_hint=False)
        else:
            return "Opzione non valida."
    
    # ========================================
    # MODIFICATIONS
    # ========================================
    
    def modify_current_option(self) -> str:
        """Modify currently selected option (toggle/cycle).
        
        v2.4.0: Checks for difficulty preset locks before modification.
        
        Returns:
            TTS confirmation message, lock message, or error
        
        State transition: OPEN_CLEAN -> OPEN_DIRTY (on first modification)
        """
        # Block if game running
        if self.settings.game_state.is_running:
            return OptionsFormatter.format_blocked_during_game()
        
        # Check if option is locked (v2.4.0)
        # Exception: difficulty_level itself is never locked (cursor_position == 1)
        if self.cursor_position != 1 and self._is_current_option_locked():
            return self._get_lock_message()
        
        # Route to appropriate handler
        handlers = [
            self._modify_deck_type,      # 0: Tipo Mazzo
            self._modify_difficulty,     # 1: Difficoltà
            self._modify_draw_count,     # 2: Carte Pescate (NEW)
            self._cycle_timer_preset,    # 3: Timer (INVIO = cycle presets)
            self._modify_shuffle_mode,   # 4: Riciclo Scarti
            self._modify_command_hints,  # 5: Suggerimenti Comandi (v1.5.0)
            self._modify_scoring,        # 6: Sistema Punti (NEW)
            self._modify_timer_strict_mode,  # 7: Modalità Timer (v1.5.2.2)
            self._modify_score_warning_level,  # 8: Avvisi Soglie Punteggio (v2.6.1)
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
        
        Only works if cursor_position == 3 (Timer selected)
        """
        if self.cursor_position != 3:
            return OptionsFormatter.format_timer_error()
        
        if self.settings.game_state.is_running:
            return OptionsFormatter.format_blocked_during_game()
        
        old_value = self.settings.max_time_game
        success, msg = self.settings.increment_timer_validated()
        
        if success and "impostato" in msg:
            self.state = "OPEN_DIRTY"
            new_value = self.settings.max_time_game
            log.settings_changed("max_time_game", old_value, new_value)
        
        return msg
    
    def decrement_timer(self) -> str:
        """Decrement timer by 5 minutes (tasto -).
        
        Returns:
            TTS message or error
        
        Only works if cursor_position == 3 (Timer selected)
        """
        if self.cursor_position != 3:
            return OptionsFormatter.format_timer_error()
        
        if self.settings.game_state.is_running:
            return OptionsFormatter.format_blocked_during_game()
        
        old_value = self.settings.max_time_game
        success, msg = self.settings.decrement_timer_validated()
        
        if success and ("impostato" in msg or "disattivato" in msg):
            self.state = "OPEN_DIRTY"
            new_value = self.settings.max_time_game
            log.settings_changed("max_time_game", old_value, new_value)
        
        return msg
    
    def toggle_timer(self) -> str:
        """Toggle timer ON(5min)/OFF (tasto T).
        
        Returns:
            TTS message or error
        
        Only works if cursor_position == 3 (Timer selected)
        """
        if self.cursor_position != 3:
            return OptionsFormatter.format_timer_error()
        
        if self.settings.game_state.is_running:
            return OptionsFormatter.format_blocked_during_game()
        
        old_value = self.settings.max_time_game
        success, msg = self.settings.toggle_timer()
        
        if success:
            self.state = "OPEN_DIRTY"
            new_value = self.settings.max_time_game
            log.settings_changed("max_time_game", old_value, new_value)
        
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
            "Carte Pescate": self.settings.get_draw_count_display(),
            "Timer": self.settings.get_timer_display(),
            "Modalità riciclo scarti": self.settings.get_shuffle_mode_display(),
            "Suggerimenti comandi": self.settings.get_command_hints_display(),
            "Sistema Punti": self.settings.get_scoring_display(),
            "Modalità Timer": self.settings.get_timer_strict_mode_display(),
            "Avvisi Soglie Punteggio": self.settings.get_score_warning_level_display()
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
            self.settings.get_draw_count_display,       # NEW
            self.settings.get_timer_display,
            self.settings.get_shuffle_mode_display,
            self.settings.get_command_hints_display,    # v1.5.0
            self.settings.get_scoring_display,          # NEW
            self.settings.get_timer_strict_mode_display, # v1.5.2.2
            self.settings.get_score_warning_level_display # v2.6.1
        ]
        
        value = value_getters[self.cursor_position]()
        
        return OptionsFormatter.format_option_item(
            self.cursor_position,
            option_name,
            value,
            include_hint
        )
    
    # ========================================
    # LOCK ENFORCEMENT (v2.4.0)
    # ========================================
    
    def _is_current_option_locked(self) -> bool:
        """Check if current option is locked by difficulty preset.
        
        Returns:
            True if option is locked (cannot be modified), False otherwise
        
        Version: v2.4.0
        """
        # Map cursor position to option name
        option_map = {
            0: "deck_type",  # Never locked
            1: "difficulty_level",  # Never locked (always can cycle)
            2: "draw_count",
            3: "max_time_game",
            4: "shuffle_discards",
            5: "command_hints_enabled",
            6: "scoring_enabled",
            7: "timer_strict_mode",
            8: "score_warning_level",  # v2.6.1 - Never locked
        }
        
        option_name = option_map.get(self.cursor_position)
        if option_name is None:
            return False
        
        # Check if option is locked
        return self.settings.is_option_locked(option_name)
    
    def _get_lock_message(self) -> str:
        """Get TTS message for locked option attempt.
        
        Returns:
            Formatted message explaining option is locked
        
        Version: v2.4.0
        """
        # Get current preset info
        preset = self.settings.get_current_preset()
        
        # Map cursor position to option name (for message)
        option_names = {
            0: "Tipo Mazzo",
            1: "Difficoltà",
            2: "Carte Pescate",
            3: "Timer",
            4: "Riciclo Scarti",
            5: "Suggerimenti Comandi",
            6: "Sistema Punti",
            7: "Modalità Timer",
            8: "Avvisi Soglie Punteggio",
        }
        
        option_name = option_names.get(self.cursor_position, "Opzione")
        
        # Format lock message
        return (f"{option_name} bloccato da {preset.name}. "
                f"Cambia livello difficoltà per sbloccare questa opzione.")
    
    # ========================================
    # PRIVATE OPTION MODIFICATION HANDLERS
    # ========================================
    
    def _modify_deck_type(self) -> str:
        """Toggle deck type (French <-> Neapolitan)."""
        success, msg = self.settings.toggle_deck_type()
        return msg
    
    def _modify_difficulty(self) -> str:
        """Cycle difficulty (1 -> 2 -> 3 -> 4 -> 5 -> 1) with preset application."""
        old_value = self.settings.difficulty_level
        success, msg = self.settings.cycle_difficulty()
        
        if success:
            new_value = self.settings.difficulty_level
            log.settings_changed("difficulty_level", old_value, new_value)
            
            # v2.4.0: Get preset and apply values
            preset = self.settings.get_current_preset()
            
            # v2.4.1: CRITICAL FIX - Apply preset values to settings
            # This actually changes timer, draw_count, etc. to preset values
            preset.apply_to(self.settings)
            
            # Log preset application
            log.debug_state("preset_applied", {
                "preset_name": preset.name,
                "values_set": len(preset.preset_values),
                "options_locked": len(preset.get_locked_options())
            })
            
            # Log each locked option with its preset value
            for option_name in preset.get_locked_options():
                preset_value = preset.preset_values.get(option_name)
                log.debug_state("option_locked", {
                    "option": option_name,
                    "difficulty": new_value,
                    "preset_value": preset_value,
                    "locked": True
                })
            
            locked_count = len(preset.get_locked_options())
            
            # Use preset formatter instead of generic message
            return OptionsFormatter.format_preset_applied(
                level=new_value,
                preset_name=preset.name,
                locked_count=locked_count
            )
        
        return msg  # Fallback for errors
    
    def _cycle_timer_preset(self) -> str:
        """Cycle timer with +5min increments and wrap-around (v1.5.1).
        
        Behavior:
        - OFF (0) → 5 min
        - 5-55 min → +5 min
        - 60 min → 5 min (wrap-around)
        
        For decrementing, use - key.
        For ON/OFF toggle, use T key.
        For fine control, use +/- keys.
        
        Returns:
            TTS confirmation message
        """
        current = self.settings.max_time_game
        old_value = current
        
        if current <= 0:
            # Timer OFF → Enable at 5 minutes
            new_value = 300  # 5 minutes in seconds
        elif current >= 3600:
            # At maximum (60 min) → Wrap to 5 minutes
            new_value = 300
        else:
            # Active timer → Increment +5 minutes
            new_value = current + 300
        
        self.settings.max_time_game = new_value
        display = self.settings.get_timer_display()
        
        # Log the change
        log.settings_changed("max_time_game", old_value, new_value)
        
        return OptionsFormatter.format_option_changed("Timer", display)
    
    def _modify_shuffle_mode(self) -> str:
        """Toggle shuffle mode (Inversione <-> Mescolata)."""
        old_value = self.settings.shuffle_discards
        success, msg = self.settings.toggle_shuffle_mode()
        if success:
            new_value = self.settings.shuffle_discards
            log.settings_changed("shuffle_discards", old_value, new_value)
        return msg
    
    def _modify_command_hints(self) -> str:
        """Toggle command hints (Attivi <-> Disattivati) (v1.5.0)."""
        old_value = self.settings.command_hints_enabled
        success, msg = self.settings.toggle_command_hints()
        if success:
            new_value = self.settings.command_hints_enabled
            log.settings_changed("command_hints_enabled", old_value, new_value)
        return msg
    
    def _modify_draw_count(self) -> str:
        """Cycle draw count (1 -> 2 -> 3 -> 1)."""
        old_value = self.settings.draw_count
        success, msg = self.settings.cycle_draw_count()
        if success:
            new_value = self.settings.draw_count
            log.settings_changed("draw_count", old_value, new_value)
        return msg
    
    def _modify_scoring(self) -> str:
        """Toggle scoring system (Attivo <-> Disattivato)."""
        old_value = self.settings.scoring_enabled
        success, msg = self.settings.toggle_scoring()
        if success:
            new_value = self.settings.scoring_enabled
            log.settings_changed("scoring_enabled", old_value, new_value)
        return msg
    
    def _modify_timer_strict_mode(self) -> str:
        """Toggle timer strict mode (STRICT <-> PERMISSIVE) (v1.5.2.2)."""
        old_value = self.settings.timer_strict_mode
        success, msg = self.settings.toggle_timer_strict_mode()
        if success:
            new_value = self.settings.timer_strict_mode
            log.settings_changed("timer_strict_mode", old_value, new_value)
        return msg
    
    def _modify_score_warning_level(self) -> str:
        """Cycle score warning level (DISABLED → MINIMAL → BALANCED → COMPLETE) (v2.6.1)."""
        old_value = self.settings.score_warning_level
        success, msg = self.settings.cycle_score_warning_level()
        if success:
            new_value = self.settings.score_warning_level
            log.settings_changed("score_warning_level", old_value.name, new_value.name)
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
            "command_hints": self.settings.command_hints_enabled,  # v1.5.0
            "timer_strict_mode": self.settings.timer_strict_mode,  # v1.5.2.2
            "score_warning_level": self.settings.score_warning_level  # v2.6.1
        }
    
    def _restore_snapshot(self) -> None:
        """Restore original settings (discard changes)."""
        self.settings.deck_type = self.original_settings["deck_type"]
        self.settings.difficulty_level = self.original_settings["difficulty"]
        self.settings.max_time_game = self.original_settings["timer"]
        self.settings.shuffle_discards = self.original_settings["shuffle"]
        self.settings.command_hints_enabled = self.original_settings["command_hints"]  # v1.5.0
        self.settings.timer_strict_mode = self.original_settings["timer_strict_mode"]  # v1.5.2.2
        self.settings.score_warning_level = self.original_settings["score_warning_level"]  # v2.6.1
    
    def _reset_state(self) -> None:
        """Reset controller state (close window)."""
        self.is_open = False
        self.state = "CLOSED"
        self.cursor_position = 0
        self.original_settings.clear()
