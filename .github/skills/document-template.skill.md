---
name: document-template
description: >
  Regole di compilazione dei documenti DESIGN e PLAN del progetto.
  Richiamabile da Agent-Design e Agent-Plan per garantire frontmatter
  YAML corretto, sezioni obbligatorie presenti e stati del ciclo di vita
  rispettati.
---

# Skill: Document Template

## DESIGN_*.md — Struttura obbligatoria

Percorso: `docs/2 - projects/DESIGN_<feature>.md`

Frontmatter YAML richiesto:
```yaml
---
feature: <nome feature>
agent: Agent-Design
status: DRAFT
version: vX.Y.Z
date: YYYY-MM-DD
---
```

Sezioni obbligatorie (nessuna può essere vuota):
1. Idea in 3 righe (descrizione sintetica)
2. Attori e Concetti (entità coinvolte)
3. Flussi Concettuali (sequenze principali)
4. Decisioni Architetturali (pattern scelti e motivazione)
5. Rischi e Vincoli (accessibilità, performance, backward compat)

Diagrammi: solo testuali (ASCII o Mermaid semplice). Mai grafici.

Ciclo di vita stati:
- `DRAFT` → prodotto da Agent-Design, in attesa di review
- `REVIEWED` → confermato dall'utente, Agent-Plan può procedere

## PLAN_*.md — Struttura obbligatoria

Percorso: `docs/3 - coding plans/PLAN_<feature>_vX.Y.Z.md`

Frontmatter YAML richiesto:
```yaml
---
feature: <nome feature>
agent: Agent-Plan
status: DRAFT
version: vX.Y.Z
design_ref: docs/2 - projects/DESIGN_<feature>.md
date: YYYY-MM-DD
---
```

Sezioni obbligatorie:
1. Executive Summary (tipo, priorità, branch, versione)
2. Problema e Obiettivo
3. File coinvolti (CREATE / MODIFY / DELETE per ogni file)
4. Fasi sequenziali (ognuna atomica e committable separatamente)
5. Test Plan (unit + integration)

Ciclo di vita stati:
- `DRAFT` → prodotto da Agent-Plan, in attesa di review
- `READY` → confermato dall'utente, Agent-Code può procedere

## docs/5 - todolist/TODO_*.md — Struttura obbligatoria

Percorso: `docs/5 - todolist/TODO_<feature>_vX.Y.Z.md`

- Link al PLAN di riferimento in testa al file
- Checklist spuntabile per ogni fase (`[ ]` / `[x]`)
- Istruzioni per Agent-Code (workflow incrementale)
- Aggiornato immediatamente dopo ogni commit di Agent-Code

Prodotto da: `Agent-Plan`
Aggiornato da: `Agent-Code` (solo il file del task attivo)

## docs/TODO.md — Ruolo (coordinatore persistente)

`docs/TODO.md` è il coordinatore persistente del sistema documentale.
NON è una checklist di task: è l'indice dei lavori attivi.

Struttura attesa:

```markdown
### Progetti
<!-- link relativi ai file attivi in docs/2 - projects/ -->

### Piani
<!-- link relativi ai file attivi in docs/3 - coding plans/ -->

### Reports
<!-- link relativi ai file attivi in docs/4 - reports/ -->

### Tasks
<!-- link relativi ai file attivi in docs/5 - todolist/ -->
```

Regole:
- Non sovrascrivere mai il contenuto esistente: solo append nelle sezioni
- Aggiornato da `Agent-Plan` (link al nuovo TODO per-task) e `Agent-Docs` (validazione)
- Per la gestione operativa completa: → `.github/skills/docs_manager.skill.md`