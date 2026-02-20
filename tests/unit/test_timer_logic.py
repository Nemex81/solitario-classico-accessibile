"""Tests for timer expiry detection logic in GameService."""

import pytest
import time
from unittest.mock import Mock

from src.domain.services.game_service import GameService
from src.domain.models.table import GameTable
from src.domain.rules.solitaire_rules import SolitaireRules


class TestTimerExpiryLogic:
    """Test timer expiry detection logic."""
    
    @pytest.fixture
    def game_service(self):
        """Create a GameService instance for testing."""
        table = Mock(spec=GameTable)
        rules = Mock(spec=SolitaireRules)
        return GameService(table, rules)
    
    def test_timer_disabled_never_expires(self, game_service):
        """Test that disabled timer (limit <= 0) never expires."""
        # Set game started 1000 seconds ago
        game_service.start_time = time.time() - 1000
        
        # Check expiry with disabled timer
        expired = game_service.check_timer_expiry(timer_limit=0)
        
        assert expired is False
        assert game_service.timer_expired is False
    
    def test_timer_not_expired_yet(self, game_service):
        """Test that timer doesn't expire before limit is reached."""
        # Set game started 10 seconds ago
        game_service.start_time = time.time() - 10
        
        # Check expiry with 60 second limit (not reached yet)
        expired = game_service.check_timer_expiry(timer_limit=60)
        
        assert expired is False
        assert game_service.timer_expired is False
    
    def test_timer_expires_first_detection(self, game_service):
        """Test that timer expires on first detection when limit is reached."""
        # Set game started 61 seconds ago
        game_service.start_time = time.time() - 61
        
        # Check expiry with 60 second limit (exceeded)
        expired = game_service.check_timer_expiry(timer_limit=60)
        
        assert expired is True
        assert game_service.timer_expired is True
    
    def test_timer_expires_only_once(self, game_service):
        """Test that timer expiry fires only once (single-fire behavior)."""
        # Set game started 61 seconds ago
        game_service.start_time = time.time() - 61
        
        # First check: should fire
        first = game_service.check_timer_expiry(timer_limit=60)
        assert first is True
        
        # Second check: should NOT fire (already expired)
        second = game_service.check_timer_expiry(timer_limit=60)
        assert second is False
        
        # Third check: should still NOT fire
        third = game_service.check_timer_expiry(timer_limit=60)
        assert third is False
