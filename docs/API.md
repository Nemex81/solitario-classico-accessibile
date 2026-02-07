# API Documentation

## 📚 Panoramica

Questo documento descrive l'API pubblica del Solitario Classico Accessibile.

## 🎮 GameController

Il `GameController` è il punto di ingresso principale per interagire con il gioco.

### Inizializzazione

```python
from src.infrastructure.di_container import get_container

container = get_container()
controller = container.get_game_controller()
```

### Metodi

#### `start_new_game(difficulty: str = "easy", deck_type: str = "french") -> str`

Inizia una nuova partita.

**Parametri:**
- `difficulty`: Difficoltà del gioco (`"easy"`, `"medium"`, `"hard"`)
- `deck_type`: Tipo di mazzo (`"french"`, `"neapolitan"`)

**Ritorna:**
- Stringa formattata con lo stato iniziale del gioco

**Esempio:**
```python
result = controller.start_new_game(difficulty="easy", deck_type="french")
print(result)
# Output:
# Stato: In corso
# Mosse: 0
# Punteggio: 0
# ...
```

---

#### `execute_move(action: str, source_pile: str = None, source_index: int = None, target_pile: str = None, target_index: int = None) -> Tuple[bool, str]`

Esegue una mossa nel gioco.

**Parametri:**
- `action`: Tipo di azione
  - `"draw"`: Pesca carte dal mazzo
  - `"recycle"`: Rimescola gli scarti nel mazzo
  - `"move_to_foundation"`: Sposta carta alla base
- `source_pile`: Tipo di pila sorgente (`"tableau"`, `"waste"`)
- `source_index`: Indice della pila sorgente (0-6 per tableau)
- `target_pile`: Tipo di pila destinazione
- `target_index`: Indice della pila destinazione (0-3 per foundation)

**Ritorna:**
- Tupla `(success: bool, message: str)`

**Esempi:**
```python
# Pescare dal mazzo
success, message = controller.execute_move("draw")
# (True, "Carte pescate dal mazzo")

# Rimescolare
success, message = controller.execute_move("recycle")
# (True, "Scarti rimescolati nel mazzo")

# Spostare alla base
success, message = controller.execute_move(
    "move_to_foundation",
    source_pile="tableau",
    source_index=0,
    target_index=0
)
# (True, "Carta spostata alla base")
```

---

#### `get_current_state_formatted() -> str`

Ottiene lo stato corrente del gioco formattato.

**Ritorna:**
- Stringa formattata con lo stato completo

**Esempio:**
```python
state = controller.get_current_state_formatted()
print(state)
# Output:
# Stato: In corso
# Mosse: 5
# Punteggio: 30
# 
# === BASI (Foundation) ===
# Base Cuori: vuota
# Base Quadri: 1 carte, in cima AD
# ...
```

---

#### `get_cursor_position_formatted() -> str`

Ottiene la posizione corrente del cursore.

**Ritorna:**
- Stringa con la descrizione della posizione

**Esempio:**
```python
position = controller.get_cursor_position_formatted()
# "Tableau 1, carta 3: Q♠"
```

---

## 🃏 GameState

Rappresentazione immutabile dello stato del gioco.

### Attributi

| Attributo | Tipo | Descrizione |
|-----------|------|-------------|
| `foundations` | `Tuple[Tuple[str, ...], ...]` | 4 pile di fondazione |
| `tableaus` | `Tuple[Tuple[str, ...], ...]` | 7 pile tableau |
| `stock` | `Tuple[str, ...]` | Mazzo |
| `waste` | `Tuple[str, ...]` | Scarti |
| `status` | `GameStatus` | Stato del gioco |
| `moves_count` | `int` | Numero di mosse |
| `score` | `int` | Punteggio |
| `cursor` | `CursorPosition` | Posizione cursore |

### Metodi

#### `with_move(**kwargs) -> GameState`

Crea un nuovo stato con i campi modificati.

```python
new_state = state.with_move(
    score=state.score + 10,
    moves_count=state.moves_count + 1
)
```

---

#### `is_victory() -> bool`

Verifica se il gioco è vinto.

```python
if state.is_victory():
    print("Hai vinto!")
```

---

## 📜 CommandHistory

Gestisce la cronologia dei comandi per undo/redo.

### Inizializzazione

```python
from src.application.commands import CommandHistory

history = CommandHistory(max_size=100)
```

### Metodi

#### `execute(command: Command, state: GameState) -> GameState`

Esegue un comando e lo aggiunge alla cronologia.

```python
from src.application.commands import DrawCommand

command = DrawCommand()
new_state = history.execute(command, current_state)
```

---

#### `undo(state: GameState) -> GameState`

Annulla l'ultimo comando.

```python
if history.can_undo():
    state = history.undo(state)
```

---

#### `redo(state: GameState) -> GameState`

Ripete il comando annullato.

```python
if history.can_redo():
    state = history.redo(state)
```

---

#### `can_undo() -> bool`

Verifica se è possibile annullare.

---

#### `can_redo() -> bool`

Verifica se è possibile ripetere.

---

#### `get_undo_description() -> Optional[str]`

Ottiene la descrizione del comando da annullare.

```python
desc = history.get_undo_description()
# "Spostare 1 carte da tableau_0 a foundation_0"
```

---

## 🎨 GameFormatter

Formattazione accessibile dello stato di gioco.

### Inizializzazione

```python
from src.presentation.game_formatter import GameFormatter

formatter = GameFormatter(language="it")
```

### Metodi

#### `format_game_state(state: GameState) -> str`

Formatta lo stato completo del gioco.

---

#### `format_cursor_position(state: GameState) -> str`

Formatta la posizione del cursore.

---

#### `format_move_result(success: bool, message: str) -> str`

Formatta il risultato di una mossa.

```python
result = formatter.format_move_result(True, "Carta spostata")
# "✓ Carta spostata"

result = formatter.format_move_result(False, "Mossa non valida")
# "✗ Mossa non valida"
```

---

#### `format_card_list(cards: List[str]) -> str`

Formatta una lista di carte.

```python
result = formatter.format_card_list(["AH", "2D", "3C"])
# "AH, 2D, 3C"

result = formatter.format_card_list([])
# "nessuna carta"
```

---

## 💉 DIContainer

Container per dependency injection.

### Utilizzo

```python
from src.infrastructure.di_container import DIContainer, get_container

# Istanza locale
container = DIContainer()

# Istanza globale (singleton)
container = get_container()
```

### Metodi

| Metodo | Ritorna | Descrizione |
|--------|---------|-------------|
| `get_move_validator()` | `MoveValidator` | Validatore mosse (singleton) |
| `get_game_service()` | `GameService` | Servizio di gioco (singleton) |
| `get_formatter(language)` | `GameFormatter` | Formatter per lingua |
| `get_command_history()` | `CommandHistory` | Cronologia comandi |
| `get_game_controller()` | `GameController` | Controller principale |
| `reset()` | `None` | Resetta tutte le istanze |

---

## 📋 Enum e Costanti

### GameStatus

```python
from src.domain.models.game_state import GameStatus

GameStatus.NOT_STARTED  # Partita non iniziata
GameStatus.IN_PROGRESS  # Partita in corso
GameStatus.WON          # Partita vinta
GameStatus.LOST         # Partita persa
```

### Suit

```python
from src.domain.models.card import Suit

# Mazzo francese
Suit.HEARTS    # Cuori (♥)
Suit.DIAMONDS  # Quadri (♦)
Suit.CLUBS     # Fiori (♣)
Suit.SPADES    # Picche (♠)

# Mazzo napoletano
Suit.COPPE     # Coppe (🍷)
Suit.DENARI    # Denari (🪙)
Suit.SPADE_IT  # Spade (🗡️)
Suit.BASTONI   # Bastoni (🏑)
```

### Rank

```python
from src.domain.models.card import Rank

Rank.ACE    # Asso (valore 1)
Rank.TWO    # Due (valore 2)
# ... fino a ...
Rank.KING   # Re (valore 13)
```

---

## 🔒 Type Hints

Tutti i metodi pubblici sono completamente tipizzati. Per verificare:

```bash
mypy src/ --strict
```
