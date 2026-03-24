# .github/templates/

Deposito dei template neutri e resettabili del framework.
I file in questa cartella sono **sorgenti di struttura**,
non documenti operativi.

## Convenzioni

- Naming: `<nome-file>.template.md`
- Contenuto: struttura canonica con tutti i campi vuoti
  o placeholder, pronti alla compilazione
- Proprietà: ogni template appartiene all'agente o alla
  skill che lo usa — non modificare senza aggiornare
  il componente referente

## File presenti

| File | Usato da | Scopo |
| ---- | -------- | ----- |
| `project-profile.template.md` | Agent-Welcome, project-profile.skill.md | Template neutro profilo progetto |

## Chi può leggere / scrivere

- **Lettura**: Agent-Welcome, qualsiasi agente che genera
  o resetta file strutturati
- **Scrittura**: Agent-FrameworkDocs (manutenzione template);
  Agent-Welcome NON scrive mai in questa cartella,
  solo legge
