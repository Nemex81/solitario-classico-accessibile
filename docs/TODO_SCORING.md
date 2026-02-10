# TODO: Scoring System Implementation v2.0.0

**Branch**: `refactoring-engine`  
**Related Documentation**: [IMPLEMENTATION_SCORING_SYSTEM.md](./IMPLEMENTATION_SCORING_SYSTEM.md)  
**Target Version**: v2.0.0  
**Estimated Effort**: 3.5 hours (Copilot) + 1.5 hours (review/testing)  
**Commits**: 8 atomic commits

---

## Phase 1: Domain Models - Scoring Data Structures

**Target Commit**: `feat(domain): Add scoring system models and configuration`

### Files to Create

- [ ] `src/domain/models/scoring.py`
  - [ ] Create `ScoreEventType` enum (7 event types)
  - [ ] Create `ScoringConfig` dataclass (frozen, with defaults)
  - [ ] Create `ScoreEvent` dataclass (frozen, with timestamp)
  - [ ] Create `ProvisionalScore` dataclass (frozen)
  - [ ] Create `FinalScore` dataclass (frozen, with `get_breakdown()` method)
  - [ ] Add complete docstrings for all classes
  - [ ] Add type hints for all attributes

### Testing

- [ ] `tests/unit/test_scoring_models.py`
  - [ ] Test `ScoringConfig` default values (10 tests)
  - [ ] Test dataclass immutability (FrozenInstanceError)
  - [ ] Test `FinalScore.get_breakdown()` formatting
  - [ ] Test enum value correctness
  - [ ] Test all default dictionaries (multipliers, bonuses)

### Acceptance Criteria

- [ ] All dataclasses are `frozen=True`
- [ ] All attributes have type hints
- [ ] `ScoringConfig` contains all 7 bonus/multiplier dicts
- [ ] `FinalScore.get_breakdown()` returns Italian TTS-friendly string
- [ ] All tests pass (minimum 10 tests)

**Commit when all checkboxes checked**

---

## Phase 2: Domain Service - Scoring Logic

**Target Commit**: `feat(domain): Implement ScoringService with event recording and calculations`

### Files to Create

- [ ] `src/domain/services/scoring_service.py`
  - [ ] Create `ScoringService` class
  - [ ] Implement `__init__(config)` with state initialization
  - [ ] Implement `record_event()` method
  - [ ] Implement `_calculate_event_points()` helper
  - [ ] Implement `calculate_provisional_score()` method
  - [ ] Implement `calculate_final_score()` method
  - [ ] Implement `_calculate_time_bonus()` with timer ON/OFF logic
  - [ ] Implement `get_base_score()` query
  - [ ] Implement `get_event_count()` query
  - [ ] Implement `get_recent_events(count)` query
  - [ ] Implement `reset()` method
  - [ ] Add complete docstrings with examples

### Testing

- [ ] `tests/unit/test_scoring_service.py`
  - [ ] Test `record_event()` for all event types (7 tests)
  - [ ] Test recycle penalty after 3rd recycle
  - [ ] Test time bonus formula (timer OFF)
  - [ ] Test time bonus formula (timer ON, various percentages)
  - [ ] Test provisional score calculation
  - [ ] Test final score calculation with victory bonus
  - [ ] Test `reset()` clears all state
  - [ ] Test `get_recent_events()` returns correct count
  - [ ] Test score never goes below 0 (min_score clamping)
  - [ ] Test difficulty multiplier application

### Acceptance Criteria

- [ ] All event types correctly award/deduct points
- [ ] Recycle penalty only applies after 3rd recycle
- [ ] Time bonus formula matches specification (sqrt for OFF, percentage for ON)
- [ ] Provisional and final scores differ only by victory bonus
- [ ] All calculations are pure (no side effects)
- [ ] All tests pass (minimum 20 tests)

**Commit when all checkboxes checked**

---

## Phase 3: GameSettings Extension - Options & Validation

**Target Commit**: `feat(domain): Extend GameSettings with draw_count, scoring toggle, and level 4-5 constraints`

### Files to Modify

- [ ] `src/domain/services/game_settings.py`
  - [ ] Add `draw_count: int = 1` attribute
  - [ ] Add `scoring_enabled: bool = True` attribute
  - [ ] Modify `cycle_difficulty()` to cycle 1→5 (not 1→3)
  - [ ] Add constraint auto-adjustment in `cycle_difficulty()`
  - [ ] Create `cycle_draw_count()` method (NEW option 3)
  - [ ] Create `toggle_scoring()` method (NEW option 7)
  - [ ] Create `validate_draw_count_for_level()` helper
  - [ ] Create `validate_timer_for_level()` helper
  - [ ] Create `validate_shuffle_for_level()` helper
  - [ ] Create `get_draw_count_display()` getter
  - [ ] Update `get_difficulty_display()` with level names (Facile...Maestro)
  - [ ] Create `get_scoring_display()` getter
  - [ ] Update all docstrings

### Testing

- [ ] `tests/unit/test_game_settings_validation.py`
  - [ ] Test `cycle_difficulty()` cycles 1→2→3→4→5→1
  - [ ] Test level 4 enforces timer ≥30min
  - [ ] Test level 5 enforces timer 15-30min range
  - [ ] Test level 4 enforces draw_count ≥2
  - [ ] Test level 5 enforces draw_count=3 (fixed)
  - [ ] Test level 4-5 locks shuffle to inverted
  - [ ] Test `cycle_draw_count()` cycles 1→2→3→1
  - [ ] Test `toggle_scoring()` toggles True↔False
  - [ ] Test validation returns correct messages
  - [ ] Test cycling difficulty auto-adjusts other settings
  - [ ] Test cannot modify during game (validate_not_running)

### Acceptance Criteria

- [ ] Difficulty now has 5 levels (was 3)
- [ ] Level 4 constraints: timer ≥30min, draw ≥2, shuffle locked
- [ ] Level 5 constraints: timer 15-30min, draw=3, shuffle locked
- [ ] All constraint violations auto-adjust with clear messages
- [ ] `draw_count` is independent of difficulty at levels 1-3
- [ ] `scoring_enabled` can be toggled at any time (when not running)
- [ ] All tests pass (minimum 15 tests)

**Commit when all checkboxes checked**

---

## Phase 4: GameService Integration - Event Recording

**Target Commit**: `feat(domain): Integrate ScoringService into GameService for event recording`

### Files to Modify

- [ ] `src/domain/services/game_service.py`
  - [ ] Add `scoring: Optional[ScoringService]` parameter to `__init__()`
  - [ ] Store `self.scoring = scoring`
  - [ ] Modify `move_card()` to record scoring events
    - [ ] Check `if self.scoring:` before recording
    - [ ] Record `WASTE_TO_FOUNDATION` when source=waste, target=foundation
    - [ ] Record `TABLEAU_TO_FOUNDATION` when source=tableau, target=foundation
    - [ ] Record `CARD_REVEALED` when top card uncovered in source
  - [ ] Modify `recycle_waste()` to record `RECYCLE_WASTE` event
  - [ ] Modify `reset_game()` to call `self.scoring.reset()` if present
  - [ ] Update all docstrings

### Testing

- [ ] `tests/integration/test_scoring_integration.py`
  - [ ] Test move waste→foundation records +10 points
  - [ ] Test move tableau→foundation records +10 points
  - [ ] Test revealed card records +5 points
  - [ ] Test recycle after 3rd records -20 points
  - [ ] Test scoring=None doesn't crash (optional dependency)
  - [ ] Test `reset_game()` clears scoring events
  - [ ] Test multiple moves accumulate score correctly
  - [ ] Test base_score matches sum of event points

### Acceptance Criteria

- [ ] All scoring calls are guarded with `if self.scoring:`
- [ ] Events recorded with correct context (card names, pile names)
- [ ] No crashes when `scoring=None` (free-play mode)
- [ ] Event points match specification (±0 tolerance)
- [ ] `reset_game()` resets scoring state
- [ ] All tests pass (minimum 12 tests)

**Commit when all checkboxes checked**

---

## Phase 5: Application Controllers - Options & Commands

**Target Commit**: `feat(application): Add draw_count and scoring toggle options to controllers`

### Files to Modify

- [ ] `src/application/options_controller.py`
  - [ ] Update `option_items` list to 7 items (add "Carte Pescate", "Sistema Punti")
  - [ ] Modify `modify_current_option()` to handle index 2 (draw_count)
  - [ ] Modify `modify_current_option()` to handle index 6 (scoring_enabled)
  - [ ] Update `get_current_option_value()` for new options
  - [ ] Update all docstrings

- [ ] `src/application/gameplay_controller.py` (if exists, or create methods in GameEngine)
  - [ ] Create `show_current_score()` method (command: P key)
    - [ ] Check `scoring_enabled`, announce disabled if False
    - [ ] Calculate `provisional_score`
    - [ ] Format with `ScoreFormatter.format_provisional_score()`
    - [ ] Announce via TTS
  - [ ] Create `show_score_breakdown()` method (command: Shift+P key)
    - [ ] Check `scoring_enabled`, announce disabled if False
    - [ ] Get last 5 events from `scoring.get_recent_events(5)`
    - [ ] Format each event with `ScoreFormatter.format_score_event()`
    - [ ] Announce via TTS

### Testing

- [ ] `tests/unit/test_options_controller.py`
  - [ ] Test option 2 (draw_count) cycles 1→2→3→1
  - [ ] Test option 6 (scoring) toggles True↔False
  - [ ] Test option navigation (previous/next)
  - [ ] Test modify announces correct messages

- [ ] `tests/unit/test_gameplay_controller.py`
  - [ ] Test `show_current_score()` with scoring enabled
  - [ ] Test `show_current_score()` with scoring disabled
  - [ ] Test `show_score_breakdown()` with events
  - [ ] Test `show_score_breakdown()` with no events

### Acceptance Criteria

- [ ] Options menu now has 7 items (was 6)
- [ ] F3 key cycles draw_count at option index 2
- [ ] F7 key toggles scoring at option index 6 (new position)
- [ ] P key shows current score with breakdown
- [ ] Shift+P shows last 5 scoring events
- [ ] Scoring disabled message clear and informative
- [ ] All tests pass (minimum 8 tests)

**Commit when all checkboxes checked**

---

## Phase 6: Presentation Formatters - TTS Messages

**Target Commit**: `feat(presentation): Add ScoreFormatter for TTS-optimized scoring messages`

### Files to Create

- [ ] `src/presentation/formatters/score_formatter.py`
  - [ ] Create `ScoreFormatter` class (all static methods)
  - [ ] Implement `format_provisional_score(score)` static method
  - [ ] Implement `format_final_score(score)` static method
  - [ ] Implement `format_score_event(event)` static method
  - [ ] Implement `format_scoring_disabled()` static method
  - [ ] Implement `format_best_score(score_dict)` static method
  - [ ] Add Italian event name translations dict
  - [ ] Ensure all messages are TTS-optimized (no symbols, clear phrasing)
  - [ ] Add complete docstrings

### Testing

- [ ] `tests/unit/test_score_formatter.py`
  - [ ] Test `format_provisional_score()` includes all components
  - [ ] Test `format_final_score()` includes victory announcement
  - [ ] Test `format_final_score()` handles no bonuses gracefully
  - [ ] Test `format_score_event()` translates all event types
  - [ ] Test `format_scoring_disabled()` returns correct message
  - [ ] Test `format_best_score()` formats correctly
  - [ ] Test all messages are in Italian
  - [ ] Test no special characters in TTS output

### Acceptance Criteria

- [ ] All methods are `@staticmethod`
- [ ] All messages in Italian (no English)
- [ ] Messages follow TTS best practices (no symbols, spell out numbers)
- [ ] Provisional score includes base + multipliers + bonuses
- [ ] Final score includes victory status + complete breakdown
- [ ] Event names translated (e.g., "waste_to_foundation" → "Scarto a fondazione")
- [ ] All tests pass (minimum 8 tests)

**Commit when all checkboxes checked**

---

## Phase 7: Infrastructure Storage - Persistent Statistics

**Target Commit**: `feat(infrastructure): Add ScoreStorage for persistent statistics with JSON backend`

### Files to Create

- [ ] `src/infrastructure/storage/score_storage.py`
  - [ ] Create `ScoreStorage` class
  - [ ] Implement `__init__(storage_path)` with default path `~/.solitario/scores.json`
  - [ ] Implement `save_score(final_score)` method
    - [ ] Convert FinalScore to dict with `asdict()`
    - [ ] Add `saved_at` timestamp
    - [ ] Load existing scores
    - [ ] Append new score
    - [ ] Keep only last 100 scores
    - [ ] Save to JSON with UTF-8 encoding
  - [ ] Implement `load_all_scores()` method
    - [ ] Handle file not found gracefully
    - [ ] Handle JSON decode errors gracefully
  - [ ] Implement `get_best_score(deck_type, difficulty)` method
    - [ ] Apply optional filters
    - [ ] Return dict with highest `total_score`
  - [ ] Implement `get_statistics()` method
    - [ ] Calculate total_games, total_wins, average_score, best_score, win_rate
  - [ ] Add complete docstrings

### Testing

- [ ] `tests/unit/test_score_storage.py`
  - [ ] Test `save_score()` creates file if not exists
  - [ ] Test `save_score()` appends to existing file
  - [ ] Test `save_score()` keeps only last 100 scores
  - [ ] Test `load_all_scores()` handles missing file
  - [ ] Test `load_all_scores()` handles corrupt JSON
  - [ ] Test `get_best_score()` with filters (deck, difficulty)
  - [ ] Test `get_best_score()` returns None if no scores
  - [ ] Test `get_statistics()` calculates correctly
  - [ ] Test `get_statistics()` handles empty file
  - [ ] Test JSON encoding with Italian characters

### Acceptance Criteria

- [ ] Storage path defaults to `~/.solitario/scores.json`
- [ ] Directory created automatically if missing
- [ ] JSON format with UTF-8 encoding (`ensure_ascii=False`)
- [ ] Graceful error handling (no crashes on corrupt files)
- [ ] Keeps only last 100 scores (LRU)
- [ ] All filters work correctly (deck_type, difficulty_level)
- [ ] Statistics calculations accurate (verified manually)
- [ ] All tests pass (minimum 10 tests)

**Commit when all checkboxes checked**

---

## Phase 8: Final Integration - GameEngine & End Game Flow

**Target Commit**: `feat(application): Integrate ScoreStorage into GameEngine with end_game flow`

### Files to Modify

- [ ] `src/application/game_engine.py`
  - [ ] Add `score_storage: Optional[ScoreStorage]` parameter to `__init__()`
  - [ ] Update `create()` factory to instantiate `ScoringService` if `settings.scoring_enabled`
  - [ ] Update `create()` factory to instantiate `ScoreStorage`
  - [ ] Pass `scoring` to `GameService` constructor
  - [ ] Create/modify `end_game(is_victory)` method
    - [ ] Check `if not settings.scoring_enabled:` → skip scoring
    - [ ] Calculate `final_score` using `scoring.calculate_final_score()`
    - [ ] Save to storage: `score_storage.save_score(final_score)`
    - [ ] Format with `ScoreFormatter.format_final_score()`
    - [ ] Announce via TTS
    - [ ] Reset game state
  - [ ] Update `new_game()` to respect `settings.scoring_enabled`
  - [ ] Update all docstrings

- [ ] `src/application/main.py` (or equivalent entry point)
  - [ ] Ensure `GameEngine.create()` called with `settings` parameter
  - [ ] Add command binding for P key → `show_current_score()`
  - [ ] Add command binding for Shift+P key → `show_score_breakdown()`

### Testing

- [ ] `tests/integration/test_end_to_end_scoring.py`
  - [ ] Test complete game with scoring enabled (deal, play, win, save)
  - [ ] Test complete game with scoring disabled (no save)
  - [ ] Test final score saved to JSON correctly
  - [ ] Test victory bonus applied when `is_victory=True`
  - [ ] Test no victory bonus when `is_victory=False`
  - [ ] Test TTS announces final score
  - [ ] Test score retrievable with `load_all_scores()`
  - [ ] Test best score updated after win

- [ ] `tests/integration/test_difficulty_constraints.py`
  - [ ] Test level 4→5 auto-adjusts timer
  - [ ] Test level 5→1 removes constraints
  - [ ] Test draw_count respects level limits
  - [ ] Test shuffle locked at level 4-5

### Acceptance Criteria

- [ ] Scoring only active when `settings.scoring_enabled=True`
- [ ] Final score calculated with all multipliers/bonuses
- [ ] Scores saved to persistent storage
- [ ] TTS announces complete breakdown at game end
- [ ] Free-play mode (scoring OFF) works without crashes
- [ ] All 8 phases integrated correctly
- [ ] Zero breaking changes to existing gameplay
- [ ] All tests pass (70+ total tests across all phases)

**Commit when all checkboxes checked**

---

## Final Validation Checklist

### Code Quality

- [ ] All new code has type hints
- [ ] All new code has docstrings (Google style)
- [ ] No TODO/FIXME comments in committed code
- [ ] No commented-out code blocks
- [ ] Consistent code style (PEP 8)
- [ ] No unused imports

### Testing

- [ ] Test coverage ≥90% for new code
- [ ] All unit tests pass (50+ tests)
- [ ] All integration tests pass (20+ tests)
- [ ] All acceptance tests pass (2+ tests)
- [ ] No test warnings or errors
- [ ] Manual testing completed (checklist in IMPLEMENTATION doc)

### Documentation

- [ ] README.md updated with scoring system overview
- [ ] CHANGELOG.md updated with v2.0.0 entry
- [ ] All docstrings complete and accurate
- [ ] Implementation guide complete
- [ ] TODO checklist complete

### Functionality

- [ ] All 7 options work correctly
- [ ] Difficulty levels 4-5 enforce constraints
- [ ] Scoring calculations verified manually (3+ test cases)
- [ ] Time bonus formula matches specification
- [ ] Scores saved/loaded correctly
- [ ] TTS messages clear and complete
- [ ] Free-play mode works
- [ ] No crashes or errors

### Performance

- [ ] Score calculation < 1ms per event
- [ ] JSON save/load < 50ms
- [ ] No memory leaks (tested with 100+ games)
- [ ] TTS doesn't block gameplay

### Accessibility

- [ ] All scoring features accessible via keyboard
- [ ] All TTS messages in Italian
- [ ] All messages screen-reader friendly
- [ ] No visual-only information

---

## Post-Implementation Tasks

- [ ] Create GitHub release v2.0.0
- [ ] Update project documentation
- [ ] Tag commit with `v2.0.0`
- [ ] Close related issues
- [ ] Merge `refactoring-engine` → `main`
- [ ] Announce new version

---

**Notes for Copilot:**

1. Complete each phase in order (don't skip ahead)
2. Check all boxes in a phase before committing
3. Run all tests before committing
4. Commit message must match "Target Commit" format
5. If a test fails, fix before proceeding
6. Update this TODO as you progress
7. Ask for clarification if any checkbox is unclear

**Current Phase**: Phase 1 (ready to start)

---

**Last Updated**: 2026-02-11  
**Status**: Ready for implementation