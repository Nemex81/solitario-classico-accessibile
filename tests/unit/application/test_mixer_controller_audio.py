import pytest

from src.application.mixer_controller import MixerController
from src.infrastructure.audio.audio_events import AudioEventType


class DummyAudio:
    def __init__(self):
        self.events = []

    def play_event(self, ev):
        self.events.append(ev)


class DummySR:
    def __init__(self):
        class TTS:
            def __init__(self):
                self.spoken = []

            def speak(self, text, interrupt=True):
                self.spoken.append(text)

        self.tts = TTS()


@pytest.mark.unit
class TestMixerControllerAudio:
    def test_open_sounds_and_tts(self):
        audio = DummyAudio()
        sr = DummySR()
        ctrl = MixerController(audio_manager=audio, screen_reader=sr)
        assert audio.events and audio.events[0].event_type == AudioEventType.MIXER_OPENED
        assert "Mixer opened" in sr.tts.spoken

    def test_navigation_with_tts_and_boundary(self):
        audio = DummyAudio()
        sr = DummySR()
        ctrl = MixerController(audio_manager=audio, screen_reader=sr)
        # at top, going up should play boundary hit
        ctrl.navigate_up()
        assert audio.events[-1].event_type == AudioEventType.UI_BOUNDARY_HIT
        # move down one step
        ctrl.navigate_down()
        assert audio.events[-1].event_type == AudioEventType.UI_NAVIGATE
        assert sr.tts.spoken[-1] == ctrl._order[1]
        # go to bottom and try again
        ctrl.cursor = len(ctrl._order) - 1
        ctrl.navigate_down()
        assert audio.events[-1].event_type == AudioEventType.UI_BOUNDARY_HIT

    def test_increase_decrease_changes_value_and_tts(self):
        audio = DummyAudio()
        sr = DummySR()
        ctrl = MixerController(audio_manager=audio, screen_reader=sr)
        initial = ctrl.channels[ctrl._order[0]]
        new = ctrl.increase()
        assert new == initial + 10
        assert audio.events[-1].event_type == AudioEventType.SETTING_VOLUME_CHANGED
        assert any(str(new) in spoken for spoken in sr.tts.spoken)
        # decrease back
        new2 = ctrl.decrease()
        assert new2 == initial
        assert audio.events[-1].event_type == AudioEventType.SETTING_VOLUME_CHANGED
        assert any(str(new2) in spoken for spoken in sr.tts.spoken)
        # try to decrease below 0 boundary
        ctrl.channels[ctrl._order[0]] = 0
        ctrl.decrease()
        assert audio.events[-1].event_type == AudioEventType.UI_BOUNDARY_HIT
