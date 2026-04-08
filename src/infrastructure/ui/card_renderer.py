"""CardRenderer — draws a single playing card onto a wx device context.

Separates drawing logic from layout and board management.  All visual
properties are sourced from ThemeProperties; no magic numbers in this file.

Usage example::

    renderer = CardRenderer()
    renderer.draw_card(dc, card_view, x=10, y=20, width=70, height=100,
                       theme=get_theme("standard"), highlighted=True)

Note on wx import:
    wx is imported at the top level.  In test environments the caller
    provides a mock dc object — wx itself does not need to be fully
    functional as long as the dc mock accepts attribute access.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import wx

from src.application.board_state import CardView
from src.infrastructure.ui.visual_theme import ThemeProperties

# Unicode suit symbols
_SUIT_SYMBOLS: dict[str, str] = {
    "cuori": "\u2665",
    "quadri": "\u2666",
    "fiori": "\u2663",
    "picche": "\u2660",
}


class CardRenderer:
    """Renders a single CardView onto a wx.DC.

    All methods are pure drawing operations with no state; the class is kept
    as a container for cohesion.
    """

    def draw_card(
        self,
        dc: object,
        card: CardView,
        x: int,
        y: int,
        width: int,
        height: int,
        theme: ThemeProperties,
        highlighted: bool = False,
        selected: bool = False,
    ) -> None:
        """Draw a single card at the given position.

        Args:
            dc: wx.DC (or compatible mock) to draw onto.
            card: Immutable card snapshot from the board state.
            x: Left edge pixel coordinate.
            y: Top edge pixel coordinate.
            width: Card width in pixels.
            height: Card height in pixels.
            theme: Visual properties bundle.
            highlighted: Draw cursor highlight border when True.
            selected: Draw selection border when True.
        """
        if card.face_up:
            self._draw_face(dc, card, x, y, width, height, theme)
        else:
            self._draw_back(dc, x, y, width, height, theme)

        # Always draw the normal card border
        self._draw_border(dc, x, y, width, height, theme.border_color, theme.border_width)

        # Cursor highlight has priority over selection border
        if highlighted:
            margin = theme.border_width + 1
            self._draw_border(
                dc,
                x + margin, y + margin,
                width - margin * 2, height - margin * 2,
                theme.cursor_color,
                theme.cursor_width,
            )
        elif selected:
            margin = theme.border_width + 1
            self._draw_border(
                dc,
                x + margin, y + margin,
                width - margin * 2, height - margin * 2,
                theme.selection_color,
                theme.cursor_width,
            )

    def _draw_face(
        self,
        dc: object,
        card: CardView,
        x: int,
        y: int,
        width: int,
        height: int,
        theme: ThemeProperties,
    ) -> None:
        """Fill card face and draw rank + suit symbol.

        Args:
            dc: Device context.
            card: Face-up card data.
            x, y, width, height: Bounding box.
            theme: Visual theme.
        """
        # Background
        self._set_brush(dc, theme.card_bg)
        self._draw_rect(dc, x, y, width, height)

        # Text colour based on suit
        text_color = theme.text_red if card.suit_color == "red" else theme.text_black

        # Rank in top-left corner
        self._set_text_foreground(dc, text_color)
        self._set_font(dc, theme.font_size_base, bold=True)
        self._draw_text(dc, card.rank, x + 3, y + 2)

        # Suit symbol centred
        symbol = _SUIT_SYMBOLS.get(card.suit.lower(), card.suit[:1])
        sym_size = max(theme.font_size_base, 12)
        self._set_font(dc, sym_size, bold=False)
        sym_x = x + (width - sym_size) // 2
        sym_y = y + (height - sym_size) // 2
        self._draw_text(dc, symbol, sym_x, sym_y)

    def _draw_back(
        self,
        dc: object,
        x: int,
        y: int,
        width: int,
        height: int,
        theme: ThemeProperties,
    ) -> None:
        """Fill card back with a uniform colour pattern.

        Args:
            dc: Device context.
            x, y, width, height: Bounding box.
            theme: Visual theme.
        """
        self._set_brush(dc, theme.card_back)
        self._draw_rect(dc, x, y, width, height)

        # Inner border for a subtle framed-back look
        margin = 4
        inner_color = tuple(
            min(255, c + 40) for c in theme.card_back
        )
        self._draw_border(dc, x + margin, y + margin, width - margin * 2,
                          height - margin * 2, inner_color, 1)

    # -----------------------------------------------------------------------
    # Low-level drawing helpers — thin wrappers around dc calls
    # -----------------------------------------------------------------------

    def _draw_border(
        self,
        dc: object,
        x: int,
        y: int,
        width: int,
        height: int,
        color: tuple[int, int, int] | tuple[int, ...],
        line_width: int,
    ) -> None:
        """Draw a rectangle outline.

        Args:
            dc: Device context.
            x, y: Top-left origin.
            width, height: Dimensions.
            color: RGB tuple.
            line_width: Pen width in pixels.
        """
        self._set_pen(dc, color, line_width)
        self._set_brush_transparent(dc)
        self._draw_rect(dc, x, y, width, height)

    def _draw_suit_symbol(
        self,
        dc: object,
        suit: str,
        x: int,
        y: int,
        size: int,
        color: tuple[int, int, int],
    ) -> None:
        """Draw the Unicode suit symbol centred at the given position.

        Args:
            dc: Device context.
            suit: Suit name in Italian (e.g. "cuori").
            x, y: Centre coordinates.
            size: Font size in points.
            color: RGB text colour.
        """
        symbol = _SUIT_SYMBOLS.get(suit.lower(), suit[:1])
        self._set_text_foreground(dc, color)
        self._set_font(dc, size, bold=False)
        self._draw_text(dc, symbol, x - size // 2, y - size // 2)

    # -----------------------------------------------------------------------
    # Adapter wrappers — allow test mocking without wx runtime
    # -----------------------------------------------------------------------

    @staticmethod
    def _set_brush(dc: object, color: tuple[int, int, int] | tuple[int, ...]) -> None:
        try:
            import wx
            dc.SetBrush(wx.Brush(wx.Colour(*color[:3])))  # type: ignore[attr-defined]
        except Exception:
            pass

    @staticmethod
    def _set_brush_transparent(dc: object) -> None:
        try:
            import wx
            dc.SetBrush(wx.TRANSPARENT_BRUSH)  # type: ignore[attr-defined]
        except Exception:
            pass

    @staticmethod
    def _set_pen(
        dc: object,
        color: tuple[int, int, int] | tuple[int, ...],
        width: int,
    ) -> None:
        try:
            import wx
            dc.SetPen(wx.Pen(wx.Colour(*color[:3]), width))  # type: ignore[attr-defined]
        except Exception:
            pass

    @staticmethod
    def _draw_rect(dc: object, x: int, y: int, w: int, h: int) -> None:
        try:
            dc.DrawRectangle(x, y, w, h)  # type: ignore[attr-defined]
        except Exception:
            pass

    @staticmethod
    def _set_text_foreground(
        dc: object, color: tuple[int, int, int] | tuple[int, ...]
    ) -> None:
        try:
            import wx
            dc.SetTextForeground(wx.Colour(*color[:3]))  # type: ignore[attr-defined]
        except Exception:
            pass

    @staticmethod
    def _set_font(dc: object, size: int, bold: bool = False) -> None:
        try:
            import wx
            weight = wx.FONTWEIGHT_BOLD if bold else wx.FONTWEIGHT_NORMAL
            font = wx.Font(
                size,
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                weight,
            )
            dc.SetFont(font)  # type: ignore[attr-defined]
        except Exception:
            pass

    @staticmethod
    def _draw_text(dc: object, text: str, x: int, y: int) -> None:
        try:
            dc.DrawText(text, x, y)  # type: ignore[attr-defined]
        except Exception:
            pass
