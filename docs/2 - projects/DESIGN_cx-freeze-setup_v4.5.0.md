---
type: design
feature: cx-freeze-setup
version: v4.5.0
status: REVIEWED
agent: Agent-Design
date: 2026-04-09
---

# DESIGN: cx_Freeze Setup v4.5.0

## 1. Idea in 3 righe

Il repository prevede già il build release via `scripts/build-release.py`, ma il file `setup.py` richiesto da quello script non esiste ancora, quindi il packaging Windows con `cx_Freeze` è bloccato. La soluzione introduce un `setup.py` di root che genera `dist/solitario-classico/solitario.exe`, include codice, asset, configurazioni e sound pack, e resta compatibile con i path runtime già usati dal progetto. Per minimizzare il rischio in modalità frozen, le risorse vengono copiate sia dove il codice le cerca per percorso relativo, sia dove le cerca a partire da `__file__` sotto `lib/`.

---

## 2. Attori e Concetti

### Componenti coinvolti

- `setup.py`: nuova definizione `cx_Freeze.setup()` con `Executable` per `acs_wx.py`.
- `scripts/build-release.py`: usa già `python setup.py build_exe` e si aspetta l’output in `dist/solitario-classico/solitario.exe`.
- `acs_wx.py`: entry point applicativo da congelare in modalità GUI Windows.
- `src/infrastructure/ui/card_image_cache.py`: risolve gli asset grafici a partire da `__file__`, quindi in build frozen li cercherà sotto `lib/assets/`.
- `src/infrastructure/config/audio_config_loader.py` e `src/infrastructure/config/scoring_config_loader.py`: cercano `config/*.json` con path relativo al working directory.
- `src/infrastructure/audio/audio_manager.py` e `src/infrastructure/audio/sound_cache.py`: leggono i sound pack da `assets/sounds`.

### Concetti chiave

- `cx_Freeze` con `base="Win32GUI"` su Windows per evitare console.
- `build_exe` path fisso: `dist/solitario-classico` per compatibilità con gli script esistenti.
- `include_files` duplicati mirati:
  - `assets/` e `config/` in root build per i loader che usano path relativi;
  - `assets/` e `config/` anche sotto `lib/` per il codice che ricostruisce il project root da `__file__`.
- Inclusione esplicita di package sensibili per freezing: `wx`, `pygame`, `accessible_output2`, namespace `src.*`.

---

## 3. Flussi Concettuali

### 3.1 Flusso di build

1. `python setup.py build_exe`
2. `cx_Freeze` congela `acs_wx.py`
3. i moduli Python vengono scritti nella cartella build con `lib/`
4. `include_files` copia asset e config nelle posizioni attese
5. l’eseguibile risultante viene verificato dal repository script `scripts/build-release.py`

### 3.2 Flusso runtime frozen

- l’eseguibile avvia `acs_wx.py`
- i loader config leggono `config/audio_config.json` e `config/scoring_config.json` dalla root della build
- il sistema audio carica `assets/sounds/default/...`
- `CardImageCache` risolve le immagini carte e sfondo sotto `lib/assets/img/...`

---

## 4. Decisioni Architetturali

### 4.1 Nessun cambio all’entrypoint

Decisione: mantenere `acs_wx.py` come script principale del build.

Motivazione: è l’entrypoint reale del progetto wxPython corrente e non richiede wrapper aggiuntivi.

### 4.2 Inclusione risorse in doppia posizione

Decisione: copiare `assets` e `config` sia nella root build sia sotto `lib/`.

Motivazione: il progetto oggi usa due strategie diverse di path resolution. La duplicazione è più sicura e meno invasiva di un refactor dei path applicativi dentro questo task di packaging.

### 4.3 Nessun refactor funzionale del runtime

Decisione: non modificare i moduli applicativi per introdurre una nuova utility `resource_path()`.

Motivazione: l’obiettivo del task è rendere buildabile questa versione con intervento focalizzato sul packaging.

---

## 5. Vincoli

- Nessun commit o push.
- Build target Windows.
- Compatibilità con `scripts/build-release.py` già presente nel repo.
- Output previsto: `dist/solitario-classico/solitario.exe`.

---

## 6. Esito atteso

Il repository acquisisce un `setup.py` funzionante e verificato, sufficiente per generare l’eseguibile di test da condividere esternamente.
