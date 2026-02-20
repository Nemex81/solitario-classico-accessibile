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

**Esempio di firma corretta:**
```python
def record_session(self, session: SessionOutcome) -> bool:
    """
    Registra sessione e aggiorna statistiche.
    
    Args:
        session: Oggetto SessionOutcome validato
        
    Returns:
        True se salvato con successo, False altrimenti
    """
```

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

**Esempio fix completo:**
```python
# ❌ ERRATO
def check_pile(pile):
    if pile.count() > 0:  # AttributeError!
        return True

# ✅ CORRETTO  
def check_pile(pile: Pile) -> bool:
    if pile.get_card_count() > 0:
        return True
    return False
```

---

### Logging (Sistema Centralizzato)

**MAI usare `print()` nel codice di produzione.** Usa esclusivamente `game_logger`:

```python
from src.infrastructure.logging.game_logger import game_logger

# Livelli disponibili
game_logger.info("operation_name", "Detailed message", extra_context={"key": "value"})
game_logger.warning("edge_case", "Warning message")
game_logger.error("failure_type", "Error details", exc_info=True)
game_logger.debug("trace", "Debug info")  # Solo se verbose >= 2
```

**Semantic Helpers (usa questi):**
```python
# State transitions
game_logger.log_state_change("game_started", old_state, new_state)

# Validations
game_logger.log_validation_error("invalid_move", reason="Card not movable")

# Performance
game_logger.log_performance("deal_cards", duration_ms=15.3)
```

**Vietato:**
- ❌ `print(f"Debug: {variable}")`  # Usa `game_logger.debug()`
- ❌ Log decorativi con emoji/box ASCII  # Screen reader unfriendly
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

**Esempio corretto:**
```python
class VictoryDialog(wx.Dialog):
    def __init__(self, parent, outcome, profile):
        super().__init__(parent, title="Partita Vinta!")  # NVDA legge "Partita Vinta!"
        
        # TTS announcement (se screen_reader disponibile)
        if self.screen_reader:
            self.screen_reader.speak("Hai vinto! Partita completata.")
        
        # Text control con summary (navigabile)
        self.summary_text = wx.TextCtrl(
            self, 
            value=formatter.format_session_outcome(outcome),
            style=wx.TE_MULTILINE | wx.TE_READONLY
        )
        self.summary_text.SetFocus()  # Focus su contenuto principale
        
        # Bottoni con acceleratori
        btn_rematch = wx.Button(self, wx.ID_YES, "&Rivincita")  # ALT+R
        btn_menu = wx.Button(self, wx.ID_NO, "&Menu")            # ALT+M
        
        # ESC = torna al menu
        self.Bind(wx.EVT_BUTTON, self.on_close, id=wx.ID_CANCEL)
```

---

## 📚 Protocollo Allineamento Documentazione (Mandatorio)

### Trigger Events (quando aggiornare docs)

Dopo **ogni modifica al codice** (`.py`), esegui questo audit:

**1. API.md**  
Aggiorna se modifichi:
- Signature metodi pubblici (parametri, return type, nome)
- Classi esportate da `__init__.py`
- Enum/costanti pubbliche
- Comportamento documentato (side effects, validazioni)

**Esempio:**
```python
# Prima
def create_profile(self, name: str, set_as_default: bool = False) -> Optional[UserProfile]:

# Dopo
def create_profile(self, name: str, is_guest: bool = False) -> Optional[UserProfile]:
```
→ **Aggiorna `docs/API.md`**: sezione `## ProfileService.create_profile` — parametro `set_as_default` → `is_guest`, aggiorna esempio d'uso

---

**2. ARCHITECTURE.md**  
Aggiorna se modifichi:
- Struttura cartelle (`src/`, `docs/`, `tests/`)
- Data flow tra layer (nuovi adapter, repositories)
- Design patterns adottati (nuovi command, observers)
- Dipendenze esterne (nuove librerie in `requirements.txt`)

**Esempio:**
- Aggiungi `src/domain/events/` per event sourcing
→ **Aggiorna `docs/ARCHITECTURE.md`**: sezione "Domain Layer" + diagramma struttura cartelle

---

**3. CHANGELOG.md**  
Aggiorna **sempre** dopo merge su `main`:
- Nuove feature → sezione `## [Unreleased] - Added`
- Bug fix → `## [Unreleased] - Fixed`
- Breaking changes → `## [Unreleased] - Changed` + ⚠️ warning

**Formato:**
```markdown
## [Unreleased]

### Added
- ProfileService: Aggiunto metodo `get_leaderboard()` per top 10 giocatori (#PR)

### Fixed
- API.md: Corretto return type `ensure_guest_profile()` (None → bool) (#Issue)

### Changed
- ⚠️ BREAKING: `create_profile()` parametro `set_as_default` rinominato `is_guest`
```

---

**4. README.md**  
Aggiorna se modifichi:
- Entry point (`acs.py` → `acs_wx.py`)
- Comandi CLI (nuove opzioni `--verbose`, `--profile`)
- Requisiti sistema (Python 3.9 → 3.11, nuove dipendenze)
- Setup environment (nuovi passi installazione)

---

### Workflow di Sync (Step-by-Step)

Quando l'utente dice *"applica le modifiche"*:

1. **Esegui modifiche codice** (`.py` files)
2. **Audit immediato**:
   ```
   Modifiche a src/domain/services/profile_service.py (line 260):
   - Cambiato return type: None → bool
   
   📋 Impatto documentazione:
   - docs/API.md: ✅ Richiede aggiornamento (sezione ProfileService.ensure_guest_profile)
   - docs/ARCHITECTURE.md: ⬜ Nessun impatto
   - CHANGELOG.md: ✅ Aggiungi entry [Unreleased] - Fixed
   ```
3. **Proposta aggiornamento**:
   ```
   Vuoi che aggiorni:
   1. docs/API.md (fix return type + esempio)
   2. CHANGELOG.md (entry Fixed)
   
   Rispondi "sì" per procedere, "solo 1" per docs/API.md, "no" per saltare.
   ```
4. **Applica aggiornamenti docs** se confermato
5. **Verifica finale**:
   ```
   ✅ Codice e documentazione sincronizzati:
   - src/domain/services/profile_service.py (modified)
   - docs/API.md (updated, sezione ProfileService.ensure_guest_profile)
   - CHANGELOG.md (updated, [Unreleased] section)
   ```

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

# Output:
# 100644 blob 47f9717e9064973963357a3cbf64eac57b4a8fe3	src/domain/services/profile_service.py
#              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#              Questo è il SHA da usare in create_or_update_file
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

## 🚨 Critical Warnings (Non Ignorare Mai)

1. **Guest Profile Protection**: Il profilo `profile_000` (Ospite) è **intoccabile**:
   - Non eliminare
   - Non rinominare
   - Usato come fallback
   
2. **Timer Overtime**: Distingui sempre:
   - `EndReason.VICTORY` = vittoria entro tempo limite
   - `EndReason.VICTORY_OVERTIME` = vittoria oltre tempo (PERMISSIVE mode)
   
3. **Draw Count Duality**: Esistono **due contatori separati**:
   - `GameService.draw_count` = azioni di pescata (per stats)
   - `ScoringService.stock_draw_count` = carte pescate (per penalità)
   
4. **Pile.count() Bug**: Il metodo **NON ESISTE**. Usa sempre:
   - ✅ `pile.get_card_count()`
   - ❌ `pile.count()` → AttributeError

---

## 🎯 TTS Feedback Tracking (Experimental - v2.4+)

```python
def tts_spoken(message: str, interrupt: bool) -> None:
    """
    Log TTS vocalization (DEBUG level).
    
    Args:
        message: Text vocalized
        interrupt: Whether previous speech interrupted
    
    Note:
        **Experimental feature** - not yet integrated in all dialogs.
        Call this after `screen_reader.speak()` for analytics and UX testing.
        Molto verboso (ogni azione genera TTS) - solo per accessibility audits.
    
    Example:
        >>> tts_spoken("7 di cuori su 8 di picche", True)
        2026-02-14 15:15:00 - DEBUG - ui - TTS: "7 di cuori su 8 di picche" (interrupt=True)
    """
```

---

## 🎯 Promemoria Finale

**Quando l'utente chiede modifiche:**
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