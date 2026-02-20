"""Unit tests for timer cycling improvements v1.5.1.

Tests the new timer cycling behavior with ENTER key:
- OFF → 5 → 10 → 15 → ... → 60 → 5 (wrap-around)
"""

import pytest
from unittest.mock import Mock

from src.domain.services.game_settings import GameSettings, GameState
from src.application.options_controller import OptionsWindowController

pytestmark = pytest.mark.gui


@pytest.fixture
def game_state_no_game():
    """GameState with no active game."""
    state = GameState()
    state.is_running = False
    return state


@pytest.fixture
def game_state_with_game():
    """GameState with active game (should block timer modification)."""
    state = GameState()
    state.is_running = True
    return state


@pytest.fixture
def settings_timer_off(game_state_no_game):
    """GameSettings with timer OFF."""
    settings = GameSettings(game_state=game_state_no_game)
    settings.max_time_game = 0
    return settings


@pytest.fixture
def settings_timer_5min(game_state_no_game):
    """GameSettings with timer at 5 minutes."""
    settings = GameSettings(game_state=game_state_no_game)
    settings.max_time_game = 300  # 5 minutes
    return settings


@pytest.fixture
def settings_timer_60min(game_state_no_game):
    """GameSettings with timer at 60 minutes (maximum)."""
    settings = GameSettings(game_state=game_state_no_game)
    settings.max_time_game = 3600  # 60 minutes
    return settings


@pytest.fixture
def controller(settings_timer_off):
    """OptionsWindowController with timer OFF."""
    controller = OptionsWindowController(settings=settings_timer_off)
    controller.open()
    controller.cursor_position = 2  # Timer option
    return controller


def test_invio_timer_off_to_5min(settings_timer_off):
    """Test ENTER on timer OFF activates at 5 minutes."""
    controller = OptionsWindowController(settings=settings_timer_off)
    controller.open_window()  # Use open_window() instead of open()
    controller.cursor_position = 2  # Timer option
    
    result = controller.modify_current_option()
    
    assert settings_timer_off.max_time_game == 300  # 5 minutes in seconds
    assert "5 minuti" in result
    assert controller.state == "OPEN_DIRTY"


def test_invio_timer_5_to_10min(settings_timer_5min):
    """Test ENTER on 5min increments to 10min."""
    controller = OptionsWindowController(settings=settings_timer_5min)
    controller.open_window()
    controller.cursor_position = 2
    
    result = controller.modify_current_option()
    
    assert settings_timer_5min.max_time_game == 600  # 10 minutes
    assert "10 minuti" in result


def test_invio_timer_55_to_60min():
    """Test ENTER on 55min increments to 60min."""
    game_state = GameState()
    game_state.is_running = False
    settings = GameSettings(game_state=game_state)
    settings.max_time_game = 3300  # 55 minutes
    
    controller = OptionsWindowController(settings=settings)
    controller.open_window()
    controller.cursor_position = 2
    
    result = controller.modify_current_option()
    
    assert settings.max_time_game == 3600  # 60 minutes
    assert "60 minuti" in result


def test_invio_timer_60_wraps_to_5min(settings_timer_60min):
    """Test ENTER on 60min wraps around to 5min (critical test)."""
    controller = OptionsWindowController(settings=settings_timer_60min)
    controller.open_window()
    controller.cursor_position = 2
    
    result = controller.modify_current_option()
    
    # This is the wrap-around behavior!
    assert settings_timer_60min.max_time_game == 300  # Back to 5 minutes
    assert "5 minuti" in result


def test_invio_multiple_cycles():
    """Test multiple ENTER presses cycle through all values."""
    game_state = GameState()
    game_state.is_running = False
    settings = GameSettings(game_state=game_state)
    settings.max_time_game = 0  # Start OFF
    
    controller = OptionsWindowController(settings=settings)
    controller.open_window()
    controller.cursor_position = 2
    
    # Cycle through: 0 → 5 → 10 → ... → 60 → 5
    expected_values = [300, 600, 900, 1200, 1500, 1800, 2100, 2400, 2700, 3000, 3300, 3600, 300]
    
    for i, expected in enumerate(expected_values):
        controller.modify_current_option()
        assert settings.max_time_game == expected, f"Cycle {i+1}: expected {expected}, got {settings.max_time_game}"
    
    # Verify we've completed a full cycle (13 steps: OFF to 60, then wrap to 5)
    assert settings.max_time_game == 300  # Back to 5


def test_invio_marks_dirty(settings_timer_off):
    """Test ENTER marks options as dirty."""
    controller = OptionsWindowController(settings=settings_timer_off)
    controller.open_window()
    controller.cursor_position = 2
    
    assert controller.state == "OPEN_CLEAN"
    
    controller.modify_current_option()
    
    assert controller.state == "OPEN_DIRTY"


def test_invio_blocked_during_game(game_state_with_game):
    """Test ENTER is blocked when game is running."""
    settings = GameSettings(game_state=game_state_with_game)
    settings.max_time_game = 300
    
    controller = OptionsWindowController(settings=settings)
    controller.open_window()
    controller.cursor_position = 2
    
    result = controller.modify_current_option()
    
    # Should be blocked
    assert settings.max_time_game == 300  # Unchanged
    assert "Non puoi modificare" in result or "durante una partita" in result


def test_plus_minus_still_work(settings_timer_5min):
    """Test +/- keys still work for fine control (regression test)."""
    controller = OptionsWindowController(settings=settings_timer_5min)
    controller.open_window()
    controller.cursor_position = 2
    
    # Test + increment
    result = controller.increment_timer()
    assert settings_timer_5min.max_time_game == 600  # 10 minutes
    
    # Test - decrement
    result = controller.decrement_timer()
    assert settings_timer_5min.max_time_game == 300  # Back to 5 minutes


def test_t_toggle_still_works(settings_timer_off):
    """Test T key still toggles ON/OFF (regression test)."""
    controller = OptionsWindowController(settings=settings_timer_off)
    controller.open_window()
    controller.cursor_position = 2
    
    # Toggle ON
    result = controller.toggle_timer()
    assert settings_timer_off.max_time_game == 300  # Activates at 5min
    
    # Toggle OFF
    result = controller.toggle_timer()
    assert settings_timer_off.max_time_game == -1  # OFF
