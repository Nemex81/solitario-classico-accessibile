"""Configuration loader for Scoring System v2.0.

Loads scoring configuration from external JSON file with fallback to hardcoded defaults.
Provides validation and type conversion for all config parameters.
"""

import json
from pathlib import Path
from typing import Dict, Optional

from src.domain.models.scoring import ScoringConfig, ScoreEventType


class ScoringConfigLoader:
    """Loader for scoring configuration with JSON externalization."""
    
    # Default config path (relative to project root)
    DEFAULT_CONFIG_PATH = Path("config/scoring_config.json")
    
    @classmethod
    def load(cls, path: Optional[Path] = None) -> ScoringConfig:
        """Load scoring configuration from JSON file with fallback.
        
        Args:
            path: Path to JSON config file. If None, uses DEFAULT_CONFIG_PATH.
            
        Returns:
            ScoringConfig instance loaded from JSON or fallback defaults
            
        Raises:
            ValueError: If JSON is malformed or validation fails
            
        Note:
            If file doesn't exist, falls back to hardcoded v2.0 defaults silently.
            This ensures robustness in case of missing config file.
        """
        if path is None:
            path = cls.DEFAULT_CONFIG_PATH
        
        # If file doesn't exist, use fallback
        if not path.exists():
            return cls.fallback_default()
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return cls._parse_and_validate(data)
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Malformed JSON in config file: {e}")
        except Exception as e:
            raise ValueError(f"Error loading config: {e}")
    
    @classmethod
    def fallback_default(cls) -> ScoringConfig:
        """Return hardcoded v2.0 default configuration.
        
        Returns:
            ScoringConfig with standard v2.0 values
            
        Note:
            This is the fallback when JSON file is missing or unreadable.
            Values must match ScoringConfig dataclass defaults.
        """
        return ScoringConfig()  # Uses dataclass defaults
    
    @classmethod
    def _parse_and_validate(cls, data: dict) -> ScoringConfig:
        """Parse JSON data and construct validated ScoringConfig.
        
        Args:
            data: Raw dictionary from JSON file
            
        Returns:
            Validated ScoringConfig instance
            
        Raises:
            ValueError: If data is invalid or validation fails
            
        Note:
            Handles type conversions:
            - JSON string keys → int keys for difficulty_multipliers
            - JSON string keys → int keys for draw_count_bonuses
            - JSON string keys → ScoreEventType enum for event_points
            - JSON arrays → tuples for thresholds/penalties
        """
        # Version check (required field)
        if "version" not in data:
            raise ValueError("Missing required field: version")
        
        version = data["version"]
        if not version.startswith("2."):
            raise ValueError(f"Invalid version '{version}', expected 2.x")
        
        # Convert event_points: string keys → ScoreEventType enum
        event_points_raw = data.get("event_points", {})
        event_points = {}
        for key, value in event_points_raw.items():
            # Convert snake_case JSON key to ScoreEventType enum
            enum_key = key.upper()  # waste_to_foundation → WASTE_TO_FOUNDATION
            try:
                event_type = ScoreEventType(enum_key.lower())  # Enum uses lowercase values
                event_points[event_type] = value
            except ValueError:
                # Skip unknown event types (forward compatibility)
                pass
        
        # Convert difficulty_multipliers: string keys → int keys
        difficulty_multipliers_raw = data.get("difficulty_multipliers", {})
        difficulty_multipliers = {
            int(k): float(v) for k, v in difficulty_multipliers_raw.items()
        }
        
        # Deck type bonuses (already correct type)
        deck_type_bonuses = data.get("deck_type_bonuses", {})
        
        # Convert draw_count_bonuses: string keys → int keys
        draw_count_bonuses_raw = data.get("draw_count_bonuses", {})
        draw_count_bonuses = {
            int(k): v for k, v in draw_count_bonuses_raw.items()
        }
        
        # Victory bonus parameters
        victory_bonus_base = data.get("victory_bonus_base", 400)
        victory_weights = data.get("victory_weights", {})
        
        # Stock draw penalties (arrays → tuples)
        stock_draw_thresholds = tuple(data.get("stock_draw_thresholds", [20, 40]))
        stock_draw_penalties = tuple(data.get("stock_draw_penalties", [0, -1, -2]))
        
        # Recycle penalties (array → tuple)
        recycle_penalties = tuple(data.get("recycle_penalties", [0, 0, -10, -20, -35, -55, -80]))
        
        # Time bonus parameters
        time_bonus_max_timer_off = data.get("time_bonus_max_timer_off", 1200)
        time_bonus_decay_per_minute = data.get("time_bonus_decay_per_minute", 40)
        time_bonus_max_timer_on = data.get("time_bonus_max_timer_on", 1000)
        overtime_penalty_per_minute = data.get("overtime_penalty_per_minute", -100)
        
        # Minimum score
        min_score = data.get("min_score", 0)
        
        # Construct and validate via ScoringConfig.__post_init__
        return ScoringConfig(
            version=version,
            event_points=event_points,
            difficulty_multipliers=difficulty_multipliers,
            deck_type_bonuses=deck_type_bonuses,
            draw_count_bonuses=draw_count_bonuses,
            victory_bonus_base=victory_bonus_base,
            victory_weights=victory_weights,
            stock_draw_thresholds=stock_draw_thresholds,
            stock_draw_penalties=stock_draw_penalties,
            recycle_penalties=recycle_penalties,
            time_bonus_max_timer_off=time_bonus_max_timer_off,
            time_bonus_decay_per_minute=time_bonus_decay_per_minute,
            time_bonus_max_timer_on=time_bonus_max_timer_on,
            overtime_penalty_per_minute=overtime_penalty_per_minute,
            min_score=min_score,
        )
