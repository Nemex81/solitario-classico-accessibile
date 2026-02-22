# 📋 Piano di Implementazione - Sistema Audio Dinamico e Accessibile

> **Riferimento Design**: `docs/2 - projects/DESIGN_audio_system.md` (stato: FROZEN)  
> Questo piano traduce il design concettuale in implementazione tecnica step-by-step.

---

## 📊 Executive Summary

**Tipo**: FEATURE  
**Priorità**: 🟠 ALTA  
**Stato**: READY (v1.1 — post-review)
**Branch**: `feature/audio-system`
**Versione Target**: `v3.4.0`  
**Data Creazione**: 2026-02-22  
**Autore**: AI Assistant + Nemex81  
**Effort Stimato**: 12-16 ore totali  
**Commits Previsti**: 10 commit atomici

---

### Problema/Obiettivo

Aggiungere un sistema audio modulare a 5 bus indipendenti che funzioni come **display uditivo parallelo a NVDA**: feedback sonoro immediato (<50ms) con panning stereo spaziale per comunicare la posizione orizzontale delle pile, firma sonora per tipo di pila (tableau/fondazione/stock), clip vocali pre-campionate per eventi narrativi, e mixer accessibile da tastiera con preferenze persistite in JSON.

---

### Soluzione Proposta

Aggiungere interamente all'**Infrastructure Layer** il sottosistema audio composto da 4 classi (`AudioEvent`, `AudioConfigLoader`, `SoundCache`, `SoundMixer`, `AudioManager`), integrato nel `DIContainer` come singleton lazy-loaded. I controller del layer Application vengono estesi per emettere `AudioEvent` dopo ogni azione validata. La Presentation layer aggiunge il dialog `AccessibleMixerDialog` e il binding `EVT_ACTIVATE`. La libreria `pygame.mixer` gestisce i canali audio (già presente nel progetto come dipendenza runtime, ma rimossa da `requirements.txt` dopo la migrazione wxPython — va re-inserita esplicitamente).

---

### Impact Assessment

| Aspetto | Impatto | Note |
|---------|---------|------|
| **Severità** | BASSA (nuova feature, nessun breaking change) | Backward compatible: senza pygame il gioco funziona normalmente |
| **Scope** | 12 file nuovi + 6 modifiche | Vedi sezione File Structure |
| **Rischio regressione** | BASSO | I controller esistenti non vengono riscritti, solo estesi |
| **Breaking changes** | NO | Tutti i parametri audio_manager sono opzionali o iniettati |
| **Testing** | MEDIO | Richiede mock pygame.mixer per test headless |

---

## ⚠️ Note Critiche Pre-Implementazione

### 1. pygame già nel codebase ma non in requirements.txt

`GamePlayController` e `InputHandler` importano già `pygame` (per costanti `KMOD_SHIFT`, `KMOD_CTRL`). La libreria **è installata nel venv ma non dichiarata** dopo la migrazione wxPython v2.3.1. La Fase 1 re-inserisce `pygame` in `requirements.txt` con spiegazione.

### 2. simpleaudio installato ma non usato

L'installazione recente di `simpleaudio` nel venv è superflua: il design ha scelto `pygame.mixer` (vedi DESIGN §Opzioni Considerate). `simpleaudio` **non va importato né usato**. Può restare nel venv o essere disinstallato — non va aggiunto a `requirements.txt`.

### 3. Naming class GamePlayController vs GameplayController

Il DESIGN usa `GameplayController` ma la classe reale è `GamePlayController` (capital P). In questo PLAN si usa sempre il nome corretto `GamePlayController`.

### 4. Stereo positions: 13 indici (0-12)

Il mapping fisico del tavolo ha 13 posizioni (indici 0-12): 7 tableau + 4 fondazioni + 1 stock + 1 waste. La formula è `panning = (pile_index / 12) * 2.0 - 1.0`. Il valore "14 posizioni" nel DESIGN include una posizione virtuale per il menu (non usata nel gameplay loop).

---

## 🎯 Requisiti Funzionali

### RF-1: Feedback sonoro immediato per azioni sulle carte

**Comportamento Atteso**:
1. Giocatore esegue un'azione (mossa valida, mossa non valida, giro carta)
2. `GamePlayController` crea `AudioEvent` con tipo evento + indici pile
3. `AudioManager.play_event()` riproduce il suono corretto con panning spaziale in <50ms

### RF-2: Panning stereo spaziale per posizione pile

**Comportamento Atteso**:
1. Ogni pila ha un indice fisso 0-12 (sinistra → destra)
2. Formula lineare: `panning = (pile_index / 12) * 2.0 - 1.0`
3. Il panning viene applicato al canale pygame.mixer via `channel.set_volume(left, right)`

### RF-3: Mixer accessibile da tastiera (tasto `M`)

**Comportamento Atteso**:
1. Durante il gioco, tasto `M` apre `AccessibleMixerDialog` (modale)
2. Frecce su/giù: selezione bus; frecce sinistra/destra: volume ±5%; Spazio: toggle mute
3. Ogni modifica viene annunciata via TTS: *"Volume Gameplay: 75%"*
4. ESC chiude il mixer, salva preferenze in `audio_config.json`, riprende loop

### RF-4: Pausa/ripresa loop audio su focus finestra

**Comportamento Atteso**:
1. `wx.EVT_ACTIVATE` con `GetActive() == False` → `audio_manager.pause_all_loops()`
2. `wx.EVT_ACTIVATE` con `GetActive() == True` → `audio_manager.resume_all_loops()`
3. I bus one-shot (Gameplay, UI, Voice) non vengono mai sospesi

### RF-5: Preferenze persistite in JSON

**Comportamento Atteso**:
1. `config/audio_config.json` contiene volumi, stato mute, pack attivo
2. Alla chiusura del mixer o del gioco: scrittura su disco
3. Al riavvio: caricamento automatico con fallback ai default se file assente/corrotto

### RF-6: Degradazione graziosa

**Comportamento Atteso**:
1. Se `pygame.mixer` non disponibile (import error): `AudioManager` in modalità stub (no crash)
2. Se un file WAV mancante in `assets/sounds/`: warning nel log, suono saltato silenziosamente
3. Se `audio_config.json` assente: valori di default hardcodati

---

## 🏗️ Architettura

### Layer Diagram

```
[Domain Layer]         Invariato. Zero dipendenze audio.

[Application Layer]    GamePlayController  → crea AudioEvent, chiama audio_manager.play_event()
                       InputHandler        → chiama audio_manager.play_boundary_hit()
                       SolitarioDialogManager → chiama audio_manager.play_event() per eventi UI

[Infrastructure Layer] AudioManager        ← Orchestratore principale, singleton DIContainer
                       SoundMixer          ← 5 bus pygame.mixer, volumi, panning
                       SoundCache          ← Caricamento WAV in RAM all'avvio
                       AudioConfigLoader   ← Deserializzazione audio_config.json
                       audio_events.py     ← Dataclass AudioEvent + costanti

[Presentation Layer]   AccessibleMixerDialog ← Dialog wx navigabile da tastiera
                       MainFrame (modifica)  ← Binding EVT_ACTIVATE per pause/resume
```

### File Structure

```
src/infrastructure/audio/
    __init__.py                  (ESISTE - aggiornare export)
    audio_manager.py             (NEW)
    sound_mixer.py               (NEW)
    audio_events.py              (NEW)
    sound_cache.py               (NEW)
    screen_reader.py             (ESISTE - invariato)
    tts_provider.py              (ESISTE - invariato)

src/infrastructure/config/
    audio_config_loader.py       (NEW - segue pattern scoring_config_loader.py)
    scoring_config_loader.py     (ESISTE - riferimento pattern)
    __init__.py                  (ESISTE)

src/application/
    gameplay_controller.py       (MODIFY - AudioEvent dopo azioni carte)
    input_handler.py             (MODIFY - AudioEvent dopo navigazione + bumper)
    dialog_manager.py            (MODIFY - AudioEvent per eventi UI)

src/infrastructure/di_container.py
    (MODIFY - get_audio_manager() + shutdown hook in reset())

src/presentation/dialogs/
    accessible_mixer_dialog.py   (NEW - mixer 5 bus navigabile da tastiera)

src/infrastructure/ui/
    main_frame.py                (MODIFY - binding EVT_ACTIVATE)

config/
    audio_config.json            (NEW)

assets/sounds/default/
    gameplay/
        card_move.wav
        foundation_drop.wav
        invalid_move.wav
        card_flip.wav
        stock_draw.wav
    ui/
        navigate.wav
        confirm.wav
        cancel.wav
        boundary_hit.wav
    ambient/
        room_tone.wav
    music/
        (vuota - feature futura)
    voice/
        victory.wav
        (altri clip futuri)

requirements.txt                 (MODIFY - re-aggiunge pygame con nota)

tests/unit/infrastructure/
    test_audio_manager.py        (NEW)
    test_audio_config_loader.py  (NEW)
    test_sound_cache.py          (NEW)
```

---

## 📝 Piano di Implementazione

---

### FASE 1: Dipendenze e struttura assets

**Priorità**: 🔴 CRITICA (prerequisito di tutto)  
**Commit**: `chore(deps): re-aggiunge pygame per sistema audio + crea struttura assets`  
**File**: `requirements.txt`, `assets/sounds/`, `.gitignore`

#### Modifiche

**`requirements.txt`** — re-inserire pygame con nota esplicativa:

```
# Audio System (v3.4.0)
# pygame.mixer usato per i 5 bus audio indipendenti con panning stereo nativo.
# Nota: pygame era stato rimosso da requirements.txt (v2.3.1) dopo migrazione wxPython,
# ma era ancora usato nel codebase per keyboard constants (KMOD_SHIFT, KMOD_CTRL).
# Re-aggiunto esplicitamente per il sistema audio.
pygame>=2.1.2
```

**Struttura `assets/sounds/default/`** — creare le cartelle vuote con `.gitkeep`:

```
assets/
    sounds/
        .gitkeep                 (file vuoto per tracciare la dir in git)
        default/
            gameplay/.gitkeep
            ui/.gitkeep
            ambient/.gitkeep
            music/.gitkeep
            voice/.gitkeep
```

**`.gitignore`** — aggiungere regola per file audio binari (mantenendo la struttura):

```gitignore
# Audio assets - file binary WAV/MP3/OGG non tracciati in git standard
# Usa Git LFS o distribuisci separatamente (decisione v3.4.0: gitignore)
assets/sounds/**/*.wav
assets/sounds/**/*.mp3
assets/sounds/**/*.ogg
# Eccezione: .gitkeep per mantenere la struttura cartelle
!assets/sounds/**/.gitkeep
```

---

### FASE 2: AudioEvent dataclass e costanti eventi

**Priorità**: 🔴 CRITICA (usata da tutti gli altri componenti)  
**Commit**: `feat(infra): aggiunge AudioEvent dataclass e costanti AudioEventType`  
**File**: `src/infrastructure/audio/audio_events.py`

#### Struttura del file

```python
"""Audio event definitions for the solitaire audio system.

AudioEvent is the immutable data contract between Application layer
controllers and the AudioManager. Controllers create events;
AudioManager consumes them.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any


class AudioEventType:
    """String constants for audio event types.
    
    Organized by bus/category for clarity.
    Controllers use these constants when creating AudioEvent instances.
    """
    # Gameplay bus - azioni sulle carte
    CARD_MOVE_SUCCESS = "card_move_success"
    CARD_FLIP = "card_flip"
    FOUNDATION_DROP = "foundation_drop"
    STOCK_DRAW = "stock_draw"
    INVALID_MOVE = "invalid_move"
    AUTO_MOVE = "auto_move"
    GAME_WON = "game_won"
    GAME_LOST = "game_lost"
    
    # UI bus - navigazione menu e dialogs
    UI_NAVIGATE = "ui_navigate"
    UI_CONFIRM = "ui_confirm"
    UI_CANCEL = "ui_cancel"
    BOUNDARY_HIT_LEFT = "boundary_hit_left"
    BOUNDARY_HIT_RIGHT = "boundary_hit_right"
    DIALOG_OPEN = "dialog_open"
    DIALOG_CLOSE = "dialog_close"
    
    # Voice bus - clip campionate
    VOICE_VICTORY = "voice_victory"
    
    # Timer events
    TIMER_WARNING = "timer_warning"
    TIMER_EXPIRED = "timer_expired"


@dataclass(frozen=True)
class AudioEvent:
    """Immutable data contract for audio system events.
    
    Created by Application layer controllers, consumed by AudioManager.
    Controllers do not know HOW the sound will be played; they only
    describe WHAT happened using event_type and optional spatial info.
    
    Args:
        event_type: String constant from AudioEventType
        source_pile: Index 0-12 of origin pile (optional, for panning)
        destination_pile: Index 0-12 of destination pile (optional, for panning)
        context: Optional dict for future extensibility
        
    Example:
        >>> event = AudioEvent(
        ...     event_type=AudioEventType.FOUNDATION_DROP,
        ...     source_pile=2,
        ...     destination_pile=8
        ... )
    
    Version:
        v3.4.0: Initial implementation
    """
    event_type: str
    source_pile: Optional[int] = None
    destination_pile: Optional[int] = None
    context: Dict[str, Any] = field(default_factory=dict)
```

---

### FASE 3: AudioConfig dataclass e AudioConfigLoader

**Priorità**: 🔴 CRITICA  
**Commit**: `feat(infra): aggiunge AudioConfig dataclass e AudioConfigLoader`  
**File**: `src/infrastructure/config/audio_config_loader.py`, `config/audio_config.json`

#### `config/audio_config.json` — schema completo

```json
{
  "version": "1.0",
  "active_sound_pack": "default",
  "bus_volumes": {
    "gameplay": 80,
    "ui": 70,
    "ambient": 40,
    "music": 30,
    "voice": 90
  },
  "bus_muted": {
    "gameplay": false,
    "ui": false,
    "ambient": false,
    "music": false,
    "voice": false
  },
  "mixer_params": {
    "frequency": 44100,
    "size": -16,
    "channels": 2,
    "buffer": 512
  }
}
```

#### `AudioConfig` dataclass (in `audio_config_loader.py`)

```python
@dataclass
class AudioConfig:
    """Audio system configuration loaded from audio_config.json.
    
    Args:
        version: Config schema version (must start with "1.")
        active_sound_pack: Name of the active sound pack folder
        bus_volumes: Dict bus_name -> volume int 0-100
        bus_muted: Dict bus_name -> bool
        mixer_params: Dict with frequency, size, channels, buffer
        
    Note:
        pile_panning rimosso in v1.1: il calcolo è dinamico in
        AudioManager._get_panning_for_event() tramite formula lineare.
        
    Version:
        v3.4.0: Initial implementation | v1.1: rimosso pile_panning
    """
    version: str = "1.0"
    active_sound_pack: str = "default"
    bus_volumes: Dict[str, int] = field(default_factory=lambda: {
        "gameplay": 80, "ui": 70, "ambient": 40, "music": 30, "voice": 90
    })
    bus_muted: Dict[str, bool] = field(default_factory=lambda: {
        "gameplay": False, "ui": False, "ambient": False, "music": False, "voice": False
    })
    # pile_panning rimosso (v1.1): il calcolo è dinamico in AudioManager._get_panning_for_event()
    # Non persistere valori derivati nel JSON — violazione DRY (cfr. scoring_config.json pattern)
    mixer_params: Dict[str, int] = field(default_factory=lambda: {
        "frequency": 44100, "size": -16, "channels": 2, "buffer": 512
    })
```

**Pattern da seguire**: `scoring_config_loader.py` — stesso schema: `load()` classmethod con fallback, `fallback_default()`, `_parse_and_validate()`.

---

### FASE 4: SoundCache

**Priorità**: 🟠 ALTA  
**Commit**: `feat(infra): aggiunge SoundCache - caricamento WAV in RAM`  
**File**: `src/infrastructure/audio/sound_cache.py`

#### API pubblica richiesta

```python
class SoundCache:
    def __init__(self, sounds_base_path: Path) -> None: ...
    
    def load_pack(self, pack_name: str) -> None:
        """Carica tutti i WAV del pack in RAM come pygame.Sound.
        File assenti: warning nel log, entry None (degradazione graziosa)."""
    
    def get(self, event_type: str) -> Optional[pygame.mixer.Sound]:
        """Restituisce il Sound pre-caricato per il tipo evento, o None se assente."""
    
    def clear(self) -> None:
        """Svuota la cache (usato su shutdown o cambio pack)."""
```

**File mapping** (event_type → file WAV relativo):

```python
SOUND_FILES: Dict[str, str] = {
    AudioEventType.CARD_MOVE_SUCCESS:   "gameplay/card_move.wav",
    AudioEventType.CARD_FLIP:           "gameplay/card_flip.wav",
    AudioEventType.FOUNDATION_DROP:     "gameplay/foundation_drop.wav",
    AudioEventType.STOCK_DRAW:          "gameplay/stock_draw.wav",
    AudioEventType.INVALID_MOVE:        "gameplay/invalid_move.wav",
    AudioEventType.AUTO_MOVE:           "gameplay/card_move.wav",  # riusa
    AudioEventType.UI_NAVIGATE:         "ui/navigate.wav",
    AudioEventType.UI_CONFIRM:          "ui/confirm.wav",
    AudioEventType.UI_CANCEL:           "ui/cancel.wav",
    AudioEventType.BOUNDARY_HIT_LEFT:   "ui/boundary_hit.wav",
    AudioEventType.BOUNDARY_HIT_RIGHT:  "ui/boundary_hit.wav",
    AudioEventType.DIALOG_OPEN:         "ui/confirm.wav",
    AudioEventType.DIALOG_CLOSE:        "ui/cancel.wav",
    AudioEventType.GAME_WON:            "voice/victory.wav",
    AudioEventType.TIMER_WARNING:       "ui/navigate.wav",
    AudioEventType.TIMER_EXPIRED:       "ui/cancel.wav",
}
```

---

### FASE 5: SoundMixer

**Priorità**: 🟠 ALTA  
**Commit**: `feat(infra): aggiunge SoundMixer - gestione 5 bus pygame.mixer`  
**File**: `src/infrastructure/audio/sound_mixer.py`

#### API pubblica richiesta

```python
BUS_NAMES = ("gameplay", "ui", "ambient", "music", "voice")

class SoundMixer:
    def __init__(self, config: AudioConfig) -> None:
        """Crea e configura i 5 canali pygame.mixer con volumi da config."""
    
    def play_one_shot(
        self,
        sound: pygame.mixer.Sound,
        bus_name: str,
        panning: float = 0.0
    ) -> None:
        """Riproduce un suono one-shot sul bus specificato con panning -1.0..+1.0."""
    
    def play_loop(self, sound: pygame.mixer.Sound, bus_name: str) -> None:
        """Avvia un loop infinito sul bus specificato (bus ambient/music)."""
    
    def pause_loops(self) -> None:
        """Sospende bus ambient e music (one-shot rimangono attivi)."""
    
    def resume_loops(self) -> None:
        """Riprende bus ambient e music."""
    
    def stop_all(self) -> None:
        """Ferma tutti i canali (usato su shutdown)."""
    
    def set_bus_volume(self, bus_name: str, volume: int) -> None:
        """Imposta volume bus 0-100 (convertito a float 0.0-1.0 internamente)."""
    
    def toggle_bus_mute(self, bus_name: str) -> bool:
        """Toggle mute del bus. Restituisce nuovo stato mute (True=silenziato)."""
    
    def get_bus_volume(self, bus_name: str) -> int:
        """Restituisce volume corrente del bus (int 0-100)."""
    
    def is_bus_muted(self, bus_name: str) -> bool: ...
```

#### Calcolo panning per canale stereo

> **Fix v1.1**: Sostituita formula lineare classica con constant-power pan law.
> La formula precedente dimezzava il volume percepito al centro (left=0.5, right=0.5 con panning=0.0).
> Con la formula corretta il volume è uniforme su tutto lo spettro stereo — essenziale per un
> sistema audio accessibile dove l'audio è un canale informativo critico.

```python
def _apply_panning(channel: pygame.mixer.Channel, panning: float) -> None:
    """Applica panning stereo al canale con constant-power pan law.
    
    Args:
        channel: pygame.mixer.Channel
        panning: float -1.0 (sinistra) ... +1.0 (destra)
    
    Formula (constant-power lineare):
        - Quando panning < 0 (sinistra): left=1.0, right ridotto proporzionalmente
        - Quando panning > 0 (destra): right=1.0, left ridotto proporzionalmente
        - Quando panning = 0 (centro): left=1.0, right=1.0 (volume massimo)
    
    Mantiene il volume percepito costante su tutto lo spettro stereo.
    La formula lineare classica (1.0-pan)/2.0 produce left=0.5/right=0.5 al centro
    (-6dB totale percepito) che è inaccettabile per feedback audio accessibile.
    """
    if panning < 0.0:  # Suono verso sinistra
        left = 1.0
        right = 1.0 + panning  # panning negativo riduce right (es. -0.5 → right=0.5)
    else:  # Suono verso destra o centro (panning=0)
        left = 1.0 - panning   # panning positivo riduce left (es. +0.5 → left=0.5)
        right = 1.0
    
    # Clamp per sicurezza
    left = max(0.0, min(1.0, left))
    right = max(0.0, min(1.0, right))
    
    channel.set_volume(left, right)
```

---

### FASE 6: AudioManager — orchestratore principale

**Priorità**: 🔴 CRITICA  
**Commit**: `feat(infra): aggiunge AudioManager - orchestratore sistema audio`  
**File**: `src/infrastructure/audio/audio_manager.py`

#### API pubblica richiesta

```python
class AudioManager:
    """Unico punto di ingresso al sistema audio.
    
    Riceve AudioEvent dai controller Application, consulta SoundCache,
    calcola panning, delega la riproduzione a SoundMixer.
    
    Stati: NON_INITIALIZED → ACTIVE ⇄ LOOPS_PAUSED → SHUTDOWN
    
    Args:
        config: AudioConfig caricato da AudioConfigLoader
        sounds_base_path: Path base per assets/sounds/ (default: Path("assets/sounds"))
    """
    
    def initialize(self) -> bool:
        """Inizializza pygame.mixer e SoundCache. 
        Returns True se successo, False con fallback stub se pygame non disponibile."""
    
    def play_event(self, event: AudioEvent) -> None:
        """Riproduce il suono associato all'evento con panning spaziale.
        No-op se non inizializzato o suono assente in cache."""
    
    def pause_all_loops(self) -> None:
        """Sospende bus Ambient e Music (chiamato da Presentation su EVT_ACTIVATE)."""
    
    def resume_all_loops(self) -> None:
        """Riprende bus Ambient e Music."""
    
    def set_bus_volume(self, bus_name: str, volume: int) -> None: ...
    def toggle_bus_mute(self, bus_name: str) -> bool: ...
    def get_bus_volume(self, bus_name: str) -> int: ...
    def is_bus_muted(self, bus_name: str) -> bool: ...
    
    def save_settings(self) -> None:
        """Scrive volumi e stato mute correnti in audio_config.json."""
    
    def shutdown(self) -> None:
        """Salva settings, ferma tutti i canali, chiama pygame.mixer.quit()."""
    
    @property
    def is_available(self) -> bool:
        """True se pyhame.mixer è inizializzato e il sistema è operativo."""
```

#### Calcolo panning da AudioEvent

> **Fix v1.1**: Il panning non viene più letto da `config.pile_panning` (rimosso dal JSON).
> Viene calcolato dinamicamente con la formula lineare `(pile_index / 12) * 2.0 - 1.0`.
> Questo elimina la duplicazione logica formula-JSON e garantisce DRY.

```python
def _get_panning_for_event(self, event: AudioEvent) -> float:
    """Determina il panning dall'evento usando formula lineare.
    
    Priorità: destination_pile > source_pile > 0.0 (centro)
    
    Args:
        event: AudioEvent con indici pile 0-12
        
    Returns:
        float da -1.0 (sinistra) a +1.0 (destra)
    
    Formula:
        panning = (pile_index / 12) * 2.0 - 1.0
        
        Mapping logico:
        - pile_index 0 (Tableau 1) → -1.0 (estrema sinistra)
        - pile_index 6 (Tableau 7) → 0.0 (centro)
        - pile_index 12 (Waste)    → +1.0 (estrema destra)
    """
    pile_index = event.destination_pile if event.destination_pile is not None else event.source_pile
    
    if pile_index is None:
        return 0.0  # Default al centro per eventi senza posizione spaziale
    
    # Formula lineare — single source of truth per il calcolo
    panning = (pile_index / 12.0) * 2.0 - 1.0
    
    # Clamp per sicurezza (pile_index dovrebbe essere già 0-12)
    return max(-1.0, min(1.0, panning))
```

#### Classe Stub per Degradazione Graziosa

> **Fix v1.1**: La classe `_AudioManagerStub` era referenziata nella FASE 7 (DIContainer)
> ma non definita in questa fase. Aggiunta qui per completezza.

```python
class _AudioManagerStub:
    """No-op stub per AudioManager quando pygame non è disponibile.
    
    Implementa la stessa interfaccia pubblica di AudioManager ma tutti
    i metodi sono no-op safe. Permette al resto del codice di chiamare
    audio_manager.play_event() senza crash anche se pygame manca.
    
    Pattern identico a TtsProvider nel codebase esistente.
    
    Version:
        v3.4.0: Initial implementation
    """
    
    @property
    def is_available(self) -> bool:
        """Sempre False per lo stub."""
        return False
    
    def initialize(self) -> bool:
        """No-op. Restituisce False."""
        return False
    
    def play_event(self, event: "AudioEvent") -> None:
        """No-op. Ignora silenziosamente l'evento."""
        pass
    
    def pause_all_loops(self) -> None:
        """No-op."""
        pass
    
    def resume_all_loops(self) -> None:
        """No-op."""
        pass
    
    def set_bus_volume(self, bus_name: str, volume: int) -> None:
        """No-op."""
        pass
    
    def toggle_bus_mute(self, bus_name: str) -> bool:
        """No-op. Restituisce sempre False."""
        return False
    
    def get_bus_volume(self, bus_name: str) -> int:
        """Restituisce sempre 0."""
        return 0
    
    def is_bus_muted(self, bus_name: str) -> bool:
        """Restituisce sempre False."""
        return False
    
    def save_settings(self) -> None:
        """No-op."""
        pass
    
    def shutdown(self) -> None:
        """No-op."""
        pass
```

**Pattern di utilizzo nel codice chiamante**:

```python
# Controller code — None check sufficiente, anche se è uno stub non crasha
if self._audio:
    self._audio.play_event(event)
```

---

### FASE 7: DIContainer integration

**Priorità**: 🟠 ALTA  
**Commit**: `feat(infra): integra AudioManager in DIContainer come singleton`  
**File**: `src/infrastructure/di_container.py`

#### Modifica da apportare

Aggiungere nella sezione `# INFRASTRUCTURE LAYER`:

```python
def get_audio_manager(self) -> Any:
    """Get or create AudioManager singleton.
    
    AudioManager manages pygame.mixer lifecycle and is shared
    across the application.
    
    Returns:
        AudioManager singleton. Returns stub (non-functional but safe)
        if pygame.mixer is not available.
        
    Version:
        v3.4.0: Initial implementation
    """
    if "audio_manager" not in self._instances:
        try:
            from src.infrastructure.audio.audio_manager import AudioManager
            from src.infrastructure.config.audio_config_loader import AudioConfigLoader
            config = AudioConfigLoader.load()
            manager = AudioManager(config)
            manager.initialize()
            self._instances["audio_manager"] = manager
        except Exception:
            # Degradazione graziosa: AudioManager stub (no-op)
            from src.infrastructure.audio.audio_manager import _AudioManagerStub
            self._instances["audio_manager"] = _AudioManagerStub()
    return self._instances["audio_manager"]
```

Modificare `reset()` e `reset_all()` per chiamare `shutdown()` sull'audio_manager prima di rimuoverlo:

```python
def reset(self) -> None:
    """Reset all singleton instances. Calls shutdown() on AudioManager if present."""
    if "audio_manager" in self._instances:
        self._instances["audio_manager"].shutdown()
    self._instances.clear()
```

---

### FASE 8: Application Layer - integrazione AudioEvent nei controller

**Priorità**: 🟠 ALTA  
**Commit**: `feat(application): integra AudioEvent in GamePlayController, InputHandler, DialogManager`  
**File**: `src/application/gameplay_controller.py`, `src/application/input_handler.py`, `src/application/dialog_manager.py`

#### GamePlayController

Aggiungere `audio_manager` come parametro opzionale all'`__init__`:

```python
def __init__(
    self,
    engine: GameEngine,
    screen_reader,
    settings: Optional[GameSettings] = None,
    on_new_game_request: Optional[Callable[[], None]] = None,
    audio_manager: Optional[Any] = None  # NEW v3.4.0
) -> None:
    ...
    self._audio = audio_manager  # None = degradazione graziosa
```

Pattern da replicare per ogni azione:

```python
def _handle_move_success(self, source_idx: int, dest_idx: int) -> None:
    """Emette AudioEvent dopo mossa valida."""
    if self._audio:
        from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
        self._audio.play_event(AudioEvent(
            event_type=AudioEventType.CARD_MOVE_SUCCESS,
            source_pile=source_idx,
            destination_pile=dest_idx
        ))
```

**Punti di integrazione in GamePlayController** (cercare nel codice i response path):
- Mossa carta su tableau → `CARD_MOVE_SUCCESS`
- Mossa carta su fondazione → `FOUNDATION_DROP`
- Pesca da mazzo → `STOCK_DRAW`
- Giro carta scoperta → `CARD_FLIP`
- Mossa non valida → `INVALID_MOVE`
- Auto-move → `AUTO_MOVE`
- Vittoria → `GAME_WON` (poi `pause_all_loops()`)

#### Integrazione eventi Timer

> **Fix v1.1**: `TIMER_WARNING` e `TIMER_EXPIRED` erano definiti in `AudioEventType` e mappati
> in `SoundCache`, ma nessun codice li emetteva. Corretti di seguito.

**Nota API reale `TimerManager`** (versione corrente del codebase):
- `warning_callback: Optional[Callable[[int], None]]` — passato in `__init__` (riceve minuti rimanenti)
- Nessun `expired_callback` e **nessun setter method** `set_warning_callback()`

**Per `TIMER_WARNING`**: passare un callback al sito di costruzione del `TimerManager`
(tipicamente in `GameEngine` o nel controller che crea il timer). Esempio:

```python
# Nel controller/engine che crea TimerManager:
def _create_timer(self, minutes: int) -> TimerManager:
    def _on_timer_warning(minutes_left: int) -> None:
        if self._audio:
            from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
            self._audio.play_event(AudioEvent(event_type=AudioEventType.TIMER_WARNING))
    
    return TimerManager(
        minutes=minutes,
        warning_callback=_on_timer_warning
    )
```

**Per `TIMER_EXPIRED`**: aggiungere `expired_callback` a `TimerManager` (piccola modifica al costruttore):

```python
# Modifica minima in timer_manager.py (FASE 8 estesa):
def __init__(
    self,
    minutes: int = 10,
    warning_callback: Optional[Callable[[int], None]] = None,
    expired_callback: Optional[Callable[[], None]] = None,  # NEW v3.4.0
    warning_intervals: Optional[list[int]] = None
) -> None:
    ...
    self.expired_callback = expired_callback
    self._expired_fired: bool = False  # NEW — evita firing ripetuto
```

E in `check_warnings()` aggiungere:

```python
# In TimerManager.check_warnings() — aggiungere PRIMA del return:
if self.is_expired() and not self._expired_fired and self.expired_callback is not None:
    self._expired_fired = True
    self.expired_callback()
```

Il `reset()` deve anche resettare `self._expired_fired = False`.

#### InputHandler

Aggiungere parametro `audio_manager` e metodo:

```python
def notify_boundary_hit(self, direction: str) -> None:
    """Emette AudioEvent per bumper di fine corsa.
    
    Args:
        direction: 'left' o 'right'
    """
    if self._audio:
        event_type = (AudioEventType.BOUNDARY_HIT_LEFT 
                      if direction == 'left' 
                      else AudioEventType.BOUNDARY_HIT_RIGHT)
        self._audio.play_event(AudioEvent(event_type=event_type))
```

#### InputHandler.GameCommand — nuovo comando mixer

Aggiungere al `GameCommand` enum:

```python
# Audio (v3.4.0)
TOGGLE_AUDIO_MIXER = auto()  # Tasto M
```

E nel mapping tasti in `input_handler.py`:
```python
pygame.K_m: GameCommand.TOGGLE_AUDIO_MIXER,
```

#### Gestione `TOGGLE_AUDIO_MIXER` in `GamePlayController`

> **Fix v1.1**: Il tasto `M` viene mappato al comando ma nessun branch lo gestiva.
> Aggiunto qui il metodo di gestione esplicito.

Nel metodo `_build_commands()` di `GamePlayController`, aggiungere la voce:

```python
# Nel dizionario costruito da _build_commands():
GameCommand.TOGGLE_AUDIO_MIXER: self._show_audio_mixer_dialog,
```

Aggiungere il metodo:

```python
def _show_audio_mixer_dialog(self) -> None:
    """Apre AccessibleMixerDialog in modalità modale.
    
    Chiamato quando il giocatore preme il tasto M durante il gameplay.
    Il dialog riceve l'AudioManager per leggere/modificare i volumi dei 5 bus.
    Al termine chiama audio_manager.save_settings() e resume_all_loops().
    
    Degradazione graziosa: se AudioManager non disponibile, notifica via TTS.
    """
    if not self._audio or not self._audio.is_available:
        if self.sr:
            self.sr.speak("Sistema audio non disponibile", interrupt=True)
        return
    
    from src.presentation.dialogs.accessible_mixer_dialog import AccessibleMixerDialog
    
    # Nota: GamePlayController non ha _frame direttamente — il frame viene
    # recuperato dal SolitarioDialogManager o passato via __init__ (da verificare
    # nella struttura effettiva al momento dell'implementazione)
    parent_frame = getattr(self, '_frame', None) or getattr(self, '_parent', None)
    
    dialog = AccessibleMixerDialog(
        parent=parent_frame,
        audio_manager=self._audio
    )
    dialog.ShowModal()
    dialog.Destroy()
```

#### SolitarioDialogManager

Aggiungere parametro `audio_manager` opzionale e chiamata:

```python
# In show_*_prompt() methods, prima del ShowModal:
if self._audio:
    self._audio.play_event(AudioEvent(event_type=AudioEventType.DIALOG_OPEN))
```

---

### FASE 9: Presentation Layer - AccessibleMixerDialog + EVT_ACTIVATE

**Priorità**: 🟡 MEDIA  
**Commit**: `feat(presentation): aggiunge AccessibleMixerDialog e binding EVT_ACTIVATE`  
**File**: `src/presentation/dialogs/accessible_mixer_dialog.py`, modifica `src/infrastructure/ui/main_frame.py` (o equivalente frame principale)

#### AccessibleMixerDialog — struttura

```
Dialog: "Mixer Audio" (wx.Dialog, title="Mixer Audio")
  ├── Testo informativo: "Usa frecce su/giù per selezionare bus, sinistra/destra per volume"
  ├── ListCtrl o sequenza di controlli navigabili (uno per bus):
  │     Gameplay  [80%] [MUTE: No]
  │     UI        [70%] [MUTE: No]
  │     Ambient   [40%] [MUTE: No]
  │     Musica    [30%] [MUTE: No]
  │     Voce      [90%] [MUTE: No]
  └── Bottone [&Chiudi] (wx.ID_CLOSE, ESC)
```

**Comportamento tastiera**:
- Frecce su/giù: navigazione tra bus
- Frecce sinistra/destra: volume ±5% (chiama `audio_manager.set_bus_volume()`)
- Spazio: toggle mute (chiama `audio_manager.toggle_bus_mute()`)
- Ogni modifica: TTS annuncia *"Gameplay: 75%"* o *"UI: silenziato"*
- ESC / Chiudi: chiama `audio_manager.save_settings()`, poi `resume_all_loops()`

**Al momento dell'apertura**: `audio_manager.pause_all_loops()` (sospende ambient/music), TTS nnuncia *"Mixer Audio aperto"*.

#### EVT_ACTIVATE binding nel frame principale

Localizzare il frame principale wxPython (probabilmente `src/infrastructure/ui/`) e aggiungere:

```python
self.Bind(wx.EVT_ACTIVATE, self._on_window_activate)

def _on_window_activate(self, event: wx.ActivateEvent) -> None:
    """Pausa/riprende loop audio su perdita/acquisizione focus finestra."""
    audio = self._container.get_audio_manager()  # o via parametro DI
    if event.GetActive():
        audio.resume_all_loops()
    else:
        audio.pause_all_loops()
    event.Skip()
```

---

### FASE 10: Test + Documentazione

**Priorità**: 🟠 ALTA  
**Commit 1**: `test: aggiunge unit test sistema audio (headless mock)`  
**Commit 2**: `docs: aggiorna API.md, ARCHITECTURE.md, CHANGELOG.md per v3.4.0`

**File test**: `tests/unit/infrastructure/test_audio_manager.py`, `test_audio_config_loader.py`

---

## 🧪 Testing Strategy

### Problema: pygame.mixer richiede un display per inizializzarsi

**Soluzione**: Mock di `pygame.mixer` per tutti i test unit/integration.

```python
# tests/unit/infrastructure/test_audio_manager.py

import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_pygame_mixer():
    """Mock completo di pygame.mixer per test headless."""
    with patch("src.infrastructure.audio.sound_mixer.pygame") as mock_pygame:
        mock_pygame.mixer.init = MagicMock()
        mock_pygame.mixer.Channel = MagicMock()
        mock_pygame.mixer.Sound = MagicMock()
        mock_pygame.mixer.quit = MagicMock()
        yield mock_pygame
```

### Unit Tests (`tests/unit/infrastructure/`)

#### `test_audio_config_loader.py` (5 test)
- [ ] `test_load_default_when_file_missing` — fallback ai default se JSON assente
- [ ] `test_load_from_valid_json` — caricamento corretto da file valido
- [ ] `test_load_raises_on_malformed_json` — ValueError su JSON corrotto
- [ ] `test_fallback_default_has_all_required_buses` — i 5 bus sono presenti nei default
- [ ] `test_version_check` — versione non inizia con "1." → ValueError

#### `test_audio_manager.py` (8 test)
- [ ] `test_is_not_available_before_initialize`
- [ ] `test_initialize_returns_true_with_mock_pygame`
- [ ] `test_play_event_no_op_when_not_initialized`
- [ ] `test_play_event_calls_sound_mixer`
- [ ] `test_pause_loops_delegates_to_mixer`
- [ ] `test_resume_loops_delegates_to_mixer`
- [ ] `test_save_settings_writes_json`
- [ ] `test_shutdown_calls_mixer_quit`

#### `test_sound_cache.py` (4 test)
- [ ] `test_get_returns_none_for_unknown_event`
- [ ] `test_get_returns_none_when_wav_missing` (degradazione graziosa)
- [ ] `test_clear_empties_cache`
- [ ] `test_load_pack_logs_warning_for_missing_file`

### Marker pytest

Tutti i test di questo modulo usano `@pytest.mark.unit` (nessuna dipendenza da wx o filesystem reale).

---

## ✅ Validation & Acceptance

### Success Criteria

**Funzionali**:
- [ ] Ogni azione sulle carte produce suono in <50ms (verifica manuale)
- [ ] Il panning è percettibilmente diverso tra pila sinistra e destra (verifica manuale con cuffie)
- [ ] Il tasto `M` apre il mixer accessibile navigabile
- [ ] Modifica volume → TTS annuncia il nuovo valore
- [ ] Alt+Tab → loop audio si sospendono, ritorno → riprendono
- [ ] File WAV assente → nessun crash, solo warning nel log

**Tecnici**:
- [ ] `pytest -m "not gui"` passa al 100%
- [ ] Nessuna importazione di `pygame.mixer` al di fuori di `src/infrastructure/audio/`
- [ ] `audio_manager` nel Domain Layer: **zero import** (verifica con grep)
- [ ] Type hints completi su tutti i metodi pubblici
- [ ] Degradazione graziosa: se `import pygame` fallisce, `AudioManager.is_available == False`

**Code Quality**:
- [ ] `mypy src/infrastructure/audio/ --strict` → 0 errori
- [ ] Docstring Google style su tutte le classi e metodi pubblici

---

## 🚨 Common Pitfalls to Avoid

### ❌ DON'T: importare AudioManager nel Domain Layer

```python
# WRONG
# src/domain/services/game_service.py
from src.infrastructure.audio.audio_manager import AudioManager  # ❌ VIOLA CLEAN ARCH
```

### ✅ DO: AudioManager ricevuto via DIContainer nei controller Application

```python
# CORRECT
# src/application/gameplay_controller.py
def __init__(self, ..., audio_manager=None):
    self._audio = audio_manager  # Iniezione, mai import diretto
```

---

### ❌ DON'T: chiamare pygame.mixer fuori da SoundMixer

```python
# WRONG
# src/infrastructure/audio/audio_manager.py
import pygame
pygame.mixer.Channel(0).play(sound)  # ❌ logica mixer nell'orchestratore
```

### ✅ DO: AudioManager delega sempre a SoundMixer

```python
# CORRECT
self._mixer.play_one_shot(sound, bus_name="gameplay", panning=panning)  # ✅
```

---

### ❌ DON'T: `pygame.mixer.init()` senza parametri (latenza alta)

```python
pygame.mixer.init()  # ❌ parametri default → buffer 1024+ → latenza >100ms
```

### ✅ DO: init con parametri espliciti per bassa latenza

```python
params = config.mixer_params
pygame.mixer.pre_init(params["frequency"], params["size"], params["channels"], params["buffer"])
pygame.mixer.init()  # ✅ buffer 512 → latenza <50ms su Windows 11
```

---

## 📦 Commit Strategy (10 commit atomici)

1. `chore(deps): re-aggiunge pygame a requirements.txt + struttura assets/sounds/`
2. `feat(infra): aggiunge AudioEvent dataclass e AudioEventType constants`
3. `feat(infra): aggiunge AudioConfig dataclass e AudioConfigLoader`
4. `feat(infra): aggiunge SoundCache - caricamento WAV in RAM con degradazione graziosa`
5. `feat(infra): aggiunge SoundMixer - 5 bus pygame.mixer con panning stereo`
6. `feat(infra): aggiunge AudioManager - orchestratore sistema audio`
7. `feat(infra): integra AudioManager in DIContainer (lazy singleton + shutdown hook)`
8. `feat(application): integra AudioEvent in GamePlayController, InputHandler, DialogManager`
9. `feat(presentation): aggiunge AccessibleMixerDialog e EVT_ACTIVATE binding`
10. `test+docs: unit test sistema audio + aggiornamento API.md, ARCHITECTURE.md, CHANGELOG.md`

---

## 📚 References

### Internal Files di Riferimento

| File | Rilevanza |
|------|-----------|
| `src/infrastructure/config/scoring_config_loader.py` | Pattern loader JSON da replicare |
| `config/scoring_config.json` | Schema JSON di riferimento |
| `src/infrastructure/di_container.py` | Pattern lazy singleton (get_screen_reader) |
| `src/infrastructure/audio/tts_provider.py` | Pattern degradazione graziosa |
| `src/application/gameplay_controller.py` | Controller principale da estendere |
| `src/application/input_handler.py` | GameCommand enum + keyboard mapping |
| `docs/2 - projects/DESIGN_audio_system.md` | Design concettuale (fonte di verità) |

### External Docs

- [pygame.mixer API](https://www.pygame.org/docs/ref/mixer.html)
- [pygame.mixer.Channel.set_volume](https://www.pygame.org/docs/ref/mixer.html#pygame.mixer.Channel.set_volume) — per panning stereo
- [pygame.mixer.pre_init](https://www.pygame.org/docs/ref/mixer.html#pygame.mixer.pre_init) — per bassa latenza

---

## 📝 Note Operative per Copilot

### Workflow per ogni fase

1. Leggi la fase da implementare in questo documento
2. Identifica i file coinvolti
3. Verifica il pattern di riferimento (sezione References)
4. Implementa scope limitato alla fase corrente
5. Commit atomico con messaggio conventional
6. Aggiorna `docs/TODO.md` spuntando la checkbox
7. Torna al punto 1

### Verifica Rapida Pre-Commit

```bash
# Sintassi Python
python -m py_compile src/infrastructure/audio/*.py

# No import audio nel Domain Layer
grep -r "audio_manager\|AudioManager\|AudioEvent" src/domain/ --include="*.py"
# DEVE restituire 0 match

# Type checking modulo audio
mypy src/infrastructure/audio/ --strict

# Unit test headless
pytest tests/unit/infrastructure/ -m "not gui" -v
```

### Troubleshooting

**Se `pygame.mixer.init()` crashca in test headless**:
- Assicurarsi che il mock `mock_pygame_mixer` fixture sia applicato
- `pygame.mixer.pre_init(0,0,0,0)` bypassa l'init (solo per test)

**Se panning non si sente**:
- Verificare che `pre_init` sia chiamato prima di `init`
- Verificare che il buffer sia 512 (non 0 o 1024)
- Su Windows: testare con cuffie (speaker mono non permette panning)

---

## 🚀 Risultato Finale Atteso

Una volta completata l'implementazione:

✅ **Panning spaziale**: Ogni pila del tavolo ha una posizione stereo distinta e progressiva  
✅ **Feedback immediato**: Conferma sonora di ogni mossa in <50ms, prima di NVDA  
✅ **Firma sonora**: Tableau, fondazioni e stock hanno timbri distinguibili  
✅ **Mixer accessibile**: Tasto M → dialog navigabile da tastiera con TTS feedback  
✅ **Persistenza**: Preferenze audio salvate tra sessioni  
✅ **Degradazione graziosa**: Gioco pienamente giocabile senza audio o file WAV

---

## 📋 Changelog Documento

### v1.1 — 2026-02-22 (post-review)

Correzioni applicate a seguito della review tecnica `REVIEW_audio_system_v3.4.0.md`:

- **[CRITICO] Fix #1**: Formula `_apply_panning` in FASE 5 sostituita con constant-power pan law. La formula precedente dimezzava il volume percepito al centro del campo stereo.
- **[ALTO] Fix #2**: Rimosso `pile_panning` da `audio_config.json` e `AudioConfig` dataclass. Il calcolo è ora dinamico in `AudioManager._get_panning_for_event()` tramite formula lineare — elimina violazione DRY.
- **[MEDIO] Fix #3**: Aggiunto pseudocodice per emissione `TIMER_WARNING`/`TIMER_EXPIRED` in FASE 8, con nota esplicita sull'API reale di `TimerManager` (nessun setter method, solo `warning_callback` in `__init__`; proposta aggiunta `expired_callback`).
- **[MEDIO] Fix #4**: Aggiunto handler `_show_audio_mixer_dialog()` e mapping in `_build_commands()` per il comando `TOGGLE_AUDIO_MIXER` in FASE 8.
- **[BASSO] Fix #5**: Aggiunta definizione completa di `_AudioManagerStub` in FASE 6, referenziata ma mancante nella bozza originale.

---

**Document Version**: v1.1  
**Data Creazione**: 2026-02-22  
**Data Revisione**: 2026-02-22  
**Stato**: READY (per implementazione)  
**Autore**: AI Assistant + Nemex81  
**Design di Riferimento**: `DESIGN_audio_system.md` v1.1 (FROZEN)
