"""Domain models for profile and session management."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Any
import uuid

from src.domain.models.game_end import EndReason


@dataclass
class UserProfile:
    """Represents a player profile with persistent identity."""
    
    # Identity
    profile_id: str                     # UUID or "profile_000" for guest
    profile_name: str                   # Display name
    created_at: datetime
    last_played: datetime
    is_default: bool = False            # Auto-selected at startup
    is_guest: bool = False              # Special guest profile
    
    # Preferences (future, placeholder)
    preferred_difficulty: int = 3
    preferred_deck: str = "french"
    
    @classmethod
    def create_new(cls, name: str, is_guest: bool = False) -> "UserProfile":
        """Factory method for new profile creation."""
        profile_id = "profile_000" if is_guest else f"profile_{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow()
        
        return cls(
            profile_id=profile_id,
            profile_name=name,
            created_at=now,
            last_played=now,
            is_default=not is_guest,
            is_guest=is_guest
        )
    
    @classmethod
    def create_guest(cls) -> "UserProfile":
        """Create the special guest profile (fixed ID)."""
        return cls.create_new("Ospite", is_guest=True)
    
    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "profile_id": self.profile_id,
            "profile_name": self.profile_name,
            "created_at": self.created_at.isoformat(),
            "last_played": self.last_played.isoformat(),
            "is_default": self.is_default,
            "is_guest": self.is_guest,
            "preferred_difficulty": self.preferred_difficulty,
            "preferred_deck": self.preferred_deck
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "UserProfile":
        """Create from JSON dict."""
        data = data.copy()
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["last_played"] = datetime.fromisoformat(data["last_played"])
        return cls(**data)


@dataclass
class SessionOutcome:
    """Complete snapshot of a finished game session.
    
    Immutable once saved (append-only). Feeds aggregates and history.
    """
    
    # ========================================
    # IDENTIFICATION
    # ========================================
    session_id: str                     # UUID unique per session
    profile_id: str                     # Which profile owns this
    timestamp: datetime                 # When it ended (ISO 8601)
    
    # ========================================
    # OUTCOME (from Timer System v2.7.0)
    # ========================================
    end_reason: EndReason               # victory | abandon_* | timeout
    is_victory: bool                    # Shortcut for aggregate queries
    
    # ========================================
    # TIME (from Timer System v2.7.0)
    # ========================================
    elapsed_time: float                 # Total seconds
    timer_enabled: bool                 # Was timer active?
    timer_limit: int                    # Configured limit (seconds, 0=off)
    timer_mode: str                     # "STRICT" | "PERMISSIVE" | "OFF"
    timer_expired: bool                 # Did expiry occur?
    overtime_duration: float = 0.0      # Seconds beyond limit (0 if none)
    
    # ========================================
    # SCORING (from Scoring System v2.0)
    # ========================================
    scoring_enabled: bool = False       # Was scoring active?
    final_score: int = 0                # Total final score
    base_score: int = 0                 # Base score (moves/time)
    difficulty_multiplier: float = 1.0  # Difficulty multiplier
    deck_bonus: int = 0                 # Deck type bonus
    quality_multiplier: float = 1.0     # Victory quality (1.0-2.0)
    
    # ========================================
    # GAME CONFIGURATION
    # ========================================
    difficulty_level: int = 3           # 1-5
    deck_type: str = "french"           # "french" | "neapolitan"
    draw_count: int = 1                 # 1-3 cards drawn
    shuffle_mode: str = "invert"        # "invert" | "random"
    
    # ========================================
    # GAMEPLAY STATS (from GameService)
    # ========================================
    move_count: int = 0                 # Total moves
    draw_count_actions: int = 0         # Draw actions
    recycle_count: int = 0              # Deck recyclings
    foundation_cards: List[int] = field(default_factory=lambda: [0, 0, 0, 0])  # Per suit
    completed_suits: int = 0            # 0-4 suits completed
    
    # ========================================
    # METADATA
    # ========================================
    game_version: str = "2.7.0"         # App version
    notes: str = ""                      # User notes (future)
    
    @classmethod
    def create_new(cls, profile_id: str, **kwargs: Any) -> "SessionOutcome":  # type: ignore[misc]
        """Factory method for new session creation."""
        return cls(
            session_id=str(uuid.uuid4()),
            profile_id=profile_id,
            timestamp=datetime.utcnow(),
            **kwargs
        )
    
    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "session_id": self.session_id,
            "profile_id": self.profile_id,
            "timestamp": self.timestamp.isoformat(),
            "end_reason": self.end_reason.value,
            "is_victory": self.is_victory,
            "elapsed_time": self.elapsed_time,
            "timer_enabled": self.timer_enabled,
            "timer_limit": self.timer_limit,
            "timer_mode": self.timer_mode,
            "timer_expired": self.timer_expired,
            "overtime_duration": self.overtime_duration,
            "scoring_enabled": self.scoring_enabled,
            "final_score": self.final_score,
            "base_score": self.base_score,
            "difficulty_multiplier": self.difficulty_multiplier,
            "deck_bonus": self.deck_bonus,
            "quality_multiplier": self.quality_multiplier,
            "difficulty_level": self.difficulty_level,
            "deck_type": self.deck_type,
            "draw_count": self.draw_count,
            "shuffle_mode": self.shuffle_mode,
            "move_count": self.move_count,
            "draw_count_actions": self.draw_count_actions,
            "recycle_count": self.recycle_count,
            "foundation_cards": self.foundation_cards,
            "completed_suits": self.completed_suits,
            "game_version": self.game_version,
            "notes": self.notes
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SessionOutcome":
        """Create from JSON dict."""
        data = data.copy()
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        data["end_reason"] = EndReason(data["end_reason"])
        return cls(**data)
