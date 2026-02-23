import json
import os
import pytest

from src.infrastructure.config.audio_config_loader import AudioConfigLoader, AudioConfig, CONFIG_PATH


def write_temp_config(tmp_path, data):
    file = tmp_path / "audio_config.json"
    file.write_text(json.dumps(data))
    return str(file)


@pytest.mark.unit
def test_audio_config_loader_valid_json(tmp_path, monkeypatch):
    data = {
        "version": "1.1",
        "enabled_events": {"timer_warning": False},
        "event_sounds": {"CARD_MOVE": "move.wav"},
        "preload_all_event_sounds": False
    }
    path = write_temp_config(tmp_path, data)
    cfg = AudioConfigLoader.load(path)
    assert isinstance(cfg, AudioConfig)
    assert cfg.version == "1.1"
    assert cfg.enabled_events.get("timer_warning") is False
    assert cfg.event_sounds.get("CARD_MOVE") == "move.wav"
    assert cfg.preload_all_event_sounds is False


@pytest.mark.unit
def test_audio_config_loader_missing_file(tmp_path, monkeypatch):
    # point loader at non-existent file, should return default config
    path = str(tmp_path / "nonexistent.json")
    cfg = AudioConfigLoader.load(path)
    assert isinstance(cfg, AudioConfig)
    assert cfg.enabled_events == {}
    assert cfg.event_sounds == {}
    assert cfg.preload_all_event_sounds is True


@pytest.mark.unit
def test_audio_config_loader_corrupted_json(tmp_path):
    # write invalid JSON
    badpath = tmp_path / "bad.json"
    badpath.write_text("{ this is not json }")
    cfg = AudioConfigLoader.load(str(badpath))
    assert isinstance(cfg, AudioConfig)
    # defaults still apply
    assert cfg.enabled_events == {}
    assert cfg.event_sounds == {}
    assert cfg.preload_all_event_sounds is True
