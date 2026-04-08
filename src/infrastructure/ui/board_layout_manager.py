"""BoardLayoutManager — calculates pixel geometry for all 13 piles.

Pile index convention (matches BoardState.piles):
  [0-6]   Tableau columns (left → right)
  [7-10]  Foundation piles  (pile_semi[0-3])
  [11]    Waste  (pile_scarti)
  [12]    Stock  (pile_mazzo)

Layout strategy
---------------
The board is divided horizontally into two zones:

  TOP ZONE  (height = card_height + top_margin * 2):
    col 0  → Stock (pile 12)
    col 1  → Waste (pile 11)
    col 3-6 → Foundation piles 7-10  (gap at col 2)

  BOTTOM ZONE  (remaining height):
    col 0-6 → Tableau piles 0-6

Card aspect ratio: 5 : 7  (≈ 2.5 : 3.5 standard playing-card ratio).

All coordinates are in pixels relative to the panel top-left corner.
The class is pure Python (no wx dependency) so it is fully unit-testable.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.infrastructure.ui.visual_theme import ThemeProperties


@dataclass
class PileGeometry:
    """Pixel geometry for a single pile.

    Attributes:
        x: Left edge of the pile's first card.
        y: Top edge of the pile's first card (top card position).
        card_width: Card width in pixels.
        card_height: Card height in pixels.
        fan_offset_face_up: Vertical offset between consecutive face-up cards.
        fan_offset_face_down: Vertical offset between consecutive face-down cards.
    """

    x: int
    y: int
    card_width: int
    card_height: int
    fan_offset_face_up: int
    fan_offset_face_down: int


# Number of visual columns across the board
_NUM_COLS = 7


class BoardLayoutManager:
    """Computes and caches the pixel layout for a given panel size and theme.

    Call :meth:`calculate_layout` whenever the panel is resized.
    """

    # Minimum card height to prevent degenerate rendering
    _MIN_CARD_HEIGHT = 30

    def calculate_layout(
        self,
        panel_width: int,
        panel_height: int,
        theme: ThemeProperties,
    ) -> dict[int, PileGeometry]:
        """Calculate pixel geometry for all 13 piles.

        The layout adapts to any panel size; card dimensions are derived from
        the available width divided by seven columns, then scaled by the theme
        ``card_scale`` factor.

        Args:
            panel_width: Panel width in pixels.
            panel_height: Panel height in pixels.
            theme: Current visual theme (provides card_scale).

        Returns:
            Mapping of pile index (0-12) to PileGeometry.
        """
        h_gap = max(4, panel_width // 80)
        v_gap = max(4, panel_height // 60)
        top_margin = v_gap

        # Base card width from 7 equal columns
        raw_card_w = (panel_width - h_gap * (_NUM_COLS + 1)) / _NUM_COLS
        card_w = max(20, int(raw_card_w * theme.card_scale))
        # 5:7 aspect ratio
        card_h = max(self._MIN_CARD_HEIGHT, int(card_w * 7 / 5))

        fan_face_up = card_h // 3
        fan_face_down = max(4, card_h // 5)

        # Column x positions (7 equal columns, full-width columns)
        col_base_w = (panel_width - h_gap * (_NUM_COLS + 1)) // _NUM_COLS
        col_x = [h_gap + i * (col_base_w + h_gap) for i in range(_NUM_COLS)]

        top_zone_y = top_margin
        bottom_zone_y = top_margin + card_h + v_gap

        layout: dict[int, PileGeometry] = {}

        # Tableau piles 0-6 (bottom zone)
        for i in range(7):
            layout[i] = PileGeometry(
                x=col_x[i],
                y=bottom_zone_y,
                card_width=card_w,
                card_height=card_h,
                fan_offset_face_up=fan_face_up,
                fan_offset_face_down=fan_face_down,
            )

        # Foundation piles 7-10 (top zone, columns 3-6)
        for fi in range(4):
            layout[7 + fi] = PileGeometry(
                x=col_x[3 + fi],
                y=top_zone_y,
                card_width=card_w,
                card_height=card_h,
                fan_offset_face_up=0,   # stacked — no fan
                fan_offset_face_down=0,
            )

        # Waste pile 11 (top zone, column 1)
        layout[11] = PileGeometry(
            x=col_x[1],
            y=top_zone_y,
            card_width=card_w,
            card_height=card_h,
            fan_offset_face_up=0,
            fan_offset_face_down=0,
        )

        # Stock pile 12 (top zone, column 0)
        layout[12] = PileGeometry(
            x=col_x[0],
            y=top_zone_y,
            card_width=card_w,
            card_height=card_h,
            fan_offset_face_up=0,
            fan_offset_face_down=0,
        )

        return layout

    def get_card_rect(
        self,
        pile_idx: int,
        card_idx: int,
        pile: list[object],
        layout: dict[int, PileGeometry],
    ) -> tuple[int, int, int, int] | None:
        """Return the bounding rect  ``(x, y, width, height)`` for a specific card.

        For non-fanned piles (foundation, waste, stock) all cards share the
        same position; only the top card is visible.

        For fanned piles (tableau) each card is offset vertically by the fan
        spacing, taking into account whether each card below it is face-up or
        face-down.

        Args:
            pile_idx: Pile index (0-12).
            card_idx: Card position within the pile (0 = bottom).
            pile: List of card objects in the pile (used to count face-up/down
                cards below ``card_idx``).
            layout: Output of :meth:`calculate_layout`.

        Returns:
            ``(x, y, width, height)`` tuple, or ``None`` if *pile_idx* is not
            in *layout* or *card_idx* is out of range.
        """
        geom = layout.get(pile_idx)
        if geom is None:
            return None
        if card_idx < 0 or card_idx >= len(pile):
            return None

        x = geom.x
        y = geom.y

        # Non-fanned piles: all cards at origin
        if geom.fan_offset_face_up == 0 and geom.fan_offset_face_down == 0:
            return (x, y, geom.card_width, geom.card_height)

        # Tableau: accumulate offsets for cards below card_idx
        for ci in range(card_idx):
            card = pile[ci]
            face_up: bool = bool(getattr(card, "face_up", False))
            if face_up:
                y += geom.fan_offset_face_up
            else:
                y += geom.fan_offset_face_down

        return (x, y, geom.card_width, geom.card_height)
