# Piano di Implementazione — Sistema Logging Categorizzato

> **Stato**: READY FOR IMPLEMENTATION  
> **Strategia adottata**: Ibrida Low-Risk (non Decorator Pattern)  
> **Basato su**: `DESIGN_categorized_logging.md` + `ANALISI_categorized_logging.md`  
> **Data**: 2026-02-21  
> **Autore**: Nemex81 + GitHub Copilot  
> **Stima**: 1 sessione (~30 minuti)

---

## Decisioni Architetturali Finali

| Decisione | Scelta |
|-----------|--------|
| Strategia implementativa | Ibrida Low-Risk (multi-handler senza decorator) |
| Backup count | **3** (allinea a design, sostituisce il valore legacy 5) |
| Root logger legacy | **Mantenuto** per library logs (wx, PIL, urllib3) su `solitario.log` |
| `logger_setup.py` | Thin wrapper con re-export (Opzione C) — `acs_wx.py` non tocca |
| Decorator Pattern | **Abbandonato** — il routing è già risolto dai named loggers Python |
| `LOGS_DIR` / `LOG_FILE` | Si spostano in `categorized_logger.py`, ri-esportati da `logger_setup.py` |

---

## Quadro Modifiche Definitivo

| File | Tipo | Entità |
|------|------|--------|
| `src/infrastructure/logging/categorized_logger.py` | **NUOVO** | ~60 righe |
| `src/infrastructure/logging/logger_setup.py` | Thin wrapper + re-export | ~10 righe cambiate |
| `src/infrastructure/logging/__init__.py` | Aggiunge export `setup_categorized_logging` | ~2 righe aggiunte |
| `src/infrastructure/logging/game_logger.py` | 3 funzioni timer + 1 fix `keyboard_command` | **4 righe cambiate** |
| `acs_wx.py` | **Nessuna modifica** | 0 righe |
| `tests/` | **Nessuna modifica** | 0 righe |

---

## Step 1 — Crea `categorized_logger.py` (file nuovo)

**Percorso**: `src/infrastructure/logging/categorized_logger.py`

```python
"""
Sistema logging categorizzato - Solitario Classico Accessibile

Sostituisce il monolite solitario.log con 7 file separati per categoria,
mantenendo l'API pubblica (setup_logging) completamente immutata.

Strategia: Multi-handler su named loggers Python esistenti.
Il routing è già risolto dai named loggers — questa classe aggiunge
solo i RotatingFileHandler dedicati a ciascun logger.

Categorie:
    - game      → game_logic.log    (lifecycle partita, mosse)
    - ui        → ui_events.log     (navigazione, dialogs, TTS)
    - error     → errors.log        (errori, warnings)
    - timer     → timer.log         (lifecycle timer, scadenza)
    - profile   → profiles.log      (CRUD profili - futuro)
    - scoring   → scoring.log       (calcoli punteggio - futuro)
    - storage   → storage.log       (I/O file/JSON - futuro)

Compatibilità:
    logger_setup.py espone ancora setup_logging() come thin wrapper.
    acs_wx.py e i test esistenti non richiedono modifiche.

Version:
    v3.2.0: Initial implementation (replaces monolithic solitario.log)
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# ── Configurazione paths ───────────────────────────────────────────────────────

LOGS_DIR = Path("logs")
LOG_FILE = LOGS_DIR / "solitario.log"   # root logger (library logs)

# ── Registro categorie ─────────────────────────────────────────────────────────

CATEGORIES: dict[str, str] = {
    'game':    'game_logic.log',
    'ui':      'ui_events.log',
    'error':   'errors.log',
    'timer':   'timer.log',
    # Categorie future — attiva aggiungendo entry qui + logger in game_logger.py
    # 'profile':  'profiles.log',
    # 'scoring':  'scoring.log',
    # 'storage':  'storage.log',
}

# ── Formatter condiviso ────────────────────────────────────────────────────────

LOG_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def setup_categorized_logging(
    logs_dir: Path = LOGS_DIR,
    level: int = logging.INFO,
    console_output: bool = False,
) -> None:
    """
    Configura logging multi-file categorizzato.

    Crea un RotatingFileHandler dedicato per ogni categoria in CATEGORIES,
    con propagate=False per evitare duplicazione su solitario.log.
    Il root logger mantiene solitario.log per i log di librerie esterne.

    Args:
        logs_dir:       Directory log (default: Path("logs"))
        level:          Livello minimo (default: logging.INFO)
        console_output: Se True, log anche su console (per sviluppo)

    Note:
        Chiamare UNA VOLTA all'avvio, prima di qualsiasi altra init.
        Sostituisce setup_logging() di logger_setup.py.

    Example:
        >>> setup_categorized_logging(level=logging.DEBUG, console_output=True)
        >>> # Risultato: 5 file in logs/ (game_logic.log, ui_events.log, ...)
    """
    logs_dir.mkdir(exist_ok=True)

    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    # ── Handler per ogni categoria ─────────────────────────────────────────────
    for category, filename in CATEGORIES.items():
        logger = logging.getLogger(category)

        # Evita doppia registrazione se chiamato più volte (es. nei test)
        if logger.handlers:
            continue

        handler = RotatingFileHandler(
            logs_dir / filename,
            maxBytes=5 * 1024 * 1024,   # 5 MB
            backupCount=3,               # .log.1 / .log.2 / .log.3
            encoding='utf-8',
        )
        handler.setFormatter(formatter)
        handler.setLevel(level)

        logger.addHandler(handler)
        logger.setLevel(level)
        logger.propagate = False         # CRITICO: evita duplicazione su solitario.log

    # ── Root logger: solitario.log (library logs: wx, PIL, urllib3) ────────────
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        root_handler = RotatingFileHandler(
            logs_dir / 'solitario.log',
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding='utf-8',
        )
        root_handler.setFormatter(formatter)
        root_logger.addHandler(root_handler)
        root_logger.setLevel(level)

    # ── Console handler (solo sviluppo) ────────────────────────────────────────
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(console_handler)

    # Sopprimi noise da librerie esterne
    logging.getLogger('PIL').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('wx').setLevel(logging.WARNING)
```

---

## Step 2 — Modifica `logger_setup.py` (thin wrapper)

**Percorso**: `src/infrastructure/logging/logger_setup.py`

Sostituire il contenuto con il thin wrapper che re-esporta tutto per backward compatibility.

```python
"""
Sistema logging centralizzato - Solitario Classico Accessibile

DEPRECATO: La logica reale è in categorized_logger.py (v3.2.0).
Mantenuto come thin wrapper per backward compatibility:
- acs_wx.py chiama ancora setup_logging() senza modifiche
- I test importano ancora LOGS_DIR, get_logger() senza modifiche

Version:
    v2.3.0: Initial implementation
    v3.2.0: Thin wrapper → categorized_logger.py
"""

import logging

# Re-export per backward compatibility
from .categorized_logger import (
    setup_categorized_logging,
    LOGS_DIR,       # Path("logs") — usato da test_logger_setup.py
    LOG_FILE,       # LOGS_DIR / "solitario.log" — usato da test_logger_setup.py
)


def setup_logging(level: int = logging.INFO, console_output: bool = False) -> None:
    """
    Configura logging globale dell'applicazione.

    DEPRECATED: Thin wrapper su setup_categorized_logging().
    Mantenuto per backward compatibility con acs_wx.py e test esistenti.

    Args:
        level:          Livello minimo (default: logging.INFO)
        console_output: Se True, log anche su console

    Example:
        >>> setup_logging(level=logging.DEBUG, console_output=True)
    """
    setup_categorized_logging(level=level, console_output=console_output)


def get_logger(name: str) -> logging.Logger:
    """
    Factory per logger specifici.

    Args:
        name: Nome logger (es: 'gameplay', 'window_controller')

    Returns:
        Logger configurato
    """
    return logging.getLogger(name)
```

---

## Step 3 — Modifica `__init__.py` (aggiungi export)

**Percorso**: `src/infrastructure/logging/__init__.py`

Aggiungere `setup_categorized_logging` agli export pubblici.

**Stato attuale**:
```python
from .logger_setup import setup_logging, get_logger

__all__ = ['setup_logging', 'get_logger']
```

**Dopo la modifica**:
```python
from .logger_setup import setup_logging, get_logger
from .categorized_logger import setup_categorized_logging, LOGS_DIR, LOG_FILE

__all__ = ['setup_logging', 'get_logger', 'setup_categorized_logging', 'LOGS_DIR', 'LOG_FILE']
```

---

## Step 4 — Modifica `game_logger.py` (4 righe)

**Percorso**: `src/infrastructure/logging/game_logger.py`

### Modifica 4a — Aggiungi `_timer_logger` (1 riga, in cima al file dopo gli altri logger)

**Punto di inserimento**: dopo la riga `_error_logger = logging.getLogger('error')` (riga ~28)

```python
# PRIMA (righe 26-28)
_game_logger = logging.getLogger('game')
_ui_logger = logging.getLogger('ui')
_error_logger = logging.getLogger('error')

# DOPO
_game_logger = logging.getLogger('game')
_ui_logger = logging.getLogger('ui')
_error_logger = logging.getLogger('error')
_timer_logger = logging.getLogger('timer')      # ← AGGIUNGI
```

### Modifica 4b — Funzione `timer_started` (1 riga)

```python
# PRIMA
def timer_started(duration: int) -> None:
    _game_logger.info(f"Timer started - Duration: {duration}s")

# DOPO
def timer_started(duration: int) -> None:
    _timer_logger.info(f"Timer started - Duration: {duration}s")
```

### Modifica 4c — Funzione `timer_expired` (1 riga)

```python
# PRIMA
def timer_expired() -> None:
    _game_logger.warning("Timer EXPIRED - Game auto-abandoned")

# DOPO
def timer_expired() -> None:
    _timer_logger.warning("Timer EXPIRED - Game auto-abandoned")
```

### Modifica 4d — Funzione `timer_paused` (1 riga)

```python
# PRIMA
def timer_paused(remaining: int) -> None:
    _game_logger.debug(f"Timer paused - Remaining: {remaining}s")

# DOPO
def timer_paused(remaining: int) -> None:
    _timer_logger.debug(f"Timer paused - Remaining: {remaining}s")
```

### Modifica 4e — Fix `keyboard_command` (1 riga — incongruenza esistente)

```python
# PRIMA (incongruente: comando tastiera finisce in game log invece di ui)
def keyboard_command(command: str, context: str) -> None:
    _game_logger.debug(f"Key command: {command} in context '{context}'")

# DOPO
def keyboard_command(command: str, context: str) -> None:
    _ui_logger.debug(f"Key command: {command} in context '{context}'")
```

---

## Step 5 — Verifica (nessuna modifica a `acs_wx.py`)

`acs_wx.py` chiama:
```python
from src.infrastructure.logging import setup_logging

setup_logging(
    level=logging.INFO,
    console_output=False
)
```

Questo continua a funzionare identico attraverso la catena:
```
setup_logging() [logger_setup.py thin wrapper]
  → setup_categorized_logging() [categorized_logger.py]
    → crea 4 handler (game_logic.log, ui_events.log, errors.log, timer.log)
    → crea root handler (solitario.log)
```

**Zero modifiche necessarie a `acs_wx.py`.**

---

## Step 6 — Verifica Test

```bash
pytest tests/unit/infrastructure/logging/ -v
```

I test esistenti continuano a funzionare perché:
- `_game_logger`, `_ui_logger`, `_error_logger` esistono ancora in `game_logger.py`
- `@patch('src.infrastructure.logging.game_logger._game_logger')` funziona identico
- `setup_logging` è ancora importabile da `src.infrastructure.logging`
- `LOGS_DIR` è ancora importabile da `src.infrastructure.logging`

**Unica cosa da verificare**: i test che testano le funzioni timer (`timer_started`, `timer_expired`, `timer_paused`) patchano `_game_logger` — dopo la modifica devono patchare `_timer_logger`. Verificare se esistono tali test.

```bash
grep -r "timer_started\|timer_expired\|timer_paused" tests/unit/infrastructure/logging/
```

Se trovati, aggiornare il patch target da `_game_logger` a `_timer_logger` per quelle specifiche funzioni.

---

## Step 7 — Test Manuale

Avviare l'applicazione e verificare la creazione dei file:

```
1. python acs_wx.py
2. Avvia una partita
3. Verificare in logs/ la presenza di:
   ✅ game_logic.log   (lifecycle partita, mosse)
   ✅ ui_events.log    (navigazione UI)
   ✅ errors.log       (vuoto se nessun errore)
   ✅ timer.log        (avvio timer se attivo)
   ✅ solitario.log    (wx library logs)
4. Verificare assenza di contenuto duplicato tra file
```

---

## Estensibilità Futura

Quando servirà aggiungere le categorie `profile`, `scoring`, `storage`:

**In `categorized_logger.py`** — decommentare le righe in `CATEGORIES`:
```python
CATEGORIES: dict[str, str] = {
    ...
    'profile':  'profiles.log',   # ← decommentare
    'scoring':  'scoring.log',    # ← decommentare
    'storage':  'storage.log',    # ← decommentare
}
```

**In `game_logger.py`** — aggiungere logger e funzioni helper:
```python
_profile_logger = logging.getLogger('profile')

def profile_created(profile_id: str, name: str) -> None:
    _profile_logger.info(f"Profile created: {profile_id} '{name}'")
```

**Zero altre modifiche necessarie** — il sistema si auto-configura al primo import.

---

## Rollback

Se qualcosa va storto dopo il deploy:

```python
# In acs_wx.py — rimuovere il wrapper e tornare alla chiamata diretta legacy
# from src.infrastructure.logging import setup_logging  # (invariato)

# In logger_setup.py — ripristinare l'implementazione originale da git
git checkout HEAD~1 -- src/infrastructure/logging/logger_setup.py
```

Il rollback è banale perché `acs_wx.py` non è stato toccato e `logger_setup.py` era l'unico entry point pubblico.

---

## Checklist Pre-Commit

- [ ] `categorized_logger.py` creato e funzionante
- [ ] `logger_setup.py` thin wrapper, re-export verificati
- [ ] `__init__.py` aggiornato con nuovi export
- [ ] `_timer_logger` aggiunto in `game_logger.py`
- [ ] 3 funzioni timer usano `_timer_logger`
- [ ] `keyboard_command` usa `_ui_logger`
- [ ] `pytest tests/unit/infrastructure/logging/ -v` → tutti pass
- [ ] Avvio manuale app → 5 file in `logs/`
- [ ] Nessun contenuto duplicato tra file log
- [ ] `pytest tests/ -v` completo → nessuna regressione

---

*Fine PLAN*  
*Prossimo step: implementazione (stimata 30 minuti)*
