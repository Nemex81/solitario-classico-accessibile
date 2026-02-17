"""Session tracking service for dirty shutdown recovery.

Provides:
- Active session lifecycle management (start/end)
- Orphaned session detection for crash recovery
- Recovery flag management to prevent duplicate processing
- Integration with SessionStorage for persistence

Orphaned sessions are those that were marked active but never properly closed,
indicating a crash or abnormal termination.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from src.infrastructure.storage.session_storage import SessionStorage
from src.infrastructure.logging import game_logger as log


class SessionTracker:
    """Service for tracking active sessions and detecting dirty shutdowns.
    
    Manages session lifecycle by:
    - Marking sessions as active when started
    - Clearing sessions when properly closed
    - Detecting orphaned sessions (crashes/dirty shutdowns)
    - Tracking recovery status to prevent duplicate recovery
    
    Attributes:
        storage: SessionStorage instance for persistence
        recovered_sessions: Set of session_ids already recovered (in-memory cache)
    """
    
    def __init__(self, storage: Optional[SessionStorage] = None):
        """Initialize SessionTracker with optional storage dependency.
        
        Args:
            storage: SessionStorage instance (creates default if None)
        """
        self.storage = storage if storage is not None else SessionStorage()
        self.recovered_sessions = set()
        
        log.info_query_requested(
            "session_tracker_init",
            "SessionTracker initialized"
        )
    
    def start_session(self, session_id: str, profile_id: str) -> bool:
        """Mark a session as active for crash recovery tracking.
        
        Args:
            session_id: Unique session identifier
            profile_id: Profile ID for this session
            
        Returns:
            True if session marked active successfully
        """
        try:
            start_time = datetime.utcnow().isoformat()
            
            success = self.storage.save_active_session(
                session_id=session_id,
                profile_id=profile_id,
                start_time=start_time
            )
            
            if success:
                log.info_query_requested(
                    "session_start",
                    f"Session started: {session_id} (profile: {profile_id})"
                )
            else:
                log.warning_issued(
                    "SessionTracker",
                    f"Failed to mark session active: {session_id}"
                )
            
            return success
            
        except Exception as e:
            log.error_occurred(
                "SessionTracker",
                f"Error starting session: {session_id}",
                e
            )
            return False
    
    def end_session(self, session_id: str) -> bool:
        """Mark a session as complete (clean shutdown).
        
        Args:
            session_id: Session identifier to close
            
        Returns:
            True if session cleared successfully
        """
        try:
            success = self.storage.clear_active_session()
            
            if success:
                log.info_query_requested(
                    "session_end",
                    f"Session ended: {session_id}"
                )
            else:
                log.warning_issued(
                    "SessionTracker",
                    f"Failed to clear session: {session_id}"
                )
            
            return success
            
        except Exception as e:
            log.error_occurred(
                "SessionTracker",
                f"Error ending session: {session_id}",
                e
            )
            return False
    
    def get_orphaned_sessions(self) -> List[Dict[str, Any]]:
        """Find sessions that were not properly closed (dirty shutdown).
        
        An orphaned session indicates:
        - App crashed during gameplay
        - System shutdown during game
        - Process killed unexpectedly
        
        Returns:
            List of session info dicts with keys:
                - session_id: str
                - profile_id: str
                - start_time: str (ISO format)
                - recovered: bool (always False - caller sets to True after recovery)
        """
        try:
            # Check for active session
            session_data = self.storage.load_active_session()
            
            if session_data is None:
                log.info_query_requested(
                    "orphan_check",
                    "No orphaned sessions found"
                )
                return []
            
            # Found orphaned session
            session_id = session_data.get("session_id", "unknown")
            
            # Skip if already recovered
            if session_id in self.recovered_sessions:
                log.info_query_requested(
                    "orphan_check",
                    f"Session already recovered: {session_id}"
                )
                return []
            
            # Add recovery flag (set to False - caller will set True after recovery)
            session_data["recovered"] = False
            
            log.warning_issued(
                "SessionTracker",
                f"Orphaned session detected: {session_id} (profile: {session_data.get('profile_id')})"
            )
            
            return [session_data]
            
        except Exception as e:
            log.error_occurred(
                "SessionTracker",
                "Error checking for orphaned sessions",
                e
            )
            return []
    
    def mark_recovered(self, session_id: str) -> bool:
        """Mark a session as recovered to prevent duplicate recovery.
        
        Args:
            session_id: Session identifier that was recovered
            
        Returns:
            True if marked successfully
        """
        try:
            self.recovered_sessions.add(session_id)
            
            log.info_query_requested(
                "session_recovery",
                f"Session marked as recovered: {session_id}"
            )
            
            return True
            
        except Exception as e:
            log.error_occurred(
                "SessionTracker",
                f"Error marking session recovered: {session_id}",
                e
            )
            return False
