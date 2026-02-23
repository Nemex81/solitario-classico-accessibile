# 🎯 PIANO DI CORREZIONE SISTEMA AUDIO v3.4.1

**Branch:** `supporto-audio-centralizzato`  
**Data Creazione:** 23 Febbraio 2026  
**Versione Target:** v3.4.1  
**Tipo:** Bug Fix + Refactoring  

---

## 📋 EXECUTIVE SUMMARY

### Problemi Identificati

#### Problema 1: Mismatch Mapping File Audio
- **Stato:** Sistema audio non riproduce suoni
- **Causa:** `SoundCache` cerca file inesistenti (es. `card_move_1.wav`, `card_select.wav`)
- **File Coinvolto:** `src/infrastructure/audio/sound_cache.py`
- **Impatto:** CRITICO - Nessun effetto sonoro nel gameplay

#### Problema 2: Logica Random Indesiderata
- **Stato:** Design prevede selezione casuale tra varianti (non implementato)
- **Causa:** `AudioManager.play_event()` contiene codice per `random.choice()`
- **Decisione:** Eliminare completamente questa logica dal design
- **File Coinvolto:** `src/infrastructure/audio/audio_manager.py`
- **Impatto:** MEDIO - Codice inutilizzato, complessità superflua

### Soluzione Proposta

**Design Definitivo:** Un evento = un suono fisso per pack. Nessuna variazione casuale.

**Principio:** La varietà sonora viene ottenuta **solo** tramite cambio sound pack (es. "default" → "retro"), non tramite randomizzazione per evento.

---

## 🔍 ANALISI DETTAGLIATA

### Stato Attuale File Audio

**Directory:** `assets/sounds/default/gameplay/`

```
✅ File Presenti:
- card_flip.wav
- card_move.wav               (1 file singolo)
- card_place.wav
- card_shuffle.wav
- card_shuffle_alt.wav
- foundation_drop.wav
- invalid_move.wav
- stock_draw.wav
- tableau_drop.wav

❌ File Mancanti (cercati erroneamente da SoundCache):
- card_move_1.wav, card_move_2.wav, card_move_3.wav
- card_select.wav
- card_drop.wav
- bumper.wav
- waste_drop.wav
```

### Mapping Attuale SoundCache (Errato)

**File:** `src/infrastructure/audio/sound_cache.py` (righe 28-48)

```python
EVENT_TO_FILES = {
    "card_move": ["gameplay/card_move_1.wav", "gameplay/card_move_2.wav", "gameplay/card_move_3.wav"],  # ❌
    "card_select": ["gameplay/card_select.wav"],   # ❌
    "card_drop": ["gameplay/card_drop.wav"],       # ❌
    "foundation_drop": ["gameplay/foundation_drop.wav"],  # ✅
    "invalid_move": ["gameplay/invalid_move.wav"],        # ✅
    "tableau_bumper": ["gameplay/bumper.wav"],     # ❌
    "stock_draw": ["gameplay/stock_draw.wav"],     # ✅
    "waste_drop": ["gameplay/waste_drop.wav"],     # ❌
    # ... (altri bus)
}
```

**Problemi:**
1. Struttura a liste anche per singolo file
2. File referenziati non esistono nel repository
3. Nomi file non corrispondono alla convenzione attuale

### Logica AudioManager (Da Rimuovere)

**File:** `src/infrastructure/audio/audio_manager.py` (righe 48-50)

```python
import random
sound = random.choice(sounds) if isinstance(sounds, list) else sounds
```

**Problema:** Codice progettato per selezione casuale, non necessario per design finale.

---

# Note di Integrazione

Il fix v3.4.1 si concentra esclusivamente sulla correzione del mapping dei file
audio e sulla rimozione della logica random. L'integrazione completa del sistema
audio nel container e nei controller (GamePlayController, InputHandler, DialogManager)
è documentata nel piano principale `PLAN_audio_system_v3.4.0.md`.

Per le modifiche infrastrutturali e i passaggi di iniezione, fare riferimento a
quella fonte; il presente documento non necessita di ulteriori modifiche in quell'area.

## 🛠️ MODIFICHE DETTAGLIATE

### MODIFICA 1: Refactoring SoundCache

**File:** `src/infrastructure/audio/sound_cache.py`

#### 1.1 Aggiornare Type Hints

**Posizione:** Riga 12 (dentro `__init__`)

```python
# ❌ PRIMA:
self._cache: Dict[str, Union[pygame.mixer.Sound, None, List[pygame.mixer.Sound]]] = {}

# ✅ DOPO:
self._cache: Dict[str, Optional[pygame.mixer.Sound]] = {}
```

**Rationale:** Cache contiene solo Sound singoli, mai liste.

---

#### 1.2 Semplificare EVENT_TO_FILES

**Posizione:** Righe 28-48 (dentro `load_pack()`)

**Struttura Corretta:**

```python
def load_pack(self, pack_name: str) -> None:
    """Carica tutti i WAV del pack in RAM come pygame.Sound.
    
    Design v3.4.1: Un evento = un file WAV fisso per pack.
    Nessuna selezione casuale tra varianti.
    
    Args:
        pack_name: Nome del pack da caricare (es. "default")
    
    Degradazione graziosa: File assenti → warning nel log, entry None.
    """
    self._cache.clear()
    self._pack_name = pack_name
    pack_path = self.sounds_base_path / pack_name
    
    # Mapping evento → file WAV singolo
    # Design: Un suono fisso per evento. Varianti solo via cambio pack.
    EVENT_TO_FILES = {
        # ========================================
        # GAMEPLAY BUS
        # ========================================
        "card_move": "gameplay/card_move.wav",
        "card_select": "gameplay/card_place.wav",      # Riusa card_place (semanticamente simile)
        "card_drop": "gameplay/card_place.wav",        # Riusa card_place (azione di posare)
        "foundation_drop": "gameplay/foundation_drop.wav",
        "invalid_move": "gameplay/invalid_move.wav",
        "tableau_bumper": "gameplay/invalid_move.wav", # Riusa invalid_move (feedback errore)
        "stock_draw": "gameplay/stock_draw.wav",
        "waste_drop": "gameplay/tableau_drop.wav",     # Riusa tableau_drop (drop generico)
        
        # ========================================
        # UI BUS
        # ========================================
        "ui_navigate": "ui/navigate.wav",
        "ui_select": "ui/select.wav",
        "ui_cancel": "ui/cancel.wav",
        "mixer_opened": "ui/mixer_opened.wav",
        
        # ========================================
        # AMBIENT BUS
        # ========================================
        "ambient_loop": "ambient/room_loop.wav",
        
        # ========================================
        # MUSIC BUS
        # ========================================
        "music_loop": "music/music_loop.wav",
        
        # ========================================
        # VOICE BUS
        # ========================================
        "game_won": "voice/victory.wav",
        
        # ========================================
        # TIMER EVENTS
        # ========================================
        "timer_warning": "ui/navigate.wav",
        "timer_expired": "ui/cancel.wav",
    }
    
    # Carica ogni file WAV singolo
    for event_type, rel_path in EVENT_TO_FILES.items():
        file_path = pack_path / rel_path
        try:
            sound = pygame.mixer.Sound(str(file_path))
            self._cache[event_type] = sound  # Salva direttamente (non lista)
            _game_logger.debug(f"Loaded sound: {event_type} → {rel_path}")
        except Exception as e:
            _game_logger.warning(f"Sound asset missing: {file_path} (event: {event_type})")
            self._cache[event_type] = None
```

**Differenze Chiave:**
- Dizionario da `Dict[str, List[str]]` a `Dict[str, str]`
- Loop semplificato: un file per evento, caricamento diretto
- Rimozione logica varianti multiple
- Riuso strategico di file esistenti per eventi simili

---

#### 1.3 Aggiornare Metodo get()

**Posizione:** Riga 60

```python
# ❌ PRIMA:
def get(self, event_type: str) -> Optional[Union[pygame.mixer.Sound, List[pygame.mixer.Sound]]]:
    """Restituisce il Sound pre-caricato per il tipo evento, o None se assente."""
    return self._cache.get(event_type)

# ✅ DOPO:
def get(self, event_type: str) -> Optional[pygame.mixer.Sound]:
    """Restituisce il Sound pre-caricato per il tipo evento, o None se assente.
    
    Returns:
        pygame.mixer.Sound singolo (design v3.4.1: nessuna lista)
    """
    return self._cache.get(event_type)
```

---

### MODIFICA 2: Semplificare AudioManager

**File:** `src/infrastructure/audio/audio_manager.py`

#### 2.1 Refactoring play_event()

**Posizione:** Righe 47-65

```python
# ❌ PRIMA:
def play_event(self, event: AudioEvent) -> None:
    """Riproduce il suono associato all'evento con panning spaziale."""
    if not self._initialized:
        return
    
    sounds = self.sound_cache.get(event.event_type)
    if sounds is None:
        return
    
    # Gestione varianti: se lista, seleziona random
    import random
    sound = random.choice(sounds) if isinstance(sounds, list) else sounds
    
    if sound is None:
        return
    
    panning = self._get_panning_for_event(event)
    bus_name = self._get_bus_for_event(event.event_type)
    self.sound_mixer.play_one_shot(sound, bus_name, panning)

# ✅ DOPO:
def play_event(self, event: AudioEvent) -> None:
    """Riproduce il suono associato all'evento con panning spaziale.
    
    Design v3.4.1: Un evento = un suono fisso per pack.
    Nessuna selezione casuale. Varianti solo via cambio pack.
    
    Args:
        event: AudioEvent con tipo evento e metadata spaziale
    """
    if not self._initialized:
        _game_logger.debug(f"AudioManager not initialized, skipping event: {event.event_type}")
        return
    
    sound = self.sound_cache.get(event.event_type)
    if sound is None:
        _game_logger.warning(f"No sound mapped for event: {event.event_type}")
        return
    
    # Calcola panning stereo basato su posizione pile (0-12)
    panning = self._get_panning_for_event(event)
    
    # Determina bus audio (gameplay/ui/ambient/music/voice)
    bus_name = self._get_bus_for_event(event.event_type)
    
    # Riproduzione immediata (one-shot) sul bus appropriato
    self.sound_mixer.play_one_shot(sound, bus_name, panning)
    
    _game_logger.debug(
        f"Played event: {event.event_type} → bus: {bus_name}, panning: {panning:.2f}"
    )
```

**Differenze Chiave:**
- ❌ Rimosso: `import random`, `random.choice()`
- ❌ Rimosso: Check `isinstance(sounds, list)`
- ✅ Aggiunto: Logging dettagliato per debug
- ✅ Semplificato: `sound` è sempre `pygame.mixer.Sound` o `None`
- ✅ Documentazione: Esplicita assenza randomizzazione

---

### MODIFICA 3: Aggiornare Documentazione

**File:** `docs/2 - projects/DESIGN_audio_system.md`

#### 3.1 Aggiungere Sezione Design Varianti

**Posizione:** Dopo "## 6. SoundTimbre: Gestione Caricamento Asset Audio" (circa riga 127)

```markdown
### 6.4 Gestione Suoni per Evento

**Design Definitivo (v3.4.1): Un Evento = Un Suono Fisso per Pack**

Il sistema audio **non implementa selezione casuale** tra varianti.
Ogni evento ha **un solo file WAV** associato nel pack attivo.

#### Principio Architetturale

```
Evento Audio → Sound Pack → File WAV singolo → Riproduzione
              ↓
       (Unico punto di variazione)
```

**Esempio:**

```
Pack "default":
  card_move → assets/sounds/default/gameplay/card_move.wav (suono legno)

Pack "retro":
  card_move → assets/sounds/retro/gameplay/card_move.wav (suono 8-bit)

Pack "luxury":
  card_move → assets/sounds/luxury/gameplay/card_move.wav (suono cristallo)
```

Spostare una carta riproduce **sempre** lo stesso suono all'interno del pack attivo.
Per cambiare suono, l'utente cambia pack (via settings o `audio_config.json`).

#### Rationale

1. **Consistenza UX**
   - Il giocatore sviluppa associazioni mentali forti: "Questo suono = Questa azione"
   - Comportamento predittivo migliora l'esperienza di gioco
   - Fondamentale per utenti non vedenti che si affidano a feedback sonoro coerente

2. **Accessibilità**
   - Variazioni casuali possono generare confusione o incertezza sull'esito azione
   - Feedback deterministico facilita apprendimento pattern di gioco
   - Screen reader users beneficiano di ambiente sonoro stabile

3. **Semplicità Implementativa**
   - Mapping diretto evento → file (no logica condizionale)
   - Debugging facilitato (sempre lo stesso output per stesso input)
   - Test automatizzati possono verificare suono atteso

4. **Manutenibilità**
   - Sound pack developers creano un file per evento (no varianti obbligatorie)
   - Struttura directory semplificata
   - Caricamento RAM ridotto (1 file vs 3+ varianti)

#### Implementazione Cambio Pack

```python
# In runtime (via settings UI o API):
audio_manager = container.get_audio_manager()
audio_manager.load_sound_pack("retro")

# In configurazione (persistente):
# config/audio_config.json
{
    "active_sound_pack": "retro",
    "sounds_path": "assets/sounds"
}
```

#### Riuso File Audio

Per ottimizzare asset, eventi semanticamente simili condividono file:

| Evento | File Usato | Rationale |
|--------|-----------|-----------|
| `card_select` | `card_place.wav` | Selezionare = iniziare a posare |
| `card_drop` | `card_place.wav` | Drop = azione di posare |
| `tableau_bumper` | `invalid_move.wav` | Bumper = feedback errore |
| `waste_drop` | `tableau_drop.wav` | Drop generico pile |

Questo riduce duplicazione asset mantenendo consistenza semantica.

#### Decisione Architetturale: No Random

**Deprecato:** Il concetto di "varianti multiple con selezione casuale" è stato **escluso dal design** nella v3.4.1.

**Motivo:** Non allineato con obiettivi di accessibilità e consistenza UX.

**Se necessario in futuro:** Implementare come feature opt-in per pack specifici (es. pack "variety" con flag dedicato), non come comportamento default.
```

---

#### 3.2 Aggiornare Changelog Interno

**Posizione:** Alla fine del documento

```markdown
## Changelog Tecnico

### v3.4.1 (2026-02-23)

#### Fixed
- **[CRITICAL]** Allineato mapping eventi audio a file esistenti in `assets/sounds/default/`
- Rimossi riferimenti a file inesistenti (`card_move_1.wav`, `card_select.wav`, `bumper.wav`, `waste_drop.wav`)

#### Changed
- **[BREAKING]** Rimossa logica selezione casuale da `AudioManager.play_event()`
- **[BREAKING]** `SoundCache.get()` ora restituisce solo `pygame.mixer.Sound`, mai liste
- **[BREAKING]** Semplificato `SoundCache.EVENT_TO_FILES`: da `Dict[str, List[str]]` a `Dict[str, str]`
- Type hints aggiornati: `self._cache` ora è `Dict[str, Optional[pygame.mixer.Sound]]`

#### Rationale
- Migliore consistenza UX per accessibilità (utenti non vedenti)
- Comportamento deterministico semplifica debugging e testing
- Eliminata complessità superflua (codice random mai utilizzato)
- Design definitivo: varianti audio solo via cambio pack, non randomizzazione

#### Migration Guide
Nessuna azione richiesta per codice esistente. Le modifiche sono interne al layer Infrastructure.
Sound pack developers: creare un file WAV per evento (no varianti multiple necessarie).
```

---

### MODIFICA 4: Verifica Asset Altri Bus

**Action Item:** Controllare esistenza file audio per UI/Ambient/Music/Voice bus.

### MODIFICA 5: Aggiunta Test Unitari

**Obiettivo:** Coprire i cambiamenti introdotti con test automatici per preservare la qualità e la copertura.

**File interessati:**
- `tests/infrastructure/audio/test_sound_cache.py`
- `tests/infrastructure/audio/test_audio_manager.py`

**Contenuti suggeriti:**

1. `test_sound_cache_get_returns_sound_or_none()`:
   - Creare una cache temporanea con pack `default`.
   - Mockare `pygame.mixer.Sound` per evitare dipendenze audio.
   - Verificare che `get()` ritorni un `pygame.mixer.Sound` o `None`, **mai** una lista.
   - Simulare file mancante e vedere che logga warning (usare caplog).

2. `test_audio_manager_play_event_no_random()`:
   - Inizializzare un `AudioManager` con una `SoundCache` stub.
   - Chiamare `play_event()` con evento noto.
   - Assicurare che il metodo non importi `random` (grep) e che il sound mixer venga chiamato con il suono esatto.
   - Utilizzare un mock per `sound_mixer.play_one_shot` e verificare argomenti.

**Verifica Copertura:**
- Eseguire `pytest tests/infrastructure/audio/ --cov=src/infrastructure/audio` per confermare nuove linee coperte e che la copertura rimanga ≥ 85 %.


#### 4.1 Script di Verifica

```bash
#!/bin/bash
# Script: verify_audio_assets.sh
# Verifica esistenza file audio per tutti i bus

echo "=== VERIFICA ASSET AUDIO ==="
echo ""
MISSING=0

echo "📁 GAMEPLAY BUS:"
for f in card_move card_place foundation_drop invalid_move stock_draw tableau_drop; do
    if [ -f "assets/sounds/default/gameplay/$f.wav" ]; then
        echo "  ✅ $f.wav"
    else
        echo "  ❌ $f.wav MANCANTE"
        ((MISSING++))
    fi
done

echo ""
echo "📁 UI BUS:"
for f in navigate select cancel mixer_opened; do
    if [ -f "assets/sounds/default/ui/$f.wav" ]; then
        echo "  ✅ $f.wav"
    else
        echo "  ❌ $f.wav MANCANTE"
        ((MISSING++))
    fi
done

echo ""
echo "📁 AMBIENT BUS:"
if [ -f "assets/sounds/default/ambient/room_loop.wav" ]; then
    echo "  ✅ room_loop.wav"
else
    echo "  ❌ room_loop.wav MANCANTE"
    ((MISSING++))
fi

echo ""
echo "📁 MUSIC BUS:"
if [ -f "assets/sounds/default/music/music_loop.wav" ]; then
    echo "  ✅ music_loop.wav"
else
    echo "  ❌ music_loop.wav MANCANTE"
    ((MISSING++))
fi

echo ""
echo "📁 VOICE BUS:"
if [ -f "assets/sounds/default/voice/victory.wav" ]; then
    echo "  ✅ victory.wav"
else
    echo "  ❌ victory.wav MANCANTE"
    ((MISSING++))
fi

echo ""
echo "========================================="
if [ $MISSING -eq 0 ]; then
    echo "✅ Tutti gli asset audio sono presenti"
    exit 0
else
    echo "⚠️  $MISSING file mancanti"
    echo "Aggiorna EVENT_TO_FILES per riusare file esistenti"
    exit 1
fi
```

#### 4.2 Gestione File Mancanti

**Se lo script rileva file mancanti:**

**Opzione A (Raccomandato):** Aggiornare mapping per riusare file esistenti simili

**Opzione B:** Creare placeholder silenziosi temporanei:
```bash
# Genera file WAV silenzioso 0.5s
ffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t 0.5 -q:a 9 -acodec pcm_s16le placeholder.wav
```

---

## 📝 IMPLEMENTAZIONE STEP-BY-STEP

### Step 1: Preparazione Ambiente

```bash
# Verifica branch attivo
git branch --show-current
# Output atteso: supporto-audio-centralizzato

# Verifica stato pulito
git status
# Output atteso: nothing to commit, working tree clean

# (Opzionale) Crea branch di lavoro per sicurezza
git checkout -b fix/audio-system-v3.4.1

# Pull latest changes
git pull origin supporto-audio-centralizzato
```

---

### Step 2: Verifica Asset Audio

```bash
# Esegui script di verifica
chmod +x verify_audio_assets.sh
./verify_audio_assets.sh

# Se file mancanti, annota quali
# Decidi strategia (Opzione A: riuso, o Opzione B: placeholder)
```

---

### Step 3: Modifica SoundCache

**File:** `src/infrastructure/audio/sound_cache.py`

1. Apri file in VS Code
2. Applica modifiche 1.1, 1.2, 1.3 (vedi sezione MODIFICA 1)
3. Salva file (Ctrl+S)

**Test Rapido:**
```python
# In Python REPL (dalla root progetto)
from pathlib import Path
import pygame
pygame.mixer.init()

from src.infrastructure.audio.sound_cache import SoundCache

cache = SoundCache(Path("assets/sounds"))
cache.load_pack("default")

# Verifica tipo restituito
sound = cache.get("card_move")
print(type(sound))  # Deve essere <class 'pygame.mixer.Sound'> o NoneType

# Verifica nessuna lista
assert not isinstance(sound, list), "ERRORE: get() restituisce lista!"
print("✅ Test SoundCache.get() passato")
```

---

### Step 4: Modifica AudioManager

**File:** `src/infrastructure/audio/audio_manager.py`

1. Apri file in VS Code
2. Applica modifica 2.1 (vedi sezione MODIFICA 2)
3. Salva file (Ctrl+S)

**Verifica Rimozione Random:**
```bash
# Cerca residui di random
grep -n "random" src/infrastructure/audio/audio_manager.py

# Output atteso: NESSUN MATCH
# (O solo nei commenti docstring se presenti)
```

---

### Step 5: Aggiorna Documentazione

**File:** `docs/2 - projects/DESIGN_audio_system.md`

1. Apri file in VS Code
2. Applica modifiche 3.1, 3.2 (vedi sezione MODIFICA 3)
3. Salva file (Ctrl+S)

**Verifica Formato:**
```bash
# Controlla sintassi Markdown (opzionale)
markdownlint docs/2\ -\ projects/DESIGN_audio_system.md
```

---

### Step 6: Test Funzionale Completo

```bash
# Avvia il gioco
python acs_wx.py
```

**Test Checklist:**

```
[ ] Gioco si avvia senza warning "Sound asset missing" nel log
[ ] Nuova partita avviata
[ ] Sposta carta 3 volte consecutive → Stesso suono ogni volta ✅
[ ] Pesca dal mazzo (Spazio su stock) → Suono "stock_draw" riprodotto ✅
[ ] Mossa invalida → Suono "invalid_move" riprodotto ✅
[ ] Carta su fondazione → Suono "foundation_drop" riprodotto ✅
[ ] Panning stereo funzionante (carta sinistra → audio left, destra → audio right) ✅
[ ] Controlli volume bus indipendenti (se implementato mixer UI) ✅
[ ] *(nuovo)* Test unitari aggiunti ed eseguiti (SoundCache, AudioManager)
```

# Esegui i test unitari appena creati
```
pytest tests/infrastructure/audio/ --cov=src/infrastructure/audio
```
Assicurati che i due nuovi casi siano passati e la copertura resti ≥ 85 %.

**Controlla Log:**
```bash
# Cerca warning nel log
grep "WARNING" logs/game.log | grep -i "sound"

# Output atteso: NESSUN MATCH (o solo per bus non ancora implementati)
```

---

### Step 7: Type Check & Linting

```bash
# Type check con mypy
mypy src/infrastructure/audio/

# Output atteso: Success: no issues found

# Linting con black (opzionale)
black src/infrastructure/audio/

# Linting con flake8 (opzionale)
flake8 src/infrastructure/audio/ --max-line-length=100
```

---

### Step 8: Commit & Push

```bash
# Verifica modifiche
git diff

# Aggiungi file modificati
git add src/infrastructure/audio/sound_cache.py
git add src/infrastructure/audio/audio_manager.py
git add docs/2\ -\ projects/DESIGN_audio_system.md
git add docs/3\ -\ coding\ plans/PLAN_audio_system_fix_v3.4.1.md  # Questo piano

# Commit con messaggio strutturato
git commit -m "fix(audio): Align sound mapping to existing files, remove unused random logic

BREAKING CHANGES:
- SoundCache.get() now returns single Sound, never List[Sound]
- EVENT_TO_FILES changed from Dict[str, List[str]] to Dict[str, str]
- AudioManager.play_event() no longer contains random selection code

Fixes:
- Aligned sound event mapping to existing files in assets/sounds/default/
- Removed references to non-existent files (card_move_1.wav, card_select.wav, etc.)
- Eliminated unused import random and random.choice() logic

Design:
- Definitive design: one event = one fixed sound per pack
- Sound variety via pack switching only, no per-event randomization
- Improved UX consistency for accessibility (blind users)

Version: v3.4.1
Closes: #[issue_number_if_exists]"

# Push (se branch separato)
git push origin fix/audio-system-v3.4.1

# Oppure merge diretto su supporto-audio-centralizzato
git checkout supporto-audio-centralizzato
git merge fix/audio-system-v3.4.1
git push origin supporto-audio-centralizzato
```

---

## ✅ CRITERI DI ACCETTAZIONE

### Funzionali

- [ ] Sistema audio riproduce effetti sonori correttamente
- [ ] Ogni evento audio riproduce **sempre lo stesso suono** (nessuna casualità)
- [ ] File audio esistenti mappati correttamente
- [ ] Nessun warning "Sound asset missing" nel log per eventi gameplay attivi
- [ ] Panning stereo funzionante (pile sinistra → audio left, destra → audio right)
- [ ] Volume bus indipendenti controllabili (se UI mixer implementato)

### Tecnici

- [ ] `AudioManager.play_event()` non contiene `import random` o `random.choice()`
- [ ] `SoundCache.get()` type hint è `Optional[pygame.mixer.Sound]` (non Union con List)
- [ ] `SoundCache._cache` type hint è `Dict[str, Optional[pygame.mixer.Sound]]`
- [ ] `EVENT_TO_FILES` è `Dict[str, str]` (non `Dict[str, List[str]]`)
- [ ] `mypy src/infrastructure/audio/` passa senza errori
- [ ] Nessun import inutilizzato (verifica con flake8 F401)

### Documentazione

- [ ] `DESIGN_audio_system.md` aggiornato con sezione "Gestione Suoni per Evento"
- [ ] Changelog interno include v3.4.1 con BREAKING CHANGES
- [ ] Commenti codice espliciti su design deterministico (no random)
- [ ] Questo piano salvato in `docs/3 - coding plans/PLAN_audio_system_fix_v3.4.1.md`

### Testing

- [ ] Test manuale gameplay: tutti gli effetti sonori riproducono
- [ ] Test deterministico: stessa azione = stesso suono (3+ ripetizioni)
- [ ] Test unitari creati per SoundCache e AudioManager
- [ ] Test log: nessun warning inatteso
- [ ] Test type check: mypy passa

---

## 🎯 METRICHE DI SUCCESSO

| Metrica | Pre-Fix | Post-Fix |
|---------|---------|----------|
| File audio mancanti | ~7 | 0 |
| Warning log "Sound asset missing" | ~7 per avvio | 0 |
| Comportamento audio | Non funzionante | Deterministico |
| Type hint `SoundCache._cache` | `Union[Sound, None, List[Sound]]` | `Optional[Sound]` |
| Complessità `play_event()` | ~15 righe + random | ~12 righe |
| Import inutilizzati | `random` | 0 |
| Consistenza UX | N/A (non funzionante) | Alta |
| LOC `sound_cache.py` | ~70 | ~65 |

---

## 🔧 PROMPT PER COPILOT AGENT

```markdown
# TASK: Correzione Sistema Audio v3.4.1

## CONTESTO
Branch: supporto-audio-centralizzato
Problema 1: SoundCache cerca file audio inesistenti
Problema 2: AudioManager contiene logica random inutilizzata

## OBIETTIVO
Implementare design definitivo: un evento = un suono fisso per pack.
Eliminare completamente logica random (non necessaria).

## MODIFICHE RICHIESTE

### 1. src/infrastructure/audio/sound_cache.py

#### a) Riga 12 - Type hint cache
```python
self._cache: Dict[str, Optional[pygame.mixer.Sound]] = {}
```

#### b) Righe 28-56 - Refactoring load_pack()
Cambia EVENT_TO_FILES da Dict[str, List[str]] a Dict[str, str]:
```python
EVENT_TO_FILES = {
    # GAMEPLAY BUS
    "card_move": "gameplay/card_move.wav",
    "card_select": "gameplay/card_place.wav",
    "card_drop": "gameplay/card_place.wav",
    "foundation_drop": "gameplay/foundation_drop.wav",
    "invalid_move": "gameplay/invalid_move.wav",
    "tableau_bumper": "gameplay/invalid_move.wav",
    "stock_draw": "gameplay/stock_draw.wav",
    "waste_drop": "gameplay/tableau_drop.wav",
    
    # UI BUS
    "ui_navigate": "ui/navigate.wav",
    "ui_select": "ui/select.wav",
    "ui_cancel": "ui/cancel.wav",
    "mixer_opened": "ui/mixer_opened.wav",
    
    # AMBIENT BUS
    "ambient_loop": "ambient/room_loop.wav",
    
    # MUSIC BUS
    "music_loop": "music/music_loop.wav",
    
    # VOICE BUS
    "game_won": "voice/victory.wav",
    
    # TIMER EVENTS
    "timer_warning": "ui/navigate.wav",
    "timer_expired": "ui/cancel.wav",
}

for event_type, rel_path in EVENT_TO_FILES.items():
    file_path = pack_path / rel_path
    try:
        sound = pygame.mixer.Sound(str(file_path))
        self._cache[event_type] = sound
        _game_logger.debug(f"Loaded sound: {event_type} → {rel_path}")
    except Exception as e:
        _game_logger.warning(f"Sound asset missing: {file_path}")
        self._cache[event_type] = None
```

#### c) Riga 60 - Type hint get()
```python
def get(self, event_type: str) -> Optional[pygame.mixer.Sound]:
```

### 2. src/infrastructure/audio/audio_manager.py

#### Righe 47-65 - Refactoring play_event()
Rimuovi random.choice(), semplifica:
```python
def play_event(self, event: AudioEvent) -> None:
    """Riproduce il suono associato all'evento con panning spaziale.
    Design v3.4.1: Un evento = un suono fisso per pack.
    """
    if not self._initialized:
        _game_logger.debug(f"AudioManager not initialized, skipping: {event.event_type}")
        return
    
    sound = self.sound_cache.get(event.event_type)
    if sound is None:
        _game_logger.warning(f"No sound for event: {event.event_type}")
        return
    
    panning = self._get_panning_for_event(event)
    bus_name = self._get_bus_for_event(event.event_type)
    self.sound_mixer.play_one_shot(sound, bus_name, panning)
    _game_logger.debug(f"Played: {event.event_type} → {bus_name}, pan: {panning:.2f}")
```

### 3. docs/2 - projects/DESIGN_audio_system.md

Aggiungi dopo sezione "SoundTimbre" (riga ~127):
```markdown
### 6.4 Gestione Suoni per Evento

**Design Definitivo (v3.4.1): Un Evento = Un Suono Fisso per Pack**

Nessuna selezione casuale. Ogni evento ha un solo file WAV per pack.
Varianti solo via cambio pack (es. "default" → "retro").

Rationale:
- Consistenza UX per accessibilità
- Comportamento deterministico
- Eliminata complessità superflua
```

Aggiungi Changelog:
```markdown
### v3.4.1 (2026-02-23)
- Fixed: Allineato mapping audio a file esistenti
- Changed: Rimossa logica random da AudioManager
- Breaking: SoundCache.get() restituisce solo Sound singoli
```

## VINCOLI
- NON modificare audio_events.py, sound_mixer.py, audio_config.json
- NON toccare file nel filesystem assets/sounds/
- Mantieni degradazione graziosa (file mancante → None)
- Aggiungi logging debug dove appropriato

## VERIFICA POST-MODIFICA
```bash
grep -n "random" src/infrastructure/audio/audio_manager.py  # Nessun match
mypy src/infrastructure/audio/  # Success
python acs_wx.py  # Test: sposta carta 3x → stesso suono ogni volta
```

Committa con: "fix(audio): Align sound mapping, remove unused random logic v3.4.1"
```

---

## 📚 RIFERIMENTI

### File Coinvolti
- `src/infrastructure/audio/sound_cache.py` (Refactoring principale)
- `src/infrastructure/audio/audio_manager.py` (Rimozione random)
- `docs/2 - projects/DESIGN_audio_system.md` (Documentazione design)
- `docs/3 - coding plans/PLAN_audio_system_fix_v3.4.1.md` (Questo piano)

### Documentazione Collegata
- `docs/2 - projects/DESIGN_audio_system.md` (Design sistema completo)
- `docs/3 - coding plans/PLAN_audio_system_v3.4.0.md` (Piano implementazione iniziale)
- `docs/3 - coding plans/REVIEW_audio_system_v3.4.0.md` (Review implementazione)

### Issue/Discussion
- GitHub Issue: [Da creare se necessario]
- Discussion: Conversazione Perplexity del 23/02/2026

---

## 📋 CHECKLIST FINALE

```
PRE-IMPLEMENTAZIONE:
[ ] Branch supporto-audio-centralizzato attivo e aggiornato
[ ] Stato git pulito (git status → nothing to commit)
[ ] Asset audio verificati (script verify_audio_assets.sh eseguito)
[ ] Piano letto e compreso

IMPLEMENTAZIONE:
[ ] MODIFICA 1.1: Type hint _cache aggiornato
[ ] MODIFICA 1.2: EVENT_TO_FILES refactorato (Dict[str, str])
[ ] MODIFICA 1.3: Type hint get() aggiornato
[ ] MODIFICA 2.1: AudioManager.play_event() semplificato (no random)
[ ] MODIFICA 3.1: Documentazione design aggiornata
[ ] MODIFICA 3.2: Changelog interno scritto
[ ] Test funzionale: suoni riproducono correttamente
[ ] Test deterministico: stesso suono per stesso evento
[ ] Verifica log: nessun warning "missing file"
[ ] Verifica type check: mypy passa
[ ] Commit eseguito con messaggio strutturato
[ ] Push su remote branch

POST-IMPLEMENTAZIONE:
[ ] Test gameplay completo (checklist Step 6 completata)
[ ] Documentazione aggiornata su GitHub
[ ] Piano salvato in docs/3 - coding plans/
[ ] Issue chiuso (se esistente)
[ ] Team notificato (se necessario)
```

---

**Fine Piano v3.4.1** 🎵✅

---

## 📝 NOTE IMPLEMENTATIVE

### Nota 1: Riuso File Audio
La strategia di riuso file (es. `card_place.wav` per `card_select` e `card_drop`) è **intenzionale** e **temporanea**. Quando sound pack personalizzati saranno creati, ogni evento potrà avere il proprio file dedicato. Il riuso riduce duplicazione asset nella fase iniziale.

### Nota 2: Eliminazione Completa Random
A differenza di architetture che mantengono codice "per futuro uso", questo piano **elimina completamente** la logica random perché:
1. Non è necessaria per il design finale
2. Aggiunge complessità superflua
3. Confonde manutentori futuri
4. Viola YAGNI (You Aren't Gonna Need It)

Se randomizzazione sarà necessaria in futuro, verrà re-implementata come feature esplicita opt-in.

### Nota 3: Test Accessibilità
Questo fix è **critico per accessibilità**. Utenti non vedenti si affidano a feedback sonoro coerente. Test con NVDA attivo fortemente raccomandato prima di merge.
