"""Unit tests for on_board_changed observer — Fase 2 gameplay_controller.

Tests verify:
- set_on_board_changed registers / removes the callback
- _notify_board_changed invokes the callback with a BoardState
- handle_wx_key_event triggers the callback on handled keys
- _build_board_state builds a coherent BoardState from the engine
- BoardState has selection active / inactive based on engine state
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.application.board_state import BoardState, CardView
from src.application.gameplay_controller import GamePlayController
from src.application.game_engine import GameEngine
from src.domain.services.game_settings import GameSettings


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class DummyTTS:
    def speak(self, text: str, interrupt: bool = True) -> None:
        pass


class DummySR:
    def __init__(self) -> None:
        self.tts = DummyTTS()


def _make_controller() -> GamePlayController:
    engine = GameEngine.create(
        audio_enabled=False,
        tts_engine="mock",
        verbose=0,
        settings=GameSettings(),
        use_native_dialogs=False,
        parent_window=None,
        profile_service=None,
    )
    return GamePlayController(
        engine=engine,
        screen_reader=DummySR(),
        settings=GameSettings(),
    )


# ---------------------------------------------------------------------------
# Observer registration tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestBoardObserverRegistration:
    def test_default_callback_is_none(self) -> None:
        ctrl = _make_controller()
        assert ctrl._on_board_changed_callback is None

    def test_set_callback_registers(self) -> None:
        ctrl = _make_controller()
        cb = MagicMock()
        ctrl.set_on_board_changed(cb)
        assert ctrl._on_board_changed_callback is cb

    def test_unregister_with_none(self) -> None:
        ctrl = _make_controller()
        cb = MagicMock()
        ctrl.set_on_board_changed(cb)
        ctrl.set_on_board_changed(None)
        assert ctrl._on_board_changed_callback is None


# ---------------------------------------------------------------------------
# _notify_board_changed tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestNotifyBoardChanged:
    def test_notify_calls_callback_with_board_state(self) -> None:
        ctrl = _make_controller()
        cb = MagicMock()
        ctrl.set_on_board_changed(cb)
        ctrl._notify_board_changed()
        cb.assert_called_once()
        args, _ = cb.call_args
        assert isinstance(args[0], BoardState)

    def test_notify_no_callback_does_not_raise(self) -> None:
        ctrl = _make_controller()
        # No callback registered — must not raise
        ctrl._notify_board_changed()

    def test_notify_callback_exception_does_not_crash(self) -> None:
        ctrl = _make_controller()
        def bad_cb(state: BoardState) -> None:
            raise RuntimeError("test error")
        ctrl.set_on_board_changed(bad_cb)
        # Must not propagate exception
        ctrl._notify_board_changed()


# ---------------------------------------------------------------------------
# _build_board_state tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestBuildBoardState:
    def test_returns_board_state_instance(self) -> None:
        ctrl = _make_controller()
        # Start a new game so the engine has a real board
        ctrl.engine.new_game()
        state = ctrl._build_board_state()
        assert isinstance(state, BoardState)

    def test_has_13_piles(self) -> None:
        ctrl = _make_controller()
        ctrl.engine.new_game()
        state = ctrl._build_board_state()
        assert len(state.piles) == 13

    def test_tableau_piles_have_cards_after_new_game(self) -> None:
        ctrl = _make_controller()
        ctrl.engine.new_game()
        state = ctrl._build_board_state()
        # Tableau piles 0-6 should have at least one card each
        for i in range(7):
            assert len(state.piles[i]) >= 1, f"Tableau pile {i} is empty"

    def test_stock_pile_has_cards(self) -> None:
        ctrl = _make_controller()
        ctrl.engine.new_game()
        state = ctrl._build_board_state()
        # Stock pile (index 12) should not be empty after new game
        assert len(state.piles[12]) > 0

    def test_cursor_indices_present(self) -> None:
        ctrl = _make_controller()
        ctrl.engine.new_game()
        state = ctrl._build_board_state()
        assert isinstance(state.cursor_pile_idx, int)
        assert isinstance(state.cursor_card_idx, int)

    def test_selection_inactive_on_new_game(self) -> None:
        ctrl = _make_controller()
        ctrl.engine.new_game()
        state = ctrl._build_board_state()
        assert state.selection_active is False
        assert state.selected_cards is None
        assert state.selected_pile_idx is None

    def test_game_over_false_on_new_game(self) -> None:
        ctrl = _make_controller()
        ctrl.engine.new_game()
        state = ctrl._build_board_state()
        assert state.game_over is False

    def test_card_view_fields_populated(self) -> None:
        ctrl = _make_controller()
        ctrl.engine.new_game()
        state = ctrl._build_board_state()
        # Find at least one face-up card in pile 0 (its last card should be face-up)
        pile_0 = state.piles[0]
        assert len(pile_0) >= 1
        top_card = pile_0[-1]
        assert isinstance(top_card, CardView)
        assert top_card.rank  # non-empty string
        assert top_card.suit  # non-empty string
        assert top_card.suit_color in ("red", "black")

    def test_card_view_face_up_top_of_tableau(self) -> None:
        ctrl = _make_controller()
        ctrl.engine.new_game()
        state = ctrl._build_board_state()
        # Top card of each tableau pile should be face-up
        for i in range(7):
            if state.piles[i]:
                assert state.piles[i][-1].face_up is True, (
                    f"Top card of tableau pile {i} should be face-up"
                )


# ---------------------------------------------------------------------------
# handle_wx_key_event integration test
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestHandleWxKeyEventTriggersObserver:
    def test_handled_key_triggers_callback(self) -> None:
        ctrl = _make_controller()
        ctrl.engine.new_game()
        cb = MagicMock()
        ctrl.set_on_board_changed(cb)

        # Simulate a wx.KeyEvent for key '1' (pile navigation)
        mock_event = MagicMock()
        mock_event.GetKeyCode.return_value = ord("1")
        mock_event.GetModifiers.return_value = 0  # no modifiers

        import wx  # noqa: F401 — needed for wx constants inside dispatch
        handled = ctrl.handle_wx_key_event(mock_event)

        assert handled is True
        cb.assert_called_once()

    def test_unknown_key_does_not_trigger_callback(self) -> None:
        ctrl = _make_controller()
        ctrl.engine.new_game()
        cb = MagicMock()
        ctrl.set_on_board_changed(cb)

        mock_event = MagicMock()
        mock_event.GetKeyCode.return_value = 0  # unknown key code
        mock_event.GetModifiers.return_value = 0

        handled = ctrl.handle_wx_key_event(mock_event)

        assert handled is False
        cb.assert_not_called()
