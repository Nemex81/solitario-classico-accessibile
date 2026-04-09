"""Unit test AudioManager, SoundMixer, SoundCache, AudioEvent (mock pygame.mixer).

Coverage: 
- AudioManager: init, play_event, pause/resume, shutdown, fallback
- SoundMixer: play_one_shot, mute, volume
- SoundCache: load_pack, get
- AudioEvent: dataclass contract

pytest --cov=src/infrastructure/audio/ --cov-report=term-missing -m "not gui"
"""
import pytest
import math
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
    cache.load_pack("default", {})
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
def test_sound_mixer_play_one_shot_applies_bus_volume_to_panning(audio_config, mock_pygame_mixer):
    audio_config.bus_volumes["gameplay"] = 30
    mixer = SoundMixer(audio_config)
    fake_sound = MagicMock()
    mixer.play_one_shot(fake_sound, "gameplay", panning=0.5)
    channel = mixer._channels["gameplay"]
    expected_left = math.cos((0.5 + 1.0) * (math.pi / 4.0)) * 0.3
    expected_right = math.sin((0.5 + 1.0) * (math.pi / 4.0)) * 0.3
    channel.set_volume.assert_any_call(expected_left, expected_right)


@pytest.mark.unit
def test_sound_mixer_equal_power_pan_keeps_total_power_stable(audio_config, mock_pygame_mixer):
    mixer = SoundMixer(audio_config)
    center_channel = MagicMock()
    edge_channel = MagicMock()

    mixer._apply_panning(center_channel, 0.0, 0.3)
    mixer._apply_panning(edge_channel, 1.0, 0.3)

    center_left, center_right = center_channel.set_volume.call_args.args
    edge_left, edge_right = edge_channel.set_volume.call_args.args

    center_power = (center_left ** 2) + (center_right ** 2)
    edge_power = (edge_left ** 2) + (edge_right ** 2)

    assert math.isclose(center_power, edge_power, rel_tol=1e-6)

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
def test_audio_manager_respects_enabled_events(audio_config, mock_pygame_mixer):
    # disable a specific event via config and ensure play_event does nothing
    audio_config.enabled_events = {"card_move": False}
    am = AudioManager(audio_config)
    am.initialize()
    # patch sound_cache to return a dummy sound so we would normally play
    am.sound_cache.get = lambda et: object()
    called = False
    def fake_play(sound, bus, panning):
        nonlocal called
        called = True
    am.sound_mixer.play_one_shot = fake_play
    # attempt to play disabled event
    from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
    am.play_event(AudioEvent(event_type=AudioEventType.CARD_MOVE))
    assert not called, "Event should have been skipped by config"


@pytest.mark.unit
def test_audio_manager_routes_menu_open_to_ui_bus(audio_config, mock_pygame_mixer):
    am = AudioManager(audio_config)
    am.initialize()
    am.sound_cache.get = lambda et: object()
    routed = {}

    def fake_play(sound, bus, panning):
        routed["bus"] = bus

    am.sound_mixer.play_one_shot = fake_play
    am.play_event(AudioEvent(event_type=AudioEventType.UI_MENU_OPEN))
    assert routed["bus"] == "ui"

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
