# 🏗️ ARCHITECTURE.md - [Project Name]

> **Architectural documentation for [project-name]**  
> Last Major Update: YYYY-MM-DD (v[X.Y.Z])

---

## 📋 Document Purpose

This document describes the **current architecture** of [project-name].

**Target Audience**:
- New developers (onboarding)
- Contributors (understanding design decisions)
- Maintainers (consistency enforcement)
- Future you (remembering why things are this way)

**What's Here**:
- High-level system overview
- Layer architecture & dependency rules
- Key patterns & conventions
- Directory structure & organization
- Decision rationale for major architectural choices

**What's NOT Here**:
- Implementation details (see source code + inline comments)
- API reference (see `API.md`)
- Feature specifications (see `PLAN_*.md` in docs/)
- Step-by-step tutorials (see README.md)

---

## 🎯 System Overview

### What This Project Does

[1-2 paragraphs explaining:
- Project purpose
- Target users
- Main functionality
- Key differentiators]

**Example**:
> Solitario Classico Accessibile is a fully keyboard-navigable, screen-reader-friendly implementation of Klondike Solitaire. It provides TTS feedback for every game action, making the classic card game playable by blind and visually impaired users without compromising gameplay depth.

### Architectural Paradigms

- **[Paradigm 1]**: [Brief description, why chosen]
- **[Paradigm 2]**: [Brief description, benefits]
- **[Paradigm 3]**: [If applicable]

**Example**:
- **Clean Architecture**: Strict separation of concerns with dependency inversion. Domain logic isolated from UI frameworks.
- **Domain-Driven Design**: Business rules (card game logic) independent of presentation layer.
- **Accessibility-First**: TTS and keyboard navigation are first-class features, not add-ons.
- **Test-Driven Development**: Core logic has >85% coverage, ensuring regression-free evolution.

### Tech Stack

**Core**:
- **[Language]**: [Version] - [Why chosen]
- **[Framework 1]**: [Version] - [Role in system]
- **[Framework 2]**: [Version] - [Role in system]

**Testing**:
- **[Testing Framework]**: [Version] - [Coverage tool if different]
- **[Mocking/Fixtures]**: [If used]

**Infrastructure**:
- **[Tool/Service 1]**: [Role]
- **[Tool/Service 2]**: [Role]

**Example**:
**Core**:
- **Python**: 3.10+ - Type hints, modern syntax, broad library ecosystem
- **wxPython**: 4.1.1 - Cross-platform GUI, mature, accessible
- **Pyttsx3**: 2.90 - Text-to-speech engine integration

**Testing**:
- **Pytest**: 7.4+ - Fixture-based testing, parametrization support
- **Coverage.py**: Code coverage measurement

**Infrastructure**:
- **JSON**: Settings persistence (human-readable, versionable)
- **Git**: Version control with conventional commits

---

## 🏛️ Layer Architecture

### Overview

[Brief explanation of layer separation philosophy - 2-3 sentences]

**Example**:
> The system follows Clean Architecture principles with strict dependency rules. Each layer has a clear responsibility and can only depend on layers "below" it. The Domain layer is the heart of the system and has ZERO dependencies on frameworks or external libraries.

### Dependency Diagram

```
┌──────────────────────────────────────────┐
│         PRESENTATION LAYER                       │
│  (UI Panels, Formatters, TTS, Accessibility)    │
│  Files: test.py, *_panel.py, *_formatter.py     │
└──────────────────────────────────────────┘
                 ↓ depends on
┌──────────────────────────────────────────┐
│        APPLICATION LAYER                         │
│  (Controllers, Use Cases, Coordinators)         │
│  Files: *_controller.py, dialog_manager.py      │
└──────────────────────────────────────────┘
                 ↓ depends on
┌──────────────────────────────────────────┐
│          DOMAIN LAYER                           │
│  (Entities, Services, Business Rules)           │
│  ← NO dependencies on outer layers            │
│  Files: game_engine.py, card.py, deck.py        │
└──────────────────────────────────────────┘
                 ↑ used by
┌──────────────────────────────────────────┐
│      INFRASTRUCTURE LAYER                        │
│  (Storage, External APIs, Framework Code)       │
│  Files: wx_dialog_provider.py, json_storage.py  │
└──────────────────────────────────────────┘
```

### Layer Details

#### Domain Layer (`src/domain/`)

**Purpose**: 
[What lives here - pure business logic, framework-independent]

**Components**:
- **Models** (`models/`): [Role - entities, value objects]
- **Services** (`services/`): [Role - domain services, complex business logic]
- **[Other directories]**: [If applicable]

**Dependency Rules**:
- ✅ **Can depend on**: Other domain components, Python standard library only
- ❌ **Cannot depend on**: Application, Infrastructure, Presentation, external frameworks

**Key Principle**:
[Explain domain isolation philosophy in 1-2 sentences]

**Example Code**:
```python
# domain/models/card.py
class Card:
    """Pure domain entity - no UI, no persistence logic."""
    def __init__(self, rank: str, suit: str):
        self.rank = rank
        self.suit = suit
    
    def is_valid_move_to(self, target: 'Card') -> bool:
        """Business rule: card stacking logic."""
        # Pure logic, no side effects
        pass
```

**Files in This Layer**:
- `models/card.py` - Card entity
- `models/deck.py` - Deck aggregate
- `services/game_engine.py` - Core game rules
- `services/scoring.py` - Scoring calculation

---

#### Application Layer (`src/application/`)

**Purpose**: 
[Coordinates domain logic, orchestrates use cases, no UI concerns]

**Components**:
- **Controllers** (`*_controller.py`): [Orchestrate workflows]
- **Services** (if applicable): [Application-level services]
- **[Other]**: [If applicable]

**Dependency Rules**:
- ✅ **Can depend on**: Domain layer, Python stdlib
- ❌ **Cannot depend on**: Presentation, Infrastructure frameworks (only abstractions)

**Key Principle**:
[Use case orchestration, no business logic here]

**Example Code**:
```python
# application/gameplay_controller.py
class GameplayController:
    """Orchestrates gameplay use cases."""
    def __init__(self, game_engine: GameEngine):
        self.engine = game_engine  # Domain dependency
    
    def handle_move_card(self, from_pile: str, to_pile: str):
        """Use case: move card between piles."""
        # Delegates to domain, coordinates responses
        result = self.engine.move_card(from_pile, to_pile)
        return result  # No UI logic here
```

**Files in This Layer**:
- `gameplay_controller.py` - Gameplay orchestration
- `options_controller.py` - Settings management
- `dialog_manager.py` - Dialog coordination (async patterns)

---

#### Infrastructure Layer (`src/infrastructure/`)

**Purpose**: 
[Framework code, external integrations, persistence, UI framework bindings]

**Components**:
- **UI** (`ui/`): [wxPython-specific code]
- **Storage** (`storage/`): [JSON persistence, file I/O]
- **[Other]**: [External APIs, etc.]

**Dependency Rules**:
- ✅ **Can depend on**: Domain (implements domain interfaces), external frameworks
- ❌ **Cannot depend on**: Application (inverted dependency)

**Key Principle**:
[All framework/library-specific code lives here, easily replaceable]

**Example Code**:
```python
# infrastructure/ui/wx_dialog_provider.py
import wx

class WxDialogProvider:
    """wxPython-specific dialog implementation."""
    def show_yes_no_async(self, message: str, callback):
        """Framework-specific async dialog."""
        dialog = wx.MessageDialog(None, message, style=wx.YES_NO)
        # wxPython-specific code here
        pass
```

**Files in This Layer**:
- `ui/wx_dialog_provider.py` - wxPython dialogs
- `ui/view_manager.py` - Panel lifecycle management
- `storage/json_settings.py` - Settings persistence

---

#### Presentation Layer (`src/presentation/`)

**Purpose**: 
[Formatting output, TTS messages, UI panels, user interaction]

**Components**:
- **Formatters** (`formatters/`): [Convert domain data to user-facing strings]
- **Panels** (`*_panel.py`): [UI views, event handlers]
- **[Other]**: [If applicable]

**Dependency Rules**:
- ✅ **Can depend on**: Application, Domain (for data), Infrastructure (for UI framework)
- ❌ **Cannot depend on**: Other presentation components directly

**Key Principle**:
[All user-facing text and UI logic here, domain stays UI-agnostic]

**Example Code**:
```python
# presentation/formatters/card_formatter.py
class CardFormatter:
    """Formats card data for TTS/display."""
    def format_card(self, card: Card) -> str:
        """Converts domain Card to Italian TTS string."""
        return f"{card.rank} di {card.suit}"
    
    def format_move_feedback(self, result: MoveResult) -> str:
        """Formats move result for accessibility."""
        # Human-readable, localized messages
        pass
```

**Files in This Layer**:
- `formatters/card_formatter.py` - Card display strings
- `formatters/score_formatter.py` - Score display
- `test.py` - Main application controller (wxPython app)
- `menu_panel.py`, `gameplay_panel.py` - UI views

---

## 🔒 Dependency Rules

### The Golden Rule

> **Dependencies always point INWARD.**  
> The Domain layer is the center and has ZERO outward dependencies.  
> Outer layers depend on inner layers, NEVER the reverse.

**Rationale**:
- Domain logic testable without UI/frameworks
- Framework changes (wxPython → Qt) don't break business rules
- Business rules evolve independently of infrastructure

### Allowed Dependencies

```
Presentation → Application → Domain
Infrastructure → Domain (implements domain interfaces)
Presentation → Infrastructure (for UI framework access)
```

### Forbidden Dependencies

```
Domain → Application      ❌ (domain is independent)
Domain → Infrastructure   ❌ (no framework coupling)
Domain → Presentation     ❌ (no UI concerns in domain)
Application → Presentation ❌ (use interfaces/callbacks)
```

### Common Violations to Avoid

#### 1. Domain Importing UI Frameworks

**❌ DON'T**:
```python
# domain/services/game_engine.py
import wx  # ❌ WRONG - domain depends on UI framework

class GameEngine:
    def show_victory_dialog(self):
        wx.MessageBox("You won!")  # ❌ Domain doing UI
```

**✅ DO**:
```python
# domain/services/game_engine.py
class GameEngine:
    def check_victory(self) -> bool:
        """Returns True if game won (pure logic)."""
        return all(pile.is_complete() for pile in self.foundations)

# presentation/gameplay_panel.py
if self.engine.check_victory():  # ✅ UI layer checks domain
    self.show_dialog("You won!")   # ✅ UI layer handles dialog
```

#### 2. Application Layer Doing Business Logic

**❌ DON'T**:
```python
# application/gameplay_controller.py
class GameplayController:
    def move_card(self, card, target):
        # ❌ Business logic in application layer
        if card.rank == target.rank - 1 and card.color != target.color:
            target.add_card(card)
```

**✅ DO**:
```python
# domain/services/game_engine.py
class GameEngine:
    def move_card(self, card, target):
        """Business logic in domain."""
        if self._is_valid_move(card, target):  # ✅ Domain logic
            target.add_card(card)

# application/gameplay_controller.py
class GameplayController:
    def handle_move(self, from_pile, to_pile):
        """Orchestrates, delegates to domain."""
        self.engine.move_card(from_pile, to_pile)  # ✅ Delegates
```

#### 3. Hardcoded UI Strings in Domain

**❌ DON'T**:
```python
# domain/services/game_engine.py
class GameEngine:
    def get_status(self) -> str:
        return "Hai vinto!"  # ❌ Localized string in domain
```

**✅ DO**:
```python
# domain/services/game_engine.py
class GameEngine:
    def get_status(self) -> GameStatus:
        return GameStatus.VICTORY  # ✅ Domain enum

# presentation/formatters/game_formatter.py
class GameFormatter:
    def format_status(self, status: GameStatus) -> str:
        return {GameStatus.VICTORY: "Hai vinto!"}[status]  # ✅ Presentation
```

---

## 🎓 Key Architectural Patterns

### Pattern 1: [Pattern Name]

**Where Used**: [Files/components that implement this pattern]

**Purpose**: [What problem this pattern solves]

**Structure**:
```python
# Example implementation
[5-10 lines showing pattern usage]
```

**Rationale**: [Why this pattern is appropriate here]

**Example**:
### Pattern 1: Deferred UI Transitions

**Where Used**: `test.py` (main app controller)

**Purpose**: Avoid nested event loops when swapping wxPython panels during event handling

**Structure**:
```python
class MainApp:
    def on_esc_pressed(self):
        """Event handler - returns immediately."""
        if self.confirm_abandon():
            self.app.CallAfter(self._safe_return_to_menu)  # Deferred
    
    def _safe_return_to_menu(self):
        """Executed after event handler completes."""
        self.view_manager.show_panel('menu')  # Safe context
```

**Rationale**: Direct panel swaps during event handlers cause `RuntimeError: wxYield called recursively`. Deferring with `CallAfter()` ensures transition happens in safe idle context.

---

### Pattern 2: [Another Pattern]

[Same structure as Pattern 1]

---

### Pattern 3: [Another Pattern]

[Same structure]

---

## 📂 Directory Structure

### Full Tree

```
project-root/
├── src/
│   ├── domain/                  # Core business logic (framework-independent)
│   │   ├── models/              # Entities, value objects
│   │   │   ├── card.py
│   │   │   ├── deck.py
│   │   │   └── pile.py
│   │   └── services/            # Domain services
│   │       ├── game_engine.py
│   │       ├── scoring.py
│   │       └── game_settings.py
│   ├── application/             # Use cases, controllers
│   │   ├── gameplay_controller.py
│   │   ├── options_controller.py
│   │   ├── dialog_manager.py
│   │   └── timer_manager.py
│   ├── infrastructure/          # External concerns (frameworks, I/O)
│   │   ├── ui/                  # UI framework code
│   │   │   ├── wx_dialog_provider.py
│   │   │   ├── view_manager.py
│   │   │   └── widget_factory.py
│   │   └── storage/             # Persistence
│   │       └── json_settings.py
│   └── presentation/            # Formatters, UI views
│       ├── formatters/
│       │   ├── card_formatter.py
│       │   ├── score_formatter.py
│       │   └── options_formatter.py
│       ├── menu_panel.py
│       └── gameplay_panel.py
├── tests/
│   ├── unit/                   # Isolated unit tests
│   │   ├── test_card.py
│   │   ├── test_game_engine.py
│   │   └── test_scoring.py
│   └── integration/            # Integration tests
│       └── test_gameplay_flow.py
├── docs/                       # Documentation
│   ├── ARCHITECTURE.md         # This file
│   ├── API.md                  # Public API reference
│   ├── PLAN_*.md               # Implementation plans
│   └── TEMPLATE_*.md           # Document templates
├── test.py                     # Application entry point
├── requirements.txt
├── CHANGELOG.md
├── README.md
└── .gitignore
```

### Directory Responsibilities

| Directory | Goes Here | Doesn't Go Here | Naming |
|-----------|-----------|-----------------|--------|
| `src/domain/` | Business logic, entities, domain services, business rules | ❌ UI code, DB/file I/O, external lib imports (except stdlib), localized strings | `PascalCase` classes, `snake_case` methods |
| `src/application/` | Use case orchestration, controllers, application services, workflow management | ❌ Business logic (in domain), UI rendering (in presentation), framework code (in infrastructure) | `*_controller.py`, `*_manager.py` |
| `src/infrastructure/` | Framework integrations (wxPython, pyttsx3), persistence (JSON, DB), external APIs | ❌ Business logic, domain entities | Prefix framework: `wx_*`, `json_*`. Suffix role: `*_provider.py`, `*_adapter.py` |
| `src/presentation/` | UI panels/views, formatters (domain → user strings), TTS templates, event handlers | ❌ Business logic, direct domain manipulation | `*_panel.py`, `*_formatter.py` |
| `tests/` | **unit/**: Single component tests (domain, services). **integration/**: Multi-component tests. Fixtures, mocks. | N/A | `test_*.py` files, `test_*()` functions (pytest) |

---

## 🔄 Data Flow

### Typical Request Flow

[Describe how a user action flows through the layers]

**Example: User Presses Key to Move Card**

```
1. [Presentation] GameplayPanel.on_key_down(event)
   │ User pressed 'M' key
   │
   ↓ delegates to
   │
2. [Application] GameplayController.handle_move_card()
   │ Orchestrates move workflow
   │
   ↓ calls domain logic
   │
3. [Domain] GameEngine.move_card(from_pile, to_pile)
   │ Validates move, applies business rules
   │ Returns MoveResult(success, reason)
   ↑
   │ result propagates back
   │
4. [Application] GameplayController processes result
   │ Updates application state
   │
   ↓ returns to presentation
   │
5. [Presentation] GameplayPanel refreshes UI
   │ Formats result with CardFormatter
   │ Announces via TTS: "7 di Coppe spostato su 8 di Picche"
   │ Updates visual display
```

### Sequence Diagram (Optional)

[ASCII sequence diagram for complex flows]

```
User    Panel         Controller      Engine       Formatter
 │       │               │              │             │
 │--M--> │               │              │             │
 │       │--move_card-->│              │             │
 │       │               │--move_card->│             │
 │       │               │<--result----│             │
 │       │               │--get_msg----------->     │
 │       │               │<--formatted_msg----------│
 │       │<--result-----│              │             │
 │<--TTS-│               │              │             │
 │       │               │              │             │
```

---

## ♿ Accessibility Architecture

[If accessibility is a core requirement - otherwise remove this section]

### Principles

- **TTS-First Design**: All game state communicated via text-to-speech
- **Keyboard-Only Navigation**: Zero mouse dependency
- **Screen Reader Compatibility**: Tested with NVDA, JAWS support
- **Clear Audio Feedback**: Every action produces descriptive TTS message

### Implementation

#### TTS Strategy

**Pattern**: Centralized TTS via `speak()` helper

```python
# Common pattern across presentation layer
def speak(message: str, interrupt: bool = False):
    """Announces message via screen reader."""
    if interrupt:
        # Stop current speech, announce immediately
        tts_engine.stop()
    tts_engine.say(message)
```

**Message Guidelines**:
- Italian language, clear and concise
- Action → Result format ("Hai pescato: 7 di Coppe")
- Error messages explain WHY ("Non puoi posare questa carta: colore sbagliato")

#### Keyboard Navigation

**Pattern**: Single-key commands + arrow navigation

- **Arrows**: Navigate between piles/options
- **Enter**: Select/confirm
- **Esc**: Cancel/back
- **Single letters**: Quick actions (P=pesca, N=nuova partita, etc.)

**All commands documented in**: README.md section "Comandi Tastiera"

#### Screen Reader Support

**Tested With**:
- NVDA 2023+ (primary)
- JAWS (secondary)

**Integration Points**:
- wxPython native accessibility hooks
- Manual TTS via pyttsx3 for game-specific feedback
- Focus management for panel transitions

---

## 🚨 Error Handling Strategy

### Philosophy

[How the project approaches error handling - fail fast, graceful degradation, etc.]

**Example**:
> Errors are caught at layer boundaries and converted to user-facing messages. Domain layer raises specific exceptions (InvalidMoveError), application layer catches and coordinates response, presentation layer formats error for TTS.

### Patterns

#### Domain Errors

**Strategy**: [How domain errors are handled]

```python
# domain/services/game_engine.py
class InvalidMoveError(Exception):
    """Raised when move violates game rules."""
    pass

def move_card(self, from_pile, to_pile):
    if not self._is_valid_move(...):
        raise InvalidMoveError("Card color/rank mismatch")
```

#### Infrastructure Errors

**Strategy**: [How I/O, network, etc. errors are handled]

```python
# infrastructure/storage/json_settings.py
try:
    with open(settings_path) as f:
        data = json.load(f)
except (FileNotFoundError, JSONDecodeError):
    # Graceful fallback to defaults
    data = self._default_settings()
```

#### User Errors

**Strategy**: [How invalid user actions are handled]

```python
# presentation/gameplay_panel.py
try:
    self.controller.move_card(...)
except InvalidMoveError as e:
    self.speak(f"Mossa non valida: {e}")  # User-friendly TTS
```

### Logging

**Strategy**: [Logging approach - levels, destinations, format]

**Example**:
- **DEBUG**: Detailed flow (navigation, state changes)
- **INFO**: Major events (game start, victory, settings changed)
- **WARNING**: Recoverable errors (invalid move, missing file)
- **ERROR**: Unrecoverable errors (crash, data corruption)

**Destination**: `logs/app.log` with rotation (5MB max, 5 backups)

---

## 🧪 Testing Strategy

### Approach

- **Testing Philosophy**: [TDD, BDD, or ad-hoc]
- **Coverage Target**: [Percentage, critical paths, etc.]
- **Test Pyramid**: [Unit heavy, integration light, E2E minimal]

**Example**:
- **TDD for domain logic**: Write test first, then implementation
- **Coverage target**: >85% for domain/application, >60% overall
- **Pyramid**: 80% unit, 15% integration, 5% manual acceptance

### Test Structure

#### Unit Tests (`tests/unit/`)

**What's Tested**:
- Domain entities (Card, Deck, Pile)
- Domain services (GameEngine, Scoring)
- Application controllers (in isolation with mocks)
- Formatters (pure functions)

**Example**:
```python
# tests/unit/test_card.py
def test_card_is_valid_move_to():
    """7 Rosso can stack on 8 Nero."""
    card1 = Card(rank=7, suit='Hearts', color='red')
    card2 = Card(rank=8, suit='Spades', color='black')
    assert card1.is_valid_move_to(card2) is True
```

#### Integration Tests (`tests/integration/`)

**What's Tested**:
- Multi-layer interactions (controller + domain + formatter)
- Persistence round-trips (save + load)
- End-to-end workflows (new game → move → victory)

**Example**:
```python
# tests/integration/test_gameplay_flow.py
def test_complete_game_flow():
    """User plays full game from start to victory."""
    controller = GameplayController(...)
    controller.new_game()
    # Simulate moves
    controller.move_card(...)
    # Assert victory state
    assert controller.check_victory() is True
```

#### Manual/Acceptance Tests

**Scenarios**:
- Full game with NVDA screen reader
- All keyboard shortcuts functional
- Settings persistence across app restarts
- Timer strict mode timeout behavior

---

## 📈 Evolution & Deprecated Patterns

### Version History (Major Architectural Changes)

[Document major refactorings, migrations, paradigm shifts]

**Example**:
- **v1.0.0** (2024-01): Initial Pygame implementation
- **v2.0.0** (2024-02): Migrated from Pygame to wxPython for better accessibility
- **v2.2.0** (2024-02): Introduced async dialog pattern (eliminated nested event loops)
- **v2.4.0** (2024-02): Added difficulty preset system with locked options

### Deprecated Patterns

#### Pattern: Synchronous ShowModal() Dialogs (Deprecated in v2.2.0)

**Was Used For**: Blocking dialogs (yes/no confirmations)

**Why Deprecated**: 
- Caused nested event loops
- Screen reader focus issues
- RuntimeError crashes on rapid interactions

**Migration Path**: 
Replace `ShowModal()` with async pattern:
```python
# OLD (v2.0-2.1)
result = dialog.ShowModal()
if result == wx.ID_YES:
    self.do_action()

# NEW (v2.2+)
def callback(confirmed: bool):
    if confirmed:
        self.do_action()

dialog_manager.show_yes_no_async(message, callback)
```

**Replaced By**: Semi-modal async dialog pattern (see "Key Patterns" section)

---

#### Pattern: [Another Deprecated Pattern]

[Same structure]

---

## 🎯 Decision Records (Optional)

[Lightweight Architecture Decision Records - use if formal ADRs needed]

### ADR-001: Use wxPython Over Pygame for UI

- **Status**: Accepted
- **Date**: 2024-02-10
- **Context**: Original Pygame implementation had poor screen reader support
- **Decision**: Migrate to wxPython for native OS accessibility
- **Consequences**: 
  - ✅ Better NVDA/JAWS integration
  - ✅ Native dialogs, menus, keyboard handling
  - ❌ Steeper learning curve (event-driven paradigm)
  - ❌ More boilerplate for UI components

---

### ADR-002: [Another Decision]

[Same structure]

---

## 📚 Related Documentation

**Internal**:
- `API.md` - Public API reference for GameEngine, Controllers
- `PLAN_*.md` - Implementation plans for features (in docs/)
- `CHANGELOG.md` - Version history with user-facing changes
- `README.md` - User guide, installation, keyboard commands

**External**:
- [wxPython Documentation](https://docs.wxpython.org/)
- [Clean Architecture (Uncle Bob)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)

---

## 🤝 Aggiornamento ARCHITECTURE.md

**Aggiorna quando**: nuovo layer, nuovo pattern architetturale, dependency rules changed, major refactoring (>10 file), directory reorganization.  
**Non aggiornare per**: singolo file added, bug fix, doc typo, test additions (a meno che nuova testing strategy).

**Workflow**: Code changes → Aggiorna sezioni rilevanti → Update "Last Major Update" se significativo → Review consistency (diagrammi match reality) → Commit `docs(architecture): [change]`

**Esempio commit**:
```
docs(architecture): Add deferred UI transition pattern

- New section in "Key Patterns"
- Updated "Common Violations" with examples
- Added rationale for CallAfter() usage
```

---

## 📌 Template Metadata

**Template Version**: v1.1 (ottimizzato -12.6%)  
**Created**: 2026-02-16  
**Last Updated**: 2026-02-22  
**Maintainer**: AI Assistant + Nemex81  
**Based On**: solitario-classico-accessibile project architecture  
**Philosophy**: Living document, evolves with codebase

---

## 🎯 Uso Template

1. **Copia**: `cp TEMPLATE_ARCHITECTURE.md ARCHITECTURE.md`
2. **Sostituisci placeholder**: `[Project Name]`, tech stack, layer details
3. **Rimuovi sezioni irrilevanti**: No ADRs? Rimuovi Decision Records. No accessibility core? Rimuovi Accessibility Architecture.
4. **Mantieni aggiornato**: Living document, evolve con codebase

**Sezioni MUST**: System Overview, Layer Architecture, Dependency Rules, Directory Structure  
**Sezioni OPTIONAL**: Accessibility (solo se core requirement), ADRs (solo se formal decisions), Event System (solo se event-driven)

Usa esempi codice reali dalla codebase, diagrammi ASCII semplici (non complex images), spiega WHY decisioni prese (rationale). Aggiorna quando architettura cambia: nuovo layer, dependency rules changed, major refactoring (>10 file).

**Good enough quando**: New developer capisce sistema in 30 min, major patterns documentati con esempi, dependency rules chiare, directory structure matches reality.

---

**End of Template**

**Happy Architecting! 🏗️**
