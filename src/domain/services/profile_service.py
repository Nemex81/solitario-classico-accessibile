"""High-level profile management service.

Provides:
- Profile CRUD operations (create, load, save, delete, list)
- Session recording with automatic stats aggregation
- Guest profile special handling
- Active profile management (load/switch profiles)
- DI-compatible constructor for testing
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from src.domain.models.profile import UserProfile, SessionOutcome
from src.domain.models.statistics import GlobalStats, TimerStats, DifficultyStats, ScoringStats
from src.infrastructure.storage.profile_storage import ProfileStorage
from src.domain.services.stats_aggregator import StatsAggregator
from src.infrastructure.logging import game_logger as log


class ProfileService:
    """High-level service for profile management and session tracking.
    
    Manages the active profile, coordinates CRUD operations with storage,
    and handles session recording with automatic stats aggregation.
    
    Attributes:
        storage: ProfileStorage instance for persistence
        aggregator: StatsAggregator instance for stats updates
        active_profile: Currently loaded UserProfile (None if no profile loaded)
        global_stats: GlobalStats for active profile
        timer_stats: TimerStats for active profile
        difficulty_stats: DifficultyStats for active profile
        scoring_stats: ScoringStats for active profile
        recent_sessions: List of recent SessionOutcome (last 50)
    """
    
    MAX_RECENT_SESSIONS = 50
    
    def __init__(
        self,
        storage: Optional[ProfileStorage] = None,
        aggregator: Optional[StatsAggregator] = None
    ):
        """Initialize ProfileService with optional dependencies.
        
        Args:
            storage: ProfileStorage instance (creates default if None)
            aggregator: StatsAggregator instance (creates default if None)
        """
        self.storage = storage if storage is not None else ProfileStorage()
        self.aggregator = aggregator if aggregator is not None else StatsAggregator()
        
        # Active profile state
        self.active_profile: Optional[UserProfile] = None
        self.global_stats: Optional[GlobalStats] = None
        self.timer_stats: Optional[TimerStats] = None
        self.difficulty_stats: Optional[DifficultyStats] = None
        self.scoring_stats: Optional[ScoringStats] = None
        self.recent_sessions: List[SessionOutcome] = []
        
        log.info_query_requested(
            "profile_service_init",
            "ProfileService initialized"
        )
    
    def create_profile(self, name: str, is_guest: bool = False) -> Optional[UserProfile]:
        """Create a new profile with initial stats.
        
        Args:
            name: Profile display name
            is_guest: Whether this is the guest profile
            
        Returns:
            Created UserProfile, or None if creation failed
        """
        try:
            # Create profile object
            profile = UserProfile.create_new(name, is_guest=is_guest)
            
            # Persist to storage
            success = self.storage.create_profile(profile)
            
            if success:
                log.info_query_requested(
                    "profile_create",
                    f"Profile created: {profile.profile_id} ({name})"
                )
                return profile
            else:
                log.warning_issued(
                    "ProfileService",
                    f"Failed to create profile: {name}"
                )
                return None
                
        except Exception as e:
            log.error_occurred(
                "ProfileService",
                f"Error creating profile: {name}",
                e
            )
            return None
    
    def load_profile(self, profile_id: str) -> bool:
        """Load profile and set as active.
        
        Args:
            profile_id: Profile ID to load
            
        Returns:
            True if loaded successfully and set as active
        """
        try:
            profile_data = self.storage.load_profile(profile_id)
            
            if profile_data is None:
                log.warning_issued(
                    "ProfileService",
                    f"Failed to load profile: {profile_id}"
                )
                return False
            
            # Parse profile data
            self.active_profile = UserProfile.from_dict(profile_data["profile"])
            
            # Parse stats
            stats_data = profile_data.get("stats", {})
            self.global_stats = GlobalStats.from_dict(stats_data.get("global", {}))
            self.timer_stats = TimerStats.from_dict(stats_data.get("timer", {}))
            self.difficulty_stats = DifficultyStats.from_dict(stats_data.get("difficulty", {}))
            self.scoring_stats = ScoringStats.from_dict(stats_data.get("scoring", {}))
            
            # Parse recent sessions
            sessions_data = profile_data.get("recent_sessions", [])
            self.recent_sessions = [
                SessionOutcome.from_dict(s) for s in sessions_data
            ]
            
            # Update last_played timestamp
            self.active_profile.last_played = datetime.utcnow()
            
            log.info_query_requested(
                "profile_load",
                f"Profile loaded and activated: {profile_id} ({self.active_profile.profile_name})"
            )
            
            return True
            
        except Exception as e:
            log.error_occurred(
                "ProfileService",
                f"Error loading profile: {profile_id}",
                e
            )
            return False
    
    def save_active_profile(self) -> bool:
        """Save current active profile to storage.
        
        Returns:
            True if saved successfully
        """
        if self.active_profile is None:
            log.warning_issued(
                "ProfileService",
                "Cannot save: no active profile"
            )
            return False
        
        try:
            # Build profile data structure
            profile_data = {
                "profile": self.active_profile.to_dict(),
                "stats": {
                    "global": self.global_stats.to_dict() if self.global_stats else {},
                    "timer": self.timer_stats.to_dict() if self.timer_stats else {},
                    "difficulty": self.difficulty_stats.to_dict() if self.difficulty_stats else {},
                    "scoring": self.scoring_stats.to_dict() if self.scoring_stats else {}
                },
                "recent_sessions": [s.to_dict() for s in self.recent_sessions]
            }
            
            # Save to storage
            success = self.storage.save_profile(
                self.active_profile.profile_id,
                profile_data
            )
            
            if success:
                log.info_query_requested(
                    "profile_save",
                    f"Active profile saved: {self.active_profile.profile_id}"
                )
            else:
                log.warning_issued(
                    "ProfileService",
                    f"Failed to save active profile: {self.active_profile.profile_id}"
                )
            
            return success
            
        except Exception as e:
            log.error_occurred(
                "ProfileService",
                f"Error saving active profile: {self.active_profile.profile_id}",
                e
            )
            return False
    
    def delete_profile(self, profile_id: str) -> bool:
        """Delete a profile.
        
        Args:
            profile_id: Profile ID to delete
            
        Returns:
            True if deleted successfully
            
        Raises:
            ValueError: If attempting to delete guest profile (profile_000)
        """
        # Guest protection - delegate to storage which will raise ValueError
        if profile_id == "profile_000":
            raise ValueError("Cannot delete guest profile (profile_000)")
        
        try:
            # Clear active profile if it's being deleted
            if self.active_profile and self.active_profile.profile_id == profile_id:
                self.active_profile = None
                self.global_stats = None
                self.timer_stats = None
                self.difficulty_stats = None
                self.scoring_stats = None
                self.recent_sessions = []
                
                log.info_query_requested(
                    "profile_delete",
                    f"Cleared active profile (being deleted): {profile_id}"
                )
            
            # Delete from storage
            success = self.storage.delete_profile(profile_id)
            
            if success:
                log.warning_issued(
                    "ProfileService",
                    f"Profile deleted: {profile_id}"
                )
            
            return success
            
        except ValueError:
            # Re-raise guest protection error
            raise
        except Exception as e:
            log.error_occurred(
                "ProfileService",
                f"Error deleting profile: {profile_id}",
                e
            )
            return False
    
    def list_profiles(self) -> List[Dict[str, Any]]:
        """List all profiles (summary information).
        
        Returns:
            List of profile summaries from storage index
        """
        try:
            profiles = self.storage.list_profiles()
            
            log.info_query_requested(
                "profile_list",
                f"Listed {len(profiles)} profiles"
            )
            
            return profiles
            
        except Exception as e:
            log.error_occurred(
                "ProfileService",
                "Error listing profiles",
                e
            )
            return []
    
    def ensure_guest_profile(self) -> bool:
        """Ensure guest profile exists (create if missing).
        
        Returns:
            True if guest profile exists or was created
        """
        try:
            # Check if guest profile exists
            if self.storage.profile_exists("profile_000"):
                log.info_query_requested(
                    "guest_profile_check",
                    "Guest profile already exists"
                )
                return True
            
            # Create guest profile
            guest = self.create_profile("Ospite", is_guest=True)
            
            if guest:
                log.info_query_requested(
                    "guest_profile_create",
                    "Guest profile created"
                )
                return True
            else:
                log.warning_issued(
                    "ProfileService",
                    "Failed to create guest profile"
                )
                return False
                
        except Exception as e:
            log.error_occurred(
                "ProfileService",
                "Error ensuring guest profile",
                e
            )
            return False
    
    def record_session(self, session: SessionOutcome) -> bool:
        """Record a session and update stats.
        
        Args:
            session: SessionOutcome to record
            
        Returns:
            True if recorded successfully
        """
        if self.active_profile is None:
            log.warning_issued(
                "ProfileService",
                "Cannot record session: no active profile"
            )
            return False
        
        try:
            # Validate session
            if not self.aggregator.validate_session(session):
                log.warning_issued(
                    "ProfileService",
                    f"Invalid session not recorded: {session.session_id}"
                )
                return False
            
            # Ensure session belongs to active profile
            if session.profile_id != self.active_profile.profile_id:
                log.warning_issued(
                    "ProfileService",
                    f"Session profile mismatch: {session.profile_id} != {self.active_profile.profile_id}"
                )
                return False
            
            # Validate stats are loaded (should always be true if active_profile exists)
            if (self.global_stats is None or self.timer_stats is None or 
                self.difficulty_stats is None or self.scoring_stats is None):
                log.error_occurred(
                    "ProfileService",
                    "Stats not loaded despite active profile",
                    ValueError("Invalid state: active profile without stats")
                )
                return False
            
            self.aggregator.update_all_stats(
                session,
                self.global_stats,
                self.timer_stats,
                self.difficulty_stats,
                self.scoring_stats
            )
            
            # Add to recent sessions (keep last 50)
            self.recent_sessions.append(session)
            if len(self.recent_sessions) > self.MAX_RECENT_SESSIONS:
                self.recent_sessions = self.recent_sessions[-self.MAX_RECENT_SESSIONS:]
            
            # Update profile last_played
            self.active_profile.last_played = session.timestamp
            
            log.info_query_requested(
                "session_record",
                f"Session recorded: {session.session_id} (end_reason={session.end_reason.value})"
            )
            
            # Auto-save after recording session
            return self.save_active_profile()
            
        except Exception as e:
            log.error_occurred(
                "ProfileService",
                f"Error recording session: {session.session_id}",
                e
            )
            return False
