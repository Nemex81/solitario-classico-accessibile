"""Game configuration settings.

Centralized management of game settings including deck type,
timer configuration, shuffle mode, and audio preferences.

Provides type-safe access to settings with validation and
default values.
"""

from typing import Optional, Literal, Tuple
from dataclasses import dataclass, field
import json
from pathlib import Path

# Import game logger for settings tracking
from src.infrastructure.logging import game_logger as log


DeckType = Literal["french", "neapolitan"]
ShuffleMode = Literal["enabled", "disabled"]


@dataclass
class GameSettings:
    """Game configuration settings.
    
    Encapsulates all user-configurable game options with
    sensible defaults and validation.
    
    Settings Categories:
    1. Deck Configuration
       - deck_type: French (52 cards) or Neapolitan (40 cards)
    
    2. Timer Configuration
       - timer_enabled: Enable/disable countdown timer
       - timer_minutes: Duration in minutes (1-60)
       - timer_warnings: Enable voice warnings
    
    3. Gameplay Options
       - shuffle_enabled: Auto-shuffle stock when empty
       - difficulty_level: 1-3 (cards drawn per draw)
    
    4. Audio Preferences
       - audio_enabled: Master audio toggle
       - audio_volume: Volume level 0.0-1.0
       - verbosity: Detail level 0-2 (0=minimal, 2=detailed)
    
    Attributes:
        deck_type: Card deck to use
        timer_enabled: Enable countdown timer
        timer_minutes: Timer duration
        timer_warnings: Enable timer warnings
        shuffle_enabled: Auto-shuffle when stock exhausted
        difficulty_level: Cards drawn per draw (1-3)
        audio_enabled: Master audio toggle
        audio_volume: Volume level (0.0-1.0)
        verbosity: TTS detail level (0-2)
    
    Example:
        >>> settings = GameSettings()
        >>> settings.deck_type  # "french" (default)
        >>> settings.set_timer(minutes=10, enabled=True)
        >>> settings.timer_minutes  # 10
    """
    
    # Deck configuration
    deck_type: DeckType = "french"
    
    # Timer configuration
    timer_enabled: bool = False
    timer_minutes: int = 20  # Default: 20 minutes
    timer_warnings: bool = True
    
    # Gameplay options
    shuffle_enabled: bool = False  # Default: reverse mode (legacy behavior)
    difficulty_level: int = 1  # Default: 1 card per draw
    
    # Audio preferences
    audio_enabled: bool = True
    audio_volume: float = 1.0
    verbosity: int = 1  # 0=minimal, 1=normal, 2=detailed
    
    # ===== ORIGINAL METHODS (unchanged) =====
    
    def set_deck_type(self, deck_type: DeckType) -> None:
        """Set card deck type.
        
        Args:
            deck_type: "french" (52 cards) or "neapolitan" (40 cards)
        
        Raises:
            ValueError: If deck_type not in valid options
        """
        if deck_type not in ["french", "neapolitan"]:
            raise ValueError(f"Invalid deck type: {deck_type}")
        self.deck_type = deck_type
    
    def toggle_deck_type(self) -> DeckType:
        """Toggle between French and Neapolitan decks.
        
        Returns:
            New deck type after toggle
        """
        self.deck_type = "neapolitan" if self.deck_type == "french" else "french"
        return self.deck_type
    
    def set_timer(
        self,
        minutes: int,
        enabled: Optional[bool] = None,
        warnings: Optional[bool] = None
    ) -> None:
        """Configure timer settings.
        
        Args:
            minutes: Timer duration (1-60 minutes)
            enabled: Enable/disable timer (None = no change)
            warnings: Enable/disable warnings (None = no change)
        
        Raises:
            ValueError: If minutes not in valid range 1-60
        """
        if not 1 <= minutes <= 60:
            raise ValueError(f"Timer minutes must be 1-60, got {minutes}")
        
        self.timer_minutes = minutes
        if enabled is not None:
            self.timer_enabled = enabled
        if warnings is not None:
            self.timer_warnings = warnings
    
    def increase_timer(self, increment: int = 1) -> int:
        """Increase timer duration.
        
        Args:
            increment: Minutes to add (default 1)
        
        Returns:
            New timer duration in minutes
        """
        new_minutes = min(60, self.timer_minutes + increment)
        self.timer_minutes = new_minutes
        return new_minutes
    
    def decrease_timer(self, decrement: int = 1) -> int:
        """Decrease timer duration.
        
        Args:
            decrement: Minutes to subtract (default 1)
        
        Returns:
            New timer duration in minutes
        """
        new_minutes = max(1, self.timer_minutes - decrement)
        self.timer_minutes = new_minutes
        return new_minutes
    
    def toggle_timer(self) -> bool:
        """Toggle timer enabled state.
        
        Returns:
            New enabled state
        """
        self.timer_enabled = not self.timer_enabled
        return self.timer_enabled
    
    def toggle_shuffle(self) -> bool:
        """Toggle shuffle mode.
        
        Returns:
            New shuffle enabled state
        """
        self.shuffle_enabled = not self.shuffle_enabled
        return self.shuffle_enabled
    
    def set_audio(
        self,
        enabled: Optional[bool] = None,
        volume: Optional[float] = None,
        verbosity: Optional[int] = None
    ) -> None:
        """Configure audio settings.
        
        Args:
            enabled: Enable/disable audio (None = no change)
            volume: Volume level 0.0-1.0 (None = no change)
            verbosity: Detail level 0-2 (None = no change)
        
        Raises:
            ValueError: If volume not in 0.0-1.0 or verbosity not in 0-2
        """
        if enabled is not None:
            self.audio_enabled = enabled
        
        if volume is not None:
            if not 0.0 <= volume <= 1.0:
                raise ValueError(f"Volume must be 0.0-1.0, got {volume}")
            self.audio_volume = volume
        
        if verbosity is not None:
            if verbosity not in [0, 1, 2]:
                raise ValueError(f"Verbosity must be 0-2, got {verbosity}")
            self.verbosity = verbosity
    
    # ===== VALIDATED METHODS FOR OPTIONS WINDOW (NEW) =====
    
    def change_deck_type_validated(self, is_game_running: bool) -> Tuple[bool, str]:
        """Change deck type with game-running validation.
        
        Args:
            is_game_running: True if game is active
        
        Returns:
            (success, message): Tuple with result and announcement
        
        Example:
            >>> settings.change_deck_type_validated(is_game_running=False)
            (True, "Tipo di mazzo impostato a: carte napoletane.")
            >>> settings.change_deck_type_validated(is_game_running=True)
            (False, "Non puoi modificare il tipo di mazzo durante una partita!")
        """
        if is_game_running:
            return (False, "Non puoi modificare il tipo di mazzo durante una partita!  \n")
        
        # Toggle deck type
        new_type = self.toggle_deck_type()
        
        # Format message
        deck_names = {"french": "carte francesi", "neapolitan": "carte napoletane"}
        msg = f"Tipo di mazzo impostato a: {deck_names[new_type]}.  \n"
        
        return (True, msg)
    
    def cycle_difficulty_validated(self, is_game_running: bool) -> Tuple[bool, str]:
        """Cycle difficulty level 1→2→3→1 with validation.
        
        Args:
            is_game_running: True if game is active
        
        Returns:
            (success, message): Tuple with result and announcement
        """
        if is_game_running:
            return (False, "Non puoi modificare il livello di difficoltà durante una partita!  \n")
        
        # Cycle: 1 → 2 → 3 → 1
        self.difficulty_level = (self.difficulty_level % 3) + 1
        
        msg = f"Livello di difficoltà impostato a: {self.difficulty_level}.  \n"
        return (True, msg)
    
    def increment_timer_validated(self, is_game_running: bool, increment: int = 5) -> Tuple[bool, str]:
        """Increment timer with validation and cap at 60 minutes.
        
        Args:
            is_game_running: True if game is active
            increment: Minutes to add (default 5)
        
        Returns:
            (success, message): Tuple with result and announcement
        """
        if is_game_running:
            return (False, "Non puoi modificare il limite massimo per il tempo di gioco durante una partita!  \n")
        
        # Increment with 60 min cap
        old_minutes = self.timer_minutes
        new_minutes = old_minutes + increment
        
        # Cap at 60, or disable if exceeding
        if new_minutes > 60:
            self.timer_enabled = False
            msg = "Il timer è stato disattivato!  \n"
        else:
            self.timer_minutes = new_minutes
            self.timer_enabled = True
            msg = f"Timer impostato a: {new_minutes} minuti.  \n"
        
        return (True, msg)
    
    def decrement_timer_validated(self, is_game_running: bool, decrement: int = 5) -> Tuple[bool, str]:
        """Decrement timer with validation and floor at 5 minutes.
        
        Args:
            is_game_running: True if game is active
            decrement: Minutes to subtract (default 5)
        
        Returns:
            (success, message): Tuple with result and announcement
        """
        if is_game_running:
            return (False, "Non puoi modificare il limite massimo per il tempo di gioco durante una partita!  \n")
        
        # Decrement with 5 min floor
        old_minutes = self.timer_minutes
        new_minutes = old_minutes - decrement
        
        # Floor at 5, or disable if below
        if new_minutes < 5:
            self.timer_enabled = False
            msg = "Il timer è stato disattivato!  \n"
        else:
            self.timer_minutes = new_minutes
            self.timer_enabled = True
            msg = f"Timer impostato a: {new_minutes} minuti.  \n"
        
        return (True, msg)
    
    def toggle_shuffle_mode_validated(self, is_game_running: bool) -> Tuple[bool, str]:
        """Toggle shuffle mode with validation.
        
        Args:
            is_game_running: True if game is active
        
        Returns:
            (success, message): Tuple with result and announcement
        """
        if is_game_running:
            return (False, "Non puoi modificare la modalità di riciclo scarti durante una partita!  \n")
        
        # Toggle shuffle
        self.shuffle_enabled = not self.shuffle_enabled
        
        if self.shuffle_enabled:
            msg = "Modalità riciclo scarti: MESCOLATA CASUALE.  \n"
        else:
            msg = "Modalità riciclo scarti: INVERSIONE SEMPLICE.  \n"
        
        return (True, msg)
    
    def disable_timer_validated(self, is_game_running: bool) -> Tuple[bool, str]:
        """Disable timer explicitly with validation.
        
        Args:
            is_game_running: True if game is active
        
        Returns:
            (success, message): Tuple with result and announcement
        """
        if is_game_running:
            return (False, "Non puoi disabilitare il timer durante una partita!  \n")
        
        self.timer_enabled = False
        msg = "Il timer è stato disattivato!  \n"
        
        return (True, msg)
    
    # ===== SERIALIZATION METHODS (updated) =====
    
    def to_dict(self) -> dict:
        """Export settings to dictionary.
        
        Returns:
            Dictionary of all settings (for JSON serialization)
        """
        return {
            "deck_type": self.deck_type,
            "timer_enabled": self.timer_enabled,
            "timer_minutes": self.timer_minutes,
            "timer_warnings": self.timer_warnings,
            "shuffle_enabled": self.shuffle_enabled,
            "difficulty_level": self.difficulty_level,
            "audio_enabled": self.audio_enabled,
            "audio_volume": self.audio_volume,
            "verbosity": self.verbosity
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GameSettings':
        """Create settings from dictionary.
        
        Args:
            data: Dictionary with settings (from JSON)
        
        Returns:
            GameSettings instance
        """
        return cls(**data)
    
    def save_to_file(self, filepath: Path) -> None:
        """Save settings to JSON file.
        
        Args:
            filepath: Path to save settings JSON
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            
            # Log successful save
            log.info_query_requested("settings_save", f"Saved to {filepath}")
        except Exception as e:
            # Log save error
            log.error_occurred("Settings", f"Failed to save: {filepath}", e)
            raise
    
    @classmethod
    def load_from_file(cls, filepath: Path) -> 'GameSettings':
        """Load settings from JSON file.
        
        Args:
            filepath: Path to settings JSON file
        
        Returns:
            GameSettings instance
        
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is invalid JSON
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            settings = cls.from_dict(data)
            
            # Log successful load
            log.settings_changed("all_settings", "default", "loaded_from_file")
            log.info_query_requested("settings_load", f"Loaded from {filepath}")
            
            return settings
            
        except FileNotFoundError:
            # Log file not found warning
            log.warning_issued("Settings", f"File not found: {filepath}, using defaults")
            raise
            
        except json.JSONDecodeError as e:
            # Log corrupted JSON error
            log.error_occurred("Settings", f"Corrupted JSON: {filepath}", e)
            raise
            
        except Exception as e:
            # Log unexpected error
            log.error_occurred("Settings", f"Unexpected error loading {filepath}", e)
            raise
