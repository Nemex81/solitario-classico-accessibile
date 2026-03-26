# docs/4 - reports

**Scopo:** Report copertura e validazione gate, output CI prodotti da Agent-Validate.

## Agenti

| Ruolo | Agente |
|-------|--------|
| Scrittura | Agent-Validate |
| Lettura | Agent-Docs |

## Convenzione naming

`REPORT_<tipo>_YYYY-MM-DD.md`

Esempi:
- `REPORT_coverage_2026-03-26.md`
- `REPORT_gate-validation_2026-03-26.md`

## Istruzioni specifiche

Questa cartella contiene i report di validazione e copertura prodotti da Agent-Validate
al termine di ogni ciclo di implementazione.

I report sono collegati al piano (PLAN_*.md) o al task (TODO_*.md) di origine.
Agent-Docs li referenzia durante la sincronizzazione documentale.

Il bootstrap non sovrascrive mai il contenuto di questa cartella.
