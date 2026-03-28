# .github/templates/

Deposito dei template neutri e resettabili del framework.
I file in questa cartella sono **sorgenti di struttura**,
non documenti operativi.

## Convenzioni

- Naming misto:
  - `*.template.md` per template persistenti di profilo o struttura generale
  - `*.md` per template operativi usati nella generazione documentale
- Contenuto: struttura canonica con tutti i campi vuoti
  o placeholder, pronti alla compilazione
- Proprietà: ogni template appartiene all'agente o alla
  skill che lo usa — non modificare senza aggiornare
  il componente referente

## File presenti

| File | Usato da | Scopo |
| ---- | -------- | ----- |
| `design.md` | docs_manager.skill.md, Agent-Design | Template operativo per documenti DESIGN |
| `coding_plan.md` | docs_manager.skill.md, Agent-Plan | Template operativo per coding plan |
| `project-profile.template.md` | Agent-Welcome, project-profile.skill.md | Template neutro profilo progetto |
| `readme_folder.md` | docs_manager.skill.md, Agent-Welcome | Template README per bootstrap cartelle docs |
| `report.md` | docs_manager.skill.md, Agent-Validate | Template operativo per report |
| `todo_coordinator.md` | docs_manager.skill.md, Agent-Welcome | Template bootstrap per docs/TODO.md |
| `todo_task.md` | docs_manager.skill.md, Agent-Plan | Template operativo per TODO per-task |
| `api.md` | project-doc-bootstrap.skill.md, Agent-Welcome (OP-4) | Template bootstrap per docs/API.md |
| `architecture.md` | project-doc-bootstrap.skill.md, Agent-Welcome (OP-4) | Template bootstrap per docs/ARCHITECTURE.md |
| `changelog.md` | project-doc-bootstrap.skill.md, Agent-Welcome (OP-4) | Template bootstrap per CHANGELOG.md root |
| `project.instructions.md` | project-doc-bootstrap.skill.md, Agent-Welcome (OP-4 livello 3) | Template bootstrap per .github/instructions/project.instructions.md |
| `copilot-instructions.md` | project-doc-bootstrap.skill.md, Agent-Welcome (ripristino esplicito) | Template neutro per ripristino .github/copilot-instructions.md su richiesta esplicita |

## Chi può leggere / scrivere

- **Lettura**: Agent-Welcome, qualsiasi agente che genera
  o resetta file strutturati
- **Scrittura**: Agent-FrameworkDocs (manutenzione template);
  Agent-Welcome NON scrive mai in questa cartella,
  solo legge
