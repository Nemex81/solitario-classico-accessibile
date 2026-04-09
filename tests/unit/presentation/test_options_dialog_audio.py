"""Unit tests for OptionsDialog audio integration (v3.5.0).

Tests:
- OptionsDialog accepts audio_manager parameter
- SETTING_CHANGED emitted on widget changes
- SETTING_SAVED emitted on save click
- UI_CANCEL emitted on cancel click
- Graceful fallback if audio_manager is None

Coverage:
- src/infrastructure/ui/options_dialog.py: audio methods

pytest -m "not gui" tests/unit/presentation/test_options_dialog_audio.py -v
"""

import pytest
import wx
from src.domain.services.game_settings import GameSettings


@pytest.fixture(scope="module", autouse=True)
def wx_app():
    """Initialize a wx application once for dialog tests."""
    app = wx.App.Get() or wx.App(False)
    yield app


class DummyAudio:
    """Mock AudioManager for testing."""
    
    def __init__(self):
        self.events = []
        self.volumes = {
            "music": 30,
            "gameplay": 80,
            "ui": 70,
            "ambient": 40,
        }
        self.save_calls = 0
    
    def play_event(self, event):
        """Record audio event for assertion."""
        self.events.append(event)

    def get_bus_volume(self, bus_name):
        return self.volumes[bus_name]

    def set_bus_volume(self, bus_name, volume):
        self.volumes[bus_name] = volume

    def get_music_volume(self):
        return round((self.volumes["music"] + self.volumes["ambient"]) / 2)

    def set_music_volume(self, volume):
        self.volumes["music"] = volume
        self.volumes["ambient"] = volume

    def get_effects_volume(self):
        return round((self.volumes["gameplay"] + self.volumes["ui"]) / 2)

    def set_effects_volume(self, volume):
        self.volumes["gameplay"] = volume
        self.volumes["ui"] = volume

    def save_settings(self):
        self.save_calls += 1


@pytest.mark.unit
class TestOptionsDialogAudio:
    """Test OptionsDialog audio integration."""
    
    def test_options_dialog_accepts_audio_manager(self):
        """OptionsDialog should accept and store audio_manager parameter."""
        from src.infrastructure.ui.options_dialog import OptionsDialog
        from src.application.options_controller import OptionsWindowController
        
        frame = wx.Frame(None, title="Test")
        frame.Show()
        
        settings = GameSettings()
        ctrl = OptionsWindowController(settings)
        ctrl.open_window()  # Initialize state snapshot
        
        audio = DummyAudio()
        
        dlg = OptionsDialog(
            parent=frame,
            controller=ctrl,
            audio_manager=audio
        )
        
        assert dlg.audio_manager is audio
        dlg.Destroy()
        frame.Destroy()
    
    def test_options_dialog_works_without_audio_manager(self):
        """OptionsDialog should work normally if audio_manager is None."""
        from src.infrastructure.ui.options_dialog import OptionsDialog
        from src.application.options_controller import OptionsWindowController
        
        frame = wx.Frame(None, title="Test")
        frame.Show()
        
        settings = GameSettings()
        ctrl = OptionsWindowController(settings)
        ctrl.open_window()
        
        dlg = OptionsDialog(
            parent=frame,
            controller=ctrl,
            audio_manager=None
        )
        
        assert dlg.audio_manager is None
        dlg.Destroy()
        frame.Destroy()
    
    def test_setting_changed_plays_audio(self):
        """Setting change should emit SETTING_CHANGED audio event."""
        from src.infrastructure.ui.options_dialog import OptionsDialog
        from src.application.options_controller import OptionsWindowController
        from src.infrastructure.audio.audio_events import AudioEventType
        
        frame = wx.Frame(None, title="Test")
        frame.Show()
        
        settings = GameSettings()
        ctrl = OptionsWindowController(settings)
        ctrl.open_window()
        
        audio = DummyAudio()
        
        dlg = OptionsDialog(
            parent=frame,
            controller=ctrl,
            audio_manager=audio
        )
        
        # Trigger a setting change (e.g., change deck type)
        change_event = wx.ScrollEvent(wx.wxEVT_SCROLL_CHANGED)
        change_event.SetEventObject(dlg.deck_type_radio)
        dlg.on_setting_changed(change_event)
        
        # Verify audio event was emitted
        assert len(audio.events) > 0, "No audio events recorded"
        assert audio.events[-1].event_type == AudioEventType.SETTING_CHANGED
        
        dlg.Destroy()
        frame.Destroy()

    def test_audio_sliders_load_current_manager_volumes(self):
        """Music/effects sliders should reflect the current runtime audio volumes."""
        from src.infrastructure.ui.options_dialog import OptionsDialog
        from src.application.options_controller import OptionsWindowController

        frame = wx.Frame(None, title="Test")
        frame.Show()

        settings = GameSettings()
        ctrl = OptionsWindowController(settings)
        ctrl.open_window()

        audio = DummyAudio()
        audio.set_music_volume(25)
        audio.set_effects_volume(65)

        dlg = OptionsDialog(parent=frame, controller=ctrl, audio_manager=audio)

        assert dlg.music_volume_slider.GetValue() == 25
        assert dlg.effects_volume_slider.GetValue() == 65

        dlg.Destroy()
        frame.Destroy()

    def test_music_slider_updates_audio_manager(self):
        """Moving the music slider should update the music bus and emit the specific event."""
        from src.infrastructure.ui.options_dialog import OptionsDialog
        from src.application.options_controller import OptionsWindowController
        from src.infrastructure.audio.audio_events import AudioEventType

        frame = wx.Frame(None, title="Test")
        frame.Show()

        settings = GameSettings()
        ctrl = OptionsWindowController(settings)
        ctrl.open_window()

        audio = DummyAudio()
        dlg = OptionsDialog(parent=frame, controller=ctrl, audio_manager=audio)

        dlg.music_volume_slider.SetValue(44)
        change_event = wx.CommandEvent(wx.wxEVT_SLIDER)
        change_event.SetEventObject(dlg.music_volume_slider)
        dlg.on_setting_changed(change_event)

        assert audio.get_bus_volume("music") == 44
        assert audio.get_bus_volume("ambient") == 44
        assert audio.events[-1].event_type == AudioEventType.SETTING_MUSIC_CHANGED

        dlg.Destroy()
        frame.Destroy()

    def test_effects_slider_updates_audio_manager(self):
        """Moving the effects slider should update gameplay and ui buses only."""
        from src.infrastructure.ui.options_dialog import OptionsDialog
        from src.application.options_controller import OptionsWindowController
        from src.infrastructure.audio.audio_events import AudioEventType

        frame = wx.Frame(None, title="Test")
        frame.Show()

        settings = GameSettings()
        ctrl = OptionsWindowController(settings)
        ctrl.open_window()

        audio = DummyAudio()
        dlg = OptionsDialog(parent=frame, controller=ctrl, audio_manager=audio)

        dlg.effects_volume_slider.SetValue(52)
        change_event = wx.CommandEvent(wx.wxEVT_SLIDER)
        change_event.SetEventObject(dlg.effects_volume_slider)
        dlg.on_setting_changed(change_event)

        assert audio.get_bus_volume("gameplay") == 52
        assert audio.get_bus_volume("ui") == 52
        assert audio.get_bus_volume("ambient") == 40
        assert audio.events[-1].event_type == AudioEventType.SETTING_VOLUME_CHANGED

        dlg.Destroy()
        frame.Destroy()

    def test_cancel_restores_audio_volumes(self):
        """Cancel should roll back live audio slider changes to the opening snapshot."""
        from src.infrastructure.ui.options_dialog import OptionsDialog
        from src.application.options_controller import OptionsWindowController

        frame = wx.Frame(None, title="Test")
        frame.Show()

        settings = GameSettings()
        ctrl = OptionsWindowController(settings)
        ctrl.open_window()

        audio = DummyAudio()
        dlg = OptionsDialog(parent=frame, controller=ctrl, audio_manager=audio)

        dlg.music_volume_slider.SetValue(10)
        dlg.effects_volume_slider.SetValue(15)
        dlg._save_audio_from_widgets()

        click_event = wx.CommandEvent(wx.wxEVT_BUTTON)
        click_event.SetEventObject(dlg.btn_cancel)
        dlg.on_cancel_click(click_event)

        assert audio.get_bus_volume("music") == 30
        assert audio.get_bus_volume("ambient") == 40
        assert audio.get_bus_volume("gameplay") == 80
        assert audio.get_bus_volume("ui") == 70

        dlg.Destroy()
        frame.Destroy()

    def test_save_persists_audio_volumes(self):
        """Save should persist the current live slider values through AudioManager."""
        from src.infrastructure.ui.options_dialog import OptionsDialog
        from src.application.options_controller import OptionsWindowController

        frame = wx.Frame(None, title="Test")
        frame.Show()

        settings = GameSettings()
        ctrl = OptionsWindowController(settings)
        ctrl.open_window()

        audio = DummyAudio()
        dlg = OptionsDialog(parent=frame, controller=ctrl, audio_manager=audio)

        dlg.music_volume_slider.SetValue(77)
        dlg.effects_volume_slider.SetValue(54)
        dlg._save_audio_from_widgets()

        click_event = wx.CommandEvent(wx.wxEVT_BUTTON)
        click_event.SetEventObject(dlg.btn_save)
        dlg.on_save_click(click_event)

        assert audio.get_bus_volume("music") == 77
        assert audio.get_bus_volume("ambient") == 77
        assert audio.get_bus_volume("gameplay") == 54
        assert audio.save_calls == 1

    def test_volume_slider_focus_announces_name_and_percentage(self):
        """Focusing a volume slider should announce both control name and value."""
        from src.infrastructure.ui.options_dialog import OptionsDialog
        from src.application.options_controller import OptionsWindowController

        class DummyTts:
            def __init__(self):
                self.messages = []

            def speak(self, text, interrupt=True):
                self.messages.append((text, interrupt))

        class DummyScreenReader:
            def __init__(self):
                self.tts = DummyTts()

        frame = wx.Frame(None, title="Test")
        frame.Show()

        settings = GameSettings()
        ctrl = OptionsWindowController(settings)
        ctrl.open_window()

        audio = DummyAudio()
        sr = DummyScreenReader()
        dlg = OptionsDialog(parent=frame, controller=ctrl, screen_reader=sr, audio_manager=audio)

        focus_event = wx.FocusEvent(wx.wxEVT_SET_FOCUS)
        focus_event.SetEventObject(dlg.music_volume_slider)
        dlg.on_volume_slider_focus(focus_event)

        assert sr.tts.messages[-1] == ("Volume musica, 35 percento", True)

        dlg.Destroy()
        frame.Destroy()

        dlg.Destroy()
        frame.Destroy()
    
    def test_save_click_plays_audio(self):
        """Save button click should emit SETTING_SAVED audio event."""
        from src.infrastructure.ui.options_dialog import OptionsDialog
        from src.application.options_controller import OptionsWindowController
        from src.infrastructure.audio.audio_events import AudioEventType
        
        frame = wx.Frame(None, title="Test")
        frame.Show()
        
        settings = GameSettings()
        ctrl = OptionsWindowController(settings)
        ctrl.open_window()
        
        audio = DummyAudio()
        
        dlg = OptionsDialog(
            parent=frame,
            controller=ctrl,
            audio_manager=audio
        )
        
        # Trigger save click manually
        click_event = wx.CommandEvent(wx.wxEVT_BUTTON)
        click_event.SetEventObject(dlg.btn_save)
        dlg.on_save_click(click_event)
        
        # Verify audio event was emitted
        assert len(audio.events) > 0, "No audio events recorded"
        assert audio.events[-1].event_type == AudioEventType.SETTING_SAVED
        
        dlg.Destroy()
        frame.Destroy()
    
    def test_cancel_click_plays_audio(self):
        """Cancel button click should emit UI_CANCEL audio event."""
        from src.infrastructure.ui.options_dialog import OptionsDialog
        from src.application.options_controller import OptionsWindowController
        from src.infrastructure.audio.audio_events import AudioEventType
        
        frame = wx.Frame(None, title="Test")
        frame.Show()
        
        settings = GameSettings()
        ctrl = OptionsWindowController(settings)
        ctrl.open_window()
        
        audio = DummyAudio()
        
        dlg = OptionsDialog(
            parent=frame,
            controller=ctrl,
            audio_manager=audio
        )
        
        # Trigger cancel click manually
        click_event = wx.CommandEvent(wx.wxEVT_BUTTON)
        click_event.SetEventObject(dlg.btn_cancel)
        dlg.on_cancel_click(click_event)
        
        # Verify audio event was emitted
        assert len(audio.events) > 0, "No audio events recorded"
        assert audio.events[-1].event_type == AudioEventType.UI_CANCEL
        
        dlg.Destroy()
        frame.Destroy()
    
    def test_setting_changed_without_audio_manager_no_crash(self):
        """Setting change without audio_manager should not crash."""
        from src.infrastructure.ui.options_dialog import OptionsDialog
        from src.application.options_controller import OptionsWindowController
        
        frame = wx.Frame(None, title="Test")
        frame.Show()
        
        settings = GameSettings()
        ctrl = OptionsWindowController(settings)
        ctrl.open_window()
        
        dlg = OptionsDialog(
            parent=frame,
            controller=ctrl,
            audio_manager=None
        )
        
        # Trigger setting change - should not raise
        change_event = wx.ScrollEvent(wx.wxEVT_SCROLL_CHANGED)
        change_event.SetEventObject(dlg.deck_type_radio)
        dlg.on_setting_changed(change_event)  # Should not crash
        
        dlg.Destroy()
        frame.Destroy()
    
    def test_save_without_audio_manager_no_crash(self):
        """Save without audio_manager should not crash."""
        from src.infrastructure.ui.options_dialog import OptionsDialog
        from src.application.options_controller import OptionsWindowController
        
        frame = wx.Frame(None, title="Test")
        frame.Show()
        
        settings = GameSettings()
        ctrl = OptionsWindowController(settings)
        ctrl.open_window()
        
        dlg = OptionsDialog(
            parent=frame,
            controller=ctrl,
            audio_manager=None
        )
        
        # Trigger save - should not raise
        click_event = wx.CommandEvent(wx.wxEVT_BUTTON)
        click_event.SetEventObject(dlg.btn_save)
        dlg.on_save_click(click_event)  # Should not crash
        
        dlg.Destroy()
        frame.Destroy()
    
    def test_cancel_without_audio_manager_no_crash(self):
        """Cancel without audio_manager should not crash."""
        from src.infrastructure.ui.options_dialog import OptionsDialog
        from src.application.options_controller import OptionsWindowController
        
        frame = wx.Frame(None, title="Test")
        frame.Show()
        
        settings = GameSettings()
        ctrl = OptionsWindowController(settings)
        ctrl.open_window()
        
        dlg = OptionsDialog(
            parent=frame,
            controller=ctrl,
            audio_manager=None
        )
        
        # Trigger cancel - should not raise
        click_event = wx.CommandEvent(wx.wxEVT_BUTTON)
        click_event.SetEventObject(dlg.btn_cancel)
        dlg.on_cancel_click(click_event)  # Should not crash
        
        dlg.Destroy()
        frame.Destroy()
