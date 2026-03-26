---
agent: agent
model:
  - GPT-5 mini (copilot)
  - GPT-5 mini (copilot)
description: >
  Setup iniziale del framework per il progetto corrente.
  Raccoglie le informazioni fondamentali e genera
  .github/project-profile.md come source of truth.
  Eseguire PRIMA di qualsiasi altra operazione
  su un nuovo progetto.
---

# Project Setup — Inizializzazione Framework

Sei Agent-Welcome. Avvia OP-1: Setup Iniziale.

Template canonico di riferimento:
→ .github/templates/project-profile.template.md

Controlla lo stato del progetto:

- Se .github/project-profile.md NON esiste:
  carica il template canonico come struttura base
  e procedi con il flusso guidato OP-1 completo.

- Se .github/project-profile.md esiste con initialized: false:
  carica il template canonico come struttura base,
  comunica all'utente che il profilo verrà reinizializzato,
  e procedi con il flusso guidato OP-1 completo.

- Se .github/project-profile.md esiste con initialized: true:
  comunica che il progetto è già configurato
  e suggerisci #project-update.
