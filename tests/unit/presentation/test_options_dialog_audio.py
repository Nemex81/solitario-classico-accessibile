"""Unit tests for OptionsDialog audio integration (v3.5.1).

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


class DummyAudio:
    """Mock AudioManager for testing."""
    
    def __init__(self):
        self.events = []
    
    def play_event(self, event):
        """Record audio event for assertion."""
        self.events.append(event)


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
