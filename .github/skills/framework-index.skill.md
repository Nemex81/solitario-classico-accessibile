---
name: framework-index
description: >
  Sequenza di lettura e formato output per costruire una panoramica
  completa del Framework Copilot da fonti interne. Riutilizzabile da
  Agent-Helper e Agent-Orchestrator.
---

# Skill: Framework Index

## Sequenza di lettura obbligatoria

Eseguire nell'ordine. Non saltare passi.

1. `.github/AGENTS.md` — versione framework, conteggio, registro ufficiale agenti
2. `.github/agents/README.md` — tabella agenti con scopo sintetico
3. `.github/prompts/README.md` — tabella prompt con trigger
4. `.github/skills/README.md` — tabella skill con agenti che le usano
5. `.github/copilot-instructions.md` — contesto globale, entry point, convenzioni
6. `.github/project-profile.md` — profilo progetto e vincoli tecnici

## Formato indice navigabile (output obbligatorio)

### Agenti disponibili
<nome> — <scopo in una riga> — <modalità: read-only/operativo/coordinamento>
(una riga per agente, ordine alfabetico)

### Prompt disponibili
<nome> — <trigger o scenario d'uso>
(una riga per prompt, ordine alfabetico)

### Skill disponibili
<nome> — <funzione> — usata da: <lista agenti>
(una riga per skill, ordine alfabetico)

### Versione framework
Versione: <vX.Y.Z> — Agenti: <N> — Prompt: <N> — Skill: <N>
