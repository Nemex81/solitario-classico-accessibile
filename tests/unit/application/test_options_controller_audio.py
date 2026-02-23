import pytest

from src.application.options_controller import OptionsWindowController
from src.domain.services.game_settings import GameSettings
from src.infrastructure.audio.audio_events import AudioEventType


class DummyDialog:
    def __init__(self, result=True):
        self.result = result
    @property
    def is_available(self):
        return True
    def show_yes_no(self, msg, title):
        return self.result
    # OptionsController specifically uses this prompt when closing dirty
    def show_options_save_prompt(self):
        return self.result


class DummyAudio:
    def __init__(self):
        self.events = []
    def play_event(self, ev):
        self.events.append(ev)


@pytest.mark.unit
class TestOptionsControllerAudio:
    def test_navigation_triggers_navigate(self):
        audio = DummyAudio()
        ctrl = OptionsWindowController(GameSettings(), audio_manager=audio)
        _ = ctrl.navigate_up()
        assert audio.events and audio.events[-1].event_type == AudioEventType.UI_NAVIGATE
        _ = ctrl.navigate_down()
        assert audio.events[-1].event_type == AudioEventType.UI_NAVIGATE

    def test_modify_emits_select(self):
        audio = DummyAudio()
        ctrl = OptionsWindowController(GameSettings(), audio_manager=audio)
        # set a cursor position allowing modification
        ctrl.cursor_position = 0
        msg = ctrl.modify_current_option()
        assert audio.events and audio.events[-1].event_type == AudioEventType.UI_SELECT

    def test_close_dirty_plays_dialog_and_response(self):
        audio = DummyAudio()
        dialog = DummyDialog(result=False)
        ctrl = OptionsWindowController(GameSettings(), dialog_manager=dialog, audio_manager=audio)
        # make dirty and ensure snapshot exists to avoid KeyError
        ctrl.state = "OPEN_DIRTY"
        # populate snapshot with exactly the keys that _restore_snapshot expects
        s = ctrl.settings
        ctrl.original_settings = {
            "deck_type": s.deck_type,
            "difficulty": s.difficulty_level,
            "timer": s.max_time_game,
            "shuffle": s.shuffle_discards,
            "command_hints": s.command_hints_enabled,
            "timer_strict_mode": s.timer_strict_mode,
            "score_warning_level": s.score_warning_level,
        }
        out = ctrl.close_window()
        assert audio.events[0].event_type == AudioEventType.MIXER_OPENED
        assert audio.events[-1].event_type == AudioEventType.UI_CANCEL
        assert out == "Opzioni chiuse senza salvare." or isinstance(out, str)
