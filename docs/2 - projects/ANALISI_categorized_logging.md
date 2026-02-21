# Rapporto di Analisi — DESIGN_categorized_logging.md

> **Data analisi**: 2026-02-21  
> **Analista**: GitHub Copilot (Claude Sonnet 4.6)  
> **Ramo**: main  
> **File analizzato**: `docs/2 - projects/DESIGN_categorized_logging.md`  
> **File di codice ispezionati**:
> - `src/infrastructure/logging/game_logger.py` (430 righe)
> - `src/infrastructure/logging/logger_setup.py` (150 righe)
> - `tests/unit/infrastructure/logging/test_game_logger.py` (127 righe)
> - `tests/unit/infrastructure/logging/test_logger_setup.py`

> ⚠️ **AGGIORNAMENTO 2026-02-21**: A seguito dell'analisi, la Strategia Decorator è stata **abbandonata** in favore della **Strategia Low-Risk (Ibrida)**. Le sezioni che descrivono i problemi del Decorator (3, 6, 7) rimangono come documentazione storica dell'analisi. Per le decisioni finali vedere **Addendum — Sezione 12** e il file `PLAN_categorized_logging.md`.

---

## 1. Validità Concettuale — ✅ VALIDA

L'idea centrale è solida: sostituire il monolite `solitario.log` con 7 file separati (`game_logic.log`, `ui_events.log`, ecc.) seguendo il pattern Paradox Interactive.

Le scelte tecniche sono tutte ben motivate:

- **RotatingFileHandler 5MB/3 backup**: basato su `logging.handlers` della stdlib Python, zero dipendenze esterne.
- **Flush immediato**: scelta corretta per affidabilità in caso di crash improvviso.
- **Decorator Pattern (Opzione A)**: la scelta migliore tra le 3 valutate — DRY, autodocumentante, Pythonic. ⚠️ *Successivamente abbandonato — vedi Addendum sezione 12.*
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

## 3. Il Problema Critico del Decorator — ⚠️ MAL DOCUMENTATO (analisi storica)

> **Nota**: I problemi descritti in questa sezione hanno motivato l'abbandono del Decorator Pattern e l'adozione della Strategia Low-Risk (Addendum sezione 12), che li risolve tutti senza modifiche invasive.

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

## 6. Incompatibilità con i Test Esistenti — ✅ RISOLTA dalla Strategia Low-Risk

> **Nota**: Con la Strategia Low-Risk le variabili `_game_logger`, `_ui_logger`, `_error_logger` rimangono invariate in `game_logger.py`. I `@patch` esistenti continuano a funzionare al 100%. La riscrittura dei test descritta di seguito era necessaria **solo** con il Decorator Pattern, che è stato abbandonato.

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

## 7. Impatto su `logger_setup.py` — ✅ Thin Wrapper (non riscrittura)

> **Nota**: Con la Strategia Low-Risk `logger_setup.py` diventa un thin wrapper che re-esporta `setup_categorized_logging`. L'API pubblica `setup_logging()` rimane identica. `acs_wx.py` non richiede modifiche.

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

1. ~~**~25 funzioni da riscrivere**~~ ✅ **RISOLTO** — Strategia Low-Risk: le funzioni non cambiano, il routing avviene tramite named loggers già esistenti.
2. **`propagate = False` mancante** — senza questa riga si ha duplicazione silente su `solitario.log`. ✅ **RISOLTO** — `categorized_logger.py` imposta `propagate = False` esplicitamente.
3. ~~**Test suite da riscrivere**~~ ✅ **RISOLTO** — Strategia Low-Risk: `_game_logger`, `_ui_logger`, `_error_logger` rimangono, tutti i `@patch` funzionano invariati.

### Priorità MEDIA (degrada funzionalità)

4. ~~**`error_occurred` caso speciale**~~ ✅ **RISOLTO** — Strategia Low-Risk: `error_occurred` logga direttamente tramite `_error_logger`, il problema `exc_info` non si pone.
5. **Funzioni mancanti per 3 categorie** — `profile`, `scoring`, `storage` non hanno helper corrispondenti. ⏳ *Rinviato a implementazione futura — categoria decommenta in `CATEGORIES` quando serve.*
6. **Timer riclassificazione** — `timer_started/expired/paused` usa `_game_logger`, va migrato a `_timer_logger`. ✅ **INCLUSO nel PLAN** — 3 righe cambiate in `game_logger.py`.

### Priorità BASSA (cosmesi/manutenzione)

7. **Backup count disallineato** — 3 (design) vs 5 (codice). ✅ **DECISO** — allineato a **3** in `categorized_logger.py`.
8. **`solitario.log` legacy** — decidere se mantenerlo per library logs o eliminarlo. ✅ **DECISO** — mantenuto per log di librerie esterne (wx, PIL, urllib3).

---

## 10. Giudizio Finale e Raccomandazioni

### Giudizio (aggiornato con Strategia Low-Risk)

Il design è **concettualmente solido**. I problemi identificati nell'analisi (sezioni 3-7) hanno motivato l'adozione della **Strategia Low-Risk**, che ottiene il risultato identico (7 file log separati) con una frazione del rischio.

**Quadro modifiche reale con Strategia Low-Risk:**

| File | Tipo di modifica |
|---|---|
| `src/infrastructure/logging/categorized_logger.py` | **NUOVO** (~60 righe) |
| `src/infrastructure/logging/logger_setup.py` | Thin wrapper (~10 righe cambiate) |
| `src/infrastructure/logging/__init__.py` | Export ampliati (~2 righe) |
| `src/infrastructure/logging/game_logger.py` | 4 righe (timer + keyboard_command) |
| `acs_wx.py` | **Nessuna modifica** |
| `tests/` | **Nessuna modifica** |

### Stima realistica (aggiornata)

- Con Decorator Pattern (abbandonato): 2-3 sessioni, riscrittura 4 file
- Con Strategia Low-Risk (adottata): **~30 minuti**, 1 sessione

### Decisioni prese

1. ✅ `error_occurred` — nessun trattamento speciale necessario (logga direttamente)
2. ✅ `solitario.log` mantenuto per library logs
3. ✅ Backup count: **3** (codice legacy 5 → allineato a design)
4. ✅ Profile/scoring/storage rinviati a implementazione futura

---

## 11. Struttura del PLAN — ✅ GIÀ REDATTO

Il PLAN operativo è disponibile in `docs/2 - projects/PLAN_categorized_logging.md`.

Contiene 7 step implementativi completi con codice pronto:  
- Step 1: `categorized_logger.py` (codice completo)  
- Step 2: `logger_setup.py` thin wrapper (codice completo)  
- Step 3: `__init__.py` export  
- Step 4: `game_logger.py` (4 modifiche con prima/dopo)  
- Step 5: Verifica `acs_wx.py` (nessuna modifica)  
- Step 6: Verifica test + grep per test timer  
- Step 7: Test manuale lista file attesi  

---

## 12. Addendum — Strategia Low-Risk Adottata

**Data decisione**: 2026-02-21  
**Motivazione**: I problemi identificati nelle sezioni 3-9 di questo rapporto hanno dimostrato che il Decorator Pattern era over-engineering per un problema già risolto dall'infrastruttura Python (named loggers).

### Principio chiave

Il routing dei log è già determinato dai named loggers Python (`logging.getLogger('game')`, ecc.). Il problema reale era solo la **configurazione degli handler** — non il routing delle chiamate. Il Decorator stava risolvendo un problema inesistente.

### Strategia scelta: Multi-Handler senza Decorator

Aggiungere `RotatingFileHandler` dedicati ai logger named esistenti, con `propagate=False`. Le funzioni in `game_logger.py` non cambiano — scrivono già sul logger corretto.

### Confronto finale

| Aspetto | Decorator (abbandonato) | Low-Risk (adottato) |
|---|---|---|
| Funzioni riscritte | ~25 | 4 (solo timer + keyboard_command) |
| Test rotti | 100% | 0% |
| File nuovi | 2 | 1 (`categorized_logger.py`) |
| Risultato | 7 file log separati | 7 file log separati |
| Tempo | 2-3 sessioni | ~30 minuti |
| Rollback | Difficile | 1 import cambiato |

### Punti risolti rispetto all'analisi originale

- ✅ Sezione 3 (Decorator incompatibile `-> None`): non si applica
- ✅ Sezione 4 (`error_occurred` speciale): non si applica
- ✅ Sezione 6 (test rotti): non si applica
- ✅ Sezione 7 (`logger_setup.py` riscrittura): thin wrapper invece
- ✅ Sezione 9 priorità ALTA (1 e 3): risolte

---

*Fine rapporto*  
*Documento aggiornato il 2026-02-21 con decisione Strategia Low-Risk*  
*Per l'implementazione operativa vedere: `docs/2 - projects/PLAN_categorized_logging.md`*
