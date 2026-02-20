"""Difficulty Preset Model - Domain layer for preset difficulty configurations.

This module defines the difficulty preset system that manages locked and customizable
options for each of the 5 difficulty levels (Principiante → Maestro).

Version: v2.4.0
Pattern: Domain-Driven Design - Pure business logic
Clean Architecture Layer: Domain/Models
Dependencies: None (pure domain model)

Features:
- 5 preset definitions (Level 1-5)
- Option locking rules per level
- Default values for each preset
- Query methods for lock status
- Immutable dataclass design

Preset Rules:
- Level 1 (Principiante): Beginner-friendly, timer OFF, most options unlocked
- Level 2 (Facile): Easy mode, permissive timer, customizable
- Level 3 (Normale): Vegas standard rules, 3 cards, balanced
- Level 4 (Esperto): Time Attack mode, 30min timer, some locks
- Level 5 (Maestro): Tournament mode, strict 15min, all options locked
"""

from dataclasses import dataclass, field
from typing import Dict, Set, Optional


@dataclass(frozen=True)
class DifficultyPreset:
    """Immutable difficulty preset configuration.
    
    Defines the complete configuration for a difficulty level including:
    - Which options are locked (non-modifiable)
    - Default/forced values for each option
    - Level name and description
    
    Attributes:
        level: Difficulty level (1-5)
        name: Level name (Principiante, Facile, Normale, Esperto, Maestro)
        description: Brief description of the preset
        locked_options: Set of option names that cannot be modified
        preset_values: Dict of option names to their forced/default values
    
    Example:
        >>> preset = DifficultyPreset.get_preset(5)  # Maestro
        >>> preset.is_locked("draw_count")  # True - locked at level 5
        >>> preset.get_value("draw_count")  # 3
    """
    
    level: int
    name: str
    description: str
    locked_options: Set[str] = field(default_factory=set)
    preset_values: Dict[str, any] = field(default_factory=dict)
    
    def is_locked(self, option_name: str) -> bool:
        """Check if an option is locked at this difficulty level.
        
        Args:
            option_name: Name of the option to check
        
        Returns:
            True if option is locked (cannot be modified), False otherwise
        
        Example:
            >>> preset = DifficultyPreset.get_preset(5)
            >>> preset.is_locked("draw_count")  # True
            >>> preset.is_locked("deck_type")  # False (never locked)
        """
        return option_name in self.locked_options
    
    def get_value(self, option_name: str) -> Optional[any]:
        """Get the preset value for an option.
        
        Args:
            option_name: Name of the option
        
        Returns:
            The preset value if option has one, None otherwise
        
        Example:
            >>> preset = DifficultyPreset.get_preset(4)
            >>> preset.get_value("max_time_game")  # 1800 (30 minutes in seconds)
        """
        return self.preset_values.get(option_name)
    
    def get_locked_options(self) -> Set[str]:
        """Get set of all locked options for this preset.
        
        Returns:
            Set of option names that are locked
        
        Example:
            >>> preset = DifficultyPreset.get_preset(5)
            >>> preset.get_locked_options()
            {'draw_count', 'max_time_game', 'timer_strict_mode', ...}
        """
        return self.locked_options.copy()
    
    def apply_to(self, settings: 'GameSettings') -> None:
        """Apply this preset's configured values to a GameSettings instance.
        
        Sets all option values according to preset specification.
        Applies values from preset_values dict to corresponding GameSettings attributes.
        
        Args:
            settings: GameSettings instance to modify
        
        Example:
            >>> from src.domain.services.game_settings import GameSettings
            >>> settings = GameSettings()
            >>> preset = DifficultyPreset.get_preset(5)  # Maestro
            >>> preset.apply_to(settings)
            >>> assert settings.max_time_game == 900  # 15 minutes
            >>> assert settings.draw_count == 3
            >>> assert settings.timer_strict_mode == True
        
        Version:
            v2.4.1: Created to fix preset value application bug
        
        Notes:
            - Applies ALL values in preset_values dict
            - Respects GameSettings attribute names
            - Does not validate if option is locked (caller's responsibility)
        """
        for option_name, value in self.preset_values.items():
            if hasattr(settings, option_name):
                setattr(settings, option_name, value)
    
    @staticmethod
    def get_preset(level: int) -> 'DifficultyPreset':
        """Factory method to get preset for a specific difficulty level.
        
        Args:
            level: Difficulty level (1-5)
        
        Returns:
            DifficultyPreset instance for the requested level
        
        Raises:
            ValueError: If level is not in range 1-5
        
        Example:
            >>> preset = DifficultyPreset.get_preset(3)
            >>> preset.name  # "Normale"
        """
        if level < 1 or level > 5:
            raise ValueError(f"Invalid difficulty level: {level}. Must be 1-5.")
        
        presets = {
            1: _create_level_1_principiante(),
            2: _create_level_2_facile(),
            3: _create_level_3_normale(),
            4: _create_level_4_esperto(),
            5: _create_level_5_maestro(),
        }
        
        return presets[level]
    
    @staticmethod
    def get_all_presets() -> Dict[int, 'DifficultyPreset']:
        """Get all 5 difficulty presets.
        
        Returns:
            Dictionary mapping level (1-5) to DifficultyPreset
        
        Example:
            >>> presets = DifficultyPreset.get_all_presets()
            >>> len(presets)  # 5
            >>> presets[1].name  # "Principiante"
        """
        return {level: DifficultyPreset.get_preset(level) for level in range(1, 6)}


# ========================================
# PRESET FACTORY FUNCTIONS
# ========================================

def _create_level_1_principiante() -> DifficultyPreset:
    """Level 1 - Principiante: Beginner-friendly preset.
    
    Locked:
    - max_time_game: OFF (0 seconds) - No time pressure for beginners
    
    Customizable:
    - draw_count: 1-3 (default 1) - Start with easiest
    - shuffle_discards: True/False (default True=Mescolata) - Easier
    - scoring_enabled: True/False (default True)
    - command_hints_enabled: True/False (default True)
    - timer_strict_mode: Not applicable (timer is OFF)
    
    Notes:
    - Minimal locks to allow exploration
    - Timer forced OFF to remove time pressure
    - Default to easiest settings
    """
    return DifficultyPreset(
        level=1,
        name="Principiante",
        description="Livello per principianti: timer disattivato, impostazioni base",
        locked_options={"max_time_game"},
        preset_values={
            "draw_count": 1,  # Default: 1 card (easiest)
            "max_time_game": 0,  # Forced: Timer OFF
            "shuffle_discards": True,  # Default: Mescolata (easier)
            "scoring_enabled": True,  # Default: scoring ON
            "command_hints_enabled": True,  # Default: hints ON
        }
    )


def _create_level_2_facile() -> DifficultyPreset:
    """Level 2 - Facile: Easy mode with permissive timer.
    
    Locked:
    - timer_strict_mode: False (PERMISSIVE) - Continue with malus if time expires
    
    Customizable:
    - draw_count: 1-3 (default 2) - Medium difficulty
    - max_time_game: 0-60 min (default customizable)
    - shuffle_discards: True/False (default True=Mescolata)
    - scoring_enabled: True/False
    - command_hints_enabled: True/False
    
    Notes:
    - Permissive timer allows continuation with penalty
    - Most options customizable for learning
    """
    return DifficultyPreset(
        level=2,
        name="Facile",
        description="Livello facile: timer permissivo, opzioni personalizzabili",
        locked_options={"timer_strict_mode"},
        preset_values={
            "draw_count": 2,  # Default: 2 cards
            "shuffle_discards": True,  # Default: Mescolata
            "timer_strict_mode": False,  # Forced: PERMISSIVE mode
        }
    )


def _create_level_3_normale() -> DifficultyPreset:
    """Level 3 - Normale: Vegas standard rules.
    
    Locked:
    - draw_count: 3 - Vegas standard 3-card draw
    
    Customizable:
    - max_time_game: 0-60 min
    - timer_strict_mode: True/False (STRICT or PERMISSIVE)
    - shuffle_discards: True/False (default False=Inversione, Vegas prefers invert)
    - scoring_enabled: True/False
    - command_hints_enabled: True/False
    
    Notes:
    - Follows Vegas Solitaire standard rules
    - 3-card draw mandatory
    - Preference for inversion (standard Vegas)
    """
    return DifficultyPreset(
        level=3,
        name="Normale",
        description="Regole Vegas standard: 3 carte, inversione preferita",
        locked_options={"draw_count"},
        preset_values={
            "draw_count": 3,  # Forced: 3 cards (Vegas standard)
            "shuffle_discards": False,  # Default: Inversione (Vegas standard)
        }
    )


def _create_level_4_esperto() -> DifficultyPreset:
    """Level 4 - Esperto: Time Attack mode with 30-minute timer.
    
    Locked:
    - draw_count: 3 - Maximum difficulty
    - max_time_game: 1800 seconds (30 minutes) - Time Attack challenge
    - timer_strict_mode: False (PERMISSIVE) - Can continue with malus
    - shuffle_discards: False (Inversione) - Standard Vegas
    - command_hints_enabled: False - No hints for experts
    
    Customizable:
    - scoring_enabled: True/False (can disable if focusing on time)
    
    Notes:
    - Time Attack mode: 30-minute challenge
    - Most options locked for consistency
    - Hints disabled (expert level)
    """
    return DifficultyPreset(
        level=4,
        name="Esperto",
        description="Time Attack: 30 minuti, 3 carte, senza suggerimenti",
        locked_options={
            "draw_count",
            "max_time_game",
            "timer_strict_mode",
            "shuffle_discards",
            "command_hints_enabled"
        },
        preset_values={
            "draw_count": 3,  # Forced: 3 cards
            "max_time_game": 1800,  # Forced: 30 minutes (1800 seconds)
            "timer_strict_mode": False,  # Forced: PERMISSIVE (can continue with malus)
            "shuffle_discards": False,  # Forced: Inversione
            "command_hints_enabled": False,  # Forced: Hints OFF
        }
    )


def _create_level_5_maestro() -> DifficultyPreset:
    """Level 5 - Maestro: Tournament strict mode.
    
    Locked (ALL OPTIONS except deck_type):
    - draw_count: 3 - Tournament standard
    - max_time_game: 900 seconds (15 minutes) - Strict tournament time
    - timer_strict_mode: True (STRICT) - Game stops at timeout
    - shuffle_discards: False (Inversione) - Tournament standard
    - scoring_enabled: True - Mandatory for ranking
    - command_hints_enabled: False - No assistance in tournament
    
    Customizable:
    - deck_type: French/Neapolitan (never locked - aesthetic choice)
    
    Notes:
    - Tournament mode: competitive fair play
    - 15-minute strict timer (auto-stop)
    - All gameplay options locked
    - Scoring mandatory for leaderboard
    - No hints or assistance
    - Anti-cheat: preset validated on load
    """
    return DifficultyPreset(
        level=5,
        name="Maestro",
        description="Modalità Tournament: 15 min strict, tutte opzioni bloccate",
        locked_options={
            "draw_count",
            "max_time_game",
            "timer_strict_mode",
            "shuffle_discards",
            "scoring_enabled",
            "command_hints_enabled"
        },
        preset_values={
            "draw_count": 3,  # Forced: 3 cards
            "max_time_game": 900,  # Forced: 15 minutes (900 seconds)
            "timer_strict_mode": True,  # Forced: STRICT mode (auto-stop)
            "shuffle_discards": False,  # Forced: Inversione
            "scoring_enabled": True,  # Forced: Scoring ON (required for ranking)
            "command_hints_enabled": False,  # Forced: Hints OFF
        }
    )
