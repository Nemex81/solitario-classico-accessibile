"""Integration tests for GameEngine + ProfileService integration.

Tests the complete flow from GameEngine.end_game() to ProfileService.record_session():
- Victory creates SessionOutcome with all fields populated
- Abandon/timeout scenarios record correctly
- Timer field mapping (STRICT, PERMISSIVE, OFF)
- EndReason correctness for all scenarios
- Stats aggregation after game end
"""

import pytest
from pathlib import Path
from datetime import datetime

from src.domain.services.profile_service import ProfileService
from src.infrastructure.storage.profile_storage import ProfileStorage
from src.domain.models.game_end import EndReason
from src.domain.services.game_settings import GameSettings
from src.domain.models.deck import FrenchDeck
from src.domain.models.table import GameTable


# ================================================================
# FIXTURES
# ================================================================

@pytest.fixture
def temp_profile_dir(tmp_path):
    """Create temporary profile storage directory."""
    profile_dir = tmp_path / ".solitario"
    profile_dir.mkdir(parents=True, exist_ok=True)
    return profile_dir


@pytest.fixture
def profile_storage(temp_profile_dir):
    """Create ProfileStorage with temp directory."""
    return ProfileStorage(data_dir=temp_profile_dir)


@pytest.fixture
def profile_service(profile_storage):
    """Create ProfileService with temp storage."""
    service = ProfileService(storage=profile_storage)
    # Create and load a test profile
    profile = service.create_profile("TestPlayer")
    service.load_profile(profile.profile_id)
    return service


@pytest.fixture
def game_table():
    """Create a basic game table for testing."""
    deck = FrenchDeck()
    return GameTable(deck)


def create_mock_game_engine(profile_service, settings=None):
    """Create a mock GameEngine-like object for testing.
    
    Since GameEngine requires pygame which may not be available,
    we create a minimal mock that has the necessary attributes
    for testing ProfileService integration.
    """
    from types import SimpleNamespace
    
    # Create settings if not provided
    if settings is None:
        settings = GameSettings()
    
    # Create minimal GameService mock
    game_service = SimpleNamespace(
        move_count=50,
        draw_count=10,
        recycle_count=2,
        elapsed_time=120.0,
        overtime_start=None,  # No overtime by default
        scoring=None
    )
    
    # Create minimal GameEngine mock
    engine = SimpleNamespace(
        profile_service=profile_service,
        settings=settings,
        service=game_service,
        table=None,  # Will be set if needed
        score_storage=None,
        last_session_outcome=None
    )
    
    return engine


def simulate_end_game(engine, end_reason: EndReason, is_victory: bool):
    """Simulate end_game flow without full GameEngine.
    
    This mimics the key steps in GameEngine.end_game() that create
    and record a SessionOutcome.
    """
    from src.domain.models.profile import SessionOutcome
    
    # Get stats from service
    elapsed_time = engine.service.elapsed_time
    move_count = engine.service.move_count
    
    # Create session outcome (mimicking GameEngine.end_game lines 1280-1294)
    session_outcome = SessionOutcome.create_new(
        profile_id=engine.profile_service.active_profile.profile_id,
        end_reason=end_reason,
        is_victory=is_victory,
        elapsed_time=elapsed_time,
        timer_enabled=(engine.settings.max_time_game > 0),
        timer_limit=engine.settings.max_time_game,
        timer_mode=("STRICT" if engine.settings.timer_strict_mode else "PERMISSIVE") if (engine.settings.max_time_game > 0) else "OFF",
        timer_expired=(end_reason == EndReason.TIMEOUT_STRICT),
        scoring_enabled=engine.settings.scoring_enabled,
        final_score=1000 if is_victory else 0,  # Simplified for testing
        difficulty_level=engine.settings.difficulty_level,
        deck_type=engine.settings.deck_type,
        move_count=move_count
    )
    
    # Record session (mimicking GameEngine.end_game line 1300)
    engine.profile_service.record_session(session_outcome)
    engine.last_session_outcome = session_outcome
    
    return session_outcome


# ================================================================
# TESTS: Session Recording Scenarios
# ================================================================

class TestVictorySessionRecording:
    """Test victory scenario creates complete SessionOutcome."""
    
    def test_victory_records_session_with_correct_fields(self, profile_service):
        """Verify victory creates SessionOutcome with all fields populated."""
        # Setup: Create mock engine with default settings
        settings = GameSettings()
        settings.max_time_game = -1  # Timer OFF
        settings.scoring_enabled = True
        settings.difficulty_level = 3
        engine = create_mock_game_engine(profile_service, settings)
        
        # Action: Simulate game end with victory
        session = simulate_end_game(engine, EndReason.VICTORY, is_victory=True)
        
        # Assert: SessionOutcome created with all fields
        assert session is not None
        assert session.end_reason == EndReason.VICTORY
        assert session.is_victory is True
        assert session.elapsed_time == 120.0
        assert session.move_count == 50
        assert session.final_score > 0
        
        # Assert: SessionOutcome saved to profile
        assert len(profile_service.recent_sessions) == 1
        assert profile_service.recent_sessions[0].session_id == session.session_id
        
        # Assert: Global stats updated
        assert profile_service.global_stats.total_victories == 1
        assert profile_service.global_stats.total_games == 1
        assert profile_service.global_stats.winrate == 1.0


class TestAbandonSessionRecording:
    """Test abandon scenario records session correctly."""
    
    def test_abandon_exit_records_session(self, profile_service):
        """Test ESC abandon creates ABANDON_EXIT session."""
        # Setup: Create mock engine
        settings = GameSettings()
        settings.max_time_game = -1
        engine = create_mock_game_engine(profile_service, settings)
        
        # Action: Simulate abandon via ESC
        session = simulate_end_game(engine, EndReason.ABANDON_EXIT, is_victory=False)
        
        # Assert: Session recorded with ABANDON_EXIT
        assert session.end_reason == EndReason.ABANDON_EXIT
        assert session.is_victory is False
        
        # Assert: Stats updated (defeats++)
        # Access stats from profile_service
        assert profile_service.global_stats.total_games == 1
        assert profile_service.global_stats.total_victories == 0
        assert profile_service.global_stats.total_defeats == 1


class TestTimeoutSessionRecording:
    """Test timeout scenarios (STRICT and PERMISSIVE)."""
    
    def test_timeout_strict_records_session(self, profile_service):
        """Test STRICT timer timeout creates TIMEOUT_STRICT session."""
        # Setup: Create mock engine with STRICT timer
        settings = GameSettings()
        settings.max_time_game = 60  # 60 seconds
        settings.timer_strict_mode = True
        engine = create_mock_game_engine(profile_service, settings)
        
        # Action: Simulate timeout (game forced to end)
        session = simulate_end_game(engine, EndReason.TIMEOUT_STRICT, is_victory=False)
        
        # Assert: Session has correct timeout fields
        assert session.end_reason == EndReason.TIMEOUT_STRICT
        assert session.is_victory is False
        assert session.timer_expired is True
        assert session.timer_mode == "STRICT"
        assert session.timer_enabled is True
        assert session.timer_limit == 60


class TestOvertimeVictoryRecording:
    """Test PERMISSIVE overtime victory scenario."""
    
    def test_overtime_victory_records_session(self, profile_service):
        """Test PERMISSIVE overtime creates VICTORY_OVERTIME."""
        # Setup: Create mock engine with PERMISSIVE timer
        settings = GameSettings()
        settings.max_time_game = 60  # 60 seconds
        settings.timer_strict_mode = False  # PERMISSIVE mode
        engine = create_mock_game_engine(profile_service, settings)
        
        # Simulate overtime: elapsed time > timer limit
        engine.service.elapsed_time = 90.0  # 30 seconds overtime
        engine.service.overtime_start = 60.0  # Overtime started at 60s
        
        # Action: Win after timer expired (PERMISSIVE allows this)
        # Note: In real GameEngine, VICTORY would be converted to VICTORY_OVERTIME
        # if overtime is active (line 1218-1219). We simulate that here.
        session = simulate_end_game(engine, EndReason.VICTORY_OVERTIME, is_victory=True)
        
        # Assert: Victory with overtime tracking
        assert session.end_reason == EndReason.VICTORY_OVERTIME
        assert session.is_victory is True  # Still a victory!
        assert session.timer_mode == "PERMISSIVE"
        assert session.elapsed_time == 90.0
        
        # Assert: Stats count this as victory
        # Access stats from profile_service
        assert profile_service.global_stats.total_victories == 1
        assert profile_service.timer_stats.victories_overtime == 1


# ================================================================
# TESTS: Timer Field Mapping
# ================================================================

class TestTimerFieldMapping:
    """Test GameSettings → SessionOutcome timer field mapping."""
    
    def test_timer_fields_mapped_strict_mode(self, profile_service):
        """Verify timer_mode='STRICT' when timer_strict_mode=True."""
        # Setup: STRICT timer mode
        settings = GameSettings()
        settings.max_time_game = 300
        settings.timer_strict_mode = True
        engine = create_mock_game_engine(profile_service, settings)
        
        # Action: End game (any outcome)
        session = simulate_end_game(engine, EndReason.ABANDON_EXIT, is_victory=False)
        
        # Assert: Timer fields mapped correctly
        assert session.timer_enabled is True
        assert session.timer_limit == 300
        assert session.timer_mode == "STRICT"
    
    def test_timer_fields_mapped_permissive_mode(self, profile_service):
        """Verify timer_mode='PERMISSIVE' when timer_strict_mode=False."""
        # Setup: PERMISSIVE timer mode
        settings = GameSettings()
        settings.max_time_game = 600
        settings.timer_strict_mode = False
        engine = create_mock_game_engine(profile_service, settings)
        
        # Action: End game
        session = simulate_end_game(engine, EndReason.VICTORY, is_victory=True)
        
        # Assert: Timer fields mapped correctly
        assert session.timer_enabled is True
        assert session.timer_limit == 600
        assert session.timer_mode == "PERMISSIVE"
    
    def test_timer_fields_mapped_off_mode(self, profile_service):
        """Verify timer_enabled=False when max_time_game=-1."""
        # Setup: Timer OFF
        settings = GameSettings()
        settings.max_time_game = -1
        engine = create_mock_game_engine(profile_service, settings)
        
        # Action: End game
        session = simulate_end_game(engine, EndReason.VICTORY, is_victory=True)
        
        # Assert: Timer disabled
        assert session.timer_enabled is False
        assert session.timer_limit == -1
        assert session.timer_mode == "OFF"


# ================================================================
# TESTS: Multiple Sessions and Stats Aggregation
# ================================================================

class TestMultipleSessionsAggregation:
    """Test stats aggregate correctly across multiple sessions."""
    
    def test_multiple_victories_accumulate(self, profile_service):
        """Test multiple victories update stats correctly."""
        # Setup
        settings = GameSettings()
        engine = create_mock_game_engine(profile_service, settings)
        
        # Action: Play 3 victories
        for i in range(3):
            engine.service.elapsed_time = 100.0 + (i * 10)  # Vary time
            simulate_end_game(engine, EndReason.VICTORY, is_victory=True)
        
        # Assert: All victories recorded
        # Access stats from profile_service
        assert len(profile_service.recent_sessions) == 3
        assert profile_service.global_stats.total_games == 3
        assert profile_service.global_stats.total_victories == 3
        assert profile_service.global_stats.winrate == 1.0
    
    def test_mixed_outcomes_update_stats(self, profile_service):
        """Test mix of victories and defeats updates stats correctly."""
        # Setup
        settings = GameSettings()
        engine = create_mock_game_engine(profile_service, settings)
        
        # Action: Play 2 victories, 1 abandon
        simulate_end_game(engine, EndReason.VICTORY, is_victory=True)
        simulate_end_game(engine, EndReason.ABANDON_EXIT, is_victory=False)
        simulate_end_game(engine, EndReason.VICTORY, is_victory=True)
        
        # Assert: Stats reflect mixed outcomes
        # Access stats from profile_service
        assert profile_service.global_stats.total_games == 3
        assert profile_service.global_stats.total_victories == 2
        assert profile_service.global_stats.total_defeats == 1
        assert profile_service.global_stats.winrate == pytest.approx(0.667, rel=0.01)


# ================================================================
# TESTS: EndReason Coverage
# ================================================================

class TestEndReasonCoverage:
    """Test all EndReason enum values are handled correctly."""
    
    def test_all_end_reasons_recorded(self, temp_profile_dir, profile_storage):
        """Test all 6 EndReason values can be recorded."""
        # Setup
        settings = GameSettings()
        settings.max_time_game = 60
        settings.timer_strict_mode = True
        
        # Test each EndReason with a fresh profile service
        test_cases = [
            (EndReason.VICTORY, True),
            (EndReason.VICTORY_OVERTIME, True),
            (EndReason.ABANDON_EXIT, False),
            (EndReason.ABANDON_NEW_GAME, False),
            (EndReason.ABANDON_APP_CLOSE, False),
            (EndReason.TIMEOUT_STRICT, False),
        ]
        
        for end_reason, is_victory in test_cases:
            # Create fresh profile service for each test to avoid session accumulation
            ps = ProfileService(storage=profile_storage)
            profile = ps.create_profile(f"TestPlayer_{end_reason.name}")
            ps.load_profile(profile.profile_id)
            
            # Create engine with this profile service
            engine = create_mock_game_engine(ps, settings)
            
            # Record session
            session = simulate_end_game(engine, end_reason, is_victory)
            
            # Assert
            assert session.end_reason == end_reason
            assert session.is_victory == is_victory
            
            # Verify it was saved (should be only 1 session for this profile)
            assert len(ps.recent_sessions) == 1
            assert ps.recent_sessions[0].end_reason == end_reason
