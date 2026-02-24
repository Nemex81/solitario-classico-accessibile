import pytest

from src.application.main_menu_controller import MainMenuController
from src.infrastructure.audio.audio_events import AudioEventType


class DummyAudio:
    def __init__(self):
        self.events = []

    def play_event(self, ev):
        self.events.append(ev)


@pytest.mark.unit
class TestMainMenuControllerAudio:
    def test_open_emits_mixer_opened(self):
        audio = DummyAudio()
        ctrl = MainMenuController(audio_manager=audio)
        assert audio.events and audio.events[0].event_type == AudioEventType.UI_MENU_OPEN

    def test_navigation_and_boundaries(self):
        audio = DummyAudio()
        ctrl = MainMenuController(audio_manager=audio)
        # at top, up should play boundary hit
        ctrl.navigate_up()
        assert audio.events[-1].event_type == AudioEventType.UI_BOUNDARY_HIT
        # move down one step
        ctrl.navigate_down()
        assert audio.events[-1].event_type == AudioEventType.UI_NAVIGATE
        # move to bottom and try down boundary
        ctrl.cursor = len(ctrl.items) - 1
        ctrl.navigate_down()
        assert audio.events[-1].event_type == AudioEventType.UI_BOUNDARY_HIT

    def test_select_and_cancel(self):
        audio = DummyAudio()
        ctrl = MainMenuController(audio_manager=audio)
        ctrl.cursor = 2
        sel = ctrl.select()
        assert sel == ctrl.items[2]
        assert audio.events[-1].event_type == AudioEventType.UI_BUTTON_CLICK
        ctrl.cancel()
        assert audio.events[-1].event_type == AudioEventType.UI_CANCEL
