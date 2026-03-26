# Copilot Custom Instructions  Solitario Classico Accessibile

## Contesto Progetto

Leggi `.github/project-profile.md` prima di
qualsiasi operazione. È la source of truth per
nome, stack tecnico e architettura del progetto.
Non usare valori hardcoded in questo file come
riferimento al progetto corrente.

Se `initialized: false`: NON interrompere l'operazione.
Aggiungi in testa alla tua risposta questo avviso,
prima di qualsiasi altro contenuto:

***
⚠️ PROGETTO NON INIZIALIZZATO
Il framework non è ancora configurato per questo progetto.
Per abilitare tutte le funzionalità in modo ottimale:
scrivi `#project-setup` in chat oppure seleziona
Agent-Welcome dal dropdown agenti, scrivi in chat 
'aiuto, iniziare o nuovo progetto'  e segui il percorso
guidato (circa 2 minuti).
Puoi continuare a usare il framework normalmente.
***

Poi prosegui normalmente con il task richiesto.

## Framework Copilot v1.8.1

**Questo progetto utilizza un framework orchestrazione Copilot con 14 agenti nativi VS Code.**

### Quick Start (3 passi)

1. **Seleziona agente**: dal dropdown agenti nella chat di VS Code (`.github/agents/`)
2. **Scopri gli agenti**: [.github/agents/Agent-NAME.md](agents/) per la specifica di ciascuno
3. **Inizio task**: scrivi `#init` in chat e seleziona `init.prompt.md` dal file picker

### Componenti Framework

| Componente | Scopo |
|-----------|-------|
| **`.github/agents/*.md`** | 14 agenti nativi VS Code con tool restrictions |
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
| **`.github/instructions/workflow-standard.instructions.md`** | Sequenza operativa standard per modifiche, TODO gate, pre-commit, sync docs |
| **`.github/skills/*.skill.md`** | Abilità atomiche riutilizzabili tra agenti |

### I 14 Agenti

0. **Agent-Helper**: Consultivo read-only sul Framework Copilot (non-E2E)
0. **Agent-Welcome**: Setup profilo progetto, inizializzazione framework (non-E2E)
1. **Agent-Orchestrator**: Coordinatore E2E, delega agli agenti specializzati
1. **Agent-Analyze**: Discovery findings (read-only)
2. **Agent-Design**: DESIGN_*.md doc (DRAFT  REVIEWED)
3. **Agent-Plan**: PLAN_*.md + docs/TODO.md (DRAFT  READY)
4. **Agent-Code**: Implementazione loop, commits atomici (TODO checklist)
   4a. **Agent-CodeRouter**: Dispatcher sotto-ciclo codifica, classifica GUI vs non-GUI
   4b. **Agent-CodeUI**: Implementazione GUI wxPython, accessibilità NVDA obbligatoria
5. **Agent-Validate**: Test coverage (85%+ threshold)
6. **Agent-Docs**: API.md, ARCHITECTURE.md, CHANGELOG.md sync
7. **Agent-Release**: Versioning SemVer, cx_freeze build, tag proposal
8. **Agent-FrameworkDocs**: Docs e changelog Framework Copilot (scope: .github/**)
9. **Agent-Git**: Operazioni git autorizzate (commit, push, merge, tag)

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
| `#verbosity` | `#verbosity.prompt.md` (richiede `#framework-unlock` se `framework_edit_mode: false`) |
| `#personality` | `#personality.prompt.md` (richiede `#framework-unlock` se `framework_edit_mode: false`) |

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
- UI wxPython → `.github/instructions/ui.instructions.md`
  (attivo automaticamente su `src/presentation/**/*.py`)

Skills riutilizzabili tra agenti: lista completa in `.github/AGENTS.md`
(sezione Agent Skills) e `.github/skills/README.md`.

---

## Documentazione e Workflow Operativo

Regole TODO gate, pre-commit checklist, sync docs e feedback strutturato:
→ `.github/instructions/workflow-standard.instructions.md` (applyTo: `**`)

Struttura DESIGN/PLAN/TODO e frontmatter:
→ `.github/skills/document-template.skill.md`

---

## Testing

Vedi `.github/instructions/tests.instructions.md` per coverage minima,
markers, naming pattern e regole CI-safe.

---

## Convenzioni Git

Formato commit, branch policy, SemVer e release steps:
→ `.github/skills/conventional-commit.skill.md`
→ `.github/instructions/git-policy.instructions.md`
→ `.github/skills/semver-bump.skill.md`

---

## Git Policy (Summary)

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

## Model Policy

Regole di selezione modello per tutti gli agenti del framework.
Dettaglio completo in:
→ `.github/instructions/model-policy.instructions.md` (applyTo: `.github/**`)

---

## Referimenti Rapidi

| Risorsa | Scopo |
|---------|-------|
| [.github/instructions/model-policy.instructions.md](instructions/model-policy.instructions.md) | Assegnazioni modelli agenti e criteri selezione |
| [.github/AGENTS.md](AGENTS.md) | 14-agent system, v1.6.0 |
| [docs/WORKFLOW.md](../docs/WORKFLOW.md) | E2E workflow |
| [docs/CI_AUTOMATION.md](../docs/CI_AUTOMATION.md) | CI locale |
| [.vscode/copilot-quick-start.md](../.vscode/copilot-quick-start.md) | Commands (5 min) |
| docs/1 - templates/ | DESIGN/PLAN/TODO scaffold |
