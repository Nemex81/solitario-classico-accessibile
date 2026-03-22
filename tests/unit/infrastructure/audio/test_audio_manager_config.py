import pytest
import logging
from unittest.mock import Mock

from src.infrastructure.audio.audio_manager import AudioManager
from src.infrastructure.audio.audio_events import AudioEventType
from src.infrastructure.config.audio_config_loader import AudioConfig


class DummyAudioMgr(AudioManager):
    # expose protected methods for testing
    pass


def make_config(event_sounds=None, preload_flag=True):
    cfg = AudioConfig()
    cfg.event_sounds = event_sounds or {}
    cfg.preload_all_event_sounds = preload_flag
    return cfg


@pytest.mark.unit
class TestAudioManagerConfig:
    def test_load_event_mapping_complete(self, caplog):
        caplog.set_level(logging.WARNING)
        cfg = make_config({"CARD_MOVE": "move.wav", "UI_SELECT": "select.wav"})
        am = AudioManager(cfg)
        mapping = am._event_sounds
        # Le chiavi nel mapping devono essere i valori stringa (es. "card_move"), non i nomi
        assert AudioEventType.CARD_MOVE in mapping
        assert mapping[AudioEventType.CARD_MOVE] == "move.wav"
        assert AudioEventType.UI_SELECT in mapping

    def test_unknown_event_key_logs_warning(self, caplog):
        caplog.set_level(logging.WARNING)
        cfg = make_config({"FOO_BAR": "x.wav"})
        am = AudioManager(cfg)
        # FOO_BAR non è una costante valida: deve essere skippato
        assert AudioEventType.CARD_MOVE not in am._event_sounds
        assert "unknown event" in caplog.text.lower()

    def test_fallback_when_no_section(self, caplog):
        caplog.set_level(logging.WARNING)
        cfg = make_config(None)
        am = AudioManager(cfg)
        assert am._event_sounds  # should have defaults
        assert "missing" in caplog.text.lower()

    def test_validate_completeness_logs_missing_files(self, caplog, tmp_path):
        caplog.set_level(logging.WARNING)
        cfg = make_config({"CARD_MOVE": "not_exist.wav"})
        am = AudioManager(cfg)
        # point sounds_base_path to tmp with empty pack folder
        am.sounds_base_path = tmp_path
        am.config.active_sound_pack = "pack"
        # call validation directly
        am._validate_config_completeness()
        assert "not found" in caplog.text.lower()

    def test_sound_cache_receives_mapping_on_initialize(self, monkeypatch, tmp_path):
        cfg = make_config({"CARD_MOVE": "move.wav"})
        am = AudioManager(cfg)
        # stub sound_cache.load_pack to capture mapping
        captured = {}
        def fake_load(pack, mapping=None):
            captured['pack'] = pack
            captured['mapping'] = mapping
        am.sound_cache.load_pack = fake_load
        # stub pygame.mixer.init to succeed
        monkeypatch.setattr('src.infrastructure.audio.audio_manager.pygame.mixer.init', lambda **kwargs: None)
        # stub SoundMixer so initialization works
        monkeypatch.setattr('src.infrastructure.audio.audio_manager.SoundMixer', lambda cfg: Mock())
        # call initialize
        am.initialize()
        # Il mapping passato alla cache usa valori stringa come chiavi (es. "card_move")
        assert captured['mapping'] == {AudioEventType.CARD_MOVE: 'move.wav'}
