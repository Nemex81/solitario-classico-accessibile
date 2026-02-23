import pygame
import pytest

from src.application.input_handler import InputHandler, GameCommand
from src.infrastructure.audio.audio_events import AudioEventType


class DummyAudio:
    def __init__(self):
        self.events = []
    def play_event(self, event):
        self.events.append(event)


@pytest.fixture(autouse=True)
def init_pygame():
    pygame.init()
    yield
    pygame.quit()


def make_key_event(key, shift=False, ctrl=False):
    mods = 0
    if shift:
        mods |= pygame.KMOD_SHIFT
    if ctrl:
        mods |= pygame.KMOD_CTRL
    ev = pygame.event.Event(pygame.KEYDOWN, key=key)
    pygame.key.set_mods(mods)
    return ev


def test_navigation_generates_ui_navigate():
    audio = DummyAudio()
    handler = InputHandler(audio_manager=audio)
    ev = make_key_event(pygame.K_UP)
    cmd = handler.handle_event(ev)
    assert cmd == GameCommand.MOVE_UP
    assert audio.events, "AudioEvent not emitted"
    assert audio.events[-1].event_type == AudioEventType.UI_NAVIGATE


def test_select_and_cancel_generate_ui():
    audio = DummyAudio()
    handler = InputHandler(audio_manager=audio)
    cmd = handler.handle_event(make_key_event(pygame.K_RETURN))
    assert cmd == GameCommand.SELECT_CARD
    assert audio.events[-1].event_type == AudioEventType.UI_SELECT

    cmd = handler.handle_event(make_key_event(pygame.K_DELETE))
    assert cmd == GameCommand.CANCEL_SELECTION
    assert audio.events[-1].event_type == AudioEventType.UI_CANCEL


def test_no_audio_manager_no_errors():
    handler = InputHandler()
    ev = make_key_event(pygame.K_LEFT)
    assert handler.handle_event(ev) == GameCommand.MOVE_LEFT
    # should not raise even though audio manager is None
