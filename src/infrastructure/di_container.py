"""Dependency injection container for Clean Architecture.

Manages creation and lifecycle of all application components
with proper dependency resolution across layers.

Provides centralized factory methods and singleton management
for domain, application, infrastructure, and presentation layers.
"""

from typing import Any, Dict, Optional, cast

# Domain imports
from src.domain.models.deck import ProtoDeck, FrenchDeck, NeapolitanDeck

# Application imports
from src.application.game_settings import GameSettings, DeckType
from src.application.timer_manager import TimerManager
from src.application.input_handler import InputHandler

# Infrastructure imports (forward references to avoid circular imports)
# ScreenReader imported conditionally in methods

# Presentation imports
from src.presentation.game_formatter import GameFormatter


class DIContainer:
    """Dependency Injection container for all application components.
    
    Manages object creation, lifecycle, and dependency resolution
    following Clean Architecture principles.
    
    Lifetime Management:
    - Singletons: GameSettings, InputHandler, ScreenReader, GameFormatter
    - Factories: Deck, Table, Rules, TimerManager (per-game instances)
    
    Usage:
        >>> container = DIContainer()
        >>> settings = container.get_settings()
        >>> deck = container.get_deck(settings.deck_type)
        >>> formatter = container.get_formatter()
    
    Attributes:
        _instances: Dict of singleton instances
        _settings: GameSettings singleton
    """
    
    def __init__(self) -> None:
        """Initialize empty container."""
        self._instances: Dict[str, Any] = {}
        self._settings: Optional[GameSettings] = None
    
    # ========================================================================
    # APPLICATION LAYER
    # ========================================================================
    
    def get_settings(self) -> GameSettings:
        """Get or create GameSettings singleton.
        
        Settings persist across games for consistent configuration.
        
        Returns:
            GameSettings singleton instance
        """
        if self._settings is None:
            self._settings = GameSettings()
        return self._settings
    
    def set_settings(self, settings: GameSettings) -> None:
        """Override settings (useful for testing or loading from file).
        
        Args:
            settings: GameSettings to use
        """
        self._settings = settings
    
    def get_timer_manager(self, settings: Optional[GameSettings] = None) -> TimerManager:
        """Create new TimerManager instance.
        
        TimerManager is per-game (not singleton) to allow proper
        reset between games.
        
        Args:
            settings: GameSettings to use (None = use container's settings)
        
        Returns:
            New TimerManager instance
        """
        if settings is None:
            settings = self.get_settings()
        
        return TimerManager(
            minutes=settings.timer_minutes,
            warning_callback=None  # Set by caller if needed
        )
    
    def get_input_handler(self) -> InputHandler:
        """Get or create InputHandler singleton.
        
        InputHandler is stateless and can be shared across games.
        
        Returns:
            InputHandler singleton
        """
        if "input_handler" not in self._instances:
            self._instances["input_handler"] = InputHandler()
        return cast(InputHandler, self._instances["input_handler"])
    
    # ========================================================================
    # DOMAIN LAYER
    # ========================================================================
    
    def get_deck(self, deck_type: Optional[str] = None) -> ProtoDeck:
        """Create deck based on type.
        
        Factory method for deck creation. Always returns new instance
        to ensure clean state for new games.
        
        Args:
            deck_type: "french" or "neapolitan" (None = use settings)
        
        Returns:
            New deck instance (FrenchDeck or NeapolitanDeck)
        
        Raises:
            ValueError: If deck_type is invalid
        """
        if deck_type is None:
            settings = self.get_settings()
            deck_type = settings.deck_type
        
        if deck_type == "french":
            return FrenchDeck()
        elif deck_type == "neapolitan":
            return NeapolitanDeck()
        else:
            raise ValueError(f"Unknown deck type: {deck_type}")
    
    # ========================================================================
    # INFRASTRUCTURE LAYER
    # ========================================================================
    
    def get_screen_reader(self) -> Any:
        """Get or create ScreenReader singleton.
        
        ScreenReader manages TTS connection and should be shared
        across the application.
        
        Returns:
            ScreenReader singleton (late import to avoid circular deps)
        """
        if "screen_reader" not in self._instances:
            # Late import to avoid circular dependency
            from src.infrastructure.accessibility.screen_reader import ScreenReader
            self._instances["screen_reader"] = ScreenReader()
        return self._instances["screen_reader"]
    
    # ========================================================================
    # PRESENTATION LAYER
    # ========================================================================
    
    def get_formatter(self, language: str = "it") -> GameFormatter:
        """Get or create GameFormatter singleton.
        
        GameFormatter is stateless and can be shared.
        
        Args:
            language: Output language (default "it" for Italian)
        
        Returns:
            GameFormatter singleton
        """
        key = f"formatter_{language}"
        if key not in self._instances:
            self._instances[key] = GameFormatter()
        return cast(GameFormatter, self._instances[key])
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def reset(self) -> None:
        """Reset all singleton instances.
        
        Useful for testing or complete application restart.
        Settings are preserved unless explicitly cleared.
        """
        self._instances.clear()
    
    def reset_all(self) -> None:
        """Reset all instances including settings.
        
        Complete container reset to factory defaults.
        """
        self._instances.clear()
        self._settings = None


# ============================================================================
# GLOBAL CONTAINER MANAGEMENT
# ============================================================================

_global_container: Optional[DIContainer] = None


def get_container() -> DIContainer:
    """Get global DIContainer instance.
    
    Provides application-wide access to the DI container.
    Lazily initializes on first access.
    
    Returns:
        Global DIContainer singleton
    
    Example:
        >>> from src.infrastructure.di_container import get_container
        >>> container = get_container()
        >>> settings = container.get_settings()
    """
    global _global_container
    if _global_container is None:
        _global_container = DIContainer()
    return _global_container


def reset_container() -> None:
    """Reset global container.
    
    Clears all singleton instances but preserves settings.
    Useful for testing or partial resets.
    
    Example:
        >>> reset_container()
        >>> container = get_container()  # Fresh instances
    """
    global _global_container
    if _global_container is not None:
        _global_container.reset()


def reset_container_complete() -> None:
    """Completely reset global container including settings.
    
    Full reset to factory state. Use with caution.
    
    Example:
        >>> reset_container_complete()
        >>> container = get_container()  # Brand new container
    """
    global _global_container
    _global_container = None
