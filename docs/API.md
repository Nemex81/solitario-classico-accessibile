# API Documentation

## 📚 Panoramica

Questo documento descrive l'API pubblica del Solitario Classico Accessibile.

**Versione API Corrente**: v3.1.2 (Bug Fixes - Dialog improvements + GameEngine documentation)

---

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

## 🎯 GameEngine (v3.1.2)

Il `GameEngine` è il layer business logic sotto il GameController. Espone metodi pubblici per l'integrazione diretta con la UI.

### Inizializzazione

```python
from src.application.game_engine import GameEngine
from src.domain.services.game_settings import GameSettings

settings = GameSettings()
engine = GameEngine.create(
    audio_enabled=True,
    tts_engine="auto",
    verbose=1,
    settings=settings,
    use_native_dialogs=True,
    parent_window=None,
    profile_service=None
)
```

### Metodi Pubblici

#### `new_game() -> None`

Inizia una nuova partita con le impostazioni correnti.

**Side Effects:**
- Redistribuisce le carte
- Applica impostazioni (draw_count, shuffle_mode, timer)
- Reset cursor e selezione
- Annuncio TTS partita iniziata

---

#### `reset_game() -> None`

Reset dello stato di gioco senza ridistribuire carte.

---

#### `is_game_running() -> bool`

Verifica se una partita è attualmente in corso.

**Ritorna:**
- `True` se partita attiva

---

#### `on_timer_tick() -> None` ⭐ NEW v3.1.0

Handler chiamato ogni secondo da `wx.Timer` per gestire timer di gioco.

**Comportamento:**
- Verifica scadenza timer (`settings.max_time_game`)
- STRICT mode: Auto-stop con `TIMEOUT_STRICT`
- PERMISSIVE mode: Avvia overtime tracking

**Esempio:**
```python
# In acs_wx.py
self.game_timer = wx.Timer(self)
self.Bind(wx.EVT_TIMER, self._on_timer_tick, self.game_timer)
self.game_timer.Start(1000)  # 1 tick/secondo

def _on_timer_tick(self, event):
    self.engine.on_timer_tick()
```

---

#### `show_last_game_summary() -> None` ⭐ NEW v3.1.0

Mostra dialog riepilogo ultima partita completata (menu "U - Ultima Partita").

**Precondizioni:**
- `profile_service` attivo
- Almeno 1 sessione in `profile.recent_sessions`

**Comportamento:**
- Recupera `SessionOutcome` da `ProfileService.recent_sessions[-1]`
- Mostra `LastGameDialog` con outcome + profile summary
- Gestisce caso "nessuna partita recente" con MessageBox

**Esempio:**
```python
# In menu handler
engine.show_last_game_summary()
# → Mostra dialog con ultima partita (persisted, funziona dopo restart)
```

---

#### `move_cursor(direction: str) -> Tuple[str, Optional[str]]`

Sposta il cursore nella direzione specificata.

**Parametri:**
- `direction`: `"up"`, `"down"`, `"left"`, `"right"`, `"tab"`, `"home"`, `"end"`

**Ritorna:**
- Tupla `(message: str, hint: Optional[str])`

---

#### `jump_to_pile(pile_idx: int) -> Tuple[str, Optional[str]]`

Salta a una pila specifica con supporto double-tap auto-selection.

**Parametri:**
- `pile_idx`: Indice pila (0-12)

**Ritorna:**
- Tupla `(message: str, hint: Optional[str])`

---

#### `select_card_at_cursor() -> Tuple[bool, str]`

Seleziona carta alla posizione cursore corrente.

**Ritorna:**
- Tupla `(success: bool, message: str)`

---

#### `execute_move() -> Tuple[bool, str]`

Esegue mossa con carte selezionate verso posizione cursore.

**Ritorna:**
- Tupla `(success: bool, message: str)`

---

#### `draw_from_stock(count: Optional[int] = None) -> Tuple[bool, str]`

Pesca carte dal mazzo (con auto-recycle waste se mazzo vuoto).

**Parametri:**
- `count`: Numero carte da pescare (None = usa `settings.draw_count`)

**Ritorna:**
- Tupla `(success: bool, message: str)`

---

#### `recycle_waste(shuffle: Optional[bool] = None) -> Tuple[bool, str]`

Ricicla scarti nel mazzo (con auto-draw dopo reshuffle).

**Parametri:**
- `shuffle`: Mode shuffle (None = usa `settings.shuffle_discards`)

**Ritorna:**
- Tupla `(success: bool, message: str)`

---

#### `end_game(is_victory: Union[EndReason, bool]) -> None`

Gestisce fine partita con report completo e prompt rematch.

**Parametri:**
- `is_victory`: `EndReason` enum o bool legacy

**Side Effects:**
- Snapshot statistiche finali
- Calcolo score finale (se scoring enabled)
- Salvataggio score storage
- Record sessione su profile (se profile_service attivo)
- Mostra dialog vittoria/abbandono
- Prompt rivincita (se dialogs disponibili)

---

#### `get_game_state() -> Dict[str, Any]`

Ottiene snapshot completo stato di gioco.

**Ritorna:**
- Dict con `statistics`, `game_over`, `piles`, `cursor`, `has_selection`

---

#### `is_victory() -> bool`

Verifica se il gioco è vinto (4 semi completati).

---

#### `open_options() -> str`

Apre finestra virtuale opzioni (F1-F5).

---

#### `close_options() -> str`

Chiude finestra virtuale opzioni.

---

#### `is_options_open() -> bool`

Verifica se finestra opzioni è aperta.

---

### Metodi Debug

#### `_debug_force_victory() -> str` 🔥 DEBUG ONLY

Simula vittoria per testing (binding CTRL+ALT+W).

**⚠️ WARNING:** Solo per development/testing!

**Comportamento:**
- Chiama `end_game(is_victory=True)` senza completare gioco
- Trigger completo victory flow (report, dialog, rematch)

**Esempio:**
```python
# In test_wx.py per testing dialogs
engine._debug_force_victory()
# → Victory dialog appare immediatamente
```

---

## 🎴 GameState

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

## 🃏 Pile (Domain Model)

**Path**: `src/domain/models/pile.py`

Rappresenta una pila di carte (tableau, foundation, stock, waste).

### Attributi

| Attributo | Tipo | Descrizione |
|-----------|------|-------------|
| `cards` | `List[Card]` | Lista carte nella pila |
| `name` | `str` | Nome human-readable (per TTS) |
| `pile_type` | `str` | Tipo (`"base"`, `"semi"`, `"mazzo"`, `"scarti"`) |
| `assigned_suit` | `Optional[str]` | Seme assegnato (foundation piles) |

### Metodi

#### `aggiungi_carta(card: Card) -> None`

Aggiunge carta in cima alla pila.

---

#### `rimuovi_carta() -> Optional[Card]`

Rimuove e ritorna carta in cima (None se vuota).

---

#### `get_top_card() -> Optional[Card]`

Ottiene carta in cima senza rimuoverla (None se vuota).

---

#### `is_empty() -> bool`

Verifica se la pila è vuota.

---

#### `get_size() -> int`

Ottiene numero carte nella pila.

---

#### `get_card_count() -> int` ⚠️ CRITICAL

Ottiene numero carte nella pila (alias di `get_size()`).

**⚠️ IMPORTANTE:**
- **Usa SEMPRE `get_card_count()`** nei loop/statistiche
- **NON usare `.count()`** → metodo inesistente! (AttributeError)
- Bug trovato: `pile.count()` → `pile.get_card_count()` ✅

**Esempio corretto:**
```python
# ✅ CORRETTO
cards_placed = sum(self.table.pile_semi[i].get_card_count() for i in range(4))

# ❌ ERRATO (AttributeError!)
cards_placed = sum(self.table.pile_semi[i].count() for i in range(4))
```

---

#### `get_all_cards() -> List[Card]`

Ottiene copia lista di tutte le carte.

---

#### `clear() -> None`

Rimuove tutte le carte dalla pila.

---

#### `remove_last_card() -> Optional[Card]`

Alias di `rimuovi_carta()`.

---

## 📋 CommandHistory

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

## 📊 StatsFormatter (v3.1.0)

Formattazione statistiche profili accessibile per NVDA.

### Inizializzazione

```python
from src.presentation.formatters.stats_formatter import StatsFormatter

formatter = StatsFormatter()
```

### Metodi Pubblici

#### `format_global_stats_summary(stats: GlobalStats) -> str`

Formatta statistiche globali sommario (2-3 righe per victory dialog).

**Parametri:**
- `stats`: Oggetto `GlobalStats` con statistiche aggregate

**Ritorna:**
- Stringa compatta formattata per NVDA (vittorie + winrate)

**Esempio:**
```python
from src.domain.models.statistics import GlobalStats

stats = profile.global_stats
text = formatter.format_global_stats_summary(stats)
print(text)
# Output:
# Vittorie totali: 23
# Winrate: 54,8%
```

---

#### `format_global_stats_detailed(stats: GlobalStats, profile_name: str) -> str`

Formatta statistiche globali dettagliate (Page 1/3 del DetailedStatsDialog).

**Parametri:**
- `stats`: Oggetto `GlobalStats`
- `profile_name`: Nome profilo per intestazione

**Ritorna:**
- Stringa formattata multi-riga con:
  - Performance globale (partite, winrate)
  - Streak corrente/massimo
  - Tempo totale/medio
  - Record personali (best time, best score)

**Esempio:**
```python
text = formatter.format_global_stats_detailed(stats, "Mario Rossi")
print(text)
# Output:
# ========================================================
#     STATISTICHE PROFILO: Mario Rossi
# ========================================================
# 
# PERFORMANCE GLOBALE
# Partite totali: 42
# Vittorie: 23 (54,8%)
# Sconfitte: 19 (45,2%)
# 
# STREAK
# Streak corrente: 3 vittorie
# Streak massimo: 8 vittorie consecutive
# ...
```

---

#### `format_timer_stats_detailed(stats: TimerStats) -> str`

Formatta statistiche timer dettagliate (Page 2/3).

**Parametri:**
- `stats`: Oggetto `TimerStats`

**Ritorna:**
- Stringa formattata con:
  - Utilizzo timer (games con/senza)
  - Performance temporale (entro limite, overtime, timeout)
  - Analisi overtime (media, massimo)
  - Breakdown per modalità (STRICT/PERMISSIVE)

**Esempio:**
```python
text = formatter.format_timer_stats_detailed(profile.timer_stats)
print(text)
# ========================================================
#     STATISTICHE TIMER
# ========================================================
# 
# UTILIZZO TIMER
# Partite con timer attivo: 15
# Partite senza timer: 27
# 
# PERFORMANCE TEMPORALE
# Entro il limite: 10
# Overtime: 2
# Timeout (sconfitte): 3
# Tasso completamento in tempo: 66,7%
# ...
```

---

#### `format_scoring_difficulty_stats(scoring_stats: ScoringStats, difficulty_stats: DifficultyStats) -> str`

Formatta statistiche scoring e difficoltà (Page 3/3 - metodo combinato).

**Parametri:**
- `scoring_stats`: Oggetto `ScoringStats`
- `difficulty_stats`: Oggetto `DifficultyStats`

**Ritorna:**
- Stringa formattata con:
  - Analisi punteggio (partite con scoring, media, massimo)
  - Breakdown per difficoltà (1-5 livelli)
  - Winrate per livello
  - Punteggio medio per livello

**Esempio:**
```python
text = formatter.format_scoring_difficulty_stats(
    profile.scoring_stats,
    profile.difficulty_stats
)
print(text)
# ========================================================
#     PUNTEGGIO & DIFFICOLTÀ
# ========================================================
# 
# PUNTEGGIO
# Partite con punteggio: 30
# Punteggio medio: 1.500 punti
# Punteggio massimo: 2.350 punti
# 
# PERFORMANCE PER DIFFICOLTÀ
# --------------------------------------------------------
# 
# Facile (Livello 1):
#   Partite: 10
#   Vittorie: 9 (90,0%)
#   Punteggio medio: 1.800 punti
# ...
```

---

#### `format_session_outcome(outcome: SessionOutcome) -> str`

Formatta riepilogo singola sessione di gioco.

**Parametri:**
- `outcome`: Oggetto `SessionOutcome` con dati partita

**Ritorna:**
- Stringa formattata con:
  - Risultato (vittoria/sconfitta + EndReason)
  - Tempo trascorso
  - Mosse effettuate
  - Punteggio finale (se scoring abilitato)
  - Info timer (se attivo)

**Esempio:**
```python
from src.domain.models.profile import SessionOutcome
from src.domain.models.game_end import EndReason

outcome = SessionOutcome.create_new(
    profile_id="profile_a1b2c3d4",
    end_reason=EndReason.VICTORY,
    is_victory=True,
    elapsed_time=225.5,
    move_count=87,
    final_score=1850,
    # ... altri campi
)

text = formatter.format_session_outcome(outcome)
# Risultato: Vittoria.
# Tempo: 3 minuti e 45 secondi.
# Mosse: 87.
# Punteggio: 1.850.
```

---

#### `format_profile_summary(profile: UserProfile) -> str`

Formatta sommario profilo (vittorie/winrate).

**Parametri:**
- `profile`: Oggetto `UserProfile`

**Ritorna:**
- Stringa formattata con:
  - Vittorie totali
  - Partite totali
  - Percentuale vittorie

**Esempio:**
```python
text = formatter.format_profile_summary(profile)
# Riepilogo Profilo:
# Vittorie Totali: 23 su 42 partite.
# Percentuale Vittorie: 54,8%.
```

---

#### `format_new_records(outcome: SessionOutcome, profile: UserProfile) -> str`

Rileva e formatta nuovi record personali.

**Parametri:**
- `outcome`: Sessione appena completata
- `profile`: Profilo corrente (con best time/score attuali)

**Ritorna:**
- Stringa formattata con record battuti (vuota se nessun record)

**Esempio:**
```python
text = formatter.format_new_records(outcome, profile)
if text:
    print(text)
# Nuovo Record!
# Miglior Tempo: 3 minuti e 45 secondi (precedente: 4 minuti e 12 secondi).
# Miglior Punteggio: 1.850 (precedente: 1.620).
```

---

#### `format_leaderboard(profiles: List[UserProfile], category: str) -> str`

Formatta classifica top 10 giocatori.

**Parametri:**
- `profiles`: Lista profili ordinati per categoria
- `category`: Nome categoria (es. "Vittoria Più Veloce", "Miglior Winrate")

**Ritorna:**
- Stringa formattata con ranking 1-10

**Esempio:**
```python
top_players = profile_service.get_top_players_by_time()
text = formatter.format_leaderboard(top_players, "Vittoria Più Veloce")
# Leaderboard: Vittoria Più Veloce
# 
# 1. Mario Rossi - 3 minuti e 45 secondi
# 2. Luigi Bianchi - 4 minuti e 12 secondi
# 3. Anna Verdi - 4 minuti e 30 secondi
# ...
```

---

### Metodi Helper (Time/Number Formatting)

#### `format_duration(seconds: float) -> str`

Formatta durata in italiano human-readable.

**Esempio:**
```python
formatter.format_duration(225.5)  # "3 minuti e 45 secondi"
formatter.format_duration(42)      # "42 secondi"
formatter.format_duration(3665)    # "1 ora, 1 minuto e 5 secondi"
```

---

#### `format_time_mm_ss(seconds: float) -> str`

Formatta tempo come MM:SS.

**Esempio:**
```python
formatter.format_time_mm_ss(325)  # "5:25"
```

---

#### `format_number(value: int) -> str`

Formatta numeri con separatore migliaia italiano.

**Esempio:**
```python
formatter.format_number(1850)  # "1.850"
```

---

#### `format_percentage(value: float, decimals: int = 1) -> str`

Formatta percentuale con decimali.

**Esempio:**
```python
formatter.format_percentage(0.548, decimals=1)  # "54,8%"
```

---

#### `format_end_reason(reason: EndReason) -> str`

Formatta EndReason come label italiano.

**Esempio:**
```python
from src.domain.models.game_end import EndReason

formatter.format_end_reason(EndReason.VICTORY)  # "Vittoria"
formatter.format_end_reason(EndReason.TIMEOUT_STRICT)  # "Tempo scaduto"
```

---

### Note NVDA

- Tutti i metodi ritornano testo ottimizzato per screen reader
- Frasi brevi con punteggiatura chiara
- Percentuali formattate con virgola decimale italiana (es. `"54,8%"`)
- Tempi formattati estesi (es. `"3 minuti e 45 secondi"`)
- Numeri con separatore migliaia punto (es. `"1.850"`)
- No elementi decorativi che confondono NVDA
- Test coverage: 93% (15 unit tests)

---

## 📝 Dialogs (v3.1.0)

Dialog nativi wxPython per visualizzazione statistiche.

### VictoryDialog

**Path**: `src/presentation/dialogs/victory_dialog.py`

**Trigger**: Fine partita vinta (`EndReason.VICTORY` o `VICTORY_OVERTIME`)

**Inizializzazione**:
```python
from src.presentation.dialogs.victory_dialog import VictoryDialog

dialog = VictoryDialog(
    parent=parent_frame,
    outcome=session_outcome,
    profile=active_profile,
    formatter=stats_formatter
)
result = dialog.ShowModal()  # wx.ID_YES (rematch) or wx.ID_NO (menu)
dialog.Destroy()
```

**Content**:
- Session outcome formattato
- Profile summary (vittorie, winrate)
- New records detection (best time/score)
- Prompt rivincita (Yes/No)

**NVDA**: TTS announcements per outcome + nuovi record

---

### AbandonDialog

**Path**: `src/presentation/dialogs/abandon_dialog.py`

**Trigger**: Fine partita abbandonata (`ABANDON_*`, `TIMEOUT_STRICT`)

**Inizializzazione**:
```python
from src.presentation.dialogs.abandon_dialog import AbandonDialog

dialog = AbandonDialog(
    parent=parent_frame,
    outcome=session_outcome,
    formatter=stats_formatter
)
dialog.ShowModal()  # wx.ID_OK
dialog.Destroy()
```

**Content**:
- EndReason classification
- Impatto su statistiche spiegato
- Opzione ritorno menu (OK)

---

### GameInfoDialog

**Path**: `src/presentation/dialogs/game_info_dialog.py`

**Trigger**: Tasto **I** durante gameplay

**Inizializzazione**:
```python
from src.presentation.dialogs.game_info_dialog import GameInfoDialog

dialog = GameInfoDialog(
    parent=parent_frame,
    current_time=engine.get_elapsed_time(),
    current_moves=engine.get_move_count(),
    current_score=engine.get_score(),
    profile=profile_service.active_profile,
    formatter=stats_formatter
)
dialog.ShowModal()  # wx.ID_OK
dialog.Destroy()
```

**Content**:
- Progresso partita corrente (tempo, mosse, score)
- Riepilogo profilo real-time

**NVDA**: Non blocca gameplay, focus return garantito

---

### DetailedStatsDialog

**Path**: `src/presentation/dialogs/detailed_stats_dialog.py`

**Trigger**: ProfileMenuPanel button 5 o menu "U - Ultima Partita"

**Inizializzazione**:
```python
from src.presentation.dialogs.detailed_stats_dialog import DetailedStatsDialog

# Build stats data dictionary
profile = profile_service.active_profile

dialog = DetailedStatsDialog(
    parent=parent_frame,
    profile_name=profile.profile_name,
    global_stats=profile.global_stats,
    timer_stats=profile.timer_stats,
    difficulty_stats=profile.difficulty_stats,
    scoring_stats=profile.scoring_stats
)
dialog.ShowModal()  # wx.ID_OK (ESC)
dialog.Destroy()
```

**Content**: 3 pagine navigabili
- **Pagina 1**: Global stats (partite, winrate, best time/score, avg moves)
- **Pagina 2**: Timer stats (timer games, timeouts, overtime, avg time)
- **Pagina 3**: Difficulty/Scoring stats (breakdown per livello, deck usage)

**Navigation**: PageUp/PageDown

**NVDA**: Page transitions announced ("Pagina 2 di 3: Statistiche Timer")

---

### LeaderboardDialog

**Path**: `src/presentation/dialogs/leaderboard_dialog.py`

**Trigger**: Menu "L - Leaderboard Globale"

**Inizializzazione**:
```python
from src.presentation.dialogs.leaderboard_dialog import LeaderboardDialog

# Ottieni top 10 per categoria
top_players = profile_service.get_top_players_by_time()  # o altre metriche

dialog = LeaderboardDialog(
    parent=parent_frame,
    profiles=top_players,
    category="Vittoria Più Veloce",
    formatter=stats_formatter
)
dialog.ShowModal()  # wx.ID_OK (ESC)
dialog.Destroy()
```

**Content**: Top 10 giocatori in 5 categorie
- Fastest victory (sort by time)
- Best winrate (sort by %)
- Highest score (sort by points)
- Most games played (sort by total)
- Best timed victory (timer-only)

**NVDA**: Rankings announced con player names + stats

---

### LastGameDialog

**Path**: `src/presentation/dialogs/last_game_dialog.py`

**Trigger**: Menu "U - Ultima Partita"

**Inizializzazione**:
```python
from src.presentation.dialogs.last_game_dialog import LastGameDialog

last_session = profile.recent_sessions[-1]

dialog = LastGameDialog(
    parent=parent_frame,
    outcome=last_session,
    profile=profile,
    formatter=stats_formatter
)
dialog.ShowModal()  # wx.ID_OK (ESC)
dialog.Destroy()
```

**Content**:
- Session outcome (last completed game)
- Profile summary snapshot

**NVDA**: Read-only summary ottimizzato

---

## 📄 ProfileMenuPanel (v3.1.0)

**Path**: `src/infrastructure/ui/profile_menu_panel.py`

**Modal Dialog** (267 lines) con 6 operazioni complete.

### Inizializzazione

```python
from src.infrastructure.ui.profile_menu_panel import ProfileMenuPanel

panel = ProfileMenuPanel(
    parent=parent_frame,
    profile_service=container.get_profile_service(),
    screen_reader=screen_reader  # Optional for TTS
)
result = panel.ShowModal()  # wx.ID_CANCEL (ESC)
panel.Destroy()
```

### Operazioni

#### 1. Create Profile

**Button**: "Crea Nuovo Profilo" (button 2)

**Flow**:
1. Input dialog (nome validazione)
2. `ProfileService.create_profile(name)`
3. `ProfileService.load_profile(new_id)` [auto-switch]
4. UI refresh
5. TTS: "Profilo creato: {name}. Attivo."

**Validation**:
- Empty names rejected
- Names >30 characters rejected
- Duplicate names rejected

---

#### 2. Switch Profile

**Button**: "Cambia Profilo" (button 1)

**Flow**:
1. Choice dialog (list all with stats preview)
2. `ProfileService.save_active_profile()`
3. `ProfileService.load_profile(selected_id)`
4. UI refresh
5. TTS: "Profilo attivo: {name}"

**UI**: Current profile marked with "(attivo)"

---

#### 3. Rename Profile

**Button**: "Rinomina Profilo" (button 3)

**Flow**:
1. Input dialog (pre-filled with current name)
2. Validation + guest protection
3. `active_profile.profile_name = new_name`
4. `ProfileService.save_active_profile()`
5. UI refresh
6. TTS: "Profilo rinominato: {new_name}"

**Safeguards**:
- Cannot rename guest profile ("Ospite")

---

#### 4. Delete Profile

**Button**: "Elimina Profilo" (button 4)

**Flow**:
1. Confirmation dialog
2. Safeguards check
3. `ProfileService.delete_profile(id)`
4. `ProfileService.load_profile("profile_000")` [auto-switch to guest]
5. UI refresh
6. TTS: "Profilo eliminato. Attivo: Ospite."

**Safeguards**:
- Cannot delete guest profile (`profile_000`)
- Cannot delete last remaining profile

---

#### 5. View Detailed Stats ⭐

**Button**: "Statistiche Dettagliate" (button 5)

**Flow**:
1. Build stats_data dict from active_profile
2. `DetailedStatsDialog(parent, profile_name, global_stats, timer_stats, difficulty_stats, scoring_stats).ShowModal()`
3. 3 pages navigation (PageUp/PageDown)
4. ESC returns to ProfileMenuPanel (not main menu)

**Content**: Global, Timer, Difficulty/Scoring stats

---

#### 6. Set Default Profile

**Button**: "Imposta Predefinito" (button 6)

**Flow**:
1. `active_profile.is_default = True`
2. `ProfileService.save_active_profile()`
3. UI refresh
4. TTS: "Profilo predefinito: {name}"

**Effect**: Profile loaded automatically on app startup

---

### NVDA Accessibility

- Complete keyboard navigation (TAB, ENTER, ESC)
- TTS announcements for all operations
- Focus management after every action
- Error messages actionable
- No decorative elements

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
| `get_stats_formatter(language)` | `StatsFormatter` | Stats formatter (v3.1.0) |
| `get_command_history()` | `CommandHistory` | Cronologia comandi |
| `get_game_controller()` | `GameController` | Controller principale |
| `get_profile_service()` | `ProfileService` | Profile service (v3.0.0) |
| `get_profile_storage()` | `ProfileStorage` | Profile storage (v3.0.0) |
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

### EndReason (v2.7.0)

```python
from src.domain.models.game_end import EndReason

EndReason.VICTORY              # Vittoria normale
EndReason.VICTORY_OVERTIME     # Vittoria in overtime (timer PERMISSIVE)
EndReason.ABANDON_NEW_GAME     # Abbandono per nuova partita
EndReason.ABANDON_EXIT         # Abbandono per uscita volontaria
EndReason.ABANDON_APP_CLOSE    # Abbandono per crash app
EndReason.TIMEOUT_STRICT       # Timeout con timer STRICT
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

## 👤 ProfileService (v3.1.0)

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

---

## 📚 Cross-References

Per dettagli architetturali:
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Panoramica layer, data flow, design patterns
- **[TODO.md](TODO.md)**: Implementation tracking Feature 1-3
- **[CHANGELOG.md](../CHANGELOG.md)**: Version history completa

---

*Document Version: 3.1.2 (Revision 2)*  
*Last Updated: 2026-02-18 14:20 CET*  
*Revision Notes: Added GameEngine public API, Pile methods reference, debug utilities*
