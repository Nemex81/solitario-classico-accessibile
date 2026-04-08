"""Unit tests for card_image_cache.py — CardImageCache.

Uses a subclass (FakeCardImageCache) that overrides _load_source to bypass
disk I/O and wx runtime.  Background bitmap tests inject _bg_source directly
or use a non-existent path to verify the missing-file branch.

Tests cover:
  - _rank_to_num mapping (A, J, Q, K, numeric ranks)
  - _load_source: missing file, valid image, invalid image, ImportError
  - get_bitmap returns None for missing card
  - get_bitmap returns scaled Bitmap for known card
  - get_bitmap uses cache on second call (no reload)
  - get_bitmap returns None on ImportError
  - invalidate_size_cache clears _cache and _bg_cache, preserves _sources
  - get_background_bitmap returns None when file is missing
  - get_background_bitmap loads from file and caches
  - get_background_bitmap returns Bitmap when _bg_source is injected
  - get_background_bitmap uses cache on second call
  - get_background_bitmap returns None on ImportError during scaling
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.infrastructure.ui.card_image_cache import CardImageCache


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


class FakeCardImageCache(CardImageCache):
    """CardImageCache subclass that bypasses disk access and wx for _load_source."""

    def __init__(
        self,
        source_map: dict[tuple[str, str], object | None] | None = None,
    ) -> None:
        super().__init__(Path("."))
        self._source_map: dict[tuple[str, str], object | None] = source_map or {}

    def _load_source(self, rank: str, suit: str) -> object | None:  # type: ignore[override]
        return self._source_map.get((rank, suit))


def _mock_wx(mock_bmp: MagicMock) -> MagicMock:
    """Build a minimal wx module mock that returns *mock_bmp* from Bitmap()."""
    mock = MagicMock()
    mock.Bitmap.return_value = mock_bmp
    mock.IMAGE_QUALITY_HIGH = 2
    return mock


def _mock_image_source(mock_bmp: MagicMock) -> MagicMock:
    """Create a mock wx.Image whose Copy() chain ends with *mock_bmp*."""
    img = MagicMock()
    img.Copy.return_value = img  # Copy() returns self so Rescale() is in-place
    return img


# ---------------------------------------------------------------------------
# _rank_to_num
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestRankToNum:
    def test_rank_to_num_asso(self) -> None:
        assert FakeCardImageCache()._rank_to_num("A") == "1"

    def test_rank_to_num_fante(self) -> None:
        assert FakeCardImageCache()._rank_to_num("J") == "11"

    def test_rank_to_num_donna(self) -> None:
        assert FakeCardImageCache()._rank_to_num("Q") == "12"

    def test_rank_to_num_re(self) -> None:
        assert FakeCardImageCache()._rank_to_num("K") == "13"

    def test_rank_to_num_numero(self) -> None:
        assert FakeCardImageCache()._rank_to_num("7") == "7"

    def test_rank_to_num_dieci(self) -> None:
        assert FakeCardImageCache()._rank_to_num("10") == "10"

    def test_rank_to_num_due(self) -> None:
        assert FakeCardImageCache()._rank_to_num("2") == "2"


# ---------------------------------------------------------------------------
# get_bitmap
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGetBitmap:
    def test_get_bitmap_missing_card_returns_none(self) -> None:
        """A card not present in source_map must yield None."""
        cache = FakeCardImageCache(source_map={})
        result = cache.get_bitmap("5", "quadri", 70, 100)
        assert result is None

    def test_get_bitmap_missing_card_populates_sources_with_none(self) -> None:
        """After a miss, _sources must store None to avoid repeated disk hits."""
        cache = FakeCardImageCache(source_map={})
        cache.get_bitmap("7", "cuori", 70, 100)
        assert ("7", "cuori") in cache._sources
        assert cache._sources[("7", "cuori")] is None

    def test_get_bitmap_returns_bitmap_for_known_card(self) -> None:
        """A card with a valid source image must yield an object (Bitmap)."""
        mock_bmp = MagicMock()
        mock_img = _mock_image_source(mock_bmp)
        mock_wx = _mock_wx(mock_bmp)

        cache = FakeCardImageCache(source_map={("K", "picche"): mock_img})
        with patch.dict("sys.modules", {"wx": mock_wx}):
            result = cache.get_bitmap("K", "picche", 70, 100)

        assert result is mock_bmp

    def test_get_bitmap_cache_hit_skips_reload(self) -> None:
        """Second identical call must not invoke Copy() again."""
        mock_bmp = MagicMock()
        mock_img = _mock_image_source(mock_bmp)
        mock_wx = _mock_wx(mock_bmp)

        cache = FakeCardImageCache(source_map={("A", "cuori"): mock_img})
        with patch.dict("sys.modules", {"wx": mock_wx}):
            result1 = cache.get_bitmap("A", "cuori", 70, 100)
            result2 = cache.get_bitmap("A", "cuori", 70, 100)

        assert result1 is mock_bmp
        assert result2 is mock_bmp
        assert mock_img.Copy.call_count == 1

    def test_get_bitmap_different_sizes_are_separate_cache_entries(self) -> None:
        """Different (width, height) must each produce their own Bitmap."""
        mock_bmp_small = MagicMock()
        mock_bmp_large = MagicMock()
        mock_img = MagicMock()
        mock_img.Copy.return_value = mock_img

        mock_wx = MagicMock()
        mock_wx.IMAGE_QUALITY_HIGH = 2
        # Return different bitmaps on successive calls
        mock_wx.Bitmap.side_effect = [mock_bmp_small, mock_bmp_large]

        cache = FakeCardImageCache(source_map={("3", "fiori"): mock_img})
        with patch.dict("sys.modules", {"wx": mock_wx}):
            r1 = cache.get_bitmap("3", "fiori", 40, 60)
            r2 = cache.get_bitmap("3", "fiori", 70, 100)

        assert r1 is mock_bmp_small
        assert r2 is mock_bmp_large
        assert len(cache._cache) == 2

    def test_get_bitmap_stores_result_in_cache(self) -> None:
        """After a successful get, _cache must hold the key."""
        mock_bmp = MagicMock()
        mock_img = _mock_image_source(mock_bmp)
        mock_wx = _mock_wx(mock_bmp)

        cache = FakeCardImageCache(source_map={("2", "quadri"): mock_img})
        with patch.dict("sys.modules", {"wx": mock_wx}):
            cache.get_bitmap("2", "quadri", 70, 100)

        assert ("2", "quadri", 70, 100) in cache._cache


# ---------------------------------------------------------------------------
# invalidate_size_cache
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestInvalidateSizeCache:
    def test_invalidate_size_cache_clears_cache(self) -> None:
        """_cache must be empty after invalidate_size_cache()."""
        mock_bmp = MagicMock()
        mock_img = _mock_image_source(mock_bmp)
        mock_wx = _mock_wx(mock_bmp)

        cache = FakeCardImageCache(source_map={("A", "cuori"): mock_img})
        with patch.dict("sys.modules", {"wx": mock_wx}):
            cache.get_bitmap("A", "cuori", 70, 100)

        assert len(cache._cache) == 1
        cache.invalidate_size_cache()
        assert len(cache._cache) == 0

    def test_invalidate_size_cache_clears_bg_cache(self) -> None:
        """_bg_cache must be empty after invalidate_size_cache()."""
        mock_bmp = MagicMock()
        mock_img = _mock_image_source(mock_bmp)
        mock_wx = _mock_wx(mock_bmp)

        cache = CardImageCache(Path("."))
        cache._bg_source = mock_img
        with patch.dict("sys.modules", {"wx": mock_wx}):
            cache.get_background_bitmap(800, 600)

        assert len(cache._bg_cache) == 1
        cache.invalidate_size_cache()
        assert len(cache._bg_cache) == 0

    def test_invalidate_size_cache_preserves_sources(self) -> None:
        """_sources must survive invalidate_size_cache()."""
        mock_img = MagicMock()
        cache = FakeCardImageCache(source_map={("Q", "fiori"): mock_img})
        # Populate _sources without needing wx
        cache._sources[("Q", "fiori")] = mock_img

        cache.invalidate_size_cache()

        assert ("Q", "fiori") in cache._sources
        assert cache._sources[("Q", "fiori")] is mock_img

    def test_invalidate_size_cache_preserves_bg_source(self) -> None:
        """_bg_source must survive invalidate_size_cache()."""
        mock_img = MagicMock()
        cache = CardImageCache(Path("."))
        cache._bg_source = mock_img

        cache.invalidate_size_cache()

        assert cache._bg_source is mock_img


# ---------------------------------------------------------------------------
# get_background_bitmap
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGetBackgroundBitmap:
    def test_get_background_bitmap_returns_none_when_file_missing(self) -> None:
        """Non-existent base path must yield None without raising."""
        cache = CardImageCache(Path("/nonexistent/path/that/does/not/exist"))
        result = cache.get_background_bitmap(800, 600)
        assert result is None

    def test_get_background_bitmap_returns_bitmap(self) -> None:
        """When _bg_source is pre-injected, must return a Bitmap."""
        mock_bmp = MagicMock()
        mock_img = _mock_image_source(mock_bmp)
        mock_wx = _mock_wx(mock_bmp)

        cache = CardImageCache(Path("."))
        cache._bg_source = mock_img

        with patch.dict("sys.modules", {"wx": mock_wx}):
            result = cache.get_background_bitmap(800, 600)

        assert result is mock_bmp

    def test_get_background_bitmap_cache_hit_skips_rescale(self) -> None:
        """Second identical call must not rescale again."""
        mock_bmp = MagicMock()
        mock_img = _mock_image_source(mock_bmp)
        mock_wx = _mock_wx(mock_bmp)

        cache = CardImageCache(Path("."))
        cache._bg_source = mock_img

        with patch.dict("sys.modules", {"wx": mock_wx}):
            r1 = cache.get_background_bitmap(800, 600)
            r2 = cache.get_background_bitmap(800, 600)

        assert r1 is mock_bmp
        assert r2 is mock_bmp
        assert mock_img.Copy.call_count == 1

    def test_get_background_bitmap_different_sizes_separate_entries(self) -> None:
        """Different dimensions must produce separate cache entries."""
        mock_bmp_a = MagicMock()
        mock_bmp_b = MagicMock()
        mock_img = MagicMock()
        mock_img.Copy.return_value = mock_img

        mock_wx = MagicMock()
        mock_wx.IMAGE_QUALITY_HIGH = 2
        mock_wx.Bitmap.side_effect = [mock_bmp_a, mock_bmp_b]

        cache = CardImageCache(Path("."))
        cache._bg_source = mock_img

        with patch.dict("sys.modules", {"wx": mock_wx}):
            r1 = cache.get_background_bitmap(800, 600)
            r2 = cache.get_background_bitmap(1024, 768)

        assert r1 is mock_bmp_a
        assert r2 is mock_bmp_b
        assert len(cache._bg_cache) == 2

    def test_get_background_bitmap_loads_from_file(self, tmp_path: Path) -> None:
        """When file exists on disk, loads and caches the background image."""
        bg_dir = tmp_path / "assets" / "img"
        bg_dir.mkdir(parents=True)
        (bg_dir / "Sfondo tavolo verde.jpg").write_bytes(b"fake")

        mock_bg_img = MagicMock()
        mock_bg_img.IsOk.return_value = True
        mock_bg_img.Copy.return_value = mock_bg_img
        mock_bmp = MagicMock()

        mock_wx = MagicMock()
        mock_wx.Image.return_value = mock_bg_img
        mock_wx.Bitmap.return_value = mock_bmp
        mock_wx.IMAGE_QUALITY_HIGH = 2
        mock_wx.BITMAP_TYPE_JPEG = 13

        cache = CardImageCache(tmp_path)
        with patch.dict("sys.modules", {"wx": mock_wx}):
            result = cache.get_background_bitmap(800, 600)

        assert result is mock_bmp
        assert cache._bg_source is mock_bg_img

    def test_get_background_bitmap_import_error_in_scaling_returns_none(self) -> None:
        """If wx raises ImportError during bitmap scaling, return None."""
        mock_img = MagicMock()
        cache = CardImageCache(Path("."))
        cache._bg_source = mock_img
        with patch.dict("sys.modules", {"wx": None}):  # type: ignore[dict-item]
            result = cache.get_background_bitmap(800, 600)
        assert result is None


# ---------------------------------------------------------------------------
# _load_source (tested on base class to cover real implementation)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestLoadSource:
    def test_load_source_missing_file_returns_none(self) -> None:
        """File not found must return None and log at DEBUG level."""
        cache = CardImageCache(Path("/nonexistent/path"))
        result = cache._load_source("A", "cuori")
        assert result is None

    def test_load_source_valid_image_returns_wx_image(self, tmp_path: Path) -> None:
        """Valid file + wx available → returns wx.Image mock."""
        card_dir = tmp_path / "assets" / "img" / "carte_francesi"
        card_dir.mkdir(parents=True)
        (card_dir / "1-cuori.jpg").write_bytes(b"fake")

        mock_img = MagicMock()
        mock_img.IsOk.return_value = True
        mock_wx = MagicMock()
        mock_wx.Image.return_value = mock_img
        mock_wx.BITMAP_TYPE_JPEG = 13

        cache = CardImageCache(tmp_path)
        with patch.dict("sys.modules", {"wx": mock_wx}):
            result = cache._load_source("A", "cuori")

        assert result is mock_img

    def test_load_source_image_not_ok_returns_none(self, tmp_path: Path) -> None:
        """If wx.Image.IsOk() returns False, _load_source returns None."""
        card_dir = tmp_path / "assets" / "img" / "carte_francesi"
        card_dir.mkdir(parents=True)
        (card_dir / "7-re.jpg").write_bytes(b"fake")

        mock_img = MagicMock()
        mock_img.IsOk.return_value = False
        mock_wx = MagicMock()
        mock_wx.Image.return_value = mock_img
        mock_wx.BITMAP_TYPE_JPEG = 13

        cache = CardImageCache(tmp_path)
        with patch.dict("sys.modules", {"wx": mock_wx}):
            result = cache._load_source("7", "re")

        assert result is None

    def test_load_source_import_error_returns_none(self, tmp_path: Path) -> None:
        """ImportError during wx import → _load_source returns None."""
        card_dir = tmp_path / "assets" / "img" / "carte_francesi"
        card_dir.mkdir(parents=True)
        (card_dir / "1-cuori.jpg").write_bytes(b"fake")

        cache = CardImageCache(tmp_path)
        with patch.dict("sys.modules", {"wx": None}):  # type: ignore[dict-item]
            result = cache._load_source("A", "cuori")

        assert result is None


# ---------------------------------------------------------------------------
# get_bitmap ImportError branch
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGetBitmapImportError:
    def test_get_bitmap_import_error_returns_none(self) -> None:
        """If wx raises ImportError during Bitmap creation, return None."""
        mock_img = MagicMock()
        cache = FakeCardImageCache(source_map={("A", "cuori"): mock_img})
        with patch.dict("sys.modules", {"wx": None}):  # type: ignore[dict-item]
            result = cache.get_bitmap("A", "cuori", 70, 100)
        assert result is None


# ---------------------------------------------------------------------------
# Path fix: carte_francesi (underscore) — new tests for v4.3.0
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestFrenchPathFix:
    def test_french_path_uses_underscore(self, tmp_path: Path) -> None:
        """French _load_source_french must look in 'carte_francesi' (underscore)."""
        card_dir = tmp_path / "assets" / "img" / "carte_francesi"
        card_dir.mkdir(parents=True)
        (card_dir / "1-cuori.jpg").write_bytes(b"fake")

        mock_img = MagicMock()
        mock_img.IsOk.return_value = True
        mock_wx = MagicMock()
        mock_wx.Image.return_value = mock_img
        mock_wx.BITMAP_TYPE_JPEG = 13

        cache = CardImageCache(tmp_path, deck_type="french")
        with patch.dict("sys.modules", {"wx": mock_wx}):
            result = cache._load_source("A", "cuori")

        assert result is mock_img

    def test_french_path_space_directory_not_found(self, tmp_path: Path) -> None:
        """A directory named 'carte francesi' (space) must NOT be found."""
        card_dir_space = tmp_path / "assets" / "img" / "carte francesi"
        card_dir_space.mkdir(parents=True)
        (card_dir_space / "1-cuori.jpg").write_bytes(b"fake")

        cache = CardImageCache(tmp_path, deck_type="french")
        result = cache._load_source("A", "cuori")
        assert result is None


# ---------------------------------------------------------------------------
# Neapolitan routing + sequence mapping — new tests for v4.3.0
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestNeapolitanRouting:
    def test_load_source_routes_to_napoletane_for_neapolitan_deck(
        self, tmp_path: Path
    ) -> None:
        """With deck_type='neapolitan', _load_source must call _load_source_napoletane."""
        card_dir = tmp_path / "assets" / "img" / "carte_napoletane"
        card_dir.mkdir(parents=True)
        (card_dir / "1_Asso_di_bastoni.jpg").write_bytes(b"fake")

        mock_img = MagicMock()
        mock_img.IsOk.return_value = True
        mock_wx = MagicMock()
        mock_wx.Image.return_value = mock_img
        mock_wx.BITMAP_TYPE_JPEG = 13

        cache = CardImageCache(tmp_path, deck_type="neapolitan")
        with patch.dict("sys.modules", {"wx": mock_wx}):
            result = cache._load_source("Asso", "bastoni")

        assert result is mock_img

    def test_napoletane_seq_bastoni_asso(self, tmp_path: Path) -> None:
        """Asso di bastoni -> seq 1 -> '1_Asso_di_bastoni.jpg'."""
        card_dir = tmp_path / "assets" / "img" / "carte_napoletane"
        card_dir.mkdir(parents=True)
        (card_dir / "1_Asso_di_bastoni.jpg").write_bytes(b"fake")

        mock_img = MagicMock()
        mock_img.IsOk.return_value = True
        mock_wx = MagicMock()
        mock_wx.Image.return_value = mock_img
        mock_wx.BITMAP_TYPE_JPEG = 13

        cache = CardImageCache(tmp_path, deck_type="neapolitan")
        with patch.dict("sys.modules", {"wx": mock_wx}):
            result = cache._load_source_napoletane("Asso", "bastoni")

        assert result is mock_img

    def test_napoletane_seq_coppe_re(self, tmp_path: Path) -> None:
        """Re di coppe -> offset=10 + pos=10 = seq 20 -> '20_Dieci_di_coppe.jpg'."""
        card_dir = tmp_path / "assets" / "img" / "carte_napoletane"
        card_dir.mkdir(parents=True)
        (card_dir / "20_Dieci_di_coppe.jpg").write_bytes(b"fake")

        mock_img = MagicMock()
        mock_img.IsOk.return_value = True
        mock_wx = MagicMock()
        mock_wx.Image.return_value = mock_img
        mock_wx.BITMAP_TYPE_JPEG = 13

        cache = CardImageCache(tmp_path, deck_type="neapolitan")
        with patch.dict("sys.modules", {"wx": mock_wx}):
            result = cache._load_source_napoletane("Re", "coppe")

        assert result is mock_img

    def test_napoletane_case_exception_bastoni_dieci(self, tmp_path: Path) -> None:
        """Re di bastoni -> seq 10 -> '10_Dieci_di_Bastoni.jpg' (capital B)."""
        card_dir = tmp_path / "assets" / "img" / "carte_napoletane"
        card_dir.mkdir(parents=True)
        (card_dir / "10_Dieci_di_Bastoni.jpg").write_bytes(b"fake")

        mock_img = MagicMock()
        mock_img.IsOk.return_value = True
        mock_wx = MagicMock()
        mock_wx.Image.return_value = mock_img
        mock_wx.BITMAP_TYPE_JPEG = 13

        cache = CardImageCache(tmp_path, deck_type="neapolitan")
        with patch.dict("sys.modules", {"wx": mock_wx}):
            result = cache._load_source_napoletane("Re", "bastoni")

        assert result is mock_img

    def test_napoletane_unknown_rank_returns_none(self) -> None:
        """An unrecognised rank must return None without raising."""
        cache = CardImageCache(Path("."), deck_type="neapolitan")
        result = cache._load_source_napoletane("X", "bastoni")
        assert result is None

    def test_napoletane_unknown_suit_returns_none(self) -> None:
        """An unrecognised suit must return None without raising."""
        cache = CardImageCache(Path("."), deck_type="neapolitan")
        result = cache._load_source_napoletane("Asso", "coppe_x")
        assert result is None


# ---------------------------------------------------------------------------
# get_back_bitmap — new tests for v4.3.0
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGetBackBitmap:
    def test_get_back_bitmap_french_returns_none(self) -> None:
        """French deck -> get_back_bitmap must always return None."""
        cache = CardImageCache(Path("."), deck_type="french")
        result = cache.get_back_bitmap(70, 100)
        assert result is None

    def test_get_back_bitmap_napoletane_file_missing_returns_none(
        self, tmp_path: Path
    ) -> None:
        """Neapolitan deck + no retro file -> returns None."""
        cache = CardImageCache(tmp_path, deck_type="neapolitan")
        result = cache.get_back_bitmap(70, 100)
        assert result is None

    def test_get_back_bitmap_napoletane_returns_bitmap(self, tmp_path: Path) -> None:
        """When retro file exists, must return a Bitmap."""
        card_dir = tmp_path / "assets" / "img" / "carte_napoletane"
        card_dir.mkdir(parents=True)
        (card_dir / "41_Carte_Napoletane_retro.jpg").write_bytes(b"fake")

        mock_img = MagicMock()
        mock_img.IsOk.return_value = True
        mock_img.Copy.return_value = mock_img
        mock_bmp = MagicMock()
        mock_wx = MagicMock()
        mock_wx.Image.return_value = mock_img
        mock_wx.Bitmap.return_value = mock_bmp
        mock_wx.IMAGE_QUALITY_HIGH = 2
        mock_wx.BITMAP_TYPE_JPEG = 13

        cache = CardImageCache(tmp_path, deck_type="neapolitan")
        with patch.dict("sys.modules", {"wx": mock_wx}):
            result = cache.get_back_bitmap(70, 100)

        assert result is mock_bmp

    def test_get_back_bitmap_cache_hit_skips_rescale(self, tmp_path: Path) -> None:
        """Second call with same dimensions must use cache."""
        mock_bmp = MagicMock()
        mock_img = _mock_image_source(mock_bmp)
        mock_wx = _mock_wx(mock_bmp)

        cache = CardImageCache(tmp_path, deck_type="neapolitan")
        cache._back_source = mock_img
        with patch.dict("sys.modules", {"wx": mock_wx}):
            r1 = cache.get_back_bitmap(70, 100)
            r2 = cache.get_back_bitmap(70, 100)

        assert r1 is mock_bmp
        assert r2 is mock_bmp
        assert mock_img.Copy.call_count == 1

    def test_invalidate_clears_back_cache(self) -> None:
        """invalidate_size_cache must empty _back_cache."""
        mock_bmp = MagicMock()
        cache = CardImageCache(Path("."), deck_type="neapolitan")
        cache._back_cache[(70, 100)] = mock_bmp

        assert len(cache._back_cache) == 1
        cache.invalidate_size_cache()
        assert len(cache._back_cache) == 0
