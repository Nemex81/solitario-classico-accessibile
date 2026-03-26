---
agent: agent
model:
  - GPT-5 mini (copilot)
  - GPT-5 mini (copilot)
description: >
  Aggiorna uno o più campi del profilo progetto.
  Se non specifichi cosa aggiornare, Agent-Welcome
  mostra un help con esempi d'uso.
argument-hint: "update_request — Cosa vuoi aggiornare nel profilo progetto? (opzionale — lascia vuoto per vedere il help)"
---

# Project Update — Aggiornamento Profilo Progetto

Sei Agent-Welcome. Avvia OP-2: Aggiornamento Profilo.

Input ricevuto: ${input:update_request}

Se l'input è vuoto o non specificato:
mostra il blocco help di OP-2 prima di procedere.
Se l'input contiene una richiesta specifica:
procedi direttamente con OP-2 per i campi indicati.
