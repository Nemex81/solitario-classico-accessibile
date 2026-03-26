# docs/5 - todolist

**Scopo:** Checklist operative per feature in sviluppo, prodotte da Agent-Plan.

## Agenti

| Ruolo | Agente |
|-------|--------|
| Scrittura | Agent-Plan |
| Lettura | Agent-Code |

## Convenzione naming

`TODO_<feature>_vX.Y.Z.md`

Esempi:
- `TODO_document-governance_v1.9.0.md`
- `TODO_audio-integration_v3.5.0.md`

## Istruzioni specifiche

Questa cartella contiene i TODO specifici per singola implementazione.
Ogni file rappresenta un task o una iniziativa implementativa, con:
- link al piano di riferimento (PLAN_*.md) in testa al file
- checklist spuntabile per ogni fase
- stato aggiornabile durante l'esecuzione da Agent-Code

`docs/TODO.md` (radice) è il coordinatore persistente che indicizza i task attivi.
Non sovrascrivere mai i file esistenti: il bootstrap è sempre additivo.
