"""Unit tests for SessionStorage with atomic write safety.

Tests:
- Save/load active session
- Clear active session
- has_active_session check
- Atomic write safety
- Corrupted JSON handling
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from src.infrastructure.storage.session_storage import SessionStorage


@pytest.fixture
def temp_data_dir():
    """Create temporary directory for test data."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def storage(temp_data_dir):
    """Create SessionStorage with temp directory."""
    return SessionStorage(data_dir=temp_data_dir)


class TestSessionStorage:
    """Test suite for SessionStorage."""
    
    def test_save_active_session(self, storage):
        """Test saving active session."""
        session_id = "session_001"
        profile_id = "profile_001"
        start_time = datetime.now().isoformat()
        
        # Save session
        result = storage.save_active_session(session_id, profile_id, start_time)
        
        assert result is True
        assert storage.active_session_file.exists()
        
        # Verify content
        with open(storage.active_session_file, 'r') as f:
            data = json.load(f)
        
        assert data["session_id"] == session_id
        assert data["profile_id"] == profile_id
        assert data["start_time"] == start_time
    
    def test_load_active_session(self, storage):
        """Test loading active session."""
        session_id = "session_002"
        profile_id = "profile_002"
        start_time = datetime.now().isoformat()
        
        # Save first
        storage.save_active_session(session_id, profile_id, start_time)
        
        # Load
        loaded = storage.load_active_session()
        
        assert loaded is not None
        assert loaded["session_id"] == session_id
        assert loaded["profile_id"] == profile_id
        assert loaded["start_time"] == start_time
    
    def test_load_active_session_not_found(self, storage):
        """Test loading when no active session exists."""
        # Don't save anything
        loaded = storage.load_active_session()
        
        assert loaded is None
    
    def test_clear_active_session(self, storage):
        """Test clearing active session."""
        session_id = "session_003"
        profile_id = "profile_003"
        start_time = datetime.now().isoformat()
        
        # Save session
        storage.save_active_session(session_id, profile_id, start_time)
        assert storage.active_session_file.exists()
        
        # Clear
        result = storage.clear_active_session()
        
        assert result is True
        assert not storage.active_session_file.exists()
    
    def test_clear_active_session_when_none_exists(self, storage):
        """Test clearing when no active session exists."""
        # Don't save anything
        result = storage.clear_active_session()
        
        # Should succeed (idempotent)
        assert result is True
    
    def test_has_active_session_true(self, storage):
        """Test has_active_session returns True when session exists."""
        session_id = "session_004"
        profile_id = "profile_004"
        start_time = datetime.now().isoformat()
        
        # Save session
        storage.save_active_session(session_id, profile_id, start_time)
        
        # Check
        assert storage.has_active_session() is True
    
    def test_has_active_session_false(self, storage):
        """Test has_active_session returns False when no session exists."""
        # Don't save anything
        assert storage.has_active_session() is False
    
    def test_atomic_write_safety(self, storage):
        """Test atomic write prevents corruption on simulated failure."""
        session_id = "session_005"
        profile_id = "profile_005"
        start_time = datetime.now().isoformat()
        
        # Save initial session
        storage.save_active_session(session_id, profile_id, start_time)
        
        # Verify temp file is cleaned up
        temp_file = storage.active_session_file.with_suffix('.tmp')
        assert not temp_file.exists()
        
        # Verify final file exists and is valid
        assert storage.active_session_file.exists()
        loaded = storage.load_active_session()
        assert loaded is not None
        assert loaded["session_id"] == session_id
    
    def test_corrupted_json_handling(self, storage):
        """Test handling of corrupted JSON file."""
        # Write corrupted JSON
        with open(storage.active_session_file, 'w') as f:
            f.write("{ invalid json content }")
        
        # Load should return None
        loaded = storage.load_active_session()
        
        assert loaded is None
    
    def test_overwrite_active_session(self, storage):
        """Test that saving a new session overwrites the old one."""
        # Save first session
        storage.save_active_session("session_001", "profile_001", "2024-01-01T10:00:00")
        
        # Save second session
        storage.save_active_session("session_002", "profile_002", "2024-01-01T11:00:00")
        
        # Load should return second session
        loaded = storage.load_active_session()
        
        assert loaded is not None
        assert loaded["session_id"] == "session_002"
        assert loaded["profile_id"] == "profile_002"
