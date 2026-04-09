"""Audio system configuration loader (pattern scoring_config_loader.py).

Carica e valida la configurazione audio da audio_config.json.
Degradazione graziosa: fallback ai default se file assente/corrotto.
"""

from dataclasses import dataclass, field
from typing import Dict, Union
import json
import os
from pathlib import Path

from src.infrastructure.config.runtime_root import get_runtime_root
from src.infrastructure.audio.audio_events import AudioEventType

CONFIG_PATH: str = str(get_runtime_root() / "config" / "audio_config.json")

DEFAULT_EVENT_SOUNDS: Dict[str, str] = {
    "CARD_MOVE": "gameplay/card_move.wav",
    "CARD_SELECT": "ui/select.wav",
    "CARD_FLIP": "gameplay/card_flip.wav",
    "CARD_SHUFFLE": "gameplay/card_shuffle.wav",
    "CARD_SHUFFLE_WASTE": "gameplay/card_shuffle_alt.wav",
    "FOUNDATION_DROP": "gameplay/foundation_drop.wav",
    "INVALID_MOVE": "gameplay/invalid_move.wav",
    "TABLEAU_BUMPER": "gameplay/invalid_move.wav",
    "TABLEAU_DROP": "gameplay/tableau_drop.wav",
    "STOCK_DRAW": "gameplay/stock_draw.wav",
    "CARDS_EXHAUSTED": "ui/boundary_hit.wav",
    "MULTI_CARD_MOVE": "gameplay/foundation_drop.wav",
    "UI_NAVIGATE": "ui/navigate.wav",
    "UI_NAVIGATE_FRAME": "ui/navigate_alt.wav",
    "UI_NAVIGATE_PILE": "ui/focus_change.wav",
    "UI_SELECT": "ui/select.wav",
    "UI_CANCEL": "ui/cancel.wav",
    "UI_CONFIRM": "ui/confirm.wav",
    "UI_TOGGLE": "ui/button_hover.wav",
    "UI_FOCUS_CHANGE": "ui/focus_change.wav",
    "UI_BOUNDARY_HIT": "ui/boundary_hit.wav",
    "UI_NOTIFICATION": "ui/notification.wav",
    "UI_ERROR": "ui/error.wav",
    "UI_MENU_OPEN": "ui/menu_open.wav",
    "UI_MENU_CLOSE": "ui/menu_close.wav",
    "UI_BUTTON_CLICK": "ui/button_click.wav",
    "UI_BUTTON_HOVER": "ui/button_hover.wav",
    "MIXER_OPENED": "ui/menu_open.wav",
    "SETTING_SAVED": "ui/select.wav",
    "SETTING_CHANGED": "ui/focus_change.wav",
    "SETTING_LEVEL_CHANGED": "ui/focus_change.wav",
    "SETTING_VOLUME_CHANGED": "ui/focus_change.wav",
    "SETTING_MUSIC_CHANGED": "ui/focus_change.wav",
    "SETTING_SWITCH_ON": "ui/button_click.wav",
    "SETTING_SWITCH_OFF": "ui/button_hover.wav",
    "CARD_DROP": "gameplay/tableau_drop.wav",
    "WASTE_DROP": "gameplay/stock_draw.wav",
    "GAME_WON": "voice/victory.wav",
    "WELCOME_MESSAGE": "voice/welcome_italian.wav",
    "TIMER_WARNING": "ui/navigate.wav",
    "TIMER_EXPIRED": "ui/cancel.wav",
    "MUSIC_LOOP": "music/ambient_music_01.wav",
    "AMBIENT_LOOP": "ambient/game_start_ambient.wav",
}


def _build_default_enabled_events() -> Dict[str, bool]:
    enabled_events: Dict[str, bool] = {}
    for key in DEFAULT_EVENT_SOUNDS:
        event_value = getattr(AudioEventType, key, key.lower())
        enabled_events[event_value] = True
    return enabled_events


DEFAULT_ENABLED_EVENTS: Dict[str, bool] = _build_default_enabled_events()

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
    # new in v3.4.2: allow disabling individual events for debugging or
    # accessibility configuration. Missing keys are treated as enabled.
    enabled_events: Dict[str, bool] = field(default_factory=lambda: dict(DEFAULT_ENABLED_EVENTS))
    # v3.5.0: mapping event -> sound file and preload flag
    event_sounds: Dict[str, str] = field(default_factory=lambda: dict(DEFAULT_EVENT_SOUNDS))
    preload_all_event_sounds: bool = True

class AudioConfigLoader:
    """Loader per audio_config.json con fallback e validazione.
    Pattern identico a scoring_config_loader.py.
    """
    @classmethod
    def load(cls, path: Union[str, Path] = CONFIG_PATH) -> AudioConfig:
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
        enabled_events = data.get("enabled_events") or AudioConfig().enabled_events
        event_sounds = data.get("event_sounds") or AudioConfig().event_sounds
        preload_flag = data.get("preload_all_event_sounds", True)
        return AudioConfig(
            version=version,
            active_sound_pack=active_sound_pack,
            bus_volumes=bus_volumes,
            bus_muted=bus_muted,
            mixer_params=mixer_params,
            enabled_events=enabled_events,
            event_sounds=event_sounds,
            preload_all_event_sounds=preload_flag,
        )
