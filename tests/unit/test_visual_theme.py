"""Unit tests for visual_theme.py — ThemeProperties and get_theme().

Tests cover:
- All three built-in themes are returned by get_theme()
- Unknown theme name falls back to THEME_STANDARD
- Key property values for each theme (especially high-contrast cursor colour)
- ThemeProperties immutability (frozen=True)
- Case-insensitive lookup
"""

from __future__ import annotations

import pytest

from src.infrastructure.ui.visual_theme import (
    THEME_ALTO_CONTRASTO,
    THEME_GRANDE,
    THEME_STANDARD,
    ThemeProperties,
    get_theme,
)


# ---------------------------------------------------------------------------
# get_theme() lookup
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGetTheme:
    def test_standard_returns_theme_standard(self) -> None:
        assert get_theme("standard") is THEME_STANDARD

    def test_alto_contrasto_returns_theme_alto_contrasto(self) -> None:
        assert get_theme("alto_contrasto") is THEME_ALTO_CONTRASTO

    def test_grande_returns_theme_grande(self) -> None:
        assert get_theme("grande") is THEME_GRANDE

    def test_unknown_name_falls_back_to_standard(self) -> None:
        assert get_theme("sconosciuto") is THEME_STANDARD

    def test_empty_string_falls_back_to_standard(self) -> None:
        assert get_theme("") is THEME_STANDARD

    def test_case_insensitive_standard(self) -> None:
        assert get_theme("Standard") is THEME_STANDARD
        assert get_theme("STANDARD") is THEME_STANDARD

    def test_case_insensitive_alto_contrasto(self) -> None:
        assert get_theme("Alto_Contrasto") is THEME_ALTO_CONTRASTO

    def test_case_insensitive_grande(self) -> None:
        assert get_theme("GRANDE") is THEME_GRANDE


# ---------------------------------------------------------------------------
# ThemeProperties — immutability
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestThemePropertiesImmutability:
    def test_frozen_prevents_mutation(self) -> None:
        theme = get_theme("standard")
        with pytest.raises((AttributeError, TypeError)):
            theme.font_size_base = 99  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Built-in theme property values
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestThemePropertyValues:
    # --- STANDARD ---------------------------------------------------------

    def test_standard_bg_is_green(self) -> None:
        assert THEME_STANDARD.bg_color == (0, 100, 0)

    def test_standard_card_bg_is_white(self) -> None:
        assert THEME_STANDARD.card_bg == (255, 255, 255)

    def test_standard_card_scale_is_1(self) -> None:
        assert THEME_STANDARD.card_scale == 1.0

    def test_standard_font_size_is_14(self) -> None:
        assert THEME_STANDARD.font_size_base == 14

    def test_standard_border_width_is_1(self) -> None:
        assert THEME_STANDARD.border_width == 1

    # --- ALTO CONTRASTO ---------------------------------------------------

    def test_alto_contrasto_bg_is_black(self) -> None:
        assert THEME_ALTO_CONTRASTO.bg_color == (0, 0, 0)

    def test_alto_contrasto_cursor_is_yellow(self) -> None:
        assert THEME_ALTO_CONTRASTO.cursor_color == (255, 255, 0)

    def test_alto_contrasto_font_size_is_16(self) -> None:
        assert THEME_ALTO_CONTRASTO.font_size_base == 16

    def test_alto_contrasto_border_width_is_2(self) -> None:
        assert THEME_ALTO_CONTRASTO.border_width == 2

    # --- GRANDE -----------------------------------------------------------

    def test_grande_card_scale_is_1_5(self) -> None:
        assert THEME_GRANDE.card_scale == 1.5

    def test_grande_font_size_is_21(self) -> None:
        assert THEME_GRANDE.font_size_base == 21

    def test_grande_bg_same_as_standard(self) -> None:
        assert THEME_GRANDE.bg_color == THEME_STANDARD.bg_color

    # --- All themes --------------------------------------------------------

    def test_all_themes_have_valid_rgb_tuples(self) -> None:
        for name in ("standard", "alto_contrasto", "grande"):
            theme = get_theme(name)
            for attr in (
                "bg_color", "card_bg", "card_back",
                "text_red", "text_black", "border_color",
                "cursor_color", "selection_color",
            ):
                value = getattr(theme, attr)
                assert isinstance(value, tuple) and len(value) == 3, (
                    f"{name}.{attr} should be an RGB tuple"
                )
                for component in value:
                    assert 0 <= component <= 255, (
                        f"{name}.{attr} component {component} out of [0, 255]"
                    )

    def test_all_themes_have_positive_widths(self) -> None:
        for name in ("standard", "alto_contrasto", "grande"):
            theme = get_theme(name)
            assert theme.border_width >= 1
            assert theme.cursor_width >= 1

    def test_all_themes_have_positive_font_size(self) -> None:
        for name in ("standard", "alto_contrasto", "grande"):
            assert get_theme(name).font_size_base > 0

    def test_all_themes_have_positive_card_scale(self) -> None:
        for name in ("standard", "alto_contrasto", "grande"):
            assert get_theme(name).card_scale > 0.0

    def test_standard_uses_card_images(self) -> None:
        assert THEME_STANDARD.use_card_images is True

    def test_alto_contrasto_not_card_images(self) -> None:
        assert THEME_ALTO_CONTRASTO.use_card_images is False

    def test_grande_uses_card_images(self) -> None:
        assert THEME_GRANDE.use_card_images is True
