"""JSON storage for active session tracking with atomic write safety.

Provides:
- Active session save/load for crash recovery
- Atomic write pattern (temp file + rename) to prevent corruption
- Session state checking
- Logging integration for all critical operations

Storage location: ~/.solitario/.sessions/active_session.json
"""

import json
import shutil
from pathlib import Path
from typing import Optional, Dict, Any

from src.infrastructure.logging import game_logger as log


class SessionStorage:
    """Persistent storage for active session tracking with atomic write safety.
    
    Manages active session state for crash recovery with:
    - Atomic writes to prevent corruption on crash
    - Simple session state tracking (session_id, profile_id, start_time)
    - Comprehensive logging
    
    Attributes:
        sessions_dir: Directory containing session files
        active_session_file: Path to active session JSON
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize session storage.
        
        Args:
            data_dir: Custom data directory (optional).
                     Defaults to ~/.solitario
        """
        if data_dir:
            self.sessions_dir = data_dir / ".sessions"
        else:
            # Default: ~/.solitario/.sessions
            home = Path.home()
            self.sessions_dir = home / ".solitario" / ".sessions"
        
        self.active_session_file = self.sessions_dir / "active_session.json"
        
        # Ensure directory exists
        self._ensure_directory_exists()
    
    def _ensure_directory_exists(self) -> None:
        """Create sessions directory if it doesn't exist."""
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        log.info_query_requested(
            "session_storage_init",
            f"Session storage initialized at {self.sessions_dir}"
        )
    
    def _atomic_write_json(self, file_path: Path, data: dict) -> None:
        """Write JSON atomically using temp file + rename to prevent corruption.
        
        This ensures that even if the app crashes during write, the original file
        remains intact (no partial/corrupted JSON).
        
        Args:
            file_path: Target file path
            data: Dictionary to write as JSON
            
        Raises:
            Exception: If write fails
        """
        temp_path = file_path.with_suffix('.tmp')
        
        try:
            # Write to temp file first
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Atomic replace (OS-level operation)
            shutil.move(str(temp_path), str(file_path))
            
        except Exception as e:
            # Cleanup temp file on error
            if temp_path.exists():
                temp_path.unlink()
            raise e
    
    def save_active_session(
        self,
        session_id: str,
        profile_id: str,
        start_time: str
    ) -> bool:
        """Save active session for crash recovery.
        
        Args:
            session_id: Unique session identifier
            profile_id: Profile ID for this session
            start_time: Session start time (ISO format string)
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            session_data = {
                "session_id": session_id,
                "profile_id": profile_id,
                "start_time": start_time
            }
            
            # Atomic write
            self._atomic_write_json(self.active_session_file, session_data)
            
            log.info_query_requested(
                "session_save",
                f"Active session saved: {session_id} (profile: {profile_id})"
            )
            
            return True
        
        except Exception as e:
            log.error_occurred(
                "SessionStorage",
                f"Failed to save active session: {session_id}",
                e
            )
            return False
    
    def load_active_session(self) -> Optional[Dict[str, Any]]:
        """Load active session data.
        
        Returns:
            Session data dict with session_id, profile_id, start_time,
            or None if no active session or corrupted
        """
        try:
            if not self.active_session_file.exists():
                log.info_query_requested(
                    "session_load",
                    "No active session file found"
                )
                return None
            
            with open(self.active_session_file, 'r', encoding='utf-8') as f:
                session_data: dict[str, Any] = json.load(f)
            
            log.info_query_requested(
                "session_load",
                f"Active session loaded: {session_data.get('session_id')}"
            )
            
            return session_data
        
        except json.JSONDecodeError as e:
            log.error_occurred(
                "SessionStorage",
                "Corrupted active session file",
                e
            )
            return None
        
        except Exception as e:
            log.error_occurred(
                "SessionStorage",
                "Failed to load active session",
                e
            )
            return None
    
    def clear_active_session(self) -> bool:
        """Clear active session (session completed/closed).
        
        Returns:
            True if cleared successfully, False otherwise
        """
        try:
            if not self.active_session_file.exists():
                log.info_query_requested(
                    "session_clear",
                    "No active session to clear"
                )
                return True
            
            self.active_session_file.unlink()
            
            log.info_query_requested(
                "session_clear",
                "Active session cleared"
            )
            
            return True
        
        except Exception as e:
            log.error_occurred(
                "SessionStorage",
                "Failed to clear active session",
                e
            )
            return False
    
    def has_active_session(self) -> bool:
        """Check if there is an active session.
        
        Returns:
            True if active session exists, False otherwise
        """
        return self.active_session_file.exists()
