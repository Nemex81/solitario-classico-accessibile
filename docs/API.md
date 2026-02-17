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

## 🔢 Counter Duality: Statistics vs Scoring

### Draw Counters

Il sistema mantiene **due contatori distinti** per le pescate dal mazzo:

#### `GameService.draw_count` (Legacy - Azioni)
- **Tipo:** `int` (contatore azioni di pescata)
- **Scope:** Statistiche finali
- **Incremento:** `+1` per ogni **azione** di pescata (es. pressione tasto D/P)
- **Esempio:** Dopo 7 draw-3 → `draw_count = 7`
- **Uso:** Report finali, logging analytics

#### `ScoringService.stock_draw_count` (v2.0 - Carte)
- **Tipo:** `int` (contatore carte pescate)
- **Scope:** Calcolo penalità progressive (soglie 21/41)
- **Incremento:** `+1` per ogni **carta fisica** pescata (`record_event(STOCK_DRAW)`)
- **Esempio:** Dopo 7 draw-3 → `stock_draw_count = 21`
- **Uso:** Calcolo score, threshold warnings

**⚠️ IMPORTANTE:**
- I warnings TTS leggono `stock_draw_count` (quello per le penalità)
- Non confondere i due: hanno granularità diversa (azioni vs carte)
- `stock_draw_count` è accurato perché `record_event()` è chiamato **per ogni carta** dentro `if card:` guard

---

### Recycle Counters

Il sistema mantiene **due contatori distinti** per i ricicli waste→stock:

#### `GameService.recycle_count` (Legacy - Statistics)
- **Tipo:** `int` (contatore ricicli totali)
- **Scope:** Statistiche finali, logging
- **Incremento:** Dopo `rules.can_recycle_waste()` PASS + move carte completato
- **Uso:** `get_final_statistics()`, log analytics
- **Attivo:** Sempre (anche con scoring disabilitato)

#### `ScoringService.recycle_count` (v2.0 - Scoring)
- **Tipo:** `int` (contatore ricicli per scoring)
- **Scope:** Calcolo penalità progressive (soglie 3/4/5)
- **Incremento:** Via `record_event(RECYCLE_WASTE)`
- **Uso:** Calcolo score, threshold warnings
- **Attivo:** Solo se `settings.scoring_enabled = True`

**⚠️ IMPORTANTE:**
- I warnings TTS leggono `ScoringService.recycle_count` (quello per le penalità)
- I due counter sono **sincronizzati** (entrambi incrementati da `GameService.recycle_waste()`)
- Architettura intenzionale: stats layer vs scoring layer separation

---

### Perché Questa Duality?

**Separazione delle responsabilità:**
- `GameService` = **Domain layer** (gestisce gioco, anche senza scoring)
- `ScoringService` = **Scoring layer** (modello matematico opzionale)

**Benefici:**
- ✅ Scoring può essere disabilitato senza rompere statistiche
- ✅ Granularità corretta per ogni use case (azioni vs penalità)
- ✅ Single responsibility principle rispettato

**Esempi pratici:**
```python
# Caso 1: Scoring disabilitato
game_service.recycle_waste()
# → GameService.recycle_count = 1 ✅
# → ScoringService.recycle_count = 0 (scoring=None) ✅

# Caso 2: Scoring abilitato
game_service.recycle_waste()
# → GameService.recycle_count = 1 ✅ (per stats)
# → ScoringService.recycle_count = 1 ✅ (per penalty)
# → Warning TTS al 3° riciclo (legge ScoringService counter)
```

---

## 🔒 Type Hints

Tutti i metodi pubblici sono completamente tipizzati. Per verificare:

```bash
mypy src/ --strict
```

---

## 👤 ProfileService (v3.0.0)

Il `ProfileService` gestisce i profili utente con persistenza, statistiche aggregate e tracking delle sessioni.

### Inizializzazione

```python
from src.infrastructure.di_container import get_container

container = get_container()
profile_service = container.get_profile_service()
```

### Storage Paths

- **Profili**: `~/.solitario/profiles/profile_{uuid}.json`
- **Indice**: `~/.solitario/profiles/profiles_index.json`
- **Sessione attiva**: `~/.solitario/.sessions/active_session.json`

### Metodi

#### `create_profile(name: str, set_as_default: bool = False) -> UserProfile`

Crea un nuovo profilo utente con statistiche vuote.

**Parametri:**
- `name`: Nome del profilo
- `set_as_default`: Se True, imposta come profilo predefinito

**Ritorna:**
- Oggetto `UserProfile` creato

**Esempio:**
```python
profile = profile_service.create_profile("Mario Rossi", set_as_default=True)
print(profile.profile_id)  # "profile_a1b2c3d4"
```

---

#### `load_profile(profile_id: str) -> bool`

Carica un profilo e lo imposta come attivo.

**Parametri:**
- `profile_id`: ID del profilo da caricare

**Ritorna:**
- `True` se caricato con successo, `False` altrimenti

**Esempio:**
```python
success = profile_service.load_profile("profile_a1b2c3d4")
if success:
    print(f"Profilo attivo: {profile_service.active_profile.profile_name}")
```

---

#### `save_active_profile() -> None`

Salva il profilo attivo corrente su disco (atomico).

**Esempio:**
```python
profile_service.active_profile.profile_name = "Nuovo Nome"
profile_service.save_active_profile()
```

---

#### `delete_profile(profile_id: str) -> bool`

Elimina un profilo.

**Parametri:**
- `profile_id`: ID del profilo da eliminare

**Ritorna:**
- `True` se eliminato con successo

**Solleva:**
- `ValueError`: Se si tenta di eliminare il profilo guest (`profile_000`)

**Esempio:**
```python
try:
    profile_service.delete_profile("profile_a1b2c3d4")
except ValueError as e:
    print(f"Errore: {e}")  # "Cannot delete guest profile (profile_000)"
```

---

#### `record_session(outcome: SessionOutcome) -> None`

Registra una sessione di gioco, aggiorna le statistiche e salva automaticamente.

**Parametri:**
- `outcome`: Oggetto `SessionOutcome` con i dati della partita

**Esempio:**
```python
from src.domain.models.profile import SessionOutcome
from src.domain.models.game_end import EndReason

outcome = SessionOutcome.create_new(
    profile_id=profile_service.active_profile.profile_id,
    end_reason=EndReason.VICTORY,
    is_victory=True,
    elapsed_time=180.5,
    timer_enabled=False,
    timer_limit=0,
    timer_mode="OFF",
    timer_expired=False,
    scoring_enabled=True,
    final_score=1500,
    difficulty_level=3,
    move_count=50
)

profile_service.record_session(outcome)
# → Statistiche aggiornate automaticamente
# → Profilo salvato su disco (atomic write)
```

---

#### `list_all_profiles() -> List[Dict[str, Any]]`

Ottiene la lista leggera di tutti i profili dall'indice.

**Ritorna:**
- Lista di dizionari con informazioni sommarie dei profili

**Esempio:**
```python
profiles = profile_service.list_all_profiles()
for p in profiles:
    print(f"{p['profile_name']}: {p['total_games']} partite, {p['winrate']:.1%} vittorie")
```

---

#### `ensure_guest_profile() -> None`

Assicura che il profilo guest (`profile_000`) esista, creandolo se necessario.

**Esempio:**
```python
profile_service.ensure_guest_profile()
# Ora profile_000 esiste sicuramente
```

---

## 📊 SessionTracker (v3.0.0)

Il `SessionTracker` rileva e recupera sessioni orfane da crash dell'applicazione.

### Metodi

#### `start_session(session_id: str, profile_id: str) -> None`

Marca una sessione come attiva (per rilevamento crash).

**Parametri:**
- `session_id`: ID univoco della sessione
- `profile_id`: ID del profilo

---

#### `end_session(session_id: str) -> None`

Marca una sessione come completata normalmente.

**Parametri:**
- `session_id`: ID della sessione

---

#### `get_orphaned_sessions() -> List[Dict[str, Any]]`

Ottiene la lista delle sessioni non chiuse correttamente (dirty shutdown).

**Ritorna:**
- Lista di sessioni orfane con `recovered=False`

**Esempio:**
```python
orphaned = session_tracker.get_orphaned_sessions()
for session in orphaned:
    # Crea SessionOutcome con ABANDON_APP_CLOSE
    outcome = SessionOutcome.create_new(
        profile_id=session["profile_id"],
        end_reason=EndReason.ABANDON_APP_CLOSE,
        is_victory=False,
        # ... altri campi
    )
    profile_service.record_session(outcome)
    session_tracker.mark_recovered(session["session_id"])
```

---

## 🔒 Type Hints

Tutti i metodi pubblici sono completamente tipizzati. Per verificare:

```bash
mypy src/ --strict
```