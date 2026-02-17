"""Integration tests for session recovery system.

Tests SessionTracker's ability to:
- Track active sessions
- Detect dirty shutdowns (orphaned sessions)
- Prevent duplicate recovery
- Handle clean shutdown flows
"""

import pytest
from pathlib import Path
from datetime import datetime

from src.domain.services.session_tracker import SessionTracker
from src.infrastructure.storage.session_storage import SessionStorage


@pytest.fixture
def temp_session_dir(tmp_path):
    """Create temporary session storage directory."""
    session_dir = tmp_path / ".solitario"
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir


@pytest.fixture
def session_storage(temp_session_dir):
    """Create SessionStorage with temp directory."""
    return SessionStorage(data_dir=temp_session_dir)


@pytest.fixture
def tracker(session_storage):
    """Create SessionTracker with temp storage."""
    return SessionTracker(storage=session_storage)


class TestSessionLifecycle:
    """Test normal session start/end cycle."""
    
    def test_start_session_success(self, tracker, session_storage):
        """Test session can be marked as active."""
        # Start session
        result = tracker.start_session("sess_001", "profile_123")
        
        assert result is True
        assert session_storage.has_active_session() is True
        
        # Verify session data
        session_data = session_storage.load_active_session()
        assert session_data is not None
        assert session_data["session_id"] == "sess_001"
        assert session_data["profile_id"] == "profile_123"
        assert "start_time" in session_data
    
    def test_end_session_success(self, tracker, session_storage):
        """Test session can be properly closed."""
        # Start session
        tracker.start_session("sess_001", "profile_123")
        assert session_storage.has_active_session() is True
        
        # End session
        result = tracker.end_session("sess_001")
        
        assert result is True
        assert session_storage.has_active_session() is False
    
    def test_complete_session_cycle(self, tracker, session_storage):
        """Test full start -> end cycle leaves no orphans."""
        # Start session
        tracker.start_session("sess_001", "profile_123")
        
        # End session properly
        tracker.end_session("sess_001")
        
        # Should find no orphaned sessions
        orphans = tracker.get_orphaned_sessions()
        assert len(orphans) == 0


class TestOrphanedSessionDetection:
    """Test detection of sessions not properly closed."""
    
    def test_detect_orphaned_session(self, tracker, session_storage):
        """Test orphaned session is detected after dirty shutdown."""
        # Simulate dirty shutdown: start session but don't end it
        session_storage.save_active_session("sess_orphan", "profile_123", datetime.utcnow().isoformat())
        
        # Check for orphans
        orphans = tracker.get_orphaned_sessions()
        
        assert len(orphans) == 1
        assert orphans[0]["session_id"] == "sess_orphan"
        assert orphans[0]["profile_id"] == "profile_123"
        assert orphans[0]["recovered"] is False
        assert "start_time" in orphans[0]
    
    def test_no_orphans_when_clean_shutdown(self, tracker, session_storage):
        """Test no orphans detected when session properly closed."""
        # Start and properly end session
        tracker.start_session("sess_001", "profile_123")
        tracker.end_session("sess_001")
        
        # Should find no orphans
        orphans = tracker.get_orphaned_sessions()
        assert len(orphans) == 0
    
    def test_no_orphans_when_no_session(self, tracker):
        """Test no orphans when no session ever started."""
        orphans = tracker.get_orphaned_sessions()
        assert len(orphans) == 0


class TestRecoveryFlagMechanism:
    """Test recovery tracking to prevent duplicate processing."""
    
    def test_mark_recovered_prevents_duplicate(self, tracker, session_storage):
        """Test marking session as recovered prevents duplicate detection."""
        # Create orphaned session
        session_storage.save_active_session("sess_orphan", "profile_123", datetime.utcnow().isoformat())
        
        # First check finds orphan
        orphans1 = tracker.get_orphaned_sessions()
        assert len(orphans1) == 1
        
        # Mark as recovered
        tracker.mark_recovered("sess_orphan")
        
        # Second check should not find it
        orphans2 = tracker.get_orphaned_sessions()
        assert len(orphans2) == 0
    
    def test_recovery_flag_initially_false(self, tracker, session_storage):
        """Test orphaned sessions initially have recovered=False."""
        # Create orphaned session
        session_storage.save_active_session("sess_orphan", "profile_123", datetime.utcnow().isoformat())
        
        orphans = tracker.get_orphaned_sessions()
        assert orphans[0]["recovered"] is False
    
    def test_mark_recovered_returns_true(self, tracker):
        """Test mark_recovered indicates success."""
        result = tracker.mark_recovered("sess_001")
        assert result is True
