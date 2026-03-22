# Copilot Instructions Template - Ecosistema di Template e Guida Personalizzazione

Questo file contiene due risorse complementari per configurare GitHub Copilot in progetti Python con Clean Architecture:

## Contenuto

1. **COPILOT INSTRUCTIONS TEMPLATE** — Template universale per istruzioni Copilot personalizzabili, con sezioni su architettura, logging, error handling, testing e convenzioni git.

2. **CUSTOMIZATION GUIDE** — Guida step-by-step per adattare il template al tuo progetto specifico: sostituzione placeholder, compilazione critical warnings, configurazione logger e strumenti di validazione.

Entrambi i file devono essere posizionati in `docs/1 - templates/` per costituire la base di documentazione riutilizzabile per nuovi progetti con architettura pulita.


## File 1: `docs/1 - templates/COPILOT_INSTRUCTIONS_TEMPLATE.md`

```markdown
# Copilot Instructions Template - Clean Architecture Projects

**Versione**: 1.0.0  
**Ultima revisione**: 2026-02-24  
**Scopo**: Template universale per progetti Python con Clean Architecture a 4 layer  
**Come usare**: 
1. Copia questo file in `.github/copilot-instructions.md` del tuo progetto
2. Cerca tutti i placeholder `{VARIABILE}` e sostituiscili con valori specifici
3. Compila la sezione "Critical Warnings" con regole del tuo dominio
4. Consulta `CUSTOMIZATION_GUIDE.md` per dettagli su ogni placeholder

---

## 👤 Profilo Utente e Interazione

* **Accessibilità Prima di Tutto**: L'utente utilizza screen reader `{SCREEN_READER_NAME}` (es. NVDA, JAWS, VoiceOver) su `{OS}` (Windows/Linux/macOS). Ogni proposta deve essere testabile da tastiera e compatibile con screen reader.
* **Feedback Testuale Strutturato**: Quando proponi modifiche, fornisci sempre:
  1. **Cosa**: Lista puntata delle modifiche applicate (file + line numbers)
  2. **Perché**: Rationale tecnico (1-2 frasi)
  3. **Impatto**: File di documentazione da aggiornare (se applicabile)
* **Formattazione Markdown**: Usa intestazioni gerarchiche (`##`, `###`) e liste (`-`, `1.`) per navigazione screen reader. Evita tabelle complesse o layout ASCII decorativi.
* **No Jargon Visivo**: Non usare espressioni come "come puoi vedere", "guarda qui", "nella parte superiore". Usa riferimenti testuali: "nel file X, linea Y", "nella sezione Z".

---

## 🏗️ Architettura e Standard di Codifica

### Clean Architecture (Strict Enforcement)

Il progetto segue **Clean Architecture a 4 layer**. Ogni modifica deve rispettare queste dipendenze:

```
Presentation → Application → Domain ← Infrastructure
    ↓              ↓            ↑
  (UI)       (Use Cases)   (Entities)
```

**Regole:**
- **Domain** (`src/domain/`): Zero dipendenze esterne. Solo entity, value objects, domain services, business rules.
- **Application** (`src/application/`): Dipende solo da Domain. Contiene use cases, command patterns, application services.
- **Infrastructure** (`src/infrastructure/`): Implementa interfacce Domain (repositories, external services, UI framework).
- **Presentation** (`src/presentation/`): Dipende da Application. Contiene formatters, dialogs, view logic.

**Vietato:**
- ❌ Import `src.infrastructure.*` dentro `src.domain.*`
- ❌ Import `{UI_FRAMEWORK}` (es. wx, tkinter, Qt) fuori da `src.infrastructure.ui.*`
- ❌ Import `src.application.*` dentro `src.domain.*`
- ❌ Business logic nei componenti UI (`src.presentation.*`)

**Esempio corretto di refactoring:**
```python
# ❌ ERRATO (Domain dipende da Infrastructure)
# src/domain/services/entity_service.py
from src.infrastructure.ui.dialogs import NotificationDialog  # ❌

# ✅ CORRETTO (Domain espone interfaccia, Infrastructure implementa)
# src/domain/services/entity_service.py
def complete_operation(self, entity_id: str, success: bool) -> Dict[str, Any]:
    # Ritorna dati, non mostra UI
    return {"success": success, "entity_id": entity_id, "data": self.get_data()}

# src/application/use_case_orchestrator.py (orchestrazione)
def complete_operation(self, entity_id: str, success: bool) -> None:
    result = self.entity_service.complete_operation(entity_id, success)
    if self.use_native_dialogs:
        self._show_notification(result)  # Infrastructure layer
```

---

### Naming Conventions

* **Variabili/Funzioni**: `snake_case` (es. `load_resource`, `item_count`, `validate_input`)
* **Classi**: `PascalCase` (es. `EntityService`, `ApplicationOrchestrator`, `DataRepository`)
* **Costanti**: `UPPER_SNAKE_CASE` (es. `MAX_RETRY_ATTEMPTS`, `DEFAULT_TIMEOUT`, `CONFIG_PATH`)
* **Private/Protected**: Prefisso `_` (es. `_internal_helper`, `_validate_state`, `_cache_data`)
* **Type Hints**: Sempre obbligatori per metodi pubblici

---

### Type Hints Enforcement

**Vietato:**
- ❌ `collection.count()` → AttributeError (metodo inesistente o non implementato)
- ❌ Implicit returns senza annotazione
- ❌ `Any` come type hint di default senza giustificazione

**Obbligatorio:**
- ✅ `collection.get_count() -> int`
- ✅ Ogni public method con return type esplicito
- ✅ Parametri con type hints anche per metodi privati

---

### Logging (Sistema Categorizzato)

**MAI usare `print()` nel codice di produzione.** Usa i named logger dedicati per categoria:

```python
import logging

# Named logger per categoria — scegli quello corretto per contesto
_business_logger = logging.getLogger('business')  # logica core business, operazioni dominio
_ui_logger       = logging.getLogger('ui')        # navigazione UI, dialogs, interazioni utente
_data_logger     = logging.getLogger('data')      # persistence, repository, I/O database
_error_logger    = logging.getLogger('error')     # errori, warnings, eccezioni
```

**Routing dei file di output (personalizza in `{PROJECT_NAME}/logging_config.py`):**
- `business` → `logs/business.log`
- `ui`       → `logs/ui_events.log`
- `data`     → `logs/data_access.log`
- `error`    → `logs/errors.log`
- root       → `logs/{PROJECT_NAME}.log` (library logs di terze parti)

**Regola propagate=False:** ogni named logger dovrebbe avere `propagate=False` per evitare duplicazione nei log root. Modifica questo comportamento solo se hai un rationale documentato.

**Pattern semantic logging (crea helpers project-specific):**
```python
# Esempio: src/infrastructure/logging/business_logger.py
def log_business_event(event_type: str, entity_id: str, details: Dict[str, Any]) -> None:
    _business_logger.info(f"Event: {event_type} | Entity: {entity_id} | Details: {details}")

def log_operation_start(operation_name: str, params: Dict[str, Any]) -> None:
    _business_logger.debug(f"Starting {operation_name} with params: {params}")
```

**Vietato:**
- ❌ `print(f"Debug: {variable}")` → usa `logging.getLogger('business').debug()`
- ❌ Log con emoji o box ASCII → screen reader unfriendly
- ❌ `logging.getLogger()` (root logger) nel codice applicativo → usa named loggers
- ❌ Log in Domain layer senza dependency injection

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
def process_entity(self, entity_id: str, index: int) -> None:
    if index < 0 or index >= self.max_entities:
        raise ValueError(f"Invalid entity index: {index}")  # Bug dev
```

**Custom Exceptions** — Crea sottoclassi di `Exception` solo per errori Domain-specific:
```python
# src/domain/exceptions.py
class DomainError(Exception):
    """Base class per errori Domain-specific."""
    pass

class InvalidOperationError(DomainError):
    """Operazione non valida per lo stato corrente dell'entità."""
    pass

class EntityNotFoundError(DomainError):
    """Entità richiesta non esiste in storage."""
    pass
```

**Vietato:**
- ❌ `except Exception: pass` (swallow silent)
- ❌ Exception generiche per errori Domain (`raise Exception("bad operation")` → usa `InvalidOperationError`)
- ❌ Try-catch attorno a operazioni deterministiche (es. aritmetica semplice)

---

#### Quando Usare Graceful Degradation (Log + Fallback)

**Trigger (almeno uno dei seguenti):**
- I/O esterni fallisce (filesystem, network, database connection)
- Feature non critica per core business (es. notifiche email, analytics)
- Risorsa opzionale non disponibile (file asset mancante, config corrotto)
- Servizio esterno temporaneamente down

**Pattern obbligatorio:**
```python
# ✅ CORRETTO — Degradazione feature non critica
def initialize_external_service(self) -> bool:
    try:
        self.service_client.connect()
        self._service_ready = True
        _business_logger.info("External service initialized")
        return True
    except Exception as e:
        _error_logger.exception("External service init failed, fallback to stub")
        self._service_ready = False
        return False  # ← App continua senza servizio
```

**Livelli severità logging:**
- `_error_logger.error(...)`: Config assente, feature compromessa (ma app usabile)
- `_error_logger.warning(...)`: Risorsa singola mancante (es. 1 file su 40)
- `_error_logger.exception(...)`: Exception con stack trace completo (sempre dopo `except`)

**Pattern Null Object (Stub)** — Quando una dipendenza può fallire, fornisci una versione no-op:
```python
# ✅ CORRETTO — Stub per graceful degradation
class _ExternalServiceStub:
    """No-op safe substitute per ExternalService."""
    def send_notification(self, message: str) -> None:
        pass  # Silenzioso, nessun crash
    
    @property
    def is_available(self) -> bool:
        return False

# In DI container
try:
    service = ExternalService(config)
    service.initialize()
except Exception:
    _error_logger.exception("ExternalService failed, using stub")
    service = _ExternalServiceStub()  # ← Codice chiamante non cambia
```

**Vietato:**
- ❌ Degradazione per errori di sicurezza/dati critici (es. auth, transazioni)
- ❌ Log WARNING per config assente (deve essere ERROR)
- ❌ Fallback con valori "ragionevoli" inventati senza contesto

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
    ↓ SÌ → RAISE Exception + mostra errore utente
    ↓ NO
    ↓
È I/O esterno o risorsa opzionale?
    ↓ SÌ → LOG ERROR + return fallback/stub
    ↓ NO
    ↓
Caso ambiguo? → Applica principio conservativo: RAISE Exception
```

---

#### Esempi Applicati (Template Generico)

| Scenario | Strategia | Rationale |
|----------|-----------|-----------|
| `entity.invalid_method()` chiamato | ✅ RAISE `AttributeError` | Bug dev, metodo non implementato |
| File `feature_config.json` assente | ✅ LOG ERROR + return `{}` | Feature non critica, app usabile con defaults |
| File asset singolo mancante | ✅ LOG WARNING + entry `None` in cache | Degradazione parziale |
| `EntityService.load()` con `id=None` | ✅ RAISE `ValueError` | Contratto violato, bug chiamante |
| `external_service.init()` fallisce | ✅ LOG EXCEPTION + return stub | Dipendenza esterna, stub garantisce no crash |
| Dato critico corrotto (user auth) | ⚠️ RAISE + mostra dialog utente | Dato critico, utente deve saperlo |

---

#### Osservabilità Obbligatoria

Ogni degradazione graziosa **deve** essere loggata con:
1. **Livello appropriato**: ERROR per config, WARNING per risorsa singola
2. **Contesto completo**: path file, parametri tentati, cosa fallisce
3. **Azione intrapresa**: quale fallback/stub viene usato
4. **Stack trace**: sempre con `_error_logger.exception()` dentro `except` block

**Esempio completo:**
```python
def _load_config(self, config_name: str) -> Dict[str, Any]:
    try:
        config = self._config_loader.load(config_name)
        _business_logger.info(f"Loaded config '{config_name}'")
        return config
    except FileNotFoundError:
        _error_logger.exception(
            f"Config '{config_name}' not found at {self.config_path}. "
            f"Using default configuration."
        )
        return self._get_default_config()  # Fallback
    except Exception:
        _error_logger.exception(
            f"Unexpected error loading config '{config_name}'. "
            f"Using safe defaults."
        )
        return {}
```

---

### Accessibilità UI (WAI-ARIA + Keyboard)

Ogni componente UI deve rispettare:

**Checklist obbligatoria:**
- [ ] Ogni controllo ha label descrittivo (accessibile a screen reader)
- [ ] Bottoni critici hanno acceleratori (es. `&OK`, `&Annulla`, `Alt+O`)
- [ ] Dialog hanno titolo semantico (letto all'apertura da screen reader)
- [ ] Focus management: focus automatico su primo controllo navigabile
- [ ] ESC chiude dialog (binding standard)
- [ ] TAB naviga tutti i controlli in ordine logico
- [ ] No elementi puramente decorativi senza `aria-hidden`

**Pattern specifico per `{UI_FRAMEWORK}`:**
```python
# Esempio per wxPython (sostituire con framework del progetto)
dialog.SetTitle("Titolo Semantico")
button_ok.SetLabel("&OK")
button_ok.SetFocus()
```

---

## ⚠️ Critical Warnings (Project-Specific)

**Istruzioni per personalizzazione**: Aggiungi qui 3-7 regole critiche del tuo progetto che NON devono MAI essere violate. Ogni warning deve includere:
- Nome breve (max 4 parole)
- Descrizione del vincolo
- Conseguenza della violazione
- Esempio corretto

**Template warning:**
```
N. **Nome Warning**: Descrizione breve del vincolo tecnico o di dominio.
   Conseguenza: cosa succede se violato.
   Pattern corretto: codice o procedura da seguire.
```

**Esempi da altri progetti (da sostituire con i tuoi):**
1. **Protected Entity Immutability**: L'entità `{ENTITY_NAME}` non deve essere modificata direttamente dopo creazione. Usa sempre `EntityService.update()`.
2. **Singleton Service**: `{SERVICE_NAME}` deve essere singleton applicativo. MAI creare istanze multiple con `new`.
3. **API Breaking Changes**: Modifiche ai metodi pubblici di `{MODULE_NAME}` richiedono major version bump (SemVer).

---

## 📚 Protocollo Allineamento Documentazione (Mandatorio)

### Struttura Cartella `docs/`

```
docs/
├── 1 - templates/          # Template riutilizzabili (PR body, design doc, TODO)
├── 2 - projects/           # Design doc, diagrammi di flusso testuali e analisi architetturali
│   └── DESIGN_*.md         # Analisi architetturale di una feature (accessibile: solo testo e ASCII)
├── 3 - coding plans/       # Piani di sviluppo, implementazioni, codifiche, revisioni e fix
│   └── PLAN_*.md           # Piano di implementazione/fix con checklist
├── API.md                  # Riferimento API pubblica di tutti i moduli
├── ARCHITECTURE.md         # Architettura del sistema e data flow
├── TESTING.md              # Guida testing e convenzioni
└── TODO.md                 # Cruscotto operativo del branch attivo (stato: IN PROGRESS / DONE)
```

**Regole di posizionamento:**
- Un nuovo design doc → `docs/2 - projects/DESIGN_<feature>.md`
- Un piano di fix/implementazione → `docs/3 - coding plans/PLAN_<descrizione>_vX.Y.Z.md`
- `docs/TODO.md` esiste solo durante un branch di lavoro attivo; è il cruscotto
  operativo da spuntare durante l'implementazione. Va aggiornato dopo ogni commit.

---

### Creazione File di Progetto (Design Doc, Piano, TODO)

Ogni nuovo task non banale richiede la creazione di uno o più file di progetto **prima** di scrivere codice. I modelli si trovano in `docs/1 - templates/`.

#### Quando creare un DESIGN Document

**Trigger (almeno uno dei seguenti):**
- L'utente descrive una nuova feature con comportamento non ovvio
- Il task implica decisioni architetturali (nuovo layer, nuovo pattern, nuovi attori)
- La feature coinvolge più di 3 file distinti in layer diversi
- Ci sono alternative di design da confrontare

**Template da usare:** `docs/1 - templates/TEMPLATE_DESIGN_DOCUMENT.md`

**Nome file output:** `docs/2 - projects/DESIGN_<feature-slug>.md`

**Contenuto minimo obbligatorio:**
- Metadata (data, stato, versione target)
- Idea in 3 righe (cosa, perché, problema risolto)
- Attori e concetti chiave
- Flussi concettuali (no decisioni tecniche in questa fase)

---

#### Quando creare un PLAN (Piano di Implementazione)

**Trigger (almeno uno dei seguenti):**
- Il task richiede più di 2 commit atomici
- Esiste già un DESIGN doc approvato da implementare
- Si tratta di un bugfix con root cause analisi richiesta
- Il task è un refactoring su più file

**Template da usare:** `docs/1 - templates/TEMPLATE_PIANO_IMPLEMENTAZIONE.md`

**Nome file output:** `docs/3 - coding plans/PLAN_<descrizione-slug>_vX.Y.Z.md`

**Contenuto minimo obbligatorio:**
- Executive Summary (tipo, priorità, stato, branch, versione target)
- Problema/Obiettivo (o Root Cause se bugfix)
- Lista file coinvolti con tipo operazione (CREATE / MODIFY / DELETE)
- Fasi di implementazione in ordine sequenziale
- Test plan (unit + integration)
- Criteri di completamento

---

#### Quando creare/aggiornare il TODO

**Trigger creazione (tutti devono essere veri):**
- Esiste un PLAN approvato (stato READY)
- Il branch di lavoro è attivo
- L'implementazione multi-fase è appena iniziata

**Template da usare:** `docs/1 - templates/TEMPLATE_TODO.md`

**Nome file output:** `docs/TODO.md` (uno solo, sostituisce il precedente ad ogni branch)

**Regole operative:**
- Il TODO è un **cruscotto**, non un documento tecnico: sommario operativo consultabile in 30 secondi
- Il link al PLAN completo (fonte di verità) deve essere in cima al TODO
- Ogni checkbox spuntata corrisponde a un commit già eseguito
- Va aggiornato **dopo ogni commit**, non in batch a fine lavoro
- Al merge su `main` il TODO viene archiviato o eliminato

---

#### Relazione tra i Tre File (Flusso Canonico)

```
DESIGN_<feature>.md          (CONCEPT - "cosa vogliamo")
      ↓  approva
PLAN_<feature>_vX.Y.Z.md     (TECNICO - "come lo facciamo")
      ↓  inizia
docs/TODO.md                 (OPERATIVO - "dove siamo")
      ↓  aggiorna dopo ogni commit
      ↓  a merge completato → archivia/elimina TODO
```

---

### Protocollo Obbligatorio Pre-Codifica (TODO Gate)

> **Questo protocollo è un gate bloccante.** Prima di scrivere qualsiasi riga di codice, Copilot DEVE eseguire i seguenti check nell'ordine indicato.

#### Trigger di attivazione

Il protocollo si attiva quando l'utente emette una richiesta di implementazione che soddisfa **almeno uno** dei seguenti criteri:
- Richiede modifica o creazione di file `.py`
- Fa riferimento esplicito a un DESIGN doc o a un PLAN esistente
- Usa parole come "implementa", "codifica", "inizia", "procedi con", "sviluppa"
- Coinvolge più di 2 file o più di 1 commit

#### Step 1 — Verifica esistenza `docs/TODO.md`

```
Se docs/TODO.md NON esiste:
    → Crea docs/TODO.md da TEMPLATE_TODO.md
    → Compila: link al PLAN attivo, obiettivo, lista file, checklist fasi
    → Comunica all'utente: "Ho creato docs/TODO.md per tracciare questa implementazione."
    → Procedi allo Step 3

Se docs/TODO.md ESISTE:
    → Procedi allo Step 2
```

#### Step 2 — Verifica coerenza del TODO esistente

Leggi le prime righe di `docs/TODO.md` e verifica che il link al PLAN corrisponda al PLAN attivo per il task corrente.

```
Se docs/TODO.md appartiene a un PLAN DIVERSO dal task corrente:
    → NON sovrascrivere silenziosamente
    → Notifica l'utente:
      "docs/TODO.md è riferito a [nome PLAN precedente] e potrebbe essere obsoleto.
       Vuoi che lo sostituisca con un TODO per [nome PLAN corrente]?"
    → Attendi conferma prima di procedere

Se docs/TODO.md corrisponde al task corrente ma ha checkbox già spuntate:
    → È un TODO in corso: identifica la prima fase non completata
    → Riprendi da quella fase (non ricominciare dall'inizio)
    → Comunica all'utente: "Riprendo dall'ultima fase completata: [nome fase]."

Se docs/TODO.md corrisponde e tutte le checkbox sono vuote:
    → Tutto in ordine: procedi allo Step 3
```

#### Step 3 — Caricamento documenti di riferimento

Prima di codificare il primo step, leggi (o rileggi se già letti in sessione):

1. `docs/TODO.md` → identifica la **prima fase non completata** (prima checkbox vuota)
2. Il PLAN linkato nel TODO → recupera i dettagli tecnici della fase da implementare
3. Il DESIGN linkato nel PLAN (se esiste) → verifica che i concetti architetturali siano allineati

#### Step 4 — Loop incrementale di implementazione

Per ogni fase/step del TODO, esegui questo ciclo senza eccezioni:

```
Per ogni fase non completata in docs/TODO.md:

    1. LEGGI  → La descrizione della fase nel TODO + i dettagli nel PLAN
    2. CODIFICA → Implementa solo quella fase (non anticipare la successiva)
    3. VERIFICA → Esegui pre-commit checklist (syntax, type hints, logging)
    4. COMMIT  → Copilot propone il messaggio di commit atomico convenzionale; l'utente lo esegue manualmente
    5. SPUNTA  → Aggiorna docs/TODO.md: [x] per la fase appena completata
    6. COMUNICA → Notifica l'utente: "Fase N completata: [descrizione]. Ecco il commit suggerito: `<type>(<scope>): <subject>`. Proseguo con Fase N+1?"
    7. ATTENDI  → Ricevi conferma prima di passare alla fase successiva
```

**Regola di atomicità**: ogni commit copre esattamente una fase del TODO. Non accorpare fasi, non anticipare fasi future.

**Regola di consultazione**: tra un commit e l'altro, rileggi sempre il TODO aggiornato e il PLAN prima di iniziare la fase successiva. Non procedere a memoria.

---

### Trigger Events (quando aggiornare docs)

Dopo **ogni modifica al codice** (`.py`), esegui questo audit:

**1. API.md** — Aggiorna se modifichi signature metodi pubblici, classi esportate da `__init__.py`, enum/costanti pubbliche, comportamento documentato.

**2. ARCHITECTURE.md** — Aggiorna se modifichi struttura cartelle, data flow tra layer, design patterns, dipendenze esterne (`requirements.txt`).

**3. CHANGELOG.md** — Aggiorna **sempre** prima del commit nel branch di sviluppo: nuove feature → `Added`, bug fix → `Fixed`, breaking changes → `Changed` + ⚠️. La sezione `[Unreleased]` viene rinominata in `[X.Y.Z] — YYYY-MM-DD` solo al momento del merge su `main`.

**4. README.md** — Aggiorna se modifichi entry point, comandi CLI, requisiti sistema, passi di setup.

---

### Workflow di Sync (Step-by-Step)

Quando l'utente dice *"applica le modifiche"*:

1. **Esegui modifiche codice** (`.py` files)
2. **Audit immediato**: elenca file modificati, dichiara impatto su API.md / ARCHITECTURE.md / CHANGELOG.md (richiede aggiornamento / nessun impatto)
3. **Proposta aggiornamento**: chiedi conferma per ogni doc da aggiornare
4. **Applica aggiornamenti docs** se confermato
5. **Verifica finale**: conferma che codice e documentazione sono sincronizzati

---

## 🛠️ Testing e Validazione

### Test Coverage Requirement

- **Minimum**: 85% coverage per `src/domain/` e `src/application/`
- **Target**: 90%+ coverage globale
- Ogni nuovo metodo pubblico **deve** avere almeno 1 test unitario

**Comando pre-commit:**
```bash
pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=85
```

---

### Test Pattern (Esempio da seguire)

```python
# tests/domain/services/test_entity_service.py
import pytest
from src.domain.services.entity_service import EntityService

class TestEntityService:
    @pytest.fixture
    def service(self, tmp_path):
        """Setup con storage temporaneo."""
        return EntityService(storage_path=tmp_path)
    
    def test_load_entity_creates_if_missing(self, service):
        """Verifica creazione entità se non esiste."""
        # Arrange
        entity_id = "test_001"
        assert not service.storage.exists(entity_id)
        
        # Act
        result = service.load_or_create(entity_id)
        
        # Assert
        assert result is not None
        assert service.storage.exists(entity_id)
        entity = service.storage.load(entity_id)
        assert entity.id == entity_id
```

**Naming convention test:**
- `test_<method>_<scenario>_<expected_behavior>`
- Esempio: `test_load_entity_with_invalid_id_raises_error`

---

### Marker Pytest e CI Strategy

**Marker obbligatori — applicali sempre:**

```python
@pytest.mark.unit         # Test senza dipendenze esterne (no UI, no filesystem reale)
@pytest.mark.integration  # Test tra layer senza UI (es. Application + Domain)
@pytest.mark.gui          # Test che richiedono UI framework e display
```

**Regole di assegnazione:**
- Test che usano solo `tmp_path`, mock, o oggetti puri → `@pytest.mark.unit`
- Test che istanziano componenti UI (`{UI_FRAMEWORK}`) → `@pytest.mark.gui`
- Test di integrazione tra layer senza UI → `@pytest.mark.integration`

**Comandi standard:**
```bash
pytest -m "unit" -v                           # Fast tests (headless safe)
pytest -m "unit or integration" -v            # CI-safe (no GUI)
pytest -v                                     # All tests (richiede display per GUI)
```

**Isolamento test logging:** il modulo `logging` di Python è un singleton di processo. Qualsiasi test che configura logging **deve** avere una fixture di cleanup. Esempio:

```python
@pytest.fixture
def reset_logging():
    """Reset logging configuration prima e dopo ogni test."""
    # Pre-test cleanup
    logging.root.handlers.clear()
    yield
    # Post-test cleanup
    logging.root.handlers.clear()
```

---

## 🔍 Pre-Commit Checklist (Auto-Eseguita)

Prima di ogni commit, verifica silentemente:

1. **Syntax**: `python -m py_compile src/**/*.py` (0 errori)
2. **Type Hints**: `mypy src/ --strict --python-version {PYTHON_VERSION}` (0 errori)
3. **Imports**: `pylint src/ --disable=all --enable=cyclic-import` (nessun import circolare)
4. **Logging**: `grep -r "print(" src/ --include="*.py" --exclude="__main__.py"` (0 occorrenze)
5. **Formatting** (opzionale): `black src/ --check` (se usato nel progetto)
6. **Import Sorting** (opzionale): `isort src/ --check` (se usato nel progetto)
7. **Docs Sync**: `CHANGELOG.md` e documenti correlati aggiornati nella sessione corrente?
8. **Tests**: `pytest tests/ -m "unit or integration" --cov=src --cov-fail-under=85` (100% pass, coverage >= 85%)

**Se uno fallisce:**
```
⚠️ Pre-commit check FAILED:
- mypy: Found 3 type errors in src/domain/services/entity_service.py
- docs: CHANGELOG.md non aggiornato

Vuoi che fixo automaticamente o preferisci revisione manuale?
```

---

## 📝 Convenzioni Git Commit

### Atomic Commits Policy

**Un commit = una unità logica di cambiamento.** Regole operative:

- ✅ Un commit per file modificato se le modifiche hanno motivazioni diverse
- ✅ Un commit per task logico (es. "fix signature", "add test", "update docs")
- ❌ No mega-commit che mescolano fix di codice + aggiornamenti docs + test
- ❌ No commit "WIP" o "fix fix fix" su branch destinati alla PR

**Ordine di commit consigliato** quando si lavora su un task con dipendenze:
1. Pre-requisiti (es. aggiungere un parametro a una signature)
2. Implementazione principale
3. Test
4. Aggiornamento documentazione (API.md, CHANGELOG.md)
5. Aggiornamento cruscotto operativo (TODO.md)

---

**Format obbligatorio (Conventional Commits):**
```
<type>(<scope>): <subject>

<body (opzionale)>

<footer (opzionale)>
```

**Types:**
- `feat`: Nuova feature
- `fix`: Bug fix
- `docs`: Solo documentazione
- `refactor`: Refactoring senza cambio comportamento
- `test`: Aggiunta/modifica test
- `chore`: Maintenance (deps, build, config)

**Scope:** `domain`, `application`, `infrastructure`, `presentation`, `docs`, `tests`

**Esempio:**
```
fix(domain): corretto return type EntityService.load

- Cambiato da `-> None` a `-> Optional[Entity]`
- Aggiornato docs/API.md sezione EntityService
- Aggiunto test per entity not found (coverage +2%)
```

---

## 🌿 Branch Workflow e Release Process

### Naming branch

| Tipo | Pattern | Esempio |
|---|---|------|
| Feature | `feature/<slug>` | `feature/user-authentication` |
| Fix | `fix/<slug>` | `fix/validation-error` |
| Hotfix | `hotfix/<slug>` | `hotfix/critical-null-ref` |
| Refactor | `refactor/<slug>` | `refactor/clean-arch-domain` |
| Docs | `docs/<slug>` | `docs/api-update-v1.2` |

### Quando creare un branch vs committare su `main`

- **Branch separato**: qualsiasi feature, fix non banale, refactor, o lavoro che richiede più di 1 commit.
- **Commit diretto su `main`**: solo hotfix monocommit urgenti o aggiornamenti di documentazione pura (nessun `.py` modificato).

### Release process (step obbligatori)

1. Tutti i fix e i task del branch completati e verificati
2. PR aperta verso `main` con body che linka design doc e piano (se esistono)
3. Checklist PR spuntata (vedi template `docs/1 - templates/`)
4. Merge con **merge commit** (`--no-ff`) — preserva storia del branch (eseguire manualmente)
5. Subito dopo il merge, creare il tag di versione (suggerimento da eseguire manualmente):
   ```bash
   git checkout main
   git pull origin main
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```
6. Aggiornare footer `CHANGELOG.md`:
   - Rinominare `## [Unreleased]` in `## [X.Y.Z] — YYYY-MM-DD`
   - Aggiungere nuovo `## [Unreleased]` vuoto in cima
   - Aggiornare i link di comparazione in fondo al file

### Versionamento (SemVer)

- `MAJOR` (X): breaking changes all'API pubblica
- `MINOR` (Y): nuove feature retrocompatibili
- `PATCH` (Z): bug fix retrocompatibili

---

## 🎯 Promemoria Finale

**Quando l'utente chiede modifiche:**
0. ✅ **Verifica TODO Gate** (se task multi-file/multi-commit): controlla `docs/TODO.md`, crealo se assente, riprendi dall'ultima fase completata se in corso
1. ✅ Applica modifiche con type hints completi
2. ✅ Aggiungi logging semantico (no print)
3. ✅ Verifica accessibilità (keyboard navigation, screen reader compatibility)
4. ✅ Audit documentazione (proponi sync)
5. ✅ Esegui test coverage check
6. ✅ Fornisci riepilogo testuale strutturato

**Policy comandi Git (obbligatoria):**
Copilot NON esegue direttamente comandi `git commit`, `git push`, `git pull`, `git merge`.
Al termine dell'elaborazione, propone il/i comandi suggeriti in un blocco finale separato:

```
--- COMANDI GIT SUGGERITI (da eseguire manualmente) ---
git add <file>
git commit -m "<type>(<scope>): <subject>"
```

L'utente decide se e quando eseguirli. Comandi di sola lettura (`git log`, `git ls-tree`, `git diff`) possono essere eseguiti da Copilot come parte della verifica.

---

**Fine Template. Consulta `CUSTOMIZATION_GUIDE.md` per dettagli su come personalizzare ogni sezione.**
```

## File 2: `docs/1 - templates/CUSTOMIZATION_GUIDE.md`

```markdown
# Guida alla Personalizzazione - Copilot Instructions Template

**Versione**: 1.0.0  
**Per template**: COPILOT_INSTRUCTIONS_TEMPLATE.md v1.0.0  
**Ultima revisione**: 2026-02-24

---

## 📋 Panoramica

Questo documento spiega come personalizzare `COPILOT_INSTRUCTIONS_TEMPLATE.md` per il tuo progetto specifico. Segui i passi in ordine sequenziale.

---

## 🎯 Step 1: Copia e Setup Iniziale

1. **Copia il template**:
   ```bash
   cp docs/1\ -\ templates/COPILOT_INSTRUCTIONS_TEMPLATE.md .github/copilot-instructions.md
   ```

2. **Verifica posizionamento**: il file DEVE essere in `.github/copilot-instructions.md` per essere riconosciuto da GitHub Copilot.

3. **Commit iniziale**:
   ```bash
   git add .github/copilot-instructions.md
   git commit -m "docs: aggiungi copilot instructions da template v1.0.0"
   ```

---

## 🔧 Step 2: Sostituzione Placeholders Obbligatori

Cerca nel file tutti i placeholder racchiusi tra `{PARENTESI_GRAFFE}` e sostituiscili con valori specifici del tuo progetto.

### Placeholder da sostituire

| Placeholder | Dove si trova | Cosa inserire | Esempio |
|-------------|---------------|---------------|---------|
| `{SCREEN_READER_NAME}` | Sezione "Profilo Utente" | Nome screen reader usato | `NVDA`, `JAWS`, `VoiceOver` |
| `{OS}` | Sezione "Profilo Utente" | Sistema operativo | `Windows 11`, `macOS Sonoma`, `Ubuntu 22.04` |
| `{UI_FRAMEWORK}` | Sezione "Architettura" e "Accessibilità UI" | Framework UI del progetto | `wxPython`, `tkinter`, `PyQt5`, `Kivy` |
| `{PROJECT_NAME}` | Sezione "Logging" | Nome del progetto | `my_awesome_app`, `ecommerce_platform` |
| `{PYTHON_VERSION}` | Sezione "Pre-Commit Checklist" | Versione Python target | `3.8`, `3.9`, `3.10`, `3.11` |

### Comando rapido per trovare tutti i placeholder

```bash
grep -n "{[A-Z_]*}" .github/copilot-instructions.md
```

---

## 📝 Step 3: Compilazione "Critical Warnings"

La sezione "Critical Warnings" è vuota nel template. Devi popolarla con 3-7 regole critiche specifiche del tuo dominio.

### Template warning da usare

```markdown
N. **Nome Warning**: Descrizione breve del vincolo tecnico o di dominio (max 2 frasi).
   Conseguenza: cosa succede se violato.
   Pattern corretto: codice o procedura da seguire.
```

### Esempi concreti per ispirarti

**Progetto E-commerce:**
```markdown
1. **Cart Immutability After Checkout**: Una volta che `Cart.checkout()` è chiamato, il carrello diventa immutabile. MAI modificare `cart.items` direttamente.
   Conseguenza: corruzione stato ordine, double-charge utente.
   Pattern corretto: crea un nuovo Cart se serve modifiche post-checkout.

2. **Payment Gateway Idempotency**: Ogni chiamata a `PaymentService.charge()` deve includere `idempotency_key` univoco.
   Conseguenza: doppia addebitazione utente.
   Pattern corretto: `payment_service.charge(amount, idempotency_key=order.uuid)`
```

**Progetto CMS:**
```markdown
1. **Published Content Lock**: Contenuti con `status=published` NON devono essere modificati direttamente. Usa workflow draft → review → publish.
   Conseguenza: contenuto pubblico cambia senza audit trail.
   Pattern corretto: `content.create_draft_version()` → modifica → `content.publish_draft()`

2. **Slug Uniqueness**: `Post.slug` deve essere unico per tenant. Controller automatico genera slug da title, mai sovrascrivere manualmente.
   Conseguenza: URL rotti, SEO compromesso.
   Pattern corretto: lascia che `SlugGenerator.from_title()` gestisca collisioni.
```

---

## 🎨 Step 4: Adattamento Named Logger Categories

Il template fornisce 4 categorie logger generiche. Personalizza in base al tuo dominio.

### Logger predefiniti nel template

```python
_business_logger = logging.getLogger('business')  # logica core business
_ui_logger       = logging.getLogger('ui')        # navigazione UI
_data_logger     = logging.getLogger('data')      # persistence/repository
_error_logger    = logging.getLogger('error')     # errori/eccezioni
```

### Esempi di personalizzazione per dominio

**E-commerce:**
```python
_order_logger    = logging.getLogger('order')     # lifecycle ordini
_payment_logger  = logging.getLogger('payment')   # transazioni pagamento
_inventory_logger= logging.getLogger('inventory') # gestione stock
_ui_logger       = logging.getLogger('ui')
_error_logger    = logging.getLogger('error')
```

**Data Pipeline:**
```python
_ingestion_logger = logging.getLogger('ingestion')  # caricamento dati
_transform_logger = logging.getLogger('transform')  # ETL processing
_validation_logger= logging.getLogger('validation') # quality checks
_export_logger    = logging.getLogger('export')     # output generation
_error_logger     = logging.getLogger('error')
```

**Procedura:**
1. Identifica 3-5 aree funzionali chiave del tuo progetto
2. Crea un logger dedicato per ciascuna
3. Aggiorna sezione "Logging (Sistema Categorizzato)" con i tuoi nomi
4. Crea file `src/infrastructure/logging/{NOME}_logger.py` con semantic helpers

---

## 🧪 Step 5: Configurazione Test Markers (Opzionale)

Se il tuo progetto ha marker pytest custom oltre a `unit`/`integration`/`gui`, aggiungili.

### Esempio: progetto con test di performance

```python
@pytest.mark.unit         # Fast, no external deps
@pytest.mark.integration  # Cross-layer, no UI
@pytest.mark.gui          # Requires display
@pytest.mark.performance  # Slow, measure timing  ← CUSTOM
@pytest.mark.e2e          # Full stack, external services  ← CUSTOM
```

Aggiungi nella sezione "Marker Pytest":

```markdown
**Marker custom progetto:**
```python
@pytest.mark.performance  # Test di performance (misurazione timing, memory)
@pytest.mark.e2e          # End-to-end test con servizi esterni
```

**Comandi CI:**
```bash
pytest -m "unit or integration" -v          # Fast tests
pytest -m "not (performance or e2e)" -v     # Skip slow tests
pytest -v                                   # All tests
```
```

---

## 🔍 Step 6: Verifica Pre-Commit Tools

Il template assume questi tool siano disponibili. Verifica e adatta:

| Tool | Comando | Installazione se mancante | Obbligatorio? |
|------|---------|---------------------------|---------------|
| `mypy` | `mypy src/ --strict` | `pip install mypy` | ✅ Sì |
| `pylint` | `pylint src/ --disable=all --enable=cyclic-import` | `pip install pylint` | ✅ Sì |
| `pytest` | `pytest tests/ --cov=src` | `pip install pytest pytest-cov` | ✅ Sì |
| `black` | `black src/ --check` | `pip install black` | ⚠️ Opzionale |
| `isort` | `isort src/ --check` | `pip install isort` | ⚠️ Opzionale |

**Se NON usi `black` o `isort`**: rimuovi le relative voci dalla sezione "Pre-Commit Checklist".

---

## 📚 Step 7: Creazione Template Docs Mancanti

Il template richiede questi file nella cartella `docs/1 - templates/`:

1. `TEMPLATE_DESIGN_DOCUMENT.md`
2. `TEMPLATE_PIANO_IMPLEMENTAZIONE.md`
3. `TEMPLATE_TODO.md`

**Se non li hai già**:

### Minimal TEMPLATE_DESIGN_DOCUMENT.md

```markdown
# Design Document: {FEATURE_NAME}

**Data**: YYYY-MM-DD  
**Stato**: DRAFT | REVIEW | APPROVED | FROZEN  
**Versione target**: vX.Y.Z  
**Autore**: {NOME}

***

## Idea in 3 Righe

**Cosa**: descrizione feature in 1 frase.  
**Perché**: problema che risolve.  
**Come (alto livello)**: approccio concettuale.

***

## Attori e Concetti Chiave

- **Attore 1**: ruolo e interazioni
- **Concetto chiave 1**: definizione

***

## Flussi Concettuali

1. Utente esegue azione X
2. Sistema valida Y
3. Sistema aggiorna Z

***

## Alternative Considerate (se applicabile)

- Alternativa A: pro/contro
- Alternativa B: pro/contro
```

### Minimal TEMPLATE_PIANO_IMPLEMENTAZIONE.md

```markdown
# Piano Implementazione: {DESCRIZIONE}

**Tipo**: Feature | Bugfix | Refactor  
**Priorità**: P0 (critica) | P1 (alta) | P2 (media) | P3 (bassa)  
**Stato**: DRAFT | READY | IN PROGRESS | COMPLETED  
**Branch**: `{tipo}/{slug}`  
**Versione target**: vX.Y.Z

***

## Executive Summary

**Problema/Obiettivo**: cosa viene risolto o implementato.

**File coinvolti**:
- `path/to/file1.py` — CREATE | MODIFY | DELETE
- `path/to/file2.py` — MODIFY

***

## Fasi di Implementazione

1. **Fase 1 - Descrizione**: dettagli task
2. **Fase 2 - Descrizione**: dettagli task

***

## Test Plan

**Unit tests**:
- `test_feature_x_scenario_y`

**Integration tests**:
- `test_integration_layer_a_layer_b`

***

## Criteri di Completamento

- [ ] Tutti i test passano
- [ ] Coverage >= 85%
- [ ] Docs aggiornati
```

### Minimal TEMPLATE_TODO.md

```markdown
# TODO: {TITOLO_BRANCH}

Piano di riferimento: [link al PLAN](3 - coding plans/PLAN_xxx_vX.Y.Z.md)

**Obiettivo**: descrizione breve in 3-5 righe.

**File coinvolti**:
- `path/file1.py`
- `path/file2.py`

## Checklist implementazione

### Fase 1: Nome Fase

- [ ] 1.1. Task specifico (file X, linea Y)
- [ ] 1.2. Task specifico

### Fase 2: Nome Fase

- [ ] 2.1. Task specifico
- [ ] 2.2. Task specifico

***

**Stato**: IN PROGRESS | COMPLETED
```

---

## ✅ Step 8: Verifica Finale

Checklist prima di committare `.github/copilot-instructions.md`:

- [ ] Tutti i placeholder `{VARIABILE}` sostituiti
- [ ] Sezione "Critical Warnings" compilata (almeno 3 warnings)
- [ ] Logger categories personalizzate per dominio
- [ ] Test markers aggiornati (se custom)
- [ ] Tool pre-commit verificati e installati
- [ ] Template docs creati in `docs/1 - templates/`
- [ ] File validato con syntax checker Markdown:
  ```bash
  markdownlint .github/copilot-instructions.md  # opzionale ma consigliato
  ```

---

## 🚀 Step 9: Commit e Test

```bash
# Commit finale
git add .github/copilot-instructions.md docs/1\ -\ templates/
git commit -m "docs: personalizza copilot instructions per {PROJECT_NAME}"
git push origin {branch}

# Test con Copilot
# 1. Apri un file .py nel progetto
# 2. Scrivi un commento: "# Crea una funzione che valida X"
# 3. Verifica che Copilot suggerisca codice coerente con Clean Architecture
```

---

## 📞 Supporto

Per problemi o dubbi su personalizzazione:
1. Verifica esempi concreti in `.github/copilot-instructions.md` del progetto solitario-classico-accessibile (originale)
2. Confronta differenze tra template e versione personalizzata con:
   ```bash
   diff docs/1\ -\ templates/COPILOT_INSTRUCTIONS_TEMPLATE.md .github/copilot-instructions.md
   ```

---

**Fine Guida. Buon lavoro con Copilot e Clean Architecture!**
```

***

## Comandi Git Suggeriti

```bash
# Crea i file nella posizione corretta
mkdir -p "docs/1 - templates"

# (Copia il contenuto dei due file sopra nei rispettivi path)

# Commit
git add "docs/1 - templates/COPILOT_INSTRUCTIONS_TEMPLATE.md"
git add "docs/1 - templates/CUSTOMIZATION_GUIDE.md"
git commit -m "docs: crea template universale copilot instructions con guida personalizzazione"
```