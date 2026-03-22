# Agent Skills — Framework Copilot

Le skills sono abilità atomiche riutilizzabili tra più agenti.
Non si attivano automaticamente: gli agenti le referenziano
esplicitamente nella sezione "Riferimenti Skills".

## Skills presenti

- `validate-accessibility.skill.md` — checklist WAI-ARIA + NVDA (UI)
- `conventional-commit.skill.md` — regole Conventional Commits
- `semver-bump.skill.md` — logica SemVer per release
- `clean-architecture-rules.skill.md` — regole Clean Architecture 4 layer
- `document-template.skill.md` — struttura DESIGN, PLAN e TODO
- `accessibility-output.skill.md` — standard output accessibile (tutti gli agenti)
- `git-execution.skill.md` — matrice autorizzazioni comandi git per contesto
- `file-deletion-guard.skill.md` — guardia con conferma obbligatoria
  prima di eliminare file o directory

## Agenti e skills associate

| Agente | Skills referenziate |
| ------ | ------------------ |
| Agent-Analyze | clean-architecture-rules, accessibility-output |
| Agent-Design | clean-architecture-rules, document-template, accessibility-output |
| Agent-Plan | document-template, accessibility-output |
| Agent-Code | conventional-commit, validate-accessibility, clean-architecture-rules, accessibility-output, git-execution, file-deletion-guard |
| Agent-Validate | tests (instructions), validate-accessibility, accessibility-output |
| Agent-Docs | semver-bump, accessibility-output |
| Agent-Release | semver-bump, accessibility-output |
| Agent-FrameworkDocs | accessibility-output, file-deletion-guard |
| Agent-Git | git-execution, conventional-commit, accessibility-output, file-deletion-guard |
| Agent-Orchestrator | accessibility-output, git-execution |
