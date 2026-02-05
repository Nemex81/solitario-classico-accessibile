"""Command pattern for undo/redo support."""

from abc import ABC, abstractmethod
from typing import List

from src.domain.models.game_state import GameState


class Command(ABC):
    """Abstract command interface."""

    @abstractmethod
    def execute(self, state: GameState) -> GameState:
        """Execute command and return new state."""
        pass

    @abstractmethod
    def undo(self, state: GameState) -> GameState:
        """Undo command and return previous state."""
        pass


class MoveCommand(Command):
    """Command for moving cards."""

    def __init__(self, source: str, target: str, card_count: int = 1):
        """
        Initialize move command.

        Args:
            source: Source pile identifier
            target: Target pile identifier
            card_count: Number of cards to move
        """
        self.source = source
        self.target = target
        self.card_count = card_count
        self.previous_state: GameState | None = None

    def execute(self, state: GameState) -> GameState:
        """
        Execute move command.

        Args:
            state: Current game state

        Returns:
            New game state after move
        """
        self.previous_state = state
        # Implementation would go here
        # For now, just return the state
        return state

    def undo(self, state: GameState) -> GameState:
        """
        Undo move command.

        Args:
            state: Current game state

        Returns:
            Previous game state
        """
        if self.previous_state is None:
            return state
        return self.previous_state


class CommandHistory:
    """Manages command history for undo/redo."""

    def __init__(self) -> None:
        """Initialize command history."""
        self.history: List[Command] = []
        self.position: int = -1

    def execute(self, command: Command, state: GameState) -> GameState:
        """
        Execute command and add to history.

        Args:
            command: Command to execute
            state: Current game state

        Returns:
            New game state after command execution
        """
        new_state = command.execute(state)

        # Remove any commands after current position
        self.history = self.history[: self.position + 1]
        self.history.append(command)
        self.position += 1

        return new_state

    def undo(self, state: GameState) -> GameState:
        """
        Undo last command.

        Args:
            state: Current game state

        Returns:
            Previous game state
        """
        if not self.can_undo():
            return state

        command = self.history[self.position]
        self.position -= 1
        return command.undo(state)

    def redo(self, state: GameState) -> GameState:
        """
        Redo previously undone command.

        Args:
            state: Current game state

        Returns:
            Next game state
        """
        if not self.can_redo():
            return state

        self.position += 1
        command = self.history[self.position]
        return command.execute(state)

    def can_undo(self) -> bool:
        """
        Check if undo is possible.

        Returns:
            True if undo is available
        """
        return self.position >= 0

    def can_redo(self) -> bool:
        """
        Check if redo is possible.

        Returns:
            True if redo is available
        """
        return self.position < len(self.history) - 1

    def clear(self) -> None:
        """Clear command history."""
        self.history = []
        self.position = -1
