# Copilot Custom Instructions  Solitario Classico Accessibile

## Framework Copilot v1.5.1

**Questo progetto utilizza un framework orchestrazione Copilot con 9 agenti nativi VS Code.**

### Quick Start (3 passi)

1. **Seleziona agente**: dal dropdown agenti nella chat di VS Code (`.github/agents/`)
2. **Scopri gli agenti**: [.github/agents/Agent-NAME.md](agents/) per la specifica di ciascuno
3. **Inizio task**: scrivi `#init` in chat e seleziona `init.prompt.md` dal file picker

### Componenti Framework

| Componente | Scopo |
|-----------|-------|
| **`.github/agents/*.md`** | 9 agenti nativi VS Code con tool restrictions |
| **`.github/prompts/*.md`** | Prompt files per entry point e workflow |
| **Ciclo Dev E2E** | Fase per fase, gate, transizioni |
| **Automazione CLI** | Pre-commit hook, script validation, changelog, build |
| **CI GitHub Actions** | Workflow syntax, types, lint, test |
| **Agent-Orchestrator** | Coordinatore E2E con subagent delegation |
| **Agent-FrameworkDocs** | Manutenzione docs e changelog framework |
| **Quick Reference** | Comandi rapidi, troubleshooting |
| **Script Utility** | 8 script Python per automazione |
| **`.github/instructions/*.instructions.md`** | Regole contestuali per filetype |
| **`.github/instructions/git-policy.instructions.md`** | Policy git operativa (applyTo: `**`) |
| **`.github/skills/*.skill.md`** | Abilità atomiche riutilizzabili tra agenti |

### I 9 Agenti

0. **Agent-Orchestrator**: Coordinatore E2E, delega agli agenti specializzati
1. **Agent-Analyze**: Discovery findings (read-only)
2. **Agent-Design**: DESIGN_*.md doc (DRAFT  REVIEWED)
3. **Agent-Plan**: PLAN_*.md + docs/TODO.md (DRAFT  READY)
4. **Agent-Code**: Implementazione loop, commits atomici (TODO checklist)
5. **Agent-Validate**: Test coverage (85%+ threshold)
6. **Agent-Docs**: API.md, ARCHITECTURE.md, CHANGELOG.md sync
7. **Agent-Release**: Versioning SemVer, cx_freeze build, tag proposal
8. **Agent-FrameworkDocs**: Docs e changelog Framework Copilot (scope: .github/**)

### Comandi Entry Point

| Comando testuale | Metodo nativo VS Code |
|-----------------|----------------------|
| `/init <task>` | `#init.prompt.md` (file picker o scrivi #init in chat) |
| `/start` | `#start.prompt.md` |
| `/status` | `#status.prompt.md` |
| `/sync-docs` | `#sync-docs.prompt.md` |
| `/release vX.Y.Z` | `#release.prompt.md` |
| `#orchestrate` | `#orchestrate.prompt.md` (ciclo E2E completo) |
| `/Agent-<Name>` | Seleziona dal dropdown agenti VS Code |
| `/create-agent` | Comando nativo VS Code per generare nuovo file agente |
| `/create-prompt` | Comando nativo VS Code per generare nuovo prompt file |
| `/framework-update` | `#framework-update.prompt.md` |
| `/framework-changelog` | `#framework-changelog.prompt.md` |
| `/framework-release` | `#framework-release.prompt.md` |

Per dettagli completi: [.github/AGENTS.md](AGENTS.md) e [docs/WORKFLOW.md](../docs/WORKFLOW.md).

---

## Dual-Track Documentation

Il framework adotta una separazione netta tra documentazione del framework
e documentazione del progetto ospite.

**Binario Framework** — gestito da Agent-FrameworkDocs:

- `.github/FRAMEWORK_CHANGELOG.md`: storico evoluzione framework
- `.github/AGENTS.md`: riferimento agenti e versioni
- `.github/README.md`: guida importazione framework

**Binario Progetto** — gestito da Agent-Docs nel ciclo E2E:

- `CHANGELOG.md` della root: storico del progetto applicativo
- `docs/API.md`, `docs/ARCHITECTURE.md`: documentazione tecnica progetto

**Regola invariante**: Agent-FrameworkDocs non tocca mai `CHANGELOG.md`
della root. Agent-Docs non tocca mai `FRAMEWORK_CHANGELOG.md`.
I due binari non si incrociano.

---

## Profilo Utente e Interazione

* **Accessibilità**: Programmatore non vedente, NVDA + Windows 11. Testabile da tastiera + screen reader.
* **Feedback Strutturato**: (1) Cosa cambia (file + linee), (2) Perché, (3) Impatto docs.
* **Markdown**: Header gerarchici + liste. NO tabelle complesse, NO emoji ASCII.

---

## Architettura e Standard di Codifica

### Clean Architecture (Summary)

4 Layer: Presentation → Application → Domain → Infrastructure

Regole dettagliate per layer, naming, type hints, logging, error
handling e accessibilità sono nelle instructions contestuali:

- Python standards → `.github/instructions/python.instructions.md`
  (attivo automaticamente su tutti i file `*.py`)
- Test standards → `.github/instructions/tests.instructions.md`
  (attivo automaticamente su `tests/**/*.py`)
- Domain rules → `.github/instructions/domain.instructions.md`
  (attivo automaticamente su `src/domain/**/*.py`)

Skills riutilizzabili tra agenti:
- Accessibilità NVDA (UI) → `.github/skills/validate-accessibility.skill.md`
- Conventional Commits → `.github/skills/conventional-commit.skill.md`
- SemVer bump → `.github/skills/semver-bump.skill.md`
- Clean Architecture → `.github/skills/clean-architecture-rules.skill.md`
- Template documenti → `.github/skills/document-template.skill.md`
- Output accessibile → `.github/skills/accessibility-output.skill.md`
- Git execution matrix → `.github/skills/git-execution.skill.md`

---

## Documentazione: TODO Gate + Sync (Essentials)

### TODO Gate

Trigger: multi-file/multi-commit implementation.

**Step rapido:**
1. Controlla docs/TODO.md (crea se assente)
2. Verifica TODO appartiene task corrente
3. Leggi TODO + PLAN collegato
4. Loop: CODIFICA  VERIFICA  COMMIT  SPUNTA

### File Obbligatori

| File | Trigger | Stato |
|------|---------|-------|
| DESIGN_*.md | Feature architetturale | DRAFT  REVIEWED |
| PLAN_*.md | Task multi-commit | DRAFT  READY |
| docs/TODO.md | PLAN approvato | Operativo |

**Workflow**: DESIGN  PLAN  TODO  implementazione  sync docs

### Sync Trigger

Dopo ogni modifica .py:
- **API.md**: Signature pubbliche, export da __init__.py?
- **ARCHITECTURE.md**: Struttura, layer flow, pattern, dipendenze?
- **CHANGELOG.md**: SEMPRE (Added/Fixed/Changed). Usa [Unreleased] nel branch.

### Pre-Commit Checklist

```
1. Syntax: python -m py_compile src/**/*.py
2. Type Hints: mypy src/ --strict
3. Imports: pylint --enable=cyclic-import
4. Logging: grep -r "print(" src/ (0 occorrenze)
5. Tests: pytest --cov=src --cov-fail-under=85
6. Gates: python scripts/validate_gates.py --check-all docs/2\ -\ projects/
```

---

## Testing

Vedi `.github/instructions/tests.instructions.md` per coverage minima,
markers, naming pattern e regole CI-safe.

---

## Convenzioni Git

### Atomic Commits

Format: <type>(<scope>): <subject>

Types: feat, fix, docs, refactor, test, chore

Scope: domain, application, infrastructure, presentation, docs, tests

**Ordine consigliato**:
1. Pre-requisiti
2. Implementazione
3. Test
4. Update docs
5. Update TODO.md

### Branch & Release

| Tipo | Pattern | Regola |
|------|---------|--------|
| Feature | feature/<slug> | Branch separato |
| Fix | fix/<slug> | Branch separato |
| Release | Merge --no-ff | Preserva storia |

**Release steps**: Branch verificato  PR on main  Merge --no-ff  Tag vX.Y.Z  Update CHANGELOG.md

**SemVer**: MAJOR (breaking), MINOR (feature), PATCH (bugfix)

---

## Workflow Standard

**Quando l'utente chiede modifiche:**
1. TODO Gate (se multi-file): verifica/crea docs/TODO.md
2. Type hints + logging semantico
3. Verifica accessibilità
4. Audit docs (proponi sync)
5. Test coverage check (85%+)
6. Feedback strutturato (file+linee, why, docs impact)

**Git policy**:

Copilot NON esegue direttamente `git push`, `git merge` su main,
né `git commit` durante implementazioni automatizzate degli agenti.
Propone sempre i comandi in blocco testuale: è l'utente a eseguirli.
Read-only sempre consentito: `git log`, `git diff`, `git status`.

**Eccezioni autorizzate (unici contesti in cui Copilot può eseguire
git tramite `run_in_terminal`)**:
- `Agent-Git` — agente dedicato, unico punto di esecuzione git diretta
- `#git-commit.prompt.md` — dispatcher leggero, delega ad Agent-Git
- `#git-merge.prompt.md` — dispatcher leggero, delega ad Agent-Git

Agent-Git è l'unico agente autorizzato a eseguire git tramite
run_in_terminal. Tutti gli altri agenti propongono i comandi come
testo e delegano ad Agent-Git quando necessario.

Questi 2 prompt sono gli UNICI punti di esecuzione git diretta.
In qualsiasi altro contesto (agenti, chat libera, altri prompt)
la policy di blocco è assoluta.

Per dettaglio operativo completo:
→ `.github/instructions/git-policy.instructions.md`
→ `.github/skills/git-execution.skill.md`

---

## Referimenti Rapidi

| Risorsa | Scopo |
|---------|-------|
| [.github/AGENTS.md](AGENTS.md) | 9-agent system |
| [docs/WORKFLOW.md](../docs/WORKFLOW.md) | E2E workflow |
| [docs/CI_AUTOMATION.md](../docs/CI_AUTOMATION.md) | CI locale |
| [.vscode/copilot-quick-start.md](../.vscode/copilot-quick-start.md) | Commands (5 min) |
| docs/1 - templates/ | DESIGN/PLAN/TODO scaffold |
