---
name: Status Check
description: >
  Mostra lo stato attuale del workflow in corso.
---

Leggi i seguenti file e produci un report di stato:
- docs/TODO.md (progresso fasi)
- docs/3 - coding plans/ (PLAN attivi)
- docs/2 - projects/ (DESIGN attivi)

Formato output (testo piano, accessibile screen reader):

```
Workflow attivo: [nome task o "nessuno"]
Agente corrente: [Agent-X o "nessuno"]
Fase corrente: [N di M -- descrizione]
Fasi completate: [N]
Fasi rimanenti: [N]
Gate coverage: [% se disponibile o "non ancora eseguito"]
Prossimo step: [azione suggerita]
```

Se non c'e alcun workflow attivo, suggerisci di usare #init.prompt.md
per avviare un nuovo task.
