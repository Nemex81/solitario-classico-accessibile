import pytest
from pathlib import Path

dummy_path = Path("assets/sounds")

class DummySound:
    pass

@pytest.fixture(autouse=True)
def patch_pygame(monkeypatch):
    """Replace pygame.mixer.Sound with a dummy constructor."""
    class Mixer:
        @staticmethod
        def Sound(path):
            # return an object with path attribute for assertion
            s = DummySound()
            s.path = path
            return s
    monkeypatch.setattr("src.infrastructure.audio.sound_cache.pygame.mixer", Mixer)

from src.infrastructure.audio.sound_cache import SoundCache


def test_sound_cache_get_returns_sound_or_none(tmp_path, caplog):
    """get() must return Sound or None, never a list.

    When a file is missing, the cache entry should be None and a warning logged.
    """
    caplog.set_level("WARNING")
    cache = SoundCache(tmp_path)

    # create fake pack directory with one file and missing others
    pack = tmp_path / "default" / "gameplay"
    pack.mkdir(parents=True)
    (pack / "card_move.wav").write_bytes(b"")

    cache.load_pack("default")

    sound = cache.get("card_move")
    assert isinstance(sound, DummySound)

    # event that wasn't created should yield None
    missing = cache.get("nonexistent_event")
    assert missing is None

    # verify that no list types present
    for v in cache._cache.values():
        assert not isinstance(v, list)


def test_sound_cache_logs_warning_for_missing(tmp_path, caplog):
    caplog.set_level("WARNING")
    cache = SoundCache(tmp_path)
    cache.load_pack("doesnotexist")
    # should have warning entries for each expected event
    assert "Sound asset missing" in "\n".join(msg.message for msg in caplog.records)
