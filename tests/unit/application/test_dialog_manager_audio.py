import pytest

from src.application.dialog_manager import SolitarioDialogManager
from src.infrastructure.audio.audio_events import AudioEventType


class DummyAudio:
    def __init__(self):
        self.events = []
    def play_event(self, event):
        self.events.append(event)


class DummyDialog:
    def __init__(self):
        self.called = 0
    def show_yes_no(self, msg, title):
        self.called += 1
        return True


@pytest.fixture

def dummy_audio():
    return DummyAudio()


def test_show_abandon_triggers_audio(dummy_audio):
    dm = SolitarioDialogManager(dialog_provider=DummyDialog(), audio_manager=dummy_audio)
    result = dm.show_abandon_game_prompt()
    assert result is True
    assert dummy_audio.events, "No audio event emitted"
    assert dummy_audio.events[0].event_type == AudioEventType.UI_SELECT


def test_show_new_game_triggers_audio(dummy_audio):
    dm = SolitarioDialogManager(dialog_provider=DummyDialog(), audio_manager=dummy_audio)
    assert dm.show_new_game_prompt() is True
    assert dummy_audio.events[-1].event_type == AudioEventType.UI_SELECT
