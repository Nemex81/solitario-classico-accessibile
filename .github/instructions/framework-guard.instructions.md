---
applyTo: "**"
---

# Framework Guard — Protezione Componenti Framework

## Priorita

Questa instruction prevale su qualsiasi altra instruction quando il task
richiede scrittura su un path protetto del framework.

## Path protetti

- `.github/copilot-instructions.md`
- `.github/project-profile.md`
- `.github/instructions/**`
- `.github/prompts/**`
- `.github/skills/**`
- `.github/agents/**`
- `.github/AGENTS.md`
- `.github/FRAMEWORK_CHANGELOG.md` (solo in scrittura non autorizzata)

## Regola generale

Prima di creare o modificare un path protetto, leggi `framework_edit_mode`
in `.github/project-profile.md`.

- Se `framework_edit_mode: false`: blocca la modifica e indirizza l'utente
  al prompt `#framework-unlock`.
- Se `framework_edit_mode: true`: procedi solo entro il perimetro di file
  e modifiche dichiarato nella richiesta autorizzata.

Questa instruction non autorizza mai lo sblocco autonomo del flag.
