"""Unit tests for ScoringConfigLoader."""

import json
import pytest
from pathlib import Path
from tempfile import NamedTemporaryFile

from src.infrastructure.config.scoring_config_loader import ScoringConfigLoader
from src.domain.models.scoring import ScoringConfig


class TestScoringConfigLoader:
    """Tests for config loader with JSON externalization."""
    
    def test_load_valid_json_from_default_path(self):
        """Test loading config from default JSON file."""
        # Load from default path (config/scoring_config.json)
        config = ScoringConfigLoader.load()
        
        # Verify it's a valid v2.0 config
        assert isinstance(config, ScoringConfig)
        assert config.version == "2.0.0"
        assert config.victory_bonus_base == 400
        assert config.time_bonus_max_timer_off == 1200
        assert config.difficulty_multipliers[1] == 1.0
        assert config.difficulty_multipliers[5] == 2.2
        assert config.deck_type_bonuses["neapolitan"] == 100
        assert config.deck_type_bonuses["french"] == 50
    
    def test_load_missing_file_fallback_to_defaults(self):
        """Test fallback to hardcoded defaults when file doesn't exist."""
        # Try to load from non-existent path
        nonexistent_path = Path("/tmp/nonexistent_config_12345.json")
        config = ScoringConfigLoader.load(nonexistent_path)
        
        # Should return default config
        assert isinstance(config, ScoringConfig)
        assert config.version == "2.0.0"
        assert config.victory_bonus_base == 400
        
        # Verify it matches fallback_default()
        fallback = ScoringConfigLoader.fallback_default()
        assert config.version == fallback.version
        assert config.victory_bonus_base == fallback.victory_bonus_base
    
    def test_load_malformed_json_raises_value_error(self):
        """Test that malformed JSON raises ValueError."""
        # Create temporary file with malformed JSON
        with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{invalid json syntax}")
            temp_path = Path(f.name)
        
        try:
            # Should raise ValueError
            with pytest.raises(ValueError, match="Malformed JSON"):
                ScoringConfigLoader.load(temp_path)
        finally:
            # Cleanup
            temp_path.unlink()
    
    def test_load_invalid_version_raises_value_error(self):
        """Test that invalid version raises ValueError."""
        # Create config with invalid version
        invalid_config = {
            "version": "1.0.0",  # Invalid: must be 2.x
            "victory_bonus_base": 400
        }
        
        with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_config, f)
            temp_path = Path(f.name)
        
        try:
            # Should raise ValueError during validation
            with pytest.raises(ValueError, match="Invalid version"):
                ScoringConfigLoader.load(temp_path)
        finally:
            temp_path.unlink()
    
    def test_fallback_default_returns_valid_config(self):
        """Test that fallback_default() returns valid v2.0 config."""
        config = ScoringConfigLoader.fallback_default()
        
        assert isinstance(config, ScoringConfig)
        assert config.version == "2.0.0"
        assert config.victory_bonus_base == 400
        assert config.time_bonus_max_timer_off == 1200
        
        # Should pass validation
        assert config.difficulty_multipliers[1] == 1.0
        assert len(config.recycle_penalties) == 7
    
    def test_parse_and_validate_converts_types_correctly(self):
        """Test that _parse_and_validate handles type conversions."""
        # Create JSON data with string keys (as JSON requires)
        json_data = {
            "version": "2.0.0",
            "difficulty_multipliers": {
                "1": 1.0,
                "2": 1.2,
                "3": 1.4,
                "4": 1.8,
                "5": 2.2
            },
            "draw_count_bonuses": {
                "1": {"low": 0, "high": 0},
                "2": {"low": 100, "high": 50},
                "3": {"low": 200, "high": 100}
            },
            "stock_draw_thresholds": [20, 40],
            "stock_draw_penalties": [0, -1, -2],
            "recycle_penalties": [0, 0, -10, -20, -35, -55, -80],
            "victory_bonus_base": 400,
            "victory_weights": {
                "time": 0.35,
                "moves": 0.35,
                "recycles": 0.30
            },
            "deck_type_bonuses": {
                "neapolitan": 100,
                "french": 50
            },
            "event_points": {
                "waste_to_foundation": 10,
                "tableau_to_foundation": 10,
                "card_revealed": 5,
                "foundation_to_tableau": -15
            }
        }
        
        config = ScoringConfigLoader._parse_and_validate(json_data)
        
        # Verify type conversions
        assert isinstance(config.difficulty_multipliers[1], float)
        assert isinstance(config.draw_count_bonuses[2], dict)
        assert isinstance(config.stock_draw_thresholds, tuple)
        assert isinstance(config.recycle_penalties, tuple)
        
        # Verify values
        assert config.difficulty_multipliers[1] == 1.0
        assert config.draw_count_bonuses[2]["low"] == 100
        assert config.stock_draw_thresholds == (20, 40)
        assert len(config.recycle_penalties) == 7
    
    def test_load_custom_path(self):
        """Test loading config from custom path."""
        # Create temporary config with custom values
        custom_config = {
            "version": "2.0.0",
            "victory_bonus_base": 500,  # Custom value
            "difficulty_multipliers": {
                "1": 1.0, "2": 1.2, "3": 1.4, "4": 1.8, "5": 2.2
            },
            "victory_weights": {
                "time": 0.35, "moves": 0.35, "recycles": 0.30
            },
            "deck_type_bonuses": {"neapolitan": 100, "french": 50},
            "draw_count_bonuses": {
                "1": {"low": 0, "high": 0},
                "2": {"low": 100, "high": 50},
                "3": {"low": 200, "high": 100}
            },
            "stock_draw_thresholds": [20, 40],
            "stock_draw_penalties": [0, -1, -2],
            "recycle_penalties": [0, 0, -10, -20, -35, -55, -80]
        }
        
        with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(custom_config, f)
            temp_path = Path(f.name)
        
        try:
            config = ScoringConfigLoader.load(temp_path)
            
            # Should load custom value
            assert config.victory_bonus_base == 500
            assert config.version == "2.0.0"
        finally:
            temp_path.unlink()
