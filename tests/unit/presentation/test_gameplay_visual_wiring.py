"""Unit tests for gameplay visual wiring in SolitarioController."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from acs_wx import SolitarioController


@pytest.mark.unit
class TestGameplayVisualWiring:
    def test_create_gameplay_panel_uses_visual_preferences(self) -> None:
        controller = object.__new__(SolitarioController)
        controller.frame = MagicMock()
        controller.frame.panel_container = object()
        controller.settings = MagicMock(display_mode="visual", visual_theme="alto_contrasto")

        with patch("acs_wx.GameplayPanel") as gameplay_panel_class:
            panel_instance = object()
            gameplay_panel_class.return_value = panel_instance

            created_panel = controller._create_gameplay_panel()

        assert created_panel is panel_instance
        gameplay_panel_class.assert_called_once_with(
            parent=controller.frame.panel_container,
            controller=controller,
            display_mode="visual",
            theme_name="alto_contrasto",
        )

    def test_sync_gameplay_panel_settings_applies_cached_panel_preferences(self) -> None:
        controller = object.__new__(SolitarioController)
        controller.settings = MagicMock(display_mode="visual", visual_theme="grande")
        gameplay_panel = MagicMock()
        controller.view_manager = MagicMock()
        controller.view_manager.get_panel.return_value = gameplay_panel

        controller._sync_gameplay_panel_settings()

        gameplay_panel.apply_visual_settings.assert_called_once_with(
            display_mode="visual",
            theme_name="grande",
        )

    def test_start_gameplay_syncs_preferences_and_refreshes_board(self) -> None:
        controller = object.__new__(SolitarioController)
        controller.settings = MagicMock(display_mode="visual", visual_theme="standard")
        controller.view_manager = MagicMock()
        current_panel = MagicMock()
        gameplay_panel = MagicMock()
        controller.view_manager.get_current_view.return_value = "menu"
        controller.view_manager.get_panel.side_effect = lambda name: {
            "menu": current_panel,
            "gameplay": gameplay_panel,
        }.get(name)
        controller.engine = MagicMock()
        controller.gameplay_controller = MagicMock()
        controller.screen_reader = MagicMock()
        controller.is_menu_open = True
        controller._timer_expired_announced = True

        controller.start_gameplay()

        current_panel.Hide.assert_called_once_with()
        gameplay_panel.apply_visual_settings.assert_called_once_with(
            display_mode="visual",
            theme_name="standard",
        )
        controller.view_manager.show_panel.assert_called_once_with('gameplay')
        controller.engine.reset_game.assert_called_once_with()
        controller.engine.new_game.assert_called_once_with()
        controller.gameplay_controller.refresh_board_state.assert_called_once_with()
        controller.screen_reader.tts.speak.assert_called_once()
        assert controller.is_menu_open is False
        assert controller._timer_expired_announced is False