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

#### Decorator @log_to
- **Cos'è**: Metadato applicato a funzioni helper di `game_logger.py` per dichiarare routing
- **Stati possibili**: Applicato, Non applicato
- **Proprietà**:
  - Categoria target (string o lista)
  - Livello log (default: INFO)
  - Condition (opzionale, per log condizionali)

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
@log_to('game')  (decorator intercetta)
  ↓
CategorizedLogger._write_to_category()
  ↓
RotatingFileHandler('game_logic.log')
  ↓ flush immediato
File System (logs/game_logic.log)
  ↓ quando > 5MB
Rotazione automatica (.log → .log.1 → .log.2 → .log.3 → eliminato)

Se livello >= ERROR:
  ↓ duplica anche in
RotatingFileHandler('errors.log')  (aggregatore)
```

---

## 🎬 Scenari & Flussi

### Scenario 1: Developer Chiama log.game_won() (Flusso Normale)

**Punto di partenza**: Giocatore vince partita, `game_engine.py` chiama `log.game_won(120, 45, 850)`

**Flusso**:

1. **Sistema**: Decorator `@log_to('game')` intercetta chiamata
   → **Sistema**: Esegue funzione `game_won()`, ottiene messaggio: `"Victory: time=120s, moves=45, score=850"`
   
2. **Sistema**: Decorator chiama `_write_to_category('game', INFO, messaggio)`
   → **Sistema**: Recupera handler per categoria 'game' (punta a `game_logic.log`)
   
3. **Sistema**: Logger scrive entry con timestamp
   → **File System**: `2026-02-21 14:30:15 [INFO] Victory: time=120s, moves=45, score=850` appeso a `logs/game_logic.log`
   
4. **Sistema**: Handler esegue flush immediato
   → **File System**: Dati persistiti su disco (no buffer OS)

**Punto di arrivo**: Log scritto in `game_logic.log`, nessun impatto su altri file

**Cosa cambia**: File `game_logic.log` incrementato di ~80 byte

---

### Scenario 2: Errore Critico (Multi-Target Logging)

**Punto di partenza**: Corruzione file profili, `profile_service.py` chiama `log.error_occurred('FileIO', 'Profile corrupted', exception)`

**Flusso**:

1. **Sistema**: Decorator `@log_to('error')` intercetta
   → **Sistema**: Genera messaggio: `"ERROR [FileIO]: Profile corrupted\nTraceback..."`
   
2. **Sistema**: Scrive in `errors.log` (categoria primaria)
   → **File System**: Entry in `logs/errors.log`
   
3. **Sistema**: Verifica livello >= ERROR → duplica in categoria originale se disponibile
   → **Sistema**: Se chiamata da context 'storage', scrive anche in `storage.log`
   
4. **Sistema**: Flush immediato su entrambi i file
   → **File System**: Errore visibile in 2 file (aggregato + categoria specifica)

**Punto di arrivo**: Errore tracciato in `errors.log` (per overview) e `storage.log` (per debug specifico)

**Cosa cambia**: 2 file incrementati (~200 byte ciascuno con traceback)

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
2. Developer decora nuova funzione:
   ```python
   @log_to('networking')
   def connection_established(host, port):
       return f"Connected to {host}:{port}"
   ```
3. Sistema: Al primo import, `CategorizedLogger.__init__()` crea handler per 'networking'
4. Chiamate `log.connection_established()` scrivono automaticamente in `networking.log`

**Nessun altro cambiamento necessario**: sistema scalabile per design.

---

## 🔀 Stati e Transizioni

### Stati del Sistema

#### Stato A: Logger Non Inizializzato
- **Descrizione**: Applicazione non ancora avviata, nessun file log creato
- **Può passare a**: Logger Attivo
- **Trigger**: `import game_logger` (primo import, esecuzione `__init__()`)

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
      ↓ (import game_logger)
[Logger Non Inizializzato]
      ↓ (CategorizedLogger.__init__())
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
  - Feedback atteso: 7 file × 4 backup = 28 file totali (max ~140MB), gestibile

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

- [x] ✅ **RISOLTO**: Quante categorie iniziali? → 7 categorie (game, ui, profile, scoring, timer, storage, error)
- [x] ✅ **RISOLTO**: Strategia rotazione? → Size-based, 5MB, 3 backup
- [x] ✅ **RISOLTO**: Retention policy? → Uniforme (3 backup per categoria)
- [x] ✅ **RISOLTO**: Buffer policy? → Flush immediato (affidabilità > performance)
- [x] ✅ **RISOLTO**: Viewer log accessibile? → NO (feature non necessaria)

### Decisioni Prese

- ✅ **Strategia 3 (Decorator Pattern)**: Più manutenibile, autodocumentante, DRY
- ✅ **API pubblica immutata**: Zero modifiche al codice chiamante (backward compatible)
- ✅ **7 categorie iniziali**: Coprono tutti i casi attuali + futuro prossimo (profili, scoring)
- ✅ **Size-based rotation**: 5MB max, 3 backup, encoding UTF-8
- ✅ **Flush immediato**: Affidabilità log in caso crash > micro-ottimizzazione performance
- ✅ **No UI per utente finale**: Feature infrastrutturale, trasparente al giocatore
- ✅ **Estendibilità garantita**: Aggiungere categoria = 2 righe codice (CATEGORIES dict + decorator)

### Assunzioni

- Python logging module standard (no dipendenze esterne)
- File system scrivibile in `logs/` (già verificato, app esistente)
- UTF-8 encoding supportato (Windows 11, Linux, macOS)
- RotatingFileHandler thread-safe (garantito da Python stdlib)
- Developer ha accesso a file system per leggere log (workflow esistente)

---

## 🎯 Opzioni Considerate

### Opzione A: Strategia 3 - Decorator Pattern (✅ SCELTA)

**Descrizione**: Ogni funzione helper in `game_logger.py` decorata con `@log_to(categoria)`. Decorator intercetta return value e fa routing automatico.

**Pro**: 
- ✅ DRY perfetto (logica routing in un solo posto)
- ✅ Autodocumentante (`@log_to('game')` = documentazione visiva)
- ✅ Type-safe (validazione centralizzata categorie)
- ✅ Estendibile (multi-target, livelli custom banali)
- ✅ Testabile (mock del decorator, assert su routing)

**Contro**:
- ❌ Overhead minimo (~5ns per chiamata, trascurabile)
- ❌ Setup iniziale leggermente più complesso (decorator + registry)

---

### Opzione B: Wrapper Manuale (❌ SCARTATA)

**Descrizione**: Ogni funzione chiama esplicitamente `self._log_to_category('game', 'INFO', msg)`.

**Pro**:
- ✅ Nessun "magic" (codice imperativo esplicito)
- ✅ Setup più rapido (no decorator da scrivere)

**Contro**:
- ❌ Ripetizione (ogni metodo ha boilerplate `_log_to_category()`)
- ❌ Fragile (typo in stringa categoria = bug silenzioso)
- ❌ Non DRY (logica routing ripetuta N volte)
- ❌ Difficile refactoring (rinominare categoria = N sostituzioni manuali)

---

### Opzione C: Decorator Magico (__getattribute__) (❌ SCARTATA)

**Descrizione**: Intercettare TUTTE le chiamate a metodi con `__getattribute__`, inferire categoria da nome metodo.

**Pro**:
- ✅ Zero modifiche ai metodi esistenti

**Contro**:
- ❌ Magia nera (debugging difficile)
- ❌ Mapping implicito nome→categoria (fragile, non documentato)
- ❌ Performance overhead su OGNI attributo access (non solo log)
- ❌ Pythonicamente scorretto (abuse di dunder methods)

---

### Scelta Finale

Scelto **Opzione A: Decorator Pattern** perché:
- Massima manutenibilità (DRY + autodocumentante)
- Scalabile (aggiungere categoria = 2 righe)
- Pythonic (decorators sono idiomatici)
- Trade-off perfetto: setup leggermente più complesso, ma qualità codice superiore
- Overhead trascurabile (5ns in contesto non real-time)

---

## ✅ Design Freeze Checklist

Questo design è pronto per la fase tecnica (PLAN) quando:

- [x] Tutti gli scenari principali mappati (normale, errore, rotazione, estendibilità)
- [x] Stati del sistema chiari e completi (non init, attivo, rotazione, shutdown)
- [x] Flussi logici coprono tutti i casi d'uso (write, multi-target, rotation)
- [x] Domande aperte risolte (5/5 decisioni confermate)
- [x] UX interaction definita (N/A - feature infrastrutturale)
- [x] Nessun "buco logico" evidente
- [x] Opzioni valutate e scelta finale motivata (3 opzioni, Decorator vince)

**Next Step**: Creare `PLAN_categorized_logging.md` con:
- Decisioni API (signature decorator, registry pattern)
- Layer assignment (tutto Infrastructure/Logging)
- File structure (2 nuovi file, 3 modificati)
- Testing strategy (unit test decorator, integration test routing)
- Migration path (backward compatibility garantita)

---

## 📝 Note di Brainstorming

### Idee Future (Post-v3.2.0)

- **Compressione automatica backup**: `.log.1` → `.log.1.gz` per risparmiare spazio
- **Log remoto**: Stream `errors.log` a servizio cloud per analytics aggregata (telemetria opt-in)
- **Structured logging**: JSON format per parsing automatico (tool come `jq` per query)
- **Conditional logging avanzato**: `@log_to('game', condition=lambda: settings.debug_mode)`
- **Performance profiling**: Categoria `perf.log` per timing operazioni critiche

### Collegamento Feature Esistenti

- **Profile System v3.0**: Categoria `profile` già prevista, pronta per log CRUD profili
- **Scoring System v2.0**: Categoria `scoring` pronta per tracking calcoli punteggio
- **Timer System**: Categoria `timer` copre timeout STRICT/PERMISSIVE

### Accessibilità

- File più piccoli = navigazione NVDA più fluida (meno righe da scorrere)
- Naming file semantico (`game_logic.log` vs `app.log`) = contestualizzazione immediata
- UTF-8 encoding = caratteri speciali carte napoletane renderizzati correttamente

---

## 📚 Riferimenti Contestuali

### Feature Correlate

- **Clean Architecture Refactoring (PR #79)**: Logging già spostato in Infrastructure layer, fondamenta pronte
- **Profile System (v3.0-v3.1)**: Categoria `profile` necessaria per tracking sessioni/statistiche
- **Scoring System (v2.0)**: Categoria `scoring` necessaria per debug calcoli penalità

### Vincoli da Rispettare

- **Zero modifiche codice chiamante**: `log.game_won()` deve continuare a funzionare identico
- **Backward compatibility**: Se rollback necessario, applicazione deve funzionare con vecchio sistema
- **Performance non degradata**: Overhead logging < 1% tempo totale esecuzione (già trascurabile)
- **Cross-platform**: Windows 11 (primario), Linux (testato), macOS (non testato ma compatibile)

---

## 🎯 Risultato Finale Atteso (High-Level)

Una volta implementato, il developer/maintainer potrà:

✅ Aprire file log categorizzato specifico per debug mirato (es. `timer.log` per problemi timeout)  
✅ Navigare file più piccoli (~500KB invece di 10MB) con NVDA più velocemente  
✅ Identificare pattern per categoria (es. "quante volte utenti riciclano scarti?" → grep `waste_recycled` in `game_logic.log`)  
✅ Gestire spazio disco prevedibile (max 140MB totali = 7 categorie × 20MB)  
✅ Estendere sistema con nuova categoria in 2 minuti (CATEGORIES dict + decorator)  
✅ Rollback a sistema vecchio in emergenza (API immutata, codice chiamante compatibile)  
✅ Avere log affidabili anche in crash improvviso (flush immediato, no buffer loss)

---

**Fine Design Document**

---

## 🎯 Status Progetto

**Design**: ✅ FROZEN (pronto per implementazione)  
**Piano Tecnico**: 🔄 TODO (prossimo step: `PLAN_categorized_logging.md`)  
**Implementazione**: ⏳ PENDING  
**Testing**: ⏳ PENDING  
**Deploy**: ⏳ PENDING

---

**Document Version**: v1.0  
**Data Freeze**: 2026-02-21  
**Autore**: AI Assistant + Nemex81  
**Filosofia**: "Paradox-style categorized logging per programmatori non vedenti"
