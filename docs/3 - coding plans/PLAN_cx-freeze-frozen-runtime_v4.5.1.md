---
type: plan
feature: cx-freeze-frozen-runtime
agent: Agent-Plan
status: DRAFT
version: v4.5.1
design_ref: docs/2 - projects/DESIGN_cx-freeze-frozen-runtime.md
date: 2026-04-09
---

# PLAN: cx_Freeze Frozen Runtime Correction v4.5.1

## 1. Executive Summary

- **Tipo**: correttivo — avvio/runtime frozen cx_Freeze
- **Priorità**: alta — blocca uso dell'eseguibile distribuito
- **Branch suggerito**: `fix/frozen-runtime-v4.5.1`
- **Versione target**: v4.5.1
- **Design di riferimento**: [DESIGN_cx-freeze-frozen-runtime.md](../2%20-%20projects/DESIGN_cx-freeze-frozen-runtime.md)
- **Dipendenza**: build cx_Freeze funzionante introdotto in v4.5.0

## 2. Problema e Obiettivo

### Problema

Il build cx_Freeze produce `solitario.exe` ma l'avvio frozen e fragile per tre cause combinate:

1. Nessun log anticipato con `base="Win32GUI"` — crash silenzioso non ispezionabile.
2. Path di config, assets, logs risolti da CWD invece che dalla cartella dell'exe — fallimento
   quando l'app e lanciata da shortcut o da directory diversa.
3. Init di pygame, NVDA e SAPI5 non protetti — un provider non disponibile o una DLL
   mancante blocca l'intero avvio.

### Obiettivo

Rendere l'avvio frozen deterministico, osservabile e resistente al fallimento
dei sottosistemi opzionali. Il risultato atteso e:

- `solitario.exe` si avvia correttamente da qualsiasi CWD.
- Se si verifica un errore, un file di log diagnostico leggibile esiste sempre.
- Mancanza di NVDA, SAPI5 o pygame e gestita gracefully senza crash.
- Il build e considerato valido solo se le DLL native pygame/SDL2 sono presenti e verificate.

## 3. File Coinvolti

### CREATE

| File | Motivo |
|------|--------|
| `src/infrastructure/config/runtime_root.py` | Resolver canonico del runtime root (frozen vs source). Unica fonte di verita per tutti i consumer infrastrutturali. |
| `scripts/validate_frozen_build.py` | Script di validazione post-build: verifica DLL native pygame/SDL2, struttura cartelle e smoke test dell'exe. |

### MODIFY

| File | Motivo |
|------|--------|
| `acs_wx.py` | Aggiungere bootstrap diagnostico anticipato prima di `setup_logging()` e `SolitarioController`. Usare runtime root per il path dei log di startup. |
| `src/infrastructure/logging/logger_setup.py` | Sostituire `Path("logs")` hardcoded con runtime root passato come parametro o importato da resolver. |
| `src/infrastructure/logging/categorized_logger.py` | Allineamento al runtime root per i path di log. |
| `src/infrastructure/config/audio_config_loader.py` | Sostituire path relativo con runtime root. |
| `src/infrastructure/config/scoring_config_loader.py` | Sostituire `Path("config/scoring_config.json")` con runtime root. |
| `src/infrastructure/audio/audio_manager.py` | Sostituire `Path("assets/sounds")` con runtime root; hardening init pygame.mixer (try/except non bloccante). |
| `src/infrastructure/accessibility/tts_provider.py` | Hardening init: NVDA -> SAPI5 -> dummy/no-op, nessun blocco su provider non disponibile. |
| `setup.py` | Aggiungere variante console executable (`solitario-diag.exe`) per smoke test e debug frozen. |

### DELETE

Nessuno.

## 4. Fasi Sequenziali

### Fase 1 — Bootstrap diagnostico anticipato

**Obiettivo**: rendere sempre osservabile un crash nelle prime fasi di avvio, anche con `Win32GUI`.

**Operazioni**:
- In `acs_wx.py`, prima di `setup_logging()` e prima della costruzione di wx.App,
  aggiungere un blocco try/except globale che:
  - Determina il `runtime root` (vedi Fase 2).
  - Apre un file `startup_diagnostic.log` nel runtime root in modalita append.
  - Da quel momento, qualsiasi eccezione non gestita durante l'avvio viene catturata
    e scritta nel file diagnostico prima di re-raise o sys.exit.
- Il file diagnostico non e il log applicativo standard; e separato e sempre presente.

**Files**: MODIFY `acs_wx.py`

**Gate Fase 1**: build locale + lancio dell'exe da una directory diversa dalla build dir.
Il file `startup_diagnostic.log` deve essere creato nella cartella dell'exe.

---

### Fase 2 — Runtime root/path resolver

**Obiettivo**: eliminare la dipendenza dal CWD per config, assets e log in tutto
il perimetro frozen.

**Operazioni**:
- Creare `src/infrastructure/config/runtime_root.py` con una funzione pubblica
  `get_runtime_root() -> Path` che restituisce:
  - In frozen build (`sys.frozen` presente): `Path(sys.executable).parent`
  - In sorgente: project root derivato da `__file__` del modulo o variabile d'ambiente
    `SOLITARIO_ROOT`.
- Aggiornare i consumer nell'ordine:
  1. `logger_setup.py` e `categorized_logger.py`: `Path("logs")` -> `get_runtime_root() / "logs"`
  2. `audio_config_loader.py`: path config -> `get_runtime_root() / "config" / "audio_config.json"`
  3. `scoring_config_loader.py`: path config -> `get_runtime_root() / "config" / "scoring_config.json"`
  4. `audio_manager.py`: default sounds path -> `get_runtime_root() / "assets" / "sounds"`
  5. `acs_wx.py`: path log diagnostico -> `get_runtime_root() / "startup_diagnostic.log"`
- Nessun altro file viene modificato in questa fase.

**Files**: CREATE `runtime_root.py`, MODIFY `logger_setup.py`, `categorized_logger.py`,
`audio_config_loader.py`, `scoring_config_loader.py`, `audio_manager.py`, `acs_wx.py`

**Gate Fase 2**: `pytest tests/infrastructure/config/` e `pytest tests/infrastructure/logging/`
passano senza regressioni. Lancio dell'exe da `%TEMP%\test_launch\` produce log corretti.

---

### Fase 3 — Hardening TTS e audio opzionali

**Obiettivo**: NVDA, SAPI5 e pygame non devono poter abortire l'avvio frozen.

**Operazioni**:

**tts_provider.py**:
- Avvolgere l'init di NVDA in try/except con fallback esplicito a SAPI5.
- Avvolgere l'init di SAPI5/pyttsx3 in try/except con fallback a dummy/no-op.
- Loggare ogni fallback con livello WARNING nel log applicativo.
- Nessun provider failure deve propagare eccezione al chiamante durante l'init.

**audio_manager.py**:
- Avvolgere `pygame.mixer.init()` in try/except.
- Se il mixer non si inizializza, impostare un flag interno `_audio_available = False`.
- Tutti i metodi pubblici dell'AudioManager verificano il flag prima di chiamare pygame;
  se `_audio_available` e False, il metodo esegue un no-op silenzioso con log DEBUG.

**Files**: MODIFY `tts_provider.py`, `audio_manager.py`

**Gate Fase 3**:
- `pytest tests/infrastructure/accessibility/` con mock NVDA non disponibile.
- `pytest tests/infrastructure/audio/` con mock `pygame.mixer.init` che lancia eccezione.
- Entrambi i test passano e verificano che l'applicazione raggiunga il frame principale.

---

### Fase 4 — Validazione DLL pygame/SDL2

**Obiettivo**: il build e considerato valido solo se le DLL native sono presenti e caricabili.

**Operazioni**:
- Creare `scripts/validate_frozen_build.py` con le seguenti verifiche:
  1. Verifica esistenza di `solitario.exe` nella build dir specificata come argomento.
  2. Enumera le DLL richieste da pygame/SDL2 (SDL2.dll, SDL2_mixer.dll e relative) e
     verifica che siano presenti nella cartella frozen.
  3. Tenta il caricamento di ciascuna DLL con `ctypes.WinDLL` dentro un try/except
     e riporta quelle che falliscono.
  4. Verifica struttura minimale: cartelle `assets/`, `config/`, `lib/` presenti.
  5. Exit code 0 se tutto ok, 1 con riepilogo errori se qualche verifica fallisce.
- Aggiornare `setup.py` (o il README/CI note) per documentare che `validate_frozen_build.py`
  deve essere eseguito dopo ogni `build_exe`.

**Files**: CREATE `scripts/validate_frozen_build.py`, MODIFY `setup.py` (commento/docstring)

**Gate Fase 4**: `python scripts/validate_frozen_build.py dist/solitario-classico` restituisce
exit code 0 su un build completo e valido.

---

### Fase 5 — Variante diagnostica (build console)

**Obiettivo**: affiancare all'exe release un exe console per smoke test e debug frozen,
senza toccare il comportamento release.

**Operazioni**:
- In `setup.py`, nella lista degli executable, aggiungere un secondo entry con:
  - `target_name = "solitario-diag.exe"`
  - `base = "Console"` (invece di `Win32GUI`)
  - Stesso script di ingresso (`acs_wx.py`)
- L'exe diagnostico viene incluso nella stessa build ma il README deve chiarire
  che non e per l'utente finale.
- Aggiungere a `validate_frozen_build.py` la verifica dell'esistenza di `solitario-diag.exe`.

**Files**: MODIFY `setup.py`, MODIFY `scripts/validate_frozen_build.py`

**Gate Fase 5**: `python setup.py build_exe` produce sia `solitario.exe` che `solitario-diag.exe`.
`solitario-diag.exe` lancia un terminale con output leggibile.

---

### Fase 6 — Verifica build, smoke test ed exe

**Obiettivo**: validazione integrata end-to-end del correttivo.

**Operazioni**:
1. Build completo: `python setup.py build_exe`
2. Eseguire `python scripts/validate_frozen_build.py dist/solitario-classico`
3. Lanciare `solitario-diag.exe` da una directory esterna alla build e verificare:
   - `startup_diagnostic.log` creato nella cartella build (non nella CWD esterna)
   - Nessun traceback nel log
   - Il frame GUI si apre
4. Lanciare `solitario.exe` in modalita normale e verificare lo stesso.
5. Verificare i log applicativi in `dist/solitario-classico/logs/` (non in CWD esterno).

**Files**: nessun file di codice modificato in questa fase — solo validazione.

**Gate Fase 6**:
- `validate_frozen_build.py` exit 0
- `startup_diagnostic.log` presente e senza errori critici
- `logs/` generati sotto la build dir, non in CWD esterno

---

## 5. Test Plan

### Unit

| Test | File/modulo target | Scenario |
|------|--------------------|----------|
| `test_get_runtime_root_frozen` | `runtime_root.py` | Simula `sys.frozen = True`, verifica path = exe parent |
| `test_get_runtime_root_source` | `runtime_root.py` | Nessun `sys.frozen`, verifica path = project root |
| `test_tts_nvda_fallback` | `tts_provider.py` | Mock NVDA non disponibile, verifica attivazione SAPI5 |
| `test_tts_all_fail_noop` | `tts_provider.py` | Mock NVDA + SAPI5 falliscono, verifica no crash + dummy |
| `test_audio_mixer_fail_noop` | `audio_manager.py` | Mock `pygame.mixer.init` che lancia eccezione, verifica flag `_audio_available=False` |
| `test_audio_noop_when_unavailable` | `audio_manager.py` | `_audio_available=False`, verifica che i metodi pubblici non crashino |

### Integration / Smoke

| Test | Metodo |
|------|--------|
| Build frozen completo | `python setup.py build_exe` — exit 0 |
| Validazione DLL | `python scripts/validate_frozen_build.py dist/solitario-classico` — exit 0 |
| Avvio da CWD esterno | Lanciare `solitario-diag.exe` da `%TEMP%`, verificare log in build dir |
| Log diagnostico | Verificare esistenza e contenuto di `startup_diagnostic.log` nella build dir |

## 6. Dipendenze

- Build cx_Freeze v4.5.0 funzionante (gia presente).
- Python 3.11, cx_Freeze, pygame, pyttsx3, accessible_output2 installati nel venv.
- Nessuna nuova dipendenza di produzione — `runtime_root.py` usa solo stdlib (`sys`, `pathlib`).

## 7. Rischi

- DLL pygame variabili per versione di SDL2 installata: la lista da verificare in
  `validate_frozen_build.py` va calibrata sul venv corrente (usare `pip show pygame`
  e listare le DLL nella cartella di installazione).
- `accessible_output2` e `pyttsx3` possono dipendere da componenti COM Windows non
  completamente congelabili; il correttivo riduce il crash, non garantisce feature parity
  tra ambiente sorgente e frozen su macchina pulita.
- Regressions: cambiare come vengono passati i path ai loader di config puo impattare
  test unitari esistenti — verificare con `pytest` prima di ogni commit di fase.
