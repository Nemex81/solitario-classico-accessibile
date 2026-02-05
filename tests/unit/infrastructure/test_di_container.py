"""Unit tests for DIContainer."""

import pytest

from src.application.game_controller import GameController
from src.domain.rules.move_validator import MoveValidator
from src.domain.services.game_service import GameService
from src.infrastructure.di_container import DIContainer
from src.presentation.game_formatter import GameFormatter


class TestDIContainer:
    """Test suite for DIContainer."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.container = DIContainer()

    def test_initialization(self) -> None:
        """Test container initialization."""
        assert self.container._instances == {}

    def test_get_move_validator(self) -> None:
        """Test getting MoveValidator instance."""
        validator = self.container.get_move_validator()

        assert isinstance(validator, MoveValidator)

    def test_get_move_validator_singleton(self) -> None:
        """Test MoveValidator is singleton."""
        validator1 = self.container.get_move_validator()
        validator2 = self.container.get_move_validator()

        assert validator1 is validator2

    def test_get_game_service(self) -> None:
        """Test getting GameService instance."""
        service = self.container.get_game_service()

        assert isinstance(service, GameService)

    def test_get_game_service_singleton(self) -> None:
        """Test GameService is singleton."""
        service1 = self.container.get_game_service()
        service2 = self.container.get_game_service()

        assert service1 is service2

    def test_get_formatter(self) -> None:
        """Test getting GameFormatter instance."""
        formatter = self.container.get_formatter()

        assert isinstance(formatter, GameFormatter)
        assert formatter.language == "it"

    def test_get_formatter_with_language(self) -> None:
        """Test getting GameFormatter with specific language."""
        formatter = self.container.get_formatter(language="en")

        assert isinstance(formatter, GameFormatter)
        assert formatter.language == "en"

    def test_get_formatter_singleton_per_language(self) -> None:
        """Test GameFormatter is singleton per language."""
        formatter1_it = self.container.get_formatter("it")
        formatter2_it = self.container.get_formatter("it")
        formatter_en = self.container.get_formatter("en")

        assert formatter1_it is formatter2_it
        assert formatter1_it is not formatter_en

    def test_get_game_controller(self) -> None:
        """Test getting GameController instance."""
        controller = self.container.get_game_controller()

        assert isinstance(controller, GameController)
        assert isinstance(controller.game_service, GameService)
        assert isinstance(controller.formatter, GameFormatter)

    def test_get_game_controller_singleton(self) -> None:
        """Test GameController is singleton."""
        controller1 = self.container.get_game_controller()
        controller2 = self.container.get_game_controller()

        assert controller1 is controller2

    def test_game_controller_uses_same_service(self) -> None:
        """Test GameController uses same service instance."""
        service = self.container.get_game_service()
        controller = self.container.get_game_controller()

        assert controller.game_service is service

    def test_game_controller_uses_same_formatter(self) -> None:
        """Test GameController uses same formatter instance."""
        formatter = self.container.get_formatter()
        controller = self.container.get_game_controller()

        assert controller.formatter is formatter

    def test_clear(self) -> None:
        """Test clearing container instances."""
        self.container.get_move_validator()
        self.container.get_game_service()
        self.container.get_formatter()

        self.container.clear()

        assert self.container._instances == {}

    def test_clear_creates_new_instances(self) -> None:
        """Test clear allows creating new instances."""
        validator1 = self.container.get_move_validator()

        self.container.clear()
        validator2 = self.container.get_move_validator()

        assert validator1 is not validator2
