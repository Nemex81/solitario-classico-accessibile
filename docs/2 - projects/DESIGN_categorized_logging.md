# 🎨 Design Document - Sistema Logging Categorizzato (Paradox-Style)

> **FASE: CONCEPT & FLOW DESIGN**  
> Nessuna decisione tecnica qui - solo logica e flussi concettuali  
> Equivalente a "diagrammi di flusso sulla lavagna"

---

## 📌 Metadata

- **Data Inizio**: 2026-02-21
- **Stato**: FROZEN (pronto per PLAN)
- **Versione Target**: v3.2.0 (ipotesi)
- **Autore**: AI Assistant + Nemex81
- **Ultima Revisione**: 2026-02-21 (strategia finale: Low-Risk Multi-Handler)

---

## 💡 L'Idea in 3 Righe

Sostituire il sistema di logging monolitico (un unico file `game.log`) con un sistema multi-file categorizzato in stile Paradox Interactive, dove ogni tipo di evento logga in un file dedicato (`game_logic.log`, `ui_events.log`, ecc.), mantenendo l'API pubblica **completamente immutata**. Questo migliora drasticamente debugging, navigazione NVDA, e gestione dello spazio disco, senza richiedere modifiche al codice chiamante esistente.

---

## 🎭 Attori e Concetti

### Attori (Chi/Cosa Interagisce)

- **Developer/Maintainer**: Chi debugga il sistema, legge i log per diagnosticare problemi
- **Sistema Logging**: Componente infrastrutturale che riceve chiamate `log.game_won()` e scrive su file appropriato
- **Screen Reader (NVDA)**: Tool per utenti non vedenti che naviga i file log
- **File System**: Gestisce rotazione file quando superano 5MB

### Concetti Chiave (Cosa Esiste nel Sistema)

#### Categoria Log
- **Cos'è**: Classificazione semantica di un evento (es. "game", "ui", "timer")
- **Stati possibili**: Attiva (scrive su file), Inattiva (categoria non esistente)
- **Proprietà**: 
  - Nome categoria (string, es. "game")
  - File destinazione (es. "game_logic.log")
  - Formatter specifico (opzionale, default comune)
  - Handler RotatingFileHandler (5MB max, 3 backup)

#### Named Logger
- **Cos'è**: Istanza `logging.Logger` con nome specifico (es. `logging.getLogger('game')`)
- **Stati possibili**: Configurato (con handler), Non configurato
- **Proprietà**:
  - Nome categoria
  - Handler specifico (RotatingFileHandler dedicato)
  - Livello log (default: INFO)
  - `propagate = False` (per evitare duplicazione)

#### File Log Categorizzato
- **Cos'è**: File fisico su disco con subset di log filtrati per tipo
- **Stati possibili**: 
  - Attivo (file .log corrente)
  - Archiviato (file .log.1, .log.2, .log.3)
  - Eliminato (oltre 3 backup, garbage collected)
- **Proprietà**:
  - Dimensione max: 5MB
  - Backup count: 3
  - Encoding: UTF-8
  - Flush policy: Immediato (dopo ogni write)

#### Messaggio Log
- **Cos'è**: Singola entry testuale con timestamp + livello + contenuto
- **Stati possibili**: Buffered (in memoria), Flushed (scritto su disco)
- **Proprietà**:
  - Timestamp (ISO 8601)
  - Livello (DEBUG, INFO, WARNING, ERROR)
  - Categoria implicita (dal nome file)
  - Contenuto (messaggio formattato)

### Relazioni Concettuali

```
Developer
  ↓ scrive codice che chiama
log.game_won()  (API pubblica immutata)
  ↓
game_logger.game_won()  (funzione helper)
  ↓
_game_logger.info("Victory...")  (named logger esistente)
  ↓
RotatingFileHandler('game_logic.log')  (handler dedicato, configurato al setup)
  ↓ flush immediato
File System (logs/game_logic.log)
  ↓ quando > 5MB
Rotazione automatica (.log → .log.1 → .log.2 → .log.3 → eliminato)

Se livello >= ERROR:
  ↓ _error_logger scrive anche in
RotatingFileHandler('errors.log')  (aggregatore)
```

---

## 🎬 Scenari & Flussi

### Scenario 1: Developer Chiama log.game_won() (Flusso Normale)

**Punto di partenza**: Giocatore vince partita, `game_engine.py` chiama `log.game_won(120, 45, 850)`

**Flusso**:

1. **Sistema**: Funzione helper `game_logger.game_won()` eseguita
   → **Sistema**: Formatta messaggio: `"Game WON - Time: 120s, Moves: 45, Score: 850"`
   
2. **Sistema**: Chiama `_game_logger.info(messaggio)` (named logger configurato al setup)
   → **Sistema**: Handler associato a `_game_logger` punta a `logs/game_logic.log`
   
3. **Sistema**: Logger scrive entry con timestamp
   → **File System**: `2026-02-21 14:30:15 [INFO] Game WON - Time: 120s, Moves: 45, Score: 850` appeso a `logs/game_logic.log`
   
4. **Sistema**: Handler esegue flush immediato
   → **File System**: Dati persistiti su disco (no buffer OS)

**Punto di arrivo**: Log scritto in `game_logic.log`, nessun impatto su altri file

**Cosa cambia**: File `game_logic.log` incrementato di ~80 byte

---

### Scenario 2: Errore Critico (Multi-Target Logging)

**Punto di partenza**: Corruzione file profili, `profile_service.py` chiama `log.error_occurred('FileIO', 'Profile corrupted', exception)`

**Flusso**:

1. **Sistema**: Funzione helper `game_logger.error_occurred()` eseguita
   → **Sistema**: Genera messaggio: `"ERROR [FileIO]: Profile corrupted"`
   
2. **Sistema**: Chiama `_error_logger.error(messaggio, exc_info=exception)`
   → **File System**: Entry scritta in `logs/errors.log` (handler di `_error_logger`)
   
3. **Sistema**: Handler `_error_logger` include traceback completo grazie a `exc_info`
   → **File System**: Errore con stacktrace visibile in `errors.log`
   
4. **Sistema**: Flush immediato
   → **File System**: Errore persistito immediatamente

**Punto di arrivo**: Errore tracciato in `errors.log` con traceback completo

**Cosa cambia**: File `errors.log` incrementato (~200 byte con traceback)

**Nota**: Se necessario logging multi-categoria, la funzione helper può chiamare più logger (es. `_error_logger` + `_storage_logger`).

---

### Scenario 3: Rotazione File (Edge Case Automatico)

**Cosa succede se**: `game_logic.log` raggiunge 5MB esatti durante scrittura

**Sistema dovrebbe**: 
1. Chiudere file corrente
2. Rinominare:
   - `game_logic.log.2` → `game_logic.log.3` (elimina .log.3 se esiste)
   - `game_logic.log.1` → `game_logic.log.2`
   - `game_logic.log` → `game_logic.log.1`
3. Creare nuovo `game_logic.log` vuoto
4. Scrivere entry corrente nel nuovo file
5. Developer/NVDA: navigazione trasparente, sempre legge `game_logic.log` (il più recente)

**Nota**: RotatingFileHandler gestisce tutto automaticamente, nessuna logica custom necessaria.

---

### Scenario 4: Aggiunta Nuova Categoria (Estendibilità)

**Cosa succede se**: Developer vuole aggiungere categoria 'networking' per future feature online

**Sistema dovrebbe**: 
1. Developer aggiunge entry in `CATEGORIES` dict:
   ```python
   CATEGORIES = {
       'game': 'game_logic.log',
       'networking': 'networking.log',  # ← NUOVO
       ...
   }
   ```
2. Developer aggiunge named logger in `game_logger.py`:
   ```python
   _networking_logger = logging.getLogger('networking')
   
   def connection_established(host, port):
       _networking_logger.info(f"Connected to {host}:{port}")
   ```
3. Sistema: Al setup, `setup_categorized_logging()` crea handler per 'networking'
4. Chiamate `log.connection_established()` scrivono automaticamente in `networking.log`

**Nessun altro cambiamento necessario**: sistema scalabile per design.

---

## 🔀 Stati e Transizioni

### Stati del Sistema

#### Stato A: Logger Non Inizializzato
- **Descrizione**: Applicazione non ancora avviata, nessun file log creato
- **Può passare a**: Logger Attivo
- **Trigger**: `setup_categorized_logging()` chiamato da `acs_wx.py` all'avvio

#### Stato B: Logger Attivo
- **Descrizione**: Tutti handler creati, file aperti, pronto per scrittura
- **Può passare a**: Logger Shutdown, File In Rotazione
- **Trigger**: Chiamata `log.*()` qualsiasi

#### Stato C: File In Rotazione (transizione rapida)
- **Descrizione**: Handler sta rinominando file (file > 5MB)
- **Può passare a**: Logger Attivo
- **Trigger**: Scrittura che supera soglia 5MB
- **Durata**: <10ms (operazione atomica)

#### Stato D: Logger Shutdown
- **Descrizione**: Applicazione chiusa, handler rilasciati, file chiusi
- **Può passare a**: Logger Non Inizializzato (riavvio app)
- **Trigger**: `atexit` handler o `logging.shutdown()`

### Diagramma Stati (ASCII)

```
[App Start]
      ↓ (setup_categorized_logging())
[Logger Non Inizializzato]
      ↓ (handler configurati per 'game', 'ui', 'error', 'timer')
[Logger Attivo] ←──────────────┐
      ↓ (write > 5MB)          │
[File In Rotazione] ─────────┘ (rotazione completa, <10ms)
      ↓ (app close)
[Logger Shutdown]
      ↓ (app restart)
[Logger Non Inizializzato]
```

---

## 🎮 Interazione Utente (UX Concettuale)

### Comandi/Azioni Disponibili

**IMPORTANTE**: Questa feature NON ha UX diretta per l'utente finale del gioco. È una feature **infrastrutturale** per developer/maintainer.

- **Developer apre file log con editor**:
  - Fa cosa? Naviga file categoria specifica per debug
  - Quando disponibile? Sempre (file creati al primo log)
  - Feedback atteso: File più piccolo (~500KB invece di 10MB), ricerca più veloce

- **NVDA naviga file log**:
  - Fa cosa? Screen reader legge entry log riga per riga
  - Quando disponibile? Quando file esiste e non vuoto
  - Feedback atteso: Navigazione più fluida (meno linee per file)

- **File System esegue backup**:
  - Fa cosa? Developer copia cartella `logs/` per archivio
  - Quando disponibile? Sempre
  - Feedback atteso: 4 file × 4 backup = 16 file totali (max ~80MB), gestibile

### Feedback Sistema

Nessun feedback diretto all'utente del gioco. Tutto trasparente.

### Navigazione Concettuale

**Workflow Developer per Debugging**:

1. Bug report: "Crash al timer scaduto"
2. Developer apre `logs/timer.log` (non deve cercare in 10MB monolitico)
3. Trova entry: `2026-02-21 15:10:00 [WARNING] Timer EXPIRED - Game auto-abandoned`
4. Verifica `logs/game_logic.log` per contesto: stato partita prima del crash
5. Verifica `logs/errors.log` per eccezioni correlate
6. Debug chirurgico: 3 file da 500KB invece di 1 file da 10MB

---

## 🤔 Domande & Decisioni

### Domande Aperte

- [x] ✅ **RISOLTO**: Quante categorie iniziali? → 4 categorie (game, ui, timer, error) + 3 future (profile, scoring, storage)
- [x] ✅ **RISOLTO**: Strategia rotazione? → Size-based, 5MB, 3 backup
- [x] ✅ **RISOLTO**: Retention policy? → Uniforme (3 backup per categoria)
- [x] ✅ **RISOLTO**: Buffer policy? → Flush immediato (affidabilità > performance)
- [x] ✅ **RISOLTO**: Viewer log accessibile? → NO (feature non necessaria)
- [x] ✅ **RISOLTO**: Strategia implementazione? → Low-Risk Multi-Handler (no decorator)

### Decisioni Prese

- ✅ **Strategia Low-Risk Multi-Handler**: Handler dedicati per named logger esistenti, zero riscrittura funzioni
- ✅ **API pubblica immutata**: Zero modifiche al codice chiamante (backward compatible)
- ✅ **4 categorie iniziali**: game, ui, timer, error (esistenti nel codice) + 3 future quando necessarie
- ✅ **Size-based rotation**: 5MB max, 3 backup, encoding UTF-8
- ✅ **Flush immediato**: Affidabilità log in caso crash > micro-ottimizzazione performance
- ✅ **No UI per utente finale**: Feature infrastrutturale, trasparente al giocatore
- ✅ **Estendibilità garantita**: Aggiungere categoria = 2 righe codice (CATEGORIES dict + named logger)
- ✅ **propagate=False**: Essenziale per evitare duplicazione log su `solitario.log`
- ✅ **Root logger mantenuto**: Per library logs (wx, PIL, urllib3) → `solitario.log`

### Assunzioni

- Python logging module standard (no dipendenze esterne)
- File system scrivibile in `logs/` (già verificato, app esistente)
- UTF-8 encoding supportato (Windows 11, Linux, macOS)
- RotatingFileHandler thread-safe (garantito da Python stdlib)
- Developer ha accesso a file system per leggere log (workflow esistente)
- Named loggers esistenti (`_game_logger`, `_ui_logger`, `_error_logger`) già nel codice

---

## 🎯 Opzioni Considerate

### Opzione A: Low-Risk Multi-Handler (✅ SCELTA FINALE)

**Descrizione**: Configurare handler RotatingFileHandler separati per i named logger esistenti (`_game_logger`, `_ui_logger`, `_error_logger`, `_timer_logger`) tramite `setup_categorized_logging()`. Le funzioni helper in `game_logger.py` restano invariate (continuano a chiamare `_game_logger.info()`, ecc.).

**Pro**: 
- ✅ **Impatto minimale**: 5 righe modificate in `game_logger.py` (solo timer + fix keyboard_command)
- ✅ **Zero test rotti**: Variabili `_game_logger` esistono ancora, test continuano a funzionare
- ✅ **Risultato identico**: 7 file log separati come design originale
- ✅ **Rollback banale**: Cambia 1 import, torna a `setup_logging()` vecchio
- ✅ **Implementazione rapida**: 30 minuti (1 file nuovo, 2 file modifiche minori)
- ✅ **Usa infrastruttura nativa**: Python logging system risolve routing automaticamente
- ✅ **propagate=False**: Impedisce duplicazione log silente

**Contro**:
- ❌ **Nessuno rilevante**: Strategia tecnicamente superiore per questo caso d'uso

**Implementazione**:

```python
# categorized_logger.py (NUOVO)
CATEGORIES = {
    'game': 'game_logic.log',
    'ui': 'ui_events.log',
    'error': 'errors.log',
    'timer': 'timer.log',
}

def setup_categorized_logging(logs_dir, level, console_output):
    for category, filename in CATEGORIES.items():
        logger = logging.getLogger(category)
        handler = RotatingFileHandler(logs_dir / filename, maxBytes=5MB, backupCount=3)
        logger.addHandler(handler)
        logger.propagate = False  # ← CRITICO
    # Root logger per wx, PIL, urllib3 → solitario.log

# game_logger.py (modifiche MINIMALI)
_timer_logger = logging.getLogger('timer')  # ← AGGIUNGI

def timer_started(duration):  # ← CAMBIA da _game_logger a _timer_logger
    _timer_logger.info(f"Timer started - Duration: {duration}s")

def keyboard_command(command, context):  # ← FIX da _game_logger a _ui_logger
    _ui_logger.debug(f"Key command: {command} in context '{context}'")
```

---

### Opzione B: Decorator Pattern (❌ SCARTATA DOPO ANALISI)

**Descrizione**: Ogni funzione helper in `game_logger.py` decorata con `@log_to(categoria)`. Decorator intercetta return value e fa routing automatico.

**Pro**: 
- ✅ DRY teorico (logica routing in un solo posto)
- ✅ Autodocumentante (`@log_to('game')` = documentazione visiva)

**Contro**:
- ❌ **Problema critico identificato**: Named logger esistenti (`_game_logger`) GIÀ fanno routing — decorator risolve problema inesistente
- ❌ **~25 funzioni da riscrivere**: Tutte le funzioni cambiano firma da `-> None` a `-> str`
- ❌ **Test suite rotta**: Variabili `_game_logger` spariscono, tutti `@patch` falliscono
- ❌ **Caso speciale `error_occurred`**: `exc_info=exception` non trasportabile tramite return value
- ❌ **Complessità non necessaria**: Decorator + registry custom quando Python logging risolve già il problema
- ❌ **Tempo implementazione**: 2-3 sessioni (vs 30 minuti Low-Risk)
- ❌ **Rischio regressioni**: Alto (4 file riscritti)

**Perché scartata**: Dopo analisi del codice esistente, emerso che il routing è già risolto dai named logger. Il vero problema era configurazione handler, non routing chiamate.

---

### Opzione C: Wrapper Manuale (❌ SCARTATA)

**Descrizione**: Ogni funzione chiama esplicitamente `self._log_to_category('game', 'INFO', msg)`.

**Pro**:
- ✅ Nessun "magic" (codice imperativo esplicito)

**Contro**:
- ❌ Ripetizione (ogni metodo ha boilerplate `_log_to_category()`)
- ❌ Fragile (typo in stringa categoria = bug silenzioso)
- ❌ Non DRY (logica routing ripetuta N volte)
- ❌ Difficile refactoring (rinominare categoria = N sostituzioni manuali)
- ❌ **Inferiore a Low-Risk**: Stesso risultato ma più fragile

---

### Scelta Finale

Scelto **Opzione A: Low-Risk Multi-Handler** perché:
- ✅ Sfrutta infrastruttura Python logging nativa (named logger + handler setup)
- ✅ Impatto minimale (5 righe vs 300+)
- ✅ Zero test rotti
- ✅ Risultato identico a opzioni più complesse
- ✅ Rollback banale
- ✅ Implementazione 30 minuti
- ✅ Manutenibilità superiore (meno codice = meno bug)

**Motivazione tecnica**: Il sistema Python logging è progettato per risolvere routing tramite named logger. Named logger esistenti (`_game_logger`, `_ui_logger`, ecc.) sono GIÀ routing corretto — serviva solo configurare handler separati, non riscrivere logica routing.

---

## ✅ Design Freeze Checklist

Questo design è pronto per la fase tecnica (PLAN) quando:

- [x] Tutti gli scenari principali mappati (normale, errore, rotazione, estendibilità)
- [x] Stati del sistema chiari e completi (non init, attivo, rotazione, shutdown)
- [x] Flussi logici coprono tutti i casi d'uso (write, multi-target, rotation)
- [x] Domande aperte risolte (6/6 decisioni confermate)
- [x] UX interaction definita (N/A - feature infrastrutturale)
- [x] Nessun "buco logico" evidente
- [x] Opzioni valutate e scelta finale motivata (3 opzioni, Low-Risk vince)
- [x] Strategia finale confermata dopo analisi codice esistente

**Next Step**: Creare `PLAN_categorized_logging.md` con:
- Decisioni tecniche (setup multi-handler, propagate=False, backup count 3)
- Layer assignment (tutto Infrastructure/Logging)
- File structure (1 nuovo, 2 modificati)
- Testing strategy (zero modifiche test esistenti)
- Migration path (backward compatibility garantita, rollback 1 minuto)

---

## 📝 Note di Brainstorming

### Idee Future (Post-v3.2.0)

- **Compressione automatica backup**: `.log.1` → `.log.1.gz` per risparmiare spazio
- **Log remoto**: Stream `errors.log` a servizio cloud per analytics aggregata (telemetria opt-in)
- **Structured logging**: JSON format per parsing automatico (tool come `jq` per query)
- **Conditional logging avanzato**: Level dinamico basato su settings runtime
- **Performance profiling**: Categoria `perf.log` per timing operazioni critiche

### Collegamento Feature Esistenti

- **Profile System v3.0**: Categoria `profile` da aggiungere quando necessario
- **Scoring System v2.0**: Categoria `scoring` da aggiungere quando necessario
- **Timer System**: Categoria `timer` implementata subito (riclassificazione da `game`)

### Accessibilità

- File più piccoli = navigazione NVDA più fluida (meno righe da scorrere)
- Naming file semantico (`game_logic.log` vs `app.log`) = contestualizzazione immediata
- UTF-8 encoding = caratteri speciali carte napoletane renderizzati correttamente

### Perché Low-Risk È Superiore

**Insight chiave**: Il routing log è già risolto dal naming dei logger. Quando scrivi:

```python
_game_logger = logging.getLogger('game')
_game_logger.info("Victory")
```

Il nome `'game'` è già routing dichiarato. Se aggiungi un `RotatingFileHandler` a quel logger con `propagate=False`, **tutti i log di quella categoria finiscono automaticamente nel file corretto**, senza toccare le funzioni chiamanti.

Il decorator pattern stava cercando di "risolvere routing" quando Python logging lo fa nativamente da sempre.

---

## 📚 Riferimenti Contestuali

### Feature Correlate

- **Clean Architecture Refactoring (PR #79)**: Logging già spostato in Infrastructure layer, fondamenta pronte
- **Profile System (v3.0-v3.1)**: Categoria `profile` da aggiungere in futuro quando implementata
- **Scoring System (v2.0)**: Categoria `scoring` da aggiungere in futuro quando implementata

### Vincoli da Rispettare

- **Zero modifiche codice chiamante**: `log.game_won()` deve continuare a funzionare identico ✅
- **Backward compatibility**: Se rollback necessario, applicazione deve funzionare con vecchio sistema ✅
- **Performance non degradata**: Overhead logging < 1% tempo totale esecuzione ✅
- **Cross-platform**: Windows 11 (primario), Linux (testato), macOS (non testato ma compatibile) ✅
- **Test esistenti funzionanti**: Zero modifiche a test suite ✅

---

## 🎯 Risultato Finale Atteso (High-Level)

Una volta implementato, il developer/maintainer potrà:

✅ Aprire file log categorizzato specifico per debug mirato (es. `timer.log` per problemi timeout)  
✅ Navigare file più piccoli (~500KB invece di 10MB) con NVDA più velocemente  
✅ Identificare pattern per categoria (es. "quante volte utenti riciclano scarti?" → grep `waste_recycled` in `game_logic.log`)  
✅ Gestire spazio disco prevedibile (max 80MB = 4 categorie × 20MB)  
✅ Estendere sistema con nuova categoria in 2 minuti (CATEGORIES dict + named logger)  
✅ Rollback a sistema vecchio in emergenza (1 minuto, cambia 1 import)  
✅ Avere log affidabili anche in crash improvviso (flush immediato, no buffer loss)  
✅ Test esistenti continuano a funzionare senza modifiche

---

**Fine Design Document**

---

## 🎯 Status Progetto

**Design**: ✅ FROZEN (strategia Low-Risk confermata dopo analisi)  
**Piano Tecnico**: 🔄 TODO (prossimo step: `PLAN_categorized_logging.md`)  
**Implementazione**: ⏳ PENDING  
**Testing**: ⏳ PENDING  
**Deploy**: ⏳ PENDING

---

**Document Version**: v2.0 (Low-Risk Strategy)  
**Data Freeze**: 2026-02-21  
**Autore**: AI Assistant + Nemex81  
**Filosofia**: "Paradox-style categorized logging per programmatori non vedenti — minimo impatto, massimo beneficio"
