# Workflow Ciclo Sviluppo Completo

## Introduzione

Questo documento descrive il **ciclo di sviluppo end-to-end** per il progetto "Solitario Classico Accessibile", orchestrato da **7 agenti specializzati** descritti in [.github/AGENTS.md](../.github/AGENTS.md).

Ogni fase del workflow ha:
- **Input richiesto**: cosa serve per iniziare
- **Responsabilità agente**: cosa fa l'agente
- **Output deliverable**: cosa produce
- **Gate di completamento**: criteri di approvazione
- **Transizione**: come passare alla fase successiva

---

## 🎯 Fasi del Workflow

### Fase 1️⃣: Analisi (Agent-Analyze)

**Quando inizia**: User richiede una feature, suggerisce refactor, o chiede investigazione.

**Input**:
- User description: "Voglio feature X" / "Analizza come funziona Y"
- (Opzionale) Specifiche tecniche aggiuntive

**Responsabilità Agent-Analyze**:
1. **Discovery read-only**:
   - Leggi ARCHITECTURE.md per contesto architetturale
   - Esplora `src/` directory per codice rilevante
   - Identifica asset, config, dipendenze
   - Estrai precedenti design decisions (da docs/2 - projects/)

2. **Findings Report**:
   - Riassunto: percorsi file, classi, dipendenze
   - Pattern architetturali già in uso
   - Possibili insidie (circular imports, dead code, etc.)
   - Domande di chiarimento per user

3. **Suggerimento successivo agente**:
   - Se richiesta è "spiega/studia" → fine qui
   - Se richiesta è "voglio aggiungere/cambiare" → suggerisci Agent-Design

**Output**:
```
Comunicazione strutturata (no file creato):
- Findings: lista bullet di scoperte
- Code Snippets: 2-3 rilevanti
- Architectural Context: quali layer interessati
- Follow-up Questions: se ambiguitā
- Next Agent Suggestion: Agent-Design or Agent-Plan?

Esempio:
"Analisi feature 'timer overtime':
 - Found: src/application/game_engine.py (GameEngine class)
 - Found: src/domain/models/game_end.py (EndReason enum)
 - Pattern: Game state management tramite GameService
 - Dipendenze: scoring_service, session_tracker
 - Questione: back-compat con partite vecchie senza overtime flag?
 - Suggerito: Agent-Design per decisioni architetturali"
```

**Gate di Completamento**:
- ✅ Analisi copre tutte le sezioni architetturali interessate
- ✅ Seguire-up questions risolte
- ✅ Agente suggerisce step successivo

**Transizione a Fase 2**:
```
User risponde: "Ok, disegna il sistema"
  ↓
Agent-Design prende il controllo (Phase 2)
```

---

### Fase 2️⃣: Design (Agent-Design)

**Quando inizia**: Dopo analisi conclusa (facoltativo: user può saltare direttamente da richiesta se simple feature).

**Input**:
- Findings da Agent-Analyze (o user description direttamente)
- Feature scope e requirement
- DI constraints (accessibility, performance, backward compat)

**Responsabilità Agent-Design**:
1. **Architectural Decisions**:
   - Identificare layer interessati (Domain/Application/Infrastructure)
   - Scegliere patterns (Strategy, Observer, Factory, etc.)
   - Design data flow (input → processing → output)
   - Identificare nuove entities/value objects (Domain)

2. **Crea DESIGN_<feature>.md** in `docs/2 - projects/`:
   ```markdown
   # DESIGN_<feature>
   
   **Status**: DRAFT (→ REVIEWED dopo user approval)
   **Data**: YYYY-MM-DD
   **Versione Target**: vX.Y.Z
   **Autore**: Agent-Design
   
   ## Idea Riassunto (3 righe)
   [Descrizione concisa di cosa, perché, problema risolto]
   
   ## Attori e Concetti Chiave
   - Entity A: ruolo
   - Service B: responsabilità
   - Value Object C: semantica
   
   ## Flussi Concettuali (NO codice, solo logica)
   [Diagramma testuale di come la feature fluisce]
   
   ## Decisioni Architetturali
   - Layer interessati: Domain, Application
   - Dependency direction: verso Domain (no inverse)
   - Pattern usato/nuovo: es Strategy Pattern
   - Breaking Changes?: no / sì → details
   
   ## Considerazioni (Accessibility, Backward Compat, etc.)
   - Screen reader impact: ...
   - Performance impact: ...
   - Data migration needed?: ...
   ```

3. **Output Artifacts**:
   - DESIGN_*.md file (DRAFT status iniziale)
   - ASCII/Mermaid diagram (opzionale, solo se chiarisce logica)

**Gate di Completamento**:
- ✅ DESIGN_*.md creato e completo (no section vuota)
- ✅ Status escalato a **REVIEWED** (user ha letto e approvato)
- ✅ REVIEWED status verbalmente confermato dall'agente

**Transizione a Fase 3**:
```
User conferma: "DESIGN ok, procediamo"
  ↓
Agent-Plan prende il controllo (Phase 3)
```

---

### Fase 3️⃣: Planning (Agent-Plan)

**Quando inizia**: After DESIGN_*.md REVIEWED status.

**Input**:
- DESIGN_*.md **REVIEWED** (status obbligatorio)
- Versione target (es v3.6.0)
- Priorità/dipendenze (criticalpath first)

**Responsabilità Agent-Plan**:
1. **Decomposizione in Fasi**:
   - Breaking down DESIGN in implementable steps
   - Sequenza rispettando dipendenze (domain → app → infrastructure)
   - Stima sforzo (nessuna deadline, solo sequenza logica)

2. **Crea PLAN_<feature>_vX.Y.Z.md** in `docs/3 - coding plans/`:
   ```markdown
   # PLAN_<feature>_vX.Y.Z
   
   **Status**: DRAFT (→ READY dopo user review)
   **Data**: YYYY-MM-DD
   **Versione**: X.Y.Z
   **Branch**: feature/<slug>
   **Autore**: Agent-Plan
   
   ## Executive Summary
   - Tipo: nuova feature / bugfix / refactor
   - Priorità: critica / alta / media
   - Branch da: main
   - Commit attesi: N
   
   ## Problema / Obiettivo
   [Link a DESIGN_*.md + obiettivo misurabile]
   
   ## File Coinvolti (con operazioni)
   ```
   src/domain/models/
     - new_entity.py (CREATE)
     - existing_service.py (MODIFY)
   src/application/
     - use_case.py (CREATE)
   src/infrastructure/
     - adapter.py (MODIFY)
   tests/
     - test_new_entity.py (CREATE)
   docs/
     - API.md (MODIFY - add entries)
     - ARCHITECTURE.md (MODIFY - update flow)
   ```
   
   ## Fasi di Implementazione (Sequenza Logica)
   
   ### Fase 1: Domain Layer
   Crea NewEntity + NewService
   - File: src/domain/models/new_entity.py, src/domain/services/new_service.py
   - Type hints: 100%, logging: domain-specific
   - Test: unit test basic lifecycle
   
   ### Fase 2: Application Layer
   Crea UseCase orchestrator
   - File: src/application/use_case.py
   - Dipende da: Fase 1 domain
   - Test: integration test use case
   
   ### Fase 3: Infrastructure Layer
   Implementa adapter
   - File: src/infrastructure/adapter.py
   - Dipende da: Fase 2 app
   - Test: integration test con I/O
   
   ### Fase 4: Documentation & Tests
   Aggiorna API.md, coverage target 85%+
   - File: docs/API.md, tests/domain/test_new_entity.py
   - Dipende da: Fase 1-3 code complete
   
   ## Test Plan
   - Unit: Domain entities (70% test)
   - Integration: UseCase orchestration (15%)
   - E2E: (15% coverage target)
   - Coverage target: 85% minimum
   
   ## Criteri di Completamento
   - [ ] Tutti i commit atomici e convenzionali
   - [ ] Type hints 100%
   - [ ] Logging categorizzato usato
   - [ ] Test coverage >= 85%
   - [ ] No broken imports, no dead code
   - [ ] Docs sincronizzate (API.md, ARCHITECTURE.md)
   ```

3. **Crea docs/TODO.md** (cruscotto operativo):
   ```markdown
   # TODO: Implementazione PLAN_<feature>_vX.Y.Z
   
   **Link Progetto**: [PLAN_<feature>_vX.Y.Z](3%20-%20coding%20plans/PLAN_*.md)
   **Status**: IN PROGRESS
   **Versione Target**: X.Y.Z
   **Branch**: feature/<slug>
   
   ## Istruzioni per Copilot
   Esegui `/start` per riprendere dall'ultima fase completata.
   Ogni fase = 1 commit atomico.
   Non anticipare fasi future, non accorpare fasi.
   
   ## Obiettivo in 3-5 Righe
   [Copia from PLAN executive summary]
   
   ## File Coinvolti
   [Copia from PLAN file list]
   
   ## Checklist Implementazione
   - [ ] **FASE 1: Domain Layer**
     - [ ] Create: src/domain/models/new_entity.py
     - [ ] Commit message: feat(domain): aggiunto NewEntity + NewService
     - [ ] Type hints: 100%
     - [ ] Logging: categorizzato
   
   - [ ] **FASE 2: Application Layer**
     - [ ] Create: src/application/use_case.py
     - [ ] Commit message: feat(application): aggiunto UseCase orchestrator
     - [ ] Type hints: 100%
   
   - [ ] **FASE 3: Infrastructure Layer**
     - [ ] Modify: src/infrastructure/adapter.py
     - [ ] Commit message: feat(infrastructure): implementato adapter
   
   - [ ] **FASE 4: Tests & Docs**
     - [ ] Create: tests/domain/test_new_entity.py
     - [ ] Modify: docs/API.md
     - [ ] Commit message: docs(api): aggiunto entry NewEntity + NewService
     - [ ] Coverage: >= 85%
   
   ## Test Execution
   ```bash
   pytest -m "not gui" --cov=src --cov-fail-under=85
   ```
   ```

**Gate di Completamento**:
- ✅ PLAN_*.md completo (tutte le fasi dettagliate)
- ✅ TODO.md creato e pronto
- ✅ Status PLAN escalato a **READY**
- ✅ User ha confermato priorità + versione

**Transizione a Fase 4**:
```
User esegue: /start
  ↓
Agent-Code prende il controllo (Phase 4)
Agent-Code legge TODO.md e PLAN_*.md
Agent-Code implementa Fase 1
```

---

### Fase 4️⃣: Codifica (Agent-Code)

**Quando inizia**: User esegue `/start`, oppure direttamente dopo PLAN READY.

**Input**:
- docs/TODO.md READY
- PLAN_*.md dettagliato
- DESIGN_*.md riferimento architetturale

**Responsabilità Agent-Code** (per OGNI fase):
```
LOOP per ogni ☐ in docs/TODO.md:
  1. LEGGI docs/TODO.md → individua prima fase ☐
  2. LEGGI PLAN_*.md sezione fase per dettagli tecnici
  3. LEGGI DESIGN_*.md per contesto architetturale
  
  4. CODIFICA:
     - Implementa solo quella fase (no anticipare)
     - Type hints: 100% (mypy strict)
     - Logging: categorizzato (domain/game/ui/error/timer logger)
     - Clean Architecture: dipendenze corrette tra layer
  
  5. PRE-COMMIT CHECKLIST (automatizzato):
     ✓ python -m py_compile (syntax K)
     ✓ mypy src/ --strict (type hints 100%)
     ✓ pylint cyclic-import check (no circular)
     ✓ grep "print(" = 0 occurrenze in src/ (no prints)
     ✓ pytest -m "not gui" --cov=src --cov-fail-under=85 (unit test K)
  
  6. COMMIT (atomico, convenzionale):
     Message: <type>(<scope>): <subject>
     Body: [opzionale] descrizione cambio
     Types: feat, fix, docs, refactor, test, chore
  
  7. SPUNTA docs/TODO.md:
     Change: [ ] FASE N → [x] FASE N
     Save & commit (o include in pre-commit)
  
  8. COMUNICAZIONE:
     "FASE N completata (Commit <SHA7>). 
      Cosa ho fatto: <list 2-3 cose>.
      Procedo FASE N+1?"
  
  9. ATTENDI user confirm
     User può dire: "yes, procedi" / "stop, review" / "modifica"
```

**Output per Fase**:
- File Python con type hints 100%
- Logging categorizzato (domain/game/ui/error/timer)
- **Exacty 1 commit atomico** (non split, non accorpare)
- docs/TODO.md aggiornato (checkbox spuntato)

**Gate di Completamento** (per intero task multi-fase):
- ✅ Tutti i file creati/modificati con type hints 100%
- ✅ Tutti i commit atomici (no "fixup" commits)
- ✅ Coverage >= 85% (pre-commit threshold)
- ✅ docs/TODO.md completamente spuntato
- ✅ Nessun import circolare, no dead code, no print statement

**Transizione a Fase 5**:
```
docs/TODO.md completamente spuntato
  ↓
Agent-Code comunica: "Codifica completa. Procediamo validazione?"
  ↓
Agent-Validate prende il controllo (Phase 5)
```

---

### Fase 5️⃣: Validazione (Agent-Validate)

**Quando inizia**: After all code phases complete (TODO fully checked).

**Input**:
- Committed code da Agent-Code
- Test coverage goal: >= 85%

**Responsabilità Agent-Validate**:
1. **Coverage Report**:
   ```bash
   pytest -m "not gui" --cov=src --cov-report=html --cov-fail-under=85
   ```
   - Genera htmlcov/index.html
   - Identifica file sotto threshold

2. **Gap Analysis**:
   - Quali funzioni/classi non coperte?
   - Quali edge case mancano?

3. **Test Skeleton Auto-Generation**:
   - Propone test stubs per gap coverage
   - User approva/modifica test
   - Incorpora nel codebase

4. **Regression Testing**:
   - Full test suite run: `pytest -v` (all markers, including GUI)
   - Verifica backward compatibility

**Output**:
```
Coverage Report:
- HTMLcov generated: htmlcov/index.html
- Gap summary:
  * src/domain/models/new_entity.py: 75% (5 lines uncovered)
  * src/infrastructure/adapter.py: 80% (3 lines uncovered)
  
Test Skeleton Proposal:
- test_new_entity_lifecycle()
- test_adapter_error_handling()
- [Propone code skeleton]

User Approval:
- Accept skeleton + add details → 92% coverage achieved ✓
- Reject + modify → manual test writing
```

**Gate di Completamento**:
- ✅ Coverage >= 85% (pre-commit) or 90%+ (release)
- ✅ All tests pass (no failures)
- ✅ Test markers correct (@pytest.mark.unit / @pytest.mark.gui)
- ✅ HTML report reviewed

**Transizione a Fase 6**:
```
Coverage validated (85%+ or 90%+)
  ↓
Agent-Validate comunicates: "Tests validated. Sincronizziamo documentazione?"
  ↓
Agent-Docs prende il controllo (Phase 6)
```

---

### Fase 6️⃣: Documentazione (Agent-Docs)

**Quando inizia**: After validation passed.

**Input**:
- Commits da Agent-Code
- Coverage report da Agent-Validate
- PLAN_*.md reference

**Responsabilità Agent-Docs**:
1. **API.md Sync**:
   - Estrae classi/funzioni pubbliche dagli import di `__init__.py`
   - Aggiunge entry per ogni new public API
   - Mantiene descrizioni manualmente scritte (no full code generation)

2. **ARCHITECTURE.md Update**:
   - Se agente ha suggerito refactor strutturale: aggiorna sezioni rilevanti
   - Valida che diagrammi/flussi siano coerenti

3. **CHANGELOG.md Semi-Auto**:
   - Analizza commit messages (convenzionali):
     - `feat:` → sezione FEATURES
     - `fix:` → sezione BUGFIXES
     - `refactor:`, `docs:`, `test:` → sezioni appropriate
   - Propone versione (SemVer):
     - feat → MINOR
     - fix → PATCH
     - breaking change → MAJOR
   - Crea sezione draft [UNRELEASED] → [X.Y.Z — YYYY-MM-DD]

4. **Link Validation**:
   - Grep per link rotti (404)
   - Valida cross-references (DESIGN_* → PLAN_*, PLAN_* → API.md, etc.)

**Output**:
```
Sync Report:
✓ API.md: 3 new entries added (NewEntity, NewService, UseCase)
✓ ARCHITECTURE.md: "Application Layer" sezione updated
✓ CHANGELOG.md: [UNRELEASED] → [3.6.0 — 2026-03-17] creata
✓ Cross-links: 0 broken

Pronto per release?
```

**Gate di Completamento**:
- ✅ API.md ha entry per TUTTE le nuove public APIs
- ✅ ARCHITECTURE.md riflette struttura codebase
- ✅ CHANGELOG.md ha feature summary completa
- ✅ Link validation: 0 broken

**Transizione a Fase 7**:
```
Documentazione validata
  ↓
Agent-Docs comunicates: "Docs synced. Ready per release?"
  ↓
User conferma: "Rilascia v3.6.0"
  ↓
Agent-Release prende il controllo (Phase 7)
```

---

### Fase 7️⃣: Release (Agent-Release)

**Quando inizia**: User richiede esplicitamente release / versioning.

**Input**:
- Branch review-ready (no uncommitted changes)
- Docs completi (from Agent-Docs)
- Test coverage >= 90% (release threshold)
- CHANGELOG.md con versione proposta

**Responsabilità Agent-Release**:
1. **Semantic Versioning Confirmation**:
   - Propone versione basata su CHANGELOG.md analysis
   - User confirm o manual override
   - Verifica versione sia consistente con formato

2. **CHANGELOG Finalization**:
   - Copia sezione [UNRELEASED] → [X.Y.Z — YYYY-MM-DD]
   - Aggiorna footer link comparazione GitHub
   - Crea sezione [UNRELEASED] vuota nuovo

3. **Build & Package**:
   ```bash
   python scripts/build-release.py --version 3.6.0
   ```
   - Esegui cx_freeze build
   - Output: dist/solitario-classico/solitario.exe
   - Genera checksum SHA256
   - Crea MANIFEST.txt (dependencies, versions)

4. **Git Tag Preparation**:
   - Propone: `git tag v3.6.0`
   - (User esegue manualmente)

5. **Release Notes Draft**:
   - Template GitHub Release automtico
   - User modifica + pubblica manualmente

**Output**:
```
Release Readiness Checklist:
✓ Version: 3.6.0 confirmed
✓ CHANGELOG finalized
✓ Build succeeded: dist/solitario-classico/solitario.exe
✓ Checksum: dist/solitario-classico/solitario.exe.sha256
✓ MANIFEST: dist/solitario-classico/MANIFEST.txt

Manual Steps Required:
1. git tag v3.6.0
2. git push origin main
3. git push origin v3.6.0
4. Create GitHub Release + upload artifacts

Draft Release Notes: [copied to clipboard]
```

**Gate di Completamento** (User Manual Actions):
- ✅ User esegue: `git tag v3.6.0`
- ✅ User esegue: `git push origin main`
- ✅ User esegue: `git push origin tags/v3.6.0`
- ✅ User crea GitHub Release (opzionale, manual)
- ✅ **RELEASE COMPLETE** ✅

---

## 📋 Trigger Events (Automazioni Riflessi)

Alcuni eventi **triggerano automaticamente** il prossimo step (senza user request esplicita):

| Evento | Trigger | Agente Attivato | Condizione |
|--------|---------|----------------|-----------|
| User esegue `/start` | Entrata fase codifica | Agent-Code | docs/TODO.md esiste |
| Tutti i commit code-phase spuntati in TODO | Codifica completa | Agent-Validate | Todo fully checked |
| Coverage >= 85% validato | Test OK | Agent-Docs | Validation passed |
| Docs syncato completo | Documentazione OK | Agent-Release | Docs verified |

**User può sempre**:
- Saltare trigger: `hold, no auto-advance` → aspetta conferma manuale
- Forzare bypass: `/force-release` → salta validation gates (non consigliato)
- Status check: `/status` → mostra workflow corrente

---

## 🔄 Flusso Ricapitolativo (A Colpo d'Occhio)

```
USER REQUEST (feature/fix/refactor)
     ↓
[Copilot suggest agente]
     ↓
AGENT-ANALYZE
  Input: User description
  Output: Findings report
  Gate: Analysis complete
     ↓
AGENT-DESIGN
  Input: Findings + requirements
  Output: DESIGN_*.md (DRAFT → REVIEWED)
  Gate: Status REVIEWED confirmed
     ↓
AGENT-PLAN
  Input: DESIGN_*.md REVIEWED + version target
  Output: PLAN_*.md (DRAFT → READY) + docs/TODO.md
  Gate: Status READY + TODO ready
     ↓
AGENT-CODE (LOOP per ogni fase)
  Input: docs/TODO.md current fase
  Action: Code + commit + spunta TODO
  Loop: fino TODO fully checked
  Gate: All phases complete + coverage >= 85%
     ↓
AGENT-VALIDATE
  Input: Committed code
  Output: Coverage report + test skeletons
  Gate: Coverage >= 85% (or 90% for release)
     ↓
AGENT-DOCS
  Input: Code commits + coverage OK
  Output: API.md + ARCHITECTURE.md + CHANGELOG.md synced
  Gate: Docs validated + links OK
     ↓
AGENT-RELEASE
  Input: Branch ready + docs OK + tests OK
  Output: Versioning + build + tag proposal
  Gate: User manual git push
     ↓
RELEASE COMPLETE ✅
  Executable: dist/solitario-classico/solitario.exe
  Versioned: vX.Y.Z tagged
  Documented: CHANGELOG updated
```

---

## 🚀 Comandi Rapidi (Riferimento)

| Comando | Effetto | Agente |
|---------|---------|--------|
| `/init feature-name` | Inizio workflow da analisi | Agent-Analyze (suggerisce) |
| `/start` | Riprendi fase codifica corrente | Agent-Code |
| `/Agent-Design` | Forza Agent-Design | Agent-Design |
| `/sync-docs` | Richiedi update docs | Agent-Docs |
| `/status` | Mostra workflow info | (no agente, info solo) |
| `/release v3.6.0` | Inizio fase release esplicita | Agent-Release |

---

## 📝 File di Stato Critici

- **docs/TODO.md** → cruscotto operativo durante branch (create/update da Agent-Plan, spunta da Agent-Code)
- **docs/3 - coding plans/PLAN_*.md** → fonte di verità implementazione
- **docs/2 - projects/DESIGN_*.md** → fonte di verità architetturale
- **.github/AGENTS.md** → descrizione agenti (questo file genitore)
- **CHANGELOG.md** → source of truth per versioni release
- **docs/API.md** → public API reference (aggiornato da Agent-Docs)
- **docs/ARCHITECTURE.md** → struttura e data flow (aggiornato da Agent-Docs)

**MAI ELIMINARE** questi file durante workflow attivo.

---

## 🔗 Cross-References

- **Agenti Dettagliati**: [.github/AGENTS.md](../.github/AGENTS.md)
- **Automazione CLI**: [docs/CI_AUTOMATION.md](CI_AUTOMATION.md) (create dopo)
- **Copilot Instructions**: [.github/copilot-instructions.md](../.github/copilot-instructions.md)
- **Template Progetti**: [docs/1 - templates/](1%20-%20templates/)

---

**Versione**: 1.0.0 — 17 Marzo 2026
