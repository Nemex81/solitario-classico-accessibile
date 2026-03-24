---
name: framework-scope-guard
description: >
  Limiti operativi e risposte standard per agenti read-only del framework.
  Importabile da tutti gli agenti con modalità read-only o consultiva.
---

# Skill: Framework Scope Guard

## Path autorizzati in lettura

- `.github/AGENTS.md`
- `.github/FRAMEWORK_CHANGELOG.md`
- `.github/README.md`
- `.github/copilot-instructions.md`
- `.github/project-profile.md`
- `.github/agents/*.md`
- `.github/prompts/*.md`
- `.github/skills/*.md`
- `.github/instructions/*.md`

## Azioni vietate (assolute)

- Creare file
- Modificare file
- Eliminare file
- Proporre o suggerire comandi git
- Leggere file fuori da `.github/`

## Risposte standard per richieste fuori scope

### Richiesta di modifica file:
```
OPERAZIONE NON CONSENTITA
────────────────────────────────────────
Azione richiesta: modifica file
Motivo: Agent-Helper è read-only
Agente corretto per questa operazione: Agent-FrameworkDocs
────────────────────────────────────────
```

### Richiesta git:
```
OPERAZIONE NON CONSENTITA
────────────────────────────────────────
Azione richiesta: operazione git
Motivo: Agent-Helper non gestisce git
Agente corretto: Agent-Git
────────────────────────────────────────
```

### Richiesta su file fuori da .github/:
```
OPERAZIONE NON CONSENTITA
────────────────────────────────────────
Azione richiesta: lettura fuori da .github/
Motivo: scope limitato a .github/
Agente corretto per analisi codebase: Agent-Analyze
────────────────────────────────────────
```
