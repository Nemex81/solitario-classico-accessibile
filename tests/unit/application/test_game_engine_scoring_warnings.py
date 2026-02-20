"""Comprehensive tests for scoring warnings integration in GameEngine (v2.6.0).

Tests the graduated TTS threshold warning system that announces penalty
thresholds to users based on their selected warning level.

Test Strategy:
- Uses deterministic fixture with draw_count=1 (predictable thresholds)
- Tag-based detection via SCORING_WARNING_TAG (robust, non-fragile)
- Parametric tests for all 4 warning levels
- Mock TTS for call inspection without audio dependency

Version: v2.6.0
"""

import pytest
from unittest.mock import Mock
from src.application.game_engine import GameEngine
from src.domain.services.game_settings import GameSettings
from src.domain.models.scoring import ScoreWarningLevel
from src.presentation.formatters.score_formatter import ScoreFormatter


@pytest.fixture
def scoring_engine_draw1(mocker):
    """GameEngine fixture with scoring enabled and draw_count=1 forced.
    
    ✅ CORRECTED v2.1: Uses real API GameEngine.create(settings=...)
    Does NOT use non-existent parameters like scoring_enabled= or draw_count=
    
    Provides deterministic setup for threshold warning tests:
    - TTS is mocked for call inspection
    - draw_count=1 ensures predictable threshold crossing
    - Scoring enabled with difficulty level 1
    - Full deck (52 cards) for adequate test range
    
    Usage:
        def test_warnings(scoring_engine_draw1):
            engine = scoring_engine_draw1
            engine.settings.score_warning_level = ScoreWarningLevel.BALANCED
            # ... test logic ...
    
    Version: v2.6.0 (API-corrected v2.1)
    """
    # ✅ v2.1: Create settings with CORRECT API
    settings = GameSettings()
    settings.scoring_enabled = True
    settings.draw_count = 1  # Force determinism: 1 action = 1 card
    settings.deck_type = "french"
    settings.difficulty_level = 1
    settings.score_warning_level = ScoreWarningLevel.BALANCED  # Default
    
    # ✅ v2.1: Create engine with REAL API
    engine = GameEngine.create(
        settings=settings,
        audio_enabled=False  # Will be mocked below
    )
    
    # Mock TTS for call inspection
    mock_tts = mocker.Mock()
    mock_screen_reader = mocker.Mock()
    mock_screen_reader.tts = mock_tts
    engine.screen_reader = mock_screen_reader
    
    # Initialize game state
    engine.new_game()
    
    return engine


class TestStockDrawWarnings:
    """Test graduated warnings for stock draw thresholds."""
    
    @pytest.mark.parametrize("level,expected_warnings", [
        (ScoreWarningLevel.DISABLED, 0),      # No warnings
        (ScoreWarningLevel.MINIMAL, 1),       # Only at 21
        (ScoreWarningLevel.BALANCED, 2),      # At 21 and 41
        (ScoreWarningLevel.COMPLETE, 3),      # At 20, 21, and 41
    ])
    def test_stock_draw_warnings_per_level(self, scoring_engine_draw1, level, expected_warnings):
        """Verify correct number of warnings per level (deterministic, tag-based).
        
        Uses scoring_engine_draw1 fixture with draw_count=1 for predictable
        threshold crossing at exactly cards 20, 21, 41.
        
        Detection via SCORING_WARNING_TAG (robust, non-fragile).
        """
        engine = scoring_engine_draw1
        engine.settings.score_warning_level = level
        
        # Draw exactly 45 times (actions = cards with draw-1)
        # Need to handle stock exhaustion and recycle
        draws_made = 0
        while draws_made < 45:
            stock = engine.table.pile_mazzo
            waste = engine.table.pile_scarti
            
            # Check if we need to recycle
            if stock.is_empty() and not waste.is_empty():
                engine.recycle_waste()
            
            # Draw if possible
            if not stock.is_empty():
                engine.draw_from_stock()
                draws_made += 1
            else:
                # Both empty, can't continue
                break
        
        # ✅ Count warnings by TAG (robust, non-fragile to text changes)
        warning_calls = [
            call for call in engine.screen_reader.tts.speak.call_args_list
            if ScoreFormatter.SCORING_WARNING_TAG in str(call[0][0])
        ]
        
        assert len(warning_calls) == expected_warnings, \
            f"Level {level.name}: expected {expected_warnings} warnings, " \
            f"got {len(warning_calls)}"
    
    def test_draw_warnings_announce_correct_thresholds(self, scoring_engine_draw1):
        """Verify warnings announce at correct draw counts for COMPLETE level."""
        engine = scoring_engine_draw1
        engine.settings.score_warning_level = ScoreWarningLevel.COMPLETE
        
        # Reset mock to clear any initialization calls
        engine.screen_reader.tts.speak.reset_mock()
        
        # Track when warnings occur by draw count
        warning_draws = []
        
        for i in range(45):
            stock = engine.table.pile_mazzo
            waste = engine.table.pile_scarti
            
            # Recycle if needed
            if stock.is_empty() and not waste.is_empty():
                engine.recycle_waste()
            
            # Draw and check current draw count
            engine.draw_from_stock()
            current_draw_count = engine.service.scoring.stock_draw_count
            
            # Check last call for stock draw warning (not recycle warning)
            if engine.screen_reader.tts.speak.call_count > 0:
                last_call = engine.screen_reader.tts.speak.call_args_list[-1]
                msg = str(last_call[0][0])
                if ScoreFormatter.SCORING_WARNING_TAG in msg:
                    # Only count if it's a draw warning, not recycle
                    if "pescata" in msg or "draw" in msg:
                        warning_draws.append(current_draw_count)
        
        # COMPLETE level: warnings at draws 20, 21, 41
        assert 20 in warning_draws, f"Expected warning at 20th draw (pre-warning), got {warning_draws}"
        assert 21 in warning_draws, f"Expected warning at 21st draw (first penalty), got {warning_draws}"
        assert 41 in warning_draws, f"Expected warning at 41st draw (penalty doubles), got {warning_draws}"


class TestRecycleWarnings:
    """Test graduated warnings for recycle thresholds."""
    
    @pytest.mark.parametrize("level,expected_warnings", [
        (ScoreWarningLevel.DISABLED, 0),      # No warnings
        (ScoreWarningLevel.MINIMAL, 1),       # Only at 3rd recycle
        (ScoreWarningLevel.BALANCED, 1),      # Only at 3rd recycle
        (ScoreWarningLevel.COMPLETE, 3),      # At 3rd, 4th, and 5th recycle
    ])
    def test_recycle_warnings_per_level(self, scoring_engine_draw1, level, expected_warnings):
        """Verify correct number of RECYCLE warnings per level during 6 recycles.
        
        Detection via SCORING_WARNING_TAG for robustness.
        Filters out draw warnings to count only recycle-specific warnings.
        """
        engine = scoring_engine_draw1
        engine.settings.score_warning_level = level
        
        # Simulate 6 recycles
        for i in range(6):
            # First, draw all cards from stock to waste
            while not engine.table.pile_mazzo.is_empty():
                engine.draw_from_stock()
            
            # Then recycle
            engine.recycle_waste()
        
        # ✅ Count ONLY recycle warnings by TAG (filter out draw warnings)
        warning_calls = [
            call for call in engine.screen_reader.tts.speak.call_args_list
            if ScoreFormatter.SCORING_WARNING_TAG in str(call[0][0])
            and "riciclo" in str(call[0][0])  # Only recycle warnings
        ]
        
        assert len(warning_calls) == expected_warnings, \
            f"Level {level.name}: expected {expected_warnings} recycle warnings, " \
            f"got {len(warning_calls)}"
    
    def test_recycle_warnings_announce_at_correct_counts(self, scoring_engine_draw1):
        """Verify RECYCLE warnings announce at correct counts for COMPLETE level."""
        engine = scoring_engine_draw1
        engine.settings.score_warning_level = ScoreWarningLevel.COMPLETE
        
        warning_recycles = []
        
        for i in range(6):
            # Draw all cards
            while not engine.table.pile_mazzo.is_empty():
                engine.draw_from_stock()
            
            # Track calls before recycle
            calls_before = len(engine.screen_reader.tts.speak.call_args_list)
            
            # Recycle
            engine.recycle_waste()
            
            # Check if recycle warning was announced
            calls_after = len(engine.screen_reader.tts.speak.call_args_list)
            if calls_after > calls_before:
                # Check last call for warning tag and recycle keyword
                last_call = engine.screen_reader.tts.speak.call_args_list[-1]
                msg = str(last_call[0][0])
                if ScoreFormatter.SCORING_WARNING_TAG in msg and "riciclo" in msg:
                    # Recycle count is i+1
                    warning_recycles.append(i + 1)
        
        # COMPLETE level: warnings at 3rd, 4th, 5th recycle
        assert 3 in warning_recycles, f"Expected warning at 3rd recycle, got {warning_recycles}"
        assert 4 in warning_recycles, f"Expected warning at 4th recycle, got {warning_recycles}"
        assert 5 in warning_recycles, f"Expected warning at 5th recycle, got {warning_recycles}"


class TestWarningsIntegration:
    """Test warnings integration with game settings and scoring system."""
    
    def test_no_warnings_when_scoring_disabled(self, scoring_engine_draw1):
        """Verify no warnings announced when scoring system is disabled."""
        engine = scoring_engine_draw1
        engine.settings.score_warning_level = ScoreWarningLevel.COMPLETE
        engine.settings.scoring_enabled = False  # 👈 Scoring OFF
        
        # Need to restart game for settings to take effect
        engine.new_game()
        
        # Simulate 45 draws (would exceed thresholds if scoring active)
        draws_made = 0
        while draws_made < 45:
            stock = engine.table.pile_mazzo
            waste = engine.table.pile_scarti
            
            if stock.is_empty() and not waste.is_empty():
                engine.recycle_waste()
            
            if not stock.is_empty():
                engine.draw_from_stock()
                draws_made += 1
            else:
                break
        
        # Verify NO warnings
        warning_calls = [
            call for call in engine.screen_reader.tts.speak.call_args_list
            if ScoreFormatter.SCORING_WARNING_TAG in str(call[0][0])
        ]
        
        assert len(warning_calls) == 0, \
            "No warnings should be announced when scoring is disabled"
    
    def test_warnings_respect_level_changes(self, scoring_engine_draw1):
        """Verify warnings respect dynamic level changes during game."""
        engine = scoring_engine_draw1
        
        # Start with DISABLED
        engine.settings.score_warning_level = ScoreWarningLevel.DISABLED
        
        # Draw to threshold 20 (no warnings)
        for _ in range(20):
            engine.draw_from_stock()
        
        warning_calls = [
            call for call in engine.screen_reader.tts.speak.call_args_list
            if ScoreFormatter.SCORING_WARNING_TAG in str(call[0][0])
        ]
        assert len(warning_calls) == 0, "No warnings with DISABLED level"
        
        # Change to COMPLETE (enables pre-warning at 20, but we're past it)
        engine.settings.score_warning_level = ScoreWarningLevel.COMPLETE
        
        # Draw 21st card - should get warning
        engine.draw_from_stock()
        
        warning_calls = [
            call for call in engine.screen_reader.tts.speak.call_args_list
            if ScoreFormatter.SCORING_WARNING_TAG in str(call[0][0])
        ]
        assert len(warning_calls) == 1, "Should get warning at 21st draw"
    
    def test_safe_tts_pattern_no_crash_without_screen_reader(self, scoring_engine_draw1):
        """Verify safe TTS pattern prevents crashes when screen_reader is None."""
        engine = scoring_engine_draw1
        engine.settings.score_warning_level = ScoreWarningLevel.COMPLETE
        
        # Remove screen_reader to simulate unavailable TTS
        engine.screen_reader = None
        
        # Draw to thresholds - should not crash
        try:
            for _ in range(25):
                engine.draw_from_stock()
            success = True
        except Exception as e:
            success = False
            pytest.fail(f"Should not crash without screen_reader: {e}")
        
        assert success, "Engine should handle missing screen_reader gracefully"


class TestCycleScoreWarningLevel:
    """Test cycling through warning levels in GameSettings."""
    
    def test_cycle_score_warning_level(self):
        """Verify cycling through all warning levels."""
        settings = GameSettings()
        
        # Default is BALANCED
        assert settings.score_warning_level == ScoreWarningLevel.BALANCED
        
        # Cycle: BALANCED → COMPLETE
        success, msg = settings.cycle_score_warning_level()
        assert success
        assert settings.score_warning_level == ScoreWarningLevel.COMPLETE
        assert "Completi" in msg
        
        # Cycle: COMPLETE → DISABLED
        success, msg = settings.cycle_score_warning_level()
        assert success
        assert settings.score_warning_level == ScoreWarningLevel.DISABLED
        assert "Disattivati" in msg
        
        # Cycle: DISABLED → MINIMAL
        success, msg = settings.cycle_score_warning_level()
        assert success
        assert settings.score_warning_level == ScoreWarningLevel.MINIMAL
        
        # Cycle: MINIMAL → BALANCED (full loop)
        success, msg = settings.cycle_score_warning_level()
        assert success
        assert settings.score_warning_level == ScoreWarningLevel.BALANCED
    
    def test_get_score_warning_level_display(self):
        """Verify display strings for all levels."""
        settings = GameSettings()
        
        settings.score_warning_level = ScoreWarningLevel.DISABLED
        assert settings.get_score_warning_level_display() == "Disattivati"
        
        settings.score_warning_level = ScoreWarningLevel.MINIMAL
        assert settings.get_score_warning_level_display() == "Minimi"
        
        settings.score_warning_level = ScoreWarningLevel.BALANCED
        assert settings.get_score_warning_level_display() == "Equilibrati"
        
        settings.score_warning_level = ScoreWarningLevel.COMPLETE
        assert settings.get_score_warning_level_display() == "Completi"


class TestScoringWarningTag:
    """Test the SCORING_WARNING_TAG constant for robust test detection."""
    
    def test_tag_constant_exists(self):
        """Verify SCORING_WARNING_TAG constant is defined."""
        assert hasattr(ScoreFormatter, 'SCORING_WARNING_TAG')
        assert ScoreFormatter.SCORING_WARNING_TAG == "[SCORING_WARNING]"
    
    def test_format_threshold_warning_includes_tag(self):
        """Verify format_threshold_warning() includes the tag prefix."""
        # Test stock_draw warning
        warning = ScoreFormatter.format_threshold_warning("stock_draw", 21, 20, -1)
        assert ScoreFormatter.SCORING_WARNING_TAG in warning
        assert warning.startswith(ScoreFormatter.SCORING_WARNING_TAG)
        
        # Test recycle warning
        warning = ScoreFormatter.format_threshold_warning("recycle", 3, 2, -10)
        assert ScoreFormatter.SCORING_WARNING_TAG in warning
        assert warning.startswith(ScoreFormatter.SCORING_WARNING_TAG)
