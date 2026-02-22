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
    """Initialize game engine.
    
    Args:
        settings: Game configuration (difficulty, rules). Defaults to standard settings if None.
    
    Example:
        >>> settings = GameSettings(difficulty=DifficultyLevel.NORMAL)
        >>> engine = GameEngine(settings)
    """
```

---

#### move_card()

```python
def move_card(from_pile: str, to_pile: str) -> MoveResult:
    """Valida ed esegue spostamento carta tra pile.
    
    Args:
        from_pile: Source pile ID ('tableau_0', 'stock', 'waste')
        to_pile: Target pile ID ('foundation_hearts', 'tableau_3')
    
    Returns:
        MoveResult(success: bool, reason: str)
    
    Example:
        >>> result = engine.move_card('waste', 'foundation_hearts')
        >>> if result.success: print("Mossa eseguita")
        >>> else: print(f"Errore: {result.reason}")
    
    Note:
        Modifica stato interno. Business rules:
        - Tableau: colori alternati, rank discendente (King → Ace)
        - Foundation: stesso seme, rank crescente (Ace → King)
        - Waste: solo top card movibile
    
    Version: v1.0.0
    """
```

---

#### draw_from_stock()

```python
def draw_from_stock() -> DrawResult:
    """Pesca carta/e da stock a waste.
    
    Returns:
        DrawResult(cards_drawn: List[Card], stock_empty: bool)
    
    Example:
        >>> result = engine.draw_from_stock()
        >>> print(f"Pescate {len(result.cards_drawn)} carte")
        >>> if result.stock_empty: print("Stock esaurito")
    
    Note:
        Numero carte pescate dipende da settings (draw-1 o draw-3).
        Incrementa contatore interno (impatta scoring).
    
    Version: v1.0.0, Modified v2.0.0 (scoring integration)
    """
```

---

#### check_victory()

```python
def check_victory() -> bool:
    """Verifica vittoria (tutte le foundations complete).
    
    Returns:
        bool: True se tutte e 4 le foundations hanno 13 carte (Ace → King)
    
    Example:
        >>> if engine.check_victory():
        ...     print("Hai vinto!")
    
    Note: Pure query, nessun side effect. Safe da chiamare ripetutamente.
    
    Version: v1.0.0
    """
```

---

#### new_game()

```python
def new_game() -> None:
    """Reset stato e distribuisce nuovo mazzo mescolato.
    
    Example:
        >>> engine.new_game()
        >>> print("Nuova partita iniziata")
    
    Note:
        Side effects: shuffle deck, distribuzione tableau (7 pile),
        reset stock/waste/foundations, reset counters/score/timer.
    
    Version: v1.0.0
    """
```

---

#### get_state()

```python
def get_state() -> GameState:
    """Ritorna snapshot stato corrente per UI rendering o persistence.
    
    Returns:
        GameState: dataclass con tableau, foundations, stock, waste, move_count, score
    
    Example:
        >>> state = engine.get_state()
        >>> print(f"Mosse: {state.move_count}, Score: {state.score}")
        >>> print(f"Tableau 0: {len(state.tableau[0])} carte")
    
    Version: v1.0.0
    """
```

---

### Card

**File**: `src/domain/models/card.py`

**Purpose**: Immutable entity representing a single playing card.

**Constructor**:
```python
Card(rank: str, suit: str, face_up: bool = False)
    """Crea carta immutabile.
    
    Args:
        rank: Rank carta ('A', '2'-'10', 'J', 'Q', 'K')
        suit: Seme ('hearts', 'diamonds', 'clubs', 'spades')
        face_up: Stato visibilità (default False)
    
    Properties (read-only):
        color (str): 'red' o 'black' (derivato da suit)
        value (int): Valore numerico (A=1, 2-10=face, J=11, Q=12, K=13)
    
    Example:
        >>> card = Card('A', 'hearts', face_up=True)
        >>> print(card.rank, card.suit, card.color, card.value)
        'A' 'hearts' 'red' 1
    
    Version: v1.0.0
    """
```

---

#### is_valid_tableau_move()

```python
def is_valid_tableau_move(target: Card) -> bool:
    """Verifica validità spostamento su tableau.
    
    Args:
        target: Carta target su cui impilare
    
    Returns:
        bool: True se colore opposto e rank = target.rank - 1
    
    Example:
        >>> card1 = Card('7', 'hearts')    # 7 Rosso
        >>> card2 = Card('8', 'spades')    # 8 Nero
        >>> assert card1.is_valid_tableau_move(card2) is True
    
    Version: v1.0.0
    """
```

---

#### is_valid_foundation_move()

```python
def is_valid_foundation_move(target: Optional[Card]) -> bool:
    """Verifica validità spostamento su foundation.
    
    Args:
        target: Top card foundation, o None se foundation vuota
    
    Returns:
        bool: True se (foundation vuota AND card è Ace) OR (stesso seme AND rank = target.rank + 1)
    
    Example:
        >>> ace = Card('A', 'hearts')
        >>> two = Card('2', 'hearts')
        >>> assert ace.is_valid_foundation_move(None) is True    # Ace su vuoto
        >>> assert two.is_valid_foundation_move(ace) is True     # 2 su Ace
    
    Version: v1.0.0
    """
```

---

### Deck

**File**: `src/domain/models/deck.py`

**Purpose**: Manages a standard 52-card deck with shuffle and deal operations.

**Constructor**:
```python
Deck()
    """Crea mazzo standard 52 carte.
    
    Example:
        >>> deck = Deck()
        >>> deck.shuffle()
        >>> cards = deck.deal(7)
    """
```

---

#### shuffle()

```python
def shuffle() -> None:
    """Mescola mazzo usando random.shuffle().
    
    Note: Modifica ordine interno carte.
    
    Version: v1.0.0
    """
```

---

#### deal()

```python
def deal(count: int) -> List[Card]:
    """Rimuove e ritorna N carte dal mazzo.
    
    Args:
        count: Numero carte da distribuire
    
    Returns:
        List[Card]: Carte distribuite (può essere < count se mazzo esaurito)
    
    Example:
        >>> hand = deck.deal(5)
        >>> print(f"Distribuite {len(hand)} carte")
    
    Version: v1.0.0
    """
```

---

### Scoring

**File**: `src/domain/services/scoring.py`

**Purpose**: Calculates score based on moves, time, penalties. Tracks scoring events during gameplay.

**Constructor**:
```python
Scoring(settings: GameSettings)
    """Inizializza scoring service.
    
    Args:
        settings: Configurazione che impatta regole scoring
    """
```

---

#### calculate_score()

```python
def calculate_score() -> int:
    """Calcola punteggio corrente basato su eventi registrati.
    
    Returns:
        int: Punteggio totale (minimo 0)
    
    Example:
        >>> scoring.record_event(ScoreEventType.CARD_TO_FOUNDATION)
        >>> score = scoring.calculate_score()
        >>> print(f"Score: {score}")
    
    Note:
        Formula esempio: Base 100 + 10/card in foundation - 1/stock draw oltre soglia
        - 15/recycle oltre limite + time bonus se timer attivo.
    
    Version: v1.5.0
    """
```

---

#### record_event()

```python
def record_event(event_type: ScoreEventType) -> None:
    """Registra evento scoring per calcolo successivo.
    
    Args:
        event_type: Tipo evento (STOCK_DRAW, CARD_TO_FOUNDATION, etc.)
    
    Note: Incrementa contatori interni eventi.
    
    Version: v1.5.0
    """
```

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
    """Configurazione gioco immutabile.
    
    Key Fields:
        difficulty: Preset difficoltà (impatta multiple settings)
        draw_count: Carte pescate per stock draw (1 o 3)
        timer_enabled: Se timer è attivo
        timer_duration: Limite timer in secondi (0 = infinito)
        score_warning_level: Verbosità TTS per soglie score
    
    Example:
        >>> settings = GameSettings(
        ...     difficulty=DifficultyLevel.EXPERT,
        ...     draw_count=1,
        ...     timer_enabled=True,
        ...     timer_duration=1800  # 30 minuti
        ... )
        >>> engine = GameEngine(settings)
    
    Version: v1.0.0, Extended v2.4.0 (difficulty presets)
    """
```

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
    """Inizializza gameplay controller.
    
    Dependencies:
        engine: Domain service per game logic
        formatter: Formatta domain data per display
        scoring: Traccia scoring events
    """
```

---

#### handle_move_card()

```python
def handle_move_card(from_pile: str, to_pile: str) -> CommandResult:
    """Processa richiesta move carta, esegue via domain, ritorna feedback formattato.
    
    Args:
        from_pile: Source pile ID
        to_pile: Target pile ID
    
    Returns:
        CommandResult(success: bool, message: str, state_changed: bool)
    
    Example:
        >>> result = controller.handle_move_card('waste', 'tableau_0')
        >>> if result.success:
        ...     speak(result.message)  # "7 di Coppe spostato su 8 di Picche"
        >>> else:
        ...     speak(result.message)  # "Mossa non valida: colore sbagliato"
    
    Version: v2.0.0
    """
```

---

#### handle_draw_stock()

```python
def handle_draw_stock() -> CommandResult:
    """Processa azione draw stock, annuncia carte pescate.
    
    Returns:
        CommandResult con messaggio TTS formattato
    
    Example:
        >>> result = controller.handle_draw_stock()
        >>> speak(result.message)  # "Hai pescato: Asso di Cuori, 7 di Picche, Regina di Fiori"
    
    Version: v2.0.0
    """
```

---

#### new_game()

```python
def new_game() -> None:
    """Inizia nuova partita (reset engine, scoring, timer).
    
    Example:
        >>> controller.new_game()
        >>> speak("Nuova partita iniziata")
    
    Note: Side effects: chiama engine.new_game(), reset scoring counters, restart timer se enabled.
    
    Version: v2.0.0
    """
```

---

### OptionsController

**File**: `src/application/options_controller.py`

**Purpose**: Manages game settings changes. Validates and applies configuration updates.

**Constructor**:
```python
OptionsController(settings: GameSettings)
    """Inizializza options controller.
    
    Args:
        settings: Current game settings
    """
```

---

#### cycle_difficulty()

```python
def cycle_difficulty() -> DifficultyLevel:
    """Cicla a prossimo preset difficoltà (wrap around).
    
    Returns:
        DifficultyLevel: Nuovo livello difficoltà
    
    Example:
        >>> new_level = controller.cycle_difficulty()
        >>> speak(f"Difficoltà: {new_level.name}")
    
    Note: Aggiorna settings interni, può lock/unlock opzioni.
    
    Version: v2.4.0
    """
```

---

#### modify_draw_count()

```python
def modify_draw_count() -> int:
    """Toggle draw count tra 1 e 3.
    
    Returns:
        int: Nuovo draw count (1 o 3)
    
    Example:
        >>> new_count = controller.modify_draw_count()
        >>> speak(f"Pescate per turno: {new_count}")
    
    Version: v1.0.0
    """
```

---

## 🎨 Presentation Layer API

### CardFormatter

**File**: `src/presentation/formatters/card_formatter.py`

**Purpose**: Converts domain Card objects to Italian TTS strings for screen reader accessibility.

---

#### format_card()

```python
def format_card(card: Card) -> str:
    """Formatta singola carta per annuncio TTS.
    
    Args:
        card: Domain card entity
    
    Returns:
        str: Descrizione italiana carta (es. "Asso di Cuori", "7 di Picche")
    
    Example:
        >>> card = Card('A', 'hearts', face_up=True)
        >>> print(formatter.format_card(card))  # "Asso di Cuori"
    
    Note: Localizzazione Italian only (attualmente).
    
    Version: v1.0.0
    """
```

---

#### format_move_result()

```python
def format_move_result(result: MoveResult, card: Card, target_pile: str) -> str:
    """Formatta move result per TTS feedback.
    
    Args:
        result: Move outcome da domain
        card: Carta spostata
        target_pile: Destination pile ID
    
    Returns:
        str: Messaggio feedback italiano
    
    Example:
        >>> result = MoveResult(success=True)
        >>> card = Card('7', 'hearts')
        >>> message = formatter.format_move_result(result, card, 'tableau_0')
        # "7 di Cuori spostato su Tableau 1"
    
    Version: v2.0.0
    """
```

---

### ScoreFormatter

**File**: `src/presentation/formatters/score_formatter.py`

**Purpose**: Formats score and scoring events for TTS display.

---

#### format_score()

```python
def format_score(score: int) -> str:
    """Formatta punteggio per annuncio.
    
    Args:
        score: Punteggio corrente
    
    Returns:
        str: Stringa formattata (es. "Punteggio: 245 punti")
    
    Example:
        >>> print(formatter.format_score(245))  # "Punteggio: 245 punti"
    
    Version: v1.5.0
    """
```

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

**Version**: v1.0.0

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

**Version**: v2.4.0

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

**Version**: v2.6.0

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

**Version**: v1.5.0

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

**Version**: v2.0.0

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

**Version**: v2.0.0

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

**Version**: v1.0.0

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

**Version**: v2.0.0

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

## 🤝 Aggiornamento API.md

**Aggiorna quando**: nuova public class, signature changed, breaking change, nuovo enum/dataclass.  
**Non aggiornare per**: private methods, docstring typo, internal refactoring.

**Workflow**: Code + tests → Aggiorna sezione metodo → Version History se breaking → Commit `docs(api): [change]`

**Esempio commit**:
```
docs(api): Add cycle_difficulty method to OptionsController

- New method for difficulty preset cycling
- Added DifficultyLevel enum to Type Reference
- Updated Example 3 with difficulty management
```

---

## 📌 Template Metadata

**Template Version**: v1.1 (ottimizzato -25.8%)  
**Created**: 2026-02-16  
**Last Updated**: 2026-02-22  
**Maintainer**: AI Assistant + Nemex81  
**Based On**: solitario-classico-accessibile project  
**Philosophy**: "Lightweight & Focused" - Document only essential public APIs

---

## 🎯 Uso Template

1. **Copia template**: `cp TEMPLATE_API.md API.md`
2. **Sostituisci placeholder**: `[Project Name]`, version, etc.
3. **Documenta 5-6 classi critiche**: Domain (core logic), Application (controllers), Type Reference (enums/dataclasses)
4. **Aggiungi 3-4 esempi realistici** dalla codebase (copy-pasteable)
5. **Aggiorna ad ogni MINOR version bump** (v2.5 → v2.6)

**Priorità Documentazione**:
- **MUST**: Domain APIs, Type Reference, Common Patterns
- **OPTIONAL**: Presentation APIs (solo se cross-layer), Deprecated APIs

Documenta solo public APIs chiamate da altri layer. Skip private methods (`_internal`), getters semplici, event handlers UI-specific.

**Target**: 500-800 lines, readable in 15-20 minutes.

---

**End of Template**

**Happy API Documenting! 📚**
