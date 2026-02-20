"""Unit tests for ScoreStorage.

Tests JSON-based persistent storage for:
- Saving scores
- Loading scores
- Querying best scores
- Calculating statistics
- Error handling
"""

import pytest
import json
import tempfile
from pathlib import Path
from src.infrastructure.storage.score_storage import ScoreStorage
from src.domain.models.scoring import FinalScore


@pytest.fixture
def temp_storage_path(tmp_path):
    """Create temporary storage path for testing."""
    return str(tmp_path / "test_scores.json")


@pytest.fixture
def storage(temp_storage_path):
    """Create ScoreStorage instance with temporary path."""
    return ScoreStorage(temp_storage_path)


@pytest.fixture
def sample_score():
    """Create a sample FinalScore for testing."""
    return FinalScore(
        base_score=85,
        deck_bonus=150,
        draw_bonus=100,
        difficulty_multiplier=2.0,
        time_bonus=345,
        victory_bonus=500,
        total_score=1015,
        is_victory=True,
        elapsed_seconds=180.5,
        difficulty_level=4,
        deck_type="french",
        draw_count=2,
        recycle_count=1,
        move_count=42
    )


class TestSaveScore:
    """Tests for saving scores."""
    
    def test_save_score_creates_file(self, storage, sample_score, temp_storage_path):
        """Test that saving creates the JSON file."""
        assert not Path(temp_storage_path).exists()
        
        result = storage.save_score(sample_score)
        
        assert result is True
        assert Path(temp_storage_path).exists()
    
    def test_save_score_creates_directory(self, tmp_path, sample_score):
        """Test that saving creates parent directory if needed."""
        storage_path = tmp_path / "subdir" / "scores.json"
        storage = ScoreStorage(str(storage_path))
        
        result = storage.save_score(sample_score)
        
        assert result is True
        assert storage_path.exists()
        assert storage_path.parent.exists()
    
    def test_save_score_appends_to_existing(self, storage, temp_storage_path):
        """Test that saving appends to existing scores."""
        # Save first score
        score1 = FinalScore(10, 0, 0, 1.0, 0, 0, 10, False, 60.0, 1, "french", 1, 0, 10)
        storage.save_score(score1)
        
        # Save second score
        score2 = FinalScore(20, 0, 0, 1.0, 0, 0, 20, False, 90.0, 1, "french", 1, 0, 15)
        storage.save_score(score2)
        
        # Load and verify
        scores = storage.load_all_scores()
        assert len(scores) == 2
        assert scores[0]['total_score'] == 10
        assert scores[1]['total_score'] == 20
    
    def test_save_score_keeps_only_last_100(self, storage):
        """Test that storage keeps only last 100 scores (LRU)."""
        # Save 105 scores
        for i in range(105):
            score = FinalScore(i, 0, 0, 1.0, 0, 0, i, False, 60.0, 1, "french", 1, 0, 10)
            storage.save_score(score)
        
        # Load and verify only 100 remain
        scores = storage.load_all_scores()
        assert len(scores) == 100
        # Should have scores 5-104 (oldest 5 dropped)
        assert scores[0]['total_score'] == 5
        assert scores[-1]['total_score'] == 104
    
    def test_save_score_adds_timestamp(self, storage, sample_score):
        """Test that save adds saved_at timestamp."""
        storage.save_score(sample_score)
        
        scores = storage.load_all_scores()
        assert len(scores) == 1
        assert 'saved_at' in scores[0]
        # Verify it's a valid ISO timestamp
        from datetime import datetime
        datetime.fromisoformat(scores[0]['saved_at'])
    
    def test_save_score_uses_utf8(self, storage, temp_storage_path):
        """Test that JSON is saved with UTF-8 encoding."""
        score = FinalScore(10, 0, 0, 1.0, 0, 0, 10, False, 60.0, 1, "french", 1, 0, 10)
        storage.save_score(score)
        
        # Read file directly and check encoding
        with open(temp_storage_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Should be valid JSON with Italian characters
            data = json.loads(content)
            assert isinstance(data, list)


class TestLoadScores:
    """Tests for loading scores."""
    
    def test_load_all_scores_empty_file(self, storage):
        """Test loading when file doesn't exist."""
        scores = storage.load_all_scores()
        assert scores == []
    
    def test_load_all_scores_returns_list(self, storage, sample_score):
        """Test that load returns a list."""
        storage.save_score(sample_score)
        
        scores = storage.load_all_scores()
        assert isinstance(scores, list)
        assert len(scores) == 1
    
    def test_load_all_scores_handles_corrupt_json(self, storage, temp_storage_path):
        """Test loading handles corrupt JSON gracefully."""
        # Write invalid JSON
        Path(temp_storage_path).write_text("{ invalid json }", encoding='utf-8')
        
        scores = storage.load_all_scores()
        assert scores == []
    
    def test_load_all_scores_handles_non_list_json(self, storage, temp_storage_path):
        """Test loading handles non-list JSON (dict instead of list)."""
        # Write dict instead of list
        Path(temp_storage_path).write_text('{"key": "value"}', encoding='utf-8')
        
        scores = storage.load_all_scores()
        assert scores == []


class TestBestScore:
    """Tests for querying best score."""
    
    def test_get_best_score_no_scores(self, storage):
        """Test getting best score when no scores exist."""
        best = storage.get_best_score()
        assert best is None
    
    def test_get_best_score_returns_highest(self, storage):
        """Test that best score returns highest total_score."""
        # Save 3 scores
        score1 = FinalScore(10, 0, 0, 1.0, 0, 0, 10, False, 60.0, 1, "french", 1, 0, 10)
        score2 = FinalScore(50, 0, 0, 1.0, 0, 0, 50, False, 90.0, 1, "french", 1, 0, 20)
        score3 = FinalScore(30, 0, 0, 1.0, 0, 0, 30, False, 120.0, 1, "french", 1, 0, 15)
        
        storage.save_score(score1)
        storage.save_score(score2)
        storage.save_score(score3)
        
        best = storage.get_best_score()
        assert best['total_score'] == 50
    
    def test_get_best_score_filter_by_deck_type(self, storage):
        """Test filtering best score by deck type."""
        # Save scores with different deck types
        french_score = FinalScore(100, 0, 0, 1.0, 0, 0, 100, False, 60.0, 1, "french", 1, 0, 10)
        neapolitan_score = FinalScore(80, 0, 0, 1.0, 0, 0, 80, False, 60.0, 1, "neapolitan", 1, 0, 10)
        
        storage.save_score(french_score)
        storage.save_score(neapolitan_score)
        
        best_french = storage.get_best_score(deck_type="french")
        best_neapolitan = storage.get_best_score(deck_type="neapolitan")
        
        assert best_french['total_score'] == 100
        assert best_neapolitan['total_score'] == 80
    
    def test_get_best_score_filter_by_difficulty(self, storage):
        """Test filtering best score by difficulty level."""
        # Save scores with different difficulties
        easy_score = FinalScore(50, 0, 0, 1.0, 0, 0, 50, False, 60.0, 1, "french", 1, 0, 10)
        hard_score = FinalScore(80, 0, 0, 1.0, 0, 0, 80, False, 60.0, 4, "french", 1, 0, 10)
        
        storage.save_score(easy_score)
        storage.save_score(hard_score)
        
        best_easy = storage.get_best_score(difficulty_level=1)
        best_hard = storage.get_best_score(difficulty_level=4)
        
        assert best_easy['total_score'] == 50
        assert best_hard['total_score'] == 80
    
    def test_get_best_score_combined_filters(self, storage):
        """Test best score with multiple filters."""
        # Save various scores
        storage.save_score(FinalScore(100, 0, 0, 1.0, 0, 0, 100, False, 60.0, 1, "french", 1, 0, 10))
        storage.save_score(FinalScore(150, 0, 0, 1.0, 0, 0, 150, False, 60.0, 4, "french", 1, 0, 10))
        storage.save_score(FinalScore(120, 0, 0, 1.0, 0, 0, 120, False, 60.0, 4, "neapolitan", 1, 0, 10))
        
        best = storage.get_best_score(deck_type="french", difficulty_level=4)
        assert best['total_score'] == 150
    
    def test_get_best_score_no_matches(self, storage):
        """Test best score returns None when no scores match filters."""
        score = FinalScore(50, 0, 0, 1.0, 0, 0, 50, False, 60.0, 1, "french", 1, 0, 10)
        storage.save_score(score)
        
        best = storage.get_best_score(deck_type="neapolitan", difficulty_level=5)
        assert best is None


class TestStatistics:
    """Tests for calculating statistics."""
    
    def test_get_statistics_empty(self, storage):
        """Test statistics when no scores exist."""
        stats = storage.get_statistics()
        
        assert stats['total_games'] == 0
        assert stats['total_wins'] == 0
        assert stats['win_rate'] == 0.0
        assert stats['average_score'] == 0.0
        assert stats['best_score'] == 0
        assert stats['average_time'] == 0.0
    
    def test_get_statistics_calculates_correctly(self, storage):
        """Test that statistics are calculated correctly."""
        # Save 5 scores: 3 wins, 2 losses
        storage.save_score(FinalScore(100, 0, 0, 1.0, 0, 500, 600, True, 120.0, 1, "french", 1, 0, 20))
        storage.save_score(FinalScore(50, 0, 0, 1.0, 0, 0, 50, False, 180.0, 1, "french", 1, 0, 30))
        storage.save_score(FinalScore(200, 0, 0, 1.0, 0, 500, 700, True, 150.0, 1, "french", 1, 0, 25))
        storage.save_score(FinalScore(30, 0, 0, 1.0, 0, 0, 30, False, 90.0, 1, "french", 1, 0, 15))
        storage.save_score(FinalScore(150, 0, 0, 1.0, 0, 500, 650, True, 200.0, 1, "french", 1, 0, 35))
        
        stats = storage.get_statistics()
        
        assert stats['total_games'] == 5
        assert stats['total_wins'] == 3
        assert stats['win_rate'] == 60.0
        assert stats['average_score'] == 406.0  # (600+50+700+30+650)/5
        assert stats['best_score'] == 700
        assert stats['average_time'] == 148.0  # (120+180+150+90+200)/5
    
    def test_get_statistics_rounds_values(self, storage):
        """Test that statistics are rounded properly."""
        # Save 3 scores with values that don't divide evenly
        storage.save_score(FinalScore(33, 0, 0, 1.0, 0, 0, 33, False, 100.3, 1, "french", 1, 0, 10))
        storage.save_score(FinalScore(34, 0, 0, 1.0, 0, 0, 34, False, 100.4, 1, "french", 1, 0, 10))
        storage.save_score(FinalScore(35, 0, 0, 1.0, 0, 0, 35, True, 100.5, 1, "french", 1, 0, 10))
        
        stats = storage.get_statistics()
        
        # Check that values are rounded to 1 decimal place
        assert stats['win_rate'] == 33.3
        assert stats['average_score'] == 34.0
        assert stats['average_time'] == 100.4


class TestClearScores:
    """Tests for clearing scores."""
    
    def test_clear_all_scores(self, storage, sample_score):
        """Test clearing all scores."""
        # Save some scores
        storage.save_score(sample_score)
        storage.save_score(sample_score)
        
        assert len(storage.load_all_scores()) == 2
        
        # Clear
        result = storage.clear_all_scores()
        
        assert result is True
        assert len(storage.load_all_scores()) == 0
    
    def test_clear_all_scores_when_empty(self, storage):
        """Test clearing when no scores exist."""
        result = storage.clear_all_scores()
        assert result is True
