# 🔍 Review Critico - PLAN_audio_system_v3.4.0.md

> **Documento Analizzato**: `PLAN_audio_system_v3.4.0.md`  
> **Data Review**: 2026-02-22  
> **Reviewer**: AI Assistant  
> **Stato Documento**: DRAFT → NEEDS REVISION (5 correzioni richieste)  
> **Versione Target**: v3.4.0

---

## 📊 Executive Summary

### Giudizio Complessivo: 🟢 8.5/10 - MOLTO BUONO

Il documento è **strutturalmente solido** e allineato al design concettuale FROZEN. L'architettura rispetta perfettamente la Clean Architecture del progetto, il pattern di configurazione JSON è identico a `scoring_config_loader.py`, la degradazione graziosa è implementata su tutti i livelli, e la commit strategy è atomica e rollback-safe.

**Tuttavia**, sono stati individuati **6 problemi tecnici** che richiedono correzione prima dell'implementazione. Di questi, **1 è critico** (formula panning errata che abbassa il volume), **3 sono ad alta/media priorità** (anti-pattern, eventi mancanti, handler incompleto), **1 è medio** (mappatura asset non allineata ai file reali), e **1 è minore** (classe stub non definita).

**Raccomandazione**: Applicare le correzioni indicate nelle sezioni seguenti prima di passare all'implementazione. Con queste modifiche, il PLAN diventa esecutivo al 100% senza ambiguità.

---

## ✅ Punti di Forza

### 1. Architettura Clean e Separazione Layer

**Cosa funziona**:
- Audio vive interamente nell'Infrastructure Layer
- Domain Layer completamente intonso (zero import audio)
- Application Layer riceve `audio_manager` via DI opzionale
- Pattern identico a `ScreenReader` e `ProfileService` già presenti nel codebase

**Evidenza**: Sezione "Layer Diagram" nella FASE "Architettura" mostra separazione netta tra layer. Nessuna violazione dei confini architetturali.

---

### 2. Pattern JSON Config Coerente

**Cosa funziona**:
- `AudioConfig` dataclass con `default_factory`
- `AudioConfigLoader.load()` classmethod con fallback
- Schema JSON con versioning (`"version": "1.0"`)
- Identico al pattern di `scoring_config_loader.py` esistente

**Evidenza**: Confronto diretto tra FASE 3 e `src/infrastructure/config/scoring_config_loader.py` mostra pattern matching al 100%.

---

### 3. Degradazione Graziosa su Tutti i Livelli

**Cosa funziona**:
- pygame non disponibile → `_AudioManagerStub` (no crash)
- File WAV mancante → `None` in cache con warning log
- JSON corrotto → default hardcodati
- Identico al pattern di `TtsProvider` che gestisce assenza NVDA

**Evidenza**: Ogni fase del PLAN include gestione errore. Test strategy include `test_get_returns_none_when_wav_missing`.

---

### 4. Testing Strategy Headless Completa

**Cosa funziona**:
- Mock completo di `pygame.mixer` per CI/CD
- 17 unit test coprono tutti i componenti principali
- Marker `@pytest.mark.unit` per esclusione GUI
- Success criteria funzionali e tecnici ben definiti

**Evidenza**: Sezione "Testing Strategy" include fixture `mock_pygame_mixer` e lista completa test con checkbox.

---

### 5. Commit Strategy Atomica

**Cosa funziona**:
- 10 commit atomici indipendenti
- Primo commit è zero-impact (solo dipendenze)
- Ultimo commit è test + docs (non rompe nulla)
- Conventional commits con scope coerenti

**Evidenza**: Sezione "Commit Strategy" mostra progressione safe. Pattern identico a feature complesse passate nel progetto.

---

## 🔴 PROBLEMA CRITICO #1: Formula Panning Stereo Errata

### Severità: 🔴 CRITICA

### Posizione nel Documento

**File**: `PLAN_audio_system_v3.4.0.md`  
**Sezione**: FASE 5 - SoundMixer  
**Sottosezione**: "Calcolo panning per canale stereo"  
**Righe**: Circa 450-460 (nel blocco codice `_apply_panning`)

---

### Descrizione del Problema

La formula proposta per applicare panning stereo tramite `channel.set_volume(left, right)` è:

```python
left  = max(0.0, min(1.0, (1.0 - panning) / 2.0))
right = max(0.0, min(1.0, (1.0 + panning) / 2.0))
```

Questa formula è matematicamente corretta per un **bilanciamento lineare classico**, ma ha un effetto collaterale indesiderato: quando `panning = 0.0` (centro), produce `left = 0.5` e `right = 0.5`. Questo significa che il suono al centro viene riprodotto a **metà del volume massimo**.

**Test numerico**:
- `panning = -1.0` (estrema sinistra) → `left = 1.0, right = 0.0` ✅ corretto
- `panning = 0.0` (centro) → `left = 0.5, right = 0.5` ❌ **VOLUME TOTALE DIMEZZATO**
- `panning = +1.0` (estrema destra) → `left = 0.0, right = 1.0` ✅ corretto

Per l'utente, questo si traduce in: i suoni delle pile centrali (Tableau 3-4, Fondazioni) sono percepiti come **troppo bassi** rispetto alle pile ai lati. Questo è un problema di UX grave per un sistema audio accessibile dove il volume deve essere uniforme.

---

### Soluzione Proposta

Sostituire la formula con una **constant-power pan law**, che mantiene il volume totale percepito costante indipendentemente dalla posizione stereo.

**Opzione 1: Linear Constant-Power (più semplice, raccomandato)**

```python
def _apply_panning(channel: pygame.mixer.Channel, panning: float) -> None:
    """Applica panning stereo al canale con constant-power pan law.
    
    Args:
        channel: pygame.mixer.Channel
        panning: float -1.0 (sinistra) ... +1.0 (destra)
    
    Formula:
        - Quando panning < 0 (sinistra): left=1.0, right ridotto proporzionalmente
        - Quando panning > 0 (destra): right=1.0, left ridotto proporzionalmente
        - Quando panning = 0 (centro): left=1.0, right=1.0 (volume massimo)
    
    Questa formula mantiene il volume percepito costante su tutto lo spettro stereo.
    """
    if panning < 0.0:  # Suono spostato verso sinistra
        left = 1.0
        right = 1.0 + panning  # panning negativo riduce right (es. -0.5 → right=0.5)
    else:  # Suono spostato verso destra (o centro se panning=0)
        left = 1.0 - panning   # panning positivo riduce left (es. +0.5 → left=0.5)
        right = 1.0
    
    # Clamp per sicurezza (dovrebbe essere già in range, ma previene errori)
    left = max(0.0, min(1.0, left))
    right = max(0.0, min(1.0, right))
    
    channel.set_volume(left, right)
```

**Opzione 2: Trigonometric Constant-Power (smooth curve, opzionale)**

```python
import math

def _apply_panning(channel: pygame.mixer.Channel, panning: float) -> None:
    """Applica panning stereo con curva sinusoidale (smooth constant-power).
    
    Args:
        channel: pygame.mixer.Channel
        panning: float -1.0 (sinistra) ... +1.0 (destra)
    
    Formula:
        Usa sin/cos per creare una transizione smooth che preserva l'energia totale.
        Matematicamente più accurata per percezione umana.
    """
    # Mappa panning [-1, +1] su angolo [0, π/2]
    angle = (panning + 1.0) * math.pi / 4.0
    
    left = math.cos(angle)
    right = math.sin(angle)
    
    channel.set_volume(left, right)
```

**Raccomandazione**: Usare **Opzione 1** per la prima implementazione. È più semplice da debuggare e il comportamento è prevedibile. L'Opzione 2 può essere una feature futura se si vuole una transizione ancora più smooth.

---

### Motivazione

La constant-power pan law è lo **standard de facto** nei sistemi audio professionali (DAW, game engines, librerie audio) proprio per evitare il problema del volume ridotto al centro. Pygame.mixer non la applica automaticamente perché `set_volume(left, right)` è una API low-level che dà controllo totale al programmatore.

Per un gioco accessibile dove l'audio è un canale informativo critico, avere un volume percepito uniforme è **essenziale**. L'utente non vedente non deve dover compensare mentalmente per pile centrali "più silenziose".

**Riferimenti tecnici**:
- [Constant Power Panning - Sound on Sound](https://www.soundonsound.com/techniques/stereo-panning-laws)
- [Audio Pan Laws Comparison](https://www.cs.cmu.edu/~music/icm-online/readings/panlaws/)

---

## 🟠 PROBLEMA #2: `pile_panning` Hardcoded in JSON (Anti-Pattern)

### Severità: 🟠 ALTA

### Posizione nel Documento

**File**: `PLAN_audio_system_v3.4.0.md`  
**Sezione**: FASE 3 - AudioConfig dataclass e AudioConfigLoader  
**Sottosezione**: `config/audio_config.json` - schema completo  
**Righe**: Circa 300-320 (blocco JSON con `pile_panning`)

---

### Descrizione del Problema

Lo schema JSON proposto include un dizionario `pile_panning` con 13 valori hardcodati:

```json
"pile_panning": {
  "tableau_0": -1.0,
  "tableau_1": -0.67,
  "tableau_2": -0.33,
  "tableau_3": 0.0,
  "tableau_4": 0.33,
  "tableau_5": 0.67,
  "tableau_6": 1.0,
  "foundation_0": 0.42,
  "foundation_1": 0.58,
  "foundation_2": 0.75,
  "foundation_3": 0.92,
  "stock": 0.83,
  "waste": 1.0
}
```

Questi valori sono il **risultato della formula** `panning = (pile_index / 12) * 2.0 - 1.0` già calcolati e persistiti. Questo crea diversi problemi:

1. **Duplicazione della logica**: La formula esiste nel codice E nel JSON. Se la formula cambia (es. curva non lineare futura), il JSON diventa obsoleto ma l'utente non lo sa.
2. **Manutenibilità**: Aggiungere una nuova pila richiede calcolare manualmente il valore e modificare il JSON. Errore umano probabile.
3. **Confusione concettuale**: Il JSON dovrebbe contenere **configurazione utente** (preferenze, toggle), non **output di computazione** (valori derivati).
4. **Inflazione dimensione file**: 13 righe JSON per dati che possono essere calcolati in 1 riga di codice.

---

### Soluzione Proposta

**Rimuovere completamente** la sezione `pile_panning` dal JSON. Il calcolo del panning deve avvenire **dinamicamente** nell'`AudioManager` usando la formula hardcodata.

#### Modifica 1: `audio_config.json` - schema revisionato

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

**Nota**: Se in futuro serve personalizzazione avanzata del panning, si aggiunge un parametro **moltiplicatore** o **curva**, non i valori assoluti:

```json
"panning_curve": "linear",  // o "logarithmic", "exponential"
"panning_spread": 1.0       // moltiplicatore 0.0-2.0 per comprimere/espandere lo spread
```

#### Modifica 2: `AudioConfig` dataclass - rimuovere `pile_panning`

```python
@dataclass
class AudioConfig:
    version: str = "1.0"
    active_sound_pack: str = "default"
    bus_volumes: Dict[str, int] = field(default_factory=lambda: {...})
    bus_muted: Dict[str, bool] = field(default_factory=lambda: {...})
    # RIMOSSO: pile_panning
    mixer_params: Dict[str, int] = field(default_factory=lambda: {...})
```

#### Modifica 3: `AudioManager._get_panning_for_event()` - calcolo dinamico

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
        - pile_index 6 (Tableau 7) → +0.0 (centro)
        - pile_index 12 (Waste) → +1.0 (estrema destra)
    """
    pile_index = event.destination_pile if event.destination_pile is not None else event.source_pile
    
    if pile_index is None:
        return 0.0  # Default al centro per eventi senza posizione spaziale
    
    # Formula lineare
    panning = (pile_index / 12.0) * 2.0 - 1.0
    
    # Clamp per sicurezza (dovrebbe essere già in range 0-12, ma previene errori)
    return max(-1.0, min(1.0, panning))
```

---

### Motivazione

Questa modifica segue il principio **DRY (Don't Repeat Yourself)** e il pattern già usato nel progetto. Confronto con `scoring_config.json` esistente:

- `scoring_config.json` contiene **parametri di input** (`event_points`, `difficulty_multipliers`), non output calcolati.
- Il `ScoringEngine` **calcola** il punteggio finale usando questi parametri + logica hardcodata.
- Non esiste un campo `precalculated_scores` nel JSON.

Identico ragionamento si applica qui: `audio_config.json` deve contenere parametri di input (volumi, mute, pack), non output derivati (valori panning).

**Benefici**:
- Single source of truth per la formula panning
- JSON più leggibile e compatto
- Zero rischio di desincronizzazione formula/JSON
- Aggiungere pile future non richiede toccare il JSON

---

## 🟡 PROBLEMA #3: Eventi Timer Definiti ma Mai Emessi

### Severità: 🟡 MEDIA

### Posizione nel Documento

**File**: `PLAN_audio_system_v3.4.0.md`  
**Sezione**: FASE 2 - AudioEvent dataclass  
**Sottosezione**: `AudioEventType` class  
**Righe**: Circa 220-240 (costanti `TIMER_WARNING`, `TIMER_EXPIRED`)

---

### Descrizione del Problema

Il PLAN definisce due costanti per eventi timer:

```python
# Timer events
TIMER_WARNING = "timer_warning"
TIMER_EXPIRED = "timer_expired"
```

E li mappa a file audio nella FASE 4 (SoundCache):

```python
AudioEventType.TIMER_WARNING:       "ui/navigate.wav",
AudioEventType.TIMER_EXPIRED:       "ui/cancel.wav",
```

**Tuttavia**, la FASE 8 (Application Layer - integrazione AudioEvent) **non specifica dove questi eventi vengono emessi**. Il problema è che il `TimerManager` è un servizio puro del layer Application che non ha accesso diretto all'`AudioManager` (nessuna dipendenza tra servizi nello stesso layer).

**Conseguenza**: Gli eventi timer sono definiti, mappati a suoni, ma **nessun codice li emette mai**. Rimarrebbero dead code.

---

### Soluzione Proposta

Integrare l'emissione degli eventi timer nel `GamePlayController`, che è l'unico punto che collega il `TimerManager` (servizio Application) con l'`AudioManager` (servizio Infrastructure via DI).

#### Modifica nella FASE 8: GamePlayController - callback timer

Aggiungere alla sottosezione "GamePlayController" questa specifica:

---

**Integrazione Eventi Timer**

Il `GamePlayController` deve passare callback lambda al `TimerManager` per emettere `AudioEvent` quando il timer raggiunge soglie critiche.

```python
# In GamePlayController.__init__()
def __init__(
    self,
    engine: GameEngine,
    screen_reader,
    settings: Optional[GameSettings] = None,
    on_new_game_request: Optional[Callable[[], None]] = None,
    audio_manager: Optional[Any] = None,
    timer_manager: Optional[TimerManager] = None  # NEW v3.4.0 - ricevuto dal container
) -> None:
    ...
    self._audio = audio_manager
    
    # Configura callback timer per audio feedback
    if timer_manager and audio_manager:
        timer_manager.set_warning_callback(self._on_timer_warning)
        timer_manager.set_expired_callback(self._on_timer_expired)

def _on_timer_warning(self) -> None:
    """Callback chiamato dal TimerManager quando restano 60 secondi."""
    if self._audio:
        from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
        self._audio.play_event(AudioEvent(event_type=AudioEventType.TIMER_WARNING))

def _on_timer_expired(self) -> None:
    """Callback chiamato dal TimerManager quando il tempo scade."""
    if self._audio:
        from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
        self._audio.play_event(AudioEvent(event_type=AudioEventType.TIMER_EXPIRED))
```

**Nota**: Questo richiede che il `TimerManager` esponga i metodi `set_warning_callback()` e `set_expired_callback()`, che già esistono nel codice attuale (`warning_callback` è un parametro dell'`__init__`).

---

### Motivazione

Il pattern callback è già usato nel `TimerManager` esistente per notificare la UI. Estenderlo per l'audio è coerente con l'architettura. Alternativa sarebbe introdurre un EventBus globale, ma questo è già stato escluso nel DESIGN come overengineering.

Questo approccio rispetta la separazione layer:
- `TimerManager` (Application) non conosce `AudioManager` (Infrastructure)
- `GamePlayController` (Application) orchestra entrambi tramite DI
- Callback è il pattern standard per comunicazione tra servizi nello stesso layer

---

## 🟡 PROBLEMA #4: Comando `TOGGLE_AUDIO_MIXER` Mappato ma Senza Handler

### Severità: 🟡 MEDIA

### Posizione nel Documento

**File**: `PLAN_audio_system_v3.4.0.md`  
**Sezione**: FASE 8 - Application Layer  
**Sottosezione**: InputHandler.GameCommand  
**Righe**: Circa 600-610 (enum `TOGGLE_AUDIO_MIXER`)

---

### Descrizione del Problema

La FASE 8 aggiunge il nuovo comando al `GameCommand` enum:

```python
# Audio (v3.4.0)
TOGGLE_AUDIO_MIXER = auto()  # Tasto M
```

E il mapping tasto:

```python
pygame.K_m: GameCommand.TOGGLE_AUDIO_MIXER,
```

**Tuttavia**, non viene specificato dove questo comando viene **gestito**. L'`InputHandler` mappa il tasto al comando, ma il `GamePlayController` (che gestisce i comandi) deve avere un nuovo `elif` branch per chiamare il dialog del mixer.

**Conseguenza**: Il tasto `M` viene mappato ma premendolo non succede nulla. L'implementatore potrebbe non capire dove aggiungere la logica.

---

### Soluzione Proposta

Aggiungere esplicitamente nella FASE 8 la gestione del comando nel `GamePlayController`.

#### Modifica nella FASE 8: GamePlayController - handler comando mixer

Aggiungere alla sottosezione "GamePlayController" questa specifica:

---

**Gestione Comando TOGGLE_AUDIO_MIXER**

Il `GamePlayController` deve gestire il nuovo comando nel metodo che processa i comandi gameplay (probabilmente `_handle_gameplay_command()` o `_handle_command()`).

```python
# In GamePlayController._handle_gameplay_command() o equivalente
elif command == GameCommand.TOGGLE_AUDIO_MIXER:
    self._show_audio_mixer_dialog()

def _show_audio_mixer_dialog(self) -> None:
    """Apre il dialog AccessibleMixerDialog in modalità modale.
    
    Il dialog riceve l'AudioManager per leggere/modificare i volumi.
    Al termine, il dialog chiama audio_manager.save_settings().
    """
    if not self._audio or not self._audio.is_available:
        # Sistema audio non disponibile - notifica utente via TTS
        if self._screen_reader:
            self._screen_reader.speak("Sistema audio non disponibile", interrupt=True)
        return
    
    from src.presentation.dialogs.accessible_mixer_dialog import AccessibleMixerDialog
    
    # Il dialog necessita del frame parent per modalità modale
    # Assumiamo che GamePlayController abbia accesso al frame (da verificare nel codebase)
    dialog = AccessibleMixerDialog(
        parent=self._frame,  # o self._parent, dipende dalla struttura attuale
        audio_manager=self._audio
    )
    dialog.ShowModal()
    dialog.Destroy()
```

**Nota per implementatore**: Verificare come `GamePlayController` accede al frame parent. Potrebbe essere necessario passarlo tramite `__init__` se non già presente.

---

### Motivazione

Aggiungere questa specifica rende il PLAN completo e non ambiguo. L'implementatore sa esattamente:
1. Dove aggiungere il branch `elif`
2. Quale metodo creare (`_show_audio_mixer_dialog`)
3. Come gestire il caso audio non disponibile (degradazione graziosa)
4. Cosa fare con il dialog dopo ShowModal (Destroy per cleanup)

Questo evita "buchi" nel flusso di implementazione e riduce il rischio di interpretazioni errate.

---

## 🟡 PROBLEMA #5: `_AudioManagerStub` Referenziata ma Non Definita

### Severità: 🟡 BASSA

### Posizione nel Documento

**File**: `PLAN_audio_system_v3.4.0.md`  
**Sezioni**: FASE 7 (DIContainer integration) referenzia `_AudioManagerStub`, ma FASE 6 (AudioManager) non la definisce  
**Righe**: Circa 550 (FASE 7, blocco except) e assente in FASE 6

---

### Descrizione del Problema

La FASE 7 include questo codice nel `DIContainer.get_audio_manager()`:

```python
except Exception:
    # Degradazione graziosa: AudioManager stub (no-op)
    from src.infrastructure.audio.audio_manager import _AudioManagerStub
    self._instances["audio_manager"] = _AudioManagerStub()
```

Ma la FASE 6, che descrive il file `audio_manager.py`, **non include la definizione** di `_AudioManagerStub`. Questo crea ambiguità per l'implementatore: dove deve essere definita questa classe? Quali metodi deve avere?

---

### Problema #6: AudioManager creato ma mai usato in avvio

**Sezione**: FASE 7 (DIContainer) + FASE 8 (Application Layer)  

Dopo aver definito correttamente il singleton nel container, il documento non
spiega **quando e dove** l'applicazione lo ottiene e lo passa ai controller.
La logica di esempio per `acs_wx.py` manca. Di conseguenza, un'implementazione
iniziale completa può compilare e passare tutti i test, ma in esecuzione reale
nessun suono viene mai riprodotto perché `GamePlayController._audio` resta `None`.

#### Impatto

- Il codice audio esiste e funziona in isolamento, ma non è mai invocato.  
- L'utente lamenta «suoni non riprodotti» pur avendo seguito tutte le altre fasi.

#### Soluzione proposta

Aggiungere un paragrafo esplicativo in FASE 7, come già inserito nel piano:

```markdown
**Startup integration reminder**

Dopo aver implementato `get_audio_manager()` il codice dell'applicazione deve
ricordarsi di ottenere l'istanza, inizializzarla e passarla ai controller che
emetteranno eventi audio. Questo è il passaggio mancante durante i test
manuali: senza di esso il sistema è presente ma mai utilizzato.

Esempio da aggiungere in `acs_wx.py` o equivalentemente in `App.on_startup()`:

```python
# acs_wx.py (setup iniziale)
self.audio_manager = self.container.get_audio_manager()
self.audio_manager.initialize()

self.gameplay_controller = GamePlayController(
    engine=self.engine,
    screen_reader=self.screen_reader,
    settings=self.settings,
    on_new_game_request=self.show_new_game_dialog,
    audio_manager=self.audio_manager     # <<<<< pass it here
)
```

Allo stesso modo, se altri controller (es. `DialogManager`) ricevono l'audio
manager passare lo stesso oggetto.
```

---

### Soluzione Proposta

Aggiungere la definizione completa di `_AudioManagerStub` alla fine della FASE 6.

#### Modifica nella FASE 6: AudioManager - aggiungere stub class

Aggiungere alla fine della sezione "API pubblica richiesta" (dopo la classe `AudioManager`):

---

**Classe Stub per Degradazione Graziosa**

Se pygame.mixer non è disponibile (import error o init fallito), il `DIContainer` istanzia `_AudioManagerStub` invece di `AudioManager`. Lo stub implementa la stessa interfaccia pubblica ma tutti i metodi sono no-op.

```python
class _AudioManagerStub:
    """No-op stub per AudioManager quando pygame non è disponibile.
    
    Implementa la stessa interfaccia pubblica di AudioManager ma tutti
    i metodi sono no-op safe. Permette al resto del codice di chiamare
    audio_manager.play_event() senza crash anche se pygame manca.
    
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
    
    def play_event(self, event: AudioEvent) -> None:
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
# Controller code
if self._audio:  # None check
    self._audio.play_event(event)  # Safe: potrebbe essere stub, ma non crasha
```

**Alternative non raccomandate**:
- Usare `Optional[AudioManager]` e fare `if audio_manager is not None` ovunque → verboso
- Sollevare eccezione se pygame assente → viola degradazione graziosa

---

### Motivazione

Definire esplicitamente lo stub nella stessa fase che definisce `AudioManager` rende chiara la strategia di degradazione. L'implementatore sa:
1. Dove va la classe (stesso file `audio_manager.py`)
2. Quali metodi implementare (tutti quelli pubblici)
3. Cosa restituire (valori safe: False, 0, pass)

Questo è identico al pattern usato in `TtsProvider` del codebase esistente, dove ogni provider ha un fallback no-op se il motore TTS non è disponibile.

---

## � PROBLEMA #6: mappatura suoni non allineata agli asset reali

### Severità: 🟡 MEDIA

### Posizione nel Documento

**File**: `PLAN_audio_system_v3.4.0.md`  
**Sezione**: FASE 2 - AudioEvent dataclass & FASE 4 - SoundCache  
**Sottosezione**: definizione `AudioEventType` e dizionario `SOUND_FILES`  
**Righe**: numerose (event_type e mapping)

---

### Descrizione del Problema

La cartella `assets/sounds/default` contiene un elenco di file **reali** che supera e differisce rispetto ai nomi fittizi utilizzati nel piano. Esempi:

- Esistono `card_place.wav`, `tableau_drop.wav`, `card_shuffle.wav` e `card_shuffle_alt.wav` ma il `SOUND_FILES` mappa soltanto `card_move.wav` per tutti i movimenti.
- I suoni UI (`button_click.wav`, `menu_open.wav`, `error.wav`, `focus_change.wav`, `navigate_alt.wav`, `notification.wav`, `select.wav`, ecc.) non sono nemmeno rappresentati in `AudioEventType`.
- Alcune risorse (es. `card_move.wav`) vengono riutilizzate per eventi diversi (`AUTO_MOVE`) senza spiegazione, mentre varianti possibili non vengono sfruttate.

Di fatto, molte tracce audio rimarrebbero inutilizzate e l'implementazione rischia di ignorare risorse già disponibili; inoltre la denominazione degli eventi non corrisponde ai nomi dei file, creando confusione per i futuri manutentori.

---

### Soluzione Proposta

Allineare il piano agli asset reali:

- Estendere `AudioEventType` con costanti per i suoni aggiuntivi (card_place, tableau_drop, shuffle, UI_BUTTON_CLICK, UI_MENU_OPEN/ CLOSE, UI_ERROR, UI_FOCUS_CHANGE, UI_NAVIGATE_ALT, UI_NOTIFICATION, UI_SELECT, ecc.).
- Modificare `SOUND_FILES` in FASE 4 per usare i percorsi esatti e supportare liste di file per varianti. La classe `SoundCache` dovrà gestire un valore `Union[str, List[str]]` scegliendo un elemento a caso.
- Inserire una nota nella fase 4/5 riguardo alla “variazione dinamica dei timbri” e come implementarla (pick random) per sfruttare file multipli.
- Aggiungere ai requisiti funzionali una RF‑7 generica per feedback sonoro di eventi shuffle/menu/pulsanti, lasciando la possibilità di implementare il trigger in futuro.

Queste modifiche rendono il piano coerente con la struttura `assets/sounds/default` e garantiscono che nessuna traccia rimanga orphan.

---



Prima di procedere all'implementazione, applicare queste modifiche al PLAN:

- [ ] **CRITICO**: Correggere formula panning in FASE 5 (sostituire con constant-power pan law)
- [ ] **ALTO**: Rimuovere `pile_panning` da JSON in FASE 3 (calcolo dinamico in AudioManager)
- [ ] **MEDIO**: Aggiungere callback timer in FASE 8 GamePlayController
- [ ] **MEDIO**: Aggiungere handler `TOGGLE_AUDIO_MIXER` in FASE 8 GamePlayController
- [ ] **BASSO**: Definire `_AudioManagerStub` in FASE 6 AudioManager
- [ ] **MEDIO**: Riallineare mappatura suoni agli asset reali e aggiungere eventuali nuovi eventi

---

## 📊 Impatto delle Correzioni

### Effort Aggiuntivo Stimato

| Correzione | Effort | Impatto Implementazione |
|------------|--------|-------------------------|
| #1 Formula panning | 5 minuti | Modifica 1 metodo in SoundMixer |
| #2 Rimuovi pile_panning JSON | 10 minuti | Rimuovi sezione JSON + modifica AudioConfig + aggiungi metodo calcolo |
| #3 Callback timer | 15 minuti | Aggiungi 2 metodi in GamePlayController |
| #4 Handler mixer | 10 minuti | Aggiungi 1 metodo + elif branch |
| #5 Stub definition | 5 minuti | Copia classe stub in audio_manager.py |
| #6 Mappatura asset | 20 minuti | Aggiorna AudioEventType ed elenchi SOUND_FILES, aggiungi note varianti |
| **TOTALE** | **65 minuti** | Nessun impatto sulla commit strategy o testing |

Le correzioni sono tutte **localizzate** e non richiedono riscrittura di fasi intere. L'effort stimato originale (12-16 ore) rimane valido.

---

## ✅ Conclusione

Il PLAN `PLAN_audio_system_v3.4.0.md` è di **alta qualità strutturale** e dimostra ottima comprensione dell'architettura del progetto. Le 5 correzioni richieste sono tutte **risolvibili rapidamente** e non intaccano la validità complessiva del documento.

**Raccomandazione Finale**: Applicare le correzioni indicate (45 minuti di lavoro), poi procedere con l'implementazione seguendo l'ordine delle 10 fasi. Il PLAN così revisionato sarà **production-ready** e minimizzerà il rischio di ambiguità durante il coding.

---

**Review Version**: v1.1  
**Data Review**: 2026-02-22  
**Reviewer**: AI Assistant (analisi tecnica assistita)  
**Prossimo Step**: Applicare correzioni e aggiornare PLAN a versione v1.1 (READY FOR IMPLEMENTATION)
---

## 🔊 Mappatura Eventi → File Audio, Varianti e Opzioni

### Strategia di Mapping e Gestione Varianti

**1. Mappatura esplicita**: Ogni `AudioEventType` è mappato a una o più path di file WAV (solo WAV, no OGG/MP3) nella struttura `assets/sounds/default/`.
    - La mappatura è definita in una struttura Python (dict) e documentata qui e nel DESIGN.
    - Esempio: `CARD_MOVE` → `["gameplay/card_move_1.wav", "gameplay/card_move_2.wav"]`

**2. Varianti**: Se una lista di file è associata a un evento, la selezione è randomica tra le varianti disponibili (pattern: anti-ripetitività).

**3. Bus assignment**: Ogni evento è assegnato a un bus (`Gameplay`, `UI`, `Ambient`, `Music`, `Voice`) secondo tabella seguente.

**4. Eventi opzionali**: Alcuni eventi (es. `TIMER_WARNING`, `TIMER_EXPIRED`, `MIXER_OPENED`) sono disattivabili via config JSON (`audio_config.json`).

**5. Degradazione**: Se un file manca, warning nel log e nessun crash. Se nessuna variante disponibile, l'evento è silenziato.

### Tabella Mapping Eventi → File e Bus

| AudioEventType         | File(s) WAV (relativo a assets/sounds/default/)         | Bus        | Varianti | Note |
|-----------------------|--------------------------------------------------------|------------|----------|------|
| CARD_MOVE             | gameplay/card_move_1.wav, ..._2.wav, ..._3.wav         | Gameplay   | Sì (3)   | Random |
| CARD_SELECT           | gameplay/card_select.wav                               | Gameplay   | No       |       |
| CARD_DROP             | gameplay/card_drop.wav                                 | Gameplay   | No       |       |
| FOUNDATION_DROP       | gameplay/foundation_drop.wav                           | Gameplay   | No       |       |
| INVALID_MOVE          | gameplay/invalid_move.wav                              | Gameplay   | No       |       |
| TABLEAU_BUMPER        | gameplay/bumper.wav                                    | Gameplay   | No       |       |
| STOCK_DRAW            | gameplay/stock_draw.wav                                | Gameplay   | No       |       |
| WASTE_DROP            | gameplay/waste_drop.wav                                | Gameplay   | No       |       |
| UI_NAVIGATE           | ui/navigate.wav                                        | UI         | No       |       |
| UI_SELECT             | ui/select.wav                                          | UI         | No       |       |
| UI_CANCEL             | ui/cancel.wav                                          | UI         | No       |       |
| MIXER_OPENED          | ui/mixer_opened.wav                                    | UI         | No       | Opzionale |
| AMBIENT_LOOP          | ambient/room_loop.wav                                  | Ambient    | No       | Loop |
| MUSIC_LOOP            | music/music_loop.wav                                   | Music      | No       | Loop |
| GAME_WON              | voice/victory.wav                                      | Voice      | No       |       |
| TIMER_WARNING         | ui/navigate.wav                                        | UI         | No       | Opzionale |
| TIMER_EXPIRED         | ui/cancel.wav                                          | UI         | No       | Opzionale |

**Nota**: La lista completa e aggiornata dei file disponibili è mantenuta nel DESIGN e nel README. Eventuali nuovi eventi o varianti vanno aggiunti sia qui che nel mapping Python.

### Esempio di struttura mapping Python

```python
EVENT_TO_FILES = {
        AudioEventType.CARD_MOVE: [
                "gameplay/card_move_1.wav",
                "gameplay/card_move_2.wav",
                "gameplay/card_move_3.wav",
        ],
        AudioEventType.CARD_SELECT: ["gameplay/card_select.wav"],
        # ... altri eventi ...
}
```

### Gestione Varianti

- Se la lista associata a un evento contiene più file, la selezione è randomica (`random.choice`).
- Se la lista è vuota o tutti i file mancano, l'evento è silenziato (nessun errore).

### Eventi Opzionali e Configurazione

- Gli eventi marcati come "Opzionale" possono essere abilitati/disabilitati dall'utente tramite `audio_config.json`.
- Il loader carica la config e filtra gli eventi disabilitati a runtime.

### Bus Assignment e Policy

- Ogni evento è assegnato a un bus secondo la tabella sopra.
- I bus sono gestiti da `SoundMixer` e possono essere mutati/regolati indipendentemente.
- I bus loop (Ambient, Music) sono sospesi in pausa/focus out; i bus one-shot (Gameplay, UI, Voice) restano sempre attivi.

---
