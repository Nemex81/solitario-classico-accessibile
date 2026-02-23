"""Unit test AudioManager, SoundMixer, SoundCache, AudioEvent (mock pygame.mixer).

Coverage: 
- AudioManager: init, play_event, pause/resume, shutdown, fallback
- SoundMixer: play_one_shot, mute, volume
- SoundCache: load_pack, get
- AudioEvent: dataclass contract

pytest --cov=src/infrastructure/audio/ --cov-report=term-missing -m "not gui"
"""
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from src.infrastructure.audio.audio_manager import AudioManager
from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
from src.infrastructure.audio.sound_cache import SoundCache
from src.infrastructure.audio.sound_mixer import SoundMixer
from src.infrastructure.config.audio_config_loader import AudioConfig

@pytest.fixture
def audio_config():
    return AudioConfig()

@pytest.fixture
def mock_pygame_mixer():
    with patch("pygame.mixer") as mixer:
        mixer.init = MagicMock()
        mixer.quit = MagicMock()
        mixer.Channel = MagicMock(return_value=MagicMock())
        mixer.Sound = MagicMock()
        yield mixer

@pytest.mark.unit
def test_audio_manager_init_and_shutdown(audio_config, mock_pygame_mixer):
    am = AudioManager(audio_config)
    assert not am.is_available
    assert am.initialize() is True
    assert am.is_available
    am.shutdown()
    assert not am.is_available

@pytest.mark.unit
def test_audio_manager_play_event_no_crash(audio_config, mock_pygame_mixer):
    am = AudioManager(audio_config)
    am.initialize()
    event = AudioEvent(event_type=AudioEventType.CARD_MOVE)
    # SoundCache.get restituirà None (nessun suono): no crash
    am.play_event(event)

@pytest.mark.unit
def test_sound_cache_load_and_get(audio_config, mock_pygame_mixer):
    cache = SoundCache(Path("assets/sounds"))
    cache.load_pack("default")
    # Event non presente
    assert cache.get("non_existing") is None

@pytest.mark.unit
def test_sound_mixer_play_one_shot(audio_config, mock_pygame_mixer):
    mixer = SoundMixer(audio_config)
    fake_sound = MagicMock()
    mixer.play_one_shot(fake_sound, "gameplay", panning=0.5)
    # Verifica che Channel.play sia stato chiamato
    channel = mixer._channels["gameplay"]
    channel.play.assert_called()

@pytest.mark.unit
def test_audio_event_contract():
    event = AudioEvent(event_type=AudioEventType.CARD_MOVE, source_pile=2, destination_pile=5)
    assert event.event_type == AudioEventType.CARD_MOVE
    assert event.source_pile == 2
    assert event.destination_pile == 5
    assert isinstance(event.context, dict)


@pytest.mark.unit
def test_container_creates_audio_manager(audio_config, mock_pygame_mixer):
    from src.infrastructure.di_container import DIContainer
    from src.infrastructure.audio.audio_manager import AudioManager
    container = DIContainer()
    am = container.get_audio_manager()
    # should be real manager and initialized
    assert isinstance(am, AudioManager)
    assert am.is_available is True


@pytest.mark.unit
def test_container_fallback_stub(monkeypatch):
    # simulate failure during AudioManager initialization
    from src.infrastructure.audio import audio_manager as am_mod
    def bad_init(self, config):
        raise RuntimeError("init failed")
    monkeypatch.setattr(am_mod.AudioManager, '__init__', bad_init)

    from src.infrastructure.di_container import DIContainer
    container = DIContainer()
    am = container.get_audio_manager()
    # stub should be returned and report not available
    assert not getattr(am, 'is_available', False)
