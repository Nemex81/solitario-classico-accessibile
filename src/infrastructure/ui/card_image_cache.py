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
    "ASSO": "1",
    "J": "11",
    "JACK": "11",
    "Q": "12",
    "REGINA": "12",
    "K": "13",
    "RE": "13",
}

# --- Neapolitan deck helpers ---
_NAPOL_RANK_POS: dict[str, int] = {
    "Asso": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7,
    "Regina": 8, "Cavallo": 9, "Re": 10,
}
_NAPOL_SUIT_OFFSET: dict[str, int] = {
    "bastoni": 0, "coppe": 10, "denari": 20, "spade": 30,
}
_NAPOL_SEQ_TO_NOME: dict[int, str] = {
    1: "Asso", 2: "Due", 3: "Tre", 4: "Quattro", 5: "Cinque",
    6: "Sei", 7: "Sette", 8: "Otto", 9: "Nove", 10: "Dieci",
}
# Naming exception: seq 10 (Dieci) of bastoni has capital "Bastoni"
_NAPOL_SEME_OVERRIDE: dict[tuple[int, int], str] = {
    (10, 0): "Bastoni",
}


class CardImageCache:
    """Lazy-loading cache for playing card and background bitmap images.

    Maintains two internal caches:
    - ``_sources``: original wx.Image objects loaded from disk (per card).
    - ``_cache``: scaled wx.Bitmap objects per (rank, suit, width, height).

    Calling ``invalidate_size_cache()`` drops only the scaled bitmaps so that
    a layout resize does not force a full disk reload.
    """

    def __init__(
        self,
        assets_base_path: str | os.PathLike[str],
        deck_type: str = "french",
    ) -> None:
        """Initialise with the project root (parent of the ``assets/`` directory).

        Args:
            assets_base_path: Absolute or relative path to the project root.
                              Card images are expected at
                              ``<base>/assets/img/carte_francesi/<rank>-<suit>.jpg``
                              or ``<base>/assets/img/carte_napoletane/{seq}_{nome}_di_{seme}.jpg``
                              and the background at
                              ``<base>/assets/img/Sfondo tavolo verde.jpg``.
            deck_type: ``"french"`` (default) or ``"neapolitan"``.
        """
        self._base_path: Path = Path(assets_base_path)
        self._deck_type: str = deck_type
        # (rank, suit) → wx.Image | None  (None = file missing / wx unavailable)
        self._sources: dict[tuple[str, str], object | None] = {}
        # (rank, suit, w, h) → wx.Bitmap
        self._cache: dict[tuple[str, str, int, int], object] = {}
        # background wx.Image source
        self._bg_source: object | None = None
        # (w, h) → wx.Bitmap
        self._bg_cache: dict[tuple[int, int], object] = {}
        # back-card image (neapolitan only)
        self._back_source: object | None = None
        # (w, h) → wx.Bitmap
        self._back_cache: dict[tuple[int, int], object] = {}

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
        normalized_rank = rank.strip().upper()
        return _RANK_MAP.get(normalized_rank, rank)

    def _load_source(self, rank: str, suit: str) -> object | None:
        """Load a wx.Image for the given card from disk.

        Routes to the neapolitan loader when ``deck_type="neapolitan"``,
        otherwise loads from the French cards directory.

        Args:
            rank: Card rank.
            suit: Card suit.

        Returns:
            A ``wx.Image`` instance if the file exists and wx is available,
            otherwise ``None``.
        """
        if self._deck_type == "neapolitan":
            return self._load_source_napoletane(rank, suit)
        return self._load_source_french(rank, suit)

    def _load_source_french(self, rank: str, suit: str) -> object | None:
        """Load a wx.Image from the French cards directory.

        Args:
            rank: Card rank (``"A"``, ``"2"``–``"10"``, ``"J"``, ``"Q"``, ``"K"``).
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
            / "carte_francesi"
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

    def _load_source_napoletane(self, rank: str, suit: str) -> object | None:
        """Load a wx.Image from the Neapolitan cards directory.

        Args:
            rank: Domain rank (``"Asso"``, ``"2"``–``"7"``, ``"Regina"``,
                  ``"Cavallo"``, ``"Re"``).
            suit: Domain suit (``"bastoni"``, ``"coppe"``, ``"denari"``,
                  ``"spade"``).

        Returns:
            A ``wx.Image`` instance if the file exists and wx is available,
            otherwise ``None``.
        """
        rank_pos = _NAPOL_RANK_POS.get(rank)
        suit_offset = _NAPOL_SUIT_OFFSET.get(suit)
        if rank_pos is None or suit_offset is None:
            _log.debug(
                "Rank/suit napoletano non riconosciuto: %s-%s", rank, suit
            )
            return None
        seq = suit_offset + rank_pos
        nome = _NAPOL_SEQ_TO_NOME[rank_pos]
        suit_in_file = _NAPOL_SEME_OVERRIDE.get((rank_pos, suit_offset), suit)
        filename = f"{seq}_{nome}_di_{suit_in_file}.jpg"
        file_path = (
            self._base_path / "assets" / "img" / "carte_napoletane" / filename
        )
        if not file_path.exists():
            _log.debug("Immagine napoletana non trovata: %s", filename)
            return None
        try:
            import wx  # type: ignore[import-untyped]  # noqa: PLC0415

            img = wx.Image(str(file_path), wx.BITMAP_TYPE_JPEG)
            if not img.IsOk():
                _log.debug("Immagine napoletana non valida: %s", filename)
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

        Clears ``_cache``, ``_bg_cache`` and ``_back_cache`` so that the next
        call to ``get_bitmap``, ``get_background_bitmap`` or
        ``get_back_bitmap`` rescales from the cached source image. Source
        images (``_sources``, ``_bg_source``, ``_back_source``) are preserved
        to avoid unnecessary disk I/O.
        """
        self._cache.clear()
        self._bg_cache.clear()
        self._back_cache.clear()

    def get_back_bitmap(self, width: int, height: int) -> object | None:
        """Return a scaled ``wx.Bitmap`` for the card back (neapolitan only).

        For French decks this always returns ``None`` — the back is drawn
        procedurally by ``CardRenderer._draw_back()``.

        Args:
            width: Target width in pixels.
            height: Target height in pixels.

        Returns:
            A ``wx.Bitmap`` scaled to ``(width, height)`` when
            ``deck_type="neapolitan"`` and the image file exists;
            ``None`` otherwise.
        """
        if self._deck_type != "neapolitan":
            return None
        back_key = (width, height)
        if back_key in self._back_cache:
            return self._back_cache[back_key]

        if self._back_source is None:
            back_path = (
                self._base_path
                / "assets"
                / "img"
                / "carte_napoletane"
                / "41_Carte_Napoletane_retro.jpg"
            )
            if not back_path.exists():
                _log.debug("Immagine dorso napoletano non trovata: %s", back_path)
                return None
            try:
                import wx  # noqa: PLC0415

                img = wx.Image(str(back_path), wx.BITMAP_TYPE_JPEG)
                if not img.IsOk():
                    _log.debug("Immagine dorso napoletano non valida")
                    return None
                self._back_source = img
            except ImportError:
                return None

        if self._back_source is None:
            return None

        try:
            import wx  # noqa: PLC0415

            img = self._back_source.Copy()  # type: ignore[attr-defined]
            img.Rescale(width, height, wx.IMAGE_QUALITY_HIGH)
            bmp: object = wx.Bitmap(img)
            self._back_cache[back_key] = bmp
            return bmp
        except ImportError:
            return None
