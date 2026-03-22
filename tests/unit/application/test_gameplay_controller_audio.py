import pytest

from src.application.gameplay_controller import GamePlayController
from src.application.game_engine import GameEngine
from src.domain.services.game_settings import GameSettings


class DummyAudio:
    def __init__(self):
        self.events = []
    def play_event(self, event):
        self.events.append(event)


class DummySR:
    def __init__(self):
        class TTS:
            def speak(self, text, interrupt=True):
                pass
        self.tts = TTS()

def make_controller(tmp_path, audio=None):
    engine = GameEngine.create(
        audio_enabled=False,  # audio manager provided separately
        tts_engine="mock",
        verbose=0,
        settings=GameSettings(),
        use_native_dialogs=False,
        parent_window=None,
        profile_service=None,
    )
    # provide a dummy screen reader so _speak_with_hint doesn't fail
    ctrl = GamePlayController(
        engine=engine,
        screen_reader=DummySR(),
        settings=GameSettings(),
        audio_manager=audio,
    )
    return ctrl


@pytest.mark.unit
class TestGamePlayControllerAudio:
    def test_nav_pile_base_emits_ui_navigate(self):
        audio = DummyAudio()
        ctrl = make_controller(None, audio=audio)
        ctrl._nav_pile_base(0)  # should trigger UI_NAVIGATE
        assert audio.events, "no audio emitted"
        assert audio.events[-1].event_type == "ui_navigate"
        # destination_pile should be 0 because cursor starts at 0
        assert audio.events[-1].destination_pile == 0

    def test_cursor_moves_trigger_audio(self):
        audio = DummyAudio()
        ctrl = make_controller(None, audio=audio)
        # move down/up and check navigate events
        ctrl._cursor_down()
        assert audio.events[-1].event_type == "ui_navigate"
        ctrl._cursor_up()
        assert audio.events[-1].event_type == "ui_navigate"

    def test_card_select_emits_card_select(self):
        audio = DummyAudio()
        ctrl = make_controller(None, audio=audio)
        # ensure there's a card to select by drawing first
        ctrl.engine.draw_from_stock()
        ctrl._select_card()
        assert any(ev.event_type == "card_select" for ev in audio.events), audio.events

    def test_move_cards_panning(self):
        audio = DummyAudio()
        ctrl = make_controller(None, audio=audio)
        # simulate a selection move; set some selection/pile state
        # easiest: draw then move to simulate card_move
        ctrl.engine.draw_from_stock()
        # Because mapping uses engine.selection.origin_pile, manually set
        pile = ctrl.engine.service.table.pile_base[0]
        ctrl.engine.selection.origin_pile = pile
        # pretend a selection exists so move_cards reads origin_pile
        ctrl.engine.selection.has_selection = lambda: True
        # move cursor to a different pile to make a valid move
        ctrl._cursor_right()
        # monkeypatch engine to force success
        ctrl.engine.execute_move = lambda : (True, "Moved")
        ctrl._move_cards()
        # look for the card_move event (now emitted as tableau_drop or multi_card_move)
        card_events = [ev for ev in audio.events if ev.event_type in ("tableau_drop", "multi_card_move", "foundation_drop")]
        assert card_events, audio.events
        ev = card_events[-1]
        assert ev.source_pile is not None
        assert ev.destination_pile is not None

    def test_on_game_won_plays_audio(self):
        audio = DummyAudio()
        ctrl = make_controller(None, audio=audio)
        ctrl._on_game_won()
        assert audio.events and audio.events[-1].event_type == "game_won"
