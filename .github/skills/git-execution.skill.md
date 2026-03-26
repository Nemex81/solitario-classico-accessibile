<!-- markdownlint-disable MD041 -->

---
name: git-execution
description: >
  Lista tecnica dei comandi git autorizzati per contesto.
  Definisce cosa Copilot può eseguire tramite run_in_terminal
  e cosa deve invece proporre come testo all'utente.
  Richiamabile da Agent-Git, Agent-Code e Agent-Orchestrator.
---

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

### Contesto: `Agent-Git`

| Comando | Autorizzazione | Modalità |
| ------- | -------------- | -------- |
| git status, log, diff | ESEGUIBILE diretto | read-only, senza script |
| git add | ESEGUIBILE | solo via git_runner.py |
| git commit -m "..." | ESEGUIBILE | solo via git_runner.py |
| git merge --no-ff | ESEGUIBILE | solo via git_runner.py |
| git push | ESEGUIBILE | solo via git_runner.py |
| git revert <sha> | ESEGUIBILE | solo via git_runner.py, richiede "REVERT" maiuscolo |
| git reset --soft HEAD~N | ESEGUIBILE | solo via git_runner.py, richiede "RESET" maiuscolo, solo su commit non pushati |
| git tag | PROPONIBILE | git_runner.py tag (output `TAG OK`, nessuna esecuzione) |
| git commit --amend | VIETATO | — |
| git rebase | VIETATO | — |
| git reset --hard | VIETATO | — |

### Contesto: `#git-commit.prompt.md`

| Comando | Autorizzazione |
| ------- | -------------- |
| subagent Agent-Git | ESEGUIBILE |
| git status, log, diff | NON DIRETTO — delegato |
| git add &lt;file&gt; | NON DIRETTO — delegato |
| git commit -m "..." | NON DIRETTO — delegato |
| git push | NON DIRETTO — delegato |
| git commit --amend | VIETATO |
| git reset | VIETATO |

### Contesto: `#git-merge.prompt.md`

| Comando | Autorizzazione |
| ------- | -------------- |
| subagent Agent-Git | ESEGUIBILE |
| git status, log, diff | NON DIRETTO — delegato |
| git checkout &lt;branch&gt; | NON DIRETTO — delegato |
| git merge --no-ff | NON DIRETTO — delegato |
| git tag &lt;tag&gt; | PROPONIBILE |
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

---

## Pattern di invocazione: git_runner.py

Agent-Git non esegue git add/commit/push/merge tramite
run_in_terminal diretto. Usa scripts/git_runner.py
come wrapper atomico. I prompt git-commit e git-merge
non eseguono git: raccolgono contesto e delegano ad Agent-Git.

### Contratto di invocazione

```bash
# Commit locale
python scripts/git_runner.py commit --message "<msg>"

# Commit + push in un solo comando
python scripts/git_runner.py commit --message "<msg>" --push

# Push su branch esplicito
python scripts/git_runner.py push --branch <branch>

# Merge no-fast-forward
python scripts/git_runner.py merge \
  --source <branch-sorgente> \
  --target <branch-target> \
  --message "<msg>"

# Tag (solo proposto, mai eseguito)
python scripts/git_runner.py tag --name <tag>
```

### Contratto di output

Ogni invocazione produce su stdout:

```
GIT_RUNNER: <SUBCOMMAND> <OK|FAIL>
──────────────────────────────────────────
<output tecnico raw>
──────────────────────────────────────────
RIEPILOGO:
  <chiave>  : <valore>
```

Agent-Git legge la prima riga per determinare
esito (OK → procedi, FAIL → blocca e mostra errore).
Il blocco RIEPILOGO fornisce i dati strutturati per
costruire il feedback finale all'utente.

### Cosa lo script NON fa

- Non legge né scrive file .md
- Non genera messaggi commit
- Non aggiorna CHANGELOG
- Non prende decisioni: esegue solo ciò che riceve
- Non esegue mai tag autonomamente
- Non decide se chiedere conferme utente: questo resta compito dell'agente

## Agenti che usano questa skill

- Agent-Git: logica operativa principale per operazioni git autorizzate
- Agent-Code: per sapere cosa proporre dopo ogni fase implementativa
- Agent-Orchestrator: per gestire i checkpoint git nel workflow E2E
