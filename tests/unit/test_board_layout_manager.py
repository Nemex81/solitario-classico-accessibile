"""Unit tests for board_layout_manager.py — BoardLayoutManager.

Covers:
  - calculate_layout returns 13 entries (indices 0-12)
  - Stock at column 0, Waste at column 1, Foundation at columns 3-6
  - Tableau in bottom zone (y > top zone)
  - Card dimensions respect aspect ratio and theme scale
  - get_card_rect returns None for out-of-range / unknown pile
  - get_card_rect for fanned tableau: offsets accumulate correctly
  - get_card_rect for non-fanned piles: same position regardless of index
  - Minimum card height / width guard against tiny panels
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from src.infrastructure.ui.board_layout_manager import BoardLayoutManager, PileGeometry
from src.infrastructure.ui.visual_theme import THEME_GRANDE, THEME_STANDARD


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@dataclass
class _FakeCard:
    face_up: bool


def _tableau_pile(*face_up_flags: bool) -> list[_FakeCard]:
    return [_FakeCard(face_up=f) for f in face_up_flags]


# Standard panel size used throughout most tests
_W, _H = 800, 600


@pytest.fixture
def manager() -> BoardLayoutManager:
    return BoardLayoutManager()


@pytest.fixture
def layout(manager: BoardLayoutManager) -> dict[int, PileGeometry]:
    return manager.calculate_layout(_W, _H, THEME_STANDARD)


# ---------------------------------------------------------------------------
# calculate_layout — completeness
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCalculateLayoutCompleteness:
    def test_returns_13_piles(self, layout: dict[int, PileGeometry]) -> None:
        assert len(layout) == 13

    def test_all_pile_indices_present(self, layout: dict[int, PileGeometry]) -> None:
        assert set(layout.keys()) == set(range(13))

    def test_all_entries_are_pile_geometry(self, layout: dict[int, PileGeometry]) -> None:
        for v in layout.values():
            assert isinstance(v, PileGeometry)


# ---------------------------------------------------------------------------
# calculate_layout — positional logic
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCalculateLayoutPositions:
    def test_stock_is_leftmost_top(self, layout: dict[int, PileGeometry]) -> None:
        """Stock (12) must be at the leftmost column in the top zone."""
        stock = layout[12]
        waste = layout[11]
        assert stock.x < waste.x

    def test_waste_second_column(self, layout: dict[int, PileGeometry]) -> None:
        """Waste (11) must be to the right of Stock and left of foundations."""
        waste = layout[11]
        foundation_0 = layout[7]
        assert waste.x < foundation_0.x

    def test_foundations_are_rightmost(self, layout: dict[int, PileGeometry]) -> None:
        """Foundations 7-10 (columns 3-6) must all be to the right of waste."""
        waste_x = layout[11].x
        for fi in range(4):
            assert layout[7 + fi].x > waste_x

    def test_tableau_below_top_zone(self, layout: dict[int, PileGeometry]) -> None:
        """Tableau piles 0-6 must have a larger y than the top-zone piles."""
        top_y = layout[12].y
        for i in range(7):
            assert layout[i].y > top_y

    def test_tableau_columns_ordered_left_to_right(
        self, layout: dict[int, PileGeometry]
    ) -> None:
        for i in range(6):
            assert layout[i].x < layout[i + 1].x

    def test_top_zone_same_y_for_stock_waste(self, layout: dict[int, PileGeometry]) -> None:
        assert layout[12].y == layout[11].y

    def test_top_zone_same_y_for_all_foundations(self, layout: dict[int, PileGeometry]) -> None:
        y_ref = layout[7].y
        for fi in range(1, 4):
            assert layout[7 + fi].y == y_ref


# ---------------------------------------------------------------------------
# calculate_layout — card dimensions
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCalculateLayoutCardDimensions:
    def test_card_aspect_ratio_approx_5_7(self, layout: dict[int, PileGeometry]) -> None:
        """All cards must approximate the 5:7 playing-card aspect ratio within 20%."""
        for geom in layout.values():
            ratio = geom.card_width / geom.card_height
            # 5/7 ≈ 0.714; allow ±20% tolerance for integer rounding
            assert 0.5 < ratio < 0.9, f"bad ratio {ratio} for {geom}"

    def test_same_card_size_for_all_piles(self, layout: dict[int, PileGeometry]) -> None:
        widths = {g.card_width for g in layout.values()}
        heights = {g.card_height for g in layout.values()}
        assert len(widths) == 1
        assert len(heights) == 1

    def test_theme_grande_produces_larger_cards(self, manager: BoardLayoutManager) -> None:
        layout_std = manager.calculate_layout(_W, _H, THEME_STANDARD)
        layout_big = manager.calculate_layout(_W, _H, THEME_GRANDE)
        assert layout_big[0].card_width > layout_std[0].card_width

    def test_min_card_height_is_respected(self, manager: BoardLayoutManager) -> None:
        """Even a tiny panel must produce cards at least 30px tall."""
        layout = manager.calculate_layout(100, 80, THEME_STANDARD)
        for geom in layout.values():
            assert geom.card_height >= BoardLayoutManager._MIN_CARD_HEIGHT

    def test_fan_offsets_set_for_tableau(self, layout: dict[int, PileGeometry]) -> None:
        """Tableau piles must have non-zero fan offsets."""
        for i in range(7):
            assert layout[i].fan_offset_face_up > 0
            assert layout[i].fan_offset_face_down > 0

    def test_no_fan_offset_for_foundation(self, layout: dict[int, PileGeometry]) -> None:
        for fi in range(4):
            assert layout[7 + fi].fan_offset_face_up == 0
            assert layout[7 + fi].fan_offset_face_down == 0


# ---------------------------------------------------------------------------
# get_card_rect
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGetCardRect:
    def test_returns_none_for_unknown_pile(
        self, manager: BoardLayoutManager, layout: dict[int, PileGeometry]
    ) -> None:
        pile: list[Any] = [_FakeCard(face_up=True)]
        assert manager.get_card_rect(99, 0, pile, layout) is None

    def test_returns_none_for_negative_card_idx(
        self, manager: BoardLayoutManager, layout: dict[int, PileGeometry]
    ) -> None:
        pile: list[Any] = [_FakeCard(face_up=True)]
        assert manager.get_card_rect(0, -1, pile, layout) is None

    def test_returns_none_for_card_idx_out_of_range(
        self, manager: BoardLayoutManager, layout: dict[int, PileGeometry]
    ) -> None:
        pile: list[Any] = [_FakeCard(face_up=True)]
        assert manager.get_card_rect(0, 1, pile, layout) is None

    def test_returns_tuple_of_4(
        self, manager: BoardLayoutManager, layout: dict[int, PileGeometry]
    ) -> None:
        pile: list[Any] = [_FakeCard(face_up=True)]
        rect = manager.get_card_rect(0, 0, pile, layout)
        assert isinstance(rect, tuple) and len(rect) == 4

    def test_foundation_cards_same_position_regardless_of_index(
        self, manager: BoardLayoutManager, layout: dict[int, PileGeometry]
    ) -> None:
        """Foundation is non-fanned: card 0 and card 2 share the same x,y."""
        pile: list[Any] = [_FakeCard(False)] * 5
        rect0 = manager.get_card_rect(7, 0, pile, layout)
        rect2 = manager.get_card_rect(7, 2, pile, layout)
        assert rect0 == rect2

    def test_tableau_second_card_is_below_first_face_down(
        self, manager: BoardLayoutManager, layout: dict[int, PileGeometry]
    ) -> None:
        """Second card in a tableau with a face-down first card must be offset down."""
        pile = _tableau_pile(False, True)
        rect0 = manager.get_card_rect(0, 0, pile, layout)
        rect1 = manager.get_card_rect(0, 1, pile, layout)
        assert rect0 is not None and rect1 is not None
        assert rect1[1] > rect0[1]  # y increases

    def test_tableau_face_up_offset_larger_than_face_down(
        self, manager: BoardLayoutManager, layout: dict[int, PileGeometry]
    ) -> None:
        """Face-up fan offset must be larger than face-down."""
        geom = layout[0]
        assert geom.fan_offset_face_up > geom.fan_offset_face_down

    def test_tableau_y_accumulates_proportionally(
        self, manager: BoardLayoutManager, layout: dict[int, PileGeometry]
    ) -> None:
        """With all face-up cards, each successive card adds fan_offset_face_up."""
        pile = _tableau_pile(True, True, True)
        geom = layout[0]
        rect0 = manager.get_card_rect(0, 0, pile, layout)
        rect1 = manager.get_card_rect(0, 1, pile, layout)
        rect2 = manager.get_card_rect(0, 2, pile, layout)
        assert rect0 is not None and rect1 is not None and rect2 is not None
        delta01 = rect1[1] - rect0[1]
        delta12 = rect2[1] - rect1[1]
        assert delta01 == geom.fan_offset_face_up
        assert delta12 == geom.fan_offset_face_up

    def test_stock_all_cards_same_rect(
        self, manager: BoardLayoutManager, layout: dict[int, PileGeometry]
    ) -> None:
        pile: list[Any] = [_FakeCard(False)] * 10
        rects = [manager.get_card_rect(12, i, pile, layout) for i in range(10)]
        assert all(r == rects[0] for r in rects)


# ---------------------------------------------------------------------------
# calculate_adaptive_tableau_layout
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCalculateAdaptiveTableauLayout:
    def test_adaptive_layout_cards_within_panel_height(
        self, manager: BoardLayoutManager
    ) -> None:
        """Scaled layout for 13 face-up cards per pile must not exceed panel_height."""
        panel_h = 400
        base = manager.calculate_layout(600, panel_h, THEME_STANDARD)
        pile_depths: dict[int, tuple[int, int]] = {i: (0, 13) for i in range(7)}
        adapted = manager.calculate_adaptive_tableau_layout(base, pile_depths, panel_h)
        for i in range(7):
            geom = adapted[i]
            total = geom.y + 13 * geom.fan_offset_face_up + geom.card_height
            assert total <= panel_h, f"pile {i}: total={total} exceeds panel_height={panel_h}"

    def test_adaptive_layout_y_top_unchanged(
        self, manager: BoardLayoutManager
    ) -> None:
        """y (top edge) of each tableau pile must never be altered by adaption."""
        panel_h = 400
        base = manager.calculate_layout(600, panel_h, THEME_STANDARD)
        pile_depths: dict[int, tuple[int, int]] = {i: (5, 8) for i in range(7)}
        adapted = manager.calculate_adaptive_tableau_layout(base, pile_depths, panel_h)
        for i in range(7):
            assert adapted[i].y == base[i].y, f"pile {i}: y changed from {base[i].y} to {adapted[i].y}"

    def test_adaptive_layout_no_overflow_not_modified(
        self, manager: BoardLayoutManager
    ) -> None:
        """When no pile would overflow, offsets must remain identical to base."""
        panel_h = 1080
        base = manager.calculate_layout(1920, panel_h, THEME_STANDARD)
        pile_depths: dict[int, tuple[int, int]] = {i: (0, 2) for i in range(7)}
        adapted = manager.calculate_adaptive_tableau_layout(base, pile_depths, panel_h)
        for i in range(7):
            assert adapted[i].fan_offset_face_up == base[i].fan_offset_face_up, (
                f"pile {i}: fan_offset_face_up changed"
            )
            assert adapted[i].fan_offset_face_down == base[i].fan_offset_face_down, (
                f"pile {i}: fan_offset_face_down changed"
            )

    def test_adaptive_layout_minimum_offsets_enforced(
        self, manager: BoardLayoutManager
    ) -> None:
        """Even with extreme constraints, minimum fan offsets must be preserved."""
        panel_h = 50
        base = manager.calculate_layout(800, panel_h, THEME_STANDARD)
        pile_depths: dict[int, tuple[int, int]] = {i: (3, 5) for i in range(7)}
        adapted = manager.calculate_adaptive_tableau_layout(base, pile_depths, panel_h)
        for i in range(7):
            assert adapted[i].fan_offset_face_down >= 2, (
                f"pile {i}: fan_offset_face_down={adapted[i].fan_offset_face_down} < _MIN=2"
            )
            assert adapted[i].fan_offset_face_up >= 4, (
                f"pile {i}: fan_offset_face_up={adapted[i].fan_offset_face_up} < _MIN=4"
            )

    def test_adaptive_layout_non_tableau_piles_unchanged(
        self, manager: BoardLayoutManager
    ) -> None:
        """Non-tableau piles (7-12) must be copied verbatim from base_layout."""
        panel_h = 400
        base = manager.calculate_layout(600, panel_h, THEME_STANDARD)
        pile_depths: dict[int, tuple[int, int]] = {i: (3, 8) for i in range(7)}
        adapted = manager.calculate_adaptive_tableau_layout(base, pile_depths, panel_h)
        for i in range(7, 13):
            assert adapted[i] == base[i], f"non-tableau pile {i} was unexpectedly modified"

    def test_adaptive_layout_raises_on_incomplete_layout(
        self, manager: BoardLayoutManager
    ) -> None:
        """ValueError must be raised when base_layout is missing pile keys."""
        incomplete: dict[int, PileGeometry] = {
            0: PileGeometry(x=0, y=0, card_width=50, card_height=70, fan_offset_face_up=10, fan_offset_face_down=4)
        }
        with pytest.raises(ValueError):
            manager.calculate_adaptive_tableau_layout(incomplete, {}, 600)
