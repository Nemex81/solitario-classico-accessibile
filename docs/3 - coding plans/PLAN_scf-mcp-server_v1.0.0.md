---
type: plan
feature: scf-mcp-server
agent: Agent-Plan
status: READY
version: v1.0.0
design_ref: N/A - piano tecnico richiesto senza DESIGN separato
date: 2026-03-28
---

# Plan: SCF-MCP-Server v1.0.0

## Executive Summary

Tipo iniziativa: nuova capability runtime locale per il framework SCF.

Verdetto validazione: **PASSA con normalizzazioni obbligatorie**.

Normalizzazioni integrate in questo piano:

1. Requisito Python corretto da **3.8+** a **3.10+** in coerenza con la documentazione MCP Python corrente.
2. I prompt MCP in VS Code non appaiono come `/scf-init`, ma come `/<nome-server>.<nome-prompt>`; con server `scfMcp` il comando atteso sara ` /scfMcp.init`.
3. L'obiettivo "14 agenti selezionabili come tool" e realizzabile solo come **tool MCP rappresentativi del framework** o come prompt/resource correlate, non come sostituzione dei 14 agenti nativi VS Code gia definiti in `.github/agents/`.
4. `project-profile.md` e ancora non inizializzato (`initialized: false`): il server dovra esporre questo stato come dato, non tentare correzioni automatiche.

Branch suggerito: `feature/scf-mcp-server-v1.0.0`

Versione target: `v1.0.0`

Priorita: alta. L'iniziativa riduce il carico di contesto in chat e rende il framework consumabile da client MCP compatibili senza spostare o duplicare `.github/`.

---

## Problema e Obiettivo

### Problema

Il repository contiene gia un framework SCF articolato in agenti, skill, instructions, prompt file, template e script di supporto, ma oggi quel patrimonio e leggibile solo come file locali e non come capabilities MCP on-demand. Questo comporta tre limiti:

1. I client AI devono caricare piu contesto del necessario.
2. I prompt file e le policy del framework non sono esposti come risorse e prompt MCP standard.
3. Gli script di supporto restano invocabili solo localmente, senza un layer controllato di accesso da client MCP.

### Obiettivo

Progettare un server MCP locale in `scf-mcp/` che:

1. Legga dinamicamente il framework da `.github/` nel workspace attivo.
2. Esponga Resources, Tools e Prompts coerenti con cio che esiste davvero nel repository.
3. Produca solo output testuale puro, compatibile con NVDA e terminale integrato di VS Code.
4. Rimanga completamente separato da `.github/` e da `scripts/`, trattando quei contenuti come dati e utility esterne.

---

## Inventario Framework Rilevato

### Struttura `.github/`

Inventario verificato al 2026-03-28:

- `.github/agents/` contiene 14 agenti piu `README.md`
- `.github/instructions/` contiene 11 instructions piu `README.md`
- `.github/prompts/` contiene 17 prompt file piu `README.md`
- `.github/skills/` contiene 25 skill piu `README.md`
- `.github/templates/` contiene 13 template
- `.github/workflows/` contiene `ci.yml` e `assistant-commit.yml`
- `.github/scripts/` esiste ma risulta vuota
- file radice rilevanti: `AGENTS.md`, `copilot-instructions.md`, `FRAMEWORK_CHANGELOG.md`, `project-profile.md`, `README.md`

### Agenti rilevati

Indice ufficiale da `AGENTS.md` e file in `.github/agents/`:

1. `Agent-Helper` - consulenza read-only sul framework
2. `Agent-Welcome` - setup e manutenzione `project-profile.md`
3. `Agent-Orchestrator` - coordinamento E2E
4. `Agent-Analyze` - discovery read-only
5. `Agent-Design` - DESIGN documentale
6. `Agent-Plan` - PLAN e TODO
7. `Agent-CodeRouter` - routing GUI vs non-GUI
8. `Agent-Code` - implementazione non-GUI
9. `Agent-CodeUI` - implementazione GUI accessibile
10. `Agent-Validate` - test e quality gates
11. `Agent-Docs` - sync documentazione progetto
12. `Agent-Release` - versioning e release
13. `Agent-FrameworkDocs` - documentazione framework `.github/`
14. `Agent-Git` - unico agente con esecuzione git autorizzata

Assegnazioni modello rilevanti da `model-policy.instructions.md`:

- reasoning/orchestrazione: GPT-5.4 o Claude Opus 4.6
- analisi/design/planning: Claude Sonnet 4.6
- coding e review: Claude Sonnet 4.6
- validate/refactor pipeline: GPT-5.3-Codex
- task meccanici: GPT-5 mini o Raptor mini

Nota inventario: `Agent-Welcome` e `Agent-Helper` sono presenti nel framework ma non compaiono nella tabella assegnazioni di `model-policy.instructions.md`; il server dovra gestire tale assenza senza trattarla come errore.

### Skills rilevate

Skills presenti:

- `accessibility-output`
- `agent-selector`
- `changelog-entry`
- `clean-architecture-rules`
- `code-routing`
- `conventional-commit`
- `docs_manager`
- `document-template`
- `error-recovery`
- `file-deletion-guard`
- `framework-guard`
- `framework-index`
- `framework-query`
- `framework-scope-guard`
- `git-execution`
- `personality`
- `project-doc-bootstrap`
- `project-profile`
- `project-reset`
- `rollback-procedure`
- `semantic-gate`
- `semver-bump`
- `style-setup`
- `validate-accessibility`
- `verbosity`

### Instructions rilevate

- `domain.instructions.md` - `src/domain/**/*.py`
- `framework-guard.instructions.md` - `**`
- `git-policy.instructions.md` - `**`
- `model-policy.instructions.md` - `.github/**`
- `personality.instructions.md` - `.github/**`
- `project-reset.instructions.md` - `.github/**`
- `python.instructions.md` - `**/*.py`
- `tests.instructions.md` - `tests/**/*.py`
- `ui.instructions.md` - `src/presentation/**/*.py`
- `verbosity.instructions.md` - `.github/**`
- `workflow-standard.instructions.md` - `**`

### Prompt file rilevati

Prompt presenti:

- `framework-changelog.prompt.md`
- `framework-release.prompt.md`
- `framework-unlock.prompt.md`
- `framework-update.prompt.md`
- `git-commit.prompt.md`
- `git-merge.prompt.md`
- `help.prompt.md`
- `init.prompt.md`
- `orchestrate.prompt.md`
- `personality.prompt.md`
- `project-setup.prompt.md`
- `project-update.prompt.md`
- `release.prompt.md`
- `start.prompt.md`
- `status.prompt.md`
- `sync-docs.prompt.md`
- `verbosity.prompt.md`

### Template e workflow rilevati

Template di interesse per la progettazione:

- `project-profile.template.md`
- `coding_plan.md`
- `todo_task.md`
- `todo_coordinator.md`
- `design.md`
- `api.md`
- `architecture.md`
- `changelog.md`

Workflow rilevati:

- `ci.yml`
- `assistant-commit.yml`

### Stato progetto framework

`project-profile.md` e non inizializzato:

- `initialized: false`
- campi di stack e identita vuoti
- `framework_edit_mode: false`
- `verbosity: collaborator`
- `personality: pragmatico`

Questo non blocca il server MCP, ma impone che i tool espongano chiaramente lo stato di inizializzazione come parte del risultato.

### Script Python rilevati in `scripts/`

Script applicativi/framework disponibili:

- `audio_debug.py`
- `build-release.py`
- `ci-local-validate.py`
- `create-project-files.py`
- `detect_agent.py`
- `generate-changelog.py`
- `git_runner.py`
- `sync-documentation.py`
- `update_changelog.py`
- `validate_gates.py`

Vincoli osservati:

1. Non tutti gli script hanno una CLI robusta con `argparse`.
2. `audio_debug.py` e `update_changelog.py` richiedono wrapping difensivo per essere esposti via MCP.
3. `git_runner.py` non deve essere esposto come scorciatoia per bypassare la policy git; se mappato, dovra restare fuori dal primo scope implementativo.

---

## Architettura del Server MCP

### Principi

1. Nessuna copia dei file in `.github/`.
2. Discovery dinamica di agenti, skill, instructions, prompt, template e script.
3. Solo trasporto `stdio`.
4. Nessun output su stdout fuori dal protocollo MCP; logging solo su stderr o file.
5. Errori sempre restituiti in testo leggibile e, quando utile, anche in forma strutturata serializzabile.

### Componenti principali

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class WorkspaceContext:
    """Resolve and expose the active workspace and all SCF-relevant roots."""

    workspace_root: Path
    github_root: Path
    scripts_root: Path
    scf_mcp_root: Path


@dataclass(frozen=True)
class FrameworkFile:
    """Describe a discovered SCF file and the metadata extracted from it."""

    name: str
    path: Path
    category: str
    summary: str
    metadata: dict[str, Any]


class WorkspaceLocator:
    """Resolve WORKSPACE_FOLDER with fallback to cwd and validate required folders."""

    def resolve(self) -> WorkspaceContext: ...


class FrameworkInventory:
    """Discover framework files under .github/ and scripts/ without hardcoded assumptions."""

    def list_agents(self) -> list[FrameworkFile]: ...
    def list_skills(self) -> list[FrameworkFile]: ...
    def list_instructions(self) -> list[FrameworkFile]: ...
    def list_prompts(self) -> list[FrameworkFile]: ...
    def list_scripts(self) -> list[FrameworkFile]: ...
    def get_project_profile(self) -> FrameworkFile | None: ...
    def get_global_instructions(self) -> FrameworkFile | None: ...
    def get_model_policy(self) -> FrameworkFile | None: ...
    def get_agents_index(self) -> FrameworkFile | None: ...
    def get_framework_version(self) -> str: ...


class ScriptExecutor:
    """Run selected scripts from scripts/ with allowlist, timeout and NVDA-safe text output."""

    def run(self, script_name: str, args: list[str]) -> dict[str, Any]: ...


class PromptCatalog:
    """Map .prompt.md files to MCP prompt names and build prompt payloads on demand."""

    def list_prompts(self) -> list[FrameworkFile]: ...
    def get_prompt(self, name: str, arguments: dict[str, str] | None = None) -> dict[str, Any]: ...


class ScfMcpApplication:
    """Register MCP resources, prompts and tools over FastMCP using workspace-driven discovery."""

    def register_resources(self) -> None: ...
    def register_prompts(self) -> None: ...
    def register_tools(self) -> None: ...
```

### Mapping resources -> repository reale

Resources da implementare nel primo rilascio:

- `agents://list` -> inventario da `.github/agents/*.md`
- `agents://{name}` -> file agente specifico
- `skills://list` -> inventario da `.github/skills/*.skill.md`
- `skills://{name}` -> skill specifica
- `instructions://list` -> inventario da `.github/instructions/*.instructions.md`
- `instructions://{name}` -> instruction specifica
- `prompts://list` -> elenco `.github/prompts/*.prompt.md`
- `prompts://{name}` -> contenuto prompt specifico
- `scripts://list` -> indice script in `scripts/`
- `scripts://{name}` -> scheda script con path, descrizione e note CLI
- `scf://global-instructions` -> `.github/copilot-instructions.md`
- `scf://project-profile` -> `.github/project-profile.md`
- `scf://model-policy` -> `.github/instructions/model-policy.instructions.md`
- `scf://agents-index` -> `.github/AGENTS.md`
- `scf://framework-version` -> valore estratto da `.github/FRAMEWORK_CHANGELOG.md`
- `scf://workspace-info` -> stato workspace, path, initialized, inventory summary

### Mapping tools -> repository reale

Tool v1.0.0 consigliati:

1. `scf_list_agents()`
2. `scf_get_agent(name: str)`
3. `scf_get_project_profile()`
4. `scf_get_global_instructions()`
5. `scf_get_model_policy()`
6. `scf_list_skills()`
7. `scf_get_skill(name: str)`
8. `scf_list_instructions()`
9. `scf_get_instruction(name: str)`
10. `scf_list_prompts()`
11. `scf_get_prompt(name: str)`
12. `scf_list_scripts()`
13. `scf_run_script(script_name: str, args: list[str])`
14. `scf_get_framework_version()`
15. `scf_get_workspace_info()`

Scelta di scope: non creare nel primo rilascio 14 tool distinti, uno per agente. Il tools picker di Copilot mostrera i tool MCP del server; per rappresentare gli agenti SCF senza introdurre un catalogo artificiale di tool vuoti, e preferibile partire con tool informativi e, in una fase successiva, valutare wrapper per agent-profile o task presets.

### Mapping prompts -> repository reale

Regola MCP/VS Code da rispettare:

- nome server suggerito: `scfMcp`
- prompt MCP suggeriti: `init`, `projectSetup`, `projectUpdate`, `orchestrate`, `status`, `start`, `release`, `syncDocs`, `gitCommit`, `gitMerge`, `frameworkUnlock`, `frameworkUpdate`, `frameworkChangelog`, `frameworkRelease`, `verbosity`, `personality`, `help`

In VS Code i prompt compariranno come:

- `/scfMcp.init`
- `/scfMcp.gitCommit`
- `/scfMcp.frameworkUnlock`

Non come `/scf-init`.

### Regole per `scf_run_script`

Allowlist iniziale consigliata:

- `detect_agent.py`
- `validate_gates.py`
- `ci-local-validate.py`
- `generate-changelog.py`
- `sync-documentation.py`
- `create-project-files.py`

Fuori scope v1.0.0:

- `git_runner.py` per evitare conflitti con git-policy del framework
- `update_changelog.py` finche non riceve una CLI stabile
- `audio_debug.py` finche non riceve una CLI stabile e output piu standardizzato

---

## File Coinvolti

### CREATE

- `scf-mcp/scf-mcp-server.py` - entry point FastMCP e registrazione capabilities
- `scf-mcp/scf-mcp-config.json` - configurazione esportabile per `.vscode/mcp.json`
- `scf-mcp/requirements.txt` - dipendenze runtime del server
- `scf-mcp/README.md` - installazione, uso, limiti, test

### MODIFY

- `.vscode/mcp.json` - opzionale, solo se l'utente sceglie di registrare il server nel workspace

### DELETE

- nessuno

---

## Sequenza di Implementazione Consigliata

### Fase 1 - Scaffolding e risoluzione workspace

Obiettivo: creare `scf-mcp/` con entry point minimo e risoluzione robusta del workspace.

Attivita:

1. Creare `scf-mcp/scf-mcp-server.py` con `FastMCP("scfMcp")`.
2. Implementare `WorkspaceLocator` con priorita `WORKSPACE_FOLDER`, fallback `Path.cwd()`.
3. Validare l'esistenza di `.github/` e `scripts/`.
4. Portare logging su stderr o file, mai su stdout.

Dipendenze: nessuna.

### Fase 2 - Discovery dinamica del framework

Obiettivo: costruire `FrameworkInventory` e parser minimi per metadata.

Attivita:

1. Inventariare agenti, skill, instructions, prompt e script.
2. Estrarre summary, frontmatter, `applyTo`, modelli e note git quando presenti.
3. Implementare fallback puliti per file mancanti o metadata assenti.
4. Esporre `scf://workspace-info` e `scf://framework-version`.

Dipendenze: Fase 1.

### Fase 3 - Resources MCP

Obiettivo: esporre risorse leggibili on-demand.

Attivita:

1. Registrare resource list e resource get per agenti, skill, instructions, prompt e documenti globali.
2. Usare URI stabili, testuali e deterministicamente derivabili dai nomi file.
3. Garantire che tutti i contenuti siano plain text UTF-8.

Dipendenze: Fase 2.

### Fase 4 - Prompts MCP

Obiettivo: mappare `.github/prompts/*.prompt.md` in prompt MCP nativi.

Attivita:

1. Normalizzare i nomi in camelCase senza suffissi `.prompt.md`.
2. Restituire messaggi MCP con testo puro e, se utile, risorse embedded.
3. Mantenere il contenuto sorgente leggibile e tracciabile.

Dipendenze: Fase 2.

### Fase 5 - Tools MCP

Obiettivo: esporre tool informativi e di esecuzione controllata.

Attivita:

1. Registrare i tool dell'inventario e di introspezione progetto.
2. Implementare `scf_run_script` con allowlist, timeout, cattura stdout/stderr e ritorno strutturato.
3. Aggiungere output `structuredContent` dove utile, mantenendo anche un blocco text per compatibilita client.

Dipendenze: Fase 2.

### Fase 6 - Configurazione, documentazione e test

Obiettivo: rendere il server installabile e verificabile nel workspace.

Attivita:

1. Scrivere `scf-mcp-config.json`.
2. Scrivere `README.md` con setup Windows/VS Code e uso da client Python/Anthropic.
3. Validare avvio stdio, discovery tool, prompt list e resource list.
4. Testare almeno un tool informativo e un tool scriptato.

Dipendenze: Fasi 3, 4, 5.

---

## Firme e Docstring Proposte

```python
def resolve_workspace_root() -> Path:
    """Return the active workspace root using WORKSPACE_FOLDER or cwd fallback."""


def parse_markdown_frontmatter(content: str) -> dict[str, Any]:
    """Parse optional YAML frontmatter and return normalized metadata."""


def extract_framework_version(changelog_path: Path) -> str:
    """Extract the latest framework version label from FRAMEWORK_CHANGELOG.md."""


def normalize_prompt_name(filename: str) -> str:
    """Convert a .prompt.md filename into a stable MCP prompt name for VS Code clients."""


def build_workspace_info(context: WorkspaceContext, inventory: FrameworkInventory) -> dict[str, Any]:
    """Assemble a structured summary of workspace paths, initialization state and discovered SCF assets."""


async def scf_list_agents() -> dict[str, Any]:
    """Return all discovered agents with role, model and git-related notes when available."""


async def scf_get_agent(name: str) -> dict[str, Any]:
    """Return the full normalized metadata and source content for one SCF agent file."""


async def scf_get_project_profile() -> dict[str, Any]:
    """Return project-profile metadata and explicit initialized=false fallback information."""


async def scf_run_script(script_name: str, args: list[str] | None = None) -> dict[str, Any]:
    """Execute an allowlisted script from scripts/ and return NVDA-safe text plus structured result fields."""
```

---

## Contenuto Esatto di `scf-mcp-config.json`

Configurazione minima validata per `.vscode/mcp.json`:

```json
{
  "servers": {
    "scfMcp": {
      "type": "stdio",
      "command": "python",
      "args": [
        "${workspaceFolder}/scf-mcp/scf-mcp-server.py"
      ],
      "env": {
        "WORKSPACE_FOLDER": "${workspaceFolder}"
      }
    }
  }
}
```

Note operative:

1. Se il progetto usa un interprete virtualenv dedicato, `command` puo essere sostituito con il path assoluto al Python dell'ambiente.
2. Su Windows, `${workspaceFolder}` e supportato da VS Code nel file `mcp.json`.
3. Sandboxing non e disponibile su Windows e quindi non entra nel piano v1.0.0.

---

## Installazione, Registrazione e Verifica

### Installazione suggerita

1. Creare una virtualenv dedicata per `scf-mcp/` oppure riusare l'ambiente Python del workspace.
2. Installare `mcp` in versione compatibile con FastMCP.
3. Verificare che l'interprete selezionato sia Python 3.10+.

### Registrazione workspace VS Code

1. Creare o aggiornare `.vscode/mcp.json` con la configurazione sopra.
2. Avviare o riavviare il server da MCP: List Servers.
3. Confermare il trust del server locale quando richiesto.

### Verifiche minime

1. Il server parte senza scrivere log su stdout.
2. In chat compaiono i tool MCP del server `scfMcp`.
3. In Add Context > MCP Resources compaiono le resources `agents://`, `skills://`, `instructions://`, `prompts://`, `scf://`.
4. I prompt sono richiamabili come `/scfMcp.<prompt>`.
5. `scf_get_workspace_info()` restituisce `initialized: false` nel repository corrente.
6. `scf_run_script("detect_agent.py", ["aggiungi validazione documentale"])` produce output solo testuale e serializzabile.

---

## Test Plan

### Unit e integration target

1. Test su `WorkspaceLocator` per `WORKSPACE_FOLDER` presente e fallback a cwd.
2. Test su `FrameworkInventory` per discovery corretta di agenti, skill, instructions, prompt e script.
3. Test su parsing frontmatter e campi opzionali mancanti.
4. Test su `normalize_prompt_name` con nomi reali del repository.
5. Test su `ScriptExecutor` con script allowlisted, script non allowlisted e timeout.
6. Smoke test manuale del server in VS Code via `.vscode/mcp.json`.

### Rischi e vincoli

1. L'SDK MCP Python corrente richiede Python 3.10+: questo invalida il requisito 3.8+ del testo sorgente.
2. Il repository contiene prompt file non del tutto omogenei nel frontmatter; il server dovra leggerli come dati e non affidarsi a un solo formato.
3. `FRAMEWORK_CHANGELOG.md` e `AGENTS.md` non esprimono esattamente la stessa label di versione finale; il parser versione dovra privilegiare la sorgente scelta in modo esplicito.
4. Il server non deve creare scorciatoie per aggirare `git-policy.instructions.md`.

---

## Esito Finale della Validazione

Il piano e **validato e salvabile** perche:

1. L'architettura proposta e coerente con il framework effettivamente presente nel repository.
2. VS Code supporta server MCP locali via `.vscode/mcp.json` con `type`, `command`, `args` ed `env`.
3. MCP supporta nativamente Resources, Tools e Prompts per questo caso d'uso.
4. Le discrepanze individuate sono state normalizzate nel piano e non bloccano la fase successiva di implementazione.

Questo documento e quindi pronto come base per la fase di coding successiva.