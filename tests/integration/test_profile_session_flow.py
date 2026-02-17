"""Integration tests for profile session recording flow.

Tests end-to-end session recording through ProfileService:
- Session recording updates stats correctly
- Multiple sessions accumulate properly
- Session history trimming (last 50)
- Profile last_played updates
- Auto-save after recording
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta

from src.domain.services.profile_service import ProfileService
from src.infrastructure.storage.profile_storage import ProfileStorage
from src.domain.models.profile import SessionOutcome
from src.domain.models.game_end import EndReason


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
    return ProfileService(storage=profile_storage)


@pytest.fixture
def active_profile(profile_service):
    """Create and load a test profile."""
    profile = profile_service.create_profile("TestPlayer")
    profile_service.load_profile(profile.profile_id)
    return profile


def create_test_session(profile_id: str, end_reason: EndReason, is_victory: bool, elapsed_time: float = 120.0) -> SessionOutcome:
    """Helper to create test session outcome."""
    return SessionOutcome.create_new(
        profile_id=profile_id,
        end_reason=end_reason,
        is_victory=is_victory,
        elapsed_time=elapsed_time,
        timer_enabled=True,
        timer_limit=300,
        timer_mode="PERMISSIVE",
        timer_expired=False,
        scoring_enabled=True,
        final_score=1000,
        difficulty_level=3,
        deck_type="french",
        move_count=50
    )


class TestSessionRecordingFlow:
    """Test end-to-end session recording."""
    
    def test_record_victory_session(self, profile_service, active_profile):
        """Test recording a victory session updates stats."""
        session = create_test_session(
            profile_id=active_profile.profile_id,
            end_reason=EndReason.VICTORY,
            is_victory=True
        )
        
        # Record session
        result = profile_service.record_session(session)
        
        assert result is True
        assert len(profile_service.recent_sessions) == 1
        assert profile_service.global_stats.total_games == 1
        assert profile_service.global_stats.total_victories == 1
    
    def test_record_abandon_session(self, profile_service, active_profile):
        """Test recording an abandon session updates stats."""
        session = create_test_session(
            profile_id=active_profile.profile_id,
            end_reason=EndReason.ABANDON_EXIT,
            is_victory=False
        )
        
        # Record session
        result = profile_service.record_session(session)
        
        assert result is True
        assert len(profile_service.recent_sessions) == 1
        assert profile_service.global_stats.total_games == 1
        assert profile_service.global_stats.total_victories == 0
    
    def test_record_timeout_session(self, profile_service, active_profile):
        """Test recording a timeout session updates stats."""
        session = create_test_session(
            profile_id=active_profile.profile_id,
            end_reason=EndReason.TIMEOUT_STRICT,
            is_victory=False,
            elapsed_time=305.0
        )
        session.timer_expired = True
        
        # Record session
        result = profile_service.record_session(session)
        
        assert result is True
        assert profile_service.global_stats.total_games == 1
        assert profile_service.global_stats.total_victories == 0


class TestMultipleSessionsAccumulation:
    """Test multiple sessions update stats correctly."""
    
    def test_multiple_victories_accumulate(self, profile_service, active_profile):
        """Test multiple victory sessions accumulate stats."""
        # Record 3 victories
        for i in range(3):
            session = create_test_session(
                profile_id=active_profile.profile_id,
                end_reason=EndReason.VICTORY,
                is_victory=True,
                elapsed_time=100.0 + i * 10
            )
            profile_service.record_session(session)
        
        assert len(profile_service.recent_sessions) == 3
        assert profile_service.global_stats.total_games == 3
        assert profile_service.global_stats.total_victories == 3
    
    def test_mixed_outcomes_accumulate(self, profile_service, active_profile):
        """Test mix of victories and defeats accumulates correctly."""
        # Record 2 victories, 3 defeats
        outcomes = [
            (EndReason.VICTORY, True),
            (EndReason.ABANDON_EXIT, False),
            (EndReason.VICTORY, True),
            (EndReason.TIMEOUT_STRICT, False),
            (EndReason.ABANDON_APP_CLOSE, False)
        ]
        
        for end_reason, is_victory in outcomes:
            session = create_test_session(
                profile_id=active_profile.profile_id,
                end_reason=end_reason,
                is_victory=is_victory
            )
            profile_service.record_session(session)
        
        assert len(profile_service.recent_sessions) == 5
        assert profile_service.global_stats.total_games == 5
        assert profile_service.global_stats.total_victories == 2


class TestSessionHistoryTrimming:
    """Test session history keeps only last 50 sessions."""
    
    def test_history_trims_at_50(self, profile_service, active_profile):
        """Test session history trims to last 50 sessions."""
        # Record 55 sessions
        for i in range(55):
            session = create_test_session(
                profile_id=active_profile.profile_id,
                end_reason=EndReason.VICTORY if i % 2 == 0 else EndReason.ABANDON_EXIT,
                is_victory=(i % 2 == 0)
            )
            profile_service.record_session(session)
        
        # Should keep only last 50
        assert len(profile_service.recent_sessions) == 50
        assert profile_service.global_stats.total_games == 55
    
    def test_trimmed_sessions_not_in_history(self, profile_service, active_profile):
        """Test old sessions are removed when trimming occurs."""
        # Record 60 sessions with unique timestamps
        session_ids = []
        for i in range(60):
            session = create_test_session(
                profile_id=active_profile.profile_id,
                end_reason=EndReason.VICTORY,
                is_victory=True
            )
            session_ids.append(session.session_id)
            profile_service.record_session(session)
        
        # First 10 sessions should be trimmed
        recent_ids = [s.session_id for s in profile_service.recent_sessions]
        for i in range(10):
            assert session_ids[i] not in recent_ids
        for i in range(10, 60):
            assert session_ids[i] in recent_ids


class TestProfileLastPlayedUpdate:
    """Test profile last_played timestamp updates."""
    
    def test_last_played_updates_on_session(self, profile_service, active_profile):
        """Test last_played updates after recording session."""
        original_last_played = active_profile.last_played
        
        # Wait a tiny bit to ensure timestamp difference
        import time
        time.sleep(0.01)
        
        session = create_test_session(
            profile_id=active_profile.profile_id,
            end_reason=EndReason.VICTORY,
            is_victory=True
        )
        profile_service.record_session(session)
        
        # last_played should match session timestamp
        assert profile_service.active_profile.last_played == session.timestamp
        assert profile_service.active_profile.last_played >= original_last_played


class TestAutoSaveAfterRecording:
    """Test profile auto-saves after session recording."""
    
    def test_session_persists_after_recording(self, profile_service, profile_storage, active_profile):
        """Test session is saved to disk after recording."""
        session = create_test_session(
            profile_id=active_profile.profile_id,
            end_reason=EndReason.VICTORY,
            is_victory=True
        )
        
        # Record session (should auto-save)
        profile_service.record_session(session)
        
        # Create new service instance and load profile
        new_service = ProfileService(storage=profile_storage)
        new_service.load_profile(active_profile.profile_id)
        
        # Session should be persisted
        assert len(new_service.recent_sessions) == 1
        assert new_service.recent_sessions[0].session_id == session.session_id
        assert new_service.global_stats.total_games == 1
