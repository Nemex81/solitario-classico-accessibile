# 📚 API.md - [Project Name]

> **Public API Reference for [project-name]**  
> Version: v[X.Y.Z]  
> Last Updated: YYYY-MM-DD

---

## 📋 Document Purpose

This document provides a **reference guide for public APIs** across system layers. Focus is on interfaces that other layers or components call, not internal implementation details.

**Target Audience**:
- Developers working across layers (Domain ↔ Application ↔ Presentation)
- Maintainers needing API contracts without reading full source
- AI assistants (Copilot) suggesting correct API usage
- Future you remembering how components interact

**What's Here**:
- Public methods of critical classes (GameEngine, Controllers, etc.)
- Method signatures with parameters, return types, examples
- Common types (enums, dataclasses) used across layers
- Naming conventions and error handling patterns
- Real-world usage examples

**What's NOT Here**:
- Private/internal methods (prefixed with `_`)
- Implementation details (see source code + inline comments)
- Architecture rationale (see `ARCHITECTURE.md`)
- UI event handlers (too specific, see presentation code)
- Complete method catalog (only essential APIs documented)

**Philosophy**: *"If it's not called by other layers, it's not documented here."*

---

## 🗂️ Quick Index

### By Layer

**Domain Layer** (`src/domain/`):
- [GameEngine](#gameengine) - Core game logic
- [Card](#card) - Card entity
- [Deck](#deck) - Deck management  
- [Scoring](#scoring) - Score calculation
- [GameSettings](#gamesettings) - Game configuration

**Application Layer** (`src/application/`):
- [GameplayController](#gameplaycontroller) - Gameplay orchestration
- [OptionsController](#optionscontroller) - Settings management
- [TimerManager](#timermanager) - Timer logic (if applicable)

**Presentation Layer** (`src/presentation/`):
- [CardFormatter](#cardformatter) - Card display strings
- [ScoreFormatter](#scoreformatter) - Score display
- [Other formatters as needed]

### Alphabetical

[C](#c) | [D](#d) | [G](#g) | [O](#o) | [S](#s) | [T](#t)

---

## 🏛️ Domain Layer API

### GameEngine

**File**: `src/domain/services/game_engine.py`

**Purpose**: Core game logic for [game name]. Manages game state, validates moves, enforces business rules, checks victory/defeat conditions.

**Constructor**:
```python
GameEngine(settings: GameSettings = None)
```

**Parameters**:
- `settings` (GameSettings, optional): Game configuration (difficulty, rules). Defaults to standard settings if None.

**Example**:
```python
settings = GameSettings(difficulty=DifficultyLevel.NORMAL)
engine = GameEngine(settings)
```

---

#### move_card()

```python
def move_card(from_pile: str, to_pile: str) -> MoveResult:
```

**Purpose**: Validates and executes card move between piles according to game rules.

**Parameters**:
- `from_pile` (str): Source pile ID (e.g., `'tableau_0'`, `'stock'`, `'waste'`)
- `to_pile` (str): Target pile ID (e.g., `'foundation_hearts'`, `'tableau_3'`)

**Returns**:
- `MoveResult`: Object with:
  - `success` (bool): True if move valid and executed
  - `reason` (str): Error description if failed, empty string if success

**Business Rules**:
- **Tableau**: Alternating colors, descending rank (King → Ace)
- **Foundation**: Same suit, ascending rank (Ace → King)
- **Waste**: Only top card is movable

**Example**:
```python
engine = GameEngine()
result = engine.move_card('waste', 'foundation_hearts')

if result.success:
    print("Move executed successfully")
else:
    print(f"Invalid move: {result.reason}")
```

**⚠️ Note**: Method modifies internal game state. Call `get_state()` to retrieve updated state.

**Version**: Added in v1.0.0

---

#### draw_from_stock()

```python
def draw_from_stock() -> DrawResult:
```

**Purpose**: Draws card(s) from stock pile to waste pile. Number of cards drawn depends on game settings (draw-1 or draw-3 mode).

**Parameters**: None

**Returns**:
- `DrawResult`: Object with:
  - `cards_drawn` (List[Card]): Cards moved to waste (1 or 3 cards)
  - `stock_empty` (bool): True if stock pile is now empty

**Side Effects**:
- Increments internal draw counter (affects scoring)
- Moves cards from stock to waste pile
- If stock empty, may trigger recycle logic (depending on rules)

**Example**:
```python
result = engine.draw_from_stock()
print(f"Drew {len(result.cards_drawn)} cards")

if result.stock_empty:
    print("Stock depleted, recycle available")
```

**Version**: Added in v1.0.0, Modified in v2.0.0 (scoring integration)

---

#### check_victory()

```python
def check_victory() -> bool:
```

**Purpose**: Checks if game is won (all foundations complete).

**Parameters**: None

**Returns**:
- `bool`: True if all 4 foundations have 13 cards (Ace → King), False otherwise

**Example**:
```python
if engine.check_victory():
    print("You won!")
    # Trigger victory UI/dialog
```

**⚠️ Note**: Pure query, no side effects. Safe to call repeatedly.

**Version**: Added in v1.0.0

---

#### new_game()

```python
def new_game() -> None:
```

**Purpose**: Resets game state and deals a new shuffled deck.

**Parameters**: None

**Returns**: None

**Side Effects**:
- Shuffles deck (random seed-based)
- Distributes cards to tableau (7 piles)
- Resets stock, waste, foundations
- Resets move counter, score, timer

**Example**:
```python
engine.new_game()
print("New game started")
```

**Version**: Added in v1.0.0

---

#### get_state()

```python
def get_state() -> GameState:
```

**Purpose**: Returns current game state snapshot for UI rendering or persistence.

**Parameters**: None

**Returns**:
- `GameState`: Dataclass with:
  - `tableau` (List[List[Card]]): 7 tableau piles
  - `foundations` (Dict[str, List[Card]]): 4 foundation piles
  - `stock` (List[Card]): Stock pile
  - `waste` (List[Card]): Waste pile
  - `move_count` (int): Total moves made
  - `score` (int): Current score

**Example**:
```python
state = engine.get_state()
print(f"Moves: {state.move_count}, Score: {state.score}")
print(f"Tableau 0 has {len(state.tableau[0])} cards")
```

**Version**: Added in v1.0.0

---

### Card

**File**: `src/domain/models/card.py`

**Purpose**: Immutable entity representing a single playing card.

**Constructor**:
```python
Card(rank: str, suit: str, face_up: bool = False)
```

**Parameters**:
- `rank` (str): Card rank (`'A'`, `'2'`-`'10'`, `'J'`, `'Q'`, `'K'`)
- `suit` (str): Card suit (`'hearts'`, `'diamonds'`, `'clubs'`, `'spades'`)
- `face_up` (bool): Visibility state (default False)

**Properties** (read-only):
- `color` (str): `'red'` or `'black'` (derived from suit)
- `value` (int): Numeric value (A=1, 2-10=face, J=11, Q=12, K=13)

**Example**:
```python
card = Card('A', 'hearts', face_up=True)
print(card.rank)   # 'A'
print(card.suit)   # 'hearts'
print(card.color)  # 'red'
print(card.value)  # 1
```

**Version**: Added in v1.0.0

---

#### is_valid_tableau_move()

```python
def is_valid_tableau_move(target: Card) -> bool:
```

**Purpose**: Checks if this card can be placed on target card in tableau (alternating colors, descending rank).

**Parameters**:
- `target` (Card): Target card to stack on

**Returns**:
- `bool`: True if move valid (opposite color, rank = target.rank - 1)

**Example**:
```python
card1 = Card('7', 'hearts')    # 7 Red
card2 = Card('8', 'spades')    # 8 Black

assert card1.is_valid_tableau_move(card2) is True   # OK: Red on Black, 7 on 8
assert card2.is_valid_tableau_move(card1) is False  # Wrong: Black on Red
```

**Version**: Added in v1.0.0

---

#### is_valid_foundation_move()

```python
def is_valid_foundation_move(target: Optional[Card]) -> bool:
```

**Purpose**: Checks if this card can be placed on foundation pile.

**Parameters**:
- `target` (Optional[Card]): Top card of foundation, or None if foundation empty

**Returns**:
- `bool`: True if:
  - Foundation empty AND card is Ace, OR
  - Same suit AND rank = target.rank + 1

**Example**:
```python
ace = Card('A', 'hearts')
two = Card('2', 'hearts')

assert ace.is_valid_foundation_move(None) is True    # Ace on empty
assert two.is_valid_foundation_move(ace) is True     # 2 on Ace
assert ace.is_valid_foundation_move(two) is False    # Wrong direction
```

**Version**: Added in v1.0.0

---

### Deck

**File**: `src/domain/models/deck.py`

**Purpose**: Manages a standard 52-card deck with shuffle and deal operations.

**Constructor**:
```python
Deck()
```

**Example**:
```python
deck = Deck()
deck.shuffle()
cards = deck.deal(7)  # Deal 7 cards
```

---

#### shuffle()

```python
def shuffle() -> None:
```

**Purpose**: Randomizes deck order using Python's random.shuffle().

**Parameters**: None

**Returns**: None

**Side Effects**: Modifies internal card order

**Version**: Added in v1.0.0

---

#### deal()

```python
def deal(count: int) -> List[Card]:
```

**Purpose**: Removes and returns specified number of cards from deck.

**Parameters**:
- `count` (int): Number of cards to deal

**Returns**:
- `List[Card]`: Dealt cards (may be fewer than requested if deck exhausted)

**Example**:
```python
deck = Deck()
deck.shuffle()
hand = deck.deal(5)
print(f"Dealt {len(hand)} cards")
```

**Version**: Added in v1.0.0

---

### Scoring

**File**: `src/domain/services/scoring.py`

**Purpose**: Calculates score based on moves, time, penalties. Tracks scoring events during gameplay.

**Constructor**:
```python
Scoring(settings: GameSettings)
```

**Parameters**:
- `settings` (GameSettings): Game configuration affecting scoring rules

---

#### calculate_score()

```python
def calculate_score() -> int:
```

**Purpose**: Computes current score based on recorded events and game state.

**Parameters**: None

**Returns**:
- `int`: Total score (clamped to minimum 0)

**Scoring Formula** (example):
- Base: 100 points
- +10 per card in foundation
- -1 per stock draw beyond threshold
- -15 per waste recycle beyond limit
- Time bonus if timer enabled

**Example**:
```python
scoring = Scoring(settings)
scoring.record_event(ScoreEventType.CARD_TO_FOUNDATION)
score = scoring.calculate_score()
print(f"Current score: {score}")
```

**Version**: Added in v1.5.0

---

#### record_event()

```python
def record_event(event_type: ScoreEventType) -> None:
```

**Purpose**: Records scoring event for later calculation.

**Parameters**:
- `event_type` (ScoreEventType): Event type (STOCK_DRAW, CARD_TO_FOUNDATION, etc.)

**Returns**: None

**Side Effects**: Increments internal event counters

**Example**:
```python
scoring.record_event(ScoreEventType.STOCK_DRAW)
scoring.record_event(ScoreEventType.CARD_TO_FOUNDATION)
```

**Version**: Added in v1.5.0

---

### GameSettings

**File**: `src/domain/services/game_settings.py`

**Purpose**: Immutable configuration object for game rules and preferences.

**Constructor**:
```python
GameSettings(
    difficulty: DifficultyLevel = DifficultyLevel.NORMAL,
    draw_count: int = 3,
    timer_enabled: bool = False,
    timer_duration: int = 0,
    score_warning_level: ScoreWarningLevel = ScoreWarningLevel.BALANCED,
    # ... other fields
)
```

**Key Fields**:
- `difficulty` (DifficultyLevel): Preset difficulty (affects multiple settings)
- `draw_count` (int): Cards drawn per stock draw (1 or 3)
- `timer_enabled` (bool): Whether timer is active
- `timer_duration` (int): Timer limit in seconds (0 = infinite)
- `score_warning_level` (ScoreWarningLevel): TTS verbosity for score thresholds

**Example**:
```python
settings = GameSettings(
    difficulty=DifficultyLevel.EXPERT,
    draw_count=1,
    timer_enabled=True,
    timer_duration=1800  # 30 minutes
)

engine = GameEngine(settings)
```

**Version**: Added in v1.0.0, Extended in v2.4.0 (difficulty presets)

---

## 🎮 Application Layer API

### GameplayController

**File**: `src/application/gameplay_controller.py`

**Purpose**: Orchestrates gameplay use cases. Coordinates between domain logic (GameEngine) and presentation layer (UI/TTS).

**Constructor**:
```python
GameplayController(
    engine: GameEngine,
    formatter: CardFormatter,
    scoring: Scoring
)
```

**Dependencies**:
- `engine` (GameEngine): Domain service for game logic
- `formatter` (CardFormatter): Formats domain data for display
- `scoring` (Scoring): Tracks scoring events

---

#### handle_move_card()

```python
def handle_move_card(from_pile: str, to_pile: str) -> CommandResult:
```

**Purpose**: Processes card move request, executes via domain, returns formatted feedback.

**Parameters**:
- `from_pile` (str): Source pile ID
- `to_pile` (str): Target pile ID

**Returns**:
- `CommandResult`: Object with:
  - `success` (bool): If move succeeded
  - `message` (str): TTS feedback message (Italian)
  - `state_changed` (bool): If game state modified

**Example**:
```python
controller = GameplayController(engine, formatter, scoring)
result = controller.handle_move_card('waste', 'tableau_0')

if result.success:
    speak(result.message)  # "7 di Coppe spostato su 8 di Picche"
else:
    speak(result.message)  # "Mossa non valida: colore sbagliato"
```

**Version**: Added in v2.0.0

---

#### handle_draw_stock()

```python
def handle_draw_stock() -> CommandResult:
```

**Purpose**: Processes stock draw action, announces cards drawn.

**Parameters**: None

**Returns**:
- `CommandResult`: Object with formatted TTS message

**Example**:
```python
result = controller.handle_draw_stock()
speak(result.message)  # "Hai pescato: Asso di Cuori, 7 di Picche, Regina di Fiori"
```

**Version**: Added in v2.0.0

---

#### new_game()

```python
def new_game() -> None:
```

**Purpose**: Starts new game (resets engine, scoring, timer).

**Parameters**: None

**Returns**: None

**Side Effects**:
- Calls `engine.new_game()`
- Resets scoring counters
- Restarts timer if enabled

**Example**:
```python
controller.new_game()
speak("Nuova partita iniziata")
```

**Version**: Added in v2.0.0

---

### OptionsController

**File**: `src/application/options_controller.py`

**Purpose**: Manages game settings changes. Validates and applies configuration updates.

**Constructor**:
```python
OptionsController(settings: GameSettings)
```

**Parameters**:
- `settings` (GameSettings): Current game settings

---

#### cycle_difficulty()

```python
def cycle_difficulty() -> DifficultyLevel:
```

**Purpose**: Cycles to next difficulty preset (wraps around).

**Parameters**: None

**Returns**:
- `DifficultyLevel`: New difficulty level

**Side Effects**: Updates internal settings, may lock/unlock options

**Example**:
```python
controller = OptionsController(settings)
new_level = controller.cycle_difficulty()
speak(f"Difficoltà: {new_level.name}")
```

**Version**: Added in v2.4.0

---

#### modify_draw_count()

```python
def modify_draw_count() -> int:
```

**Purpose**: Toggles draw count between 1 and 3.

**Parameters**: None

**Returns**:
- `int`: New draw count (1 or 3)

**Example**:
```python
new_count = controller.modify_draw_count()
speak(f"Pescate per turno: {new_count}")
```

**Version**: Added in v1.0.0

---

## 🎨 Presentation Layer API

### CardFormatter

**File**: `src/presentation/formatters/card_formatter.py`

**Purpose**: Converts domain Card objects to Italian TTS strings for screen reader accessibility.

---

#### format_card()

```python
def format_card(card: Card) -> str:
```

**Purpose**: Formats single card for TTS announcement.

**Parameters**:
- `card` (Card): Domain card entity

**Returns**:
- `str`: Italian card description (e.g., `"Asso di Cuori"`, `"7 di Picche"`)

**Localization**: Italian only (currently)

**Example**:
```python
formatter = CardFormatter()
card = Card('A', 'hearts', face_up=True)
print(formatter.format_card(card))  # "Asso di Cuori"

card2 = Card('K', 'spades')
print(formatter.format_card(card2))  # "Re di Picche"
```

**Version**: Added in v1.0.0

---

#### format_move_result()

```python
def format_move_result(result: MoveResult, card: Card, target_pile: str) -> str:
```

**Purpose**: Formats move result for TTS feedback.

**Parameters**:
- `result` (MoveResult): Move outcome from domain
- `card` (Card): Card that was moved
- `target_pile` (str): Destination pile ID

**Returns**:
- `str`: Italian feedback message

**Example**:
```python
result = MoveResult(success=True)
card = Card('7', 'hearts')
message = formatter.format_move_result(result, card, 'tableau_0')
# "7 di Cuori spostato su Tableau 1"
```

**Version**: Added in v2.0.0

---

### ScoreFormatter

**File**: `src/presentation/formatters/score_formatter.py`

**Purpose**: Formats score and scoring events for TTS display.

---

#### format_score()

```python
def format_score(score: int) -> str:
```

**Purpose**: Formats score value for announcement.

**Parameters**:
- `score` (int): Current score

**Returns**:
- `str`: Formatted score string (e.g., `"Punteggio: 245 punti"`)

**Example**:
```python
formatter = ScoreFormatter()
print(formatter.format_score(245))  # "Punteggio: 245 punti"
```

**Version**: Added in v1.5.0

---

## 🔧 Type Reference

### Enums

#### GameStatus

```python
class GameStatus(Enum):
    IN_PROGRESS = "in_progress"
    VICTORY = "victory"
    DEFEAT = "defeat"
```

**Usage**: Returned by `GameEngine.get_status()`

**Version**: Added in v1.0.0

---

#### DifficultyLevel

```python
class DifficultyLevel(Enum):
    BEGINNER = 1      # Timer disabled, hints enabled
    EASY = 2          # Permissive timer
    NORMAL = 3        # Standard rules
    EXPERT = 4        # Time attack 30min
    MASTER = 5        # Tournament mode 15min
```

**Usage**: Set in `GameSettings.difficulty`

**Version**: Added in v2.4.0

---

#### ScoreWarningLevel

```python
class ScoreWarningLevel(Enum):
    DISABLED = 0      # No TTS warnings
    MINIMAL = 1       # Only critical thresholds
    BALANCED = 2      # Default, moderate verbosity
    COMPLETE = 3      # All warnings + pre-warnings
```

**Usage**: Set in `GameSettings.score_warning_level`

**Version**: Added in v2.6.0

---

#### ScoreEventType

```python
class ScoreEventType(Enum):
    CARD_TO_FOUNDATION = "card_to_foundation"
    CARD_FROM_FOUNDATION = "card_from_foundation"
    STOCK_DRAW = "stock_draw"
    WASTE_RECYCLE = "waste_recycle"
```

**Usage**: Passed to `Scoring.record_event()`

**Version**: Added in v1.5.0

---

### Dataclasses

#### MoveResult

```python
@dataclass
class MoveResult:
    success: bool
    reason: str = ""
```

**Fields**:
- `success`: True if move valid and executed
- `reason`: Error description if failed (e.g., `"Colore sbagliato"`), empty if success

**Usage**: Returned by `GameEngine.move_card()`

**Version**: Added in v2.0.0

---

#### DrawResult

```python
@dataclass
class DrawResult:
    cards_drawn: List[Card]
    stock_empty: bool
```

**Fields**:
- `cards_drawn`: List of cards moved to waste (1 or 3 cards)
- `stock_empty`: True if stock pile now empty

**Usage**: Returned by `GameEngine.draw_from_stock()`

**Version**: Added in v2.0.0

---

#### GameState

```python
@dataclass
class GameState:
    tableau: List[List[Card]]              # 7 piles
    foundations: Dict[str, List[Card]]     # 4 foundations
    stock: List[Card]
    waste: List[Card]
    move_count: int
    score: int
```

**Usage**: Returned by `GameEngine.get_state()`

**Version**: Added in v1.0.0

---

#### CommandResult

```python
@dataclass
class CommandResult:
    success: bool
    message: str
    state_changed: bool
```

**Fields**:
- `success`: True if command executed
- `message`: TTS feedback message (Italian)
- `state_changed`: True if game state modified (triggers UI refresh)

**Usage**: Returned by application controllers

**Version**: Added in v2.0.0

---

## 🔧 Common Patterns

### Naming Conventions

**Methods**:
- `get_*()`: Returns data without side effects (pure query)
- `set_*()`: Mutates state (setter)
- `check_*()`: Boolean query without side effects
- `handle_*()`: Event handler/coordinator (application layer)
- `format_*()`: Data transformation for display (presentation layer)
- `calculate_*()`: Computation with return value
- `record_*()`: Logs event/data (side effect)

**Return Types**:
- `*Result`: Operation outcome (success, reason, optional data)
- `bool`: Simple yes/no query
- `Optional[T]`: May return None (explicit nullable)
- `List[T]`, `Dict[K,V]`: Collections

### Error Handling Pattern

**Domain Layer** raises specific exceptions:
```python
class InvalidMoveError(Exception):
    """Raised when move violates game rules."""
    pass

def move_card(self, from_pile, to_pile):
    if not self._is_valid_move(...):
        raise InvalidMoveError("Rank mismatch")
```

**Application Layer** catches and returns results:
```python
try:
    self.engine.move_card(from_pile, to_pile)
    return CommandResult(success=True, message="Mossa eseguita")
except InvalidMoveError as e:
    return CommandResult(success=False, message=f"Mossa non valida: {e}")
```

**Presentation Layer** formats for user:
```python
result = controller.handle_move_card(...)
if not result.success:
    speak(result.message)  # TTS announces error
```

### Return Value Conventions

**Success/Failure Operations**:
- Return `*Result` dataclass (not bare bool)
- Include `reason` field for failure context

**Query Operations**:
- Return direct value if always succeeds (`get_score() -> int`)
- Return `Optional[T]` if may not exist (`find_card() -> Optional[Card]`)

**State Mutations**:
- Return None if no meaningful return value
- Return new state if functional style (`updated_settings = settings.with_difficulty(...))`

---

## 📚 Examples Gallery

### Example 1: New Game Flow

```python
from src.domain.services.game_engine import GameEngine
from src.domain.services.game_settings import GameSettings, DifficultyLevel
from src.application.gameplay_controller import GameplayController
from src.presentation.formatters.card_formatter import CardFormatter

# Setup
settings = GameSettings(
    difficulty=DifficultyLevel.NORMAL,
    draw_count=3,
    timer_enabled=False
)

engine = GameEngine(settings)
formatter = CardFormatter()
controller = GameplayController(engine, formatter, scoring)

# Start new game
controller.new_game()
speak("Nuova partita iniziata")

# Draw cards from stock
result = controller.handle_draw_stock()
speak(result.message)  # "Hai pescato: 7 di Coppe, Asso di Picche, Regina di Fiori"

# Attempt move
result = controller.handle_move_card('waste', 'tableau_0')
if result.success:
    speak(result.message)  # "7 di Coppe spostato su 8 di Picche"
else:
    speak(result.message)  # "Mossa non valida: colore sbagliato"
```

---

### Example 2: Check Victory & Score

```python
# During gameplay loop
if engine.check_victory():
    final_score = scoring.calculate_score()
    message = formatter.format_victory(final_score)
    speak(message)  # "Hai vinto! Punteggio finale: 532 punti"
    
    # Show victory dialog
    dialog_manager.show_victory_dialog(final_score)
```

---

### Example 3: Settings Management

```python
from src.application.options_controller import OptionsController

# User opens options menu
options_controller = OptionsController(settings)

# Cycle difficulty
new_difficulty = options_controller.cycle_difficulty()
speak(f"Difficoltà: {new_difficulty.name}")  # "Difficoltà: Esperto"

# Toggle draw count
new_count = options_controller.modify_draw_count()
speak(f"Pescate per turno: {new_count}")  # "Pescate per turno: 1"

# Apply and save
options_controller.save_settings()
speak("Impostazioni salvate")
```

---

### Example 4: Error Handling Flow

```python
# User attempts invalid move
try:
    result = engine.move_card('tableau_0', 'foundation_hearts')
    
    if not result.success:
        # Format error for TTS
        error_msg = formatter.format_error(result.reason)
        speak(error_msg)  # "Non puoi posare questa carta: seme diverso"
        
        # Log for debugging
        logger.warning(f"Invalid move attempt: {result.reason}")
        
except InvalidPileError as e:
    # Pile doesn't exist (should not happen with UI)
    logger.error(f"Invalid pile ID: {e}")
    speak("Errore interno: pila non trovata")
```

---

## 🔄 Version History

### v2.6.0 - Score Warning System
- **Added**: `ScoreWarningLevel` enum (4 levels)
- **Added**: `GameSettings.score_warning_level` field
- **Added**: `GameEngine.get_warning_message()` method
- **Added**: `ScoreFormatter.format_warning()` method

### v2.4.0 - Difficulty Presets
- **Added**: `DifficultyLevel` enum (5 presets)
- **Added**: `GameSettings.apply_preset()` method
- **Changed**: `difficulty` field from `int` to `DifficultyLevel` enum (⚠️ **BREAKING**)
- **Migration**: Replace `settings.difficulty = 3` with `settings.difficulty = DifficultyLevel.NORMAL`

### v2.0.0 - Major Refactor
- **Changed**: Renamed `move()` → `move_card()` (⚠️ **BREAKING**)
- **Added**: `MoveResult` return type (replaced bare bool)
- **Added**: Application layer controllers
- **Removed**: Index-based pile access (use pile IDs) (⚠️ **BREAKING**)

### v1.5.0 - Scoring System
- **Added**: `Scoring` service
- **Added**: `ScoreEventType` enum
- **Added**: `GameEngine.get_score()` method

### v1.0.0 - Initial Release
- **Added**: Core game logic (GameEngine, Card, Deck)
- **Added**: Basic move validation
- **Added**: Victory detection

---

## ⚠️ Deprecated APIs

### GameEngine.old_move_method() [Deprecated in v2.0.0]

**Signature**: `old_move_method(card_index: int, target_pile: int)`

**Reason**: Index-based access error-prone, replaced by pile ID system

**Replacement**: Use `move_card(from_pile: str, to_pile: str)`

**Removal Planned**: v3.0.0

**Migration Example**:
```python
# OLD (v1.x) - Don't use
engine.old_move_method(5, 2)

# NEW (v2.x+) - Use this
engine.move_card('tableau_2', 'foundation_hearts')
```

---

## 🤝 Contributing to API

### When to Update This Document

**Update Required** (✅):
- New public class added to domain/application layer
- Public method signature changed (parameters, return type)
- Method deprecated or removed
- New enum/dataclass added to type reference
- Breaking change in existing API

**Update NOT Required** (❌):
- Private method added (prefixed with `_`)
- Implementation detail changed (no API impact)
- Docstring typo fixed in source code
- Internal refactoring without signature change
- UI event handler added (presentation layer internal)

### How to Update

1. **Make code changes first** (implementation + tests)
2. **Identify impacted APIs** (what methods changed?)
3. **Update relevant sections**:
   - Method signature if changed
   - Example if behavior changed
   - Type reference if new types added
4. **Add to Version History** if breaking change or major addition
5. **Mark as deprecated** if replacing old API (don't remove immediately)
6. **Update "Last Updated"** in document header
7. **Commit message**: `docs(api): [what changed]`

**Example Commit Message**:
```
docs(api): Add cycle_difficulty method to OptionsController

- New method for difficulty preset cycling
- Added DifficultyLevel enum to Type Reference
- Updated Example 3 with difficulty management
```

### Review Checklist

Before committing API.md updates:

- [ ] All code examples compile and run
- [ ] Method signatures match actual implementation
- [ ] Return types accurate (check source code)
- [ ] Examples use realistic scenarios
- [ ] Type Reference includes all new enums/dataclasses
- [ ] Deprecated APIs marked clearly with migration path
- [ ] Version History updated if breaking change
- [ ] No broken links to non-existent sections

---

## 📌 Template Metadata

**Template Version**: v1.0  
**Created**: 2026-02-16  
**Maintainer**: AI Assistant + Nemex81  
**Based On**: solitario-classico-accessibile project  
**Philosophy**: "Lightweight & Focused" - Document only essential public APIs

---

## 🎯 Instructions for Using This Template

### How to Use

1. **Copy template**: `cp TEMPLATE_API.md API.md`
2. **Fill in project-specific info**: Replace `[Project Name]`, version, etc.
3. **Document 5-6 critical classes first**:
   - Domain: GameEngine, Card, Scoring (core logic)
   - Application: Main controllers
   - Presentation: Key formatters (if used by others)
4. **Add real examples**: Copy actual code snippets from your project
5. **Expand Type Reference**: Add all enums/dataclasses
6. **Create Examples Gallery**: 3-4 realistic scenarios
7. **Keep updated**: Review every MINOR version bump (v2.5 → v2.6)

### Priority: What to Document

**🔴 HIGH Priority** (document fully):
- Classes with >5 public methods
- APIs called across layer boundaries
- Complex business logic (non-obvious behavior)
- Methods with side effects

**🟡 MEDIUM Priority** (document briefly):
- Simple getters/setters (if not self-explanatory)
- Utility methods used by multiple components
- Coordinators with straightforward orchestration

**🟢 LOW Priority** (skip or minimal mention):
- Private methods (`_internal`)
- Property accessors for simple fields
- UI event handlers (presentation layer internal)
- Infrastructure helpers (framework-specific)

### Sections Priority

**MUST HAVE** (always):
- Document Purpose
- API Index
- Domain Layer APIs (core 3-5 classes)
- Type Reference (enums, dataclasses)
- Common Patterns

**SHOULD HAVE** (most projects):
- Application Layer APIs (controllers)
- Examples Gallery (3-4 scenarios)
- Version History (major changes)

**OPTIONAL** (nice to have):
- Presentation Layer APIs (if used cross-layer)
- Deprecated APIs section (if applicable)
- Extensive version history (keep recent only)

### Best Practices

✅ **DO**:
- Use real code examples from your project (copy-pasteable)
- Keep examples short (3-7 lines, no boilerplate)
- Explain non-obvious behavior in "⚠️ Note" sections
- Link to source files when details needed
- Include return types in signatures (type hints)
- Show both success and error paths in examples

❌ **DON'T**:
- Don't document every method (only essential APIs)
- Don't duplicate source code comments (link instead)
- Don't include implementation details (how it works internally)
- Don't use placeholder examples (`foo`, `bar` variables)
- Don't let it get stale (update regularly)
- Don't document private methods

### Target Length

**Good Range**: 500-800 lines (readable in 15-20 minutes)

**Breakdown**:
- Header + Index: ~50 lines
- Domain APIs: ~300 lines (3-5 classes, key methods)
- Application APIs: ~150 lines (2-3 controllers)
- Type Reference: ~100 lines (all enums/dataclasses)
- Examples: ~100 lines (3-4 scenarios)
- Patterns + Footer: ~100 lines

**Too Short** (<300): Missing essential APIs  
**Too Long** (>1200): Over-documenting, dilutes focus

### When API Documentation Is "Good Enough"

API.md is sufficient when:

- ✅ Developer can use any public API without reading source code
- ✅ All domain/application layer public classes documented
- ✅ Type Reference complete (all enums/dataclasses)
- ✅ Examples show realistic usage patterns
- ✅ Error handling patterns clear
- ✅ No obvious gaps in critical APIs

---

**End of Template**

**Happy API Documenting! 📚**
