"""AudioManager: orchestratore principale sistema audio.

Riceve AudioEvent dai controller Application, consulta SoundCache,
calcola panning, delega la riproduzione a SoundMixer.
Gestisce ciclo di vita, pause, resume, shutdown, salvataggio settings.
"""

from typing import Optional
from pathlib import Path
import pygame
import logging
from src.infrastructure.audio.audio_events import AudioEvent
from src.infrastructure.config.audio_config_loader import AudioConfig
from src.infrastructure.audio.sound_cache import SoundCache
from src.infrastructure.audio.sound_mixer import SoundMixer

_game_logger = logging.getLogger('game')

class AudioManager:
    """Unico punto di ingresso al sistema audio.
    Stati: NON_INITIALIZED → ACTIVE ⇄ LOOPS_PAUSED → SHUTDOWN
    """
    def __init__(self, config: AudioConfig, sounds_base_path: Optional[Path] = None) -> None:
        self.config = config
        self.sounds_base_path = sounds_base_path or Path("assets/sounds")
        self.sound_cache = SoundCache(self.sounds_base_path)
        # sound_mixer cannot be created until pygame.mixer.init() succeeds;
        # instantiate lazily in initialize()
        self.sound_mixer: Optional[SoundMixer] = None
        self._initialized = False

    def initialize(self) -> bool:
        """Inizializza pygame.mixer e SoundCache. Returns True se successo, False con fallback stub."""
        try:
            pygame.mixer.init(
                frequency=self.config.mixer_params["frequency"],
                size=self.config.mixer_params["size"],
                channels=self.config.mixer_params["channels"],
                buffer=self.config.mixer_params["buffer"]
            )
            # create mixer helper now that mixer is ready
            self.sound_mixer = SoundMixer(self.config)
            self.sound_cache.load_pack(self.config.active_sound_pack)
            self._initialized = True
            _game_logger.info("AudioManager initialized successfully.")
            return True
        except Exception as e:
            _game_logger.exception(f"AudioManager initialization failed: {e}")
            # if mixer fails, leave in uninitialized state so subsequent calls are no-op
            self._initialized = False
            return False

    def play_event(self, event: AudioEvent) -> None:
        """Riproduce il suono associato all'evento con panning spaziale.
        
        Design v3.4.1: un evento = un suono fisso per pack. Nessuna
        selezione casuale tra varianti; varietà solo tramite cambio pack.

        Args:
            event: AudioEvent con tipo evento e metadata spaziale
        """
        if not self._initialized:
            _game_logger.debug(f"AudioManager not initialized, skipping event: {event.event_type}")
            return
        sound = self.sound_cache.get(event.event_type)
        if sound is None:
            _game_logger.warning(f"No sound mapped for event: {event.event_type}")
            return
        # Calcola panning stereo basato su posizione pile (0-12)
        panning = self._get_panning_for_event(event)
        # Determina bus audio
        bus_name = self._get_bus_for_event(event.event_type)
        # Riproduci il suono
        self.sound_mixer.play_one_shot(sound, bus_name, panning)
        _game_logger.debug(
            f"Played event: {event.event_type} → bus: {bus_name}, panning: {panning:.2f}"
        )

    def pause_all_loops(self) -> None:
        """Sospende bus Ambient e Music (chiamato da Presentation su EVT_ACTIVATE)."""
        if self.sound_mixer:
            self.sound_mixer.pause_loops()

    def resume_all_loops(self) -> None:
        """Riprende bus Ambient e Music."""
        if self.sound_mixer:
            self.sound_mixer.resume_loops()

    def resume_all_loops(self) -> None:
        """Riprende bus Ambient e Music."""
        self.sound_mixer.resume_loops()

    def set_bus_volume(self, bus_name: str, volume: int) -> None:
        if self.sound_mixer:
            self.sound_mixer.set_bus_volume(bus_name, volume)

    def toggle_bus_mute(self, bus_name: str) -> bool:
        return self.sound_mixer.toggle_bus_mute(bus_name) if self.sound_mixer else False

    def get_bus_volume(self, bus_name: str) -> int:
        return self.sound_mixer.get_bus_volume(bus_name) if self.sound_mixer else 0

    def is_bus_muted(self, bus_name: str) -> bool:
        return self.sound_mixer.is_bus_muted(bus_name) if self.sound_mixer else False

    def save_settings(self) -> None:
        """Scrive volumi e stato mute correnti in audio_config.json."""
        import json
        path = self.sounds_base_path.parent / "config" / "audio_config.json"
        data = {
            "version": self.config.version,
            "active_sound_pack": self.config.active_sound_pack,
            "bus_volumes": self.sound_mixer._volumes,
            "bus_muted": self.sound_mixer._muted,
            "mixer_params": self.config.mixer_params
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            _game_logger.info("Audio settings saved.")
        except Exception as e:
            _game_logger.warning(f"Failed to save audio settings: {e}")

    def shutdown(self) -> None:
        """Salva settings, ferma tutti i canali, chiama pygame.mixer.quit()."""
        self.save_settings()
        if self.sound_mixer:
            self.sound_mixer.stop_all()
        pygame.mixer.quit()
        self._initialized = False

    @property
    def is_available(self) -> bool:
        """True se pygame.mixer è inizializzato e il sistema è operativo."""
        return self._initialized

    def _get_panning_for_event(self, event: AudioEvent) -> float:
        """Determina il panning dall'evento usando formula lineare.
        Priorità: destination_pile > source_pile > 0.0 (centro)
        """
        pile_index = event.destination_pile if event.destination_pile is not None else event.source_pile
        if pile_index is None:
            return 0.0
        panning = (pile_index / 12.0) * 2.0 - 1.0
        return max(-1.0, min(1.0, panning))

    def _get_bus_for_event(self, event_type: str) -> str:
        """Mapping evento → bus audio secondo tabella di mapping."""
        # Mapping semplificato, da estendere se necessario
        gameplay = ["card_move", "card_select", "card_drop", "foundation_drop", "invalid_move", "tableau_bumper", "stock_draw", "waste_drop"]
        ui = ["ui_navigate", "ui_select", "ui_cancel", "mixer_opened", "timer_warning", "timer_expired"]
        ambient = ["ambient_loop"]
        music = ["music_loop"]
        voice = ["game_won"]
        if event_type in gameplay:
            return "gameplay"
        if event_type in ui:
            return "ui"
        if event_type in ambient:
            return "ambient"
        if event_type in music:
            return "music"
        if event_type in voice:
            return "voice"
        return "gameplay"


# ------------------------------------------------------------------
# Stub implementation used when pygame is unavailable or initialization fails
# ------------------------------------------------------------------
class _AudioManagerStub:
    """Lightweight no-op substitute for AudioManager.

    Returned by DIContainer.get_audio_manager() when audio setup cannot be
    completed. All methods are safe no-ops so callers never need to check
    for None – they can simply call the same API as the real manager.
    """

    def initialize(self) -> bool:  # keep API compatibility
        return False

    def play_event(self, event: AudioEvent) -> None:
        pass

    def pause_all_loops(self) -> None:
        pass

    def resume_all_loops(self) -> None:
        pass

    def set_bus_volume(self, bus_name: str, volume: int) -> None:
        pass

    def toggle_bus_mute(self, bus_name: str) -> bool:
        return False

    def get_bus_volume(self, bus_name: str) -> int:
        return 0

    def is_bus_muted(self, bus_name: str) -> bool:
        return False

    def save_settings(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    @property
    def is_available(self) -> bool:
        return False
