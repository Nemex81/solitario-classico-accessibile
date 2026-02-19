# 🔧 IMPLEMENTATION PLAN
# Legacy Test Suite Modernization — v3.2.0

## 📌 Informazioni Generali

**Feature**: Legacy Test Suite Modernization  
**Versione Target**: v3.2.0  
**Layer**: Test Infrastructure (tests/ directory only)  
**Stato**: Implementation Phase — **READY FOR EXECUTION**  
**Data Creazione**: 18 Febbraio 2026  
**Prerequisiti**:
- [LEGACY_TEST_AUDIT.md](../LEGACY_TEST_AUDIT.md) (Comprehensive audit report)
- Profile System v3.1.3 merged (PR #72)
- Timer System v2.7.0 merged
- Base branch: `refactoring-engine`

---

## 🎯 Obiettivo dell'Implementation Plan

Modernizzare la **legacy test suite** per allinearla con Profile System v3.1.3:
- ✅ Fix import errors (scr → src, GameState deprecato)
- ✅ Rimozione PileType enum references
- ✅ Aggiunta test integrazione Profile System + GameEngine
- ✅ Update assertions per EndReason enum (6 valori)
- ✅ GUI test markers + archiviazione test obsoleti

**Target**: Aumentare test health dal 75% all'88%+

**Scope**: **SOLO test suite**. Zero modifiche al codice di produzione (src/).

---

## 🔄 Workflow Copilot Agent (Checkpoint-Driven)

Ogni fase segue questo pattern:

```
1. 📖 READ: Consulta LEGACY_TEST_AUDIT.md + questo piano
2. ✅ CHECK: Verifica checklist fase corrente
3. 💻 CODE: Implementa modifiche atomiche test
4. 🧪 TEST: Esegui test specifici fase (non full suite)
5. 📝 COMMIT: Messaggio formato "test(scope): description [Phase N/6]"
6. 📋 UPDATE: Spunta checkbox in questo file + TODO.md
7. ♻️ REPEAT: Passa alla fase successiva
```

**Regola d'oro**: Un commit = una fase. No modifiche al codice di produzione.

---

## 📊 Progress Tracking (Aggiorna Ad Ogni Commit)

### ✅ Phase Completion Checklist

- [x] **Phase 0**: Create Implementation Plan (questo documento)
- [x] **Phase 1**: Fix Import Errors (scr → src, GameState removed)
- [x] **Phase 2**: Remove PileType References
- [x] **Phase 3**: Add Profile Integration Tests (5 scenarios)
- [x] **Phase 4**: Add Timer Field Mapping Tests (3 scenarios)
- [x] **Phase 5**: Update EndReason Assertions (SKIPPED - existing tests already use EndReason enum)
- [ ] **Phase 6**: GUI Markers + Archive Obsolete Tests

**Istruzioni**: Dopo ogni commit di fase, spunta `[x]` la fase completata.

---

## 📦 PHASE 0: Create Implementation Plan ✅

### 🎯 Obiettivo

Creare questo documento di implementazione seguendo il template esistente.

### 📝 Deliverables

- [x] File `docs/3 - coding plans/IMPLEMENTATION_LEGACY_TEST_MODERNIZATION.md` creato
- [x] Struttura completa per tutte le 6 fasi
- [x] Test scenarios documentati
- [x] Commit message format definito

### ✅ Commit Message

```
docs: Create legacy test modernization implementation plan [Phase 0/6]

- Structured plan with 6 phases
- Checkpoints and test scenarios defined
- Following DESIGN_PROFILE_STATISTICS_SYSTEM.md template
- Ready for Phase 1 execution

Refs: LEGACY_TEST_AUDIT.md Executive Summary
```

**Status**: ✅ COMPLETATA

---

## 🛠️ PHASE 1: Fix Import Errors

### 🎯 Obiettivo

Correggere errori di import legacy:
- Sostituire `scr` → `src` package (3 file)
- Rimuovere import `GameState` (modulo eliminato)
- Rimuovere import `PileType` dove non necessario

### 📝 File da Modificare

#### Category C1: Legacy scr Package (3 files)

**Files**:
- `tests/unit/scr/test_distribuisci_carte_deck_switching.py`
- `tests/unit/scr/test_game_engine_f3_f5.py`
- `tests/unit/scr/test_king_to_empty_base_pile.py`

**Changes**:
```python
# OLD
from scr.domain.models.card import Card
from scr.domain.services.game_service import GameService

# NEW
from src.domain.models.card import Card
from src.domain.services.game_service import GameService
```

#### Category C2: GameState Module (3 files)

**Files**:
- `tests/unit/domain/models/test_game_state.py`
- `tests/unit/domain/rules/test_move_validator.py`
- `tests/unit/presentation/test_game_formatter.py`

**Changes**:
```python
# REMOVE (module no longer exists)
from src.domain.models.game_state import GameState

# GameState functionality now in:
# - GameTable (state representation)
# - MoveValidator (move validation)
# - Domain services (business logic)
```

**Action**: Either update tests for new architecture OR mark for archival in Phase 6.

#### Other Import Errors (2 files)

**Files**: Identificare con `pytest --collect-only` output error analysis

### 🧪 Test Command

```bash
pytest tests/unit/scr/ tests/unit/domain/models/ -v --tb=short
```

**Expected**: Import errors risolti, test collection successful

### ✅ Commit Message Format

```
test(unit): Fix legacy import errors (scr → src) [Phase 1/6]

- Update 3 test files in tests/unit/scr/ (scr → src package)
- Remove GameState import in 3 test files (module removed)
- Fix 2 additional import errors
- All affected tests now collect successfully

Refs: LEGACY_TEST_AUDIT.md Category C1, C2
```

**Estimated Time**: 8-12 min  
**Files Modified**: 8 test files

---

## 🗑️ PHASE 2: Remove PileType References

### 🎯 Obiettivo

Rimuovere riferimenti a `PileType` enum (eliminato in Clean Architecture).

### 📝 File da Modificare

**Files**:
- `tests/unit/domain/models/test_pile.py`
- `tests/domain/services/test_selection_manager.py`

**Changes**:

```python
# OLD (using PileType enum)
from src.domain.models.pile import PileType

pile = Pile(nome="foundation", tipo=PileType.FOUNDATION)
assert pile.tipo == PileType.FOUNDATION

# NEW (using pile name strings)
pile = Pile(nome="foundation_1")
assert pile.nome == "foundation_1"
assert pile.is_foundation()  # Type determined by name pattern

# Name patterns:
# - "stock", "waste" → stock/waste piles
# - "foundation_1" ... "foundation_4" → foundation piles
# - "tableau_1" ... "tableau_7" → tableau piles
```

### 🧪 Test Command

```bash
pytest tests/unit/domain/models/test_pile.py tests/domain/services/test_selection_manager.py -v
```

**Expected**: Tests pass without PileType references

### ✅ Commit Message Format

```
test(domain): Remove PileType enum references [Phase 2/6]

- Update test_pile.py: use pile name strings instead of enum
- Update test_selection_manager.py: pile type from name pattern
- Replace PileType.FOUNDATION → "foundation_1" pattern
- Tests verify pile behavior without enum dependency

Refs: LEGACY_TEST_AUDIT.md Category C3
```

**Estimated Time**: 3-5 min  
**Files Modified**: 2 test files

---

## 🧩 PHASE 3: Profile Integration Tests

### 🎯 Obiettivo

Aggiungere test integrazione tra ProfileService e GameEngine per validare:
- SessionOutcome creation con tutti i campi
- EndReason correctness per tutti gli scenari
- Stats aggregation dopo end_game()

### 📝 New File

**File**: `tests/integration/test_profile_game_integration.py` (NEW)

### 🧪 Test Scenarios (5 tests)

#### Scenario 1: Victory Records Session

```python
def test_victory_records_session_with_correct_fields():
    """Verify victory creates SessionOutcome with all fields populated."""
    # Setup: GameEngine + ProfileService via DI
    engine = create_test_game_engine()
    profile_service = engine.profile_service
    
    # Action: Start game → force victory → end_game(EndReason.VICTORY)
    engine.new_game()
    # ... force victory state (all cards to foundations)
    engine.end_game(EndReason.VICTORY)
    
    # Assert: SessionOutcome created and saved
    profile = profile_service.get_current_profile()
    assert len(profile.recent_sessions) == 1
    
    session = profile.recent_sessions[0]
    assert session.end_reason == EndReason.VICTORY
    assert session.is_victory is True
    assert session.elapsed_time > 0
    assert session.move_count > 0
    assert session.final_score > 0
    
    # Assert: Global stats updated
    assert profile.global_stats.total_victories == 1
    assert profile.global_stats.total_games == 1
    assert profile.global_stats.winrate == 1.0
```

#### Scenario 2: Abandon Exit Records Session

```python
def test_abandon_exit_records_session():
    """Test ESC abandon creates ABANDON_EXIT session."""
    # Setup: GameEngine + ProfileService
    engine = create_test_game_engine()
    profile_service = engine.profile_service
    
    # Action: Start game → abandon via ESC
    engine.new_game()
    # ... play some moves
    engine.end_game(EndReason.ABANDON_EXIT)
    
    # Assert: Session recorded with ABANDON_EXIT
    profile = profile_service.get_current_profile()
    session = profile.recent_sessions[0]
    
    assert session.end_reason == EndReason.ABANDON_EXIT
    assert session.is_victory is False
    
    # Assert: Stats updated (defeats++)
    assert profile.global_stats.total_games == 1
    assert profile.global_stats.total_victories == 0
    assert profile.global_stats.total_defeats == 1
```

#### Scenario 3: Timeout Strict Records Session

```python
def test_timeout_strict_records_session():
    """Test STRICT timer timeout creates TIMEOUT_STRICT session."""
    # Setup: GameEngine with timer_strict_mode=True
    settings = GameSettings(
        max_time_game=60,  # 60 seconds
        timer_strict_mode=True
    )
    engine = create_test_game_engine(settings)
    
    # Action: Start game → simulate timer expiry
    engine.new_game()
    # ... mock elapsed time > 60 seconds
    engine._timer_service.force_expiry()  # Test helper
    
    # Assert: Game ended with TIMEOUT_STRICT
    profile = engine.profile_service.get_current_profile()
    session = profile.recent_sessions[0]
    
    assert session.end_reason == EndReason.TIMEOUT_STRICT
    assert session.timer_expired is True
    assert session.timer_mode == "STRICT"
```

#### Scenario 4: Overtime Victory Records Session

```python
def test_overtime_victory_records_session():
    """Test PERMISSIVE overtime creates VICTORY_OVERTIME."""
    # Setup: GameEngine with timer_strict_mode=False
    settings = GameSettings(
        max_time_game=60,
        timer_strict_mode=False  # PERMISSIVE mode
    )
    engine = create_test_game_engine(settings)
    
    # Action: Start game → expire timer → win anyway
    engine.new_game()
    # ... mock elapsed time > 60 seconds (timer expired)
    # ... force victory after overtime
    engine.end_game(EndReason.VICTORY_OVERTIME)
    
    # Assert: Victory with overtime tracking
    session = engine.profile_service.get_current_profile().recent_sessions[0]
    
    assert session.end_reason == EndReason.VICTORY_OVERTIME
    assert session.is_victory is True
    assert session.timer_expired is True
    assert session.overtime_duration > 0  # Seconds beyond limit
```

#### Scenario 5: Timer Fields Mapped Correctly

```python
def test_timer_fields_mapped_correctly():
    """Test GameSettings → SessionOutcome timer field mapping."""
    # Scenario 1: STRICT mode
    settings_strict = GameSettings(max_time_game=300, timer_strict_mode=True)
    engine = create_test_game_engine(settings_strict)
    engine.new_game()
    engine.end_game(EndReason.ABANDON_EXIT)
    
    session = engine.profile_service.get_current_profile().recent_sessions[0]
    assert session.timer_enabled is True
    assert session.timer_limit == 300
    assert session.timer_mode == "STRICT"
    
    # Scenario 2: PERMISSIVE mode
    settings_permissive = GameSettings(max_time_game=600, timer_strict_mode=False)
    engine = create_test_game_engine(settings_permissive)
    engine.new_game()
    engine.end_game(EndReason.VICTORY)
    
    session = engine.profile_service.get_current_profile().recent_sessions[-1]
    assert session.timer_enabled is True
    assert session.timer_limit == 600
    assert session.timer_mode == "PERMISSIVE"
    
    # Scenario 3: Timer OFF
    settings_off = GameSettings(max_time_game=-1)
    engine = create_test_game_engine(settings_off)
    engine.new_game()
    engine.end_game(EndReason.VICTORY)
    
    session = engine.profile_service.get_current_profile().recent_sessions[-1]
    assert session.timer_enabled is False
    assert session.timer_limit == -1
    assert session.timer_mode == "OFF"
```

### 🧪 Test Command

```bash
pytest tests/integration/test_profile_game_integration.py -v
```

**Expected**: 5 new tests passing

### ✅ Commit Message Format

```
test(integration): Add ProfileService + GameEngine integration tests [Phase 3/6]

- New file: tests/integration/test_profile_game_integration.py
- 5 test scenarios covering session recording
- Test victory, abandon, timeout, overtime scenarios
- Verify SessionOutcome field population
- Verify stats aggregation after end_game()
- All 5 tests passing

Refs: LEGACY_TEST_AUDIT.md Missing Tests Section
```

**Estimated Time**: 15-20 min  
**Test Count**: 5 new tests

---

## ⏱️ PHASE 4: Timer Field Mapping Tests

### 🎯 Obiettivo

Estendere test integrazione per validare mapping dettagliato:
- `GameSettings.max_time_game` → `SessionOutcome.timer_limit`
- `GameSettings.timer_strict_mode` → `SessionOutcome.timer_mode`
- Calcolo corretto `timer_enabled`

### 📝 File to Extend

**File**: `tests/integration/test_profile_game_integration.py` (EXTEND)

**Note**: Questo è già coperto in Scenario 5 di Phase 3. Se implementazione Phase 3 
ha incluso test completo timer mapping, questa fase può essere saltata o ridotta 
a validazione edge cases.

### 🧪 Additional Test Scenarios (se necessari)

#### Edge Case 1: Timer Disabled Mid-Game

```python
def test_timer_disabled_session_outcome():
    """Verify timer_enabled=False when timer disabled in settings."""
    settings = GameSettings(max_time_game=-1)  # Timer OFF
    engine = create_test_game_engine(settings)
    
    engine.new_game()
    engine.end_game(EndReason.VICTORY)
    
    session = engine.profile_service.get_current_profile().recent_sessions[0]
    assert session.timer_enabled is False
    assert session.timer_mode == "OFF"
```

#### Edge Case 2: Timer Mode Validation

```python
def test_timer_mode_string_values():
    """Verify timer_mode is one of: STRICT, PERMISSIVE, OFF."""
    # Test all 3 possible values
    for config, expected_mode in [
        ({"max_time_game": 300, "timer_strict_mode": True}, "STRICT"),
        ({"max_time_game": 300, "timer_strict_mode": False}, "PERMISSIVE"),
        ({"max_time_game": -1}, "OFF"),
    ]:
        settings = GameSettings(**config)
        engine = create_test_game_engine(settings)
        engine.new_game()
        engine.end_game(EndReason.ABANDON_EXIT)
        
        session = engine.profile_service.get_current_profile().recent_sessions[-1]
        assert session.timer_mode == expected_mode
```

### 🧪 Test Command

```bash
pytest tests/integration/test_profile_game_integration.py::test_timer_disabled_session_outcome -v
pytest tests/integration/test_profile_game_integration.py::test_timer_mode_string_values -v
```

**Expected**: Edge case tests passing

### ✅ Commit Message Format

```
test(integration): Add GameSettings → SessionOutcome timer mapping tests [Phase 4/6]

- Extend test_profile_game_integration.py
- Add edge case: timer disabled (-1 value)
- Add validation: timer_mode string values (STRICT/PERMISSIVE/OFF)
- Verify mapping logic for all 3 timer modes
- 2-3 additional tests passing

Refs: LEGACY_TEST_AUDIT.md Timer Field Names Section
```

**Estimated Time**: 8-10 min  
**Test Count**: 2-3 new tests (se necessari)

**Note**: Se Phase 3 Scenario 5 è completo, questa fase può essere merged con Phase 3.

---

## ✅ PHASE 5: Update EndReason Assertions (SKIPPED)

### ✅ Status: SKIPPED - No Updates Needed

**Reason**: Analysis of existing tests shows all `end_game()` calls already use `EndReason` enum correctly.

**Verification Command**:
```bash
grep -r "end_game" tests/ --include="*.py" | grep -v "test_profile_game_integration" | grep -v "archive"
```

**Findings**:
- `tests/integration/test_timer_integration.py`: Already uses `EndReason.TIMEOUT_STRICT` ✅
- `tests/integration/test_game_profile_integration.py`: Placeholder only (no actual calls) ✅
- No legacy `end_game()` calls without `EndReason` found ✅

**Conclusion**: All existing tests were already updated during Timer System v2.7.0 implementation. No additional work needed for Phase 5.

---

## 🎯 PHASE 5 ORIGINAL SPECIFICATION (for reference)

### 🎯 Obiettivo (NOT IMPLEMENTED - Not Needed)

Aggiornare test esistenti che chiamano `end_game()` per supportare nuovi valori EndReason:
- `EndReason.VICTORY` (timer off)
- `EndReason.VICTORY_OVERTIME` (permissive timer expired)
- `EndReason.ABANDON_EXIT` (ESC/N key)
- `EndReason.ABANDON_NEW_GAME` (N key)
- `EndReason.ABANDON_APP_CLOSE` (window close)
- `EndReason.TIMEOUT_STRICT` (strict timer expired)

### 📝 Find Affected Tests

**Command**:
```bash
grep -r "end_game" tests/ --include="*.py" | grep -v ".pyc"
```

**Expected**: Lista test file che chiamano `GameEngine.end_game()`

### 🔧 Update Pattern

**OLD** (pre-v3.1.x):
```python
def test_game_ends_on_victory():
    engine.force_victory()
    engine.end_game()  # No argument
    assert engine.game_ended is True
```

**NEW** (v3.1.x+):
```python
def test_game_ends_on_victory():
    engine.force_victory()
    engine.end_game(EndReason.VICTORY)  # Explicit reason
    assert engine.game_ended is True
    assert engine.end_reason == EndReason.VICTORY
```

### 📝 File Categories

#### Category A: Integration Tests

**Files** (from LEGACY_TEST_AUDIT.md):
- `tests/integration/test_game_engine_flow.py`
- `tests/integration/test_timer_integration.py`
- `tests/integration/test_profile_session_flow.py`

**Changes**:
- Add `EndReason` import
- Update `end_game()` calls with explicit reason
- Add assertions for `end_reason` field

#### Category B: Unit Tests

**Files**:
- `tests/unit/test_game_end.py`
- `tests/unit/application/test_game_controller.py` (if exists)

**Changes**: Similar to Category A

### 🧪 Test Command

```bash
pytest tests/integration/ tests/unit/test_game_end.py -v
```

**Expected**: All tests pass with updated EndReason usage

### ✅ Commit Message Format

```
test(integration): Update tests for new EndReason enum values [Phase 5/6]

- Update 8-10 test files calling end_game()
- Add EndReason import and explicit reason arguments
- Add assertions for EndReason.VICTORY, VICTORY_OVERTIME, etc.
- Test coverage for all 6 EndReason values
- All affected tests passing

Refs: LEGACY_TEST_AUDIT.md Category B2
```

**Estimated Time**: 10-15 min  
**Files Modified**: 8-10 test files

---

## 🏷️ PHASE 6: GUI Markers + Cleanup

### 🎯 Obiettivo

Configurare pytest markers per test GUI e archiviare test obsoleti:
- Update `pytest.ini` con marker `gui`
- Mark test wxPython/pygame con `@pytest.mark.gui`
- Creare directory `tests/archive/`
- Archiviare `tests/unit/scr/` (funzionalità coperta da integration tests)

### 📝 File Modifications

#### 1. Update pytest.ini

**File**: `pytest.ini` (MODIFIED)

**Add**:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-branch
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    gui: Tests requiring wxPython/pygame (skip in CI without display)  # NEW
```

#### 2. Mark GUI Tests

**Files to mark** (from LEGACY_TEST_AUDIT.md Category 1):
- `tests/infrastructure/test_view_manager.py`
- `tests/unit/presentation/widgets/test_timer_combobox.py`
- `tests/integration/test_di_container.py`
- `tests/integration/test_game_flow.py`
- `tests/integration/test_gameplay_hints_integration.py`
- `tests/unit/application/test_commands.py`
- `tests/unit/application/test_game_controller.py`
- `tests/unit/application/test_options_command_hints.py`
- `tests/unit/application/test_options_controller_timer.py`
- `tests/unit/infrastructure/test_di_container.py`

**Add decorator**:
```python
import pytest

@pytest.mark.gui
@pytest.mark.skipif(not has_display(), reason="No display available")
def test_view_manager_switches_panels():
    # ... existing test code
    pass
```

**Helper function** (add to `tests/conftest.py` if needed):
```python
import os

def has_display() -> bool:
    """Check if display is available for GUI tests."""
    return "DISPLAY" in os.environ or os.name == "nt"
```

#### 3. Archive Obsolete Tests

**Create**: `tests/archive/` directory

**Move**:
```bash
mkdir -p tests/archive/scr
mv tests/unit/scr/* tests/archive/scr/
```

**Rationale**: `scr` package tests obsoleti, funzionalità coperta da integration tests

**Keep**: README in `tests/archive/scr/README.md`
```markdown
# Archived Legacy Tests

These tests reference the old `scr` package structure (replaced by `src` in Clean Architecture migration).

## Status
- **Archived**: 2026-02-18 (v3.2.0 Test Modernization)
- **Reason**: Package structure changed, functionality covered by integration tests
- **Coverage**: See `tests/integration/test_game_engine_flow.py`

## Contents
- test_distribuisci_carte_deck_switching.py
- test_game_engine_f3_f5.py
- test_king_to_empty_base_pile.py
```

### 🧪 Test Commands

**Test without GUI**:
```bash
pytest -m "not gui" -v
```

**Expected**: All non-GUI tests pass (88%+ of suite)

**Test with GUI** (on system with display):
```bash
pytest -m "gui" -v
```

**Expected**: GUI tests skip or run (environment-dependent)

### ✅ Commit Message Format

```
test(infrastructure): Add GUI markers and archive obsolete tests [Phase 6/6]

- Update pytest.ini: add 'gui' marker for wxPython/pygame tests
- Mark 10 GUI-dependent test files with @pytest.mark.gui
- Create tests/archive/ directory
- Archive tests/unit/scr/ (old package structure)
- Add README to archived tests explaining rationale
- pytest -m "not gui" passes without display (CI-safe)

Refs: LEGACY_TEST_AUDIT.md Category 1, Category C1
```

**Estimated Time**: 5-8 min  
**Files Modified**: pytest.ini + 10 test files + archive structure

---

## ✅ Acceptance Criteria

L'implementazione è completa quando:

### Codice
- [x] Phase 0: Implementation plan creato
- [ ] Phase 1: Import errors risolti (8 file)
- [ ] Phase 2: PileType references eliminate (2 file)
- [ ] Phase 3: 5 nuovi test integrazione Profile+GameEngine
- [ ] Phase 4: Timer field mapping validato (3 scenari)
- [ ] Phase 5: EndReason assertions aggiornate (8-10 file)
- [ ] Phase 6: GUI markers configurati + test archiviati

### Testing
- [ ] Test suite health: **88%+** (da 75% attuale)
- [ ] Zero regressioni su test Category A (75% già funzionanti)
- [ ] Nuovi integration tests (Phase 3-4) passano: 5-8 tests
- [ ] `pytest -m "not gui"` passa senza display
- [ ] Full suite `pytest tests/` passa con 88%+ success rate

### Documentazione
- [x] IMPLEMENTATION_LEGACY_TEST_MODERNIZATION.md: creato con 6 fasi
- [ ] IMPLEMENTATION_LEGACY_TEST_MODERNIZATION.md: tutte le 6 checkbox spuntate
- [ ] TODO.md: sezione "Test Modernization v3.2.0" aggiornata
- [ ] pytest.ini: configurato con marker `gui`
- [ ] CHANGELOG.md: entry per v3.2.0 (Test Suite Modernization)
- [ ] tests/archive/scr/README.md: documentazione test archiviati

---

## 📊 Success Metrics

| Metrica | Before | Target | Status |
|---------|--------|--------|--------|
| Test Health Score | 75% | 88%+ | TBD |
| Import Errors | 17 | 0 | TBD |
| Profile Tests | 0 | 5+ | TBD |
| EndReason Coverage | Partial | 6/6 values | TBD |
| GUI Test Isolation | No | Yes (markers) | TBD |

**Total Commits**: 6 implementation + 6 checkpoint updates = 12 commits

---

## 🚫 Out of Scope

- ❌ Modifiche al codice di produzione (src/)
- ❌ Aggiunta nuove feature al sistema
- ❌ Refactoring architetturale
- ❌ Performance optimization
- ❌ UI changes (solo test infrastructure)

---

## 🔗 Dependencies & References

**Prerequisiti**:
- ✅ Profile System v3.1.3 merged (PR #72)
- ✅ Timer System v2.7.0 merged
- ✅ LEGACY_TEST_AUDIT.md disponibile

**Documenti di Riferimento**:
- [LEGACY_TEST_AUDIT.md](../LEGACY_TEST_AUDIT.md) - Audit completo test suite
- [TODO.md](../TODO.md) - Task tracking centrale
- [DESIGN_PROFILE_STATISTICS_SYSTEM.md](../2%20-%20projects/DESIGN_PROFILE_STATISTICS_SYSTEM.md) - Profile system design
- [DESIGN_TIMER_MODE_SYSTEM.md](../2%20-%20projects/DESIGN_TIMER_MODE_SYSTEM.md) - Timer system + EndReason

---

## 🎯 Next Steps After Completion

1. ✅ Merge PR to `refactoring-engine`
2. Update README.md con test coverage badge (88%+)
3. Plan v3.3.0: Profile UI tests (integration con wxPython panels)
4. Setup CI/CD con Xvfb per GUI tests (opzionale)

---

**Piano creato**: 18 Febbraio 2026  
**Autore**: GitHub Copilot Agent  
**Base**: LEGACY_TEST_AUDIT.md + DESIGN_PROFILE_STATISTICS_SYSTEM.md template  
**Status**: ✅ **READY FOR PHASE 1**
