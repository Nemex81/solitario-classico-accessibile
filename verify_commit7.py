#!/usr/bin/env python
"""Standalone verification for Commit 7 - Config Loader."""

import sys
import json
from pathlib import Path
from tempfile import NamedTemporaryFile

sys.path.insert(0, '/home/runner/work/solitario-classico-accessibile/solitario-classico-accessibile')

from src.infrastructure.config.scoring_config_loader import ScoringConfigLoader
from src.domain.models.scoring import ScoringConfig

print("=" * 70)
print("VERIFICA COMMIT 7: Config JSON + Loader")
print("=" * 70)

# Test 1: Load from default path
print("\n✓ Test 1: Load from default path...")
try:
    config = ScoringConfigLoader.load()
    assert config.version == "2.0.0", f"Expected version 2.0.0, got {config.version}"
    assert config.victory_bonus_base == 400, f"Expected 400, got {config.victory_bonus_base}"
    assert config.time_bonus_max_timer_off == 1200, f"Expected 1200, got {config.time_bonus_max_timer_off}"
    print(f"  ✓ Loaded config version {config.version}")
    print(f"  ✓ Victory bonus base: {config.victory_bonus_base}")
    print(f"  ✓ Time bonus max: {config.time_bonus_max_timer_off}")
except Exception as e:
    print(f"  ✗ ERROR: {e}")
    sys.exit(1)

# Test 2: Fallback to defaults
print("\n✓ Test 2: Fallback when file missing...")
try:
    nonexistent = Path("/tmp/nonexistent_12345.json")
    config = ScoringConfigLoader.load(nonexistent)
    assert config.version == "2.0.0"
    assert config.victory_bonus_base == 400
    print("  ✓ Fallback to defaults successful")
except Exception as e:
    print(f"  ✗ ERROR: {e}")
    sys.exit(1)

# Test 3: Malformed JSON raises error
print("\n✓ Test 3: Malformed JSON raises ValueError...")
try:
    with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("{invalid json")
        temp_path = Path(f.name)
    
    try:
        config = ScoringConfigLoader.load(temp_path)
        print("  ✗ ERROR: Should have raised ValueError")
        sys.exit(1)
    except ValueError as e:
        print(f"  ✓ Correctly raised ValueError: {str(e)[:60]}...")
    finally:
        temp_path.unlink()
except Exception as e:
    print(f"  ✗ ERROR: {e}")
    sys.exit(1)

# Test 4: Invalid version raises error
print("\n✓ Test 4: Invalid version raises ValueError...")
try:
    invalid_config = {
        "version": "1.0.0",
        "victory_bonus_base": 400,
        "difficulty_multipliers": {"1": 1.0, "2": 1.2, "3": 1.4, "4": 1.8, "5": 2.2},
        "victory_weights": {"time": 0.35, "moves": 0.35, "recycles": 0.30},
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
        json.dump(invalid_config, f)
        temp_path = Path(f.name)
    
    try:
        config = ScoringConfigLoader.load(temp_path)
        print("  ✗ ERROR: Should have raised ValueError")
        sys.exit(1)
    except ValueError as e:
        print(f"  ✓ Correctly raised ValueError: {str(e)[:60]}...")
    finally:
        temp_path.unlink()
except Exception as e:
    print(f"  ✗ ERROR: {e}")
    sys.exit(1)

# Test 5: Type conversions
print("\n✓ Test 5: Type conversions work correctly...")
try:
    json_data = {
        "version": "2.0.0",
        "difficulty_multipliers": {"1": 1.0, "2": 1.2, "3": 1.4, "4": 1.8, "5": 2.2},
        "draw_count_bonuses": {
            "1": {"low": 0, "high": 0},
            "2": {"low": 100, "high": 50},
            "3": {"low": 200, "high": 100}
        },
        "stock_draw_thresholds": [20, 40],
        "stock_draw_penalties": [0, -1, -2],
        "recycle_penalties": [0, 0, -10, -20, -35, -55, -80],
        "victory_bonus_base": 400,
        "victory_weights": {"time": 0.35, "moves": 0.35, "recycles": 0.30},
        "deck_type_bonuses": {"neapolitan": 100, "french": 50},
        "event_points": {
            "waste_to_foundation": 10,
            "tableau_to_foundation": 10,
            "card_revealed": 5,
            "foundation_to_tableau": -15
        }
    }
    
    config = ScoringConfigLoader._parse_and_validate(json_data)
    
    # Check type conversions
    assert isinstance(config.difficulty_multipliers[1], float)
    assert isinstance(config.stock_draw_thresholds, tuple)
    assert isinstance(config.recycle_penalties, tuple)
    assert config.difficulty_multipliers[1] == 1.0
    assert config.stock_draw_thresholds == (20, 40)
    assert len(config.recycle_penalties) == 7
    
    print("  ✓ Type conversions successful")
    print("  ✓ difficulty_multipliers: string keys → int keys")
    print("  ✓ Arrays → tuples")
except Exception as e:
    print(f"  ✗ ERROR: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ COMMIT 7 VERIFICATO: Tutti i test passano!")
print("=" * 70)
