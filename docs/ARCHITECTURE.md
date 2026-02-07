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
