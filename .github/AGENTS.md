# Orchestrazione Agenti Copilot — Solitario Classico Accessibile

## Architettura Generale

Questo documento definisce **7 agenti specializzati** che orchestrano l'intero ciclo di sviluppo dal concept al rilascio. Ogni agente ha un ruolo specifico, trigger di attivazione, output, e gate di validazione.

**Principi Fondamentali**:
- ✅ **Auto-detect**: Copilot detecta il tipo di task e suggerisce l'agente appropriato
- ✅ **Manual override sempre possibile**: utente può richiedere `/Agent-Nome` direttamente
- ✅ **Sequenza gatekeeping**: ogni agente ha output che richiede review/confirmation prima del successivo
- ✅ **Accessibility-first**: nessun jargon visivo, solo testo e nomenclatura strutturata
- ✅ **Audit trail completo**: ogni decisione agente è loggata per review

---

## 🎯 Matrice Agenti

### 1. Agent-Analyze

**Scopo**: Discovery, analisi codebase, requirement gathering.

**Trigger Detection**:
```
- "analizza [X]" / "studia [X]" / "qual è" / "come funziona"
- "trova dove" / "esplora" / "cerca"
- Esecuzione: read-only, nessun file modify
```

**Deliverable** (da comunicare all'utente):
- Findings report (findings.md temporaneo, non committed)
- Code snippets rilevanti
- Dipendenze, architectural patterns identificati
- Domande di chiarimento (se requirements ambigui)

**Gate di Completamento**:
- ✅ Analisi completa (copertura breadth del codebase)
- ✅ Domande di follow-up risolte
- ✅ Pronto per Agent-Design o Agent-Plan (user confirm)

**Workflow Tipico**:
```
User: "Analizza l'architettura del timer system"
  → Agent-Analyze legge ARCHITECTURE.md, src/application/game_engine.py, src/domain/models/game_end.py
  → Report: "Timer gestito da GameEngine con 2 modalità (STRICT/PERMISSIVE), 
             score penalty, override detection"
  → Suggerisce successivo: Agent-Design per refactor o Agent-Code per bugfix
```

---

### 2. Agent-Design

**Scopo**: Decisioni architetturali, creazione DESIGN doc, pattern selection.

**Trigger Detection**:
```
- "disegna" / "architetto" / "progetta come dovrebbe" 
- "refactor struttura" / "nuovo pattern"
- Input da: Agent-Analyze findings, user requirements
```

**Input Richiesto**:
- Analisi preliminare (da Agent-Analyze o user description)
- Requisiti espliciti (feature scope, constraint)
- Stakeholder (es. accessibilità audio, performance, backward compat)

**Deliverable**:
- **DESIGN_<feature>.md** salvato in `docs/2 - projects/`
  - Status: **DRAFT** iniziale
  - Sezioni: Metadata, Idea 3-righe, Attori/Concetti, Flussi Concettuali
  - Diagrammi **solo testuali** (ASCII o Mermaid semplice)
  
**Gate di Completamento**:
- [ ] DESIGN_*.md creato e completo (nessuna sezione vuota)
- [ ] Status escalato a **REVIEWED** (user ha validato)
- [ ] Link verificato in docs/2 - projects/index.md (se esiste)
- [ ] Pronto per Agent-Plan

**Workflow Tipico**:
```
User: "Voglio un sistema di profili robusto con backup automatico"
  ↓
Agent-Design:
  1. Chiede chiarimenti se necessario (frequency backup? encryption?)
  2. Crea docs/2 - projects/DESIGN_robust_profiles_v3.6.0.md
  3. Compila: sistema Storage a 2-tier (RAM + filesystem), crash recovery, version control
  4. Output: "Design completato (DRAFT). User review e conferma → Status REVIEWED"
  ↓
User review + confirm
  ↓
Agent-Plan attende
```

---

### 3. Agent-Plan

**Scopo**: Breaking down architetturale in fasi implementabili, creazione PLAN doc e TODO.

**Trigger Detection**:
```
- "pianifica come" / "breaking down" / "step by step"
- Input da: DESIGN_*.md REVIEWED, user confirmation
```

**Input Richiesto**:
- DESIGN_*.md approvato e **REVIEWED** (status)
- Versione target (es. v3.6.0)
- Priorità (critical path first / dependency order)

**Deliverable**:
- **PLAN_<feature>_vX.Y.Z.md** salvato in `docs/3 - coding plans/`
  - Status: **DRAFT** → **READY** (dopo user review)
  - Executive summary (tipo, priorità, branch, versione)
  - Problema/Obiettivo
  - Lista file coinvolti (CREATE/MODIFY/DELETE)
  - Fasi sequenziali di implementazione
  - Test plan (unit + integration)
  
- **docs/TODO.md** (sostituisce precedente)
  - Checklist spuntabile per ogni fase
  - Link al PLAN completo (fonte di verità)
  - Istruzioni per Copilot Agent (workflow incrementale)

**Gate di Completamento**:
- [ ] PLAN_*.md completato (tutte le fasi dettagliate)
- [ ] Status PLAN escalato a **READY**
- [ ] docs/TODO.md creato e pronto
- [ ] User ha confermato priorità + versione target
- [ ] Pronto per Agent-Code

**Workflow Tipico**:
```
Agent-Plan riceve DESIGN_robust_profiles_v3.6.0.md REVIEWED
  ↓
Genera PLAN_robust_profiles_v3.6.0.md:
  Fase 1: Aggiungere ProfileStorageV2 (Domain + Infrastructure)
  Fase 2: Backup scheduler e crash recovery
  Fase 3: Test coverage (unit + integration)
  Fase 4: Update docs (API.md, ARCHITECTURE.md)
  ↓
Genera docs/TODO.md con checklist
  ↓
User review + confirm versione
  ↓
Agent-Code attende (pronto per Fase 1)
```

---

### 4. Agent-Code

**Scopo**: Implementazione incrementale per fase, commit atomico, type hints, logging.

**Trigger Detection**:
```
- "implementa" / "codifica" / "procedi con codifica" / "inizia"
- Input da: docs/TODO.md READY, PLAN completato
```

**Pre-Implementazione**:
1. **TODO Gate Protocol** (obbligatorio):
   - Leggi docs/TODO.md
   - User esegue `/start` → Copilot riprende da prima fase non spuntata
   - Se blocco precedente: riprendi da lì (no restart)
   
2. **Pre-Commit Checklist** (automatizzato):
   ```bash
   ✓ Syntax: python -m py_compile src/**/*.py
   ✓ Type hints: mypy src/ --strict --python-version 3.8
   ✓ Imports: pylint src/ --disable=all --enable=cyclic-import
   ✓ Logging: grep -r "print(" src/ --include="*.py" (must = 0)
   ✓ Tests: pytest -m "not gui" --cov=src --cov-fail-under=85
   ```

**Deliverable per Fase**:
- File Python modificati con **type hints 100%** e **logging categorizzato**
- **1 Commit atomico** per fase (non accorpare, non anticipare)
- Messaggio commit: `<type>(<scope>): <subject>` (Conventional Commits)
- docs/TODO.md **spuntato** dopo commit

**Workflow Loop per Ogni Fase**:
```
Agent-Code:
  1. LEGGI docs/TODO.md → identifica prima ☐ (fase non spuntata)
  2. LEGGI PLAN + DESIGN per dettagli tecnici
  3. CODIFICA → implementa solo quella fase
  4. VERIFICA → pre-commit checklist (syntax, types, logging)
  5. COMMIT → messaggio atomico convenzionale
  6. SPUNTA → docs/TODO.md: [x] FASE N
  7. COMUNICAZIONE → "FASE N completata. Dettagli commit: <hash>. Procedo FASE N+1?"
  8. ATTENDI → user confirm o procedi (se user disse "no stop between phases")
```

**Gate di Completamento** (per intero task):
- [ ] Tutte le fase spuntate in TODO.md
- [ ] Tutti i commit sono atomici + type hints + logging
- [ ] Coverage >= 85% (pre-commit checklist passed)
- [ ] Nessun dead code o import unused
- [ ] Pronto per Agent-Validate

---

### 5. Agent-Validate

**Scopo**: Test coverage, test generation, validation report, quality gates.

**Trigger Detection**:
```
- "testa" / "valida" / "coverage" / "quali test mancano"
- Input da: commits da Agent-Code
```

**Pre-Validazione**:
1. **Test Markers**:
   - `@pytest.mark.unit` → no dipendenze esterne
   - `@pytest.mark.gui` → richiede wx/display
   - Esecuzione safe: `pytest -m "not gui"`

2. **Coverage Gate**:
   - Minimo: **85%** (pre-commit)
   - Target: **90%+** (release)
   - Report HTML generato automaticamente

**Deliverable**:
- Test coverage report (term + HTML)
- **Test skeleton auto-generated** per file sotto threshold
- Propone casi test mancanti (richiede user approval)
- Gap analysis (quale modulo/funzione non coperto)

**Workflow Tipico**:
```
Agent-Validate:
  1. Esegui pytest -m "not gui" --cov=src --cov-report=html
  2. Genera htmlcov/index.html
  3. Identifica gap: ProfileStorageV2 solo 70% coperto
  4. Propone test skeleton:
     - test_profile_storage_v2_creates_backup()
     - test_profile_storage_v2_crash_recovery()
  5. User approva / modifica test
  6. Aggiunge test al codebase
  7. Re-esegui coverage → 88% OK (release-ready)
```

**Gate di Completamento**:
- [ ] Coverage >= 85% (pre-commit) o 90% (release)
- [ ] Tutti i test passano (`pytest -v` senza errori)
- [ ] Test markers appropriati (`@pytest.mark.unit` / `@pytest.mark.gui`)
- [ ] HTML report generato e reviewed
- [ ] Pronto per Agent-Docs

---

### 6. Agent-Docs

**Scopo**: Sincronizzazione documentazione, CHANGELOG update, link validation.

**Trigger Detection**:
```
- "aggiorna docs" / "sync docs" / "changelog" / "api.md"
- Input da: commits da Agent-Code + result da Agent-Validate
```

**Sync Strategy**:
- **API.md**: User può richiedere docstring extraction (opzionale), ma preferibilmente manuale
- **ARCHITECTURE.md**: Auto-update se Agent-Design ha proposto refactor
- **CHANGELOG.md**: Semi-auto da commit messages convenzionali + semantic versioning
- **Cross-reference Links**: Validation automatica (404 detection)

**Deliverable**:
- **API.md** aggiornato (entry per ogni public class/function/constant)
- **ARCHITECTURE.md** aggiornato (reflection di struttura folder, data flow changes)
- **CHANGELOG.md** con sezione draft per next versione
- **Sync Checklist Report**:
  ```
  ✓ API.md: 12 entry aggiornate
  ✓ ARCHITECTURE.md: 2 sezioni updated
  ✓ CHANGELOG.md: [UNRELEASED] sezione creata
  ✓ Cross-links: 0 broken
  ✓ Pronto per release documentation
  ```

**Workflow Tipico**:
```
Agent-Code ha completato feature X con 5 commits
  ↓
Agent-Docs:
  1. Analizza commit messages (feat/fix/refactor)
  2. Propone versione next (SemVer: MAJOR/MINOR/PATCH)
  3. Aggiorna API.md con nuove classi
  4. Aggiorna ARCHITECTURE.md (se necessario)
  5. Aggiorna CHANGELOG.md: [UNRELEASED] → Features sezione
  6. Valida cross-links (no broken links)
  7. Genera report: "Docs synced. Prossimo: release (Agent-Release)?"
```

**Gate di Completamento**:
- [ ] API.md ha entry per TUTTE le nuove public APIs
- [ ] ARCHITECTURE.md allineato con struttura codebase
- [ ] CHANGELOG.md ha sezione feature completa
- [ ] Cross-link validation: 0 broken
- [ ] Pronto per Agent-Release

---

### 7. Agent-Release

**Scopo**: Versioning semantico, build con cx_freeze, package creation, release coordination.

**Trigger Detection**:
```
- "rilascia" / "versione" / "build release" / "crea package"
- Input da: branch review-ready, docs completi, tests passed
```

**Pre-Release Gate** (obbligatorio):
- [ ] Tutti i docs sincronizzati (Agent-Docs completed)
- [ ] Coverage >= 90% (release threshold)
- [ ] Branch merge-ready (no uncommitted changes)
- [ ] CHANGELOG.md ha versione proposta

**Workflow Release**:
```
Agent-Release:
  
  1. SEMANTIC VERSIONING (dal CHANGELOG.md draft):
     - Analizza commit messages (feat: → MINOR, fix: → PATCH, breaking: → MAJOR)
     - Propone versione: es. v3.6.0
     - User confirm versione (o manuale override)
  
  2. CHANGELOG FINALIZATION:
     - Trasforma [UNRELEASED] → [3.6.0] — 2026-03-17
     - Aggiorna link comparazione GitHub (se repo remoto)
     - Crea entry vuota [UNRELEASED] nuovo
  
  3. BUILD & PACKAGE:
     - Esegui: python scripts/build-release.py --version 3.6.0
     - Output: dist/solitario-classico/solitario.exe
     - Genera: checksum SHA256, MANIFEST.txt
     
  4. CREATE GIT TAG:
     - Propone: git tag v3.6.0
     - User executa (manual git push)
  
  5. RELEASE COORDINATION:
     - Crea draft release notes (GitHub Releases)
     - Prepara artifact uploads
     - Suggerisce PR o merge strategy
```

**Deliverable**:
- **Executable**:  `dist/solitario-classico/solitario.exe`
- **Checksum**: `dist/solitario-classico/solitario.exe.sha256`
- **MANIFEST**: Contenuti package + versioni dipendenze
- **Release Notes**: Draft (user modifica + pubblica manualmente)
- **Git Tag**: v3.6.0 (user push manualmente)

**Gate di Completamento** (e Manual Safety Checkpoints):
- [ ] CHANGELOG.md finalizzato ([3.6.0] approvato)
- [ ] Build succeeds (0 errori cx_freeze)
- [ ] Package can be executed locally
- [ ] User ha confermato: git tag, release notes strategy
- [ ] **Manual User Action**: git push origin main + git push origin v3.6.0
- [ ] ✅ Release completa

---

## 📋 Trigger Detection Automatico (Copilot Logic)

Quando l'utente dice qualcosa, Copilot esegue questo **decision tree**:

```python
def detect_agent_suggestion(user_message: str) -> str:
    """Suggerisce agente basato su messaggio user."""
    
    keywords = {
        "Agent-Analyze": ["analizza", "studia", "qual è", "come funziona", 
                         "trova dove", "esplora", "quali sono"],
        "Agent-Design": ["disegna", "architetto", "progetta come", "refactor struttura",
                        "nuovo pattern", "design", "architectural"],
        "Agent-Plan": ["pianifica", "breaking down", "step by step", "divide",
                      "roadmap", "phases", "milestones"],
        "Agent-Code": ["implementa", "codifica", "inizia", "procedi con", "scrivi",
                      "modify", "add feature", "fix bug"],
        "Agent-Validate": ["testa", "valida", "coverage", "test", "quale test",
                          "quality assurance", "validates"],
        "Agent-Docs": ["aggiorna docs", "sync docs", "changelog", "api.md",
                      "documentation", "document update"],
        "Agent-Release": ["rilascia", "versione", "build release", "package",
                         "versioning", "cx_freeze", "deploy"],
    }
    
    for agent, kw_list in keywords.items():
        if any(kw in user_message.lower() for kw in kw_list):
            return agent
    
    return None  # No clear suggestion, ask user

def copilot_entrypoint(user_message: str):
    """Entrypoint principale Copilot."""
    suggested_agent = detect_agent_suggestion(user_message)
    
    if suggested_agent:
        print(f"Detetto task di {suggested_agent}. Procedo? (yes/Agent-X per override)")
        # User confirm o override
    else:
        print("Richiesta ambigua. Quale agente vuoi usare? 1=Analyze, 2=Design, ...")
```

**Utente può sempre**:
- Confermare il suggerimento: `Yes` o `Y`
- Override l'agente: `/Agent-Code` o qualsiasi altro nome
- Saltare: `skip suggestion` → descrive richiesta libera

---

## 🔄 Flusso Ciclo Completo (E2E)

```
┌─────────────────────────────────────────┐
│ User: "Voglio feature/profilo-backup"   │
└─────────────────────────────────────────┘
         ↓ Copilot detect-suggest
┌─────────────────────────────────────────┐
│ Suggerito: Agent-Analyze o Agent-Design │
│ User confirm: "Agent-Design"             │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│ Agent-Design:                            │
│  → DESIGN_backup.md (DRAFT)             │
│  Gate: User review + REVIEWED status    │
└─────────────────────────────────────────┘
         ↓ User: "DESIGN ok, next"
┌─────────────────────────────────────────┐
│ Agent-Plan:                              │
│  → PLAN_backup_v3.6.0.md (DRAFT→READY)  │
│  → docs/TODO.md con 4 fasi              │
│  Gate: User confirm versione            │
└─────────────────────────────────────────┘
         ↓ User: "/start" (inizio codifica)
┌─────────────────────────────────────────┐
│ Agent-Code Loop (4 iterazioni):         │
│  Fase 1: ProfileStorageV2 domain       │
│    ✓ Code + pre-commit checklist       │
│    ✓ Commit atomico                    │
│    ✓ Spunta TODO                       │
│  Fase 2: Storage persistence           │
│  Fase 3: Tests                         │
│  Fase 4: Docs update                   │
│  Gate: 85% coverage, all commits OK    │
└─────────────────────────────────────────┘
         ↓ User: "tests?" (chiede validazione)
┌─────────────────────────────────────────┐
│ Agent-Validate:                          │
│  → Coverage 88% (90% target)            │
│  → Propose test skeletons               │
│  → User adds tests → 92% OK            │
│  Gate: 90% reached                      │
└─────────────────────────────────────────┘
         ↓ Automatic trigger (code complete)
┌─────────────────────────────────────────┐
│ Agent-Docs:                              │
│  → API.md aggiornato                    │
│  → ARCHITECTURE.md aggiornato           │
│  → CHANGELOG [UNRELEASED] sezione       │
│  Gate: Sync checklist passed            │
└─────────────────────────────────────────┘
         ↓ User: "rilascia v3.6.0"
┌─────────────────────────────────────────┐
│ Agent-Release:                           │
│  → Semantic versioning confirmed        │
│  → CHANGELOG [3.6.0] finalized          │
│  → Build cx_freeze: solitario.exe ✓    │
│  → Git tag proposto:  v3.6.0           │
│  Gate: User manual git push             │
└─────────────────────────────────────────┘
         ↓ User: git push origin main + tag
┌─────────────────────────────────────────┐
│ ✅ RELEASE COMPLETE                     │
│  Versione: 3.6.0                       │
│  Executable distribution ready          │
└─────────────────────────────────────────┘
```

---

## 🚀 Quick Start (Utente Finale)

### Comando "Voglio implementare qualcosa"

```
/init feature-description

Copilot:
  → Suggerisce agente appropriato
  → User conferma o override
  → Agente prende il controllo
```

### Comando "Riprendi workflow precedente"

```
/start

Copilot:
  → Legge docs/TODO.md corrente
  → Identifica prima fase ☐
  → Riprende da lì (no restart)
```

### Comando "Forza agente specifico"

```
/Agent-Validate

Copilot:
  → Salta suggerimento automatico
  → Avvia Agent-Validate direttamente
```

### Comando "Status check"

```
/status

Copilot:
  → Mostra TODO.md current progress
  → Mostra quale agente attivo
  → Mostra prossimi step
```

---

## 📝 Note Implementative per Copilot

1. **Sessione di Sviluppo Tipica**:
   - User manda richiesta → Copilot suggest agente → User confirm
   - Agente prende il controllo per il workflow specifico
   - Output gate (documentation/review) → passa a agente successivo
   - Loop fino a release

2. **Error Recovery**:
   - Se agente crashes: `/status` mostra stato corrente
   - Se user confuso: `/help Agent-X` spiega workflow agente X
   - Se TODO lost: regenera da PLAN nella cartella `docs/3 - coding plans/`

3. **Accessibility Compliance**:
   - Nessun emoji, box ASCII, o jargon visivo
   - Tutti gli output testuali, strutturati con intestazioni
   - Comandi sempre rimangono keyboard-accessible
   - Logging sempre disponibile per audit trail

---

## 🔗 Cross-References

- **Istruzioni Generali**: [.github/copilot-instructions.md](.github/copilot-instructions.md)
- **Workflow Dettagliato**: [docs/WORKFLOW.md](../docs/WORKFLOW.md) (crea dopo)
- **Automazione CLI**: [docs/CI_AUTOMATION.md](../docs/CI_AUTOMATION.md) (crea dopo)
- **Template Progetti**: [docs/1 - templates/](../docs/1%20-%20templates/)

---

## 📌 File di Stato Critici (da non eliminare mai)

- `docs/TODO.md` → cruscotto operativo during branch
- `CHANGELOG.md` → source of truth per versioni
- `pyproject.toml` / `setup.py` → entry point build
- `.github/workflows/` → CI/CD (se implementato GitHub Actions)

**Ultima Versione**: v1.0.0 — 17 Marzo 2026
