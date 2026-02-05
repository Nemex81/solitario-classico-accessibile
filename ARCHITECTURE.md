# Architecture Documentation

## Overview

Solitario Classico Accessibile follows a **layered architecture** inspired by Domain-Driven Design (DDD) principles, ensuring clean separation of concerns and high maintainability.

## Architecture Layers

```
┌─────────────────────────────────────────────┐
│         Presentation Layer                   │
│  (GameFormatter - Output formatting)         │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│        Application Layer                     │
│  (GameController, Commands - Use cases)      │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│          Domain Layer                        │
│  (Models, Rules, Services - Business logic)  │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│       Infrastructure Layer                   │
│  (DI Container, UI, Accessibility)           │
└─────────────────────────────────────────────┘
```

## Layer Descriptions

### 1. Domain Layer (`src/domain/`)

**Purpose**: Contains the core business logic and domain models. This layer is independent of external frameworks and infrastructure.

**Components**:

- **Models** (`domain/models/`)
  - `Card`: Immutable card representation with rank and suit
  - `GameState`: Immutable game state (foundations, tableaus, stock, waste)
  - `Pile`: Pile types and operations
  
- **Rules** (`domain/rules/`)
  - `MoveValidator`: Validates game moves according to Solitaire rules
  
- **Services** (`domain/services/`)
  - `GameService`: Orchestrates domain logic, manages game state transitions
  
- **Interfaces** (`domain/interfaces/`)
  - `protocols.py`: Protocol interfaces for dependency inversion

**Key Principles**:
- Immutable data structures (dataclasses with `frozen=True`)
- Pure functions with no side effects
- No dependencies on other layers
- Business rules are explicitly defined

### 2. Application Layer (`src/application/`)

**Purpose**: Coordinates use cases and orchestrates domain logic. Bridges the gap between domain and infrastructure.

**Components**:

- `GameController`: Main application controller
  - Manages game lifecycle
  - Coordinates domain services and presentation
  - Handles user actions and state updates
  
- `commands.py`: Command pattern implementation
  - `Command`: Abstract command interface
  - `MoveCommand`: Concrete command for moves
  - `CommandHistory`: Undo/redo functionality

**Responsibilities**:
- Use case orchestration
- Error handling and validation
- State management
- Transaction boundaries

### 3. Presentation Layer (`src/presentation/`)

**Purpose**: Formats domain data for display and accessibility.

**Components**:

- `GameFormatter`: Formats game state for screen readers
  - Italian language support
  - Accessibility-friendly descriptions
  - Cursor position formatting
  - Move result feedback

**Key Features**:
- Language-specific formatting
- Screen reader optimization
- Clear, concise descriptions

### 4. Infrastructure Layer (`src/infrastructure/`)

**Purpose**: Provides technical capabilities and external integrations.

**Components**:

- `DIContainer`: Dependency injection container
  - Singleton service management
  - Component lifecycle management
  - Dependency resolution
  
- `ui/`: User interface components (pygame)
  
- `accessibility/`: Screen reader integration

## Data Flow

```
User Input
    ↓
GameController (Application)
    ↓
GameService (Domain)
    ↓
MoveValidator (Domain)
    ↓
GameState (Domain)
    ↓
GameFormatter (Presentation)
    ↓
Output to User
```

## Design Patterns

### 1. Immutable State Pattern

All game state is immutable:

```python
@dataclass(frozen=True)
class GameState:
    foundations: Tuple[Tuple[str, ...], ...]
    tableaus: Tuple[Tuple[str, ...], ...]
    # ...
```

**Benefits**:
- Thread-safe
- Predictable behavior
- Easy undo/redo
- Simplified testing

### 2. Command Pattern

Used for undo/redo functionality:

```python
class Command(ABC):
    @abstractmethod
    def execute(self, state: GameState) -> GameState: ...
    
    @abstractmethod
    def undo(self, state: GameState) -> GameState: ...
```

**Benefits**:
- Decouples action from execution
- History tracking
- Undo/redo support

### 3. Dependency Injection

DIContainer manages all dependencies:

```python
container = DIContainer()
controller = container.get_game_controller()
```

**Benefits**:
- Loose coupling
- Testability
- Flexibility
- Single source of truth for dependencies

### 4. Protocol-based Interfaces

Using Python's `Protocol` for structural subtyping:

```python
class GameServiceProtocol(Protocol):
    def new_game(self, config: GameConfiguration) -> GameState: ...
```

**Benefits**:
- Interface segregation
- Dependency inversion
- Type safety without inheritance

## Testing Strategy

### Unit Tests (`tests/unit/`)

- Test individual components in isolation
- Mock dependencies
- Fast execution
- High coverage (>90% per module)

### Integration Tests (`tests/integration/`)

- Test component interactions
- Real dependencies (no mocks)
- End-to-end scenarios
- Validate data flow

**Coverage Target**: >80% overall (achieved: 92.57%)

## Quality Metrics

| Metric | Target | Actual |
|--------|--------|--------|
| Test Coverage | >80% | 92.57% |
| Type Hints | 100% | 100% |
| Cyclomatic Complexity | <10 | <8 |
| Tests Passing | 100% | 140/140 |

## Key Architectural Decisions

See [ADR/](ADR/) directory for detailed Architecture Decision Records:

1. **001-layered-architecture.md**: Why layered architecture
2. **002-immutable-state.md**: Why immutable game state
3. **003-dependency-injection.md**: Why DI container

## Dependencies Between Layers

```
Infrastructure → Application → Domain ← Presentation
                     ↓
                  Domain
```

**Rules**:
- Domain has NO dependencies
- Application depends only on Domain
- Presentation depends only on Domain
- Infrastructure can depend on all layers

## Future Enhancements

1. **Event Sourcing**: Track all state changes as events
2. **CQRS**: Separate read and write models
3. **Repository Pattern**: Abstract data persistence
4. **Saga Pattern**: Complex multi-step operations
5. **Observer Pattern**: UI reactivity

## References

- [Clean Architecture - Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design - Eric Evans](https://www.domainlanguage.com/ddd/)
- [Python Type Hints - PEP 484](https://www.python.org/dev/peps/pep-0484/)
