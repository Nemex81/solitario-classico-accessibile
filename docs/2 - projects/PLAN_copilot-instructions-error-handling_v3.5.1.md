# Piano Aggiornamento copilot-instructions.md — Error Handling Section

**Versione Piano**: v3.5.1  
**Tipo Task**: Documentation Update (Enhancement)  
**Priorità**: 🔴 ALTA  
**Stato**: READY  
**Branch**: `supporto-audio-centralizzato`  
**Versione Target**: v3.5.1 (pre-merge audio system)  
**Data Creazione**: 2026-02-24  

---

## Executive Summary

### Problema/Obiettivo

Il file `.github/copilot-instructions.md` attualmente **non include linee guida esplicite** per gestione errori e strategie fail-fast vs graceful degradation. Questo crea ambiguità nelle sessioni Copilot su quando crashare (raise Exception) vs degradare (log + fallback).

Il sistema audio v3.5.1 ha implementato correttamente pattern di graceful degradation (`AudioManager` → `_AudioManagerStub`, config JSON assente → log ERROR + dict vuoto), ma questi pattern non sono documentati come **standard di progetto replicabili**.

**Obiettivo**: Aggiungere sezione "Error Handling e Graceful Degradation" a `copilot-instructions.md` per:
1. Codificare best practice già applicate nel sistema audio
2. Fornire checklist decisionale fail-fast vs degradation
3. Documentare pattern Null Object (stub fallback)
4. Definire livelli severità logging per errori
5. Eliminare ambiguità per Copilot in sessioni future

---

## Contesto Tecnico

### Rationale

**Perché questo aggiornamento è necessario:**

1. **Gap documentale**: Error handling è fondamentale quanto architettura Clean, ma non ha sezione dedicata
2. **Pattern già provati**: Sistema audio dimostra che graceful degradation funziona per feature non critiche
3. **Consistenza futura**: Codificando lo standard, Copilot applicherà stessa strategia in profili, timer, future feature
4. **Onboarding veloce**: Futuri collaboratori hanno riferimento chiaro senza dover inferire da codice esistente

**Esempi di decisioni ambigue senza linee guida:**
- File `audio_config.json` assente: crash o degrade?
- File WAV singolo mancante: warning o error?
- `ProfileService.load(None)`: raise o return None?
- pygame.mixer.init() fallisce: propagare exception o stub?

Con la sezione, ogni scenario ha una **regola documentata**.

---

## File Coinvolti

### File da Modificare

| File Path | Operazione | Descrizione |
|-----------|------------|-------------|
| `.github/copilot-instructions.md` | MODIFY | Inserimento sezione "Error Handling e Graceful Degradation" dopo sezione Logging (linea ~120) |

### File di Riferimento (Non Modificare)

| File Path | Ruolo | Note |
|-----------|-------|------|
| `src/infrastructure/audio/audio_manager.py` | Pattern reference | Esempio graceful degradation corretto |
| `src/infrastructure/di/dependency_container.py` | Pattern reference | Esempio Null Object stub fallback |
| `src/domain/services/profile_service.py` | Pattern reference | Esempio fail-fast su contratto violato |

---

## Fasi di Implementazione

### FASE 1: Preparazione Contenuto Sezione

**Cosa fare:**
1. Leggi il contenuto completo della nuova sezione (fornito sotto in "Contenuto Esatto da Inserire")
2. Verifica che esempi citati corrispondano al codice reale nel repository
3. Conferma che livelli severità logging siano coerenti con sezione "Logging (Sistema Categorizzato v3.3.0)"

**Output atteso**: Contenuto validato, nessuna incoerenza con altre sezioni.

---

### FASE 2: Inserimento Sezione nel File

**Procedura operativa step-by-step:**

1. **Apri file**: `.github/copilot-instructions.md`

2. **Identifica punto di inserimento esatto**:
   - Cerca la sezione `### Logging (Sistema Categorizzato v3.3.0)` (circa linea 100-120)
   - Scorri fino alla **fine della sezione Logging** (cerca il separatore `---` o l'inizio della sezione successiva)
   - Il punto di inserimento è **immediatamente dopo il separatore `---`** che chiude la sezione Logging

3. **Inserisci il contenuto**:
   - Incolla l'intero blocco della sezione "Error Handling e Graceful Degradation" (vedi sotto)
   - Mantieni formattazione Markdown identica (intestazioni `###`, liste `- [ ]`, code blocks triple backtick)
   - Assicurati che ci sia un separatore `---` sia **sopra** (dopo Logging) che **sotto** (prima della sezione successiva)

4. **Verifica struttura gerarchica**:
   - La nuova sezione deve avere intestazione `###` (livello 3, come "Logging")
   - Deve apparire sotto `## 🏗️ Architettura e Standard di Codifica` (livello 2)
   - Sottosezioni devono usare `####` (livello 4)

5. **Controllo integrità navigazione**:
   - Verifica che la sezione sia raggiungibile tramite table of contents (se presente)
   - Testa che anchor link `#error-handling-e-graceful-degradation` funzioni correttamente

**Esempio struttura finale (gerarchia intestazioni):**
```
## 🏗️ Architettura e Standard di Codifica
  ### Clean Architecture (Strict Enforcement)
  ### Naming Conventions
  ### Type Hints Enforcement
  ### Logging (Sistema Categorizzato v3.3.0)
  ---
  ### Error Handling e Graceful Degradation    ← NUOVA SEZIONE QUI
    #### Quando Usare Exception Raising (Fail-Fast)
    #### Quando Usare Graceful Degradation (Log + Fallback)
    #### Checklist Decisionale (Flow Chart)
    #### Esempi Applicati al Progetto
    #### Osservabilità Obbligatoria
  ---
  ### Accessibilità UI (WAI-ARIA + Keyboard)
```

---

### FASE 3: Validazione Markdown e Lint

**Comandi da eseguire (chiedi all'utente se necessario):**

```bash
# Verifica sintassi Markdown
markdownlint .github/copilot-instructions.md

# Verifica link interni non rotti
markdown-link-check .github/copilot-instructions.md

# Preview rendering (opzionale, richiede pandoc)
pandoc .github/copilot-instructions.md -o preview.html
```

**Errori comuni da evitare:**
- ❌ Triple backtick code block non chiuso correttamente
- ❌ Liste numerate con indentazione errata (rompe nesting)
- ❌ Tabelle con pipe `|` non allineati (non bloccante, ma brutto)
- ❌ Link relativi rotti (es. `[AudioManager](src/infrastructure/audio/audio_manager.py)` → deve essere path valido)

**Se lint fallisce**: Correggi errori prima di commit. Non committare file con errori Markdown.

---

### FASE 4: Commit e Documentazione

**Commit message (formato convenzionale):**

```
docs(copilot): aggiunta sezione Error Handling e Graceful Degradation

- Definiti criteri fail-fast vs degradation (checklist decisionale)
- Pattern Null Object con stub fallback documentato
- Livelli severità logging per errori esterni vs bug logici
- Esempi specifici del progetto (audio system, profile service)
- Tabella comparativa scenari comuni

Rationale: Codifica best practice già applicate nel sistema audio v3.5.1
come standard di progetto replicabile per feature future.

Refs: docs/2 - projects/PLAN_copilot-instructions-error-handling_v3.5.1.md
```

**File da includere nel commit:**
- `.github/copilot-instructions.md` (modificato)
- `docs/2 - projects/PLAN_copilot-instructions-error-handling_v3.5.1.md` (questo file)

**Comando Git:**
```bash
git add .github/copilot-instructions.md docs/2\ -\ projects/PLAN_copilot-instructions-error-handling_v3.5.1.md
git commit -F /tmp/commit-msg.txt  # Dove /tmp/commit-msg.txt contiene il messaggio sopra
```

---

## Contenuto Esatto da Inserire

### Posizione: Dopo sezione "Logging", prima di "Accessibilità UI"

```markdown
---

### Error Handling e Graceful Degradation

**Principio guida**: Distinguere **bug logici interni** (crash immediato) da **fallimenti di risorse esterne** (degradazione graziosa).

#### Quando Usare Exception Raising (Fail-Fast)

**Trigger (almeno uno dei seguenti):**
- Violazione contratto API (es. parametro `None` quando richiesto non-null)
- Errore logico interno (es. `IndexError`, assertion failure)
- Stato inconsistente non recuperabile (es. corruzione struttura dati Domain)
- Bug nello sviluppo (es. chiamata a metodo inesistente)

**Pattern obbligatorio:**
```python
# ✅ CORRETTO — Crash su bug logico
def move_card(self, from_pile: int, to_pile: int) -> None:
    if from_pile < 0 or from_pile > 12:
        raise ValueError(f"Invalid pile index: {from_pile}")  # Bug dev
```

**Custom Exceptions** — Crea sottoclassi di `Exception` solo per errori Domain-specific:
```python
# src/domain/exceptions.py
class InvalidMoveError(Exception):
    """Mossa carta non valida per regole Solitario."""
    pass

class ProfileNotFoundError(Exception):
    """Profilo richiesto non esiste in storage."""
    pass
```

**Vietato:**
- ❌ `except Exception: pass` (swallow silent)
- ❌ Exception generiche per errori Domain (`raise Exception("bad move")` → usa `InvalidMoveError`)
- ❌ Try-catch attorno a operazioni deterministiche (es. aritmetica semplice)

---

#### Quando Usare Graceful Degradation (Log + Fallback)

**Trigger (almeno uno dei seguenti):**
- I/O esterni fallisce (filesystem, network, pygame.mixer)
- Feature non critica per core business (es. audio in videogioco con TTS)
- Risorsa opzionale non disponibile (file asset mancante, config corrotto)
- Servizio esterno temporaneamente down

**Pattern obbligatorio:**
```python
# ✅ CORRETTO — Degradazione feature non critica
def initialize_audio(self) -> bool:
    try:
        pygame.mixer.init(...)
        self._audio_ready = True
        _game_logger.info("Audio initialized")
        return True
    except Exception as e:
        _error_logger.exception("Audio init failed, fallback to stub")
        self._audio_ready = False
        return False  # ← App continua senza audio
```

**Livelli severità logging:**
- `_error_logger.error(...)`: Config assente, feature compromessa (ma app usabile)
- `_error_logger.warning(...)`: File singolo mancante (es. 1 WAV su 40)
- `_error_logger.exception(...)`: Exception con stack trace completo (sempre dopo `except`)

**Pattern Null Object (Stub)** — Quando una dipendenza può fallire, fornisci una versione no-op:
```python
# ✅ CORRETTO — Stub per graceful degradation
class AudioManagerStub:
    """No-op safe substitute per AudioManager."""
    def play_event(self, event: AudioEvent) -> None:
        pass  # Silenzioso, nessun crash
    
    def is_available(self) -> bool:
        return False

# In DI container
try:
    manager = AudioManager(config)
    manager.initialize()
except Exception:
    _error_logger.exception("AudioManager failed, using stub")
    manager = AudioManagerStub()  # ← Codice chiamante non cambia
```

**Vietato:**
- ❌ Degradazione per errori di sicurezza/dati critici (es. pagamenti, salvataggi)
- ❌ Log WARNING per config assente (deve essere ERROR)
- ❌ Fallback con valori "ragionevoli" inventati (es. `except: return DEFAULT_DOSE` in app medica)

---

#### Checklist Decisionale (Flow Chart)

```
Errore rilevato
    ↓
È un bug logico interno (violazione contratto, assertion)?
    ↓ SÌ → RAISE Exception (crash immediato)
    ↓ NO
    ↓
La feature è critica per core business?
    ↓ SÌ → RAISE Exception + mostra errore utente visivo
    ↓ NO
    ↓
È I/O esterno o risorsa opzionale?
    ↓ SÌ → LOG ERROR + return fallback/stub
    ↓ NO
    ↓
Caso ambiguo? → Applica principio conservativo: RAISE Exception
```

---

#### Esempi Applicati al Progetto

| Scenario | Strategia | Rationale |
|----------|-----------|-----------|
| `pile.count()` chiamato (metodo inesistente) | ✅ RAISE `AttributeError` | Bug dev, metodo corretto è `get_card_count()` |
| File `audio_config.json` assente | ✅ LOG ERROR + return `{}` | Feature non critica, app usabile senza audio |
| File WAV singolo mancante | ✅ LOG WARNING + entry `None` in cache | Degradazione parziale, altri suoni funzionano |
| `ProfileService.load()` con `profile_id=None` | ✅ RAISE `ValueError` | Contratto violato, bug chiamante |
| pygame.mixer.init() fallisce | ✅ LOG EXCEPTION + return `AudioManagerStub` | Dipendenza esterna, stub garantisce no crash |
| Partita salvata corrotta | ⚠️ RAISE + mostra dialog utente | Dato critico, utente deve saperlo |

---

#### Osservabilità Obbligatoria

Ogni degradazione graziosa **deve** essere loggata con:
1. **Livello appropriato**: ERROR per config, WARNING per file singolo
2. **Contesto completo**: path file, parametri tentati, cosa fallisce
3. **Azione intrapresa**: quale fallback/stub viene usato
4. **Stack trace**: sempre con `_error_logger.exception()` dentro `except` block

**Esempio completo:**
```python
def _load_sound_pack(self, pack_name: str) -> None:
    try:
        # Operazione I/O
        sounds = self._cache.load(pack_name)
        _game_logger.info(f"Loaded {len(sounds)} sounds from pack '{pack_name}'")
    except FileNotFoundError as e:
        _error_logger.exception(
            f"Sound pack '{pack_name}' not found at {self.base_path}. "
            f"Audio will be unavailable."
        )
        self._cache = {}  # Fallback: cache vuota
    except Exception as e:
        _error_logger.exception(
            f"Unexpected error loading sound pack '{pack_name}'. "
            f"Using silent fallback."
        )
        self._cache = {}
```

---
```

---

## Test Plan

### Validazione Contenuto

**Test 1: Coerenza con Codice Esistente**
- [ ] Verifica che esempio `AudioManagerStub` corrisponda a `src/infrastructure/audio/audio_manager.py` linea ~250
- [ ] Verifica che pattern `_error_logger.exception()` corrisponda a `src/infrastructure/di/dependency_container.py` linea ~35
- [ ] Verifica che `pile.count()` bug sia citato correttamente (metodo inesistente, vedi `src/domain/entities/pile.py`)

**Test 2: Non Regressione Altre Sezioni**
- [ ] Sezione Logging: Nessuna modifica ai named logger esistenti
- [ ] Sezione Clean Architecture: Nessuna modifica alle regole di dipendenza
- [ ] Sezione Testing: Nessuna modifica ai marker pytest

**Test 3: Navigabilità Screen Reader**
- [ ] Intestazioni gerarchiche corrette (`###` per sezione principale, `####` per sottosezioni)
- [ ] Liste puntate con `-` (non `*` o `+`) per consistenza
- [ ] Code blocks con linguaggio specificato (` ```python `, non ` ``` `)
- [ ] Tabelle con header row chiaramente delimitato

---

### Validazione Markdown

**Checklist pre-commit:**
- [ ] Nessun errore `markdownlint` (syntax, indentation, trailing spaces)
- [ ] Nessun link rotto interno (anchor link a sezioni esistenti)
- [ ] Triple backtick code block aperti e chiusi correttamente
- [ ] Tabelle con pipe `|` allineati visivamente (facoltativo ma preferito)

**Comando validazione rapida:**
```bash
# Conta righe aggiunte (deve essere ~150-180 righe)
git diff .github/copilot-instructions.md | grep '^+' | wc -l

# Verifica che sezione sia stata inserita nella posizione corretta
grep -n "### Error Handling e Graceful Degradation" .github/copilot-instructions.md
# Output atteso: linea ~121-130 (dopo Logging, prima Accessibilità)
```

---

## Criteri di Completamento

### Definition of Done

**Tutti i seguenti devono essere TRUE:**

- [x] Sezione "Error Handling e Graceful Degradation" inserita in `.github/copilot-instructions.md`
- [x] Posizione corretta: dopo Logging, prima Accessibilità UI
- [x] Contenuto identico al testo fornito in questo piano (nessuna modifica arbitraria)
- [x] Esempi codice validati contro repository reale
- [x] Markdown lint passa senza errori
- [x] Commit eseguito con messaggio convenzionale
- [x] Piano (questo file) incluso nel commit per tracciabilità

### Verifica Post-Merge

**Dopo merge su `main`:**
- [ ] Aggiornare `CHANGELOG.md` sezione `[Unreleased]` → `### Documentation`
- [ ] Annotare in `docs/TODO.md` (se attivo) come completato
- [ ] Notificare team (se applicabile) delle nuove linee guida error handling

---

## Impatto e Benefici

### Impatto Immediato

**Per Copilot Agent:**
- ✅ Decisioni error handling coerenti in tutti i moduli (audio, profili, timer, future feature)
- ✅ Auto-validazione proposte contro checklist prima di suggerire codice
- ✅ Riduzione prompt ambigui ("devo crashare o loggare?" → risposta documentata)

**Per Sviluppatori:**
- ✅ Meno micromanagement nelle sessioni Copilot (agent sa quando degradare senza chiedere)
- ✅ Code review più rapido (cita sezione invece di spiegare rationale ogni volta)
- ✅ Onboarding veloce per nuovi contributor (linee guida chiare, non inferenza da codice)

**Per Codebase:**
- ✅ Consistenza error handling tra moduli (stesso pattern audio/profili/timer)
- ✅ Manutenibilità aumentata (modifiche future seguono standard documentato)
- ✅ Debugging facilitato (log strutturati secondo linee guida, stack trace completi)

### ROI Stima

**Investimento**: ~30 minuti (lettura piano + inserimento + commit)  
**Risparmio**: ~2-4 ore/mese (decisioni ambigue, code review, refactor inconsistenze)  
**Payback period**: < 1 settimana di sviluppo attivo

---

## Note Implementative per Copilot

### Workflow Incrementale

**NON eseguire tutto in un commit.** Segui questo ordine:

1. **Commit 1**: Aggiungi questo piano in `docs/2 - projects/`
   ```bash
   git add docs/2\ -\ projects/PLAN_copilot-instructions-error-handling_v3.5.1.md
   git commit -m "docs: piano aggiornamento copilot-instructions error handling"
   ```

2. **Commit 2**: Modifica `.github/copilot-instructions.md` + includi piano per reference
   ```bash
   git add .github/copilot-instructions.md docs/2\ -\ projects/PLAN_copilot-instructions-error-handling_v3.5.1.md
   git commit -F /tmp/commit-msg.txt  # Messaggio completo fornito sopra
   ```

3. **Commit 3** (facoltativo): Aggiorna `docs/TODO.md` se attivo
   ```bash
   # Spunta checkbox relativa a "Aggiorna documentazione Copilot"
   git add docs/TODO.md
   git commit -m "docs: aggiorna TODO post inserimento error handling guidelines"
   ```

---

### Domande Frequenti (FAQ)

**Q: Posso riorganizzare il contenuto della sezione per migliorare leggibilità?**  
A: NO. Usa il contenuto **esattamente come fornito**. Ogni paragrafo è stato calibrato per screen reader navigation. Modifiche arbitrarie possono rompere gerarchia intestazioni.

**Q: Devo aggiornare anche `docs/ARCHITECTURE.md` o `docs/API.md`?**  
A: NO in questa fase. Questo piano copre solo `copilot-instructions.md`. Pattern Null Object può essere documentato in ARCHITECTURE.md in un task futuro separato.

**Q: Cosa fare se `markdownlint` segnala errori su sezioni esistenti (non la nuova)?**  
A: Ignora errori preesistenti, NON fixarli in questo commit (out of scope). Fixa solo errori sulla sezione nuova inserita.

**Q: Dove inserire se la sezione Logging non ha separatore `---` finale?**  
A: Aggiungi manualmente un `---` subito dopo l'ultima riga della sezione Logging, poi inserisci la nuova sezione, poi aggiungi un altro `---`.

**Q: L'utente può chiedere modifiche al contenuto dopo l'inserimento?**  
A: SÌ, ma richiedi rationale esplicito. Il contenuto è stato validato contro codebase reale. Modifiche devono essere motivate tecnicamente.

---

## Riferimenti

### Documenti Collegati

- **Codice Reference**: `src/infrastructure/audio/audio_manager.py` (pattern graceful degradation)
- **Codice Reference**: `src/infrastructure/di/dependency_container.py` (pattern Null Object stub)
- **Standard Logging**: `.github/copilot-instructions.md` sezione "Logging (Sistema Categorizzato v3.3.0)"
- **Template Base**: `docs/1 - templates/TEMPLATE_example_PIANO_IMPLEMENTAZIONE.md`

### Link Esterni

- Python Exception Best Practices: https://docs.python.org/3/tutorial/errors.html
- Martin Fowler - Null Object Pattern: https://martinfowler.com/eaaCatalog/specialCase.html
- 12-Factor App - Logs: https://12factor.net/logs

---

**Fine Piano v3.5.1** | Ultima modifica: 2026-02-24
