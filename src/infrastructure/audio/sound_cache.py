"""SoundCache: caricamento e gestione asset audio in RAM.

Carica tutti i file WAV del sound pack attivo in RAM come pygame.Sound.
Degradazione graziosa: file mancante → warning log, entry None.
"""

from typing import Dict, Optional
from pathlib import Path
import pygame
import logging

_game_logger = logging.getLogger('game')

class SoundCache:
    def __init__(self, sounds_base_path: Path) -> None:
        self.sounds_base_path = sounds_base_path
        self._cache: Dict[str, Optional[pygame.mixer.Sound]] = {}
        self._pack_name: Optional[str] = None

    def load_pack(self, pack_name: str) -> None:
        """Carica tutti i WAV del pack in RAM come pygame.Sound.
        File assenti: warning nel log, entry None (degradazione graziosa).
        """
        self._cache.clear()
        self._pack_name = pack_name
        pack_path = self.sounds_base_path / pack_name
        # Mapping evento → file WAV singolo (design v3.4.1)
        EVENT_TO_FILES = {
            # ========================================
            # GAMEPLAY BUS
            # ========================================
            "card_move": "gameplay/card_move.wav",
            "card_select": "gameplay/card_place.wav",      # riuso file
            "card_drop": "gameplay/card_place.wav",        # riuso file
            "foundation_drop": "gameplay/foundation_drop.wav",
            "invalid_move": "gameplay/invalid_move.wav",
            "tableau_bumper": "gameplay/invalid_move.wav", # riuso invalid_move
            "stock_draw": "gameplay/stock_draw.wav",
            "waste_drop": "gameplay/tableau_drop.wav",     # riuso tableau_drop
            # ========================================
            # UI BUS
            # ========================================
            "ui_navigate": "ui/navigate.wav",
            "ui_select": "ui/select.wav",
            "ui_cancel": "ui/cancel.wav",
            "mixer_opened": "ui/mixer_opened.wav",
            # ========================================
            # AMBIENT BUS
            # ========================================
            "ambient_loop": "ambient/room_loop.wav",
            # ========================================
            # MUSIC BUS
            # ========================================
            "music_loop": "music/music_loop.wav",
            # ========================================
            # VOICE BUS
            # ========================================
            "game_won": "voice/victory.wav",
            # ========================================
            # TIMER EVENTS
            # ========================================
            "timer_warning": "ui/navigate.wav",
            "timer_expired": "ui/cancel.wav",
        }

        # Carica ogni file WAV singolo
        for event_type, rel_path in EVENT_TO_FILES.items():
            file_path = pack_path / rel_path
            try:
                sound = pygame.mixer.Sound(str(file_path))
                self._cache[event_type] = sound
                _game_logger.debug(f"Loaded sound: {event_type} → {rel_path}")
            except Exception as e:
                _game_logger.warning(f"Sound asset missing: {file_path} (event: {event_type})")
                self._cache[event_type] = None

    def get(self, event_type: str) -> Optional[pygame.mixer.Sound]:
        """Restituisce il Sound pre-caricato per il tipo evento, o None se assente.
        
        Returns:
            pygame.mixer.Sound singolo (design v3.4.1: nessuna lista)
        """
        return self._cache.get(event_type)

    def clear(self) -> None:
        """Svuota la cache (usato su shutdown o cambio pack)."""
        self._cache.clear()
        self._pack_name = None
