"""Unit tests for ProfileStorage."""

import pytest
import json
import tempfile
from pathlib import Path
from src.infrastructure.storage.profile_storage import ProfileStorage
from src.domain.models.profile import UserProfile
from src.domain.models.statistics import GlobalStats


class TestProfileStorage:
    """Test suite for ProfileStorage."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def storage(self, temp_dir):
        """Create ProfileStorage with temporary directory."""
        return ProfileStorage(data_dir=temp_dir)
    
    @pytest.fixture
    def test_profile(self):
        """Create test profile."""
        return UserProfile.create_new("Test Player", is_guest=False)
    
    @pytest.fixture
    def guest_profile(self):
        """Create guest profile."""
        return UserProfile.create_guest()
    
    def test_initialization(self, temp_dir) -> None:
        """Test storage initialization creates directory."""
        storage = ProfileStorage(data_dir=temp_dir)
        
        assert storage.profiles_dir.exists()
        assert storage.profiles_dir.is_dir()
        assert storage.index_file.parent == storage.profiles_dir
    
    def test_create_profile(self, storage, test_profile) -> None:
        """Test creating a new profile."""
        result = storage.create_profile(test_profile)
        
        assert result is True
        
        # Verify file was created
        file_path = storage.profiles_dir / f"{test_profile.profile_id}.json"
        assert file_path.exists()
        
        # Verify content
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        assert "profile" in data
        assert "stats" in data
        assert "recent_sessions" in data
        assert data["profile"]["profile_name"] == "Test Player"
    
    def test_create_duplicate_profile(self, storage, test_profile) -> None:
        """Test that creating duplicate profile fails."""
        storage.create_profile(test_profile)
        result = storage.create_profile(test_profile)
        
        assert result is False
    
    def test_load_profile(self, storage, test_profile) -> None:
        """Test loading a profile."""
        storage.create_profile(test_profile)
        
        loaded = storage.load_profile(test_profile.profile_id)
        
        assert loaded is not None
        assert loaded["profile"]["profile_name"] == "Test Player"
        assert loaded["profile"]["profile_id"] == test_profile.profile_id
    
    def test_load_nonexistent_profile(self, storage) -> None:
        """Test loading a profile that doesn't exist."""
        loaded = storage.load_profile("nonexistent_id")
        
        assert loaded is None
    
    def test_load_corrupted_profile(self, storage, test_profile) -> None:
        """Test loading a corrupted JSON file."""
        # Create profile
        storage.create_profile(test_profile)
        
        # Corrupt the file
        file_path = storage.profiles_dir / f"{test_profile.profile_id}.json"
        with open(file_path, 'w') as f:
            f.write("{ invalid json }")
        
        loaded = storage.load_profile(test_profile.profile_id)
        
        assert loaded is None
    
    def test_save_profile(self, storage, test_profile) -> None:
        """Test saving profile data."""
        storage.create_profile(test_profile)
        
        # Load and modify
        profile_data = storage.load_profile(test_profile.profile_id)
        profile_data["stats"]["global"]["total_games"] = 10
        
        result = storage.save_profile(test_profile.profile_id, profile_data)
        
        assert result is True
        
        # Verify changes persisted
        reloaded = storage.load_profile(test_profile.profile_id)
        assert reloaded["stats"]["global"]["total_games"] == 10
    
    def test_delete_profile(self, storage, test_profile) -> None:
        """Test deleting a profile."""
        storage.create_profile(test_profile)
        
        result = storage.delete_profile(test_profile.profile_id)
        
        assert result is True
        
        # Verify file was deleted
        file_path = storage.profiles_dir / f"{test_profile.profile_id}.json"
        assert not file_path.exists()
    
    def test_delete_guest_profile_raises_error(self, storage, guest_profile) -> None:
        """Test that deleting guest profile raises ValueError."""
        storage.create_profile(guest_profile)
        
        with pytest.raises(ValueError, match="Cannot delete guest profile"):
            storage.delete_profile("profile_000")
    
    def test_delete_nonexistent_profile(self, storage) -> None:
        """Test deleting a profile that doesn't exist."""
        result = storage.delete_profile("nonexistent_id")
        
        assert result is False
    
    def test_list_profiles(self, storage, test_profile, guest_profile) -> None:
        """Test listing all profiles."""
        storage.create_profile(test_profile)
        storage.create_profile(guest_profile)
        
        profiles = storage.list_profiles()
        
        assert len(profiles) == 2
        assert any(p["profile_id"] == test_profile.profile_id for p in profiles)
        assert any(p["profile_id"] == guest_profile.profile_id for p in profiles)
    
    def test_list_profiles_empty(self, storage) -> None:
        """Test listing profiles when none exist."""
        profiles = storage.list_profiles()
        
        assert profiles == []
    
    def test_profile_exists(self, storage, test_profile) -> None:
        """Test checking if profile exists."""
        assert storage.profile_exists(test_profile.profile_id) is False
        
        storage.create_profile(test_profile)
        
        assert storage.profile_exists(test_profile.profile_id) is True
    
    def test_atomic_write_safety(self, storage, test_profile) -> None:
        """Test that atomic write pattern is used."""
        storage.create_profile(test_profile)
        
        file_path = storage.profiles_dir / f"{test_profile.profile_id}.json"
        temp_path = file_path.with_suffix('.tmp')
        
        # Temp file should not exist after successful write
        assert not temp_path.exists()
        
        # Main file should exist
        assert file_path.exists()
    
    def test_index_update_on_create(self, storage, test_profile) -> None:
        """Test that index is updated when profile is created."""
        storage.create_profile(test_profile)
        
        assert storage.index_file.exists()
        
        with open(storage.index_file, 'r') as f:
            index_data = json.load(f)
        
        assert "profiles" in index_data
        assert len(index_data["profiles"]) == 1
        assert index_data["profiles"][0]["profile_id"] == test_profile.profile_id
    
    def test_index_update_on_delete(self, storage, test_profile) -> None:
        """Test that index is updated when profile is deleted."""
        storage.create_profile(test_profile)
        storage.delete_profile(test_profile.profile_id)
        
        with open(storage.index_file, 'r') as f:
            index_data = json.load(f)
        
        assert len(index_data["profiles"]) == 0
    
    def test_multiple_profiles(self, storage) -> None:
        """Test creating and managing multiple profiles."""
        profiles = []
        for i in range(3):
            profile = UserProfile.create_new(f"Player {i}")
            profiles.append(profile)
            storage.create_profile(profile)
        
        # List all
        listed = storage.list_profiles()
        assert len(listed) == 3
        
        # Load each
        for profile in profiles:
            loaded = storage.load_profile(profile.profile_id)
            assert loaded is not None
    
    def test_profile_data_structure(self, storage, test_profile) -> None:
        """Test that created profile has correct data structure."""
        storage.create_profile(test_profile)
        loaded = storage.load_profile(test_profile.profile_id)
        
        # Verify structure
        assert "profile" in loaded
        assert "stats" in loaded
        assert "recent_sessions" in loaded
        
        # Verify stats structure
        assert "global" in loaded["stats"]
        assert "timer" in loaded["stats"]
        assert "difficulty" in loaded["stats"]
        assert "scoring" in loaded["stats"]
        
        # Verify recent_sessions is list
        assert isinstance(loaded["recent_sessions"], list)
        assert len(loaded["recent_sessions"]) == 0
