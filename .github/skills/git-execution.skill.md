<!-- markdownlint-disable MD041 -->

***
name: git-execution
description: >
  Lista tecnica dei comandi git autorizzati per contesto.
  Definisce cosa Copilot può eseguire tramite run_in_terminal
  e cosa deve invece proporre come testo all'utente.
  Richiamabile da Agent-Code e Agent-Orchestrator.
***

# Skill: Git Execution

## Principio base

La git policy del progetto distingue tre categorie di comandi:

- **ESEGUIBILI**: Copilot può eseguire tramite `run_in_terminal`
  solo nei prompt autorizzati
- **PROPONIBILI**: Copilot produce il comando come testo,
  l'utente lo copia e lo esegue
- **VIETATI**: mai eseguiti né proposti da Copilot

## Matrice autorizzazioni per contesto

### Contesto: agenti (Code, Validate, Docs, Release, ecc.)

| Comando | Autorizzazione |
| ------- | -------------- |
| git status, log, diff | ESEGUIBILE (read-only) |
| git add | PROPONIBILE |
| git commit | PROPONIBILE |
| git merge | PROPONIBILE |
| git push | PROPONIBILE |
| git tag | PROPONIBILE |
| git rebase | VIETATO |
| git reset --hard | VIETATO |

### Contesto: `#git-commit.prompt.md`

| Comando | Autorizzazione |
| ------- | -------------- |
| git status, log, diff | ESEGUIBILE |
| git add &lt;file&gt; | ESEGUIBILE (con conferma utente) |
| git commit -m "..." | ESEGUIBILE (Conventional Commits) |
| git push | PROPONIBILE |
| git commit --amend | VIETATO |
| git reset | VIETATO |

### Contesto: `#git-merge.prompt.md`

| Comando | Autorizzazione |
| ------- | -------------- |
| git status, log, diff | ESEGUIBILE |
| git checkout &lt;branch&gt; | ESEGUIBILE |
| git merge --no-ff | ESEGUIBILE (con conferma utente) |
| git tag &lt;tag&gt; | ESEGUIBILE (con conferma esplicita) |
| git push | PROPONIBILE |
| git merge --squash | VIETATO |
| git rebase | VIETATO |
| git reset --hard | VIETATO |

## Formato output comandi proponibili

Quando un comando è PROPONIBILE, Copilot lo presenta SEMPRE così:

```bash
# Esegui manualmente nel terminale:
git commit -m "feat(domain): aggiungi CardStack"
```

Mai presentare comandi proponibili inline nel testo senza
il blocco bash e il commento esplicativo.

## Agenti che usano questa skill

- Agent-Code: per sapere cosa proporre dopo ogni fase implementativa
- Agent-Orchestrator: per gestire i checkpoint git nel workflow E2E
