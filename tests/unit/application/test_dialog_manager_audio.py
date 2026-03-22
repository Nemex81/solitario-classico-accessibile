import pytest

from src.application.dialog_manager import SolitarioDialogManager
from src.infrastructure.audio.audio_events import AudioEventType


class DummyAudio:
    def __init__(self):
        self.events = []
    def play_event(self, event):
        self.events.append(event)


class DummyDialog:
    def __init__(self, result=True):
        self.called = 0
        self.result = result
        self.async_callback = None
    @property
    def is_available(self):
        return True
    def show_yes_no(self, msg, title):
        self.called += 1
        return self.result
    def show_yes_no_async(self, title, message, callback):
        # immediately call callback with preset result
        callback(self.result)


@pytest.fixture

def dummy_audio():
    return DummyAudio()


def test_show_abandon_triggers_audio(dummy_audio):
    dm = SolitarioDialogManager(dialog_provider=DummyDialog(), audio_manager=dummy_audio)
    result = dm.show_abandon_game_prompt()
    assert result is True
    # open event should be first (UI_ERROR = dialog di conferma/avviso)
    assert dummy_audio.events[0].event_type == AudioEventType.UI_ERROR
    assert dummy_audio.events[-1].event_type == AudioEventType.UI_CONFIRM


def test_show_new_game_triggers_audio(dummy_audio):
    dm = SolitarioDialogManager(dialog_provider=DummyDialog(), audio_manager=dummy_audio)
    result = dm.show_new_game_prompt()
    assert result is True
    assert dummy_audio.events[0].event_type == AudioEventType.UI_ERROR
    assert dummy_audio.events[-1].event_type == AudioEventType.UI_CONFIRM


def test_async_abandon_wraps_audio(dummy_audio):
    dm = SolitarioDialogManager(dialog_provider=DummyDialog(), audio_manager=dummy_audio)
    called = []
    def cb(res):
        called.append(res)
    # DummyDialog.show_yes_no_async calls the callback immediately, so
    # invoking the method will both open the dialog and trigger the
    # wrapped callback once.
    dm.show_abandon_game_prompt_async(cb)
    # open event should have been played (UI_ERROR = dialog di conferma/avviso)
    assert dummy_audio.events and dummy_audio.events[0].event_type == AudioEventType.UI_ERROR
    # callback should have been invoked exactly once by DummyDialog
    assert called == [True]
    # the audio close event should also have been emitted
    assert dummy_audio.events[-1].event_type == AudioEventType.UI_CONFIRM

