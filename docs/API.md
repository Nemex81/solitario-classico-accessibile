
# LeaderboardDialog (Presentation Layer)


**Modulo:** `src/presentation/dialogs/leaderboard_dialog.py`  
**Layer:** Presentation

Dialog accessibile per la visualizzazione della classifica (leaderboard). Compatibile con screen reader e navigazione da tastiera secondo checklist WAI-ARIA del progetto.

### API pubblica

- `LeaderboardDialog(parent: wx.Window, profiles_with_stats: list = None, current_profile_id: str = None, metric: str = "victories")`
    - Crea un dialog per mostrare la classifica. Accetta:
        - `profiles_with_stats`: lista di dict o oggetti con dati classifica
        - `current_profile_id`: profilo attivo da evidenziare
        - `metric`: metrica di ordinamento/visualizzazione (es. "victories")
    - Navigabile da tastiera, titolo e label descrittivi, focus su primo controllo, ESC chiude dialog.

**Esempio d’uso:**
```python
from src.presentation.dialogs.leaderboard_dialog import LeaderboardDialog
dlg = LeaderboardDialog(parent, profiles_with_stats=profiles, current_profile_id="profile_001", metric="victories")
dlg.ShowModal()
```

**Note:**
- Non contiene logica di business/statistiche, solo presentazione dati.
- Evidenzia il profilo attivo con un asterisco.
- Aggiornare questa sezione se vengono aggiunte funzionalità di filtro, ordinamento o esportazione.


# DependencyContainer (Infrastructure Layer)

**Modulo:** `src/infrastructure/di/dependency_container.py`
**Layer:** Infrastructure

Contenitore IoC per la risoluzione centralizzata delle dipendenze secondo Clean Architecture.

### API pubblica

- `get_audio_manager() -> AudioManager | _AudioManagerStub`
    - Restituisce l'istanza singleton di AudioManager (lazy-load). Se fallisce, ritorna uno stub no-op.
    - Non accetta parametri. Nessuna dipendenza da Presentation/Application layer.

**Note:**
- Singleton per sessione. Fallback automatico a stub in caso di errore.
- Logging su logger 'error' in caso di fallimento.

# InputHandler (Application Layer)

**Modulo:** `src/application/input_handler.py`
**Layer:** Application

Gestisce la traduzione di eventi tastiera pygame in `GameCommand`.

### API pubblica

- `__init__(audio_manager: Optional[Any] = None)`
  - `audio_manager`: opzionale, istanza di `AudioManager` iniettata via DI.
    Se fornito, l'handler emette `AudioEvent` per navigazione e azioni UI.

- `handle_event(event: pygame.event.Event) -> Optional[GameCommand]`
  - Traduce l'evento in `GameCommand` secondo la tabella di binding.
  - Se `audio_manager` è presente, chiama `audio_manager.play_event(...)`
    con `AudioEventType.UI_NAVIGATE`, `UI_SELECT` o `UI_CANCEL` come appropriato.

- `add_binding(...)`, `remove_binding(...)` (restano invariate)

**Note:**
- L'handler è stateless e condivisibile. Riceve AudioManager solo per effetti sonori;
  non lo usa per decisioni logiche.

# DialogManager (Application Layer)

**Modulo:** `src/application/dialog_manager.py`
**Layer:** Application

Gestisce finestre di dialogo accessibili (abbandona, nuova partita, etc.).

### API pubblica

- `__init__(dialog_provider: Optional[DialogProvider] = None, audio_manager: Optional[Any] = None)`
  - `audio_manager`: opzionale, riproduce un effetto sonoro `UI_SELECT` ogni volta che
    un dialogo sincrono viene mostrato o chiuso.

- `show_abandon_game_prompt() -> bool`, `show_new_game_prompt() -> bool`, ...
  - Ogni metodo ora invoca il `audio_manager` se disponibile.

**Note:**
- L'audio è completamente opzionale per la gestione dei dialoghi; la funzionalità
  degrada in assenza di manager.

# MainMenuController (Application Layer)

**Modulo:** `src/application/main_menu_controller.py`
**Layer:** Application

Controller per la logica del menu principale. Riceve un `AudioManager` opzionale
per riprodurre effetti sonori quando l'utente naviga o seleziona voci di menu.

### API pubblica

- `__init__(audio_manager: Optional[Any] = None, items: Optional[List[str]] = None)`
  - `items`: lista di etichette menu personalizzabili.

- `navigate_up() -> int`
- `navigate_down() -> int`
  - Muovono il cursore, emettono `UI_NAVIGATE` o `TABLEAU_BUMPER` in caso di
    bordo.

- `select() -> str`  – restituisce etichetta selezionata; emette `UI_SELECT`.
- `cancel() -> None` – emette `UI_CANCEL`.

**Note:**
- Il controller chiama `audio_manager.play_event(...)` se disponibile.

# MixerController (Application Layer)

**Modulo:** `src/application/mixer_controller.py`
**Layer:** Application

Controller per il mixer accessibile (canali master, music, effects). Si integra
con il `ScreenReader` per feedback TTS e con `AudioManager` per effetti sonori.

### API pubblica

- `__init__(audio_manager: Optional[Any] = None, screen_reader: Optional[Any] = None, channels: Optional[Dict[str,int]] = None)`
  - `screen_reader` tipicamente ottenuto da `DIContainer.get_screen_reader()`.

- `navigate_up()`, `navigate_down()`: spostano cursore tra i canali;
  emettono `UI_NAVIGATE`/`TABLEAU_BUMPER` e possono chiamare TTS.

- `increase()`, `decrease()`: modificano valore canale (0‑100); emettono
  `UI_SELECT` o `TABLEAU_BUMPER`.

**Note:**
- Utilizzato dalla finestra mixer accessibile (tasto "M").

# AudioConfig (Infrastructure Layer)

**Modulo:** `src/infrastructure/config/audio_config_loader.py`

Dataclass che rappresenta la configurazione del sistema audio, caricata da
`config/audio_config.json` tramite `AudioConfigLoader`. A partire da v3.5.0 la
config contiene:

- `event_sounds`: mappa event_type → nome file (es. "CARD_MOVE": "card_move.wav").
- `preload_all_event_sounds`: flag booleano, se true carica automaticamente tutti
  i suoni mappati.
- `enabled_events`: mappa event_type → bool per disabilitare singoli eventi.

La classe viene usata internamente da `AudioManager` e da `DIContainer`.

## API pubblica

- `AudioConfigLoader.load(path: str = CONFIG_PATH) -> AudioConfig`
  - Carica e validà il JSON, crea fallback se il file è mancante o illegibile.


# AudioManager (Infrastructure Layer)

[...existing lines...]

**Modulo:** `src/infrastructure/audio/audio_manager.py`  
**Accesso via DI:** `container.get_audio_manager()` (singleton lazy-loaded)

Orchestratore principale del sistema audio. Riceve `AudioEvent` dai controller Application, consulta `SoundCache`, calcola panning, delega la riproduzione a `SoundMixer`. Gestisce ciclo di vita, pause, resume, shutdown, salvataggio settings.

### Metodi principali

- `AudioManager(config: AudioConfig, sounds_base_path: Optional[Path] = None)`
- `initialize() -> bool`
- `play_event(event: AudioEvent) -> None`
- `pause_all_loops() -> None`
- `resume_all_loops() -> None`
- `set_bus_volume(bus_name: str, volume: int) -> None`
- `toggle_bus_mute(bus_name: str) -> bool`
- `get_bus_volume(bus_name: str) -> int`
- `is_bus_muted(bus_name: str) -> bool`
- `save_settings() -> None`
- `shutdown() -> None`
- `is_available: bool`

#### Accesso tramite DIContainer

- `container.get_audio_manager() -> AudioManager`
- `container.shutdown_audio_manager() -> None`

**Note:**
- Singleton, lazy-loaded. Non importare mai direttamente nel Domain/Application layer.
- Cross-reference: [ARCHITECTURE.md](ARCHITECTURE.md#audio-manager)

# API Documentation
## 🟦 AudioManager

Classe orchestratore principale del sistema audio.
Riceve `AudioEvent` dai controller Application, consulta `SoundCache`, calcola panning, delega la riproduzione a `SoundMixer`. Gestisce ciclo di vita, pause, resume, shutdown, salvataggio settings.

**API pubblica:**
- `__init__(config: AudioConfig, sounds_base_path: Optional[Path] = None)`: Costruttore, inizializza cache e mixer.
- `initialize() -> bool`: Inizializza pygame.mixer e SoundCache. Ritorna True se successo, False con fallback.
- `play_event(event: AudioEvent) -> None`: Riproduce il suono associato all'evento con panning spaziale.
- `pause_all_loops() -> None`: Sospende bus Ambient e Music.
- `resume_all_loops() -> None`: Riprende bus Ambient e Music.
- `set_bus_volume(bus_name: str, volume: int) -> None`: Imposta volume bus.
- `toggle_bus_mute(bus_name: str) -> bool`: Toggle mute bus.
- `get_bus_volume(bus_name: str) -> int`: Restituisce volume bus.
- `is_bus_muted(bus_name: str) -> bool`: Stato mute bus.
- `save_settings() -> None`: Salva volumi e stato mute in audio_config.json.
- `shutdown() -> None`: Salva settings, ferma tutti i canali, chiama pygame.mixer.quit().
- `is_available`: Proprietà, True se pygame.mixer è inizializzato.

**Esempio d’uso:**
```python
from src.infrastructure.audio.audio_manager import AudioManager
from src.infrastructure.config.audio_config_loader import AudioConfig
from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType

config = AudioConfig.load_from_file("config/audio_config.json")
audio_manager = AudioManager(config)
audio_manager.initialize()

event = AudioEvent(event_type=AudioEventType.CARD_MOVE, source_pile=2, destination_pile=8)
audio_manager.play_event(event)
audio_manager.set_bus_volume("gameplay", 80)
audio_manager.toggle_bus_mute("ambient")
audio_manager.save_settings()
audio_manager.shutdown()
```

**Note tecniche:**
- Mapping evento→bus secondo tabella (gameplay, ui, ambient, music, voice)
- Gestione varianti: **non utilizzata** in versione v3.4.1, il mapping è semplice evento→file
- Panning calcolato da destination_pile/source_pile (range -1.0 a +1.0)
- Fallback robusto: warning log se asset mancante, nessun crash
- Logging semantico su azioni critiche (inizializzazione, errori, salvataggio)
- Policy bus: Ambient/Music sospesi in pausa, one-shot sempre attivi
- Salvataggio settings persistente in JSON

**Cross-reference:**
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): architettura layer, orchestrazione audio
- [CHANGELOG.md](CHANGELOG.md): voce Added AudioManager orchestratore audio

---
## 🟦 SoundMixer

Classe per la gestione dei 5 bus audio, volumi, mute, panning stereo constant-power, loop.
Gestisce i canali pygame.mixer.Channel, policy di mute, volumi, loop e panning.

**API pubblica:**
- `play_one_shot(sound, bus_name, panning=0.0)`: Riproduce suono one-shot con panning.
- `play_loop(sound, bus_name)`: Avvia loop infinito su bus.
- `pause_loops()`: Sospende bus ambient e music.
- `resume_loops()`: Riprende bus ambient e music.
- `stop_all()`: Ferma tutti i canali.
- `set_bus_volume(bus_name, volume)`: Imposta volume bus.
- `toggle_bus_mute(bus_name)`: Toggle mute bus.
- `get_bus_volume(bus_name)`: Restituisce volume bus.
- `is_bus_muted(bus_name)`: Stato mute bus.

**Esempio d’uso:**
```python
from src.infrastructure.audio.sound_mixer import SoundMixer
mixer = SoundMixer(config)
mixer.play_one_shot(sound, "gameplay", panning=0.5)
mixer.set_bus_volume("ui", 60)
mixer.toggle_bus_mute("ambient")
```

**Note:**
- Panning stereo constant-power: volume uniforme su tutto lo spettro
- Policy mute/loop: bus ambient/music sospesi, one-shot sempre attivi
- Logging semantico su azioni critiche

---
## 🟦 SoundCache

Classe per il caricamento e gestione asset audio in RAM.
Carica tutti i file WAV del sound pack attivo come oggetti pygame.Sound.
Gestisce varianti, fallback e warning log per asset mancanti.

**API pubblica:**
- `load_pack(pack_name: str) -> None`: Carica tutti i WAV del pack in RAM.
- `get(event_type: str) -> Optional[Union[pygame.mixer.Sound, List[pygame.mixer.Sound]]]`: Restituisce il sound pre-caricato per l’evento.
- `clear() -> None`: Svuota la cache.

**Esempio d’uso:**
```python
from src.infrastructure.audio.sound_cache import SoundCache
cache = SoundCache(Path("assets/sounds"))
cache.load_pack("default")
sound = cache.get("card_move")
```

**Note:**
- Asset mancante → warning log, entry None (degradazione graziosa)
- Varianti: lista di sound (deprecated, non usata; ora un solo file per evento)

---
## 🟦 AudioEventType & AudioEvent

### AudioEventType

Classe di costanti stringa per i tipi di evento audio. Usata dai controller Application per descrivere azioni, feedback e eventi di gioco.

**Esempio:**
```python
from src.infrastructure.audio.audio_events import AudioEventType
event_type = AudioEventType.CARD_MOVE
```

**Principali costanti:**
- CARD_MOVE, CARD_SELECT, CARD_DROP, FOUNDATION_DROP, INVALID_MOVE, TABLEAU_BUMPER, STOCK_DRAW, WASTE_DROP
- UI_NAVIGATE, UI_SELECT, UI_CANCEL, MIXER_OPENED
- AMBIENT_LOOP, MUSIC_LOOP
- GAME_WON
- TIMER_WARNING, TIMER_EXPIRED

### AudioEvent

Dataclass immutabile che rappresenta un evento audio. Creato dai controller Application, consumato dall’AudioManager.

**Signature:**
```python
@dataclass(frozen=True)
class AudioEvent:
    event_type: str
    source_pile: Optional[int] = None
    destination_pile: Optional[int] = None
    context: Dict[str, Any] = field(default_factory=dict)
```

**Esempio d’uso:**
```python
from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
event = AudioEvent(
    event_type=AudioEventType.FOUNDATION_DROP,
    source_pile=2,
    destination_pile=8
)
```

**Note:**
- I controller descrivono solo COSA è successo, non COME il suono sarà riprodotto.
- Il campo context permette estensioni future (es. info extra per bus, varianti, ecc).

---

## 📚 Panoramica

Questo documento descrive l'API pubblica del Solitario Classico Accessibile.

**Versione API Corrente**: v3.2.2

---

### TimerManager

Utility per la gestione di un conto alla rovescia con callback.
Non è usato direttamente dall'utente finale ma viene creato
automaticamente dal `GameEngine` quando una partita inizia con timer
abilitato.  Parametri principali:

```python
TimerManager(
    minutes: int = 10,
    warning_callback: Optional[Callable[[int], None]] = None,
    warning_intervals: Optional[list[int]] = None,
    expired_callback: Optional[Callable[[], None]] = None  # v3.4.2
)
```

- `warning_callback(minutes_left)` invocato una volta per ciascun
  intervallo configurato (default 5,2,1 minuti).
- `expired_callback()` invocato una sola volta al termine del timer.

Metodi utili: `start()`, `pause()`, `resume()`, `reset()`,
`check_warnings()`.

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

Note: when a game is started via controller the underlying `GameEngine` will also initialize an internal `TimerManager` (minutes derived from `settings.max_time_game`).

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

## 🎴 Pile (Domain Model)

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

#### `format_timer_stats_detailed(stats: TimerStats, global_stats: GlobalStats) -> str`

Formatta statistiche timer dettagliate (Page 2/3).

**Parametri:**
- `stats`: Oggetto `TimerStats` con timer-specific data
- `global_stats`: Oggetto `GlobalStats` per cross-stat calculations (richiesto per calcolare `games_without_timer`)

**Ritorna:**
- Stringa formattata con:
  - Utilizzo timer (games con/senza)
  - Performance temporale (entro limite, overtime, timeout)
  - Analisi overtime (media, massimo)
  - Breakdown per modalità (STRICT/PERMISSIVE)

**⚠️ Breaking Change v3.1.1:**
Parametro `global_stats` aggiunto nella versione 3.1.1 per supportare statistiche incrociate.
Se usi versioni precedenti (≤3.1.0), consulta il codice per signature compatibile.

**Esempio:**
```python
# v3.1.1+ (current)
text = formatter.format_timer_stats_detailed(
    profile.timer_stats,
    profile.global_stats  # ← PARAMETRO OBBLIGATORIO
)
print(text)
# ========================================================
#     STATISTICHE TIMER
# ========================================================
# 
# UTILIZZO TIMER
# Partite con timer attivo: 15
# Partite senza timer: 27  # ← Calcolato da global_stats
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

**Path**: `src/infrastructure/ui/dialogs/victory_dialog.py`

**Trigger**: Fine partita vinta (`EndReason.VICTORY` o `VICTORY_OVERTIME`)

**Inizializzazione**:
```python
from src.infrastructure.ui.dialogs.victory_dialog import VictoryDialog

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

**Path**: `src/infrastructure/ui/dialogs/abandon_dialog.py`

**Trigger**: Fine partita abbandonata (`ABANDON_*`, `TIMEOUT_STRICT`)

**Inizializzazione**:
```python
from src.infrastructure.ui.dialogs.abandon_dialog import AbandonDialog

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

**Path**: `src/infrastructure/ui/dialogs/game_info_dialog.py`

**Trigger**: Tasto **I** durante gameplay

**Inizializzazione**:
```python
from src.infrastructure.ui.dialogs.game_info_dialog import GameInfoDialog

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

**Path**: `src/infrastructure/ui/dialogs/detailed_stats_dialog.py`

**Trigger**: ProfileMenuPanel button 5 o menu "U - Ultima Partita"

**Inizializzazione**:
```python
from src.infrastructure.ui.dialogs.detailed_stats_dialog import DetailedStatsDialog

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

**Path**: `src/infrastructure/ui/dialogs/leaderboard_dialog.py`

**Trigger**: Menu "L - Leaderboard Globale"

**Inizializzazione**:
```python
from src.infrastructure.ui.dialogs.leaderboard_dialog import LeaderboardDialog

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

**Path**: `src/infrastructure/ui/dialogs/last_game_dialog.py`

**Trigger**: Menu "U - Ultima Partita"

**Inizializzazione**:
```python
from src.infrastructure.ui.dialogs.last_game_dialog import LastGameDialog

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

**Esempio VICTORY_OVERTIME:**
```python
# Scenario: Timer PERMISSIVE mode, limite 15 minuti
# Il giocatore vince dopo 17 minuti (2 minuti overtime)

outcome = SessionOutcome.create_new(
    profile_id="profile_123",
    end_reason=EndReason.VICTORY_OVERTIME,  # Automatic conversion
    is_victory=True,
    elapsed_time=1020.0,  # 17 minuti
    timer_enabled=True,
    timer_limit=900,      # 15 minuti
    timer_mode="PERMISSIVE",
    timer_expired=True,
    overtime_seconds=120, # 2 minuti overtime
    # ... altri campi
)

# Formattazione automatica
formatter.format_end_reason(outcome.end_reason)
# Output: "Vittoria in overtime"

# In victory dialog
# "Hai vinto! (tempo scaduto: 2 minuti oltre il limite)"
# "Tempo totale: 17 minuti."
# "Penalità punti: -200 (2 minuti × -100 punti/min)"
```

**Conversione automatica:**
- `GameEngine.end_game()` rileva overtime via `timer_manager.is_in_overtime()`
- Se vittoria + overtime attivo → `EndReason.VICTORY` diventa `VICTORY_OVERTIME`
- Stats separano vittorie normali da overtime (tracking separato)

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

#### `create_profile(name: str, is_guest: bool = False) -> Optional[UserProfile]`

Crea un nuovo profilo utente con statistiche vuote.

**Parametri:**
- `name`: Nome del profilo (display name)
- `is_guest`: Se True, crea come profilo guest protetto (default: False)
  - **Note:** Il profilo guest (`profile_000`, nome "Ospite") ha protezione speciale:
    - Non può essere eliminato
    - Non può essere rinominato
    - Usato come fallback quando nessun profilo è caricato

**Ritorna:**
- Oggetto `UserProfile` creato, oppure `None` se creazione fallisce

**⚠️ Breaking Change v3.0.0:**
Il parametro `set_as_default` è stato rinominato in `is_guest` per riflettere meglio la semantica.
Per impostare un profilo come predefinito, usa `profile.is_default = True` e poi `save_active_profile()`.

**Esempio:**
```python
# Crea profilo utente normale
profile = profile_service.create_profile("Mario Rossi")
if profile:
    print(profile.profile_id)  # "profile_a1b2c3d4"

# Crea profilo guest (uso interno)
guest = profile_service.create_profile("Ospite", is_guest=True)
# guest.profile_id == "profile_000" (ID fisso per guest)

# Per impostare come predefinito (post-creazione):
profile.is_default = True
profile_service.save_active_profile()
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

#### `save_active_profile() -> bool`

Salva il profilo attivo corrente su disco (atomico).

**Ritorna:**
- `True` se salvato con successo
- `False` se fallimento (es. errore I/O, profilo non attivo)

**Side Effects:**
- Scrittura atomica su `~/.solitario/profiles/profile_{uuid}.json`
- Aggiornamento `profiles_index.json` con timestamp

**Esempio:**
```python
profile_service.active_profile.profile_name = "Nuovo Nome"
success = profile_service.save_active_profile()

if not success:
    print("⚠️ Errore: impossibile salvare profilo!")
    # Handle error (retry, notify user, etc.)
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

#### `record_session(outcome: SessionOutcome) -> bool`

Registra una sessione di gioco, aggiorna le statistiche e salva automaticamente.

**Parametri:**
- `outcome`: Oggetto `SessionOutcome` con i dati della partita

**Ritorna:**
- `True` se sessione registrata e salvata con successo
- `False` se errore (validazione fallita, profilo non attivo, errore I/O)

**Side Effects:**
- Aggiornamento statistiche aggregate (GlobalStats, TimerStats, DifficultyStats, ScoringStats)
- Aggiunta sessione a `recent_sessions` (mantiene ultime 50)
- Salvataggio automatico profilo su disco

**Validazioni:**
- Sessione deve appartenere al profilo attivo (`session.profile_id == active_profile.profile_id`)
- Campi obbligatori devono essere popolati (`end_reason`, `is_victory`, `elapsed_time`, ecc.)

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

success = profile_service.record_session(outcome)

if success:
    print("✅ Sessione registrata! Statistiche aggiornate.")
else:
    print("⚠️ Errore: sessione non registrata (controlla validazione)")
```

---

#### `list_profiles() -> List[Dict[str, Any]]`

Ottiene la lista leggera di tutti i profili dall'indice.

**Ritorna:**
- Lista di dizionari con informazioni sommarie dei profili:
  - `profile_id`: ID profilo
  - `profile_name`: Nome display
  - `total_games`: Numero partite totali
  - `winrate`: Percentuale vittorie (0.0-1.0)
  - `is_guest`: Flag profilo guest
  - `last_played`: Timestamp ultima partita (ISO 8601)

**Note:**
- Operazione leggera: legge solo `profiles_index.json` (non carica file profili completi)
- Usa `get_all_profiles_with_stats()` se serve accesso completo a statistiche

**Esempio:**
```python
profiles = profile_service.list_profiles()  # ✅ Nome corretto

for p in profiles:
    print(f"{p['profile_name']}: {p['total_games']} partite, {p['winrate']:.1%} vittorie")

# Output:
# Mario Rossi: 42 partite, 54.8% vittorie
# Luigi Bianchi: 15 partite, 60.0% vittorie
# Ospite: 3 partite, 33.3% vittorie
```

---

#### `ensure_guest_profile() -> bool`

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

## � Infrastructure Logging

**Modulo**: `src/infrastructure/logging/`  
**Versione**: v3.2.0 (sistema categorizzato Paradox-style)

### Setup

#### `setup_logging(level: int = logging.INFO, console_output: bool = False) -> None`

Configura il logging globale dell'applicazione. Thin wrapper backward-compatible
su `setup_categorized_logging()`. Chiamata da `acs_wx.py` all'avvio.

**Parametri:**
- `level`: Livello minimo (`logging.DEBUG`, `logging.INFO`, ecc.) — default `INFO`
- `console_output`: Se `True`, log anche su console (utile in sviluppo)

**Importazione:**
```python
from src.infrastructure.logging import setup_logging
setup_logging(level=logging.INFO, console_output=False)
```

---

#### `setup_categorized_logging(logs_dir: Path = Path("logs"), level: int = logging.INFO, console_output: bool = False) -> None`

Implementazione reale del sistema di logging. Crea un `RotatingFileHandler`
dedicato per ogni categoria (5 MB, 3 backup, UTF-8), con `propagate=False`
per evitare duplicazione. Il root logger mantiene `solitario.log` per le
librerie esterne (`wx`, `PIL`, `urllib3`).

**Parametri:**
- `logs_dir`: Directory di destinazione (default: `Path("logs")`)
- `level`: Livello minimo
- `console_output`: Se `True`, aggiunge handler console

**Categorie attive → file prodotti:**

| Categoria | File | Contenuto |
|-----------|------|-----------|
| `game`    | `logs/game_logic.log`  | Lifecycle partita, mosse, settings |
| `ui`      | `logs/ui_events.log`   | Navigazione UI, dialogs, TTS, keyboard |
| `error`   | `logs/errors.log`      | Errori, warnings, eccezioni |
| `timer`   | `logs/timer.log`       | Avvio/scadenza/pausa timer |
| *(root)*  | `logs/solitario.log`   | Library logs (wx, PIL, urllib3) |

**Importazione:**
```python
from src.infrastructure.logging import setup_categorized_logging
setup_categorized_logging(level=logging.DEBUG, console_output=True)
```

---

### Helper Semantici (`game_logger`)

Usare sempre gli helper semantici invece dei logger diretti.

```python
from src.infrastructure.logging import game_logger as log
```

#### Categoria `game` → `game_logic.log`

| Funzione | Livello | Descrizione |
|----------|---------|-------------|
| `log.game_started(deck_type, difficulty, timer_enabled)` | INFO | Inizio partita |
| `log.game_won(elapsed_time, moves_count, score)` | INFO | Vittoria |
| `log.game_abandoned(elapsed_time, moves_count)` | INFO | Abbandono |
| `log.card_moved(from_pile, to_pile, card, success)` | INFO/WARNING | Mossa carta |
| `log.cards_drawn(count)` | DEBUG | Pesca da mazzo |
| `log.waste_recycled(recycle_count)` | INFO | Riciclo scarti |
| `log.invalid_action(action, reason)` | WARNING | Azione non valida |
| `log.settings_changed(name, old_value, new_value)` | INFO | Cambio impostazione |
| `log.cursor_moved(from_pos, to_pos)` | DEBUG | Spostamento cursore |
| `log.pile_jumped(from_pile, to_pile)` | DEBUG | Salto diretto pila |
| `log.info_query_requested(query_type, context)` | INFO | Query informativa |

#### Categoria `ui` → `ui_events.log`

| Funzione | Livello | Descrizione |
|----------|---------|-------------|
| `log.panel_switched(from_panel, to_panel)` | INFO | Cambio panel |
| `log.dialog_shown(dialog_type, title)` | DEBUG | Apertura dialog |
| `log.dialog_closed(dialog_type, result)` | DEBUG | Chiusura dialog |
| `log.keyboard_command(command, context)` | DEBUG | Comando tastiera |
| `log.tts_spoken(message, interrupt)` | DEBUG | Vocalizzo TTS |

#### Categoria `error` → `errors.log`

| Funzione | Livello | Descrizione |
|----------|---------|-------------|
| `log.error_occurred(error_type, details, exception)` | ERROR | Errore con traceback |
| `log.warning_issued(warning_type, message)` | WARNING | Warning gestito |

#### Categoria `timer` → `timer.log`

| Funzione | Livello | Descrizione |
|----------|---------|-------------|
| `log.timer_started(duration)` | INFO | Avvio timer |
| `log.timer_expired()` | WARNING | Scadenza timer |
| `log.timer_paused(remaining)` | DEBUG | Pausa timer |

**Esempio completo:**
```python
from src.infrastructure.logging import game_logger as log

# Fine partita con vittoria
log.game_won(elapsed_time=120, moves_count=45, score=850)
# → logs/game_logic.log: 2026-02-21 14:30:15 [INFO] Game WON - Time: 120s, Moves: 45, Score: 850

# Errore con eccezione
try:
    load_profile()
except IOError as e:
    log.error_occurred("FileIO", "Profile corrupted", e)
# → logs/errors.log: 2026-02-21 14:30:16 [ERROR] ERROR [FileIO]: Profile corrupted
#                     Traceback (most recent call last): ...
```

---

## �🔒 Type Hints

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

*Document Version: 3.2.0*  
*Last Updated: 2026-02-22*  
*Revision Notes: Added Infrastructure Logging section (setup_categorized_logging, game_logger helpers)*

**Changelog v3.1.3:**
- 🔴 CRITICAL: Fixed `format_timer_stats_detailed()` signature (added missing `global_stats` 

     parametri:
- 🟡 Fixed `ProfileService.create_profile()` parameter (`is_guest` vs `set_as_default`)
- 🟡 Fixed `ProfileService.save_active_profile()` return type (`bool` vs `None`)
- 🟡 Fixed `ProfileService.record_session()` return type (`bool` vs `None`)
- 🟢 Fixed `ProfileService.list_all_profiles()` method name → `list_profiles()`

- Added breaking change warnings for v3.0.0 and v3.1.1 modifications
