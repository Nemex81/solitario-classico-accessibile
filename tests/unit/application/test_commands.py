"""Unit tests for Command pattern."""

import pytest

from src.application.commands import Command, CommandHistory, MoveCommand
from src.domain.models.game_state import GameState, GameStatus


class TestMoveCommand:
    """Test suite for MoveCommand."""

    def test_initialization(self) -> None:
        """Test command initialization."""
        cmd = MoveCommand("tableau_0", "foundation_0", card_count=1)

        assert cmd.source == "tableau_0"
        assert cmd.target == "foundation_0"
        assert cmd.card_count == 1
        assert cmd.previous_state is None

    def test_execute_saves_previous_state(self) -> None:
        """Test that execute saves previous state."""
        state = GameState(status=GameStatus.IN_PROGRESS, moves_count=10)
        cmd = MoveCommand("source", "target")

        result = cmd.execute(state)

        assert cmd.previous_state is state
        assert isinstance(result, GameState)

    def test_undo_returns_previous_state(self) -> None:
        """Test undo returns previous state."""
        state1 = GameState(status=GameStatus.IN_PROGRESS, moves_count=10)
        state2 = GameState(status=GameStatus.IN_PROGRESS, moves_count=11)
        cmd = MoveCommand("source", "target")

        cmd.execute(state1)
        result = cmd.undo(state2)

        assert result is state1

    def test_undo_without_execute(self) -> None:
        """Test undo without previous execute."""
        state = GameState(status=GameStatus.IN_PROGRESS)
        cmd = MoveCommand("source", "target")

        result = cmd.undo(state)

        assert result is state


class TestCommandHistory:
    """Test suite for CommandHistory."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.history = CommandHistory()

    def test_initialization(self) -> None:
        """Test history initialization."""
        assert len(self.history.history) == 0
        assert self.history.position == -1

    def test_execute_adds_to_history(self) -> None:
        """Test executing command adds to history."""
        state = GameState()
        cmd = MoveCommand("source", "target")

        self.history.execute(cmd, state)

        assert len(self.history.history) == 1
        assert self.history.position == 0

    def test_execute_multiple_commands(self) -> None:
        """Test executing multiple commands."""
        state = GameState()
        cmd1 = MoveCommand("s1", "t1")
        cmd2 = MoveCommand("s2", "t2")

        self.history.execute(cmd1, state)
        self.history.execute(cmd2, state)

        assert len(self.history.history) == 2
        assert self.history.position == 1

    def test_can_undo_initially_false(self) -> None:
        """Test can_undo returns False initially."""
        assert not self.history.can_undo()

    def test_can_undo_after_execute(self) -> None:
        """Test can_undo returns True after execute."""
        state = GameState()
        cmd = MoveCommand("source", "target")

        self.history.execute(cmd, state)

        assert self.history.can_undo()

    def test_can_redo_initially_false(self) -> None:
        """Test can_redo returns False initially."""
        assert not self.history.can_redo()

    def test_can_redo_after_undo(self) -> None:
        """Test can_redo returns True after undo."""
        state = GameState()
        cmd = MoveCommand("source", "target")

        self.history.execute(cmd, state)
        self.history.undo(state)

        assert self.history.can_redo()

    def test_undo_decrements_position(self) -> None:
        """Test undo decrements position."""
        state = GameState()
        cmd = MoveCommand("source", "target")

        self.history.execute(cmd, state)
        initial_position = self.history.position
        self.history.undo(state)

        assert self.history.position == initial_position - 1

    def test_redo_increments_position(self) -> None:
        """Test redo increments position."""
        state = GameState()
        cmd = MoveCommand("source", "target")

        self.history.execute(cmd, state)
        self.history.undo(state)
        initial_position = self.history.position
        self.history.redo(state)

        assert self.history.position == initial_position + 1

    def test_execute_after_undo_clears_forward_history(self) -> None:
        """Test executing new command after undo clears forward history."""
        state = GameState()
        cmd1 = MoveCommand("s1", "t1")
        cmd2 = MoveCommand("s2", "t2")
        cmd3 = MoveCommand("s3", "t3")

        self.history.execute(cmd1, state)
        self.history.execute(cmd2, state)
        self.history.undo(state)
        self.history.execute(cmd3, state)

        assert len(self.history.history) == 2
        assert self.history.history[0] is cmd1
        assert self.history.history[1] is cmd3

    def test_undo_without_commands(self) -> None:
        """Test undo without commands returns same state."""
        state = GameState()

        result = self.history.undo(state)

        assert result is state

    def test_redo_without_undone_commands(self) -> None:
        """Test redo without undone commands returns same state."""
        state = GameState()

        result = self.history.redo(state)

        assert result is state

    def test_clear_resets_history(self) -> None:
        """Test clear resets history."""
        state = GameState()
        cmd = MoveCommand("source", "target")

        self.history.execute(cmd, state)
        self.history.clear()

        assert len(self.history.history) == 0
        assert self.history.position == -1

    def test_full_undo_redo_cycle(self) -> None:
        """Test full undo/redo cycle."""
        state1 = GameState(moves_count=1)
        state2 = GameState(moves_count=2)
        state3 = GameState(moves_count=3)
        cmd1 = MoveCommand("s1", "t1")
        cmd2 = MoveCommand("s2", "t2")

        # Execute commands via history
        self.history.execute(cmd1, state1)
        self.history.execute(cmd2, state2)

        # Undo both
        result1 = self.history.undo(state3)
        result2 = self.history.undo(result1)

        # Redo both
        result3 = self.history.redo(result2)
        result4 = self.history.redo(result3)

        assert self.history.position == 1
        assert result2 is state1
        assert result3 is state1  # Redo first command returns state1
