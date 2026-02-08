"""Game configuration settings.

Centralized management of game settings including deck type,
timer configuration, shuffle mode, and audio preferences.

Provides type-safe access to settings with validation and
default values.
"""

from typing import Optional, Literal
from dataclasses import dataclass, field
import json
from pathlib import Path


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
    timer_minutes: int = 10  # Default: 10 minutes
    timer_warnings: bool = True
    
    # Gameplay options
    shuffle_enabled: bool = True
    
    # Audio preferences
    audio_enabled: bool = True
    audio_volume: float = 1.0
    verbosity: int = 1  # 0=minimal, 1=normal, 2=detailed
    
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
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
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
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
