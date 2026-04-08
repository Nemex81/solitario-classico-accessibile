"""Unit tests for OptionsWindowController visual preference snapshots."""

import pytest

from src.application.options_controller import OptionsWindowController
from src.domain.services.game_settings import GameSettings


@pytest.mark.unit
class TestOptionsControllerVisualPreferences:
    def test_save_snapshot_includes_visual_preferences(self) -> None:
        settings = GameSettings()
        settings.display_mode = "visual"
        settings.visual_theme = "grande"
        controller = OptionsWindowController(settings)

        controller._save_snapshot()

        assert controller.original_settings["display_mode"] == "visual"
        assert controller.original_settings["visual_theme"] == "grande"

    def test_restore_snapshot_restores_visual_preferences(self) -> None:
        settings = GameSettings()
        controller = OptionsWindowController(settings)

        controller._save_snapshot()
        settings.display_mode = "visual"
        settings.visual_theme = "alto_contrasto"

        controller._restore_snapshot()

        assert settings.display_mode == "audio_only"
        assert settings.visual_theme == "standard"