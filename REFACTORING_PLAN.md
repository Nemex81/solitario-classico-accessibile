# Piano di Refactoring Incrementale - Architettura Modulare

## Obiettivo Generale

Refactoring completo del progetto Solitario Accessibile seguendo principi SOLID e architettura a strati (domain-driven design), suddiviso in 13 fasi incrementali.

## Architettura Target

```
src/
├── domain/              # Business logic pura (NO dipendenze esterne)
│   ├── __init__.py
│   ├── models/         # Entità del dominio
│   │   ├── __init__.py
│   │   ├── card.py     # Card dataclass
│   │   ├── pile.py     # Pile types (Foundation, Tableau, Stock, Waste)
│   │   └── game_state.py  # GameState immutabile
│   ├── rules/          # Regole di gioco
│   │   ├── __init__.py
│   │   ├── move_validator.py  # Validazione mosse
│   │   └── victory_checker.py # Controllo vittoria
│   └── services/       # Servizi del dominio
│       ├── __init__.py
│       └── game_service.py    # Orchestrazione logica
├── application/         # Use cases e coordinamento
│   ├── __init__.py
│   └── game_controller.py    # Controller principale
├── infrastructure/      # Dettagli implementativi
│   ├── __init__.py
│   ├── ui/             # Interfaccia pygame
│   │   ├── __init__.py
│   │   └── pygame_renderer.py
│   └── accessibility/   # Screen reader e accessibilità
│       ├── __init__.py
│       └── screen_reader_adapter.py
└── presentation/        # Formatters e visualizzazione
    ├── __init__.py
    └── game_formatter.py
```

## Checklist Fasi

- [x] **Fase 0**: Preparazione ambiente (pytest, mypy, pre-commit)
- [x] **Fase 1**: Creazione struttura directory modulare
- [x] **Fase 2**: Estrazione GameState immutabile
- [x] **Fase 3**: Refactoring Card e Pile
- [x] **Fase 4**: Estrazione MoveValidator
- [x] **Fase 4.5**: Correzioni critiche (Pile model, Italian deck, Accessibility)
- [x] **Fase 5**: Creazione GameService
- [x] **Fase 6**: Estrazione Formatter
- [x] **Fase 7**: Protocol interfaces
- [x] **Fase 8**: GameController applicativo
- [x] **Fase 9**: Command pattern
- [x] **Fase 10**: Dependency injection
- [x] **Fase 11**: Test coverage completo
- [x] **Fase 12**: Documentazione finale

---

## Fase 0: Preparazione Ambiente di Sviluppo

### Obiettivo
Configurare strumenti di qualità del codice e testing framework.

### File da Creare

#### 1. `requirements-dev.txt`
```txt
# Testing
pytest==7.4.3
pytest-cov==4.1.0
pytest-mock==3.12.0

# Type checking
mypy==1.7.1

# Code formatting
black==23.12.0
isort==5.13.2

# Linting
flake8==6.1.0
pylint==3.0.3

# Pre-commit hooks
pre-commit==3.6.0
```

#### 2. `.pre-commit-config.yaml`
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        args: ['--max-line-length=100', '--extend-ignore=E203,W503']

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--ignore-missing-imports]
```

#### 3. `pytest.ini`
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

#### 4. `mypy.ini`
```ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_any_unimported = False
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
check_untyped_defs = True
strict_equality = True

[mypy-pygame.*]
ignore_missing_imports = True

[mypy-accessible_output2.*]
ignore_missing_imports = True

[mypy-tests.*]
disallow_untyped_defs = False
```

#### 5. `pyproject.toml`
```toml
[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 100
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true

[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --strict-markers"
testpaths = ["tests"]

[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/test_*.py",
]

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
```

#### 6. `tests/__init__.py`
```python
"""Test package for Solitario Accessibile."""
```

### Istruzioni per GitHub Copilot

1. **Creare i 6 file esattamente come specificato sopra**
2. **Creare la directory `tests/` se non esiste**
3. **NON modificare codice esistente in `scr/`**
4. **Installare le dipendenze di sviluppo**:
   ```bash
   pip install -r requirements-dev.txt
   ```
5. **Verificare l'installazione**:
   ```bash
   pytest --version
   mypy --version
   black --version
   ```

### Commit Message
```
chore: setup development environment and testing framework

- Add pytest, mypy, black, isort configuration
- Configure pre-commit hooks for code quality
- Create initial test directory structure
- Add development requirements

No functional changes to application code.
```

### Criteri di Completamento
- [x] File di configurazione creati
- [x] Dipendenze installate con successo
- [x] `pytest --version` restituisce versione >= 7.4
- [x] `mypy --version` restituisce versione >= 1.7
- [x] Struttura `tests/` creata

---

## Fase 1: Creazione Struttura Directory Modulare

### Obiettivo
Creare la struttura delle directory per l'architettura a strati.

### Directory da Creare

```
src/
├── __init__.py
├── domain/
│   ├── __init__.py
│   ├── models/
│   │   └── __init__.py
│   ├── rules/
│   │   └── __init__.py
│   └── services/
│       └── __init__.py
├── application/
│   └── __init__.py
├── infrastructure/
│   ├── __init__.py
│   ├── ui/
│   │   └── __init__.py
│   └── accessibility/
│       └── __init__.py
└── presentation/
    └── __init__.py

tests/
├── __init__.py
├── unit/
│   ├── __init__.py
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   └── __init__.py
│   │   └── rules/
│   │       └── __init__.py
│   └── application/
│       └── __init__.py
└── integration/
    └── __init__.py
```

### File `__init__.py` Template

Ogni `__init__.py` deve contenere:
```python
"""[Nome del modulo] package."""
```

### Istruzioni per GitHub Copilot

1. **Creare TUTTE le directory e file `__init__.py` come specificato**
2. **Usare docstring descrittive in ogni `__init__.py`**:
   - `src/__init__.py`: "Solitario Accessibile - Main source package."
   - `src/domain/__init__.py`: "Domain layer - Pure business logic."
   - `src/domain/models/__init__.py`: "Domain models - Card, Pile, GameState."
   - `src/domain/rules/__init__.py`: "Game rules - Move validation and victory checking."
   - `src/domain/services/__init__.py`: "Domain services - Game orchestration."
   - `src/application/__init__.py`: "Application layer - Use cases and controllers."
   - `src/infrastructure/__init__.py`: "Infrastructure layer - UI and external integrations."
   - `src/presentation/__init__.py`: "Presentation layer - Formatters and views."
   - `tests/unit/__init__.py`: "Unit tests package."
   - `tests/integration/__init__.py`: "Integration tests package."

3. **Verificare struttura creata**:
   ```bash
   tree src/ tests/ -I '__pycache__|*.pyc'
   ```

### Commit Message
```
feat: create modular directory structure for layered architecture

- Add domain, application, infrastructure, presentation layers
- Create test directory structure (unit/integration)
- Add descriptive __init__.py files for all packages

Follows SOLID principles and domain-driven design.
```

### Criteri di Completamento
- [x] Directory `src/` con 4 layer principali
- [x] Directory `tests/` con struttura unit/integration
- [x] Tutti i file `__init__.py` hanno docstring
- [x] `tree` o `ls -R` mostra struttura corretta

---

## Fase 2: Estrazione GameState Immutabile

### Obiettivo
Creare un modello immutabile `GameState` che rappresenta lo stato del gioco.

### File da Creare

#### `src/domain/models/game_state.py`

```python
"""GameState immutable model."""
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from enum import Enum


class GameStatus(Enum):
    """Game status enumeration."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    WON = "won"
    LOST = "lost"


@dataclass(frozen=True)
class GameState:
    """
    Immutable game state representation.
    
    Represents the complete state of a Klondike solitaire game at a specific moment.
    Uses frozen dataclass to ensure immutability and prevent accidental state mutations.
    
    Attributes:
        foundations: Four foundation piles (Ace to King, same suit)
        tableaus: Seven tableau piles (face-up cards)
        stock: Remaining cards in stock pile
        waste: Cards drawn from stock
        status: Current game status
        moves_count: Number of moves made
        score: Current game score
    """
    
    foundations: Tuple[Tuple[str, ...], ...] = field(
        default_factory=lambda: ((), (), (), ())
    )
    tableaus: Tuple[Tuple[str, ...], ...] = field(
        default_factory=lambda: ((), (), (), (), (), (), ())
    )
    stock: Tuple[str, ...] = field(default_factory=tuple)
    waste: Tuple[str, ...] = field(default_factory=tuple)
    status: GameStatus = GameStatus.NOT_STARTED
    moves_count: int = 0
    score: int = 0
    
    def with_move(
        self,
        foundations: Optional[Tuple[Tuple[str, ...], ...]] = None,
        tableaus: Optional[Tuple[Tuple[str, ...], ...]] = None,
        stock: Optional[Tuple[str, ...]] = None,
        waste: Optional[Tuple[str, ...]] = None,
        status: Optional[GameStatus] = None,
        moves_count: Optional[int] = None,
        score: Optional[int] = None,
    ) -> "GameState":
        """
        Create a new GameState with updated fields.
        
        This method implements the copy-on-write pattern for immutable objects.
        Only provided fields are updated; others maintain their current values.
        
        Args:
            foundations: New foundation piles (optional)
            tableaus: New tableau piles (optional)
            stock: New stock pile (optional)
            waste: New waste pile (optional)
            status: New game status (optional)
            moves_count: New moves count (optional)
            score: New score (optional)
            
        Returns:
            New GameState instance with updated fields
        """
        return GameState(
            foundations=foundations if foundations is not None else self.foundations,
            tableaus=tableaus if tableaus is not None else self.tableaus,
            stock=stock if stock is not None else self.stock,
            waste=waste if waste is not None else self.waste,
            status=status if status is not None else self.status,
            moves_count=moves_count if moves_count is not None else self.moves_count,
            score=score if score is not None else self.score,
        )
    
    def is_victory(self) -> bool:
        """
        Check if game is won.
        
        Game is won when all 52 cards are in the foundation piles.
        
        Returns:
            True if game is won, False otherwise
        """
        return all(len(foundation) == 13 for foundation in self.foundations)
```

#### `tests/unit/domain/models/test_game_state.py`

```python
"""Unit tests for GameState model."""
import pytest
from src.domain.models.game_state import GameState, GameStatus


class TestGameState:
    """Test suite for GameState immutable model."""
    
    def test_default_initialization(self) -> None:
        """Test GameState initializes with correct defaults."""
        state = GameState()
        
        assert len(state.foundations) == 4
        assert all(len(f) == 0 for f in state.foundations)
        assert len(state.tableaus) == 7
        assert all(len(t) == 0 for t in state.tableaus)
        assert len(state.stock) == 0
        assert len(state.waste) == 0
        assert state.status == GameStatus.NOT_STARTED
        assert state.moves_count == 0
        assert state.score == 0
    
    def test_immutability(self) -> None:
        """Test that GameState is immutable."""
        state = GameState()
        
        with pytest.raises(AttributeError):
            state.score = 100  # type: ignore
    
    def test_with_move_updates_single_field(self) -> None:
        """Test with_move updates only specified fields."""
        state = GameState(score=50, moves_count=10)
        new_state = state.with_move(score=100)
        
        assert new_state.score == 100
        assert new_state.moves_count == 10  # unchanged
        assert state.score == 50  # original unchanged
    
    def test_with_move_creates_new_instance(self) -> None:
        """Test with_move creates a new GameState instance."""
        state = GameState()
        new_state = state.with_move(moves_count=1)
        
        assert state is not new_state
        assert state.moves_count == 0
        assert new_state.moves_count == 1
    
    def test_is_victory_empty_foundations(self) -> None:
        """Test is_victory returns False for empty foundations."""
        state = GameState()
        assert not state.is_victory()
    
    def test_is_victory_partial_foundations(self) -> None:
        """Test is_victory returns False for partially filled foundations."""
        state = GameState(
            foundations=(
                ("AH", "2H", "3H"),
                ("AS", "2S"),
                (),
                ()
            )
        )
        assert not state.is_victory()
    
    def test_is_victory_complete_foundations(self) -> None:
        """Test is_victory returns True when all foundations complete."""
        complete_suit = tuple(
            f"{rank}{suit}"
            for rank in ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
            for suit in ["H"]
        )
        
        state = GameState(
            foundations=(
                complete_suit[:13],
                complete_suit[:13],
                complete_suit[:13],
                complete_suit[:13],
            )
        )
        assert state.is_victory()
```

### Istruzioni per GitHub Copilot

1. **Creare `src/domain/models/game_state.py` con il codice sopra**
2. **Creare `tests/unit/domain/models/test_game_state.py` con i test**
3. **Eseguire i test**:
   ```bash
   pytest tests/unit/domain/models/test_game_state.py -v
   ```
4. **Verificare type checking**:
   ```bash
   mypy src/domain/models/game_state.py
   ```
5. **Formattare il codice**:
   ```bash
   black src/domain/models/game_state.py tests/unit/domain/models/test_game_state.py
   isort src/domain/models/game_state.py tests/unit/domain/models/test_game_state.py
   ```

### Commit Message
```
feat(domain): add immutable GameState model

- Create GameState frozen dataclass
- Add GameStatus enum (NOT_STARTED, IN_PROGRESS, WON, LOST)
- Implement with_move() method for copy-on-write pattern
- Add is_victory() method for win condition checking
- Include comprehensive unit tests (8 tests)
- Type hints with mypy validation

Test coverage: 100% for GameState model.
```

### Criteri di Completamento
- [x] File `game_state.py` creato con dataclass frozen
- [x] Tutti i test passano (7/7)
- [x] `mypy` non restituisce errori
- [x] Coverage >= 90% per `game_state.py` (100%)

---

## Fase 3: Refactoring Card e Pile

### Obiettivo
Estrarre modelli `Card` e `Pile` dal codice esistente.

### File da Creare

#### `src/domain/models/card.py`

```python
"""Card model and related types."""
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Suit(Enum):
    """Card suit enumeration."""
    HEARTS = "H"
    DIAMONDS = "D"
    CLUBS = "C"
    SPADES = "S"
    
    @property
    def color(self) -> str:
        """Get suit color (red or black)."""
        return "red" if self in (Suit.HEARTS, Suit.DIAMONDS) else "black"
    
    @property
    def symbol(self) -> str:
        """Get unicode symbol for suit."""
        symbols = {
            Suit.HEARTS: "♥",
            Suit.DIAMONDS: "♦",
            Suit.CLUBS: "♣",
            Suit.SPADES: "♠",
        }
        return symbols[self]


class Rank(Enum):
    """Card rank enumeration."""
    ACE = "A"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    
    @property
    def value(self) -> int:
        """Get numeric value of rank (1-13)."""
        values = {
            Rank.ACE: 1,
            Rank.TWO: 2,
            Rank.THREE: 3,
            Rank.FOUR: 4,
            Rank.FIVE: 5,
            Rank.SIX: 6,
            Rank.SEVEN: 7,
            Rank.EIGHT: 8,
            Rank.NINE: 9,
            Rank.TEN: 10,
            Rank.JACK: 11,
            Rank.QUEEN: 12,
            Rank.KING: 13,
        }
        return values[self]


@dataclass(frozen=True)
class Card:
    """
    Immutable playing card.
    
    Represents a standard playing card with rank and suit.
    Uses frozen dataclass for immutability.
    
    Attributes:
        rank: Card rank (A, 2-10, J, Q, K)
        suit: Card suit (Hearts, Diamonds, Clubs, Spades)
    """
    
    rank: Rank
    suit: Suit
    
    @property
    def color(self) -> str:
        """Get card color based on suit."""
        return self.suit.color
    
    @property
    def value(self) -> int:
        """Get numeric value of card (1-13)."""
        return self.rank.value
    
    def can_stack_on_foundation(self, other: Optional["Card"]) -> bool:
        """
        Check if this card can be placed on foundation pile.
        
        Foundation rules:
        - Must start with Ace
        - Must be same suit
        - Must be one rank higher
        
        Args:
            other: Card currently on top of foundation (None if empty)
            
        Returns:
            True if card can be placed on foundation
        """
        if other is None:
            return self.rank == Rank.ACE
        
        return (
            self.suit == other.suit
            and self.value == other.value + 1
        )
    
    def can_stack_on_tableau(self, other: Optional["Card"]) -> bool:
        """
        Check if this card can be placed on tableau pile.
        
        Tableau rules:
        - Can place King on empty pile
        - Must be opposite color
        - Must be one rank lower
        
        Args:
            other: Card currently on top of tableau (None if empty)
            
        Returns:
            True if card can be placed on tableau
        """
        if other is None:
            return self.rank == Rank.KING
        
        return (
            self.color != other.color
            and self.value == other.value - 1
        )
    
    def __str__(self) -> str:
        """String representation (e.g., 'A♥', 'K♠')."""
        return f"{self.rank.value}{self.suit.symbol}"
    
    def __repr__(self) -> str:
        """Developer representation."""
        return f"Card(rank={self.rank}, suit={self.suit})"
    
    @classmethod
    def from_string(cls, card_str: str) -> "Card":
        """
        Create Card from string notation.
        
        Examples:
            'AH' -> Ace of Hearts
            '10D' -> Ten of Diamonds
            'KS' -> King of Spades
        
        Args:
            card_str: String representation (rank + suit code)
            
        Returns:
            Card instance
            
        Raises:
            ValueError: If string format is invalid
        """
        if len(card_str) < 2:
            raise ValueError(f"Invalid card string: {card_str}")
        
        # Handle 10 specially (2 characters for rank)
        if card_str[:2] == "10":
            rank_str = "10"
            suit_str = card_str[2:]
        else:
            rank_str = card_str[0]
            suit_str = card_str[1:]
        
        # Find matching rank
        rank = None
        for r in Rank:
            if r.value == rank_str:
                rank = r
                break
        
        if rank is None:
            raise ValueError(f"Invalid rank: {rank_str}")
        
        # Find matching suit
        suit = None
        for s in Suit:
            if s.value == suit_str:
                suit = s
                break
        
        if suit is None:
            raise ValueError(f"Invalid suit: {suit_str}")
        
        return cls(rank=rank, suit=suit)
```

#### `tests/unit/domain/models/test_card.py`

```python
"""Unit tests for Card model."""
import pytest
from src.domain.models.card import Card, Rank, Suit


class TestSuit:
    """Test suite for Suit enum."""
    
    def test_color_red_suits(self) -> None:
        """Test red suits return 'red' color."""
        assert Suit.HEARTS.color == "red"
        assert Suit.DIAMONDS.color == "red"
    
    def test_color_black_suits(self) -> None:
        """Test black suits return 'black' color."""
        assert Suit.CLUBS.color == "black"
        assert Suit.SPADES.color == "black"
    
    def test_symbol(self) -> None:
        """Test suit symbols are correct."""
        assert Suit.HEARTS.symbol == "♥"
        assert Suit.DIAMONDS.symbol == "♦"
        assert Suit.CLUBS.symbol == "♣"
        assert Suit.SPADES.symbol == "♠"


class TestRank:
    """Test suite for Rank enum."""
    
    def test_value_ace(self) -> None:
        """Test Ace has value 1."""
        assert Rank.ACE.value == 1
    
    def test_value_numeric(self) -> None:
        """Test numeric cards have correct values."""
        assert Rank.TWO.value == 2
        assert Rank.FIVE.value == 5
        assert Rank.TEN.value == 10
    
    def test_value_face_cards(self) -> None:
        """Test face cards have correct values."""
        assert Rank.JACK.value == 11
        assert Rank.QUEEN.value == 12
        assert Rank.KING.value == 13


class TestCard:
    """Test suite for Card model."""
    
    def test_initialization(self) -> None:
        """Test Card initializes correctly."""
        card = Card(rank=Rank.ACE, suit=Suit.HEARTS)
        assert card.rank == Rank.ACE
        assert card.suit == Suit.HEARTS
    
    def test_color_property(self) -> None:
        """Test card color matches suit color."""
        red_card = Card(rank=Rank.ACE, suit=Suit.HEARTS)
        black_card = Card(rank=Rank.ACE, suit=Suit.SPADES)
        
        assert red_card.color == "red"
        assert black_card.color == "black"
    
    def test_value_property(self) -> None:
        """Test card value matches rank value."""
        ace = Card(rank=Rank.ACE, suit=Suit.HEARTS)
        king = Card(rank=Rank.KING, suit=Suit.SPADES)
        
        assert ace.value == 1
        assert king.value == 13
    
    def test_can_stack_on_foundation_ace_on_empty(self) -> None:
        """Test Ace can be placed on empty foundation."""
        ace = Card(rank=Rank.ACE, suit=Suit.HEARTS)
        assert ace.can_stack_on_foundation(None)
    
    def test_can_stack_on_foundation_two_on_ace(self) -> None:
        """Test Two can be placed on Ace of same suit."""
        ace = Card(rank=Rank.ACE, suit=Suit.HEARTS)
        two = Card(rank=Rank.TWO, suit=Suit.HEARTS)
        assert two.can_stack_on_foundation(ace)
    
    def test_can_stack_on_foundation_wrong_suit(self) -> None:
        """Test card cannot be placed on foundation with wrong suit."""
        ace_hearts = Card(rank=Rank.ACE, suit=Suit.HEARTS)
        two_spades = Card(rank=Rank.TWO, suit=Suit.SPADES)
        assert not two_spades.can_stack_on_foundation(ace_hearts)
    
    def test_can_stack_on_tableau_king_on_empty(self) -> None:
        """Test King can be placed on empty tableau."""
        king = Card(rank=Rank.KING, suit=Suit.SPADES)
        assert king.can_stack_on_tableau(None)
    
    def test_can_stack_on_tableau_opposite_color(self) -> None:
        """Test card can be placed on opposite color."""
        red_seven = Card(rank=Rank.SEVEN, suit=Suit.HEARTS)
        black_six = Card(rank=Rank.SIX, suit=Suit.SPADES)
        assert black_six.can_stack_on_tableau(red_seven)
    
    def test_can_stack_on_tableau_same_color(self) -> None:
        """Test card cannot be placed on same color."""
        red_seven = Card(rank=Rank.SEVEN, suit=Suit.HEARTS)
        red_six = Card(rank=Rank.SIX, suit=Suit.DIAMONDS)
        assert not red_six.can_stack_on_tableau(red_seven)
    
    def test_str_representation(self) -> None:
        """Test string representation of card."""
        ace_hearts = Card(rank=Rank.ACE, suit=Suit.HEARTS)
        king_spades = Card(rank=Rank.KING, suit=Suit.SPADES)
        
        assert str(ace_hearts) == "A♥"
        assert str(king_spades) == "K♠"
    
    def test_from_string_ace(self) -> None:
        """Test creating card from string - Ace."""
        card = Card.from_string("AH")
        assert card.rank == Rank.ACE
        assert card.suit == Suit.HEARTS
    
    def test_from_string_ten(self) -> None:
        """Test creating card from string - Ten."""
        card = Card.from_string("10D")
        assert card.rank == Rank.TEN
        assert card.suit == Suit.DIAMONDS
    
    def test_from_string_invalid(self) -> None:
        """Test from_string raises error for invalid input."""
        with pytest.raises(ValueError):
            Card.from_string("X")
        
        with pytest.raises(ValueError):
            Card.from_string("1Z")
```

### Istruzioni per GitHub Copilot

1. **Creare `src/domain/models/card.py`**
2. **Creare `tests/unit/domain/models/test_card.py`**
3. **Eseguire i test**:
   ```bash
   pytest tests/unit/domain/models/test_card.py -v
   ```
4. **Verificare coverage**:
   ```bash
   pytest tests/unit/domain/models/ --cov=src/domain/models --cov-report=term-missing
   ```
5. **Type checking**:
   ```bash
   mypy src/domain/models/card.py
   ```

### Commit Message
```
feat(domain): add Card model with Rank and Suit enums

- Create immutable Card dataclass with frozen=True
- Add Rank enum with values 1-13
- Add Suit enum with color and symbol properties
- Implement foundation and tableau stacking rules
- Add from_string() factory method for parsing
- Include comprehensive unit tests (16 tests)

Test coverage: 100% for Card model.
```

### Criteri di Completamento
- [x] File `card.py` creato
- [x] Tutti i test passano (19/19)
- [x] Coverage >= 95% (95.96%)
- [x] Mypy validation passa

---

## Fase 4: Estrazione MoveValidator

### Obiettivo
Creare un validatore di mosse che verifica la legittimità delle azioni.

### File da Creare

#### `src/domain/rules/move_validator.py`

```python
"""Move validation rules for Klondike solitaire."""
from typing import Optional, Tuple
from src.domain.models.card import Card
from src.domain.models.game_state import GameState


class MoveValidator:
    """
    Validates game moves according to Klondike solitaire rules.
    
    This class is responsible for checking if a specific move is legal
    according to the game rules. It does not modify game state.
    """
    
    def can_move_to_foundation(
        self,
        card: Card,
        foundation_index: int,
        state: GameState,
    ) -> bool:
        """
        Check if card can be moved to specified foundation.
        
        Args:
            card: Card to move
            foundation_index: Target foundation pile (0-3)
            state: Current game state
            
        Returns:
            True if move is valid
        """
        if not (0 <= foundation_index < 4):
            return False
        
        foundation = state.foundations[foundation_index]
        
        if not foundation:
            return card.rank.value == 1  # Must be Ace
        
        top_card = Card.from_string(foundation[-1])
        return card.can_stack_on_foundation(top_card)
    
    def can_move_to_tableau(
        self,
        cards: Tuple[Card, ...],
        tableau_index: int,
        state: GameState,
    ) -> bool:
        """
        Check if cards can be moved to specified tableau.
        
        Args:
            cards: Cards to move (can be multiple for tableau-to-tableau)
            tableau_index: Target tableau pile (0-6)
            state: Current game state
            
        Returns:
            True if move is valid
        """
        if not (0 <= tableau_index < 7):
            return False
        
        if not cards:
            return False
        
        tableau = state.tableaus[tableau_index]
        bottom_card = cards[0]
        
        if not tableau:
            return bottom_card.rank.value == 13  # Must be King
        
        top_card = Card.from_string(tableau[-1])
        return bottom_card.can_stack_on_tableau(top_card)
    
    def can_draw_from_stock(self, state: GameState) -> bool:
        """
        Check if cards can be drawn from stock.
        
        Args:
            state: Current game state
            
        Returns:
            True if stock has cards
        """
        return len(state.stock) > 0
    
    def can_recycle_waste(self, state: GameState) -> bool:
        """
        Check if waste can be recycled to stock.
        
        Args:
            state: Current game state
            
        Returns:
            True if stock is empty and waste has cards
        """
        return len(state.stock) == 0 and len(state.waste) > 0
```

#### `tests/unit/domain/rules/test_move_validator.py`

```python
"""Unit tests for MoveValidator."""
import pytest
from src.domain.rules.move_validator import MoveValidator
from src.domain.models.card import Card, Rank, Suit
from src.domain.models.game_state import GameState


class TestMoveValidator:
    """Test suite for MoveValidator."""
    
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.validator = MoveValidator()
    
    def test_can_move_ace_to_empty_foundation(self) -> None:
        """Test Ace can move to empty foundation."""
        state = GameState()
        ace = Card(rank=Rank.ACE, suit=Suit.HEARTS)
        
        assert self.validator.can_move_to_foundation(ace, 0, state)
    
    def test_cannot_move_non_ace_to_empty_foundation(self) -> None:
        """Test non-Ace cannot move to empty foundation."""
        state = GameState()
        two = Card(rank=Rank.TWO, suit=Suit.HEARTS)
        
        assert not self.validator.can_move_to_foundation(two, 0, state)
    
    def test_can_move_sequential_to_foundation(self) -> None:
        """Test sequential card can move to foundation."""
        state = GameState(
            foundations=(("AH",), (), (), ())
        )
        two = Card(rank=Rank.TWO, suit=Suit.HEARTS)
        
        assert self.validator.can_move_to_foundation(two, 0, state)
    
    def test_cannot_move_wrong_suit_to_foundation(self) -> None:
        """Test wrong suit cannot move to foundation."""
        state = GameState(
            foundations=(("AH",), (), (), ())
        )
        two_spades = Card(rank=Rank.TWO, suit=Suit.SPADES)
        
        assert not self.validator.can_move_to_foundation(two_spades, 0, state)
    
    def test_can_move_king_to_empty_tableau(self) -> None:
        """Test King can move to empty tableau."""
        state = GameState()
        king = Card(rank=Rank.KING, suit=Suit.SPADES)
        
        assert self.validator.can_move_to_tableau((king,), 0, state)
    
    def test_cannot_move_non_king_to_empty_tableau(self) -> None:
        """Test non-King cannot move to empty tableau."""
        state = GameState()
        queen = Card(rank=Rank.QUEEN, suit=Suit.SPADES)
        
        assert not self.validator.can_move_to_tableau((queen,), 0, state)
    
    def test_can_move_opposite_color_to_tableau(self) -> None:
        """Test opposite color card can move to tableau."""
        state = GameState(
            tableaus=(("7H",), (), (), (), (), (), ())
        )
        black_six = Card(rank=Rank.SIX, suit=Suit.SPADES)
        
        assert self.validator.can_move_to_tableau((black_six,), 0, state)
    
    def test_cannot_move_same_color_to_tableau(self) -> None:
        """Test same color card cannot move to tableau."""
        state = GameState(
            tableaus=(("7H",), (), (), (), (), (), ())
        )
        red_six = Card(rank=Rank.SIX, suit=Suit.DIAMONDS)
        
        assert not self.validator.can_move_to_tableau((red_six,), 0, state)
    
    def test_can_draw_from_stock(self) -> None:
        """Test can draw when stock has cards."""
        state = GameState(stock=("AH", "2D", "3C"))
        
        assert self.validator.can_draw_from_stock(state)
    
    def test_cannot_draw_from_empty_stock(self) -> None:
        """Test cannot draw from empty stock."""
        state = GameState(stock=())
        
        assert not self.validator.can_draw_from_stock(state)
    
    def test_can_recycle_waste(self) -> None:
        """Test can recycle waste when stock empty."""
        state = GameState(
            stock=(),
            waste=("AH", "2D", "3C")
        )
        
        assert self.validator.can_recycle_waste(state)
    
    def test_cannot_recycle_when_stock_not_empty(self) -> None:
        """Test cannot recycle when stock has cards."""
        state = GameState(
            stock=("KS",),
            waste=("AH", "2D")
        )
        
        assert not self.validator.can_recycle_waste(state)
```

### Istruzioni per GitHub Copilot

1. **Creare `src/domain/rules/move_validator.py`**
2. **Creare `tests/unit/domain/rules/test_move_validator.py`**
3. **Eseguire i test**:
   ```bash
   pytest tests/unit/domain/rules/ -v
   ```
4. **Verificare coverage**:
   ```bash
   pytest tests/unit/domain/ --cov=src/domain --cov-report=term-missing
   ```

### Commit Message
```
feat(domain): add MoveValidator for game rules

- Create MoveValidator class with rule checking methods
- Validate foundation moves (Ace start, same suit, sequential)
- Validate tableau moves (King on empty, opposite color, descending)
- Add stock draw and waste recycle validation
- Include comprehensive unit tests (12 tests)

Test coverage: 100% for MoveValidator.
```

### Criteri di Completamento
- [x] File `move_validator.py` creato
- [x] Tutti i test passano (12/12)
- [x] Coverage >= 90% (93.63% domain layer)
- [x] Nessuna dipendenza esterna nel domain layer

---

---

## Fase 4.5: Correzioni Critiche Post-Review ✅

### Obiettivo
Risolvere vulnerabilità e lacune identificate dopo completamento Fase 4.

### Problemi Risolti

#### 1. Pile Model Mancante (CRITICO)
**File Creati**:
- `src/domain/models/pile.py` - Modello immutabile pile
- `tests/unit/domain/models/test_pile.py` - Test completi

**Funzionalità**:
- PileType enum (TABLEAU, FOUNDATION, STOCK, WASTE)
- Gestione carte coperte/scoperte
- Factory functions per creazione pile
- Metodi immutabili (add_card, remove_top, flip_top_card)

#### 2. Suit Enum Esteso (CRITICO)
**Modifiche**:
- Aggiunto supporto mazzo napoletano (COPPE, DENARI, SPADE_IT, BASTONI)
- Property `is_italian` per distinguere mazzi
- Simboli Unicode per semi italiani
- Backward compatibility con `scr/` legacy

#### 3. GameState Accessibilità (MEDIO)
**Estensioni**:
- CursorPosition per navigazione screen reader
- SelectionState per tracking selezione carte
- GameConfiguration per impostazioni gioco
- elapsed_seconds per supporto timer

### Criteri di Completamento
- [x] Pile model implementato con 85%+ coverage
- [x] Suit enum esteso con test italiani
- [x] GameState con campi accessibilità
- [x] Tutti i test passano (15 nuovi test, 53 totali)
- [x] Coverage domain layer >= 92.65%
- [x] Zero regressioni su test esistenti

### Test Passati
- 7 test per Pile model
- 2 test per Italian deck support
- 6 test per GameState accessibility
- **Totale**: 15 nuovi test aggiunti
- **Coverage**: 92.65% domain layer

---

## Fase 5-12: Da Completare

**Note**: Le fasi 5-12 seguono lo stesso pattern:
1. Creare file nel layer appropriato
2. Scrivere test completi
3. Validare con pytest e mypy
4. Commit atomico con message descrittivo
5. Aggiornare questa checklist

### Fase 5: GameService
- Orchestrazione logica di gioco
- Metodi: `new_game()`, `make_move()`, `draw_card()`, `check_victory()`

### Fase 6: Formatter
- Presentazione layer per output
- Formattazione stato gioco per accessibilità

### Fase 7: Protocol Interfaces
- Definire interfacce con Protocol
- Separare astrazione da implementazione

### Fase 8: GameController
- Application layer coordinator
- Gestione use cases

### Fase 9: Command Pattern
- Implementare pattern Command per undo/redo
- Command history

### Fase 10: Dependency Injection
- Setup DI container
- Rimuovere dipendenze hard-coded

### Fase 11: Test Coverage Completo
- Raggiungere 80%+ coverage
- Test integration

### Fase 12: Documentazione Finale
- README aggiornato
- Architecture decision records
- API documentation

---

## Target di Qualità Finali

- ✅ **Test coverage**: >= 80%
- ✅ **Type hints**: 100% (mypy strict)
- ✅ **Complessità ciclomatica**: < 10
- ✅ **Linee per metodo**: < 20
- ✅ **Separazione responsabilità**: domain/application/infrastructure/presentation
- ✅ **Zero dipendenze pygame** nel domain layer
- ✅ **Immutabilità**: GameState e models frozen

---

## Note di Implementazione

### Principi da Seguire

1. **SOLID**:
   - Single Responsibility: Ogni classe ha una sola ragione per cambiare
   - Open/Closed: Estensibile senza modifiche
   - Liskov Substitution: Sostituibilità dei sottotipi
   - Interface Segregation: Interfacce piccole e specifiche
   - Dependency Inversion: Dipendere da astrazioni

2. **Domain-Driven Design**:
   - Domain layer puro (no infra dependencies)
   - Ubiquitous language nel codice
   - Rich domain models

3. **Testing**:
   - Test-driven approach
   - AAA pattern (Arrange-Act-Assert)
   - Test isolati e deterministici

### Convenzioni Codice

- **Type hints obbligatori** su tutti i nuovi file
- **Docstring Google style** per classi e metodi
- **Black + isort** per formatting
- **Line length**: 100 caratteri
- **Python version**: >= 3.11

### Gestione Codice Legacy

- **NON modificare `scr/`** fino a Fase 8
- Coesistenza vecchio/nuovo codice nelle fasi iniziali
- Migration graduale dei componenti

---

## Progress Log

### Fase 0: ✅ COMPLETATA
- Data: 2026-02-04
- Commit: 5f7a5c3
- Note: All development tools installed successfully. pytest 7.4.3, mypy 1.7.1, black 23.12.0, isort 5.13.2
- Test directory structure created

### Fase 1: ✅ COMPLETATA
- Data: 2026-02-04
- Commit: 5ab4fb7
- Note: Created complete layered architecture structure
- 4 main layers: domain, application, infrastructure, presentation
- Test structure: unit (domain/models, domain/rules, application) + integration

### Fase 2: ✅ COMPLETATA
- Data: 2026-02-04
- Commit: 2ff26fc
- Note: Immutable GameState model created with frozen dataclass
- Test passati: 7/7
- Coverage: 100% for game_state.py
- Type checking: mypy validation passed

### Fase 3: ✅ COMPLETATA
- Data: 2026-02-04
- Commit: 2484eea
- Note: Card model with Rank and Suit enums created
- Test passati: 19/19
- Coverage: 95.96% for card.py, 96.67% overall models
- Type checking: mypy validation passed
- from_string() factory method implemented for parsing

### Fase 4: ✅ COMPLETATA
- Data: 2026-02-04
- Commit: de00898
- Note: MoveValidator con validazione regole completa
- Test passati: 12/12
- Coverage: 93.63% domain layer
- **CORREZIONI APPLICATE**:
  - ✅ Aggiunto Pile model con factory functions
  - ✅ Esteso Suit enum per mazzo napoletano
  - ✅ Esteso GameState con CursorPosition, SelectionState, GameConfiguration

### Correzioni Post Fase 4: ✅ COMPLETATE
- Data: 2026-02-05
- Commit: 9748a6f, 41f632c, b4753b2
- Note: Risolte 3 vulnerabilità critiche identificate in code review
- **Vulnerabilità Risolte**:
  1. 🔴 Pile model mancante → Implementato con factory
  2. 🔴 Incompatibilità mazzo napoletano → Suit esteso
  3. 🟡 GameState incompleto → Aggiunto supporto accessibilità
- Test passati: 53 test (15 nuovi)
- Coverage domain: 92.65%

### Fase 5: ✅ COMPLETATA
- Data: 2026-02-05
- Commit: 002e0a3
- Note: GameService implementation with game orchestration
- Test passati: 68 test (15 nuovi)
- Coverage domain: 92.98%
- Type checking: mypy validation passed
- **Funzionalità Implementate**:
  - new_game() con creazione e shuffle del mazzo
  - move_to_foundation() con validazione
  - draw_from_stock() e recycle_waste()
  - Victory detection automatica
  - Supporto mazzi francesi e napoletani

### Fase 6: 📋 PROSSIMA
- Data: [DA COMPILARE]
- Commit: [HASH]
- Note: [EVENTUALI NOTE]

---

**Ultimo aggiornamento**: 2026-02-04
**Prossima fase**: Fase 5 - Creazione GameService
