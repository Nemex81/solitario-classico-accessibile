"""Application controller for game use cases."""

from typing import Optional

from src.domain.models.game_state import GameConfiguration, GameState
from src.domain.services.game_service import GameService
from src.presentation.game_formatter import GameFormatter


class GameController:
    """
    Coordinates game use cases.

    This controller bridges UI/infrastructure with domain logic,
    orchestrating game operations and state management.
    """

    def __init__(self, game_service: GameService, formatter: GameFormatter):
        """Initialize with dependencies."""
        self.game_service = game_service
        self.formatter = formatter
        self.current_state: Optional[GameState] = None

    def start_new_game(self, difficulty: str = "easy", deck_type: str = "french") -> str:
        """
        Start new game use case.

        Args:
            difficulty: Game difficulty
            deck_type: Type of deck (french/neapolitan)

        Returns:
            Formatted initial state description
        """
        config = GameConfiguration(difficulty=difficulty, deck_type=deck_type)
        self.current_state = self.game_service.new_game(config)
        return self.formatter.format_game_state(self.current_state)

    def execute_move(
        self,
        action: str,
        source_pile: Optional[str] = None,
        source_index: Optional[int] = None,
        target_pile: Optional[str] = None,
        target_index: Optional[int] = None,
    ) -> tuple[bool, str]:
        """
        Execute game move use case.

        Args:
            action: Action type ("move_to_foundation", "draw", "recycle")
            source_pile: Source pile type
            source_index: Source pile index
            target_pile: Target pile type
            target_index: Target pile index

        Returns:
            Tuple of (success, message)
        """
        if self.current_state is None:
            return False, "Nessuna partita in corso"

        try:
            if action == "move_to_foundation":
                if source_pile is None or source_index is None or target_index is None:
                    return False, "Parametri mancanti per move_to_foundation"
                self.current_state = self.game_service.move_to_foundation(
                    self.current_state, source_pile, source_index, target_index
                )
                return True, "Carta spostata alla base"

            elif action == "draw":
                self.current_state = self.game_service.draw_from_stock(self.current_state)
                return True, "Carte pescate dal mazzo"

            elif action == "recycle":
                self.current_state = self.game_service.recycle_waste(self.current_state)
                return True, "Scarti rimescolati nel mazzo"

            else:
                return False, f"Azione sconosciuta: {action}"

        except ValueError as e:
            return False, str(e)

    def get_current_state_formatted(self) -> str:
        """Get formatted current game state."""
        if self.current_state is None:
            return "Nessuna partita in corso"
        return self.formatter.format_game_state(self.current_state)

    def get_cursor_position_formatted(self) -> str:
        """Get formatted cursor position."""
        if self.current_state is None:
            return "Nessuna partita in corso"
        return self.formatter.format_cursor_position(self.current_state)
