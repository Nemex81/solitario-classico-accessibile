# Copilot Quick Start — Solitario Classico Accessibile

> **Ultimo aggiornamento**: 21 Marzo 2026  
> **Versione Framework**: 1.2.0

Questo file è un **quick reference** per usare il framework Copilot di questo workspace. Consultalo quando inizi un task.

---

## Entrypoint Principale

### Come iniziare un task

**Metodo 1 (consigliato)**: scrivi `#init` in chat, seleziona `init.prompt.md` dal file picker.

**Metodo 2 (alternativo)**: scrivi `/init <descrizione>` in chat.

**Esempio**:
```
#init
-> Seleziona init.prompt.md -> Descrivi: "Voglio aggiungere un sistema di backup automatico per i profili utente"
```

**Copilot fara**:
1. Analizza la descrizione
2. Suggerisce quale agente usare (Analyze / Design / Plan / Code / Validate / Docs / Release)
3. Tu confermi o overridei: `yes`, `no`, `/Agent-Name`

---

## Comandi Rapidi (Copy-Paste Ready)

| Comando testuale | Metodo nativo VS Code | Effetto |
|-----------------|----------------------|--------|
| `/init <descrizione>` | `#init.prompt.md` dal file picker | Inizio task da analisi |
| `/start` | `#start.prompt.md` | Riprendi codifica da TODO.md |
| `/status` | `#status.prompt.md` | Mostra stato workflow |
| `/sync-docs` | `#sync-docs.prompt.md` | Sincronizza API.md, ARCHITECTURE.md |
| `/release v3.6.0` | `#release.prompt.md` | Trigger Agent-Release |
| `/help <agente>` | `#help.prompt.md` | Info su come funziona agente |
| `/Agent-X` | Dropdown agenti in chat (seleziona Agent-X) | Forza agente specifico |

---

## Agenti Nativi VS Code

Gli agenti del framework sono ora disponibili nel dropdown agenti
della chat di VS Code.

Per attivare un agente specifico:
- Metodo 1: clicca dropdown agenti nella chat, seleziona Agent-X
- Metodo 2: scrivi /Agent-Analyze per attivazione testuale (fallback)

Ogni agente ha tool restrictions proprie:
- Agent-Analyze: solo lettura (no modifiche file)
- Agent-Code: lettura + scrittura + terminale
- Agent-Release: lettura + scrittura + terminale
- Agent-Design, Agent-Plan, Agent-Docs: lettura + scrittura
- Agent-Validate: lettura + terminale

I file agente si trovano in `.github/agents/`.

---

## Workflow Standard (7 Agenti)

```
Fase 1: ANALYZE
├─ Agent-Analyze
├─ Input: User description
├─ Output: Findings report
└─ Gate: Analysis complete ✓ → Designer pronto

Fase 2: DESIGN
├─ Agent-Design
├─ Input: Findings + requirements
├─ Output: DESIGN_*.md (DRAFT → REVIEWED)
└─ Gate: Status REVIEWED ✓ → Planner pronto

Fase 3: PLAN
├─ Agent-Plan
├─ Input: DESIGN_*.md REVIEWED
├─ Output: PLAN_*.md (DRAFT → READY) + docs/TODO.md
└─ Gate: Status READY ✓ → Developer pronto

Fase 4: CODE (LOOP per ogni fase)
├─ Agent-Code
├─ Input: docs/TODO.md corrente
├─ Azioni: Code → Pre-commit check → Commit → Spunta TODO
└─ Gate: All phases complete + 85% coverage ✓ → Validator pronto

Fase 5: VALIDATE
├─ Agent-Validate
├─ Input: Committed code
├─ Output: Coverage report + test skeletons
└─ Gate: Coverage >= 85% ✓ → Documentarian pronto

Fase 6: DOCS
├─ Agent-Docs
├─ Input: Code commits + coverage OK
├─ Output: API.md + ARCHITECTURE.md + CHANGELOG.md synced
└─ Gate: Docs validated ✓ → Release Engineer pronto

Fase 7: RELEASE
├─ Agent-Release
├─ Input: Branch ready + docs OK + tests OK
├─ Output: Build + versioning + tag proposal
└─ Gate: User manual git push (final control)
```

---

## File Critici da Conoscere

| File | Scopo | Chi modifica | Note |
|------|-------|-------------|------|
| [.github/AGENTS.md](.github/AGENTS.md) | Descrizione 7 agenti | (Non toccare) | Overview e indice agenti (v1.2.0) |
| [docs/WORKFLOW.md](docs/WORKFLOW.md) | Ciclo dev end-to-end | (Non toccare) | Processo dettagliato |
| [docs/CI_AUTOMATION.md](docs/CI_AUTOMATION.md) | Setup automazione | (Non toccare) | Setup pre-commit, script |
| **docs/TODO.md** | Cruscotto operativo | Agent-Plan crea, Agent-Code aggiorna | **Vedi questo durante codifica** |
| **docs/2 - projects/DESIGN_*.md** | Design doc | Agent-Design crea | Fonte di verità architetturale |
| **docs/3 - coding plans/PLAN_*.md** | Piano implementazione | Agent-Plan crea | Fonte di verità implementativa |
| `.github/copilot-instructions.md` | Istruzioni generali Copilot | (Non toccare) | Policy accessibilità, architecture |

---

## Directory Script (Automazione)

Tutti i script si trovano in `scripts/`:

```
scripts/
├── detect_agent.py                # Rileva agente appropriato da descrizione task
├── validate_gates.py              # Valida frontmatter YAML dei doc DESIGN/PLAN/TODO
├── ci-local-validate.py           # Pre-commit checklist (syntax, types, coverage)
├── generate-changelog.py          # SemVer + CHANGELOG.md update
├── build-release.py               # cx_freeze build + checksums
├── sync-documentation.py          # Valida API.md, ARCHITECTURE.md, links
├── create-project-files.py        # Scaffolding DESIGN/PLAN/TODO
└── pre-commit-hook-template.sh    # Git hook template
```

### Esecuzione Rapida

**Pre-commit checklist (comando development)**:
```bash
python scripts/ci-local-validate.py
```

**Genera versione + aggiorna CHANGELOG**:
```bash
python scripts/generate-changelog.py
```

**Build release**:
```bash
python scripts/build-release.py --version 3.6.0
```

**Valida documentazione**:
```bash
python scripts/sync-documentation.py
```

---

## Architettura Codebase (Reference Veloce)

**Clean Architecture a 4 Layer**:

```
Domain Layer (src/domain/)
  ├─ models/          # Entities, Value Objects
  ├─ services/        # Domain Services (business rules)
  ├─ exceptions.py    # Domain-specific exceptions
  └─ interfaces/      # Abstract interfaces per Infrastructure

Application Layer (src/application/)
  ├─ use_cases/       # Orchestration di Domain services
  ├─ services/        # App-specific services (game_engine, cursor_manager)
  └─ commands/        # Command patterns

Infrastructure Layer (src/infrastructure/)
  ├─ ui/              # wxPython UI code (Presentation)
  ├─ audio/           # Audio system (pygame, TTS)
  ├─ persistence/     # File I/O, JSON serialization
  ├─ logging/         # Logging setup
  └─ di_container.py  # Dependency injection

Presentation Layer (src/presentation/)
  ├─ dialogs/         # Dialog windows (no business logic!)
  ├─ formatters/      # Output formatting
  └─ screen_reader/   # Screen reader integration
```

**Dipendenze Rigorose**:
- ✅ Domain ha ZERO dipendenze esterne
- ✅ Application dipende SOLO da Domain
- ✅ Infrastructure dipende da Domain (implementa interfacce)
- ✅ Presentation dipende da Application + Infrastructure

**No Circularità**: mai `domain` → `infrastructure` verso `domain`

---

## Troubleshooting Veloce

### "Non so da dove cominciare"
Scrivi `#init` in chat, seleziona init.prompt.md e descrivi il task.

### "Voglio riprendere da dove ho lasciato"
Scrivi `#start` in chat oppure `/start`. Legge docs/TODO.md e riprende dalla prima fase non completata.

### "Pre-commit check fallisce"
Esegui `python scripts/ci-local-validate.py --verbose` e leggi gli errori.

### "Non so quale agente usare"
Scrivi `#help` in chat oppure consulta [.github/AGENTS.md](.github/AGENTS.md).

### "Coverage e basso"
Esegui `pytest -m "not gui" --cov=src --cov-report=html` e apri `htmlcov/index.html`.

### "Voglio skippare un agente"
Seleziona l'agente desiderato dal dropdown agenti nella chat, oppure scrivi `/Agent-NomeAgente`.

### "L'agente non appare nel dropdown"
Verifica che il file `.github/agents/Agent-X.md` esista e abbia il frontmatter YAML corretto (name, description, tools, model).

### "Il prompt file non si attiva"
Scrivi `#` in chat e verifica che VS Code mostri il file nel picker. Se assente, controlla che il file sia in `.github/prompts/` con estensione `.prompt.md`.

### "validate_gates.py segnala errori"
Controlla che il documento abbia un frontmatter YAML valido (delimitato da `---`) con almeno i campi: type, feature, status. Esegui `python scripts/validate_gates.py --check-design <file>` per dettagli.

---

## Documentazione Completa

Per approfondire ogni componente:

1. **Agenti Specializzati**: [.github/AGENTS.md](.github/AGENTS.md)
   - Descrizione dettagliata di ognuno dei 7 agenti
   - Input/Output di ogni agente
   - Gate di completamento

2. **Workflow Ciclo Completo**: [docs/WORKFLOW.md](docs/WORKFLOW.md)
   - Fase per fase del ciclo dev
   - Transizioni tra agenti
   - Trigger events automatici

3. **Automazione Locale**: [docs/CI_AUTOMATION.md](docs/CI_AUTOMATION.md)
   - Setup pre-commit hook
   - Comandi script (ci-validate, changelog, build, release)
   - Troubleshooting

4. **Copilot Instructions Generali**: [.github/copilot-instructions.md](.github/copilot-instructions.md)
   - Policy Clean Architecture
   - Naming conventions
   - Type hints obbligatori
   - Logging categoria
   - Error handling
   - Accessibilità

5. **Template Progetti**: [docs/1 - templates/](docs/1%20-%20templates/)
   - Template DESIGN document
   - Template PLAN document
   - Template TODO cruscotto

---

## Sei Comandi Piu Frequenti

Durante sviluppo, userai ricorrentemente:

```bash
# 1. Inizia nuovo task
/init <descrizione>

# 2. Riprendi codifica in corso
/start

# 3. Valida codice prima di commit (local)
python scripts/ci-local-validate.py

# 4. Aggiorna versione + CHANGELOG
python scripts/generate-changelog.py

# 5. Valida frontmatter documenti progetto
python scripts/validate_gates.py --check-all docs/2\ -\ projects/

# 6. Status check during workflow
/status
```

---

## Esempio Workflow Completo (5 minuti)

```
1. User:  "/init Voglio backup automatico profili"
   Copilot: "Suggerito: Agent-Analyze. Procedo?"
   
2. User:  "yes"
   Copilot: [Analizza codebase, suggerisce Agent-Design]
   
3. User:  "procedi design"
   Agent-Design: [Crea docs/2 - projects/DESIGN_backup.md (DRAFT)]
   "Review DESIGN_backup.md e conferma status REVIEWED"
   
4. User:  [Edita DESIGN, conferma REVIEWED]
   Agent-Plan: [Crea PLAN_backup_v3.6.0.md + docs/TODO.md]
   "Pronto per codifica"
   
5. User:  "/start"
   Agent-Code: [Implementa FASE 1: Domain model]
   Commit: "feat(domain): aggiunto BackupStorage entity"
   Spunta TODO
   "Procedo FASE 2?"
   
6. User:  "yes"
   [... loop fasi ...]
   
7. Agent-Code: "Codifica completa!"
   Agent-Validate: [Coverage 88%, testa skeletons accepted]
   
8. Agent-Docs: [Sincronizza API.md, ARCHITECTURE.md, CHANGELOG.md]
   
9. Agent-Release: "Build v3.6.0"
   python scripts/build-release.py --version 3.6.0
   
10. User: [Esegue git push, release pubblicata]
    ✅ DONE
```

---

## Aiuto e Support

- **Leggi il file AGENTS.md**: risponde a "chi fa cosa"
- **Leggi il file WORKFLOW.md**: risponde a "in che ordine"
- **Esegui `/help <agente>`**: ottieni aiuto su agente specifico
- **Esegui `/status`**: vedi dove sei nel workflow
- **Consulta i template**: `docs/1 - templates/` per esempi

---

**Ultimo Update**: 21 Marzo 2026 | **Framework Version**: 1.2.0 | **Python**: 3.8+ | **Versionamento**: SemVer
