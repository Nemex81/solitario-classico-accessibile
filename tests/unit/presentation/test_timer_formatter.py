"""Unit tests for GameFormatter timer announcements."""

import pytest
from src.presentation.game_formatter import GameFormatter


class TestTimerAnnouncements:
    """Test timer-related TTS formatting."""
    
    def test_timer_expired_strict(self):
        """Test timer expiry message for STRICT mode."""
        message = GameFormatter.format_timer_expired(strict_mode=True)
        assert message == "Tempo scaduto!"
    
    def test_timer_expired_permissive(self):
        """Test timer expiry message for PERMISSIVE mode."""
        message = GameFormatter.format_timer_expired(strict_mode=False)
        assert "Tempo scaduto!" in message
        assert "continua" in message
        assert "penalità" in message
    
    def test_overtime_warning_singular(self):
        """Test overtime warning with 1 minute."""
        message = GameFormatter.format_overtime_warning(minutes_over=1)
        assert "1 minuto" in message
        assert "superato il tempo limite" in message
    
    def test_overtime_warning_plural(self):
        """Test overtime warning with multiple minutes."""
        message = GameFormatter.format_overtime_warning(minutes_over=5)
        assert "5 minuti" in message
        assert "superato il tempo limite" in message
