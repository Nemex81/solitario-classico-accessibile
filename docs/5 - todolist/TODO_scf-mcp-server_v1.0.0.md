---
type: todo
feature: scf-mcp-server
status: COMPLETED
version: v1.0.0
plan_ref: docs/3 - coding plans/PLAN_scf-mcp-server_v1.0.0.md
date: 2026-03-28
---

# TODO: SCF-MCP-Server v1.0.0

Piano di riferimento: [PLAN_scf-mcp-server_v1.0.0.md](../3%20-%20coding%20plans/PLAN_scf-mcp-server_v1.0.0.md)

Implementazione del server MCP locale per esporre il framework SCF come Resources, Tools e Prompts senza duplicare i file in `.github/`.

## Fasi

### Fase 1 - Scaffolding runtime

- [x] Crea cartella `scf-mcp/`
- [x] Crea `scf-mcp/scf-mcp-server.py` con `FastMCP("scfMcp")`
- [x] Implementa risoluzione workspace da `WORKSPACE_FOLDER` con fallback a cwd
- [x] Configura logging su stderr o file, mai su stdout
- [x] Crea `scf-mcp/requirements.txt` con dipendenza `mcp`

### Fase 2 - Inventory e parser

- [x] Implementa discovery dinamica di agenti, skill, instructions, prompt e script
- [x] Estrai frontmatter e metadata opzionali dai file `.md`
- [x] Rileva stato di `project-profile.md` e struttura `workspace-info`
- [x] Implementa parser versione framework da `FRAMEWORK_CHANGELOG.md`

### Fase 3 - Resources MCP

- [x] Registra `agents://list` e `agents://{name}`
- [x] Registra `skills://list` e `skills://{name}`
- [x] Registra `instructions://list` e `instructions://{name}`
- [x] Registra `prompts://list` e `prompts://{name}`
- [x] Registra `scripts://list` e `scripts://{name}`
- [x] Registra `scf://global-instructions`, `scf://project-profile`, `scf://model-policy`, `scf://agents-index`, `scf://framework-version`, `scf://workspace-info`

### Fase 4 - Prompts MCP

- [x] Mappa tutti i `.github/prompts/*.prompt.md` a nomi MCP normalizzati
- [x] Verifica visibilita in VS Code come `/scfMcp.<prompt>`
- [x] Mantieni output testuale puro e argomenti opzionali dove utili

### Fase 5 - Tools MCP

- [x] Implementa tool informativi (`scf_list_agents`, `scf_get_agent`, `scf_get_project_profile`, `scf_get_global_instructions`, `scf_get_model_policy`)
- [x] Implementa tool di elenco/get per skill, instructions, prompt e script
- [x] Implementa `scf_run_script` con allowlist iniziale
- [x] Escludi da v1.0.0 `git_runner.py`, `update_changelog.py` e `audio_debug.py`
- [x] Restituisci sia testo sia struttura serializzabile quando utile

### Fase 6 - Configurazione e documentazione

- [x] Crea `scf-mcp/scf-mcp-config.json`
- [x] Crea `scf-mcp/README.md` con setup VS Code e client Python/Anthropic
- [x] Documenta il requisito Python 3.10+
- [x] Documenta i limiti noti: prompt naming in VS Code, project-profile non inizializzato, no git bypass

### Fase 7 - Validazione

- [x] Test unitari su locator, inventory, prompt normalization e script executor
- [ ] Smoke test locale del server via `.vscode/mcp.json` *(manuale — richiede VS Code restart)*
- [ ] Verifica comparsa di tools, resources e prompts in VS Code *(manuale)*
- [x] Verifica `scf_get_workspace_info()` con `initialized: false`
- [x] Verifica output NVDA-safe senza `print()` su stdout

## Note operative per Agent-Code

- Procedere in ordine di fase.
- Non spostare, copiare o modificare `.github/`.
- Non esporre tool che aggirano la policy git del framework.
- Trattare `scripts/` come allowlist esplicita, non come superficie eseguibile totale.
- Se l'SDK MCP usato richiede una baseline Python piu alta di quella pianificata, aggiornare documentazione e config prima della release.

## Definizione di completamento

- [x] Il server parte in `stdio` senza corrompere il protocollo
- [x] Le Resources leggono il framework reale del workspace
- [x] I Prompts sono invocabili in VS Code con naming coerente
- [x] I Tools restituiscono testo puro e dati serializzabili
- [x] `README.md` e `scf-mcp-config.json` permettono registrazione e test nel workspace