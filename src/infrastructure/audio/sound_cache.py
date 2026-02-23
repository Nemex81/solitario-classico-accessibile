"""SoundCache: caricamento e gestione asset audio in RAM.

Carica tutti i file WAV del sound pack attivo in RAM come pygame.Sound.
Degradazione graziosa: file mancante → warning log, entry None.
"""

from typing import Dict, Optional, List, Union
from pathlib import Path
import pygame
import logging

_game_logger = logging.getLogger('game')

class SoundCache:
    def __init__(self, sounds_base_path: Path) -> None:
        self.sounds_base_path = sounds_base_path
        self._cache: Dict[str, Union[pygame.mixer.Sound, None, List[pygame.mixer.Sound]]] = {}
        self._pack_name: Optional[str] = None

    def load_pack(self, pack_name: str) -> None:
        """Carica tutti i WAV del pack in RAM come pygame.Sound.
        File assenti: warning nel log, entry None (degradazione graziosa).
        """
        self._cache.clear()
        self._pack_name = pack_name
        pack_path = self.sounds_base_path / pack_name
        # Mapping evento → file(s) WAV
        EVENT_TO_FILES = {
            # Gameplay bus
            "card_move": ["gameplay/card_move_1.wav", "gameplay/card_move_2.wav", "gameplay/card_move_3.wav"],
            "card_select": ["gameplay/card_select.wav"],
            "card_drop": ["gameplay/card_drop.wav"],
            "foundation_drop": ["gameplay/foundation_drop.wav"],
            "invalid_move": ["gameplay/invalid_move.wav"],
            "tableau_bumper": ["gameplay/bumper.wav"],
            "stock_draw": ["gameplay/stock_draw.wav"],
            "waste_drop": ["gameplay/waste_drop.wav"],
            # UI bus
            "ui_navigate": ["ui/navigate.wav"],
            "ui_select": ["ui/select.wav"],
            "ui_cancel": ["ui/cancel.wav"],
            "mixer_opened": ["ui/mixer_opened.wav"],
            # Ambient bus
            "ambient_loop": ["ambient/room_loop.wav"],
            # Music bus
            "music_loop": ["music/music_loop.wav"],
            # Voice bus
            "game_won": ["voice/victory.wav"],
            # Timer events
            "timer_warning": ["ui/navigate.wav"],
            "timer_expired": ["ui/cancel.wav"],
        }
        for event_type, files in EVENT_TO_FILES.items():
            loaded_sounds = []
            for rel_path in files:
                file_path = pack_path / rel_path
                try:
                    sound = pygame.mixer.Sound(str(file_path))
                    loaded_sounds.append(sound)
                except Exception:
                    _game_logger.warning(f"Sound asset missing: {file_path}")
                    loaded_sounds.append(None)
            # Se solo una variante, salva direttamente; se più, salva lista
            self._cache[event_type] = loaded_sounds if len(loaded_sounds) > 1 else loaded_sounds[0]

    def get(self, event_type: str) -> Optional[Union[pygame.mixer.Sound, List[pygame.mixer.Sound]]]:
        """Restituisce il Sound pre-caricato per il tipo evento, o None se assente."""
        return self._cache.get(event_type)

    def clear(self) -> None:
        """Svuota la cache (usato su shutdown o cambio pack)."""
        self._cache.clear()
        self._pack_name = None
