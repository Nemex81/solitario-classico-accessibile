"""Unit tests for MenuPanel audio integration (v3.5.1).

Tests:
- MenuPanel audio_manager parameter acceptance
- UI_BUTTON_HOVER on button focus
- UI_BUTTON_CLICK on 6 button clicks
- No crash if audio_manager is None (graceful fallback)

Coverage:
- src/infrastructure/ui/menu_panel.py: audio methods

pytest -m "not gui" tests/unit/presentation/test_menu_panel_audio.py -v
"""

import pytest
import wx


class DummyAudio:
    """Mock AudioManager for testing."""
    
    def __init__(self):
        self.events = []
    
    def play_event(self, event):
        """Record audio event for assertion."""
        self.events.append(event)


class DummyController:
    """Mock Controller with all MenuPanel methods."""
    
    def __init__(self):
        self.calls = []
    
    def start_gameplay(self):
        self.calls.append('start_gameplay')
    
    def show_last_game_summary(self):
        self.calls.append('show_last_game_summary')
    
    def show_leaderboard(self):
        self.calls.append('show_leaderboard')
    
    def show_profile_menu(self):
        self.calls.append('show_profile_menu')
    
    def show_options(self):
        self.calls.append('show_options')
    
    def show_exit_dialog(self):
        self.calls.append('show_exit_dialog')


@pytest.mark.unit
class TestMenuPanelAudio:
    """Test MenuPanel audio integration."""
    
    def test_menu_panel_accepts_audio_manager(self):
        """MenuPanel should accept and store audio_manager parameter."""
        from src.infrastructure.ui.menu_panel import MenuPanel
        
        # Create dummy objects
        frame = wx.Frame(None, title="Test")
        frame.Show()
        container = wx.Panel(frame)
        
        audio = DummyAudio()
        ctrl = DummyController()
        
        # Create MenuPanel with audio_manager
        panel = MenuPanel(
            parent=container,
            controller=ctrl,
            audio_manager=audio
        )
        
        assert panel.audio_manager is audio
        frame.Destroy()
    
    def test_menu_panel_works_without_audio_manager(self):
        """MenuPanel should work normally if audio_manager is None."""
        from src.infrastructure.ui.menu_panel import MenuPanel
        
        frame = wx.Frame(None, title="Test")
        frame.Show()
        container = wx.Panel(frame)
        
        ctrl = DummyController()
        
        # Create without audio_manager
        panel = MenuPanel(
            parent=container,
            controller=ctrl
        )
        
        assert panel.audio_manager is None
        frame.Destroy()
    
    def test_button_focus_plays_ui_button_hover(self):
        """Button focus should emit UI_BUTTON_HOVER audio event."""
        from src.infrastructure.ui.menu_panel import MenuPanel
        from src.infrastructure.audio.audio_events import AudioEventType
        
        frame = wx.Frame(None, title="Test")
        frame.Show()
        container = wx.Panel(frame)
        
        audio = DummyAudio()
        ctrl = DummyController()
        
        panel = MenuPanel(
            parent=container,
            controller=ctrl,
            audio_manager=audio
        )
        
        # Get first button (Play button)
        buttons = [child for child in panel.GetChildren() 
                   if isinstance(child, wx.Button)]
        assert len(buttons) > 0, "No buttons found"
        
        play_button = buttons[0]
        
        # Trigger focus event manually
        focus_event = wx.FocusEvent(wx.wxEVT_SET_FOCUS)
        focus_event.SetEventObject(play_button)
        panel.on_button_focus(focus_event)
        
        # Verify audio event was emitted
        assert len(audio.events) > 0, "No audio events recorded"
        assert audio.events[-1].event_type == AudioEventType.UI_BUTTON_HOVER
        
        frame.Destroy()
    
    def test_play_button_click_plays_ui_button_click(self):
        """Play button click should emit UI_BUTTON_CLICK audio event."""
        from src.infrastructure.ui.menu_panel import MenuPanel
        from src.infrastructure.audio.audio_events import AudioEventType
        
        frame = wx.Frame(None, title="Test")
        frame.Show()
        container = wx.Panel(frame)
        
        audio = DummyAudio()
        ctrl = DummyController()
        
        panel = MenuPanel(
            parent=container,
            controller=ctrl,
            audio_manager=audio
        )
        
        # Get first button (Play button)
        buttons = [child for child in panel.GetChildren() 
                   if isinstance(child, wx.Button)]
        play_button = buttons[0]
        
        # Trigger click event manually
        click_event = wx.CommandEvent(wx.wxEVT_BUTTON)
        click_event.SetEventObject(play_button)
        panel.on_play_click(click_event)
        
        # Verify audio event was emitted
        assert len(audio.events) > 0, "No audio events recorded"
        assert audio.events[-1].event_type == AudioEventType.UI_BUTTON_CLICK
        
        # Verify controller was called
        assert 'start_gameplay' in ctrl.calls
        
        frame.Destroy()
    
    def test_all_button_clicks_emit_ui_button_click(self):
        """All 6 button clicks should emit UI_BUTTON_CLICK."""
        from src.infrastructure.ui.menu_panel import MenuPanel
        from src.infrastructure.audio.audio_events import AudioEventType
        
        frame = wx.Frame(None, title="Test")
        frame.Show()
        container = wx.Panel(frame)
        
        audio = DummyAudio()
        ctrl = DummyController()
        
        panel = MenuPanel(
            parent=container,
            controller=ctrl,
            audio_manager=audio
        )
        
        click_methods = [
            (panel.on_play_click, 'start_gameplay'),
            (panel.on_last_game_click, 'show_last_game_summary'),
            (panel.on_leaderboard_click, 'show_leaderboard'),
            (panel.on_profile_menu_click, 'show_profile_menu'),
            (panel.on_options_click, 'show_options'),
            (panel.on_exit_click, 'show_exit_dialog'),
        ]
        
        click_event = wx.CommandEvent(wx.wxEVT_BUTTON)
        
        for click_method, controller_call in click_methods:
            audio.events.clear()
            ctrl.calls.clear()
            
            # Trigger click
            click_method(click_event)
            
            # Verify audio event
            assert len(audio.events) > 0, f"No audio event for {click_method.__name__}"
            assert audio.events[-1].event_type == AudioEventType.UI_BUTTON_CLICK
            
            # Verify controller call
            assert controller_call in ctrl.calls
        
        frame.Destroy()
    
    def test_focus_without_audio_manager_no_crash(self):
        """Button focus without audio_manager should not crash."""
        from src.infrastructure.ui.menu_panel import MenuPanel
        
        frame = wx.Frame(None, title="Test")
        frame.Show()
        container = wx.Panel(frame)
        
        ctrl = DummyController()
        
        panel = MenuPanel(
            parent=container,
            controller=ctrl,
            audio_manager=None  # Explicitly None
        )
        
        # Get first button
        buttons = [child for child in panel.GetChildren() 
                   if isinstance(child, wx.Button)]
        play_button = buttons[0]
        
        # Trigger focus event - should not raise
        focus_event = wx.FocusEvent(wx.wxEVT_SET_FOCUS)
        focus_event.SetEventObject(play_button)
        panel.on_button_focus(focus_event)  # Should not crash
        
        frame.Destroy()
    
    def test_click_without_audio_manager_no_crash(self):
        """Button click without audio_manager should not crash."""
        from src.infrastructure.ui.menu_panel import MenuPanel
        
        frame = wx.Frame(None, title="Test")
        frame.Show()
        container = wx.Panel(frame)
        
        ctrl = DummyController()
        
        panel = MenuPanel(
            parent=container,
            controller=ctrl,
            audio_manager=None
        )
        
        # Trigger click event - should not raise
        click_event = wx.CommandEvent(wx.wxEVT_BUTTON)
        panel.on_play_click(click_event)  # Should not crash
        
        assert 'start_gameplay' in ctrl.calls
        
        frame.Destroy()
