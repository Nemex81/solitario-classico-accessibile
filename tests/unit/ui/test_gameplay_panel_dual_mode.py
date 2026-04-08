"""Unit tests for GameplayPanel dual-mode — Fase 6.

Tests verify:
  - toggle_display_mode switches between audio_only and visual
  - _on_board_changed updates _board_state and _nvda_info_zone
  - _build_nvda_text returns correct strings for various board states
  - set_theme updates _current_theme
  - display_mode property returns current mode
  - Observer registration happens if controller has gameplay_controller

These tests use a minimal wx.App + wx.Frame for constructing the panel
(wx.Window requires an active app), but no actual event loop is run.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

# Guard: skip entire module if wx cannot be imported
wx_available = False
try:
    import wx
    _app = wx.App(False)
    wx_available = True
except Exception:
    pass

from src.application.board_state import BoardState, CardView

pytestmark = pytest.mark.skipif(not wx_available, reason="wx not available in this environment")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_panel(display_mode: str = "audio_only", with_gc: bool = True) -> object:
    """Build a GameplayPanel inside a transient wx.Frame."""
    from src.infrastructure.ui.gameplay_panel import GameplayPanel

    global _app
    if wx.GetApp() is None:
        _app = wx.App(False)

    frame = wx.Frame(None)
    ctrl = MagicMock()
    ctrl.screen_reader = MagicMock()
    if with_gc:
        gc = MagicMock()
        gc.set_on_board_changed = MagicMock()
        ctrl.gameplay_controller = gc
    else:
        del ctrl.gameplay_controller

    panel = GameplayPanel(
        parent=frame,
        controller=ctrl,
        display_mode=display_mode,
    )
    return panel


def _empty_board_state(**kwargs: object) -> BoardState:
    defaults: dict[str, object] = {
        "piles": [[] for _ in range(13)],
        "cursor_pile_idx": 0,
        "cursor_card_idx": 0,
        "selection_active": False,
        "selected_pile_idx": None,
        "selected_cards": None,
        "game_over": False,
    }
    defaults.update(kwargs)
    return BoardState(**defaults)  # type: ignore[arg-type]


def _board_with_card(
    pile_idx: int,
    rank: str = "A",
    suit: str = "cuori",
    face_up: bool = True,
) -> BoardState:
    piles: list[list[CardView]] = [[] for _ in range(13)]
    piles[pile_idx] = [CardView(rank=rank, suit=suit, face_up=face_up, suit_color="red")]
    return _empty_board_state(piles=piles, cursor_pile_idx=pile_idx, cursor_card_idx=0)


# ---------------------------------------------------------------------------
# display_mode property
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.gui
class TestDisplayModeProperty:
    def test_default_is_audio_only(self) -> None:
        panel = _make_panel()
        assert panel.display_mode == "audio_only"

    def test_visual_mode_from_constructor(self) -> None:
        panel = _make_panel(display_mode="visual")
        assert panel.display_mode == "visual"


# ---------------------------------------------------------------------------
# toggle_display_mode
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.gui
class TestToggleDisplayMode:
    def test_toggle_audio_to_visual(self) -> None:
        panel = _make_panel("audio_only")
        panel.toggle_display_mode()
        assert panel.display_mode == "visual"

    def test_toggle_visual_to_audio(self) -> None:
        panel = _make_panel("visual")
        panel.toggle_display_mode()
        assert panel.display_mode == "audio_only"

    def test_double_toggle_returns_to_original(self) -> None:
        panel = _make_panel("audio_only")
        panel.toggle_display_mode()
        panel.toggle_display_mode()
        assert panel.display_mode == "audio_only"


# ---------------------------------------------------------------------------
# _on_board_changed — updates board_state and info_zone
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.gui
class TestOnBoardChanged:
    def test_board_state_is_stored(self) -> None:
        panel = _make_panel()
        state = _empty_board_state()
        panel._on_board_changed(state)
        assert panel._board_state is state

    def test_nvda_info_zone_label_updated(self) -> None:
        panel = _make_panel()
        state = _board_with_card(2, "K", "picche", True)
        panel._on_board_changed(state)
        assert panel._nvda_info_zone is not None
        label = panel._nvda_info_zone.GetLabel()
        assert "K" in label or "Pila" in label

    def test_board_state_replaces_previous(self) -> None:
        panel = _make_panel()
        state1 = _empty_board_state()
        state2 = _board_with_card(0, "A", "cuori", True)
        panel._on_board_changed(state1)
        panel._on_board_changed(state2)
        assert panel._board_state is state2


# ---------------------------------------------------------------------------
# _build_nvda_text
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.gui
class TestBuildNvdaText:
    def test_face_up_card_text(self) -> None:
        panel = _make_panel()
        state = _board_with_card(0, "A", "cuori", True)
        text = panel._build_nvda_text(state)
        assert "A" in text
        assert "cuori" in text

    def test_face_down_card_text(self) -> None:
        panel = _make_panel()
        state = _board_with_card(1, "K", "picche", False)
        text = panel._build_nvda_text(state)
        assert "coperta" in text.lower()

    def test_game_over_text(self) -> None:
        panel = _make_panel()
        state = _empty_board_state(game_over=True)
        text = panel._build_nvda_text(state)
        assert "terminata" in text.lower()

    def test_empty_pile_returns_pile_name(self) -> None:
        panel = _make_panel()
        state = _empty_board_state(cursor_pile_idx=3, cursor_card_idx=0)
        text = panel._build_nvda_text(state)
        assert "Pila" in text

    def test_pile_number_1_based(self) -> None:
        """Pile index 0 should display as 'Pila 1'."""
        panel = _make_panel()
        state = _board_with_card(0, "2", "quadri", True)
        text = panel._build_nvda_text(state)
        assert "Pila 1" in text


# ---------------------------------------------------------------------------
# set_theme
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.gui
class TestSetTheme:
    def test_set_theme_updates_current_theme(self) -> None:
        from src.infrastructure.ui.visual_theme import THEME_ALTO_CONTRASTO
        panel = _make_panel()
        panel.set_theme("alto_contrasto")
        assert panel._current_theme == THEME_ALTO_CONTRASTO

    def test_set_unknown_theme_falls_back_to_standard(self) -> None:
        from src.infrastructure.ui.visual_theme import THEME_STANDARD
        panel = _make_panel()
        panel.set_theme("UNKNOWN_THEME")
        assert panel._current_theme == THEME_STANDARD


@pytest.mark.unit
@pytest.mark.gui
class TestApplyVisualSettings:
    def test_apply_visual_settings_updates_mode_and_theme(self) -> None:
        from src.infrastructure.ui.visual_theme import THEME_ALTO_CONTRASTO
        panel = _make_panel(display_mode="audio_only")

        panel.apply_visual_settings("visual", "alto_contrasto")

        assert panel.display_mode == "visual"
        assert panel._current_theme == THEME_ALTO_CONTRASTO

    def test_apply_visual_settings_invalid_mode_falls_back_to_audio(self) -> None:
        panel = _make_panel(display_mode="visual")

        panel.apply_visual_settings("invalid", "standard")

        assert panel.display_mode == "audio_only"


# ---------------------------------------------------------------------------
# Observer registration
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.gui
class TestObserverRegistration:
    def test_observer_registered_when_gc_available(self) -> None:
        panel = _make_panel(with_gc=True)
        gc = panel.controller.gameplay_controller
        gc.set_on_board_changed.assert_called_once_with(panel._on_board_changed)

    def test_no_crash_when_gc_unavailable(self) -> None:
        """Panel must initialise without error even when no gameplay_controller is present."""
        panel = _make_panel(with_gc=False)
        assert panel is not None
