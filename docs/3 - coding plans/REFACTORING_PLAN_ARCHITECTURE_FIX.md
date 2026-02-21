# Piano di Refactoring: Correzione Architetturale Clean Architecture

**Data Creazione:** 2026-02-21  
**Versione:** 1.0  
**Stato:** Da Implementare  
**Priorità:** CRITICA ⚠️

---

## Indice

1. [Panoramica](#panoramica)
2. [Problemi Identificati](#problemi-identificati)
3. [Fase 1: Riorganizzazione Layer Presentation/Infrastructure](#fase-1-riorganizzazione-layer-presentationinfrastructure)
4. [Fase 2: Refactoring Logging](#fase-2-refactoring-logging)
5. [Fase 3: Verifica e Validazione](#fase-3-verifica-e-validazione)
6. [Checklist Finale](#checklist-finale)

---

## Panoramica

### Obiettivo
Correggere violazioni dell'architettura Clean Architecture nel progetto, separando correttamente i layer Presentation e Infrastructure.

### Problema Principale
I moduli in `src/presentation/dialogs/` e `src/presentation/widgets/` importano direttamente `wx` (dipendenza concreta da framework UI), quindi appartengono al layer **Infrastructure**, non **Presentation**.

### Principio Architetturale Violato
**Dependency Rule:** Il layer Presentation non deve dipendere da framework/librerie concrete (wx, tkinter, pygame, ecc.). Deve dipendere solo da astrazioni (interfacce/protocolli).

### Impatto
- **Severità:** CRITICA
- **Effetto:** Viola principi SOLID (Dependency Inversion) e rende difficile testare/sostituire UI
- **Urgenza:** Alta (blocca future evoluzioni architetturali)

---

## Problemi Identificati

### 1. ❌ Violazione Separazione Layer (CRITICO)

**File Coinvolti:**
```
src/presentation/dialogs/
├── abandon_dialog.py       → import wx
├── detailed_stats_dialog.py → import wx
├── last_game_dialog.py     → import wx
└── leaderboard_dialog.py   → import wx

src/presentation/widgets/
└── timer_combobox.py       → import wx
```

**Problema:** Questi moduli dipendono direttamente da `wxPython`, quindi appartengono a Infrastructure.

**Soluzione:** Spostare in `src/infrastructure/ui/`.

---

### 2. ⚠️ Statement `print()` in Codice di Produzione

**File Coinvolti:**
- `src/infrastructure/ui/wx_frame.py` (2 occorrenze di debug)
- Altri file in `src/` (16 totali trovati)

**Problema:** Le `print()` vanno bene per debug locale, ma in produzione dovrebbero usare `logging`.

**Soluzione:** Sostituire con `logging.Logger`.

---

## Fase 1: Riorganizzazione Layer Presentation/Infrastructure

### Priorità: **MASSIMA** ⚠️

### Step 1.1: Creare Nuove Directory

**Azione:** Creare directory in `src/infrastructure/ui/`:

```bash
mkdir -p src/infrastructure/ui/dialogs
mkdir -p src/infrastructure/ui/widgets
```

**Verificare:**
```
src/infrastructure/ui/
├── dialogs/          ← NUOVO
├── widgets/          ← NUOVO
├── factories/        ← GIÀ ESISTENTE
├── wx_app.py
├── wx_frame.py
└── ...
```

---

### Step 1.2: Spostare File `dialogs/`

**Azione:** Spostare 4 file da `presentation` a `infrastructure`:

```bash
# Da
src/presentation/dialogs/abandon_dialog.py
src/presentation/dialogs/detailed_stats_dialog.py
src/presentation/dialogs/last_game_dialog.py
src/presentation/dialogs/leaderboard_dialog.py

# A
src/infrastructure/ui/dialogs/abandon_dialog.py
src/infrastructure/ui/dialogs/detailed_stats_dialog.py
src/infrastructure/ui/dialogs/last_game_dialog.py
src/infrastructure/ui/dialogs/leaderboard_dialog.py
```

**Comando Git:**
```bash
git mv src/presentation/dialogs/abandon_dialog.py src/infrastructure/ui/dialogs/
git mv src/presentation/dialogs/detailed_stats_dialog.py src/infrastructure/ui/dialogs/
git mv src/presentation/dialogs/last_game_dialog.py src/infrastructure/ui/dialogs/
git mv src/presentation/dialogs/leaderboard_dialog.py src/infrastructure/ui/dialogs/
```

---

### Step 1.3: Spostare File `widgets/`

**Azione:** Spostare 1 file da `presentation` a `infrastructure`:

```bash
# Da
src/presentation/widgets/timer_combobox.py

# A
src/infrastructure/ui/widgets/timer_combobox.py
```

**Comando Git:**
```bash
git mv src/presentation/widgets/timer_combobox.py src/infrastructure/ui/widgets/
```

---

### Step 1.4: Aggiornare Import nei File Dipendenti

**File da Modificare:**

#### 1. `src/infrastructure/ui/wx_dialog_provider.py`

**Cambio Import:**
```python
# PRIMA
from src.presentation.dialogs.abandon_dialog import AbandonDialog
from src.presentation.dialogs.detailed_stats_dialog import DetailedStatsDialog
from src.presentation.dialogs.last_game_dialog import LastGameDialog
from src.presentation.dialogs.leaderboard_dialog import LeaderboardDialog

# DOPO
from src.infrastructure.ui.dialogs.abandon_dialog import AbandonDialog
from src.infrastructure.ui.dialogs.detailed_stats_dialog import DetailedStatsDialog
from src.infrastructure.ui.dialogs.last_game_dialog import LastGameDialog
from src.infrastructure.ui.dialogs.leaderboard_dialog import LeaderboardDialog
```

**Posizione:** Righe 8-11 (circa)

---

#### 2. `src/infrastructure/ui/options_dialog.py`

**Cambio Import:**
```python
# PRIMA
from src.presentation.widgets.timer_combobox import TimerComboBox

# DOPO
from src.infrastructure.ui.widgets.timer_combobox import TimerComboBox
```

**Posizione:** Riga 8 (circa)

---

#### 3. Altri file potenzialmente coinvolti

**Ricerca Globale:**
```bash
# Trova tutti i file che importano da presentation/dialogs
grep -r "from src.presentation.dialogs" src/

# Trova tutti i file che importano da presentation/widgets
grep -r "from src.presentation.widgets" src/
```

**Azione:** Per ogni file trovato, aggiornare gli import come sopra.

---

### Step 1.5: Aggiornare `__init__.py` (se esistono)

**Verificare presenza:**
```bash
# Controllare se esistono file __init__.py
ls src/presentation/dialogs/__init__.py
ls src/presentation/widgets/__init__.py
ls src/infrastructure/ui/dialogs/__init__.py
ls src/infrastructure/ui/widgets/__init__.py
```

**Se esistono:**

#### `src/infrastructure/ui/dialogs/__init__.py`
```python
"""Dialog implementations based on wxPython.

This module provides concrete dialog implementations for the application.
All dialogs depend on wxPython and belong to Infrastructure layer.
"""

from .abandon_dialog import AbandonDialog
from .detailed_stats_dialog import DetailedStatsDialog
from .last_game_dialog import LastGameDialog
from .leaderboard_dialog import LeaderboardDialog

__all__ = [
    'AbandonDialog',
    'DetailedStatsDialog',
    'LastGameDialog',
    'LeaderboardDialog',
]
```

#### `src/infrastructure/ui/widgets/__init__.py`
```python
"""Custom wxPython widgets for the application.

This module provides reusable UI widgets based on wxPython.
Belongs to Infrastructure layer due to concrete wx dependency.
"""

from .timer_combobox import TimerComboBox

__all__ = ['TimerComboBox']
```

---

### Step 1.6: Rimuovere Directory Vuote

**Azione:** Eliminare le directory vuote in `presentation/`:

```bash
# Verificare che siano vuote
ls -la src/presentation/dialogs/
ls -la src/presentation/widgets/

# Se vuote, eliminare
rmdir src/presentation/dialogs/
rmdir src/presentation/widgets/
```

**Comando Git:**
```bash
git rm -r src/presentation/dialogs/
git rm -r src/presentation/widgets/
```

---

### Step 1.7: Mantenere `formatters/` in Presentation

**Verificare che `formatters/` NON dipenda da wx:**

```bash
grep -r "import wx" src/presentation/formatters/
```

**Risultato Atteso:** Nessun match (formatters è corretto in Presentation).

**Se trovato wx:** Ripetere procedura di spostamento anche per `formatters/`.

---

### Step 1.8: Verificare Struttura Finale

**Struttura Attesa:**

```
src/
├── presentation/
│   └── formatters/          ✅ Nessuna dipendenza da wx
│       └── report_formatter.py
│
├── infrastructure/
│   └── ui/
│       ├── dialogs/         ✅ SPOSTATO da presentation
│       │   ├── __init__.py
│       │   ├── abandon_dialog.py
│       │   ├── detailed_stats_dialog.py
│       │   ├── last_game_dialog.py
│       │   └── leaderboard_dialog.py
│       │
│       ├── widgets/         ✅ SPOSTATO da presentation
│       │   ├── __init__.py
│       │   └── timer_combobox.py
│       │
│       ├── factories/       ✅ GIÀ CORRETTO
│       ├── wx_app.py
│       ├── wx_frame.py
│       └── ...
```

---

## Fase 2: Refactoring Logging

### Priorità: **MEDIA**

### Step 2.1: Sostituire `print()` in `wx_frame.py`

**File:** `src/infrastructure/ui/wx_frame.py`

**Righe da Modificare:** Circa righe 160-170

**PRIMA:**
```python
def _on_close_event(self, event: wx.CloseEvent) -> None:
    print("[Frame] Close event received (ALT+F4 or X button)")
    
    if not event.CanVeto():
        print("[Frame] Close event cannot be vetoed (forced close)")
        self.Destroy()
        return
    
    print("[Frame] Vetoing close event - showing confirmation dialog")
    event.Veto()
    
    if self.on_close is not None:
        self.on_close()
    else:
        print("[Frame] No on_close callback registered - destroying frame")
        self.Destroy()
```

**DOPO:**
```python
import logging

logger = logging.getLogger(__name__)


def _on_close_event(self, event: wx.CloseEvent) -> None:
    logger.debug("Close event received (ALT+F4 or X button)")
    
    if not event.CanVeto():
        logger.debug("Close event cannot be vetoed (forced close)")
        self.Destroy()
        return
    
    logger.debug("Vetoing close event - showing confirmation dialog")
    event.Veto()
    
    if self.on_close is not None:
        self.on_close()
    else:
        logger.warning("No on_close callback registered - destroying frame")
        self.Destroy()
```

**Cambiamenti:**
1. Aggiungere `import logging` in cima al file
2. Aggiungere `logger = logging.getLogger(__name__)` dopo gli import
3. Sostituire tutti i `print()` con `logger.debug()` o `logger.warning()`

---

### Step 2.2: Configurare Logging nel Main Entry Point

**File:** `main.py` (o entry point principale)

**Aggiungere configurazione logging:**

```python
import logging
import sys

def setup_logging(debug: bool = False) -> None:
    """Configure logging for the application.
    
    Args:
        debug: Enable debug logging (default: False)
    """
    level = logging.DEBUG if debug else logging.INFO
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger('wx').setLevel(logging.WARNING)


def main():
    # Setup logging
    setup_logging(debug=False)  # Set to True for debug mode
    
    # Rest of main logic...
    pass
```

---

### Step 2.3: Verificare Altri File con `print()`

**Ricerca Globale:**
```bash
grep -rn "print(" src/ --include="*.py" | grep -v "__pycache__" | grep -v ".pyc"
```

**Per ogni file trovato:**
1. Verificare se è codice di debug o produzione
2. Se produzione: sostituire con `logging`
3. Se debug/test: valutare se mantenere o rimuovere

**File Prioritari:**
- `src/application/` (logica business)
- `src/domain/` (core domain)
- `src/infrastructure/` (adapter esterni)

**File Non Prioritari:**
- `tests/` (print() accettabili nei test)
- Script di utility/tools

---

## Fase 3: Verifica e Validazione

### Priorità: **ALTA**

### Step 3.1: Eseguire Test Suite

**Comando:**
```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

**Verificare:**
- ✅ Tutti i test passano
- ✅ Nessun import error
- ✅ Coverage non diminuita

**Se test falliscono:**
1. Controllare traceback per individuare import mancanti
2. Verificare che tutti gli import siano stati aggiornati
3. Ripetere Step 1.4 se necessario

---

### Step 3.2: Verificare Import con Linter

**Comando:**
```bash
# Verificare import non utilizzati
flake8 src/ --select=F401

# Verificare import mancanti
mypy src/ --ignore-missing-imports
```

**Azione:** Correggere eventuali warning/errori rilevati.

---

### Step 3.3: Test Manuale Applicazione

**Procedura:**
1. Avviare applicazione: `python main.py`
2. Verificare che tutte le dialog si aprano correttamente:
   - Menu → Nuova Partita
   - Menu → Statistiche
   - Menu → Classifica
   - Durante partita → Abbandona
3. Verificare widget timer in opzioni
4. Verificare log output in console (dopo Step 2.2)

**Se crash/errori:**
1. Controllare traceback
2. Verificare import nei file indicati dal traceback
3. Correggere e riprovare

---

### Step 3.4: Aggiornare Documentazione

**File da Aggiornare:**

#### `docs/ARCHITECTURE.md`

**Sezione da Modificare:** "File Organization"

**PRIMA:**
```markdown
src/presentation/
├── dialogs/
├── widgets/
└── formatters/
```

**DOPO:**
```markdown
src/presentation/
└── formatters/          # UI-agnostic formatters (no framework dependency)

src/infrastructure/ui/
├── dialogs/             # wxPython-based dialogs (moved from presentation)
├── widgets/             # wxPython-based widgets (moved from presentation)
└── factories/           # Widget factories
```

**Aggiungere nota:**
```markdown
### Layer Separation Clarification

**Presentation Layer:**
- Contains UI-agnostic logic (formatters, view models, etc.)
- No direct dependency on UI frameworks (wx, tkinter, pygame, etc.)
- Depends only on abstractions (interfaces/protocols)

**Infrastructure Layer (UI):**
- Contains concrete UI implementations (dialogs, widgets, frames)
- Depends on specific UI frameworks (wxPython in this case)
- Implements interfaces defined in Presentation/Application layers
```

---

#### `docs/API.md`

**Aggiornare path dei moduli:**

**Ricerca e Sostituzione:**
```
Find:    src.presentation.dialogs
Replace: src.infrastructure.ui.dialogs

Find:    src.presentation.widgets
Replace: src.infrastructure.ui.widgets
```

---

### Step 3.5: Commit Changes

**Strategia di Commit:**

**Commit 1 - Riorganizzazione File:**
```bash
git add src/infrastructure/ui/dialogs/
git add src/infrastructure/ui/widgets/
git commit -m "refactor: move dialogs and widgets from presentation to infrastructure

- Move src/presentation/dialogs/ to src/infrastructure/ui/dialogs/
- Move src/presentation/widgets/ to src/infrastructure/ui/widgets/
- Reason: These modules depend directly on wxPython framework

BREAKING CHANGE: Import paths changed for dialogs and widgets"
```

**Commit 2 - Aggiornamento Import:**
```bash
git add src/infrastructure/ui/wx_dialog_provider.py
git add src/infrastructure/ui/options_dialog.py
# ... altri file modificati
git commit -m "refactor: update imports after dialogs/widgets relocation

- Update import paths to src.infrastructure.ui.dialogs
- Update import paths to src.infrastructure.ui.widgets
- Ensure all references are updated consistently"
```

**Commit 3 - Refactoring Logging:**
```bash
git add src/infrastructure/ui/wx_frame.py
git add main.py  # se modificato
git commit -m "refactor: replace print() with logging in wx_frame

- Add logging configuration in main entry point
- Replace debug print() statements with logger.debug()
- Improve production logging consistency"
```

**Commit 4 - Documentazione:**
```bash
git add docs/ARCHITECTURE.md
git add docs/API.md
git commit -m "docs: update architecture documentation after refactoring

- Update file organization diagrams
- Clarify Presentation vs Infrastructure layer separation
- Update API reference with new import paths"
```

---

## Checklist Finale

### Fase 1: Riorganizzazione
- [ ] Directory `src/infrastructure/ui/dialogs/` creata
- [ ] Directory `src/infrastructure/ui/widgets/` creata
- [ ] 4 file spostati da `presentation/dialogs/` a `infrastructure/ui/dialogs/`
- [ ] 1 file spostato da `presentation/widgets/` a `infrastructure/ui/widgets/`
- [ ] Import aggiornati in `wx_dialog_provider.py`
- [ ] Import aggiornati in `options_dialog.py`
- [ ] Altri import verificati con grep
- [ ] `__init__.py` creati/aggiornati
- [ ] Directory vuote rimosse da `presentation/`
- [ ] `formatters/` verificato e lasciato in `presentation/`

### Fase 2: Logging
- [ ] `print()` sostituiti con `logging` in `wx_frame.py`
- [ ] Configurazione logging aggiunta in main entry point
- [ ] Altri file con `print()` valutati e corretti (se necessario)

### Fase 3: Verifica
- [ ] Test suite eseguiti con successo
- [ ] Linter/mypy eseguiti senza errori
- [ ] Test manuale applicazione completato
- [ ] `docs/ARCHITECTURE.md` aggiornato
- [ ] `docs/API.md` aggiornato
- [ ] Commit separati creati per ogni fase

### Validazione Finale
- [ ] ✅ Architettura conforme a Clean Architecture
- [ ] ✅ Dependency Rule rispettata
- [ ] ✅ Logging configurato correttamente
- [ ] ✅ Documentazione allineata con codice
- [ ] ✅ Test suite verde
- [ ] ✅ Nessun breaking change non documentato

---

## Note Implementative

### Per l'Agente di Codifica GitHub

**Priorità di Esecuzione:**
1. **FASE 1 COMPLETA** (Step 1.1 → 1.8) - NON SALTARE NESSUNO STEP
2. **FASE 3.1** (Test Suite) - BLOCCARE SE FALLISCONO
3. **FASE 2** (Logging) - Opzionale ma raccomandato
4. **FASE 3.2-3.5** (Verifica completa e documentazione)

**Modalità Sicura:**
- Creare branch separato: `refactor/architecture-layer-separation`
- Eseguire ogni step sequenzialmente
- Verificare dopo ogni commit
- Merge a main solo dopo validazione completa

**In Caso di Errori:**
1. NON procedere al prossimo step
2. Analizzare traceback completo
3. Verificare import path
4. Testare modulo isolato prima di proseguire

---

## Riferimenti

- **Clean Architecture:** Robert C. Martin - "Clean Architecture: A Craftsman's Guide to Software Structure and Design"
- **SOLID Principles:** Dependency Inversion Principle (DIP)
- **Python Logging:** https://docs.python.org/3/library/logging.html
- **wxPython Best Practices:** https://wxpython.org/Phoenix/docs/html/

---

**Fine del Piano di Refactoring**
