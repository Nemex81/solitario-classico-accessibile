***
applyTo: "**"
***

# Git Policy — Solitario Classico Accessibile

## Regola fondamentale

Copilot NON esegue comandi git in autonomia durante implementazioni,
analisi, design, planning o documentazione.
La regola è assoluta in tutti questi contesti.

## Comandi sempre vietati in autonomia

- `git push` — mai, in nessun contesto
- `git merge` — vietato fuori dai prompt autorizzati
- `git commit` — vietato fuori dai prompt autorizzati
- `git rebase` — mai, in nessun contesto
- `git reset --hard` — mai, in nessun contesto
- `git tag` — solo proposto come comando testuale, mai eseguito

## Comandi sempre consentiti (read-only)

- `git log`, `git log --oneline`
- `git diff`, `git diff --staged`
- `git status`
- `git branch`, `git branch -a`
- `git show <sha>`

## Eccezioni autorizzate

I seguenti 2 prompt sono gli UNICI contesti in cui Copilot può
eseguire comandi git tramite `run_in_terminal`:

### `#git-commit.prompt.md`
Comandi consentiti:
- `git add <file>` o `git add .` (con conferma esplicita utente)
- `git commit -m "<messaggio>"` (formato Conventional Commits obbligatorio)

Comandi vietati anche in questo prompt:
- `git push`
- `git commit --amend`
- `git commit -a` senza staging esplicito

### `#git-merge.prompt.md`
Comandi consentiti:
- `git checkout <branch>`
- `git merge --no-ff <branch> -m "<messaggio>"`
- `git tag <tag>` (proposto come comando testuale, eseguito solo
  con conferma esplicita utente)

Comandi vietati anche in questo prompt:
- `git push` (proposto come comando testuale, mai eseguito)
- `git merge --squash`
- `git merge --ff-only`

## Comportamento atteso degli agenti

Durante qualsiasi fase del ciclo E2E (Analyze, Design, Plan, Code,
Validate, Docs, Release), se Copilot determina che un commit o un
merge sarebbe appropriato:

1. NON eseguire il comando
2. Produrre un blocco testuale con i comandi proposti:
   ```bash
   # Comandi da eseguire manualmente:
   git add src/application/game_service.py
   git commit -m "feat(application): aggiungi metodo draw_card"
   ```
3. Comunicare: "Comandi proposti sopra. Eseguili nel terminale
   quando sei pronto, poi confermami per procedere."

## Riferimento skill

Per la lista tecnica completa dei comandi autorizzati per contesto:
→ `.github/skills/git-execution.skill.md`
