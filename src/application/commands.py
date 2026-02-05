"""Command pattern for undo/redo support."""

from abc import ABC, abstractmethod
from typing import List, Optional

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

    @property
    @abstractmethod
    def description(self) -> str:
        """Get human-readable description of command."""
        pass


class MoveCommand(Command):
    """Command for moving cards."""

    def __init__(
        self,
        source: str,
        target: str,
        card_count: int = 1,
    ):
        """
        Initialize move command.

        Args:
            source: Source pile identifier (e.g., "tableau_0", "waste")
            target: Target pile identifier (e.g., "foundation_0", "tableau_1")
            card_count: Number of cards to move
        """
        self.source = source
        self.target = target
        self.card_count = card_count
        self.previous_state: Optional[GameState] = None

    def execute(self, state: GameState) -> GameState:
        """
        Execute move command and return new state.

        Args:
            state: Current game state

        Returns:
            New game state after move
        """
        self.previous_state = state
        # In real implementation, this would perform the move using GameService
        # For now, we return the state unchanged (placeholder for future integration)
        return state

    def undo(self, state: GameState) -> GameState:
        """
        Undo move command and return previous state.

        Args:
            state: Current game state (unused, returns stored state)

        Returns:
            Previous game state
        """
        if self.previous_state is None:
            return state
        return self.previous_state

    @property
    def description(self) -> str:
        """Get description of move command."""
        return f"Spostare {self.card_count} carte da {self.source} a {self.target}"


class DrawCommand(Command):
    """Command for drawing cards from stock."""

    def __init__(self):
        """Initialize draw command."""
        self.previous_state: Optional[GameState] = None

    def execute(self, state: GameState) -> GameState:
        """Execute draw command."""
        self.previous_state = state
        return state

    def undo(self, state: GameState) -> GameState:
        """Undo draw command."""
        if self.previous_state is None:
            return state
        return self.previous_state

    @property
    def description(self) -> str:
        """Get description of draw command."""
        return "Pescare carte dal mazzo"


class RecycleCommand(Command):
    """Command for recycling waste to stock."""

    def __init__(self):
        """Initialize recycle command."""
        self.previous_state: Optional[GameState] = None

    def execute(self, state: GameState) -> GameState:
        """Execute recycle command."""
        self.previous_state = state
        return state

    def undo(self, state: GameState) -> GameState:
        """Undo recycle command."""
        if self.previous_state is None:
            return state
        return self.previous_state

    @property
    def description(self) -> str:
        """Get description of recycle command."""
        return "Rimescolare gli scarti nel mazzo"


class CommandHistory:
    """Manages command history for undo/redo."""

    def __init__(self, max_size: int = 100):
        """
        Initialize command history.

        Args:
            max_size: Maximum number of commands to store
        """
        self.history: List[Command] = []
        self.position: int = -1
        self.max_size = max_size

    def execute(self, command: Command, state: GameState) -> GameState:
        """
        Execute command and add to history.

        Args:
            command: Command to execute
            state: Current game state

        Returns:
            New game state after execution
        """
        new_state = command.execute(state)

        # Remove any commands after current position (discard redo stack)
        self.history = self.history[: self.position + 1]
        self.history.append(command)
        self.position += 1

        # Trim history if exceeds max size
        if len(self.history) > self.max_size:
            self.history = self.history[-self.max_size :]
            self.position = len(self.history) - 1

        return new_state

    def undo(self, state: GameState) -> GameState:
        """
        Undo last command.

        Args:
            state: Current game state

        Returns:
            Game state after undo
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
            Game state after redo
        """
        if not self.can_redo():
            return state

        self.position += 1
        command = self.history[self.position]
        return command.execute(state)

    def can_undo(self) -> bool:
        """Check if undo is possible."""
        return self.position >= 0

    def can_redo(self) -> bool:
        """Check if redo is possible."""
        return self.position < len(self.history) - 1

    def clear(self) -> None:
        """Clear command history."""
        self.history = []
        self.position = -1

    def get_undo_description(self) -> Optional[str]:
        """Get description of command to undo."""
        if not self.can_undo():
            return None
        return self.history[self.position].description

    def get_redo_description(self) -> Optional[str]:
        """Get description of command to redo."""
        if not self.can_redo():
            return None
        return self.history[self.position + 1].description
