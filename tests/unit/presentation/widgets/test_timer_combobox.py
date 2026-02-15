"""Unit tests for TimerComboBox widget.

Tests the custom wx.ComboBox widget for timer duration selection with preset values.

Version: v2.4.0
Test Framework: pytest + wxPython
Coverage Target: 95%+

Test Categories:
1. Initialization tests (constructor, default values)
2. Get/Set methods tests (get_selected_minutes, set_minutes)
3. Edge cases (invalid values, boundary conditions)
4. Preset management (get_presets, get_preset_count)
5. Rounding logic (_round_to_nearest_preset)
"""

import pytest
import wx
from src.presentation.widgets.timer_combobox import TimerComboBox


class TestTimerComboBoxInitialization:
    """Test TimerComboBox initialization and construction."""
    
    @pytest.fixture
    def app(self):
        """Create wx.App for testing."""
        app = wx.App()
        yield app
        app.Destroy()
    
    @pytest.fixture
    def parent(self, app):
        """Create parent frame for widget testing."""
        frame = wx.Frame(None)
        yield frame
        frame.Destroy()
    
    def test_initialization_default(self, parent):
        """Test TimerComboBox initializes with default values."""
        combo = TimerComboBox(parent)
        
        # Should default to "0 minuti - Timer disattivato"
        assert combo.GetValue() == "0 minuti - Timer disattivato"
        assert combo.get_selected_minutes() == 0
        assert combo.GetSelection() == 0
    
    def test_initialization_with_value(self, parent):
        """Test TimerComboBox initializes with specified value."""
        combo = TimerComboBox(parent, value="15 minuti")
        
        assert combo.GetValue() == "15 minuti"
        assert combo.get_selected_minutes() == 15
    
    def test_has_13_preset_options(self, parent):
        """Test TimerComboBox has exactly 13 preset options."""
        combo = TimerComboBox(parent)
        
        assert combo.GetCount() == 13
        assert combo.get_preset_count() == 13
    
    def test_preset_values_correct(self, parent):
        """Test preset values are [0, 5, 10, 15, ..., 60]."""
        combo = TimerComboBox(parent)
        presets = combo.get_presets()
        
        expected = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]
        assert presets == expected
    
    def test_first_choice_is_disabled_option(self, parent):
        """Test first ComboBox choice is '0 minuti - Timer disattivato'."""
        combo = TimerComboBox(parent)
        
        assert combo.GetString(0) == "0 minuti - Timer disattivato"
    
    def test_readonly_style(self, parent):
        """Test ComboBox is read-only (prevents manual input)."""
        combo = TimerComboBox(parent)
        
        # Check that CB_READONLY style is set
        assert combo.GetWindowStyle() & wx.CB_READONLY


class TestTimerComboBoxGetSetMethods:
    """Test get_selected_minutes() and set_minutes() methods."""
    
    @pytest.fixture
    def app(self):
        """Create wx.App for testing."""
        app = wx.App()
        yield app
        app.Destroy()
    
    @pytest.fixture
    def parent(self, app):
        """Create parent frame for widget testing."""
        frame = wx.Frame(None)
        yield frame
        frame.Destroy()
    
    @pytest.fixture
    def combo(self, parent):
        """Create TimerComboBox instance for testing."""
        return TimerComboBox(parent)
    
    def test_get_selected_minutes_zero(self, combo):
        """Test get_selected_minutes() returns 0 for disabled option."""
        combo.SetValue("0 minuti - Timer disattivato")
        assert combo.get_selected_minutes() == 0
    
    def test_get_selected_minutes_various_values(self, combo):
        """Test get_selected_minutes() for various preset values."""
        test_values = [5, 10, 15, 30, 45, 60]
        
        for minutes in test_values:
            combo.SetValue(f"{minutes} minuti")
            assert combo.get_selected_minutes() == minutes
    
    def test_set_minutes_zero(self, combo):
        """Test set_minutes(0) selects disabled option."""
        combo.set_minutes(0)
        
        assert combo.GetValue() == "0 minuti - Timer disattivato"
        assert combo.get_selected_minutes() == 0
    
    def test_set_minutes_various_presets(self, combo):
        """Test set_minutes() for various preset values."""
        test_values = [5, 10, 20, 30, 45, 60]
        
        for minutes in test_values:
            combo.set_minutes(minutes)
            assert combo.get_selected_minutes() == minutes
            assert combo.GetValue() == f"{minutes} minuti"
    
    def test_set_minutes_rounds_to_nearest(self, combo):
        """Test set_minutes() rounds non-preset values to nearest preset."""
        # Test cases: (input, expected_output)
        test_cases = [
            (7, 5),    # 7 rounds to 5
            (13, 15),  # 13 rounds to 15
            (17, 15),  # 17 rounds to 15
            (23, 25),  # 23 rounds to 25
            (27, 25),  # 27 rounds to 25
            (33, 35),  # 33 rounds to 35
            (57, 55),  # 57 rounds to 55
        ]
        
        for input_minutes, expected_minutes in test_cases:
            combo.set_minutes(input_minutes)
            assert combo.get_selected_minutes() == expected_minutes


class TestTimerComboBoxEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @pytest.fixture
    def app(self):
        """Create wx.App for testing."""
        app = wx.App()
        yield app
        app.Destroy()
    
    @pytest.fixture
    def parent(self, app):
        """Create parent frame for widget testing."""
        frame = wx.Frame(None)
        yield frame
        frame.Destroy()
    
    @pytest.fixture
    def combo(self, parent):
        """Create TimerComboBox instance for testing."""
        return TimerComboBox(parent)
    
    def test_set_minutes_negative_rounds_to_zero(self, combo):
        """Test set_minutes() with negative value rounds to 0."""
        combo.set_minutes(-10)
        assert combo.get_selected_minutes() == 0
    
    def test_set_minutes_above_max_rounds_to_max(self, combo):
        """Test set_minutes() with value > 60 rounds to 60."""
        combo.set_minutes(100)
        assert combo.get_selected_minutes() == 60
    
    def test_set_minutes_exactly_max(self, combo):
        """Test set_minutes(60) works correctly."""
        combo.set_minutes(60)
        assert combo.get_selected_minutes() == 60
        assert combo.GetValue() == "60 minuti"
    
    def test_get_selected_minutes_with_invalid_value(self, combo):
        """Test get_selected_minutes() returns 0 for invalid format."""
        # Manually set an invalid value (should not happen in practice due to CB_READONLY)
        # but test fallback behavior
        combo.SetValue("invalid format")
        assert combo.get_selected_minutes() == 0
    
    def test_round_to_nearest_boundary_2_5(self, combo):
        """Test rounding at 2.5 boundary (should round to 0 or 5)."""
        combo.set_minutes(2)  # < 2.5, should round to 0
        assert combo.get_selected_minutes() == 0
        
        combo.set_minutes(3)  # > 2.5, should round to 5
        assert combo.get_selected_minutes() == 5


class TestTimerComboBoxPresetManagement:
    """Test preset-related methods."""
    
    @pytest.fixture
    def app(self):
        """Create wx.App for testing."""
        app = wx.App()
        yield app
        app.Destroy()
    
    @pytest.fixture
    def parent(self, app):
        """Create parent frame for widget testing."""
        frame = wx.Frame(None)
        yield frame
        frame.Destroy()
    
    @pytest.fixture
    def combo(self, parent):
        """Create TimerComboBox instance for testing."""
        return TimerComboBox(parent)
    
    def test_get_presets_returns_copy(self, combo):
        """Test get_presets() returns a copy, not reference."""
        presets1 = combo.get_presets()
        presets2 = combo.get_presets()
        
        # Should be equal but not same object
        assert presets1 == presets2
        assert presets1 is not presets2
        
        # Modifying copy should not affect widget
        presets1.append(999)
        assert 999 not in combo.get_presets()
    
    def test_get_preset_count(self, combo):
        """Test get_preset_count() returns correct count."""
        assert combo.get_preset_count() == 13
    
    def test_all_presets_selectable(self, combo):
        """Test all preset values are selectable via ComboBox."""
        presets = combo.get_presets()
        
        for minutes in presets:
            combo.set_minutes(minutes)
            assert combo.get_selected_minutes() == minutes


class TestTimerComboBoxIntegration:
    """Integration tests for complete workflows."""
    
    @pytest.fixture
    def app(self):
        """Create wx.App for testing."""
        app = wx.App()
        yield app
        app.Destroy()
    
    @pytest.fixture
    def parent(self, app):
        """Create parent frame for widget testing."""
        frame = wx.Frame(None)
        yield frame
        frame.Destroy()
    
    @pytest.fixture
    def combo(self, parent):
        """Create TimerComboBox instance for testing."""
        return TimerComboBox(parent)
    
    def test_workflow_enable_disable_timer(self, combo):
        """Test workflow: set timer to 30 min, then disable."""
        # Enable timer with 30 minutes
        combo.set_minutes(30)
        assert combo.get_selected_minutes() == 30
        
        # Disable timer
        combo.set_minutes(0)
        assert combo.get_selected_minutes() == 0
        assert combo.GetValue() == "0 minuti - Timer disattivato"
    
    def test_workflow_cycle_through_all_presets(self, combo):
        """Test workflow: cycle through all preset values."""
        presets = combo.get_presets()
        
        for i, minutes in enumerate(presets):
            combo.SetSelection(i)
            assert combo.get_selected_minutes() == minutes
    
    def test_workflow_load_from_settings(self, combo):
        """Test workflow: load timer value from game settings (seconds -> minutes)."""
        # Simulate loading from GameSettings.max_time_game (seconds)
        test_cases = [
            (0, 0),       # 0 seconds -> 0 minutes (disabled)
            (300, 5),     # 300 seconds -> 5 minutes
            (900, 15),    # 900 seconds -> 15 minutes
            (1800, 30),   # 1800 seconds -> 30 minutes
            (3600, 60),   # 3600 seconds -> 60 minutes
        ]
        
        for seconds, expected_minutes in test_cases:
            minutes = seconds // 60
            combo.set_minutes(minutes)
            assert combo.get_selected_minutes() == expected_minutes
    
    def test_workflow_save_to_settings(self, combo):
        """Test workflow: save timer value to game settings (minutes -> seconds)."""
        # Simulate saving to GameSettings.max_time_game
        combo.set_minutes(20)
        
        # Convert to seconds (as GameSettings expects)
        minutes = combo.get_selected_minutes()
        seconds = minutes * 60
        
        assert seconds == 1200  # 20 minutes * 60 = 1200 seconds
