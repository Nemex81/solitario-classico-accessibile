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

## Chi può leggere / scrivere

- **Lettura**: Agent-Welcome, qualsiasi agente che genera
  o resetta file strutturati
- **Scrittura**: Agent-FrameworkDocs (manutenzione template);
  Agent-Welcome NON scrive mai in questa cartella,
  solo legge
