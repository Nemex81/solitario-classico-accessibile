---
name: Sync Documentazione
description: >
  Avvia Agent-Docs per sincronizzare API.md, ARCHITECTURE.md, CHANGELOG.md.
---

Avvia Agent-Docs per sincronizzare la documentazione dopo i commit recenti.

Contesto da analizzare:
- File modificati: ${input:Elenca i file .py modificati (separati da virgola)}
- Tipo di modifica: ${input:Tipo (feat/fix/refactor)}
- Versione target: ${input:Versione (es: v3.6.0)}

Segui la Sync Strategy definita in .github/agents/Agent-Docs.md.
Produci al termine la Sync Checklist con stato di ogni documento.
