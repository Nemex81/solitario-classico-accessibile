---

# Copilot Custom Instructions - Solitario Classico Accessibile

## 👤 Profilo Utente e Interazione

* **Accessibilità Prima di Tutto**: L'utente è un programmatore non vedente che utilizza NVDA su Windows 11. Ogni proposta deve essere testabile da tastiera e compatibile con screen reader.
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
- **Application** (`src/application/`): Dipende solo da Domain. Contiene use cases, command patterns, game engine.
- **Infrastructure** (`src/infrastructure/`): Implementa interfacce Domain (repositories, external services, UI framework).
- **Presentation** (`src/presentation/`): Dipende da Application. Contiene formatters, dialogs, view logic.

**Vietato:**
- ❌ Import `src.infrastructure.*` dentro `src.domain.*`
- ❌ Import `wx` (wxPython) fuori da `src.infrastructure.ui.*`
- ❌ Import `src.application.game_engine` dentro `src.domain.*`
- ❌ Business logic nei dialog (`src.presentation.dialogs.*`)

**Esempio corretto di refactoring:**
```python
# ❌ ERRATO (Domain dipende da Infrastructure)
# src/domain/services/game_service.py
from src.infrastructure.ui.dialogs import VictoryDialog  # ❌

# ✅ CORRETTO (Domain espone interfaccia, Infrastructure implementa)
# src/domain/services/game_service.py
def end_game(self, is_victory: bool) -> Dict[str, Any]:
    # Ritorna dati, non mostra UI
    return {"is_victory": is_victory, "stats": self.get_stats()}

# src/application/game_engine.py (orchestrazione)
def end_game(self, is_victory: bool) -> None:
    result = self.game_service.end_game(is_victory)
    if self.use_native_dialogs:
        self._show_victory_dialog(result)  # Infrastructure layer
```

---

### Naming Conventions

* **Variabili/Funzioni**: `snake_case` (es. `ensure_guest_profile`, `draw_count`)
* **Classi**: `PascalCase` (es. `GameEngine`, `ProfileService`, `SessionOutcome`)
* **Costanti**: `UPPER_SNAKE_CASE` (es. `MAX_RECENT_SESSIONS`, `GUEST_PROFILE_ID`)
* **Private/Protected**: Prefisso `_` (es. `_handle_crash_recovery`, `_debug_force_victory`)
* **Type Hints**: Sempre obbligatori per metodi pubblici

---

### Type Hints Enforcement

**Vietato:**
- ❌ `pile.count()` → AttributeError (metodo inesistente)
- ❌ Implicit returns senza annotazione
- ❌ `Any` come type hint di default

**Obbligatorio:**
- ✅ `pile.get_card_count() -> int`
- ✅ Ogni public method con return type esplicito
- ✅ Parametri con type hints anche per metodi privati

---

### Logging (Sistema Categorizzato v3.3.0)

**MAI usare `print()` nel codice di produzione.** Usa i named logger dedicati per categoria:

```python
import logging

# Named logger per categoria — scegli quello corretto per contesto
_game_logger  = logging.getLogger('game')   # lifecycle partita, mosse, stato
_ui_logger    = logging.getLogger('ui')     # navigazione UI, dialogs, TTS
_error_logger = logging.getLogger('error')  # errori, warnings, eccezioni
_timer_logger = logging.getLogger('timer')  # lifecycle timer, scadenza, pausa
```

**Routing dei file di output:**
- `game`  → `logs/game_logic.log`
- `ui`    → `logs/ui_events.log`
- `error` → `logs/errors.log`
- `timer` → `logs/timer.log`
- root    → `logs/solitario.log` (library logs: wx, PIL, urllib3)

**Regola propagate=False:** ogni named logger ha `propagate=False` — i messaggi
NON finiscono su `solitario.log`. Questo è intenzionale. Non modificare mai
questo comportamento senza aggiornare `categorized_logger.py`.

**Usare i semantic helpers di `game_logger.py`** (`log_game_start`, `log_move`, `log_error`, `log_keyboard_command`, `log_timer_started`, `log_timer_expired`).

**Vietato:**
- ❌ `print(f"Debug: {variable}")` → usa `logging.getLogger('game').debug()`
- ❌ Log con emoji o box ASCII → screen reader unfriendly
- ❌ `logging.getLogger()` (root logger) nel codice applicativo → usa named loggers
- ❌ Log in Domain layer senza dependency injection

---

### Accessibilità UI (WAI-ARIA + Keyboard)

Ogni componente UI (`wx.Dialog`, `wx.Panel`, `wx.Button`) deve rispettare:

**Checklist obbligatoria:**
- [ ] Ogni controllo ha `SetLabel()` con testo descrittivo
- [ ] Bottoni critici hanno acceleratori (es. `&OK`, `&Annulla`)
- [ ] Dialog hanno `SetTitle()` semantico (letto da NVDA all'apertura)
- [ ] Focus management: `SetFocus()` su primo controllo navigabile
- [ ] ESC chiude dialog (binding `wx.ID_CANCEL`)
- [ ] TAB naviga tutti i controlli in ordine logico
- [ ] No elementi puramente decorativi (spacer con label vuote)

---

## � Critical Warnings (Non Ignorare Mai)

1. **Guest Profile Protection**: Il profilo `profile_000` (Ospite) è **intoccabile**: non eliminare, non rinominare, usato come fallback.

2. **Timer Overtime**: `EndReason.VICTORY` = vittoria entro tempo limite. `EndReason.VICTORY_OVERTIME` = vittoria oltre tempo (PERMISSIVE mode). Non confonderli.

3. **Draw Count Duality**: `GameService.draw_count` = azioni di pescata (per stats). `ScoringService.stock_draw_count` = carte pescate (per penalità). Sono contatori separati.

4. **Pile.count() Bug**: il metodo **NON ESISTE** → usa sempre `pile.get_card_count()`. `pile.count()` genera `AttributeError`.

---

## �📚 Protocollo Allineamento Documentazione (Mandatorio)

### Struttura Cartella `docs/`

```
docs/
├── 1 - templates/          # Template riutilizzabili (PR body, design doc, TODO)
├── 2 - projects/           # Design doc e piani pre-merge per feature attive
│   ├── DESIGN_*.md         # Analisi architetturale di una feature
│   └── PLAN_*.md           # Piano di implementazione/fix con checklist
├── 3 - coding plans/       # Piani di coding dettagliati (step-by-step implementazione)
├── API.md                  # Riferimento API pubblica di tutti i moduli
├── ARCHITECTURE.md         # Architettura del sistema e data flow
├── TESTING.md              # Guida testing e convenzioni
└── TODO.md                 # Cruscotto operativo del branch attivo (stato: IN PROGRESS / DONE)
```

**Regole di posizionamento:**
- Un nuovo design doc → `docs/2 - projects/DESIGN_<feature>.md`
- Un piano di fix/implementazione → `docs/2 - projects/PLAN_<descrizione>_vX.Y.Z.md`
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

**Template da usare:** `docs/1 - templates/TEMPLATE_example_DESIGN_DOCUMENT.md`

**Nome file output:** `docs/2 - projects/DESIGN_<feature-slug>.md`

**Contenuto minimo obbligatorio:**
- Metadata (data, stato, versione target)
- Idea in 3 righe (cosa, perché, problema risolto)
- Attori e concetti chiave
- Flussi concettuali (no decisioni tecniche in questa fase)

**Esempio creazione:**
```
Utente: "Voglio aggiungere un sistema audio con varianti per difficoltà"
→ Crea: docs/2 - projects/DESIGN_audio_system.md
→ Usa: TEMPLATE_example_DESIGN_DOCUMENT.md come base
→ Stato iniziale: DRAFT
```

---

#### Quando creare un PLAN (Piano di Implementazione)

**Trigger (almeno uno dei seguenti):**
- Il task richiede più di 2 commit atomici
- Esiste già un DESIGN doc approvato da implementare
- Si tratta di un bugfix con root cause analisi richiesta
- Il task è un refactoring su più file

**Template da usare:** `docs/1 - templates/TEMPLATE_example_PIANO_IMPLEMENTAZIONE.md`

**Nome file output:** `docs/2 - projects/PLAN_<descrizione-slug>_vX.Y.Z.md`

**Contenuto minimo obbligatorio:**
- Executive Summary (tipo, priorità, stato, branch, versione target)
- Problema/Obiettivo (o Root Cause se bugfix)
- Lista file coinvolti con tipo operazione (CREATE / MODIFY / DELETE)
- Fasi di implementazione in ordine sequenziale
- Test plan (unit + integration)
- Criteri di completamento

**Esempio creazione:**
```
Utente: "Implementa il sistema audio descritto nel DESIGN"
→ Crea: docs/2 - projects/PLAN_audio-system_v3.4.0.md
→ Usa: TEMPLATE_example_PIANO_IMPLEMENTAZIONE.md come base
→ Stato iniziale: DRAFT → poi READY prima del primo commit
```

---

#### Quando creare/aggiornare il TODO

**Trigger creazione (tutti devono essere veri):**
- Esiste un PLAN approvato (stato READY)
- Il branch di lavoro è attivo
- L'implementazione multi-fase è appena iniziata

**Template da usare:** `docs/1 - templates/TEMPLATE_exaple_TODO.md`

**Nome file output:** `docs/TODO.md` (uno solo, sostituisce il precedente ad ogni branch)

**Regole operative:**
- Il TODO è un **cruscotto**, non un documento tecnico: sommario operativo consultabile in 30 secondi
- Il link al PLAN completo (fonte di verità) deve essere in cima al TODO
- Ogni checkbox spuntata corrisponde a un commit già eseguito
- Va aggiornato **dopo ogni commit**, non in batch a fine lavoro
- Al merge su `main` il TODO viene archiviato o eliminato

**Contenuto minimo obbligatorio:**
- Riferimento al PLAN completo (link relativo)
- Istruzioni per Copilot Agent (workflow incrementale)
- Obiettivo in 3-5 righe
- Lista file coinvolti
- Checklist implementazione per layer
- Criteri di completamento

**Esempio aggiornamento post-commit:**
```
Dopo commit "feat(domain): aggiunto AudioEvent model":
→ Apri docs/TODO.md
→ Spunta: [x] Modifica modello / entità (Domain layer)
→ Salva e includi nel commit successivo (o commit separato "docs: aggiorna TODO fase 1")
```

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

**Vincoli di sequenza:**
- Non creare un PLAN senza aver prima chiarito i requisiti (DESIGN o discussione esplicita)
- Non iniziare commit di codice senza un TODO aggiornato se il task ha più di 2 fasi
- Non modificare uno DESIGN doc a FROZEN senza aggiornare il PLAN corrispondente

#### Workflow Completo di Creazione (Step-by-Step)

Quando l'utente introduce un nuovo task significativo:

1. **Valuta la complessità**: meno di 2 file e 1 commit → nessun file di progetto necessario
2. **Crea DESIGN** (se architetturale): copia `TEMPLATE_example_DESIGN_DOCUMENT.md`, compila sezioni obbligatorie, salva in `docs/2 - projects/`
3. **Crea PLAN**: copia `TEMPLATE_example_PIANO_IMPLEMENTAZIONE.md`, collega al DESIGN se esiste, definisci fasi, salva in `docs/2 - projects/`
4. **Crea TODO**: copia `TEMPLATE_exaple_TODO.md`, metti link al PLAN in cima, trascrivi le fasi come checklist, salva come `docs/TODO.md`
5. **Inizia implementazione**: segui il workflow incrementale descritto nel TODO
6. **Aggiorna TODO** dopo ogni commit (spunta checkbox)
7. **A merge completato**: aggiorna CHANGELOG, archivia o elimina `docs/TODO.md`

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
    → Crea docs/TODO.md da TEMPLATE_exaple_TODO.md
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
    4. COMMIT  → Commit atomico con messaggio convenzionale
    5. SPUNTA  → Aggiorna docs/TODO.md: [x] per la fase appena completata
    6. COMUNICA → Notifica l'utente: "Fase N completata: [descrizione]. Proseguo con Fase N+1?"
    7. ATTENDI  → Ricevi conferma prima di passare alla fase successiva
                  (oppure procedi automaticamente se l'utente ha detto "procedi senza chiedere")
```

**Regola di atomicità**: ogni commit copre esattamente una fase del TODO. Non accorpare fasi, non anticipare fasi future.

**Regola di consultazione**: tra un commit e l'altro, rileggi sempre il TODO aggiornato e il PLAN prima di iniziare la fase successiva. Non procedere a memoria.

#### Esempio operativo

```
Utente: "Inizia l'implementazione del sistema audio"

→ Step 1: Verifico docs/TODO.md...
  ASSENTE → Lo creo da TEMPLATE_exaple_TODO.md con link a PLAN_audio_system_v3.4.0.md

→ Step 3: Leggo TODO (FASE 1: dipendenze), PLAN (dettagli requirements.txt + assets)

→ Step 4, ciclo FASE 1:
  Codifica: aggiungo pygame a requirements.txt, creo struttura assets/sounds/
  Commit: chore(deps): re-aggiunge pygame per sistema audio + crea struttura assets
  Spunta: [x] FASE 1 in docs/TODO.md
  Comunicazione: "FASE 1 completata. Procedo con FASE 2 (AudioEvent dataclass)?"
```

---

### Trigger Events (quando aggiornare docs)

Dopo **ogni modifica al codice** (`.py`), esegui questo audit:

**1. API.md** — Aggiorna se modifichi signature metodi pubblici, classi esportate da `__init__.py`, enum/costanti pubbliche, comportamento documentato.

---

**2. ARCHITECTURE.md** — Aggiorna se modifichi struttura cartelle, data flow tra layer, design patterns, dipendenze esterne (`requirements.txt`).

---

**3. CHANGELOG.md** — Aggiorna **sempre** dopo merge su `main`: nuove feature → `Added`, bug fix → `Fixed`, breaking changes → `Changed` + ⚠️.

---

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

### Integrità Link e Cross-References

Prima di chiudere un task, verifica:

- [ ] Ogni file Python pubblico ha entry in `docs/API.md`
- [ ] Ogni sezione `docs/API.md` ha link a `docs/ARCHITECTURE.md` per contesto
- [ ] `docs/TODO.md` riflette task aperti (nessun TODO completato dimenticato)
- [ ] `CHANGELOG.md` ha entry per ogni modifica in `main`
- [ ] Nessun link rotto (es. `[ProfileService](docs/API.md#profileservice)` → verifica anchor esiste)

**Comando verifica** (chiedi all'utente di eseguire):
```bash
# Verifica link rotti in Markdown
grep -r '\[.*\](.*)' docs/ | grep -v http | while read line; do
  # Parse e verifica esistenza file/anchor
done
```

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
# tests/domain/services/test_profile_service.py
import pytest
from src.domain.services.profile_service import ProfileService

class TestProfileService:
    @pytest.fixture
    def service(self, tmp_path):
        """Setup con storage temporaneo."""
        return ProfileService(storage_path=tmp_path)
    
    def test_ensure_guest_profile_creates_if_missing(self, service):
        """Verifica creazione guest profile se non esiste."""
        # Arrange
        assert not service.storage.exists("profile_000")
        
        # Act
        result = service.ensure_guest_profile()
        
        # Assert
        assert result is True  # ← Verifica return type bool
        assert service.storage.exists("profile_000")
        profile = service.storage.load("profile_000")
        assert profile.profile_name == "Ospite"
```

**Naming convention test:**
- `test_<method>_<scenario>_<expected_behavior>`
- Esempio: `test_record_session_with_invalid_profile_id_returns_false`

---

### Marker Pytest e CI Strategy

**Marker obbligatori — applicali sempre:**

```python
@pytest.mark.unit   # Test senza dipendenze esterne (no wx, no filesystem reale)
@pytest.mark.gui    # Test che richiedono wx e display (Xvfb o Windows)
```

**Regole di assegnazione:**
- Test che usano solo `tmp_path`, mock, o oggetti puri → `@pytest.mark.unit`
- Test che istanziano `wx.App`, dialog, o frame → `@pytest.mark.gui`
- Test di integrazione tra layer senza UI → `@pytest.mark.unit`

**Comandi standard:**
```bash
pytest -m "not gui" -v        # CI-safe (headless): obbligatorio pre-merge
pytest -v                     # Test completi (richiede display o Xvfb)
```

**Isolamento test logging:** il modulo `logging` di Python è un singleton di
processo. Qualsiasi test che chiama `setup_logging()` o `setup_categorized_logging()`
**deve** avere una fixture `reset_logging` con cleanup pre+post yield. Vedi
`tests/infrastructure/test_categorized_logger.py` come riferimento canonico.

---

## 🔍 Pre-Commit Checklist (Auto-Eseguita)

Prima di ogni commit, verifica silentemente:

1. **Syntax**: `python -m py_compile src/**/*.py` (0 errori)
2. **Type Hints**: `mypy src/ --strict --python-version 3.8` (0 errori, 100% copertura type hints)
3. **Imports**: `pylint src/ --disable=all --enable=cyclic-import` (nessun import circolare)
4. **Logging**: `grep -r "print(" src/ --include="*.py" --exclude="__main__.py"` (must return 0 occorrenze)
5. **Docs Sync**: Changelog modificato nelle ultime 48h? (verifica manuale)
6. **Tests**: `pytest tests/ --cov=src --cov-report=term --cov-fail-under=85` (100% pass, coverage >= 85%)

**Output esempio comando Git:**
```bash
# Ottenere SHA prima di update file
git ls-tree HEAD src/domain/services/profile_service.py
```

**Se uno fallisce:**
```
⚠️ Pre-commit check FAILED:
- mypy: Found 3 type errors in src/domain/services/profile_service.py
- docs: CHANGELOG.md non aggiornato (ultima modifica: 2 giorni fa)

Vuoi che fixo automaticamente o preferisci revisione manuale?
```

---

## 📝 Convenzioni Git Commit

### Atomic Commits Policy

**Un commit = una unità logica di cambiamento.** Regole operative:

- ✅ Un commit per file modificato se le modifiche hanno motivazioni diverse
- ✅ Un commit per task logico (es. "fix firma", "aggiunta test", "fix docstring")
- ❌ No mega-commit che mescolano fix di codice + aggiornamenti docs + test
- ❌ No commit "WIP" o "fix fix fix" su branch destinati alla PR

**Ordine di commit consigliato** quando si lavora su un task con dipendenze:
1. Pre-requisiti (es. aggiungere un parametro a una firma)
2. Implementazione principale
3. Test
4. Aggiornamento documentazione (API.md, CHANGELOG.md)
5. Aggiornamento cruscotto operativo (TODO.md)

---

**Format obbligatorio:**
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
fix(domain): corretto return type ProfileService.ensure_guest_profile

- Cambiato da `-> None` a `-> bool`
- Aggiornato docs/API.md sezione ProfileService
- Aggiunto test per error handling (coverage +2%)

Refs: #42, docs/3 - coding plans/PLAN-docs-allineamento-v3.2.2.md
```

---

## 🌿 Branch Workflow e Release Process

### Naming branch

| Tipo | Pattern | Esempio |
|---|---|---|
| Feature | `feature/<slug>` | `feature/timer-overtime` |
| Fix | `fix/<slug>` | `fix/pile-count-crash` |
| Hotfix | `hotfix/<slug>` | `hotfix/guest-profile-null` |
| Refactor | `refactor/<slug>` | `refactor/clean-arch-domain` |
| Docs | `docs/<slug>` | `docs/api-update-v3.3` |

### Quando creare un branch vs committare su `main`

- **Branch separato**: qualsiasi feature, fix non banale, refactor, o lavoro
  che richiede più di 1 commit.
- **Commit diretto su `main`**: solo hotfix monocommit urgenti o aggiornamenti
  di documentazione pura (nessun `.py` modificato).

### Release process (step obbligatori)

1. Tutti i fix e i task del branch completati e verificati
2. PR aperta verso `main` con body che linka design doc e piano (se esistono)
3. Checklist PR spuntata (vedi template `docs/1 - templates/`)
4. Merge con **merge commit** (`--no-ff`) — preserva storia del branch
5. Subito dopo il merge, creare il tag di versione:
   ```bash
   git checkout main && git pull origin main
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
- `BUILD` (W) *(facoltativo)*: bugfix minori o aggiornamenti di documentazione pura (es. `v3.3.0.1`)

---

## 🎯 Promemoria Finale

**Quando l'utente chiede modifiche:**
0. ✅ **Verifica TODO Gate** (se task multi-file/multi-commit): controlla `docs/TODO.md`, crealo se assente, riprendi dall'ultima fase completata se in corso
1. ✅ Applica modifiche con type hints completi
2. ✅ Aggiungi logging semantico (no print)
3. ✅ Verifica accessibilità (ARIA, keyboard, screen reader)
4. ✅ Audit documentazione (proponi sync)
5. ✅ Esegui test coverage check
6. ✅ Fornisci riepilogo testuale strutturato

**Frase magica per audit completo:**
*"Codice, documentazione e test sono sincronizzati al 100% secondo gli standard v2.3+"*

Quando l'utente la richiede, esegui tutti i 6 check pre-commit + verifica manuale cross-references docs prima di confermare sync.

---
