"""Tests for EndReason enum."""

import pytest
from src.domain.models.game_end import EndReason


class TestEndReason:
    """Test EndReason enum helper methods."""
    
    def test_victory_detection(self):
        """Test is_victory() method for all end reasons."""
        assert EndReason.VICTORY.is_victory() is True
        assert EndReason.VICTORY_OVERTIME.is_victory() is True
        assert EndReason.ABANDON_EXIT.is_victory() is False
        assert EndReason.TIMEOUT_STRICT.is_victory() is False
    
    def test_defeat_detection(self):
        """Test is_defeat() method for all end reasons."""
        assert EndReason.VICTORY.is_defeat() is False
        assert EndReason.ABANDON_EXIT.is_defeat() is True
        assert EndReason.TIMEOUT_STRICT.is_defeat() is True
    
    def test_abandon_detection(self):
        """Test is_abandon() method for all abandon types."""
        assert EndReason.ABANDON_NEW_GAME.is_abandon() is True
        assert EndReason.ABANDON_EXIT.is_abandon() is True
        assert EndReason.ABANDON_APP_CLOSE.is_abandon() is True
        assert EndReason.VICTORY.is_abandon() is False
        assert EndReason.TIMEOUT_STRICT.is_abandon() is False
    
    def test_timeout_detection(self):
        """Test is_timeout() method for timeout-related reasons."""
        assert EndReason.TIMEOUT_STRICT.is_timeout() is True
        assert EndReason.VICTORY_OVERTIME.is_timeout() is True
        assert EndReason.VICTORY.is_timeout() is False
        assert EndReason.ABANDON_EXIT.is_timeout() is False
    
    def test_enum_values(self):
        """Verify enum string values for serialization."""
        assert EndReason.VICTORY.value == "victory"
        assert EndReason.TIMEOUT_STRICT.value == "timeout_strict"
        assert EndReason.VICTORY_OVERTIME.value == "victory_overtime"
        assert EndReason.ABANDON_NEW_GAME.value == "abandon_new_game"
