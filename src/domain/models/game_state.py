"""GameState immutable model."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple


class GameStatus(Enum):
    """Game status enumeration."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    WON = "won"
    LOST = "lost"


@dataclass(frozen=True)
class GameState:
    """
    Immutable game state representation.

    Represents the complete state of a Klondike solitaire game at a specific moment.
    Uses frozen dataclass to ensure immutability and prevent accidental state mutations.

    Attributes:
        foundations: Four foundation piles (Ace to King, same suit)
        tableaus: Seven tableau piles (face-up cards)
        stock: Remaining cards in stock pile
        waste: Cards drawn from stock
        status: Current game status
        moves_count: Number of moves made
        score: Current game score
    """

    foundations: Tuple[Tuple[str, ...], ...] = field(default_factory=lambda: ((), (), (), ()))
    tableaus: Tuple[Tuple[str, ...], ...] = field(
        default_factory=lambda: ((), (), (), (), (), (), ())
    )
    stock: Tuple[str, ...] = field(default_factory=tuple)
    waste: Tuple[str, ...] = field(default_factory=tuple)
    status: GameStatus = GameStatus.NOT_STARTED
    moves_count: int = 0
    score: int = 0

    def with_move(
        self,
        foundations: Optional[Tuple[Tuple[str, ...], ...]] = None,
        tableaus: Optional[Tuple[Tuple[str, ...], ...]] = None,
        stock: Optional[Tuple[str, ...]] = None,
        waste: Optional[Tuple[str, ...]] = None,
        status: Optional[GameStatus] = None,
        moves_count: Optional[int] = None,
        score: Optional[int] = None,
    ) -> "GameState":
        """
        Create a new GameState with updated fields.

        This method implements the copy-on-write pattern for immutable objects.
        Only provided fields are updated; others maintain their current values.

        Args:
            foundations: New foundation piles (optional)
            tableaus: New tableau piles (optional)
            stock: New stock pile (optional)
            waste: New waste pile (optional)
            status: New game status (optional)
            moves_count: New moves count (optional)
            score: New score (optional)

        Returns:
            New GameState instance with updated fields
        """
        return GameState(
            foundations=foundations if foundations is not None else self.foundations,
            tableaus=tableaus if tableaus is not None else self.tableaus,
            stock=stock if stock is not None else self.stock,
            waste=waste if waste is not None else self.waste,
            status=status if status is not None else self.status,
            moves_count=moves_count if moves_count is not None else self.moves_count,
            score=score if score is not None else self.score,
        )

    def is_victory(self) -> bool:
        """
        Check if game is won.

        Game is won when all 52 cards are in the foundation piles.

        Returns:
            True if game is won, False otherwise
        """
        return all(len(foundation) == 13 for foundation in self.foundations)
