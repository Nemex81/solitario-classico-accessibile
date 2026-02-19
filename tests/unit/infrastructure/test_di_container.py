"""Unit tests for DIContainer."""

import pytest

from src.application.commands import CommandHistory
from src.application.game_controller import GameController
from src.domain.rules.move_validator import MoveValidator
from src.domain.services.game_service import GameService
from src.infrastructure.di_container import (
    DIContainer,
    get_container,
    reset_container,
)
from src.presentation.game_formatter import GameFormatter

pytestmark = pytest.mark.gui


class TestDIContainer:
    """Test suite for DIContainer."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.container = DIContainer()

    def test_initialization(self) -> None:
        """Test container initializes with empty instances."""
        assert len(self.container._instances) == 0

    def test_get_move_validator(self) -> None:
        """Test getting MoveValidator instance."""
        validator = self.container.get_move_validator()

        assert isinstance(validator, MoveValidator)

    def test_get_move_validator_singleton(self) -> None:
        """Test MoveValidator is a singleton."""
        validator1 = self.container.get_move_validator()
        validator2 = self.container.get_move_validator()

        assert validator1 is validator2

    def test_get_game_service(self) -> None:
        """Test getting GameService instance."""
        service = self.container.get_game_service()

        assert isinstance(service, GameService)
        assert isinstance(service.validator, MoveValidator)

    def test_get_game_service_singleton(self) -> None:
        """Test GameService is a singleton."""
        service1 = self.container.get_game_service()
        service2 = self.container.get_game_service()

        assert service1 is service2

    def test_get_game_service_uses_same_validator(self) -> None:
        """Test GameService uses container's validator."""
        validator = self.container.get_move_validator()
        service = self.container.get_game_service()

        assert service.validator is validator

    def test_get_formatter_default_language(self) -> None:
        """Test getting formatter with default language."""
        formatter = self.container.get_formatter()

        assert isinstance(formatter, GameFormatter)
        assert formatter.language == "it"

    def test_get_formatter_custom_language(self) -> None:
        """Test getting formatter with custom language."""
        formatter = self.container.get_formatter(language="en")

        assert formatter.language == "en"

    def test_get_formatter_caches_by_language(self) -> None:
        """Test formatter is cached per language."""
        formatter_it1 = self.container.get_formatter("it")
        formatter_it2 = self.container.get_formatter("it")
        formatter_en = self.container.get_formatter("en")

        assert formatter_it1 is formatter_it2
        assert formatter_it1 is not formatter_en

    def test_get_command_history(self) -> None:
        """Test getting CommandHistory instance."""
        history = self.container.get_command_history()

        assert isinstance(history, CommandHistory)

    def test_get_command_history_singleton(self) -> None:
        """Test CommandHistory is a singleton."""
        history1 = self.container.get_command_history()
        history2 = self.container.get_command_history()

        assert history1 is history2

    def test_get_game_controller(self) -> None:
        """Test getting GameController instance."""
        controller = self.container.get_game_controller()

        assert isinstance(controller, GameController)

    def test_get_game_controller_singleton(self) -> None:
        """Test GameController is a singleton."""
        controller1 = self.container.get_game_controller()
        controller2 = self.container.get_game_controller()

        assert controller1 is controller2

    def test_get_game_controller_uses_container_dependencies(self) -> None:
        """Test GameController uses container's dependencies."""
        service = self.container.get_game_service()
        formatter = self.container.get_formatter("it")
        controller = self.container.get_game_controller()

        assert controller.game_service is service
        assert controller.formatter is formatter

    def test_reset_clears_instances(self) -> None:
        """Test reset clears all instances."""
        self.container.get_move_validator()
        self.container.get_game_service()

        self.container.reset()

        assert len(self.container._instances) == 0

    def test_reset_creates_new_instances(self) -> None:
        """Test instances are new after reset."""
        validator1 = self.container.get_move_validator()

        self.container.reset()

        validator2 = self.container.get_move_validator()
        assert validator1 is not validator2

    def test_has_instance(self) -> None:
        """Test has_instance method."""
        assert self.container.has_instance("move_validator") is False

        self.container.get_move_validator()

        assert self.container.has_instance("move_validator") is True

    def test_controller_different_languages(self) -> None:
        """Test controllers for different languages are different."""
        controller_it = self.container.get_game_controller("it")
        controller_en = self.container.get_game_controller("en")

        assert controller_it is not controller_en
        assert controller_it.formatter.language == "it"
        assert controller_en.formatter.language == "en"


class TestGlobalContainer:
    """Test suite for global container functions."""

    def teardown_method(self) -> None:
        """Clean up global container after each test."""
        reset_container()

    def test_get_container_creates_instance(self) -> None:
        """Test get_container creates new instance."""
        container = get_container()

        assert isinstance(container, DIContainer)

    def test_get_container_returns_singleton(self) -> None:
        """Test get_container returns same instance."""
        container1 = get_container()
        container2 = get_container()

        assert container1 is container2

    def test_reset_container_clears_global(self) -> None:
        """Test reset_container creates new instance on next call."""
        container1 = get_container()

        reset_container()

        container2 = get_container()
        assert container1 is not container2
