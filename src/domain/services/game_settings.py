"""Game settings service for configuration management.

Manages all game configuration parameters including:
- Deck type (French/Neapolitan)
- Difficulty level (1-5, v2.0.0 extended from 1-3)
- Draw count (1-3 cards, v2.0.0 separated from difficulty)
- Timer settings (OFF or 5-60 minutes)
- Shuffle mode (invert/random)
- Command hints (v1.5.0) - contextual voice hints
- Scoring system (v2.0.0) - enable/disable scoring

Provides validation to prevent modifications during active games.
All methods return (success, message) tuples for TTS feedback.

v2.0.0 Changes:
- Difficulty extended to 5 levels (was 3)
- Levels 4-5 have auto-adjustment constraints
- Draw count separated from difficulty level
- Scoring system toggle added

v2.4.0 Changes:
- Difficulty preset system with option locking
- Progressive lock rules (Level 1: 1 lock → Level 5: 6 locks)
- Tournament mode (Level 5) with strict enforcement
"""

from typing import Tuple, Set
from src.domain.models.difficulty_preset import DifficultyPreset


class GameState:
    """Mock game state for validation.
    
    This will be replaced with actual GameService reference
    in production integration.
    """
    def __init__(self):
        self.is_running = False


class GameSettings:
    """Game configuration settings manager (domain service).
    
    Centralizes all game settings with validation and consistent
    feedback messages for accessibility (TTS output).
    
    Attributes:
        deck_type: "french" or "neapolitan"
        difficulty_level: 1-5 (v2.0.0: extended from 1-3)
        draw_count: 1-3 cards drawn from stock (v2.0.0: separated from difficulty)
        max_time_game: Timer in seconds (-1=OFF, or 300-3600)
        shuffle_discards: True=random shuffle, False=invert order
        command_hints_enabled: (v1.5.0) Enable/disable contextual voice hints
        scoring_enabled: (v2.0.0) Enable/disable scoring system
        timer_strict_mode: (v1.5.2.2) Timer expiration behavior
            - True: STRICT mode (auto-stop at timeout, legacy behavior)
            - False: PERMISSIVE mode (continue with -100pts/min malus)
        game_state: Reference to game state for validation
    
    Design:
        - All modification methods return (bool, str) tuples
        - Validation blocks changes during active games
        - Timer range: OFF or 5-60 minutes (5min increments)
        - Italian language messages for TTS
        - Levels 4-5 have constraint auto-adjustment (v2.0.0)
    """
    
    def __init__(self, game_state=None):
        """Initialize game settings with defaults.
        
        Args:
            game_state: Optional GameState/GameService reference
        """
        # Default settings
        self.deck_type = "french"  # "french" or "neapolitan"
        self.difficulty_level = 1  # 1-5 (v2.0.0: was 1-3)
        self.draw_count = 1        # 1-3 cards (v2.0.0: separated from difficulty)
        self.max_time_game = -1    # -1 = OFF, or seconds (300-3600)
        self.shuffle_discards = False  # False = invert, True = random
        
        # Feature v1.5.0: Command hints
        self.command_hints_enabled = True  # Enable/disable command hints during gameplay
        
        # Feature v2.0.0: Scoring system
        self.scoring_enabled = True  # Enable/disable scoring system
        
        # Feature v1.5.2.2: Timer strict mode
        self.timer_strict_mode = True  # True = STRICT (auto-stop), False = PERMISSIVE (malus)
        #   True  = STRICT: Partita interrotta alla scadenza (comportamento legacy)
        #   False = PERMISSIVE: Continua con malus punti (-100/min oltre limite)
        
        # Game state reference for validation
        self.game_state = game_state or GameState()
    
    # ========================================
    # VALIDATION
    # ========================================
    
    def validate_not_running(self) -> bool:
        """Check if modifications are allowed (game not running).
        
        Returns:
            True if game is NOT running (modifications allowed)
        """
        return not self.game_state.is_running
    
    # ========================================
    # DIFFICULTY PRESET SYSTEM (v2.4.0)
    # ========================================
    
    def apply_difficulty_preset(self, level: int) -> None:
        """Apply difficulty preset for specified level.
        
        Applies all preset values (locked and default) for the given
        difficulty level. Used when cycling difficulty or loading from save.
        
        Args:
            level: Difficulty level (1-5)
        
        Example:
            >>> settings.apply_difficulty_preset(5)  # Apply Maestro preset
            >>> settings.draw_count  # 3 (locked)
            >>> settings.max_time_game  # 900 (15 min, locked)
        
        Note:
            This method directly sets attribute values without validation.
            It's intended for internal use during difficulty changes.
        
        Version: v2.4.0
        """
        preset = DifficultyPreset.get_preset(level)
        
        # Apply all preset values
        for option_name, value in preset.preset_values.items():
            if hasattr(self, option_name):
                setattr(self, option_name, value)
    
    def is_option_locked(self, option_name: str) -> bool:
        """Check if option is locked at current difficulty level.
        
        Args:
            option_name: Name of the option (e.g., "draw_count", "max_time_game")
        
        Returns:
            True if option is locked (cannot be modified), False otherwise
        
        Example:
            >>> settings.difficulty_level = 5
            >>> settings.is_option_locked("draw_count")  # True
            >>> settings.is_option_locked("deck_type")  # False (never locked)
        
        Note:
            Used by OptionsController to block modification attempts.
        
        Version: v2.4.0
        """
        try:
            preset = DifficultyPreset.get_preset(self.difficulty_level)
            return preset.is_locked(option_name)
        except ValueError:
            # Invalid difficulty level - no locks
            return False
    
    def get_locked_options(self) -> Set[str]:
        """Get set of all locked options at current difficulty level.
        
        Returns:
            Set of option names that are locked
        
        Example:
            >>> settings.difficulty_level = 5
            >>> locked = settings.get_locked_options()
            >>> "draw_count" in locked  # True
            >>> "deck_type" in locked  # False
        
        Version: v2.4.0
        """
        try:
            preset = DifficultyPreset.get_preset(self.difficulty_level)
            return preset.get_locked_options()
        except ValueError:
            # Invalid difficulty level - no locks
            return set()
    
    def get_current_preset(self) -> DifficultyPreset:
        """Get the current difficulty preset.
        
        Returns:
            DifficultyPreset for current difficulty_level
        
        Example:
            >>> settings.difficulty_level = 3
            >>> preset = settings.get_current_preset()
            >>> preset.name  # "Normale"
        
        Version: v2.4.0
        """
        return DifficultyPreset.get_preset(self.difficulty_level)
    
    # ========================================
    # DECK TYPE
    # ========================================
    
    def toggle_deck_type(self) -> Tuple[bool, str]:
        """Toggle deck type between French and Neapolitan.
        
        Returns:
            Tuple[bool, str]: (success, message)
        
        Examples:
            >>> settings.deck_type = "french"
            >>> settings.toggle_deck_type()
            (True, "Tipo mazzo impostato a: Carte Napoletane.")
        """
        if not self.validate_not_running():
            return (False, "Non puoi modificare il tipo di mazzo durante una partita!")
        
        # Toggle
        if self.deck_type == "french":
            self.deck_type = "neapolitan"
            return (True, "Tipo mazzo impostato a: Carte Napoletane.")
        else:
            self.deck_type = "french"
            return (True, "Tipo mazzo impostato a: Carte Francesi.")
    
    # ========================================
    # DIFFICULTY
    # ========================================
    
    def cycle_difficulty(self) -> Tuple[bool, str]:
        """Cycle difficulty level through 1 -> 2 -> 3 -> 4 -> 5 -> 1.
        
        v2.4.0: Uses DifficultyPreset system for automatic configuration:
        - Level 1 (Principiante): Timer OFF, beginner-friendly
        - Level 2 (Facile): PERMISSIVE timer, customizable
        - Level 3 (Normale): 3-card draw locked, Vegas standard
        - Level 4 (Esperto): Time Attack 30min, 5 options locked
        - Level 5 (Maestro): Tournament strict 15min, all options locked
        
        Preset values are applied automatically via apply_difficulty_preset().
        
        Returns:
            Tuple[bool, str]: (success, message with applied changes)
        
        Examples:
            >>> settings.difficulty_level = 3
            >>> settings.cycle_difficulty()
            (True, "Difficoltà impostata a: Livello 4 - Esperto...")
        
        Version: v2.4.0 - Refactored to use DifficultyPreset system
        """
        if not self.validate_not_running():
            return (False, "Non puoi modificare la difficoltà durante una partita!")
        
        # Cycle: 1 -> 2 -> 3 -> 4 -> 5 -> 1
        self.difficulty_level = (self.difficulty_level % 5) + 1
        
        # Apply difficulty preset
        self.apply_difficulty_preset(self.difficulty_level)
        
        # Get level name
        level_name = self.get_difficulty_display()
        base_message = f"Difficoltà impostata a: {level_name}."
        
        # Get preset to announce locked options
        preset = self.get_current_preset()
        locked_options = preset.get_locked_options()
        
        # Build announcement of applied changes
        adjustments = []
        
        # Announce key locked values based on level
        if self.difficulty_level == 1:
            adjustments.append("Timer disattivato (preset principiante)")
        elif self.difficulty_level == 2:
            adjustments.append("Modalità timer: Permissive")
        elif self.difficulty_level == 3:
            adjustments.append("Carte pescate: 3 (Vegas standard)")
        elif self.difficulty_level == 4:
            adjustments.append("Timer: 30 minuti (Time Attack)")
            adjustments.append("Suggerimenti disattivati")
        elif self.difficulty_level == 5:
            adjustments.append("Timer: 15 minuti STRICT (Tournament)")
            adjustments.append("Tutte le opzioni bloccate")
        
        # Build final message
        if adjustments:
            adjustment_text = "; ".join(adjustments)
            return (True, f"{base_message} {adjustment_text}.")
        
        return (True, base_message)
        
    # ========================================
    # DRAW COUNT (v2.0.0)
    # ========================================
    
    def cycle_draw_count(self) -> Tuple[bool, str]:
        """Cycle draw count through 1 -> 2 -> 3 -> 1.
        
        v2.0.0: Separated from difficulty level.
        
        Validation:
        - Cannot modify during game
        - Level 4: draw_count must be ≥2 (auto-corrects invalid values)
        - Level 5: draw_count must be 3 (auto-corrects invalid values)
        
        Returns:
            Tuple[bool, str]: (success, message with validation if needed)
        
        Examples:
            >>> settings.draw_count = 1
            >>> settings.cycle_draw_count()
            (True, "Carte pescate impostate a: 2.")
        """
        if not self.validate_not_running():
            return (False, "Non puoi modificare le carte pescate durante una partita!")
        
        # Cycle: 1 -> 2 -> 3 -> 1
        self.draw_count = (self.draw_count % 3) + 1
        
        # Validate against difficulty constraints
        validation_msg = self._validate_draw_count_for_level()
        
        if validation_msg:
            return (True, f"Carte pescate impostate a: {self.draw_count}. {validation_msg}")
        
        return (True, f"Carte pescate impostate a: {self.draw_count}.")
    
    def _validate_draw_count_for_level(self) -> str:
        """Validate draw_count compatibility with difficulty level.
        
        v1.5.2.5: Levels 1-3 have no validation (user can modify freely).
        Levels 4-5 maintain strict validation for competitive play.
        
        Returns:
            Validation message if adjustments needed, empty string otherwise
        """
        # Levels 1-3: No validation - user can change draw_count freely
        if self.difficulty_level <= 3:
            return ""
        
        # Level 4: Minimum 2 cards
        if self.difficulty_level == 4 and self.draw_count < 2:
            self.draw_count = 2
            return "Livello Esperto richiede almeno 2 carte."
        
        # Level 5: Exactly 3 cards (locked)
        elif self.difficulty_level == 5 and self.draw_count != 3:
            self.draw_count = 3
            return "Livello Maestro richiede esattamente 3 carte."
        
        return ""
    
    # ========================================
    # TIMER
    # ========================================
    
    def toggle_timer(self) -> Tuple[bool, str]:
        """Toggle timer ON/OFF with default 5 minutes.
        
        Logic:
        - If OFF (max_time_game <= 0): Activate to 5 minutes (300 seconds)
        - If ON (max_time_game > 0): Deactivate (max_time_game = -1)
        
        This method supports the dedicated 'T' key in options window
        for quick toggle between OFF and default 5-minute timer.
        
        Returns:
            Tuple[bool, str]: (success, message)
        
        Examples:
            >>> settings.max_time_game = -1  # OFF
            >>> settings.toggle_timer()
            (True, "Timer attivato a: 5 minuti.")
            
            >>> settings.max_time_game = 600  # 10 min
            >>> settings.toggle_timer()
            (True, "Timer disattivato.")
        
        Reference:
            User requirement: Tasto T per toggle rapido OFF <-> 5min
            OPTIONS_WINDOW_ROADMAP.md Commit #17
        """
        # Validation: block if game is running
        if not self.validate_not_running():
            return (False, "Non puoi modificare il timer durante una partita!")
        
        # Toggle logic
        if self.max_time_game <= 0:
            # OFF -> ON (default 5 minutes)
            self.max_time_game = 300  # 5 minutes in seconds
            return (True, "Timer attivato a: 5 minuti.")
        else:
            # ON -> OFF
            self.max_time_game = -1
            return (True, "Timer disattivato.")
    
    def increment_timer_validated(self) -> Tuple[bool, str]:
        """Increment timer by 5 minutes (300 seconds).
        
        Range: 5-60 minutes (300-3600 seconds)
        If timer is OFF, activates to 5 minutes first.
        
        Returns:
            Tuple[bool, str]: (success, message)
        
        Examples:
            >>> settings.max_time_game = 300  # 5 min
            >>> settings.increment_timer_validated()
            (True, "Timer impostato a: 10 minuti.")
            
            >>> settings.max_time_game = 3600  # 60 min (max)
            >>> settings.increment_timer_validated()
            (True, "Timer già al massimo: 60 minuti.")
        """
        if not self.validate_not_running():
            return (False, "Non puoi modificare il timer durante una partita!")
        
        # If OFF, activate to 5 min
        if self.max_time_game <= 0:
            self.max_time_game = 300
            return (True, "Timer impostato a: 5 minuti.")
        
        # Check maximum (60 minutes = 3600 seconds)
        if self.max_time_game >= 3600:
            return (True, "Timer già al massimo: 60 minuti.")
        
        # Increment by 5 minutes (300 seconds)
        self.max_time_game += 300
        
        # Cap at 60 minutes
        if self.max_time_game > 3600:
            self.max_time_game = 3600
        
        minutes = self.max_time_game // 60
        return (True, f"Timer impostato a: {minutes} minuti.")
    
    def decrement_timer_validated(self) -> Tuple[bool, str]:
        """Decrement timer by 5 minutes (300 seconds).
        
        Range: 5-60 minutes, or OFF (reaching 0 disables timer)
        
        Returns:
            Tuple[bool, str]: (success, message)
        
        Examples:
            >>> settings.max_time_game = 600  # 10 min
            >>> settings.decrement_timer_validated()
            (True, "Timer impostato a: 5 minuti.")
            
            >>> settings.max_time_game = 300  # 5 min
            >>> settings.decrement_timer_validated()
            (True, "Timer disattivato.")
            
            >>> settings.max_time_game = -1  # Already OFF
            >>> settings.decrement_timer_validated()
            (True, "Timer già disattivato.")
        """
        if not self.validate_not_running():
            return (False, "Non puoi modificare il timer durante una partita!")
        
        # Check if already OFF
        if self.max_time_game <= 0:
            return (True, "Timer già disattivato.")
        
        # Decrement by 5 minutes (300 seconds)
        self.max_time_game -= 300
        
        # If reached 0 or below, disable (set to -1)
        if self.max_time_game <= 0:
            self.max_time_game = -1
            return (True, "Timer disattivato.")
        
        minutes = self.max_time_game // 60
        return (True, f"Timer impostato a: {minutes} minuti.")
    
    # ========================================
    # SHUFFLE MODE
    # ========================================
    
    def toggle_shuffle_mode(self) -> Tuple[bool, str]:
        """Toggle waste recycle shuffle mode.
        
        Modes:
        - False (default): Invert order (simple reverse)
        - True: Random shuffle
        
        v2.0.0: Levels 4-5 lock shuffle to invert mode (cannot toggle).
        
        Returns:
            Tuple[bool, str]: (success, message)
        
        Examples:
            >>> settings.shuffle_discards = False
            >>> settings.toggle_shuffle_mode()
            (True, "Modalità riciclo scarti impostata a: Mescolata Casuale.")
        """
        if not self.validate_not_running():
            return (False, "Non puoi modificare la modalità riciclo durante una partita!")
        
        # Check level 4-5 constraint
        if self.difficulty_level >= 4:
            self.shuffle_discards = False
            return (False, "Livelli Esperto e Maestro richiedono Inversione Semplice.")
        
        # Toggle
        self.shuffle_discards = not self.shuffle_discards
        
        if self.shuffle_discards:
            return (True, "Modalità riciclo scarti impostata a: Mescolata Casuale.")
        else:
            return (True, "Modalità riciclo scarti impostata a: Inversione Semplice.")
    
    # ========================================
    # SCORING SYSTEM (v2.0.0)
    # ========================================
    
    def toggle_scoring(self) -> Tuple[bool, str]:
        """Toggle scoring system on/off.
        
        v2.0.0: Enable/disable scoring system for free-play mode.
        Can be toggled at any time when game is not running.
        
        Returns:
            Tuple[bool, str]: (success, message)
        
        Examples:
            >>> settings.scoring_enabled = True
            >>> settings.toggle_scoring()
            (True, "Sistema punti disattivato.")
        """
        if not self.validate_not_running():
            return (False, "Non puoi modificare questa opzione durante una partita!")
        
        # Toggle
        self.scoring_enabled = not self.scoring_enabled
        
        if self.scoring_enabled:
            return (True, "Sistema punti attivo.")
        else:
            return (True, "Sistema punti disattivato.")
    
    # ========================================
    # GETTERS (for display)
    # ========================================
    
    def get_deck_type_display(self) -> str:
        """Get human-readable deck type."""
        return "Carte Francesi" if self.deck_type == "french" else "Carte Napoletane"
    
    def get_difficulty_display(self) -> str:
        """Get human-readable difficulty with level names.
        
        v2.0.0: Extended to 5 levels with names.
        """
        level_names = {
            1: "Livello 1 - Facile",
            2: "Livello 2 - Medio",
            3: "Livello 3 - Difficile",
            4: "Livello 4 - Esperto",
            5: "Livello 5 - Maestro"
        }
        return level_names.get(self.difficulty_level, f"Livello {self.difficulty_level}")
    
    def get_draw_count_display(self) -> str:
        """Get human-readable draw count.
        
        v2.0.0: New method for separated draw count option.
        """
        return f"{self.draw_count} {'carta' if self.draw_count == 1 else 'carte'}"
    
    def get_scoring_display(self) -> str:
        """Get human-readable scoring status.
        
        v2.0.0: New method for scoring toggle option.
        """
        return "Attivo" if self.scoring_enabled else "Disattivato"
    
    def get_timer_display(self) -> str:
        """Get human-readable timer value."""
        if self.max_time_game <= 0:
            return "Disattivato"
        else:
            minutes = self.max_time_game // 60
            return f"{minutes} minuti"
    
    def get_shuffle_mode_display(self) -> str:
        """Get human-readable shuffle mode."""
        return "Mescolata Casuale" if self.shuffle_discards else "Inversione Semplice"
    
    # ========================================
    # COMMAND HINTS (v1.5.0)
    # ========================================
    
    def toggle_command_hints(self) -> Tuple[bool, str]:
        """Toggle command hints on/off.
        
        Command hints provide contextual voice hints during gameplay
        to help users (especially screen reader users) discover available
        commands in each context.
        
        Cannot be modified during active game for consistency.
        
        Returns:
            Tuple[bool, str]: (success, message)
        
        Examples:
            >>> settings.command_hints_enabled = True
            >>> settings.toggle_command_hints()
            (True, "Suggerimenti comandi disattivati.")
            
            >>> settings.toggle_command_hints()
            (True, "Suggerimenti comandi attivi.")
        """
        if not self.validate_not_running():
            return (False, "Non puoi modificare questa opzione durante una partita!")
        
        # Toggle
        self.command_hints_enabled = not self.command_hints_enabled
        
        if self.command_hints_enabled:
            return (True, "Suggerimenti comandi attivi.")
        else:
            return (True, "Suggerimenti comandi disattivati.")
    
    def get_command_hints_display(self) -> str:
        """Get human-readable command hints status.
        
        Returns:
            "Attivi" if enabled, "Disattivati" if disabled
        
        Used by OptionsFormatter for option #5 display.
        """
        return "Attivi" if self.command_hints_enabled else "Disattivati"
    
    # ========================================
    # TIMER STRICT MODE (v1.5.2.2)
    # ========================================
    
    def toggle_timer_strict_mode(self) -> Tuple[bool, str]:
        """Toggle timer strict mode on/off.
        
        v1.5.2.2: Configure timer expiration behavior.
        
        STRICT mode (True):
            - Game stops automatically when timer expires
            - Shows final statistics and returns to menu
            - No scoring penalty (game over by timeout)
            - Legacy behavior from scr/ version
        
        PERMISSIVE mode (False):
            - Game continues beyond time limit
            - TTS announces timeout and malus
            - Scoring penalty: -100 points per overtime minute
            - Allows completing game after timeout
        
        Returns:
            Tuple[bool, str]: (success, message)
        
        Note:
            - Only affects behavior when timer is enabled
            - Default is STRICT (backward compatible)
            - PERMISSIVE mode designed for learning/casual play
        
        Examples:
            >>> settings.timer_strict_mode = True
            >>> settings.toggle_timer_strict_mode()
            (True, "Modalità timer: PERMISSIVE (malus). Il gioco continua oltre il limite con penalità di 100 punti al minuto.")
        """
        if not self.validate_not_running():
            return (False, "Non puoi modificare questa opzione durante una partita!")
        
        # Toggle
        self.timer_strict_mode = not self.timer_strict_mode
        
        if self.timer_strict_mode:
            return (True, "Modalità timer: STRICT (auto-stop). Il gioco si interrompe alla scadenza del timer.")
        else:
            return (True, "Modalità timer: PERMISSIVE (malus). Il gioco continua oltre il limite con penalità di 100 punti al minuto.")
    
    def get_timer_strict_mode_display(self) -> str:
        """Get human-readable timer strict mode status.
        
        v1.5.2.2: Display current timer expiration behavior.
        
        Returns:
            "STRICT (auto-stop)" if strict mode enabled,
            "PERMISSIVE (malus)" if permissive mode enabled
        
        Used by OptionsFormatter for option #8 display.
        """
        return "STRICT (auto-stop)" if self.timer_strict_mode else "PERMISSIVE (malus)"
    
    # ========================================
    # PERSISTENCE & VALIDATION (v2.4.0)
    # ========================================
    
    def to_dict(self) -> dict:
        """Export settings to dictionary for JSON serialization.
        
        Returns:
            Dictionary with all setting values
        
        Example:
            >>> settings = GameSettings()
            >>> data = settings.to_dict()
            >>> data['difficulty_level']
            1
        
        Version: v2.4.0
        """
        return {
            "deck_type": self.deck_type,
            "difficulty_level": self.difficulty_level,
            "draw_count": self.draw_count,
            "max_time_game": self.max_time_game,
            "shuffle_discards": self.shuffle_discards,
            "command_hints_enabled": self.command_hints_enabled,
            "scoring_enabled": self.scoring_enabled,
            "timer_strict_mode": self.timer_strict_mode,
        }
    
    def load_from_dict(self, data: dict) -> None:
        """Load settings from dictionary and reapply preset (anti-cheat).
        
        This method loads settings from JSON and then reapplies the difficulty
        preset to enforce lock rules. This prevents manual JSON editing to
        bypass tournament restrictions.
        
        Args:
            data: Dictionary with setting values
        
        Example:
            >>> settings = GameSettings()
            >>> data = {"difficulty_level": 5, "draw_count": 1}  # Cheating attempt
            >>> settings.load_from_dict(data)
            >>> settings.draw_count  # 3 (preset enforced, not 1)
        
        Anti-cheat:
            If user manually edits JSON to set Level 5 with draw_count=1,
            the preset system will override it back to 3 (locked value).
        
        Version: v2.4.0
        """
        # Load all values from dictionary
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Reapply difficulty preset to enforce locks (anti-cheat)
        if hasattr(self, 'difficulty_level'):
            self.apply_difficulty_preset(self.difficulty_level)
