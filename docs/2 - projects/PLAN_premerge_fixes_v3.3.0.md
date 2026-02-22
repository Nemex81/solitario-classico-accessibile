# Piano Fix Pre-Merge — Branch `sistema-log-categorizzati` → `main`
## Target release: v3.3.0

**Data redazione:** 2026-02-22
**Branch:** `sistema-log-categorizzati`
**Stato branch:** pronto al merge tranne le segnalazioni sotto
**Autore analisi:** Perplexity AI (revisione pre-merge)

---

## Contesto

Verifica pre-merge eseguita sul branch `sistema-log-categorizzati` in data 2026-02-22.
La feature principale (sistema logging multi-file categorizzato, Paradox-style) risulta
implementata correttamente e la documentazione è sostanzialmente allineata al codice.

Sono emerse 3 segnalazioni da risolvere prima del merge su `main`:

| # | Priorità | Area | Descrizione breve |
|---|---|---|---|
| 1 | 🔴 BLOCCANTE | `CHANGELOG.md` | Conflitto di merge non risolto (marker Git presenti) |
| 2 | 🟡 Minore | `categorized_logger.py` | Docstring versione non allineata (v3.2.0 → v3.3.0) |
| 3 | 🟠 Quality | `tests/infrastructure/` | Nessun test per il nuovo modulo logging |

---

## Task 1 — 🔴 BLOCCANTE: Risoluzione conflitto CHANGELOG.md

### Problema

Il file `CHANGELOG.md` contiene marker di conflitto Git non risolti nella sezione `[Unreleased]`:

```
<<<<<<< HEAD
### Added
- **Logging**: Sistema logging multi-file categorizzato Paradox-style (`v3.2.0` infrastruttura). ...
=======
### Added
- **Logging**: Sistema logging multi-file categorizzato (Paradox-style). ...
>>>>>>> 5ee89a39d3295b0d6b9b53aa51ceed727e8bc91f
```

Il conflitto è residuo del merge di allineamento eseguito il 2026-02-22 alle 00:41.
Le due versioni sono quasi identiche nel contenuto; la versione HEAD è più dettagliata.

Il file è **sintatticamente non valido** in questa forma. Qualsiasi tool CI, parser
Markdown, o script di release che lo legga fallirà.

### Soluzione

**File da modificare:** `CHANGELOG.md`

**Operazione 1 — Rimozione marker e scelta versione da mantenere:**

Eliminare l'intera sezione compresa tra `<<<<<<< HEAD` e `>>>>>>> 5ee89a39...` (inclusi
i marker), tenendo **solo il blocco HEAD** (la versione più dettagliata).

La sezione `[Unreleased]` corretta deve risultare così dopo la pulizia:

```markdown
## [Unreleased] — targeting v3.3.0

### Added

- **Logging**: Sistema logging multi-file categorizzato Paradox-style (`v3.2.0` infrastruttura).
  Sostituisce il monolite `solitario.log` con 4 file dedicati: `game_logic.log` (lifecycle
  partita, mosse), `ui_events.log` (navigazione UI, dialogs, TTS), `errors.log` (errori e
  warnings), `timer.log` (lifecycle timer). Root logger mantenuto per library logs (`wx`,
  `PIL`, `urllib3`) su `solitario.log`. Ogni file: `RotatingFileHandler` 5 MB, 3 backup,
  UTF-8. API pubblica (`setup_logging()`) completamente invariata — `acs_wx.py` e test
  esistenti zero modifiche. Strategia: Low-Risk Multi-Handler su named loggers Python
  esistenti (`propagate=False`).
- **`src/infrastructure/logging/categorized_logger.py`**: Nuovo modulo con
  `setup_categorized_logging()`, dict `CATEGORIES` (4 categorie attive + 3 future
  commentate: `profile`, `scoring`, `storage`), costanti `LOGS_DIR` / `LOG_FILE` /
  `LOG_FORMAT`.
- **`game_logger.py`**: Aggiunto `_timer_logger = logging.getLogger('timer')`;
  `timer_started`, `timer_expired`, `timer_paused` ora loggano su `timer.log`;
  `keyboard_command` ora logga su `ui_events.log` (fix incongruenza precedente: usava
  `_game_logger`).
```

**Operazione 2 — Aggiornamento link in fondo al file:**

Il footer del CHANGELOG ha la riga:
```
[Unreleased]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v3.2.2...HEAD
```

Al momento del merge va trasformata in due righe:
```markdown
[Unreleased]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v3.3.0...HEAD
[3.3.0]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v3.2.2...v3.3.0
```

### Verifica

Dopo la modifica, eseguire:
```bash
# Controllo visivo: nessuna riga deve contenere <<<<, ====, >>>>
grep -n "^<<<\|^===\|^>>>" CHANGELOG.md
# Output atteso: nessun risultato
```

### Commit suggerito

```
fix: resolve merge conflict in CHANGELOG.md [Unreleased] section
```

---

## Task 2 — 🟡 Minore: Allineamento docstring versione in categorized_logger.py

### Problema

Il file `src/infrastructure/logging/categorized_logger.py` riporta in due punti
la versione `v3.2.0` anziché `v3.3.0`:

1. Nel docstring del modulo (riga circa 35):
   ```python
   Version:
       v3.2.0: Initial implementation (replaces monolithic solitario.log)
   ```

2. Nel docstring della funzione `setup_categorized_logging()` (riga circa 80):
   ```python
   Version:
       v3.2.0: Initial implementation
   ```

Il modulo è stato creato in questo branch per la v3.3.0. La stringa `v3.2.0` è fuorviante
e contraddice il CHANGELOG (dove la feature è correttamente attributa a v3.3.0).

### Soluzione

**File da modificare:** `src/infrastructure/logging/categorized_logger.py`

Sostituire entrambe le occorrenze:

```python
# PRIMA
Version:
    v3.2.0: Initial implementation (replaces monolithic solitario.log)

# DOPO
Version:
    v3.3.0: Initial implementation (replaces monolithic solitario.log)
```

```python
# PRIMA (nella docstring di setup_categorized_logging)
Version:
    v3.2.0: Initial implementation

# DOPO
Version:
    v3.3.0: Initial implementation
```

### Commit suggerito

```
docs: align version strings in categorized_logger.py to v3.3.0
```

---

## Task 3 — 🟠 Quality: Test unitari per il sistema logging categorizzato

### Problema

In `tests/infrastructure/` non esiste alcun file di test per i nuovi moduli:
- `src/infrastructure/logging/categorized_logger.py` → **0 test**
- `src/infrastructure/logging/logger_setup.py` (thin wrapper) → **0 test**

Il CHANGELOG afferma che "API pubblica (`setup_logging()`) completamente invariata —
`acs_wx.py` e test esistenti zero modifiche", il che è vero ma significa che il
**nuovo comportamento non è validato automaticamente**.

In caso di refactor futuro o aggiunta di categorie, non c'è rete di sicurezza.

### Soluzione

**File da creare:** `tests/infrastructure/test_categorized_logger.py`

Il file deve essere autonomo, senza dipendenze da wx, usando solo `tmp_path` di pytest
(fixture standard, zero configurazione aggiuntiva). Va marcato `@pytest.mark.unit`.

```python
"""
Test unitari per src/infrastructure/logging/categorized_logger.py

Verifica:
- Creazione file di log per ogni categoria attiva
- Guard anti-doppia-registrazione (idempotenza)
- propagate=False su tutti i named logger (no duplicazioni su root)
- Retrocompatibilità wrapper setup_logging() -> setup_categorized_logging()
- Soppressione rumore librerie esterne (PIL, urllib3, wx)

Non richiede wx. Usa tmp_path di pytest per isolamento filesystem.
Marker: @pytest.mark.unit
"""

import logging
import pytest

from src.infrastructure.logging.categorized_logger import (
    CATEGORIES,
    setup_categorized_logging,
)
from src.infrastructure.logging.logger_setup import setup_logging


# ---------------------------------------------------------------------------
# Fixture: reset stato logging tra i test
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_logging():
    """
    Rimuove i handler aggiunti dai test dai named logger e dal root logger,
    garantendo isolamento tra i test.
    """
    yield
    # Cleanup: rimuovi handler da tutti i logger coinvolti
    for category in CATEGORIES:
        logger = logging.getLogger(category)
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
        logger.propagate = True  # ripristina default

    root = logging.getLogger()
    for handler in root.handlers[:]:
        handler.close()
        root.removeHandler(handler)


# ---------------------------------------------------------------------------
# Test 1: creazione file di log per ogni categoria attiva
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_setup_creates_log_files_for_all_categories(tmp_path):
    """
    setup_categorized_logging() deve creare un file .log per ogni categoria
    in CATEGORIES, più solitario.log per il root logger.
    """
    setup_categorized_logging(logs_dir=tmp_path)

    for category, filename in CATEGORIES.items():
        log_file = tmp_path / filename
        assert log_file.exists(), (
            f"File di log mancante per categoria '{category}': {log_file}"
        )

    # Root logger
    assert (tmp_path / "solitario.log").exists(), (
        "solitario.log mancante (root logger)"
    )


# ---------------------------------------------------------------------------
# Test 2: guard anti-doppia-registrazione (idempotenza)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_setup_idempotent_no_duplicate_handlers(tmp_path):
    """
    Chiamare setup_categorized_logging() due volte non deve aggiungere
    handler duplicati ai named logger. Ogni logger deve avere esattamente 1 handler.
    """
    setup_categorized_logging(logs_dir=tmp_path)
    setup_categorized_logging(logs_dir=tmp_path)  # seconda chiamata

    for category in CATEGORIES:
        logger = logging.getLogger(category)
        assert len(logger.handlers) == 1, (
            f"Logger '{category}' ha {len(logger.handlers)} handler dopo doppia init "
            f"(atteso: 1)"
        )


# ---------------------------------------------------------------------------
# Test 3: propagate=False su tutti i named logger
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_setup_sets_propagate_false_on_all_category_loggers(tmp_path):
    """
    Ogni named logger per categoria deve avere propagate=False per evitare
    che i messaggi vengano duplicati su solitario.log (root logger).
    """
    setup_categorized_logging(logs_dir=tmp_path)

    for category in CATEGORIES:
        logger = logging.getLogger(category)
        assert logger.propagate is False, (
            f"Logger '{category}' ha propagate=True (deve essere False)"
        )


# ---------------------------------------------------------------------------
# Test 4: retrocompatibilità wrapper setup_logging()
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_setup_logging_wrapper_creates_same_files(tmp_path):
    """
    setup_logging() in logger_setup.py è un thin wrapper su
    setup_categorized_logging(). Deve produrre gli stessi file di log.
    """
    setup_logging(logs_dir=tmp_path)

    for category, filename in CATEGORIES.items():
        log_file = tmp_path / filename
        assert log_file.exists(), (
            f"Wrapper setup_logging() non ha creato '{filename}' per '{category}'"
        )


# ---------------------------------------------------------------------------
# Test 5: soppressione rumore librerie esterne
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_setup_suppresses_external_library_loggers(tmp_path):
    """
    Dopo setup_categorized_logging(), i logger di librerie esterne (PIL,
    urllib3, wx) devono avere livello >= WARNING per non inquinare i log.
    """
    setup_categorized_logging(logs_dir=tmp_path)

    for lib in ('PIL', 'urllib3', 'wx'):
        lib_logger = logging.getLogger(lib)
        assert lib_logger.level >= logging.WARNING, (
            f"Logger '{lib}' ha livello {lib_logger.level} "
            f"(atteso >= {logging.WARNING})"
        )
```

### Note implementative

- La fixture `reset_logging` con `autouse=True` garantisce che ogni test parta
  con un registro logging pulito. Senza di essa i test si contaminano a vicenda
  perché il modulo `logging` di Python è un singleton di processo.
- I test usano `tmp_path` (pytest built-in): nessun file viene scritto nella
  directory del progetto durante i test.
- Zero import da `wx` — il file è CI-safe senza Xvfb e senza `@pytest.mark.gui`.
- La fixture `logger_setup.py` deve esporre `setup_logging(logs_dir=...)` con
  la stessa signature di `setup_categorized_logging()`. Verificare prima di
  eseguire il test 4.

### Verifica

```bash
# Esegui solo i nuovi test (headless, niente GUI)
pytest tests/infrastructure/test_categorized_logger.py -v

# Output atteso: 5 passed
```

### Commit suggerito

```
test: add unit tests for categorized logging system (5 tests, CI-safe)
```

---

## Checklist finale pre-merge

Prima di aprire la PR verso `main`, verificare nell'ordine:

- [ ] **Task 1** — `CHANGELOG.md` privo di marker `<<<`, `===`, `>>>` (`grep` pulito)
- [ ] **Task 1** — Link footer CHANGELOG aggiornato con `v3.3.0`
- [ ] **Task 2** — Docstring `categorized_logger.py` riporta `v3.3.0`
- [ ] **Task 3** — File `tests/infrastructure/test_categorized_logger.py` presente
- [ ] **Task 3** — `pytest tests/infrastructure/test_categorized_logger.py` → 5 passed
- [ ] **Smoke test** — `pytest -m "not gui"` passa senza regressioni
- [ ] **PR title** — Esempio: `feat: sistema logging categorizzato v3.3.0 (#XX)`
- [ ] **PR body** — Linkare questo documento e il `DESIGN_categorized_logging.md`

---

## Stima effort

| Task | Tipo | Stima |
|---|---|---|
| Task 1 — Conflict CHANGELOG | Editing manuale | 5 minuti |
| Task 2 — Docstring versione | Editing manuale | 2 minuti |
| Task 3 — Test logging | Scrittura codice | 20-30 minuti |
| Verifica smoke test | Esecuzione pytest | 5 minuti |
| **Totale** | | **~15-25 minuti** |

---

*Piano generato da Perplexity AI in data 2026-02-22 — revisione pre-merge branch `sistema-log-categorizzati`.*
