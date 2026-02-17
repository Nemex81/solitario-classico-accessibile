"""Unit tests for StatsFormatter utility methods."""

import pytest
from src.presentation.formatters.stats_formatter import StatsFormatter
from src.domain.models.game_end import EndReason


class TestTimeFormatting:
    """Test time formatting methods."""
    
    def test_format_duration_seconds_only(self):
        """Test formatting durations under 1 minute."""
        assert StatsFormatter.format_duration(42) == "42 secondi"
        assert StatsFormatter.format_duration(15) == "15 secondi"
        assert StatsFormatter.format_duration(1) == "1 secondi"
    
    def test_format_duration_minutes_only(self):
        """Test formatting durations in minutes without seconds."""
        assert StatsFormatter.format_duration(60) == "1 minuto"
        assert StatsFormatter.format_duration(120) == "2 minuti"
        assert StatsFormatter.format_duration(300) == "5 minuti"
    
    def test_format_duration_minutes_and_seconds(self):
        """Test formatting durations with minutes and seconds."""
        result = StatsFormatter.format_duration(90)
        assert "1 minuto e 30 secondi" in result
        
        result = StatsFormatter.format_duration(323)
        assert "5 minuti e 23 secondi" in result
    
    def test_format_duration_hours(self):
        """Test formatting durations with hours."""
        result = StatsFormatter.format_duration(3665)  # 1h 1m 5s
        assert "1 ora" in result
        assert "1 minuto" in result
        assert "5 secondi" in result
        
        result = StatsFormatter.format_duration(7200)  # 2h exactly
        assert "2 ore" in result
    
    def test_format_time_mm_ss_short(self):
        """Test MM:SS formatting for times under 1 minute."""
        assert StatsFormatter.format_time_mm_ss(42) == "0:42"
        assert StatsFormatter.format_time_mm_ss(5) == "0:05"
    
    def test_format_time_mm_ss_long(self):
        """Test MM:SS formatting for times over 1 minute."""
        assert StatsFormatter.format_time_mm_ss(325) == "5:25"
        assert StatsFormatter.format_time_mm_ss(601) == "10:01"


class TestNumberFormatting:
    """Test number formatting methods."""
    
    def test_format_number_no_thousands(self):
        """Test formatting numbers without thousands separator."""
        assert StatsFormatter.format_number(450) == "450"
        assert StatsFormatter.format_number(99) == "99"
    
    def test_format_number_with_thousands(self):
        """Test formatting numbers with thousands separator."""
        assert StatsFormatter.format_number(1250) == "1.250"
        assert StatsFormatter.format_number(10500) == "10.500"
        assert StatsFormatter.format_number(1000000) == "1.000.000"
    
    def test_format_percentage_default(self):
        """Test percentage formatting with default 1 decimal."""
        assert StatsFormatter.format_percentage(0.6742) == "67,4%"
        assert StatsFormatter.format_percentage(0.5) == "50,0%"
        assert StatsFormatter.format_percentage(1.0) == "100,0%"
    
    def test_format_percentage_custom_decimals(self):
        """Test percentage formatting with custom decimal places."""
        assert StatsFormatter.format_percentage(0.6742, decimals=2) == "67,42%"
        assert StatsFormatter.format_percentage(0.333, decimals=0) == "33%"


class TestEndReasonFormatting:
    """Test EndReason formatting."""
    
    def test_format_victory(self):
        """Test formatting victory reasons."""
        assert StatsFormatter.format_end_reason(EndReason.VICTORY) == "Vittoria"
        assert "oltre tempo" in StatsFormatter.format_end_reason(EndReason.VICTORY_OVERTIME)
    
    def test_format_abandons(self):
        """Test formatting abandon reasons."""
        assert "Abbandono" in StatsFormatter.format_end_reason(EndReason.ABANDON_EXIT)
        assert "nuova partita" in StatsFormatter.format_end_reason(EndReason.ABANDON_NEW_GAME)
        assert "Chiusura app" in StatsFormatter.format_end_reason(EndReason.ABANDON_APP_CLOSE)
    
    def test_format_timeout(self):
        """Test formatting timeout reason."""
        assert "Tempo scaduto" in StatsFormatter.format_end_reason(EndReason.TIMEOUT_STRICT)
