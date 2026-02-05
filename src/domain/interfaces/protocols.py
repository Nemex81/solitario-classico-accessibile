"""Domain protocol interfaces."""

from typing import Protocol, Tuple

from src.domain.models.card import Card
from src.domain.models.game_state import GameConfiguration, GameState


class MoveValidatorProtocol(Protocol):
    """Interface for move validation."""

    def can_move_to_foundation(
        self,
        card: Card,
        foundation_index: int,
        state: GameState,
    ) -> bool:
        """Check if card can move to foundation."""
        ...

    def can_move_to_tableau(
        self,
        cards: Tuple[Card, ...],
        tableau_index: int,
        state: GameState,
    ) -> bool:
        """Check if cards can move to tableau."""
        ...


class GameServiceProtocol(Protocol):
    """Interface for game service."""

    def new_game(self, config: GameConfiguration) -> GameState:
        """Start new game."""
        ...

    def move_to_foundation(
        self,
        state: GameState,
        source_pile_type: str,
        source_index: int,
        foundation_index: int,
    ) -> GameState:
        """Move card to foundation."""
        ...


class FormatterProtocol(Protocol):
    """Interface for state formatting."""

    def format_game_state(self, state: GameState) -> str:
        """Format game state as string."""
        ...

    def format_cursor_position(self, state: GameState) -> str:
        """Format cursor position."""
        ...
