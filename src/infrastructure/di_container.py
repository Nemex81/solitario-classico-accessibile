"""Dependency injection container."""

from src.application.game_controller import GameController
from src.domain.rules.move_validator import MoveValidator
from src.domain.services.game_service import GameService
from src.presentation.game_formatter import GameFormatter


class DIContainer:
    """Simple dependency injection container."""

    def __init__(self) -> None:
        """Initialize the DI container."""
        self._instances: dict[str, object] = {}

    def get_move_validator(self) -> MoveValidator:
        """Get or create MoveValidator instance."""
        if "move_validator" not in self._instances:
            self._instances["move_validator"] = MoveValidator()
        return self._instances["move_validator"]  # type: ignore

    def get_game_service(self) -> GameService:
        """Get or create GameService instance."""
        if "game_service" not in self._instances:
            validator = self.get_move_validator()
            self._instances["game_service"] = GameService(validator)
        return self._instances["game_service"]  # type: ignore

    def get_formatter(self, language: str = "it") -> GameFormatter:
        """Get or create GameFormatter instance."""
        key = f"formatter_{language}"
        if key not in self._instances:
            self._instances[key] = GameFormatter(language)
        return self._instances[key]  # type: ignore

    def get_game_controller(self) -> GameController:
        """Get or create GameController instance."""
        if "game_controller" not in self._instances:
            service = self.get_game_service()
            formatter = self.get_formatter()
            self._instances["game_controller"] = GameController(service, formatter)
        return self._instances["game_controller"]  # type: ignore

    def clear(self) -> None:
        """Clear all cached instances."""
        self._instances.clear()
