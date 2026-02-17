"""JSON storage for profile data with atomic write safety.

Provides:
- Profile CRUD operations (create, load, list, delete)
- Atomic write pattern (temp file + rename) to prevent corruption
- Guest profile protection (profile_000 cannot be deleted)
- Logging integration for all critical operations

Storage location: ~/.solitario/profiles/{profile_id}.json
Index file: ~/.solitario/profiles/profiles_index.json
"""

import json
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any

from src.domain.models.profile import UserProfile
from src.domain.models.statistics import GlobalStats, TimerStats, DifficultyStats, ScoringStats
from src.infrastructure.logging import game_logger as log


class ProfileStorage:
    """Persistent storage for user profiles with atomic write safety.
    
    Manages profile data persistence with:
    - Atomic writes to prevent corruption on crash
    - Profile index for fast listing
    - Guest profile protection
    - Comprehensive logging
    
    Attributes:
        profiles_dir: Directory containing profile files
        index_file: Path to profiles index JSON
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize profile storage.
        
        Args:
            data_dir: Custom data directory (optional).
                     Defaults to ~/.solitario
        """
        if data_dir:
            self.profiles_dir = data_dir / "profiles"
        else:
            # Default: ~/.solitario/profiles
            home = Path.home()
            self.profiles_dir = home / ".solitario" / "profiles"
        
        self.index_file = self.profiles_dir / "profiles_index.json"
        
        # Ensure directory exists
        self._ensure_directory_exists()
    
    def _ensure_directory_exists(self) -> None:
        """Create profiles directory if it doesn't exist."""
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        log.info_query_requested(
            "profile_storage_init",
            f"Profile storage initialized at {self.profiles_dir}"
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
    
    def create_profile(self, profile: UserProfile) -> bool:
        """Create a new profile.
        
        Args:
            profile: UserProfile to create
            
        Returns:
            True if created successfully, False otherwise
        """
        try:
            file_path = self.profiles_dir / f"{profile.profile_id}.json"
            
            if file_path.exists():
                log.warning_issued(
                    "ProfileStorage",
                    f"Profile already exists: {profile.profile_id}"
                )
                return False
            
            # Create profile data structure
            profile_data = {
                "profile": profile.to_dict(),
                "stats": {
                    "global": GlobalStats().to_dict(),
                    "timer": TimerStats().to_dict(),
                    "difficulty": DifficultyStats().to_dict(),
                    "scoring": ScoringStats().to_dict()
                },
                "recent_sessions": []
            }
            
            # Atomic write
            self._atomic_write_json(file_path, profile_data)
            
            # Update index
            self._update_index()
            
            log.info_query_requested(
                "profile_create",
                f"Profile created: {profile.profile_id} ({profile.profile_name})"
            )
            
            return True
        
        except Exception as e:
            log.error_occurred(
                "ProfileStorage",
                f"Failed to create profile: {profile.profile_id}",
                e
            )
            return False
    
    def load_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Load a profile by ID.
        
        Args:
            profile_id: Profile ID to load
            
        Returns:
            Profile data dict, or None if not found/corrupted
        """
        try:
            file_path = self.profiles_dir / f"{profile_id}.json"
            
            if not file_path.exists():
                log.warning_issued(
                    "ProfileStorage",
                    f"Profile not found: {profile_id}"
                )
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
            
            log.info_query_requested(
                "profile_load",
                f"Profile loaded: {profile_id}"
            )
            
            return profile_data
        
        except json.JSONDecodeError as e:
            log.error_occurred(
                "ProfileStorage",
                f"Corrupted profile file: {profile_id}",
                e
            )
            return None
        
        except Exception as e:
            log.error_occurred(
                "ProfileStorage",
                f"Failed to load profile: {profile_id}",
                e
            )
            return None
    
    def save_profile(self, profile_id: str, profile_data: Dict[str, Any]) -> bool:
        """Save profile data (update existing).
        
        Args:
            profile_id: Profile ID
            profile_data: Complete profile data dict
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            file_path = self.profiles_dir / f"{profile_id}.json"
            
            # Atomic write
            self._atomic_write_json(file_path, profile_data)
            
            # Update index
            self._update_index()
            
            log.info_query_requested(
                "profile_save",
                f"Profile saved: {profile_id}"
            )
            
            return True
        
        except Exception as e:
            log.error_occurred(
                "ProfileStorage",
                f"Failed to save profile: {profile_id}",
                e
            )
            return False
    
    def delete_profile(self, profile_id: str) -> bool:
        """Delete a profile.
        
        Args:
            profile_id: Profile ID to delete
            
        Returns:
            True if deleted successfully, False otherwise
            
        Raises:
            ValueError: If attempting to delete guest profile (profile_000)
        """
        # Guest protection - hard fail
        if profile_id == "profile_000":
            raise ValueError("Cannot delete guest profile (profile_000)")
        
        try:
            file_path = self.profiles_dir / f"{profile_id}.json"
            
            if not file_path.exists():
                log.warning_issued(
                    "ProfileStorage",
                    f"Profile not found for deletion: {profile_id}"
                )
                return False
            
            file_path.unlink()
            
            # Update index
            self._update_index()
            
            log.warning_issued(
                "ProfileStorage",
                f"Profile deleted: {profile_id}"
            )
            
            return True
        
        except Exception as e:
            log.error_occurred(
                "ProfileStorage",
                f"Failed to delete profile: {profile_id}",
                e
            )
            return False
    
    def list_profiles(self) -> List[Dict[str, Any]]:
        """List all profiles (summary from index).
        
        Returns:
            List of profile summaries
        """
        try:
            if not self.index_file.exists():
                log.info_query_requested(
                    "profile_list",
                    "No profiles index found, returning empty list"
                )
                return []
            
            with open(self.index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            profiles = index_data.get("profiles", [])
            
            log.info_query_requested(
                "profile_list",
                f"Profiles listed: {len(profiles)} profiles"
            )
            
            return profiles
        
        except Exception as e:
            log.error_occurred(
                "ProfileStorage",
                "Failed to list profiles",
                e
            )
            return []
    
    def _update_index(self) -> None:
        """Update profiles index with current profile files.
        
        Scans profiles directory and rebuilds index.
        """
        try:
            profiles = []
            
            # Scan all profile files
            for file_path in self.profiles_dir.glob("profile_*.json"):
                if file_path.name == "profiles_index.json":
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        profile_data = json.load(f)
                    
                    profile_info = profile_data.get("profile", {})
                    stats = profile_data.get("stats", {}).get("global", {})
                    
                    # Create summary
                    profiles.append({
                        "profile_id": profile_info.get("profile_id"),
                        "profile_name": profile_info.get("profile_name"),
                        "is_guest": profile_info.get("is_guest", False),
                        "is_default": profile_info.get("is_default", False),
                        "last_played": profile_info.get("last_played"),
                        "total_games": stats.get("total_games", 0),
                        "total_victories": stats.get("total_victories", 0)
                    })
                
                except Exception as e:
                    log.error_occurred(
                        "ProfileStorage",
                        f"Failed to read profile for index: {file_path.name}",
                        e
                    )
            
            # Sort by last_played (most recent first)
            profiles.sort(key=lambda p: p.get("last_played", ""), reverse=True)
            
            # Write index atomically
            index_data = {
                "profiles": profiles,
                "last_updated": None  # Could add timestamp if needed
            }
            
            self._atomic_write_json(self.index_file, index_data)
        
        except Exception as e:
            log.error_occurred(
                "ProfileStorage",
                "Failed to update profiles index",
                e
            )
    
    def profile_exists(self, profile_id: str) -> bool:
        """Check if a profile exists.
        
        Args:
            profile_id: Profile ID to check
            
        Returns:
            True if profile exists, False otherwise
        """
        file_path = self.profiles_dir / f"{profile_id}.json"
        return file_path.exists()
