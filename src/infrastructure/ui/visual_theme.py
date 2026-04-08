"""Visual theme system for GameplayPanel rendering.

Defines ThemeProperties (colours, fonts, sizes) and the three built-in
themes (standard, alto_contrasto, grande).  The presentation layer reads
a ThemeProperties instance from get_theme() — no hard-coded values elsewhere.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ThemeProperties:
    """Immutable set of visual properties for board rendering.

    Attributes:
        bg_color: RGB background colour of the board surface.
        card_bg: RGB fill colour of a face-up card.
        card_back: RGB fill colour of a face-down card.
        text_red: RGB text colour for red suits (cuori, quadri).
        text_black: RGB text colour for black suits (fiori, picche).
        border_color: RGB colour of the normal card border.
        cursor_color: RGB colour of the cursor highlight border.
        selection_color: RGB colour of the selection border.
        border_width: Pixel width of the normal card border.
        cursor_width: Pixel width of the cursor/selection border.
        font_size_base: Base font size in points for rank text.
        card_scale: Multiplier for card dimensions (1.0 = standard).
    """

    bg_color: tuple[int, int, int]
    card_bg: tuple[int, int, int]
    card_back: tuple[int, int, int]
    text_red: tuple[int, int, int]
    text_black: tuple[int, int, int]
    border_color: tuple[int, int, int]
    cursor_color: tuple[int, int, int]
    selection_color: tuple[int, int, int]
    border_width: int
    cursor_width: int
    font_size_base: int
    card_scale: float


# ---------------------------------------------------------------------------
# Built-in themes
# ---------------------------------------------------------------------------

THEME_STANDARD: ThemeProperties = ThemeProperties(
    bg_color=(0, 100, 0),           # traditional green felt
    card_bg=(255, 255, 255),        # white card face
    card_back=(30, 30, 180),        # blue card back
    text_red=(200, 0, 0),           # dark red for hearts/diamonds
    text_black=(0, 0, 0),           # black for clubs/spades
    border_color=(100, 100, 100),   # grey border
    cursor_color=(0, 200, 255),     # cyan cursor highlight
    selection_color=(255, 180, 0),  # amber selection
    border_width=1,
    cursor_width=3,
    font_size_base=14,
    card_scale=1.0,
)

THEME_ALTO_CONTRASTO: ThemeProperties = ThemeProperties(
    bg_color=(0, 0, 0),             # black background for max contrast
    card_bg=(230, 230, 230),        # light grey card face
    card_back=(20, 20, 20),         # near-black card back
    text_red=(255, 60, 60),         # bright red
    text_black=(0, 0, 0),           # black
    border_color=(200, 200, 200),   # light grey border visible on dark bg
    cursor_color=(255, 255, 0),     # fluorescent yellow cursor (NVDA-friendly)
    selection_color=(255, 100, 255),  # magenta selection
    border_width=2,
    cursor_width=4,
    font_size_base=16,
    card_scale=1.0,
)

THEME_GRANDE: ThemeProperties = ThemeProperties(
    bg_color=(0, 100, 0),           # same as standard
    card_bg=(255, 255, 255),
    card_back=(30, 30, 180),
    text_red=(200, 0, 0),
    text_black=(0, 0, 0),
    border_color=(100, 100, 100),
    cursor_color=(0, 200, 255),
    selection_color=(255, 180, 0),
    border_width=2,
    cursor_width=4,
    font_size_base=21,
    card_scale=1.5,
)

# ---------------------------------------------------------------------------
# Registry and lookup
# ---------------------------------------------------------------------------

_THEMES: dict[str, ThemeProperties] = {
    "standard": THEME_STANDARD,
    "alto_contrasto": THEME_ALTO_CONTRASTO,
    "grande": THEME_GRANDE,
}


def get_theme(name: str) -> ThemeProperties:
    """Return the ThemeProperties for the given name.

    Performs a case-insensitive look-up.  Falls back to THEME_STANDARD if the
    requested name is not found.

    Args:
        name: Theme identifier, e.g. ``"standard"``, ``"alto_contrasto"``,
            ``"grande"``.

    Returns:
        ThemeProperties for the requested theme, or THEME_STANDARD as fallback.
    """
    return _THEMES.get(name.lower(), THEME_STANDARD)
