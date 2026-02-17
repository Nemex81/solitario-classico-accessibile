"""Game end reason classification for outcome tracking."""

from enum import Enum


class EndReason(Enum):
    """Reasons why a game session ended.
    
    Used to differentiate victory/defeat types for statistics and UI.
    Replaces boolean is_victory with fine-grained classification.
    """
    
    # ========================================
    # VICTORIES
    # ========================================
    VICTORY = "victory"
    """Victory within time limit (or timer disabled)."""
    
    VICTORY_OVERTIME = "victory_overtime"
    """Victory after time limit expired (PERMISSIVE mode only)."""
    
    # ========================================
    # VOLUNTARY ABANDONS
    # ========================================
    ABANDON_NEW_GAME = "abandon_new_game"
    """User started new game during active game."""
    
    ABANDON_EXIT = "abandon_exit"
    """User pressed ESC/menu and confirmed abandon."""
    
    # ========================================
    # NON-VOLUNTARY ABANDONS
    # ========================================
    ABANDON_APP_CLOSE = "abandon_app_close"
    """App closed during game (no clean exit)."""
    
    # ========================================
    # TIMER DEFEATS
    # ========================================
    TIMEOUT_STRICT = "timeout_strict"
    """Time limit expired in STRICT mode (auto-stop)."""
    
    def is_victory(self) -> bool:
        """Check if reason represents a victory."""
        return self in (EndReason.VICTORY, EndReason.VICTORY_OVERTIME)
    
    def is_defeat(self) -> bool:
        """Check if reason represents a defeat."""
        return not self.is_victory()
    
    def is_abandon(self) -> bool:
        """Check if reason is any type of abandon."""
        return self in (
            EndReason.ABANDON_NEW_GAME,
            EndReason.ABANDON_EXIT,
            EndReason.ABANDON_APP_CLOSE
        )
    
    def is_timeout(self) -> bool:
        """Check if reason is timeout-related."""
        return self in (EndReason.TIMEOUT_STRICT, EndReason.VICTORY_OVERTIME)
