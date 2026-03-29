# SCF-MCP-Server

Server MCP locale che espone il framework SPARK Code Framework (SCF) in `.github/`
come Resources, Tools e Prompts consumabili da GitHub Copilot e client Anthropic.

Il server legge i file del framework dinamicamente — non copia nulla fuori da `.github/`.

---

## Requisiti

- Python 3.10 o superiore (richiesto dall'SDK MCP)
- Dipendenza runtime: `mcp` (include FastMCP)

---

## Installazione

```powershell
# Opzione A: riusa l'ambiente Python del workspace
pip install mcp

# Opzione B: virtualenv dedicata (consigliata)
python -m venv scf-mcp/.venv
scf-mcp/.venv/Scripts/activate
pip install mcp
```

Se si usa un virtualenv dedicato, sostituire `command` in `scf-mcp-config.json`
con il path assoluto all'interprete:

```json
"command": "C:/path/to/scf-mcp/.venv/Scripts/python.exe"
```

---

## Registrazione in VS Code

1. Aprire o creare `.vscode/mcp.json` nella radice del workspace.
2. Copiare il contenuto di `scf-mcp/scf-mcp-config.json` nel file.
3. Riavviare il server da: MCP: List Servers > scfMcp > Restart.
4. Confermare il trust del server locale quando VS Code lo richiede.

Contenuto da copiare in `.vscode/mcp.json`:

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

`${workspaceFolder}` e una variabile predefinita di VS Code, supportata su Windows.

---

## Uso da VS Code (GitHub Copilot)

### Tools

Dopo l'avvio il server espone 15 tool nel picker di Copilot:

```
scf_list_agents           scf_get_agent(name)
scf_list_skills           scf_get_skill(name)
scf_list_instructions     scf_get_instruction(name)
scf_list_prompts          scf_get_prompt(name)
scf_list_scripts          scf_run_script(script_name, args)
scf_get_project_profile   scf_get_global_instructions
scf_get_model_policy      scf_get_framework_version
scf_get_workspace_info
```

### Resources

Resources disponibili in Add Context > MCP Resources:

```
agents://list             agents://{name}
skills://list             skills://{name}
instructions://list       instructions://{name}
prompts://list            prompts://{name}
scripts://list            scripts://{name}
scf://global-instructions
scf://project-profile
scf://model-policy
scf://agents-index
scf://framework-version
scf://workspace-info
```

### Prompts

I prompt file di `.github/prompts/` sono disponibili come:

```
/scfMcp.init              /scfMcp.orchestrate
/scfMcp.projectSetup      /scfMcp.projectUpdate
/scfMcp.status            /scfMcp.start
/scfMcp.release           /scfMcp.syncDocs
/scfMcp.gitCommit         /scfMcp.gitMerge
/scfMcp.frameworkUnlock   /scfMcp.frameworkUpdate
/scfMcp.frameworkChangelog /scfMcp.frameworkRelease
/scfMcp.verbosity         /scfMcp.personality
/scfMcp.help
```

Il naming e: `/<nome-server>.<nomePromptCamelCase>`.

---

## Uso da client Python (Anthropic API)

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="python",
    args=["scf-mcp/scf-mcp-server.py"],
    env={"WORKSPACE_FOLDER": "/path/to/workspace"},
)

async def main() -> None:
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("scf_get_workspace_info", {})
            print(result)

asyncio.run(main())
```

---

## Script eseguibili tramite scf_run_script

Lista allowlistata per v1.0.0:

| Script | Descrizione |
|---|---|
| `detect_agent.py` | Suggerisce l'agente appropriato per un task |
| `validate_gates.py` | Valida struttura e frontmatter dei documenti |
| `ci-local-validate.py` | Esegue validazione CI in locale |
| `generate-changelog.py` | Genera voci di changelog |
| `sync-documentation.py` | Sincronizza la documentazione |
| `create-project-files.py` | Crea file progetto da template |

Script esclusi da v1.0.0: `git_runner.py`, `update_changelog.py`, `audio_debug.py`.

---

## Limiti noti

### Prompt naming in VS Code

I prompt MCP non appaiono come `/scf-init` ma come `/<nome-server>.<nomeCamelCase>`.
Con server `scfMcp`: `/scfMcp.init`, `/scfMcp.frameworkUnlock`, ecc.

### Project profile non inizializzato

Il repository ha `initialized: false` in `.github/project-profile.md`.
Il tool `scf_get_project_profile` e la resource `scf://project-profile` restituiscono
un avviso esplicito. Il server non tenta correzioni automatiche.
Per inizializzare: selezionare Agent-Welcome in VS Code e scrivere "nuovo progetto".

### Nessun bypass della policy git

`git_runner.py` non e nella allowlist di `scf_run_script`. Il server non espone
nessuna scorciatoia per aggirare `git-policy.instructions.md`.
Per operazioni git, usare Agent-Git tramite il dropdown agenti di VS Code.

### Output testuale puro

Tutti i tool e le resources producono solo testo UTF-8 o dict serializzabili.
Nessun `print()` su stdout: il flusso stdio e riservato al protocollo JSON-RPC MCP.

---

## Verifica post-installazione

1. Il server avvia senza errori su stderr relativi all'import MCP.
2. I 15 tool compaiono nel picker di Copilot.
3. `scf_get_workspace_info` restituisce `initialized: false` e i conteggi corretti.
4. `agents://list` mostra i 14 agenti SCF.
5. `/scfMcp.init` e invocabile in chat.
6. `scf_run_script("validate_gates.py", ["--check-structure"])` restituisce output
   di testo senza corrompere il protocollo.
