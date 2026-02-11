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
"""

from typing import Tuple


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
        
        v2.0.0: Extended to 5 levels with auto-adjustment constraints:
        - Levels 1-3: Full flexibility (existing behavior)
        - Level 4 (Esperto): Timer ≥30min, draw_count ≥2, shuffle locked to invert
        - Level 5 (Maestro): Timer 15-30min, draw_count=3, shuffle locked to invert
        
        When cycling to levels 4-5, settings are auto-adjusted if needed.
        
        Returns:
            Tuple[bool, str]: (success, message with adjustments if any)
        
        Examples:
            >>> settings.difficulty_level = 3
            >>> settings.cycle_difficulty()
            (True, "Difficoltà impostata a: Livello 4 - Esperto...")
        """
        if not self.validate_not_running():
            return (False, "Non puoi modificare la difficoltà durante una partita!")
        
        # Cycle: 1 -> 2 -> 3 -> 4 -> 5 -> 1
        self.difficulty_level = (self.difficulty_level % 5) + 1
        
        # Get level name
        level_name = self.get_difficulty_display()
        base_message = f"Difficoltà impostata a: {level_name}."
        
        # Apply constraints for levels 4-5
        adjustments = []
        
        if self.difficulty_level == 4:
            # Level 4: Timer ≥30min, draw ≥2, shuffle locked
            if self.max_time_game > 0 and self.max_time_game < 1800:
                self.max_time_game = 1800  # 30 minutes
                adjustments.append("Timer aumentato a 30 minuti")
            
            if self.draw_count < 2:
                self.draw_count = 2
                adjustments.append("Carte pescate impostate a 2")
            
            if self.shuffle_discards:
                self.shuffle_discards = False
                adjustments.append("Riciclo impostato su Inversione")
        
        elif self.difficulty_level == 5:
            # Level 5: Timer 15-30min, draw=3, shuffle locked
            if self.max_time_game > 0:
                if self.max_time_game < 900:
                    self.max_time_game = 900  # 15 minutes
                    adjustments.append("Timer aumentato a 15 minuti")
                elif self.max_time_game > 1800:
                    self.max_time_game = 1800  # 30 minutes
                    adjustments.append("Timer ridotto a 30 minuti")
            
            if self.draw_count != 3:
                self.draw_count = 3
                adjustments.append("Carte pescate impostate a 3")
            
            if self.shuffle_discards:
                self.shuffle_discards = False
                adjustments.append("Riciclo impostato su Inversione")
        
        # Build final message
        if adjustments:
            adjustment_text = "; ".join(adjustments)
            return (True, f"{base_message} Regolazioni automatiche: {adjustment_text}.")
        
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
        """Validate draw_count against current difficulty level.
        
        Returns:
            Validation message if adjustments needed, empty string otherwise
        """
        if self.difficulty_level == 4 and self.draw_count < 2:
            self.draw_count = 2
            return "Livello Esperto richiede almeno 2 carte."
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
