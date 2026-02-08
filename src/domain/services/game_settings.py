"""Game settings service for configuration management.

Manages all game configuration parameters including:
- Deck type (French/Neapolitan)
- Difficulty level (1-3)
- Timer settings (OFF or 5-60 minutes)
- Shuffle mode (invert/random)

Provides validation to prevent modifications during active games.
All methods return (success, message) tuples for TTS feedback.
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
        difficulty_level: 1, 2, or 3 (cards drawn from stock)
        max_time_game: Timer in seconds (-1=OFF, or 300-3600)
        shuffle_discards: True=random shuffle, False=invert order
        game_state: Reference to game state for validation
    
    Design:
        - All modification methods return (bool, str) tuples
        - Validation blocks changes during active games
        - Timer range: OFF or 5-60 minutes (5min increments)
        - Italian language messages for TTS
    """
    
    def __init__(self, game_state=None):
        """Initialize game settings with defaults.
        
        Args:
            game_state: Optional GameState/GameService reference
        """
        # Default settings
        self.deck_type = "french"  # "french" or "neapolitan"
        self.difficulty_level = 1  # 1, 2, or 3
        self.max_time_game = -1    # -1 = OFF, or seconds (300-3600)
        self.shuffle_discards = False  # False = invert, True = random
        
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
        """Cycle difficulty level through 1 -> 2 -> 3 -> 1.
        
        Difficulty affects cards drawn from stock:
        - Level 1: Draw 1 card
        - Level 2: Draw 2 cards
        - Level 3: Draw 3 cards
        
        Returns:
            Tuple[bool, str]: (success, message)
        
        Examples:
            >>> settings.difficulty_level = 1
            >>> settings.cycle_difficulty()
            (True, "Difficoltà impostata a: Livello 2.")
        """
        if not self.validate_not_running():
            return (False, "Non puoi modificare la difficoltà durante una partita!")
        
        # Cycle: 1 -> 2 -> 3 -> 1
        self.difficulty_level = (self.difficulty_level % 3) + 1
        
        return (True, f"Difficoltà impostata a: Livello {self.difficulty_level}.")
    
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
        
        Returns:
            Tuple[bool, str]: (success, message)
        
        Examples:
            >>> settings.shuffle_discards = False
            >>> settings.toggle_shuffle_mode()
            (True, "Modalità riciclo scarti impostata a: Mescolata Casuale.")
        """
        if not self.validate_not_running():
            return (False, "Non puoi modificare la modalità riciclo durante una partita!")
        
        # Toggle
        self.shuffle_discards = not self.shuffle_discards
        
        if self.shuffle_discards:
            return (True, "Modalità riciclo scarti impostata a: Mescolata Casuale.")
        else:
            return (True, "Modalità riciclo scarti impostata a: Inversione Semplice.")
    
    # ========================================
    # GETTERS (for display)
    # ========================================
    
    def get_deck_type_display(self) -> str:
        """Get human-readable deck type."""
        return "Carte Francesi" if self.deck_type == "french" else "Carte Napoletane"
    
    def get_difficulty_display(self) -> str:
        """Get human-readable difficulty."""
        return f"Livello {self.difficulty_level}"
    
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
