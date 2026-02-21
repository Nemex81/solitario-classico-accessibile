# Rapporto di Analisi — DESIGN_categorized_logging.md

> **Data analisi**: 2026-02-21  
> **Analista**: GitHub Copilot (Claude Sonnet 4.6)  
> **Ramo**: sistema-log-categorizzati  
> **File analizzato**: `docs/2 - projects/DESIGN_categorized_logging.md`  
> **File di codice ispezionati**:
> - `src/infrastructure/logging/game_logger.py` (430 righe)
> - `src/infrastructure/logging/logger_setup.py` (150 righe)
> - `tests/unit/infrastructure/logging/test_game_logger.py` (127 righe)
> - `tests/unit/infrastructure/logging/test_logger_setup.py`

---

## 1. Validità Concettuale — ✅ VALIDA

L'idea centrale è solida: sostituire il monolite `solitario.log` con 7 file separati (`game_logic.log`, `ui_events.log`, ecc.) seguendo il pattern Paradox Interactive.

Le scelte tecniche sono tutte ben motivate:

- **RotatingFileHandler 5MB/3 backup**: basato su `logging.handlers` della stdlib Python, zero dipendenze esterne.
- **Flush immediato**: scelta corretta per affidabilità in caso di crash improvviso.
- **Decorator Pattern (Opzione A)**: la scelta migliore tra le 3 valutate — DRY, autodocumentante, Pythonic.
- **7 categorie**: coprono i layer esistenti del sistema (game, ui, error, timer, profile, scoring, storage).
- **API pubblica immutata**: il codice chiamante (`log.game_won()`, ecc.) non cambia.

Non ci sono errori logici nei flussi descritti (Scenario 1-4), né nei diagrammi di stato.

---

## 2. Coerenza con il Sistema Attuale — ⚠️ PARZIALMENTE COERENTE

### Cosa esiste già

Il file `src/infrastructure/logging/game_logger.py` usa già **3 logger named separati**:

```python
_game_logger = logging.getLogger('game')
_ui_logger = logging.getLogger('ui')
_error_logger = logging.getLogger('error')
```

Questo dimostra che la direzione è giusta — la struttura per categorie è già abbozzata nel codice attuale.

### Divergenza: categorizzazione `timer`

Le funzioni `timer_started`, `timer_expired`, `timer_paused` usano attualmente `_game_logger`, non un `_timer_logger`:

```python
def timer_started(duration: int) -> None:
    _game_logger.info(f"Timer started - Duration: {duration}s")  # ← va in _timer_logger

def timer_expired() -> None:
    _game_logger.warning("Timer EXPIRED - Game auto-abandoned")  # ← va in _timer_logger
```

Il design prevede una categoria `timer` separata, ma il codice la tratta come sottocategoria di `game`. Va allineato.

### Categorie mancanti nel codice

| Categoria (design) | Logger attuale | Funzioni esistenti |
|---|---|---|
| `game` | `_game_logger` | ✅ Presenti |
| `ui` | `_ui_logger` | ✅ Presenti |
| `error` | `_error_logger` | ✅ Presenti |
| `timer` | `_game_logger` ← **errato** | Timer functions da riclassificare |
| `profile` | *(assente)* | ❌ Nessuna funzione |
| `scoring` | *(assente)* | ❌ Nessuna funzione |
| `storage` | *(assente)* | ❌ Nessuna funzione |

**4 categorie su 7 necessitano lavoro**: una riclassificazione + 3 categorie da creare da zero con le relative funzioni helper.

---

## 3. Il Problema Critico del Decorator — ⚠️ MAL DOCUMENTATO

### Il design assume funzioni che restituiscono `str`

Il decorator proposto intercetta il **return value** della funzione per ottenere il messaggio da loggare:

```python
# Flusso previsto dal design
@log_to('game')
def game_won(elapsed_time, moves_count, score) -> str:
    return f"Game WON - Time: {elapsed_time}s, Moves: {moves_count}, Score: {score}"
    # Il decorator prende questa stringa e la logga in game_logic.log
```

### Il codice attuale NON restituisce nulla

Tutte le ~25 funzioni in `game_logger.py` logano **direttamente** e restituiscono `None`:

```python
# Codice ATTUALE (incompatibile con il decorator proposto)
def game_won(elapsed_time: int, moves_count: int, score: int) -> None:
    _game_logger.info(
        f"Game WON - Time: {elapsed_time}s, "
        f"Moves: {moves_count}, Score: {score}"
    )
    # Nessun return value → decorator non può intercettare nulla
```

### Entità reale della migrazione

Il documento afferma "API pubblica immutata — zero modifiche al codice chiamante". Questo è **vero per i caller esterni**, ma è fuorviante: tutte le ~25 funzioni interne di `game_logger.py` devono essere riscritte **completamente** cambiando:

1. La firma: `-> None` → `-> str`
2. Il corpo: da "logga direttamente" a "ritorna messaggio"
3. Rimuovere le chiamate dirette a `_game_logger.info(...)`, `_ui_logger.debug(...)`, ecc.

Il design descrive questo come "modifiche zero al codice chiamante" senza specificare che `game_logger.py` stesso è una riscrittura totale.

---

## 4. Caso Speciale: `error_occurred` Non Decorabile

La funzione `error_occurred` (righe 260-280 di `game_logger.py`) ha logica condizionale basata sulla presenza dell'eccezione:

```python
def error_occurred(error_type: str, details: str, exception: Optional[Exception] = None) -> None:
    if exception:
        _error_logger.error(
            f"ERROR [{error_type}]: {details}",
            exc_info=exception   # ← questo deve avvenire DURANTE la chiamata al logger
        )
    else:
        _error_logger.error(f"ERROR [{error_type}]: {details}")
```

Il parametro `exc_info` **non può essere trasportato in un return value stringa** — deve essere passato direttamente all'handler logger al momento della chiamata. Un decorator generico `@log_to('error')` che legge solo la stringa restituita perderebbe le informazioni del traceback.

Questa funzione è un **caso speciale** che richiede trattamento ad hoc nel PLAN:

- **Opzione A**: Il decorator accetta parametri opzionali aggiuntivi (`exc_info`)
- **Opzione B**: `error_occurred` bypassa il decorator e chiama direttamente l'handler
- **Opzione C**: La funzione ritorna una tupla `(messaggio, exc_info)` invece di una stringa

Nessuna delle tre opzioni è descritta nel design corrente.

---

## 5. Problema Infrastrutturale: Root Logger e Duplicazione Log

### Come funziona attualmente

Il `logger_setup.py` configura un **root logger unico** con un `RotatingFileHandler` su `solitario.log`:

```python
root_logger = logging.getLogger()  # root logger
root_logger.addHandler(file_handler)  # punta a solitario.log
```

Tutti i logger named (`_game_logger`, `_ui_logger`, ecc.) **ereditano dal root** per propagazione:

```python
_game_logger = logging.getLogger('game')
# Non ha handler propri → propaga al root → scrive su solitario.log
```

### Il problema dopo il refactoring

Se si aggiungono handler separati ai logger categorizzati **senza disabilitare la propagazione**, ogni entry finirà in **due file contemporaneamente**:

```
game_logger.info("victory") 
  → scrive in game_logic.log (handler nuovo)
  → propaga al root → scrive anche in solitario.log (handler vecchio)
  → DUPLICAZIONE
```

### Soluzione richiesta (non menzionata nel design)

Ogni logger categorizzato deve avere `propagate = False`:

```python
# In CategorizedLogger.__init__() — DA AGGIUNGERE AL PLAN
for category, filename in CATEGORIES.items():
    logger = logging.getLogger(category)
    logger.addHandler(RotatingFileHandler(f"logs/{filename}", ...))
    logger.propagate = False  # ← ESSENZIALE, impedisce duplicazione
```

Senza questa riga, il sistema funziona ma produce log duplicati — un bug silenzioso difficile da diagnosticare.

---

## 6. Incompatibilità Diretta con i Test Esistenti — ❌ RISCRITTURA OBBLIGATORIA

### Strategia di test attuale

Tutti i test in `test_game_logger.py` mockano le **variabili private interne** del modulo:

```python
@patch('src.infrastructure.logging.game_logger._game_logger')
def test_game_won_includes_stats(self, mock_logger):
    game_logger.game_won(elapsed_time=120, moves_count=45, score=850)
    mock_logger.info.assert_called_once()
    call_args = mock_logger.info.call_args[0][0]
    assert "WON" in call_args
```

### Perché smette di funzionare

Dopo il refactoring con decorator e registry centralizzato, le variabili `_game_logger`, `_ui_logger`, `_error_logger` **spariscono** (sostituite da `_HANDLERS: Dict[str, logging.Handler]` o simile). I `@patch` puntano a simboli inesistenti → tutti i test falliscono con `AttributeError`.

### Nuovo pattern di test richiesto

I test devono essere riscritti per verificare il **comportamento osservabile** (routing al file corretto) invece dell'implementazione interna:

```python
# Nuovo pattern — verifica via file temporanei
def test_game_won_routes_to_game_category(self, tmp_path):
    setup_categorized_logging(logs_dir=tmp_path)
    game_logger.game_won(elapsed_time=120, moves_count=45, score=850)
    
    log_content = (tmp_path / "game_logic.log").read_text()
    assert "WON" in log_content
    assert "120s" in log_content

# O verifica tramite mock del registry
def test_game_won_calls_game_handler(self):
    with patch.dict('src.infrastructure.logging.game_logger._HANDLERS', {...}):
        game_logger.game_won(120, 45, 850)
        # assert sul mock del handler 'game'
```

**File da riscrivere completamente**:
- `tests/unit/infrastructure/logging/test_game_logger.py`
- `tests/unit/infrastructure/logging/test_logger_setup.py`

---

## 7. Impatto su `logger_setup.py` — Riscrittura Necessaria

Il file attuale (`setup_logging()`) è incompatibile con il nuovo sistema:

```python
# ATTUALE — da sostituire
def setup_logging(level: int = logging.INFO, console_output: bool = False) -> None:
    file_handler = RotatingFileHandler(LOG_FILE, ...)  # unico file
    root_logger.addHandler(file_handler)               # root logger

# NUOVO — da progettare nel PLAN
def setup_categorized_logging(
    logs_dir: Path = LOGS_DIR,
    level: int = logging.INFO,
    console_output: bool = False
) -> None:
    for category, filename in CATEGORIES.items():
        logger = logging.getLogger(category)
        logger.addHandler(RotatingFileHandler(logs_dir / filename, ...))
        logger.propagate = False
    # Root logger: mantieni per library logs (PIL, urllib3, wx) → solitario.log
    # oppure rimuovi del tutto
```

Il punto di chiamata in `acs_wx.py` che oggi chiama `setup_logging()` deve essere aggiornato alla nuova firma.

---

## 8. Disallineamento Backup Count

| Sorgente | Valore |
|---|---|
| Design document | 3 backup (`maxBytes=5MB, backupCount=3`) |
| `logger_setup.py` attuale | 5 backup (`maxBytes=5MB, backupCount=5`) |

Risultato: il calcolo dello spazio disco nel design ("max 140MB = 7 × 20MB") è sbagliato se si usa il valore attuale di 5 backup. Va scelto e allineato in modo esplicito nel PLAN.

---

## 9. Riepilogo Problemi per Priorità

### Priorità ALTA (blocca il funzionamento corretto)

1. **~25 funzioni da riscrivere** — `game_logger.py` richiede migrazione completa da `-> None` (log diretto) a `-> str` (return message + decorator logga). Il design lo minimizza.
2. **`propagate = False` mancante** — senza questa riga si ha duplicazione silente su `solitario.log`.
3. **Test suite da riscrivere** — tutti i `@patch` su variabili private rotte dopo refactoring.

### Priorità MEDIA (degrada funzionalità)

4. **`error_occurred` caso speciale** — `exc_info=exception` non può essere gestito da decorator generico. Richiede soluzione dedicata.
5. **Funzioni mancanti per 3 categorie** — `profile`, `scoring`, `storage` non hanno helper corrispondenti. Il sistema di routing esiste ma non ha funzioni da chiamare.
6. **Timer riclassificazione** — `timer_started/expired/paused` usa `_game_logger`, va migrato a categoria `timer`.

### Priorità BASSA (cosmesi/manutenzione)

7. **Backup count disallineato** — 3 (design) vs 5 (codice). Scegliere e allineare.
8. **`solitario.log` legacy** — decidere se mantenerlo per library logs o eliminarlo completamente.

---

## 10. Giudizio Finale e Raccomandazioni

### Giudizio

Il design è **concettualmente solido e correttamente impostato** per la fase PLAN. La filosofia, l'architettura, le scelte tecniche e i flussi sono tutti validi. Il documento rispetta la Clean Architecture e i vincoli del progetto.

Tuttavia il design **sottostima significativamente la portata dell'implementazione**. Non è "aggiungere un decorator sopra le funzioni esistenti" — è una riscrittura coordinata su 4 file:

| File | Tipo di modifica |
|---|---|
| `src/infrastructure/logging/game_logger.py` | Riscrittura completa (~25 funzioni) |
| `src/infrastructure/logging/logger_setup.py` | Riscrittura completa (nuova architettura multi-handler) |
| `tests/unit/infrastructure/logging/test_game_logger.py` | Riscrittura completa (nuovo pattern di mock) |
| `tests/unit/infrastructure/logging/test_logger_setup.py` | Riscrittura completa |
| `acs_wx.py` (entry point) | Modifica puntuale (nuova firma `setup_categorized_logging`) |

### Stima realistica

- Design attuale dichiara: "modifiche zero al codice chiamante" ✅ (vero per caller esterni)
- Design sottintende: "poche modifiche interne" ❌ (in realtà è riscrittura di 4 file)
- Stima sessioni di lavoro: **2-3 sessioni** (non 1 come potrebbe sembrare)

### Cosa fare prima di scrivere il PLAN

1. Decidere come gestire `error_occurred` (le 3 opzioni sono nel paragrafo 4 di questo rapporto)
2. Decidere se mantenere `solitario.log` per library logs o eliminarlo
3. Confermare backup count: 3 o 5?
4. Decidere se aggiungere subito le funzioni helper mancanti (profile/scoring/storage) nel mismo PLAN o in un PLAN separato

---

## 11. Struttura Suggerita per `PLAN_categorized_logging.md`

Quando si redige il PLAN, includere obbligatoriamente:

```markdown
## Sezioni obbligatorie nel PLAN

1. Decisioni pre-implementazione
   - Strategia error_occurred (opzione A/B/C)
   - Backup count (3 o 5)
   - Root logger legacy (mantieni / rimuovi)
   
2. Schema CategorizedLogger
   - Signature CategorizedLogger.__init__()
   - Signature decorator @log_to()
   - CATEGORIES dict (tutte le 7 categorie)
   - Gestione propagate=False
   
3. Migration plan game_logger.py
   - Lista completa 25+ funzioni da riscrivere
   - Trattamento speciale error_occurred
   
4. Nuove funzioni helper (categorie mancanti)
   - profile_*: create_profile, load_profile, save_profile, delete_profile
   - scoring_*: score_calculated, penalty_applied, bonus_awarded
   - storage_*: file_read, file_write, file_error, file_corrupted
   
5. Testing strategy
   - Nuovo pattern (file temporanei vs mock registry)
   - Elenco test da riscrivere
   
6. Migration path (backward compat)
   - Come rollback se emergenza
   - Ordine di modifica file (per evitare rotture intermedie)
```

---

## 12. Strategia Low-Risk Raccomandata — ✅ APPROCCIO ALTERNATIVO

### 12.1 Perché Il Decorator È Over-Engineering

Dopo analisi approfondita del codice esistente, emerge un fatto cruciale: **il routing delle chiamate log è già risolto dalle variabili named logger esistenti** (`_game_logger`, `_ui_logger`, `_error_logger`). Il problema reale non è "come fare routing", ma **"come configurare gli handler per scrivere su file separati"**.

Il decorator pattern nel design originale stava risolvendo un problema inesistente:

```python
# Il sistema attuale GIÀ fa routing corretto
_game_logger = logging.getLogger('game')  # ← routing già dichiarato qui
_game_logger.info("Victory")  # ← scrive nel logger 'game'

# Il problema è che tutti i logger 'game', 'ui', 'error' condividono
# lo stesso handler (root logger → solitario.log)
```

Quando aggiungi un `RotatingFileHandler` specifico a `logging.getLogger('game')` con `propagate=False`, **tutte le chiamate a `_game_logger.info()` iniziano automaticamente a scrivere su `game_logic.log`**, senza toccare una singola riga nelle funzioni helper.

### 12.2 Architettura Low-Risk Proposta

#### File Nuovo: `categorized_logger.py`

```python
"""
Setup multi-file handler per logging categorizzato.
Zero decorator, routing tramite named loggers esistenti.
"""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Costanti (migrate da logger_setup.py)
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

CATEGORIES = {
    'game': 'game_logic.log',
    'ui': 'ui_events.log',
    'error': 'errors.log',
    'timer': 'timer.log',
    # profile/scoring/storage: aggiungi quando necessario
}

def setup_categorized_logging(
    logs_dir: Path = LOGS_DIR,
    level: int = logging.INFO,
    console_output: bool = False
) -> None:
    """
    Configura handler separati per categorie log.
    
    Args:
        logs_dir: Directory log (default: logs/)
        level: Livello minimo logging
        console_output: Se True, logga anche su console
    
    Note:
        - Crea 1 RotatingFileHandler per categoria (5MB, 3 backup)
        - Imposta propagate=False per evitare duplicazione
        - Mantiene root logger per library logs (wx, PIL, urllib3)
    """
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Setup handler per categorie
    for category, filename in CATEGORIES.items():
        logger = logging.getLogger(category)
        
        handler = RotatingFileHandler(
            logs_dir / filename,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,              # .log.1, .log.2, .log.3
            encoding='utf-8'
        )
        handler.setFormatter(formatter)
        handler.setLevel(level)
        
        logger.addHandler(handler)
        logger.setLevel(level)
        logger.propagate = False  # ← CRITICO: impedisce duplicazione
    
    # Root logger per library logs (wx, PIL, urllib3)
    root_logger = logging.getLogger()
    root_handler = RotatingFileHandler(
        logs_dir / 'solitario.log',
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding='utf-8'
    )
    root_handler.setFormatter(formatter)
    root_logger.addHandler(root_handler)
    root_logger.setLevel(level)
    
    # Console output opzionale
    if console_output:
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        root_logger.addHandler(console)
    
    # Silenzia library verbose
    logging.getLogger('PIL').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('wx').setLevel(logging.WARNING)
```

#### Modifiche a `logger_setup.py` (Thin Wrapper)

```python
"""
Backward compatibility wrapper per setup_logging().
"""
from src.infrastructure.logging.categorized_logger import (
    setup_categorized_logging,
    LOGS_DIR,
    CATEGORIES
)

# Re-export costanti per backward compat
LOG_FILE = LOGS_DIR / 'solitario.log'

def setup_logging(level: int = logging.INFO, console_output: bool = False) -> None:
    """
    DEPRECATED: usa setup_categorized_logging().
    Mantenuto per compatibilità con test esistenti.
    """
    setup_categorized_logging(level=level, console_output=console_output)
```

#### Modifiche a `game_logger.py` (MINIMALI)

```python
# AGGIUNGI in cima file (dopo import)
_timer_logger = logging.getLogger('timer')  # ← NUOVA categoria

# CAMBIA 3 funzioni timer
def timer_started(duration: int) -> None:
    _timer_logger.info(f"Timer started - Duration: {duration}s")  # era _game_logger

def timer_expired() -> None:
    _timer_logger.warning("Timer EXPIRED - Game auto-abandoned")  # era _game_logger

def timer_paused(remaining: int) -> None:
    _timer_logger.debug(f"Timer PAUSED - Remaining: {remaining}s")  # era _game_logger

# FIX keyboard_command (inconsistenza esistente)
def keyboard_command(command: str, context: str) -> None:
    _ui_logger.debug(f"Key command: {command} in context '{context}'")  # era _game_logger
```

**Totale modifiche `game_logger.py`**: 1 riga aggiunta + 4 righe cambiate = **5 righe**

#### Modifiche a `acs_wx.py` (ZERO)

```python
# INVARIATO — continua a chiamare setup_logging()
from src.infrastructure.logging.logger_setup import setup_logging

setup_logging(level=logging.INFO)
```

### 12.3 Confronto Strategia Decorator vs Low-Risk

| Aspetto | Decorator (Design Originale) | Low-Risk (Raccomandato) |
|---------|------------------------------|---------------------------|
| **File nuovi** | 2 (`categorized_logger.py`, `log_decorator.py`) | 1 (`categorized_logger.py`) |
| **Righe modificate `game_logger.py`** | ~25 funzioni riscritte (~300 righe) | 5 righe (4 funzioni) |
| **Test rotti** | 100% (variabili `_game_logger` spariscono) | 0% (variabili esistono ancora) |
| **API pubblica** | Immutata ✅ | Immutata ✅ |
| **Risultato finale** | 7 file log separati ✅ | 7 file log separati ✅ |
| **Complessità** | Alta (decorator + registry + riscrittura) | Bassa (solo setup handler) |
| **Rischio regressioni** | Alto (4 file riscritti) | Minimo (1 file nuovo, 2 file modifiche minori) |
| **Tempo implementazione** | 2-3 sessioni | 30 minuti |
| **Rollback** | Difficile (4 file da ripristinare) | Banale (cambia 1 import) |
| **Estendibilità futura** | Identica (aggiungi categoria = 2 righe) | Identica (aggiungi categoria = 2 righe) |

### 12.4 Risoluzione Problemi Critici

I 3 problemi a **priorità ALTA** identificati nella sezione 9 vengono risolti:

| Problema | Stato con Low-Risk |
|----------|--------------------|
| ~25 funzioni da riscrivere | ✅ **Scomparso** — funzioni invariate |
| `propagate = False` mancante | ✅ **Implementato** — riga presente nel setup |
| Test suite rotta | ✅ **Scomparso** — `_game_logger` esiste ancora |

Problemi priorità MEDIA:

| Problema | Stato con Low-Risk |
|----------|--------------------|
| `error_occurred` caso speciale | ✅ **Scomparso** — logga già direttamente, decorator non coinvolto |
| Funzioni mancanti 3 categorie | ⚠️ **Invariato** — profile/scoring/storage aggiunti in futuro quando necessario |
| Timer riclassificazione | ✅ **Risolto** — 3 funzioni cambiate da `_game_logger` a `_timer_logger` |

### 12.5 Decisioni Pre-Implementazione Risolte

**1. Gestione `error_occurred`**  
RISPOSTA: Nessun problema — la funzione logga già direttamente con `_error_logger.error(exc_info=exception)`, continua a funzionare identica.

**2. Backup count**  
RISPOSTA: **3 backup** (allineato al design, corretto dal valore legacy 5 in `logger_setup.py`).

**3. Root logger legacy**  
RISPOSTA: **Mantieni** — continua a scrivere `solitario.log` per library logs (wx, PIL, urllib3). Utile per debug dipendenze esterne.

**4. Funzioni helper mancanti**  
RISPOSTA: **PLAN separato futuro** — profile/scoring/storage non necessari ora, aggiungi quando le feature corrispondenti saranno implementate.

**5. `keyboard_command` inconsistenza**  
RISPOSTA: **Fix nella stessa sessione** — cambia da `_game_logger` a `_ui_logger` (1 riga).

### 12.6 Stima Implementazione Realistica

| Task | Tempo |
|------|-------|
| Crea `categorized_logger.py` | 15 min |
| Modifica `logger_setup.py` (thin wrapper) | 5 min |
| Modifica `game_logger.py` (5 righe) | 5 min |
| Test manuale (avvia app, verifica 7 file) | 5 min |
| Run test suite (verifica zero regressioni) | 5 min |
| **TOTALE** | **35 minuti** |

### 12.7 Piano Rollback

Se emergenza in produzione:

```python
# In logger_setup.py — torna al vecchio setup
def setup_logging(level: int = logging.INFO, console_output: bool = False) -> None:
    # Riattiva il codice legacy commentato (1 minuto)
    file_handler = RotatingFileHandler(LOG_FILE, ...)
    root_logger.addHandler(file_handler)
```

Tempo rollback: **1 minuto**  
Impatto: App torna a scrivere `solitario.log` monolitico, zero perdita funzionalità.

### 12.8 Raccomandazione Finale

**ADOTTA STRATEGIA LOW-RISK** perché:

✅ Risultato identico al design originale (7 file log separati)  
✅ Rischio minimo (5 righe modificate invece di 300)  
✅ Test esistenti continuano a funzionare senza modifiche  
✅ Implementazione 35 minuti (vs 2-3 sessioni)  
✅ Rollback banale (1 minuto)  
✅ Estendibilità identica (aggiungi categoria = 2 righe)  
✅ Zero over-engineering (usa infrastruttura Python logging nativa)  

**SCARTA STRATEGIA DECORATOR** perché:

❌ Rischio alto (riscrittura 4 file, 300+ righe cambiate)  
❌ Benefit marginale (routing già centralizzato nelle variabili)  
❌ Complessità non necessaria (decorator + registry custom)  
❌ Test suite da riscrivere completamente  
❌ Tempo implementazione 10x superiore  

---

*Fine rapporto*  
*Documento generato da analisi statica del codice + revisione design document*  
*Ultima revisione: 2026-02-21 (aggiunta sezione 12: Strategia Low-Risk)*
