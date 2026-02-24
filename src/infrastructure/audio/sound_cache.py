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

    def load_pack(self, pack_name: str, event_to_files: Dict[str, str]) -> None:
        """Carica tutti i WAV del pack in RAM come pygame.Sound.
        
        File assenti: warning nel log, entry None (degradazione graziosa).

        Args:
            pack_name: nome della cartella del sound pack (es. "default")
            event_to_files: mappa evento->percorso relativo (es. {"card_move": "gameplay/card_move.wav"}).
                            Fornita da AudioManager._load_event_mapping() caricata da JSON config.
        
        **v3.5.1**: Mapping JSON-driven è unica sorgente di verità. 
        Non esiste più fallback hardcoded legacy.
        """
        self._cache.clear()
        self._pack_name = pack_name
        pack_path = self.sounds_base_path / pack_name
        
        # Carica ogni file WAV dal mapping JSON-driven
        for event_type, rel_path in event_to_files.items():
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
