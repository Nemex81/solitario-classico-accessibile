from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Tuple, Optional

logger = logging.getLogger(__name__)


class CardImageCache:
    """Cache semplice per immagini carte e sfondo.

    Implementazione minimal compatibile con i test unitari.
    """

    def __init__(self, assets_base_path: Path) -> None:
        self._base_path: Path = assets_base_path
        self._sources: Dict[Tuple[str, str], object | None] = {}
        self._cache: Dict[Tuple[str, str, int, int], object] = {}
        self._bg_source: Optional[object] = None
        self._bg_cache: Dict[Tuple[int, int], object] = {}

    # --------------------- helpers ---------------------
    def _rank_to_num(self, rank: str) -> str:
        if rank == "A":
            return "1"
        if rank == "J":
            return "11"
        if rank == "Q":
            return "12"
        if rank == "K":
            return "13"
        return rank

    def _load_source(self, rank: str, suit: str) -> object | None:
        try:
            wx = __import__("wx")
        except Exception:
            logger.debug("wx not available while loading source %s %s", rank, suit)
            return None

        rank_num = self._rank_to_num(rank)
        img_path = (
            self._base_path
            / "assets"
            / "img"
            / "carte francesi"
            / f"{rank_num}-{suit}.jpg"
        )

        if not img_path.exists():
            logger.debug("Card image missing: %s", img_path)
            return None

        try:
            img = wx.Image(str(img_path), wx.BITMAP_TYPE_JPEG)
            if not getattr(img, "IsOk", lambda: True)():
                return None
            return img
        except Exception:
            logger.debug("Exception loading image %s", img_path, exc_info=True)
            return None

    # --------------------- public API ---------------------
    def get_bitmap(self, rank: str, suit: str, width: int, height: int) -> object | None:
        key = (rank, suit, width, height)
        if key in self._cache:
            return self._cache[key]

        # Ensure source present (may be None to avoid repeated loads)
        if (rank, suit) not in self._sources:
            self._sources[(rank, suit)] = self._load_source(rank, suit)

        src = self._sources[(rank, suit)]
        if src is None:
            return None

        try:
            wx = __import__("wx")
            img = src.Copy()
            # Rescale API may vary; tests expect Rescale/Copy pattern
            if hasattr(img, "Rescale"):
                img.Rescale(width, height, quality=wx.IMAGE_QUALITY_HIGH)
            bmp = wx.Bitmap(img)
            self._cache[key] = bmp
            return bmp
        except Exception:
            logger.debug("Error creating bitmap for %s %s %sx%s", rank, suit, width, height, exc_info=True)
            return None

    def get_background_bitmap(self, width: int, height: int) -> object | None:
        key = (width, height)
        if key in self._bg_cache:
            return self._bg_cache[key]

        if self._bg_source is None:
            # try to load from assets
            try:
                wx = __import__("wx")
            except Exception:
                logger.debug("wx not available for background load")
                return None

            bg_path = self._base_path / "assets" / "img" / "Sfondo tavolo verde.jpg"
            if not bg_path.exists():
                return None

            try:
                img = wx.Image(str(bg_path), wx.BITMAP_TYPE_JPEG)
                if not getattr(img, "IsOk", lambda: True)():
                    return None
                self._bg_source = img
            except Exception:
                logger.debug("Error loading background image %s", bg_path, exc_info=True)
                return None

        try:
            wx = __import__("wx")
            img = self._bg_source.Copy()
            if hasattr(img, "Rescale"):
                img.Rescale(width, height, quality=wx.IMAGE_QUALITY_HIGH)
            bmp = wx.Bitmap(img)
            self._bg_cache[key] = bmp
            return bmp
        except Exception:
            logger.debug("Error creating background bitmap %sx%s", width, height, exc_info=True)
            return None

    def invalidate_size_cache(self) -> None:
        self._cache.clear()
        self._bg_cache.clear()
"""CardImageCache — lazy-loading cache for card bitmap images.

Loads JPEG card images from disk on first request, caches both the original
wx.Image source and scaled wx.Bitmap objects per (width, height) combination.

wx is imported lazily inside each method to allow use in test environments
that do not have a wx runtime available.

Usage example::

    cache = CardImageCache(Path("."))          # repo root as base
    bmp = cache.get_bitmap("A", "cuori", 70, 100)
    if bmp is not None:
        dc.DrawBitmap(bmp, x, y)
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

_log = logging.getLogger(__name__)

_RANK_MAP: dict[str, str] = {
    "A": "1",
    "J": "11",
    "Q": "12",
    "K": "13",
}


class CardImageCache:
    """Lazy-loading cache for playing card and background bitmap images.

    Maintains two internal caches:
    - ``_sources``: original wx.Image objects loaded from disk (per card).
    - ``_cache``: scaled wx.Bitmap objects per (rank, suit, width, height).

    Calling ``invalidate_size_cache()`` drops only the scaled bitmaps so that
    a layout resize does not force a full disk reload.
    """

    def __init__(self, assets_base_path: str | os.PathLike[str]) -> None:
        """Initialise with the project root (parent of the ``assets/`` directory).

        Args:
            assets_base_path: Absolute or relative path to the project root.
                              Card images are expected at
                              ``<base>/assets/img/carte francesi/<rank>-<suit>.jpg``
                              and the background at
                              ``<base>/assets/img/Sfondo tavolo verde.jpg``.
        """
        self._base_path: Path = Path(assets_base_path)
        # (rank, suit) → wx.Image | None  (None = file missing / wx unavailable)
        self._sources: dict[tuple[str, str], object | None] = {}
        # (rank, suit, w, h) → wx.Bitmap
        self._cache: dict[tuple[str, str, int, int], object] = {}
        # background wx.Image source
        self._bg_source: object | None = None
        # (w, h) → wx.Bitmap
        self._bg_cache: dict[tuple[int, int], object] = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _rank_to_num(self, rank: str) -> str:
        """Convert a rank string to the numeric string used in filenames.

        Args:
            rank: Card rank — ``"A"``, ``"2"``–``"10"``, ``"J"``, ``"Q"``, ``"K"``.

        Returns:
            Numeric string: ``"A"``→``"1"``, ``"J"``→``"11"``,
            ``"Q"``→``"12"``, ``"K"``→``"13"``, others unchanged.
        """
        return _RANK_MAP.get(rank, rank)

    def _load_source(self, rank: str, suit: str) -> object | None:
        """Load a wx.Image for the given card from disk.

        Args:
            rank: Card rank.
            suit: Card suit (``"cuori"``, ``"fiori"``, ``"picche"``, ``"quadri"``).

        Returns:
            A ``wx.Image`` instance if the file exists and wx is available,
            otherwise ``None``.
        """
        rank_num = self._rank_to_num(rank)
        file_path = (
            self._base_path
            / "assets"
            / "img"
            / "carte francesi"
            / f"{rank_num}-{suit}.jpg"
        )
        if not file_path.exists():
            _log.debug("Immagine carta non trovata: %s-%s", rank, suit)
            return None
        try:
            import wx  # type: ignore[import-untyped]  # noqa: PLC0415

            img = wx.Image(str(file_path), wx.BITMAP_TYPE_JPEG)
            if not img.IsOk():
                _log.debug("Immagine carta non valida: %s-%s", rank, suit)
                return None
            return img  # type: ignore[no-any-return]
        except ImportError:
            return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_bitmap(
        self, rank: str, suit: str, width: int, height: int
    ) -> object | None:
        """Return a scaled ``wx.Bitmap`` for the given card and dimensions.

        The result is cached: subsequent calls with the same arguments return
        the cached bitmap without disk I/O or rescaling.

        Args:
            rank: Card rank.
            suit: Card suit.
            width: Target width in pixels.
            height: Target height in pixels.

        Returns:
            A ``wx.Bitmap`` scaled to ``(width, height)``, or ``None`` if the
            image file is missing or wx is not available.
        """
        cache_key = (rank, suit, width, height)
        if cache_key in self._cache:
            return self._cache[cache_key]

        source_key = (rank, suit)
        if source_key not in self._sources:
            self._sources[source_key] = self._load_source(rank, suit)

        source = self._sources[source_key]
        if source is None:
            return None

        try:
            import wx  # noqa: PLC0415

            img = source.Copy()  # type: ignore[attr-defined]
            img.Rescale(width, height, wx.IMAGE_QUALITY_HIGH)
            bmp: object = wx.Bitmap(img)
            self._cache[cache_key] = bmp
            return bmp
        except ImportError:
            return None

    def get_background_bitmap(self, width: int, height: int) -> object | None:
        """Return a scaled ``wx.Bitmap`` for the table background image.

        Args:
            width: Target width in pixels.
            height: Target height in pixels.

        Returns:
            A ``wx.Bitmap`` scaled to ``(width, height)``, or ``None`` if the
            background file is missing or wx is not available.
        """
        bg_key = (width, height)
        if bg_key in self._bg_cache:
            return self._bg_cache[bg_key]

        if self._bg_source is None:
            bg_path = self._base_path / "assets" / "img" / "Sfondo tavolo verde.jpg"
            if not bg_path.exists():
                _log.debug("Immagine sfondo non trovata: %s", bg_path)
                return None
            try:
                import wx  # noqa: PLC0415

                img = wx.Image(str(bg_path), wx.BITMAP_TYPE_JPEG)
                if not img.IsOk():
                    _log.debug("Immagine sfondo non valida: %s", bg_path)
                    return None
                self._bg_source = img
            except ImportError:
                return None

        if self._bg_source is None:
            return None

        try:
            import wx  # noqa: PLC0415

            img = self._bg_source.Copy()  # type: ignore[union-attr]
            img.Rescale(width, height, wx.IMAGE_QUALITY_HIGH)
            bmp: object = wx.Bitmap(img)
            self._bg_cache[bg_key] = bmp
            return bmp
        except ImportError:
            return None

    def invalidate_size_cache(self) -> None:
        """Invalidate all cached scaled bitmaps.

        Clears ``_cache`` and ``_bg_cache`` so that the next call to
        ``get_bitmap`` or ``get_background_bitmap`` rescales from the cached
        source image. Source images (``_sources``, ``_bg_source``) are
        preserved to avoid unnecessary disk I/O.
        """
        self._cache.clear()
        self._bg_cache.clear()
