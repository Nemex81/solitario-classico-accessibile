---
type: todo
feature: cx-freeze-frozen-runtime
agent: Agent-Plan
status: COMPLETED
version: v4.5.1
plan_ref: docs/3 - coding plans/PLAN_cx-freeze-frozen-runtime_v4.5.1.md
date: 2026-04-09
---

# TODO: cx_Freeze Frozen Runtime Correction v4.5.1

Piano di riferimento: [PLAN_cx-freeze-frozen-runtime_v4.5.1.md](../3%20-%20coding%20plans/PLAN_cx-freeze-frozen-runtime_v4.5.1.md)

---

## Istruzioni per Agent-Code

- Implementa **una fase alla volta**, nell'ordine indicato.
- Prima di iniziare una fase: leggi il PLAN per i dettagli tecnici della fase.
- Dopo ogni fase: esegui il **gate di validazione** elencato sotto la checklist.
  Se il gate fallisce, correggere prima di passare alla fase successiva.
- Aggiorna questa checklist spuntando i task completati (`[ ]` -> `[x]`).
- Non modificare file `.github/**`.
- Non implementare codice al di fuori del perimetro dichiarato nei file coinvolti.
- Per ogni commit: seguire la convenzione `fix(infra): ...` o `feat(infra): ...` per
  il canale correttivo v4.5.1.

---

## Fase 1 — Bootstrap diagnostico anticipato

**File**: `acs_wx.py`

- [x] Aggiungere blocco try/except globale prima di `setup_logging()`
- [x] Determinare runtime root (anticipato rispetto a Fase 2 — usa logica inline per ora)
- [x] Aprire `startup_diagnostic.log` nel runtime root in modalita append
- [x] Catturare qualsiasi eccezione non gestita durante l'avvio e scriverla nel log

**Gate**: Lanciare exe da directory diversa dalla build dir.
`startup_diagnostic.log` creato nella cartella dell'exe (non in CWD).

---

## Fase 2 — Runtime root/path resolver

**File**: CREATE `src/infrastructure/config/runtime_root.py`  
**File**: MODIFY `logger_setup.py`, `categorized_logger.py`, `audio_config_loader.py`,
`scoring_config_loader.py`, `audio_manager.py`, `acs_wx.py`

- [x] Creare `runtime_root.py` con `get_runtime_root() -> Path`
  - [x] Frozen mode: `Path(sys.executable).parent`
  - [x] Source mode: project root da `__file__` o `SOLITARIO_ROOT` env var
- [x] Aggiornare `logger_setup.py`: `Path("logs")` -> `get_runtime_root() / "logs"`
- [x] Aggiornare `categorized_logger.py`: allineamento al runtime root
- [x] Aggiornare `audio_config_loader.py`: path hardcoded -> runtime root
- [x] Aggiornare `scoring_config_loader.py`: `Path("config/scoring_config.json")` -> runtime root
- [x] Aggiornare `audio_manager.py`: default sounds path -> runtime root
- [x] Aggiornare `acs_wx.py`: usare `get_runtime_root()` per log diagnostico

**Gate**:
```
pytest tests/infrastructure/config/
pytest tests/infrastructure/logging/
```
Entrambi passano. Lancio exe da `%TEMP%\test_launch\` produce log in build dir.

---

## Fase 3 — Hardening TTS e audio opzionali

**File**: MODIFY `src/infrastructure/accessibility/tts_provider.py`  
**File**: MODIFY `src/infrastructure/audio/audio_manager.py`

- [x] `tts_provider.py`: wrap init NVDA in try/except, fallback a SAPI5
- [x] `tts_provider.py`: wrap init SAPI5/pyttsx3 in try/except, fallback a dummy/no-op
- [x] `tts_provider.py`: log WARNING per ogni fallback
- [x] `audio_manager.py`: wrap `pygame.mixer.init()` in try/except
- [x] `audio_manager.py`: flag `_audio_available = False` se mixer non si inizializza
- [x] `audio_manager.py`: metodi pubblici verificano flag, no-op silenzioso se unavailable

**Gate**:
```
pytest tests/infrastructure/accessibility/
pytest tests/infrastructure/audio/
```
Test con mock NVDA non disponibile e mock `pygame.mixer.init` che lancia eccezione passano.

---

## Fase 4 — Validazione DLL pygame/SDL2

**File**: CREATE `scripts/validate_frozen_build.py`  
**File**: MODIFY `setup.py` (commento/docstring build validation)

- [x] Implementare `validate_frozen_build.py` con verifica:
  - [x] Esistenza `solitario.exe`
  - [x] Presenza DLL SDL2.dll, SDL2_mixer.dll (e altre richieste da pygame)
  - [x] Caricamento DLL con `ctypes.WinDLL` (try/except per ciascuna)
  - [x] Struttura `assets/`, `config/`, `lib/` presenti
  - [x] Riepilogo errori e exit code 1 se qualcosa manca
- [x] Aggiungere nota in `setup.py` che rimanda a `validate_frozen_build.py`

**Gate**:
```
python scripts/validate_frozen_build.py dist/solitario-classico
```
Exit 0 su build completo valido.

---

## Fase 5 — Variante diagnostica (build console)

**File**: MODIFY `setup.py`  
**File**: MODIFY `scripts/validate_frozen_build.py`

- [x] Aggiungere executable `solitario-diag.exe` con `base="Console"` in `setup.py`
- [x] `validate_frozen_build.py`: aggiungere verifica presenza `solitario-diag.exe`

**Gate**:
```
python setup.py build_exe
```
Produce sia `solitario.exe` che `solitario-diag.exe`.
`solitario-diag.exe` apre terminale con output leggibile.

---

## Fase 6 — Verifica build, smoke test ed exe

**Nessun file di codice modificato in questa fase — solo validazione.**

- [x] Build completo: `python setup.py build_exe` — exit 0
- [x] Eseguire: `python scripts/validate_frozen_build.py dist/solitario-classico` — exit 0
- [x] Lanciare `solitario-diag.exe` da directory esterna, verificare:
  - [x] `startup_diagnostic.log` in build dir (non in CWD esterno)
  - [x] Nessun traceback critico nel log
  - [x] Frame GUI si apre
- [x] Lanciare `solitario.exe` da directory esterna, stesso esito
- [x] `logs/` generati sotto `dist/solitario-classico/logs/` (non in CWD esterno)

**Gate finale**: tutte e tre le verifiche precedenti passano.

---

## Stato Avanzamento

- [x] Fase 1 completata
- [x] Fase 2 completata
- [x] Fase 3 completata
- [x] Fase 4 completata
- [x] Fase 5 completata
- [x] Fase 6 — validazione finale superata
