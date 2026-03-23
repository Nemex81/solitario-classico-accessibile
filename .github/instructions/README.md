# Instructions Files — Framework Copilot

Le instructions files si attivano automaticamente in VS Code Copilot
in base al file aperto nell'editor (frontmatter `applyTo`).

## File presenti

- `python.instructions.md` — standard Python
  (applyTo: `**/*.py`)
- `tests.instructions.md` — standard test e coverage
  (applyTo: `tests/**/*.py`)
- `domain.instructions.md` — regole layer domain
  (applyTo: `src/domain/**/*.py`)
- `git-policy.instructions.md` — git policy e comandi autorizzati
  (applyTo: `**` — attivo in tutti i contesti)
- `model-policy.instructions.md` — Model Policy agenti: assegnazioni modello
  primario e fallback per tutti e 10 gli agenti del framework. Attivo
  automaticamente su `.github/**`.

## Come funzionano

VS Code Copilot legge automaticamente le instructions il cui `applyTo`
corrisponde al file attivo nell'editor. Non richiedono invocazione esplicita.
Le instructions con `applyTo: "**"` sono attive in qualsiasi contesto.
