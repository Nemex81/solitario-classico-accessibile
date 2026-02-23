"""SoundMixer: gestione 5 bus audio, volumi, panning, loop.

Gestisce i canali pygame.mixer, volumi, mute, panning stereo constant-power.
"""

from typing import Dict
import pygame
import logging

_game_logger = logging.getLogger('game')

BUS_NAMES = ("gameplay", "ui", "ambient", "music", "voice")

class SoundMixer:
    def __init__(self, config) -> None:
        """Crea e configura i 5 canali pygame.mixer con volumi da config."""
        self._channels: Dict[str, pygame.mixer.Channel] = {}
        self._volumes: Dict[str, int] = dict(config.bus_volumes)
        self._muted: Dict[str, bool] = dict(config.bus_muted)
        self._looping: Dict[str, bool] = {bus: False for bus in BUS_NAMES}
        for idx, bus in enumerate(BUS_NAMES):
            self._channels[bus] = pygame.mixer.Channel(idx)
            self._channels[bus].set_volume(self._get_volume(bus))

    def play_one_shot(self, sound: pygame.mixer.Sound, bus_name: str, panning: float = 0.0) -> None:
        """Riproduce un suono one-shot sul bus specificato con panning -1.0..+1.0."""
        if self._muted.get(bus_name, False):
            return
        channel = self._channels[bus_name]
        self._apply_panning(channel, panning)
        channel.play(sound)

    def play_loop(self, sound: pygame.mixer.Sound, bus_name: str) -> None:
        """Avvia un loop infinito sul bus specificato (bus ambient/music)."""
        if self._muted.get(bus_name, False):
            return
        channel = self._channels[bus_name]
        channel.play(sound, loops=-1)
        self._looping[bus_name] = True

    def pause_loops(self) -> None:
        """Sospende bus ambient e music (one-shot rimangono attivi)."""
        for bus in ("ambient", "music"):
            channel = self._channels[bus]
            channel.pause()
            self._looping[bus] = False

    def resume_loops(self) -> None:
        """Riprende bus ambient e music."""
        for bus in ("ambient", "music"):
            channel = self._channels[bus]
            channel.unpause()
            self._looping[bus] = True

    def stop_all(self) -> None:
        """Ferma tutti i canali (usato su shutdown)."""
        for channel in self._channels.values():
            channel.stop()
        for bus in BUS_NAMES:
            self._looping[bus] = False

    def set_bus_volume(self, bus_name: str, volume: int) -> None:
        """Imposta volume bus 0-100 (convertito a float 0.0-1.0 internamente)."""
        self._volumes[bus_name] = volume
        self._channels[bus_name].set_volume(self._get_volume(bus_name))

    def toggle_bus_mute(self, bus_name: str) -> bool:
        """Toggle mute del bus. Restituisce nuovo stato mute (True=silenziato)."""
        self._muted[bus_name] = not self._muted[bus_name]
        return self._muted[bus_name]

    def get_bus_volume(self, bus_name: str) -> int:
        """Restituisce volume corrente del bus (int 0-100)."""
        return self._volumes.get(bus_name, 100)

    def is_bus_muted(self, bus_name: str) -> bool:
        return self._muted.get(bus_name, False)

    def _get_volume(self, bus_name: str) -> float:
        """Converte volume int 0-100 in float 0.0-1.0."""
        return max(0.0, min(1.0, self._volumes.get(bus_name, 100) / 100.0))

    def _apply_panning(self, channel: pygame.mixer.Channel, panning: float) -> None:
        """Applica panning stereo constant-power pan law.
        panning: float -1.0 (sinistra) ... +1.0 (destra)
        """
        if panning < 0.0:
            left = 1.0
            right = 1.0 + panning
        else:
            left = 1.0 - panning
            right = 1.0
        left = max(0.0, min(1.0, left))
        right = max(0.0, min(1.0, right))
        channel.set_volume(left, right)
