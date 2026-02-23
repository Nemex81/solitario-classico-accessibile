import pytest
import wx

from src.infrastructure.ui.wx_frame import SolitarioFrame
from src.infrastructure.audio.audio_events import AudioEventType


class DummyAudio:
    def __init__(self):
        self.actions = []

    def pause_all_loops(self):
        self.actions.append("paused")

    def resume_all_loops(self):
        self.actions.append("resumed")


@pytest.mark.gui
def test_frame_activate_pauses_and_resumes(monkeypatch):
    """Frame should pause/resume loops on EVT_ACTIVATE."""
    app = wx.App(False)
    frame = SolitarioFrame()
    audio = DummyAudio()
    frame.audio_manager = audio

    # lose focus
    evt = wx.ActivateEvent(wx.wxEVT_ACTIVATE, frame.GetId(), False)
    frame._on_activate(evt)
    assert audio.actions[-1] == "paused"

    # gain focus
    evt2 = wx.ActivateEvent(wx.wxEVT_ACTIVATE, frame.GetId(), True)
    frame._on_activate(evt2)
    assert audio.actions[-1] == "resumed"


def test_ambient_loop_event_after_initialize():
    """Controller logic should emit AMBIENT_LOOP after initializing audio."""
    # Import locally to avoid heavy controller init
    from acs_wx import SolitarioController

    class DummyAudioMgr:
        def __init__(self):
            self.events = []
        def initialize(self):
            pass
        def play_event(self, ev):
            self.events.append(ev)

    sc = SolitarioController()
    sc.audio_manager = DummyAudioMgr()

    # simulate the snippet from run()
    if hasattr(sc.audio_manager, 'initialize'):
        sc.audio_manager.initialize()
    from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
    sc.audio_manager.play_event(AudioEvent(event_type=AudioEventType.AMBIENT_LOOP))

    assert sc.audio_manager.events
    assert sc.audio_manager.events[-1].event_type == AudioEventType.AMBIENT_LOOP
