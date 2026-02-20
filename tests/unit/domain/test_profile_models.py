"""Unit tests for profile domain models."""

import pytest
from datetime import datetime
from src.domain.models.profile import UserProfile, SessionOutcome
from src.domain.models.game_end import EndReason


class TestUserProfile:
    """Test suite for UserProfile model."""
    
    def test_create_new_normal_profile(self) -> None:
        """Test creation of a normal (non-guest) profile."""
        profile = UserProfile.create_new("Test Player", is_guest=False)
        
        assert profile.profile_name == "Test Player"
        assert profile.profile_id.startswith("profile_")
        assert profile.is_guest is False
        assert profile.is_default is True  # First non-guest profile is default
        assert isinstance(profile.created_at, datetime)
        assert isinstance(profile.last_played, datetime)
    
    def test_create_guest_profile(self) -> None:
        """Test creation of the special guest profile."""
        guest = UserProfile.create_guest()
        
        assert guest.profile_name == "Ospite"
        assert guest.profile_id == "profile_000"
        assert guest.is_guest is True
        assert guest.is_default is False
    
    def test_profile_id_uniqueness(self) -> None:
        """Test that normal profiles get unique IDs."""
        profile1 = UserProfile.create_new("Player 1")
        profile2 = UserProfile.create_new("Player 2")
        
        assert profile1.profile_id != profile2.profile_id
    
    def test_guest_profile_id_consistency(self) -> None:
        """Test that guest profile always gets the same ID."""
        guest1 = UserProfile.create_guest()
        guest2 = UserProfile.create_guest()
        
        assert guest1.profile_id == "profile_000"
        assert guest2.profile_id == "profile_000"
    
    def test_to_dict_serialization(self) -> None:
        """Test profile serialization to dictionary."""
        profile = UserProfile.create_new("Test Player")
        data = profile.to_dict()
        
        assert data["profile_name"] == "Test Player"
        assert data["profile_id"] == profile.profile_id
        assert isinstance(data["created_at"], str)  # ISO format
        assert isinstance(data["last_played"], str)
        assert data["is_guest"] is False
        assert data["preferred_difficulty"] == 3
        assert data["preferred_deck"] == "french"
    
    def test_from_dict_deserialization(self) -> None:
        """Test profile deserialization from dictionary."""
        profile = UserProfile.create_new("Test Player")
        data = profile.to_dict()
        restored = UserProfile.from_dict(data)
        
        assert restored.profile_name == profile.profile_name
        assert restored.profile_id == profile.profile_id
        assert restored.is_guest == profile.is_guest
        assert isinstance(restored.created_at, datetime)
        assert isinstance(restored.last_played, datetime)
    
    def test_roundtrip_serialization(self) -> None:
        """Test that serialize + deserialize preserves data."""
        original = UserProfile.create_new("Test Player")
        data = original.to_dict()
        restored = UserProfile.from_dict(data)
        
        assert restored.to_dict() == data


class TestSessionOutcome:
    """Test suite for SessionOutcome model."""
    
    def test_create_new_victory_session(self) -> None:
        """Test creation of a victory session."""
        session = SessionOutcome.create_new(
            profile_id="profile_123",
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=180.5,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False
        )
        
        assert session.profile_id == "profile_123"
        assert session.end_reason == EndReason.VICTORY
        assert session.is_victory is True
        assert session.elapsed_time == 180.5
        assert isinstance(session.session_id, str)
        assert isinstance(session.timestamp, datetime)
    
    def test_create_victory_overtime_session(self) -> None:
        """Test creation of a victory overtime session."""
        session = SessionOutcome.create_new(
            profile_id="profile_123",
            end_reason=EndReason.VICTORY_OVERTIME,
            is_victory=True,
            elapsed_time=420.0,
            timer_enabled=True,
            timer_limit=300,
            timer_mode="PERMISSIVE",
            timer_expired=True,
            overtime_duration=120.0
        )
        
        assert session.end_reason == EndReason.VICTORY_OVERTIME
        assert session.is_victory is True
        assert session.overtime_duration == 120.0
        assert session.timer_enabled is True
        assert session.timer_expired is True
    
    def test_create_abandon_session(self) -> None:
        """Test creation of an abandon session."""
        session = SessionOutcome.create_new(
            profile_id="profile_123",
            end_reason=EndReason.ABANDON_EXIT,
            is_victory=False,
            elapsed_time=60.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False
        )
        
        assert session.end_reason == EndReason.ABANDON_EXIT
        assert session.is_victory is False
    
    def test_create_timeout_session(self) -> None:
        """Test creation of a timeout session."""
        session = SessionOutcome.create_new(
            profile_id="profile_123",
            end_reason=EndReason.TIMEOUT_STRICT,
            is_victory=False,
            elapsed_time=300.0,
            timer_enabled=True,
            timer_limit=300,
            timer_mode="STRICT",
            timer_expired=True
        )
        
        assert session.end_reason == EndReason.TIMEOUT_STRICT
        assert session.is_victory is False
        assert session.timer_expired is True
    
    def test_session_id_uniqueness(self) -> None:
        """Test that sessions get unique IDs."""
        session1 = SessionOutcome.create_new(
            profile_id="profile_123",
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=100.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False
        )
        session2 = SessionOutcome.create_new(
            profile_id="profile_123",
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=100.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False
        )
        
        assert session1.session_id != session2.session_id
    
    def test_to_dict_serialization(self) -> None:
        """Test session serialization to dictionary."""
        session = SessionOutcome.create_new(
            profile_id="profile_123",
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=180.5,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False,
            scoring_enabled=True,
            final_score=1500,
            difficulty_level=3,
            move_count=50
        )
        data = session.to_dict()
        
        assert data["profile_id"] == "profile_123"
        assert data["end_reason"] == "victory"
        assert data["is_victory"] is True
        assert data["elapsed_time"] == 180.5
        assert data["scoring_enabled"] is True
        assert data["final_score"] == 1500
        assert isinstance(data["timestamp"], str)  # ISO format
    
    def test_from_dict_deserialization(self) -> None:
        """Test session deserialization from dictionary."""
        session = SessionOutcome.create_new(
            profile_id="profile_123",
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=180.5,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False
        )
        data = session.to_dict()
        restored = SessionOutcome.from_dict(data)
        
        assert restored.profile_id == session.profile_id
        assert restored.end_reason == session.end_reason
        assert restored.is_victory == session.is_victory
        assert isinstance(restored.timestamp, datetime)
        assert isinstance(restored.end_reason, EndReason)
    
    def test_roundtrip_serialization(self) -> None:
        """Test that serialize + deserialize preserves data."""
        original = SessionOutcome.create_new(
            profile_id="profile_123",
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=180.5,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False
        )
        data = original.to_dict()
        restored = SessionOutcome.from_dict(data)
        
        # Compare all key fields
        assert restored.profile_id == original.profile_id
        assert restored.end_reason == original.end_reason
        assert restored.is_victory == original.is_victory
        assert restored.elapsed_time == original.elapsed_time
    
    def test_default_values(self) -> None:
        """Test that default values are set correctly."""
        session = SessionOutcome.create_new(
            profile_id="profile_123",
            end_reason=EndReason.VICTORY,
            is_victory=True,
            elapsed_time=100.0,
            timer_enabled=False,
            timer_limit=0,
            timer_mode="OFF",
            timer_expired=False
        )
        
        assert session.overtime_duration == 0.0
        assert session.scoring_enabled is False
        assert session.final_score == 0
        assert session.difficulty_level == 3
        assert session.deck_type == "french"
        assert session.draw_count == 1
        assert session.move_count == 0
        assert session.foundation_cards == [0, 0, 0, 0]
        assert session.completed_suits == 0
        assert session.notes == ""
