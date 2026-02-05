# API Documentation

## Public API Reference

### GameController

Main application controller for game operations.

```python
from src.infrastructure.di_container import DIContainer

container = DIContainer()
controller = container.get_game_controller()
```

#### Methods

##### `start_new_game(difficulty: str = "easy", deck_type: str = "french") -> str`

Start a new game with specified configuration.

**Parameters:**
- `difficulty`: Game difficulty ("easy", "medium", "hard")
- `deck_type`: Type of deck ("french", "neapolitan")

**Returns:**
- Formatted string describing initial game state

**Example:**
```python
formatted_state = controller.start_new_game(difficulty="easy", deck_type="french")
print(formatted_state)
```

##### `execute_move(action: str, source_pile: Optional[str] = None, source_index: Optional[int] = None, target_pile: Optional[str] = None, target_index: Optional[int] = None) -> tuple[bool, str]`

Execute a game move.

**Parameters:**
- `action`: Action type ("draw", "recycle", "move_to_foundation")
- `source_pile`: Source pile type (when moving cards)
- `source_index`: Source pile index
- `target_pile`: Target pile type (when moving cards)
- `target_index`: Target pile index

**Returns:**
- Tuple of (success: bool, message: str)

**Example:**
```python
success, message = controller.execute_move("draw")
if success:
    print(f"Success: {message}")
else:
    print(f"Error: {message}")
```

##### `get_current_state_formatted() -> str`

Get formatted current game state.

**Returns:**
- Formatted string describing current game state

**Example:**
```python
state = controller.get_current_state_formatted()
print(state)
```

##### `get_cursor_position_formatted() -> str`

Get formatted cursor position.

**Returns:**
- Description of current cursor position

### GameFormatter

Formats game state for presentation.

```python
from src.presentation.game_formatter import GameFormatter

formatter = GameFormatter(language="it")
```

#### Methods

##### `format_game_state(state: GameState) -> str`

Format complete game state as text.

**Parameters:**
- `state`: Current game state

**Returns:**
- Formatted string describing game state

##### `format_cursor_position(state: GameState) -> str`

Format cursor position for screen reader.

**Parameters:**
- `state`: Current game state with cursor

**Returns:**
- Description of current cursor position

##### `format_move_result(success: bool, message: str) -> str`

Format move result for feedback.

**Parameters:**
- `success`: Whether move was successful
- `message`: Result message

**Returns:**
- Formatted feedback string

### DIContainer

Dependency injection container.

```python
from src.infrastructure.di_container import DIContainer

container = DIContainer()
```

#### Methods

##### `get_game_controller() -> GameController`

Get or create GameController instance.

##### `get_game_service() -> GameService`

Get or create GameService instance.

##### `get_formatter(language: str = "it") -> GameFormatter`

Get or create GameFormatter instance.

##### `get_move_validator() -> MoveValidator`

Get or create MoveValidator instance.

##### `clear() -> None`

Clear all cached instances.

## Domain Models

### GameState

Immutable game state representation.

**Fields:**
- `foundations`: Tuple of 4 foundation piles
- `tableaus`: Tuple of 7 tableau piles
- `stock`: Stock pile
- `waste`: Waste pile
- `status`: Game status (NOT_STARTED, IN_PROGRESS, WON, LOST)
- `moves_count`: Number of moves made
- `score`: Current score
- `cursor`: Current cursor position
- `selection`: Current selection state
- `config`: Game configuration

### Card

Immutable card representation.

**Fields:**
- `rank`: Card rank (ACE, TWO, ..., KING)
- `suit`: Card suit (HEARTS, DIAMONDS, CLUBS, SPADES)

**Methods:**
- `color() -> str`: Get card color ("red" or "black")
- `value() -> int`: Get card numeric value
- `can_stack_on_foundation(target: Optional[Card]) -> bool`: Check if can stack on foundation
- `can_stack_on_tableau(target: Optional[Card]) -> bool`: Check if can stack on tableau

## Usage Examples

### Basic Game Flow

```python
from src.infrastructure.di_container import DIContainer

# Initialize container
container = DIContainer()
controller = container.get_game_controller()

# Start new game
formatted_state = controller.start_new_game()
print(formatted_state)

# Draw cards from stock
success, message = controller.execute_move("draw")
print(message)

# Get current state
current_state = controller.get_current_state_formatted()
print(current_state)
```

### Custom Game Configuration

```python
# Start game with Italian deck on hard difficulty
formatted_state = controller.start_new_game(
    difficulty="hard",
    deck_type="neapolitan"
)
```

### Error Handling

```python
# Execute move and handle errors
success, message = controller.execute_move("move_to_foundation",
                                          source_pile="tableau",
                                          source_index=0,
                                          target_index=0)

if not success:
    print(f"Move failed: {message}")
else:
    print(f"Move successful: {message}")
```

## Type Hints

All public API methods include full type hints for IDE support:

```python
def execute_move(
    self,
    action: str,
    source_pile: Optional[str] = None,
    source_index: Optional[int] = None,
    target_pile: Optional[str] = None,
    target_index: Optional[int] = None,
) -> tuple[bool, str]:
    ...
```

## Thread Safety

GameState is immutable and thread-safe. However, GameController maintains mutable state and should not be shared between threads without synchronization.
