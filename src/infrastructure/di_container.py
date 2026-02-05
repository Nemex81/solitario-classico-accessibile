"""Dependency injection container."""

from typing import Any, Dict, cast

from src.application.commands import CommandHistory
from src.application.game_controller import GameController
from src.domain.rules.move_validator import MoveValidator
from src.domain.services.game_service import GameService
from src.presentation.game_formatter import GameFormatter


class DIContainer:
    """
    Simple dependency injection container.

    Manages creation and lifecycle of application components,
    ensuring proper dependency wiring and singleton behavior
    where appropriate.
    """

    def __init__(self) -> None:
        """Initialize the container with empty instances cache."""
        self._instances: Dict[str, Any] = {}

    def get_move_validator(self) -> MoveValidator:
        """
        Get or create MoveValidator instance.

        Returns:
            Singleton MoveValidator instance
        """
        if "move_validator" not in self._instances:
            self._instances["move_validator"] = MoveValidator()
        return cast(MoveValidator, self._instances["move_validator"])

    def get_game_service(self) -> GameService:
        """
        Get or create GameService instance.

        Returns:
            Singleton GameService instance with injected validator
        """
        if "game_service" not in self._instances:
            validator = self.get_move_validator()
            self._instances["game_service"] = GameService(validator)
        return cast(GameService, self._instances["game_service"])

    def get_formatter(self, language: str = "it") -> GameFormatter:
        """
        Get or create GameFormatter instance.

        Args:
            language: Language for formatting (default: Italian)

        Returns:
            GameFormatter instance for specified language
        """
        key = f"formatter_{language}"
        if key not in self._instances:
            self._instances[key] = GameFormatter(language)
        return cast(GameFormatter, self._instances[key])

    def get_command_history(self, max_size: int = 100) -> CommandHistory:
        """
        Get or create CommandHistory instance.

        Args:
            max_size: Maximum history size

        Returns:
            Singleton CommandHistory instance
        """
        if "command_history" not in self._instances:
            self._instances["command_history"] = CommandHistory(max_size)
        return cast(CommandHistory, self._instances["command_history"])

    def get_game_controller(self, language: str = "it") -> GameController:
        """
        Get or create GameController instance.

        Args:
            language: Language for formatting

        Returns:
            Singleton GameController instance with injected dependencies
        """
        key = f"game_controller_{language}"
        if key not in self._instances:
            service = self.get_game_service()
            formatter = self.get_formatter(language)
            self._instances[key] = GameController(service, formatter)
        return cast(GameController, self._instances[key])

    def reset(self) -> None:
        """
        Reset all instances.

        Useful for testing or when needing fresh instances.
        """
        self._instances.clear()

    def has_instance(self, key: str) -> bool:
        """
        Check if an instance exists.

        Args:
            key: Instance key to check

        Returns:
            True if instance exists
        """
        return key in self._instances


# Global container instance
_container: DIContainer | None = None


def get_container() -> DIContainer:
    """
    Get global DIContainer instance.

    Returns:
        Singleton DIContainer instance
    """
    global _container
    if _container is None:
        _container = DIContainer()
    return _container


def reset_container() -> None:
    """Reset global container instance."""
    global _container
    _container = None
