"""Unit tests for ProfileService."""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch

from src.domain.services.profile_service import ProfileService
from src.domain.models.profile import UserProfile, SessionOutcome
from src.domain.models.statistics import GlobalStats, TimerStats, DifficultyStats, ScoringStats
from src.domain.models.game_end import EndReason
from src.infrastructure.storage.profile_storage import ProfileStorage
from src.domain.services.stats_aggregator import StatsAggregator


class TestProfileService:
    """Test suite for ProfileService."""
    
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
    def service(self, storage):
        """Create ProfileService with real storage."""
        return ProfileService(storage=storage)
    
    @pytest.fixture
    def mock_storage(self):
        """Create mock ProfileStorage."""
        return Mock(spec=ProfileStorage)
    
    @pytest.fixture
    def mock_service(self, mock_storage):
        """Create ProfileService with mock storage."""
        return ProfileService(storage=mock_storage)
    
    def test_initialization(self, service) -> None:
        """Test ProfileService initialization."""
        assert service.storage is not None
        assert service.aggregator is not None
        assert service.active_profile is None
        assert service.global_stats is None
        assert service.timer_stats is None
        assert service.difficulty_stats is None
        assert service.scoring_stats is None
        assert service.recent_sessions == []
    
    def test_initialization_with_defaults(self) -> None:
        """Test ProfileService creates default dependencies."""
        service = ProfileService()
        
        assert isinstance(service.storage, ProfileStorage)
        assert isinstance(service.aggregator, StatsAggregator)
    
    def test_create_profile(self, service) -> None:
        """Test creating a new profile."""
        profile = service.create_profile("Test Player", is_guest=False)
        
        assert profile is not None
        assert profile.profile_name == "Test Player"
        assert profile.is_guest is False
        assert profile.profile_id.startswith("profile_")
        
        # Verify it was persisted
        loaded = service.storage.load_profile(profile.profile_id)
        assert loaded is not None
        assert loaded["profile"]["profile_name"] == "Test Player"
    
    def test_create_guest_profile(self, service) -> None:
        """Test creating the guest profile."""
        profile = service.create_profile("Ospite", is_guest=True)
        
        assert profile is not None
        assert profile.profile_name == "Ospite"
        assert profile.is_guest is True
        assert profile.profile_id == "profile_000"
    
    def test_create_profile_failure(self, mock_service, mock_storage) -> None:
        """Test profile creation failure."""
        mock_storage.create_profile.return_value = False
        
        profile = mock_service.create_profile("Test")
        
        assert profile is None
        mock_storage.create_profile.assert_called_once()
    
    def test_load_profile(self, service) -> None:
        """Test loading a profile."""
        # Create a profile first
        created = service.create_profile("Test Player")
        profile_id = created.profile_id
        
        # Clear active profile
        service.active_profile = None
        
        # Load profile
        success = service.load_profile(profile_id)
        
        assert success is True
        assert service.active_profile is not None
        assert service.active_profile.profile_id == profile_id
        assert service.active_profile.profile_name == "Test Player"
        assert service.global_stats is not None
        assert service.timer_stats is not None
        assert service.difficulty_stats is not None
        assert service.scoring_stats is not None
    
    def test_load_profile_updates_last_played(self, service) -> None:
        """Test that loading a profile updates last_played timestamp."""
        created = service.create_profile("Test Player")
        original_time = created.last_played
        
        # Load profile
        service.load_profile(created.profile_id)
        
        assert service.active_profile.last_played > original_time
    
    def test_load_nonexistent_profile(self, service) -> None:
        """Test loading a profile that doesn't exist."""
        success = service.load_profile("nonexistent_id")
        
        assert success is False
        assert service.active_profile is None
    
    def test_load_profile_with_sessions(self, service) -> None:
        """Test loading profile that has recent sessions."""
        # Create profile
        profile = service.create_profile("Test Player")
        service.load_profile(profile.profile_id)
        
        # Add a session
        session = SessionOutcome.create_new(
            profile_id=profile.profile_id,
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=100.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False
        )
        service.record_session(session)
        
        # Clear and reload
        service.active_profile = None
        success = service.load_profile(profile.profile_id)
        
        assert success is True
        assert len(service.recent_sessions) == 1
        assert service.recent_sessions[0].session_id == session.session_id
    
    def test_save_active_profile(self, service) -> None:
        """Test saving active profile."""
        # Create and load profile
        profile = service.create_profile("Test Player")
        service.load_profile(profile.profile_id)
        
        # Modify profile
        service.active_profile.profile_name = "Modified Name"
        
        # Save
        success = service.save_active_profile()
        
        assert success is True
        
        # Verify changes persisted
        service.active_profile = None
        service.load_profile(profile.profile_id)
        assert service.active_profile.profile_name == "Modified Name"
    
    def test_save_active_profile_no_active(self, service) -> None:
        """Test saving when no active profile."""
        success = service.save_active_profile()
        
        assert success is False
    
    def test_delete_profile(self, service) -> None:
        """Test deleting a profile."""
        # Create profile
        profile = service.create_profile("Test Player")
        profile_id = profile.profile_id
        
        # Delete
        success = service.delete_profile(profile_id)
        
        assert success is True
        
        # Verify it's gone
        loaded = service.storage.load_profile(profile_id)
        assert loaded is None
    
    def test_delete_active_profile(self, service) -> None:
        """Test deleting the currently active profile."""
        # Create and load profile
        profile = service.create_profile("Test Player")
        service.load_profile(profile.profile_id)
        
        # Delete active profile
        success = service.delete_profile(profile.profile_id)
        
        assert success is True
        assert service.active_profile is None
        assert service.global_stats is None
        assert service.recent_sessions == []
    
    def test_delete_guest_profile_raises_error(self, service) -> None:
        """Test that deleting guest profile raises ValueError."""
        with pytest.raises(ValueError, match="Cannot delete guest profile"):
            service.delete_profile("profile_000")
    
    def test_delete_nonexistent_profile(self, service) -> None:
        """Test deleting a profile that doesn't exist."""
        success = service.delete_profile("nonexistent_id")
        
        assert success is False
    
    def test_list_profiles(self, service) -> None:
        """Test listing all profiles."""
        # Create multiple profiles
        service.create_profile("Player 1")
        service.create_profile("Player 2")
        service.create_profile("Player 3")
        
        profiles = service.list_profiles()
        
        assert len(profiles) == 3
        assert all("profile_id" in p for p in profiles)
        assert all("profile_name" in p for p in profiles)
    
    def test_list_profiles_empty(self, service) -> None:
        """Test listing when no profiles exist."""
        profiles = service.list_profiles()
        
        assert profiles == []
    
    def test_ensure_guest_profile_creates_if_missing(self, service) -> None:
        """Test ensure_guest_profile creates guest if missing."""
        # Ensure no guest exists
        assert not service.storage.profile_exists("profile_000")
        
        success = service.ensure_guest_profile()
        
        assert success is True
        assert service.storage.profile_exists("profile_000")
    
    def test_ensure_guest_profile_exists_already(self, service) -> None:
        """Test ensure_guest_profile when guest already exists."""
        # Create guest
        service.create_profile("Ospite", is_guest=True)
        
        success = service.ensure_guest_profile()
        
        assert success is True
    
    def test_record_session(self, service) -> None:
        """Test recording a game session."""
        # Create and load profile
        profile = service.create_profile("Test Player")
        service.load_profile(profile.profile_id)
        
        # Create session
        session = SessionOutcome.create_new(
            profile_id=profile.profile_id,
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=150.0,
            timer_enabled=True,
            timer_limit=300,
            timer_mode="STRICT",
            timer_expired=False,
            scoring_enabled=True,
            final_score=1500,
            difficulty_level=3
        )
        
        # Record session
        success = service.record_session(session)
        
        assert success is True
        assert len(service.recent_sessions) == 1
        assert service.global_stats.total_games == 1
        assert service.global_stats.total_victories == 1
        assert service.timer_stats.games_with_timer == 1
        assert service.difficulty_stats.games_by_level[3] == 1
        assert service.scoring_stats.games_with_scoring == 1
    
    def test_record_session_no_active_profile(self, service) -> None:
        """Test recording session when no active profile."""
        session = SessionOutcome.create_new(
            profile_id="test",
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=100.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False
        )
        
        success = service.record_session(session)
        
        assert success is False
    
    def test_record_session_profile_mismatch(self, service) -> None:
        """Test recording session with wrong profile_id."""
        # Create and load profile
        profile = service.create_profile("Test Player")
        service.load_profile(profile.profile_id)
        
        # Create session for different profile
        session = SessionOutcome.create_new(
            profile_id="wrong_profile_id",
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=100.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False
        )
        
        success = service.record_session(session)
        
        assert success is False
    
    def test_record_session_invalid_session(self, service) -> None:
        """Test recording an invalid session."""
        # Create and load profile
        profile = service.create_profile("Test Player")
        service.load_profile(profile.profile_id)
        
        # Create invalid session (negative time)
        session = SessionOutcome.create_new(
            profile_id=profile.profile_id,
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=-10.0,  # Invalid
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False
        )
        
        success = service.record_session(session)
        
        assert success is False
        assert len(service.recent_sessions) == 0
    
    def test_record_session_updates_last_played(self, service) -> None:
        """Test that recording session updates last_played."""
        # Create and load profile
        profile = service.create_profile("Test Player")
        service.load_profile(profile.profile_id)
        
        original_time = service.active_profile.last_played
        
        # Create session with specific timestamp
        session = SessionOutcome.create_new(
            profile_id=profile.profile_id,
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=100.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False
        )
        
        service.record_session(session)
        
        assert service.active_profile.last_played == session.timestamp
        assert service.active_profile.last_played >= original_time
    
    def test_record_session_limits_recent_sessions(self, service) -> None:
        """Test that recent sessions are limited to MAX_RECENT_SESSIONS."""
        # Create and load profile
        profile = service.create_profile("Test Player")
        service.load_profile(profile.profile_id)
        
        # Record more than MAX_RECENT_SESSIONS
        for i in range(60):
            session = SessionOutcome.create_new(
                profile_id=profile.profile_id,
                end_reason=EndReason.VICTORY if i % 2 == 0 else EndReason.ABANDON_EXIT,
                is_victory=i % 2 == 0,
                elapsed_time=100.0 + i,
                timer_enabled=False,
                timer_limit=0,
                timer_mode="OFF",
                timer_expired=False
            )
            service.record_session(session)
        
        # Should only keep last 50
        assert len(service.recent_sessions) == ProfileService.MAX_RECENT_SESSIONS
        
        # Should be the most recent ones
        assert service.recent_sessions[-1].elapsed_time == 159.0
    
    def test_record_session_auto_saves(self, service) -> None:
        """Test that recording session auto-saves the profile."""
        # Create and load profile
        profile = service.create_profile("Test Player")
        service.load_profile(profile.profile_id)
        
        # Record session
        session = SessionOutcome.create_new(
            profile_id=profile.profile_id,
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=100.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False
        )
        service.record_session(session)
        
        # Clear and reload
        service.active_profile = None
        service.load_profile(profile.profile_id)
        
        # Stats should be persisted
        assert service.global_stats.total_games == 1
        assert service.global_stats.total_victories == 1
    
    def test_multiple_sessions_update_stats(self, service) -> None:
        """Test that multiple sessions correctly update all stats."""
        # Create and load profile
        profile = service.create_profile("Test Player")
        service.load_profile(profile.profile_id)
        
        # Record 3 victories
        for i in range(3):
            session = SessionOutcome.create_new(
                profile_id=profile.profile_id,
                end_reason=EndReason.VICTORY,
                is_victory=True,
                elapsed_time=100.0 + i * 10,
                timer_enabled=True,
                timer_limit=300,
                timer_mode="STRICT",
                timer_expired=False,
                difficulty_level=3
            )
            service.record_session(session)
        
        # Record 2 defeats
        for i in range(2):
            session = SessionOutcome.create_new(
                profile_id=profile.profile_id,
                end_reason=EndReason.ABANDON_EXIT,
                is_victory=False,
                elapsed_time=50.0,
                timer_enabled=False,
                timer_limit=0,
                timer_mode="OFF",
                timer_expired=False,
                difficulty_level=3
            )
            service.record_session(session)
        
        assert service.global_stats.total_games == 5
        assert service.global_stats.total_victories == 3
        assert service.global_stats.total_defeats == 2
        assert service.global_stats.winrate == pytest.approx(0.6, rel=0.01)
        assert service.timer_stats.games_with_timer == 3
        assert service.difficulty_stats.games_by_level[3] == 5
