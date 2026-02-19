# 🔧 IMPLEMENTATION PLAN
# GUI Test Markers Configuration — v3.2.1

## 📌 Informazioni Generali

**Feature**: GUI Test Markers (Phase 6 Deferred from v3.2.0)  
**Versione Target**: v3.2.1 (Housekeeping release)  
**Layer**: Test Infrastructure (tests/ directory + pytest.ini)  
**Stato**: Implementation Phase — **READY FOR EXECUTION**  
**Data Creazione**: 19 Febbraio 2026, 15:30 CET  
**Prerequisiti**:
- v3.2.0 Test Modernization merged (PR #74) ✅
- Base branch: `refactoring-engine` ✅
- pytest 7.0+ with `--strict-markers` ✅

---

## 🎯 Obiettivo dell'Implementation Plan

Configurare pytest marker `gui` per isolare test wxPython-dipendenti:
- ✅ Aggiungere marker `gui` a pytest.ini
- ✅ Marcare SOLO test con dipendenze wxPython esplicite (import wx)
- ✅ Documentare uso marker in TESTING.md
- ✅ Verificare funzionamento con `pytest -m "not gui"`

**Strategia**: **Opzione A (Conservativa)** — Zero falsi positivi
- Marca SOLO file con `import wx` esplicito
- NON marca test che mockano wx (già GUI-safe)
- NON marca test application/presentation layer senza wx

**Scope**: **SOLO test infrastructure**. Zero modifiche al codice di produzione (src/).

---

## 🔄 Workflow Copilot Agent (Checkpoint-Driven)

Ogni fase segue questo pattern:

```
1. 📖 READ: Consulta questo piano + verifica file status
2. ✅ CHECK: Verifica checklist fase corrente
3. 💻 CODE: Implementa modifiche atomiche (1 file/fase)
4. 🧪 TEST: Esegui test command specifico fase
5. 📝 COMMIT: Messaggio formato "test(scope): description [Phase N/4]"
6. 📋 UPDATE: Spunta checkbox in questo file
7. ♻️ REPEAT: Passa alla fase successiva
```

**Regola d'oro**: Un commit = una fase. Un file modificato = un commit.

---

## 📊 Progress Tracking (Aggiorna Ad Ogni Commit)

### ✅ Phase Completion Checklist

- [x] **Phase 0**: Create Implementation Plan (questo documento)
- [ ] **Phase 1**: Audit GUI Test Dependencies
- [ ] **Phase 2**: Update pytest.ini with gui marker
- [ ] **Phase 3**: Mark test_timer_combobox.py as GUI
- [ ] **Phase 4**: Create TESTING.md documentation

**Istruzioni**: Dopo ogni commit di fase, spunta `[x]` la fase completata.

---

## 📦 PHASE 0: Create Implementation Plan ✅

### 🎯 Obiettivo

Creare questo documento di implementazione seguendo il template esistente.

### 📝 Deliverables

- [x] File `docs/3 - coding plans/IMPLEMENTATION_GUI_TEST_MARKERS.md` creato
- [x] Struttura completa per tutte le 4 fasi
- [x] Test scenarios documentati
- [x] Commit message format definito
- [x] Conservative strategy (Opzione A) documentata

### ✅ Commit Message

```
docs: Create GUI test markers implementation plan [Phase 0/4]

- Structured plan with 4 atomic phases
- Conservative approach: mark only explicit wx dependencies
- Zero false positives strategy (Opzione A)
- Checkpoints and test scenarios defined
- Ready for Phase 1 execution

Refs: Priority 1.1 from v3.2.0 housekeeping backlog
```

**Status**: ✅ COMPLETATA (commit automatico alla creazione di questo file)

---

## 🔍 PHASE 1: Audit GUI Test Dependencies

### 🎯 Obiettivo

Identificare TUTTI i test file con dipendenze wxPython esplicite:
- File con `import wx`
- File con `wx.App()`, `wx.Frame()`, `wx.Dialog()`
- Escludere file che usano SOLO mock di wx (già GUI-safe)

### 📝 Audit Commands

**Command 1: Find explicit wx imports**
```bash
grep -r "import wx" tests/ --include="*.py" | grep -v "archive" | grep -v ".pyc"
```

**Command 2: Find wx.App instantiation**
```bash
grep -r "wx\.App\|wx\.Frame\|wx\.Dialog" tests/ --include="*.py" | grep -v "archive" | grep -v "mock" | grep -v "MagicMock"
```

**Command 3: Verify test_timer_combobox.py (known GUI test)**
```bash
grep -A 5 "def test_" tests/unit/presentation/widgets/test_timer_combobox.py | head -30
```

### 📊 Expected Output

**Confirmed GUI test files** (from v3.2.0 analysis):
1. ✅ `tests/unit/presentation/widgets/test_timer_combobox.py`
   - Imports: `import wx`
   - Creates: `wx.App()`, `wx.Frame()` in fixtures
   - Test count: 40+ tests in 5 classes

**Potential GUI test files** (da verificare):
- `tests/unit/application/*.py` — verifica se istanziano GameEngine con wx components
- `tests/integration/test_game_engine_flow.py` — 13KB, potrebbe usare wx.Timer
- `tests/unit/infrastructure/test_view_manager.py` — se esiste, probabilmente GUI

### 📝 Audit Report Template

**File**: Non serve file separato, report inline in commit message Phase 1

**Format**:
```
GUI Test Dependencies Audit Results:

✅ CONFIRMED GUI TESTS (mark with @pytest.mark.gui):
- tests/unit/presentation/widgets/test_timer_combobox.py
  → import wx, wx.App() fixtures (40+ tests)

⚪ NO GUI DEPENDENCIES FOUND:
- tests/unit/application/* — uses mocks only
- tests/integration/* — no wx imports

❌ EXCLUDED (mocked wx, GUI-safe):
- (nessun file trovato in questa categoria)

TOTAL GUI TEST FILES: 1
TOTAL GUI TEST CLASSES: 5
TOTAL GUI TEST FUNCTIONS: 40+
```

### 🧪 Test Command

**Non serve pytest**, solo grep audit. Output audit va nel commit message.

### ✅ Commit Message Format

```
test(audit): Identify GUI test dependencies [Phase 1/4]

- Audit test suite with grep for wx imports
- Confirmed: 1 file with explicit wx dependencies
- File: tests/unit/presentation/widgets/test_timer_combobox.py
- Contains: 40+ tests requiring wx.App and display
- Other test files: no wx dependencies found (mocks only)
- Strategy: Conservative marking (Opzione A confirmed)

Audit Results:
✅ GUI test files: 1
⚪ Non-GUI files: 789+ tests
❌ False positives: 0

Refs: IMPLEMENTATION_GUI_TEST_MARKERS.md Phase 1
```

**Estimated Time**: 5 min (audit + commit)  
**Files Modified**: NONE (audit only, report in commit message)

---

## ⚙️ PHASE 2: Update pytest.ini

### 🎯 Obiettivo

Aggiungere marker `gui` alla configurazione pytest esistente.

### 📝 File Modificato

**File**: `pytest.ini`

**Current Content** (da v3.2.0):
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
```

**New Content** (add 1 line to markers section):
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
    gui: Tests requiring wxPython display (skip in headless CI with -m "not gui")  # ← NEW LINE
```

### 🧪 Test Command

**Verify marker registered**:
```bash
pytest --markers | grep gui
```

**Expected Output**:
```
@pytest.mark.gui: Tests requiring wxPython display (skip in headless CI with -m "not gui")
```

**Verify no collection errors**:
```bash
pytest --collect-only tests/ | head -20
```

**Expected**: Collection successful, no errors

### ✅ Commit Message Format

```
test(config): Add gui marker to pytest.ini [Phase 2/4]

- Add @pytest.mark.gui marker definition
- Enables skipping wxPython tests in headless environments
- Usage: pytest -m "not gui" (skip GUI tests)
- Usage: pytest -m "gui" (run only GUI tests)
- --strict-markers prevents typo in test files
- Marker registered successfully (verified with pytest --markers)

Refs: IMPLEMENTATION_GUI_TEST_MARKERS.md Phase 2
```

**Estimated Time**: 2 min  
**Files Modified**: 1 (pytest.ini)

---

## 🏷️ PHASE 3: Mark test_timer_combobox.py as GUI

### 🎯 Obiettivo

Aggiungere `@pytest.mark.gui` a tutte le classi di test in `test_timer_combobox.py`.

### 📝 File Modificato

**File**: `tests/unit/presentation/widgets/test_timer_combobox.py`

**Strategia di marcatura**: Decorator su OGNI classe test (non intero modulo)
- **Perché**: Maggiore granularità, più facile debug futuri test non-GUI nello stesso file
- **Alternative scartate**: `pytestmark = pytest.mark.gui` a inizio file (troppo ampio)

### 🔧 Changes

**5 classi da marcare**:
1. `TestTimerComboBoxInitialization`
2. `TestTimerComboBoxGetSetMethods`
3. `TestTimerComboBoxEdgeCases`
4. `TestTimerComboBoxPresetManagement`
5. `TestTimerComboBoxIntegration`

**Pattern**:

**BEFORE**:
```python
import pytest
import wx
from src.presentation.widgets.timer_combobox import TimerComboBox


class TestTimerComboBoxInitialization:
    """Test TimerComboBox initialization and construction."""
    
    @pytest.fixture
    def app(self):
        """Create wx.App for testing."""
        app = wx.App()
        yield app
        app.Destroy()
    # ... rest of class
```

**AFTER**:
```python
import pytest
import wx
from src.presentation.widgets.timer_combobox import TimerComboBox


@pytest.mark.gui  # ← ADD THIS LINE
class TestTimerComboBoxInitialization:
    """Test TimerComboBox initialization and construction."""
    
    @pytest.fixture
    def app(self):
        """Create wx.App for testing."""
        app = wx.App()
        yield app
        app.Destroy()
    # ... rest of class
```

**Ripeti per tutte le 5 classi**.

### 🧪 Test Commands

**1. Verify marker applied**:
```bash
pytest --collect-only tests/unit/presentation/widgets/test_timer_combobox.py -m "gui" | grep "<Class"
```

**Expected**: Lista le 5 classi marcate

**2. Verify tests skipped with -m "not gui"**:
```bash
pytest tests/unit/presentation/widgets/test_timer_combobox.py -m "not gui" --co
```

**Expected**: Output contiene "40+ deselected by '-m'"

**3. Verify GUI tests still runnable locally**:
```bash
pytest tests/unit/presentation/widgets/test_timer_combobox.py -m "gui" -v
```

**Expected**: 40+ tests passing (se display disponibile), oppure 40+ skipped (se headless)

### ✅ Commit Message Format

```
test(presentation): Mark timer_combobox tests as GUI [Phase 3/4]

- Add @pytest.mark.gui to all 5 test classes
- Tests require wx.App() and wx.Frame() (display needed)
- Marked tests: TestTimerComboBoxInitialization, GetSetMethods, EdgeCases, PresetManagement, Integration
- Test count: 40+ tests now marked as GUI
- Skippable in CI with: pytest -m "not gui"
- Verified: tests deselected correctly with -m "not gui"

Refs: IMPLEMENTATION_GUI_TEST_MARKERS.md Phase 3
```

**Estimated Time**: 5 min  
**Files Modified**: 1 (test_timer_combobox.py)
**Lines Added**: 5 (one `@pytest.mark.gui` per class)

---

## 📚 PHASE 4: Create TESTING.md Documentation

### 🎯 Obiettivo

Documentare uso dei marker pytest per sviluppatori e CI.

### 📝 New File

**File**: `docs/TESTING.md` (NEW)

**Content**:

```markdown
# 🧪 Testing Guide — Solitario Classico Accessibile

## Overview

La test suite del progetto utilizza **pytest** con copertura dell'88.2% (v3.2.0).

### Test Statistics (v3.2.1)

| Category | Count | Marker |
|----------|-------|--------|
| Unit Tests | ~680 | `@pytest.mark.unit` |
| Integration Tests | ~110 | `@pytest.mark.integration` |
| GUI Tests | ~40 | `@pytest.mark.gui` |
| Slow Tests | ~15 | `@pytest.mark.slow` |
| **Total** | **790+** | - |

### Test Coverage (v3.2.0)

- **Domain Layer**: 96%+
- **Application Layer**: 87%+
- **Infrastructure Layer**: 72%+
- **Overall**: 88.2%

---

## Running Tests

### Full Test Suite (local with display)

```bash
pytest tests/ -v
```

Runs all 790+ tests including GUI tests (requires wxPython display).

### Headless CI Mode (skip GUI tests)

```bash
pytest tests/ -m "not gui" -v
```

Skips ~40 GUI tests that require wxPython display. Ideal for CI environments without X server.

### Run Only GUI Tests (local)

```bash
pytest tests/ -m "gui" -v
```

Runs only the ~40 GUI tests (requires display).

### Run Specific Layer

```bash
# Domain layer tests only
pytest tests/unit/domain/ -v

# Application layer tests only
pytest tests/unit/application/ -v

# Integration tests only
pytest tests/integration/ -m "integration" -v
```

### Run with Coverage Report

```bash
pytest --cov=src --cov-report=term-missing tests/
```

Generates coverage report with line numbers for missing coverage.

### Run with HTML Coverage Report

```bash
pytest --cov=src --cov-report=html tests/
open htmlcov/index.html  # Linux/Mac
start htmlcov/index.html  # Windows
```

---

## Pytest Markers

### `@pytest.mark.unit`

**Purpose**: Mark unit tests (fast, isolated, no external dependencies).

**Usage**:
```python
@pytest.mark.unit
def test_card_creation():
    card = Card(suit="hearts", rank="A")
    assert card.suit == "hearts"
```

**Run**: `pytest -m "unit" -v`

---

### `@pytest.mark.integration`

**Purpose**: Mark integration tests (slower, require DI container, multiple components).

**Usage**:
```python
@pytest.mark.integration
def test_game_engine_profile_flow():
    engine = GameEngine(profile_service=ProfileService())
    engine.new_game()
    # ... test cross-component behavior
```

**Run**: `pytest -m "integration" -v`

---

### `@pytest.mark.gui` ⚠️

**Purpose**: Mark tests requiring wxPython display (wx.App, wx.Frame, wx.Dialog).

**Critical**: These tests **WILL FAIL** in headless CI without X server or Xvfb.

**Usage**:
```python
import pytest
import wx

@pytest.mark.gui
class TestTimerComboBox:
    @pytest.fixture
    def app(self):
        app = wx.App()
        yield app
        app.Destroy()
    
    def test_combobox_initialization(self, app):
        frame = wx.Frame(None)
        combo = TimerComboBox(frame)
        # ... test GUI behavior
```

**Run locally** (with display):
```bash
pytest -m "gui" -v
```

**Skip in CI** (headless):
```bash
pytest -m "not gui" -v
```

**Files with GUI tests**:
- `tests/unit/presentation/widgets/test_timer_combobox.py` (40+ tests)

---

### `@pytest.mark.slow`

**Purpose**: Mark tests that take >1s to run (I/O, large datasets, simulation).

**Usage**:
```python
@pytest.mark.slow
def test_1000_game_simulation():
    # ... long-running test
```

**Skip slow tests**:
```bash
pytest -m "not slow" -v
```

---

## CI Configuration Examples

### GitHub Actions (headless Linux)

```yaml
- name: Run tests (skip GUI)
  run: |
    pytest tests/ -m "not gui" -v --cov=src --cov-report=xml
```

### GitHub Actions (with Xvfb for GUI tests)

```yaml
- name: Install Xvfb
  run: sudo apt-get install -y xvfb

- name: Run all tests (including GUI)
  run: |
    xvfb-run --auto-servernum pytest tests/ -v --cov=src
```

### Local Development (Windows/macOS with display)

```bash
# Run full suite including GUI
pytest tests/ -v
```

---

## Test Structure

```
tests/
├── unit/                      # Unit tests (~680 tests)
│   ├── domain/               # Domain layer (models, rules, services)
│   ├── application/          # Application layer (engine, controllers)
│   ├── infrastructure/       # Infrastructure (DI, storage, UI)
│   └── presentation/         # Presentation (formatters, widgets)
│       └── widgets/
│           └── test_timer_combobox.py  # ⚠️ GUI tests (40+)
├── integration/              # Integration tests (~110 tests)
│   ├── test_profile_game_integration.py  # ProfileService + GameEngine
│   ├── test_timer_integration.py         # Timer + GameEngine
│   └── ...
└── archive/                  # Archived legacy tests (obsolete)
    └── scr/                  # Old package structure tests
```

---

## Troubleshooting

### Error: "No display available"

**Cause**: Running GUI tests in headless environment.

**Solution**:
```bash
# Option 1: Skip GUI tests
pytest -m "not gui" -v

# Option 2: Use Xvfb (Linux)
xvfb-run --auto-servernum pytest tests/ -v
```

### Error: "pytest: unknown marker: gui"

**Cause**: pytest.ini not configured or outdated.

**Solution**: Verify `pytest.ini` contains:
```ini
markers =
    gui: Tests requiring wxPython display (skip in headless CI)
```

### Error: "Import error: cannot import name 'GameState'"

**Cause**: Test references old `GameState` module (removed in Clean Architecture).

**Solution**: These tests are archived in `tests/archive/`. If you encounter this in active tests, report as bug.

---

## Best Practices

### Writing New Tests

1. **Mark appropriately**:
   - Unit test? → `@pytest.mark.unit`
   - Integration test? → `@pytest.mark.integration`
   - GUI test? → `@pytest.mark.gui`
   - Slow test? → `@pytest.mark.slow`

2. **GUI tests checklist**:
   - [ ] Import `wx` only if absolutely necessary
   - [ ] Use `@pytest.mark.gui` on class or function
   - [ ] Test works with `pytest -m "gui"` locally
   - [ ] Test skipped with `pytest -m "not gui"`
   - [ ] Consider mocking wx components if possible (GUI-safe alternative)

3. **Integration tests checklist**:
   - [ ] Use DI container for dependencies
   - [ ] Clean up resources (profiles, temp files)
   - [ ] Test realistic user workflows
   - [ ] Keep test time <5s if possible

### Test Coverage Goals

- **Domain Layer**: ≥95% (business logic critical)
- **Application Layer**: ≥85% (complex orchestration)
- **Infrastructure Layer**: ≥70% (UI, I/O)
- **Overall**: ≥88% (current: 88.2%)

---

## References

- [pytest Documentation](https://docs.pytest.org/)
- [pytest Markers Guide](https://docs.pytest.org/en/stable/how-to/mark.html)
- [ARCHITECTURE.md](ARCHITECTURE.md) — Project architecture overview
- [CHANGELOG.md](CHANGELOG.md) — Test suite evolution history

---

**Last Updated**: 19 Febbraio 2026 (v3.2.1)  
**Maintainer**: Nemex81  
**Test Framework**: pytest 7.0+  
**Coverage Tool**: pytest-cov 4.0+
```

### 🧪 Verification

**No pytest command needed** — documentation only.

**Manual check**:
1. File created in `docs/TESTING.md`
2. Markdown renders correctly on GitHub
3. Code examples have correct syntax highlighting

### ✅ Commit Message Format

```
docs(testing): Add comprehensive testing guide [Phase 4/4]

- New file: docs/TESTING.md (comprehensive pytest guide)
- Document all 4 pytest markers (unit, integration, gui, slow)
- Add usage examples for local dev and CI
- Document test structure and coverage goals
- Add troubleshooting section for headless environments
- Include CI configuration examples (GitHub Actions)
- Reference test statistics from v3.2.0 (790+ tests, 88.2% coverage)

Refs: IMPLEMENTATION_GUI_TEST_MARKERS.md Phase 4
```

**Estimated Time**: 10 min  
**Files Created**: 1 (docs/TESTING.md, ~250 lines)

---

## ✅ Acceptance Criteria

L'implementazione è completa quando:

### Codice
- [x] Phase 0: Implementation plan creato ✅
- [ ] Phase 1: Audit GUI dependencies completato (1 file identificato)
- [ ] Phase 2: pytest.ini aggiornato con marker `gui`
- [ ] Phase 3: test_timer_combobox.py marcato (5 classi)
- [ ] Phase 4: docs/TESTING.md creato

### Testing
- [ ] `pytest --markers | grep gui` mostra marker registrato
- [ ] `pytest -m "not gui" tests/` passa senza display
- [ ] `pytest -m "gui" tests/` seleziona solo 40+ test timer_combobox
- [ ] `pytest --collect-only tests/` non ha errori
- [ ] Coverage non degrada (rimane 88.2%)

### Documentazione
- [x] IMPLEMENTATION_GUI_TEST_MARKERS.md: creato con 4 fasi ✅
- [ ] IMPLEMENTATION_GUI_TEST_MARKERS.md: tutte le 4 checkbox spuntate
- [ ] docs/TESTING.md: guida completa pytest marker
- [ ] CHANGELOG.md: entry per v3.2.1 (GUI Test Markers)

---

## 📊 Success Metrics

| Metrica | Before | Target | Status |
|---------|--------|--------|--------|
| GUI Tests Isolated | No | Yes | TBD |
| CI-Safe Test Suite | No | Yes (`-m "not gui"`) | TBD |
| Pytest Markers | 3 | 4 (+gui) | TBD |
| False Positives | N/A | 0 | TBD |
| Documentation | No marker docs | TESTING.md | TBD |

**Total Commits**: 4 implementation + 1 questo plan = 5 commits

---

## 🚫 Out of Scope

- ❌ Modifiche al codice di produzione (src/)
- ❌ Aggiunta nuovi test GUI
- ❌ Configurazione CI/CD (solo documentazione esempi)
- ❌ Setup Xvfb automatico (opzionale, non bloccante)
- ❌ Refactoring test esistenti
- ❌ Marcatura aggressiva di test non-GUI (solo Opzione A)

---

## 🔗 Dependencies & References

**Prerequisiti**:
- ✅ Test Modernization v3.2.0 merged (PR #74)
- ✅ pytest.ini già configurato con `--strict-markers`
- ✅ Base branch `refactoring-engine` aggiornato

**Documenti di Riferimento**:
- [IMPLEMENTATION_LEGACY_TEST_MODERNIZATION.md](IMPLEMENTATION_LEGACY_TEST_MODERNIZATION.md) - v3.2.0 test modernization
- [LEGACY_TEST_AUDIT.md](../LEGACY_TEST_AUDIT.md) - Test suite audit
- [pytest markers documentation](https://docs.pytest.org/en/stable/how-to/mark.html)

---

## 🎯 Next Steps After Completion

1. ✅ Merge PR to `refactoring-engine`
2. Update README.md con link a TESTING.md
3. (Optional) Setup GitHub Actions con Xvfb per GUI tests
4. Proceed to Priority 1.2: Startup Recovery Dialog (Fix 7.5.4)

---

## 📝 Notes for Copilot Agent

### Critical Instructions

1. **Conservative Strategy**: Marca SOLO `test_timer_combobox.py`. Se audit trova altri file con `import wx`, chiedere conferma prima di marcare.

2. **One File Per Commit**: Ogni fase modifica MAX 1 file. Non raggruppare Phase 2+3 nello stesso commit.

3. **Test Verification**: Dopo Phase 3, verifica che `pytest -m "not gui" tests/` passa senza errori di display.

4. **Documentation Quality**: TESTING.md deve essere completo e pronto per sviluppatori esterni (esempi chiari, no assunzioni implicite).

### Troubleshooting

**Se audit trova 0 file GUI**:
- ❌ NON procedere con Phase 3
- ✅ Aggiorna questo plan con "No GUI tests found, Phase 3-4 skipped"
- ✅ Commit solo Phase 1-2

**Se audit trova >1 file GUI**:
- ⚠️ Chiedere conferma prima di marcare
- ✅ Aggiornare Phase 3 con lista completa file
- ✅ Creare commit separato per ogni file marcato

---

**Piano creato**: 19 Febbraio 2026, 15:30 CET  
**Autore**: AI Assistant (Claude) + User Nemex81  
**Base**: IMPLEMENTATION_LEGACY_TEST_MODERNIZATION.md template  
**Status**: ✅ **READY FOR PHASE 1**
