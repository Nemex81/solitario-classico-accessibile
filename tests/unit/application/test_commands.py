"""Unit tests for Command pattern implementation."""

import pytest

from src.application.commands import (
    Command,
    CommandHistory,
    DrawCommand,
    MoveCommand,
    RecycleCommand,
)
from src.domain.models.game_state import GameState, GameStatus


class TestMoveCommand:
    """Test suite for MoveCommand."""

    def test_initialization(self) -> None:
        """Test MoveCommand initialization."""
        command = MoveCommand("tableau_0", "foundation_0", card_count=1)

        assert command.source == "tableau_0"
        assert command.target == "foundation_0"
        assert command.card_count == 1

    def test_execute_stores_previous_state(self) -> None:
        """Test that execute stores previous state."""
        command = MoveCommand("tableau_0", "foundation_0")
        state = GameState(status=GameStatus.IN_PROGRESS)

        command.execute(state)

        assert command.previous_state is state

    def test_undo_returns_previous_state(self) -> None:
        """Test that undo returns stored previous state."""
        command = MoveCommand("tableau_0", "foundation_0")
        original_state = GameState(status=GameStatus.IN_PROGRESS, score=50)
        modified_state = GameState(status=GameStatus.IN_PROGRESS, score=100)

        command.execute(original_state)
        result = command.undo(modified_state)

        assert result is original_state

    def test_undo_without_execute_returns_current(self) -> None:
        """Test undo without execute returns current state."""
        command = MoveCommand("tableau_0", "foundation_0")
        state = GameState(status=GameStatus.IN_PROGRESS)

        result = command.undo(state)

        assert result is state

    def test_description(self) -> None:
        """Test command description."""
        command = MoveCommand("tableau_0", "foundation_0", card_count=3)

        assert "3" in command.description
        assert "tableau_0" in command.description
        assert "foundation_0" in command.description


class TestDrawCommand:
    """Test suite for DrawCommand."""

    def test_execute_stores_previous_state(self) -> None:
        """Test that execute stores previous state."""
        command = DrawCommand()
        state = GameState(status=GameStatus.IN_PROGRESS)

        command.execute(state)

        assert command.previous_state is state

    def test_undo_returns_previous_state(self) -> None:
        """Test that undo returns stored previous state."""
        command = DrawCommand()
        original_state = GameState(status=GameStatus.IN_PROGRESS)
        modified_state = GameState(status=GameStatus.WON)

        command.execute(original_state)
        result = command.undo(modified_state)

        assert result is original_state

    def test_description(self) -> None:
        """Test command description."""
        command = DrawCommand()

        assert "Pescare" in command.description or "mazzo" in command.description


class TestRecycleCommand:
    """Test suite for RecycleCommand."""

    def test_execute_stores_previous_state(self) -> None:
        """Test that execute stores previous state."""
        command = RecycleCommand()
        state = GameState(status=GameStatus.IN_PROGRESS)

        command.execute(state)

        assert command.previous_state is state

    def test_undo_returns_previous_state(self) -> None:
        """Test that undo returns stored previous state."""
        command = RecycleCommand()
        original_state = GameState(status=GameStatus.IN_PROGRESS)
        modified_state = GameState(status=GameStatus.WON)

        command.execute(original_state)
        result = command.undo(modified_state)

        assert result is original_state

    def test_description(self) -> None:
        """Test command description."""
        command = RecycleCommand()

        assert "Rimescolare" in command.description or "scarti" in command.description


class TestCommandHistory:
    """Test suite for CommandHistory."""

    def test_initialization(self) -> None:
        """Test CommandHistory initialization."""
        history = CommandHistory()

        assert history.position == -1
        assert len(history.history) == 0
        assert history.can_undo() is False
        assert history.can_redo() is False

    def test_execute_adds_to_history(self) -> None:
        """Test that execute adds command to history."""
        history = CommandHistory()
        command = MoveCommand("tableau_0", "foundation_0")
        state = GameState()

        history.execute(command, state)

        assert len(history.history) == 1
        assert history.position == 0

    def test_can_undo_after_execute(self) -> None:
        """Test can_undo returns True after execute."""
        history = CommandHistory()
        command = MoveCommand("tableau_0", "foundation_0")
        state = GameState()

        history.execute(command, state)

        assert history.can_undo() is True

    def test_undo_decrements_position(self) -> None:
        """Test undo decrements position."""
        history = CommandHistory()
        command = MoveCommand("tableau_0", "foundation_0")
        state = GameState()

        history.execute(command, state)
        history.undo(state)

        assert history.position == -1
        assert history.can_undo() is False

    def test_can_redo_after_undo(self) -> None:
        """Test can_redo returns True after undo."""
        history = CommandHistory()
        command = MoveCommand("tableau_0", "foundation_0")
        state = GameState()

        history.execute(command, state)
        history.undo(state)

        assert history.can_redo() is True

    def test_redo_increments_position(self) -> None:
        """Test redo increments position."""
        history = CommandHistory()
        command = MoveCommand("tableau_0", "foundation_0")
        state = GameState()

        history.execute(command, state)
        history.undo(state)
        history.redo(state)

        assert history.position == 0
        assert history.can_redo() is False

    def test_execute_after_undo_clears_redo_stack(self) -> None:
        """Test that executing after undo clears redo history."""
        history = CommandHistory()
        state = GameState()

        history.execute(MoveCommand("t0", "f0"), state)
        history.execute(MoveCommand("t1", "f1"), state)
        history.undo(state)  # Go back one
        history.execute(MoveCommand("t2", "f2"), state)  # New command

        assert len(history.history) == 2
        assert history.can_redo() is False

    def test_multiple_undo_redo(self) -> None:
        """Test multiple undo and redo operations."""
        history = CommandHistory()
        state = GameState()

        history.execute(MoveCommand("t0", "f0"), state)
        history.execute(MoveCommand("t1", "f1"), state)
        history.execute(MoveCommand("t2", "f2"), state)

        assert history.position == 2

        history.undo(state)
        assert history.position == 1

        history.undo(state)
        assert history.position == 0

        history.redo(state)
        assert history.position == 1

    def test_undo_returns_state(self) -> None:
        """Test undo returns the previous state."""
        history = CommandHistory()
        original_state = GameState(score=100)

        history.execute(MoveCommand("t0", "f0"), original_state)
        result = history.undo(GameState(score=200))

        assert result is original_state

    def test_max_size_limit(self) -> None:
        """Test history respects max size limit."""
        history = CommandHistory(max_size=3)
        state = GameState()

        for i in range(5):
            history.execute(MoveCommand(f"t{i}", f"f{i}"), state)

        assert len(history.history) == 3
        assert history.position == 2

    def test_clear_history(self) -> None:
        """Test clearing history."""
        history = CommandHistory()
        state = GameState()

        history.execute(MoveCommand("t0", "f0"), state)
        history.execute(MoveCommand("t1", "f1"), state)
        history.clear()

        assert len(history.history) == 0
        assert history.position == -1
        assert history.can_undo() is False

    def test_get_undo_description(self) -> None:
        """Test get_undo_description returns command description."""
        history = CommandHistory()
        command = MoveCommand("tableau_0", "foundation_0")
        state = GameState()

        history.execute(command, state)
        description = history.get_undo_description()

        assert description is not None
        assert "tableau_0" in description

    def test_get_undo_description_empty(self) -> None:
        """Test get_undo_description returns None when empty."""
        history = CommandHistory()

        assert history.get_undo_description() is None

    def test_get_redo_description(self) -> None:
        """Test get_redo_description returns command description."""
        history = CommandHistory()
        command = MoveCommand("tableau_1", "foundation_1")
        state = GameState()

        history.execute(command, state)
        history.undo(state)
        description = history.get_redo_description()

        assert description is not None
        assert "tableau_1" in description

    def test_get_redo_description_empty(self) -> None:
        """Test get_redo_description returns None when no redo available."""
        history = CommandHistory()
        command = MoveCommand("t0", "f0")
        state = GameState()

        history.execute(command, state)

        assert history.get_redo_description() is None
