<!--
Template canonico neutro per ripristino di .github/copilot-instructions.md.

Scopo: SOLO su richiesta esplicita dell'utente tramite Agent-Welcome.
       Non viene mai compilato durante il bootstrap progetto standard (OP-1-4).

Agent-Welcome legge project-profile.md e sostituisce i tre placeholder:
  {{NOME_PROGETTO}}       — da project_name in project-profile.md
  {{VERSIONE_FRAMEWORK}}  — versione corrente del framework (es. v1.10.3)
  {{PROFILO_UTENTE}}      — righe * **<categoria>**: <testo> del profilo utente

Richiede: framework_edit_mode: true + conferma esplicita "RIPRISTINA" dell'utente.
Owner: Agent-FrameworkDocs
-->

# Copilot Custom Instructions  {{NOME_PROGETTO}}

## Contesto Progetto

Leggi `.github/project-profile.md` prima di
qualsiasi operazione. E la source of truth per
nome, stack tecnico e architettura del progetto.
Non usare valori hardcoded in questo file come
riferimento al progetto corrente.

Se `initialized: false`: NON interrompere l'operazione.
Aggiungi in testa alla tua risposta questo avviso,
prima di qualsiasi altro contenuto:

***
Avvertimento: PROGETTO NON INIZIALIZZATO
Framework non configurato. Per abilitare tutte le funzionalita:
scrivi `#project-setup` in chat, oppure seleziona Agent-Welcome e scrivi "nuovo progetto".
Puoi continuare a usare il framework normalmente.
***

Poi prosegui normalmente con il task richiesto.

## Framework Copilot {{VERSIONE_FRAMEWORK}}

**Questo progetto utilizza un framework orchestrazione Copilot con agenti nativi VS Code.**

### Quick Start (3 passi)

1. **Seleziona agente**: dal dropdown agenti nella chat di VS Code (`.github/agents/`)
2. **Scopri gli agenti**: [.github/agents/Agent-NAME.md](agents/) per la specifica di ciascuno

### Componenti Framework

| Componente | Scopo |
|-----------|-------|
| **`.github/agents/*.md`** | 14 agenti nativi VS Code |
| **`.github/skills/*.skill.md`** | Abilita atomiche riutilizzabili |
| **`.github/instructions/*.instructions.md`** | Regole contestuali per filetype |
| **`.github/prompts/*.md`** | Entry point e workflow |

Dettaglio completo: vedi `.github/AGENTS.md`

### Gli Agenti

14 agenti disponibili nel dropdown VS Code. Ruoli, trigger e deliverable:
vedi `.github/AGENTS.md`

### Comandi Entry Point

| Comando testuale | Metodo nativo VS Code |
|-----------------|----------------------|
| `/init <task>` | `#init.prompt.md` |
| `#orchestrate` | `#orchestrate.prompt.md` |
| `#framework-unlock` | `#framework-unlock.prompt.md` |
| `#verbosity` | `#verbosity.prompt.md` |
| `#personality` | `#personality.prompt.md` |
| `/Agent-<Name>` | Seleziona dal dropdown agenti VS Code |

Lista completa comandi: vedi `.github/AGENTS.md` sezione Prompt Files

---

## Dual-Track Documentation

Framework: Agent-FrameworkDocs gestisce `.github/**` e `FRAMEWORK_CHANGELOG.md`.
Progetto: Agent-Docs gestisce `CHANGELOG.md`, `docs/API.md`, `docs/ARCHITECTURE.md`.
Regola invariante: i due scope non si incrociano mai.
Dettaglio: vedi `.github/AGENTS.md` sezione Dual-Track Documentation

---

## Script di Supporto

Script di supporto in `scripts/` per automazione git, validation, changelog, build e scaffolding.
Dettaglio completo: vedi `.github/AGENTS.md` sezione Script di Supporto.
Per operazioni git, delega ad Agent-Git.

---

## Profilo Utente e Interazione

{{PROFILO_UTENTE}}

---

## Architettura e Standard di Codifica

### Clean Architecture (Summary)

4 Layer: Presentation, Application, Domain, Infrastructure

Regole dettagliate per layer, naming, type hints, logging, error
handling e accessibilita sono nelle instructions contestuali:

- Python standards: `.github/instructions/python.instructions.md`
  (attivo automaticamente su tutti i file `*.py`)
- Test standards: `.github/instructions/tests.instructions.md`
  (attivo automaticamente su `tests/**/*.py`)
- Domain rules: `.github/instructions/domain.instructions.md`
  (attivo automaticamente su `src/domain/**/*.py`)
- UI wxPython: `.github/instructions/ui.instructions.md`
  (attivo automaticamente su `src/presentation/**/*.py`)
- Istruzioni progetto: `.github/instructions/project.instructions.md`
  (generato da Agent-Welcome OP-4 livello 3 — non sempre presente)

Skills riutilizzabili tra agenti: lista completa in `.github/AGENTS.md`
(sezione Agent Skills) e `.github/skills/README.md`.

---

## Documentazione e Workflow Operativo

Regole TODO gate, pre-commit checklist, sync docs e feedback strutturato:
vedi `.github/instructions/workflow-standard.instructions.md` (applyTo: `**`)

Struttura DESIGN/PLAN/TODO e frontmatter:
vedi `.github/skills/document-template.skill.md`

---

## Testing

Vedi `.github/instructions/tests.instructions.md` per coverage minima,
markers, naming pattern e regole CI-safe.

---

## Convenzioni Git

Formato commit, branch policy, SemVer e release steps:
vedi `.github/skills/conventional-commit.skill.md`
vedi `.github/instructions/git-policy.instructions.md`
vedi `.github/skills/semver-bump.skill.md`

---

## Git Policy (Summary)

Copilot NON esegue direttamente: `git push`, `git merge` su main,
`git commit` in implementazioni automatizzate. Propone i comandi come
testo. Read-only sempre consentito: `git log`, `git diff`, `git status`.

| Contesto autorizzato | Modalita |
|---|---|
| Agent-Git | Unico agente con `run_in_terminal` su git |
| `#git-commit.prompt.md` | Dispatcher, delega ad Agent-Git |
| `#git-merge.prompt.md` | Dispatcher, delega ad Agent-Git |

In qualsiasi altro contesto il blocco e assoluto.

Policy completa: vedi `.github/instructions/git-policy.instructions.md`
e `.github/skills/git-execution.skill.md`

---

## Model Policy

Regole di selezione modello per tutti gli agenti del framework.
Dettaglio completo in:
vedi `.github/instructions/model-policy.instructions.md` (applyTo: `.github/**`)

---

## Referimenti Rapidi

| Risorsa | Scopo |
|---------|-------|
| [docs/WORKFLOW.md](../docs/WORKFLOW.md) | E2E workflow |
| [docs/CI_AUTOMATION.md](../docs/CI_AUTOMATION.md) | CI locale |
| [.vscode/copilot-quick-start.md](../.vscode/copilot-quick-start.md) | Commands (5 min) |
