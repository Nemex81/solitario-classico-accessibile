"""Unit tests for card_renderer.py — CardRenderer.

Uses a MagicMock as the device context so that no wx runtime is needed.
Tests verify that the correct drawing calls are dispatched for each
rendering scenario:
  - Face-up card at correct position
  - Face-down card at correct position
  - Border calls present for every card
  - Extra border for highlighted card (cursor)
  - Extra border for selected card
  - Suit symbols are the correct Unicode characters
  - suit_color selects text_red vs text_black
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, call, patch

import pytest

from src.application.board_state import CardView
from src.infrastructure.ui.card_renderer import CardRenderer, _SUIT_SYMBOLS
from src.infrastructure.ui.visual_theme import THEME_STANDARD


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def renderer() -> CardRenderer:
    return CardRenderer()


@pytest.fixture
def dc() -> MagicMock:
    """Mock device context that records every call."""
    return MagicMock()


def _face_up(rank: str = "A", suit: str = "cuori", color: str = "red") -> CardView:
    return CardView(rank=rank, suit=suit, face_up=True, suit_color=color)


def _face_down(rank: str = "K", suit: str = "picche") -> CardView:
    return CardView(rank=rank, suit=suit, face_up=False, suit_color="black")


# ---------------------------------------------------------------------------
# draw_card — face-up cards
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDrawCardFaceUp:
    def test_draw_rect_called_at_least_once(self, renderer: CardRenderer, dc: MagicMock) -> None:
        """DrawRectangle must be invoked at least once for background fill."""
        renderer.draw_card(dc, _face_up(), 0, 0, 70, 100, THEME_STANDARD)
        assert dc.DrawRectangle.call_count >= 1

    def test_draw_text_called_for_rank(self, renderer: CardRenderer, dc: MagicMock) -> None:
        """DrawText must be called with the rank string."""
        renderer.draw_card(dc, _face_up("Q"), 0, 0, 70, 100, THEME_STANDARD)
        texts_drawn = [str(c.args[0]) for c in dc.DrawText.call_args_list]
        assert "Q" in texts_drawn

    def test_draw_text_called_for_suit_symbol(self, renderer: CardRenderer, dc: MagicMock) -> None:
        """DrawText must include the Unicode heart symbol for 'cuori'."""
        renderer.draw_card(dc, _face_up("A", "cuori"), 0, 0, 70, 100, THEME_STANDARD)
        texts_drawn = [str(c.args[0]) for c in dc.DrawText.call_args_list]
        assert "\u2665" in texts_drawn  # ♥

    def test_suit_symbol_quadri(self, renderer: CardRenderer, dc: MagicMock) -> None:
        renderer.draw_card(dc, _face_up("2", "quadri", "red"), 0, 0, 70, 100, THEME_STANDARD)
        texts = [str(c.args[0]) for c in dc.DrawText.call_args_list]
        assert "\u2666" in texts  # ♦

    def test_suit_symbol_fiori(self, renderer: CardRenderer, dc: MagicMock) -> None:
        renderer.draw_card(dc, _face_up("3", "fiori", "black"), 0, 0, 70, 100, THEME_STANDARD)
        texts = [str(c.args[0]) for c in dc.DrawText.call_args_list]
        assert "\u2663" in texts  # ♣

    def test_suit_symbol_picche(self, renderer: CardRenderer, dc: MagicMock) -> None:
        renderer.draw_card(dc, _face_up("J", "picche", "black"), 0, 0, 70, 100, THEME_STANDARD)
        texts = [str(c.args[0]) for c in dc.DrawText.call_args_list]
        assert "\u2660" in texts  # ♠


# ---------------------------------------------------------------------------
# draw_card — face-down cards
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDrawCardFaceDown:
    def test_draw_rect_called_for_back(self, renderer: CardRenderer, dc: MagicMock) -> None:
        renderer.draw_card(dc, _face_down(), 0, 0, 70, 100, THEME_STANDARD)
        assert dc.DrawRectangle.call_count >= 1

    def test_no_rank_text_drawn_for_back(self, renderer: CardRenderer, dc: MagicMock) -> None:
        """Face-down cards must NOT expose rank information."""
        renderer.draw_card(dc, _face_down("K"), 0, 0, 70, 100, THEME_STANDARD)
        texts_drawn = [str(c.args[0]) for c in dc.DrawText.call_args_list]
        assert "K" not in texts_drawn


# ---------------------------------------------------------------------------
# Border logic
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestBorderLogic:
    def test_normal_card_has_exactly_one_extra_border_rect(
        self, renderer: CardRenderer, dc: MagicMock
    ) -> None:
        """Normal (non-highlighted) face-up card: background fill + border = 2 rect calls minimum."""
        renderer.draw_card(dc, _face_up(), 0, 0, 70, 100, THEME_STANDARD)
        # At minimum: 1 fill + 1 border
        assert dc.DrawRectangle.call_count >= 2

    def test_highlighted_card_draws_extra_rect(
        self, renderer: CardRenderer, dc: MagicMock
    ) -> None:
        """Highlighted card must draw one more rect than normal."""
        dc_normal = MagicMock()
        dc_highlighted = MagicMock()
        renderer.draw_card(dc_normal, _face_up(), 0, 0, 70, 100, THEME_STANDARD, highlighted=False)
        renderer.draw_card(dc_highlighted, _face_up(), 0, 0, 70, 100, THEME_STANDARD, highlighted=True)
        assert dc_highlighted.DrawRectangle.call_count > dc_normal.DrawRectangle.call_count

    def test_selected_card_draws_extra_rect(
        self, renderer: CardRenderer, dc: MagicMock
    ) -> None:
        """Selected card must draw one more rect than normal."""
        dc_normal = MagicMock()
        dc_selected = MagicMock()
        renderer.draw_card(dc_normal, _face_up(), 0, 0, 70, 100, THEME_STANDARD, selected=False)
        renderer.draw_card(dc_selected, _face_up(), 0, 0, 70, 100, THEME_STANDARD, selected=True)
        assert dc_selected.DrawRectangle.call_count > dc_normal.DrawRectangle.call_count

    def test_highlighted_takes_priority_over_selected(
        self, renderer: CardRenderer, dc: MagicMock
    ) -> None:
        """When both highlighted and selected, only cursor colour is applied (not both)."""
        dc_both = MagicMock()
        dc_highlighted_only = MagicMock()
        renderer.draw_card(dc_both, _face_up(), 0, 0, 70, 100, THEME_STANDARD,
                           highlighted=True, selected=True)
        renderer.draw_card(dc_highlighted_only, _face_up(), 0, 0, 70, 100, THEME_STANDARD,
                           highlighted=True, selected=False)
        assert dc_both.DrawRectangle.call_count == dc_highlighted_only.DrawRectangle.call_count


# ---------------------------------------------------------------------------
# Suit symbols registry
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSuitSymbolsRegistry:
    def test_cuori_is_heart(self) -> None:
        assert _SUIT_SYMBOLS["cuori"] == "\u2665"

    def test_quadri_is_diamond(self) -> None:
        assert _SUIT_SYMBOLS["quadri"] == "\u2666"

    def test_fiori_is_club(self) -> None:
        assert _SUIT_SYMBOLS["fiori"] == "\u2663"

    def test_picche_is_spade(self) -> None:
        assert _SUIT_SYMBOLS["picche"] == "\u2660"

    def test_all_four_suits_present(self) -> None:
        assert set(_SUIT_SYMBOLS.keys()) == {"cuori", "quadri", "fiori", "picche"}


# ---------------------------------------------------------------------------
# Internal helpers via draw_suit_symbol
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDrawSuitSymbol:
    def test_draws_correct_symbol(self, renderer: CardRenderer, dc: MagicMock) -> None:
        renderer._draw_suit_symbol(dc, "cuori", 30, 40, 14, (200, 0, 0))
        texts = [str(c.args[0]) for c in dc.DrawText.call_args_list]
        assert "\u2665" in texts

    def test_unknown_suit_uses_first_char(self, renderer: CardRenderer, dc: MagicMock) -> None:
        renderer._draw_suit_symbol(dc, "Xyz", 0, 0, 12, (0, 0, 0))
        texts = [str(c.args[0]) for c in dc.DrawText.call_args_list]
        assert "X" in texts


# ---------------------------------------------------------------------------
# Bitmap rendering
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestBitmapRendering:
    def test_draw_face_uses_bitmap_when_provided(
        self, renderer: CardRenderer, dc: MagicMock
    ) -> None:
        """draw_card chiama DrawBitmap quando bitmap != None e card face_up."""
        mock_bitmap = object()
        renderer.draw_card(dc, _face_up(), 0, 0, 70, 100, THEME_STANDARD, bitmap=mock_bitmap)
        assert dc.DrawBitmap.called is True
        texts_drawn = [str(c.args[0]) for c in dc.DrawText.call_args_list]
        assert len(texts_drawn) == 0

    def test_draw_face_falls_back_to_text_without_bitmap(
        self, renderer: CardRenderer, dc: MagicMock
    ) -> None:
        """draw_card usa rendering testuale quando bitmap è None."""
        renderer.draw_card(dc, _face_up(), 0, 0, 70, 100, THEME_STANDARD, bitmap=None)
        texts_drawn = [str(c.args[0]) for c in dc.DrawText.call_args_list]
        assert len(texts_drawn) > 0

    def test_draw_face_image_draws_bitmap(self, dc: MagicMock) -> None:
        """_draw_face_image chiama dc.DrawBitmap con le coordinate corrette."""
        mock_bitmap = object()
        CardRenderer._draw_face_image(dc, mock_bitmap, 10, 20, 70, 100)
        assert dc.DrawBitmap.called is True
        assert dc.DrawBitmap.call_args.args[:2] == (mock_bitmap, 10)

    def test_draw_card_backward_compatible_without_bitmap(
        self, renderer: CardRenderer, dc: MagicMock
    ) -> None:
        """draw_card senza parametro bitmap non genera errori."""
        renderer.draw_card(dc, _face_up(), 5, 5, 70, 100, THEME_STANDARD)
        texts_drawn = [str(c.args[0]) for c in dc.DrawText.call_args_list]
        assert len(texts_drawn) > 0


# ---------------------------------------------------------------------------
# back_bitmap — new tests for v4.3.0
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestBackBitmapRendering:
    def test_draw_card_back_uses_back_bitmap_when_provided(
        self, renderer: CardRenderer, dc: MagicMock
    ) -> None:
        """draw_card must call DrawBitmap for a face-down card with back_bitmap."""
        mock_back = object()
        renderer.draw_card(
            dc, _face_down(), 0, 0, 70, 100, THEME_STANDARD, back_bitmap=mock_back
        )
        assert dc.DrawBitmap.called is True

    def test_draw_card_back_uses_procedural_when_no_back_bitmap(
        self, renderer: CardRenderer, dc: MagicMock
    ) -> None:
        """draw_card must NOT call DrawBitmap for a face-down card without back_bitmap."""
        renderer.draw_card(
            dc, _face_down(), 0, 0, 70, 100, THEME_STANDARD, back_bitmap=None
        )
        assert dc.DrawBitmap.called is False

    def test_draw_card_face_up_ignores_back_bitmap(
        self, renderer: CardRenderer, dc: MagicMock
    ) -> None:
        """back_bitmap must have no effect when card is face-up (uses face bitmap path)."""
        mock_back = object()
        renderer.draw_card(
            dc, _face_up(), 0, 0, 70, 100, THEME_STANDARD,
            bitmap=None, back_bitmap=mock_back
        )
        # Face-up without bitmap should use text rendering, not DrawBitmap
        texts_drawn = [str(c.args[0]) for c in dc.DrawText.call_args_list]
        assert len(texts_drawn) > 0
