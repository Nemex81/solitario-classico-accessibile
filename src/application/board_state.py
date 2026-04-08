"""BoardState DTO and CardView — application/presentation boundary.

This module defines the data transfer objects that cross the boundary between
the application layer (GameplayController) and the presentation layer
(GameplayPanel). Using lightweight immutable value objects here allows the
presentation layer to render cards without importing any domain entities.

Clean Architecture note: The presentation layer must NOT import domain.Card.
All information needed for rendering is carried by CardView and BoardState.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CardView:
    """Immutable snapshot of a single card for presentation rendering.

    Attributes:
        rank: Card rank string, e.g. "A", "2" ... "10", "J", "Q", "K".
        suit: Card suit name in Italian, e.g. "cuori", "quadri", "fiori", "picche".
        face_up: True if the card is visible (face up), False if hidden (face down).
        suit_color: "red" for cuori/quadri, "black" for fiori/picche.
    """

    rank: str
    suit: str
    face_up: bool
    suit_color: str


@dataclass
class BoardState:
    """Mutable snapshot of the full game board state.

    Produced by GameplayController._build_board_state() and passed to the
    presentation layer via the on_board_changed observer callback.

    Pile index convention (matches _map_pile_to_index in gameplay_controller):
        0-6   — tableau piles (pile base)
        7-10  — foundation piles (pile semi)
        11    — waste pile (scarti)
        12    — stock pile (mazzo)

    Attributes:
        piles: 13 lists of CardView, one per pile, ordered top-to-bottom.
        cursor_pile_idx: Index (0-12) of the pile currently under the cursor.
        cursor_card_idx: Index within the current pile (0 = bottom card).
        selection_active: True if one or more cards are currently selected.
        selected_pile_idx: Index of the pile from which cards were selected,
            or None if selection is inactive.
        selected_cards: List of CardView objects currently selected,
            or None if selection is inactive.
        game_over: True if the game has ended (won or abandoned).
    """

    piles: list[list[CardView]] = field(default_factory=lambda: [[] for _ in range(13)])
    cursor_pile_idx: int = 0
    cursor_card_idx: int = 0
    selection_active: bool = False
    selected_pile_idx: int | None = None
    selected_cards: list[CardView] | None = None
    game_over: bool = False
