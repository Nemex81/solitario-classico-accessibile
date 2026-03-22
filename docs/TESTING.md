# 🧪 Testing Guide — Solitario Classico Accessibile

## Overview

La test suite del progetto utilizza **pytest** con copertura dell'88.2% (v3.5.0).

### Test Statistics (v3.5.0)

| Category | Count | Marker |
|----------|-------|--------|
| Unit Tests | ~680 | `@pytest.mark.unit` |
| Integration Tests | ~110 | `@pytest.mark.integration` |
| GUI Tests | ~50 | `@pytest.mark.gui` |
| Slow Tests | ~15 | `@pytest.mark.slow` |
| **Total** | **790+** | - |

### Test Coverage (v3.5.0)

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

Skips ~50 GUI tests that require wxPython display. Ideal for CI environments without X server.

### Run Only GUI Tests (local)

```bash
pytest tests/ -m "gui" -v
```

Runs only the ~50 GUI tests (requires display).

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

**Purpose**: Mark tests requiring wxPython display (`wx.App`, `wx.Frame`, `wx.Dialog`).

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

**Files with GUI tests** (v3.2.1):
- `tests/unit/presentation/widgets/test_timer_combobox.py` (40+ tests, 5 classes)
- `tests/infrastructure/test_view_manager.py` (10+ tests)

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
├── infrastructure/            # Infrastructure tests
│   └── test_view_manager.py  # ⚠️ GUI tests (10+)
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

**Cause**: `pytest.ini` not configured or outdated.

**Solution**: Verify `pytest.ini` contains:
```ini
markers =
    gui: Tests requiring wxPython display (skip in headless CI with -m "not gui")
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
- [CHANGELOG.md](../CHANGELOG.md) — Test suite evolution history

---

**Last Updated**: 24 Febbraio 2026 (v3.5.0)  
**Maintainer**: Nemex81  
**Test Framework**: pytest 7.0+  
**Coverage Tool**: pytest-cov 4.0+
