"""Tests for timer state attributes in GameService."""

import pytest
import time
from unittest.mock import Mock

from src.domain.services.game_service import GameService
from src.domain.models.table import GameTable
from src.domain.rules.solitaire_rules import SolitaireRules


class TestTimerState:
    """Test timer state attributes in GameService."""
    
    @pytest.fixture
    def game_service(self):
        """Create a GameService instance for testing."""
        table = Mock(spec=GameTable)
        rules = Mock(spec=SolitaireRules)
        return GameService(table, rules)
    
    def test_initial_state(self, game_service):
        """Test that timer state is initialized correctly."""
        assert game_service.timer_expired is False
        assert game_service.overtime_start is None
    
    def test_reset_clears_timer_state(self, game_service):
        """Test that reset_game() clears timer state."""
        # Set timer state
        game_service.timer_expired = True
        game_service.overtime_start = time.time()
        
        # Reset game
        game_service.reset_game()
        
        # Verify timer state is cleared
        assert game_service.timer_expired is False
        assert game_service.overtime_start is None
    
    def test_overtime_duration_no_overtime(self, game_service):
        """Test get_overtime_duration() when no overtime is active."""
        assert game_service.get_overtime_duration() == 0.0
    
    def test_overtime_duration_active(self, game_service):
        """Test get_overtime_duration() when overtime is active."""
        # Set overtime start time to 10 seconds ago
        game_service.overtime_start = time.time() - 10.0
        
        # Get duration
        duration = game_service.get_overtime_duration()
        
        # Allow 0.5s tolerance for test execution time
        assert 9.5 <= duration <= 10.5
