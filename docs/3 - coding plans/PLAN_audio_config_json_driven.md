# PLAN Refactoring Audio Config JSON-Driven

**Branch:** `supporto-audio-centralizzato` → `refactor-audio-config-json`  
**Versione Target:** v3.4.x → v3.5.0  
**Tipo:** Refactoring / Technical Debt  
**Priorità:** MEDIUM (Quality of Life)  
**Stato:** READY FOR IMPLEMENTATION  

---

## 🎯 Executive Summary

Il sistema audio attuale richiede modifiche in **due punti separati** per cambiare un suono associato a un evento:
1. Dizionario hardcoded `_event_sounds` in `AudioManager.__init__()` (Python)
2. Array `preload_sounds` in `audio_config.json` (JSON)

Questo crea **duplicazione configurativa** con rischi di:
- ❌ Desincronizzazione (modifica uno, dimentichi l'altro)
- ❌ Maintenance overhead (doppio lavoro)
- ❌ Nessuna validazione automatica

**Obiettivo:** Spostare l'intero mapping `AudioEventType → filename` in `audio_config.json`, rendendo Python **JSON-driven** invece di hardcoded. Il file JSON diventa **Single Source of Truth** per tutta la configurazione audio.

**Benefici:**
- ✅ Modifica suoni senza toccare codice Python
- ✅ Configurabile senza ricompilare
- ✅ Validazione automatica con warning per eventi sconosciuti
- ✅ Base per future feature (hot-reload config, modding audio)

---

## 🔍 Scope

### In Scope
- Ristrutturazione `audio_config.json` con sezione `event_sounds`
- Refactoring `AudioManager.__init__()` per leggere mapping da JSON
- Rimozione dizionario hardcoded `_event_sounds`
- Preload automatico di tutti i file negli `event_sounds`
- Validazione eventi sconosciuti con logging
- Test unitari per nuovo loader
- Documentazione aggiornata (API.md, README)

### Out of Scope
- Hot-reload config a runtime (feature futura)
- Modding system per suoni custom (v4.x)
- Modifica infrastruttura audio esistente
- Cambio formato file audio (WAV/OGG supporto invariato)

---

## 🛠️ Fasi del Lavoro

### Fase 1 – Ristrutturazione `audio_config.json` (30 min)

**File:** `assets/audio/audio_config.json`

**Obiettivo:** Aggiungere sezione `event_sounds` con mapping evento → file

#### Struttura Attuale
```json
{
  "preload_sounds": [
    "card_move.wav",
    "card_select.wav",
    "invalid.wav",
    "stock_draw.wav",
    "ui_navigate.wav",
    "ui_select.wav",
    "ui_cancel.wav",
    "boundary.wav",
    "victory.wav",
    "timer_warning.wav",
    "timer_expired.wav",
    "mixer_open.wav"
  ],
  "music_tracks": []
}
```

#### Struttura Target
```json
{
  "event_sounds": {
    "CARD_MOVE": "card_move.wav",
    "CARD_SELECT": "card_select.wav",
    "INVALID_MOVE": "invalid.wav",
    "STOCK_DRAW": "stock_draw.wav",
    "UI_NAVIGATE": "ui_navigate.wav",
    "UI_SELECT": "ui_select.wav",
    "UI_CANCEL": "ui_cancel.wav",
    "TABLEAU_BUMPER": "boundary.wav",
    "GAME_WON": "victory.wav",
    "TIMER_WARNING": "timer_warning.wav",
    "TIMER_EXPIRED": "timer_expired.wav",
    "MIXER_OPENED": "mixer_open.wav"
  },
  "preload_all_event_sounds": true,
  "music_tracks": []
}
```

**Cambiamenti:**
- ✅ Sezione `event_sounds` con chiavi `AudioEventType` (nomi enum)
- ✅ Flag `preload_all_event_sounds` per auto-preload (default: `true`)
- ⚠️ Deprecato: `preload_sounds` (ignorato se `preload_all_event_sounds=true`)
- ✅ Backward compatibility: se `event_sounds` manca, fallback a dizionario hardcoded con warning

**Checklist:**
- [ ] Creare sezione `event_sounds` con tutti i 12 eventi correnti
- [ ] Aggiungere flag `preload_all_event_sounds: true`
- [ ] Mantenere `preload_sounds` per backward compatibility (deprecato)
- [ ] Validare JSON con linter online

---

### Fase 2 – Refactoring `AudioManager.__init__()` (1.5 ore)

**File:** `src/infrastructure/audio/audio_manager.py`

**Obiettivo:** Rimuovere dizionario hardcoded, caricare mapping da JSON

#### Modifiche a `__init__()`

**Codice Attuale (linee ~50-70):**
```python
self._event_sounds: Dict[AudioEventType, str] = {
    AudioEventType.CARD_MOVE: "card_move.wav",
    AudioEventType.CARD_SELECT: "card_select.wav",
    # ... 12 linee hardcoded ...
}
```

**Codice Target:**
```python
# Load event-to-sound mapping from JSON config
self._event_sounds: Dict[AudioEventType, str] = self._load_event_mapping(config_data)

# Auto-preload all event sounds if flag enabled
if config_data.get("preload_all_event_sounds", True):
    for sound_file in self._event_sounds.values():
        self._preload_sound(sound_file)
```

#### Nuovo Metodo `_load_event_mapping()`

**Posizione:** Dopo `__init__()`, prima di `initialize()`

```python
def _load_event_mapping(self, config: dict) -> Dict[AudioEventType, str]:
    """Load event-to-sound mapping from JSON config.
    
    Converts JSON key strings (e.g. "CARD_MOVE") to AudioEventType enum.
    Falls back to hardcoded defaults if config section missing.
    
    Args:
        config: Parsed audio_config.json dictionary
        
    Returns:
        Dictionary mapping AudioEventType enum to sound filenames
        
    Raises:
        None (logs warnings for unknown events, uses defaults on error)
        
    Example:
        >>> config = {"event_sounds": {"CARD_MOVE": "card.wav"}}
        >>> mapping = self._load_event_mapping(config)
        >>> mapping[AudioEventType.CARD_MOVE]
        'card.wav'
    """
    # Check if event_sounds section exists
    event_sounds_config = config.get("event_sounds", {})
    
    if not event_sounds_config:
        # FALLBACK: Use hardcoded defaults (backward compatibility)
        log.warning(
            "AudioManager: 'event_sounds' section missing in audio_config.json. "
            "Using hardcoded defaults. Consider updating config file."
        )
        return self._get_default_event_mapping()
    
    # Parse JSON keys to AudioEventType enum
    mapping = {}
    for event_name_str, sound_file in event_sounds_config.items():
        try:
            # Convert string "CARD_MOVE" to AudioEventType.CARD_MOVE
            event_type = AudioEventType[event_name_str]
            mapping[event_type] = sound_file
        except KeyError:
            # Unknown event in config (typo or obsolete entry)
            log.warning(
                f"AudioManager: Unknown event type in config: '{event_name_str}'. "
                f"Skipping. Valid events: {[e.name for e in AudioEventType]}"
            )
            continue
    
    # Validate completeness (all enum values should have mapping)
    missing_events = set(AudioEventType) - set(mapping.keys())
    if missing_events:
        log.warning(
            f"AudioManager: Missing events in config: {[e.name for e in missing_events]}. "
            f"These events will have no sound."
        )
    
    return mapping
```

#### Nuovo Metodo `_get_default_event_mapping()` (Fallback)

**Posizione:** Dopo `_load_event_mapping()`

```python
def _get_default_event_mapping(self) -> Dict[AudioEventType, str]:
    """Hardcoded default event mapping (backward compatibility fallback).
    
    Used when audio_config.json is missing 'event_sounds' section.
    
    Returns:
        Dictionary with default sound assignments for all events
    """
    return {
        AudioEventType.CARD_MOVE: "card_move.wav",
        AudioEventType.CARD_SELECT: "card_select.wav",
        AudioEventType.INVALID_MOVE: "invalid.wav",
        AudioEventType.STOCK_DRAW: "stock_draw.wav",
        AudioEventType.UI_NAVIGATE: "ui_navigate.wav",
        AudioEventType.UI_SELECT: "ui_select.wav",
        AudioEventType.UI_CANCEL: "ui_cancel.wav",
        AudioEventType.TABLEAU_BUMPER: "boundary.wav",
        AudioEventType.GAME_WON: "victory.wav",
        AudioEventType.TIMER_WARNING: "timer_warning.wav",
        AudioEventType.TIMER_EXPIRED: "timer_expired.wav",
        AudioEventType.MIXER_OPENED: "mixer_open.wav",
    }
```

**Checklist:**
- [ ] Rimuovere dizionario hardcoded da `__init__()`
- [ ] Implementare `_load_event_mapping()` con parsing JSON
- [ ] Implementare `_get_default_event_mapping()` per fallback
- [ ] Aggiungere auto-preload condizionale (`preload_all_event_sounds`)
- [ ] Logging warning per eventi sconosciuti/mancanti
- [ ] Documentare nuovi metodi con docstring complete

---

### Fase 3 – Validazione e Backward Compatibility (45 min)

**Obiettivo:** Gestire gracefully configurazioni legacy e errori

#### Validazione Sync (Opzionale)

**Nuovo Metodo:** `_validate_config_completeness()`

```python
def _validate_config_completeness(self) -> None:
    """Validate that all AudioEventType enums have a sound mapping.
    
    Logs warnings for missing events (informational, not critical).
    Called during initialization for sanity check.
    
    Side Effects:
        Logs warning messages for incomplete configuration
    """
    all_events = set(AudioEventType)
    mapped_events = set(self._event_sounds.keys())
    
    missing = all_events - mapped_events
    if missing:
        log.warning(
            f"AudioManager: Configuration incomplete. "
            f"Events without sound mapping: {[e.name for e in missing]}"
        )
    
    # Optional: Check for files that exist in mapping but not on disk
    for event_type, sound_file in self._event_sounds.items():
        file_path = os.path.join(self._sounds_path, sound_file)
        if not os.path.exists(file_path):
            log.warning(
                f"AudioManager: Sound file not found for {event_type.name}: {sound_file}"
            )
```

**Chiamata:** Aggiungere in `__init__()` dopo caricamento mapping:

```python
# Validate configuration completeness (non-blocking)
self._validate_config_completeness()
```

#### Test Backward Compatibility

**Scenario 1:** Config JSON vecchio (solo `preload_sounds`)
- ✅ Sistema usa `_get_default_event_mapping()` con warning
- ✅ Funziona come prima del refactoring

**Scenario 2:** Config JSON parziale (mancano alcuni eventi)
- ✅ Sistema carica eventi presenti
- ✅ Log warning per eventi mancanti
- ✅ Eventi senza mapping semplicemente non producono suono

**Scenario 3:** Config JSON corrotto (syntax error)
- ✅ ConfigLoader solleva eccezione
- ✅ AudioManager fallback a defaults con error log
- ✅ Applicazione continua (graceful degradation)

**Checklist:**
- [ ] Implementare `_validate_config_completeness()`
- [ ] Test manuale con config vecchio (solo `preload_sounds`)
- [ ] Test manuale con config parziale (4/12 eventi)
- [ ] Test manuale con JSON corrotto (syntax error)
- [ ] Verificare logging warning/error in tutti i casi

---

### Fase 4 – Test Unitari (1 ora)

**File:** `tests/unit/infrastructure/audio/test_audio_manager_config.py` (nuovo)

**Obiettivo:** Test coverage per nuovo loader con mocking

#### Test Case 1: Caricamento Config Completo

```python
def test_load_event_mapping_complete_config():
    """Test che tutti gli eventi vengano mappati correttamente da JSON."""
    config = {
        "event_sounds": {
            "CARD_MOVE": "custom_move.wav",
            "CARD_SELECT": "custom_select.wav",
            # ... tutti i 12 eventi ...
        }
    }
    
    manager = AudioManager(enabled=False)  # Mock pygame
    manager._config_data = config
    mapping = manager._load_event_mapping(config)
    
    assert len(mapping) == 12
    assert mapping[AudioEventType.CARD_MOVE] == "custom_move.wav"
    assert mapping[AudioEventType.CARD_SELECT] == "custom_select.wav"
```

#### Test Case 2: Fallback a Defaults

```python
def test_load_event_mapping_missing_section():
    """Test fallback a defaults quando 'event_sounds' manca."""
    config = {"music_tracks": []}  # No event_sounds
    
    manager = AudioManager(enabled=False)
    mapping = manager._load_event_mapping(config)
    
    # Deve usare defaults hardcoded
    assert len(mapping) == 12
    assert mapping[AudioEventType.CARD_MOVE] == "card_move.wav"
```

#### Test Case 3: Evento Sconosciuto (Typo)

```python
def test_load_event_mapping_unknown_event(caplog):
    """Test che eventi sconosciuti vengano ignorati con warning."""
    config = {
        "event_sounds": {
            "CARD_MOVE": "move.wav",
            "UNKNOWN_EVENT": "typo.wav"  # Typo
        }
    }
    
    manager = AudioManager(enabled=False)
    mapping = manager._load_event_mapping(config)
    
    assert "UNKNOWN_EVENT" in caplog.text  # Warning logged
    assert AudioEventType.CARD_MOVE in mapping
    assert len(mapping) == 1  # Solo evento valido
```

#### Test Case 4: Preload Automatico

```python
def test_auto_preload_event_sounds(mocker):
    """Test che preload_all_event_sounds carichi tutti i file."""
    mock_preload = mocker.patch.object(AudioManager, '_preload_sound')
    
    config = {
        "event_sounds": {
            "CARD_MOVE": "move.wav",
            "UI_SELECT": "select.wav"
        },
        "preload_all_event_sounds": True
    }
    
    manager = AudioManager(enabled=False)
    manager._config_data = config
    manager.__init__(...)  # Trigger preload
    
    # Verify _preload_sound chiamato 2 volte
    assert mock_preload.call_count == 2
    mock_preload.assert_any_call("move.wav")
    mock_preload.assert_any_call("select.wav")
```

#### Test Case 5: Validazione Completezza

```python
def test_validate_config_completeness_missing_events(caplog):
    """Test warning per eventi senza mapping."""
    manager = AudioManager(enabled=False)
    manager._event_sounds = {
        AudioEventType.CARD_MOVE: "move.wav"
        # Mancano 11 eventi
    }
    
    manager._validate_config_completeness()
    
    assert "Configuration incomplete" in caplog.text
    assert "CARD_SELECT" in caplog.text  # Evento mancante
```

**Checklist:**
- [ ] Creare file test `test_audio_manager_config.py`
- [ ] Implementare 5 test case con pytest
- [ ] Mock pygame.mixer per evitare dipendenze audio
- [ ] Verificare coverage ≥90% per nuovi metodi
- [ ] Integrare in CI/CD pipeline

---

### Fase 5 – Documentazione (30 min)

**File da Aggiornare:**

#### 1. `docs/API.md` – Sezione AudioManager

**Aggiungere:**
```markdown
### Configurazione Event-to-Sound Mapping

Il mapping tra `AudioEventType` e file audio è configurabile via `audio_config.json`:

```json
{
  "event_sounds": {
    "CARD_MOVE": "card_move.wav",
    "GAME_WON": "victory.wav"
  },
  "preload_all_event_sounds": true
}
```

**Cambiare Suono:**
1. Copiare nuovo file `.wav` in `assets/audio/sounds/`
2. Modificare `event_sounds` in `audio_config.json`
3. Restart applicazione

**Fallback:** Se sezione `event_sounds` manca, usa defaults hardcoded con warning log.
```

#### 2. `README.md` – Sezione Configurazione

**Aggiungere:**
```markdown
## 🔊 Configurazione Audio

Personalizza i suoni degli eventi modificando `assets/audio/audio_config.json`:

```json
{
  "event_sounds": {
    "GAME_WON": "epic_fanfare.wav"
  }
}
```

File audio supportati: `.wav`, `.ogg`, `.mp3` (posizione: `assets/audio/sounds/`)
```

#### 3. `assets/audio/audio_config.json` – Commenti

**Aggiungere header:**
```json
{
  "_comment": "AudioManager configuration file. Modify 'event_sounds' to customize game sounds.",
  "_version": "3.5.0",
  "event_sounds": { ... }
}
```

**Checklist:**
- [ ] Aggiornare `docs/API.md` con sezione configurazione
- [ ] Aggiornare `README.md` con esempio pratico
- [ ] Aggiungere commenti esplicativi in `audio_config.json`
- [ ] Creare esempio config in `docs/examples/audio_config_custom.json`

---

### Fase 6 – Integration Testing (45 min)

**Obiettivo:** Test end-to-end con applicazione reale

#### Test Manuale 1: Config Standard

**Setup:**
- Config JSON con tutti i 12 eventi standard
- File audio presenti in `assets/audio/sounds/`

**Procedura:**
1. Avviare applicazione
2. Verificare log: nessun warning caricamento config
3. Testare eventi gameplay (CARD_MOVE, UI_NAVIGATE, GAME_WON)
4. Verificare audio output corretto

**Atteso:** ✅ Nessun warning, tutti i suoni funzionano

---

#### Test Manuale 2: Config Personalizzato

**Setup:**
- Modificare `audio_config.json`:
  ```json
  {
    "event_sounds": {
      "GAME_WON": "custom_victory.wav"
    }
  }
  ```
- Copiare `custom_victory.wav` in `assets/audio/sounds/`

**Procedura:**
1. Avviare applicazione
2. Forzare vittoria (CTRL+ALT+W)
3. Verificare audio: suono custom riprodotto

**Atteso:** ✅ Suono personalizzato, nessun crash

---

#### Test Manuale 3: Config Parziale (Missing Events)

**Setup:**
- Config JSON con solo 3 eventi:
  ```json
  {
    "event_sounds": {
      "CARD_MOVE": "move.wav",
      "UI_SELECT": "select.wav",
      "GAME_WON": "victory.wav"
    }
  }
  ```

**Procedura:**
1. Avviare applicazione
2. Verificare log: warning "Missing events in config"
3. Testare evento mancante (es. CARD_SELECT)

**Atteso:** ✅ Warning logged, eventi mancanti silenziosi (no crash)

---

#### Test Manuale 4: Config Legacy (Solo preload_sounds)

**Setup:**
- Config JSON vecchio formato:
  ```json
  {
    "preload_sounds": ["card_move.wav", "ui_select.wav"]
  }
  ```

**Procedura:**
1. Avviare applicazione
2. Verificare log: warning "Using hardcoded defaults"
3. Testare eventi gameplay

**Atteso:** ✅ Fallback a defaults, funziona come v3.4.x

---

#### Test Manuale 5: Config Corrotto (JSON Invalido)

**Setup:**
- Corrompere `audio_config.json`:
  ```json
  {
    "event_sounds": {
      "CARD_MOVE": "move.wav",  // Syntax error: trailing comma
    }
  }
  ```

**Procedura:**
1. Avviare applicazione
2. Verificare gestione errore

**Atteso:** ✅ Error log, fallback a defaults, no crash

---

**Checklist:**
- [ ] Eseguire tutti i 5 test manuali
- [ ] Documentare risultati in `tests/manual/audio_config_tests.md`
- [ ] Verificare nessun regression su funzionalità esistenti
- [ ] Confermare graceful degradation in tutti gli scenari

---

## 📋 File Coinvolti

### Modificati
- `src/infrastructure/audio/audio_manager.py` – Core refactoring
- `assets/audio/audio_config.json` – Nuova struttura
- `docs/API.md` – Documentazione API
- `README.md` – Configurazione utente
- `CHANGELOG.md` – Entry v3.5.0

### Creati
- `tests/unit/infrastructure/audio/test_audio_manager_config.py` – Unit tests
- `tests/manual/audio_config_tests.md` – Procedura test manuali
- `docs/examples/audio_config_custom.json` – Esempio configurazione custom

### Deprecati (Soft)
- Sezione `preload_sounds` in `audio_config.json` (ancora supportata, ma ignorata se `event_sounds` presente)

---

## ✅ Criteri di Completamento

- [ ] Dizionario hardcoded `_event_sounds` rimosso da `__init__()`
- [ ] Nuovo loader `_load_event_mapping()` implementato e testato
- [ ] Fallback a defaults funzionante (backward compatibility)
- [ ] Validazione config con warning per eventi sconosciuti/mancanti
- [ ] Test unitari coverage ≥90% per nuovi metodi
- [ ] Test manuali 5/5 passati senza regressioni
- [ ] Documentazione aggiornata (API.md, README.md)
- [ ] CHANGELOG entry creato per v3.5.0
- [ ] Nessun warning/error in log con config standard
- [ ] Branch `refactor-audio-config-json` pronto per merge

---

## 🚀 Workflow di Implementazione

### Step 1: Setup Branch
```bash
git checkout supporto-audio-centralizzato
git pull origin supporto-audio-centralizzato
git checkout -b refactor-audio-config-json
```

### Step 2: Implementazione Fasi 1-3
- Fase 1: Modificare `audio_config.json`
- Fase 2: Refactoring `AudioManager`
- Fase 3: Implementare validazione
- Commit atomici: `refactor(audio): [fase-X] description`

### Step 3: Testing (Fasi 4-6)
- Fase 4: Unit tests con pytest
- Fase 5: Documentazione
- Fase 6: Integration testing
- Commit: `test(audio): add config loader tests`

### Step 4: Review e Merge
```bash
git push origin refactor-audio-config-json
# Create PR: refactor-audio-config-json → supporto-audio-centralizzato
# Review checklist completata
# Merge con squash commit
```

---

## 📊 Stime Temporali

| Fase | Descrizione | Tempo Stimato |
|------|-------------|---------------|
| 1 | Ristrutturazione JSON | 30 min |
| 2 | Refactoring AudioManager | 1.5 ore |
| 3 | Validazione & Backward Compat | 45 min |
| 4 | Test Unitari | 1 ora |
| 5 | Documentazione | 30 min |
| 6 | Integration Testing | 45 min |
| **TOTALE** | | **~5 ore** |

**Buffer contingenza:** +30 min (10%)  
**Totale realistico:** **5.5 ore** (circa 1 giornata lavorativa)

---

## 🎯 Metriche di Successo

### Quantitative
- ✅ 0 linee hardcoded per event mapping in Python
- ✅ 1 singolo file config (audio_config.json) per tutte le modifiche
- ✅ ≥90% test coverage per `_load_event_mapping()`
- ✅ 0 regressioni su funzionalità esistenti

### Qualitative
- ✅ Cambio suono richiede 2 step invece di 4
- ✅ Config modificabile da utenti non-programmatori
- ✅ Base per future feature (hot-reload, modding)
- ✅ Codice più manutenibile e SOLID-compliant

---

## 🔄 Rollback Strategy

**Se problemi critici durante testing:**

1. **Rollback immediato:** `git revert` commit refactoring
2. **Fallback automatico:** Sistema usa `_get_default_event_mapping()` se config corrotto
3. **Backward compatibility:** Config vecchio formato continua a funzionare

**Zero downtime:** Utenti con vecchio config non vedono differenze.

---

## 📝 Note Implementative

### Best Practices

1. **Import Lazy:** `AudioEventType` importato solo quando necessario (evita circular imports)
2. **Logging Verboso:** Warning/error chiari per debug (ma non critici)
3. **Graceful Degradation:** Nessun crash se config malformato
4. **Type Hints:** Tutti i nuovi metodi annotati con tipi
5. **Docstring Complete:** Google style per tutti i metodi pubblici/privati

### Pitfall da Evitare

❌ **Non** sollevare eccezioni se evento mancante (log warning, continua)  
❌ **Non** richiedere restart manuale dopo modifica config (per ora, hot-reload è v4.x)  
❌ **Non** validare esistenza file audio in loader (fallo in `_validate_config_completeness()`)  
❌ **Non** rimuovere fallback defaults (backward compatibility critica)

---

## 🔗 Riferimenti

- Issue GitHub: #TBD (da creare dopo approval piano)
- Branch: `refactor-audio-config-json`
- Related Plan: `PLAN_revisione_audio_centralizzato.md`
- Architecture Doc: `docs/ARCHITECTURE.md` (sezione Audio System)

---

*Versione 1.0 – 23 Febbraio 2026, 22:35 CET*  
*Autore: Perplexity AI (assistente sviluppo)*  
*Reviewer: Da assegnare*
