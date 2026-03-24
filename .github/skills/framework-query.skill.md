---
name: framework-query
description: >
  Contratto di output per Agent-Helper. Definisce come strutturare risposte
  descrittive, comparative e di workflow sul Framework Copilot.
  Non applicabile ad agenti operativi.
---

# Skill: Framework Query

## Pattern 1 — Risposta descrittiva (es. "cosa fa Agent-X")

Struttura output obbligatoria:

- Scopo: <una riga>
- Modalità: <read-only / operativo / coordinamento>
- Tool disponibili: <lista>
- Trigger di attivazione: <lista sintetica>
- Gate di completamento: <lista sintetica>
- Agenti correlati: <lista con relazione>

## Pattern 2 — Risposta comparativa (es. "differenza tra X e Y")

Struttura output obbligatoria:

- Intestazione: "Confronto: Agent-X vs Agent-Y"
- Tabella con righe: Scopo / Modalità / Tool / Trigger / Quando usare
- Raccomandazione finale: quale usare e in quale contesto

## Pattern 3 — Mappa di workflow (es. "come si fa X nel framework")

Struttura output obbligatoria:

- Intestazione: "Workflow: <descrizione task>"
- Sequenza agenti con frecce logiche:
  Agent-A → Agent-B → Agent-C
- Per ogni agente: output atteso e condizione di passaggio
- Nota finale: azione utente richiesta (se presente)

## Regola assenza documentazione

Se l'informazione richiesta non è presente nei file del framework:

```
INFORMAZIONE NON DISPONIBILE
────────────────────────────────────────
Query: <domanda utente>
Motivo: documentazione assente in .github/
Suggerimento: aggiornare [file pertinente] oppure consultare [agente pertinente]
────────────────────────────────────────
```

Non inferire mai contenuto non documentato.
