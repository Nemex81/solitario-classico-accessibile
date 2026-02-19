# Archived Legacy Tests

**Archived**: 2026-02-19 (v3.2.0 Test Modernization)  
**Reason**: Old `scr` package structure (replaced by `src` Clean Architecture)  
**Coverage**: Functionality covered by `tests/integration/test_profile_game_integration.py`

## Files

- `test_distribuisci_carte_deck_switching.py` - Dynamic card distribution tests (covered by integration tests)
- `test_game_engine_f3_f5.py` - Timer and shuffle toggle tests (requires pygame, obsolete API)
- `test_king_to_empty_base_pile.py` - King placement tests (covered by domain rules tests)

## Why Archived

These tests reference the legacy `scr` package structure that was replaced during the Clean Architecture migration. They use deprecated class names:
- `TavoloSolitario` → replaced by `GameTable`
- `EngineSolitario` → replaced by `GameEngine`
- Legacy method names that no longer exist in current API

The functionality tested here is now covered by:
- `tests/integration/test_profile_game_integration.py` - Session recording and game end scenarios
- `tests/integration/test_game_engine_flow.py` - Game engine integration tests
- `tests/unit/domain/rules/` - Domain rule tests for card placement logic

## Migration Notes

If these tests need to be resurrected:
1. Update imports: `from scr.*` → `from src.*`
2. Update class names: `TavoloSolitario` → `GameTable`, `EngineSolitario` → `GameEngine`
3. Update method names to match current API (see `src/domain/models/table.py`)
4. Remove pygame dependencies or mark with `@pytest.mark.gui`
