"""Game state formatting for accessibility and UI."""

from typing import List

from src.domain.models.game_state import GameState, GameStatus


class GameFormatter:
    """
    Formats game state for presentation.

    Provides screen reader friendly descriptions and
    formatted output for UI display.
    """

    def __init__(self, language: str = "it"):
        """Initialize formatter with language preference."""
        self.language = language

    def format_game_state(self, state: GameState) -> str:
        """
        Format complete game state as text.

        Args:
            state: Current game state

        Returns:
            Formatted string describing game state
        """
        lines = []
        lines.append(f"Stato: {self._format_status(state.status)}")
        lines.append(f"Mosse: {state.moves_count}")
        lines.append(f"Punteggio: {state.score}")
        lines.append("")

        # Foundations
        lines.append("=== BASI (Foundation) ===")
        for i, foundation in enumerate(state.foundations):
            suit_name = self._get_suit_name(i)
            if foundation:
                top_card = foundation[-1]
                lines.append(f"Base {suit_name}: {len(foundation)} carte, in cima {top_card}")
            else:
                lines.append(f"Base {suit_name}: vuota")
        lines.append("")

        # Tableaus
        lines.append("=== TABLEAU ===")
        for i, tableau in enumerate(state.tableaus):
            if tableau:
                lines.append(f"Pila {i+1}: {len(tableau)} carte")
            else:
                lines.append(f"Pila {i+1}: vuota")
        lines.append("")

        # Stock and Waste
        lines.append(f"Mazzo (Stock): {len(state.stock)} carte")
        lines.append(f"Scarti (Waste): {len(state.waste)} carte")

        return "\n".join(lines)

    def format_cursor_position(self, state: GameState) -> str:
        """
        Format cursor position for screen reader.

        Args:
            state: Current game state with cursor

        Returns:
            Description of current cursor position
        """
        cursor = state.cursor
        pile_type = cursor.pile_type
        pile_index = cursor.pile_index

        if pile_type == "tableau":
            tableau = state.tableaus[pile_index]
            if tableau:
                card = (
                    tableau[cursor.card_index] if cursor.card_index < len(tableau) else tableau[-1]
                )
                return f"Tableau {pile_index + 1}, carta {cursor.card_index + 1}: {card}"
            return f"Tableau {pile_index + 1}: vuoto"

        elif pile_type == "foundation":
            foundation = state.foundations[pile_index]
            if foundation:
                return f"Base {pile_index + 1}, in cima: {foundation[-1]}"
            return f"Base {pile_index + 1}: vuota"

        elif pile_type == "stock":
            return f"Mazzo: {len(state.stock)} carte rimanenti"

        elif pile_type == "waste":
            if state.waste:
                return f"Scarti: in cima {state.waste[-1]}"
            return "Scarti: vuoto"

        return "Posizione sconosciuta"

    def format_move_result(self, success: bool, message: str) -> str:
        """
        Format move result for feedback.

        Args:
            success: Whether move was successful
            message: Result message

        Returns:
            Formatted feedback string
        """
        if success:
            return f"✓ {message}"
        return f"✗ {message}"

    def format_card_list(self, cards: List[str]) -> str:
        """
        Format list of cards for reading.

        Args:
            cards: List of card strings

        Returns:
            Comma-separated card list
        """
        if not cards:
            return "nessuna carta"
        return ", ".join(cards)

    def _format_status(self, status: "GameStatus") -> str:
        """Format game status in Italian."""
        status_map = {
            "NOT_STARTED": "Non iniziato",
            "IN_PROGRESS": "In corso",
            "WON": "Vinto!",
            "LOST": "Perso",
        }
        return status_map.get(status.name, str(status))

    def _get_suit_name(self, index: int) -> str:
        """Get suit name by foundation index."""
        suits = ["Cuori", "Quadri", "Fiori", "Picche"]
        return suits[index] if index < len(suits) else f"Seme {index}"
