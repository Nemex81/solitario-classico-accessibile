"""Unit tests for countdown timer display v1.5.1.

Tests the new timer info behavior with countdown display:
- Timer OFF: Shows elapsed time
- Timer ON: Shows countdown (remaining time)
- Timer expired: Shows "Tempo scaduto!"
"""

import pytest
from unittest.mock import Mock
import time

from src.domain.services.game_service import GameService
from src.domain.models.table import GameTable
from src.domain.models.deck import FrenchDeck
from src.domain.rules.solitaire_rules import SolitaireRules


@pytest.fixture
def game_table():
    """Create a game table for testing."""
    deck = FrenchDeck()
    deck.crea()
    return GameTable(deck)


@pytest.fixture
def game_service(game_table):
    """Create game service with started timer."""
    deck = FrenchDeck()
    rules = SolitaireRules(deck)
    service = GameService(game_table, rules)
    service.start_time = time.time()  # Start timer
    return service


def test_get_timer_info_elapsed_when_no_max_time(game_service):
    """Test elapsed time display when max_time is None."""
    # Set elapsed time to 323 seconds (5:23)
    game_service.start_time = time.time() - 323
    
    message, hint = game_service.get_timer_info(max_time=None)
    
    assert "Tempo trascorso" in message
    assert "5 minuti" in message
    assert "23 secondi" in message
    assert hint is None  # No hint during gameplay


def test_get_timer_info_elapsed_when_max_time_zero(game_service):
    """Test elapsed time display when max_time is explicitly 0."""
    # Set elapsed time to 120 seconds (2:00)
    game_service.start_time = time.time() - 120
    
    message, hint = game_service.get_timer_info(max_time=0)
    
    assert "Tempo trascorso" in message
    assert "2 minuti" in message
    assert "0 secondi" in message
    assert hint is None


def test_get_timer_info_countdown_when_timer_active(game_service):
    """Test countdown display when timer is active."""
    # max_time = 600 seconds (10 minutes)
    # elapsed = 323 seconds
    # remaining = 277 seconds (4:37)
    game_service.start_time = time.time() - 323
    
    message, hint = game_service.get_timer_info(max_time=600)
    
    assert "Tempo rimanente" in message
    assert "4 minuti" in message
    assert "37 secondi" in message
    assert hint is None


def test_get_timer_info_countdown_exact_seconds(game_service):
    """Test countdown with exact minute values."""
    # max_time = 300 (5:00)
    # elapsed = 180 (3:00)
    # remaining = 120 (2:00)
    game_service.start_time = time.time() - 180
    
    message, hint = game_service.get_timer_info(max_time=300)
    
    assert "Tempo rimanente" in message
    assert "2 minuti" in message
    assert "0 secondi" in message
    assert hint is None


def test_get_timer_info_countdown_zero_remaining(game_service):
    """Test 'Tempo scaduto!' when timer reaches zero."""
    # max_time = 300 (5 minutes)
    # elapsed = 300 (exactly at limit)
    # remaining = 0
    game_service.start_time = time.time() - 300
    
    message, hint = game_service.get_timer_info(max_time=300)
    
    assert message == "Tempo scaduto!"
    assert hint is None


def test_get_timer_info_countdown_prevents_negative(game_service):
    """Test that countdown prevents negative values."""
    # max_time = 300
    # elapsed = 500 (beyond limit)
    # remaining should be 0, NOT -200!
    game_service.start_time = time.time() - 500
    
    message, hint = game_service.get_timer_info(max_time=300)
    
    # Should show "Tempo scaduto!" not negative time
    assert message == "Tempo scaduto!"
    assert hint is None
    
    # Verify max(0, ...) works correctly
    elapsed = int(game_service.get_elapsed_time())
    remaining = max(0, 300 - elapsed)
    assert remaining == 0  # Not negative!


def test_get_timer_info_countdown_one_second_remaining(game_service):
    """Test countdown with just one second remaining."""
    # max_time = 300
    # elapsed = 299
    # remaining = 1
    game_service.start_time = time.time() - 299
    
    message, hint = game_service.get_timer_info(max_time=300)
    
    assert "Tempo rimanente" in message
    assert "0 minuti" in message
    assert "1 secondi" in message
    assert hint is None


def test_hint_always_none_during_gameplay(game_service):
    """Test that hint is always None during gameplay (no more options hint)."""
    # Test with timer OFF
    game_service.start_time = time.time() - 120
    message1, hint1 = game_service.get_timer_info(max_time=None)
    assert hint1 is None
    
    # Test with timer ON
    message2, hint2 = game_service.get_timer_info(max_time=600)
    assert hint2 is None
    
    # Test with timer expired
    game_service.start_time = time.time() - 400
    message3, hint3 = game_service.get_timer_info(max_time=300)
    assert hint3 is None


def test_backward_compatible_no_parameter(game_service):
    """Test backward compatibility when called without parameter."""
    # Old code: get_timer_info() without parameters
    # Should default to max_time=None and show elapsed time
    game_service.start_time = time.time() - 180
    
    message, hint = game_service.get_timer_info()  # No parameter
    
    # Should show elapsed time (backward compatible)
    assert "Tempo trascorso" in message
    assert "3 minuti" in message
    assert hint is None
