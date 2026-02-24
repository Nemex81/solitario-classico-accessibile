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
def test_audio_config_loader_full_mapping(tmp_path):
    """Loader should accept a comprehensive config with all new keys."""
    data = {
        "version": "2.0",
        "enabled_events": {"ui_navigate": False, "card_flip": True, "welcome_message": True},
        "event_sounds": {
            "CARD_MOVE": "gameplay/card_move.wav",
            "CARD_FLIP": "gameplay/card_flip.wav",
            "UI_MENU_OPEN": "ui/menu_open.wav",
            "WELCOME_MESSAGE": "voice/welcome_english.wav"
        },
        "preload_all_event_sounds": False
    }
    path = write_temp_config(tmp_path, data)
    cfg = AudioConfigLoader.load(path)

    # basics
    assert cfg.version == "2.0"
    assert cfg.preload_all_event_sounds is False

    # check that no keys are dropped
    assert cfg.event_sounds["CARD_MOVE"] == "gameplay/card_move.wav"
    assert cfg.event_sounds["CARD_FLIP"] == "gameplay/card_flip.wav"
    assert cfg.event_sounds["UI_MENU_OPEN"] == "ui/menu_open.wav"
    assert cfg.event_sounds["WELCOME_MESSAGE"] == "voice/welcome_english.wav"

    assert cfg.enabled_events.get("ui_navigate") is False
    assert cfg.enabled_events.get("card_flip") is True
    assert cfg.enabled_events.get("welcome_message") is True


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
