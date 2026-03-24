---
name: agent-selector
description: >
  Pattern matching deterministico per selezionare l'agente corretto
  dato un task o una domanda. Prima regola che corrisponde vince.
  Riutilizzabile da Agent-Helper e Agent-Orchestrator.
---

# Skill: Agent Selector

## Regola primaria

Analizza il testo del task o della domanda utente.
Applica i pattern nell'ordine indicato. Prima corrispondenza vince.

## Pattern → Agent-Helper

Corrisponde se il testo contiene:
- "come funziona", "cosa fa", "spiegami", "qual è la differenza"
- "quali agenti", "quali tool", "quando uso", "come si attiva"
- "struttura del framework", "panoramica framework"

## Pattern → Agent-Analyze

Corrisponde se il testo contiene:
- "analizza", "studia", "esplora", "trova dove", "cerca nel codice"
- "architettura", "dipendenze", "come funziona [componente progetto]"

## Pattern → Agent-Plan

Corrisponde se il testo contiene:
- "pianifica", "piano di lavoro", "task list", "fasi di sviluppo"
- "come implementare", "strategia per"

## Pattern → Agent-Design

Corrisponde se il testo contiene:
- "progetta", "design", "architettura da creare", "struttura da definire"
- "pattern da usare", "come strutturare"

## Pattern → Agent-Code / Agent-CodeUI

Corrisponde se il testo contiene keyword operative di implementazione.
Delegare a skill `code-routing` per la distinzione Code/CodeUI.

## Pattern → Agent-Git

Corrisponde se il testo contiene:
- "commit", "push", "branch", "merge", "tag", "git"

## Pattern → Agent-FrameworkDocs

Corrisponde se il testo contiene:
- "aggiorna framework", "aggiorna AGENTS.md", "aggiorna changelog framework"
- "aggiungi agente", "modifica agente"

## Pattern → Agent-Orchestrator

Corrisponde se il testo contiene:
- "esegui il workflow", "avvia il task", "coordina"
- Task complessi multi-agente non classificabili altrimenti

## Caso ambiguo

Se nessun pattern corrisponde o più pattern corrispondono con uguale peso:

```
ROUTING AMBIGUO
────────────────────────────────────────
Task: <testo utente>
Pattern rilevati: <lista>
Opzioni:
  A: <Agent-X> — motivo
  B: <Agent-Y> — motivo
Quale scegli?
────────────────────────────────────────
```
