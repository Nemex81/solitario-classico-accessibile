# Architettura del Sistema

## 📐 Panoramica

Il Solitario Classico Accessibile utilizza una **Clean Architecture** (architettura a cipolla) che separa le responsabilità in livelli distinti, garantendo:

- **Testabilità**: Ogni componente può essere testato in isolamento
- **Manutenibilità**: Le modifiche in un livello non impattano gli altri
- **Flessibilità**: Facile sostituzione di componenti (es. UI)
- **Indipendenza dal framework**: Il core non dipende da librerie esterne

## 🏛️ Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                  GameFormatter                       │    │
│  │  - Formattazione stato per screen reader            │    │
│  │  - Localizzazione italiano                          │    │
│  │  - Output accessibile                               │    │
│  └─────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│                    Application Layer                         │
│  ┌───────────────────┐  ┌────────────────────────────┐     │
│  │  GameController   │  │     Command Pattern        │     │
│  │  - Orchestrazione │  │  - MoveCommand             │     │
│  │  - Use cases      │  │  - DrawCommand             │     │
│  │  - State mgmt     │  │  - CommandHistory          │     │
│  └───────────────────┘  └────────────────────────────┘     │
├─────────────────────────────────────────────────────────────┤
│                      Domain Layer                            │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────────────┐   │
│  │   Models    │  │   Rules     │  │    Services       │   │
│  │  - Card     │  │  - Move     │  │  - GameService    │   │
│  │  - Pile     │  │    Validator│  │  - Orchestration  │   │
│  │  - GameState│  │             │  │                   │   │
│  └─────────────┘  └─────────────┘  └───────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                 Protocol Interfaces                  │   │
│  │  - MoveValidatorProtocol                            │   │
│  │  - GameServiceProtocol                              │   │
│  │  - FormatterProtocol                                │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                   Infrastructure Layer                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   DIContainer                        │   │
│  │  - Dependency Injection                             │   │
│  │  - Component lifecycle                              │   │
│  │  - Configuration                                    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Struttura delle Directory

```
src/
├── __init__.py
├── application/           # Application Layer
│   ├── __init__.py
│   ├── commands.py       # Command pattern per undo/redo
│   └── game_controller.py # Controller principale
├── domain/               # Domain Layer (Core)
│   ├── __init__.py
│   ├── interfaces/       # Protocol interfaces
│   │   ├── __init__.py
│   │   └── protocols.py
│   ├── models/           # Entità di dominio
│   │   ├── __init__.py
│   │   ├── card.py      # Card, Rank, Suit
│   │   ├── game_state.py # GameState immutabile
│   │   └── pile.py      # Pile, PileType
│   ├── rules/           # Business rules
│   │   ├── __init__.py
│   │   └── move_validator.py
│   └── services/        # Domain services
│       ├── __init__.py
│       └── game_service.py
├── infrastructure/       # Infrastructure Layer
│   ├── __init__.py
│   ├── accessibility/   # Screen reader support
│   ├── di_container.py  # Dependency injection
│   └── ui/              # User interface
└── presentation/        # Presentation Layer
    ├── __init__.py
    └── game_formatter.py
```

## 🧩 Componenti Principali

### Domain Layer

#### Card (`src/domain/models/card.py`)

Rappresentazione immutabile di una carta da gioco.

```python
@dataclass(frozen=True)
class Card:
    rank: Rank
    suit: Suit
    
    def can_stack_on_foundation(self, other: Optional[Card]) -> bool: ...
    def can_stack_on_tableau(self, other: Optional[Card]) -> bool: ...
```

#### GameState (`src/domain/models/game_state.py`)

Stato immutabile del gioco con pattern copy-on-write.

```python
@dataclass(frozen=True)
class GameState:
    foundations: Tuple[Tuple[str, ...], ...]
    tableaus: Tuple[Tuple[str, ...], ...]
    stock: Tuple[str, ...]
    waste: Tuple[str, ...]
    status: GameStatus
    
    def with_move(self, **kwargs) -> GameState: ...
```

#### MoveValidator (`src/domain/rules/move_validator.py`)

Validazione delle mosse secondo le regole del Klondike.

```python
class MoveValidator:
    def can_move_to_foundation(card, foundation_index, state) -> bool: ...
    def can_move_to_tableau(cards, tableau_index, state) -> bool: ...
```

#### GameService (`src/domain/services/game_service.py`)

Orchestrazione della logica di gioco.

```python
class GameService:
    def new_game(config: GameConfiguration) -> GameState: ...
    def move_to_foundation(state, source, target) -> GameState: ...
    def draw_from_stock(state) -> GameState: ...
```

### Application Layer

#### GameController (`src/application/game_controller.py`)

Coordina i use cases e gestisce lo stato dell'applicazione.

```python
class GameController:
    def start_new_game(difficulty, deck_type) -> str: ...
    def execute_move(action, source, target) -> Tuple[bool, str]: ...
    def get_current_state_formatted() -> str: ...
```

#### Command Pattern (`src/application/commands.py`)

Supporto per undo/redo tramite Command pattern.

```python
class Command(ABC):
    def execute(state: GameState) -> GameState: ...
    def undo(state: GameState) -> GameState: ...

class CommandHistory:
    def execute(command, state) -> GameState: ...
    def undo(state) -> GameState: ...
    def redo(state) -> GameState: ...
```

### Presentation Layer

#### GameFormatter (`src/presentation/game_formatter.py`)

Formattazione accessibile per screen reader.

```python
class GameFormatter:
    def format_game_state(state) -> str: ...
    def format_cursor_position(state) -> str: ...
    def format_move_result(success, message) -> str: ...
```

### Infrastructure Layer

#### DIContainer (`src/infrastructure/di_container.py`)

Container per dependency injection.

```python
class DIContainer:
    def get_game_controller() -> GameController: ...
    def get_game_service() -> GameService: ...
    def get_formatter() -> GameFormatter: ...
```

## 🔄 Flusso dei Dati

### Nuova Partita

```
User Input
    │
    ▼
GameController.start_new_game()
    │
    ▼
GameService.new_game()
    │
    ▼
Create immutable GameState
    │
    ▼
GameFormatter.format_game_state()
    │
    ▼
Screen Reader Output
```

### Esecuzione Mossa

```
User Input (action)
    │
    ▼
GameController.execute_move()
    │
    ▼
MoveValidator.validate()
    │
    ├── Invalid → Return error message
    │
    └── Valid ─────┐
                   ▼
          GameService.execute()
                   │
                   ▼
          New GameState (immutable)
                   │
                   ▼
          GameFormatter.format_result()
                   │
                   ▼
          Screen Reader Output
```

## 🎨 Design Patterns

### 1. Immutable State Pattern

Lo stato del gioco è immutabile. Ogni modifica crea un nuovo oggetto.

```python
# Invece di modificare lo stato esistente
state.score += 10  # ❌ Non funziona

# Si crea un nuovo stato
new_state = state.with_move(score=state.score + 10)  # ✅
```

**Vantaggi:**
- Thread safety
- Facilita undo/redo
- Debugging più semplice
- Nessun side effect

### 2. Command Pattern

Ogni azione è incapsulata in un oggetto Command.

```python
command = MoveCommand(source="tableau_0", target="foundation_0")
history.execute(command, state)
history.undo(state)  # Annulla
history.redo(state)  # Ripristina
```

**Vantaggi:**
- Undo/redo naturale
- Logging delle azioni
- Macro commands

### 3. Dependency Injection

Le dipendenze sono iniettate tramite container.

```python
container = DIContainer()
controller = container.get_game_controller()
```

**Vantaggi:**
- Testabilità (mock injection)
- Loose coupling
- Configurabilità

### 4. Protocol Interfaces

Definizione di interfacce tramite Python Protocol.

```python
class MoveValidatorProtocol(Protocol):
    def can_move_to_foundation(self, card, index, state) -> bool: ...
```

**Vantaggi:**
- Structural typing
- Nessuna ereditarietà richiesta
- Type checking statico

## 📊 Metriche di Qualità

| Metrica | Target | Attuale |
|---------|--------|---------|
| Test Coverage | ≥ 80% | 91.47% |
| Type Hints | 100% | ✅ |
| Complessità Ciclomatica | < 10 | ✅ |
| Linee per Metodo | < 20 | ✅ |

## 🔒 Principi SOLID

### Single Responsibility
- `GameFormatter`: solo formattazione
- `MoveValidator`: solo validazione
- `GameService`: solo orchestrazione

### Open/Closed
- Nuove regole aggiungibili senza modificare codice esistente
- Nuovi formatter possono essere creati

### Liskov Substitution
- Tutti i Command sono intercambiabili
- Validator può essere sostituito

### Interface Segregation
- Protocol separati per ogni responsabilità
- Client dipendono solo dalle interfacce necessarie

### Dependency Inversion
- Domain non dipende da Infrastructure
- Controller dipende da astrazioni (Protocol)

## 🎯 Deferred UI Transitions Pattern (v2.1)

### Overview

A critical architectural pattern for handling UI panel transitions in wxPython
applications. Ensures safe, crash-free transitions by deferring UI operations
until after event handlers complete.

### Problem Statement

Direct UI transitions from event handlers can cause:
- **Nested event loops**: wxPython processes events during UI operations
- **AssertionError**: `wx.GetApp()` returns None during certain lifecycle states
- **RuntimeError**: `wxYield called recursively` when SafeYield used improperly
- **Crashes/hangs**: Unpredictable behavior from synchronous UI manipulation

### Solution: self.app.CallAfter() Pattern

Use the wx.App instance method `CallAfter()` to defer UI transitions:

```python
# ✅ CORRECT: Deferred UI transition
def on_esc_pressed(self):
    """Event handler for ESC key."""
    result = self.show_dialog()
    if result:
        # Schedule UI transition for AFTER handler completes
        self.app.CallAfter(self._safe_return_to_menu)
    # Handler returns immediately

def _safe_return_to_menu(self):
    """Deferred callback - runs AFTER event handler completes."""
    # Safe context: no nested event loop
    self.view_manager.show_panel('menu')
    self.engine.reset_game()
```

### Pattern Flow

```
1. User Action → Event Handler
                    ↓
2. Event Handler → Dialog (modal, blocking)
                    ↓
3. User Confirms → self.app.CallAfter(deferred_method)
                    ↓
4. Handler Returns → Event processing completes
                    ↓
5. [wxPython Idle Loop]
                    ↓
6. Deferred Method → Panel swap, state reset
                    ↓
7. UI Updates Complete → Safe, no nested loops
```

### Why self.app.CallAfter() Works

1. **Direct Instance Method**: No `wx.GetApp()` global lookup needed
2. **Always Available**: `self.app` assigned before MainLoop starts
3. **No Timing Issues**: Python object always exists (not C++ dependent)
4. **Deferred Execution**: Runs in wxPython idle loop, safe context
5. **No Nested Loops**: Event handler completes before UI operations

### Anti-Patterns to AVOID

#### ❌ Anti-Pattern 1: wx.CallAfter()
```python
# WRONG: Global function, depends on wx.GetApp() timing
wx.CallAfter(self._safe_return_to_menu)
# May fail with: AssertionError: No wx.App created yet
```

**Problem**: `wx.CallAfter()` internally calls `wx.GetApp()` which may return
None during app initialization or certain lifecycle transitions.

#### ❌ Anti-Pattern 2: wx.SafeYield()
```python
# WRONG: Creates nested event loop
def show_panel(self, name):
    wx.SafeYield()  # Forces event processing
    panel.Hide()
    panel.Show()
# Causes: RuntimeError: wxYield called recursively
```

**Problem**: When called from deferred callback, creates second nested event
loop. wxPython detects recursion and raises RuntimeError.

#### ❌ Anti-Pattern 3: Direct Panel Swap from Handler
```python
# WRONG: Synchronous UI manipulation in event handler
def on_esc_pressed(self):
    result = self.show_dialog()
    if result:
        self.view_manager.show_panel('menu')  # Direct call
        self.engine.reset_game()
# Risk: Nested loops, timing issues, crashes
```

**Problem**: UI operations during event handling can trigger nested event
loops or access UI state at unsafe times.

### Decision Tree: When to Use Pattern

```
Is this a UI transition? (panel swap, dialog, etc.)
    ├─ NO → Direct call OK
    │       Example: Pure logic, calculations, validation
    │
    └─ YES → Check calling context
            ├─ Event handler (keyboard, timer, callback)
            │   └─ Use self.app.CallAfter(deferred_method)
            │
            ├─ Deferred callback (already in CallAfter context)
            │   └─ Direct call OK (safe context)
            │
            └─ Initialization (run(), on_init())
                └─ Direct call OK (before MainLoop starts)
```

### Implementation Guidelines

#### 1. Separate Event Handlers from Deferred Callbacks

```python
# Event Handler: Shows dialog, schedules defer
def show_abandon_game_dialog(self):
    """Handle ESC key - show dialog and defer transition."""
    result = self.dialog_manager.show_abandon_game_prompt()
    if result:
        self.app.CallAfter(self._safe_abandon_to_menu)

# Deferred Callback: Performs UI transition
def _safe_abandon_to_menu(self):
    """Deferred handler - safe panel transition."""
    self.view_manager.show_panel('menu')
    self.engine.reset_game()
```

#### 2. Name Deferred Callbacks Clearly

Use prefixes to indicate deferred execution:
- `_safe_*`: Deferred UI transition methods
- `_deferred_*`: General deferred operations
- `_on_*`: Event handlers (not deferred)

#### 3. Document Pattern in Docstrings

```python
def _safe_abandon_to_menu(self):
    """Deferred handler for abandon → menu transition.
    
    Called via self.app.CallAfter() from show_abandon_game_dialog().
    Executes AFTER event handler completes, preventing nested loops.
    
    IMPORTANT: Do NOT call directly from event handlers.
    Always use self.app.CallAfter(self._safe_abandon_to_menu).
    
    Version:
        v2.0.9: Uses self.app.CallAfter() pattern
        v2.1: Architectural integration and documentation
    """
```

### Version History

| Version | Change | Impact |
|---------|--------|--------|
| v2.0.3 | Added wx.SafeYield() | ❌ Caused crashes (nested loops) |
| v2.0.4 | Introduced wx.CallAfter() | ⚠️ Timing issues (wx.GetApp()) |
| v2.0.6 | Tried self.frame.CallAfter() | ❌ Version incompatibility |
| v2.0.7 | Reverted to wx.CallAfter() | ⚠️ Still had timing issues |
| v2.0.8 | Removed wx.SafeYield() | ✅ Fixed nested loop crash |
| v2.0.9 | **DEFINITIVE**: self.app.CallAfter() | ✅ Reliable, works always |
| v2.1 | Systematic integration | ✅ Complete architectural pattern |

### Current Implementation Status (v2.1)

#### ✅ test.py (Presentation Layer)
- 4/4 UI transitions use `self.app.CallAfter()`
- Pattern compliance: 100%
- All deferred methods documented

#### ✅ view_manager.py (Infrastructure Layer)
- No wx.SafeYield() (removed v2.0.8)
- Synchronous Hide/Show operations
- Safe for deferred callback context

#### ✅ Application Layer
- Zero instances of CallAfter (correct)
- Clean Architecture separation
- Business logic framework-independent

### Testing Validation

Manual testing scenarios for pattern verification:

#### Test 1: ESC Abandon Game
```
Steps:
1. Start game (Nuova Partita)
2. Press ESC during gameplay
3. Confirm "Sì" to abandon

Expected:
✅ Menu appears instantly
✅ No crash or hang
✅ Console: "Scheduling deferred transition" → "Executing deferred..."
✅ Game state reset properly
```

#### Test 2: Victory Decline Rematch
```
Steps:
1. Complete game (win)
2. Victory dialog appears
3. Click "No" to decline rematch

Expected:
✅ Menu appears instantly
✅ No crash or hang
✅ Smooth transition without flicker
```

#### Test 3: Timer STRICT Expiration
```
Steps:
1. Enable timer STRICT mode (if available)
2. Let timer expire during gameplay
3. Automatic transition to menu

Expected:
✅ Menu appears after timeout message
✅ No crash or hang
✅ Deferred callback executes correctly
```

### References

- **wxPython wx.App.CallAfter()**: Instance method, always available
- **wxPython wx.CallAfter()**: Global function, depends on wx.GetApp()
- **Pattern Documentation**: `docs/IMPLEMENTATION_TIMER_STRICT_MODE_SYSTEM_v2.1.md`
- **Audit Reports**: `docs/AUDIT_CALLAFTER_PATTERNS_v2.1.md`

### Summary

The Deferred UI Transitions Pattern is a critical architectural component
that ensures:
- ✅ Crash-free panel transitions
- ✅ No nested event loops
- ✅ Reliable timing (no wx.GetApp() dependency)
- ✅ Clean separation of event handling and UI operations
- ✅ Maintainable, documented codebase

**Always use `self.app.CallAfter()` for UI transitions from event handlers.**

---

*Document Version: 2.1*  
*Last Updated: 2026-02-14*
