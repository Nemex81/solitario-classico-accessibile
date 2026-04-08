"""Unit tests for GameSettings visual preference persistence."""

import pytest

from src.domain.services.game_settings import GameSettings


@pytest.mark.unit
class TestGameSettingsVisualPersistence:
    def test_to_dict_includes_visual_preferences(self) -> None:
        settings = GameSettings()
        settings.display_mode = "visual"
        settings.visual_theme = "alto_contrasto"

        data = settings.to_dict()

        assert data["display_mode"] == "visual"
        assert data["visual_theme"] == "alto_contrasto"

    def test_load_from_dict_restores_visual_preferences(self) -> None:
        settings = GameSettings()

        settings.load_from_dict({
            "display_mode": "visual",
            "visual_theme": "grande",
            "difficulty_level": 1,
        })

        assert settings.display_mode == "visual"
        assert settings.visual_theme == "grande"

    def test_load_from_dict_invalid_visual_preferences_use_defaults(self) -> None:
        settings = GameSettings()
        settings.display_mode = "visual"
        settings.visual_theme = "alto_contrasto"

        settings.load_from_dict({
            "display_mode": "invalid",
            "visual_theme": "unknown",
            "difficulty_level": 1,
        })

        assert settings.display_mode == "audio_only"
        assert settings.visual_theme == "standard"