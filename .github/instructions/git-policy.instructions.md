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

I seguenti contesti sono gli UNICI in cui Copilot può eseguire
comandi git tramite `run_in_terminal`:

### `Agent-Git` (logica operativa principale)
Agente dedicato. Gestisce commit, push, merge, tag.
Invocabile dal dropdown o tramite subagent delegation.
Regole di conferma:
- Push: richiede "PUSH" maiuscolo
- Merge: richiede "MERGE" maiuscolo
- Commit: richiede conferma messaggio

### `#git-commit.prompt.md` (dispatcher)
Delega ad Agent-Git. Non esegue git direttamente.

### `#git-merge.prompt.md` (dispatcher)
Delega ad Agent-Git. Non esegue git direttamente.

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

## Protezione eliminazione file

Qualsiasi operazione che elimina file o directory è soggetta
alla procedura definita in:
→ `.github/skills/file-deletion-guard.skill.md`

Questa regola si applica in TUTTI i contesti git, inclusi:
- Risoluzione conflitti durante merge
- Operazioni `git rm` o `git clean`

Nessun agente può bypassare questa procedura.

## Riferimento skill

Per la lista tecnica completa dei comandi autorizzati per contesto:
→ `.github/skills/git-execution.skill.md`
