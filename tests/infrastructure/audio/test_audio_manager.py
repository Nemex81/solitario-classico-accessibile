import pytest
from types import SimpleNamespace

from src.infrastructure.audio.audio_manager import AudioManager
from src.infrastructure.audio.audio_events import AudioEvent


class DummySound:
    pass

class DummyMixer:
    def __init__(self):
        self.played = []
    def play_one_shot(self, sound, bus_name, panning):
        self.played.append((sound, bus_name, panning))
    def pause_loops(self):
        pass
    def resume_loops(self):
        pass


@pytest.fixture(autouse=True)
def patch_dependencies(monkeypatch):
    # patch pygame.mixer with dummy Sound class and init
    class Mixer:
        @staticmethod
        def init(*args, **kwargs):
            pass
        @staticmethod
        def Sound(path):
            s = DummySound()
            s.path = path
            return s
        @staticmethod
        def quit():
            pass
    monkeypatch.setattr("src.infrastructure.audio.audio_manager.pygame.mixer", Mixer)
    # patch SoundCache to avoid file I/O
    class StubCache:
        def __init__(self, *_):
            self._map = {}
        def load_pack(self, pack):
            # populate with a known sound
            s = DummySound()
            s.id = pack
            self._map = {"event1": s}
        def get(self, event_type):
            return self._map.get(event_type)
    monkeypatch.setattr("src.infrastructure.audio.audio_manager.SoundCache", StubCache)
    # patch SoundMixer with dummy
    monkeypatch.setattr("src.infrastructure.audio.audio_manager.SoundMixer", lambda cfg: DummyMixer())


@pytest.fixture

def config():
    return SimpleNamespace(
        mixer_params={"frequency":44100,"size":-16,"channels":2,"buffer":512},
        active_sound_pack="default",
        version="1.0"
    )


def test_play_event_no_random(monkeypatch, config, caplog):
    caplog.set_level("DEBUG")
    am = AudioManager(config)
    assert am.initialize()  # should succeed with stub
    ev = AudioEvent(event_type="event1")
    am.play_event(ev)
    # verify playback occurred with sound from stub cache
    assert hasattr(am.sound_mixer, "played")
    assert len(am.sound_mixer.played) == 1
    sound, bus, pan = am.sound_mixer.played[0]
    assert isinstance(sound, DummySound)
    assert bus == "gameplay"  # default fallback mapping
    assert -1.0 <= pan <= 1.0
    # ensure log contains debug line
    assert "Played event: event1" in "\n".join(r.message for r in caplog.records)


def test_no_random_imported():
    # verify code does not import random in play_event
    import inspect, src.infrastructure.audio.audio_manager as ammod
    src = inspect.getsource(ammod.AudioManager.play_event)
    assert "random" not in src
