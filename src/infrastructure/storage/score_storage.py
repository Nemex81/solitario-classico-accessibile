"""Score storage for persistent score history and statistics.

Provides JSON-based storage for:
- Saving final scores
- Loading score history
- Querying best scores
- Calculating statistics

Storage location: ~/.solitario/scores.json
Maximum scores kept: 100 (LRU)
"""

import json
import os
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional, Any

from src.domain.models.scoring import FinalScore
from src.infrastructure.logging import game_logger as log


class ScoreStorage:
    """Persistent storage for game scores.
    
    Stores scores in JSON format with UTF-8 encoding.
    Automatically manages storage directory and file creation.
    Keeps only the last 100 scores (LRU policy).
    
    Attributes:
        storage_path: Path to JSON file (default: ~/.solitario/scores.json)
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize score storage.
        
        Args:
            storage_path: Custom storage path (optional).
                         Defaults to ~/.solitario/scores.json
        """
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            # Default: ~/.solitario/scores.json
            home = Path.home()
            self.storage_path = home / ".solitario" / "scores.json"
        
        # Ensure directory exists
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
    
    def save_score(self, final_score: FinalScore) -> bool:
        """Save a final score to storage.
        
        Adds timestamp and saves to JSON file.
        Keeps only last 100 scores (LRU).
        
        Args:
            final_score: FinalScore to save
            
        Returns:
            True if saved successfully, False otherwise
            
        Example:
            >>> storage = ScoreStorage()
            >>> storage.save_score(final_score)
            True
        """
        try:
            # Convert to dict
            score_dict = asdict(final_score)
            
            # Add save timestamp
            score_dict['saved_at'] = datetime.now(timezone.utc).isoformat()
            
            # Load existing scores
            existing_scores = self.load_all_scores()
            
            # Append new score
            existing_scores.append(score_dict)
            
            # Keep only last 100 scores (LRU policy)
            if len(existing_scores) > 100:
                existing_scores = existing_scores[-100:]
            
            # Save to file
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(existing_scores, f, ensure_ascii=False, indent=2)
            
            # Log successful save
            log.info_query_requested(
                "score_save",
                f"Statistics saved to {self.storage_path}"
            )
            
            return True
        
        except Exception as e:
            # Log error
            log.error_occurred(
                "ScoreStorage",
                f"Failed to save: {self.storage_path}",
                e
            )
            return False
    
    def load_all_scores(self) -> List[Dict[str, Any]]:
        """Load all scores from storage.
        
        Returns:
            List of score dictionaries, empty list if file doesn't exist
            
        Example:
            >>> storage = ScoreStorage()
            >>> scores = storage.load_all_scores()
            >>> len(scores)
            42
        """
        try:
            if not self.storage_path.exists():
                # Log file not found warning
                log.warning_issued(
                    "ScoreStorage",
                    f"File not found: {self.storage_path}, returning empty list"
                )
                return []
            
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                scores = json.load(f)
            
            # Log successful load
            log.info_query_requested(
                "score_load",
                f"Statistics loaded from {self.storage_path}"
            )
            
            return scores if isinstance(scores, list) else []
        
        except json.JSONDecodeError as e:
            # Corrupt JSON - log error and return empty list
            log.error_occurred(
                "ScoreStorage",
                f"Corrupted file: {self.storage_path}",
                e
            )
            return []
        
        except Exception as e:
            # Other errors - log and return empty list
            log.error_occurred(
                "ScoreStorage",
                f"Unexpected error loading {self.storage_path}",
                e
            )
            return []
    
    def get_best_score(
        self,
        deck_type: Optional[str] = None,
        difficulty_level: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Get best score with optional filters.
        
        Returns the score with the highest total_score that matches
        the given filters.
        
        Args:
            deck_type: Filter by deck type ("french" or "neapolitan")
            difficulty_level: Filter by difficulty level (1-5)
            
        Returns:
            Dict with best score, or None if no scores match
            
        Example:
            >>> storage = ScoreStorage()
            >>> best = storage.get_best_score(deck_type="french", difficulty_level=4)
            >>> best['total_score']
            1250
        """
        scores = self.load_all_scores()
        
        if not scores:
            return None
        
        # Apply filters
        filtered_scores = scores
        
        if deck_type:
            filtered_scores = [
                s for s in filtered_scores
                if s.get('deck_type') == deck_type
            ]
        
        if difficulty_level is not None:
            filtered_scores = [
                s for s in filtered_scores
                if s.get('difficulty_level') == difficulty_level
            ]
        
        if not filtered_scores:
            return None
        
        # Return score with highest total_score
        return max(filtered_scores, key=lambda s: s.get('total_score', 0))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Calculate statistics from all scores.
        
        Returns:
            Dict with statistics:
            - total_games: Total games played
            - total_wins: Total victories
            - win_rate: Percentage of wins (0-100)
            - average_score: Average total_score
            - best_score: Highest total_score
            - average_time: Average elapsed_seconds
            
        Example:
            >>> storage = ScoreStorage()
            >>> stats = storage.get_statistics()
            >>> stats['win_rate']
            65.5
        """
        scores = self.load_all_scores()
        
        if not scores:
            return {
                'total_games': 0,
                'total_wins': 0,
                'win_rate': 0.0,
                'average_score': 0.0,
                'best_score': 0,
                'average_time': 0.0
            }
        
        total_games = len(scores)
        total_wins = sum(1 for s in scores if s.get('is_victory', False))
        win_rate = (total_wins / total_games * 100) if total_games > 0 else 0.0
        
        total_scores = sum(s.get('total_score', 0) for s in scores)
        average_score = total_scores / total_games if total_games > 0 else 0.0
        
        best_score = max(s.get('total_score', 0) for s in scores)
        
        total_time = sum(s.get('elapsed_seconds', 0) for s in scores)
        average_time = total_time / total_games if total_games > 0 else 0.0
        
        return {
            'total_games': total_games,
            'total_wins': total_wins,
            'win_rate': round(win_rate, 1),
            'average_score': round(average_score, 1),
            'best_score': best_score,
            'average_time': round(average_time, 1)
        }
    
    def clear_all_scores(self) -> bool:
        """Clear all scores from storage.
        
        Used for testing or resetting statistics.
        
        Returns:
            True if cleared successfully
        """
        try:
            if self.storage_path.exists():
                self.storage_path.unlink()
            return True
        except Exception as e:
            print(f"Error clearing scores: {e}")
            return False
