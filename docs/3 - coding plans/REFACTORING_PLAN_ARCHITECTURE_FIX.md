# Piano di Refactoring: Correzione Architetturale Clean Architecture

**Data Creazione:** 2026-02-21  
**Versione:** 1.1  
**Ultima Revisione:** 2026-02-21 (allineato al codice reale)  
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


## ⚠️ ATTENZIONI CRITICHE PER L'AGENTE

### STOP 1: Step 1.4 - Import Lazy in game_engine.py
**CRITICO**: Le righe 1353/1354/1374/1525 contengono **import lazy DENTRO metodi**, NON top-level.
- **NON modificare senza prima care il contesto circostante**
- Questi import sono dentro metodi per evitare circular dependency
- Verifica che ogni modifica mantenga l'import DENTRO il metodo, non in cima al file
- Test obbligatorio: `pytest tests/test_game_engine.py -v` dopo modifica

### STOP 2: Step 1.6 - Eliminazione Directory
**ESEGUI SOLO DOPO** aver verificato con `git status` che:
- `src/presentation/dialogs/__init__.py` è vuoto (0 bytes)
- `src/presentation/widgets/__init__.py` è vuoto (0 bytes)
- Tutti i 6 dialog + 1 widget sono stati spostati con successo
- **grep -rn "from src.presentation.dialogs" src/** ritorna zero match

### STOP 3: Step 2.1 - Import game_logger
**`game_logger` è già importato** in tutti e 3 i file target:
- `wx_frame.py` — verifica riga ~20-30
- `wx_dialog_provider.py` — già presente riga 21
- `score_storage.py` — già presente riga 21
- **NON aggiungere import duplicati**

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

**File Coinvolti (verificati sul repository):**
```
src/presentation/dialogs/
├── abandon_dialog.py         → import wx  (runtime)
├── detailed_stats_dialog.py  → import wx  (runtime)
├── game_info_dialog.py       → import wx  (runtime)
├── last_game_dialog.py       → import wx  (runtime)
├── leaderboard_dialog.py     → import wx  (runtime)
└── victory_dialog.py         → import wx  (runtime)

src/presentation/widgets/
└── timer_combobox.py         → import wx  (runtime)
```

**Problema:** Tutti e 6 i dialog e il widget dipendono direttamente da `wxPython`, quindi appartengono al layer Infrastructure, non Presentation.

**Soluzione:** Spostare in `src/infrastructure/ui/`.

---

### 2. ⚠️ Statement `print()` in Codice di Produzione

**Print runtime reali (da correggere obbligatoriamente):**
- `src/infrastructure/ui/wx_frame.py` — righe 161, 166, 171, 182 (close event handler)
- `src/infrastructure/ui/wx_dialog_provider.py` — riga 529 (statistics report closed)
- `src/infrastructure/storage/score_storage.py` — riga 270 (error clearing scores)

**Print in docstring/esempi (non codice eseguito — lasciare invariate):**
- Tutte le occorrenze all'interno di blocchi `>>>` o `...` nei docstring (es. `game_engine.py`, `game_service.py`, `scoring_service.py`, `timer_combobox.py`, `report_formatter.py`)

**Problema:** Le `print()` runtime violano la regola "mai print in produzione" delle istruzioni operative del progetto.

**Soluzione:** Sostituire con `game_logger` centralizzato (`src.infrastructure.logging.game_logger`), già presente e usato nel progetto. **Non** introdurre `logging.getLogger` standard — usare sempre il logger di progetto.

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

**Azione:** Spostare **tutti e 6** i file da `presentation` a `infrastructure`:

```bash
# Da
src/presentation/dialogs/abandon_dialog.py
src/presentation/dialogs/detailed_stats_dialog.py
src/presentation/dialogs/game_info_dialog.py
src/presentation/dialogs/last_game_dialog.py
src/presentation/dialogs/leaderboard_dialog.py
src/presentation/dialogs/victory_dialog.py

# A
src/infrastructure/ui/dialogs/abandon_dialog.py
src/infrastructure/ui/dialogs/detailed_stats_dialog.py
src/infrastructure/ui/dialogs/game_info_dialog.py
src/infrastructure/ui/dialogs/last_game_dialog.py
src/infrastructure/ui/dialogs/leaderboard_dialog.py
src/infrastructure/ui/dialogs/victory_dialog.py
```

**Comando Git:**
```bash
git mv src/presentation/dialogs/abandon_dialog.py src/infrastructure/ui/dialogs/
git mv src/presentation/dialogs/detailed_stats_dialog.py src/infrastructure/ui/dialogs/
git mv src/presentation/dialogs/game_info_dialog.py src/infrastructure/ui/dialogs/
git mv src/presentation/dialogs/last_game_dialog.py src/infrastructure/ui/dialogs/
git mv src/presentation/dialogs/leaderboard_dialog.py src/infrastructure/ui/dialogs/
git mv src/presentation/dialogs/victory_dialog.py src/infrastructure/ui/dialogs/
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

#### 3. `src/application/game_engine.py` (import lazy a righe 1353, 1354, 1374, 1525)

**Cambio Import (lazy import dentro metodi):**
```python
# PRIMA
from src.presentation.dialogs.victory_dialog import VictoryDialog
from src.presentation.dialogs.abandon_dialog import AbandonDialog
from src.presentation.dialogs.detailed_stats_dialog import DetailedStatsDialog
from src.presentation.dialogs.last_game_dialog import LastGameDialog

# DOPO
from src.infrastructure.ui.dialogs.victory_dialog import VictoryDialog
from src.infrastructure.ui.dialogs.abandon_dialog import AbandonDialog
from src.infrastructure.ui.dialogs.detailed_stats_dialog import DetailedStatsDialog
from src.infrastructure.ui.dialogs.last_game_dialog import LastGameDialog
```

**Nota:** Questi import sono lazy (dentro metodi) — verificare il contesto prima di modificare.

---

#### 4. `src/infrastructure/ui/profile_menu_panel.py` (riga 686)

**Cambio Import (lazy import):**
```python
# PRIMA
from src.presentation.dialogs.detailed_stats_dialog import DetailedStatsDialog

# DOPO
from src.infrastructure.ui.dialogs.detailed_stats_dialog import DetailedStatsDialog
```

---

#### 5. Verifica di completezza (ricerca globale obbligatoria)

```bash
# Trova tutti i file che importano da presentation/dialogs
grep -rn "from src.presentation.dialogs" src/

# Trova tutti i file che importano da presentation/widgets
grep -rn "from src.presentation.widgets" src/
```

**Risultato atteso post-migrazione:** zero match in entrambe le ricerche.

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
from .game_info_dialog import GameInfoDialog
from .last_game_dialog import LastGameDialog
from .leaderboard_dialog import LeaderboardDialog
from .victory_dialog import VictoryDialog

__all__ = [
    'AbandonDialog',
    'DetailedStatsDialog',
    'GameInfoDialog',
    'LastGameDialog',
    'LeaderboardDialog',
    'VictoryDialog',
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

**Pre-condizione:** eseguire questo step SOLO dopo aver confermato che tutti e 6 i dialog e il widget siano stati spostati e che gli `__init__.py` di `presentation/dialogs/` e `presentation/widgets/` siano vuoti (lo sono già — verificato).

**Azione:** Eliminare le directory ora vuote in `presentation/`:

```bash
# Verificare che siano vuote (devono contenere solo __init__.py vuoto e __pycache__)
Get-ChildItem src/presentation/dialogs/
Get-ChildItem src/presentation/widgets/

# Eliminare via Git (include __init__.py vuoti)
git rm -r src/presentation/dialogs/
git rm -r src/presentation/widgets/
```

**Nota:** Non rimuovere `src/presentation/` — il layer esiste e contiene ancora `formatters/`.

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
│   ├── formatters/          ✅ Nessuna dipendenza da wx
│   │   └── report_formatter.py
│   ├── game_formatter.py    ✅ Nessuna dipendenza da wx
│   └── options_formatter.py ✅ Nessuna dipendenza da wx
│
├── infrastructure/
│   └── ui/
│       ├── dialogs/         ✅ SPOSTATO da presentation (6 file)
│       │   ├── __init__.py
│       │   ├── abandon_dialog.py
│       │   ├── detailed_stats_dialog.py
│       │   ├── game_info_dialog.py
│       │   ├── last_game_dialog.py
│       │   ├── leaderboard_dialog.py
│       │   └── victory_dialog.py
│       │
│       ├── widgets/         ✅ SPOSTATO da presentation
│       │   ├── __init__.py
│       │   └── timer_combobox.py
│       │
│       ├── factories/       ✅ GIÀ CORRETTO
│       ├── options_dialog.py
│       ├── profile_menu_panel.py
│       ├── wx_app.py
│       ├── wx_frame.py
│       ├── wx_dialog_provider.py
│       └── ...
```

---

## Fase 2: Refactoring Logging

### Priorità: **MEDIA**

### Step 2.1: Sostituire `print()` nei 3 file con occorrenze runtime

**Regola progetto:** usare sempre `game_logger` da `src.infrastructure.logging`, già presente, **non** introdurre `logging.getLogger` standard.

---

#### File 1: `src/infrastructure/ui/wx_frame.py` (righe 161, 166, 171, 182)

**Aggiungere in cima agli import (se non presente):**
```python
from src.infrastructure.logging import game_logger as log
```

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
def _on_close_event(self, event: wx.CloseEvent) -> None:
    log.debug("close_event", "Close event received (ALT+F4 or X button)")
    
    if not event.CanVeto():
        log.debug("close_event", "Close event cannot be vetoed (forced close)")
        self.Destroy()
        return
    
    log.debug("close_event", "Vetoing close event - showing confirmation dialog")
    event.Veto()
    
    if self.on_close is not None:
        self.on_close()
    else:
        log.warning("close_event", "No on_close callback registered - destroying frame")
        self.Destroy()
```

---

#### File 2: `src/infrastructure/ui/wx_dialog_provider.py` (riga 529)

**Aggiungere import se non presente:** `from src.infrastructure.logging import game_logger as log`  
(già presente a riga 21 — verificato)

**PRIMA:**
```python
            print("Statistics report closed")
```

**DOPO:**
```python
            log.debug("dialog_provider", "Statistics report closed")
```

---

#### File 3: `src/infrastructure/storage/score_storage.py` (riga 270)

**Aggiungere import se non presente:** `from src.infrastructure.logging import game_logger as log`  
(già presente a riga 21 — verificato)

**PRIMA:**
```python
            print(f"Error clearing scores: {e}")
```

**DOPO:**
```python
            log.error("score_storage", f"Error clearing scores: {e}", exc_info=True)
```

---

### Step 2.2: Verificare configurazione logging nell'entry point reale

**File:** `acs_wx.py` (entry point reale del progetto — `main.py` non esiste)

**Stato attuale (già corretto):** `acs_wx.py` usa già `setup_logging` e `game_logger` da `src.infrastructure.logging`:

```python
# acs_wx.py — import già presenti
from src.infrastructure.logging import setup_logging
from src.infrastructure.logging import game_logger as log
```

**Nessuna modifica strutturale richiesta** su questo file. Verificare solo che:
- `setup_logging()` venga chiamata prima di qualsiasi istanza di componente
- Il livello di log sia configurabile (es. via argomento `--verbose`)

**Per avviare l'applicazione:**
```bash
python acs_wx.py
```

---

### Step 2.3: Verifica post-intervento — nessun print runtime residuo

**Ricerca mirata (solo print eseguiti, non docstring):**
```bash
grep -rn "print(" src/ --include="*.py" | grep -v "__pycache__" | grep -v ">>>" | grep -v "\.\.\."
```

**Risultato atteso dopo correzioni Step 2.1:** zero occorrenze runtime.

**Nota:** Tutti i `print(` restanti nel codebase sono dentro docstring/esempi (blocchi `>>>` o `...`) — sono accettabili e non vanno rimossi (fanno parte della documentazione inline).

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
1. Avviare applicazione: `python acs_wx.py`
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

**1. Aggiornare path dei moduli:**

```
Find:    src.presentation.dialogs
Replace: src.infrastructure.ui.dialogs

Find:    src.presentation.widgets
Replace: src.infrastructure.ui.widgets
```

**2. Correggere firma di `ProfileService.ensure_guest_profile` (drift esistente):**

```
# Riga 1686 attuale (ERRATA):
#### `ensure_guest_profile() -> None`

# Correggere in:
#### `ensure_guest_profile() -> bool`
```

Return type reale nel codice: `-> bool` (`src/domain/services/profile_service.py`, riga 347).

---

#### `docs/ARCHITECTURE.md` — Rimozione riferimenti a file inesistenti

**Problema:** `docs/ARCHITECTURE.md` fa riferimento a `move_validator.py` in più sezioni (righe 209, 329, 390, 516, 558, 972), ma il file **non esiste**. La logica di validazione regole risiede in `src/domain/rules/solitaire_rules.py`.

**Azione:**
- Sostituire ogni occorrenza di `move_validator.py` con `solitaire_rules.py` nelle sezioni architetturali.
- Aggiornare la sezione descrittiva `MoveValidator` con il nome reale della classe/modulo.

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
git add src/infrastructure/ui/wx_dialog_provider.py
git add src/infrastructure/storage/score_storage.py
git commit -m "refactor: replace print() with game_logger in runtime code

- Replace print() runtime statements with game_logger semantico
- wx_frame.py: close event handler
- wx_dialog_provider.py: statistics report closed
- score_storage.py: error clearing scores
- game_logger già importato, nessuna nuova dipendenza"
```

**Commit 4 - Documentazione:**
```bash
git add docs/ARCHITECTURE.md
git add docs/API.md
git commit -m "docs: update architecture documentation after refactoring

- Update file organization diagrams
- Clarify Presentation vs Infrastructure layer separation
- Update API reference with new import paths (dialogs, widgets)
- Fix ensure_guest_profile return type: None -> bool in API.md
- Fix move_validator.py -> solitaire_rules.py in ARCHITECTURE.md"
```

---

## Checklist Finale

### Fase 1: Riorganizzazione
- [ ] Directory `src/infrastructure/ui/dialogs/` creata
- [ ] Directory `src/infrastructure/ui/widgets/` creata
- [ ] **6 file** spostati da `presentation/dialogs/` a `infrastructure/ui/dialogs/` (abandon, detailed_stats, game_info, last_game, leaderboard, victory)
- [ ] 1 file spostato da `presentation/widgets/` a `infrastructure/ui/widgets/`
- [ ] Import aggiornati in `wx_dialog_provider.py`
- [ ] Import aggiornati in `options_dialog.py` (riga 228 — lazy import)
- [ ] Import aggiornati in `game_engine.py` (righe 1353, 1354, 1374, 1525 — lazy imports)
- [ ] Import aggiornati in `profile_menu_panel.py` (riga 686 — lazy import)
- [ ] Ricerca globale grep eseguita: zero match residui `src.presentation.dialogs` / `src.presentation.widgets`
- [ ] `__init__.py` creati/aggiornati (con tutti e 6 i dialog)
- [ ] Directory vuote rimosse da `presentation/` (solo dopo verifica completezza)
- [ ] `formatters/`, `game_formatter.py`, `options_formatter.py` verificati e lasciati in `presentation/`

### Fase 2: Logging
- [ ] `print()` runtime sostituiti con `game_logger` in `wx_frame.py` (righe 161, 166, 171, 182)
- [ ] `print()` runtime sostituito con `game_logger` in `wx_dialog_provider.py` (riga 529)
- [ ] `print()` runtime sostituito con `game_logger` in `score_storage.py` (riga 270)
- [ ] Verifica grep post-intervento: zero print runtime residui in `src/`
- [ ] `acs_wx.py` (entry point reale) già usa `setup_logging` e `game_logger` — nessuna modifica necessaria

### Fase 3: Verifica e Documentazione
- [ ] Test suite eseguiti con successo (`pytest tests/ -v --cov=src --cov-report=term-missing`)
- [ ] Linter/mypy eseguiti senza errori (`mypy src/ --python-version 3.11`)
- [ ] Test manuale applicazione completato (`python acs_wx.py`)
- [ ] `docs/ARCHITECTURE.md` aggiornato (file organization + rimozione `move_validator.py`)
- [ ] `docs/API.md` aggiornato (import paths + `ensure_guest_profile -> bool`)
- [ ] `CHANGELOG.md` aggiornato sezione `[Unreleased]` con entry `refactor` e `fixed`
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

**Modalità Sicura (opzionale ma raccomandata):**
- Creare branch separato: `refactor/architecture-layer-separation`
- Eseguire ogni step sequenzialmente
- Verificare test suite dopo ogni fase (non solo al termine)
- Merge a main solo dopo validazione completa e `CHANGELOG.md` aggiornato

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
