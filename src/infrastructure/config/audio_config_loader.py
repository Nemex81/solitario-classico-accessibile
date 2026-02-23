"""Audio system configuration loader (pattern scoring_config_loader.py).

Carica e valida la configurazione audio da audio_config.json.
Degradazione graziosa: fallback ai default se file assente/corrotto.
"""

from dataclasses import dataclass, field
from typing import Dict
import json
import os

CONFIG_PATH = os.path.join("config", "audio_config.json")

@dataclass
class AudioConfig:
    """Configurazione sistema audio.
    Versione: v3.4.0 | v1.1: pile_panning rimosso, calcolo dinamico.
    """
    version: str = "1.0"
    active_sound_pack: str = "default"
    bus_volumes: Dict[str, int] = field(default_factory=lambda: {
        "gameplay": 80, "ui": 70, "ambient": 40, "music": 30, "voice": 90
    })
    bus_muted: Dict[str, bool] = field(default_factory=lambda: {
        "gameplay": False, "ui": False, "ambient": False, "music": False, "voice": False
    })
    mixer_params: Dict[str, int] = field(default_factory=lambda: {
        "frequency": 44100, "size": -16, "channels": 2, "buffer": 512
    })

class AudioConfigLoader:
    """Loader per audio_config.json con fallback e validazione.
    Pattern identico a scoring_config_loader.py.
    """
    @classmethod
    def load(cls, path: str = CONFIG_PATH) -> AudioConfig:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls._parse_and_validate(data)
        except Exception:
            return cls.fallback_default()

    @classmethod
    def fallback_default(cls) -> AudioConfig:
        return AudioConfig()

    @classmethod
    def _parse_and_validate(cls, data: dict) -> AudioConfig:
        # Version check
        version = data.get("version", "1.0")
        active_sound_pack = data.get("active_sound_pack", "default")
        bus_volumes = data.get("bus_volumes", AudioConfig().bus_volumes)
        bus_muted = data.get("bus_muted", AudioConfig().bus_muted)
        mixer_params = data.get("mixer_params", AudioConfig().mixer_params)
        return AudioConfig(
            version=version,
            active_sound_pack=active_sound_pack,
            bus_volumes=bus_volumes,
            bus_muted=bus_muted,
            mixer_params=mixer_params
        )
